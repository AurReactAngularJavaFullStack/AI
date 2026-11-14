# Étape 31 — Attention — Attention par produit scalaire mis à l'échelle (Scaled Dot-Product Attention)

> Étape 31 du parcours · Prérequis : [GraphRAG et mémoire en graphe](<../05-RAG/30g-RAG-GraphRAG-et-Memoire-en-Graphe.md>) · Suite : [Formules de l'attention et facteur d'échelle](<32-Attention-Formules-et-Role-de-Racine-dk.md>)

**Dossier :** 06-Attention-et-Transformer
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers
**Nom du fichier :** 31-Attention-Formule-Produit-Scalaire-Normalise.md

## Définition

L'attention est l'opération par laquelle un modèle de langage, pour chaque position du texte qu'il traite, fabrique un résumé de tout le contexte en donnant plus de poids aux positions qui lui « ressemblent ». Chaque position émet une **requête** (query) ; chaque position du contexte expose une **clé** (key) et porte une **valeur** (value). Le modèle mesure la ressemblance entre la requête et chaque clé par un produit scalaire (étape 14), divise ce score par √dₖ, transforme les scores en poids positifs de somme 1 avec la softmax (étape 2), puis renvoie la moyenne des valeurs pondérée par ces poids. Ces poids sont calculés par le modèle à partir du texte : le développeur d'agent ne les règle jamais ; il ne contrôle que ce qu'il met dans le contexte, sous quelle forme et dans quel ordre. La formule a été publiée par Vaswani et al. en 2017 (« Attention Is All You Need ») ; elle est au cœur de tous les modèles Transformer qui animent les agents.

## Rôle dans un agent

L'attention ne se code pas dans l'agent : elle s'exécute à l'intérieur du LLM, à chaque couche et pour chaque token, pendant l'étape **décider** de la boucle percevoir → décider → agir → observer. Elle explique pourtant les décisions que le développeur prend, lui, au moment d'assembler le prompt : quoi mettre dans le contexte (le retriever et la fusion des étapes 18 à 24 choisissent les passages), sous quelle forme (un résultat d'outil de trois lignes plutôt qu'un document brut de trente pages) et dans quel ordre (instructions, faits établis, question). Elle explique aussi deux contraintes de production. D'abord, chaque passage ajouté prend sa part d'un budget d'attention qui somme toujours à 1 (démonstration, point 1). Ensuite, le calcul et la mémoire de l'attention croissent comme le carré de la longueur du contexte (point 5). L'ingénierie de contexte — sélection, compaction, résumé, placement — existe pour gérer ces deux contraintes.

## Équation complète

Attention, forme matricielle, avec un masque M (la matrice nulle quand rien n'est interdit) :

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} + M \right) V
$$

Score mis à l'échelle de la requête i pour la clé j :

$$
s_{ij} = \frac{\mathbf{q}_i \cdot \mathbf{k}_j}{\sqrt{d_k}} + M_{ij} = \frac{1}{\sqrt{d_k}} \sum_{l=1}^{d_k} q_{il}\, k_{jl} + M_{ij}
$$

Poids d'attention, softmax de la ligne i :

$$
a_{ij} = \frac{e^{s_{ij}}}{\sum_{r=1}^{n_k} e^{s_{ir}}}
$$

Sortie de la requête i :

$$
\mathbf{o}_i = \sum_{j=1}^{n_k} a_{ij}\, \mathbf{v}_j
$$

Masque causal, utilisé par un modèle qui génère le texte de gauche à droite (la position i ne voit que le passé et elle-même) :

$$
M_{ij} = \begin{cases} 0 & \text{si } j \le i \\ -\infty & \text{si } j > i \end{cases}
$$

## Décryptage des symboles

$$
Q
$$

**Sens :** matrice des requêtes : une ligne 𝐪ᵢ par position qui cherche de l'information · **Type / plage :** (formule ci-dessous), réels · **Variable Python :** `Q`

$$
n_q \times d_k
$$

$$
K
$$

**Sens :** matrice des clés : une ligne 𝐤ⱼ par position du contexte · **Type / plage :** nₖ × dₖ, réels · **Variable Python :** `K`

$$
V
$$

**Sens :** matrice des valeurs : la ligne 𝐯ⱼ est le contenu transmis par la position j · **Type / plage :** nₖ × dᵥ, réels · **Variable Python :** `V`

$$
n_q,\quad n_k
$$

**Sens :** nombre de requêtes et de clés ; en auto-attention, (formule ci-dessous), la longueur du contexte en tokens · **Type / plage :** entiers ≥ 1 · **Variable Python :** `len(Q)`, `len(K)`

$$
n_q = n_k = n
$$

$$
d_k,\quad d_v
$$

**Sens :** largeur des requêtes et des clés ; largeur des valeurs · **Type / plage :** entiers ≥ 1 · **Variable Python :** `d_k`, `len(V[0])`

$$
K^\top
$$

**Sens :** transposée de K : la ligne j devient la colonne j · **Type / plage :** dₖ × nₖ · **Variable Python :** `transposer(K)`

$$
\sqrt{d_k}
$$

**Sens :** facteur d'échelle, justifié à l'étape 32 · **Type / plage :** réel > 0 · **Variable Python :** `echelle`

$$
M
$$

**Sens :** masque additif : 0 si la clé est autorisée, −∞ si elle est interdite · **Type / plage :** (formule ci-dessous), valeurs 0 ou −∞ · **Variable Python :** `masque`

$$
n_q \times n_k
$$

$$
s_{ij}
$$

**Sens :** score mis à l'échelle de la requête i pour la clé j · **Type / plage :** réel, ou −∞ · **Variable Python :** `scores[i][j]`

$$
a_{ij}
$$

**Sens :** poids d'attention ; chaque ligne de A somme à 1 · **Type / plage :** réel dans [0, 1] · **Variable Python :** `poids[i][j]`

$$
\mathbf{o}_i
$$

**Sens :** sortie de la requête i : moyenne des valeurs pondérée par les aᵢⱼ · **Type / plage :** vecteur de taille dᵥ · **Variable Python :** `sortie[i]`

L'ancienne version de ce fichier écrivait les symboles avec `\(…\)` et plaçait des blocs de formule centrés à l'intérieur des puces, ce qui cassait l'affichage ; ils sont désormais tous dans ce tableau.

## Démonstration

### 1. Chaque ligne de poids est une distribution : positive, de somme 1

On fixe une requête i. Chaque numérateur

$$
e^{s_{ij}}
$$

est strictement positif pour un score fini, parce que l'exponentielle est strictement positive ; le dénominateur est la somme de tous les numérateurs de la ligne. Donc :

$$
\sum_{j=1}^{n_k} a_{ij} = \frac{\sum_{j=1}^{n_k} e^{s_{ij}}}{\sum_{r=1}^{n_k} e^{s_{ir}}} = 1
$$

L'égalité tient parce que le numérateur et le dénominateur sont la même somme, écrite avec un autre nom d'indice. Chaque poids est de plus au plus égal à 1, parce qu'un terme positif ne dépasse pas la somme de tous les termes positifs. Ce sont les propriétés de la softmax démontrées à l'étape 2, appliquées ici ligne par ligne : chaque requête répartit un budget fixe, égal à 1, entre toutes les clés du contexte.

**Conséquence : la dilution.** Supposons qu'une clé utile ait une avance de score Δ sur n − 1 autres clés, qui ont toutes le score 0. Parce que e⁰ = 1, son poids vaut :

$$
a_{\text{utile}} = \frac{e^{\Delta}}{e^{\Delta} + (n - 1)}
$$

Avec Δ = 2 (donc e² ≈ 7,389), ce poids vaut 7,389 / 10,389 ≈ 0,7112 pour n = 4 clés, mais 7,389 / 46,389 ≈ 0,1593 pour n = 40. Pour garder le même poids avec 40 clés qu'avec 4, il faut garder le même rapport

$$
e^{\Delta}/(n - 1) ,
$$

parce que

$$
a_{\text{utile}} = 1 / \left(1 + (n-1)\,e^{-\Delta}\right) ;
$$

d'où

$$
\Delta' = 2 + \ln(39/3) = 2 + \ln 13 \approx 4{,}5649 .
$$

L'avance nécessaire croît comme le logarithme du nombre de concurrents. C'est tout ce que la formule implique : ajouter du contexte partage davantage un budget qui reste égal à 1. L'« oubli du milieu » (*lost in the middle*) est un autre phénomène : un effet **observé** sur des modèles entraînés, qui exploitent souvent moins bien une information placée au milieu d'un long contexte qu'au début ou à la fin ; il ne se déduit pas de cette équation (étape 32).

### 2. La sortie est une combinaison convexe des valeurs

Parce que les poids aᵢⱼ sont positifs et somment à 1, la sortie 𝐨ᵢ = ∑ⱼ aᵢⱼ 𝐯ⱼ est, par définition, une combinaison convexe (un barycentre) des lignes de V. On en déduit une borne coordonnée par coordonnée. Pour une coordonnée c :

$$
o_{ic} = \sum_{j} a_{ij}\, v_{jc} \le \sum_{j} a_{ij} \max_{r} v_{rc} = \max_{r} v_{rc}
$$

L'inégalité tient parce que chaque aᵢⱼ est positif ou nul : remplacer

$$
v_{jc}
$$

par le maximum de la colonne ne peut qu'augmenter chaque terme. La dernière égalité tient parce que ∑ⱼ aᵢⱼ = 1. Le même raisonnement avec le minimum donne

$$
o_{ic} \ge \min_r v_{rc} .
$$

L'attention ne fabrique donc aucune valeur hors de ce que le contexte contient : elle mélange. Deux cas particuliers en découlent. Si tous les scores d'une ligne sont égaux, chaque poids vaut 1/nₖ et la sortie est la moyenne simple des valeurs. Si un score domine tous les autres, les poids tendent vers 1 pour cette clé et vers 0 ailleurs (limite de la softmax, étape 2), et la sortie recopie presque sa valeur. Enfin, une contrainte linéaire respectée par toutes les valeurs l'est aussi par la sortie : dans l'exemple du point 7, chaque 𝐯ⱼ a des coordonnées de somme 1, donc

$$
o_1 + o_2 = \sum_j a_j (v_{j1} + v_{j2}) = \sum_j a_j = 1 .
$$

### 3. Un masque −∞ donne un poids exactement nul

Si Mᵢⱼ = −∞, alors sᵢⱼ = −∞ et le numérateur vaut

$$
e^{-\infty} = 0 ,
$$

parce que eˣ tend vers 0 quand x tend vers −∞ ; en arithmétique flottante IEEE 754, `math.exp(-math.inf)` renvoie exactement `0.0`. Le poids aᵢⱼ est donc exactement nul, et non seulement petit. Les autres poids de la ligne se renormalisent entre les seules clés autorisées : le dénominateur ne contient plus que leurs exponentielles, et la somme reste 1 (point 1). Il faut au moins une clé autorisée par ligne : si toutes valent −∞, le dénominateur est nul et le poids 0/0 n'est pas défini (une implémentation naïve renvoie NaN ; le code de ce fichier lève `ValueError`). Le masque causal autorise toujours la diagonale j = i : le premier token ne voit que lui-même, son poids vaut 1 et sa sortie recopie 𝐯₁.

### 4. L'ordre du contexte n'entre pas dans la formule

Le poids aᵢⱼ ne dépend que de 𝐪ᵢ, de 𝐤ⱼ et de la somme du dénominateur, qui ne dépend pas de l'ordre de ses termes. La sortie est une somme, et l'addition est commutative. Si l'on permute les couples (𝐤ⱼ, 𝐯ⱼ) — la même permutation pour les lignes de K et de V —, chaque 𝐨ᵢ reste donc identique. L'ordre n'atteint le modèle que par l'encodage de position ajouté aux tokens (étape 35) et par le masque causal. Conséquence pratique : « placer la clause importante juste avant la question » n'est pas dicté par cette équation ; c'est un choix qu'on valide en mesurant, sur le modèle visé, la justesse des réponses.

### 5. Le coût : n² (dₖ + dᵥ) multiplications et n² scores en mémoire

On compte les opérations, étage par étage :

- le produit Q Kᵀ remplit

$$
n_q \times n_k
$$

cases ; chacune est un produit scalaire de longueur dₖ, soit

$$
n_q n_k d_k
$$

multiplications ;
- la mise à l'échelle coûte

$$
n_q n_k
$$

divisions, et la softmax

$$
n_q n_k
$$

exponentielles ;
- le produit A V remplit

$$
n_q \times d_v
$$

cases ; chacune est une somme de nₖ produits, soit

$$
n_q n_k d_v
$$

multiplications.

En auto-attention,

$$
n_q = n_k = n ,
$$

et le nombre total de multiplications vaut :

$$
n_q\, n_k\, (d_k + d_v) = n^2 (d_k + d_v)
$$

La matrice des scores compte n² cases à garder en mémoire. Doubler le contexte multiplie ces deux coûts par 4, parce que (2n)² = 4n². Avec dₖ = dᵥ = 2, on trouve 9 × 4 = 36 multiplications pour n = 3 et 36 × 4 = 144 pour n = 6 : le compteur du code mesure exactement ces nombres. Pour n = 4 096 et dₖ = dᵥ = 128, on obtient 4 096² × 256 = 4 294 967 296 multiplications, environ 4,3 milliards, pour une seule tête d'une seule couche. C'est pour cela qu'un long contexte coûte en latence et en mémoire, et que la compaction paie au carré : diviser le contexte par r divise cette partie du calcul par r².

### 6. Le facteur √dₖ est une température

Diviser tous les scores d'une ligne par √dₖ revient exactement à appliquer la softmax à température T de l'étape 2 aux scores bruts zᵢⱼ = 𝐪ᵢ · 𝐤ⱼ :

$$
a_{ij} = \frac{e^{z_{ij} / T}}{\sum_{r} e^{z_{ir} / T}} \qquad \text{avec} \qquad T = \sqrt{d_k}
$$

L'étape 32 démontre pourquoi cette valeur : si les composantes de 𝐪 et 𝐤 sont indépendantes, de moyenne 0 et de variance 1, le score brut a une variance dₖ, et la division par √dₖ la ramène à 1, ce qui tient la softmax loin de la saturation. Ici, on retient l'effet : une température supérieure à 1 aplatit la distribution. Dans l'exemple du point 7, la softmax des scores bruts donnerait un poids de 0,4718 à la première clé ; avec le facteur √2, ce poids descend à 0,4307.

### 7. Exemple fait à la main (le code reprend ces nombres)

On reprend les matrices de l'ancien code NumPy de ce fichier : une requête 𝐪 = [1, 0], trois clés 𝐤₁ = [0,9 ; 0,1], 𝐤₂ = [0,1 ; 0,9], 𝐤₃ = [0,5 ; 0,5], des valeurs égales aux clés (V = K), et dₖ = 2, donc

$$
\sqrt{2} \approx 1{,}41421 .
$$

| Clé j | 𝐪 · 𝐤ⱼ | sⱼ = 𝐪 · 𝐤ⱼ / √2 | e^(sⱼ) | aⱼ = e^(sⱼ) / 4,38705 |
|---|---|---|---|---|
| 1 | 0,9 | 0,63640 | 1,88966 | 0,43074 |
| 2 | 0,1 | 0,07071 | 1,07327 | 0,24465 |
| 3 | 0,5 | 0,35355 | 1,42412 | 0,32462 |
| Somme |  |  | 4,38705 | 1 |

La sortie est la moyenne pondérée des valeurs :

$$
\mathbf{o} = 0{,}43074 \begin{bmatrix} 0{,}9 \\ 0{,}1 \end{bmatrix} + 0{,}24465 \begin{bmatrix} 0{,}1 \\ 0{,}9 \end{bmatrix} + 0{,}32462 \begin{bmatrix} 0{,}5 \\ 0{,}5 \end{bmatrix} = \begin{bmatrix} 0{,}38767 + 0{,}02447 + 0{,}16231 \\ 0{,}04307 + 0{,}22019 + 0{,}16231 \end{bmatrix} \approx \begin{bmatrix} 0{,}57444 \\ 0{,}42556 \end{bmatrix}
$$

Le « ≈ » vient des arrondis : avec les poids arrondis du tableau, la première somme donne 0,57445 ; avec les poids exacts, la première coordonnée vaut 0,574436, soit 0,57444 à cinq décimales. À la main, un écart d'une unité sur la dernière décimale est donc normal. On retrouve, arrondie à quatre décimales, la sortie `[[0.5744, 0.4256]]` de l'ancien code NumPy, et 0,57444 + 0,42556 = 1 comme l'annonçait le point 2. Chaque coordonnée reste bien entre le minimum (0,1) et le maximum (0,9) de sa colonne de V.

Avec le masque causal, on fait de l'auto-attention sur trois tokens dont les lignes sont ces mêmes vecteurs (Q = K = V = X, sans projection : les projections arrivent à l'étape 33). Le token 1 ne voit que lui-même : poids [1 ; 0 ; 0], sortie [0,9 ; 0,1]. Le token 2 voit les tokens 1 et 2 : ses scores valent

$$
0{,}18 / \sqrt{2} = 0{,}12728
$$

et

$$
0{,}82 / \sqrt{2} = 0{,}57983 ,
$$

le troisième vaut −∞ ; ses poids valent [0,3888 ; 0,6112 ; 0] et sa sortie [0,411 ; 0,589]. Le token 3 voit les trois tokens avec le même score brut, 0,5, donc des poids égaux à 1/3 et une sortie égale à la moyenne [0,5 ; 0,5].

## Effets et comportement

- **Des scores proches donnent des poids presque uniformes.** La sortie est alors la moyenne des valeurs : aucun passage ne ressort.
- **Un score qui domine concentre le poids.** La sortie recopie presque la valeur de cette clé ; c'est le comportement recherché quand une seule information compte.
- **Plus de contexte dilue chaque poids.** Le budget reste égal à 1 ; une clé utile doit avoir une avance qui croît comme ln n pour garder le même poids (point 1).
- **Le facteur √dₖ agit comme une température.** Sans lui, plus dₖ grandit, plus les poids tendent vers « tout sur une clé » et plus l'apprentissage se bloque (étape 32). L'ancienne formulation « les scores explosent » est juste sous l'hypothèse de variance de l'étape 32, pas pour n'importe quels vecteurs.
- **L'ordre n'entre que par l'encodage de position et le masque.** La formule seule est insensible à l'ordre des couples clé-valeur (point 4).
- **Le coût est quadratique.** Diviser le contexte par 2 divise par 4 le calcul et la mémoire de l'attention (point 5).

## Du symbole au code Python

$$
Q,\quad K,\quad V
$$

**Variable ou fonction :** `Q`, `K`, `V` : listes de listes de `float`

$$
K^\top
$$

**Variable ou fonction :** `transposer(K)`

$$
Q K^\top / \sqrt{d_k} + M
$$

**Variable ou fonction :** `scores_mis_a_echelle(Q, K, masque)`

**Symbole :** M causal · **Variable ou fonction :** `masque_causal(n)`

**Symbole :** softmax d'une ligne · **Variable ou fonction :** `softmax_stable(scores)`

$$
A V
$$

**Variable ou fonction :** `produit(poids, V)`

$$
\operatorname{Attention}(Q, K, V)
$$

**Variable ou fonction :** `attention(Q, K, V, masque)`, qui renvoie `(sortie, poids)`

### Déroulé, ligne par ligne

**`transposer(m)`**. `zip(*m)` regroupe les premiers éléments de chaque ligne, puis les deuxièmes. Pour `K = [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]]`, on obtient `[[0.9, 0.1, 0.5], [0.1, 0.9, 0.5]]` : deux lignes de trois, la forme dₖ × nₖ.

**`produit(a, b, compteur)`**. C'est le produit matriciel écrit avec trois boucles, comme on l'écrirait en Java.

- `n, d, m = len(a), len(b), len(b[0])` : pour 𝐪 (1 × 2) fois Kᵀ (2 × 3), on a `n = 1`, `d = 2`, `m = 3`.
- La garde vérifie que chaque ligne de `a` a bien `d` éléments ; sinon `ValueError`, plutôt qu'un résultat tronqué en silence par `zip`.
- La boucle intérieure accumule `a[i][l] * b[l][j]` : pour `i = 0` et `j = 0`, `1.0 * 0.9 + 0.0 * 0.1` donne 0,9.
- `compteur["multiplications"] += 1` compte chaque multiplication réellement faite : c'est ce qui permet au bloc 6 de **mesurer** le coût au lieu de le supposer.

**`softmax_stable(scores)`**. C'est la softmax de l'étape 2, sur une ligne.

- `m = max(scores)` : pour `[0.6364, 0.07071, 0.35355]`, `m = 0.6364`.
- `if m == -math.inf` : une ligne dont toutes les clés sont masquées n'a pas de poids définis ; on lève `ValueError` au lieu de renvoyer des NaN.
- `exps = [math.exp(s - m) for s in scores]` donne `[1.0, 0.56797, 0.75364]`, et non `[1.88966, …]` : le facteur commun e⁻⁰,⁶³⁶⁴ se simplifie dans la division (étape 2), donc les poids sont les mêmes et aucun `math.exp` ne peut déborder. Pour un score masqué, `s - m` vaut `-inf` et `math.exp(-inf)` renvoie exactement `0.0`.
- `return [e / total for e in exps]` : avec `total = 2.32161`, on obtient `[0.43074, 0.24465, 0.32462]`.

**`masque_causal(n)`**. Pour `n = 3`, elle renvoie `[[0.0, -inf, -inf], [0.0, 0.0, -inf], [0.0, 0.0, 0.0]]` : la condition `j <= i` autorise le passé et la diagonale.

**`scores_mis_a_echelle(Q, K, masque, compteur)`**. C'est Q Kᵀ / √dₖ + M.

- `d_k = len(Q[0])` vaut 2, et `echelle = math.sqrt(d_k)` vaut 1,41421.
- La garde refuse une clé qui n'a pas la largeur dₖ de la requête.
- La liste en compréhension divise chaque produit scalaire par `echelle` : 0,9 devient 0,6364.
- Si un masque est donné, on vérifie sa forme, puis `s + m` ajoute 0 (rien ne change) ou `-inf` (le score devient `-inf`).

**`attention(Q, K, V, masque, compteur)`**. Elle vérifie que `K` et `V` ont le même nombre de lignes, applique `softmax_stable` à chaque ligne de scores, puis renvoie `produit(poids, V)` et les poids, pour pouvoir les inspecter.

**`main()`**, bloc par bloc.

1. On calcule séparément les scores bruts `[0.9, 0.1, 0.5]`, les scores mis à l'échelle, les exponentielles `[1.88966, 1.07327, 1.42412]` de somme 4,38705, puis on appelle `attention`. Les `assert` reprennent chaque colonne du tableau du point 7, la sortie `[[0.57444, 0.42556]]`, et les poids sans facteur d'échelle `[0.4718, 0.212, 0.3162]` (point 6).
2. Pour chaque ligne de poids, on vérifie la somme 1 à `1e-12` près et la plage [0, 1] (point 1) ; pour chaque colonne de `V`, on vérifie que la sortie reste entre son minimum et son maximum (point 2), puis que `o_1 + o_2` vaut 1.
3. `scores_mis_a_echelle(X, X, masque_causal(3))` donne pour le token 2 `[0.12728, 0.57983, -inf]`. Les poids au-dessus de la diagonale sont comparés à `0.0` avec `==` : ils sont exactement nuls (point 3). Le token 3, aux trois scores égaux, reçoit `1/3` partout.
4. On réordonne les clés **et** les valeurs selon `[2, 0, 1]` : la sortie reste `[[0.5744, 0.4256]]` (point 4).
5. `softmax_stable([2.0] + [0.0] * (n - 1))` donne le poids de la clé utile : 0,7112 pour 4 clés, 0,1593 pour 40, et de nouveau 0,7112 pour 40 clés avec une avance de `2 + math.log(13)`, soit 4,5649 (point 1).
6. Le compteur passe dans les deux produits de `attention` : 36 multiplications pour 3 tokens, 144 pour 6, soit quatre fois plus pour un contexte deux fois plus long (point 5). Les `assert` suivants vérifient les ordres de grandeur cités dans les cas d'usage.
7. Une requête de largeur 3 face à des clés de largeur 2, puis une ligne entièrement masquée, doivent lever `ValueError` ; sinon `raise AssertionError` arrête le programme.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`transposer(m)`** — On peut l'imaginer comme un employé qui recopie un tableau en échangeant lignes et colonnes, pour que chaque clé, rangée en ligne, devienne une colonne prête à être multipliée par la requête : la fonction reçoit une matrice sous forme de liste de lignes, regroupe avec `zip(*m)` les premiers éléments de toutes les lignes, puis les deuxièmes, et renvoie ces groupes sous forme de listes. Pour K = [[0,9 ; 0,1], [0,1 ; 0,9], [0,5 ; 0,5]], elle renvoie deux lignes de trois nombres, la forme dₖ × nₖ dont `scores_mis_a_echelle` a besoin pour calculer Q Kᵀ.

**`produit(a, b, compteur)`** — C'est le calculateur à l'ancienne qui fait un produit matriciel avec trois boucles imbriquées, en notant chaque multiplication sur un carnet : la fonction reçoit deux matrices et un dictionnaire de comptage facultatif, lève `ValueError` si une ligne de la première n'a pas autant d'éléments que la seconde a de lignes, puis remplit chaque case (i, j) du résultat avec la somme des produits a[i][l] × b[l][j], en ajoutant 1 au compteur à chaque multiplication. Elle renvoie la matrice résultat ; pour la requête [1, 0] face à Kᵀ, elle donne les scores bruts 0,9, 0,1 et 0,5, et le compteur permet au point 6 de mesurer 36 multiplications pour 3 tokens et 144 pour 6.

**`softmax_stable(scores)`** — Cette fonction est l'arbitre qui transforme une ligne de scores en parts d'un même gâteau, toutes positives et de somme 1 : elle reçoit une liste de scores, cherche le maximum, lève `ValueError` si ce maximum vaut −∞, car une ligne entièrement masquée n'a aucune clé autorisée, puis retire le maximum à chaque score avant de prendre l'exponentielle, pour qu'aucun calcul ne déborde, et divise chaque exponentielle par leur somme. Elle renvoie les poids ; pour les scores 0,6364, 0,07071 et 0,35355, elle donne 0,43074, 0,24465 et 0,32462, et un score masqué reçoit un poids exactement nul, puisque exp(−∞) vaut 0.

**`masque_causal(n)`** — Elle dresse le règlement intérieur d'une conversation où personne n'a le droit de lire l'avenir : la fonction reçoit le nombre n de tokens et renvoie une matrice carrée n × n qui contient 0 sur et sous la diagonale, là où la colonne j est au plus égale à la ligne i, et −∞ au-dessus, là où un token regarderait un token futur. Ajoutée aux scores avant la softmax, elle force à zéro les poids interdits ; pour n = 3, le premier token ne voit que lui-même, le deuxième voit les deux premiers, et le troisième voit tout.

**`scores_mis_a_echelle(Q, K, masque, compteur)`** — C'est le juge qui note la compatibilité de chaque requête avec chaque clé, puis corrige l'échelle pour que les notes ne s'emballent pas quand la dimension grandit : la fonction reçoit les requêtes, les clés, un masque et un compteur facultatifs, lit la largeur dₖ des requêtes, lève `ValueError` si une clé n'a pas cette largeur, calcule Q Kᵀ avec `produit` et `transposer`, divise chaque score par √dₖ, puis, si un masque est donné, vérifie sa forme, lève `ValueError` s'il ne correspond pas, et l'ajoute case par case. Elle renvoie la matrice des scores ; avec dₖ = 2, le score brut 0,9 devient 0,6364, et pour le deuxième token de l'auto-attention masquée, la ligne vaut 0,12728, 0,57983 et −∞.

**`attention(Q, K, V, masque, compteur)`** — Cette fonction assemble toute la formule, comme un chef qui suit la recette pas à pas : elle reçoit les requêtes, les clés, les valeurs, un masque et un compteur facultatifs, lève `ValueError` si K et V n'ont pas le même nombre de lignes, calcule les scores mis à l'échelle et masqués, applique `softmax_stable` à chaque ligne pour obtenir les poids, puis multiplie ces poids par V avec `produit`. Elle renvoie le couple (sortie, poids), pour qu'on puisse inspecter les poids ; avec la requête [1, 0] et V = K, la sortie vaut [[0,57444 ; 0,42556]], une moyenne pondérée qui reste dans l'enveloppe des valeurs.

**`arrondir(m, n)`** — Cette petite fonction est le typographe qui prépare les matrices pour l'affichage et les comparaisons : elle reçoit une matrice et un nombre de décimales, 4 par défaut, et renvoie une nouvelle matrice où chaque nombre est arrondi à ce nombre de décimales, sans modifier l'original. `main` s'en sert pour imprimer les sorties et pour les comparer aux valeurs attendues sans buter sur les derniers chiffres des flottants, par exemple [[0,5744 ; 0,4256]] à quatre décimales et [[0,57444 ; 0,42556]] à cinq.

**`main()`** — Le chef d'orchestre déroule sept démonstrations : le calcul complet pour une requête et trois clés, des scores bruts aux poids et à la sortie, comparé aux poids plus concentrés obtenus sans le facteur √2, puis les deux propriétés démontrées, somme des poids égale à 1 et sortie dans l'enveloppe des valeurs. Il passe ensuite à l'auto-attention de trois tokens avec masque causal, dont les poids interdits sont exactement nuls, à l'invariance par permutation des couples (clé, valeur), à la dilution d'une clé utile, 0,7112 parmi 4 clés et 0,1593 parmi 40, au coût mesuré de 36 puis 144 multiplications, et enfin au refus par `ValueError` d'une requête trop large et d'une ligne entièrement masquée. La dernière ligne n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 31 — attention par produit scalaire mis à l'échelle, en Python pur (listes de listes)."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

Matrice = list[list[float]]


def transposer(m: Matrice) -> Matrice:
    """Kᵀ : la ligne j de K devient la colonne j."""
    return [list(colonne) for colonne in zip(*m)]


def produit(a: Matrice, b: Matrice, compteur: dict[str, int] | None = None) -> Matrice:
    """Produit matriciel (n × d) · (d × m) → (n × m), avec trois boucles explicites."""
    n, d, m = len(a), len(b), len(b[0])
    if any(len(ligne) != d for ligne in a):
        raise ValueError("dimensions incompatibles pour le produit matriciel")
    c = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s = 0.0
            for l in range(d):
                s += a[i][l] * b[l][j]
                if compteur is not None:
                    compteur["multiplications"] += 1
            c[i][j] = s
    return c


def softmax_stable(scores: list[float]) -> list[float]:
    """Softmax d'une ligne, en retirant le maximum (étape 2). Un score −inf reçoit un poids exactement nul."""
    m = max(scores)
    if m == -math.inf:
        raise ValueError("ligne entièrement masquée : aucune clé autorisée, les poids ne sont pas définis")
    exps = [math.exp(s - m) for s in scores]  # math.exp(-inf) vaut 0.0 exactement
    total = sum(exps)
    return [e / total for e in exps]


def masque_causal(n: int) -> Matrice:
    """M[i][j] = 0 si j <= i (passé et présent), −inf si j > i (futur interdit)."""
    return [[0.0 if j <= i else -math.inf for j in range(n)] for i in range(n)]


def scores_mis_a_echelle(Q: Matrice, K: Matrice, masque: Matrice | None = None,
                         compteur: dict[str, int] | None = None) -> Matrice:
    """S = Q Kᵀ / √d_k + M."""
    d_k = len(Q[0])
    if any(len(k) != d_k for k in K):
        raise ValueError("Q et K doivent avoir la même largeur d_k")
    echelle = math.sqrt(d_k)
    scores = [[s / echelle for s in ligne] for ligne in produit(Q, transposer(K), compteur)]
    if masque is not None:
        if len(masque) != len(scores) or any(len(lm) != len(K) for lm in masque):
            raise ValueError("le masque doit avoir la forme n_q × n_k")
        scores = [[s + m for s, m in zip(ls, lm)] for ls, lm in zip(scores, masque)]
    return scores


def attention(Q: Matrice, K: Matrice, V: Matrice, masque: Matrice | None = None,
              compteur: dict[str, int] | None = None) -> tuple[Matrice, Matrice]:
    """softmax(Q Kᵀ / √d_k + M) V, ligne par ligne. Renvoie (sortie, poids)."""
    if len(K) != len(V):
        raise ValueError("K et V doivent avoir le même nombre de lignes")
    poids = [softmax_stable(ligne) for ligne in scores_mis_a_echelle(Q, K, masque, compteur)]
    return produit(poids, V, compteur), poids


def arrondir(m: Matrice, n: int = 4) -> list[list[float]]:
    return [[round(x, n) for x in ligne] for ligne in m]


def main() -> None:
    print("1. Une requête, trois clés, d_k = 2 (V = K)")
    q = [[1.0, 0.0]]
    K = [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]]
    V = [ligne[:] for ligne in K]
    bruts = produit(q, transposer(K))[0]
    s = [x / math.sqrt(2) for x in bruts]
    exps = [math.exp(x) for x in s]
    sortie, poids = attention(q, K, V)
    print(f"  scores bruts q·k_j = {[round(x, 4) for x in bruts]}")
    print(f"  s_j = q·k_j / √2   = {[round(x, 5) for x in s]}")
    print(f"  e^(s_j)            = {[round(x, 5) for x in exps]} ; somme = {sum(exps):.5f}")
    print(f"  poids a_j          = {[round(p, 5) for p in poids[0]]}")
    print(f"  sortie Σ a_j·v_j   = {arrondir(sortie, 5)}")
    sans_echelle = softmax_stable(bruts)
    print(f"  sans le facteur √2 : poids = {[round(p, 4) for p in sans_echelle]} (plus concentrés)")
    assert [round(x, 10) for x in bruts] == [0.9, 0.1, 0.5]
    assert [round(x, 5) for x in s] == [0.6364, 0.07071, 0.35355]
    assert [round(x, 5) for x in exps] == [1.88966, 1.07327, 1.42412] and round(sum(exps), 5) == 4.38705
    assert [round(p, 5) for p in poids[0]] == [0.43074, 0.24465, 0.32462]
    assert [round(p, 4) for p in poids[0]] == [0.4307, 0.2446, 0.3246]
    assert arrondir(sortie, 5) == [[0.57444, 0.42556]] and arrondir(sortie) == [[0.5744, 0.4256]]
    assert [round(p, 4) for p in sans_echelle] == [0.4718, 0.212, 0.3162] and sans_echelle[0] > poids[0][0]

    print("2. Propriétés démontrées : somme 1 et enveloppe convexe")
    for ligne in poids:
        assert abs(sum(ligne) - 1.0) < 1e-12 and all(0.0 <= p <= 1.0 for p in ligne)
    for c in range(len(V[0])):
        colonne = [v[c] for v in V]
        assert min(colonne) <= sortie[0][c] <= max(colonne)
    assert abs(sum(sortie[0]) - 1.0) < 1e-12  # chaque v_j somme à 1, la moyenne pondérée aussi
    print(f"  Σ a_j = {sum(poids[0]):.12f} ; o_1 + o_2 = {sum(sortie[0]):.12f}")

    print("3. Auto-attention de 3 tokens avec masque causal (Q = K = V = X)")
    X = [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]]
    S = scores_mis_a_echelle(X, X, masque_causal(3))
    print(f"  scores du token 2 : {[round(x, 5) for x in S[1]]}")
    assert [round(x, 5) for x in S[1][:2]] == [0.12728, 0.57983] and S[1][2] == -math.inf
    sortie_m, poids_m = attention(X, X, X, masque_causal(3))
    for i, ligne in enumerate(poids_m):
        print(f"  token {i + 1} : poids = {[round(p, 4) for p in ligne]}  sortie = {[round(x, 4) for x in sortie_m[i]]}")
    for i in range(3):
        for j in range(i + 1, 3):
            assert poids_m[i][j] == 0.0  # exactement zéro, pas « presque » zéro
        assert abs(sum(poids_m[i]) - 1.0) < 1e-12
    assert poids_m[0] == [1.0, 0.0, 0.0] and sortie_m[0] == X[0]
    assert [round(p, 4) for p in poids_m[1]] == [0.3888, 0.6112, 0.0]
    assert [round(x, 4) for x in sortie_m[1]] == [0.411, 0.589]
    assert all(abs(p - 1 / 3) < 1e-12 for p in poids_m[2]) and arrondir(sortie_m[2:]) == [[0.5, 0.5]]

    print("4. Permuter les couples (clé, valeur) ne change pas la sortie")
    ordre = [2, 0, 1]
    sortie_p, _ = attention(q, [K[j] for j in ordre], [V[j] for j in ordre])
    assert all(abs(a - b) < 1e-12 for a, b in zip(sortie_p[0], sortie[0]))
    print(f"  ordre {ordre} : sortie = {arrondir(sortie_p)}")

    print("5. Dilution : une clé d'avance Δ parmi n clés")
    for n, delta, attendu in ((4, 2.0, 0.7112), (40, 2.0, 0.1593), (40, 2 + math.log(13), 0.7112)):
        p = softmax_stable([delta] + [0.0] * (n - 1))[0]
        assert abs(p - math.exp(delta) / (math.exp(delta) + n - 1)) < 1e-12 and round(p, 4) == attendu
        print(f"  n = {n:>2}, Δ = {delta:.4f} : poids de la clé utile = {p:.4f}")
    assert round(2 + math.log(13), 4) == 4.5649

    print("6. Coût : multiplications comptées dans les boucles")
    for n in (3, 6):
        compteur = {"multiplications": 0}
        Xn = [[0.1 * (i + 1), 0.2] for i in range(n)]
        attention(Xn, Xn, Xn, masque_causal(n), compteur)
        assert compteur["multiplications"] == n * n * 2 + n * n * 2  # n²·d_k + n²·d_v
        print(f"  n = {n} tokens, d_k = d_v = 2 : {compteur['multiplications']} multiplications")
    assert 4096 * 4096 * (128 + 128) == 4_294_967_296
    # ordres de grandeur repris dans les cas d'usage : un contexte divisé par r divise ce calcul par r²
    assert (30_000 // 300) ** 2 == 10_000 and (8_000 // 800) ** 2 == 100 and (120_000 // 4_000) ** 2 == 900
    assert (60 // 5) ** 2 == 144
    assert round(120_000 ** 2 * 256 / 1e12, 1) == 3.7
    print(f"  n = 4096, d_k = d_v = 128 : {4096 * 4096 * 256:_} multiplications par tête et par couche")

    print("7. Entrées invalides refusées")
    for args in (([[1.0, 0.0, 0.0]], K, V, None), (q, K, V, [[-math.inf, -math.inf, -math.inf]])):
        try:
            attention(*args)
        except ValueError as e:
            print(f"  ValueError : {e}")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Une requête, trois clés, d_k = 2 (V = K)
  s_j = q·k_j / √2   = [0.6364, 0.07071, 0.35355]
  e^(s_j)            = [1.88966, 1.07327, 1.42412] ; somme = 4.38705
  poids a_j          = [0.43074, 0.24465, 0.32462]
  sortie Σ a_j·v_j   = [[0.57444, 0.42556]]
  sans le facteur √2 : poids = [0.4718, 0.212, 0.3162] (plus concentrés)
…
  scores du token 2 : [0.12728, 0.57983, -inf]
  token 1 : poids = [1.0, 0.0, 0.0]  sortie = [0.9, 0.1]
  token 2 : poids = [0.3888, 0.6112, 0.0]  sortie = [0.411, 0.589]
  token 3 : poids = [0.3333, 0.3333, 0.3333]  sortie = [0.5, 0.5]
…
  n =  4, Δ = 2.0000 : poids de la clé utile = 0.7112
  n = 40, Δ = 2.0000 : poids de la clé utile = 0.1593
  n = 40, Δ = 4.5649 : poids de la clé utile = 0.7112
…
  n = 4096, d_k = d_v = 128 : 4_294_967_296 multiplications par tête et par couche
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : l'attention n'est qu'une moyenne pondérée dont les poids somment à 1. Tout ce qu'un agent en subit — la dilution quand le contexte grossit, le coût qui croît au carré — se lit directement dans la formule et se vérifie en quelques lignes.

### La même chose avec NumPy

L'ancien bloc de ce fichier, présenté comme un « code Python complet », dépendait de NumPy et ne vérifiait rien. Le voici en extrait, complété du masque ; il calcule les mêmes nombres que le bloc exécutable ci-dessus.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(x)`** — C'est la même opération que `softmax_stable`, confiée à une machine qui traite toutes les lignes d'un coup au lieu de les prendre une à une : la fonction reçoit un tableau NumPy, retire à chaque ligne son maximum le long du dernier axe pour éviter tout débordement, prend l'exponentielle, puis divise chaque élément par la somme de sa ligne, et renvoie le tableau des poids, chaque ligne sommant à 1. Contrairement à la version du programme, elle ne vérifie pas le cas d'une ligne entièrement masquée, qui produirait ici des valeurs indéfinies au lieu d'une erreur explicite.

**`scaled_dot_product_attention(Q, K, V, masque)`** — Elle réunit toute la formule en trois lignes vectorisées : la fonction reçoit les tableaux des requêtes, des clés et des valeurs et un masque facultatif, lit la largeur dₖ sur le dernier axe des requêtes, calcule Q Kᵀ divisé par √dₖ avec l'opérateur `@`, ajoute le masque s'il est fourni, applique `softmax` puis multiplie le résultat par V. Elle renvoie la matrice de sortie, environ [[0,5744 ; 0,4256]] pour la requête [1, 0], et, avec le masque triangulaire construit par `np.triu`, les mêmes lignes que l'auto-attention masquée du programme ; l'extrait n'est pas exécuté par le harnais, puisqu'il demande NumPy.

```python
# [extrait] — version NumPy, non exécutée par le harnais (NumPy n'est pas dans la bibliothèque standard)
import numpy as np


def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))   # stabilité : on retire le maximum de chaque ligne
    return e_x / e_x.sum(axis=-1, keepdims=True)


def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray, masque=None) -> np.ndarray:
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)
    if masque is not None:
        scores = scores + masque                           # 0 ou -np.inf
    return softmax(scores) @ V


Q = np.array([[1.0, 0.0]])
K = np.array([[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]])
V = K.copy()
print(scaled_dot_product_attention(Q, K, V))              # environ [[0.5744 0.4256]]
masque = np.triu(np.full((3, 3), -np.inf), k=1)           # -inf strictement au-dessus de la diagonale, 0 ailleurs
print(scaled_dot_product_attention(K, K, K, masque))      # mêmes lignes que le bloc 3 du programme
```

## Squelette algorithmique

L'attention transforme trois matrices (requêtes, clés, valeurs) en une nouvelle représentation de chaque position. L'algorithme suit exactement la formule, ligne par ligne, avec deux précautions : soustraire le maximum avant l'exponentielle, et appliquer le masque avant la softmax.

```text
ALGORITHME AttentionParProduitScalaireNormalisé
ENTRÉES : Q (n_q × d_k), K (n_k × d_k), V (n_k × d_v), masque M (n_q × n_k, valeurs 0 ou −∞) facultatif
SORTIE  : O (n_q × d_v) et les poids A (n_q × n_k)

  POUR i DE 1 À n_q FAIRE
      POUR j DE 1 À n_k FAIRE
          s[i][j] ← (Σₗ Q[i][l] × K[j][l]) / √d_k + M[i][j]
      FIN POUR
      m ← maxⱼ s[i][j]                                   (stabilité : exp(−∞) = 0, exp(0) = 1)
      POUR j FAIRE  e[j] ← exp(s[i][j] − m)  FIN POUR
      POUR j FAIRE  A[i][j] ← e[j] / Σ e  FIN POUR       (chaque ligne de A somme à 1)
      POUR c DE 1 À d_v FAIRE
          O[i][c] ← Σⱼ A[i][j] × V[j][c]
      FIN POUR
  FIN POUR
  RETOURNER O, A

MASQUE CAUSAL (génération) : M[i][j] ← 0 si j ≤ i, −∞ si j > i     (un token ne lit pas le futur)
```

**Complexité.** Les scores coûtent n_q × n_k × d_k multiplications, la sortie n_q × n_k × d_v : O(n² d) en self-attention, où n_q = n_k = n. La matrice A occupe O(n²) en mémoire, ce qui explique le coût des longs contextes. La softmax ligne par ligne coûte O(n²). Le compteur de multiplications du programme vérifie ces nombres sur l'exemple.

**Du squelette au code.** `scores_mis_a_echelle` calcule s avec `produit` et `transposer`, puis ajoute le masque ; `softmax_stable` est la ligne « m, e, A » ; `attention` enchaîne les deux et fait le produit A × V ; `masque_causal` construit M. La version NumPy plus bas fait le même calcul avec des opérations matricielles.

## Cas d'usage réels aux Émirats

Dans chaque cas, l'équipe ne règle aucun poids d'attention : elle n'en contrôle aucun. Elle choisit ce qui entre dans le contexte, sous quelle forme et dans quel ordre. Les volumes de tokens et les montants non réglementaires sont illustratifs.

### Assurance — une clause de franchise noyée parmi 40 messages

Un assureur auto et santé confie à un agent le suivi des sinistres : pour chaque dossier, le prompt contient les conditions particulières du contrat et tout l'historique des échanges avec l'assuré, devis de garages, descriptions de photos et relances compris. Au 41e message, l'assuré demande combien il sera remboursé pour son pare-brise, et la réponse dépend d'une franchise de 500 AED mentionnée une seule fois, au troisième message. Dans le modèle simplifié de la démonstration, une phrase qui n'a qu'une avance de score Δ = 2 garde un poids de 0,71 face à 3 concurrentes, mais seulement 0,16 face à 39 : la formule ne promet rien d'autre qu'un budget égal à 1, partagé entre davantage de candidats. L'équipe change donc le contexte : un outil `conditions_contrat` renvoie la franchise, le plafond et la règle de vétusté du contrat, placés dans un bloc « Faits établis du dossier » juste avant la question, et les 37 messages intermédiaires sont compactés en un résumé de dix lignes. L'emplacement de ce bloc n'est pas dicté par l'équation, qui ignore l'ordre (point 4) : il est retenu parce qu'il donne les meilleures réponses sur le jeu d'évaluation de l'équipe, et revérifié à chaque changement de modèle. Sans ce travail, l'agent peut promettre par écrit un remboursement intégral, et l'assureur, supervisé par la CBUAE, doit ensuite revenir sur une réponse donnée à un client. L'indicateur suivi est la part des réponses qui citent la bonne franchise, mesurée sur 200 dossiers rejoués à chaque modification du prompt.

### Banque — un résultat d'outil plutôt que six mois de relevés

Une banque de détail de Dubaï utilise un agent qui prépare, pour les conseillers, la recevabilité des demandes de prêt personnel. Le premier prototype collait dans le prompt six mois de relevés de compte, environ 30 000 tokens, et demandait au modèle de repérer lui-même les mensualités en cours parmi des milliers de lignes de transactions. La règle à appliquer tient pourtant en une ligne : toutes les mensualités, y compris la nouvelle, ne doivent pas dépasser 50 % du salaire (règle de la CBUAE). La version de production calcule hors du modèle : un outil extrait les prélèvements récurrents, calcule le ratio — par exemple (6 000 + 5 558,32) / 40 000 ≈ 28,9 % — et ne place dans le contexte que trois lignes : le ratio, le plafond et la conclusion. Le contexte passe d'environ 30 000 à environ 300 tokens ; comme le calcul de l'attention croît comme n² (point 5), cette partie du calcul est divisée par 100² = 10 000, et il ne reste plus de transactions parasites pour diluer les poids. Sans cette compaction, l'agent peut manquer un crédit auto prélevé une fois par mois et déclarer recevable un dossier qui dépasse le plafond. L'indicateur suivi est le nombre d'écarts entre le ratio écrit par l'agent et celui que recalcule le contrôle de conformité, avec un objectif de zéro.

### Immobilier — cinq comparables plutôt que soixante

Une agence et un promoteur actifs à Dubaï et Abu Dhabi utilisent un agent qui rédige une estimation de prix pour un appartement off-plan. Le retriever renvoie 60 transactions enregistrées au DLD dans le quartier ; toutes les copier dans le prompt fait partager le budget d'attention de chaque token entre 60 blocs, dont la plupart concernent d'autres tours, d'autres étages ou d'autres années. L'équipe garde les cinq meilleures après fusion des classements (étapes 23 et 24), les présente dans un tableau homogène — prix en AED/sqft, date, étage, vue, surface en sqft — et ajoute une ligne qui rappelle les frais de transfert DLD de 4 % de la valeur du bien, à intégrer au budget de l'acheteur. Passer de 60 à 5 blocs ne garantit pas que le modèle donnera le plus de poids au meilleur comparable, puisque les poids restent calculés par le modèle, mais il ne reste plus que des candidats pertinents entre lesquels répartir la masse d'attention, et le calcul de l'attention sur cette partie du prompt est divisé par 12² = 144. Sans ce tri, l'agent peut citer comme référence une vente ancienne dans une autre tour et produire une estimation éloignée du marché. L'indicateur suivi est l'écart médian entre l'estimation de l'agent et le prix final des transactions conclues, revu chaque mois.

### RH — un bloc d'état plutôt qu'un historique de 40 messages

Un cabinet RH multi-émirats accompagne chaque recrutement par un agent : contrat enregistré auprès du MOHRE, visite médicale, demande d'Emirates ID, inscription au WPS pour le versement des salaires. Au bout de quelques semaines, la conversation compte une quarantaine de messages, et le statut de chaque démarche a changé plusieurs fois : « visite médicale à planifier », puis « planifiée », puis « faite ». Si ces versions successives restent dans l'historique, elles obtiennent des scores voisins et se partagent le poids presque à parts égales : la sortie mélange alors « à planifier » et « faite », exactement comme le token 3 de l'exemple fait la moyenne de trois valeurs (point 2). L'équipe remplace l'historique brut par un bloc d'état unique, mis à jour par les outils après chaque démarche et réinjecté à chaque tour, avec une seule ligne par démarche et la date de sa dernière vérification. Cette compaction réduit aussi le coût : passer de 8 000 à 800 tokens d'historique divise par 100 le calcul d'attention sur cette partie, parce que (8 000 / 800)² = 100. Sans le bloc d'état, l'agent peut annoncer au candidat une visite « à planifier » alors qu'elle a eu lieu, ou l'inverse, et retarder la délivrance du visa. L'indicateur suivi est la part des réponses de statut conformes au système de suivi du cabinet, contrôlée sur un échantillon chaque semaine.

### Crypto — des journaux de liquidité condensés avant l'analyse

Une plateforme d'actifs virtuels agréée par la VARA fait analyser par un agent les alertes de liquidité de ses pools, avec pour consigne de proposer une action à l'astreinte en quelques minutes. Les journaux bruts des dernières 24 heures représentent environ 120 000 tokens, dont l'immense majorité décrit des opérations normales. Les envoyer tels quels coûte cher en latence — pour une seule tête d'une seule couche, n² (dₖ + dᵥ) vaut environ 3,7 × 10¹² multiplications avec n = 120 000 et dₖ = dᵥ = 128 — et noie les quelques lignes anormales parmi des milliers de lignes banales. L'équipe ajoute une étape déterministe avant le modèle : un outil agrège les journaux par pool et par tranche de cinq minutes et ne garde que les dépassements de seuil, ce qui ramène le contexte à environ 4 000 tokens, soit (120 000 / 4 000)² = 900 fois moins de calcul d'attention. Le modèle reçoit alors un tableau court où chaque ligne est un incident candidat, au lieu d'un fil de journaux. Sans cette étape, l'analyse peut arriver après la fenêtre de réaction prévue par la procédure interne, donc après l'incident. L'indicateur suivi est le 95e percentile de la latence d'analyse, avec la part des incidents réels correctement remontés.

### BTP — les trois clauses utiles d'un contrat de sous-traitance

Un groupe de construction qui mène de grands chantiers à Dubaï fait vérifier par un agent les factures de ses sous-traitants avant paiement. Chaque facture doit être confrontée au contrat de sous-traitance, un document d'environ 80 pages dont seules quelques clauses comptent pour ce contrôle : le taux de retenue de garantie, la révision des prix et l'application de la TVA à 5 %. Mettre le contrat entier dans le prompt à côté de la facture place ces clauses au milieu de centaines de paragraphes juridiques qui se partagent le même budget d'attention. L'équipe découpe le contrat en clauses indexées, récupère par recherche hybride (étape 23) les clauses citées par la facture et les place, avec leur numéro, juste au-dessus des lignes à contrôler. L'agent appelle ensuite un outil pour calculer la retenue et la TVA attendues — par exemple 600 AED de TVA sur 12 000 AED hors taxes — et signale tout écart, au lieu de faire le calcul de tête. Sans cette sélection, une facture qui oublie la retenue de garantie peut passer le contrôle, et le groupe paie un montant qu'il devra ensuite récupérer auprès du sous-traitant. L'indicateur suivi est la part des écarts signalés par l'agent puis confirmés par l'audit interne.

## Pièges et limites

- **Croire qu'on règle les poids d'attention.** Le développeur d'agent ne choisit ni Q, ni K, ni les poids : il choisit le texte du contexte. Ses leviers sont la sélection (retriever), la forme (résultat d'outil compact), la compaction (résumé) et l'ordre, chacun validé par une mesure.
- **Lire les poids comme une explication.** Un poids élevé dans une tête d'une couche ne prouve pas que ce passage a causé la réponse : un modèle empile des dizaines de couches de plusieurs têtes (étape 34), et la sortie de l'attention passe encore par d'autres transformations.
- **Mal construire le masque.** Écrire `j < i` au lieu de `j <= i` masque aussi la diagonale : le premier token n'a plus aucune clé autorisée et sa ligne vaut 0/0. À l'inverse, oublier le masque à l'entraînement laisse le modèle lire le token qu'il doit prédire.
- **Oublier de retirer le maximum.** `math.exp(1000)` lève `OverflowError` en Python, et NumPy renvoie `inf`, puis `inf / inf` donne `nan`. Retirer le maximum ne change pas les poids (étape 2) et rend le calcul sûr.
- **Confondre fenêtre maximale et fenêtre utile.** Un modèle qui accepte des centaines de milliers de tokens ne les exploite pas tous également ; et le calcul de l'attention croît comme n², même si la facture d'une API est, elle, proportionnelle au nombre de tokens.

### Exercice feuille blanche

1. Sans regarder le code, écrire `softmax_stable`, puis `attention` pour une seule requête, et retrouver les poids `[0.4307, 0.2446, 0.3246]` de l'exemple.
2. Prédire, puis vérifier : avec 𝐪 = [0, 1] au lieu de [1, 0], que deviennent les poids et la sortie ? (Réponse : les rôles de 𝐤₁ et 𝐤₂ s'échangent, les poids valent `[0.2446, 0.4307, 0.3246]` et la sortie `[0.4256, 0.5744]`.)
3. Trouver le bug : `[[0.0 if j < i else -math.inf for j in range(n)] for i in range(n)]`. Que se passe-t-il pour le premier token ? (Réponse : sa diagonale est masquée, toute sa ligne vaut `-inf` et `softmax_stable` lève `ValueError`.)

## Pour aller plus loin

FlashAttention (Dao et al., 2022) calcule exactement la même softmax par blocs, sans jamais stocker la matrice n × n : la mémoire devient linéaire en n, le calcul reste en n². Les noyaux optimisés sautent aussi les blocs entièrement masqués, ce qui épargne environ la moitié du calcul en attention causale. Le cache KV, utilisé pendant la génération, évite de recalculer les clés et les valeurs des tokens déjà produits. Les attentions à fenêtre glissante ou creuses ne calculent qu'une partie des n² scores, au prix d'une perte d'information sur les positions lointaines.

> Suite : [Formules de l'attention et facteur d'échelle](<32-Attention-Formules-et-Role-de-Racine-dk.md>) — étape 32.
