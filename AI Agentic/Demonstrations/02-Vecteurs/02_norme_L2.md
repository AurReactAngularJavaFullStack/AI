# 02 — Norme L2 : démonstrations

> Fiche : [02 — Norme L2](<../../Images/02-Vecteurs/02_norme_L2.md>) · Image : `02_norme_L2.jpg` · Leçon : [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\lVert x \rVert = \sqrt{x_1^2 + x_2^2 + \dots + x_d^2} = \sqrt{x \cdot x}
$$

La norme est la longueur du vecteur.

## Les symboles, un par un

La leçon de l'étape 14 écrit A et n ; ce fichier suit la fiche et écrit x et d.

$$
x
$$

x est le vecteur mesuré, une liste de d réels (un embedding, un vecteur de caractéristiques, un vecteur d'écarts) ; en Python, un tuple comme `v`.

$$
x_i
$$

xᵢ est la coordonnée numéro i, un réel de signe quelconque ; en Python, l'élément `a` dans `for a in x`.

$$
x_i^2
$$

xᵢ² est la coordonnée au carré, toujours ≥ 0 : le carré efface le signe et grossit les grandes coordonnées ; en Python, `a * a`.

$$
d
$$

d est la dimension, un entier ≥ 1 ; en Python, `len(x)`.

$$
\lVert x \rVert
$$

‖x‖ est la norme L2, la longueur euclidienne, réel ≥ 0 dans l'unité des coordonnées ; en Python, `norme(x)`.

$$
\hat{x} = \frac{x}{\lVert x \rVert}
$$

x̂ est le vecteur normalisé, de même direction que x et de longueur 1, défini seulement si x ≠ 0 ; en Python, `normaliser(x)`.

$$
\lambda
$$

λ est un réel qui multiplie un vecteur dans les démonstrations ; en Python, `lam`.

$$
\lVert x - y \rVert
$$

‖x − y‖ est la distance euclidienne entre x et y, la norme de leur différence ; en Python, `distance(x, y)`.

$$
\cos(x, y)
$$

cos(x, y) est la similarité cosinus de la fiche 03, dans [−1, 1] ; en Python, la variable `cos`.

$$
z_i = \frac{v_i - \mu_i}{\sigma_i}
$$

zᵢ est une caractéristique standardisée : la valeur brute vᵢ moins sa moyenne μᵢ, divisée par son écart-type σᵢ > 0 ; sans unité, elle se lit « nombre d'écarts-types au-dessus de la moyenne » ; en Python, `standardiser(valeurs, moyennes, ecarts)`.

## Le mécanisme, avant les preuves

Ce qui entre, ce sont d coordonnées de signes quelconques. La première opération est le carré de chaque coordonnée : il efface le signe (−3 et 3 donnent tous deux 9) et il grossit les grandes coordonnées plus que les petites (3 devient 9, mais 0,1 devient 0,01). La deuxième opération est la somme : elle cumule ces carrés, sans qu'aucune compensation soit possible, puisque tous les termes sont positifs. La troisième est la racine carrée : elle ramène le résultat dans l'unité des coordonnées et rend la norme homogène, ‖2x‖ = 2‖x‖, alors que la somme des carrés seule serait multipliée par 4. Ce qui sort est un réel ≥ 0, nul seulement pour le vecteur nul.

Pourquoi des carrés et pas des valeurs absolues : la somme des |xᵢ| (la norme L1) existe aussi, mais seule la somme des carrés est égale au produit scalaire x · x. C'est ce lien qui rend vrai le théorème de Pythagore (démonstration 1), qui fait de la longueur une quantité qui ne dépend pas de l'orientation des axes, et qui donne l'identité ‖x̂ − ŷ‖² = 2 − 2 cos(x, y) entre distance et cosinus (démonstration 5). Le prix à payer : comme les carrés grossissent les grandes valeurs, une seule coordonnée nettement plus grande que les autres domine la norme (démonstration 6).

Petit film chiffré, avec x = (3 ; 4). Carrés : 9 et 16. Somme : 25. Racine : 5. Avec (1 ; 2 ; 2) : carrés 1, 4, 4 ; somme 9 ; racine 3. Avec l'embedding du cas 1, v = (0,6 ; −0,2 ; 0,3 ; 0,9 ; 0,1) : carrés 0,36, 0,04, 0,09, 0,81 et 0,01 ; somme 1,31 ; racine 1,14455. La seule coordonnée 0,9 porte 0,81 / 1,31 = 61,8 % de la somme des carrés.

## Démonstration 1 — Pythagore, de 2 à d dimensions

**Ce qu'on démontre.** Dans un repère dont les axes sont deux à deux perpendiculaires et gradués avec la même unité, la longueur de la flèche qui va de l'origine au point x = (x₁ ; … ; x_d) vaut

$$
\lVert x \rVert = \sqrt{x_1^2 + x_2^2 + \dots + x_d^2}
$$

**L'idée.** En dimension 2, c'est le théorème de Pythagore. Pour ajouter une dimension, on remarque que la nouvelle coordonnée est perpendiculaire à tout le « plancher » formé par les précédentes : on refait un triangle rectangle, et chaque nouvelle coordonnée ajoute son carré.

**La preuve, pas à pas.** Par récurrence sur la dimension.

**Étape 1.** En dimension 2, la flèche (x₁ ; x₂) est l'hypoténuse du triangle rectangle de côtés |x₁| et |x₂|, parce que les deux axes sont perpendiculaires. Pythagore donne :

$$
\lVert (x_1\ ;\ x_2) \rVert^2 = x_1^2 + x_2^2
$$

**Étape 2.** On suppose la formule vraie en dimension k. En dimension k + 1, on décompose x en deux flèches : b = (x₁ ; … ; xₖ ; 0), dans le plancher des k premiers axes, et h = (0 ; … ; 0 ; xₖ₊₁), le long du dernier axe. h est perpendiculaire à b, parce que le dernier axe est perpendiculaire à chacun des k premiers.

**Étape 3.** b, h et x forment un triangle rectangle d'hypoténuse x ; Pythagore, puis l'hypothèse de récurrence appliquée à b, donnent :

$$
\lVert x \rVert^2 = \lVert b \rVert^2 + x_{k+1}^2 = (x_1^2 + \dots + x_k^2) + x_{k+1}^2
$$

La formule est vraie en dimension k + 1, donc en toute dimension. ∎

**Vérification chiffrée.** Pour (1 ; 2 ; 2), la diagonale du plancher mesure √(1 + 4) = √5, puis la flèche entière √(5 + 4) = √9 = 3, comme la formule directe √(1 + 4 + 4) = 3. Contre-exemple quand les axes ne sont pas perpendiculaires : avec deux vecteurs de base u et v de longueur 1 formant un angle de 60°, le point de coordonnées (1 ; 1) est u + v, de longueur au carré 1 + 1 + 2 cos 60° = 3, et non 1² + 1² = 2.

**Ce que la preuve révèle du mécanisme.** La somme des carrés n'est la longueur que parce que chaque coordonnée est mesurée sur un axe perpendiculaire aux autres : chaque coordonnée apporte sa part, indépendamment des autres.

**Conséquence pour un agent.** Les coordonnées d'un embedding sont traitées comme des axes perpendiculaires et de même unité. Pour des caractéristiques métier (surface, nombre de chambres, montant), ce n'est vrai qu'après les avoir mises sur une même échelle (cas 2 et 3).

## Démonstration 2 — Positivité et homogénéité

**Ce qu'on démontre.** Pour tout vecteur x et tout réel λ :

$$
\lVert x \rVert \ge 0, \qquad \lVert x \rVert = 0 \iff x = 0, \qquad \lVert \lambda x \rVert = \lvert \lambda \rvert \, \lVert x \rVert
$$

**L'idée.** Une somme de carrés n'est jamais négative et ne s'annule que si tout est nul. Multiplier x par λ multiplie chaque carré par λ², et la racine de λ² est |λ|, pas λ.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Chaque xᵢ² ≥ 0, donc la somme est ≥ 0 et sa racine existe et est ≥ 0.

**Étape 2.** Si ‖x‖ = 0, la somme des carrés est nulle ; une somme de nombres positifs ne s'annule que si chacun est nul, donc chaque xᵢ = 0. Réciproquement, le vecteur nul donne 0.

**Étape 3.** La i-ème coordonnée de λx est λxᵢ, de carré λ²xᵢ² ; le facteur λ² sort de la somme, puis la racine d'un produit de nombres positifs est le produit des racines :

$$
\lVert \lambda x \rVert = \sqrt{\sum_i \lambda^2 x_i^2} = \sqrt{\lambda^2} \sqrt{\sum_i x_i^2} = \lvert \lambda \rvert \, \lVert x \rVert
$$

∎

**Vérification chiffrée.** ‖(1,5 ; −2 ; 0,5)‖ = √(2,25 + 4 + 0,25) = √6,5 = 2,54951. Avec λ = −2,5, le vecteur (−3,75 ; 5 ; −1,25) a pour norme √(14,0625 + 25 + 1,5625) = √40,625 = 6,37377 = 2,5 × 2,54951. Contre-exemple de l'oubli de la valeur absolue : écrire ‖−2 × (3 ; 4)‖ = −2 × 5 = −10 donnerait une longueur négative, alors que ‖(−6 ; −8)‖ = √100 = 10.

**Ce que la preuve révèle du mécanisme.** La racine est ce qui rend la norme proportionnelle à l'échelle ; sans elle, doubler un vecteur quadruplerait sa « longueur ». Le signe de λ disparaît : retourner un vecteur ne change pas sa longueur.

**Conséquence pour un agent.** Diviser un vecteur par un nombre positif change sa longueur sans changer sa direction : c'est ce qui rend la normalisation possible (démonstration 4). Une norme nulle signale un vecteur vide, qu'on refuse au lieu de le normaliser.

## Démonstration 3 — L'inégalité triangulaire

**Ce qu'on démontre.** Pour tous vecteurs x et y de même dimension :

$$
\lVert x + y \rVert \le \lVert x \rVert + \lVert y \rVert
$$

avec égalité si et seulement si l'un est un multiple positif de l'autre (ou si l'un est nul).

**L'idée.** On compare les carrés, qui sont plus faciles à développer. Le seul terme différent est le double produit : 2 x · y à gauche, 2 ‖x‖ ‖y‖ à droite, et Cauchy–Schwarz dit que le premier ne dépasse pas le second.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** On développe le carré de la norme par bilinéarité du produit scalaire (fiche 01, démonstration 1) :

$$
\lVert x + y \rVert^2 = \lVert x \rVert^2 + 2\, x \cdot y + \lVert y \rVert^2
$$

**Étape 2.** x · y ≤ |x · y| ≤ ‖x‖ ‖y‖ par Cauchy–Schwarz (fiche 01, démonstration 4), donc :

$$
\lVert x \rVert^2 + 2\, x \cdot y + \lVert y \rVert^2 \le \lVert x \rVert^2 + 2 \lVert x \rVert \lVert y \rVert + \lVert y \rVert^2 = \left(\lVert x \rVert + \lVert y \rVert\right)^2
$$

**Étape 3.** Les deux membres ‖x + y‖ et ‖x‖ + ‖y‖ sont positifs, et la racine carrée est croissante : on peut prendre la racine sans changer le sens. L'égalité exige x · y = ‖x‖ ‖y‖, c'est-à-dire un cosinus égal à 1 : même direction et même sens. ∎

**Vérification chiffrée.** x = (1 ; 0) et y = (0 ; 1) : ‖x + y‖ = √2 = 1,414 ≤ 1 + 1 = 2. Cas d'égalité : x = (3 ; 4) et y = (6 ; 8), x + y = (9 ; 12), ‖x + y‖ = √(81 + 144) = 15 = 5 + 10. Conséquence inverse (exercice 6) : ‖x − y‖ ≥ |‖x‖ − ‖y‖|, par exemple ‖(3 ; 4) − (6 ; 8)‖ = 5 ≥ |5 − 10| = 5.

**Ce que la preuve révèle du mécanisme.** La norme définit une vraie distance : passer par un point intermédiaire ne raccourcit jamais le chemin. Le « manque à gagner » entre ‖x + y‖ et ‖x‖ + ‖y‖ vient entièrement de l'angle entre x et y.

**Conséquence pour un agent.** L'inégalité inverse donne une borne basse gratuite de la distance entre deux vecteurs à partir de leurs distances à un même point de référence : on peut écarter un candidat lointain sans calculer sa distance exacte (cas 3).

## Démonstration 4 — Normaliser donne une longueur 1

**Ce qu'on démontre.** Pour x ≠ 0, le vecteur x̂ = x / ‖x‖ a pour longueur 1 et la même direction que x :

$$
\lVert \hat x \rVert = 1
$$

**L'idée.** Normaliser, c'est multiplier x par le nombre positif 1/‖x‖ ; l'homogénéité dit que la longueur est multipliée par ce même nombre.

**La preuve, pas à pas.** Deux étapes.

**Étape 1.** Comme x ≠ 0, ‖x‖ > 0 (démonstration 2), donc λ = 1/‖x‖ existe et est positif.

**Étape 2.** Par homogénéité, avec |λ| = λ parce que λ > 0 :

$$
\lVert \hat x \rVert = \left\lVert \frac{1}{\lVert x \rVert}\, x \right\rVert = \frac{1}{\lVert x \rVert} \, \lVert x \rVert = 1
$$

La direction ne change pas, parce que λ est positif. ∎

**Vérification chiffrée.** (3 ; 4) / 5 = (0,6 ; 0,8), et 0,36 + 0,64 = 1. Pour l'embedding du cas 1, v̂ = v / 1,14455 = (0,52422 ; −0,17474 ; 0,26211 ; 0,78633 ; 0,08737), de norme 1. Contre-exemple de l'hypothèse x ≠ 0 : (0 ; 0) / 0 n'existe pas, et le code lève `ValueError` au lieu d'ajouter un epsilon qui fabriquerait une direction au hasard.

**Ce que la preuve révèle du mécanisme.** Normaliser sépare un vecteur en deux informations : sa longueur ‖x‖ et sa direction x̂. Après normalisation, seule la direction reste.

**Conséquence pour un agent.** On normalise tout l'index une seule fois, à l'écriture : le produit scalaire de deux vecteurs normalisés est alors leur cosinus, sans racine ni division à chaque requête.

## Démonstration 5 — Distance entre deux vecteurs normalisés

**Ce qu'on démontre.** Pour x et y non nuls :

$$
\lVert \hat x - \hat y \rVert^2 = 2 - 2 \cos(x, y)
$$

d'où, pour un seuil de distance τ ∈ [0, 2] :

$$
\lVert \hat x - \hat y \rVert \le \tau \iff \cos(x, y) \ge 1 - \frac{\tau^2}{2}
$$

**L'idée.** On développe le carré de la distance ; les deux carrés valent 1 après normalisation, et le double produit est le cosinus.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** Par bilinéarité :

$$
\lVert \hat x - \hat y \rVert^2 = \lVert \hat x \rVert^2 - 2\, \hat x \cdot \hat y + \lVert \hat y \rVert^2
$$

**Étape 2.** ‖x̂‖ = ‖ŷ‖ = 1 (démonstration 4), et x̂ · ŷ = (x · y)/(‖x‖ ‖y‖) = cos(x, y), parce que les facteurs 1/‖x‖ et 1/‖y‖ sortent du produit scalaire. Donc le carré vaut 1 − 2 cos(x, y) + 1 = 2 − 2 cos(x, y).

**Étape 3.** Les deux membres de ‖x̂ − ŷ‖ ≤ τ sont positifs : on peut élever au carré sans changer le sens, ce qui donne 2 − 2 cos ≤ τ², puis cos ≥ 1 − τ²/2. ∎

**Vérification chiffrée.** Pour un cosinus de 0,8 : √(2 − 1,6) = √0,4 = 0,63246 ; inversement, 1 − 0,63246²/2 = 1 − 0,2 = 0,8. Pour 0,95 : √0,1 = 0,31623. Contre-exemple sans normalisation, repris de la leçon : (3 ; 0) et (0,6 ; 0,8) ont un cosinus de 1,8 / (3 × 1) = 0,6, donc 2 − 2 × 0,6 = 0,80, alors que ‖(3 ; 0) − (0,6 ; 0,8)‖² = 2,4² + 0,8² = 5,76 + 0,64 = 6,40.

**Ce que la preuve révèle du mécanisme.** Sur des vecteurs normalisés, la distance ne dépend que du cosinus, et c ↦ √(2 − 2c) est strictement décroissante : classer par distance croissante ou par cosinus décroissant donne le même ordre.

**Conséquence pour un agent.** Une base vectorielle réglée en distance L2 peut appliquer exactement un seuil métier exprimé en cosinus, à condition d'avoir normalisé et de convertir le seuil par τ = √(2 − 2c) (cas 1).

## Démonstration 6 — La plus grande coordonnée encadre la norme

**Ce qu'on démontre.** Pour tout vecteur x de dimension d :

$$
\max_i \lvert x_i \rvert \le \lVert x \rVert \le \sqrt{d} \, \max_i \lvert x_i \rvert
$$

**L'idée.** La somme des carrés contient au moins le plus grand carré, et au plus d fois ce plus grand carré.

**La preuve, pas à pas.** Trois étapes.

**Étape 1.** On note k l'indice de la plus grande |xᵢ|. Tous les termes de la somme sont ≥ 0, donc la somme est au moins égale à son terme xₖ² :

$$
\lVert x \rVert^2 = \sum_i x_i^2 \ge x_k^2
$$

**Étape 2.** Chaque xᵢ² ≤ xₖ², parce que |xᵢ| ≤ |xₖ| ; on additionne les d inégalités :

$$
\lVert x \rVert^2 \le d \, x_k^2
$$

**Étape 3.** La racine est croissante : on la prend dans les deux inégalités, avec √(xₖ²) = |xₖ|. ∎

**Vérification chiffrée.** Pour les écarts de cotation du cas 4, e = (12 ; −8 ; 15 ; −40 ; 5) : max |eᵢ| = 40 ≤ ‖e‖ = √2 058 = 45,36518 ≤ √5 × 40 = 89,44272. Cas d'égalité à gauche : (0 ; 7 ; 0) a pour norme 7 ; à droite : (1 ; 1 ; 1 ; 1) a pour norme 2 = √4 × 1.

**Ce que la preuve révèle du mécanisme.** Quand une coordonnée est nettement plus grande que les autres, la norme est proche de cette coordonnée : dans e, le seul −40 porte 1 600 / 2 058 = 77,7 % de la somme des carrés. La norme agrège, mais elle est dominée par les grandes valeurs.

**Conséquence pour un agent.** Avant de calculer une distance sur des caractéristiques brutes, on les standardise : sinon la caractéristique aux plus grands nombres (une surface en sqft face à un nombre de chambres) devient le maximum et décide seule de la distance (cas 3).

## Exemple simple, à la main

$$
\lVert (3\ ;\ 4) \rVert = \sqrt{9 + 16} = \sqrt{25} = 5, \qquad \lVert (1\ ;\ 2\ ;\ 2) \rVert = \sqrt{1 + 4 + 4} = \sqrt{9} = 3
$$

On normalise (3 ; 4) en divisant chaque coordonnée par 5 : 3 / 5 = 0,6 et 4 / 5 = 0,8. On vérifie la longueur :

$$
\lVert (0{,}6\ ;\ 0{,}8) \rVert = \sqrt{0{,}36 + 0{,}64} = \sqrt{1} = 1
$$

La distance entre (1 ; 2 ; 3) et (4 ; 6 ; 3) est la norme de leur différence (3 ; 4 ; 0) : √(9 + 16 + 0) = 5.

## Cas d'usage complexes, démontrés

### Cas 1 — Cabinet RH multi-émirats : normaliser un index de CV et régler le seuil

**Contexte.** Un cabinet RH présent dans plusieurs émirats vectorise 250 000 CV et les fiches de poste de ses clients pour proposer des candidats. Sa base vectorielle mesure la distance L2, alors que l'équipe métier a fixé son seuil en cosinus : un CV est proposé si son cosinus avec la fiche de poste atteint 0,8. Les vecteurs sortent du modèle d'embedding sans être normalisés. La question : faut-il normaliser, quel seuil de distance configurer, et combien de mémoire prévoir ? Volumes et vecteurs (réduits à 5 dimensions) sont illustratifs.

**Données.**

| Donnée | Valeur |
| --- | --- |
| CV indexés | 250 000 |
| Dimension | 1 536, en float32 (4 octets par coordonnée) |
| Seuil métier | cos ≥ 0,8 |
| Exemple de CV brut v | 0,6 ; −0,2 ; 0,3 ; 0,9 ; 0,1 |
| Fiche de poste du contre-calcul | norme 0,9, cosinus 0,8 avec v |

**Calcul pas à pas.** Arrondis à 5 décimales.

**Étape 1.** Norme du CV :

$$
\lVert v \rVert = \sqrt{0{,}36 + 0{,}04 + 0{,}09 + 0{,}81 + 0{,}01} = \sqrt{1{,}31} = 1{,}14455
$$

**Étape 2.** Normalisation, coordonnée par coordonnée (0,6 / 1,14455, etc.) :

$$
\hat v = (0{,}52422\ ;\ -0{,}17474\ ;\ 0{,}26211\ ;\ 0{,}78633\ ;\ 0{,}08737), \qquad \lVert \hat v \rVert = 1
$$

**Étape 3.** Seuil de distance équivalent au cosinus 0,8 (démonstration 5) :

$$
\tau = \sqrt{2 - 2 \times 0{,}8} = \sqrt{0{,}4} = 0{,}63246
$$

**Étape 4.** Mémoire et coût. Un CV occupe 1 536 × 4 = 6 144 octets, l'index 250 000 × 6 144 = 1 536 000 000 octets, soit 1,536 Go. Sans normalisation ni norme stockée, chaque comparaison coûte 2 × 1 536 = 3 072 multiplications (le produit scalaire et la norme du CV), soit 768 000 000 par requête ; normalisé, 1 536 par CV, soit 384 000 000. La normalisation de l'index coûte une fois 250 000 × 3 072 = 768 000 000 opérations.

**Décision de l'agent.** On normalise les 250 000 CV à l'indexation et l'on configure la base avec le seuil de distance 0,63246, strictement équivalent au cosinus 0,8. Le coût de normalisation est remboursé dès la deuxième requête, et chaque requête coûte ensuite deux fois moins.

**Contre-calcul.** Sans normalisation, la base compare des vecteurs bruts. Pour v (norme 1,14455) et une fiche de norme 0,9 avec un cosinus de 0,8, la distance vaut :

$$
\sqrt{1{,}31 + 0{,}81 - 2 \times 0{,}8 \times 1{,}14455 \times 0{,}9} = \sqrt{2{,}12 - 1{,}64816} = \sqrt{0{,}47184} = 0{,}68691 > 0{,}63246
$$

Le CV est écarté alors qu'il atteint exactement le seuil métier : la longueur des vecteurs, qui ne dit rien de l'adéquation au poste, élimine des candidats valables.

**Sensibilité.** Le seuil de cosinus équivalent est c = 1 − τ²/2. Desserrer la distance de 10 %, τ = 0,63246 × 1,1 = 0,69570, abaisse le cosinus exigé de 0,8 à 1 − 0,69570²/2 = 0,758 : une variation de 10 % sur τ déplace le seuil de 0,042 en cosinus, assez pour changer nettement le nombre de candidats proposés.

**En production.** On suit chaque nuit le plus grand écart |‖v‖ − 1| sur l'index (alerte au-dessus de 10⁻³ : une partie de l'index a été écrite sans normalisation) et le nombre de CV proposés par offre. Les CV sont des données personnelles : la PDPL (décret-loi fédéral 45/2021) s'applique hors des zones franches financières DIFC et ADGM, qui ont leurs propres lois ; les durées de conservation sont à confirmer avec le texte en vigueur.

### Cas 2 — Assureur auto : la norme d'un sinistre standardisé comme score d'anomalie

**Contexte.** Un assureur auto et santé repère les déclarations atypiques avant de les payer. Pour chaque sinistre, l'agent standardise quatre caractéristiques par rapport aux sinistres habituels, puis calcule la norme du vecteur obtenu, c'est-à-dire sa distance au « sinistre moyen ». Au-delà de 3 écarts-types de distance, le dossier part en revue humaine. Un assuré de Sharjah déclare un sinistre de 18 500 AED. Moyennes, écarts-types et seuil sont illustratifs.

**Données.**

| Caractéristique | Valeur du dossier A | Moyenne μᵢ | Écart-type σᵢ |
| --- | --- | --- | --- |
| Montant du devis (AED) | 18 500 | 9 000 | 4 000 |
| Délai de déclaration (jours) | 1 | 6 | 4 |
| Pièces remplacées | 9 | 4 | 2 |
| Âge du véhicule (ans) | 2 | 5 | 3 |

Seuil de revue : ‖z‖ ≥ 3. Dossier B du contre-calcul : 9 500 AED, déclaré le jour même (0 jour), 15 pièces, véhicule de 1 an.

**Calcul pas à pas.** Arrondis à 5 décimales.

**Étape 1.** Standardisation, zᵢ = (vᵢ − μᵢ) / σᵢ :

$$
z = \left(\frac{18\,500 - 9\,000}{4\,000}\ ;\ \frac{1 - 6}{4}\ ;\ \frac{9 - 4}{2}\ ;\ \frac{2 - 5}{3}\right) = (2{,}375\ ;\ -1{,}25\ ;\ 2{,}5\ ;\ -1)
$$

**Étape 2.** Carrés et somme :

$$
5{,}640625 + 1{,}5625 + 6{,}25 + 1 = 14{,}453125
$$

**Étape 3.** Norme :

$$
\lVert z \rVert = \sqrt{14{,}453125} = 3{,}80173 \ge 3
$$

**Décision de l'agent.** Le dossier A part en revue humaine. Aucune caractéristique seule n'atteint 3 écarts-types (la plus grande vaut 2,5), mais leur combinaison est atypique : c'est ce que la norme mesure, et la démonstration 6 l'encadre entre 2,5 et √4 × 2,5 = 5.

**Contre-calcul.** Sans standardisation, la distance du dossier B à la moyenne brute serait ‖(500 ; −6 ; 11 ; −4)‖ = √250 173 = 500,17, presque égale à l'écart de montant (500 AED) : les jours, les pièces et l'âge, exprimés en petits nombres, n'y comptent pour rien (démonstration 6). Or B a 15 pièces remplacées pour un devis normal ; standardisé, z = (0,125 ; −1,5 ; 5,5 ; −1,33333) et ‖z‖ = √34,29340 = 5,85606, très au-dessus du seuil. Une règle « un seul critère à plus de 3 écarts-types » aurait, à l'inverse, laissé passer le dossier A.

**Sensibilité.** Valeur de bascule du montant pour A, les trois autres caractéristiques fixées : il faut z₁² + 8,8125 ≥ 9, donc z₁ ≥ √0,1875 = 0,43301, soit un devis de 9 000 + 0,43301 × 4 000 = 10 732 AED. Au-dessus de 10 732 AED, ce profil part en revue. Un devis plus élevé de 10 % (20 350 AED) donne z₁ = 2,8375 et ‖z‖ = 4,10657.

**En production.** On suit la part de dossiers envoyés en revue et l'on recalcule chaque mois les moyennes et écarts-types, parce qu'une inflation des prix des pièces décalerait tous les z. L'assurance est supervisée par la CBUAE ; la documentation de la règle de revue est à confirmer avec le texte en vigueur.

### Cas 3 — Agence immobilière à Dubaï : trouver les comparables d'un appartement

**Contexte.** Une agence de Dubaï estime un appartement de 1 250 sqft, 3 chambres, au 10ᵉ étage, à partir de biens comparables vendus. Chaque bien est décrit par trois caractéristiques standardisées ; un bien est un comparable si sa distance au bien estimé est au plus r = 0,8. Pour ne pas calculer les 15 000 distances à chaque estimation, l'agent garde pour chaque bien sa norme, c'est-à-dire sa distance au bien moyen (le point de référence), et utilise l'inégalité triangulaire inverse pour écarter d'office les biens trop lointains. Les moyennes, écarts-types, prix et volumes sont illustratifs.

**Données.**

| Bien | Surface (sqft) | Chambres | Étage | Prix (AED/sqft) |
| --- | --- | --- | --- | --- |
| q, à estimer | 1 250 | 3 | 10 | ? |
| a₁, villa | 4 000 | 5 | 0 | — |
| a₂ | 1 370 | 3 | 14 | 1 750 |
| a₃ | 1 250 | 1 | 40 | 2 400 |

Standardisation : surface (μ = 1 100, σ = 300), chambres (μ = 2, σ = 1), étage (μ = 15, σ = 10). Rayon r = 0,8. Base de 15 000 biens, dont 70 % ont une norme éloignée de plus de 0,8 de celle de q. Frais de transfert du DLD : 4 % de la valeur.

**Calcul pas à pas.** Arrondis à 5 décimales.

**Étape 1.** Standardisation :

$$
q = (0{,}5\ ;\ 1\ ;\ -0{,}5), \quad a_1 = (9{,}66667\ ;\ 3\ ;\ -1{,}5), \quad a_2 = (0{,}9\ ;\ 1\ ;\ -0{,}1), \quad a_3 = (0{,}5\ ;\ -1\ ;\ 2{,}5)
$$

**Étape 2.** Normes (distances au bien moyen) :

$$
\lVert q \rVert = \sqrt{1{,}5} = 1{,}22474, \qquad \lVert a_1 \rVert = \sqrt{104{,}69444} = 10{,}23203, \qquad \lVert a_2 \rVert = \sqrt{1{,}82} = 1{,}34907
$$

**Étape 3.** Bornes basses par l'inégalité triangulaire inverse (démonstration 3, exercice 6), ‖q − a‖ ≥ |‖q‖ − ‖a‖| :

$$
\lVert q - a_1 \rVert \ge 10{,}23203 - 1{,}22474 = 9{,}00729 > 0{,}8, \qquad \lVert q - a_2 \rVert \ge 1{,}34907 - 1{,}22474 = 0{,}12433
$$

a₁ est écarté sans calcul ; pour a₂, la borne ne permet pas de conclure.

**Étape 4.** Distance exacte pour a₂ :

$$
\lVert q - a_2 \rVert = \lVert (-0{,}4\ ;\ 0\ ;\ -0{,}4) \rVert = \sqrt{0{,}32} = 0{,}56569 \le 0{,}8
$$

**Décision de l'agent.** a₂ est un comparable, a₁ ne l'est pas, et sur toute la base l'agent ne calcule que 15 000 × 0,3 = 4 500 distances exactes au lieu de 15 000. Avec le prix de a₂, l'estimation vaut 1 250 × 1 750 = 2 187 500 AED.

**Contre-calcul.** Sans standardisation, la surface en sqft domine (démonstration 6) : la distance brute de q à a₂ vaut ‖(−120 ; 0 ; −4)‖ = 120,07 et celle de q à a₃ ‖(0 ; 2 ; 30)‖ = 30,07, si bien que a₃, un bien d'une chambre au 40ᵉ étage, passe pour le plus proche. Standardisé, a₃ est à √(0 + 4 + 9) = 3,60555, très loin. Une estimation fondée sur a₃ donnerait 1 250 × 2 400 = 3 000 000 AED au lieu de 2 187 500, soit 812 500 AED d'écart, et une erreur de 4 % × 812 500 = 32 500 AED sur les frais de transfert du DLD annoncés à l'acheteur.

**Sensibilité.** a₂ reste un comparable tant que 0,4² + Δ² ≤ 0,8², où Δ est l'écart d'étage standardisé, donc Δ ≤ √0,48 = 0,69282, soit au plus 6,93 étages d'écart avec q : a₂ resterait un comparable jusqu'au 16ᵉ étage, et ne le serait plus au 17ᵉ.

**En production.** On suit la part des estimations dont le prix de vente final tombe dans la fourchette annoncée, et le nombre de comparables trouvés (une estimation avec moins de cinq comparables part chez un conseiller). Les frais de transfert du DLD sont de 4 % à Dubaï ; les règles de publicité de la RERA sont à confirmer avec le texte en vigueur.

### Cas 4 — Plateforme d'actifs virtuels agréée VARA : une source de cotation qui dérive

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA compare chaque minute le prix d'un actif sur cinq sources de cotation à son prix de référence interne. L'agent de surveillance forme le vecteur des écarts en points de base (1 point de base = 0,01 %) et calcule leur écart quadratique moyen, ‖e‖ / √5. Une alerte globale part au-delà de 25 points de base. La question : y a-t-il une alerte, et une source est-elle en cause ? Écarts, seuil et montant d'ordre sont illustratifs.

**Données.**

| Source | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Écart eᵢ (points de base) | 12 | −8 | 15 | −40 | 5 |

Seuil d'alerte globale : 25 points de base d'écart quadratique moyen. Ordre type exécuté sur la référence : 2 000 000 USD, à 3,6725 AED par USD.

**Calcul pas à pas.** Arrondis à 5 décimales.

**Étape 1.** Somme des carrés et norme :

$$
144 + 64 + 225 + 1\,600 + 25 = 2\,058, \qquad \lVert e \rVert = \sqrt{2\,058} = 45{,}36518
$$

**Étape 2.** Écart quadratique moyen :

$$
\frac{45{,}36518}{\sqrt{5}} = 20{,}28793 < 25
$$

**Étape 3.** Part de la source 4 dans la somme des carrés : 1 600 / 2 058 = 77,7 %.

**Étape 4.** Sans la source 4 :

$$
\lVert (12\ ;\ -8\ ;\ 15\ ;\ 5) \rVert = \sqrt{458} = 21{,}40093, \qquad \frac{21{,}40093}{\sqrt{4}} = 10{,}70047
$$

**Décision de l'agent.** Pas d'alerte globale (20,29 < 25), mais la source 4 porte 77,7 % de l'écart : l'agent la marque comme aberrante, l'exclut du calcul du prix de référence et ouvre un ticket ; les quatre autres sources restent à 10,7 points de base, ce qui est normal.

**Contre-calcul.** La moyenne signée des écarts, (12 − 8 + 15 − 40 + 5) / 5 = −3,2 points de base, dit que tout va bien : les écarts de signes opposés se compensent. La norme ne le permet pas, parce que les carrés effacent les signes. Si l'on exécutait un ordre de 2 000 000 USD au prix de la source 4, l'écart de 0,40 % coûterait 0,004 × 2 000 000 = 8 000 USD, soit 8 000 × 3,6725 = 29 380 AED.

**Sensibilité.** Valeur de bascule de l'alerte globale, les quatre autres sources fixées : il faut ‖e‖ ≥ 25 × √5 = 55,90170, donc e₄² ≥ 3 125 − 458 = 2 667 et |e₄| ≥ √2 667 = 51,64301 points de base. Une source peut donc dériver jusqu'à 51 points de base sans déclencher l'alerte globale : c'est pourquoi l'agent surveille aussi la part de chaque source, et pas seulement la norme.

**En production.** On suit l'écart quadratique moyen chaque minute (alerte à 25 points de base) et la part de la plus grande source (alerte au-dessus de 50 %). Les obligations de la plateforme sur la qualité des prix et la journalisation des incidents relèvent de la VARA, à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer ‖(2 ; −3 ; 6)‖.

**Exercice 2.** Normaliser (1 ; 1 ; 1 ; 1).

**Exercice 3.** Vérifier l'inégalité triangulaire avec x = (1 ; 0) et y = (0 ; 1).

**Exercice 4.** Calculer la distance entre (1 ; 2 ; 3) et (4 ; 6 ; 3).

**Exercice 5.** Deux vecteurs normalisés ont un cosinus de 0,95. Quelle est leur distance ?

**Exercice 6.** Démontrer que ‖x − y‖ ≥ ‖x‖ − ‖y‖. (Indice : écrire x = (x − y) + y.)

**Exercice 7.** Dans le cas 2, l'expert corrige le nombre de pièces remplacées du dossier A : 5 au lieu de 9. Recalculer ‖z‖ et donner la nouvelle décision.

**Exercice 8.** Trouver l'erreur. Un collègue « normalise » (3 ; 4) en divisant par la somme de ses coordonnées : (3/7 ; 4/7). Calculer la norme du résultat et corriger.

**Exercice 9.** Redémontrer de mémoire l'encadrement max |xᵢ| ≤ ‖x‖ ≤ √d max |xᵢ| (démonstration 6), puis le vérifier sur e = (12 ; −8 ; 15 ; −40 ; 5).

## Corrigé

**Exercice 1.** Carrés : 4, 9, 36 ; somme 49 ; racine √49 = 7.

**Exercice 2.** La norme vaut √(1 + 1 + 1 + 1) = √4 = 2 ; on divise chaque coordonnée par 2 : x̂ = (0,5 ; 0,5 ; 0,5 ; 0,5). Contrôle : 4 × 0,25 = 1.

**Exercice 3.** x + y = (1 ; 1) et ‖x + y‖ = √2 ≈ 1,414 ; ‖x‖ + ‖y‖ = 1 + 1 = 2 ; on a bien 1,414 ≤ 2. L'inégalité est stricte parce que x et y sont perpendiculaires, pas alignés.

**Exercice 4.** Différence : (4 − 1 ; 6 − 2 ; 3 − 3) = (3 ; 4 ; 0) ; norme √(9 + 16 + 0) = 5.

**Exercice 5.** Par la démonstration 5 : √(2 − 2 × 0,95) = √(2 − 1,9) = √0,1 ≈ 0,31623.

**Exercice 6.** Étape 1 : x = (x − y) + y. Étape 2 : l'inégalité triangulaire donne ‖x‖ ≤ ‖x − y‖ + ‖y‖. Étape 3 : on retranche ‖y‖ : ‖x − y‖ ≥ ‖x‖ − ‖y‖. En échangeant x et y, ‖x − y‖ ≥ ‖y‖ − ‖x‖, d'où ‖x − y‖ ≥ |‖x‖ − ‖y‖|, la borne utilisée au cas 3.

**Exercice 7.** La troisième coordonnée devient (5 − 4) / 2 = 0,5, de carré 0,25. Somme des carrés : 5,640625 + 1,5625 + 0,25 + 1 = 8,453125 ; norme √8,453125 = 2,90743 < 3. La décision change : le dossier n'est plus atypique et suit le circuit normal.

**Exercice 8.** (3/7 ; 4/7) a pour norme √(9/49 + 16/49) = √(25/49) = 5/7 ≈ 0,71429, pas 1 : diviser par la somme des coordonnées (la norme L1 pour des coordonnées positives) ne donne pas un vecteur de longueur euclidienne 1. Il faut diviser par la norme L2, 5 : (0,6 ; 0,8).

**Exercice 9.** Étape 1 : la somme des carrés contient le plus grand carré, et ses autres termes sont ≥ 0, donc ‖x‖² ≥ max xᵢ². Étape 2 : chaque carré est ≤ le plus grand, donc ‖x‖² ≤ d × max xᵢ². Étape 3 : on prend la racine, croissante. Vérification : 40 ≤ √2 058 = 45,36518 ≤ √5 × 40 = 89,44272.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`norme(x)`** — Cette fonction est l'arpenteur qui mesure la longueur d'une flèche tracée dans un espace à autant de directions qu'on veut : elle reçoit un vecteur, élève chacune de ses coordonnées au carré, additionne ces carrés puis renvoie la racine carrée de la somme, ‖x‖ = √(x₁² + x₂² + …), c'est-à-dire le théorème de Pythagore répété dimension après dimension. Elle renvoie 5 pour (3, 4), 3 pour (1, 2, 2) et 1,14455 pour le CV v du cas 1, et toutes les autres fonctions du programme s'appuient sur elle, qu'il s'agisse de normaliser, de mesurer une distance ou de transformer un sinistre standardisé en score d'anomalie.

**`normaliser(x)`** — Celle-ci ramène toute flèche à la longueur 1 sans toucher à sa direction, comme un cartographe qui ne garde de chaque trajet que le cap à suivre : elle reçoit un vecteur, calcule sa norme avec `norme`, refuse le vecteur nul par une `ValueError` « vecteur nul : pas de direction », puisqu'on ne peut pas diviser par 0, et renvoie sinon le tuple de chaque coordonnée divisée par cette norme. Elle transforme (3, 4) en (0.6, 0.8) et le CV du cas 1 en un vecteur dont la première coordonnée vaut 0,52422, et c'est elle qui permet de régler un seuil de distance strictement équivalent à un seuil de cosinus.

**`distance(x, y)`** — Cette fonction joue le rôle du géomètre qui tend un cordeau entre deux bornes et lit la longueur du segment : elle reçoit deux vecteurs, vérifie qu'ils ont le même nombre de coordonnées et lève sinon une `ValueError` « dimensions différentes », puis forme le vecteur des différences coordonnée par coordonnée et renvoie sa norme, ‖x − y‖. Elle donne 5 entre (1, 2, 3) et (4, 6, 3), 0,56569 entre l'appartement à estimer et le comparable a2 une fois standardisés, et c'est elle que le cas 3 appelle seulement pour les biens que l'inégalité triangulaire n'a pas déjà écartés.

**`standardiser(valeurs, moyennes, ecarts)`** — Ici l'on suit un traducteur qui convertit des mesures dans des unités incompatibles, des dirhams, des jours, des pièces ou des étages, en une seule langue commune, celle des écarts-types : la fonction reçoit les valeurs d'un dossier, les moyennes et les écarts-types de référence, lève une `ValueError` « écart-type nul ou négatif » si l'un des écarts n'est pas strictement positif, puis renvoie le tuple des zᵢ = (vᵢ − μᵢ) / σᵢ. Le sinistre A du cas 2 devient ainsi (2.375, -1.25, 2.5, -1.0) et l'appartement q du cas 3 (0.5, 1.0, -0.5), si bien qu'aucune grandeur ne peut plus écraser les autres par la seule taille de ses nombres.

**`cas_1_index_cv_rh()`** — Cette fonction raconte le cabinet RH qui range 250 000 CV en dimension 1 536 dans une base qui mesure des distances alors que le métier raisonne en cosinus, avec un seuil de 0,8 : elle calcule la norme 1,14455 d'un CV réduit à cinq coordonnées, sa version normalisée, puis le seuil de distance équivalent τ = √(2 − 2 × 0,8) = 0,63246. Elle chiffre la mémoire de l'index, 1 536 000 000 octets, et le coût d'une requête, 768 000 000 multiplications sans normalisation contre 384 000 000 avec, montre qu'un CV brut au cosinus exact de 0,8 avec une fiche de norme 0,9 se retrouve à la distance 0,68691, donc écarté à tort, et calcule enfin qu'un τ desserré de 10 % abaisse le cosinus exigé à 0,758, avant de renvoyer ces valeurs dans un dictionnaire.

**`cas_2_anomalie_sinistre_assurance()`** — On y voit l'agent d'un assureur auto qui mesure à quel point un sinistre s'éloigne du « sinistre moyen » : il standardise le dossier A, de 18 500 AED, en (2.375, -1.25, 2.5, -1.0), dont les carrés font 14,453125 et la norme 3,80173, ce qui dépasse le seuil de 3 et envoie le dossier en « revue », bien qu'aucun critère isolé n'atteigne 3. La fonction traite aussi le dossier B, dont la distance brute de 500,17 ne voit que le montant alors que sa version standardisée atteint 5,85606, calcule le montant de bascule de 10 732 AED à partir du reste 8,8125, puis la norme 4,10657 d'un devis majoré de 10 %, et renvoie le tout dans un dictionnaire.

**`cas_3_comparables_immobilier()`** — Cette fonction met en scène l'estimateur d'une agence immobilière qui cherche les comparables d'un appartement de 1 250 sqft sans calculer toutes les distances : elle standardise le bien q et les biens a1, a2 et a3, calcule leurs normes, puis les bornes basses |‖a‖ − ‖q‖| de l'inégalité triangulaire inverse, qui valent 9,00729 pour la villa a1, aussitôt écartée car au-delà du rayon 0,8, et 0,12433 pour a2, qui exige un calcul exact. Elle trouve d(q, a2) = 0,56569, retient a2 comme comparable, estime le bien à 2 187 500 AED, compte 4 500 distances au lieu de 15 000, montre qu'en unités brutes a3 paraîtrait plus proche que a2, et calcule l'étage maximal 16,93 au-delà duquel a2 cesserait d'être comparable.

**`cas_4_ecarts_cotation_crypto()`** — Ici l'on suit le surveillant d'une plateforme d'actifs virtuels qui compare chaque minute cinq sources de cotation à son prix de référence, avec les écarts (12, -8, 15, -40, 5) en points de base : la fonction calcule la somme des carrés 2 058, la norme 45,36518 et l'écart quadratique moyen 20,28793, sous le seuil global de 25, mais découvre que la quatrième source porte à elle seule 0,777 de la somme des carrés et conclut « source 4 aberrante ». Elle recalcule les indicateurs sans cette source, montre que la moyenne signée de −3,2 masquerait tout, chiffre la perte de 8 000 USD, soit 29 380 AED, sur un ordre de 2 000 000 USD, et trouve l'écart de bascule de 51,64301 points de base, avant de renvoyer ces valeurs.

**`main()`** — C'est le correcteur méticuleux qui reprend la fiche ligne à ligne, chaque résultat validé par un `assert` : il refait le mécanisme et l'exemple simple, avec la part 0,618 du carré de 0,9 dans la somme, puis Pythagore avec ses axes obliques, l'homogénéité avec λ = −2,5, l'inégalité triangulaire et sa forme inverse, la normalisation et le refus du vecteur nul, le lien entre distance et cosinus et l'encadrement 40 ≤ 45,36518 ≤ 89,44272. Il appelle ensuite les quatre cas et confronte chacune de leurs valeurs aux nombres du texte, rejoue les exercices du corrigé, dont le dossier de l'exercice 7 qui retombe à 2,90743 et la fausse normalisation (3/7, 4/7) de norme 0,71429, et n'annonce « OK — toutes les vérifications sont passées. » qu'à la toute fin.

```python
"""Démonstration 02 — norme L2 : Pythagore, homogénéité, triangle, normalisation, distance, encadrement, quatre cas aux EAU."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def norme(x) -> float:
    """‖x‖ = √(x₁² + … + x_d²)."""
    return math.sqrt(sum(a * a for a in x))


def normaliser(x) -> tuple:
    """x̂ = x / ‖x‖ ; le vecteur nul n'a pas de direction."""
    n = norme(x)
    if n == 0:
        raise ValueError("vecteur nul : pas de direction")
    return tuple(a / n for a in x)


def distance(x, y) -> float:
    """‖x − y‖, distance euclidienne ; refuse deux dimensions différentes."""
    if len(x) != len(y):
        raise ValueError("dimensions différentes")
    return norme(tuple(a - b for a, b in zip(x, y)))


def standardiser(valeurs, moyennes, ecarts) -> tuple:
    """zᵢ = (vᵢ − μᵢ) / σᵢ, chaque σᵢ strictement positif."""
    if any(s <= 0 for s in ecarts):
        raise ValueError("écart-type nul ou négatif")
    return tuple((v - m) / s for v, m, s in zip(valeurs, moyennes, ecarts))


def cas_1_index_cv_rh() -> dict:
    """[RH] 250 000 CV en dimension 1536 : normaliser, seuil de distance équivalent à cos 0.8, mémoire, coût."""
    v = (0.6, -0.2, 0.3, 0.9, 0.1)
    n_cv, dim, octets, cos_seuil = 250_000, 1536, 4, 0.8
    nv = norme(v)
    vh = normaliser(v)
    tau = math.sqrt(2 - 2 * cos_seuil)
    memoire = n_cv * dim * octets
    brut, normalise = n_cv * 2 * dim, n_cv * dim
    norme_fiche = 0.9
    d_brute = math.sqrt(nv ** 2 + norme_fiche ** 2 - 2 * cos_seuil * nv * norme_fiche)
    tau_10 = tau * 1.1
    cos_10 = 1 - tau_10 ** 2 / 2
    decision = "normaliser, seuil de distance %.5f" % tau
    print(f"Cas 1 RH : ‖v‖ = {nv:.5f} ; v̂ = ({' ; '.join(format(a, '.5f') for a in vh)}) ; τ = {tau:.5f}")
    print(f"  mémoire {memoire:,} octets ; {brut:,} -> {normalise:,} multiplications/requête")
    print(f"  distance brute {d_brute:.5f} > τ ; τ+10 % = {tau_10:.5f} -> cos {cos_10:.3f}")
    return {"nv": nv, "vh": vh, "tau": tau, "memoire": memoire, "brut": brut, "normalise": normalise,
            "d_brute": d_brute, "tau_10": tau_10, "cos_10": cos_10, "decision": decision}


def cas_2_anomalie_sinistre_assurance() -> dict:
    """[ASSUR] norme d'un sinistre standardisé, seuil 3, contre-calcul sans standardisation."""
    moyennes, ecarts, seuil = (9000, 6, 4, 5), (4000, 4, 2, 3), 3.0
    za = standardiser((18_500, 1, 9, 2), moyennes, ecarts)
    zb = standardiser((9_500, 0, 15, 1), moyennes, ecarts)
    brut_b = tuple(v - m for v, m in zip((9_500, 0, 15, 1), moyennes))
    na, nb = norme(za), norme(zb)
    decision = "revue" if na >= seuil else "circuit normal"
    reste = sum(z * z for z in za[1:])
    z1_bascule = math.sqrt(seuil ** 2 - reste)
    montant_bascule = moyennes[0] + z1_bascule * ecarts[0]
    za_10 = standardiser((18_500 * 1.1, 1, 9, 2), moyennes, ecarts)
    print(f"Cas 2 ASSUR : z = {za} ; Σz² = {sum(z * z for z in za)} ; ‖z‖ = {na:.5f} -> {decision}")
    print(f"  B brut {norme(brut_b):.2f}, B standardisé {nb:.5f} ; bascule montant {montant_bascule:.0f} AED ;"
          f" devis +10 % -> {norme(za_10):.5f}")
    return {"za": za, "zb": zb, "na": na, "nb": nb, "brut_b": norme(brut_b), "decision": decision,
            "reste": reste, "z1": z1_bascule, "montant": montant_bascule, "n10": norme(za_10), "z10": za_10}


def cas_3_comparables_immobilier() -> dict:
    """[IMMO] comparables à Dubaï : standardisation, élagage par l'inégalité triangulaire inverse."""
    moyennes, ecarts, rayon = (1100, 2, 15), (300, 1, 10), 0.8
    biens = {"q": (1250, 3, 10), "a1": (4000, 5, 0), "a2": (1370, 3, 14), "a3": (1250, 1, 40)}
    z = {k: standardiser(v, moyennes, ecarts) for k, v in biens.items()}
    normes = {k: norme(v) for k, v in z.items()}
    bornes = {k: abs(normes[k] - normes["q"]) for k in ("a1", "a2")}
    ecartes = [k for k, b in bornes.items() if b > rayon]
    d_a2 = distance(z["q"], z["a2"])
    comparables = [k for k in ("a2",) if k not in ecartes and distance(z["q"], z[k]) <= rayon]
    calculs = round(15_000 * 0.3)
    brute_a2 = distance(biens["q"], biens["a2"])
    brute_a3 = distance(biens["q"], biens["a3"])
    d_a3 = distance(z["q"], z["a3"])
    estimation, mauvaise = 1250 * 1750, 1250 * 2400
    delta_max = math.sqrt(rayon ** 2 - 0.4 ** 2)
    etage_max = 10 + 10 * delta_max
    print(f"Cas 3 IMMO : ‖q‖ = {normes['q']:.5f}, ‖a1‖ = {normes['a1']:.5f}, ‖a2‖ = {normes['a2']:.5f}")
    print(f"  bornes a1 {bornes['a1']:.5f}, a2 {bornes['a2']:.5f} ; d(q, a2) = {d_a2:.5f} -> comparables {comparables}")
    print(f"  {calculs} distances au lieu de 15000 ; estimation {estimation} AED")
    print(f"  brut a2 {brute_a2:.2f}, a3 {brute_a3:.2f} ; a3 standardisé {d_a3:.5f} ; étage max {etage_max:.2f}")
    return {"z": z, "normes": normes, "bornes": bornes, "ecartes": ecartes, "d_a2": d_a2,
            "comparables": comparables, "calculs": calculs, "brute_a2": brute_a2, "brute_a3": brute_a3,
            "d_a3": d_a3, "estimation": estimation, "mauvaise": mauvaise, "delta_max": delta_max,
            "etage_max": etage_max}


def cas_4_ecarts_cotation_crypto() -> dict:
    """[CRYPTO] plateforme agréée VARA : écart quadratique moyen de 5 sources, source dominante."""
    e = (12, -8, 15, -40, 5)
    seuil, ordre_usd, taux = 25.0, 2_000_000, 3.6725
    somme = sum(a * a for a in e)
    ne = norme(e)
    rms = ne / math.sqrt(len(e))
    part = max(a * a for a in e) / somme
    sans = tuple(a for a in e if a != -40)
    rms_sans = norme(sans) / math.sqrt(len(sans))
    moyenne = sum(e) / len(e)
    perte_usd = 0.004 * ordre_usd
    norme_bascule = seuil * math.sqrt(len(e))
    e4_bascule = math.sqrt(norme_bascule ** 2 - sum(a * a for a in sans))
    decision = "alerte globale" if rms > seuil else ("source 4 aberrante" if part > 0.5 else "normal")
    print(f"Cas 4 VARA : Σe² = {somme}, ‖e‖ = {ne:.5f}, quadratique moyen {rms:.5f} ; part source 4 {part:.3f} -> {decision}")
    print(f"  sans la source 4 : ‖e‖ = {norme(sans):.5f}, moyen {rms_sans:.5f} ; moyenne signée {moyenne}")
    print(f"  perte {perte_usd:.0f} USD = {perte_usd * taux:.0f} AED ; bascule |e4| = {e4_bascule:.5f}")
    return {"e": e, "somme": somme, "ne": ne, "rms": rms, "part": part, "norme_sans": norme(sans),
            "rms_sans": rms_sans, "moyenne": moyenne, "perte_usd": perte_usd, "perte_aed": perte_usd * taux,
            "norme_bascule": norme_bascule, "e4": e4_bascule, "decision": decision}


def main() -> None:
    # Mécanisme et exemple simple
    v = (0.6, -0.2, 0.3, 0.9, 0.1)
    carres = [round(a * a, 2) for a in v]
    print(f"‖(3,4)‖ = {norme((3, 4))} ; ‖(1,2,2)‖ = {norme((1, 2, 2))} ; carrés de v {carres}, part de 0.9 {0.81 / 1.31:.3f}")
    assert norme((3, 4)) == 5 and norme((1, 2, 2)) == 3 and carres == [0.36, 0.04, 0.09, 0.81, 0.01]
    assert round(sum(a * a for a in v), 2) == 1.31 and round(norme(v), 5) == 1.14455 and round(0.81 / 1.31, 3) == 0.618
    assert normaliser((3, 4)) == (0.6, 0.8) and math.isclose(norme(normaliser((3, 4))), 1.0) and distance((1, 2, 3), (4, 6, 3)) == 5

    # Démonstration 1 — Pythagore
    plancher = norme((1, 2))
    oblique = math.sqrt(1 + 1 + 2 * math.cos(math.radians(60)))
    print(f"D1 : plancher √5 = {plancher:.5f}, puis √(5 + 4) = {math.sqrt(plancher ** 2 + 4):.0f} ; axes à 60° : {oblique ** 2:.0f} au lieu de 2")
    assert math.isclose(plancher ** 2, 5) and math.isclose(math.sqrt(plancher ** 2 + 4), 3) and math.isclose(oblique ** 2, 3)

    # Démonstration 2 — homogénéité
    x, lam = (1.5, -2.0, 0.5), -2.5
    lx = tuple(lam * a for a in x)
    print(f"D2 : ‖x‖ = {norme(x):.5f} ; λx = {lx}, ‖λx‖ = {norme(lx):.5f} = 2.5 x ‖x‖ ; ‖(-6,-8)‖ = {norme((-6, -8))}")
    assert round(sum(a * a for a in x), 2) == 6.5 and round(norme(x), 5) == 2.54951 and lx == (-3.75, 5.0, -1.25)
    assert round(sum(a * a for a in lx), 4) == 40.625 and round(norme(lx), 5) == 6.37377 and math.isclose(norme(lx), 2.5 * norme(x))
    assert norme((-6, -8)) == 10 and norme((0, 0, 0)) == 0

    # Démonstration 3 — triangle
    y = (-0.5, 3.0, 2.0)
    print(f"D3 : ‖(1,1)‖ = {norme((1, 1)):.3f} <= 2 ; ‖(9,12)‖ = {norme((9, 12))} = 5 + 10 ; ‖(3,4)-(6,8)‖ = {distance((3, 4), (6, 8))}")
    assert round(norme((1, 1)), 3) == 1.414 and norme((9, 12)) == 15 and distance((3, 4), (6, 8)) == 5
    assert norme(tuple(a + b for a, b in zip(x, y))) <= norme(x) + norme(y)
    assert distance(x, y) >= abs(norme(x) - norme(y))                       # exercice 6

    # Démonstration 4 — normalisation
    try:
        normaliser((0, 0))
    except ValueError:
        nul_refuse = True
    else:
        nul_refuse = False
    print(f"D4 : (3,4) -> {normaliser((3, 4))}, norme {norme(normaliser((3, 4)))} ; vecteur nul refusé : {nul_refuse}")
    assert nul_refuse and math.isclose(norme(normaliser(x)), 1.0)

    # Démonstration 5 — distance et cosinus
    xh, yh = normaliser(x), normaliser(y)
    cos = sum(a * b for a, b in zip(xh, yh))
    a5, b5 = (3, 0), (0.6, 0.8)
    cos5 = sum(p * r for p, r in zip(a5, b5)) / (norme(a5) * norme(b5))
    print(f"D5 : cos 0.8 -> {math.sqrt(2 - 1.6):.5f} ; cos 0.95 -> {math.sqrt(0.1):.5f} ; sans normaliser :"
          f" cos {cos5:.1f}, 2 - 2cos = {2 - 2 * cos5:.2f}, ‖a-b‖² = {distance(a5, b5) ** 2:.2f}")
    assert math.isclose(distance(xh, yh) ** 2, 2 - 2 * cos)
    assert round(math.sqrt(0.4), 5) == 0.63246 and math.isclose(1 - math.sqrt(0.4) ** 2 / 2, 0.8)
    assert round(math.sqrt(0.1), 5) == 0.31623 and round(cos5, 1) == 0.6 and round(2 - 2 * cos5, 2) == 0.80
    assert round(2.4 ** 2, 2) == 5.76 and round(0.8 ** 2, 2) == 0.64 and round(distance(a5, b5) ** 2, 2) == 6.40

    # Démonstration 6 — encadrement
    e = (12, -8, 15, -40, 5)
    print(f"D6 : {max(abs(a) for a in e)} <= ‖e‖ = {norme(e):.5f} <= √5 x 40 = {math.sqrt(5) * 40:.5f} ;"
          f" (0,7,0) -> {norme((0, 7, 0))} ; (1,1,1,1) -> {norme((1, 1, 1, 1))}")
    assert max(abs(a) for a in e) == 40 <= norme(e) <= math.sqrt(5) * 40 and round(math.sqrt(5) * 40, 5) == 89.44272
    assert norme((0, 7, 0)) == 7 and norme((1, 1, 1, 1)) == 2 and round(1600 / 2058, 3) == 0.777

    # Cas 1 — RH
    c1 = cas_1_index_cv_rh()
    assert round(c1["nv"], 5) == 1.14455 and [round(a, 5) for a in c1["vh"]] == [0.52422, -0.17474, 0.26211, 0.78633, 0.08737]
    assert math.isclose(norme(c1["vh"]), 1.0) and round(c1["tau"], 5) == 0.63246
    assert 1536 * 4 == 6_144 and c1["memoire"] == 1_536_000_000 and 2 * 1536 == 3_072
    assert c1["brut"] == 768_000_000 and c1["normalise"] == 384_000_000 and 250_000 * 3_072 == 768_000_000
    assert round(1.31 + 0.81, 2) == 2.12 and round(2 * 0.8 * c1["nv"] * 0.9, 5) == 1.64816
    assert round(c1["d_brute"] ** 2, 5) == 0.47184 and round(c1["d_brute"], 5) == 0.68691 and c1["d_brute"] > c1["tau"]
    assert round(c1["tau_10"], 5) == 0.6957 and round(c1["cos_10"], 3) == 0.758 and round(0.8 - c1["cos_10"], 3) == 0.042

    # Cas 2 — assurance
    c2 = cas_2_anomalie_sinistre_assurance()
    assert c2["za"] == (2.375, -1.25, 2.5, -1.0) and [z * z for z in c2["za"]] == [5.640625, 1.5625, 6.25, 1.0]
    assert sum(z * z for z in c2["za"]) == 14.453125 and round(c2["na"], 5) == 3.80173 and c2["decision"] == "revue"
    assert max(abs(z) for z in c2["za"]) == 2.5 < 3 and math.sqrt(4) * 2.5 == 5
    assert round(c2["brut_b"], 2) == 500.17 and round(c2["brut_b"] ** 2) == 250_173
    assert [round(z, 5) for z in c2["zb"]] == [0.125, -1.5, 5.5, -1.33333]
    assert round(sum(z * z for z in c2["zb"]), 5) == 34.2934 and round(c2["nb"], 5) == 5.85606
    assert c2["reste"] == 8.8125 and round(9 - c2["reste"], 4) == 0.1875 and round(c2["z1"], 5) == 0.43301
    assert round(c2["montant"]) == 10_732 and round(c2["z10"][0], 4) == 2.8375 and round(c2["n10"], 5) == 4.10657

    # Cas 3 — immobilier
    c3 = cas_3_comparables_immobilier()
    z3 = c3["z"]
    assert z3["q"] == (0.5, 1.0, -0.5) and [round(a, 5) for a in z3["a1"]] == [9.66667, 3.0, -1.5]
    assert [round(a, 5) for a in z3["a2"]] == [0.9, 1.0, -0.1] and z3["a3"] == (0.5, -1.0, 2.5)
    assert round(c3["normes"]["q"] ** 2, 5) == 1.5 and round(c3["normes"]["q"], 5) == 1.22474
    assert round(c3["normes"]["a1"] ** 2, 5) == 104.69444 and round(c3["normes"]["a1"], 5) == 10.23203
    assert round(c3["normes"]["a2"] ** 2, 5) == 1.82 and round(c3["normes"]["a2"], 5) == 1.34907
    assert round(c3["bornes"]["a1"], 5) == 9.00729 and round(c3["bornes"]["a2"], 5) == 0.12433 and c3["ecartes"] == ["a1"]
    assert round(c3["d_a2"] ** 2, 5) == 0.32 and round(c3["d_a2"], 5) == 0.56569 and c3["comparables"] == ["a2"]
    assert c3["calculs"] == 4_500 and c3["estimation"] == 2_187_500 and c3["mauvaise"] == 3_000_000
    assert round(c3["brute_a2"], 2) == 120.07 and round(c3["brute_a3"], 2) == 30.07 and c3["brute_a3"] < c3["brute_a2"]
    assert round(c3["d_a3"], 5) == 3.60555 and c3["mauvaise"] - c3["estimation"] == 812_500
    assert round(0.04 * 812_500) == 32_500 and round(c3["delta_max"], 5) == 0.69282 and round(10 * c3["delta_max"], 2) == 6.93
    assert round(c3["etage_max"], 2) == 16.93 and math.floor(c3["etage_max"]) == 16

    # Cas 4 — crypto
    c4 = cas_4_ecarts_cotation_crypto()
    assert [a * a for a in c4["e"]] == [144, 64, 225, 1600, 25] and c4["somme"] == 2_058
    assert round(c4["ne"], 5) == 45.36518 and round(c4["rms"], 5) == 20.28793 and round(c4["rms"], 2) == 20.29
    assert round(c4["part"], 3) == 0.777 and c4["decision"] == "source 4 aberrante"
    assert round(c4["norme_sans"] ** 2) == 458 and round(c4["norme_sans"], 5) == 21.40093 and round(c4["rms_sans"], 5) == 10.70047
    assert c4["moyenne"] == -3.2 and c4["perte_usd"] == 8_000 and round(c4["perte_aed"]) == 29_380
    assert round(c4["norme_bascule"], 5) == 55.9017 and round(c4["norme_bascule"] ** 2) == 3_125 and 3125 - 458 == 2_667
    assert round(c4["e4"], 5) == 51.64301 and math.floor(c4["e4"]) == 51

    # Corrigé
    print("Corrigé")
    print(f"  ex1 {norme((2, -3, 6))} ; ex2 {normaliser((1, 1, 1, 1))} ; ex3 {norme((1, 1)):.3f} <= 2 ;"
          f" ex4 {norme((3, 4, 0))} ; ex5 {math.sqrt(2 - 2 * 0.95):.5f}")
    assert norme((2, -3, 6)) == 7 and normaliser((1, 1, 1, 1)) == (0.5, 0.5, 0.5, 0.5)
    assert norme((1, 1)) <= 2 and norme((4 - 1, 6 - 2, 3 - 3)) == 5 and round(math.sqrt(2 - 2 * 0.95), 5) == 0.31623
    z7 = standardiser((18_500, 1, 5, 2), (9000, 6, 4, 5), (4000, 4, 2, 3))
    faux = (3 / 7, 4 / 7)
    print(f"  ex7 ‖z‖ = {norme(z7):.5f} -> {'revue' if norme(z7) >= 3 else 'circuit normal'} ; ex8 ‖(3/7, 4/7)‖ = {norme(faux):.5f} ;"
          f" ex9 40 <= {norme(e):.5f} <= {math.sqrt(5) * 40:.5f}")
    assert z7[2] == 0.5 and sum(z * z for z in z7) == 8.453125 and round(norme(z7), 5) == 2.90743 and norme(z7) < 3
    assert round(norme(faux), 5) == 0.71429 and math.isclose(norme(faux), 5 / 7)
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
‖(3,4)‖ = 5.0 ; ‖(1,2,2)‖ = 3.0 ; carrés de v [0.36, 0.04, 0.09, 0.81, 0.01], part de 0.9 0.618
D1 : plancher √5 = 2.23607, puis √(5 + 4) = 3 ; axes à 60° : 3 au lieu de 2
D2 : ‖x‖ = 2.54951 ; λx = (-3.75, 5.0, -1.25), ‖λx‖ = 6.37377 = 2.5 x ‖x‖ ; ‖(-6,-8)‖ = 10.0
D3 : ‖(1,1)‖ = 1.414 <= 2 ; ‖(9,12)‖ = 15.0 = 5 + 10 ; ‖(3,4)-(6,8)‖ = 5.0
D4 : (3,4) -> (0.6, 0.8), norme 1.0 ; vecteur nul refusé : True
D5 : cos 0.8 -> 0.63246 ; cos 0.95 -> 0.31623 ; sans normaliser : cos 0.6, 2 - 2cos = 0.80, ‖a-b‖² = 6.40
D6 : 40 <= ‖e‖ = 45.36518 <= √5 x 40 = 89.44272 ; (0,7,0) -> 7.0 ; (1,1,1,1) -> 2.0
Cas 1 RH : ‖v‖ = 1.14455 ; v̂ = (0.52422 ; -0.17474 ; 0.26211 ; 0.78633 ; 0.08737) ; τ = 0.63246
  mémoire 1,536,000,000 octets ; 768,000,000 -> 384,000,000 multiplications/requête
  distance brute 0.68691 > τ ; τ+10 % = 0.69570 -> cos 0.758
Cas 2 ASSUR : z = (2.375, -1.25, 2.5, -1.0) ; Σz² = 14.453125 ; ‖z‖ = 3.80173 -> revue
  B brut 500.17, B standardisé 5.85606 ; bascule montant 10732 AED ; devis +10 % -> 4.10657
Cas 3 IMMO : ‖q‖ = 1.22474, ‖a1‖ = 10.23203, ‖a2‖ = 1.34907
  bornes a1 9.00729, a2 0.12433 ; d(q, a2) = 0.56569 -> comparables ['a2']
  4500 distances au lieu de 15000 ; estimation 2187500 AED
  brut a2 120.07, a3 30.07 ; a3 standardisé 3.60555 ; étage max 16.93
Cas 4 VARA : Σe² = 2058, ‖e‖ = 45.36518, quadratique moyen 20.28793 ; part source 4 0.777 -> source 4 aberrante
  sans la source 4 : ‖e‖ = 21.40093, moyen 10.70047 ; moyenne signée -3.2
  perte 8000 USD = 29380 AED ; bascule |e4| = 51.64301
Corrigé
  ex1 7.0 ; ex2 (0.5, 0.5, 0.5, 0.5) ; ex3 1.414 <= 2 ; ex4 5.0 ; ex5 0.31623
  ex7 ‖z‖ = 2.90743 -> circuit normal ; ex8 ‖(3/7, 4/7)‖ = 0.71429 ; ex9 40 <= 45.36518 <= 89.44272
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule la longueur d'un vecteur et le normalise, en refusant le vecteur nul qui n'a pas de direction ; une variante mesure une distance après standardisation et écarte d'office les candidats trop lointains grâce à l'inégalité triangulaire.

```text
ALGORITHME NormeEtNormalisation
ENTRÉE  : x = (x₁ … x_d)
SORTIE  : (‖x‖, x̂)

  s ← 0
  POUR i DE 1 À d FAIRE
      s ← s + xᵢ²
  FIN POUR
  n ← √s
  SI n = 0 ALORS ERREUR « vecteur nul : pas de direction »
  POUR i DE 1 À d FAIRE
      x̂ᵢ ← xᵢ / n
  FIN POUR
  RETOURNER n, x̂

ALGORITHME ComparablesÉlagués
ENTRÉES : bien q, biens a₁ … a_N, moyennes μ, écarts-types σ, rayon r
SORTIE  : les biens à distance ≤ r de q
  z(q) ← (q − μ) / σ ; ‖z(q)‖ calculée une fois
  POUR CHAQUE bien aⱼ FAIRE
      SI |‖z(aⱼ)‖ − ‖z(q)‖| > r ALORS passer au suivant      (borne basse, sans calcul)
      SI ‖z(q) − z(aⱼ)‖ ≤ r ALORS garder aⱼ
  FIN POUR
  RETOURNER les biens gardés
```

**Complexité.** O(d) en temps pour la norme et la normalisation (deux passages sur les coordonnées), O(d) en mémoire pour le vecteur normalisé. Normaliser tout un index de N vecteurs coûte O(N × d), une seule fois, et divise ensuite par deux le coût de chaque comparaison. Pour les comparables, les normes des N biens se calculent une fois en O(N × d) ; chaque estimation coûte O(N) comparaisons de normes plus O(d) par bien non écarté.

**Du squelette au code.** La première boucle et la racine sont la fonction `norme` ; la vérification du vecteur nul et la seconde boucle sont `normaliser`. La distance est `distance`, la standardisation `standardiser`. La relation ‖x̂ − ŷ‖² = 2 − 2 cos entre vecteurs normalisés est vérifiée directement dans `main`. ComparablesÉlagués correspond aux dictionnaires `bornes` et `comparables` de `cas_3_comparables_immobilier`. Les trois autres cas sont `cas_1_index_cv_rh`, `cas_2_anomalie_sinistre_assurance` et `cas_4_ecarts_cotation_crypto`.
