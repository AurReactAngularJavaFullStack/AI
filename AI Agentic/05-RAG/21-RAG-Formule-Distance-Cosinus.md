# Étape 21 — RAG — Distance cosinus

> Étape 21 du parcours · Prérequis : [Distance euclidienne](<20-RAG-Formule-Distance-Euclidienne.md>) · Suite : [BM25](<22-RAG-Formule-BM25.md>)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  
**Nom du fichier :** 21-RAG-Formule-Distance-Cosinus.md

## Définition

La distance cosinus est le complément à 1 de la similarité cosinus de l'étape 19 :

$$
d_{\cos}(a, b) = 1 - \cos\theta .
$$

Elle transforme une similarité, où « plus grand » veut dire « plus proche », en un nombre où « plus petit » veut dire « plus proche », parce que beaucoup d'index vectoriels sont écrits pour minimiser une distance. Elle vaut 0 pour deux vecteurs de même direction, 1 pour deux vecteurs orthogonaux et 2 pour deux vecteurs de directions opposées. Malgré son nom, ce n'est pas une distance au sens mathématique : elle ne vérifie pas l'inégalité triangulaire, et elle vaut 0 pour deux vecteurs différents qui ont la même direction. La distance angulaire θ / π, elle, est une vraie distance entre directions, et elle classe les documents exactement dans le même ordre.

## Rôle dans un agent

Quand l'agent perçoit une question, le **retriever** l'encode puis demande à la base les k passages les plus proches ; avec pgvector, la requête SQL trie par `embedding <=> requete`, c'est-à-dire par distance cosinus croissante. L'agent décide ensuite s'il peut répondre : si le meilleur passage est à une distance inférieure au seuil fixé, il l'injecte dans le prompt et le cite ; sinon il pose une question de clarification ou passe la main à un humain. La même distance sert à la **mémoire** pour repérer deux souvenirs presque identiques, et à un **garde-fou** pour écarter une question trop éloignée du domaine de l'agent. Dans tous ces cas, l'erreur la plus fréquente n'est pas mathématique mais opérationnelle : lire une distance comme une similarité, ou recopier un seuil d'une base à une autre sans le convertir.

## Équation complète

Distance cosinus :

$$
d_{\cos}(a, b) = 1 - \cos\theta = 1 - \frac{a \cdot b}{\lVert a \rVert \, \lVert b \rVert}
$$

Pour des vecteurs normalisés, lien avec la distance euclidienne de l'étape 20 :

$$
d_{\cos}(\hat a, \hat b) = \frac{\lVert \hat a - \hat b \rVert^2}{2}
$$

Distance angulaire normalisée, une vraie distance :

$$
d_{ang}(a, b) = \frac{\arccos(\cos\theta)}{\pi} = \frac{\theta}{\pi}
$$

## Décryptage des symboles

$$
a,\quad b
$$

**Sens :** vecteurs d'embedding · **Type / plage :** listes de n réels, non nuls · **Variable Python :** `a`, `b`

$$
\cos\theta
$$

**Sens :** similarité cosinus de l'étape 19 · **Type / plage :** réel dans [−1, 1] · **Variable Python :** `cosinus(a, b)`

$$
\theta
$$

**Sens :** angle entre les deux vecteurs · **Type / plage :** radians, dans [0, π] · **Variable Python :** `math.acos(cosinus(a, b))`

$$
d_{\cos}(a, b)
$$

**Sens :** distance cosinus · **Type / plage :** réel dans [0, 2] · **Variable Python :** `distance_cosinus(a, b)`

$$
d_{ang}(a, b)
$$

**Sens :** distance angulaire normalisée · **Type / plage :** réel dans [0, 1] · **Variable Python :** `distance_angulaire(a, b)`

$$
\hat a
$$

**Sens :** vecteur normalisé a / ‖ a ‖ · **Type / plage :** norme 1 · **Variable Python :** `normaliser(a)`

$$
\lVert \hat a - \hat b \rVert
$$

**Sens :** distance L2 entre vecteurs normalisés (étape 20) · **Type / plage :** réel dans [0, 2] · **Variable Python :** `math.dist(a, b)`

$$
\tau
$$

**Sens :** seuil de décision, exprimé sur le cosinus · **Type / plage :** réel dans [−1, 1] · **Variable Python :** `tau`

## Démonstration

### 1. Bornes et valeurs remarquables

L'inégalité de Cauchy-Schwarz, démontrée à l'[étape 14](<../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>), donne −1 ≤ cosθ ≤ 1. En multipliant par −1, ce qui renverse les inégalités, puis en ajoutant 1, on obtient 0 ≤ 1 − cosθ ≤ 2. La distance vaut 0 quand cosθ = 1 (même direction), 1 quand cosθ = 0 (vecteurs orthogonaux) et 2 quand cosθ = −1 (directions opposées). L'ancienne version de ce fichier annonçait un cosinus « souvent de 0 à 1 pour les embeddings de texte » : c'est une tendance observée avec beaucoup de modèles, pas une propriété ; rien ne garantit qu'un cosinus soit positif, et le code doit prévoir toute la plage [0, 2] pour la distance.

### 2. Elle ne voit que la direction

Pour tout nombre m > 0,

$$
d_{\cos}(m\,a, b) = d_{\cos}(a, b) ,
$$

parce que le cosinus est invariant par changement d'échelle (étape 14) : le facteur m apparaît au numérateur et au dénominateur, et se simplifie. Conséquence :

$$
d_{\cos}([1, 0], [3, 0]) = 1 - 3/3 = 0
$$

alors que les deux vecteurs sont différents. L'axiome de séparation d'une distance (d = 0 seulement pour deux points identiques) est donc en défaut sur les vecteurs eux-mêmes ; la distance cosinus compare des **directions**. Sur des vecteurs normalisés, une direction correspond à un seul vecteur, et ce défaut disparaît.

### 3. Lien avec la distance L2 sur la sphère unité

L'étape 20 a établi, pour des vecteurs normalisés, ‖ â − b̂ ‖² = 2 (1 − cosθ). En divisant par 2 :

$$
d_{\cos}(\hat a, \hat b) = 1 - \cos\theta = \frac{\lVert \hat a - \hat b \rVert^2}{2}
$$

La distance cosinus est donc la **moitié du carré** d'une vraie distance. Avec a = [1, 0] et b = [0,6 ; 0,8] : 1 − 0,6 = 0,4, et ‖ a − b ‖² = 0,4² + 0,8² = 0,8, dont la moitié vaut bien 0,4. La formule de l'angle double, cosθ = 1 − 2sin²(θ/2), donne aussi

$$
d_{\cos} = 2 \sin^2(\theta/2) .
$$

Pour un petit angle, sin(θ/2) ≈ θ/2, donc

$$
d_{\cos} \approx \theta^2 / 2
$$

Doubler un petit angle multiplie la distance cosinus par environ 4. En chiffres, 1 − cos 10° = 0,0152 et 1 − cos 20° = 0,0603, soit un rapport de 3,97.

### 4. Ce n'est pas une distance : contre-exemple chiffré

On prend trois vecteurs unitaires : a = [1, 0],

$$
b = [1, 1]/\sqrt 2
$$

et c = [0, 1]. Les cosinus valent

$$
\cos(a, b) = 1/\sqrt 2 \approx 0{,}7071 ,
$$

$$
\cos(b, c) = 1/\sqrt 2
$$

et cos(a, c) = 0. D'où :

$$
d_{\cos}(a, b) + d_{\cos}(b, c) = 0{,}293 + 0{,}293 = 0{,}586 < 1 = d_{\cos}(a, c)
$$

Passer par b « coûte » moins cher que d'aller directement de a à c : l'inégalité triangulaire est violée. La raison est celle du point 3. Les longueurs des cordes, elles, la respectent :

$$
\lVert a - b \rVert + \lVert b - c \rVert = 0{,}7654 + 0{,}7654 = 1{,}5307 \ge 1{,}4142 = \lVert a - c \rVert .
$$

Mais la distance cosinus est la moitié de leurs **carrés**, et le carré pénalise les grands sauts : pour x, y > 0, (x + y)² = x² + 2xy + y² > x² + y². Un grand saut coûte donc plus cher que deux demi-sauts. En pratique, les structures d'index qui élaguent des branches entières grâce à l'inégalité triangulaire (arbres métriques comme le *ball tree* ou le *VP-tree*) peuvent écarter à tort un vrai voisin si on leur donne 1 − cos ; les index en graphe comme HNSW l'acceptent sans difficulté.

### 5. La distance angulaire est une vraie distance

On travaille sur des vecteurs unitaires et l'on note

$$
\theta(u, v) = \arccos(u \cdot v) ,
$$

à valeurs dans [0, π]. La positivité vient de ce que

$$
\arccos
$$

prend ses valeurs dans [0, π] ; la symétrie, de ce que u · v = v · u ; la séparation, de ce que θ(u, v) = 0 équivaut à u · v = 1, donc à ‖ u − v ‖² = 2 − 2 u · v = 0, donc à u = v.

Reste l'inégalité triangulaire. Soient a, b, c unitaires, α = θ(a, b) et γ = θ(b, c). On décompose a selon b : sa composante le long de b est (a · b) b = cosα b, et le reste a − cosα b est orthogonal à b, de norme

$$
\sqrt{1 - \cos^2\alpha} = \sin\alpha
$$

par le théorème de Pythagore, puisque ‖ a ‖ = 1. On écrit donc a = cosα b + sinα u et, de même, c = cosγ b + sinγ w, où u et w sont des vecteurs unitaires orthogonaux à b (si sinα = 0, n'importe quel u convient, puisque son coefficient est nul). En développant le produit scalaire, et parce que b · b = 1 et b · u = b · w = 0 :

$$
a \cdot c = \cos\alpha \cos\gamma + \sin\alpha \sin\gamma \; (u \cdot w)
$$

Les sinus sont positifs ou nuls, parce que α et γ sont dans [0, π], et u · w ≥ −1 par Cauchy-Schwarz. Donc

$$
a \cdot c \ge \cos\alpha \cos\gamma - \sin\alpha \sin\gamma = \cos(\alpha + \gamma) .
$$

Si α + γ ≤ π, comme

$$
\arccos
$$

est décroissante,

$$
\theta(a, c) = \arccos(a \cdot c) \le \arccos(\cos(\alpha + \gamma)) = \alpha + \gamma .
$$

Si α + γ > π, l'inégalité est immédiate, puisque θ(a, c) ≤ π. Dans les deux cas, θ(a, c) ≤ θ(a, b) + θ(b, c), et la division par π conserve l'inégalité. Sur le contre-exemple du point 4 : 0,25 + 0,25 = 0,5 ≥ 0,5, avec égalité parce que b est exactement à mi-chemin sur l'arc qui va de a à c.

### 6. Les trois mesures donnent le même classement

Sur des vecteurs normalisés,

$$
d_{\cos} = 1 - s ,
$$

$$
d_{ang} = \arccos(s)/\pi
$$

et

$$
d_{L2} = \sqrt{2(1 - s)}
$$

sont trois fonctions strictement décroissantes du cosinus s sur [−1, 1] : 1 − s diminue quand s augmente,

$$
\arccos
$$

est décroissante, et la racine carrée est croissante. Trier par l'une d'elles, en ordre croissant, revient donc à trier par cosinus décroissant : les trois top-k sont identiques. Ce qui change d'une mesure à l'autre, ce sont les **valeurs**, donc les seuils, et le respect de l'inégalité triangulaire.

### 7. Ce que renvoient les bases, et comment convertir un seuil

| Base et réglage | Nombre renvoyé | Le meilleur est | Cosinus retrouvé à partir de la valeur v |
|---|---|---|---|
| pgvector, opérateur `<=>` | 1 − cosθ | le plus petit | 1 − v |
| Chroma, espace « cosine » | 1 − cosθ | le plus petit | 1 − v |
| FAISS : vecteurs normalisés, puis index en produit scalaire | â · b̂ = cosθ | le plus grand | v |
| Chroma, espace « l2 » ; FAISS, index L2 (vecteurs normalisés) | ‖ â − b̂ ‖² | le plus petit | 1 − v/2 |
| pgvector, opérateur `<->` (vecteurs normalisés) | ‖ â − b̂ ‖ | le plus petit | 1 − v²/2 |

FAISS n'a pas de cosinus natif : on normalise les vecteurs, à l'indexation comme à la requête, puis on utilise un index en produit scalaire, qui renvoie alors directement le cosinus, une **similarité**. Une version antérieure de cette fiche affirmait que « certains index vectoriels (FAISS, etc.) optimisent sur la distance plutôt que sur la similarité » : c'est inexact pour FAISS en cosinus, et c'est justement en sachant qui renvoie quoi que l'on règle correctement un seuil. Pour un seuil de décision τ = 0,8 sur le cosinus, les seuils équivalents valent, pour des vecteurs unitaires :

$$
\cos\theta \ge 0{,}8 \iff d_{\cos} \le 0{,}2 \iff \lVert \hat a - \hat b \rVert^2 \le 0{,}4 \iff \lVert \hat a - \hat b \rVert \le 0{,}6325 \iff \theta \le 36{,}87°
$$

### 8. Exemple fait à la main (le code reprend ces nombres)

$$
\cos\theta
$$

**a = [1, 0], b = [0,6 ; 0,8] :** 0,6 · **Contre-exemple : d(a, b), d(b, c), d(a, c) :** 0,7071 ; 0,7071 ; 0

$$
d_{\cos} = 1 - \cos\theta
$$

**a = [1, 0], b = [0,6 ; 0,8] :** 0,4 · **Contre-exemple : d(a, b), d(b, c), d(a, c) :** 0,293 ; 0,293 ; 1

$$
\lVert \hat a - \hat b \rVert^2 / 2
$$

**a = [1, 0], b = [0,6 ; 0,8] :** 0,8 / 2 = 0,4 · **Contre-exemple : d(a, b), d(b, c), d(a, c) :** identique à la ligne précédente

$$
\theta
$$

**a = [1, 0], b = [0,6 ; 0,8] :** 53,13° · **Contre-exemple : d(a, b), d(b, c), d(a, c) :** 45° ; 45° ; 90°

$$
d_{ang} = \theta/\pi
$$

**a = [1, 0], b = [0,6 ; 0,8] :** 0,2952 · **Contre-exemple : d(a, b), d(b, c), d(a, c) :** 0,25 ; 0,25 ; 0,5

## Effets et comportement

- **0, 1 et 2 ont un sens précis.** L'ancienne version disait « plus elle se rapproche de 1 (ou 2), plus les vecteurs sont éloignés ». Plus précisément : 1 signifie « orthogonaux », c'est-à-dire cosinus nul, et 2 « directions opposées ». Une distance de 0,2 ne veut pas dire « 20 % différents ».
- **Près de 0, la distance croît comme le carré de l'angle** (point 3) : entre deux bons candidats à 0,015 et 0,060, l'angle a seulement doublé.
- **La distance cosinus ne dépend que de la direction** (point 2) : elle ignore la norme, exactement comme le cosinus.
- **Le vecteur nul n'a pas de distance cosinus.** L'ancien code ajoutait `1e-8` au dénominateur. Pour un vecteur nul, le produit scalaire vaut 0, le quotient vaut 0 et la fonction renvoyait 1 en silence : le document paraissait « orthogonal » et restait au milieu du classement, au lieu de signaler une donnée corrompue. La version corrigée hérite du `ValueError` du cosinus canonique.
- **Les classements ne changent pas, les seuils si** (points 6 et 7).

## Du symbole au code Python

$$
\cos\theta
$$

**Variable ou fonction :** `cosinus(a, b)`, fonction canonique du parcours

$$
d_{\cos}
$$

**Variable ou fonction :** `distance_cosinus(a, b)`

$$
d_{ang}
$$

**Variable ou fonction :** `distance_angulaire(a, b)`

$$
\lVert \hat a - \hat b \rVert
$$

**Variable ou fonction :** `math.dist(a, b)` sur des vecteurs normalisés

**Symbole :** τ et ses équivalents · **Variable ou fonction :** `seuils_equivalents(tau)`

**Symbole :** conversion d'un renvoi de base · **Variable ou fonction :** `similarite_depuis(valeur, renvoi)`

### Déroulé, ligne par ligne

**`cosinus(a, b)`** est la fonction canonique de l'étape 19 : `ValueError` si les dimensions diffèrent ou si un vecteur est nul, puis rabattement dans [−1, 1].

**`distance_cosinus(a, b)`** renvoie `1.0 - cosinus(a, b)`. Elle n'a besoin d'aucune garde propre : si un vecteur est nul, `cosinus` lève déjà `ValueError`. Pour `a = [1.0, 0.0]` et `b = [0.6, 0.8]`, elle renvoie 0,4.

**`distance_angulaire(a, b)`** renvoie `math.acos(cosinus(a, b)) / math.pi`. Le rabattement du cosinus dans [−1, 1] est indispensable ici : `math.acos(1.0000000000000002)` lèverait `ValueError`. Pour le même couple, `math.acos(0.6)` vaut 0,9273 radian, soit 53,13°, et la fonction renvoie 0,2952.

**`normaliser(a)`** divise chaque coordonnée par la norme et refuse le vecteur nul.

**`ancienne_distance_cosinus(a, b)`** est l'ancien code, traduit sans NumPy pour pouvoir l'exécuter : `na * nb + eps` au dénominateur. Avec `b = [0.0, 0.0]`, `nb` vaut 0, le dénominateur vaut `1e-8`, le numérateur vaut 0 et la fonction renvoie `1.0` sans rien signaler.

**`similarite_depuis(valeur, renvoi)`** applique la dernière colonne du tableau du point 7. Pour `"L2 au carré"`, elle renvoie `1 - valeur / 2` : avec `valeur = 0.8`, on retrouve 0,6.

**`seuils_equivalents(tau)`** calcule les quatre seuils du point 7. Pour `tau = 0.8` : `1 - 0.8 = 0.2`, `2 * 0.2 = 0.4`, `math.sqrt(0.4) = 0.6325`, et `math.degrees(math.acos(0.8)) = 36.87`.

**`classer(q, docs, distance)`** trie les documents par `(distance(q, v), nom)` : on lui passe `distance_cosinus`, `distance_angulaire` ou `math.dist`, ce qui permet de comparer les trois classements avec le même code.

**`main()`**, bloc par bloc.

1. Depuis `a = [1.0, 0.0]`, trois vecteurs donnent 0, 1 et 2 (point 1). `[3.0, 0.0]` donne 0 alors qu'il diffère de `a` : c'est le défaut de séparation du point 2.
2. Le couple `a`, `b` du point 8 : `1 - cos` vaut 0,40, `math.dist(a, b) ** 2` vaut 0,80, dont la moitié vaut 0,40 (point 3) ; l'angle vaut 53,13° et `distance_angulaire` 0,2952. Les petits angles donnent 0,0152 et 0,0603. Puis 1 000 couples aléatoires normalisés vérifient l'identité à `1e-12` près.
3. Le contre-exemple du point 4 : `r = 1 / math.sqrt(2)`, puis 0,293 + 0,293 = 0,586 < 1. Les cordes `math.dist` vérifient, elles, l'inégalité.
4. La distance angulaire sur les mêmes points : 0,25 + 0,25 ≥ 0,5. Sur 2 000 triplets aléatoires en dimension 3, on compte les violations : plusieurs centaines pour `distance_cosinus`, aucune pour `distance_angulaire` (point 5).
5. 200 requêtes face à 25 documents normalisés : `classer` donne le même ordre avec les trois mesures (point 6).
6. `seuils_equivalents(0.8)` affiche les quatre seuils ; puis, pour le couple `a`, `b`, les quatre nombres que renverraient les bases du tableau, une fois passés dans `similarite_depuis`, redonnent tous 0,6.
7. Le vecteur nul : l'ancienne fonction renvoie 1,0, la nouvelle lève `ValueError` ; si elle ne le faisait pas, `raise AssertionError` arrêterait le programme.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — C'est la boussole canonique de l'étape 19, que toutes les autres mesures de ce programme consultent avant de rendre leur verdict : la fonction reçoit deux vecteurs, lève `ValueError` si leurs dimensions diffèrent ou si l'un d'eux est nul, calcule le produit scalaire divisé par le produit des normes, puis rabat ce quotient dans [−1, 1] pour qu'un arrondi ne le fasse jamais déborder. Elle renvoie ainsi 0,6 pour a = [1, 0] et b = [0,6 ; 0,8], et ce rabattement n'est pas un luxe, puisque `distance_angulaire` passe son résultat à `math.acos`, qui refuserait 1,0000000000000002.

**`distance_cosinus(a, b)`** — Cette fonction retourne la boussole pour en faire une règle : au lieu de dire combien deux directions se ressemblent, elle dit combien elles s'éloignent, en renvoyant simplement 1 − cos θ, un nombre compris entre 0 pour deux flèches alignées et 2 pour deux flèches opposées. Elle reçoit deux vecteurs et n'a besoin d'aucune garde propre, car si l'un d'eux est nul, `cosinus` lève déjà `ValueError` ; pour a et b, elle vaut 0,4, soit la moitié du carré 0,80 de leur distance L2. Le programme s'en sert pour montrer à la fois sa commodité et ses défauts : elle donne 0 au vecteur [3, 0] qui diffère pourtant de a, et viole l'inégalité triangulaire.

**`distance_angulaire(a, b)`** — Celle-ci mesure le chemin qu'un marcheur parcourrait sur le cercle pour passer d'une direction à l'autre, rapporté au demi-tour complet : la fonction reçoit deux vecteurs, demande leur cosinus à `cosinus`, en tire l'angle θ par `math.acos`, puis renvoie θ / π, un nombre entre 0 et 1. Pour a et b, l'angle vaut 53,13° et la fonction rend 0,2952 ; sur les trois points du contre-exemple, elle donne 0,25 + 0,25 = 0,5, exactement la distance de a à c. Contrairement à 1 − cos θ, c'est une vraie distance, et `main` le confirme en ne lui trouvant aucune violation de l'inégalité triangulaire sur 2 000 triplets tirés au hasard.

**`normaliser(a)`** — On peut l'imaginer comme un tailleur de flèches qui les recoupe toutes à la longueur exacte de 1 sans dévier leur pointe : la fonction reçoit un vecteur, calcule sa norme, lève `ValueError` si elle est nulle, car le vecteur nul n'a pas de direction, et renvoie la liste de ses coordonnées divisées par cette norme. Le programme l'utilise pour préparer les 1 000 couples sur lesquels il vérifie l'identité 1 − cos θ = ‖â − b̂‖² / 2, puis les 200 requêtes et 25 documents sur lesquels les trois mesures de distance donnent le même classement.

**`ancienne_distance_cosinus(a, b, eps)`** — Cette fonction est la pièce à conviction du dossier : elle reproduit sans NumPy l'ancien code, qui ajoutait un petit epsilon, `1e-8` par défaut, au produit des normes pour ne jamais diviser par zéro. Elle reçoit deux vecteurs et cet epsilon, calcule les normes et le produit scalaire, et renvoie 1 moins le produit divisé par le dénominateur gonflé ; avec le vecteur nul [0, 0], le numérateur vaut 0 et elle renvoie 1,0 sans rien signaler, comme si les deux textes étaient simplement orthogonaux. `main` la confronte à `distance_cosinus`, qui, elle, refuse ce vecteur par `ValueError`.

**`similarite_depuis(valeur, renvoi)`** — C'est un interprète polyglotte qui traduit en cosinus le nombre que renvoie chaque base vectorielle, chacune parlant sa propre langue : la fonction reçoit la valeur renvoyée et le nom de la convention, puis renvoie 1 − valeur pour « 1 - cos », la valeur telle quelle pour « produit scalaire », 1 − valeur / 2 pour « L2 au carré » et 1 − valeur² / 2 pour « L2 », les trois derniers cas supposant des vecteurs normalisés. Toute autre convention lève `ValueError`. Le programme vérifie que, pour a et b, les quatre nombres renvoyés par les bases redonnent tous le même cosinus 0,6.

**`seuils_equivalents(tau)`** — Elle joue le traducteur de consignes : on lui donne un seuil de similarité exprimé en cosinus, et elle le réécrit dans l'unité de chaque base, comme on convertirait une limite de vitesse en kilomètres et en miles. Elle reçoit τ, lève `ValueError` s'il sort de [−1, 1], et renvoie un dictionnaire de quatre seuils valables pour des vecteurs unitaires : 1 − τ pour la distance cosinus, 2(1 − τ) pour la L2 au carré, sa racine pour la L2 et arccos τ en degrés pour l'angle. Pour τ = 0,8, elle donne 0,2, 0,4, 0,6325 et 36,87°.

**`classer(q, docs, distance)`** — Cette fonction est un juge de course impartial qui accepte n'importe quel chronomètre : elle reçoit le vecteur de la requête, un dictionnaire de documents et la fonction de distance à utiliser, trie les documents par distance croissante en départageant les égalités par leur nom, et renvoie la liste ordonnée de leurs noms. Comme on peut lui passer `distance_cosinus`, `distance_angulaire` ou `math.dist`, le même code sert à vérifier que les trois mesures produisent exactement le même classement sur des vecteurs normalisés, pour 200 requêtes face à 25 documents.

**`main()`** — Le chef d'orchestre mène sept épreuves : les bornes 0, 1 et 2 de 1 − cos θ et son défaut de séparation, puis l'identité avec la L2 au carré sur le couple a, b, les petits angles de 10° et 20° qui donnent 0,0152 et 0,0603, et 1 000 couples aléatoires. Il exhibe ensuite le contre-exemple où 0,293 + 0,293 = 0,586 reste inférieur à 1, montre que la distance angulaire, elle, respecte l'inégalité et ne compte aucune violation sur 2 000 triplets, vérifie la coïncidence des trois classements, traduit le seuil 0,8 pour chaque base, et termine en opposant l'ancien epsilon, qui répond 1,0 en silence, à la nouvelle fonction qui lève `ValueError`. Chaque nombre est gardé par un `assert`, et la ligne finale n'annonce le succès que si tous ont tenu.

```python
"""Étape 21 — distance cosinus : 1 − cos, lien avec L2, inégalité triangulaire, distance angulaire, seuils."""
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


def distance_cosinus(a: list[float], b: list[float]) -> float:
    """1 − cos θ, dans [0, 2]. Un vecteur nul lève ValueError (hérité de cosinus)."""
    return 1.0 - cosinus(a, b)


def distance_angulaire(a: list[float], b: list[float]) -> float:
    """θ / π, dans [0, 1] : une vraie distance entre directions."""
    return math.acos(cosinus(a, b)) / math.pi


def normaliser(a: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in a))
    if n == 0.0:
        raise ValueError("vecteur nul : impossible de le normaliser")
    return [x / n for x in a]


def ancienne_distance_cosinus(a: list[float], b: list[float], eps: float = 1e-8) -> float:
    """L'ancienne version, traduite sans NumPy : l'epsilon masque le vecteur nul."""
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return 1.0 - sum(x * y for x, y in zip(a, b)) / (na * nb + eps)


def similarite_depuis(valeur: float, renvoi: str) -> float:
    """Ramène au cosinus le nombre renvoyé par une base (vecteurs normalisés pour les trois derniers cas)."""
    if renvoi == "1 - cos":          # pgvector <=>, espace « cosine » de Chroma
        return 1.0 - valeur
    if renvoi == "produit scalaire":  # FAISS IndexFlatIP sur vecteurs normalisés
        return valeur
    if renvoi == "L2 au carré":       # espace « l2 » de Chroma, IndexFlatL2 de FAISS
        return 1.0 - valeur / 2.0
    if renvoi == "L2":                # pgvector <->
        return 1.0 - valeur * valeur / 2.0
    raise ValueError(f"renvoi inconnu : {renvoi}")


def seuils_equivalents(tau: float) -> dict[str, float]:
    """Vecteurs unitaires : cos ≥ τ ⇔ 1 − cos ≤ 1 − τ ⇔ d² ≤ 2(1 − τ) ⇔ θ ≤ arccos τ."""
    if not -1.0 <= tau <= 1.0:
        raise ValueError("un seuil de cosinus est dans [-1, 1]")
    return {"distance cosinus ≤": 1.0 - tau, "L2 au carré ≤": 2.0 * (1.0 - tau),
            "L2 ≤": math.sqrt(2.0 * (1.0 - tau)), "angle en degrés ≤": math.degrees(math.acos(tau))}


def classer(q: list[float], docs: dict[str, list[float]], distance) -> list[str]:
    return [nom for nom, _ in sorted(docs.items(), key=lambda kv: (distance(q, kv[1]), kv[0]))]


def main() -> None:
    print("1. Bornes : 1 − cos θ va de 0 (même direction) à 2 (directions opposées)")
    a = [1.0, 0.0]
    for nom, v, attendu in (("même direction [3, 0]", [3.0, 0.0], 0.0), ("orthogonal [0, 2]", [0.0, 2.0], 1.0),
                            ("opposé [-1, 0]", [-1.0, 0.0], 2.0)):
        d = distance_cosinus(a, v)
        print(f"  {nom:<22} 1 − cos = {d:.1f}")
        assert d == attendu
    assert distance_cosinus(a, [3.0, 0.0]) == 0.0 and [3.0, 0.0] != a   # séparation en défaut sur les vecteurs bruts

    print("2. Vecteurs unitaires : 1 − cos θ = ‖â − b̂‖² / 2   (a = [1, 0], b = [0.6, 0.8])")
    b = [0.6, 0.8]
    l2_carre = math.dist(a, b) ** 2
    theta = math.degrees(math.acos(cosinus(a, b)))
    print(f"  1 − cos = {distance_cosinus(a, b):.2f}   ‖â − b̂‖² / 2 = {l2_carre:.2f} / 2 = {l2_carre / 2:.2f}"
          f"   θ = {theta:.2f}°   θ/π = {distance_angulaire(a, b):.4f}")
    assert abs(distance_cosinus(a, b) - 0.4) < 1e-12 and abs(l2_carre / 2 - 0.4) < 1e-12
    assert round(theta, 2) == 53.13 and round(distance_angulaire(a, b), 4) == 0.2952
    petits = [1 - math.cos(math.radians(deg)) for deg in (10, 20)]
    print(f"  petits angles : 1 − cos 10° = {petits[0]:.4f}, 1 − cos 20° = {petits[1]:.4f} (rapport {petits[1] / petits[0]:.2f})")
    assert [round(x, 4) for x in petits] == [0.0152, 0.0603] and 3.9 < petits[1] / petits[0] < 4.0
    random.seed(21)
    for _ in range(1000):
        u, v = normaliser([random.gauss(0, 1) for _ in range(12)]), normaliser([random.gauss(0, 1) for _ in range(12)])
        assert abs(distance_cosinus(u, v) - math.dist(u, v) ** 2 / 2) < 1e-12

    print("3. Contre-exemple : 1 − cos θ viole l'inégalité triangulaire")
    r = 1 / math.sqrt(2)
    p_a, p_b, p_c = [1.0, 0.0], [r, r], [0.0, 1.0]
    dab, dbc, dac = distance_cosinus(p_a, p_b), distance_cosinus(p_b, p_c), distance_cosinus(p_a, p_c)
    print(f"  d(a,b) + d(b,c) = {dab:.3f} + {dbc:.3f} = {dab + dbc:.3f}  <  d(a,c) = {dac:.3f}")
    assert round(dab, 3) == 0.293 and round(dbc, 3) == 0.293 and round(dab + dbc, 3) == 0.586
    assert abs(dac - 1.0) < 1e-12 and dab + dbc < dac
    cordes = (math.dist(p_a, p_b), math.dist(p_b, p_c), math.dist(p_a, p_c))
    print(f"  la distance L2 la respecte : {cordes[0]:.4f} + {cordes[1]:.4f} = {cordes[0] + cordes[1]:.4f} ≥ {cordes[2]:.4f}")
    assert cordes[0] + cordes[1] >= cordes[2]

    print("4. La distance angulaire θ/π la respecte")
    gab, gbc, gac = distance_angulaire(p_a, p_b), distance_angulaire(p_b, p_c), distance_angulaire(p_a, p_c)
    print(f"  {gab:.2f} + {gbc:.2f} = {gab + gbc:.2f} ≥ {gac:.2f}   (45° + 45° = 90° : b est sur le chemin de a à c)")
    assert abs(gab - 0.25) < 1e-12 and abs(gbc - 0.25) < 1e-12 and abs(gac - 0.5) < 1e-12
    random.seed(4)
    violations_cos = violations_ang = 0
    for _ in range(2000):
        u, v, w = ([random.gauss(0, 1) for _ in range(3)] for _ in range(3))
        if distance_cosinus(u, w) > distance_cosinus(u, v) + distance_cosinus(v, w) + 1e-12:
            violations_cos += 1
        if distance_angulaire(u, w) > distance_angulaire(u, v) + distance_angulaire(v, w) + 1e-12:
            violations_ang += 1
    print(f"  2 000 triplets aléatoires : {violations_cos} violations pour 1 − cos, {violations_ang} pour θ/π")
    assert violations_cos > 0 and violations_ang == 0

    print("5. Même classement par 1 − cos, par θ/π et par L2 sur vecteurs normalisés")
    random.seed(5)
    for _ in range(200):
        q = normaliser([random.gauss(0, 1) for _ in range(16)])
        base = {f"doc{i:02d}": normaliser([random.gauss(0, 1) for _ in range(16)]) for i in range(25)}
        ordre = classer(q, base, distance_cosinus)
        assert ordre == classer(q, base, distance_angulaire) == classer(q, base, math.dist)
    print("  200 requêtes × 25 documents : les trois classements coïncident")

    print("6. Un seuil de similarité 0.8, traduit pour chaque base")
    for nom, valeur in seuils_equivalents(0.8).items():
        print(f"  {nom:<19} {valeur:.4f}")
    s = seuils_equivalents(0.8)
    assert abs(s["distance cosinus ≤"] - 0.2) < 1e-12 and abs(s["L2 au carré ≤"] - 0.4) < 1e-12
    assert round(s["L2 ≤"], 4) == 0.6325 and round(s["angle en degrés ≤"], 2) == 36.87
    renvois = {"1 - cos": 1.0 - cosinus(a, b), "produit scalaire": sum(x * y for x, y in zip(a, b)),
               "L2 au carré": math.dist(a, b) ** 2, "L2": math.dist(a, b)}
    for renvoi, valeur in renvois.items():
        assert abs(similarite_depuis(valeur, renvoi) - 0.6) < 1e-12
    print("  les quatre nombres renvoyés pour a = [1, 0] et b = [0.6, 0.8] redonnent bien cos = 0.6")

    print("7. Vecteur nul : l'ancien epsilon répond « orthogonal » en silence")
    nul = [0.0, 0.0]
    print(f"  ancienne_distance_cosinus([1, 0], [0, 0]) = {ancienne_distance_cosinus(a, nul):.1f}")
    assert ancienne_distance_cosinus(a, nul) == 1.0
    try:
        distance_cosinus(a, nul)
    except ValueError as e:
        print(f"  distance_cosinus([1, 0], [0, 0]) → ValueError : {e}")
    else:
        raise AssertionError("un vecteur nul aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Bornes : 1 − cos θ va de 0 (même direction) à 2 (directions opposées)
  même direction [3, 0]  1 − cos = 0.0
  orthogonal [0, 2]      1 − cos = 1.0
  opposé [-1, 0]         1 − cos = 2.0
2. Vecteurs unitaires : 1 − cos θ = ‖â − b̂‖² / 2   (a = [1, 0], b = [0.6, 0.8])
  1 − cos = 0.40   ‖â − b̂‖² / 2 = 0.80 / 2 = 0.40   θ = 53.13°   θ/π = 0.2952
  petits angles : 1 − cos 10° = 0.0152, 1 − cos 20° = 0.0603 (rapport 3.97)
3. Contre-exemple : 1 − cos θ viole l'inégalité triangulaire
  d(a,b) + d(b,c) = 0.293 + 0.293 = 0.586  <  d(a,c) = 1.000
  la distance L2 la respecte : 0.7654 + 0.7654 = 1.5307 ≥ 1.4142
4. La distance angulaire θ/π la respecte
  0.25 + 0.25 = 0.50 ≥ 0.50   (45° + 45° = 90° : b est sur le chemin de a à c)
  2 000 triplets aléatoires : 312 violations pour 1 − cos, 0 pour θ/π
…
  distance cosinus ≤  0.2000
  L2 au carré ≤       0.4000
…
  ancienne_distance_cosinus([1, 0], [0, 0]) = 1.0
  distance_cosinus([1, 0], [0, 0]) → ValueError : vecteur nul : le cosinus n'est pas défini
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : 1 − cosθ est un excellent critère de tri, mais une mauvaise « distance » au sens strict. Pour classer, les trois mesures se valent ; pour élaguer un index ou raisonner par l'inégalité triangulaire, il faut la distance angulaire ou la distance L2 sur vecteurs normalisés ; pour décider, il faut un seuil converti dans l'unité exacte que renvoie la base.

## Squelette algorithmique

La distance cosinus transforme une similarité en distance, pour les index qui ne savent travailler qu'avec des distances. Le point délicat est de traduire un seuil d'une forme à l'autre sans se tromper de sens.

```text
ALGORITHME SeuilsÉquivalents
ENTRÉE  : seuil τ sur le cosinus, dans [−1 ; 1]
SORTIE  : le même filtre exprimé dans les autres mesures (vecteurs unitaires)

  SI τ ∉ [−1 ; 1] ALORS ERREUR
  RETOURNER {
      distance cosinus ≤ 1 − τ,
      L2 au carré      ≤ 2 (1 − τ),
      L2               ≤ √(2 (1 − τ)),
      angle            ≤ arccos(τ) }

ALGORITHME ClasserParDistanceCosinus
ENTRÉES : vecteur q, documents (nom, v)
  POUR CHAQUE document FAIRE  d(nom) ← 1 − cos(q, v)  FIN POUR
  trier par d croissant (égalités par nom) ; RETOURNER la liste
```

**Complexité.** La conversion de seuils coûte O(1). Le classement coûte O(n × d) pour les distances et O(n log n) pour le tri, exactement comme le classement par cosinus, dont il donne l'ordre inverse. La distance angulaire θ / π demande en plus un arc cosinus par document, toujours O(1) chacun.

**Du squelette au code.** `SeuilsÉquivalents` correspond à `seuils_equivalents`, `ClasserParDistanceCosinus` à `classer`, et les mesures à `distance_cosinus` et `distance_angulaire`. `ancienne_distance_cosinus` reproduit l'ancienne version fautive du fichier, avec son `eps`, et `similarite_depuis` montre comment retrouver une similarité à partir d'une valeur renvoyée par un index, selon la convention qu'il utilise.

## Cas d'usage réels aux Émirats

Les seuils et les volumes ci-dessous sont illustratifs : ils se calibrent sur des paires étiquetées, propres à chaque modèle d'embedding et à chaque domaine.

### Banque — un seuil écrit à l'envers

L'assistant de FAQ d'une banque de détail de Dubaï répond aux clients sur les frais de carte, les virements et les prêts personnels, à partir de fiches produits stockées dans PostgreSQL avec pgvector. Pendant le prototype, l'équipe a calibré un seuil de similarité : au-dessus d'un cosinus de 0,82, le passage est jugé fiable. En production, la requête trie par `embedding <=> requete`, qui renvoie 1 − cosθ, mais un développeur a recopié le filtre tel quel, « distance supérieure ou égale à 0,82 » : l'agent ne garde plus que des passages de cosinus inférieur ou égal à 0,18, presque sans rapport avec la question. Le bon filtre est « distance inférieure ou égale à 1 − 0,82 = 0,18 » (point 7) ; si aucun passage ne le franchit, l'agent passe la main à un conseiller au lieu d'improviser. Sans cette conversion, l'agent cite des fiches hors sujet ou répond « je ne sais pas » à presque tout, et une réponse fausse sur des frais exposerait la banque aux exigences de la CBUAE en matière de protection du consommateur (à confirmer avec le texte en vigueur). L'équipe ajoute un test automatique qui vérifie le sens du seuil sur dix questions dont la bonne réponse est connue. En production, elle suit le taux de transfert vers un conseiller et la justesse des réponses sur un échantillon audité chaque semaine.

### Immobilier — changer de base sans changer de sens

Une agence immobilière de Dubaï et d'Abu Dhabi migre sa recherche de biens d'une base Chroma, configurée dans l'espace « cosine », vers FAISS, pour tenir des millions de vecteurs. Dans Chroma, le nombre renvoyé était 1 − cosθ et le filtre gardait les biens à une distance inférieure à 0,25 ; dans FAISS, après normalisation des vecteurs, l'index en produit scalaire renvoie le cosinus lui-même, et le meilleur bien est celui qui a la plus **grande** valeur. Le filtre doit donc devenir « cosinus supérieur ou égal à 0,75 » ; laissé tel quel, il ne garderait que les biens de cosinus inférieur à 0,25, c'est-à-dire les moins pertinents. Le point 6 garantit que, une fois le sens corrigé, l'ordre des biens est identique d'une base à l'autre. L'équipe le vérifie sur un jeu de requêtes étiquetées : le Recall@10 (étape 25) doit être exactement le même avant et après la migration, et tout écart signale une erreur de configuration plutôt qu'un « changement de modèle ». L'indicateur suivi en production est le taux de visites programmées après une recherche.

### Crypto — un arbre métrique qui perd des voisins

Une plateforme d'actifs virtuels agréée par la VARA regroupe les alertes de surveillance qui décrivent le même incident, pour que l'astreinte ne traite pas cinquante fois la même anomalie. L'équipe a indexé les textes d'alerte dans un arbre métrique (un *VP-tree*), qui élague des branches entières en s'appuyant sur l'inégalité triangulaire, et lui a donné 1 − cosθ comme distance. Le point 4 montre pourquoi cela échoue : l'arbre écarte une branche quand l'inégalité triangulaire lui garantit qu'aucun point de cette branche ne peut être assez proche de la requête, et avec 1 − cosθ cette garantie est fausse, si bien qu'il écarte parfois la branche qui contenait la vraie alerte voisine. Dans l'expérience du programme, plusieurs centaines de triplets sur 2 000 tirés au hasard en dimension 3 violent l'inégalité. L'équipe passe à la distance angulaire θ/π, qui est une vraie distance (point 5) et donne exactement le même classement (point 6). Les alertes dupliquées ne remontent plus séparément et l'astreinte voit chaque incident une seule fois. On suit le nombre d'alertes en double qui atteignent l'astreinte et le délai de prise en charge d'une alerte critique.

### Assurance — le vecteur nul qui se cache

Un assureur auto et santé indexe chaque déclaration de sinistre dès sa réception. Quand l'appel au modèle d'embedding échoue, par exemple sur une coupure réseau, le pipeline d'ingestion écrivait un vecteur de zéros « en attendant ». Avec l'ancien code à epsilon, ces dossiers étaient à une distance de 1,0 de toutes les requêtes : ni proches, ni lointains, ils restaient au milieu des classements, jamais retrouvés par les gestionnaires et jamais signalés. Avec la version corrigée, le calcul lève `ValueError` sur ces vecteurs, l'ingestion les met dans une file de reprise et l'équipe d'exploitation voit le problème dans l'heure. L'assurance est supervisée par la CBUAE et les délais de traitement d'un sinistre font partie de la relation avec l'assuré : un dossier invisible est un dossier en retard. Les indicateurs suivis sont le nombre de vecteurs nuls dans l'index, avec un objectif de zéro, et le nombre de déclarations sans embedding depuis plus d'une heure.

### RH — un seuil par paire de langues

Un cabinet RH présent dans plusieurs émirats rapproche des CV rédigés en arabe ou en anglais de fiches de poste rédigées en anglais, avec un modèle d'embedding multilingue. Sur un échantillon étiqueté, les bons appariements dans la même langue ont des distances cosinus de l'ordre de 0,15 à 0,25, alors que les bons appariements entre l'arabe et l'anglais se situent plutôt entre 0,30 et 0,40 (valeurs illustratives, à mesurer pour chaque modèle). Un seuil unique de 0,25 écarterait donc la plupart des bons CV rédigés en arabe, ce qui pénaliserait en particulier des candidats émiriens et irait à l'encontre des objectifs d'Émiratisation suivis par le MOHRE. L'équipe calibre un seuil par paire de langues, ou traduit d'abord le CV, puis vérifie le résultat sur des paires étiquetées des deux langues. L'agent ne rejette jamais un candidat seul : il classe et présente une liste au recruteur. L'indicateur suivi est le rappel des bons CV, mesuré séparément pour chaque langue (étape 25).

### BTP — rapprocher une facture de son bon de commande

Un groupe de construction qui mène de grands chantiers à Dubaï reçoit des milliers de lignes de factures de sous-traitants, que l'agent doit rapprocher des lignes de bons de commande avant paiement. Il calcule la distance cosinus entre la description de chaque ligne de facture et celles du bon de commande : à moins de 0,10, le rapprochement est automatique ; entre 0,10 et 0,30, la ligne part en revue humaine ; au-delà de 0,30, elle est rejetée comme article inconnu. Par exemple, « Ciment CEM I 42,5 N, sac de 50 kg » face à « Ciment Portland CEM I, sacs de 50 kg » peut tomber sous 0,10, tandis que « location de grue mobile » face à « grue à tour » tombe dans la zone de revue (valeurs illustratives). Une fois la ligne rapprochée, l'agent vérifie le montant et la TVA de 5 % ; une ligne de 12 000 AED hors taxes doit porter 600 AED de TVA. Sans des seuils exprimés dans la bonne unité, l'agent paierait des articles mal rapprochés ou bloquerait des factures correctes, et les retenues de garantie seraient calculées sur de mauvaises bases. On suit le taux de rapprochement automatique et le taux d'erreur relevé lors des audits mensuels.

## Pièges et limites

- **Similarité ou distance : le sens du tri et du seuil s'inverse.** Avec une distance on trie en ordre croissant et le seuil est un maximum ; avec une similarité, l'inverse. Un `ORDER BY embedding <=> requete DESC` renvoie les passages les moins pertinents en premier.
- **Un seuil ne se recopie pas d'une mesure à l'autre.** On le convertit avec le tableau du point 7, et seulement sur des vecteurs normalisés pour les lignes L2.
- **Ce n'est pas une distance.** Ni arbre métrique, ni raisonnement du type « A est proche de B, B est proche de C, donc A est proche de C » avec 1 − cosθ : on utilise la distance angulaire ou la distance L2 sur vecteurs normalisés.
- **Le vecteur nul est une donnée corrompue, pas un vecteur « orthogonal ».** Jamais d'epsilon au dénominateur : on lève `ValueError` et on corrige l'ingestion.
- **Un produit scalaire n'est un cosinus que sur des vecteurs normalisés.** Dans un index en produit scalaire, oublier de normaliser une seule fois, à l'indexation ou à la requête, réintroduit l'effet de la norme vu à l'étape 20.

### Exercice feuille blanche

1. Sans regarder le code, écrire `distance_cosinus` et `distance_angulaire` à partir de la fonction `cosinus`, puis vérifier le contre-exemple du point 4 : 0,293 + 0,293 < 1, mais 0,25 + 0,25 ≥ 0,5.
2. Prédire, puis vérifier avec `seuils_equivalents(0.9)` : quels seuils correspondent à un cosinus minimal de 0,9 ? (Réponse : distance cosinus ≤ 0,1 ; L2 au carré ≤ 0,2 ; L2 ≤ 0,4472 ; angle ≤ 25,84°.)
3. Trouver le bug : `return 1.0 - dot / (na * nb + 1e-8)`. Que renvoie cette ligne pour un vecteur nul, et où ce document apparaît-il dans le classement ?

## Pour aller plus loin

Certaines bibliothèques exposent la « similarité angulaire » 1 − θ/π, dans [0, 1], quand elles veulent une similarité bornée qui découle d'une vraie distance. Certains modèles d'embedding sont asymétriques : leur documentation demande un préfixe différent pour la requête et pour le document, et omettre ces préfixes dégrade le classement, quelle que soit la mesure de distance choisie. Enfin, la distance cosinus entre embeddings n'est qu'un signal parmi d'autres : l'étape suivante présente BM25, qui mesure la correspondance exacte des mots, et l'étape 23 montre comment combiner les deux.

> Suite : [BM25](<22-RAG-Formule-BM25.md>) — étape 22.
