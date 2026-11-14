# Étape 33 — Mécanisme d'Attention (Self-Attention) et Scaled Dot-Product

> Étape 33 du parcours · Prérequis : [Formules de l'attention et facteur d'échelle](<32-Attention-Formules-et-Role-de-Racine-dk.md>) · Suite : [Génération : prefill, décodage, cache KV, TTFT et streaming](<33b-Generation-Prefill-Decode-Cache-KV-Streaming.md>)

## Définition

Le mécanisme d'attention est le cœur mathématique des Transformers, l'architecture des modèles de langage qui animent les agents. Il permet au modèle de peser l'importance relative de chaque token d'un texte par rapport aux autres, afin de comprendre le contexte. Chaque token commence par un vecteur, son **embedding** ; trois matrices apprises en tirent trois vecteurs différents : ce que le token **cherche** (sa requête), ce qu'il **expose** (sa clé) et ce qu'il **transmet** (sa valeur). Le score d'un couple de tokens est le produit scalaire de la requête de l'un et de la clé de l'autre, divisé par √dₖ ; la softmax transforme chaque ligne de scores en poids de somme 1, et chaque token reçoit la moyenne des valeurs pondérée par ces poids. Ce chapitre ajoute aux étapes 31 et 32 les deux pièces qui manquaient pour écrire une couche complète : les projections X → Q, K, V et le masque causal.

## Rôle dans un agent

Un réseau récurrent (RNN) lit les tokens un par un et doit faire passer toute l'information du début dans un état de taille fixe, transmis de proche en proche ; plus le lien est lointain, plus il est fragile. L'attention relie au contraire **directement** chaque position à toutes celles qu'elle a le droit de voir : un pronom (« il ») peut être relié à son sujet même s'ils sont séparés de 1 000 tokens. Pour un développeur d'agent, ce mécanisme se manifeste à chaque appel du LLM, pendant l'étape **décider** de la boucle percevoir → décider → agir → observer, et il dicte trois règles pratiques : le masque causal fait qu'un passage ne peut intégrer que ce qui le précède dans le prompt ; la mémoire et le calcul de l'attention croissent comme le carré du nombre de tokens ; et le cache clé-valeur, qui évite de recalculer K et V pendant la génération, grandit avec chaque token produit.

## Équation complète

Projections des embeddings X (une ligne par token) :

$$
Q = X\, W_Q
$$

$$
K = X\, W_K
$$

$$
V = X\, W_V
$$

Attention avec masque :

$$
\text{Attention}(Q, K, V) = \text{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} + M \right) V
$$

Masque causal :

$$
M_{ij} = \begin{cases} 0 & \text{si } j \le i \\ -\infty & \text{si } j > i \end{cases}
$$

Mémoire de la matrice des scores, pour une tête, en flottants 16 bits (2 octets) :

$$
\text{mémoire} = 2\, N^2 \ \text{octets}
$$

## Décryptage des symboles

$$
X
$$

**Sens :** embeddings des tokens, une ligne par token · **Type / plage :** voir le bloc ci-dessous · **Variable Python :** `X`

$$
N \times d_{model}
$$

$$
W_Q,\quad W_K,\quad W_V
$$

**Sens :** matrices de projection apprises pendant l'entraînement · **Type / plage :** voir le bloc ci-dessous · **Variable Python :** `W_Q`, `W_K`, `W_V`

$$
d_{model} \times d_k,\quad d_{model} \times d_k,\quad d_{model} \times d_v
$$

**Symbole :** Q (Query) · **Sens :** la question que pose chaque token : « qu'est-ce que je cherche ? » · **Type / plage :** N × dₖ · **Variable Python :** `Q`

**Symbole :** K (Key) · **Sens :** l'étiquette de chaque token : « voici ce que je contiens » · **Type / plage :** N × dₖ · **Variable Python :** `K`

**Symbole :** V (Value) · **Sens :** le contenu réel, le sens, que chaque token transmet · **Type / plage :** N × dᵥ · **Variable Python :** `V`

$$
Q K^\top
$$

**Sens :** tous les produits scalaires requête-clé : un score de compatibilité par couple de tokens · **Type / plage :** N × N · **Variable Python :** `scores_bruts`

$$
d_k
$$

**Sens :** dimension des requêtes et des clés · **Type / plage :** entier ≥ 1 · **Variable Python :** `d_k`

$$
\sqrt{d_k}
$$

**Sens :** facteur d'échelle, démontré à l'étape 32 · **Type / plage :** réel > 0 · **Variable Python :** `echelle`

**Symbole :** softmax · **Sens :** transforme chaque ligne de scores en poids positifs de somme 1 · **Type / plage :** fonction · **Variable Python :** `softmax`

$$
M
$$

**Sens :** masque causal : 0 pour le passé et le présent, −∞ pour le futur · **Type / plage :** N × N · **Variable Python :** `masque_causal(n)`

$$
N
$$

**Sens :** nombre de tokens du contexte · **Type / plage :** entier ≥ 1 · **Variable Python :** `n`

Dans la multiplication finale par V, les poids choisissent et les valeurs apportent le contenu : on fait une moyenne pondérée des contenus réels. L'ancienne version de ce tableau était une liste dont les puces commençaient par des formules en gras et contenaient des blocs de formule centrés et des `\)` orphelins, ce qui ne s'affichait pas.

## Démonstration

### 1. Les projections : trois lectures linéaires du même embedding

La ligne i de

$$
Q = X W_Q
$$

vaut

$$
\mathbf{q}_i = \mathbf{x}_i W_Q = \sum_{l} x_{il}\, \mathbf{w}_l ,
$$

où 𝐰ₗ est la ligne l de

$$
W_Q ,
$$

parce qu'un produit matriciel se calcule ligne par ligne et que multiplier un vecteur ligne par une matrice combine les lignes de cette matrice avec les coordonnées du vecteur pour coefficients. Avec un embedding one-hot 𝐱ᵢ = 𝐞ᵢ (un 1 en position i, des 0 ailleurs), il ne reste qu'un terme : 𝐪ᵢ = 𝐰ᵢ, la ligne i de

$$
W_Q .
$$

C'est pourquoi, dans l'exemple, Q, K et V sont exactement

$$
W_Q ,
$$

$$
W_K
$$

et

$$
W_V .
$$

Avec un embedding dense 𝐱 = [1 ; 0 ; 0,5], on obtient

$$
\mathbf{q} = 1 \times [2 ; 0] + 0{,}5 \times [0 ; 1{,}5] = [2 ; 0{,}75] .
$$

Les trois matrices sont différentes, si bien qu'un même token peut chercher une chose (sa requête), en annoncer une autre (sa clé) et en transmettre une troisième (sa valeur).

### 2. Sans projections, chaque token se regarde lui-même

Supposons Q = K = X, sans projection, et des embeddings qui ont tous la même norme r. Pour tout couple (i, j), l'inégalité de Cauchy-Schwarz (étape 14) donne :

$$
\mathbf{x}_i \cdot \mathbf{x}_j \le \lVert \mathbf{x}_i \rVert \, \lVert \mathbf{x}_j \rVert = r^2 = \mathbf{x}_i \cdot \mathbf{x}_i
$$

L'égalité n'a lieu que si 𝐱ⱼ = 𝐱ᵢ (même norme et même direction). Le plus grand score de chaque ligne est donc sur la diagonale : chaque token donne son plus grand poids à lui-même, et l'attention ne relie rien. Avec les embeddings one-hot de l'exemple, X Xᵀ est la matrice identité, et le programme affiche bien que « il » regarde « il », « Paul » regarde « Paul » et « dort » regarde « dort ». Les projections brisent cette symétrie : avec

$$
W_Q \neq W_K ,
$$

la requête de « il » ressemble davantage à la clé de « Paul » qu'à la sienne, puisque

$$
\mathbf{q}_{il} \cdot \mathbf{k}_{Paul} = 4 > \mathbf{q}_{il} \cdot \mathbf{k}_{il} = 1 .
$$

### 3. La sortie est une moyenne pondérée des valeurs

La sortie du token i vaut 𝐨ᵢ = ∑ⱼ aᵢⱼ 𝐯ⱼ, avec des poids positifs de somme 1 : c'est une moyenne pondérée, démontrée à l'étape 31 (points 1 et 2). Avec des valeurs one-hot (V égale à l'identité), 𝐨ᵢ = ∑ⱼ aᵢⱼ 𝐞ⱼ = (aᵢ₁, aᵢ₂, aᵢ₃) : la sortie **est** la ligne de poids, ce que le programme vérifie. À la main, pour « il » : les scores bruts [1 ; 4 ; 0] deviennent [0,70711 ; 2,82843 ; 0] après division par √2 ; leurs exponentielles valent 2,02811, 16,91883 et 1, de somme 19,94694 ; les poids valent donc 0,1017, 0,8482 et 0,0501. La sortie de « il » contient 84,8 % de la valeur de « Paul ». Pour « dort », les scores [0 ; 0 ; 3] donnent

$$
e^{3/\sqrt{2}} \approx 8{,}34214
$$

et un poids sur lui-même de 8,34214 / 10,34214 ≈ 0,8066.

### 4. Le masque causal : seul le passé est visible

Un score masqué vaut −∞, donc son poids vaut exactement 0, et les poids restants se renormalisent entre les tokens visibles (étape 31, point 3). Dans l'ordre (il, Paul, dort), « il » est en tête : il ne voit que lui-même, son poids vaut [1 ; 0 ; 0], et un modèle génératif ne peut pas relier ce pronom à un nom qui vient après lui. Dans l'ordre (Paul, dort, il), « il » est en dernier et voit les trois tokens ; ses poids sur (Paul, dort, il) valent [0,8482 ; 0,0501 ; 0,1017], exactement ceux du calcul sans masque, réordonnés. Ce n'est pas un hasard : la formule ne dépend pas de l'ordre des couples clé-valeur (étape 31, point 4), donc seul le masque décide qui voit qui.

### 5. Le facteur d'échelle (démontré à l'étape 32)

L'étape 32 démontre que, si les composantes de 𝐪 et 𝐤 sont indépendantes, de moyenne 0 et de variance 1, alors Var(𝐪 · 𝐤) = dₖ, et que la division par √dₖ ramène cette variance à 1. Le programme le vérifie ici par Monte-Carlo : sur 2 000 tirages en dimension 64, il estime une variance de 65,2 avant division et de 1,019 après. Il montre aussi l'effet d'un score énorme : avec [30 ; 0 ; 0], la probabilité maximale vaut 1/(1 + 2e⁻³⁰), donc 1 − p ≈ 2e⁻³⁰ ≈ 1,87 × 10⁻¹³, et la pente p(1−p) vaut environ 1,87 × 10⁻¹³. Après division par

$$
\sqrt{64} = 8 ,
$$

les scores [3,75 ; 0 ; 0] donnent p = e³,⁷⁵/(e³,⁷⁵ + 2) ≈ 0,9551 et une pente de 0,0429, environ 2,3 × 10¹¹ fois plus grande.

### 6. Le coût : N² en calcul et en mémoire

La matrice Q Kᵀ a N × N cases ; chacune demande un produit scalaire de dₖ multiplications, puis la moyenne des valeurs en demande N² dᵥ (décompte détaillé à l'étape 31, point 5). Pour une tête de dimension dₖ = dᵥ = 128 et N = 100 000, cela fait 100 000² × 256 = 2,56 × 10¹² multiplications. Si la matrice des scores est stockée en entier, en flottants de 2 octets, elle occupe 2N² octets :

| N (tokens) | cases N² | mémoire, une tête, fp16 |
|---|---|---|
| 4 000 | 16 000 000 | 0,032 Go |
| 32 000 | 1 024 000 000 | 2,048 Go |
| 100 000 | 10 000 000 000 | 20 Go |
| 128 000 | 16 384 000 000 | 32,768 Go |

Multiplier N par 4, de 32 000 à 128 000 tokens, multiplie la mémoire par 16, parce que les deux dimensions de la matrice grandissent. Les projections, elles, coûtent

$$
N \cdot d_{model} \cdot d_k
$$

multiplications chacune, une quantité linéaire en N (étape 34) : sur un long contexte, c'est le terme en N² qui domine.

## Effets mathématiques (le principe de levier)

- **Si la dimension dₖ augmente sans le facteur.** La variance du produit scalaire croît comme dₖ (étape 32) ; la softmax « sature » (poids proches de 0 ou de 1), le gradient disparaît et le modèle n'apprend plus. Diviser par √dₖ maintient les scores à variance 1.
- **Si un score est très élevé (forte similarité).** Le poids de ce token se rapproche de 1 : l'agent « prête toute son attention » à ce token et ignore les autres.
- **Si les projections sont identiques ou absentes.** Avec des embeddings de même norme, chaque token se regarde lui-même (point 2) ; ce sont les différences entre

$$
W_Q
$$

et

$$
W_K
$$

qui créent des liens entre tokens différents.
- **Si un token est placé avant ce qu'il doit regarder.** Avec le masque causal, il ne peut pas le voir (point 4) ; l'ordre du prompt compte par le masque, pas par la formule.
- **Complexité quadratique.** La taille de la matrice Q Kᵀ est proportionnelle au carré du nombre de tokens : si le texte double de longueur, le calcul et la mémoire de l'attention quadruplent.

## Du symbole au code Python

L'attention est un enchaînement fixe. Le déroulé le suit sur le token « il », puis sur le cas où l'on retire la division. Copiez dans `attention.py`.

$$
X W
$$

**Variable ou fonction :** `projeter(X, W)`

$$
\mathbf{q} \cdot \mathbf{k}
$$

**Variable ou fonction :** `produit(ligne, colonne)`

**Symbole :** softmax d'une ligne · **Variable ou fonction :** `softmax(logits)`

$$
M
$$

**Variable ou fonction :** `masque_causal(n)`

$$
\text{softmax}(Q K^\top / \sqrt{d_k} + M)\, V
$$

**Variable ou fonction :** `attention(Q, K, V, mettre_a_echelle, masque)`

**Symbole :** Var(𝐪 · 𝐤) estimée · **Variable ou fonction :** `variance_du_produit_scalaire(d_k)`

### Déroulé, ligne par ligne

Trois tokens, dans l'ordre `il`, `Paul`, `dort`. Leurs embeddings sont one-hot : `X` est la matrice identité 3 × 3. Chaque ligne de `Q` et de `K` est un vecteur de longueur `d_k = 2`. Chaque ligne de `V` est le contenu qu'on mélangera, ici un vecteur one-hot : la valeur de « Paul » est `[0, 1, 0]`.

**`projeter(X, W)`** — c'est X W.

- La garde vérifie que chaque embedding a `len(W)` composantes, c'est-à-dire

$$
d_{model} ;
$$

sinon `ValueError`.
- `colonnes = [[W[l][c] for l in range(len(W))] for c in range(len(W[0]))]` extrait les colonnes de `W` : pour `W_Q`, `[2.0, 0.0, 0.0]` et `[0.0, 1.0, 1.5]`.
- Chaque ligne de sortie est la liste des produits scalaires de l'embedding avec ces colonnes. Pour l'embedding dense `[1.0, 0.0, 0.5]`, on obtient `[2.0, 0.75]` (démonstration, point 1) ; pour un embedding one-hot, on recopie la ligne du token.

**`produit(ligne, colonne)`** — `sum(a * b for a, b in zip(ligne, colonne))`. C'est le produit scalaire du chapitre 1, sans l'affichage. Pour la requête « il » = [2 ; 0] :

- contre la clé « il » [0,5 ; 0] : 2 × 0,5 + 0 × 0 = 1 ;
- contre « Paul » [2 ; 0] : 2 × 2 + 0 = 4 ;
- contre « dort » [0 ; 2] : 2 × 0 + 0 × 2 = 0.

La ligne de scores bruts vaut donc `[1, 4, 0]`. « il » ressemble à « Paul », pas à « dort ».

**`softmax(logits)`** — la même fonction que le chapitre 2, sur une seule ligne de scores.

- `pic = max(logits)` : on retranche le plus grand pour que `exp` ne déborde pas. Si `pic` vaut `-inf`, toute la ligne est masquée et les poids ne sont pas définis : `ValueError`.
- On divise chaque exponentielle par la somme. La ligne sort avec une somme égale à 1.

**`masque_causal(n)`** — pour `n = 3`, `[[0.0, -inf, -inf], [0.0, 0.0, -inf], [0.0, 0.0, 0.0]]` : la ligne i autorise les colonnes j ≤ i.

**`attention(Q, K, V, mettre_a_echelle, masque)`** — enchaîne les étapes pour chaque requête.

- `d_k = len(Q[0])` : 2, lu sur la première requête. Toutes les requêtes ont cette longueur.
- `echelle = math.sqrt(d_k)` si `mettre_a_echelle` est vrai, sinon `1`. Ici

$$
\sqrt{2} \approx 1{,}4142 .
$$

- Boucle `for i, q in enumerate(Q)`. Pour chaque requête, `scores = [produit(q, k) / echelle for k in K]`. La ligne `[1, 4, 0]` devient `[0.707, 2.828, 0.0]`.
- Si un masque est donné, `s + m` ajoute 0 aux tokens visibles et `-inf` aux tokens futurs.
- `poids.append(softmax(scores))`. Après softmax, la ligne de « il » vaut `[0.102, 0.848, 0.050]`. 84,8 % de l'attention est sur « Paul ».
- Deuxième boucle, sur les poids. `melange = [0.0] * d_v`, puis pour chaque token `j` et chaque coordonnée : `melange[coord] += poids_j * V[j][coord]`. La variable s'appelait `alpha` dans l'ancienne version ; elle s'appelle `poids_j`, parce que α désigne dans ce parcours le poids du score hybride (étape 23).
- Pour « il », la coordonnée 1 du mélange reçoit 0,848 × 1, parce que seule la valeur de « Paul » a un 1 à cet endroit. Les coordonnées 0 et 2 reçoivent les petits poids 0,102 et 0,050. La sortie de « il » est donc presque la valeur de « Paul ». C'est le sens de la multiplication finale par V : les poids choisissent, les valeurs apportent le contenu.

Les deux autres requêtes refont le même chemin. « dort » a un score brut de 3 contre sa propre clé et 0 contre les autres. Après échelle et softmax, 80,7 % de son poids reste sur lui-même. « Paul » a un score brut de 2 contre « dort » et 0 contre les autres : il donne 67,3 % de son poids à « dort », un choix des matrices de l'exemple, pas une règle.

**`variance_du_produit_scalaire(d_k, n_tirages, graine)`** — l'ancienne version ne tirait aucun nombre au hasard : elle renvoyait `(d_k, 1)` écrit en dur, ce qui ne vérifiait rien. Elle tire maintenant 2 000 couples `(q, k)` avec un générateur privé `random.Random(6)` à graine fixe, chaque coordonnée suivant une loi normale centrée de variance 1 (les hypothèses de l'étape 32). Elle renvoie la variance empirique des produits, puis celle des produits divisés par √dₖ : 65,2 et 1,019 pour dₖ = 64.

**`main()`, bloc 0 : les projections.** `projeter(X, W_Q)` recopie `W_Q` parce que `X` est l'identité ; l'`assert` le vérifie pour les trois matrices. L'embedding dense donne `[2.0, 0.75]`. Enfin, `attention(X, X, X)` sans projection montre que chaque token se regarde lui-même : la liste des préférés vaut `['il', 'Paul', 'dort']` (point 2).

**`main()`, bloc 1 bis : le masque.** Dans l'ordre d'origine, « il » reçoit `[1.0, 0.0, 0.0]`. On réordonne ensuite les lignes de `Q`, `K` et `V` selon `[1, 2, 0]`, soit (Paul, dort, il) : « il » est dernier et retrouve les poids `[0.8482, 0.0501, 0.1017]`, ceux du bloc 1 dans le nouvel ordre. Les poids au-dessus de la diagonale sont comparés à `0.0` avec `==` : ils sont exactement nuls.

**Pourquoi la division existe**, bloc 2 de `main`.

- On fabrique des scores déjà énormes, `[30.0, 0.0, 0.0]`, comme si le produit scalaire avait tourné en dimension `d_k = 64` sans être ramené.
- `p_max_et_gradient` calcule la softmax, prend la plus grande probabilité, puis `p * (1 - p)`. C'est la dérivée diagonale du chapitre 2, le signal qui sert à apprendre.
- Sans division : la probabilité maximale vaut 1 − 1,87 × 10⁻¹³. Le gradient vaut 1,87 × 10⁻¹³. Il est numériquement mort.
- Avec division : on remplace les scores par `[30 / 8, 0, 0]`, soit `[3.75, 0.0, 0.0]`, parce que

$$
\sqrt{64} = 8 .
$$

La probabilité maximale vaut 0,955. Le gradient vaut 0,0429, soit environ 2,3 × 10¹¹ fois plus grand.
- `variance_du_produit_scalaire(64)` fournit les deux variances estimées ; les `assert` exigent qu'elles soient à moins de 10 % de 64 et de 1.

**La mémoire**, bloc 3.

- `cases = n * n` : la matrice des scores a une case par couple de tokens.
- `octets = cases * 2` : chaque case est un flottant 16 bits, donc 2 octets.
- À N = 100 000, 100 000² × 2 / 10⁹ = 20 Go pour une seule tête. Doubler N multiplie ce nombre par 4, parce que les deux dimensions de la matrice grandissent. Les derniers `assert` vérifient le tableau du point 6 et les nombres des cas d'usage.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`produit(ligne, colonne)`** — Cette fonction est le geste élémentaire d'un comptable qui pose deux colonnes de chiffres côte à côte : elle reçoit deux listes, multiplie leurs éléments rang par rang et additionne le tout, puis renvoie ce nombre, le produit scalaire. Elle ne vérifie rien elle-même, car `projeter` contrôle les dimensions en amont ; on la retrouve partout, pour projeter les embeddings sur les colonnes de W, pour calculer les scores requête-clé (la requête « il » donne 1, 4 et 0 contre les trois clés) et pour les produits aléatoires de l'expérience de variance.

**`softmax(logits)`** — On peut la voir en répartiteur qui distribue cent pour cent de l'attention d'un token entre les autres : elle reçoit une ligne de scores, repère le plus grand, et lève une `ValueError` si ce maximum vaut moins l'infini, c'est-à-dire si le masque a caché toute la ligne et qu'aucun token n'est visible. Sinon, elle retranche ce maximum à chaque score, prend les exponentielles et les divise par leur somme, puis renvoie une ligne de poids qui totalisent 1 ; un score masqué à moins l'infini y reçoit un poids exactement nul, ce que `main` vérifie au-dessus de la diagonale.

**`projeter(X, W)`** — Imaginons un traducteur qui réécrit chaque mot dans un autre alphabet : la fonction reçoit la liste X des embeddings, un par token, et une matrice W, lève une `ValueError` si un embedding n'a pas exactement autant de composantes que W a de lignes, puis extrait les colonnes de W et calcule, pour chaque embedding, ses produits scalaires avec chacune d'elles. Elle renvoie ainsi le produit matriciel X W, ligne par ligne ; `main` s'en sert pour fabriquer Q, K et V à partir des embeddings one-hot, qui recopient simplement les lignes de W, et pour montrer que l'embedding dense `[1.0, 0.0, 0.5]` donne la requête `[2.0, 0.75]`.

**`masque_causal(n)`** — Cette fonction dresse le règlement d'une salle où chacun ne peut regarder que ceux qui sont entrés avant lui : elle reçoit le nombre n de tokens et renvoie une matrice n × n dont la case (i, j) vaut 0 quand j ≤ i, pour le passé et le présent, et moins l'infini quand j > i, pour le futur interdit. Ajoutée aux scores dans `attention`, elle rend nul le poids de tout token futur ; avec n = 3, la première ligne n'autorise que la première colonne, si bien que « il », placé en tête, reçoit les poids `[1.0, 0.0, 0.0]`.

**`attention(Q, K, V, mettre_a_echelle, masque)`** — C'est la scène entière de l'attention, jouée token par token : la fonction reçoit les requêtes Q, les clés K, les valeurs V, un drapeau qui décide si l'on divise les scores par √dₖ (vrai par défaut) et un masque facultatif. Pour chaque requête, elle calcule les produits scalaires avec toutes les clés, les divise par l'échelle, leur ajoute la ligne du masque s'il existe, garde aussi les scores bruts non divisés et passe la ligne à `softmax` ; elle mélange ensuite les valeurs, coordonnée par coordonnée, selon ces poids. Elle renvoie trois listes, scores bruts, poids et sorties, et sur l'exemple la requête « il » obtient les scores `[1.0, 4.0, 0.0]` puis les poids `[0.1017, 0.8482, 0.0501]`, presque tout sur « Paul ».

**`variance(xs)`** — Cette petite fonction interne vit dans `variance_du_produit_scalaire`, comme un statisticien installé au fond de la salle des tirages : elle reçoit une liste de nombres, calcule leur moyenne, puis la somme des carrés des écarts à cette moyenne divisée par le nombre de valeurs moins un, ce qui donne l'estimation sans biais de la variance. Elle renvoie ce seul nombre, et la fonction qui l'abrite l'appelle deux fois, sur les 2 000 produits bruts puis sur ces mêmes produits divisés par √dₖ, d'où les variances 65,2 et 1,019 affichées pour dₖ = 64.

**`p_max_et_gradient(logits)`** — Cette fonction interne vit dans `main`, au bloc 2, et joue le médecin qui prend le pouls de l'apprentissage : elle reçoit une ligne de scores, la passe à `softmax`, repère la plus grande probabilité p et renvoie le couple formé de p et de p (1 − p), la pente par laquelle le gradient remonte vers ce score. Appelée sur les scores bruts `[30.0, 0.0, 0.0]`, elle rend une probabilité presque égale à 1 et un gradient d'environ 1,87 × 10⁻¹³, numériquement mort ; appelée sur `[3.75, 0.0, 0.0]`, après division par √64 = 8, elle rend 0,955 et un gradient de 0,0429.

```python
"""Chapitre 6 — scaled dot-product attention, écrite comme la formule, terme à terme."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def produit(ligne, colonne):
    return sum(a * b for a, b in zip(ligne, colonne))


def softmax(logits):
    pic = max(logits)
    if pic == -math.inf:
        raise ValueError("ligne entièrement masquée : aucun token visible")
    expo = [math.exp(z - pic) for z in logits]
    total = sum(expo)
    return [e / total for e in expo]


def projeter(X, W):
    """X (n × d_model) · W (d_model × d) : chaque embedding x_i devient le vecteur x_i W."""
    if any(len(x) != len(W) for x in X):
        raise ValueError("chaque ligne de X doit avoir d_model = len(W) composantes")
    colonnes = [[W[l][c] for l in range(len(W))] for c in range(len(W[0]))]
    return [[produit(x, col) for col in colonnes] for x in X]


def masque_causal(n):
    """0 si j <= i (passé et présent), -inf si j > i (futur interdit)."""
    return [[0.0 if j <= i else -math.inf for j in range(n)] for i in range(n)]


def attention(Q, K, V, mettre_a_echelle=True, masque=None):
    """Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k) + M) V.

    Q, K : listes de vecteurs (un par token). V : le contenu qu'on moyenne. M : masque optionnel.
    """
    d_k = len(Q[0])
    echelle = math.sqrt(d_k) if mettre_a_echelle else 1.0
    poids = []
    scores_bruts = []
    for i, q in enumerate(Q):
        scores = [produit(q, k) / echelle for k in K]
        if masque is not None:
            scores = [s + m for s, m in zip(scores, masque[i])]
        scores_bruts.append([produit(q, k) for k in K])
        poids.append(softmax(scores))
    # Chaque ligne de sortie est Σ_j poids_ij × V_j
    sortie = []
    for ligne in poids:
        d_v = len(V[0])
        melange = [0.0] * d_v
        for j, poids_j in enumerate(ligne):
            for coord in range(d_v):
                melange[coord] += poids_j * V[j][coord]
        sortie.append(melange)
    return scores_bruts, poids, sortie


def variance_du_produit_scalaire(d_k, n_tirages=2000, graine=6):
    """Estime Var(q · k), avant et après division par sqrt(d_k), par Monte-Carlo.

    Chaque coordonnée de q et de k est tirée indépendamment, centrée, de variance 1 :
    ce sont les hypothèses sous lesquelles l'étape 32 démontre Var(q · k) = d_k.
    """
    rng = random.Random(graine)
    bruts = []
    for _ in range(n_tirages):
        q = [rng.gauss(0.0, 1.0) for _ in range(d_k)]
        k = [rng.gauss(0.0, 1.0) for _ in range(d_k)]
        bruts.append(produit(q, k))

    def variance(xs):
        m = sum(xs) / len(xs)
        return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)

    return variance(bruts), variance([s / math.sqrt(d_k) for s in bruts])


def main():
    tokens = ["il", "Paul", "dort"]

    print("=== 0. Projections : chaque embedding donne trois vecteurs q, k et v ===")
    X = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]  # embeddings one-hot de « il », « Paul », « dort »
    # d_k = 2. W_Q fait pointer la requête de « il » dans la direction de la clé de « Paul ».
    W_Q = [
        [2.0, 0.0],  # il
        [0.0, 1.0],  # Paul
        [0.0, 1.5],  # dort
    ]
    W_K = [
        [0.5, 0.0],  # il
        [2.0, 0.0],  # Paul
        [0.0, 2.0],  # dort
    ]
    W_V = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]
    Q, K, V = projeter(X, W_Q), projeter(X, W_K), projeter(X, W_V)
    assert Q == W_Q and K == W_K and V == W_V  # un embedding one-hot recopie la ligne de son token
    x_dense = [1.0, 0.0, 0.5]  # un embedding dense : 1 × « il » + 0,5 × « dort »
    q_dense = projeter([x_dense], W_Q)[0]
    print(f"  embedding dense {x_dense} → q = x W_Q = {q_dense}")
    assert q_dense == [2.0, 0.75]
    _, poids_sans_proj, _ = attention(X, X, X)
    prefere = [tokens[ligne.index(max(ligne))] for ligne in poids_sans_proj]
    print(f"  sans projection (Q = K = X), chaque token regarde surtout : {prefere}")
    assert prefere == tokens  # chacun se regarde lui-même (Cauchy-Schwarz, étape 14)

    print("\n=== 1. Scores, échelle, softmax, mélange des valeurs ===")
    scores, poids, sortie = attention(Q, K, V, mettre_a_echelle=True)
    print(f"  sqrt(d_k) = sqrt(2) = {math.sqrt(2):.4f}")
    for i, token in enumerate(tokens):
        print(f"  requête « {token} »")
        print(f"    QK^T brut     = {[round(s, 4) for s in scores[i]]}")
        print(f"    après /sqrt   puis softmax = {[round(p, 4) for p in poids[i]]}")
        print(f"    sortie        = {[round(v, 4) for v in sortie[i]]}")
        assert abs(sum(poids[i]) - 1.0) < 1e-12
        assert all(abs(o - p) < 1e-12 for o, p in zip(sortie[i], poids[i]))  # V = identité : sortie = poids
    # « il » · « Paul » = 4, « il » · « il » = 1, « il » · « dort » = 0.
    assert scores[0] == [1.0, 4.0, 0.0]
    assert poids[0][1] == max(poids[0])
    assert [round(p, 4) for p in poids[0]] == [0.1017, 0.8482, 0.0501]
    assert round(poids[2][2], 4) == 0.8066  # « dort » garde 80,7 % de son poids sur lui-même
    # La sortie de « il » doit ressembler surtout à la valeur de « Paul », qui est [0, 1, 0].
    assert sortie[0][1] > sortie[0][0]
    assert sortie[0][1] > sortie[0][2]

    print("\n=== 1 bis. Masque causal : un token ne regarde que ce qui le précède ===")
    _, poids_m, _ = attention(Q, K, V, masque=masque_causal(3))
    print(f"  ordre il, Paul, dort : poids de « il » = {[round(p, 4) for p in poids_m[0]]}")
    assert poids_m[0] == [1.0, 0.0, 0.0]  # « il » est en tête : il ne voit que lui-même
    ordre = [1, 2, 0]  # Paul, dort, il
    Qp, Kp, Vp = [Q[j] for j in ordre], [K[j] for j in ordre], [V[j] for j in ordre]
    _, poids_p, _ = attention(Qp, Kp, Vp, masque=masque_causal(3))
    print(f"  ordre Paul, dort, il : poids de « il » sur (Paul, dort, il) = {[round(p, 4) for p in poids_p[2]]}")
    assert all(abs(poids_p[2][a] - poids[0][ordre[a]]) < 1e-12 for a in range(3))
    for i in range(3):
        assert all(poids_p[i][j] == 0.0 for j in range(i + 1, 3))  # futur : poids exactement nul

    print("\n=== 2. Sans la division, la softmax sature et le gradient meurt ===")
    # Un produit scalaire de 30 en dimension 64 est un écart de 30/8 = 3,75 après échelle.
    d_k = 64
    brut = [30.0, 0.0, 0.0]
    al_echelle = [s / math.sqrt(d_k) for s in brut]

    def p_max_et_gradient(logits):
        p = softmax(logits)
        i = p.index(max(p))
        # ∂p_i/∂z_i = p_i (1 - p_i). C'est le signal d'apprentissage sur ce logit.
        return p[i], p[i] * (1.0 - p[i])

    p_sature, g_sature = p_max_et_gradient(brut)
    p_stable, g_stable = p_max_et_gradient(al_echelle)
    var_brute, var_echelle = variance_du_produit_scalaire(d_k)
    print(f"  d_k = {d_k} : Var(q·k) estimée sur 2 000 tirages = {var_brute:.1f} (théorie {d_k})")
    print(f"  après /sqrt(d_k) : variance estimée = {var_echelle:.3f} (théorie 1)")
    print(f"  sans échelle : p_max = {p_sature:.6f}   gradient p(1-p) = {g_sature:.3e}")
    print(f"  avec échelle : p_max = {p_stable:.6f}   gradient p(1-p) = {g_stable:.3e}")
    assert abs(var_brute / d_k - 1) < 0.1 and abs(var_echelle - 1) < 0.1
    assert abs(g_sature - 2 * math.exp(-30)) < 1e-15  # 1 − p ≈ 2 e^(−30) ≈ 1,87e-13
    assert round(p_stable, 3) == 0.955 and round(g_stable, 4) == 0.0429
    assert g_stable > 1000 * g_sature and round(math.log10(g_stable / g_sature), 1) == 11.4

    print("\n=== 3. Pourquoi la fenêtre de contexte coûte N² ===")
    print(f"  {'N tokens':>10}  {'cases de QK^T':>16}  {'mémoire fp16':>14}")
    memoires = []
    for n in (4_000, 32_000, 128_000):
        cases = n * n
        octets = cases * 2  # fp16 = 2 octets, une tête
        memoires.append(octets / 1e9)
        print(f"  {n:10,}  {cases:16,}  {octets / 1e9:10.2f} Go")
    assert memoires == [0.032, 2.048, 32.768]
    assert memoires[2] / memoires[1] == 16.0  # 4 fois plus de tokens : 16 fois plus de mémoire
    n = 100_000
    go = n * n * 2 / 1e9
    print(f"  À N = 100 000, une seule tête stocke {go:.0f} Go de scores. D'où FlashAttention,")
    print("  qui recalcule les blocs au lieu de garder la matrice N × N entière.")
    assert abs(go - 20.0) < 1e-9
    multiplications = n * n * (128 + 128)  # N² d_k pour QK^T, N² d_v pour la moyenne, tête de dimension 128
    assert multiplications == 2_560_000_000_000
    # Nombres des cas d'usage : 10 lots de N/10 tokens coûtent N²/10 ; 1 m² vaut environ 10,76 sqft
    n_paie, lots = 60_000, 10
    assert lots * (n_paie // lots) ** 2 * 10 == n_paie ** 2 and round(1 / 0.3048 ** 2, 2) == 10.76
    assert round(32_000 ** 2 * 2 / 1e9, 2) == 2.05
    print("  « il » regarde « Paul », et le facteur d'échelle garde un gradient non nul.")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== 0. Projections : chaque embedding donne trois vecteurs q, k et v ===
  embedding dense [1.0, 0.0, 0.5] → q = x W_Q = [2.0, 0.75]
  sans projection (Q = K = X), chaque token regarde surtout : ['il', 'Paul', 'dort']
…
  requête « il »
    QK^T brut     = [1.0, 4.0, 0.0]
    après /sqrt   puis softmax = [0.1017, 0.8482, 0.0501]
    sortie        = [0.1017, 0.8482, 0.0501]
…
  ordre il, Paul, dort : poids de « il » = [1.0, 0.0, 0.0]
  ordre Paul, dort, il : poids de « il » sur (Paul, dort, il) = [0.8482, 0.0501, 0.1017]
…
  d_k = 64 : Var(q·k) estimée sur 2 000 tirages = 65.2 (théorie 64)
  après /sqrt(d_k) : variance estimée = 1.019 (théorie 1)
  sans échelle : p_max = 1.000000   gradient p(1-p) = 1.872e-13
  avec échelle : p_max = 0.955077   gradient p(1-p) = 4.290e-02
…
  À N = 100 000, une seule tête stocke 20 Go de scores. D'où FlashAttention,
…
OK — toutes les vérifications sont passées.
```

Ce que vous reliez à un agent : la matrice N × N est la raison pour laquelle doubler le contexte ne double pas le calcul de l'attention, mais le quadruple. Le cache clé-valeur, lui, évite de refaire K et V pour les tokens déjà produits. La formule ci-dessus reste la même ; seul le nombre de lignes recalculées change.

## Squelette algorithmique

Le déroulé numérique de ce fichier part d'une matrice d'entrée X et montre chaque étape de l'auto-attention : projection en requêtes, clés et valeurs, scores, mise à l'échelle, masque, softmax, mélange des valeurs. Il mesure aussi pourquoi la division par √d_k est nécessaire.

```text
ALGORITHME AutoAttention
ENTRÉES : X (N × d_model), matrices de projection W_Q, W_K, W_V, option mise à l'échelle, option masque causal
SORTIE  : la sortie (N × d_v) et la matrice de poids (N × N)

  Q ← X × W_Q ; K ← X × W_K ; V ← X × W_V
  S ← Q × Kᵀ
  SI mise à l'échelle ALORS S ← S / √d_k
  SI masque causal ALORS S[i][j] ← −∞ pour tout j > i
  A ← softmax de chaque ligne de S
  RETOURNER A × V, A

ALGORITHME VarianceDuProduitScalaire (expérience)
ENTRÉES : d_k, nombre de tirages T
  POUR t DE 1 À T FAIRE  tirer q et k de coordonnées aléatoires centrées réduites ; garder q · k  FIN POUR
  RETOURNER la variance des T produits                        (proche de d_k)
```

**Complexité.** Les trois projections coûtent O(N × d_model × d_k) chacune, les scores O(N² × d_k), la softmax O(N²) et le mélange O(N² × d_v). La matrice des poids occupe N² nombres : en 16 bits, 2 N² octets, la formule de mémoire du fichier, soit 2 Go pour N = 32 768 et une seule tête. L'expérience de variance coûte O(T × d_k).

**Du squelette au code.** `projeter` calcule Q, K et V, `produit` les produits de matrices, `attention` enchaîne scores, mise à l'échelle optionnelle (`mettre_a_echelle`), masque optionnel (`masque`, construit par `masque_causal`) et `softmax`, et `variance_du_produit_scalaire` est l'expérience.

## Cas d'usage réels aux Émirats

Les volumes de tokens ci-dessous sont des ordres de grandeur illustratifs ; les nombres issus d'une formule sont vérifiés par le programme.

### Immobilier — un contrat off-plan où « il » renvoie au promoteur défini en page 1

Une agence et un promoteur actifs à Dubaï et Abu Dhabi utilisent un agent qui résume, pour les acheteurs, les contrats de vente off-plan : échéancier de paiement, pénalités de retard, conditions de résiliation. Dans ces contrats, « le Promoteur » et « l'Acheteur » sont définis en page 1, et la clause de résiliation de la page 14 écrit seulement « il pourra résilier si… ». Le mécanisme de ce chapitre explique comment un modèle peut relier ce « il » à sa définition, même éloignée de milliers de tokens : un modèle entraîné a pu apprendre des projections telles que la requête du pronom ressemble à la clé de son antécédent, et le lien se fait en une seule étape, sans transiter de proche en proche comme dans un réseau récurrent. Le masque causal dicte, lui, une règle de mise en page : les tokens d'une clause n'intègrent que ce qui les précède, donc l'agent place la section des définitions **avant** les clauses extraites, et non en annexe à la fin du prompt. Le contrat complet fait environ 30 000 tokens ; au lieu de l'envoyer en entier, l'agent envoie les définitions, l'échéancier et les trois clauses demandées, et rappelle que les frais de transfert DLD de 4 % de la valeur du bien s'ajoutent au prix. Sans cette préparation, le résumé peut attribuer au Promoteur un droit qui appartient à l'Acheteur, une erreur lourde sur un engagement de plusieurs millions d'AED. L'indicateur suivi est la part des résumés validés sans correction par le juriste de l'agence.

### Banque — la matrice N × N sur des serveurs internes

Une banque de détail de Dubaï exécute sur ses propres serveurs un modèle de langage ouvert, Jais ou Falcon par exemple, pour analyser les dossiers KYC, parce que sa politique interne interdit que les pièces des clients quittent son infrastructure. Un dossier complet — pièces d'identité, justificatifs de revenus, relevés — peut dépasser 32 000 tokens. Si la couche d'attention stockait la matrice des scores en entier, une seule tête d'une seule couche occuperait 32 000² × 2 octets, soit 2,05 Go en fp16 ; or un modèle compte des dizaines de têtes et de couches, et la mémoire du serveur serait saturée bien avant la fin du dossier. L'équipe vérifie donc que son moteur d'inférence utilise un noyau d'attention par blocs, du type FlashAttention, qui calcule exactement la même softmax sans jamais stocker la matrice N × N, et elle découpe les dossiers en sections traitées séparément quand le lien entre sections n'est pas nécessaire. Elle surveille aussi le cache clé-valeur, qui évite de recalculer K et V pendant la génération mais grandit avec chaque token, linéairement en N. Sans ces précautions, le service tombe en panne de mémoire sur les dossiers les plus longs, qui sont souvent les plus sensibles pour la lutte anti-blanchiment. L'indicateur suivi est le pic de mémoire GPU par dossier, avec le 95e percentile de latence, comparés au plafond fixé par l'exploitation.

### Assurance — « il roulait trop vite » : qui est « il » ?

Un assureur auto et santé fait extraire par un agent les faits d'une déclaration d'accident rédigée par l'assuré : « Le tiers a percuté l'assuré au rond-point ; il roulait trop vite. » Le pronom « il » a deux antécédents possibles, et rien dans la formule ne garantit qu'il sera relié au bon : dans le modèle simplifié, si la requête de « il » obtient des scores voisins pour « le tiers » et pour « l'assuré », sa sortie est un mélange à parts presque égales des deux valeurs, parce que l'attention fait une moyenne pondérée (point 3). L'agent ne doit donc pas deviner : son schéma de sortie impose des champs explicites, comme `conducteur_en_exces_de_vitesse` et `phrase_source`, et une règle renvoie le dossier au gestionnaire quand l'attribution n'est pas certaine. Le prompt place la consigne d'extraction après la déclaration, pour que les tokens de la consigne puissent intégrer toute la déclaration malgré le masque causal. Sans cette précaution, l'agent peut attribuer la faute au mauvais conducteur et proposer une indemnisation erronée, alors que l'assureur, supervisé par la CBUAE, doit pouvoir justifier chaque décision. L'indicateur suivi est le taux de dossiers renvoyés pour ambiguïté et, parmi les autres, le taux d'attributions correctes vérifiées par sondage.

### RH — découper un fichier de paie WPS sans perdre les totaux

Un cabinet RH multi-émirats prépare pour ses clients les fichiers de paie transmis par le WPS, et un agent contrôle chaque fichier avant envoi : salaires de base, indemnités, numéros d'Emirates ID au bon format (15 chiffres commençant par 784). Un fichier de 2 000 lignes représente environ 60 000 tokens. L'envoyer d'un bloc coûte N² en attention ; le découper en 10 lots de 200 lignes coûte 10 × (N/10)² = N²/10, soit dix fois moins, parce que chaque lot ne compare ses tokens qu'entre eux. Le découpage est sans risque pour le contrôle ligne à ligne, car chaque ligne de paie se vérifie seule ; en revanche, le total du fichier et la recherche de doublons d'Emirates ID entre lots ne peuvent plus être faits par le modèle, puisqu'aucun lot ne voit les autres, et ils sont confiés à un outil déterministe qui additionne et compare. Sans cette répartition, soit le contrôle coûte dix fois plus d'attention, soit un doublon entre deux lots passe inaperçu et un salaire est versé deux fois. L'indicateur suivi est le nombre d'anomalies détectées avant envoi, rapporté au nombre d'anomalies signalées après coup par les employeurs.

### BTP — un agent qui écrit du code de métré

Un groupe de construction qui mène de grands chantiers à Dubaï utilise un agent qui écrit de petits scripts Python de métré : surfaces de dalles en sqft, quantités de béton, montants hors taxes et TVA à 5 %. L'attention permet au modèle, quand il écrit la ligne 60, de relier directement une variable à sa définition de la ligne 10, par exemple `surface_sqft = longueur_ft * largeur_ft`, au lieu de faire transiter l'information de ligne en ligne. Le masque causal impose un ordre au prompt : le code généré ne s'appuie que sur ce qui le précède, donc l'agent place en tête les signatures des fonctions utilitaires, les unités (des sqft, pas des m²) et les conventions de l'entreprise, puis la demande. Comme la mémoire et le calcul de l'attention croissent comme le carré du nombre de tokens, l'agent ne fournit que les modules utiles plutôt que tout le dépôt. Chaque script produit est exécuté sur des cas de test qui vérifient, par exemple, que la TVA d'une facture de 12 000 AED hors taxes vaut 600 AED. Sans ces garde-fous, l'agent peut mélanger mètres et pieds, une erreur qui multiplie ou divise une surface par environ 10,76. L'indicateur suivi est la part des scripts qui passent tous leurs tests au premier essai.

## Pièges et limites

- **Confondre Q, K, V avec les embeddings.** Ce sont trois projections différentes des mêmes embeddings ; sans projections distinctes, chaque token se regarde lui-même (point 2).
- **Se tromper de masque.** Oublier le masque causal en entraînant un modèle génératif lui laisse voir le token qu'il doit prédire ; à l'inverse, un masque causal dans un encodeur de classification lui interdit des liens utiles vers la droite.
- **Croire que les noyaux par blocs suppriment le coût quadratique.** Ils suppriment le **stockage** de la matrice N × N, pas les N² produits scalaires à calculer.
- **Oublier le cache clé-valeur dans le budget mémoire.** Il évite de recalculer K et V, mais il grandit avec chaque token ; sur un long contexte, c'est souvent lui qui remplit la mémoire pendant la génération.
- **Lire une ligne de poids comme un raisonnement.** Un modèle réel empile des dizaines de couches de plusieurs têtes (étape 34) ; un poids élevé dans l'une d'elles n'explique pas à lui seul la réponse.

### Exercice feuille blanche

1. Sans regarder le code, écrire `projeter`, `masque_causal` et `attention`, puis retrouver les poids `[0.1017, 0.8482, 0.0501]` de « il ».
2. Prédire, puis vérifier : si la clé de « Paul » vaut `[1.0, 0.0]` au lieu de `[2.0, 0.0]`, que devient le poids de « Paul » pour « il » ? (Réponse : les scores deviennent `[1, 2, 0]` et le poids passe de 0,848 à 0,576.)
3. Trouver le bug : `return [[produit(x, ligne) for ligne in W] for x in X]` à la place de la dernière ligne de `projeter`. Que calcule cette version avec `W_Q` de taille 3 × 2, et pourquoi Python ne lève-t-il aucune erreur ? (Réponse : elle fait le produit scalaire de l'embedding avec les **lignes** de `W`, qui n'ont que deux éléments, et `zip` tronque en silence le troisième ; on obtient trois nombres au lieu de deux.)

## Pour aller plus loin

FlashAttention calcule l'attention exacte par blocs en recalculant ce qu'il faut au lieu de stocker la matrice N × N. Le cache clé-valeur garde K et V des tokens déjà produits ; les variantes MQA et GQA partagent ces clés et ces valeurs entre têtes pour le réduire (étape 34). Les encodeurs (classification, embeddings pour le RAG) utilisent l'attention sans masque, les décodeurs (génération) avec masque causal.

> Suite : [Génération : prefill, décodage, cache KV, TTFT et streaming](<33b-Generation-Prefill-Decode-Cache-KV-Streaming.md>) — étape 33 bis.
