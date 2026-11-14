# Étape 20 — RAG — Distance euclidienne (L2)

> Étape 20 du parcours · Prérequis : [Similarité cosinus](<19-RAG-Formule-Similarite-Cosinus.md>) · Suite : [Distance cosinus](<21-RAG-Formule-Distance-Cosinus.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 20-RAG-Formule-Distance-Euclidienne.md

## Définition

La distance euclidienne, ou distance L2, est la longueur du segment qui relie deux points : c'est la distance « à la règle » de la géométrie du lycée, généralisée à n dimensions. Pour deux vecteurs d'embedding a et b, on calcule l'écart coordonnée par coordonnée, on met chaque écart au carré, on additionne ces carrés, puis on prend la racine carrée du total. Elle vaut 0 si et seulement si les deux vecteurs sont identiques, et elle grandit à mesure qu'ils s'éloignent. Contrairement au cosinus de l'étape 19, elle tient compte de la **norme** des vecteurs (leur longueur), et pas seulement de leur direction : deux vecteurs qui pointent dans la même direction mais n'ont pas la même longueur sont à une distance non nulle. Sur des vecteurs normalisés, c'est-à-dire de norme 1, elle classe les documents exactement comme le cosinus, ce qui explique qu'on la trouve comme métrique par défaut dans plusieurs index vectoriels.

## Rôle dans un agent

À chaque tour, l'agent perçoit une question et la transforme en vecteur avec le même modèle d'embedding que celui qui a servi à indexer la base. Pour décider quels passages injecter dans le prompt, le **retriever** demande à l'index vectoriel les k vecteurs les plus proches de la question ; quand l'index est configuré en L2, « les plus proches » veut dire « à la plus petite distance euclidienne ». La même distance sert hors du classement. Dans la **mémoire** (étapes 16 et 17), deux souvenirs à très petite distance sont des doublons que l'agent fusionne avant de les écrire. Dans un **garde-fou**, un vecteur de comportement trop éloigné du comportement habituel déclenche une alerte. Savoir que L2 et cosinus coïncident sur des vecteurs normalisés, et divergent sinon, évite de changer de métrique sans le savoir le jour où l'on change de base vectorielle.

## Équation complète

Distance euclidienne entre deux vecteurs de dimension n :

$$
d(a, b) = \lVert a - b \rVert = \sqrt{\sum_{i=1}^{n} (a_i - b_i)^2}
$$

Développement du carré de la distance :

$$
\lVert a - b \rVert^2 = \lVert a \rVert^2 + \lVert b \rVert^2 - 2\, a \cdot b
$$

Vecteur normalisé (de norme 1) :

$$
\hat a = \frac{a}{\lVert a \rVert}
$$

Sur la sphère unité, lien avec le cosinus :

$$
\lVert \hat a - \hat b \rVert^2 = 2\,(1 - \cos\theta)
$$

$$
d(\hat a, \hat b) = \sqrt{2\,(1 - \cos\theta)}
$$

## Décryptage des symboles

$$
a,\quad b
$$

**Sens :** vecteurs d'embedding (la requête et un document) · **Type / plage :** listes de n réels · **Variable Python :** `a`, `b`

$$
n
$$

**Sens :** dimension de l'espace · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(a)`

$$
a_i,\quad b_i
$$

**Sens :** i-ième coordonnée de chaque vecteur · **Type / plage :** réels · **Variable Python :** `x`, `y` dans `zip(a, b)`

$$
d(a, b)
$$

**Sens :** distance euclidienne · **Type / plage :** réel ≥ 0 · **Variable Python :** `distance_l2(a, b)` ou `math.dist(a, b)`

$$
d(a, b)^2
$$

**Sens :** distance au carré, sans la racine · **Type / plage :** réel ≥ 0 · **Variable Python :** `distance_l2_carree(a, b)`

$$
\lVert a \rVert
$$

**Sens :** norme (longueur) du vecteur · **Type / plage :** réel ≥ 0 · **Variable Python :** `norme(a)`

$$
a \cdot b
$$

**Sens :** produit scalaire ∑ᵢ aᵢ bᵢ · **Type / plage :** réel · **Variable Python :** `produit_scalaire(a, b)`

$$
\hat a
$$

**Sens :** vecteur normalisé a / ‖ a ‖ · **Type / plage :** norme 1 · **Variable Python :** `normaliser(a)`

$$
\cos\theta
$$

**Sens :** similarité cosinus de l'étape 19 · **Type / plage :** réel dans [−1, 1] · **Variable Python :** `cosinus(a, b)`

## Démonstration

### 1. La distance L2 est une vraie distance

Une fonction d mérite le nom de distance si elle vérifie quatre axiomes, pour tous vecteurs a, b, c de même dimension :

1. positivité : d(a, b) ≥ 0 ;
2. séparation : d(a, b) = 0 si et seulement si a = b ;
3. symétrie : d(a, b) = d(b, a) ;
4. inégalité triangulaire : d(a, c) ≤ d(a, b) + d(b, c).

La positivité tient parce qu'une racine carrée est toujours positive ou nulle. La séparation tient parce qu'une somme de carrés est nulle si et seulement si chaque carré est nul : chaque terme est positif ou nul, donc un seul terme strictement positif rendrait la somme strictement positive ; et (aᵢ − bᵢ)² = 0 veut dire aᵢ = bᵢ. La symétrie tient parce que (aᵢ − bᵢ)² = (bᵢ − aᵢ)² : un nombre et son opposé ont le même carré.

Pour l'inégalité triangulaire, on pose u = a − b et v = b − c, de sorte que u + v = a − c. En développant comme au point 2 ci-dessous,

$$
\lVert u + v \rVert^2 = \lVert u \rVert^2 + 2\, u \cdot v + \lVert v \rVert^2 .
$$

L'inégalité de Cauchy-Schwarz, démontrée à l'[étape 14](<../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>), donne u · v ≤ ‖ u ‖ ‖ v ‖. Donc :

$$
\lVert u + v \rVert^2 \le \lVert u \rVert^2 + 2\,\lVert u \rVert\,\lVert v \rVert + \lVert v \rVert^2 = \left(\lVert u \rVert + \lVert v \rVert\right)^2
$$

Les deux membres sont positifs, et la racine carrée est croissante sur les nombres positifs : on peut prendre la racine des deux côtés sans changer le sens de l'inégalité, ce qui donne ‖ a − c ‖ ≤ ‖ a − b ‖ + ‖ b − c ‖. Cet axiome n'est pas un détail : les structures d'index qui éliminent des régions entières de l'espace sans les visiter s'appuient dessus, et l'étape 21 montre que la « distance cosinus » ne le vérifie pas.

### 2. Le carré de la distance se développe en trois morceaux

$$
\lVert a - b \rVert^2 = \sum_{i=1}^{n} (a_i - b_i)^2 = \sum_{i=1}^{n} \left(a_i^2 - 2\,a_i b_i + b_i^2\right) = \sum_{i=1}^{n} a_i^2 + \sum_{i=1}^{n} b_i^2 - 2 \sum_{i=1}^{n} a_i b_i
$$

La deuxième égalité vient de l'identité (x − y)² = x² − 2xy + y², appliquée à chaque coordonnée. La troisième vient de ce qu'une somme de trois termes se coupe en trois sommes. Les trois sommes obtenues sont, dans l'ordre, ‖ a ‖², ‖ b ‖² et a · b : la distance dépend donc des deux normes **et** du produit scalaire.

### 3. Sur la sphère unité, la distance ne dépend plus que du cosinus

Si ‖ â ‖ = ‖ b̂ ‖ = 1, les deux premiers morceaux valent 1 chacun. Le troisième vaut â · b̂ = cosθ, parce que cosθ = (a · b) / (‖ a ‖ ‖ b ‖) et que les normes du dénominateur valent 1 ; normaliser ne change pas l'angle, c'est l'invariance d'échelle de l'étape 14. On obtient :

$$
\lVert \hat a - \hat b \rVert^2 = 1 + 1 - 2\cos\theta = 2\,(1 - \cos\theta)
$$

C'est l'identité démontrée à l'[étape 14](<../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>), redéveloppée ici. Comme cosθ est compris entre −1 et 1, le carré de la distance est compris entre 0 et 4, donc la distance entre 0 et 2. Elle vaut 0 pour deux vecteurs de même direction (cosθ = 1),

$$
\sqrt 2 \approx 1{,}4142
$$

pour deux vecteurs orthogonaux (cosθ = 0) et 2 pour deux vecteurs opposés (cosθ = −1).

### 4. Sur des vecteurs normalisés, L2 et cosinus donnent le même classement

On fixe une requête normalisée q̂. Pour chaque document normalisé x̂, le point 3 donne d(q̂, x̂) = f(cosθ) avec

$$
f(s) = \sqrt{2(1 - s)} .
$$

La fonction f est strictement décroissante sur [−1, 1], parce que 1 − s diminue quand s augmente et que la racine carrée est croissante. Donc, pour deux documents :

$$
\cos(\hat q, \hat x_1) > \cos(\hat q, \hat x_2) \iff d(\hat q, \hat x_1) < d(\hat q, \hat x_2)
$$

Trier par distance croissante revient exactement à trier par cosinus décroissant : le top-k en L2 et le top-k en cosinus contiennent les mêmes documents, dans le même ordre. Le même raisonnement vaut pour d², puisque x ↦ x² est strictement croissante sur les nombres positifs.

### 5. Sans normalisation, les deux classements divergent : contre-exemple

On part de la requête q = [1, 0] et de deux documents, b₁ = [10, 0] et b₂ = [0,6 ; 0,8].

- Pour b₁ :

$$
\cos = (1 \times 10 + 0 \times 0) / (1 \times 10) = 1
$$

et

$$
d = \sqrt{(1 - 10)^2 + 0^2} = \sqrt{81} = 9 .
$$

- Pour b₂ :

$$
\cos = (1 \times 0{,}6 + 0 \times 0{,}8) / (1 \times 1) = 0{,}6
$$

et

$$
d = \sqrt{(1 - 0{,}6)^2 + (0 - 0{,}8)^2} = \sqrt{0{,}16 + 0{,}64} = \sqrt{0{,}8} \approx 0{,}894 .
$$

Le cosinus classe b₁ en tête, parce qu'il pointe exactement dans la direction de la requête. La distance L2 classe b₂ en tête, parce que b₁, bien que parfaitement aligné, est dix fois plus long. Après normalisation, b̂₁ = [1, 0] coïncide avec la requête (distance 0), b₂ est déjà de norme 1 (distance 0,894), et l'ordre L2 redevient celui du cosinus. On vérifie au passage le point 3 : 0,894² = 0,8 = 2 (1 − 0,6). La leçon est pratique : sur des vecteurs non normalisés, choisir la métrique, c'est choisir le résultat.

### 6. Distance ou distance au carré : même ordre, autres seuils

Comme x ↦ x² est strictement croissante sur les nombres positifs, classer par d ou par d² donne le même ordre. Les seuils, eux, ne se recopient pas : d ≤ 0,5 équivaut à d² ≤ 0,25, et, pour des vecteurs unitaires, à cosθ ≥ 1 − 0,25/2 = 0,875. Ce point compte en pratique, parce que les bases ne renvoient pas toutes le même nombre : l'espace « l2 », réglage par défaut de Chroma, renvoie la distance **au carré**, tout comme l'index L2 de FAISS, tandis que l'opérateur `<->` de pgvector renvoie la distance elle-même.

### 7. Les coordonnées doivent être à la même échelle

Le carré amplifie les grands écarts : une coordonnée décalée de 3 apporte 9 à la somme, trois coordonnées décalées de 1 n'apportent que 3. Quand les coordonnées n'ont pas la même unité, la plus grande unité écrase les autres. Un portefeuille décrit par (transactions par heure, montant moyen en AED), comparé au comportement habituel (5 ; 2 000), le montre : la « rafale » (35 ; 2 000) est à distance

$$
\sqrt{30^2 + 0^2} = 30 ,
$$

le « montant » (5 ; 2 600) est à distance

$$
\sqrt{0^2 + 600^2} = 600 .
$$

En divisant chaque écart par l'écart-type observé (3 transactions et 500 AED), les distances deviennent 30/3 = 10 et 600/500 = 1,2 : l'anomalie réelle est la rafale. Les coordonnées d'un embedding n'ont pas d'unité propre, puisqu'elles sont toutes produites par le même modèle, et l'on ne les standardise pas une à une dans l'usage courant ; les vecteurs de caractéristiques métier, qui mélangent des unités, doivent en revanche être standardisés avant toute distance L2.

### 8. Exemple fait à la main (le code reprend ces nombres)

Avec a = [1, 2, 3] et b = [4, 6, 3] :

| Étape | Calcul | Résultat |
|---|---|---|
| écarts aᵢ − bᵢ | 1 − 4, 2 − 6, 3 − 3 | −3, −4, 0 |
| carrés | 9, 16, 0 | somme 25 |
| distance | √25 | 5 |
| contrôle par le point 2 | ‖ a ‖² = 14, ‖ b ‖² = 61, a · b = 25 | 14 + 61 − 2 × 25 = 25 |

## Effets et comportement

- **La distance suit l'échelle des vecteurs.** Multiplier les deux vecteurs par un même nombre m > 0 multiplie la distance par m, parce que ‖ m a − m b ‖ = m ‖ a − b ‖, alors que le cosinus ne bouge pas. Une valeur L2 n'a donc d'échelle fixe que sur des vecteurs normalisés, où elle vit dans [0 ; 2].
- **La distance ne bouge pas quand on translate les deux vecteurs.** Ajouter le même vecteur t à a et à b laisse a − b inchangé, donc la distance aussi ; le cosinus, lui, change, parce que les angles vus depuis l'origine changent.
- **La longueur d'un texte n'est pas la norme de son vecteur.** L'ancienne version de ce fichier affirmait que « deux textes de longueurs très différentes sur le même sujet peuvent avoir un bon cosinus mais une distance L2 plus élevée ». C'est une confusion entre la longueur du texte et la norme du vecteur. Beaucoup de modèles d'embedding renvoient des vecteurs déjà normalisés, quelle que soit la longueur du texte ; d'autres non, et la norme dépend alors du modèle et du contenu, ce qui se vérifie en calculant `norme(v)` sur quelques vecteurs. Ce qui fait diverger L2 et cosinus, c'est une différence de **norme** entre vecteurs, quelle qu'en soit la cause ; sur des vecteurs normalisés, il n'y a aucune divergence (point 4).
- **« Cosinus ou L2 ? » est souvent la mauvaise question.** L'ancienne version disait que le cosinus est « généralement préféré » pour le texte. Sur des vecteurs normalisés, les deux donnent le même classement ; la vraie décision est de normaliser ou non, puis de convertir les seuils selon ce que renvoie la base.

## Du symbole au code Python

$$
a,\quad b,\quad q
$$

**Variable ou fonction :** `a`, `b`, `q` (listes de `float`)

$$
d(a, b)
$$

**Variable ou fonction :** `distance_l2(a, b)`, ou `math.dist(a, b)` de la bibliothèque standard

$$
d(a, b)^2
$$

**Variable ou fonction :** `distance_l2_carree(a, b)`

$$
\lVert a \rVert,\quad a \cdot b
$$

**Variable ou fonction :** `norme(a)`, `produit_scalaire(a, b)`

$$
\hat a
$$

**Variable ou fonction :** `normaliser(a)`

$$
\cos\theta
$$

**Variable ou fonction :** `cosinus(a, b)`, fonction canonique du parcours

**Symbole :** classement top-k · **Variable ou fonction :** `classer_par_distance(q, docs)`, `classer_par_cosinus(q, docs)`

### Déroulé, ligne par ligne

**`cosinus(a, b)`** est la fonction canonique du parcours, recopiée telle quelle. Elle lève `ValueError` si les dimensions diffèrent ou si un vecteur est nul, puis rabat le quotient dans [−1, 1] pour absorber les erreurs d'arrondi.

**`distance_l2(a, b)`**. C'est √(∑ (aᵢ − bᵢ)²).

- `if len(a) != len(b)` : sans partenaire, l'écart aᵢ − bᵢ n'existe pas. `zip` tronquerait en silence à la plus courte des deux listes ; on préfère lever `ValueError`.
- `sum((x - y) ** 2 for x, y in zip(a, b))` : pour `a = [1.0, 2.0, 3.0]` et `b = [4.0, 6.0, 3.0]`, les écarts valent `-3.0`, `-4.0` et `0.0`, les carrés `9.0`, `16.0` et `0.0`, la somme `25.0`.
- `math.sqrt(...)` donne `5.0`. La fonction `math.dist(a, b)` de la bibliothèque standard fait le même calcul et lève, elle aussi, `ValueError` si les dimensions diffèrent.

**`distance_l2_carree(a, b)`** renvoie la même somme sans la racine : `25.0` dans l'exemple. C'est le nombre que renvoient l'espace « l2 » de Chroma et l'index L2 de FAISS.

**`norme(a)`** et **`produit_scalaire(a, b)`** calculent ‖ a ‖ et a · b : √14 et 25 dans l'exemple.

**`normaliser(a)`** divise chaque coordonnée par la norme. La garde `if n == 0.0` refuse le vecteur nul, qui n'a pas de direction : `[0.0, 0.0]` lève `ValueError` au lieu de produire une division par zéro ou, pire, un vecteur arbitraire.

**`classer_par_distance(q, docs)`** trie le dictionnaire `docs` avec la clé `(distance_l2(q, v), nom)` : distance croissante d'abord, puis nom en cas d'égalité, pour que la sortie soit la même à chaque exécution. **`classer_par_cosinus(q, docs)`** fait de même avec la clé `(-cosinus(q, v), nom)` : le signe moins trie du plus grand cosinus au plus petit.

**`standardiser(v, centre, ecarts_types)`** calcule (vᵢ − centreᵢ) / σᵢ pour chaque coordonnée. Pour la rafale `[35.0, 2000.0]`, avec le centre `[5.0, 2000.0]` et les écarts-types `[3.0, 500.0]`, elle renvoie `[10.0, 0.0]`.

**`ecart_naif(a, b)`** renvoie `a - b`, exactement ce que l'ancien code calculait avant d'appeler `np.linalg.norm`. Sur deux listes Python, cette soustraction lève `TypeError` : l'ancien code ne fonctionnait qu'avec des tableaux NumPy.

**`main()`**, bloc par bloc.

1. L'exemple du point 8. On vérifie les écarts, la somme 25, la distance 5, l'égalité avec `math.dist`, puis le développement du point 2 : `round(norme(a) ** 2, 9)` vaut 14, `round(norme(b) ** 2, 9)` vaut 61, `produit_scalaire(a, b)` vaut 25, et 14 + 61 − 50 = 25 = d². Le `round(…, 9)` efface l'erreur d'arrondi de (√14)².
2. `random.seed(20)` rend le tirage reproductible. Pour 2 000 triplets (u, v, w) de dimension 8, on vérifie les quatre axiomes du point 1. La tolérance `1e-12` de l'inégalité triangulaire absorbe les arrondis, pas une erreur de raisonnement.
3. Avec â = [1, 0] et b̂ = [0,6 ; 0,8], `distance_l2_carree` vaut 0,80 et `2 * (1 - c)` aussi (point 3). La boucle vérifie ensuite les trois valeurs remarquables : 0, √2 et 2.
4. Le contre-exemple du point 5 : cosinus 1 et distance 9 pour `b1`, cosinus 0,6 et distance 0,894 pour `b2`. `classer_par_cosinus` renvoie `['b1', 'b2']`, `classer_par_distance` renvoie `['b2', 'b1']`. Après `normaliser`, `b1` devient `[1.0, 0.0]` et le classement L2 redevient `['b1', 'b2']`.
5. `random.seed(7)`, puis 200 requêtes face à 30 documents, tous normalisés, en dimension 16. Pour chacune, les deux classements doivent être identiques (point 4) et chaque couple doit vérifier d² = 2(1 − cos) à `1e-12` près : 6 000 couples en tout.
6. Sur la dernière base tirée, le classement par `distance_l2_carree` est le même que par `distance_l2` (point 6). Le seuil `0.5` se traduit en `0.25` pour d² et en `0.875` pour le cosinus.
7. Le portefeuille du point 7 : distances brutes 30 et 600, distances standardisées 10 et 1,2.
8. Trois entrées invalides doivent lever `ValueError` : dimensions différentes pour `distance_l2` et pour `math.dist`, vecteur nul pour `normaliser`. Puis `ecart_naif` sur deux listes doit lever `TypeError`. Si l'une de ces erreurs ne se produit pas, `raise AssertionError` arrête le programme.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — C'est la boussole canonique du parcours, recopiée ici pour servir de témoin face à la règle graduée qu'est la distance : la fonction reçoit deux vecteurs, lève `ValueError` si leurs dimensions diffèrent ou si l'un d'eux est nul, calcule leurs deux normes et leur produit scalaire, puis renvoie le quotient rabattu dans [−1, 1] pour absorber les arrondis. Elle ne regarde que l'angle entre les flèches, jamais leur longueur ; c'est pourquoi, depuis la requête [1, 0], elle donne 1 au long document b1 = [10, 0] et seulement 0,6 au document b2 = [0,6 ; 0,8], et qu'elle sert de référence à tous les classements comparés dans `main`.

**`distance_l2(a, b)`** — Cette fonction joue l'arpenteur qui tend une corde droite entre deux bornes plantées dans un champ à plusieurs dimensions : elle reçoit deux vecteurs, lève `ValueError` si leurs longueurs diffèrent plutôt que de laisser `zip` tronquer en silence, fait pour chaque coordonnée la différence des deux valeurs, l'élève au carré, additionne ces carrés et renvoie la racine de la somme. Pour a = [1, 2, 3] et b = [4, 6, 3], les écarts −3, −4 et 0 donnent des carrés dont la somme vaut 25, et la distance renvoyée vaut 5, exactement comme `math.dist`. C'est l'objet même de la fiche, utilisé pour les axiomes, le contre-exemple et le portefeuille.

**`distance_l2_carree(a, b)`** — C'est la même corde d'arpenteur, mais dont on note la longueur au carré sans prendre la peine d'extraire la racine, comme le font l'espace « l2 » de Chroma et l'index L2 de FAISS : la fonction reçoit deux vecteurs, refuse par `ValueError` des dimensions différentes, et renvoie la somme des carrés des écarts, 25 dans l'exemple de base. Sur les vecteurs unitaires [1, 0] et [0,6 ; 0,8], elle vaut 0,80, soit exactement 2(1 − cos θ) ; et comme la racine ne change pas l'ordre, `main` vérifie qu'elle classe les documents comme `distance_l2`, à condition de convertir le seuil, 0,5 sur d devenant 0,25 sur d².

**`norme(a)`** — Cette petite fonction mesure la longueur d'une seule flèche, comme un tailleur qui prend la mesure d'un bras depuis l'épaule : elle reçoit un vecteur, additionne les carrés de ses coordonnées et renvoie la racine de cette somme, sans aucun contrôle, puisqu'un vecteur seul ne peut pas avoir de dimension incompatible. Pour a = [1, 2, 3], elle renvoie √14, et pour b = [4, 6, 3], √61 ; `main` s'en sert pour vérifier le développement ‖a‖² + ‖b‖² − 2 a · b = 14 + 61 − 50 = 25, et `normaliser` l'appelle pour ramener chaque vecteur à la longueur 1.

**`produit_scalaire(a, b)`** — C'est le comptable qui fait la somme des produits terme à terme, chaque coordonnée de l'une des flèches multipliée par sa partenaire dans l'autre : la fonction reçoit deux vecteurs, lève `ValueError` si leurs dimensions diffèrent, et renvoie cette somme, 25 pour a = [1, 2, 3] et b = [4, 6, 3]. Dans le programme, elle sert uniquement à vérifier l'identité qui relie la distance au carré aux deux normes et au produit scalaire, d² = ‖a‖² + ‖b‖² − 2 a · b, celle d'où découle tout le lien avec le cosinus.

**`normaliser(a)`** — Elle agit comme un atelier qui recoupe toutes les flèches à la même longueur unité sans toucher à leur direction : la fonction reçoit un vecteur, demande sa longueur à `norme`, lève `ValueError` si cette longueur est nulle, car le vecteur nul n'a aucune direction à préserver, et sinon renvoie la liste des coordonnées divisées par la norme. Le long document b1 = [10, 0] devient ainsi [1, 0], et après cette opération le classement par distance retrouve l'ordre du cosinus, b1 avant b2 ; c'est la clé de la démonstration du point 4, que `main` éprouve encore sur 200 requêtes face à 30 documents.

**`standardiser(v, centre, ecarts_types)`** — Cette fonction traduit chaque coordonnée dans une monnaie commune, l'écart-type, comme un changeur qui convertit des dirhams et des transactions par heure en une même unité avant de comparer : elle reçoit un vecteur, un centre et la liste des écarts-types, lève `ValueError` si les trois longueurs ne concordent pas, et renvoie, coordonnée par coordonnée, (vᵢ − centreᵢ) / σᵢ. Avec le centre [5, 2000] et les écarts-types [3, 500], la rafale [35, 2000] devient [10, 0] et le portefeuille au montant inhabituel [5, 2600] devient [0 ; 1,2], si bien que la rafale, invisible en distance brute (30 contre 600), redevient la plus suspecte.

**`ecart_naif(a, b)`** — Cette fonction est un témoin à charge : elle reproduit fidèlement le geste de l'ancien code, qui soustrayait directement deux vecteurs avant d'appeler NumPy. Elle reçoit deux objets et renvoie simplement a − b, ce qui fonctionne sur des tableaux NumPy mais, sur deux listes Python ordinaires, lève `TypeError`, car Python ne sait pas soustraire une liste d'une autre ; `main` provoque volontairement cette erreur avec [1, 2] et [1, 0] pour montrer pourquoi l'ancien `np.linalg.norm(a - b)` cassait.

**`main()`** — Le chef d'orchestre déroule huit vérifications : le calcul à la main de la distance 5 et de l'identité 14 + 61 − 50 = 25, puis les quatre axiomes d'une distance contrôlés sur 2 000 triplets tirés au hasard en dimension 8 avec une graine fixe, puis la relation d² = 2(1 − cos θ) sur des vecteurs unitaires et ses trois valeurs remarquables 0, √2 et 2. Viennent ensuite le contre-exemple b1 et b2, où la distance et le cosinus se contredisent jusqu'à la normalisation, la coïncidence des deux classements sur 6 000 couples normalisés, la conversion du seuil 0,5 en 0,25 et en 0,875, le portefeuille standardisé, et enfin quatre entrées invalides qui doivent lever `ValueError` ou `TypeError`, faute de quoi `AssertionError` arrête tout. La dernière ligne n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 20 — distance euclidienne (L2) : calcul, axiomes, lien avec le cosinus, contre-exemple."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cosinus(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


def distance_l2(a: list[float], b: list[float]) -> float:
    """d(a, b) = racine carrée de la somme des carrés des écarts."""
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def distance_l2_carree(a: list[float], b: list[float]) -> float:
    """d(a, b)², sans la racine : ce que renvoient l'espace « l2 » de Chroma et l'index L2 de FAISS."""
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    return sum((x - y) ** 2 for x, y in zip(a, b))


def norme(a: list[float]) -> float:
    return math.sqrt(sum(x * x for x in a))


def produit_scalaire(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    return sum(x * y for x, y in zip(a, b))


def normaliser(a: list[float]) -> list[float]:
    """â = a / ‖a‖ ; le vecteur nul n'a pas de direction."""
    n = norme(a)
    if n == 0.0:
        raise ValueError("vecteur nul : impossible de le normaliser")
    return [x / n for x in a]


def classer_par_distance(q: list[float], docs: dict[str, list[float]]) -> list[str]:
    """Du plus proche au plus lointain ; égalités départagées par le nom."""
    return [nom for nom, _ in sorted(docs.items(), key=lambda kv: (distance_l2(q, kv[1]), kv[0]))]


def classer_par_cosinus(q: list[float], docs: dict[str, list[float]]) -> list[str]:
    """Du cosinus le plus grand au plus petit ; égalités départagées par le nom."""
    return [nom for nom, _ in sorted(docs.items(), key=lambda kv: (-cosinus(q, kv[1]), kv[0]))]


def standardiser(v: list[float], centre: list[float], ecarts_types: list[float]) -> list[float]:
    """z_i = (v_i − centre_i) / écart-type_i : chaque coordonnée compte en « écarts-types »."""
    if not len(v) == len(centre) == len(ecarts_types):
        raise ValueError("dimensions différentes")
    return [(x - c) / s for x, c, s in zip(v, centre, ecarts_types)]


def ecart_naif(a, b):
    """Ce que faisait l'ancien code avant d'appeler NumPy : a − b."""
    return a - b


def main() -> None:
    print("1. Calcul à la main : a = [1, 2, 3], b = [4, 6, 3]")
    a, b = [1.0, 2.0, 3.0], [4.0, 6.0, 3.0]
    ecarts = [x - y for x, y in zip(a, b)]
    carres = [e * e for e in ecarts]
    d = distance_l2(a, b)
    print(f"  écarts = {ecarts}   carrés = {carres}   d = √{sum(carres):.0f} = {d}")
    assert ecarts == [-3.0, -4.0, 0.0] and sum(carres) == 25.0 and d == 5.0
    assert math.dist(a, b) == d
    na2, nb2, ab = round(norme(a) ** 2, 9), round(norme(b) ** 2, 9), produit_scalaire(a, b)
    print(f"  ‖a‖² + ‖b‖² − 2 a·b = {na2:.0f} + {nb2:.0f} − 2 × {ab:.0f} = {na2 + nb2 - 2 * ab:.0f} = d²")
    assert (na2, nb2, ab) == (14.0, 61.0, 25.0) and na2 + nb2 - 2 * ab == d * d

    print("2. Les axiomes d'une distance, sur 2 000 triplets aléatoires en dimension 8")
    random.seed(20)
    for _ in range(2000):
        u, v, w = ([random.uniform(-1, 1) for _ in range(8)] for _ in range(3))
        duv, dvw, duw = distance_l2(u, v), distance_l2(v, w), distance_l2(u, w)
        assert duv > 0 and distance_l2(u, u) == 0.0      # positivité et séparation
        assert duv == distance_l2(v, u)                  # symétrie
        assert duw <= duv + dvw + 1e-12                  # inégalité triangulaire
    print("  positivité, séparation, symétrie, inégalité triangulaire : vérifiées")

    print("3. Vecteurs unitaires : ‖â − b̂‖² = 2(1 − cos θ)")
    a_u, b_u = [1.0, 0.0], [0.6, 0.8]
    d2, c = distance_l2_carree(a_u, b_u), cosinus(a_u, b_u)
    print(f"  ‖â − b̂‖² = 0.4² + 0.8² = {d2:.2f}   et   2 × (1 − {c:.1f}) = {2 * (1 - c):.2f}")
    assert abs(d2 - 0.8) < 1e-12 and abs(2 * (1 - c) - 0.8) < 1e-12
    for nom, v, attendu in (("même direction", [1.0, 0.0], 0.0), ("orthogonaux", [0.0, 1.0], math.sqrt(2)),
                            ("opposés", [-1.0, 0.0], 2.0)):
        print(f"  {nom:<15} cos = {cosinus(a_u, v):+.1f}   d = {distance_l2(a_u, v):.4f}")
        assert abs(distance_l2(a_u, v) - attendu) < 1e-12

    print("4. Contre-exemple sans normalisation, depuis la requête q = [1, 0]")
    q = [1.0, 0.0]
    docs = {"b1": [10.0, 0.0], "b2": [0.6, 0.8]}
    for nom, v in docs.items():
        print(f"  {nom} = {v}   cos = {cosinus(q, v):.3f}   d = {distance_l2(q, v):.3f}")
    par_cos, par_l2 = classer_par_cosinus(q, docs), classer_par_distance(q, docs)
    print(f"  classement par cosinus = {par_cos}   classement par L2 = {par_l2}")
    assert cosinus(q, docs["b1"]) == 1.0 and distance_l2(q, docs["b1"]) == 9.0
    assert round(cosinus(q, docs["b2"]), 3) == 0.6 and round(distance_l2(q, docs["b2"]), 3) == 0.894
    assert par_cos == ["b1", "b2"] and par_l2 == ["b2", "b1"]
    unitaires = {nom: normaliser(v) for nom, v in docs.items()}
    apres = classer_par_distance(normaliser(q), unitaires)
    print(f"  après normalisation : b1 devient {unitaires['b1']} ; classement par L2 = {apres}")
    assert apres == par_cos

    print("5. Vecteurs normalisés : même classement par L2 et par cosinus (200 requêtes × 30 documents)")
    random.seed(7)
    for _ in range(200):
        qn = normaliser([random.gauss(0, 1) for _ in range(16)])
        base = {f"doc{i:02d}": normaliser([random.gauss(0, 1) for _ in range(16)]) for i in range(30)}
        assert classer_par_distance(qn, base) == classer_par_cosinus(qn, base)
        for v in base.values():
            assert abs(distance_l2_carree(qn, v) - 2 * (1 - cosinus(qn, v))) < 1e-12
    print("  6 000 couples : d² = 2(1 − cos) à 1e-12 près, et les 200 classements coïncident")

    print("6. d ou d² : même ordre, mais un seuil se convertit")
    seuil_d = 0.5
    print(f"  d ≤ {seuil_d}   ⇔   d² ≤ {seuil_d ** 2}   ⇔   cos ≥ {1 - seuil_d ** 2 / 2} (vecteurs unitaires)")
    par_d2 = [nom for nom, _ in sorted(base.items(), key=lambda kv: (distance_l2_carree(qn, kv[1]), kv[0]))]
    assert par_d2 == classer_par_distance(qn, base) and 1 - seuil_d ** 2 / 2 == 0.875

    print("7. Coordonnées d'unités différentes : standardiser avant de mesurer")
    centre, ecarts_types = [5.0, 2000.0], [3.0, 500.0]      # transactions par heure, montant moyen en AED
    portefeuilles = {"rafale": [35.0, 2000.0], "montant": [5.0, 2600.0]}
    brutes = {nom: distance_l2(v, centre) for nom, v in portefeuilles.items()}
    reduites = {nom: distance_l2(standardiser(v, centre, ecarts_types), [0.0, 0.0]) for nom, v in portefeuilles.items()}
    print(f"  brutes : rafale = {brutes['rafale']:.1f}, montant = {brutes['montant']:.1f}"
          f"   standardisées : rafale = {reduites['rafale']:.1f}, montant = {reduites['montant']:.1f}")
    assert brutes == {"rafale": 30.0, "montant": 600.0}
    assert abs(reduites["rafale"] - 10.0) < 1e-12 and abs(reduites["montant"] - 1.2) < 1e-12

    print("8. Entrées invalides refusées")
    invalides = (("distance_l2([1, 2], [1])", lambda: distance_l2([1.0, 2.0], [1.0])),
                 ("math.dist([1, 2], [1])", lambda: math.dist([1.0, 2.0], [1.0])),
                 ("normaliser([0, 0])", lambda: normaliser([0.0, 0.0])))
    for libelle, appel in invalides:
        try:
            appel()
        except ValueError:
            print(f"  {libelle} → ValueError")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    try:
        ecart_naif([1.0, 2.0], [1.0, 0.0])
    except TypeError:
        print("  [1, 2] − [1, 0] sur des listes → TypeError (l'ancien np.linalg.norm(a - b) cassait ici)")
    else:
        raise AssertionError("la soustraction de deux listes aurait dû échouer")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Calcul à la main : a = [1, 2, 3], b = [4, 6, 3]
  écarts = [-3.0, -4.0, 0.0]   carrés = [9.0, 16.0, 0.0]   d = √25 = 5.0
  ‖a‖² + ‖b‖² − 2 a·b = 14 + 61 − 2 × 25 = 25 = d²
…
  ‖â − b̂‖² = 0.4² + 0.8² = 0.80   et   2 × (1 − 0.6) = 0.80
  orthogonaux     cos = +0.0   d = 1.4142
  opposés         cos = -1.0   d = 2.0000
4. Contre-exemple sans normalisation, depuis la requête q = [1, 0]
  b1 = [10.0, 0.0]   cos = 1.000   d = 9.000
  b2 = [0.6, 0.8]   cos = 0.600   d = 0.894
  classement par cosinus = ['b1', 'b2']   classement par L2 = ['b2', 'b1']
  après normalisation : b1 devient [1.0, 0.0] ; classement par L2 = ['b1', 'b2']
…
  6 000 couples : d² = 2(1 − cos) à 1e-12 près, et les 200 classements coïncident
…
  d ≤ 0.5   ⇔   d² ≤ 0.25   ⇔   cos ≥ 0.875 (vecteurs unitaires)
…
  brutes : rafale = 30.0, montant = 600.0   standardisées : rafale = 10.0, montant = 1.2
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la distance L2 n'est qu'une somme de carrés et une racine. Elle classe comme le cosinus dès que les vecteurs sont normalisés, et autrement dès qu'ils ne le sont pas ; tout le travail d'ingénierie consiste à savoir dans quel cas on se trouve.

La même distance en NumPy, pour une base entière d'un coup (non exécuté par le harnais) :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`distance_l2_np(a, b)`** — C'est le même arpenteur que `distance_l2`, équipé cette fois d'un télémètre capable de mesurer d'un seul geste des vecteurs de milliers de coordonnées : la fonction reçoit deux séquences, listes ou tableaux, les convertit en tableaux NumPy de flottants avec `np.asarray`, ce qui corrige précisément l'ancien code qui cassait sur des listes, lève `ValueError` si leurs formes diffèrent, puis renvoie sous forme de `float` ordinaire la norme du vecteur différence calculée par `np.linalg.norm`. Les lignes commentées qui suivent montrent comment la même idée calcule en une seule instruction les N distances d'une requête à toute une matrice de documents, puis les cinq plus proches.

```python
# [extrait] — NumPy : np.asarray accepte aussi des listes, ce qui corrige l'ancien code
import numpy as np


def distance_l2_np(a, b) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("dimensions différentes")
    return float(np.linalg.norm(a - b))


# Une matrice X de forme (N, n) et une requête q de forme (n,) : N distances en une ligne.
# distances = np.linalg.norm(X - q, axis=1)
# top_k = np.argsort(distances)[:5]
```

## Squelette algorithmique

La distance euclidienne classe les documents du plus proche au plus lointain. Ce classement ne coïncide avec celui du cosinus que si les vecteurs sont normalisés ; quand les coordonnées n'ont pas la même unité, il faut d'abord les standardiser.

```text
ALGORITHME ClasserParDistance
ENTRÉES : vecteur q, documents (nom, v), option normaliser, option standardiser (centre c, écarts-types σ)
SORTIE  : les noms des documents du plus proche au plus lointain

  SI standardiser ALORS q ← (q − c) / σ ; chaque v ← (v − c) / σ          (coordonnée par coordonnée)
  SI normaliser ALORS q ← q / ‖q‖ ; chaque v ← v / ‖v‖
  POUR CHAQUE document (nom, v) FAIRE
      d²(nom) ← Σᵢ (qᵢ − vᵢ)²                     (on peut garder le carré : la racine ne change pas l'ordre)
  FIN POUR
  trier par d² croissant, égalités départagées par le nom
  RETOURNER la liste des noms

PROPRIÉTÉ utilisée : sur des vecteurs normalisés, d² = 2 (1 − cos θ), donc trier par d² croissant
                     revient à trier par cosinus décroissant.
```

**Complexité.** O(n × d) pour n documents de dimension d, plus O(n log n) pour le tri. Garder le carré de la distance évite n racines carrées sans changer l'ordre, parce que la racine est croissante. La standardisation ajoute une passe O(n × d).

**Du squelette au code.** `distance_l2` et `distance_l2_carree` calculent d et d², `normaliser` et `standardiser` les deux options, `classer_par_distance` et `classer_par_cosinus` les deux classements que le programme compare, et `produit_scalaire` et `norme` servent à vérifier l'identité ‖a − b‖² = ‖a‖² + ‖b‖² − 2 a · b. `ecart_naif` montre ce qui se passe quand on oublie la standardisation.

## Cas d'usage réels aux Émirats

Les seuils et les volumes ci-dessous sont illustratifs : en production, on les règle sur un jeu de paires étiquetées par les équipes métier.

### Immobilier — repérer la même annonce publiée trois fois

Une agence immobilière de Dubaï reçoit chaque jour des annonces de plusieurs courtiers partenaires, et le même appartement de Dubai Marina arrive souvent deux ou trois fois, avec une description reformulée et un prix légèrement différent. L'agent d'ingestion calcule l'embedding normalisé de chaque description, puis cherche dans l'index les annonces déjà présentes à une distance L2 inférieure à 0,2. Comme les vecteurs sont unitaires, ce seuil équivaut à un cosinus supérieur à 1 − 0,2²/2 = 0,98 (démonstration, point 6) : deux descriptions doivent être presque identiques pour être rapprochées. Quand un doublon probable apparaît, l'agent ne supprime rien : il rattache la nouvelle annonce à la fiche existante, compare les prix en AED/sqft et signale l'écart à l'équipe commerciale. Sans ce contrôle, un acheteur reçoit trois fois le même bien à trois prix différents, ce qui ruine la confiance et fausse le décompte du stock disponible. Les annonces doivent par ailleurs respecter les règles de la RERA sur la publicité immobilière (à confirmer avec le texte en vigueur), ce qui oblige à savoir quelle annonce fait foi. L'indicateur suivi est la part des doublons signalés que l'équipe confirme, et le nombre de doublons encore remontés par les clients.

### Banque — une migration d'index qui change la métrique sans prévenir

Une banque de détail de Dubaï migre son assistant de politique de crédit d'un index configuré en cosinus vers une base dont l'espace par défaut est « l2 ». Le modèle d'embedding retenu ne renvoie pas des vecteurs normalisés, et les vecteurs de certains passages, en particulier des introductions génériques, ont une norme nettement plus grande que les autres. Après la migration, l'agent se met à citer un paragraphe d'introduction au lieu de la règle précise sur le ratio d'endettement, exactement comme dans le contre-exemple du point 5, où un vecteur dix fois plus long passe de la première à la dernière place. L'équipe corrige en normalisant les vecteurs à l'indexation et à chaque requête, ce qui rend les deux classements identiques (point 4), et en convertissant ses seuils, puisque l'espace « l2 » renvoie d² et non d. Sans cette correction, l'agent pourrait annoncer à un client un plafond erroné, alors que la règle de la CBUAE fixe le ratio d'endettement total, toutes mensualités comprises, à 50 % du revenu (30 % pour un retraité). La banque ajoute à ses tests de non-régression un jeu de questions étiquetées et vérifie que le Recall@5 (étape 25) ne baisse pas d'une base à l'autre. En production, elle suit la part des réponses qui citent le bon article de sa politique interne.

### Crypto — une anomalie de comportement, à condition de standardiser

Une plateforme d'actifs virtuels agréée par la VARA décrit chaque portefeuille client par un petit vecteur de comportement : nombre de transactions par heure et montant moyen en AED. L'agent de surveillance calcule la distance L2 entre ce vecteur et le comportement habituel, (5 transactions, 2 000 AED), et lève une alerte au-delà d'un seuil. Ici la norme compte, car on mesure un écart réel et non une direction : L2 est le bon outil, à condition de mettre les coordonnées à la même échelle (point 7). Sans standardisation, un portefeuille qui passe à 35 transactions par heure est à distance 30, tandis qu'un portefeuille dont le montant moyen monte à 2 600 AED est à distance 600 : l'agent alerte sur le second, banal, et laisse passer le premier, qui ressemble à un automate. En divisant chaque écart par l'écart-type observé (3 transactions et 500 AED), les distances deviennent 10 et 1,2, et c'est bien la rafale qui ressort. L'alerte part vers l'équipe conformité, qui décide seule : l'agent ne gèle jamais un compte de lui-même. On suit la précision des alertes (étape 50) et le délai de traitement d'une alerte critique.

### Assurance — une déclaration de sinistre déjà vue

Un assureur auto et santé compare la description de chaque nouvelle déclaration de sinistre aux déclarations indemnisées pendant les douze derniers mois. Les embeddings sont normalisés ; une distance inférieure à 0,3, soit un cosinus supérieur à 1 − 0,09/2 = 0,955, signale une description presque identique, par exemple le même accident raconté mot pour mot sur deux polices différentes. L'agent ne refuse jamais un dossier : il le place dans la file de revue d'un enquêteur, avec les deux textes côte à côte et la distance mesurée. Sans normalisation, la distance dépendrait aussi de la norme des vecteurs et le seuil n'aurait pas de sens stable d'un lot de dossiers à l'autre. L'assurance est supervisée par la CBUAE, et une décision défavorable à un assuré doit pouvoir être expliquée : montrer les deux descriptions et la distance rend la décision de l'enquêteur explicable. L'indicateur suivi est la part des dossiers signalés que l'enquête confirme, et le nombre de dossiers retardés à tort.

### RH — le même candidat, translittéré de trois façons

Un cabinet RH présent dans plusieurs émirats reçoit des candidatures pour Dubaï, Abu Dhabi et Sharjah, et le même candidat peut s'inscrire sous « Mohammed », « Muhammad » ou « Mohamed », avec un CV légèrement différent à chaque fois. Comparer les noms seuls échoue, parce que ces trois graphies diffèrent caractère par caractère. L'agent calcule plutôt l'embedding normalisé du profil complet (expérience, diplômes, langues) et propose de fusionner deux fiches à une distance L2 inférieure à 0,25, soit un cosinus supérieur à 1 − 0,0625/2 ≈ 0,969. La fusion est proposée à un recruteur, jamais faite automatiquement, parce qu'une erreur mélangerait les données de deux personnes. Sans ce contrôle, le même candidat est contacté trois fois et les tableaux de suivi de l'Émiratisation comptent des doublons. La PDPL demande de limiter les données personnelles à ce qui est nécessaire, ce qui plaide aussi pour une fiche unique par personne. On suit le taux de doublons dans la base et le taux de fusions annulées par les recruteurs.

### Secteur public — orienter une demande vers le bon service

Un service public en ligne accessible par UAE Pass reçoit des demandes en arabe et en anglais et doit les orienter vers l'un de ses guichets : renouvellement, paiement ou réclamation. Pour chaque guichet, l'équipe calcule le centre, c'est-à-dire la moyenne des embeddings normalisés de quelques centaines de demandes étiquetées, et l'agent oriente chaque nouvelle demande vers le centre le plus proche en distance L2. Le piège est que la moyenne de vecteurs unitaires n'est pas unitaire : sa norme est inférieure à 1, d'autant plus que les demandes du groupe sont variées, et la distance au centre dépend alors de cette norme et plus seulement de l'angle, comme dans le contre-exemple du point 5. L'équipe renormalise donc chaque centre, et la distance se lit à nouveau comme un cosinus. Si la distance au centre le plus proche dépasse 0,8, soit un cosinus inférieur à 1 − 0,64/2 = 0,68, l'agent ne devine pas : il pose une question de clarification ou passe la main à un agent humain. On suit le taux d'orientation correcte et le taux de transfert vers un humain, séparément pour l'arabe et pour l'anglais.

## Pièges et limites

- **Distance ou distance au carré.** L'espace « l2 » de Chroma, réglage par défaut, et l'index L2 de FAISS renvoient d² ; l'opérateur `<->` de pgvector renvoie d. Le classement est le même, les seuils non : d ≤ 0,5 correspond à d² ≤ 0,25.
- **Normaliser d'un seul côté.** Pour une requête fixée, ‖ q ‖ est le même pour tous les documents : si les documents sont normalisés, le classement L2 est déjà celui du cosinus, même si la requête ne l'est pas. Mais la valeur de la distance, donc tout seuil, dépend alors de ‖ q ‖. On normalise les deux côtés.
- **Les moyennes de vecteurs unitaires ne sont pas unitaires.** Un centre de groupe, un profil moyen ou un « souvenir résumé » doivent être renormalisés avant d'entrer dans un calcul de distance.
- **Des coordonnées d'unités différentes faussent tout.** Sur des caractéristiques métier (montants, comptages, durées), on standardise avant de mesurer (point 7).
- **En grande dimension, les distances se resserrent.** Entre points tirés au hasard, l'écart entre le plus proche et le plus lointain voisin se réduit quand n grandit (étape 15, section 4) : un seuil réglé en dimension 384 ne se transpose pas tel quel en dimension 3072.

### Exercice feuille blanche

1. Sans regarder le code, écrire `distance_l2(a, b)` avec sa garde sur les dimensions, puis vérifier que `distance_l2([1, 2, 3], [4, 6, 3])` vaut 5.
2. Prédire, puis vérifier : deux vecteurs unitaires ont un cosinus de 0,82. Que vaut leur distance L2, et que renverrait l'espace « l2 » de Chroma ? (Réponse : d² = 2 × 0,18 = 0,36, donc d = 0,6 ; Chroma renverrait 0,36.)
3. Trouver le bug : `return math.sqrt(sum(x - y for x, y in zip(a, b)) ** 2)`. Que renvoie cette fonction pour `[1, 0]` et `[0, 1]`, et pourquoi deux vecteurs orthogonaux semblent-ils identiques ? (Indice : on additionne les écarts avant de les mettre au carré, donc +1 et −1 s'annulent.)

## Pour aller plus loin

La distance L1, ou distance de Manhattan, additionne les valeurs absolues des écarts au lieu de leurs carrés ; elle est moins sensible à un seul grand écart. Les distances de Minkowski Lₚ généralisent les deux. La distance de Mahalanobis, √((a − b)ᵀ Σ⁻¹ (a − b)), généralise la standardisation du point 7 : avec une matrice de covariance Σ diagonale, elle divise chaque écart par l'écart-type de sa coordonnée ; avec une matrice pleine, elle tient compte en plus des corrélations entre coordonnées. Pour chercher parmi des millions de vecteurs, les index approchés renoncent au calcul exact sur toute la base : un graphe HNSW n'évalue la distance que sur une petite partie des vecteurs, et la quantification par produit compresse les vecteurs pour calculer des distances approchées. Dans les deux cas, on paie la vitesse par un rappel légèrement inférieur à 1, que l'on mesure avec le Recall@k de l'étape 25.

> Suite : [Distance cosinus](<21-RAG-Formule-Distance-Cosinus.md>) — étape 21.
