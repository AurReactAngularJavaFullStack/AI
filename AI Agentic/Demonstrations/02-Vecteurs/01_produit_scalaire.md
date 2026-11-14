# 01 — Produit scalaire : démonstrations

> Fiche : [01 — Produit scalaire](<../../Images/02-Vecteurs/01_produit_scalaire.md>) · Image : `01_produit_scalaire.jpg` · Leçon : [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
x \cdot y = x_1 y_1 + x_2 y_2 + \dots + x_d y_d = \sum_{i=1}^{d} x_i \, y_i
$$

On multiplie les coordonnées deux à deux, puis on additionne. Le résultat est un nombre, pas un vecteur.

## Les symboles, un par un

La leçon de l'étape 14 écrit A, B et n ; ce fichier suit la fiche et écrit x, y et d. C'est la même formule.

$$
x, \quad y
$$

x et y sont les deux vecteurs comparés, par exemple une question encodée et un passage encodé ; ce sont des listes de d réels, portées en Python par des tuples (`q`, `docs["d1"]`…).

$$
x_i, \quad y_i
$$

xᵢ et yᵢ sont les coordonnées numéro i de chaque vecteur ; i va de 1 à d en maths et de 0 à d − 1 en Python, où les deux coordonnées sont lues ensemble par `zip(x, y)`.

$$
d
$$

d est la dimension, le nombre de coordonnées (384, 768, 1 536 ou 3 072 selon le modèle d'embedding) ; c'est un entier ≥ 1, `len(x)` en Python.

$$
\sum_{i=1}^{d}
$$

∑ se lit « additionne ce qui suit pour i allant de 1 à d » ; en Python, c'est `sum(...)` sur un générateur.

$$
x \cdot y
$$

x · y est le produit scalaire, un réel sans borne a priori ; son unité est le produit des unités des coordonnées (des AED quand on multiplie des quantités par des prix unitaires) ; en Python, `dot(x, y)`.

$$
\lambda
$$

λ est un réel quelconque qui multiplie un vecteur dans les démonstrations ; en Python, `lam`.

$$
\lVert x \rVert = \sqrt{x \cdot x}
$$

‖x‖ est la norme L2 de x, sa longueur, réel ≥ 0 (fiche 02) ; en Python, `norme(x)`.

$$
\theta
$$

θ est l'angle entre x et y, entre 0° et 180°, défini quand x et y sont non nuls ; en Python, `theta` (en radians).

$$
N
$$

N est le nombre de vecteurs auxquels on compare une question (passages, annonces) ; c'est un entier, `n_annonces` dans le cas 4.

$$
w, \quad b
$$

w est le vecteur des poids et b le biais d'un score linéaire w · x + b (cas 3) ; en Python, `w` et `b`.

## Le mécanisme, avant les preuves

Ce qui entre, ce sont deux listes de d nombres de même longueur. La première opération est un produit coordonnée par coordonnée : xᵢyᵢ est grand et positif quand les deux coordonnées sont grandes et de même signe (les deux vecteurs « sont d'accord » sur cette dimension), négatif quand leurs signes s'opposent (désaccord), et nul dès que l'une des deux vaut 0 (cette dimension ne compte pas). La seconde opération est une somme : elle cumule les accords et retranche les désaccords, et ce qui sort est un seul nombre. Il n'y a ni division ni racine : rien ne neutralise la longueur des vecteurs, si bien que doubler x double le score (démonstration 5) ; c'est le cosinus de la fiche 03 qui ajoutera cette division.

Pourquoi un produit et pas une différence ou une somme simple : la somme des différences |xᵢ − yᵢ| mesurerait un écart, pas un alignement, et la somme simple x₁ + y₁ + … ne dépendrait pas de la façon dont les coordonnées se correspondent. Le produit coordonnée par coordonnée est la façon la plus simple d'obtenir un nombre à la fois symétrique et linéaire dans chaque vecteur (démonstration 1) ; c'est cette double propriété qui lui donne un sens géométrique (démonstration 3) et qui permet de le calculer en une seule passe. L'unité du résultat est le produit des unités : des quantités multipliées par des prix unitaires donnent des AED, des poids sans unité multipliés par des caractéristiques donnent un score.

Petit film chiffré, avec x = (1 ; 2 ; 3) et y = (4 ; −5 ; 6). Coordonnée 1 : 1 × 4 = 4, total 4. Coordonnée 2 : 2 × (−5) = −10, désaccord, total 4 − 10 = −6. Coordonnée 3 : 3 × 6 = 18, total −6 + 18 = 12. Le résultat 12 est positif : les accords l'emportent sur le désaccord de la deuxième coordonnée.

Analogie Java/Spring : le montant hors taxe d'une facture est un produit scalaire, ∑ quantitéᵢ × prixUnitaireᵢ, la boucle qu'on écrit avec `BigDecimal` dans n'importe quel service de facturation. Le cas 2 l'exploite tel quel.

## Démonstration 1 — Symétrie et linéarité

**Ce qu'on démontre.** Pour x, y, z de même dimension d et un réel λ :

$$
x \cdot y = y \cdot x, \qquad (x + z) \cdot y = x \cdot y + z \cdot y, \qquad (\lambda x) \cdot y = \lambda \, (x \cdot y)
$$

**L'idée.** Chaque propriété est vraie pour un seul terme xᵢyᵢ, parce que la multiplication des réels est commutative et distributive ; une somme de termes qui la vérifient la vérifie aussi.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Symétrie : xᵢyᵢ = yᵢxᵢ pour chaque i, parce que la multiplication des réels est commutative ; on additionne les d égalités et l'on obtient x · y = y · x.

**Étape 2.** Additivité : la i-ème coordonnée de x + z est xᵢ + zᵢ ; on distribue le produit, puis on sépare la somme en deux, parce qu'une somme de sommes peut se regrouper dans n'importe quel ordre :

$$
(x + z) \cdot y = \sum_i (x_i + z_i)\, y_i = \sum_i x_i y_i + \sum_i z_i y_i = x \cdot y + z \cdot y
$$

**Étape 3.** Homogénéité : la i-ème coordonnée de λx est λxᵢ ; le facteur λ, commun à tous les termes, sort de la somme :

$$
(\lambda x) \cdot y = \sum_i \lambda x_i y_i = \lambda \sum_i x_i y_i = \lambda\, (x \cdot y)
$$

∎

**Vérification chiffrée.** Avec x = (1 ; 2 ; 3), y = (4 ; −5 ; 6), z = (2 ; 0 ; 1) et λ = 3 : x + z = (3 ; 2 ; 4) et (x + z) · y = 12 − 10 + 24 = 26 ; de l'autre côté, x · y + z · y = 12 + (8 + 0 + 6) = 12 + 14 = 26. Et (3x) · y = (3 ; 6 ; 9) · (4 ; −5 ; 6) = 12 − 30 + 54 = 36 = 3 × 12. Contre-exemple d'une mesure non linéaire : la somme des produits en valeur absolue, ∑|xᵢyᵢ|, vaut 4 + 10 + 18 = 32 pour x et y, et toujours 32 pour (−x) et y, alors que la linéarité exigerait −32.

**Ce que la preuve révèle du mécanisme.** Le produit scalaire se distribue comme un produit ordinaire : le score d'une somme est la somme des scores, et le score d'un vecteur agrandi est agrandi d'autant. Un écart entre deux vecteurs se mesure donc directement : x′ · y − x · y = (x′ − x) · y.

**Conséquence pour un agent.** Pour expliquer un écart de montant ou de score, l'agent calcule le produit scalaire de la **différence** des vecteurs, ligne par ligne, au lieu de comparer deux totaux opaques (cas 2). Et le score d'un profil moyen est la moyenne des scores : multiplier la question par un nombre positif ne change pas l'ordre des passages.

## Démonstration 2 — Le produit d'un vecteur par lui-même

**Ce qu'on démontre.** Pour tout vecteur x à coordonnées réelles :

$$
x \cdot x = \sum_i x_i^2 = \lVert x \rVert^2 \ge 0, \qquad x \cdot x = 0 \iff x = 0
$$

**L'idée.** Le produit d'un vecteur par lui-même ne contient que des carrés ; un carré de réel n'est jamais négatif, et une somme de nombres positifs ne s'annule que si chacun s'annule.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Par définition, x · x = x₁x₁ + … + x_d x_d = x₁² + … + x_d², parce que chaque terme multiplie une coordonnée par elle-même.

**Étape 2.** Chaque xᵢ² est ≥ 0, parce que le produit de deux réels de même signe est positif ; la somme de d nombres positifs est positive : x · x ≥ 0.

**Étape 3.** Si x · x = 0, chaque terme xᵢ² vaut 0, parce qu'un seul terme strictement positif rendrait la somme strictement positive ; donc chaque xᵢ = 0 et x = 0. Réciproquement, le vecteur nul donne une somme nulle. ∎

**Vérification chiffrée.** (3 ; 4) · (3 ; 4) = 9 + 16 = 25 = 5², donc ‖(3 ; 4)‖ = 5. Contraste : deux vecteurs non nuls peuvent avoir un produit scalaire nul entre eux, (1 ; −1) · (1 ; 1) = 1 − 1 = 0 (ils sont orthogonaux), mais jamais un vecteur non nul avec lui-même : (1 ; −1) · (1 ; −1) = 1 + 1 = 2.

**Ce que la preuve révèle du mécanisme.** Le produit scalaire contient la longueur : la norme de la fiche 02 n'est rien d'autre que la racine de x · x. C'est ce qui permet de passer du produit scalaire au cosinus avec les seules opérations « produit scalaire » et « racine ».

**Conséquence pour un agent.** Un embedding dont le produit avec lui-même vaut 0 est le vecteur nul : un texte vide ou un appel au modèle d'embedding qui a échoué. Le code le refuse par une erreur explicite au lieu de calculer un score dessus (fiche 02).

## Démonstration 3 — La forme géométrique

**Ce qu'on démontre.** Pour x et y non nuls, d'angle θ ∈ [0°, 180°] :

$$
x \cdot y = \lVert x \rVert \, \lVert y \rVert \cos\theta
$$

**L'idée.** On calcule de deux façons la longueur du troisième côté du triangle formé par x et y : une fois par l'algèbre du produit scalaire, une fois par la géométrie (loi des cosinus). Les deux résultats doivent coïncider, ce qui force l'égalité.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** On développe ‖x − y‖² avec la démonstration 1 (bilinéarité et symétrie), comme un carré ordinaire :

$$
\lVert x - y \rVert^2 = (x - y) \cdot (x - y) = \lVert x \rVert^2 - 2\, x \cdot y + \lVert y \rVert^2
$$

**Étape 2.** Les points 0, x et y sont dans un même plan, quelle que soit la dimension d, et forment un triangle de côtés ‖x‖, ‖y‖ et ‖x − y‖. La loi des cosinus (Al-Kashi) dans ce triangle, avec θ l'angle au sommet 0, donne :

$$
\lVert x - y \rVert^2 = \lVert x \rVert^2 + \lVert y \rVert^2 - 2 \lVert x \rVert \lVert y \rVert \cos\theta
$$

**Étape 3.** On égale les deux expressions et l'on retire ‖x‖² + ‖y‖² des deux côtés, puis l'on divise par −2 :

$$
- 2\, x \cdot y = - 2 \lVert x \rVert \lVert y \rVert \cos\theta \quad\Longrightarrow\quad x \cdot y = \lVert x \rVert \, \lVert y \rVert \cos\theta
$$

∎

**Vérification chiffrée.** u = (2 ; 0) et v = (3 cos 60° ; 3 sin 60°) = (1,5 ; 2,598076). D'un côté, u · v = 2 × 1,5 + 0 = 3 ; de l'autre, ‖u‖ ‖v‖ cos 60° = 2 × 3 × 0,5 = 3. Le troisième côté vérifie aussi l'étape 2 : ‖u − v‖² = 0,5² + 2,598076² = 0,25 + 6,75 = 7, et 4 + 9 − 2 × 2 × 3 × 0,5 = 7. Hypothèse nécessaire : si x = 0, l'angle n'est pas défini, et x · y = 0 quel que soit y.

**Ce que la preuve révèle du mécanisme.** Le produit scalaire mélange deux informations : les longueurs ‖x‖ ‖y‖ et l'alignement cos θ. Son signe ne dépend que de l'angle : positif si θ < 90°, nul si θ = 90°, négatif si θ > 90°.

**Conséquence pour un agent.** Pour ne garder que l'alignement, il faut diviser par les deux normes : c'est le cosinus de la fiche 03. Tant qu'on ne divise pas, un score élevé peut venir d'un vecteur long plutôt que d'un vecteur bien orienté (démonstration 5).

## Démonstration 4 — L'inégalité de Cauchy–Schwarz

**Ce qu'on démontre.** Pour tous vecteurs x et y de même dimension :

$$
\lvert x \cdot y \rvert \le \lVert x \rVert \, \lVert y \rVert
$$

avec égalité si et seulement si x et y sont colinéaires.

**L'idée.** La longueur au carré de x + ty est un trinôme en t qui ne devient jamais négatif. Un trinôme toujours positif a un discriminant négatif ou nul, et ce discriminant est exactement 4(x · y)² − 4‖x‖²‖y‖².

**La preuve, pas à pas.** Quatre étapes.

**Étape 1.** Si y = 0, les deux membres valent 0 et l'inégalité est vraie. On suppose donc y ≠ 0, donc ‖y‖² > 0 (démonstration 2).

**Étape 2.** Pour tout réel t, on développe par bilinéarité ; le résultat est ≥ 0 parce que c'est une longueur au carré :

$$
f(t) = \lVert x + t y \rVert^2 = \lVert y \rVert^2 t^2 + 2 (x \cdot y)\, t + \lVert x \rVert^2 \ge 0
$$

**Étape 3.** f est un trinôme de coefficient dominant ‖y‖² > 0. S'il avait deux racines distinctes, il serait strictement négatif entre elles ; il a donc au plus une racine, et son discriminant est négatif ou nul :

$$
4 (x \cdot y)^2 - 4 \lVert x \rVert^2 \lVert y \rVert^2 \le 0
$$

**Étape 4.** On divise par 4, on passe ‖x‖²‖y‖² à droite et l'on prend la racine carrée de deux nombres positifs, ce qui conserve l'ordre :

$$
(x \cdot y)^2 \le \lVert x \rVert^2 \lVert y \rVert^2 \quad\Longrightarrow\quad \lvert x \cdot y \rvert \le \lVert x \rVert \, \lVert y \rVert
$$

L'égalité correspond à un discriminant nul, donc à une racine double t₀ où ‖x + t₀y‖ = 0, c'est-à-dire x = −t₀y : les vecteurs sont colinéaires. ∎

**Vérification chiffrée.** x = (3 ; 4) et y = (4 ; 3) : ‖x‖² = ‖y‖² = 25 et x · y = 24, donc f(t) = 25t² + 48t + 25 et le discriminant vaut 48² − 4 × 25 × 25 = 2 304 − 2 500 = −196 < 0 ; on a bien 24 ≤ 5 × 5 = 25. Cas d'égalité : avec y = 2x = (6 ; 8), x · y = 18 + 32 = 50 = 5 × 10.

**Ce que la preuve révèle du mécanisme.** Le produit scalaire ne peut jamais dépasser le produit des longueurs : c'est ce qui borne le cosinus entre −1 et 1. L'écart entre |x · y| et ‖x‖ ‖y‖ mesure à quel point les vecteurs ne sont pas alignés.

**Conséquence pour un agent.** Un « cosinus » calculé hors de [−1, 1], au-delà d'un arrondi de l'ordre de 10⁻¹⁶, trahit un bug (normes oubliées, priorité des opérateurs) : on le détecte par une assertion plutôt que de le masquer en le tronquant. La même inégalité borne l'effet d'une perturbation (démonstration 6).

## Démonstration 5 — La longueur décide du classement

**Ce qu'on démontre.** Pour une question q non nulle et deux passages non nuls d₁ et d₂, de cosinus c₁ = cos(q, d₁) et c₂ = cos(q, d₂) avec c₁ > c₂ > 0 :

$$
q \cdot d_2 > q \cdot d_1 \iff \frac{\lVert d_2 \rVert}{\lVert d_1 \rVert} > \frac{c_1}{c_2}
$$

Le passage le moins bien orienté passe devant dès qu'il est assez long. Et multiplier q par λ > 0 ne change jamais l'ordre.

**L'idée.** Par la démonstration 3, chaque score vaut ‖q‖ × ‖dⱼ‖ × cⱼ. Le facteur ‖q‖ est commun à tous les passages et ne compte pas ; il reste à comparer deux produits « longueur × alignement ».

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Par la démonstration 3, pour j = 1 et j = 2 :

$$
q \cdot d_j = \lVert q \rVert \, \lVert d_j \rVert \, c_j
$$

**Étape 2.** On divise l'inégalité q · d₂ > q · d₁ par ‖q‖ > 0, ce qui conserve son sens, parce qu'on divise par un nombre positif :

$$
q \cdot d_2 > q \cdot d_1 \iff \lVert d_2 \rVert \, c_2 > \lVert d_1 \rVert \, c_1
$$

**Étape 3.** On divise par ‖d₁‖ c₂ > 0, encore positif parce que c₂ > 0, d'où l'énoncé. Pour λ > 0, la démonstration 1 donne (λq) · dⱼ = λ(q · dⱼ) : tous les scores sont multipliés par le même λ > 0, l'ordre ne change pas. ∎

**Vérification chiffrée.** Les vecteurs du cas 1 donnent c₁ = 0,98623 pour d₁ et c₃ = 0,92158 pour d₃, donc c₁ / c₃ = 1,07015, alors que ‖d₃‖ / ‖d₁‖ = 0,98489 / 0,83666 = 1,17716 > 1,07015 : le produit scalaire met d₃ devant (0,88 contre 0,80), alors que d₁ est mieux aligné. Hypothèse c₂ > 0 nécessaire : si c₂ < 0, allonger d₂ fait baisser son score au lieu de le monter, et l'équivalence change de sens.

**Ce que la preuve révèle du mécanisme.** Le classement par produit scalaire est un classement par « longueur × alignement ». La longueur de la question ne compte jamais ; celle des passages compte toujours. Un écart de 7 % sur les cosinus se rattrape par 7 % de longueur.

**Conséquence pour un agent.** On normalise les passages à l'indexation (fiche 02), une fois pour toutes : le produit scalaire devient alors le cosinus et la longueur ne décide plus de rien. Normaliser la question n'est utile que si l'on applique un seuil absolu au score.

## Démonstration 6 — Une petite erreur sur x bouge le score d'au plus ‖Δx‖ × ‖y‖

**Ce qu'on démontre.** Pour un vecteur x perturbé en x + e (bruit de mesure, arrondi, quantification d'un embedding) :

$$
\lvert (x + e) \cdot y - x \cdot y \rvert = \lvert e \cdot y \rvert \le \lVert e \rVert \, \lVert y \rVert
$$

**L'idée.** Par linéarité, l'écart de score est le produit scalaire de la perturbation par y ; Cauchy–Schwarz borne ce produit par le produit des longueurs.

**La preuve, pas à pas.** Deux étapes.

**Étape 1.** Par la démonstration 1 (additivité), (x + e) · y = x · y + e · y, donc la différence vaut e · y.

**Étape 2.** Par la démonstration 4 appliquée à e et y, |e · y| ≤ ‖e‖ ‖y‖. ∎

**Vérification chiffrée.** On perturbe la question du cas 1 par e = (0,01 ; −0,01 ; 0,01 ; 0). Son score avec d₁ bouge de e · d₁ = 0,007 − 0,002 + 0,004 + 0 = 0,009, sous la borne ‖e‖ ‖d₁‖ = 0,017321 × 0,83666 = 0,014491. La borne est atteinte quand e est aligné sur y : avec e = 0,01 × d₁ / ‖d₁‖, l'écart vaut 0,01 × ‖d₁‖ = 0,0083666 = ‖e‖ ‖d₁‖.

**Ce que la preuve révèle du mécanisme.** La sensibilité du score à la coordonnée i de x est yᵢ : une erreur δ sur xᵢ bouge le score de yᵢ δ. Les dimensions où y est grand sont celles où une erreur coûte le plus.

**Conséquence pour un agent.** L'écart entre deux passages, q · d₃ − q · d₁, bouge d'au plus ‖e‖ × ‖d₃ − d₁‖ ; ici ‖d₃ − d₁‖ = ‖(−0,1 ; −0,2 ; 0,2 ; 0,4)‖ = √0,25 = 0,5, donc d'au plus 0,017321 × 0,5 = 0,0086603, bien moins que l'écart de 0,08 entre les deux scores : la perturbation ne peut pas inverser ce classement. Quand l'écart du top-2 est plus petit que cette borne, on reclasse avec les vecteurs en pleine précision.

## Exemple simple, à la main

x = (1 ; 2 ; 3) et y = (4 ; −5 ; 6). On écrit chaque produit, puis le total cumulé :

| i | xᵢ | yᵢ | xᵢ × yᵢ | total cumulé |
| --- | --- | --- | --- | --- |
| 1 | 1 | 4 | 4 | 4 |
| 2 | 2 | −5 | −10 | −6 |
| 3 | 3 | 6 | 18 | 12 |

$$
x \cdot y = 1 \times 4 + 2 \times (-5) + 3 \times 6 = 4 - 10 + 18 = 12
$$

L'exemple de la fiche, une question et un passage en dimension 3 :

$$
(0{,}8\ ;\ 0{,}3\ ;\ 0{,}5) \cdot (0{,}7\ ;\ 0{,}4\ ;\ 0{,}6) = 0{,}56 + 0{,}12 + 0{,}30 = 0{,}98
$$

En doublant le premier vecteur, (1,6 ; 0,6 ; 1,0), les produits deviennent 1,12, 0,24 et 0,60, et le score 1,96 = 2 × 0,98 : le score double alors que la direction, donc le sens du texte, n'a pas changé (démonstration 1, homogénéité).

## Cas d'usage complexes, démontrés

### Cas 1 — Banque de détail à Dubaï : le produit scalaire brut classe mal la FAQ

**Contexte.** Une banque de détail de Dubaï fait répondre son application par un agent qui cherche, dans un index de 20 000 passages de FAQ en arabe et en anglais, ceux qui répondent à la question du client. L'index a été construit avec une ancienne version du modèle d'embedding qui renvoyait des vecteurs non normalisés, et le classement se fait par produit scalaire brut. Un client écrit « I forgot my password, how do I reset it? ». La question : le bon passage arrive-t-il en tête, et sinon que coûte l'erreur ? Les vecteurs (réduits à 4 dimensions), le volume et les coûts sont illustratifs.

**Données.**

| Vecteur | Contenu | Coordonnées |
| --- | --- | --- |
| q | la question | 0,8 ; 0,1 ; 0,5 ; 0,2 |
| d₁ | procédure de réinitialisation du mot de passe | 0,7 ; 0,2 ; 0,4 ; 0,1 |
| d₂ | frais de la carte | 0,1 ; 0,9 ; 0 ; 0,3 |
| d₃ | article général sur la sécurité du compte | 0,6 ; 0 ; 0,6 ; 0,5 |

Autres données : 20 000 passages en dimension 1 024 ; 3 000 questions de ce type par jour ; taux de transfert vers un conseiller de 8 % quand la procédure est en tête et de 14 % sinon ; 12 AED par transfert.

**Calcul pas à pas.** Arrondis à 5 décimales.

**Étape 1.** Les trois produits scalaires, terme à terme :

$$
q \cdot d_1 = 0{,}56 + 0{,}02 + 0{,}20 + 0{,}02 = 0{,}80, \qquad q \cdot d_2 = 0{,}08 + 0{,}09 + 0 + 0{,}06 = 0{,}23
$$

$$
q \cdot d_3 = 0{,}48 + 0 + 0{,}30 + 0{,}10 = 0{,}88
$$

**Étape 2.** Les normes, par la démonstration 2 :

$$
\lVert q \rVert = \sqrt{0{,}94} = 0{,}96954, \quad \lVert d_1 \rVert = \sqrt{0{,}70} = 0{,}83666, \quad \lVert d_2 \rVert = \sqrt{0{,}91} = 0{,}95394, \quad \lVert d_3 \rVert = \sqrt{0{,}97} = 0{,}98489
$$

**Étape 3.** La décomposition de la démonstration 5 : on divise chaque score par ‖q‖ pour obtenir ‖dⱼ‖ × cⱼ, puis par ‖dⱼ‖ pour obtenir l'alignement cⱼ :

$$
d_1 : \frac{0{,}80}{0{,}96954} = 0{,}82514 \;\Rightarrow\; c_1 = \frac{0{,}82514}{0{,}83666} = 0{,}98623 \qquad d_3 : \frac{0{,}88}{0{,}96954} = 0{,}90765 \;\Rightarrow\; c_3 = \frac{0{,}90765}{0{,}98489} = 0{,}92158
$$

**Étape 4.** Le coût d'une question en recherche exhaustive :

$$
N \times d = 20\,000 \times 1\,024 = 20\,480\,000 \text{ multiplications}
$$

**Décision de l'agent.** Le produit scalaire brut met l'article général d₃ en tête (0,88), devant la procédure d₁ (0,80), uniquement parce que d₃ est plus long. L'équipe normalise les 20 000 passages à l'indexation, une seule fois : le score devient le cosinus, d₁ passe en tête (0,98623 contre 0,92158) et c'est lui que l'agent colle dans le prompt.

**Contre-calcul.** Avec le classement brut, le client lit un article général au lieu de la procédure : le taux de transfert passe de 8 % à 14 %, soit 3 000 × (0,14 − 0,08) = 180 transferts de plus par jour, 180 × 12 = 2 160 AED par jour, pour une erreur qui ne vient que de la longueur des vecteurs.

**Sensibilité.** Par la démonstration 5, d₃ reste devant tant que ‖d₃‖ / ‖d₁‖ > c₁ / c₃ = 1,07015 ; le rapport réel vaut 1,17716. En multipliant d₃ par 0,80 / 0,88 = 0,90909, son score tomberait exactement à 0,80 : un passage plus court de 9,1 % seulement n'aurait plus gagné. L'erreur n'a donc rien d'un cas limite : tout passage environ 7 % plus long que la procédure, avec un cosinus de 0,92, la devance.

**En production.** Après normalisation, on contrôle chaque nuit le plus grand écart |‖v‖ − 1| sur l'index (attendu de l'ordre de 10⁻¹⁶, alerte au-dessus de 10⁻³, signe qu'une partie de l'index vient d'un autre modèle) et le taux de transfert par langue, arabe et anglais. L'agent ne demande jamais de mot de passe ni de code reçu par SMS ; ce garde-fou est séparé du classement, et les exigences de la CBUAE sur le service client sont à confirmer avec le texte en vigueur.

### Cas 2 — Groupe de construction à Dubaï : contrôler une facture de sous-traitant

**Contexte.** Un groupe de construction qui mène de grands chantiers à Dubaï reçoit chaque mois des centaines de factures de sous-traitants. Son agent de contrôle compare chaque facture au devis signé : le montant hors taxe est le produit scalaire du vecteur des quantités par celui des prix unitaires. La facture d'un lot de gros œuvre arrive avec des quantités différentes du devis. La question : faut-il la payer, la bloquer, et quelles lignes expliquent l'écart ? Quantités, prix, taux de retenue et tolérance sont illustratifs ; la TVA de 5 % est le taux en vigueur aux Émirats.

**Données.**

| Poste | Unité | Quantité au devis | Quantité facturée | Prix unitaire (AED) |
| --- | --- | --- | --- | --- |
| Béton | m³ | 120 | 126 | 450 |
| Acier | tonne | 18 | 18 | 3 200 |
| Coffrage | m² | 640 | 640 | 85 |
| Main-d'œuvre | heure | 1 500 | 1 560 | 38 |

Autres données : TVA 5 % ; retenue de garantie contractuelle de 10 % du hors taxe ; tolérance de paiement automatique de 0,5 % du hors taxe du devis.

**Calcul pas à pas.** Montants en AED, exacts.

**Étape 1.** Hors taxe du devis, x · y avec x les quantités et y les prix :

$$
x \cdot y = 120 \times 450 + 18 \times 3\,200 + 640 \times 85 + 1\,500 \times 38 = 54\,000 + 57\,600 + 54\,400 + 57\,000 = 223\,000
$$

**Étape 2.** Écart par linéarité (démonstration 1) : Δx = x′ − x = (6 ; 0 ; 0 ; 60), et

$$
\Delta x \cdot y = 6 \times 450 + 0 + 0 + 60 \times 38 = 2\,700 + 2\,280 = 4\,980
$$

Contrôle : x′ · y = 227 980 = 223 000 + 4 980.

**Étape 3.** Montants du devis : TVA 223 000 × 0,05 = 11 150, TTC 234 150, retenue 223 000 × 0,10 = 22 300, à payer 234 150 − 22 300 = 211 850. L'écart facturé vaut 4 980 × 1,05 = 5 229 AED TTC.

**Étape 4.** Tolérance :

$$
0{,}005 \times 223\,000 = 1\,115 < 4\,980
$$

**Décision de l'agent.** L'écart dépasse la tolérance : la facture est bloquée et une demande de justificatifs part au sous-traitant, en citant les deux lignes responsables, 2 700 AED pour 6 m³ de béton (bons de livraison) et 2 280 AED pour 60 heures (feuilles de pointage). L'agent ne corrige rien de lui-même.

**Contre-calcul.** Une méthode naïve multiplie l'écart total de quantités par le prix unitaire moyen : 6 + 60 = 66 unités, prix moyen (450 + 3 200 + 85 + 38) / 4 = 943,25 AED, soit 66 × 943,25 = 62 254,5 AED, 12,5 fois l'écart réel. Elle additionne des m³ et des heures et ignore quelle quantité va avec quel prix : c'est exactement l'appariement coordonnée par coordonnée que fait le produit scalaire. Sur cette facture, elle déclencherait une alerte de 62 000 AED et une négociation inutile.

**Sensibilité.** Si le sous-traitant justifie les 6 m³ de béton, il reste 2 280 AED d'heures, toujours au-dessus de 1 115 ; la valeur de bascule sur les heures est 1 115 / 38 = 29,3 heures : jusqu'à 29 heures de plus, la facture serait passée automatiquement. Sur le béton seul, la bascule est 1 115 / 450 = 2,48 m³.

**En production.** On suit le taux de factures bloquées que le contrôleur de gestion confirme (attendu élevé ; s'il tombe sous 70 %, la tolérance est trop basse). Les montants se calculent en décimal exact, comme `BigDecimal` en Java, jamais par le modèle ; la TVA de 5 % et la retenue s'appliquent selon le contrat et la facture fiscale, modalités à confirmer avec le texte en vigueur.

### Cas 3 — Assureur auto : un score de fraude linéaire w · x + b

**Contexte.** Un assureur auto et santé trie chaque mois 4 000 déclarations de sinistre auto. Avant tout paiement, un score linéaire s = w · x + b, appris par l'équipe actuarielle, décide si le dossier part en revue humaine (s ≥ 0,5) ou s'il est payé automatiquement. Un assuré de Sharjah déclare un sinistre avec un devis de garage de 12 000 AED. La question : payer automatiquement ou envoyer en revue, compte tenu de l'incertitude sur les données ? Poids, biais, seuil, volumes et coûts sont illustratifs.

**Données.**

| Caractéristique | xᵢ | Poids wᵢ | Incertitude |
| --- | --- | --- | --- |
| Montant du devis, en milliers d'AED | 12 | 0,06 | ± 0,5 |
| Sinistres déclarés sur 24 mois | 3 | 0,50 | 0 |
| Garage hors réseau (1 = oui) | 1 | 0,90 | 0 |
| Écart relatif entre déclaration et devis | 0,25 | 1,20 | ± 0,05 |

Autres données : biais b = −3,0 ; seuil de revue 0,5 ; vétusté 20 % et franchise 500 AED au contrat ; revue humaine 60 AED par dossier ; 12 % des dossiers vont habituellement en revue.

**Calcul pas à pas.** Scores à 2 décimales, montants en AED.

**Étape 1.** Contributions wᵢxᵢ, puis score :

$$
w \cdot x = 0{,}72 + 1{,}50 + 0{,}90 + 0{,}30 = 3{,}42, \qquad s = 3{,}42 - 3{,}0 = 0{,}42
$$

**Étape 2.** Incertitude par linéarité : s(x + Δx) = s(x) + w · Δx, et le pire Δx vaut

$$
\lvert w \cdot \Delta x \rvert \le 0{,}06 \times 0{,}5 + 1{,}20 \times 0{,}05 = 0{,}03 + 0{,}06 = 0{,}09
$$

donc s est dans [0,33 ; 0,51].

**Étape 3.** Ce qui est en jeu si l'on paie :

$$
12\,000 \times (1 - 0{,}20) - 500 = 9\,600 - 500 = 9\,100 \text{ AED}
$$

**Décision de l'agent.** s = 0,42 < 0,5, mais la borne haute 0,51 dépasse le seuil : le dossier est en zone grise. L'agent l'envoie en revue humaine (60 AED) plutôt que de payer automatiquement 9 100 AED sur un score que l'incertitude des données peut faire basculer. Il joint les quatre contributions, qui montrent que le poids des 3 sinistres (1,50) domine.

**Contre-calcul.** Si une mise à jour du formulaire envoie le devis en AED (12 000) au lieu de milliers d'AED, la contribution devient 0,06 × 12 000 = 720 et s = 719,7 : tous les dossiers dépassent le seuil, et l'assureur paie 4 000 × 60 = 240 000 AED de revues par mois au lieu de 0,12 × 4 000 × 60 = 28 800 AED. Le produit scalaire n'a aucune protection contre une erreur d'unité : une coordonnée multipliée par 1 000 multiplie sa contribution par 1 000 (démonstration 1).

**Sensibilité.** Les trois autres contributions valent 3,42 − 0,30 = 3,12. Le seuil est atteint quand 3,12 + 1,20 × écart − 3,0 = 0,5, soit 1,20 × écart = 0,38 et un écart relatif de 0,38 / 1,20 = 0,31667 (c'est aussi 0,25 + 0,08 / 1,20) : la valeur de bascule est 31,7 %. Un devis plus élevé de 10 % (13,2 milliers) ne donne que s = 0,492 : le score est bien plus sensible à l'écart (1,20 par unité) qu'au montant (0,06 par millier d'AED), comme le prévoit la démonstration 6 (la sensibilité à xᵢ est wᵢ).

**En production.** On suit la part des dossiers en revue : attendue à 12 %, alerte au-dessus de 20 %, le signe typique d'une erreur d'unité ou d'une dérive des données. Chaque décision garde ses contributions wᵢxᵢ, ce qui rend le score explicable à l'assuré et à l'auditeur. L'assurance est supervisée par la CBUAE ; la documentation du modèle et de son seuil est à confirmer avec le texte en vigueur.

### Cas 4 — Agence immobilière à Dubaï et Abu Dhabi : faut-il un index approché ?

**Contexte.** Une agence immobilière recommande des annonces en calculant le produit scalaire entre le profil normalisé du client et chacune de ses 15 000 annonces normalisées, en dimension 768. Aux heures de pointe, elle reçoit 40 requêtes par seconde, avec un budget de latence de 50 ms par requête. L'équipe hésite à installer un index approché. La question : la recherche exhaustive, exacte, tient-elle, et jusqu'à quand ? Les volumes et la vitesse de la machine sont illustratifs.

**Données.**

| Donnée | Valeur |
| --- | --- |
| Annonces N | 15 000 |
| Dimension d | 768 |
| Pic de requêtes | 40 par seconde |
| Budget de latence | 50 ms |
| Vitesse d'un cœur | 2 × 10⁹ multiplications-additions par seconde |
| Cœurs disponibles | 4 |
| Projet | modèle en dimension 3 072 et 40 000 annonces avec Abu Dhabi |

**Calcul pas à pas.** Durées arrondies à 2 décimales.

**Étape 1.** Un produit scalaire coûte d multiplications-additions ; une requête en coûte :

$$
N \times d = 15\,000 \times 768 = 11\,520\,000
$$

**Étape 2.** Latence sur un cœur :

$$
\frac{11\,520\,000}{2 \times 10^9} = 0{,}00576 \text{ s} = 5{,}76 \text{ ms}
$$

**Étape 3.** Charge au pic : 40 × 5,76 ms = 230,4 ms de calcul par seconde, soit 0,2304 cœur sur 4.

**Étape 4.** Limites : la latence atteint 50 ms pour N = 0,05 × 2 × 10⁹ / 768 = 130 208 annonces, et les 4 cœurs saturent pour N = 4 × 2 × 10⁹ / (768 × 40) = 260 416 annonces.

**Décision de l'agent.** 5,76 ms ≪ 50 ms et 0,23 cœur ≪ 4 : on garde la recherche exhaustive, qui donne le classement exact, sans index approché. L'index occupe 15 000 × 768 × 4 octets = 46 080 000 octets, soit 46,08 Mo en float32 : il tient en mémoire.

**Contre-calcul.** Pour le projet, l'estimation naïve « 4 fois plus de dimensions, donc 4 × 5,76 = 23,04 ms, ça passe » oublie que N grandit aussi : le coût est un produit N × d, et 40 000 × 3 072 / (2 × 10⁹) = 61,44 ms dépasse le budget de 50 ms. Lancé sur cette estimation, le projet dégraderait chaque recommandation aux heures de pointe.

**Sensibilité.** La latence est linéaire en N et en d : 10 % d'annonces de plus coûtent 10 % de temps de plus. La valeur de bascule est N = 130 208 annonces en dimension 768, mais seulement 0,05 × 2 × 10⁹ / 3 072 = 32 552 en dimension 3 072. Le projet doit donc choisir : rester en 768, ou passer en 3 072 avec un index approché (ou une requête répartie sur plusieurs cœurs).

**En production.** On suit la latence au 95ᵉ centile, avec une alerte à 40 ms (80 % du budget), et le nombre d'annonces indexées par rapport à la bascule. Seules les annonces publiables entrent dans l'index ; les règles de publicité immobilière de la RERA sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer (2 ; −1 ; 0) · (3 ; 4 ; 5).

**Exercice 2.** Trouver t pour que (1 ; t) et (3 ; −2) soient orthogonaux.

**Exercice 3.** Démontrer que (x + y) · (x − y) = ‖x‖² − ‖y‖², puis le vérifier avec x = (3 ; 4) et y = (1 ; 2).

**Exercice 4.** Vérifier Cauchy–Schwarz avec x = (1 ; 2) et y = (3 ; 4).

**Exercice 5.** Combien de multiplications pour comparer une question à 50 000 passages en dimension 768 ?

**Exercice 6.** Dans le cas 2, le sous-traitant renvoie une facture corrigée avec 121 m³ de béton et 1 510 heures, le reste inchangé. Calculer l'écart hors taxe par linéarité et donner la nouvelle décision de l'agent.

**Exercice 7.** Trouver l'erreur. Un collègue écrit : « ‖x − y‖² = (x − y) · (x − y) = ‖x‖² − ‖y‖² ». Vérifier sur x = (3 ; 4) et y = (1 ; 2), puis corriger le développement.

**Exercice 8.** Redémontrer de mémoire l'inégalité de Cauchy–Schwarz par le discriminant, puis écrire le trinôme et son discriminant pour x = (3 ; 4) et y = (4 ; 3).

## Corrigé

**Exercice 1.** On multiplie terme à terme : 2 × 3 = 6, (−1) × 4 = −4, 0 × 5 = 0 ; on additionne : 6 − 4 + 0 = 2.

**Exercice 2.** Orthogonaux signifie produit scalaire nul : 1 × 3 + t × (−2) = 3 − 2t = 0, donc t = 1,5. Contrôle : (1 ; 1,5) · (3 ; −2) = 3 − 3 = 0.

**Exercice 3.** Par la démonstration 1 : (x + y) · (x − y) = x · x − x · y + y · x − y · y. Les deux termes du milieu s'annulent, parce que x · y = y · x, d'où ‖x‖² − ‖y‖². Vérification : x + y = (4 ; 6), x − y = (2 ; 2), produit 8 + 12 = 20, et ‖x‖² − ‖y‖² = 25 − 5 = 20.

**Exercice 4.** x · y = 3 + 8 = 11. ‖x‖ = √5 et ‖y‖ = √25 = 5, donc ‖x‖ ‖y‖ = 5√5 ≈ 11,180. On a bien 11 ≤ 11,180 ; l'écart est petit parce que les deux vecteurs sont presque alignés.

**Exercice 5.** Chaque comparaison coûte 768 multiplications, donc 50 000 × 768 = 38 400 000 multiplications.

**Exercice 6.** Δx = (121 − 120 ; 0 ; 0 ; 1 510 − 1 500) = (1 ; 0 ; 0 ; 10). Par linéarité, l'écart vaut 1 × 450 + 10 × 38 = 450 + 380 = 830 AED hors taxe. 830 ≤ 1 115 : la décision change, la facture passe en paiement automatique, avec l'écart de 830 AED (871,5 AED TTC) mentionné au contrôleur.

**Exercice 7.** Vérification : x − y = (2 ; 2), donc ‖x − y‖² = 4 + 4 = 8, alors que ‖x‖² − ‖y‖² = 25 − 5 = 20 : la formule est fausse. L'erreur est d'avoir traité le produit comme (x − y) · (x + y) ; le bon développement garde le double produit, ‖x‖² − 2 x · y + ‖y‖² = 25 − 2 × 11 + 5 = 8.

**Exercice 8.** Étape 1 : si y = 0, tout vaut 0. Étape 2 : sinon, f(t) = ‖x + ty‖² = ‖y‖²t² + 2(x · y)t + ‖x‖² ≥ 0 pour tout t. Étape 3 : un trinôme de coefficient dominant positif qui ne devient jamais négatif a un discriminant ≤ 0, soit 4(x · y)² − 4‖x‖²‖y‖² ≤ 0. Étape 4 : on divise par 4 et l'on prend la racine. Pour x = (3 ; 4) et y = (4 ; 3) : f(t) = 25t² + 48t + 25, discriminant 48² − 4 × 25 × 25 = 2 304 − 2 500 = −196 ≤ 0, et 24 ≤ 25.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dot(x, y)`** — Cette fonction est le caissier qui passe deux listes en parallèle, l'une des quantités, l'autre des prix, et multiplie chaque ligne par sa voisine avant de tout additionner : elle reçoit deux vecteurs, vérifie qu'ils ont la même longueur et lève sinon une `ValueError` « dimensions différentes », puis renvoie la somme des produits terme à terme x₁y₁ + x₂y₂ + …, jusqu'à la dernière coordonnée. C'est la brique de tout le programme, qu'il s'agisse du score 12 de (1, 2, 3) · (4, −5, 6), du hors taxe de 223 000 AED du cas 2 ou du score de fraude du cas 3, et `main` vérifie à la fin qu'elle refuse bien un vecteur de trois coordonnées face à un vecteur de deux.

**`norme(x)`** — Celle-ci mesure la longueur d'une flèche, comme un arpenteur qui applique Pythagore à toutes les directions à la fois : elle reçoit un seul vecteur, le fait passer par `dot` contre lui-même pour obtenir la somme des carrés de ses coordonnées, et renvoie la racine carrée de ce nombre, ‖x‖ = √(x · x). Elle donne 5 pour (3, 4), 0,96954 pour la question q du cas 1 et 0,83666, 0,95394 et 0,98489 pour ses trois passages, ce qui permet au programme de diviser les produits scalaires par les longueurs et de montrer que c'est la longueur, et non l'alignement, qui fausse le classement brut.

**`contributions(x, y)`** — Cette fonction est l'expert-comptable qui, au lieu de donner seulement le total d'une facture, détaille ligne par ligne d'où vient chaque dirham : elle reçoit deux vecteurs de même dimension, lève une `ValueError` s'ils diffèrent, et renvoie la liste des d produits xᵢyᵢ, dont la somme redonne exactement x · y. On s'en sert pour voir le cumul 4, −6 puis 12 de l'exemple simple, les quatre montants 54 000, 57 600, 54 400 et 57 000 AED du devis du cas 2, ou les contributions 0,72, 1,5, 0,9 et 0,3 du score de fraude, celles que l'agent joint au dossier pour le rendre explicable.

**`cas_1_faq_banque()`** — Ici l'on suit le documentaliste d'une banque de détail qui doit retrouver la bonne procédure pour un client parmi 20 000 passages en dimension 1 024 : la fonction prend la question q = (0.8, 0.1, 0.5, 0.2) et trois passages, calcule leurs produits scalaires 0,80, 0,23 et 0,88, leurs normes, la longueur de chaque passage le long de q, puis leurs cosinus 0,98623, 0,24868 et 0,92158. Elle constate que le score brut met en tête le passage long d3 alors que le cosinus choisit d1, chiffre les 20 480 000 multiplications d'une recherche et les 3 000 × (0,14 − 0,08) = 180 transferts de plus par jour, soit 2 160 AED, imprime ces lignes et renvoie un dictionnaire de toutes ces grandeurs, que `main` réutilise aussi pour les démonstrations 5 et 6.

**`cas_2_facture_btp()`** — Cette fonction joue le contrôleur de gestion d'un groupe de construction qui confronte la facture d'un sous-traitant au devis signé : elle reçoit implicitement les quantités du devis (120, 18, 640, 1500), celles de la facture (126, 18, 640, 1560) et les prix unitaires (450, 3200, 85, 38), calcule le hors taxe du devis, 223 000 AED, puis l'écart de quantités (6, 0, 0, 60) et, par linéarité, l'écart de 4 980 AED. Elle le compare à la tolérance de 0,5 % du hors taxe, soit 1 115 AED, décide « bloquer », calcule au passage la TVA de 5 %, le TTC de 234 150 AED, la retenue de 10 % et la méthode naïve du prix moyen qui annoncerait 62 254,5 AED, puis renvoie tout cela dans un dictionnaire.

**`cas_3_score_fraude_assurance()`** — On y voit l'actuaire d'un assureur auto qui fait tourner un score linéaire s = w · x + b sur un dossier de sinistre : avec les poids (0.06, 0.50, 0.90, 1.20), les données (12, 3, 1, 0.25) et le biais −3,0, la fonction obtient s = 0,42, sous le seuil de 0,5, puis additionne les incertitudes pondérées par la valeur absolue des poids pour une marge de 0,09. Comme la borne haute 0,51 dépasse le seuil, elle classe le dossier en « revue (zone grise) » plutôt qu'en paiement automatique des 9 100 AED en jeu, puis calcule le score aberrant 719,7 obtenu si le devis arrive en AED au lieu de milliers d'AED, l'écart de bascule 0,31667 et le score 0,492 d'un devis majoré de 10 %, avant de renvoyer ces valeurs.

**`cas_4_recherche_immobilier()`** — Cette fonction est l'ingénieur d'une agence immobilière qui chronomètre sa recherche exhaustive avant d'acheter un index approché : pour 15 000 annonces en dimension 768, une machine à 2 × 10⁹ opérations par seconde, 40 requêtes par seconde au pic et 4 cœurs, elle compte 11 520 000 opérations par requête, une latence de 5,76 ms et une charge de 0,2304 cœur, donc la décision « exhaustive ». Elle calcule aussi les seuils où tout bascule, 130 208 annonces pour le budget de 50 ms en dimension 768 et 32 552 en dimension 3 072, la saturation à 260 416 annonces, la mémoire de 46 080 000 octets et le projet à 61,44 ms que l'estimation naïve croyait tenir en 23,04 ms, puis renvoie ces grandeurs dans un dictionnaire.

**`main()`** — C'est le professeur qui refait au tableau, dans l'ordre de la fiche, chaque calcul de la leçon et le fait contresigner par un `assert` : il commence par le mécanisme et l'exemple simple, vérifie la symétrie et la linéarité de la démonstration 1, le carré de la longueur de la démonstration 2, la forme géométrique avec un angle de 60 degrés et ‖u − v‖² = 7, puis Cauchy–Schwarz avec le discriminant −196. Il appelle ensuite les quatre cas, s'appuie sur le premier pour les démonstrations 5 et 6, contrôle chaque valeur renvoyée, rejoue les exercices du corrigé jusqu'à l'écart de 830 AED de l'exercice 6, vérifie que `dot` refuse deux dimensions différentes et n'imprime « OK — toutes les vérifications sont passées. » qu'au bout de ce parcours sans faute.

```python
"""Démonstration 01 — produit scalaire : propriétés, Cauchy–Schwarz, longueur, perturbation, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dot(x, y) -> float:
    """x · y = x₁y₁ + … + x_d y_d ; refuse deux vecteurs de dimensions différentes."""
    if len(x) != len(y):
        raise ValueError("dimensions différentes")
    return sum(a * b for a, b in zip(x, y))


def norme(x) -> float:
    """‖x‖ = √(x · x) (fiche 02)."""
    return math.sqrt(dot(x, x))


def contributions(x, y) -> list[float]:
    """Les d produits xᵢyᵢ, dont la somme est x · y."""
    if len(x) != len(y):
        raise ValueError("dimensions différentes")
    return [a * b for a, b in zip(x, y)]


def cas_1_faq_banque() -> dict:
    """[BANQUE] FAQ à Dubaï : le produit scalaire brut met un passage long devant le bon passage."""
    q = (0.8, 0.1, 0.5, 0.2)
    docs = {"d1": (0.7, 0.2, 0.4, 0.1), "d2": (0.1, 0.9, 0.0, 0.3), "d3": (0.6, 0.0, 0.6, 0.5)}
    n_passages, dim, par_jour, cout_transfert = 20_000, 1024, 3_000, 12
    scores = {k: dot(q, d) for k, d in docs.items()}
    normes = {k: norme(d) for k, d in docs.items()}
    longueur_alignement = {k: scores[k] / norme(q) for k in docs}
    cos = {k: longueur_alignement[k] / normes[k] for k in docs}
    brut = max(scores, key=scores.get)
    normalise = max(cos, key=cos.get)
    transferts = round(par_jour * (0.14 - 0.08))
    for k, s in scores.items():
        print(f"Cas 1 FAQ : q·{k} = {s:.2f}   ‖{k}‖ = {normes[k]:.5f}   cos = {cos[k]:.5f}")
    print(f"  brut -> {brut}, normalisé -> {normalise} ; {n_passages * dim:,} multiplications ;"
          f" {transferts} transferts/jour = {transferts * cout_transfert} AED")
    return {"q": q, "docs": docs, "scores": scores, "normes": normes, "la": longueur_alignement,
            "cos": cos, "brut": brut, "normalise": normalise, "transferts": transferts,
            "cout": transferts * cout_transfert, "mult": n_passages * dim}


def cas_2_facture_btp() -> dict:
    """[BTP] Dubaï : hors taxe = quantités · prix unitaires, écart par linéarité, tolérance 0.5 %."""
    devis = (120, 18, 640, 1500)
    facture = (126, 18, 640, 1560)
    prix = (450, 3200, 85, 38)
    tva, retenue, tolerance = 0.05, 0.10, 0.005
    ht = dot(devis, prix)
    ecart_x = tuple(a - b for a, b in zip(facture, devis))
    ecart = dot(ecart_x, prix)
    seuil = tolerance * ht
    decision = "bloquer" if ecart > seuil else "payer"
    naif = sum(ecart_x) * sum(prix) / len(prix)
    print(f"Cas 2 BTP : HT devis {ht} AED ({contributions(devis, prix)}) ; écart {ecart_x} -> {ecart} AED HT")
    print(f"  TVA {ht * tva:.0f}, TTC {ht * (1 + tva):.0f}, retenue {ht * retenue:.0f}, à payer"
          f" {ht * (1 + tva) - ht * retenue:.0f} ; tolérance {seuil:.0f} -> {decision} ; naïf {naif:.1f} AED")
    return {"ht": ht, "contrib": contributions(devis, prix), "ecart_x": ecart_x, "ecart": ecart,
            "facture_ht": dot(facture, prix), "tva": ht * tva, "ttc": ht * (1 + tva), "retenue": ht * retenue,
            "seuil": seuil, "decision": decision, "naif": naif, "prix": prix}


def cas_3_score_fraude_assurance() -> dict:
    """[ASSUR] score linéaire s = w · x + b, incertitude par linéarité, erreur d'unité."""
    w = (0.06, 0.50, 0.90, 1.20)
    x = (12, 3, 1, 0.25)
    b, seuil = -3.0, 0.5
    incertitude = (0.5, 0, 0, 0.05)
    s = dot(w, x) + b
    marge = sum(abs(wi) * di for wi, di in zip(w, incertitude))
    indemnite = 12_000 * (1 - 0.20) - 500
    if s >= seuil:
        decision = "revue"
    elif s + marge >= seuil:
        decision = "revue (zone grise)"
    else:
        decision = "paiement automatique"
    s_unite = dot(w, (12_000, 3, 1, 0.25)) + b
    bascule_ecart = x[3] + (seuil - s) / w[3]
    s_devis = dot(w, (13.2, 3, 1, 0.25)) + b
    print(f"Cas 3 ASSUR : contributions {[round(c, 2) for c in contributions(w, x)]}, s = {s:.2f},"
          f" intervalle [{s - marge:.2f} ; {s + marge:.2f}] -> {decision} ; en jeu {indemnite:.0f} AED")
    print(f"  devis en AED : s = {s_unite:.1f} ; revues {4_000 * 60} au lieu de {0.12 * 4_000 * 60:.0f} AED ;"
          f" bascule écart {bascule_ecart:.5f} ; devis +10 % : s = {s_devis:.3f}")
    return {"w": w, "s": s, "marge": marge, "indemnite": indemnite, "decision": decision,
            "s_unite": s_unite, "bascule": bascule_ecart, "s_devis": s_devis, "wx": dot(w, x)}


def cas_4_recherche_immobilier() -> dict:
    """[IMMO] recherche exhaustive : coût N × d, latence, charge, valeurs de bascule."""
    n_annonces, dim, pic, budget_s, vitesse, coeurs = 15_000, 768, 40, 0.050, 2e9, 4
    operations = n_annonces * dim
    latence_ms = operations / vitesse * 1000
    charge = pic * operations / vitesse
    n_bascule = math.floor(budget_s * vitesse / dim)          # nombre entier d'annonces : arrondi vers le bas
    n_sature = math.floor(coeurs * vitesse / (dim * pic))
    memoire = n_annonces * dim * 4
    projet_ms = 40_000 * 3072 / vitesse * 1000
    bascule_3072 = math.floor(budget_s * vitesse / 3072)
    decision = "exhaustive" if latence_ms < budget_s * 1000 and charge < coeurs else "index approché"
    print(f"Cas 4 IMMO : {operations:,} opérations, {latence_ms:.2f} ms, charge {charge:.4f} cœur -> {decision} ;"
          f" index {memoire:,} octets")
    print(f"  bascules N = {n_bascule} (768) et {bascule_3072} (3072), saturation {n_sature} ;"
          f" projet {projet_ms:.2f} ms (naïf {4 * latence_ms:.2f} ms)")
    return {"operations": operations, "latence": latence_ms, "charge": charge, "n_bascule": n_bascule,
            "n_sature": n_sature, "memoire": memoire, "projet": projet_ms, "bascule_3072": bascule_3072,
            "decision": decision}


def main() -> None:
    # Mécanisme et exemple simple
    x0, y0 = (1, 2, 3), (4, -5, 6)
    cumul = [sum(contributions(x0, y0)[:k]) for k in (1, 2, 3)]
    print(f"(1,2,3)·(4,-5,6) = {dot(x0, y0)} ; produits {contributions(x0, y0)} ; cumul {cumul}")
    assert contributions(x0, y0) == [4, -10, 18] and cumul == [4, -6, 12] and dot(x0, y0) == 12
    xf, yf = (0.8, 0.3, 0.5), (0.7, 0.4, 0.6)
    x2 = tuple(2 * a for a in xf)
    print(f"Fiche : x·y = {dot(xf, yf):.2f} ; (2x)·y = {dot(x2, yf):.2f} ; produits {[round(c, 2) for c in contributions(x2, yf)]}")
    assert [round(c, 2) for c in contributions(xf, yf)] == [0.56, 0.12, 0.30] and round(dot(xf, yf), 2) == 0.98
    assert [round(c, 2) for c in contributions(x2, yf)] == [1.12, 0.24, 0.60] and round(dot(x2, yf), 2) == 1.96

    # Démonstration 1 — symétrie et linéarité
    z, lam = (2, 0, 1), 3
    xz = tuple(a + c for a, c in zip(x0, z))
    print(f"D1 : (x+z)·y = {dot(xz, y0)} = {dot(x0, y0)} + {dot(z, y0)} ; (3x)·y = {dot(tuple(lam * a for a in x0), y0)} ;"
          f" Σ|xᵢyᵢ| = {sum(abs(c) for c in contributions(x0, y0))} pour x et pour -x")
    assert dot(x0, y0) == dot(y0, x0) and xz == (3, 2, 4) and dot(xz, y0) == 26 and dot(z, y0) == 14
    assert dot(tuple(lam * a for a in x0), y0) == 36 == lam * dot(x0, y0)
    assert sum(abs(c) for c in contributions(x0, y0)) == 32 == sum(abs(c) for c in contributions(tuple(-a for a in x0), y0))
    xr, yr, zr = (1.0, -2.0, 3.5), (0.5, 4.0, -1.0), (2.0, 0.0, 1.0)
    assert math.isclose(dot(tuple(a + c for a, c in zip(xr, zr)), yr), dot(xr, yr) + dot(zr, yr))
    assert math.isclose(dot(tuple(-2.5 * a for a in xr), yr), -2.5 * dot(xr, yr))

    # Démonstration 2 — x · x
    print(f"D2 : (3,4)·(3,4) = {dot((3, 4), (3, 4))} ; (1,-1)·(1,1) = {dot((1, -1), (1, 1))} ; (1,-1)·(1,-1) = {dot((1, -1), (1, -1))}")
    assert dot((3, 4), (3, 4)) == 25 and norme((3, 4)) == 5 and dot((1, -1), (1, 1)) == 0 and dot((1, -1), (1, -1)) == 2

    # Démonstration 3 — forme géométrique
    theta = math.radians(60)
    u, v = (2.0, 0.0), (3 * math.cos(theta), 3 * math.sin(theta))
    d_uv = tuple(a - b for a, b in zip(u, v))
    print(f"D3 : v = ({v[0]:.1f} ; {v[1]:.6f}) ; u·v = {dot(u, v):.1f} = {norme(u) * norme(v) * math.cos(theta):.1f} ;"
          f" ‖u−v‖² = {dot(d_uv, d_uv):.2f}")
    assert round(v[0], 1) == 1.5 and round(v[1], 6) == 2.598076 and round(v[1] ** 2, 2) == 6.75
    assert math.isclose(dot(u, v), 3) and math.isclose(dot(u, v), norme(u) * norme(v) * math.cos(theta))
    assert math.isclose(dot(d_uv, d_uv), 7) and math.isclose(4 + 9 - 2 * 2 * 3 * 0.5, 7) and dot((0, 0), (5, 7)) == 0

    # Démonstration 4 — Cauchy–Schwarz
    a4, b4 = (3, 4), (4, 3)
    disc = (2 * dot(a4, b4)) ** 2 - 4 * dot(b4, b4) * dot(a4, a4)
    print(f"D4 : (3,4)·(4,3) = {dot(a4, b4)} <= {norme(a4) * norme(b4):.0f} ; discriminant {disc} ;"
          f" égalité (3,4)·(6,8) = {dot(a4, (6, 8))} = {norme(a4) * norme((6, 8)):.0f}")
    assert dot(a4, b4) == 24 and dot(a4, a4) == 25 and 2 * dot(a4, b4) == 48 and disc == -196
    assert 48 ** 2 == 2304 and 4 * 25 * 25 == 2500 and dot(a4, (6, 8)) == 50 and math.isclose(norme(a4) * norme((6, 8)), 50)
    assert abs(dot(xr, yr)) <= norme(xr) * norme(yr)

    # Cas 1 — banque (sert aussi aux démonstrations 5 et 6)
    c1 = cas_1_faq_banque()
    q, docs, sc = c1["q"], c1["docs"], c1["scores"]
    assert [round(c, 2) for c in contributions(q, docs["d1"])] == [0.56, 0.02, 0.20, 0.02]
    assert [round(c, 2) for c in contributions(q, docs["d2"])] == [0.08, 0.09, 0.0, 0.06]
    assert [round(c, 2) for c in contributions(q, docs["d3"])] == [0.48, 0.0, 0.30, 0.10]
    assert [round(sc[k], 2) for k in ("d1", "d2", "d3")] == [0.80, 0.23, 0.88] and max(sc, key=sc.get) == "d3"
    assert round(dot(q, q), 2) == 0.94 and round(norme(q), 5) == 0.96954
    assert [round(dot(docs[k], docs[k]), 2) for k in ("d1", "d2", "d3")] == [0.70, 0.91, 0.97]
    assert [round(c1["normes"][k], 5) for k in ("d1", "d2", "d3")] == [0.83666, 0.95394, 0.98489]
    assert round(c1["la"]["d1"], 5) == 0.82514 and round(c1["la"]["d3"], 5) == 0.90765
    assert round(c1["cos"]["d1"], 5) == 0.98623 and round(c1["cos"]["d3"], 5) == 0.92158 and round(c1["cos"]["d2"], 5) == 0.24868
    assert c1["brut"] == "d3" and c1["normalise"] == "d1" and c1["mult"] == 20_480_000
    assert c1["transferts"] == 180 and c1["cout"] == 2_160

    # Démonstration 5 — la longueur décide du classement
    rc = c1["cos"]["d1"] / c1["cos"]["d3"]
    rn = c1["normes"]["d3"] / c1["normes"]["d1"]
    print(f"D5 : c1/c3 = {rc:.5f} < ‖d3‖/‖d1‖ = {rn:.5f} -> d3 devant au produit scalaire ; facteur d'égalité {0.80 / 0.88:.5f}")
    assert round(rc, 5) == 1.07015 and round(rn, 5) == 1.17716 and rn > rc and round(0.80 / 0.88, 5) == 0.90909
    assert math.isclose(dot(q, tuple(0.80 / 0.88 * a for a in docs["d3"])), 0.80)
    q5 = tuple(5 * a for a in q)
    assert max(docs, key=lambda k: dot(q5, docs[k])) == "d3"                 # λq ne change pas l'ordre

    # Démonstration 6 — perturbation
    e = (0.01, -0.01, 0.01, 0.0)
    ecart_31 = tuple(a - b for a, b in zip(docs["d3"], docs["d1"]))
    e_aligne = tuple(0.01 * a / c1["normes"]["d1"] for a in docs["d1"])
    print(f"D6 : e·d1 = {dot(e, docs['d1']):.3f} <= ‖e‖‖d1‖ = {norme(e):.6f} x {c1['normes']['d1']:.5f} = {norme(e) * c1['normes']['d1']:.6f} ;"
          f" ‖d3−d1‖ = {norme(ecart_31):.1f}, borne de l'écart {norme(e) * norme(ecart_31):.7f}")
    assert [round(c, 3) for c in contributions(e, docs["d1"])] == [0.007, -0.002, 0.004, 0.0] and round(dot(e, docs["d1"]), 3) == 0.009
    assert round(norme(e), 6) == 0.017321 and round(norme(e) * c1["normes"]["d1"], 6) == 0.014491
    assert math.isclose(dot(e_aligne, docs["d1"]), 0.01 * c1["normes"]["d1"]) and round(0.01 * c1["normes"]["d1"], 7) == 0.0083666
    assert [round(c, 1) for c in ecart_31] == [-0.1, -0.2, 0.2, 0.4] and round(dot(ecart_31, ecart_31), 2) == 0.25
    assert round(norme(ecart_31), 1) == 0.5 and round(norme(e) * norme(ecart_31), 7) == 0.0086603
    assert norme(e) * norme(ecart_31) < round(sc["d3"] - sc["d1"], 2) == 0.08

    # Cas 2 — BTP
    c2 = cas_2_facture_btp()
    assert c2["contrib"] == [54_000, 57_600, 54_400, 57_000] and c2["ht"] == 223_000
    assert c2["ecart_x"] == (6, 0, 0, 60) and c2["ecart"] == 4_980 and 6 * 450 == 2_700 and 60 * 38 == 2_280
    assert c2["facture_ht"] == 227_980 == c2["ht"] + c2["ecart"]
    assert round(c2["tva"]) == 11_150 and round(c2["ttc"]) == 234_150 and round(c2["retenue"]) == 22_300
    assert round(c2["ttc"] - c2["retenue"]) == 211_850 and round(c2["ecart"] * 1.05) == 5_229
    assert round(c2["seuil"]) == 1_115 and c2["decision"] == "bloquer"
    assert sum(c2["ecart_x"]) == 66 and sum(c2["prix"]) / 4 == 943.25 and round(c2["naif"], 1) == 62_254.5
    assert round(c2["naif"] / c2["ecart"], 1) == 12.5
    assert round(c2["seuil"] / 38, 1) == 29.3 and int(c2["seuil"] // 38) == 29 and round(c2["seuil"] / 450, 2) == 2.48

    # Cas 3 — assurance
    c3 = cas_3_score_fraude_assurance()
    assert round(c3["wx"], 2) == 3.42 and round(c3["s"], 2) == 0.42 and round(c3["marge"], 2) == 0.09
    assert round(c3["s"] - c3["marge"], 2) == 0.33 and round(c3["s"] + c3["marge"], 2) == 0.51
    assert 12_000 * 0.8 == 9_600 and c3["indemnite"] == 9_100 and c3["decision"] == "revue (zone grise)"
    assert round(0.06 * 12_000) == 720 and round(c3["s_unite"], 1) == 719.7 and 4_000 * 60 == 240_000
    assert round(0.12 * 4_000 * 60) == 28_800 and round(c3["bascule"], 5) == 0.31667 and round(c3["s_devis"], 3) == 0.492
    assert round(0.5 - c3["s"], 2) == 0.08 and round(c3["wx"] - 0.30, 2) == 3.12
    assert round(0.5 + 3.0 - 3.12, 2) == 0.38 and round(0.38 / 1.20, 5) == round(c3["bascule"], 5)

    # Cas 4 — immobilier
    c4 = cas_4_recherche_immobilier()
    assert c4["operations"] == 11_520_000 and round(c4["latence"], 2) == 5.76 and round(c4["charge"], 4) == 0.2304
    assert round(40 * c4["latence"], 1) == 230.4 and c4["n_bascule"] == 130_208 and c4["n_sature"] == 260_416
    assert c4["decision"] == "exhaustive" and c4["memoire"] == 46_080_000
    assert round(4 * c4["latence"], 2) == 23.04 and round(c4["projet"], 2) == 61.44 and c4["projet"] > 50
    assert c4["bascule_3072"] == 32_552

    # Corrigé
    print("Corrigé")
    e3 = dot((4, 6), (2, 2))
    print(f"  ex1 {dot((2, -1, 0), (3, 4, 5))} ; ex2 t = {3 / 2} ; ex3 {e3} = {25 - 5} ;"
          f" ex4 {dot((1, 2), (3, 4))} <= {norme((1, 2)) * norme((3, 4)):.3f} ; ex5 {50_000 * 768:,}")
    assert dot((2, -1, 0), (3, 4, 5)) == 2 and dot((1, 1.5), (3, -2)) == 0 and e3 == 20
    assert dot((1, 2), (3, 4)) == 11 and round(norme((1, 2)) * norme((3, 4)), 3) == 11.180
    assert math.isclose(norme((1, 2)) * norme((3, 4)), 5 * math.sqrt(5)) and 50_000 * 768 == 38_400_000
    ex6 = dot((121 - 120, 0, 0, 1510 - 1500), c2["prix"])
    xm = tuple(a - b for a, b in zip((3, 4), (1, 2)))
    print(f"  ex6 écart {ex6} AED HT ({ex6 * 1.05:.1f} TTC) -> {'payer' if ex6 <= c2['seuil'] else 'bloquer'} ;"
          f" ex7 ‖x−y‖² = {dot(xm, xm)} et non {25 - 5} ; ex8 discriminant {disc}")
    assert ex6 == 830 and round(ex6 * 1.05, 1) == 871.5 and ex6 <= c2["seuil"]
    assert xm == (2, 2) and dot(xm, xm) == 8 and 25 - 2 * dot((3, 4), (1, 2)) + 5 == 8
    try:
        dot((1, 2, 3), (4, 5))
    except ValueError:
        pass
    else:
        raise AssertionError("dimensions différentes acceptées")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
(1,2,3)·(4,-5,6) = 12 ; produits [4, -10, 18] ; cumul [4, -6, 12]
Fiche : x·y = 0.98 ; (2x)·y = 1.96 ; produits [1.12, 0.24, 0.6]
D1 : (x+z)·y = 26 = 12 + 14 ; (3x)·y = 36 ; Σ|xᵢyᵢ| = 32 pour x et pour -x
D2 : (3,4)·(3,4) = 25 ; (1,-1)·(1,1) = 0 ; (1,-1)·(1,-1) = 2
D3 : v = (1.5 ; 2.598076) ; u·v = 3.0 = 3.0 ; ‖u−v‖² = 7.00
D4 : (3,4)·(4,3) = 24 <= 25 ; discriminant -196 ; égalité (3,4)·(6,8) = 50 = 50
Cas 1 FAQ : q·d1 = 0.80   ‖d1‖ = 0.83666   cos = 0.98623
Cas 1 FAQ : q·d2 = 0.23   ‖d2‖ = 0.95394   cos = 0.24868
Cas 1 FAQ : q·d3 = 0.88   ‖d3‖ = 0.98489   cos = 0.92158
  brut -> d3, normalisé -> d1 ; 20,480,000 multiplications ; 180 transferts/jour = 2160 AED
D5 : c1/c3 = 1.07015 < ‖d3‖/‖d1‖ = 1.17716 -> d3 devant au produit scalaire ; facteur d'égalité 0.90909
D6 : e·d1 = 0.009 <= ‖e‖‖d1‖ = 0.017321 x 0.83666 = 0.014491 ; ‖d3−d1‖ = 0.5, borne de l'écart 0.0086603
Cas 2 BTP : HT devis 223000 AED ([54000, 57600, 54400, 57000]) ; écart (6, 0, 0, 60) -> 4980 AED HT
  TVA 11150, TTC 234150, retenue 22300, à payer 211850 ; tolérance 1115 -> bloquer ; naïf 62254.5 AED
Cas 3 ASSUR : contributions [0.72, 1.5, 0.9, 0.3], s = 0.42, intervalle [0.33 ; 0.51] -> revue (zone grise) ; en jeu 9100 AED
  devis en AED : s = 719.7 ; revues 240000 au lieu de 28800 AED ; bascule écart 0.31667 ; devis +10 % : s = 0.492
Cas 4 IMMO : 11,520,000 opérations, 5.76 ms, charge 0.2304 cœur -> exhaustive ; index 46,080,000 octets
  bascules N = 130208 (768) et 32552 (3072), saturation 260416 ; projet 61.44 ms (naïf 23.04 ms)
Corrigé
  ex1 2 ; ex2 t = 1.5 ; ex3 20 = 20 ; ex4 11 <= 11.180 ; ex5 38,400,000
  ex6 écart 830 AED HT (871.5 TTC) -> payer ; ex7 ‖x−y‖² = 8 et non 20 ; ex8 discriminant -196
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule le produit scalaire de deux vecteurs de même dimension, puis l'utilise pour classer des passages par rapport à une question, ou pour calculer un montant et expliquer un écart ligne par ligne.

```text
ALGORITHME ProduitScalaire
ENTRÉES : x = (x₁ … x_d), y = (y₁ … y_d)
SORTIE  : le nombre x · y

  SI dimension(x) ≠ dimension(y) ALORS ERREUR « dimensions différentes »
  s ← 0
  POUR i DE 1 À d FAIRE
      s ← s + xᵢ × yᵢ
  FIN POUR
  RETOURNER s

ALGORITHME ClasserPassages
ENTRÉES : question q, passages d₁ … d_N (normalisés à l'indexation)
SORTIE  : passages triés par score décroissant
  POUR CHAQUE passage dⱼ FAIRE scoreⱼ ← ProduitScalaire(q, dⱼ) FIN POUR
  RETOURNER les passages triés par scoreⱼ décroissant

ALGORITHME ExpliquerÉcart
ENTRÉES : quantités prévues x, quantités constatées x′, prix unitaires y, tolérance τ
SORTIE  : écart, lignes responsables, décision
  Δ ← x′ − x
  écart ← ProduitScalaire(Δ, y)                 (linéarité : x′ · y − x · y = Δ · y)
  lignes ← les i tels que Δᵢ × yᵢ ≠ 0
  SI écart > τ × ProduitScalaire(x, y) ALORS RETOURNER écart, lignes, « bloquer »
  RETOURNER écart, lignes, « payer »
```

**Complexité.** O(d) pour un produit scalaire ; O(N × d) pour comparer une question à N passages, plus O(N log N) pour le tri ; O(d) pour expliquer un écart. Le cas 4 chiffre ce coût : 15 000 × 768 = 11 520 000 multiplications-additions par requête, soit 5,76 ms sur un cœur ; c'est ce produit N × d qui pousse, au-delà d'une valeur de bascule, vers un index approché.

**Du squelette au code.** ProduitScalaire est la fonction `dot`, avec sa vérification de dimension ; `contributions` renvoie les termes xᵢyᵢ un par un. ClasserPassages correspond au dictionnaire `scores` de `cas_1_faq_banque` et à `max(scores, key=scores.get)`. La norme utilisée pour l'explication est `norme`, qui réutilise `dot(x, x)`. ExpliquerÉcart est le calcul de `ecart` et de `decision` dans `cas_2_facture_btp`. Le score linéaire est `cas_3_score_fraude_assurance` et le coût de la recherche exhaustive `cas_4_recherche_immobilier`.
