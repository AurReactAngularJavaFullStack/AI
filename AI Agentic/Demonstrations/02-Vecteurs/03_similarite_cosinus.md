# 03 — Similarité cosinus : démonstrations

> Fiche : [03 — Similarité cosinus](<../../Images/02-Vecteurs/03_similarite_cosinus.md>) · Image : `03_similarite_cosinus.jpg` · Leçon : [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\cos(x, y) = \frac{x \cdot y}{\lVert x \rVert \times \lVert y \rVert}
$$

Le cosinus mesure l'alignement des directions, sans tenir compte des longueurs. Il n'est défini que si x et y sont non nuls.

## Les symboles, un par un

La leçon de l'étape 14 écrit A, B et cos θ ; ce fichier suit la fiche et écrit x, y et cos(x, y).

$$
x, \quad y
$$

x et y sont les deux vecteurs comparés, non nuls et de même dimension d (une question et un passage, deux souvenirs, deux alertes) ; en Python, des tuples comme `q` ou `docs["d1"]`.

$$
x \cdot y
$$

x · y est le produit scalaire de la fiche 01, un réel sans borne ; en Python, `dot(x, y)`.

$$
\lVert x \rVert, \quad \lVert y \rVert
$$

‖x‖ et ‖y‖ sont les normes L2 de la fiche 02, réels > 0 ici ; en Python, `norme(x)`.

$$
\theta
$$

θ est l'angle entre les deux vecteurs, entre 0° et 180° ; en Python, `angle_deg(c)` le donne en degrés à partir du cosinus.

$$
\cos(x, y)
$$

cos(x, y) est la similarité cosinus, un réel sans unité dans [−1, 1] ; en Python, `cosinus(x, y)`.

$$
\hat{x} = \frac{x}{\lVert x \rVert}
$$

x̂ est le vecteur normalisé de la fiche 02, de longueur 1 ; en Python, `normaliser(x)`.

$$
\lambda
$$

λ est un réel non nul qui multiplie un vecteur dans la démonstration 2 ; en Python, les facteurs `3` et `-2` appliqués à (3 ; 4).

$$
s, \quad \delta
$$

s est le seuil de cosinus au-dessus duquel l'agent agit (répondre, rattacher, fusionner), δ la marge minimale exigée entre le meilleur candidat et le deuxième ; en Python, `seuil` et `marge`.

## Le mécanisme, avant les preuves

Ce qui entre, ce sont deux vecteurs non nuls de même dimension. La formule enchaîne trois opérations. Le produit scalaire au numérateur mélange deux informations : l'alignement des directions et les longueurs des deux vecteurs (fiche 01, démonstration 3). Les deux normes au dénominateur mesurent ces longueurs, et rien d'autre. La division retire exactement les longueurs et laisse l'alignement pur : ce qui sort est cos θ, un nombre sans unité compris entre −1 et 1.

Pourquoi diviser par le **produit** des normes, et pas par leur somme ou par la plus grande : parce que x · y = ‖x‖ ‖y‖ cos θ, et diviser par exactement ce produit isole cos θ. Une division par ‖x‖ + ‖y‖ laisserait un résultat qui change quand on double un seul des deux vecteurs. Le résultat se lit comme un angle : 1 pour la même direction, 0 pour des directions perpendiculaires, −1 pour des directions opposées, et un cosinus de 0,8 n'est pas « 80 % de chances » de quoi que ce soit.

Petit film chiffré, avec la question q = (0,8 ; 0,1 ; 0,5 ; 0,2) et le passage d₃ = (0,6 ; 0 ; 0,6 ; 0,5) du cas 1. Produit scalaire : 0,48 + 0 + 0,30 + 0,10 = 0,88. Normes : ‖q‖ = 0,96954 et ‖d₃‖ = 0,98489, de produit 0,95488. Division : 0,88 / 0,95488 = 0,92158. On double d₃ : le produit scalaire passe à 1,76, la norme à 1,96977, le produit des normes à 1,90976, et le quotient reste 0,92158 ; le facteur 2 est apparu en haut et en bas.

Analogie Java/Spring : comparer deux chaînes avec `equalsIgnoreCase` ignore la casse comme le cosinus ignore la longueur ; on retire volontairement une information (la casse, la longueur) pour ne comparer que ce qui compte (les lettres, la direction).

## Démonstration 1 — Le cosinus reste entre −1 et 1

**Ce qu'on démontre.** Pour x et y non nuls :

$$
-1 \le \cos(x, y) \le 1
$$

**L'idée.** L'inégalité de Cauchy–Schwarz dit que le produit scalaire ne dépasse jamais, en valeur absolue, le produit des normes. Le cosinus est leur quotient : il ne peut donc pas sortir de [−1, 1].

**La preuve, pas à pas.** Deux étapes.

**Étape 1.** Par Cauchy–Schwarz (fiche 01, démonstration 4) :

$$
\lvert x \cdot y \rvert \le \lVert x \rVert \, \lVert y \rVert
$$

**Étape 2.** On divise par ‖x‖ ‖y‖, strictement positif parce que x et y sont non nuls (fiche 02, démonstration 2) ; diviser par un nombre positif conserve le sens, et |cos| ≤ 1 équivaut à −1 ≤ cos ≤ 1 :

$$
\lvert \cos(x, y) \rvert = \frac{\lvert x \cdot y \rvert}{\lVert x \rVert \, \lVert y \rVert} \le 1
$$

∎

**Vérification chiffrée.** x = (3 ; 4) et y = (4 ; 3) : x · y = 24, ‖x‖ ‖y‖ = 25, cos = 0,96 ∈ [−1, 1]. Hypothèse nécessaire : si x = 0, le quotient est 0 / 0 et n'existe pas ; le code lève `ValueError` au lieu de renvoyer 0, qui masquerait un embedding vide.

**Ce que la preuve révèle du mécanisme.** La borne vient entièrement de Cauchy–Schwarz : le numérateur ne peut atteindre le dénominateur que pour des vecteurs alignés (démonstration 3).

**Conséquence pour un agent.** Une valeur hors de [−1, 1] trahit un bug : la ligne `dot / na * nb`, qui divise avant de multiplier, renvoie 24 / 5 × 5 = 24 pour (3 ; 4) et (4 ; 3) (exercice 8). On l'attrape par une assertion ; tronquer le résultat avec `max(-1.0, min(1.0, …))` ne doit servir qu'aux arrondis de l'ordre de 10⁻¹⁶.

## Démonstration 2 — La longueur ne compte pas

**Ce qu'on démontre.** Pour x et y non nuls et un réel λ ≠ 0 :

$$
\cos(\lambda x, y) = \frac{\lambda}{\lvert \lambda \rvert} \cos(x, y)
$$

donc cos(λx, y) = cos(x, y) si λ > 0, et cos(λx, y) = −cos(x, y) si λ < 0.

**L'idée.** Multiplier x par λ multiplie le numérateur par λ (linéarité) et le dénominateur par |λ| (homogénéité de la norme). Le quotient garde seulement le signe de λ.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Par linéarité du produit scalaire (fiche 01, démonstration 1), (λx) · y = λ (x · y).

**Étape 2.** Par homogénéité de la norme (fiche 02, démonstration 2), ‖λx‖ = |λ| ‖x‖.

**Étape 3.** On forme le quotient ; ‖x‖ ‖y‖ se retrouve en haut et en bas :

$$
\cos(\lambda x, y) = \frac{\lambda\, (x \cdot y)}{\lvert \lambda \rvert \, \lVert x \rVert \, \lVert y \rVert} = \frac{\lambda}{\lvert \lambda \rvert} \cos(x, y)
$$

Le quotient λ / |λ| vaut 1 si λ > 0 et −1 si λ < 0. ∎

**Vérification chiffrée.** Avec x = (3 ; 4) et y = (4 ; 3) : cos(3x, y) = cos((9 ; 12), (4 ; 3)) = (36 + 36) / (15 × 5) = 72 / 75 = 0,96 ; cos(−2x, y) = cos((−6 ; −8), (4 ; 3)) = −48 / (10 × 5) = −0,96. Pour λ = 0, le vecteur devient nul et le cosinus n'existe plus.

**Ce que la preuve révèle du mécanisme.** La division par les normes neutralise exactement l'échelle de chaque vecteur, et seulement elle : retourner un vecteur change le signe, l'allonger ne change rien. C'est la norme des **vecteurs** qui est neutralisée, pas la longueur des **textes** (leçon, étape 14).

**Conséquence pour un agent.** Le classement par cosinus ne favorise jamais un passage parce que son vecteur est long ; c'est ce qui corrige le défaut du produit scalaire brut (fiche 01, démonstration 5, et cas 1).

## Démonstration 3 — Cas d'égalité

**Ce qu'on démontre.** Pour x et y non nuls :

$$
\cos(x, y) = 1 \iff y = \lambda x \text{ avec } \lambda > 0
$$

et de même cos(x, y) = −1 si et seulement si y = λx avec λ < 0.

**L'idée.** Un cosinus de 1 veut dire que les vecteurs normalisés sont à distance nulle, donc égaux ; deux vecteurs qui ont la même direction normalisée sont multiples positifs l'un de l'autre.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Sens direct. Par la fiche 02 (démonstration 5), ‖x̂ − ŷ‖² = 2 − 2 cos(x, y) = 2 − 2 = 0.

**Étape 2.** Un vecteur de norme nulle est le vecteur nul (fiche 02, démonstration 2), donc x̂ = ŷ, c'est-à-dire x / ‖x‖ = y / ‖y‖, d'où y = (‖y‖ / ‖x‖) x avec ‖y‖ / ‖x‖ > 0.

**Étape 3.** Réciproque. Si y = λx avec λ > 0, la démonstration 2 (appliquée au second vecteur, le cosinus étant symétrique) donne cos(x, λx) = cos(x, x) = ‖x‖² / ‖x‖² = 1. Le cas −1 se traite de même avec λ < 0. ∎

**Vérification chiffrée.** (1 ; 2 ; 3) et (2 ; 4 ; 6) : produit scalaire 2 + 8 + 18 = 28, normes √14 et √56, produit √784 = 28, cosinus 1, avec λ = 2. (1 ; 0) et (−2 ; 0) : −2 / (1 × 2) = −1, avec λ = −2. Contre-exemple de « presque égal » : les souvenirs (0,5 ; 0,5 ; 0,7) et (0,52 ; 0,47 ; 0,71) du cas 4 ont un cosinus de 0,99930, très proche de 1 mais pas égal : ils ne sont pas colinéaires.

**Ce que la preuve révèle du mécanisme.** Le cosinus vaut 1 pour toute une demi-droite de vecteurs, pas pour un seul : il ne distingue pas deux textes dont les embeddings ne diffèrent que par l'échelle.

**Conséquence pour un agent.** Un cosinus exactement égal à 1 entre deux passages différents signale le plus souvent un doublon (même texte encodé deux fois, ou même texte à une casse près) : on peut le fusionner sans le relire, alors qu'un cosinus de 0,9993 demande encore un seuil (cas 4).

## Démonstration 4 — Cosinus et distance classent de la même façon

**Ce qu'on démontre.** Pour une question q et des passages d₁, …, d_N non nuls, trier les passages par cosinus décroissant ou par distance croissante entre vecteurs **normalisés** donne le même ordre, parce que

$$
\lVert \hat q - \hat d_j \rVert = \sqrt{2 - 2 \cos(q, d_j)}
$$

**L'idée.** La distance entre vecteurs normalisés est une fonction strictement décroissante du cosinus : plus le cosinus est grand, plus la distance est petite, sans exception.

**La preuve, pas à pas.** Deux étapes.

**Étape 1.** Par la fiche 02 (démonstration 5), ‖q̂ − d̂ⱼ‖² = 2 − 2 cos(q, dⱼ), et la racine carrée d'un nombre positif donne la distance.

**Étape 2.** La fonction c ↦ √(2 − 2c) est strictement décroissante sur [−1, 1], parce que c ↦ 2 − 2c l'est et que la racine carrée est strictement croissante. Si cos(q, dᵢ) > cos(q, dⱼ), alors ‖q̂ − d̂ᵢ‖ < ‖q̂ − d̂ⱼ‖ : les deux tris coïncident. ∎

**Vérification chiffrée.** Avec les cosinus du cas 1 : d₁ (0,98623) est à √(2 − 2 × 0,98623) = √0,027545 = 0,16597 (en gardant six décimales sous la racine) ; d₃ (0,92158) à 0,39603 ; d₂ (0,24868) à 1,22582. Contre-exemple sans normalisation : pour q = (1 ; 0), le passage a = (0,6 ; 0,8) a un cosinus de 0,6 et le passage b = (3 ; 3) un cosinus de 0,70711 ; pourtant la distance brute préfère a, ‖q − a‖ = √0,8 = 0,89443, à b, ‖q − b‖ = √13 = 3,60555.

**Ce que la preuve révèle du mécanisme.** Sur la sphère unité, il n'y a qu'une seule notion de proximité : distance et cosinus sont deux écritures de l'angle. Hors de la sphère, la distance brute mélange l'angle et les longueurs.

**Conséquence pour un agent.** Une base vectorielle réglée en distance L2 et une autre réglée en cosinus rendent les mêmes passages, à condition de normaliser à l'indexation et à la requête.

## Démonstration 5 — Le cosinus est le produit scalaire des vecteurs normalisés

**Ce qu'on démontre.** Pour x et y non nuls :

$$
\cos(x, y) = \hat x \cdot \hat y
$$

**L'idée.** Normaliser, c'est diviser chaque vecteur par sa norme ; par linéarité, ces deux divisions sortent du produit scalaire et redonnent la formule du cosinus.

**La preuve, pas à pas.** Deux étapes.

**Étape 1.** Par définition, x̂ = (1/‖x‖) x et ŷ = (1/‖y‖) y.

**Étape 2.** Par linéarité du produit scalaire dans chaque vecteur (fiche 01, démonstration 1), les deux facteurs sortent :

$$
\hat x \cdot \hat y = \frac{1}{\lVert x \rVert} \cdot \frac{1}{\lVert y \rVert} \, (x \cdot y) = \cos(x, y)
$$

∎

**Vérification chiffrée.** x = (3 ; 4) donne x̂ = (0,6 ; 0,8), y = (4 ; 3) donne ŷ = (0,8 ; 0,6), et x̂ · ŷ = 0,48 + 0,48 = 0,96 = cos(x, y).

**Ce que la preuve révèle du mécanisme.** Le coût du cosinus se partage : les normes se calculent une fois par vecteur, puis chaque comparaison n'est plus qu'un produit scalaire.

**Conséquence pour un agent.** On normalise l'index une fois pour toutes ; à la requête, on normalise la question une fois, et chaque cosinus coûte d multiplications, sans racine ni division (fiche 02, cas 1).

## Démonstration 6 — Près de 1, le cosinus écrase les écarts d'angle

**Ce qu'on démontre.** Pour un angle θ en radians :

$$
1 - \cos\theta = 2 \sin^2\!\left(\frac{\theta}{2}\right) \le \frac{\theta^2}{2}
$$

et 1 − cos θ ≈ θ²/2 quand θ est petit : l'écart à 1 croît comme le **carré** de l'angle.

**L'idée.** Deux vecteurs normalisés sont deux points du cercle unité dans leur plan ; la corde qui les relie mesure 2 sin(θ/2), et la démonstration 4 relie le carré de cette corde à 1 − cos θ. Pour un petit angle, la corde et l'arc se confondent.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Par la démonstration 4, la distance entre x̂ et ŷ vérifie ‖x̂ − ŷ‖² = 2 − 2 cos θ.

**Étape 2.** Le triangle (0, x̂, ŷ) est isocèle, de côtés 1 et d'angle au sommet θ ; la hauteur issue de 0 le coupe en deux triangles rectangles d'angle θ/2 et d'hypoténuse 1, donc la base mesure 2 sin(θ/2). En égalant les carrés :

$$
2 - 2\cos\theta = 4 \sin^2\!\left(\frac{\theta}{2}\right) \quad\Longrightarrow\quad 1 - \cos\theta = 2 \sin^2\!\left(\frac{\theta}{2}\right)
$$

**Étape 3.** Pour u ≥ 0, sin u ≤ u, parce que u − sin u vaut 0 en 0 et a pour dérivée 1 − cos u ≥ 0. Avec u = θ/2, on élève au carré deux nombres positifs : 2 sin²(θ/2) ≤ 2 (θ/2)² = θ²/2. ∎

**Vérification chiffrée.** θ = 10° = 0,174533 rad : 1 − cos θ = 0,015192 et θ²/2 = 0,015231, à 0,25 % près. θ = 60° : 1 − cos θ = 0,5 et θ²/2 = 0,548311, l'approximation se dégrade pour un grand angle. Les seuils usuels se lisent en angle : 0,8 ↔ 36,87°, 0,95 ↔ 18,19°, 0,97 ↔ 14,07°, 0,99 ↔ 8,11°, 0,999 ↔ 2,56°.

**Ce que la preuve révèle du mécanisme.** Près de 1, une petite différence de cosinus cache une grande différence d'angle : entre 0,99 et 0,999, l'angle est divisé par plus de trois. Les cosinus des passages pertinents se tassent donc tous près de 1.

**Conséquence pour un agent.** Un seuil de déduplication se règle avec trois décimales ou en degrés, pas « à vue » : passer de 0,99 à 0,95 double l'angle toléré (cas 4).

## Exemple simple, à la main

x = (1 ; 0) et y = (1 ; 1). Produit scalaire : 1 × 1 + 0 × 1 = 1. Normes : ‖x‖ = √1 = 1 et ‖y‖ = √(1 + 1) = √2. Quotient :

$$
\cos(x, y) = \frac{1}{1 \times \sqrt{2}} = \frac{1}{1{,}414214} = 0{,}707107
$$

C'est le cosinus de 45° : y est la diagonale du carré construit sur x.

Avec x = (1 ; 2 ; 3) et y = (3 ; 2 ; 1) : x · y = 3 + 4 + 3 = 10, ‖x‖ = ‖y‖ = √14, produit des normes 14, cosinus 10 / 14 = 0,714286.

## Cas d'usage complexes, démontrés

### Cas 1 — Banque de détail à Dubaï : reclasser la FAQ et filtrer le top-k

**Contexte.** On reprend l'agent de FAQ de la banque de détail de Dubaï (fiche 01, cas 1), qui classait les passages par produit scalaire brut. L'équipe passe au cosinus et ajoute un seuil d'injection : un passage n'entre dans le prompt que si son cosinus atteint 0,5, même s'il fait partie du top-3. La question : quels passages l'agent injecte-t-il, et que rapporte le seuil ? Les vecteurs (réduits à 4 dimensions), le volume et les prix sont illustratifs.

**Données.**

| Vecteur | Contenu | Coordonnées |
| --- | --- | --- |
| q | « I forgot my password, how do I reset it? » | 0,8 ; 0,1 ; 0,5 ; 0,2 |
| d₁ | procédure de réinitialisation | 0,7 ; 0,2 ; 0,4 ; 0,1 |
| d₂ | frais de la carte | 0,1 ; 0,9 ; 0 ; 0,3 |
| d₃ | article général sur la sécurité | 0,6 ; 0 ; 0,6 ; 0,5 |

Autres données : top-k avec k = 3 ; seuil d'injection s = 0,5 ; 350 tokens par passage injecté ; 3 000 questions de ce type par jour ; 3 USD par million de tokens d'entrée, à 3,6725 AED par USD.

**Calcul pas à pas.** Arrondis à 5 décimales.

**Étape 1.** Produits scalaires (fiche 01) : q · d₁ = 0,80, q · d₂ = 0,23, q · d₃ = 0,88.

**Étape 2.** Normes : ‖q‖ = √0,94 = 0,96954, ‖d₁‖ = √0,70 = 0,83666, ‖d₂‖ = √0,91 = 0,95394, ‖d₃‖ = √0,97 = 0,98489.

**Étape 3.** Cosinus :

$$
\cos(q, d_1) = \frac{0{,}80}{0{,}96954 \times 0{,}83666} = 0{,}98623, \qquad \cos(q, d_2) = \frac{0{,}23}{0{,}96954 \times 0{,}95394} = 0{,}24868
$$

$$
\cos(q, d_3) = \frac{0{,}88}{0{,}96954 \times 0{,}98489} = 0{,}92158
$$

**Étape 4.** Contrôle d'invariance (démonstration 2) : avec d₃ doublé, le produit scalaire passe à 1,76 et la norme à 1,96977, et le cosinus reste 0,92158.

**Étape 5.** Seuil : d₁ et d₃ dépassent 0,5, d₂ non.

**Décision de l'agent.** L'agent injecte d₁ puis d₃, dans cet ordre, et écarte d₂ bien qu'il fasse partie du top-3. Le seuil économise 350 × 3 000 = 1 050 000 tokens par jour, soit 1,05 × 3 = 3,15 USD = 11,57 AED par jour, et surtout il évite de mettre sous les yeux du modèle un passage sur les frais de carte sans rapport avec la question.

**Contre-calcul.** Le produit scalaire brut mettait d₃ devant d₁ (0,88 contre 0,80), et un top-3 sans seuil injecte d₂ dans chaque réponse : le modèle lit d'abord l'article général et risque de répondre par des conseils de sécurité au lieu de la procédure, pour 1 050 000 tokens inutiles par jour.

**Sensibilité.** En angle (démonstration 6), d₁ est à 9,52° de la question et d₃ à 22,84° : 13,3° les séparent, un écart qu'aucune perturbation raisonnable de la question n'inverse. Le seuil bascule pour d₂ à 0,24868 (en dessous, il entrerait) et pour d₃ à 0,92158 (au-dessus, il sortirait) : tout seuil entre ces deux valeurs donne la même décision, ce qui laisse une large marge de réglage.

**En production.** On suit la part des questions dont le meilleur cosinus reste sous 0,5 ; l'agent y répond qu'il transmet à un conseiller au lieu d'inventer une procédure. On la suit séparément en arabe et en anglais, parce qu'un même modèle d'embedding n'a pas la même distribution de cosinus dans les deux langues. Les règles de la CBUAE sur le service client sont à confirmer avec le texte en vigueur.

### Cas 2 — Entité de services publics en ligne : répondre ou demander une précision

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, reçoit 40 000 questions par mois, en arabe, en anglais ou mélangées. Son agent compare chaque question normalisée aux fiches de procédure. Il ne répond que si le meilleur cosinus atteint s = 0,90 **et** devance le deuxième d'au moins δ = 0,05 ; sinon, il demande une précision. Avant de vectoriser, l'équipe normalise l'arabe (formes de l'alef, ta marbuta, diacritiques). La question : que fait l'agent sur trois questions types, et que coûterait l'absence de normalisation ? Vecteurs, seuils, volumes et coûts sont illustratifs.

**Données.** Coordonnées sur quatre axes de sens : renouveler, perte, carte, adresse.

| Vecteur | Contenu | Coordonnées | Norme |
| --- | --- | --- | --- |
| f₁ | fiche « renouveler sa carte » | 0,9 ; 0,1 ; 0,8 ; 0 | √1,46 = 1,20830 |
| f₂ | fiche « remplacer une carte perdue » | 0,3 ; 0,9 ; 0,8 ; 0 | √1,54 = 1,24097 |
| f₃ | fiche « changer d'adresse » | 0,2 ; 0 ; 0,1 ; 0,9 | √0,86 = 0,92736 |
| q | « ma carte a expiré », arabe normalisé | 0,7 ; 0,3 ; 0,7 ; 0,1 | √1,08 = 1,03923 |
| q′ | même question, arabe non normalisé (clé `q_brut` du programme) | 0,7 ; 0,3 ; 0,2 ; 0,1 | √0,63 = 0,79373 |
| q₂ | « j'ai un problème avec ma carte » | 0,6 ; 0,5 ; 0,7 ; 0 | √1,10 = 1,04881 |

Part des questions arabes avec une variante d'écriture : 30 % des 40 000 ; 5 % des usagers à qui l'on demande une précision inutile abandonnent et appellent le centre de contact, à 25 AED l'appel.

**Calcul pas à pas.** Arrondis à 5 décimales.

**Étape 1.** Question q : produits scalaires 1,22, 1,04 et 0,30, d'où

$$
\cos(q, f_1) = \frac{1{,}22}{1{,}03923 \times 1{,}20830} = 0{,}97156, \qquad \cos(q, f_2) = 0{,}80642, \qquad \cos(q, f_3) = 0{,}31129
$$

Marge : 0,97156 − 0,80642 = 0,16514.

**Étape 2.** Question q′ : le mot « carte » écrit avec une variante d'alef n'a pas été reconnu, la troisième coordonnée tombe à 0,2 :

$$
\cos(q_{\text{brut}}, f_1) = \frac{0{,}82}{0{,}79373 \times 1{,}20830} = 0{,}85500
$$

**Étape 3.** Question q₂ : produits scalaires 1,15 et 1,19 avec f₁ et f₂, d'où cos(q₂, f₁) = 0,90745 et cos(q₂, f₂) = 0,91430, marge 0,00685.

**Décision de l'agent.** Pour q : 0,97156 ≥ 0,90 et marge 0,16514 ≥ 0,05, l'agent répond avec la fiche f₁. Pour q₂ : le meilleur cosinus 0,91430 dépasse le seuil, mais la marge 0,00685 est trop faible ; l'agent demande « s'agit-il d'un renouvellement ou d'une carte perdue ? » au lieu de deviner. Pour q′ : 0,85500 < 0,90, l'agent demanderait une précision alors que la question était claire, d'où la normalisation de l'arabe.

**Contre-calcul.** Sans normalisation de l'arabe, les 30 % de questions arabes avec une variante d'écriture, soit 0,30 × 40 000 = 12 000 par mois, risquent la même chute que q′ : autant de précisions demandées pour rien. Avec 5 % d'abandons vers le centre de contact, cela fait 12 000 × 0,05 = 600 appels, soit 600 × 25 = 15 000 AED par mois. Sans la marge δ, à l'inverse, q₂ serait envoyé vers « carte perdue » une fois sur deux selon des différences de cosinus de l'ordre de 0,007, sans aucun sens.

**Sensibilité.** Valeurs de bascule : q′ serait accepté avec un seuil s ≤ 0,85500, et q₂ avec une marge δ ≤ 0,00685. Baisser s à 0,85 pour « sauver » q′ accepterait aussi des questions mal comprises : la normalisation corrige la cause, le seuil n'en masquerait que l'effet.

**En production.** On suit la part des sessions qui aboutissent à la bonne procédure sans appel au centre de contact, et la part des demandes de précision, séparément pour l'arabe et pour l'anglais. Seules les fiches publiques sont vectorisées, aucune donnée personnelle de l'usager ; le régime de protection des données applicable à l'entité est à confirmer avec le texte en vigueur.

### Cas 3 — Groupe de construction à Dubaï : rattacher les lignes de facture aux postes du devis

**Contexte.** Un groupe de construction qui mène de grands chantiers à Dubaï reçoit 400 lignes de facture de sous-traitants par mois, dont les libellés reprennent rarement ceux du devis signé. Son agent vectorise chaque ligne et chaque poste, puis rattache automatiquement la ligne au poste de plus grand cosinus si ce cosinus atteint s = 0,85 et devance le deuxième d'au moins δ = 0,05 ; sinon, la ligne part chez le contrôleur de gestion avec les deux candidats. La question : que devient chacune des deux lignes reçues ce jour-là ? Vecteurs, seuils, volumes et coûts sont illustratifs.

**Données.** Axes de sens : béton, plancher, voile, coffrage.

| Vecteur | Libellé | Coordonnées | Norme |
| --- | --- | --- | --- |
| P₁ | poste « béton armé, plancher R+3 » | 0,9 ; 0,8 ; 0 ; 0,1 | √1,46 = 1,20830 |
| P₂ | poste « béton armé, voile R+3 » | 0,9 ; 0,1 ; 0,8 ; 0,1 | √1,47 = 1,21244 |
| P₃ | poste « coffrage plancher R+3 » | 0,2 ; 0,7 ; 0 ; 0,9 | √1,34 = 1,15758 |
| L₁ | ligne « coulage dalle niveau 3 » | 0,8 ; 0,7 ; 0,1 ; 0,2 | √1,18 = 1,08628 |
| L₂ | ligne « béton niveau 3 », 30 m³ à 450 AED | 0,9 ; 0,3 ; 0,3 ; 0,1 | √1,00 = 1 |

Contrôle manuel : 4 minutes par ligne, à 3 AED la minute.

**Calcul pas à pas.** Arrondis à 5 décimales.

**Étape 1.** Ligne L₁ : produits scalaires 0,72 + 0,56 + 0 + 0,02 = 1,30 avec P₁, 0,72 + 0,07 + 0,08 + 0,02 = 0,89 avec P₂, 0,16 + 0,49 + 0 + 0,18 = 0,83 avec P₃ ; d'où

$$
\cos(L_1, P_1) = \frac{1{,}30}{1{,}08628 \times 1{,}20830} = 0{,}99043, \qquad \cos(L_1, P_2) = 0{,}67576, \qquad \cos(L_1, P_3) = 0{,}66006
$$

**Étape 2.** Marge de L₁ : 0,99043 − 0,67576 = 0,31467 avec les cosinus arrondis ; le programme, qui n'arrondit pas en cours de route, trouve 0,31468.

**Étape 3.** Ligne L₂ : produits scalaires 1,06, 1,09 et 0,48 ; comme ‖L₂‖ = 1,

$$
\cos(L_2, P_1) = \frac{1{,}06}{1{,}20830} = 0{,}87726, \qquad \cos(L_2, P_2) = \frac{1{,}09}{1{,}21244} = 0{,}89902, \qquad \cos(L_2, P_3) = 0{,}41466
$$

**Étape 4.** Marge de L₂ : 0,89902 − 0,87726 = 0,02176 avec les cosinus arrondis, 0,02175 sans arrondi intermédiaire.

**Décision de l'agent.** L₁ est rattachée automatiquement à P₁ (0,99043 ≥ 0,85, marge 0,31468 ≥ 0,05). L₂ part chez le contrôleur : son meilleur poste, P₂, dépasse le seuil, mais la marge 0,02175 est trop faible pour distinguer « plancher » de « voile ». Le contrôle coûte 4 × 3 = 12 AED.

**Contre-calcul.** Avec le seuil seul, sans marge, L₂ serait rattachée automatiquement à P₂, le voile, alors qu'il s'agit du plancher : ses 30 × 450 = 13 500 AED HT afficheraient un faux dépassement sur le voile et masqueraient un vrai dépassement sur le plancher, découvert seulement à la clôture du lot. Douze AED de contrôle contre une erreur de 13 500 AED mal imputée : la marge paie largement son coût.

**Sensibilité.** La décision sur L₂ bascule si δ ≤ 0,02175. Sur L₁, il faudrait un seuil au-dessus de 0,99043 ou une marge au-dessus de 0,31468 pour refuser le rattachement : la ligne est très loin des deux bascules. Avec 400 lignes par mois, chaque point de pourcentage de lignes envoyées au contrôleur coûte 4 lignes × 12 = 48 AED par mois.

**En production.** On suit la part des rattachements automatiques que le contrôleur ne corrige pas (alerte sous 98 %) et la part des lignes envoyées au contrôle. Le montant hors taxe, la TVA de 5 % et la retenue de garantie se calculent ensuite par des règles exactes (fiche 01, cas 2) ; le cosinus ne sert qu'à trouver le poste.

### Cas 4 — Plateforme d'actifs virtuels agréée VARA : regrouper les alertes d'un même incident

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA reçoit environ 1 200 alertes par jour. Son agent d'exploitation vectorise chaque message d'alerte et regroupe deux alertes dans le même incident si leur cosinus atteint un seuil s, pour que l'opérateur n'en traite qu'une. Trois alertes arrivent à la suite : m₁ et m₂ signalent un retrait bloqué, m₃ un écart de prix entre deux sources de cotation. La question : quel seuil choisir pour regrouper m₁ et m₂ sans absorber m₃ ? Vecteurs, volumes et durées sont illustratifs.

**Données.**

| Alerte | Contenu | Coordonnées | Norme |
| --- | --- | --- | --- |
| m₁ | retrait bloqué, portefeuille A | 0,5 ; 0,5 ; 0,7 | √0,99 = 0,99499 |
| m₂ | retrait bloqué, portefeuille A, relance | 0,52 ; 0,47 ; 0,71 | 0,99770 |
| m₃ | écart de prix entre deux sources | 0,7 ; 0,3 ; 0,7 | √1,07 = 1,03441 |

Seuils candidats : 0,95 et 0,99. Volume : 1 200 alertes par jour, 3,75 alertes par incident en moyenne, 4 minutes de traitement par groupe.

**Calcul pas à pas.** Cosinus à 5 décimales, angles à 2 décimales.

**Étape 1.** Paire m₁, m₂ : produit scalaire 0,26 + 0,235 + 0,497 = 0,992, d'où

$$
\cos(m_1, m_2) = \frac{0{,}992}{0{,}99499 \times 0{,}99770} = 0{,}99930 \;\leftrightarrow\; 2{,}15°
$$

**Étape 2.** Paire m₁, m₃ : produit scalaire 0,35 + 0,15 + 0,49 = 0,99, d'où

$$
\cos(m_1, m_3) = \frac{0{,}99}{0{,}99499 \times 1{,}03441} = 0{,}96189 \;\leftrightarrow\; 15{,}87°
$$

**Étape 3.** Paire m₂, m₃ : produit scalaire 0,364 + 0,141 + 0,497 = 1,002, cosinus 0,97091 ↔ 13,85°.

**Étape 4.** Un seuil sépare correctement les incidents s'il est au-dessus du plus grand cosinus entre incidents différents (0,97091) et au plus égal au cosinus entre alertes du même incident (0,99930). Le seuil 0,99 vaut 8,11° : il laisse 8,11 − 2,15 = 5,96° de marge côté m₂ et 13,85 − 8,11 = 5,74° côté m₃.

**Décision de l'agent.** Seuil 0,99 : m₁ et m₂ sont regroupées, m₃ ouvre un incident distinct. Sur la journée, 1 200 alertes à 3,75 par incident font 1 200 / 3,75 = 320 groupes, soit 320 × 4 = 1 280 minutes de traitement au lieu de 1 200 × 4 = 4 800 sans regroupement.

**Contre-calcul.** Avec le seuil 0,95, qui « paraît » exigeant, m₃ (0,96189 avec m₁, 0,97091 avec m₂) est absorbée dans l'incident du retrait bloqué : l'écart de prix n'est jamais traité comme tel, alors qu'il peut faire exécuter des ordres à un mauvais prix. En angle, 0,95 tolère 18,19°, plus du double des 8,11° du seuil 0,99 (démonstration 6).

**Sensibilité.** L'intervalle des seuils corrects va de 0,97091 (exclu) à 0,99930 (inclus). En angle, de 2,15° à 13,85° ; son milieu, 8,00°, correspond à un cosinus de 0,99027, très proche du seuil retenu. Un seuil de 0,97 (14,07°) serait déjà du mauvais côté pour la paire m₂, m₃.

**En production.** On suit le nombre d'alertes par groupe et, sur un échantillon relu par l'astreinte, la part de groupes qui mélangent deux types d'incident (objectif zéro). Chaque regroupement, son cosinus et la décision de l'opérateur sont journalisés pour être expliqués lors d'un contrôle ; les exigences de la VARA en la matière sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer cos((1 ; 2), (2 ; 4)).

**Exercice 2.** Calculer cos((1 ; 0), (0 ; 1)) et l'angle correspondant.

**Exercice 3.** Calculer cos((1 ; 2 ; 3), (3 ; 2 ; 1)).

**Exercice 4.** Calculer cos((3 ; 4), (−3 ; −4)).

**Exercice 5.** Quel angle correspond à un cosinus de 0,5 ?

**Exercice 6.** Montrer que cos(x, y) = x̂ · ŷ, où x̂ et ŷ sont les vecteurs normalisés.

**Exercice 7.** Dans le cas 3, le sous-traitant précise le libellé de L₂ : « béton plancher niveau 3 », vecteur (0,9 ; 0,6 ; 0,2 ; 0,1). Calculer les cosinus avec P₁ et P₂, la marge, et la nouvelle décision.

**Exercice 8.** Trouver l'erreur. Un collègue code `cosinus = dot / na * nb` et obtient 24 pour (3 ; 4) et (4 ; 3). Expliquer le résultat, dire pourquoi il est impossible, et corriger.

**Exercice 9.** Redémontrer de mémoire l'invariance d'échelle (démonstration 2), puis calculer cos((9 ; 12), (4 ; 3)) et cos((−6 ; −8), (4 ; 3)).

## Corrigé

**Exercice 1.** (2 ; 4) = 2 × (1 ; 2), avec λ = 2 > 0 : par la démonstration 3, le cosinus vaut 1. Contrôle : 2 + 8 = 10, normes √5 et √20, produit √100 = 10, quotient 1.

**Exercice 2.** Produit scalaire 1 × 0 + 0 × 1 = 0, donc cosinus 0 : les vecteurs sont orthogonaux, l'angle vaut 90°.

**Exercice 3.** x · y = 3 + 4 + 3 = 10 ; ‖x‖ = ‖y‖ = √(1 + 4 + 9) = √14, produit 14 ; cosinus 10 / 14 = 0,714286.

**Exercice 4.** (−3 ; −4) = −1 × (3 ; 4), avec λ = −1 < 0 : cosinus −1. Contrôle : (−9 − 16) / (5 × 5) = −25 / 25 = −1.

**Exercice 5.** L'angle dont le cosinus vaut 0,5 est 60°, le triangle équilatéral coupé en deux.

**Exercice 6.** x̂ · ŷ = (x / ‖x‖) · (y / ‖y‖). Par linéarité, les deux facteurs 1/‖x‖ et 1/‖y‖ sortent du produit scalaire : x̂ · ŷ = (x · y) / (‖x‖ ‖y‖) = cos(x, y).

**Exercice 7.** Norme de la ligne : √(0,81 + 0,36 + 0,04 + 0,01) = √1,22 = 1,10454. Produits scalaires : avec P₁, 0,81 + 0,48 + 0 + 0,01 = 1,30 ; avec P₂, 0,81 + 0,06 + 0,16 + 0,01 = 1,04. Cosinus : 1,30 / (1,10454 × 1,20830) = 0,97406 et 1,04 / (1,10454 × 1,21244) = 0,77660. Marge 0,97406 − 0,77660 = 0,19746 (0,19747 sans arrondi intermédiaire) ≥ 0,05 et 0,97406 ≥ 0,85 : la décision change, la ligne est rattachée automatiquement au poste plancher P₁.

**Exercice 8.** Python évalue `dot / na * nb` de gauche à droite : (24 / 5) × 5 = 24. Un cosinus de 24 viole la démonstration 1 (|cos| ≤ 1), ce qui trahit le bug. Correction : `dot / (na * nb)` = 24 / 25 = 0,96.

**Exercice 9.** Étape 1 : (λx) · y = λ (x · y) par linéarité. Étape 2 : ‖λx‖ = |λ| ‖x‖ par homogénéité. Étape 3 : le quotient vaut (λ / |λ|) cos(x, y). Calculs : (9 ; 12) = 3 × (3 ; 4), donc 0,96 ; (−6 ; −8) = −2 × (3 ; 4), donc −0,96.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dot(x, y)`** — Cette fonction est la même que dans la fiche 01, le caissier qui passe deux colonnes en parallèle et additionne les produits ligne à ligne : elle reçoit deux vecteurs, lève une `ValueError` « dimensions différentes » s'ils n'ont pas la même longueur, et renvoie la somme x₁y₁ + x₂y₂ + … de leurs produits terme à terme. Ici elle sert de numérateur au cosinus et donne par exemple 0,88 pour la question q et le passage d3 du cas 1, ou 24 pour (3, 4) et (4, 3), le point de départ du bug de parenthèses que la démonstration 1 démasque.

**`norme(x)`** — Comme dans la fiche 02, cette fonction est l'arpenteur qui mesure la longueur d'une flèche, mais elle passe ici par `dot` : elle reçoit un vecteur, calcule son produit scalaire avec lui-même, c'est-à-dire la somme des carrés de ses coordonnées, et renvoie la racine carrée de ce nombre. Elle fournit les deux longueurs du dénominateur du cosinus, 0,96954 pour q et 0,98489 pour d3 dans le mécanisme, et permet de vérifier que doubler d3 double sa norme, qui passe à 1,96977, sans rien changer à l'angle.

**`cosinus(x, y)`** — Celle-ci est le rapporteur qu'on pose entre deux flèches pour lire leur écart de direction en oubliant leur longueur : elle reçoit deux vecteurs, calcule leurs deux normes, lève une `ValueError` « cosinus indéfini pour un vecteur nul » si l'une d'elles vaut 0, et renvoie sinon le produit scalaire divisé par le produit des normes, x · y / (‖x‖ × ‖y‖), avec les parenthèses qui évitent le faux cosinus de 24. Elle donne 0,92158 pour q et d3, 0,707107 pour (1, 0) et (1, 1), et c'est sur ses résultats que s'appuient toutes les décisions des quatre cas.

**`normaliser(x)`** — Cette fonction ramène une flèche à la longueur 1 en gardant son cap, comme un pilote qui ne retient d'un trajet que la direction de la boussole : elle reçoit un vecteur, calcule sa norme, lève une `ValueError` « vecteur nul : pas de direction » si elle est nulle, puis renvoie le tuple des coordonnées divisées par cette norme. Elle transforme (3, 4) en (0.6, 0.8) et (4, 3) en (0.8, 0.6), dont le simple produit scalaire redonne le cosinus 0,96, ce que la démonstration 5 vérifie, et `main` s'en sert aussi pour montrer que la distance entre vecteurs normalisés vaut √(2 − 2 cos).

**`angle_deg(c)`** — Ici l'on suit un géomètre qui traduit un cosinus en degrés, l'unité que l'opérateur comprend d'un coup d'œil : la fonction reçoit un cosinus, lève une `ValueError` « cosinus hors de [-1, 1] : bug en amont » s'il dépasse 1 en valeur absolue de plus de 10⁻¹², ramène sinon un léger débordement d'arrondi dans [−1, 1], puis renvoie l'arc cosinus converti en degrés. Elle donne 45° pour 0,707107, 9,52° et 22,84° pour les passages d1 et d3 du cas 1, et 8,11° pour le seuil 0,99 du cas 4, ce qui rend visible la marge de chaque seuil.

**`choisir(cosinus_par_candidat, seuil, marge)`** — Cette fonction est l'aiguilleur prudent qui ne lance un train que si la voie est à la fois sûre et sans ambiguïté : elle reçoit un dictionnaire de cosinus par candidat, un seuil et une marge, trie les candidats du plus grand au plus petit cosinus, garde le premier et calcule son écart avec le deuxième. Elle renvoie le triplet formé du meilleur candidat, de cet écart et de la décision, « agir » seulement si le meilleur cosinus atteint le seuil et si l'écart atteint la marge, « demander » sinon ; c'est elle qui tranche dans les cas 2 et 3 et dans l'exercice 7, où la ligne est rattachée à P1 avec une marge de 0,19747.

**`cas_1_faq_banque()`** — Cette fonction reprend le documentaliste de la banque de détail de la fiche 01, qui passe maintenant au cosinus avec un seuil d'injection de 0,5 : avec la question q et les trois passages, elle calcule les cosinus 0,98623, 0,24868 et 0,92158, les range dans l'ordre d1, d3, d2 et n'injecte que d1 et d3, écartant d2 bien qu'il soit dans le top-3. Elle vérifie qu'un d3 doublé garde le même cosinus, chiffre l'économie de 350 tokens par passage sur 3 000 questions par jour, soit 1 050 000 tokens, 3,15 USD et 11,57 AED, traduit les cosinus en angles de 9,52° et 22,84°, imprime trois lignes et renvoie ces valeurs dans un dictionnaire.

**`cas_2_guichet_public()`** — On y voit le guichetier d'un service public en ligne qui ne répond que s'il est sûr de la procédure, avec un seuil de 0,90 et une marge de 0,05 : la fonction compare trois questions aux trois fiches f1, f2 et f3 et passe chaque jeu de cosinus à `choisir`. La question q bien normalisée obtient 0,97156 pour f1 avec une marge de 0,16514, d'où « agir » ; sa version à l'arabe non normalisé tombe à 0,855 et la question vague q2 ne départage f2 et f1 que de 0,00685, d'où « demander » dans les deux cas. Elle chiffre enfin le coût de l'absence de normalisation, 12 000 questions, 600 appels et 15 000 AED par mois, et renvoie fiches, questions, résultats et coûts.

**`cas_3_rapprochement_btp()`** — Cette fonction met en scène le contrôleur de gestion d'un groupe de construction qui rattache les lignes de facture aux postes du devis, avec un seuil de 0,85 et une marge de 0,05 : pour chaque ligne, elle calcule les cosinus avec les postes P1, P2 et P3 et laisse `choisir` décider. La ligne L1 va à P1 avec un cosinus de 0,99043 et une marge de 0,31468, donc « agir », tandis que L2 préfère P2 à 0,89902 mais ne devance P1 que de 0,02175 et part chez le contrôleur ; la fonction imprime aussi le coût de 12 AED d'un contrôle manuel et les 13 500 AED HT mal imputés qu'il évite, puis renvoie postes, lignes, résultats et coût du contrôle.

**`cas_4_alertes_crypto()`** — Ici l'on suit l'opérateur d'astreinte d'une plateforme d'actifs virtuels qui veut regrouper les alertes d'un même incident sans en noyer un autre : la fonction calcule les cosinus des trois paires d'alertes, 0,9993 pour m1 et m2, 0,96189 pour m1 et m3, 0,97091 pour m2 et m3, avec leurs angles de 2,15°, 15,87° et 13,85°. Avec le seuil 0,99, seuls m1 et m2 sont regroupés, alors qu'à 0,95 l'alerte m3 serait absorbée ; elle compte ensuite 320 groupes et 1 280 minutes de traitement au lieu de 4 800, calcule le milieu en angle de l'intervalle correct, 8,00°, soit un cosinus de 0,99027, et renvoie ces grandeurs dans un dictionnaire.

**`main()`** — C'est le professeur qui refait chaque calcul de la fiche au tableau, sous le contrôle d'un `assert` à chaque ligne : il commence par le mécanisme et l'exemple simple, démasque le bug `dot / na * nb` qui donne 24 au lieu de 0,96, vérifie que le cosinus reste dans [−1, 1], refuse le vecteur nul, ne bouge pas quand on multiplie un vecteur par 3 et change de signe quand on le multiplie par −2. Il appelle ensuite le cas 1 pour les démonstrations 4 à 6, la distance √(2 − 2 cos), le produit des vecteurs normalisés et l'approximation de 1 − cos θ par θ²/2, puis les trois autres cas et les exercices du corrigé, et n'imprime « OK — toutes les vérifications sont passées. » qu'au bout de ce parcours sans faute.

```python
"""Démonstration 03 — similarité cosinus : bornes, invariance, égalité, distance, angle, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def dot(x, y) -> float:
    """Produit scalaire (fiche 01) ; refuse deux dimensions différentes."""
    if len(x) != len(y):
        raise ValueError("dimensions différentes")
    return sum(a * b for a, b in zip(x, y))


def norme(x) -> float:
    """Norme L2 (fiche 02)."""
    return math.sqrt(dot(x, x))


def cosinus(x, y) -> float:
    """cos(x, y) = x · y / (‖x‖ × ‖y‖) ; indéfini pour un vecteur nul."""
    nx, ny = norme(x), norme(y)
    if nx == 0 or ny == 0:
        raise ValueError("cosinus indéfini pour un vecteur nul")
    return dot(x, y) / (nx * ny)


def normaliser(x) -> tuple:
    """x̂ = x / ‖x‖."""
    n = norme(x)
    if n == 0:
        raise ValueError("vecteur nul : pas de direction")
    return tuple(a / n for a in x)


def angle_deg(c: float) -> float:
    """Angle en degrés d'un cosinus ; un arrondi de 1e-12 au-delà de ±1 est ramené, pas davantage."""
    if abs(c) > 1 + 1e-12:
        raise ValueError("cosinus hors de [-1, 1] : bug en amont")
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def choisir(cosinus_par_candidat: dict, seuil: float, marge: float) -> tuple:
    """Renvoie (meilleur, écart au deuxième, décision) : agir seulement si seuil ET marge sont tenus."""
    tries = sorted(cosinus_par_candidat.items(), key=lambda kv: kv[1], reverse=True)
    (meilleur, c1), (_, c2) = tries[0], tries[1]
    ecart = c1 - c2
    decision = "agir" if c1 >= seuil and ecart >= marge else "demander"
    return meilleur, ecart, decision


def cas_1_faq_banque() -> dict:
    """[BANQUE] FAQ à Dubaï : reclassement par le cosinus et seuil d'injection 0.5."""
    q = (0.8, 0.1, 0.5, 0.2)
    docs = {"d1": (0.7, 0.2, 0.4, 0.1), "d2": (0.1, 0.9, 0.0, 0.3), "d3": (0.6, 0.0, 0.6, 0.5)}
    seuil, tokens, par_jour, prix_million, taux = 0.5, 350, 3_000, 3.0, 3.6725
    c = {k: cosinus(q, d) for k, d in docs.items()}
    ordre = sorted(c, key=c.get, reverse=True)
    injectes = [k for k in ordre if c[k] >= seuil]
    d3x2 = tuple(2 * a for a in docs["d3"])
    economie = tokens * par_jour
    usd = economie / 1e6 * prix_million
    angles = {k: angle_deg(v) for k, v in c.items()}
    print("Cas 1 FAQ : cosinus " + " ; ".join(f"{k} {v:.5f}" for k, v in c.items()) + f" -> injectés {injectes}")
    print(f"  d3 doublé : produit scalaire {dot(q, d3x2):.2f}, norme {norme(d3x2):.5f}, cosinus {cosinus(q, d3x2):.5f} ;"
          f" économie {economie:,} tokens/jour = {usd:.2f} USD = {usd * taux:.2f} AED")
    print(f"  angles d1 {angles['d1']:.2f}°, d3 {angles['d3']:.2f}°, écart {angles['d3'] - angles['d1']:.1f}°")
    return {"q": q, "docs": docs, "c": c, "ordre": ordre, "injectes": injectes, "d3x2": d3x2,
            "economie": economie, "usd": usd, "aed": usd * taux, "angles": angles}


def cas_2_guichet_public() -> dict:
    """[PUBLIC] guichet UAE Pass : répondre si cos >= 0.90 et marge >= 0.05, sinon demander une précision."""
    fiches = {"f1": (0.9, 0.1, 0.8, 0.0), "f2": (0.3, 0.9, 0.8, 0.0), "f3": (0.2, 0.0, 0.1, 0.9)}
    questions = {"q": (0.7, 0.3, 0.7, 0.1), "q_brut": (0.7, 0.3, 0.2, 0.1), "q2": (0.6, 0.5, 0.7, 0.0)}
    seuil, marge, par_mois, part_variantes, abandon, cout_appel = 0.90, 0.05, 40_000, 0.30, 0.05, 25
    resultats = {}
    for nom, v in questions.items():
        cos = {k: cosinus(v, f) for k, f in fiches.items()}
        resultats[nom] = (cos, choisir(cos, seuil, marge))
        meilleur, ecart, decision = resultats[nom][1]
        print(f"Cas 2 UAE Pass : {nom} -> " + " ; ".join(f"{k} {c:.5f}" for k, c in cos.items())
              + f" ; meilleur {meilleur}, marge {ecart:.5f} -> {decision}")
    touchees = round(part_variantes * par_mois)
    appels = round(touchees * abandon)
    print(f"  sans normalisation de l'arabe : {touchees} questions, {appels} appels, {appels * cout_appel} AED/mois")
    return {"fiches": fiches, "questions": questions, "resultats": resultats, "touchees": touchees,
            "appels": appels, "cout": appels * cout_appel}


def cas_3_rapprochement_btp() -> dict:
    """[BTP] Dubaï : rattacher une ligne de facture au poste du devis si cos >= 0.85 et marge >= 0.05."""
    postes = {"P1": (0.9, 0.8, 0.0, 0.1), "P2": (0.9, 0.1, 0.8, 0.1), "P3": (0.2, 0.7, 0.0, 0.9)}
    lignes = {"L1": (0.8, 0.7, 0.1, 0.2), "L2": (0.9, 0.3, 0.3, 0.1)}
    seuil, marge, minutes, prix_minute = 0.85, 0.05, 4, 3
    resultats = {}
    for nom, v in lignes.items():
        cos = {k: cosinus(v, p) for k, p in postes.items()}
        resultats[nom] = (cos, choisir(cos, seuil, marge))
        meilleur, ecart, decision = resultats[nom][1]
        print(f"Cas 3 BTP : {nom} -> " + " ; ".join(f"{k} {c:.5f}" for k, c in cos.items())
              + f" ; meilleur {meilleur}, marge {ecart:.5f} -> {decision}")
    print(f"  contrôle d'une ligne : {minutes * prix_minute} AED ; montant mal imputé évité : {30 * 450} AED HT")
    return {"postes": postes, "lignes": lignes, "resultats": resultats, "controle": minutes * prix_minute}


def cas_4_alertes_crypto() -> dict:
    """[CRYPTO] plateforme agréée VARA : regrouper les alertes d'un même incident, seuil 0.99 contre 0.95."""
    m1, m2, m3 = (0.5, 0.5, 0.7), (0.52, 0.47, 0.71), (0.7, 0.3, 0.7)
    par_jour, par_incident, minutes = 1_200, 3.75, 4
    m = cosinus(m1, m2)
    c13, c23 = cosinus(m1, m3), cosinus(m2, m3)
    seuil = 0.99
    groupes = {"m1-m2": m >= seuil, "m1-m3": c13 >= seuil, "m2-m3": c23 >= seuil}
    absorbe_a_095 = c13 >= 0.95 or c23 >= 0.95
    milieu = (angle_deg(m) + angle_deg(c23)) / 2
    print(f"Cas 4 VARA : m1-m2 {m:.5f} ({angle_deg(m):.2f}°), m1-m3 {c13:.5f} ({angle_deg(c13):.2f}°),"
          f" m2-m3 {c23:.5f} ({angle_deg(c23):.2f}°)")
    print(f"  seuil {seuil} ({angle_deg(seuil):.2f}°) : regroupements {groupes} ; à 0.95, m3 absorbée : {absorbe_a_095}")
    print(f"  {par_jour / par_incident:.0f} groupes, {par_jour / par_incident * minutes:.0f} min au lieu de {par_jour * minutes} ;"
          f" milieu en angle {milieu:.2f}° -> cos {math.cos(math.radians(milieu)):.5f}")
    return {"m": m, "c13": c13, "c23": c23, "groupes": groupes, "absorbe": absorbe_a_095,
            "milieu": milieu, "seuil": seuil, "groupes_jour": par_jour / par_incident,
            "minutes": par_jour / par_incident * minutes}


def main() -> None:
    # Mécanisme et exemple simple
    q, d3 = (0.8, 0.1, 0.5, 0.2), (0.6, 0.0, 0.6, 0.5)
    d3x2 = tuple(2 * a for a in d3)
    print(f"Mécanisme : q·d3 = {dot(q, d3):.2f}, normes {norme(q):.5f} et {norme(d3):.5f}, produit {norme(q) * norme(d3):.5f},"
          f" cos {cosinus(q, d3):.5f} ; doublé : {dot(q, d3x2):.2f} / {norme(q) * norme(d3x2):.5f}")
    assert round(dot(q, d3), 2) == 0.88 and round(norme(q) * norme(d3), 5) == 0.95488 and round(cosinus(q, d3), 5) == 0.92158
    assert round(norme(d3x2), 5) == 1.96977 and round(norme(q) * norme(d3x2), 5) == 1.90976
    print(f"Exemple : cos((1,0),(1,1)) = {cosinus((1, 0), (1, 1)):.6f} ({angle_deg(cosinus((1, 0), (1, 1))):.0f}°) ;"
          f" cos((1,2,3),(3,2,1)) = {cosinus((1, 2, 3), (3, 2, 1)):.6f}")
    assert round(cosinus((1, 0), (1, 1)), 6) == 0.707107 and round(math.sqrt(2), 6) == 1.414214
    assert round(angle_deg(cosinus((1, 0), (1, 1)))) == 45 and dot((1, 2, 3), (3, 2, 1)) == 10
    assert math.isclose(norme((1, 2, 3)) * norme((3, 2, 1)), 14) and round(cosinus((1, 2, 3), (3, 2, 1)), 6) == 0.714286

    # Démonstrations 1 à 3
    a, b = (3, 4), (4, 3)
    faux = dot(a, b) / norme(a) * norme(b)
    print(f"D1 : cos((3,4),(4,3)) = {cosinus(a, b):.2f} ; bug dot / na * nb = {faux:.0f}")
    assert dot(a, b) == 24 and norme(a) * norme(b) == 25 and math.isclose(cosinus(a, b), 0.96) and faux == 24
    x, y = (1.5, -2.0, 0.5), (-0.5, 3.0, 2.0)
    assert -1 <= cosinus(x, y) <= 1
    try:
        cosinus((0, 0), (1, 2))
    except ValueError:
        pass
    else:
        raise AssertionError("vecteur nul accepté")
    print(f"D2 : cos(3x, y) = {cosinus((9, 12), b):.2f} ({dot((9, 12), b)}/{norme((9, 12)) * norme(b):.0f}) ;"
          f" cos(-2x, y) = {cosinus((-6, -8), b):.2f}")
    assert dot((9, 12), b) == 72 and norme((9, 12)) == 15 and math.isclose(cosinus((9, 12), b), 0.96)
    assert dot((-6, -8), b) == -48 and math.isclose(cosinus((-6, -8), b), -0.96)
    assert math.isclose(cosinus(tuple(-2 * a_ for a_ in x), y), -cosinus(x, y))
    m12 = cosinus((0.5, 0.5, 0.7), (0.52, 0.47, 0.71))
    print(f"D3 : cos((1,2,3),(2,4,6)) = {cosinus((1, 2, 3), (2, 4, 6)):.0f} ; cos((1,0),(-2,0)) = {cosinus((1, 0), (-2, 0)):.0f} ;"
          f" presque égal : {m12:.5f}")
    assert dot((1, 2, 3), (2, 4, 6)) == 28 and math.isclose(norme((1, 2, 3)) * norme((2, 4, 6)), 28)
    assert math.isclose(cosinus((1, 2, 3), (2, 4, 6)), 1) and cosinus((1, 0), (-2, 0)) == -1 and round(m12, 5) == 0.9993

    # Démonstrations 4 à 6
    c1 = cas_1_faq_banque()
    dist = {k: math.sqrt(2 - 2 * v) for k, v in c1["c"].items()}
    qa, aa, bb = (1, 0), (0.6, 0.8), (3, 3)
    print(f"D4 : distances normalisées d1 {dist['d1']:.5f}, d3 {dist['d3']:.5f}, d2 {dist['d2']:.5f} ;"
          f" brut : cos a {cosinus(qa, aa):.1f}, b {cosinus(qa, bb):.5f}, distances {norme((0.4, -0.8)):.5f} et {norme((-2, -3)):.5f}")
    assert round(2 - 2 * c1["c"]["d1"], 6) == 0.027545
    assert [round(dist[k], 5) for k in ("d1", "d3", "d2")] == [0.16597, 0.39603, 1.22582]
    assert sorted(dist, key=dist.get) == c1["ordre"]
    for k in c1["docs"]:
        assert math.isclose(norme(tuple(p - r for p, r in zip(normaliser(c1["q"]), normaliser(c1["docs"][k])))), dist[k])
    assert round(cosinus(qa, aa), 1) == 0.6 and round(cosinus(qa, bb), 5) == 0.70711
    assert round(norme((0.4, -0.8)), 5) == 0.89443 and round(norme((-2, -3)), 5) == 3.60555
    xh, yh = normaliser(a), normaliser(b)
    print(f"D5 : x̂ = {xh}, ŷ = {yh}, x̂·ŷ = {dot(xh, yh):.2f}")
    assert xh == (0.6, 0.8) and yh == (0.8, 0.6) and math.isclose(dot(xh, yh), cosinus(a, b))
    assert math.isclose(dot(normaliser(x), normaliser(y)), cosinus(x, y))
    t10, t60 = math.radians(10), math.radians(60)
    seuils = {s: angle_deg(s) for s in (0.8, 0.95, 0.97, 0.99, 0.999)}
    print(f"D6 : 10° = {t10:.6f} rad, 1 - cos = {1 - math.cos(t10):.6f}, θ²/2 = {t10 ** 2 / 2:.6f} ; 60° : {1 - math.cos(t60):.1f}"
          f" et {t60 ** 2 / 2:.6f} ; seuils " + " ; ".join(f"{s} -> {v:.2f}°" for s, v in seuils.items()))
    assert round(t10, 6) == 0.174533 and round(1 - math.cos(t10), 6) == 0.015192 and round(t10 ** 2 / 2, 6) == 0.015231
    assert round(1 - (1 - math.cos(t10)) / (t10 ** 2 / 2), 4) == 0.0025 and math.isclose(1 - math.cos(t60), 0.5)
    assert round(t60 ** 2 / 2, 6) == 0.548311
    assert [round(v, 2) for v in seuils.values()] == [36.87, 18.19, 14.07, 8.11, 2.56] and seuils[0.99] / seuils[0.999] > 3
    for t in (0.01, 0.3, 1.0, 2.5):
        assert math.isclose(1 - math.cos(t), 2 * math.sin(t / 2) ** 2) and 1 - math.cos(t) <= t * t / 2

    # Cas 1 — banque
    cc = c1["c"]
    assert [round(cc[k], 5) for k in ("d1", "d2", "d3")] == [0.98623, 0.24868, 0.92158] and c1["ordre"] == ["d1", "d3", "d2"]
    assert c1["injectes"] == ["d1", "d3"] and round(dot(c1["q"], c1["d3x2"]), 2) == 1.76
    assert math.isclose(cosinus(c1["q"], c1["d3x2"]), cc["d3"]) and max(c1["docs"], key=lambda k: dot(c1["q"], c1["docs"][k])) == "d3"
    assert c1["economie"] == 1_050_000 and round(c1["usd"], 2) == 3.15 and round(c1["aed"], 2) == 11.57
    assert round(c1["angles"]["d1"], 2) == 9.52 and round(c1["angles"]["d3"], 2) == 22.84
    assert round(c1["angles"]["d3"] - c1["angles"]["d1"], 1) == 13.3

    # Cas 2 — secteur public
    c2 = cas_2_guichet_public()
    f, qs, r2 = c2["fiches"], c2["questions"], c2["resultats"]
    assert [round(dot(v, v), 2) for v in f.values()] == [1.46, 1.54, 0.86]
    assert [round(norme(v), 5) for v in f.values()] == [1.2083, 1.24097, 0.92736]
    assert [round(dot(v, v), 2) for v in qs.values()] == [1.08, 0.63, 1.10]
    assert [round(norme(v), 5) for v in qs.values()] == [1.03923, 0.79373, 1.04881]
    assert [round(dot(qs["q"], v), 2) for v in f.values()] == [1.22, 1.04, 0.30]
    assert [round(v, 5) for v in r2["q"][0].values()] == [0.97156, 0.80642, 0.31129]
    assert r2["q"][1][0] == "f1" and round(r2["q"][1][1], 5) == 0.16514 and r2["q"][1][2] == "agir"
    assert round(dot(qs["q_brut"], f["f1"]), 2) == 0.82 and round(r2["q_brut"][0]["f1"], 5) == 0.855 and r2["q_brut"][1][2] == "demander"
    assert [round(dot(qs["q2"], f[k]), 2) for k in ("f1", "f2")] == [1.15, 1.19]
    assert round(r2["q2"][0]["f1"], 5) == 0.90745 and round(r2["q2"][0]["f2"], 5) == 0.9143
    assert r2["q2"][1][0] == "f2" and round(r2["q2"][1][1], 5) == 0.00685 and r2["q2"][1][2] == "demander"
    assert c2["touchees"] == 12_000 and c2["appels"] == 600 and c2["cout"] == 15_000

    # Cas 3 — BTP
    c3 = cas_3_rapprochement_btp()
    p, lg, r3 = c3["postes"], c3["lignes"], c3["resultats"]
    assert [round(dot(v, v), 2) for v in p.values()] == [1.46, 1.47, 1.34]
    assert [round(norme(v), 5) for v in p.values()] == [1.2083, 1.21244, 1.15758]
    assert round(dot(lg["L1"], lg["L1"]), 2) == 1.18 and round(norme(lg["L1"]), 5) == 1.08628 and math.isclose(norme(lg["L2"]), 1)
    assert [round(dot(lg["L1"], v), 2) for v in p.values()] == [1.30, 0.89, 0.83]
    assert [round(v, 5) for v in r3["L1"][0].values()] == [0.99043, 0.67576, 0.66006]
    assert r3["L1"][1][0] == "P1" and round(r3["L1"][1][1], 5) == 0.31468 and r3["L1"][1][2] == "agir"
    assert round(round(r3["L1"][0]["P1"], 5) - round(r3["L1"][0]["P2"], 5), 5) == 0.31467
    assert [round(dot(lg["L2"], v), 2) for v in p.values()] == [1.06, 1.09, 0.48]
    assert [round(v, 5) for v in r3["L2"][0].values()] == [0.87726, 0.89902, 0.41466]
    assert r3["L2"][1][0] == "P2" and round(r3["L2"][1][1], 5) == 0.02175 and r3["L2"][1][2] == "demander"
    assert round(round(r3["L2"][0]["P2"], 5) - round(r3["L2"][0]["P1"], 5), 5) == 0.02176
    assert c3["controle"] == 12 and 30 * 450 == 13_500 and 400 // 100 * 12 == 48

    # Cas 4 — crypto
    c4 = cas_4_alertes_crypto()
    assert round(norme((0.5, 0.5, 0.7)) ** 2, 2) == 0.99 and round(norme((0.5, 0.5, 0.7)), 5) == 0.99499
    assert round(norme((0.52, 0.47, 0.71)), 5) == 0.9977 and round(norme((0.7, 0.3, 0.7)), 5) == 1.03441
    assert round(dot((0.5, 0.5, 0.7), (0.52, 0.47, 0.71)), 3) == 0.992 and round(c4["m"], 5) == 0.9993
    assert round(dot((0.5, 0.5, 0.7), (0.7, 0.3, 0.7)), 2) == 0.99 and round(c4["c13"], 5) == 0.96189
    assert round(dot((0.52, 0.47, 0.71), (0.7, 0.3, 0.7)), 3) == 1.002 and round(c4["c23"], 5) == 0.97091
    assert [round(angle_deg(v), 2) for v in (c4["m"], c4["c13"], c4["c23"])] == [2.15, 15.87, 13.85]
    assert c4["groupes"] == {"m1-m2": True, "m1-m3": False, "m2-m3": False} and c4["absorbe"]
    assert c4["c23"] < c4["seuil"] <= c4["m"] and round(angle_deg(0.99), 2) == 8.11
    assert round(8.11 - 2.15, 2) == 5.96 and round(13.85 - 8.11, 2) == 5.74
    assert round(c4["groupes_jour"]) == 320 and round(c4["minutes"]) == 1_280 and 1_200 * 4 == 4_800
    assert round(c4["milieu"], 2) == 8.0 and round(math.cos(math.radians(c4["milieu"])), 5) == 0.99027
    assert angle_deg(0.97) > angle_deg(c4["c23"]) and round(angle_deg(0.95) / angle_deg(0.99), 1) > 2

    # Corrigé
    print("Corrigé")
    angle = angle_deg(0.5)
    print(f"  ex1 {cosinus((1, 2), (2, 4)):.0f} ; ex2 {cosinus((1, 0), (0, 1))} ; ex3 {cosinus((1, 2, 3), (3, 2, 1)):.6f} ;"
          f" ex4 {cosinus((3, 4), (-3, -4)):.0f} ; ex5 {angle:.0f}°")
    assert math.isclose(cosinus((1, 2), (2, 4)), 1) and cosinus((1, 0), (0, 1)) == 0 and dot((1, 2), (2, 4)) == 10
    assert round(cosinus((1, 2, 3), (3, 2, 1)), 6) == 0.714286 and math.isclose(cosinus((3, 4), (-3, -4)), -1)
    assert dot((3, 4), (-3, -4)) == -25 and round(angle) == 60
    l7 = (0.9, 0.6, 0.2, 0.1)
    cos7 = {k: cosinus(l7, v) for k, v in p.items()}
    meilleur7, ecart7, decision7 = choisir(cos7, 0.85, 0.05)
    print(f"  ex7 P1 {cos7['P1']:.5f}, P2 {cos7['P2']:.5f}, marge {ecart7:.5f} -> {decision7} {meilleur7} ;"
          f" ex8 {faux:.0f} -> {dot(a, b) / (norme(a) * norme(b)):.2f} ; ex9 {cosinus((9, 12), b):.2f} et {cosinus((-6, -8), b):.2f}")
    assert round(dot(l7, l7), 2) == 1.22 and round(norme(l7), 5) == 1.10454
    assert [round(dot(l7, p[k]), 2) for k in ("P1", "P2")] == [1.30, 1.04]
    assert round(cos7["P1"], 5) == 0.97406 and round(cos7["P2"], 5) == 0.7766 and round(ecart7, 5) == 0.19747
    assert round(round(cos7["P1"], 5) - round(cos7["P2"], 5), 5) == 0.19746
    assert decision7 == "agir" and meilleur7 == "P1"
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Mécanisme : q·d3 = 0.88, normes 0.96954 et 0.98489, produit 0.95488, cos 0.92158 ; doublé : 1.76 / 1.90976
Exemple : cos((1,0),(1,1)) = 0.707107 (45°) ; cos((1,2,3),(3,2,1)) = 0.714286
D1 : cos((3,4),(4,3)) = 0.96 ; bug dot / na * nb = 24
D2 : cos(3x, y) = 0.96 (72/75) ; cos(-2x, y) = -0.96
D3 : cos((1,2,3),(2,4,6)) = 1 ; cos((1,0),(-2,0)) = -1 ; presque égal : 0.99930
Cas 1 FAQ : cosinus d1 0.98623 ; d2 0.24868 ; d3 0.92158 -> injectés ['d1', 'd3']
  d3 doublé : produit scalaire 1.76, norme 1.96977, cosinus 0.92158 ; économie 1,050,000 tokens/jour = 3.15 USD = 11.57 AED
  angles d1 9.52°, d3 22.84°, écart 13.3°
D4 : distances normalisées d1 0.16597, d3 0.39603, d2 1.22582 ; brut : cos a 0.6, b 0.70711, distances 0.89443 et 3.60555
D5 : x̂ = (0.6, 0.8), ŷ = (0.8, 0.6), x̂·ŷ = 0.96
D6 : 10° = 0.174533 rad, 1 - cos = 0.015192, θ²/2 = 0.015231 ; 60° : 0.5 et 0.548311 ; seuils 0.8 -> 36.87° ; 0.95 -> 18.19° ; 0.97 -> 14.07° ; 0.99 -> 8.11° ; 0.999 -> 2.56°
Cas 2 UAE Pass : q -> f1 0.97156 ; f2 0.80642 ; f3 0.31129 ; meilleur f1, marge 0.16514 -> agir
Cas 2 UAE Pass : q_brut -> f1 0.85500 ; f2 0.64975 ; f3 0.33964 ; meilleur f1, marge 0.20525 -> demander
Cas 2 UAE Pass : q2 -> f1 0.90745 ; f2 0.91430 ; f3 0.19535 ; meilleur f2, marge 0.00685 -> demander
  sans normalisation de l'arabe : 12000 questions, 600 appels, 15000 AED/mois
Cas 3 BTP : L1 -> P1 0.99043 ; P2 0.67576 ; P3 0.66006 ; meilleur P1, marge 0.31468 -> agir
Cas 3 BTP : L2 -> P1 0.87726 ; P2 0.89902 ; P3 0.41466 ; meilleur P2, marge 0.02175 -> demander
  contrôle d'une ligne : 12 AED ; montant mal imputé évité : 13500 AED HT
Cas 4 VARA : m1-m2 0.99930 (2.15°), m1-m3 0.96189 (15.87°), m2-m3 0.97091 (13.85°)
  seuil 0.99 (8.11°) : regroupements {'m1-m2': True, 'm1-m3': False, 'm2-m3': False} ; à 0.95, m3 absorbée : True
  320 groupes, 1280 min au lieu de 4800 ; milieu en angle 8.00° -> cos 0.99027
Corrigé
  ex1 1 ; ex2 0.0 ; ex3 0.714286 ; ex4 -1 ; ex5 60°
  ex7 P1 0.97406, P2 0.77660, marge 0.19747 -> agir P1 ; ex8 24 -> 0.96 ; ex9 0.96 et -0.96
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme mesure l'alignement de deux vecteurs, sans tenir compte de leurs longueurs, et sert à classer des passages, à décider entre plusieurs candidats avec un seuil et une marge, ou à fusionner des alertes et des souvenirs presque identiques.

```text
ALGORITHME Cosinus
ENTRÉES : x, y de même dimension d
SORTIE  : cos(x, y) dans [−1 ; 1]

  p ← ProduitScalaire(x, y)
  nx ← Norme(x)
  ny ← Norme(y)
  SI nx = 0 OU ny = 0 ALORS ERREUR « cosinus indéfini pour un vecteur nul »
  RETOURNER p / (nx × ny)

ALGORITHME ChoisirAvecMarge
ENTRÉES : vecteur v, candidats c₁ … c_K (K ≥ 2), seuil s, marge δ
SORTIE  : (meilleur candidat, écart au deuxième, « agir » ou « demander »)
  POUR CHAQUE candidat cⱼ FAIRE scoreⱼ ← Cosinus(v, cⱼ) FIN POUR
  trier les candidats par score décroissant
  écart ← score₁ − score₂
  SI score₁ ≥ s ET écart ≥ δ ALORS RETOURNER (c₁, écart, « agir »)
  RETOURNER (c₁, écart, « demander »)

ALGORITHME Dédupliquer
ENTRÉES : alerte ou souvenir m, éléments existants, seuil (par exemple 0,99)
  POUR CHAQUE élément existant e FAIRE
      SI Cosinus(m, e) ≥ seuil ALORS RETOURNER « fusionner avec e »
  FIN POUR
  RETOURNER « ajouter m »
```

**Complexité.** O(d) pour un cosinus (trois passages sur les coordonnées). Choisir parmi K candidats coûte O(K × d) plus O(K log K) pour le tri ; dédupliquer contre M éléments coûte O(M × d). Si tous les vecteurs sont normalisés à l'avance, le cosinus se réduit au produit scalaire (démonstration 5).

**Du squelette au code.** Cosinus est la fonction `cosinus`, qui appelle `dot` et `norme` ; `angle_deg` convertit un cosinus en degrés. ChoisirAvecMarge est la fonction `choisir`, utilisée par `cas_2_guichet_public` et `cas_3_rapprochement_btp`. Le classement du RAG est le dictionnaire `c` de `cas_1_faq_banque`. La déduplication est le test `m >= seuil` de `cas_4_alertes_crypto`, avec le seuil 0,99 justifié par la démonstration 6.
