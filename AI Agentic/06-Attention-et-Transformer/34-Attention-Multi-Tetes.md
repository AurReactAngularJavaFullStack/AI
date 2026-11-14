# Étape 34 — Multi-Head Attention — Attention Multi-Têtes pour la Compréhension Parallèle

> Étape 34 du parcours · Prérequis : [Génération : prefill, décodage, cache KV, TTFT et streaming](<33b-Generation-Prefill-Decode-Cache-KV-Streaming.md>) · Suite : [Encodage de position](<35-Encodage-de-Position.md>)

## Définition

L'attention multi-têtes découpe la largeur du modèle,

$$
d_{model} ,
$$

en h **têtes** de largeur

$$
d_k = d_{model}/h .
$$

Chaque tête projette les embeddings avec ses propres matrices, calcule sa propre attention (étapes 31 à 33) dans son petit espace, et produit sa propre sortie. Les h sorties sont ensuite recollées côte à côte (concaténation), puis mélangées par une dernière matrice, Wᴼ, qui ramène le résultat à la largeur

$$
d_{model} .
$$

Une seule tête ne fait qu'une moyenne pondérée par token ; plusieurs têtes posent plusieurs questions en parallèle — « de quoi parle-t-on ? », « qu'arrive-t-il à cette chose ? » — et gardent leurs réponses séparées. Le nombre de paramètres et le nombre de multiplications ne dépendent pas de h : on partage la même largeur entre plusieurs questions.

## Rôle dans un agent

L'attention multi-têtes s'exécute dans chaque couche du LLM, pendant l'étape **décider** de la boucle percevoir → décider → agir → observer. Le développeur d'agent ne l'écrit pas, mais il en manipule les conséquences dès qu'il choisit, héberge ou adapte un modèle : la mémoire des poids (

$$
4 d_{model}^2
$$

paramètres par couche), le coût de calcul selon la longueur des requêtes (projections linéaires en n, attention quadratique en n), et la taille du cache clé-valeur qui fixe le nombre de sessions simultanées. Il les rencontre aussi quand il porte un modèle vers un autre moteur d'inférence : les biais ajoutés par défaut, la largeur des têtes et le masque doivent correspondre exactement à la formule.

## Équation complète

En auto-attention, les trois entrées valent les embeddings X, et l'on écrit MultiHead(X). L'article d'origine écrit MultiHead(Q, K, V), où Q, K et V désignent les **entrées** avant projection ; l'ancienne version de ce fichier mélangeait les deux notations (elle projetait X, puis écrivait MultiHead(Q, K, V)). Ici, Q, K et V désignent toujours des matrices déjà projetées.

Sortie de la tête i, pour i = 1, …, h :

$$
\text{head}_i = \text{softmax}\left( \frac{(X W_i^Q)(X W_i^K)^\top}{\sqrt{d_k}} + M \right) X W_i^V
$$

Attention multi-têtes :

$$
\text{MultiHead}(X) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)\, W^O
$$

Dimensions :

$$
W_i^Q, W_i^K \in \mathbb{R}^{d_{model} \times d_k}, \qquad W_i^V \in \mathbb{R}^{d_{model} \times d_v}, \qquad W^O \in \mathbb{R}^{h d_v \times d_{model}}
$$

$$
d_k = d_v = \frac{d_{model}}{h}
$$

Nombre de paramètres d'une couche, sans biais :

$$
P = 4\, d_{model}^2
$$

Coût en multiplications de l'attention proprement dite, puis des quatre projections :

$$
C_{attention} = h\, n^2 (d_k + d_v) = 2\, n^2 d_{model}
$$

$$
C_{projections} = 4\, n\, d_{model}^2
$$

## Décryptage des symboles

$$
X
$$

**Sens :** embeddings, une ligne par token · **Type / plage :** voir le bloc ci-dessous · **Variable Python :** `X`

$$
n \times d_{model}
$$

$$
n
$$

**Sens :** nombre de tokens · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(X)`

$$
d_{model}
$$

**Sens :** largeur du modèle · **Type / plage :** entier, multiple de h · **Variable Python :** `d_model`

$$
h
$$

**Sens :** nombre de têtes · **Type / plage :** entier ≥ 1 qui divise (formule ci-dessous) · **Variable Python :** `h`

$$
d_{model}
$$

$$
d_k,\quad d_v
$$

**Sens :** largeur d'une tête : (formule ci-dessous) · **Type / plage :** entier ≥ 1 · **Variable Python :** `d_k`

$$
d_{model}/h
$$

$$
W_i^Q,\quad W_i^K,\quad W_i^V
$$

**Sens :** projections propres à la tête i · **Type / plage :** voir le bloc ci-dessous · **Variable Python :** `bande(W_Q, i, d_k)`…

$$
d_{model} \times d_k
$$

$$
W_Q,\quad W_K,\quad W_V
$$

**Sens :** les h petites matrices posées côte à côte · **Type / plage :** voir le bloc ci-dessous · **Variable Python :** `W_Q`, `W_K`, `W_V`

$$
d_{model} \times d_{model}
$$

$$
\text{head}_i
$$

**Sens :** sortie de la tête i · **Type / plage :** n × dᵥ · **Variable Python :** `tetes[i]`

$$
\text{Concat}
$$

**Sens :** recolle les h sorties côte à côte · **Type / plage :** n × h dᵥ · **Variable Python :** `concatener(tetes)`

$$
W^O
$$

**Sens :** projection de sortie, qui mélange les têtes · **Type / plage :** voir le bloc ci-dessous · **Variable Python :** `W_O`

$$
h d_v \times d_{model}
$$

$$
M
$$

**Sens :** masque causal, construit une fois et partagé par toutes les têtes · **Type / plage :** n × n, valeurs 0 ou −∞ · **Variable Python :** `masque_causal(n)`

$$
P
$$

**Sens :** nombre de paramètres des quatre matrices · **Type / plage :** entier · **Variable Python :** `nombre_parametres(d_model)`

## Démonstration

### 1. Couper une grande projection en bandes revient à appliquer h petites matrices

On pose

$$
W_Q = [\,W_1^Q \mid W_2^Q \mid \cdots \mid W_h^Q\,]
$$

Les h petites matrices côte à côte, chacune de dₖ colonnes. Le coefficient

$$
(X W_Q)_{rc} = \sum_l x_{rl}\, (W_Q)_{lc}
$$

ne dépend que de la colonne c de

$$
W_Q ,
$$

parce qu'un produit matriciel associe chaque colonne du résultat à la même colonne du second facteur. Les colonnes (i−1) dₖ + 1 à i dₖ de

$$
X W_Q
$$

valent donc exactement

$$
X W_i^Q .
$$

C'est ce qui justifie l'implémentation habituelle : une seule grande multiplication, puis un découpage de la sortie en h bandes de dₖ colonnes. Le programme le vérifie : la bande i de `produit(X, W_Q)` est égale à `produit(X, bande(W_Q, i, 2))`.

### 2. Le nombre de paramètres vaut

$$
4 d_{model}^2 ,
$$

quel que soit h

$$
W_Q ,
$$

$$
W_K
$$

et

$$
W_V
$$

ont chacune

$$
d_{model}
$$

lignes et

$$
h\, d_k = d_{model}
$$

colonnes ; Wᴼ a

$$
h\, d_v = d_{model}
$$

lignes et

$$
d_{model}
$$

colonnes. On a donc quatre matrices carrées de

$$
d_{model}^2
$$

coefficients :

$$
P = 3\, d_{model} (h\, d_k) + (h\, d_v)\, d_{model} = 4\, d_{model}^2
$$

L'égalité tient parce que

$$
h\, d_k = h\, d_v = d_{model}
$$

Le nombre de têtes s'élimine. Pour

$$
d_{model} = 4 ,
$$

cela fait 64 coefficients, ceux que le programme compte un par un dans ses quatre matrices ; pour

$$
d_{model} = 512 ,
$$

4 × 512² = 1 048 576. La formule n'a pas de biais. La couche `nn.Linear` de PyTorch, utilisée dans l'ancienne version de ce fichier, en ajoute un par défaut (`bias=True`), soit

$$
d_{model}
$$

paramètres de plus par matrice et

$$
4 d_{model}
$$

au total : 1 050 624 pour

$$
d_{model} = 512 .
$$

Ce n'est pas une erreur de PyTorch, mais ce n'est plus la formule écrite ; l'extrait corrigé ci-dessous passe `bias=False`.

### 3. Le coût de l'attention est le même qu'avec une seule tête de largeur

$$
d_{model}
$$

Dans une tête, la matrice des scores demande n² dₖ multiplications et la moyenne des valeurs n² dᵥ (décompte de l'étape 31, point 5). Pour h têtes :

$$
h \left( n^2 d_k + n^2 d_v \right) = n^2 (h\, d_k + h\, d_v) = 2\, n^2 d_{model}
$$

parce que

$$
h\, d_k = h\, d_v = d_{model} .
$$

Une seule tête de largeur

$$
d_{model}
$$

coûte

$$
n^2 (d_{model} + d_{model}) ,
$$

exactement la même chose. Avec n = 3 et

$$
d_{model} = 4 ,
$$

le compteur du programme mesure 72 multiplications pour h = 1, 2 et 4. En revanche, il y a h matrices de scores de n × n cases au lieu d'une : le programme compte 9, 18 et 36 cases. Le nombre d'exponentielles et la mémoire des scores, quand on les stocke, sont donc **multipliés par h**. L'ancienne phrase « on n'a pas multiplié la facture par huit » est juste pour les multiplications, fausse pour ces deux postes.

### 4. Le coût des projections est linéaire en n, et il domine sur les textes courts

L'ancienne version donnait seulement

$$
O(n^2 \cdot d_{model})
$$

et oubliait les projections. Chacune des trois projections

$$
X W_Q ,
$$

$$
X W_K ,
$$

$$
X W_V
$$

multiplie une matrice

$$
n \times d_{model}
$$

par une matrice

$$
d_{model} \times d_{model} ,
$$

soit

$$
n\, d_{model}^2
$$

multiplications ; la projection de sortie aussi. Au total,

$$
4\, n\, d_{model}^2
$$

192 dans l'exemple (4 × 3 × 4²), ce que le compteur mesure. Le rapport entre les deux coûts vaut :

$$
\frac{C_{attention}}{C_{projections}} = \frac{2\, n^2 d_{model}}{4\, n\, d_{model}^2} = \frac{n}{2\, d_{model}}
$$

Les deux coûts sont égaux pour

$$
n = 2 d_{model} .
$$

Avec

$$
d_{model} = 4\,096 ,
$$

le seuil est à 8 192 tokens : pour un message de 300 tokens, le rapport vaut 0,037 et les projections dominent ; pour un contrat de 20 000 tokens, il vaut 2,441 et l'attention domine. Le coût complet de la couche est donc en

$$
O(n\, d_{model}^2 + n^2 d_{model}) .
$$

### 5. Chaque tête divise par √dₖ, pas par

$$
\sqrt{d_{model}}
$$

Dans une tête, le produit scalaire ne compte que dₖ termes ; sous les hypothèses de l'étape 32, sa variance vaut dₖ, et c'est √dₖ qui la ramène à 1. Diviser par

$$
\sqrt{d_{model}} = \sqrt{h\, d_k}
$$

donnerait une variance

$$
d_k / d_{model} = 1/h
$$

Des scores trop petits, des poids trop plats. Dans l'exemple, la tête 1 de « il » donne un poids de 0,8943 à « contrat » avec

$$
\sqrt{d_k} = \sqrt{2} ,
$$

mais seulement e² / (e² + 2) ≈ 0,7870 si l'on divise par

$$
\sqrt{4} = 2 .
$$

### 6. Exemple fait à la main (le code reprend ces nombres)

Trois tokens, « contrat », « expire », « il », avec des embeddings one-hot en dimension

$$
d_{model} = 4
$$

(le quatrième axe ne sert pas), h = 2 têtes de largeur dₖ = 2 et le masque causal. Seul « il » pose une question : sa requête vaut [2 ; 0 ; 2 ; 0], soit [2 ; 0] dans chaque tête. La clé de « contrat » vaut [2 ; 0] dans la tête 1 et [0 ; 0] dans la tête 2 ; celle de « expire », l'inverse. Les valeurs de « contrat » et « expire » sont [1 ; 0] et [0 ; 1] dans chaque tête, celle de « il » est nulle, et Wᴼ est l'identité.

- Tête 1 : scores

$$
[4 ; 0 ; 0] / \sqrt{2} = [2{,}82843 ; 0 ; 0] ,
$$

d'où les poids 16,91883 / 18,91883 ≈ 0,8943 sur « contrat » et 1 / 18,91883 ≈ 0,0529 sur les deux autres ; sortie [0,8943 ; 0,0529].
- Tête 2 : scores [0 ; 4 ; 0] / √2, poids [0,0529 ; 0,8943 ; 0,0529], sortie [0,0529 ; 0,8943].
- Concaténation, puis Wᴼ : [0,8943 ; 0,0529 ; 0,0529 ; 0,8943].

Avec une seule tête de largeur 4, la requête [2 ; 0 ; 2 ; 0] obtient le score 4 contre « contrat » et contre « expire », soit [2 ; 2 ; 0] après division par √4 ; les poids valent e² / (2e² + 1) ≈ 0,4683 sur chacun et 0,0634 sur « il », et la sortie vaut 0,4683 dans les quatre coordonnées. Les deux têtes gardent deux réponses séparées — la tête 1 a trouvé « contrat », la tête 2 « expire » — alors que la tête unique les a fondues dans une seule moyenne où l'on ne sait plus qui est qui. Le masque, enfin, est le même dans les deux têtes : « contrat » ne voit que lui-même (poids [1 ; 0 ; 0]), et « expire », dont la requête est nulle, répartit son poids à parts égales entre les deux tokens qu'il voit ([0,5 ; 0,5 ; 0]).

## Effets et comportement

- **Plus de têtes, des têtes plus étroites.** À

$$
d_{model}
$$

fixé, doubler h divise dₖ par deux ; les paramètres et les multiplications ne bougent pas.
- **Plus de têtes, plus de matrices de scores.** Il y en a h ; le nombre d'exponentielles et la mémoire des scores croissent comme h n².
- **Des réponses séparées.** Chaque tête peut se spécialiser dans un type de lien ; Wᴼ décide ensuite comment combiner les réponses.
- **Textes courts et textes longs.** Sous

$$
n = 2 d_{model} ,
$$

les projections dominent et le coût croît comme n ; au-delà, l'attention domine et il croît comme n².
- **Le découpage doit tomber juste.**

$$
d_{model}
$$

doit être un multiple de h, sinon les têtes n'ont pas la même largeur et la concaténation ne reforme pas

$$
d_{model}
$$

colonnes.

## Du symbole au code Python

$$
X W
$$

**Variable ou fonction :** `produit(X, W, compteur, "projections")`

**Symbole :** bande i de dₖ colonnes · **Variable ou fonction :** `bande(M, i, d_k)`

$$
\text{head}_i
$$

**Variable ou fonction :** `attention(bande(Q, i, d_k), bande(K, i, d_k), bande(V, i, d_k), masque)`

$$
\text{Concat}
$$

**Variable ou fonction :** `concatener(tetes)`

$$
\text{MultiHead}(X)
$$

**Variable ou fonction :** `multi_tetes(X, W_Q, W_K, W_V, W_O, h, masque)`

$$
4 d_{model}^2
$$

**Variable ou fonction :** `nombre_parametres(d_model)`

### Déroulé, ligne par ligne

**`produit(a, b, compteur, cle)`**. Le produit matriciel en trois boucles, comme aux étapes 31 et 33. Chaque multiplication réellement faite incrémente `compteur[cle]` ; la clé vaut `"projections"` pour X W et Concat · Wᴼ, et `"attention"` pour Q Kᵀ et A V. C'est ce qui permet de **mesurer** les deux coûts séparément.

**`softmax(ligne)`** et **`masque_causal(n)`**. Les fonctions des étapes 31 et 33 : retirer le maximum, refuser une ligne entièrement masquée ; 0 sur et sous la diagonale, `-inf` au-dessus. Le masque est construit **une fois** dans `main` et passé à toutes les têtes, parce que les positions sont les mêmes pour toutes.

**`attention(Q, K, V, masque, compteur, diviseur)`**. Une tête.

- `echelle = math.sqrt(len(Q[0]))` : la largeur des requêtes **de la tête**, soit √2 ici, et non √4. Le paramètre `diviseur` ne sert qu'à l'expérience du point 5.
- Pour chaque ligne de Q Kᵀ, on divise, on ajoute le masque, on applique la softmax ; pour « il » dans la tête 1, les scores `[4.0, 0.0, 0.0]` deviennent `[2.82843, 0.0, 0.0]`, puis les poids `[0.8943, 0.0529, 0.0529]`.

**`bande(M, i, largeur)`**. `ligne[i * largeur:(i + 1) * largeur]` extrait les colonnes de la tête `i`. Pour la ligne de « il » dans `Q = [2.0, 0.0, 2.0, 0.0]`, la bande 0 vaut `[2.0, 0.0]` et la bande 1 aussi.

**`concatener(blocs)`**. Pour chaque ligne `r`, `[x for bloc in blocs for x in bloc[r]]` met bout à bout la ligne `r` de chaque tête : `[0.8943, 0.0529]` puis `[0.0529, 0.8943]` donnent `[0.8943, 0.0529, 0.0529, 0.8943]`.

**`multi_tetes(X, W_Q, W_K, W_V, W_O, h, masque, compteur)`**. La formule, dans l'ordre.

- `if d_model % h != 0` : un découpage avec reste est refusé (`ValueError`), comme le `assert` de l'ancien code PyTorch.
- `d_k = d_model // h` : 2 pour h = 2.
- Trois grandes projections, puis une boucle sur les têtes qui découpe `Q`, `K` et `V` en bandes (point 1) et appelle `attention` sur chacune.
- `produit(concatener(tetes), W_O, ...)` : la concaténation, puis le mélange par Wᴼ. La fonction renvoie aussi les poids et les sorties de chaque tête, pour les inspecter.

**`nombre_parametres(d_model, biais)`** renvoie `4 * d_model * d_model`, plus `4 * d_model` si `biais` est vrai (point 2).

**`main()`**, bloc par bloc.

1. L'exemple du point 6 : les poids et sorties des deux têtes, la concaténation `[0.8943, 0.0529, 0.0529, 0.8943]`, puis la tête unique `[0.4683, 0.4683, 0.0634]` et sa sortie uniforme à 0,4683.
2. Le masque partagé : dans les deux têtes, « contrat » reçoit `[1.0, 0.0, 0.0]` et « expire » `[0.5, 0.5, 0.0]`.
3. Le découpage en bandes est comparé, tête par tête, au produit par la petite matrice (point 1).
4. Le compte des coefficients des quatre matrices de l'exemple vaut 64, comme `nombre_parametres(4)` ; puis 1 048 576 et 1 050 624 pour

$$
d_{model} = 512
$$

(point 2).
5. Pour h = 1, 2 et 4, les compteurs mesurent 192 multiplications de projection et 72 d'attention, mais 9, 18 et 36 cases de scores (points 3 et 4). Ensuite, la tête 1 divisée par 2 au lieu de √2 donne 0,7870 (point 5).
6. Les ordres de grandeur des cas d'usage : le rapport

$$
n / (2 d_{model}) ,
$$

la mémoire des poids d'attention d'un modèle de 32 couches et le cache clé-valeur.
7. Deux découpages avec reste, 4 / 3 et 512 / 12, doivent lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`transposer(m)`** — Cette fonction fait pivoter un tableau comme on ferait tourner d'un quart de tour une feuille de relevés pour lire les colonnes à la place des lignes : elle reçoit une matrice m, la passe à `zip(*m)`, qui regroupe les éléments de même rang, et transforme chaque groupe en liste. Elle renvoie la transposée mᵀ, sans rien modifier de l'original ; `attention` s'en sert pour fabriquer Kᵀ avant le produit Q Kᵀ, de sorte que chaque case de la matrice des scores soit le produit scalaire d'une requête avec une clé.

**`attention(Q, K, V, masque, compteur, diviseur)`** — C'est une seule tête d'attention, une enquêtrice qui ne pose qu'une question : la fonction reçoit les requêtes Q, les clés K et les valeurs V de sa tête, un masque facultatif, le registre des multiplications et un diviseur facultatif. Elle prend pour échelle la racine de la largeur des requêtes de la tête, √2 ici et non √4, sauf si un diviseur lui est imposé, calcule Q Kᵀ en comptant dans la case `"attention"`, divise chaque ligne, ajoute le masque et applique `softmax`, puis multiplie ces poids par V. Elle renvoie la sortie de la tête et ses poids : pour « il » dans la tête 1, les scores `[4.0, 0.0, 0.0]` deviennent les poids `[0.8943, 0.0529, 0.0529]`, et le diviseur 2 de l'expérience du point 5 les fait tomber à 0,7870 pour « contrat ».

**`bande(M, i, largeur)`** — Imaginons un découpeur qui tranche une longue bande de tissu en coupons de même largeur et remet à chaque tête le sien : la fonction reçoit une matrice M, le numéro i d'une tête et la largeur d'un coupon, puis garde, dans chaque ligne, les colonnes de i × largeur jusqu'à (i + 1) × largeur − 1. Elle renvoie cette sous-matrice, la part de la tête i ; `multi_tetes` l'applique à Q, K et V, et `main` vérifie au bloc 3 que couper X W_Q en bandes revient exactement à multiplier X par la bande correspondante de W_Q.

**`concatener(blocs)`** — Cette fonction est la couturière qui recoud les coupons après que chaque tête a travaillé sur le sien : elle reçoit la liste des matrices de sortie des h têtes, toutes de même nombre de lignes, et, pour chaque ligne r, met bout à bout la ligne r de la première tête, puis celle de la deuxième, et ainsi de suite. Elle renvoie une matrice de n lignes et h × dᵥ colonnes ; pour « il », les sorties `[0.8943, 0.0529]` et `[0.0529, 0.8943]` des deux têtes donnent `[0.8943, 0.0529, 0.0529, 0.8943]`, que Wᴼ mélange ensuite.

**`multi_tetes(X, W_Q, W_K, W_V, W_O, h, masque, compteur)`** — C'est le chef de service qui distribue un même dossier à h enquêteurs puis réunit leurs rapports : la fonction reçoit les embeddings X, les quatre matrices de poids, le nombre h de têtes, un masque et un registre facultatifs, et lève une `ValueError` si la largeur du modèle ne se divise pas exactement par h. Elle calcule ensuite les trois grandes projections, découpe Q, K et V en h bandes de largeur dₖ, appelle `attention` sur chaque bande, concatène les sorties et les multiplie par Wᴼ. Elle renvoie la sortie finale, la liste des poids et la liste des sorties de chaque tête ; sur l'exemple, deux têtes séparent « contrat » et « expire » là où une tête unique rend une sortie uniforme à 0,4683, et les compteurs restent à 192 et 72 multiplications quel que soit h.

**`nombre_parametres(d_model, biais)`** — Cette fonction est l'inventaire du magasin des poids : elle reçoit la largeur du modèle et un drapeau `biais`, faux par défaut, et renvoie 4 × d_model², pour les quatre matrices carrées `W_Q`, `W_K`, `W_V` et `W_O`, auxquels elle ajoute 4 × d_model si les biais de `nn.Linear` sont comptés. Le nombre ne dépend pas de h, ce que le point 2 démontre ; elle donne 64 pour l'exemple, 1 048 576 et 1 050 624 pour d_model = 512, et 2 147 483 648 paramètres pour 32 couches de largeur 4 096.

**`arrondir(v, n)`** — Ce petit utilitaire joue le greffier qui recopie des nombres au propre avant de les comparer : il reçoit une liste de flottants et un nombre n de décimales, 4 par défaut, et renvoie la liste des valeurs arrondies à n chiffres après la virgule. Il ne sert qu'à l'affichage et aux `assert` de `main`, qui peuvent ainsi comparer les poids calculés aux valeurs écrites à la main, comme `[0.8943, 0.0529, 0.0529]`, sans être trahis par les derniers chiffres d'un calcul en virgule flottante.

**`main()`** — Le chef d'orchestre joue les sept tableaux du fichier sur trois tokens one-hot, « contrat », « expire » et « il », avec des matrices choisies pour que seul « il » pose une question : il compare deux têtes à une seule, vérifie que le masque causal partagé donne `[1.0, 0.0, 0.0]` à « contrat » et `[0.5, 0.5, 0.0]` à « expire » dans les deux têtes, contrôle le découpage en bandes et le compte des paramètres. Il mesure ensuite les multiplications pour h = 1, 2 et 4 et les 9, 18 et 36 cases de scores, montre l'effet d'un mauvais diviseur, recalcule les ordres de grandeur des cas d'usage et s'assure que les découpages 4 / 3 et 512 / 12 lèvent une `ValueError` ; il ne renvoie rien et n'imprime le message final que si tout concorde.

```python
"""Étape 34 — attention multi-têtes en Python pur : découpage, attention par tête, concaténation, W^O."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

Matrice = list[list[float]]


def produit(a: Matrice, b: Matrice, compteur: dict[str, int] | None = None, cle: str = "attention") -> Matrice:
    """(n × d) · (d × m) → (n × m) ; compte chaque multiplication dans compteur[cle]."""
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
                    compteur[cle] += 1
            c[i][j] = s
    return c


def transposer(m: Matrice) -> Matrice:
    return [list(colonne) for colonne in zip(*m)]


def softmax(ligne: list[float]) -> list[float]:
    pic = max(ligne)
    if pic == -math.inf:
        raise ValueError("ligne entièrement masquée : aucun token visible")
    e = [math.exp(x - pic) for x in ligne]
    total = sum(e)
    return [x / total for x in e]


def masque_causal(n: int) -> Matrice:
    """0 si j <= i, −inf si j > i : construit une fois, partagé par toutes les têtes."""
    return [[0.0 if j <= i else -math.inf for j in range(n)] for i in range(n)]


def attention(Q: Matrice, K: Matrice, V: Matrice, masque: Matrice | None = None,
              compteur: dict[str, int] | None = None, diviseur: float | None = None) -> tuple[Matrice, Matrice]:
    """Une tête : softmax(Q Kᵀ / √d_k + M) V. diviseur remplace √d_k pour l'expérience du point 5."""
    echelle = math.sqrt(len(Q[0])) if diviseur is None else diviseur
    poids = []
    for i, ligne in enumerate(produit(Q, transposer(K), compteur, "attention")):
        s = [x / echelle for x in ligne]
        if masque is not None:
            s = [x + m for x, m in zip(s, masque[i])]
        poids.append(softmax(s))
    return produit(poids, V, compteur, "attention"), poids


def bande(M: Matrice, i: int, largeur: int) -> Matrice:
    """Colonnes i·largeur … (i+1)·largeur − 1 de M : la part de la tête i."""
    return [ligne[i * largeur:(i + 1) * largeur] for ligne in M]


def concatener(blocs: list[Matrice]) -> Matrice:
    """Recolle h matrices n × d_v côte à côte : une matrice n × (h·d_v)."""
    return [[x for bloc in blocs for x in bloc[r]] for r in range(len(blocs[0]))]


def multi_tetes(X: Matrice, W_Q: Matrice, W_K: Matrice, W_V: Matrice, W_O: Matrice, h: int,
                masque: Matrice | None = None, compteur: dict[str, int] | None = None):
    """MultiHead(X) = Concat(head_1, …, head_h) W^O, avec head_i = Attention(X W_i^Q, X W_i^K, X W_i^V)."""
    d_model = len(X[0])
    if d_model % h != 0:
        raise ValueError(f"d_model = {d_model} n'est pas divisible par h = {h}")
    d_k = d_model // h
    Q = produit(X, W_Q, compteur, "projections")  # les h projections W_i^Q d'un seul coup
    K = produit(X, W_K, compteur, "projections")
    V = produit(X, W_V, compteur, "projections")
    tetes, poids = [], []
    for i in range(h):
        sortie_i, poids_i = attention(bande(Q, i, d_k), bande(K, i, d_k), bande(V, i, d_k), masque, compteur)
        tetes.append(sortie_i)
        poids.append(poids_i)
    return produit(concatener(tetes), W_O, compteur, "projections"), poids, tetes


def nombre_parametres(d_model: int, biais: bool = False) -> int:
    """W_Q, W_K, W_V, W_O : quatre matrices d_model × d_model ; nn.Linear ajoute par défaut quatre biais de d_model."""
    return 4 * d_model * d_model + (4 * d_model if biais else 0)


def arrondir(v: list[float], n: int = 4) -> list[float]:
    return [round(x, n) for x in v]


def main() -> None:
    tokens = ["contrat", "expire", "il"]
    X = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]  # one-hot, d_model = 4
    zero = [0.0, 0.0, 0.0, 0.0]
    W_Q = [zero, zero, [2.0, 0.0, 2.0, 0.0], zero]  # seul « il » pose une question, une par tête
    W_K = [[2.0, 0.0, 0.0, 0.0], [0.0, 0.0, 2.0, 0.0], zero, zero]  # tête 1 : « contrat » ; tête 2 : « expire »
    W_V = [[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0], zero, zero]  # chaque tête reçoit une copie des contenus
    W_O = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]  # identité : on lit la concaténation
    M = masque_causal(3)

    print("1. Deux têtes (d_k = 2) contre une seule tête (d_k = 4), requête « il »")
    sortie2, poids2, tetes2 = multi_tetes(X, W_Q, W_K, W_V, W_O, h=2, masque=M)
    sortie1, poids1, _ = multi_tetes(X, W_Q, W_K, W_V, W_O, h=1, masque=M)
    for i in range(2):
        print(f"  tête {i + 1} : poids = {arrondir(poids2[i][2])}  sortie = {arrondir(tetes2[i][2])}")
    print(f"  concaténation · W^O     = {arrondir(sortie2[2])}")
    print(f"  une seule tête : poids = {arrondir(poids1[0][2])}  sortie = {arrondir(sortie1[2])}")
    assert arrondir(poids2[0][2]) == [0.8943, 0.0529, 0.0529] and arrondir(poids2[1][2]) == [0.0529, 0.8943, 0.0529]
    assert arrondir(sortie2[2]) == [0.8943, 0.0529, 0.0529, 0.8943]
    assert arrondir(poids1[0][2]) == [0.4683, 0.4683, 0.0634] and arrondir(sortie1[2]) == [0.4683] * 4

    print("2. Le masque causal est le même pour toutes les têtes")
    for t in range(2):
        assert poids2[t][0] == [1.0, 0.0, 0.0] and poids2[t][1] == [0.5, 0.5, 0.0]
    print(f"  « {tokens[0]} » : {poids2[0][0]} ; « {tokens[1]} » : {poids2[0][1]} (dans les deux têtes)")

    print("3. Couper X W_Q en bandes = appliquer h petites matrices W_i^Q")
    Q = produit(X, W_Q)
    for i in range(2):
        assert bande(Q, i, 2) == produit(X, bande(W_Q, i, 2))
    print(f"  bande 1 de Q = {bande(Q, 0, 2)[2]}, bande 2 = {bande(Q, 1, 2)[2]} (ligne de « il »)")

    print("4. Paramètres : 4·d_model², quel que soit h")
    compte = sum(len(ligne) for W in (W_Q, W_K, W_V, W_O) for ligne in W)
    for d in (4, 512):
        print(f"  d_model = {d:>3} : {nombre_parametres(d):_} sans biais, {nombre_parametres(d, biais=True):_} avec biais")
    assert compte == nombre_parametres(4) == 64
    assert nombre_parametres(512) == 1_048_576 and nombre_parametres(512, biais=True) == 1_050_624

    print("5. Coûts mesurés (n = 3, d_model = 4) et échelle par tête")
    for h in (1, 2, 4):
        compteur = {"projections": 0, "attention": 0}
        _, poids_h, _ = multi_tetes(X, W_Q, W_K, W_V, W_O, h=h, masque=M, compteur=compteur)
        cases = sum(len(p) * len(p[0]) for p in poids_h)  # une matrice n × n de scores par tête
        print(f"  h = {h} : projections = {compteur['projections']}  attention = {compteur['attention']}"
              f"  cases de scores = {cases}")
        assert compteur["projections"] == 4 * 3 * 4 * 4  # 4 n d_model²
        assert compteur["attention"] == 2 * 3 * 3 * 4  # h · n² (d_k + d_v) = 2 n² d_model
        assert cases == h * 3 * 3  # h · n² : mémoire des scores et exponentielles multipliées par h
    _, poids_trop = attention(bande(Q, 0, 2), bande(produit(X, W_K), 0, 2), bande(produit(X, W_V), 0, 2), M,
                              diviseur=math.sqrt(4))
    print(f"  tête 1 divisée par √d_model = 2 au lieu de √d_k : poids de « contrat » = {poids_trop[2][0]:.4f}")
    assert round(poids_trop[2][0], 4) == 0.787 and poids_trop[2][0] < poids2[0][2][0]

    print("6. Ordres de grandeur (dimensions illustratives)")
    d, L = 4096, 32
    assert 2 * d == 8192  # attention (2 n² d) = projections (4 n d²) quand n = 2 d
    for n in (300, 20_000):
        rapport = (2 * n * n * d) / (4 * n * d * d)
        print(f"  n = {n:>6} tokens : attention / projections = {rapport:.3f}")
        assert abs(rapport - n / (2 * d)) < 1e-12
    assert nombre_parametres(512, biais=True) - nombre_parametres(512) == 2_048 and L * 32 == 1_024
    params = nombre_parametres(d) * L
    print(f"  attention de {L} couches en d_model = {d} : {params:_} paramètres, {params * 2 / 1e9:.2f} Go en fp16")
    assert params == 2_147_483_648
    for h_kv, attendu in ((32, 4_194_304_000), (8, 1_048_576_000)):
        cache = 2 * L * h_kv * 128 * 8_000 * 2  # K et V, par couche, par tête KV, par token, 2 octets
        assert cache == attendu
        print(f"  cache KV pour 8 000 tokens avec {h_kv:>2} têtes KV : {cache / 1e9:.2f} Go")

    print("7. Entrées invalides refusées")
    for d_model, h in ((4, 3), (512, 12)):
        X_test = [[0.0] * d_model]
        W = [[0.0] * d_model for _ in range(d_model)]
        try:
            multi_tetes(X_test, W, W, W, W, h=h)
        except ValueError as e:
            print(f"  ValueError : {e}")
        else:
            raise AssertionError("un découpage avec reste aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Deux têtes (d_k = 2) contre une seule tête (d_k = 4), requête « il »
  tête 1 : poids = [0.8943, 0.0529, 0.0529]  sortie = [0.8943, 0.0529]
  tête 2 : poids = [0.0529, 0.8943, 0.0529]  sortie = [0.0529, 0.8943]
  concaténation · W^O     = [0.8943, 0.0529, 0.0529, 0.8943]
  une seule tête : poids = [0.4683, 0.4683, 0.0634]  sortie = [0.4683, 0.4683, 0.4683, 0.4683]
…
  d_model = 512 : 1_048_576 sans biais, 1_050_624 avec biais
…
  h = 1 : projections = 192  attention = 72  cases de scores = 9
  h = 2 : projections = 192  attention = 72  cases de scores = 18
  h = 4 : projections = 192  attention = 72  cases de scores = 36
  tête 1 divisée par √d_model = 2 au lieu de √d_k : poids de « contrat » = 0.7870
…
  n =    300 tokens : attention / projections = 0.037
  n =  20000 tokens : attention / projections = 2.441
  attention de 32 couches en d_model = 4096 : 2_147_483_648 paramètres, 4.29 Go en fp16
  cache KV pour 8 000 tokens avec 32 têtes KV : 4.19 Go
  cache KV pour 8 000 tokens avec  8 têtes KV : 1.05 Go
…
OK — toutes les vérifications sont passées.
```

### La version PyTorch (extrait) et ce qui s'y passe vraiment

L'ancienne version de ce fichier ne contenait que ce code, qui dépend de PyTorch. Le voici en extrait, corrigé sur trois points : les biais sont désactivés pour suivre la formule, l'entrée s'appelle `X` (auto-attention), et le masque causal est construit explicitement.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`MultiHeadAttention.__init__(d_model, n_heads, dropout, biais)`** — Le constructeur installe l'atelier avant l'arrivée du premier dossier : il reçoit la largeur du modèle, 512 par défaut, le nombre de têtes, 8 par défaut, le taux de dropout, 0,1 par défaut, et le drapeau `biais`, faux par défaut, puis vérifie par un `assert` que la largeur se divise exactement par le nombre de têtes et calcule dₖ, soit 64. Il crée ensuite les quatre couches linéaires carrées `W_q`, `W_k`, `W_v` et `W_o`, sans biais pour suivre la formule, ainsi qu'une couche de dropout ; il ne renvoie rien, mais la couche ainsi construite compte 1 048 576 paramètres, comme l'imprime la dernière ligne.

**`MultiHeadAttention.scaled_dot_product_attention(Q, K, V, mask)`** — Cette méthode fait travailler toutes les têtes d'un coup, comme une salle d'examen où chaque candidat répond en même temps à sa propre question : elle reçoit des tenseurs Q, K et V déjà découpés par tête et un masque facultatif, calcule les scores Q Kᵀ divisés par √dₖ, remplace par moins l'infini toutes les cases où le masque vaut 0, applique la softmax sur la dernière dimension, puis le dropout, actif seulement à l'entraînement. Elle renvoie le produit des poids par V et les poids eux-mêmes ; c'est la version tensorielle de la fonction `attention` en Python pur du programme précédent.

**`MultiHeadAttention.forward(X, mask)`** — C'est le passage complet d'un lot de phrases dans la couche, la tournée du chef de service : la méthode reçoit le tenseur X des embeddings et un masque facultatif, applique les trois projections, puis, par `view` et `transpose`, range chaque projection en n_heads bandes de largeur dₖ pour obtenir une forme (lot, têtes, positions, dₖ). Elle appelle `scaled_dot_product_attention`, remet les têtes côte à côte par la transposition inverse, `contiguous` et `view`, ce qui est la concaténation, et renvoie la sortie projetée par `W_o` ainsi que les poids d'attention, exactement comme `multi_tetes` le fait à la main.

```python
# [extrait] — version PyTorch, non exécutée par le harnais (PyTorch n'est pas dans la bibliothèque standard)
import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model=512, n_heads=8, dropout=0.1, biais=False):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        # nn.Linear ajoute un biais par défaut (bias=True) ; la formule n'en a pas.
        self.W_q = nn.Linear(d_model, d_model, bias=biais)
        self.W_k = nn.Linear(d_model, d_model, bias=biais)
        self.W_v = nn.Linear(d_model, d_model, bias=biais)
        self.W_o = nn.Linear(d_model, d_model, bias=biais)
        self.dropout = nn.Dropout(dropout)

    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))  # convention : 1 = visible, 0 = interdit
        attn = F.softmax(scores, dim=-1)
        attn = self.dropout(attn)  # actif à l'entraînement seulement ; model.eval() le coupe
        return torch.matmul(attn, V), attn

    def forward(self, X, mask=None):  # auto-attention : MultiHead(X)
        batch_size = X.size(0)
        Q = self.W_q(X).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(X).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(X).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        attn_output, attn_weights = self.scaled_dot_product_attention(Q, K, V, mask)
        concat = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        return self.W_o(concat), attn_weights


n = 10
mask = torch.tril(torch.ones(n, n, dtype=torch.bool))  # masque causal : True sur et sous la diagonale
couche = MultiHeadAttention()
print(sum(p.numel() for p in couche.parameters()))  # 1048576 = 4 × 512², sans biais
```

Une seule tête d'attention répond à une seule question : « à qui ce token ressemble-t-il ? ». Dans « le contrat expire demain, il est signé », « il » doit à la fois retrouver « contrat » (de quoi on parle) et « expire » (ce qui lui arrive). Une seule moyenne pondérée mélange les deux besoins, comme le montre la sortie uniforme à 0,4683 du point 6. Plusieurs têtes posent plusieurs questions en parallèle, chacune dans un petit espace.

`d_model = 512` et `n_heads = 8` donnent `d_k = 64`. Le `assert d_model % n_heads == 0` refuse un découpage qui laisserait un reste : les têtes doivent avoir la même largeur, sinon la concaténation ne reforme pas 512.

`W_q`, `W_k`, `W_v` sont des couches linéaires de 512 vers 512. On ne crée pas huit petites matrices séparées. On en crée une grande, et le `view` la coupe en huit bandes de 64. C'est le même produit

$$
X W_i^Q ,
$$

rangé autrement en mémoire (point 1). `W_o` est la matrice Wᴼ qui ramène la concaténation vers 512. Par défaut, `nn.Linear` ajoute à chacune un vecteur de biais : l'ancienne version comptait donc 4 × 512 paramètres de plus que la formule, d'où le paramètre `biais=False` de l'extrait.

Dans `forward`, `X.size(0)` est le nombre de phrases du lot. `self.W_q(X)` projette. `.view(batch, -1, 8, 64)` dit : garde le lot, laisse la longueur de séquence se calculer (`-1`), puis sépare 8 têtes de 64. `.transpose(1, 2)` met les têtes devant la séquence, pour que `matmul` calcule l'attention de chaque tête d'un coup. `K` et `V` subissent le même découpage. Après ça, chaque tête voit ses propres 64 coordonnées et plus les 512.

`scaled_dot_product_attention` est l'attention du chapitre 6, une fois par tête.

- `Q @ K.transpose` fait tous les produits scalaires. Diviser par `sqrt(d_k)` avec `d_k = 64` donne une division par 8, pas par √512. L'échelle suit la largeur de la tête, pas celle du modèle. Si on divisait par √512, la variance des scores tomberait à 1/8 et les têtes se concentreraient beaucoup moins (point 5).
- `mask == 0` remplace les cases interdites par −∞. Après softmax,

$$
e^{-\infty}
$$

vaut 0. Dans cette convention, le masque vaut 1 (ou `True`) pour une case visible, l'inverse du masque additif du programme (0 visible, −∞ interdit). `torch.tril` le construit : un agent qui génère le token 5 n'a pas le droit de lire le token 6.
- `dropout` met quelques poids à zéro pendant l'entraînement seulement, pour que la tête ne s'habitue pas à un seul token ; il multiplie les autres par 1/(1−p), si bien qu'une ligne ne somme plus exactement à 1 pendant l'entraînement. En inférence, `model.eval()` le désactive.
- `matmul(attn, V)` mélange les valeurs avec ces poids. La sortie d'une tête a la forme `(lot, tête, longueur, 64)`.

`transpose(1, 2)` remet la séquence avant les têtes. `contiguous().view(..., d_model)` recolle les 8 bandes de 64 en un vecteur de 512. `contiguous` est là parce que `transpose` a permuté les axes sans bouger la mémoire, et `view` refuse un tableau dont les cases ne se suivent plus. `W_o` mélange ensuite les têtes : une coordonnée de la sortie peut prendre un peu de la tête « syntaxe » et un peu de la tête « coréférence ». Sans Wᴼ, les têtes resteraient juxtaposées et ne se parleraient pas.

Le coût des multiplications de l'attention reste

$$
2 n^2 d_{model}
$$

Huit têtes de largeur 64 font autant de produits qu'une tête de largeur 512, parce que 8 × 64 = 512 (point 3). Mais il y a huit matrices de scores au lieu d'une, et les quatre projections ajoutent

$$
4 n\, d_{model}^2
$$

multiplications (point 4).

## Squelette algorithmique

L'attention multi-têtes découpe la dimension du modèle en h sous-espaces de taille d_k = d_model / h, fait une attention dans chacun, puis recolle les h résultats et les projette. Le coût total reste celui d'une seule grande tête.

```text
ALGORITHME AttentionMultiTêtes
ENTRÉES : X (n × d_model), W_Q, W_K, W_V, W_O (d_model × d_model), nombre de têtes h, masque causal facultatif
SORTIE  : la sortie (n × d_model)

  d_k ← d_model / h                               (h doit diviser d_model)
  Q ← X × W_Q ; K ← X × W_K ; V ← X × W_V
  POUR i DE 1 À h FAIRE
      Qᵢ ← colonnes (i−1) d_k + 1 … i d_k de Q        (une bande de largeur d_k)
      Kᵢ ← même bande de K ; Vᵢ ← même bande de V
      têteᵢ ← Attention(Qᵢ, Kᵢ, Vᵢ, masque)          (avec la division par √d_k)
  FIN POUR
  RETOURNER Concat(tête₁, …, tête_h) × W_O

PARAMÈTRES : 4 × d_model² (sans biais), quel que soit h
```

**Complexité.** Les projections coûtent O(n × d_model²). Chaque tête coûte O(n² × d_k), donc les h têtes ensemble O(n² × h × d_k) = O(n² × d_model) : autant qu'une seule tête de dimension d_model, ce que le compteur de multiplications du programme vérifie. La mémoire des poids d'attention est O(h × n²), une matrice n × n par tête.

**Du squelette au code.** `bande` extrait les colonnes d'une tête, `attention` (avec `softmax`, `produit`, `transposer` et `masque_causal`) calcule chaque tête, `concatener` recolle les têtes, `multi_tetes` enchaîne le tout avec la projection finale, et `nombre_parametres` vérifie la formule 4 d_model². La classe PyTorch `MultiHeadAttention`, plus bas, fait le même calcul avec des tenseurs.

## Cas d'usage réels aux Émirats

Les dimensions de modèles ci-dessous sont illustratives : en production, on lit celles du fichier de configuration du modèle retenu. Les nombres qui en découlent sont vérifiés par le programme (bloc 6).

### Banque — dimensionner un serveur pour un modèle hébergé sur site

Une banque de détail de Dubaï prépare l'hébergement, sur ses propres serveurs, d'un modèle de langage ouvert pour ses assistants internes de conformité et de KYC. Avant de commander les cartes graphiques, l'équipe calcule la mémoire des seuls poids d'attention : chaque couche porte quatre matrices

$$
d_{model} \times d_{model} ,
$$

soit

$$
4 d_{model}^2
$$

paramètres, un nombre qui ne dépend pas du nombre de têtes. Pour un modèle de dimension 4 096 à 32 couches, cela fait 2 147 483 648 paramètres, soit 4,29 Go en fp16, avant même les couches feed-forward, les embeddings et le cache clé-valeur. Si le fichier de configuration indique des biais dans les projections, il faut ajouter

$$
4 d_{model}
$$

paramètres par couche : c'est négligeable en mémoire, mais indispensable pour qu'un export vers un autre moteur d'inférence reproduise les mêmes sorties. L'équipe additionne ensuite tous les postes et garde une marge pour les pics de charge de fin de mois, quand les demandes de prêt affluent. Sans ce calcul, elle découvre en recette que le modèle ne tient pas en mémoire avec la longueur de contexte visée, et doit choisir entre tronquer les dossiers et racheter du matériel. L'indicateur suivi est la marge de mémoire GPU au pic de charge, mesurée en recette sur des dossiers anonymisés.

### Secteur public — combien de sessions par carte graphique

Une entité de services publics en ligne accessible par UAE Pass sert un assistant bilingue arabe-anglais à des milliers d'usagers simultanés. La mémoire qui limite le nombre de sessions par carte n'est pas celle des poids, mais celle du cache clé-valeur : pour chaque session, le modèle garde K et V de chaque couche, de chaque tête de clés-valeurs et de chaque token, soit 2 × L × hₖᵥ × dₖ × n nombres de 2 octets, où L est le nombre de couches et hₖᵥ le nombre de têtes de clés-valeurs. Avec 32 couches, des têtes de largeur 128 et une conversation de 8 000 tokens, cela fait 4,19 Go par session si les 32 têtes ont chacune leurs clés et leurs valeurs, mais 1,05 Go avec une variante où 8 têtes de clés-valeurs sont partagées entre les 32 têtes de requêtes (GQA) : quatre fois plus de sessions sur la même carte. L'équipe retient donc un modèle qui partage ses clés et ses valeurs, et elle compacte les conversations au-delà d'une longueur fixée, puisque le cache croît linéairement avec chaque token échangé. Sans ce calcul, le service refuse des sessions aux heures de pointe, au moment précis où les usagers en ont besoin, par exemple à l'approche des échéances de renouvellement. Garder des sessions courtes sert aussi la minimisation des données personnelles qu'exige la PDPL. L'indicateur suivi est le nombre de sessions simultanées par carte au 95e percentile de latence visé.

### RH — des messages courts et des contrats longs n'ont pas le même coût

Un cabinet RH multi-émirats fait tourner un même modèle sur deux flux : des messages de candidats d'environ 300 tokens (questions de visa, de date de prise de poste) et des contrats ou règlements intérieurs d'environ 20 000 tokens. Le rapport entre le calcul de l'attention et celui des projections vaut

$$
n / (2 d_{model})
$$

Avec

$$
d_{model} = 4\,096 ,
$$

il vaut 0,037 pour un message de 300 tokens, où les projections dominent et le coût croît comme n, mais 2,441 pour un contrat de 20 000 tokens, où l'attention domine et le coût croît comme n². Le seuil se trouve à

$$
n = 2 d_{model} = 8\,192
$$

tokens. L'équipe en tire deux règles : regrouper les messages courts en lots pour remplir la carte, puisque leur coût est presque proportionnel à leur longueur, et découper les contrats en sections avant envoi, puisque leur coût croît au carré. Pour les contrats, elle vérifie que le découpage ne sépare pas deux clauses qui se renvoient l'une à l'autre, comme le préavis et l'indemnité de fin de service. Sans cette distinction, le budget de calcul est estimé sur la moyenne des requêtes, et les contrats longs, rares mais très coûteux, font exploser la latence. L'indicateur suivi est le coût de calcul et la latence par type de requête, suivis séparément.

### BTP — porter un petit modèle sur des tablettes de chantier

Un groupe de construction qui mène de grands chantiers à Dubaï veut classer hors ligne, sur des tablettes, le texte extrait des bons de livraison et des documents de chantier, avec un petit modèle Transformer de dimension 512 à 8 têtes. L'équipe exporte les poids depuis PyTorch vers un moteur embarqué et vérifie d'abord le compte des paramètres d'attention : 1 048 576 par couche sans biais, mais 1 050 624 avec les biais que `nn.Linear` ajoute par défaut ; un écart de 2 048 dans le fichier exporté signale des biais oubliés, qui décalent toutes les sorties. Elle se sert ensuite de l'implémentation en Python pur de ce fichier comme d'un oracle : sur des entrées fixes, les sorties de la couche portée doivent coïncider avec celles de l'oracle à 10⁻³ près. Une tentative de passer à 12 têtes échoue d'emblée, parce que 512 n'est pas divisible par 12 : les têtes doivent avoir la même largeur pour que la concaténation reforme 512 colonnes. Sans ces contrôles, une erreur d'export reste invisible tant que personne ne compare les classements, et des bons de livraison mal classés retardent le règlement des fournisseurs. L'indicateur suivi est l'écart maximal entre le modèle porté et l'oracle sur le jeu de test, puis la justesse du classement sur des documents réels.

### Crypto — ne pas présenter une tête d'attention comme une justification

Une plateforme d'actifs virtuels agréée par la VARA doit justifier auprès de son équipe conformité chaque alerte de transaction suspecte proposée par son agent. Un prototype affichait, comme « explication », les poids d'attention d'une tête sur les champs de la transaction. Ce fichier montre pourquoi c'est fragile : un modèle de 32 couches à 32 têtes calcule 32 × 32 = 1 024 matrices de poids différentes, chaque tête ne voit que sa bande de dₖ coordonnées, et Wᴼ mélange ensuite toutes les têtes ; aucune de ces matrices, prise seule, n'est la raison de la sortie. L'équipe remplace donc la carte de chaleur par une sortie structurée : l'agent doit citer les champs et les règles qui motivent l'alerte — montant, contrepartie, fréquence —, et chaque citation est vérifiée par du code contre la transaction réelle. Sans ce changement, un contrôleur pourrait valider une alerte sur la foi d'une image qui n'explique rien, et un audit ne pourrait pas reconstituer la décision. L'indicateur suivi est la part des alertes dont toutes les citations sont vérifiées, avec le taux d'alertes confirmées par la conformité.

## Pièges et limites

- **Oublier les biais de `nn.Linear`.** Ils sont actifs par défaut ; la formule n'en a pas. Pour comparer deux implémentations ou porter des poids, il faut savoir lequel des deux on suit.
- **Diviser par**

$$
\sqrt{d_{model}}
$$

**.** Chaque tête doit diviser par la racine de **sa** largeur ; sinon la variance tombe à 1/h et les poids s'aplatissent (0,7870 au lieu de 0,8943 dans l'exemple).
- **Croire que plus de têtes ne coûtent rien.** Les multiplications ne changent pas, mais il y a h matrices de scores et h fois plus d'exponentielles.
- **Oublier les projections dans le budget.** Elles coûtent

$$
4 n\, d_{model}^2
$$

et dominent pour tous les textes plus courts que

$$
2 d_{model}
$$

tokens.
- **Tester avec Wᴼ égale à l'identité.** Le programme le fait pour rendre l'exemple lisible, mais un test de non-régression doit utiliser une Wᴼ quelconque, sinon il ne détecte pas l'oubli de la projection de sortie (exercice 3).

### Exercice feuille blanche

1. Sans regarder le code, écrire `bande`, `concatener` et `multi_tetes`, puis retrouver la sortie `[0.8943, 0.0529, 0.0529, 0.8943]` de « il ».
2. Prédire, puis vérifier : avec h = 4 têtes de largeur 1 sur l'exemple, combien de multiplications d'attention et combien de cases de scores ? (Réponse : toujours 72 multiplications, mais 36 cases.)
3. Trouver le bug : `return concatener(tetes), poids, tetes` à la place de la dernière ligne de `multi_tetes`. Que manque-t-il, et pourquoi les `assert` du bloc 1 passent-ils quand même ? (Réponse : il manque le mélange par Wᴼ ; les tests passent parce que Wᴼ vaut l'identité dans l'exemple.)

## Pour aller plus loin

Les variantes MQA (une seule tête de clés-valeurs) et GQA (quelques têtes de clés-valeurs partagées) réduisent le cache clé-valeur sans toucher au nombre de têtes de requêtes. Dans un Transformer complet, chaque couche contient aussi un bloc feed-forward qui, avec la largeur intermédiaire habituelle de

$$
4 d_{model} ,
$$

coûte

$$
8\, n\, d_{model}^2
$$

multiplications, deux fois les projections de l'attention. Les noyaux par blocs comme FlashAttention évitent de stocker les h matrices de scores sans changer le résultat.

> Suite : [Encodage de position](<35-Encodage-de-Position.md>) — étape 35.
