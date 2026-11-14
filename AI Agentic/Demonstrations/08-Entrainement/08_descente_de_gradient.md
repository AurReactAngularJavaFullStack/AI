# 08 — Descente de gradient : démonstrations

> Fiche : [08 — Descente de gradient](<../../Images/08-Entrainement/08_descente_de_gradient.md>) · Image : `08_descente_de_gradient.jpg` · Leçon : [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\theta_{t+1} = \theta_t - \eta \times \nabla L(\theta_t)
$$

θ est l'ensemble des paramètres, L la perte, ∇L son gradient (fiche 34) et η > 0 le pas d'apprentissage. On fait un pas dans la direction qui fait baisser la perte le plus vite.

## Les symboles, un par un

$$
\theta_t
$$

Les paramètres du modèle après t pas : un réel ou un vecteur de réels. Dans le programme, `theta` pour un paramètre quelconque et `w` pour le poids d'une régression.

$$
t
$$

Le numéro du pas, entier ≥ 0 ; θ₀ est le point de départ. Dans le programme, c'est la position dans la liste renvoyée par `descente`.

$$
\eta
$$

Le pas d'apprentissage (taux d'apprentissage), réel strictement positif ; il convertit une pente en déplacement. Variable `eta`.

$$
L(\theta)
$$

La perte, réel ≥ 0, que l'on veut rendre minimale. La leçon 73 l'écrit ℒ et réserve la lettre L à sa constante de régularité ; ce fichier garde la notation de la fiche, L pour la perte, et appelle a la courbure. Dans le programme, `L` pour la parabole (θ − 3)².

$$
\nabla L(\theta_t)
$$

Le gradient de la perte au point θₜ : même forme que θ, il pointe vers la plus forte hausse de la perte (fiche 34). Fonctions `grad` (argument de `descente`) et `grad_w`.

$$
a
$$

La courbure d'une perte quadratique L(θ) = a(θ − c)²/2, réel > 0 : c'est la dérivée seconde, la constante que la leçon 73 note L. Fonction `courbure(x)` pour une régression.

$$
c
$$

Le point où la perte quadratique est minimale, dans l'unité du paramètre. Variables `w_star` (régression) et 3 dans la parabole (θ − 3)².

$$
e_t
$$

L'écart au minimum, eₜ = θₜ − c, dans l'unité du paramètre ; e₀ est l'écart de départ. Argument `e0` de `pas_pour_tolerance`.

$$
q
$$

Le facteur q = 1 − ηa par lequel chaque pas multiplie l'écart sur une parabole, sans unité ; la descente converge si |q| < 1. Variable `q`.

$$
\tau
$$

La tolérance, réel > 0 : on s'arrête quand |eₜ| < τ, ou quand l'écart-type du bruit passe sous τ. Variable `tau`.

$$
n, \; x_i, \; y_i, \; w
$$

Pour une régression y ≈ w x : n points, d'entrée xᵢ et de sortie yᵢ, et le poids w qu'on apprend. Variables `x`, `y` (listes) et `w`.

$$
B
$$

La taille d'un mini-lot, entier ≥ 1 : le nombre d'exemples tirés au hasard pour estimer un gradient. Variable `B`.

$$
\sigma^2
$$

La variance du gradient d'un seul exemple tiré au hasard, en unités de gradient au carré. Variable `sigma2`.

## Le mécanisme, avant les preuves

La formule prend deux entrées, la position actuelle θₜ et la pente ∇L(θₜ) en ce point, et rend une nouvelle position. La première opération, le produit η × ∇L, transforme une pente en déplacement : η fixe combien d'unités de paramètre on parcourt par unité de pente. La seconde, la soustraction, choisit le sens : le gradient pointe vers la montée, on recule donc contre lui. Le pas est proportionnel à la pente, et non de longueur fixe : loin du minimum la pente est forte et l'on avance vite, près du minimum elle s'annule et les pas rétrécissent d'eux-mêmes, sans aucun test d'arrêt. C'est pour cela que la formule multiplie le gradient au lieu d'ajouter un pas constant dans sa direction : un pas constant tournerait autour du minimum sans jamais s'y poser. Sur une perte quadratique, la pente est proportionnelle à l'écart au minimum, ∇L = a eₜ, si bien que tout le mécanisme se résume à une multiplication de l'écart par q = 1 − ηa à chaque pas. Trois régimes en découlent : q entre 0 et 1, on glisse vers le minimum ; q entre −1 et 0, on le dépasse en oscillant de moins en moins ; |q| > 1, chaque pas aggrave l'erreur. Le seul réglage qui compte est donc le produit ηa : un pas η n'a de sens que rapporté à la courbure a de la perte. Enfin, quand le gradient est estimé sur un mini-lot, la formule reste la même mais elle reçoit une pente bruitée : le bruit ne biaise pas la direction moyenne, il fait trembler le point d'arrivée.

Petit film chiffré, sur la perte L(θ) = (θ − 3)², donc a = 2, avec η = 0,1, donc q = 0,8. On part de θ₀ = 0 : la pente vaut 2 × (0 − 3) = −6 ; le produit par η donne −0,6 ; la soustraction donne θ₁ = 0 − (−0,6) = 0,6, et l'écart passe de −3 à −2,4. Deuxième pas : pente 2 × (0,6 − 3) = −4,8 ; produit −0,48 ; θ₂ = 1,08, écart −1,92. Troisième pas : pente −3,84 ; produit −0,384 ; θ₃ = 1,464, écart −1,536. Chaque écart vaut 0,8 fois le précédent : −3, −2,4, −1,92, −1,536.

## Démonstration 1 — Un petit pas fait baisser la perte

**Ce qu'on démontre.** Si L est dérivable en θ et si le gradient g = ∇L(θ) n'est pas nul, il existe un pas η > 0 assez petit pour que

$$
L(\theta - \eta g) < L(\theta)
$$

Pour une perte quadratique de courbure a, on a même l'égalité exacte

$$
L(\theta - \eta g) = L(\theta) - \eta \lVert g \rVert^2 \left(1 - \frac{a \eta}{2}\right)
$$

si bien que la perte baisse si et seulement si 0 < η < 2/a.

**L'idée.** Près d'un point, une fonction dérivable ressemble à sa tangente. Un petit déplacement d change donc L d'environ ∇L · d. En prenant d = −ηg, ce produit vaut −η‖g‖², un nombre strictement négatif : on descend. Le reste négligé grandit comme η², et il finit par l'emporter si η est trop grand.

**La preuve, pas à pas.**

**Étape 1.** On écrit le développement de Taylor au premier ordre, parce que L est dérivable en θ :

$$
L(\theta + d) = L(\theta) + \nabla L(\theta) \cdot d + o(\lVert d \rVert)
$$

**Étape 2.** On remplace d par −ηg, parce que c'est le déplacement que fait la formule :

$$
\nabla L(\theta) \cdot (-\eta g) = -\eta \, g \cdot g = -\eta \lVert g \rVert^2
$$

**Étape 3.** On obtient, parce que ‖d‖ = η‖g‖ est proportionnel à η :

$$
L(\theta - \eta g) = L(\theta) - \eta \lVert g \rVert^2 + o(\eta)
$$

Comme ‖g‖² > 0, le terme −η‖g‖² est négatif et domine le reste o(η) quand η tend vers 0 : il existe donc η₀ > 0 tel que la perte baisse pour tout 0 < η < η₀.

**Étape 4.** Cas quadratique, L(θ) = a(θ − c)²/2, donc g = a(θ − c). Le nouveau point θ − ηg a pour écart au minimum (θ − c) − ηa(θ − c), parce que g = a(θ − c) ; d'où

$$
L(\theta - \eta g) = \frac{a}{2}(1 - \eta a)^2 (\theta - c)^2 = (1 - \eta a)^2 \, L(\theta)
$$

**Étape 5.** On développe (1 − ηa)² = 1 − 2ηa + η²a², et l'on utilise ‖g‖² = a²(θ − c)² = 2a L(θ), parce que L(θ) = a(θ − c)²/2 :

$$
(1 - \eta a)^2 L(\theta) = L(\theta) - \eta \,(2 a L(\theta)) + \frac{\eta^2 a}{2}\,(2 a L(\theta)) = L(\theta) - \eta \lVert g \rVert^2 + \frac{\eta^2 a}{2} \lVert g \rVert^2
$$

C'est l'égalité annoncée ; la parenthèse 1 − aη/2 est positive si et seulement si η < 2/a. ∎

**Vérification chiffrée.** L(θ) = (θ − 3)² s'écrit 2(θ − 3)²/2, donc a = 2. Au point θ = 0 : L(0) = 9, g = −6, ‖g‖² = 36. Avec η = 0,1, le premier ordre prédit 9 − 0,1 × 36 = 5,4 ; la formule exacte donne 9 − 3,6 × (1 − 0,1) = 9 − 3,24 = 5,76 ; et directement L(0,6) = (0,6 − 3)² = 5,76. Contre-exemple quand l'hypothèse « η assez petit » manque : η = 1,1 > 2/a = 1 donne θ = 0 + 1,1 × 6 = 6,6 et L(6,6) = 3,6² = 12,96 > 9 ; la formule exacte le confirme, 9 − 1,1 × 36 × (1 − 1,1) = 12,96.

**Ce que la preuve révèle du mécanisme.** La baisse vient du terme −η‖g‖², proportionnel au carré de la pente : un gradient deux fois plus fort donne, au premier ordre, une baisse quatre fois plus grande. Le frein vient du terme en η²a, qui mesure la courbure : plus la perte se recourbe, plus vite la tangente cesse d'être une bonne approximation. La frontière η = 2/a est l'endroit exact où les deux termes s'équilibrent.

**Conséquence pour un agent.** Un job d'entraînement doit surveiller la perte après chaque pas ou chaque évaluation : si elle monte, le pas a franchi la frontière 2/a et il faut le diviser, par exemple par deux. C'est le garde-fou « recharger le dernier point de sauvegarde et réduire η » de la leçon 73.

## Démonstration 2 — La direction de descente la plus rapide

**Ce qu'on démontre.** Pour un gradient non nul, parmi tous les vecteurs u de longueur 1, la pente de L dans la direction u vérifie

$$
\nabla L \cdot u \ge -\lVert \nabla L \rVert
$$

avec égalité seulement pour u = −∇L/‖∇L‖.

**L'idée.** La pente dans une direction est un produit scalaire, et un produit scalaire est le plus négatif quand les deux vecteurs sont opposés. Aller contre le gradient est donc, localement, la descente la plus raide.

**La preuve, pas à pas.**

**Étape 1.** Par la règle de la chaîne (fiche 34, démonstration 1), la pente de L le long du chemin θ + s u, au point s = 0, vaut ∇L · u.

**Étape 2.** Par l'inégalité de Cauchy–Schwarz (fiche 01), parce que |a · b| ≤ ‖a‖ ‖b‖ pour tous vecteurs a et b, et que ‖u‖ = 1 :

$$
\lvert \nabla L \cdot u \rvert \le \lVert \nabla L \rVert \, \lVert u \rVert = \lVert \nabla L \rVert
$$

donc ∇L · u ≥ −‖∇L‖.

**Étape 3.** Le vecteur u = −∇L/‖∇L‖ est de longueur 1, parce que diviser un vecteur non nul par sa norme le ramène à la longueur 1, et il atteint la borne :

$$
\nabla L \cdot \left(-\frac{\nabla L}{\lVert \nabla L \rVert}\right) = -\frac{\lVert \nabla L \rVert^2}{\lVert \nabla L \rVert} = -\lVert \nabla L \rVert
$$

L'égalité dans Cauchy–Schwarz n'a lieu que pour des vecteurs colinéaires, d'où l'unicité. ∎

**Vérification chiffrée.** L(θ₁, θ₂) = θ₁² + 3θ₂² au point (1 ; 1) : ∇L = (2 ; 6) et ‖∇L‖ = √40 ≈ 6,32456. Direction (−1 ; 0) : pente −2. Direction (0 ; −1) : pente −6. Direction (−0,6 ; −0,8) : pente −1,2 − 4,8 = −6. Direction −∇L/‖∇L‖ = (−0,31623 ; −0,94868) : pente −6,32456, la plus négative des quatre.

**Ce que la preuve révèle du mécanisme.** La direction optimale suit le gradient coordonnée par coordonnée, en proportion : ici θ₂ reçoit 0,94868 contre 0,31623 pour θ₁, trois fois plus, parce que la perte y est trois fois plus pentue. C'est une propriété locale : elle dit où aller au prochain pas, pas où se trouve le minimum.

**Conséquence pour un agent.** La descente de gradient n'a besoin que du gradient, jamais d'une recherche de direction coûteuse : c'est ce qui la rend praticable sur des millions de paramètres. Mais « la plus raide localement » ne veut pas dire « la plus courte vers le minimum » quand les courbures diffèrent : c'est le cas 4, et la raison d'être d'Adam (fiche 31).

## Démonstration 3 — Sur une parabole, l'erreur est multipliée par 1 − ηa

**Ce qu'on démontre.** Pour L(θ) = a(θ − c)²/2 avec a > 0, et eₜ = θₜ − c :

$$
e_{t+1} = (1 - \eta a)\, e_t, \qquad e_t = (1 - \eta a)^t \, e_0
$$

La descente converge vers c pour tout départ si et seulement si 0 < η < 2/a. Pour une tolérance τ > 0 avec τ < |e₀|, et 0 < |q| < 1, le nombre de pas nécessaire pour avoir |eₖ| < τ est le plus petit entier k tel que

$$
k > \frac{\ln(\tau / \lvert e_0 \rvert)}{\ln \lvert q \rvert}
$$

**L'idée.** Sur une parabole, la pente est proportionnelle à l'écart. Retirer η fois la pente revient à retirer la fraction ηa de l'écart : il en reste la fraction 1 − ηa, à chaque pas, toujours la même. Une multiplication répétée par un même nombre tend vers 0 si et seulement si ce nombre est de valeur absolue inférieure à 1.

**La preuve, pas à pas.**

**Étape 1.** On calcule le gradient, parce que la dérivée de a(θ − c)²/2 vaut a(θ − c) :

$$
\nabla L(\theta_t) = a\,(\theta_t - c) = a\, e_t
$$

**Étape 2.** On soustrait c des deux côtés de la mise à jour, parce que c ne change pas d'un pas à l'autre :

$$
\theta_{t+1} - c = (\theta_t - c) - \eta a (\theta_t - c) = (1 - \eta a)\, e_t
$$

**Étape 3.** Par récurrence sur t, parce que chaque pas multiplie par le même facteur q = 1 − ηa, on obtient eₜ = qᵗ e₀.

**Étape 4.** |qᵗ e₀| tend vers 0 pour tout e₀ si et seulement si |q| < 1, ce qui s'écrit, parce que a > 0 et η > 0 :

$$
-1 < 1 - \eta a < 1 \iff 0 < \eta a < 2 \iff 0 < \eta < \frac{2}{a}
$$

**Étape 5.** Nombre de pas : |eₖ| = |q|ᵏ |e₀| < τ équivaut, en prenant le logarithme, qui est croissant, à k ln|q| < ln(τ/|e₀|) ; on divise par ln|q|, qui est négatif, ce qui retourne l'inégalité. ∎

**Vérification chiffrée.** a = 2 (perte (θ − 3)²) et e₀ = −3. Avec η = 0,1, q = 0,8 : régime monotone, et le rapport de deux gradients successifs, −4,8/(−6) = 0,8, retrouve q. Avec η = 0,9, q = −0,8 : θ vaut 5,4 puis 1,08, on dépasse 3 puis on revient, de moins en moins loin. Avec η = 1,1 > 2/a = 1, q = −1,2 : θ vaut 6,6 puis −1,32 puis 8,184, c'est la divergence. Nombre de pas pour τ = 0,01 avec q = 0,8 : ln(0,01/3)/ln 0,8 = (−5,70378)/(−0,22314) ≈ 25,56, donc k = 26 ; contrôle : 3 × 0,8²⁵ ≈ 0,01133 est encore au-dessus de 0,01, et 3 × 0,8²⁶ ≈ 0,00907 est en dessous.

**Ce que la preuve révèle du mécanisme.** Tout dépend du seul produit ηa : doubler η ou doubler la courbure a le même effet. Le meilleur pas est η = 1/a, qui donne q = 0 : on tombe sur le minimum en un pas. Le nombre de pas croît comme 1/|ln|q||, donc il explose quand |q| s'approche de 1 des deux côtés : un η trop petit (q proche de +1) et un η presque à la frontière (q proche de −1) sont aussi lents l'un que l'autre.

**Conséquence pour un agent.** On ne règle pas η dans l'absolu mais par rapport à la courbure. Un garde-fou simple mesure le rapport de deux gradients successifs, qui vaut exactement q sur une parabole : s'il dépasse 1 en valeur absolue, on divise η ; s'il reste proche de 1, on peut l'augmenter.

## Démonstration 4 — La courbure d'une régression vaut 2Σx²/n et grandit comme le carré de l'échelle

**Ce qu'on démontre.** Pour n points (xᵢ ; yᵢ), avec des xᵢ non tous nuls, et le modèle y ≈ w x, la perte quadratique moyenne

$$
L(w) = \frac{1}{n} \sum_{i=1}^{n} (w x_i - y_i)^2
$$

est une parabole en w, de minimum et de courbure

$$
w^* = \frac{\sum x_i y_i}{\sum x_i^2}, \qquad a = \frac{2}{n} \sum x_i^2
$$

Si l'on multiplie toutes les entrées xᵢ par un facteur s > 0 (changement d'unité), la courbure est multipliée par s², et la limite de pas 2/a est divisée par s².

**L'idée.** Développer le carré donne un polynôme du second degré en w ; son coefficient de w² fixe la courbure. Les xᵢ y entrent au carré, d'où l'effet en s².

**La preuve, pas à pas.**

**Étape 1.** On développe chaque carré, parce que (wx − y)² = w²x² − 2wxy + y² :

$$
L(w) = \frac{1}{n}\left( w^2 \sum x_i^2 - 2 w \sum x_i y_i + \sum y_i^2 \right)
$$

**Étape 2.** On dérive par rapport à w, parce que le gradient d'une fonction d'une variable est sa dérivée, puis on met (2/n)Σxᵢ² en facteur, ce qui est permis parce que Σxᵢ² > 0 :

$$
\nabla L(w) = \frac{2}{n}\left( w \sum x_i^2 - \sum x_i y_i \right) = \frac{2}{n} \sum x_i^2 \; (w - w^*)
$$

Le gradient s'annule en w* et s'écrit a(w − w*) : c'est exactement la forme de la démonstration 3, avec c = w*.

**Étape 3.** Changement d'échelle xᵢ → s xᵢ : chaque xᵢ² devient s² xᵢ², parce que (s xᵢ)² = s² xᵢ² ; donc a devient s² a et 2/a devient (2/a)/s². ∎

**Vérification chiffrée.** Pour x = (1 ; 2 ; 3 ; 4) milliers de tokens et y = (2,1 ; 3,9 ; 6,2 ; 7,8) secondes (cas 1) : Σx² = 30, Σxy = 59,7, w* = 59,7/30 = 1,99 et a = 2 × 30/4 = 15, d'où ∇L(w) = 15w − 29,85 et la limite η < 2/15 ≈ 0,13333. Si l'on compte les tokens un par un au lieu de milliers (s = 1 000), a devient 15 × 10⁶ = 1,5 × 10⁷ et la limite tombe à 2/(1,5 × 10⁷) ≈ 1,333 × 10⁻⁷. Contre-exemple de l'hypothèse « xᵢ non tous nuls » : avec x = (0 ; 0), Σx² = 0, w* n'a pas de dénominateur et le programme renvoie `None`.

**Ce que la preuve révèle du mécanisme.** La courbure ne dépend que des entrées xᵢ, pas des sorties yᵢ : les yᵢ déplacent le minimum, les xᵢ fixent la forme de la vallée. Une entrée mal mise à l'échelle rend la vallée si étroite que tout pas raisonnable la fait diverger.

**Conséquence pour un agent.** Avant d'entraîner, on normalise chaque entrée (division par un maximum ou par un écart-type) : c'est ce qui permet de garder un même η d'un jeu de données à l'autre. Un contrôle d'échelle à l'ingestion est un garde-fou plus sûr qu'une surveillance de la perte, qui ne voit le problème qu'une fois la divergence commencée (cas 2).

## Démonstration 5 — Le gradient d'un mini-lot est sans biais, et sa variance vaut σ²/B

**Ce qu'on démontre.** La perte totale est une moyenne de pertes individuelles, L = (1/n)ΣLᵢ. On tire B indices I₁, …, I_B uniformément et avec remise, et l'on forme le gradient du mini-lot :

$$
\hat g = \frac{1}{B} \sum_{j=1}^{B} \nabla L_{I_j}
$$

Alors, si σ² est la variance du gradient d'un seul exemple tiré au hasard,

$$
\mathbb{E}[\hat g] = \nabla L, \qquad \operatorname{Var}(\hat g) = \frac{\sigma^2}{B}
$$

**L'idée.** Un exemple tiré au hasard vaut, en moyenne, la moyenne de tous : c'est la linéarité de l'espérance. Moyenner B tirages indépendants ne change pas la moyenne mais divise la variance par B, comme dans un sondage.

**La preuve, pas à pas.**

**Étape 1.** Le gradient d'une moyenne est la moyenne des gradients, parce que la dérivation est linéaire : ∇L = (1/n)Σ∇Lᵢ.

**Étape 2.** Un indice I tiré uniformément vaut chaque i avec la probabilité 1/n, donc, par définition de l'espérance :

$$
\mathbb{E}[\nabla L_I] = \sum_{i=1}^{n} \frac{1}{n} \nabla L_i = \nabla L
$$

**Étape 3.** Par linéarité de l'espérance (fiche 22), la moyenne de B tirages a la même espérance :

$$
\mathbb{E}[\hat g] = \frac{1}{B} \sum_{j=1}^{B} \mathbb{E}[\nabla L_{I_j}] = \nabla L
$$

**Étape 4.** Les tirages sont indépendants (avec remise), donc leurs variances s'additionnent, et le facteur 1/B sort au carré, parce que Var(cX) = c² Var(X) :

$$
\operatorname{Var}(\hat g) = \frac{1}{B^2} \sum_{j=1}^{B} \operatorname{Var}(\nabla L_{I_j}) = \frac{1}{B^2} \times B \sigma^2 = \frac{\sigma^2}{B}
$$

∎

**Vérification chiffrée.** Données du cas 1, au point w = 1. Les résidus w xᵢ − yᵢ valent −1,1 ; −1,9 ; −3,2 ; −3,8, et les gradients individuels 2(w xᵢ − yᵢ)xᵢ valent −2,2 ; −7,6 ; −19,2 ; −30,4. Leur moyenne vaut −59,4/4 = −14,85, exactement ∇L(1) = 15 − 29,85. Écarts à la moyenne : 12,65 ; 7,25 ; −4,35 ; −15,55 ; carrés : 160,0225 ; 52,5625 ; 18,9225 ; 241,8025 ; donc σ² = 473,31/4 = 118,3275 et σ ≈ 10,8778. Un mini-lot de B = 4 a un écart-type σ/2 ≈ 5,4389. Le programme tire 20 000 gradients d'un seul exemple : leur moyenne vaut −14,907, à moins de 0,1 de la valeur exacte. Contre-exemple quand le tirage n'est pas uniforme : un lot qui ne contient jamais le quatrième point (les réponses les plus longues) a pour moyenne (−2,2 − 7,6 − 19,2)/3 ≈ −9,6667, environ 35 % trop faible en valeur absolue, et aucune taille de lot ne corrige ce biais.

**Ce que la preuve révèle du mécanisme.** Le mini-lot ne change pas la direction moyenne, seulement le bruit autour d'elle, et ce bruit baisse lentement : diviser l'écart-type par 2 demande 4 fois plus d'exemples. L'hypothèse qui compte est le tirage uniforme : un lot qui sur-représente un type d'exemples est biaisé, quel que soit B.

**Conséquence pour un agent.** On mélange les données avant de découper les lots, et l'on choisit B par un calcul de bruit, pas par habitude (cas 3). Un lot construit par ordre de date ou par client, sans mélange, donne un gradient faux en moyenne.

## Démonstration 6 — Avec un pas constant, la descente stochastique garde un bruit plancher

**Ce qu'on démontre.** Près du minimum d'une parabole de courbure a, on modélise le pas stochastique par

$$
e_{t+1} = q\, e_t - \eta\, \xi_t, \qquad q = 1 - \eta a
$$

où les bruits ξₜ sont indépendants entre eux et de eₜ, de moyenne 0 et de variance σ²/B (démonstration 5, avec σ² mesurée au minimum). Si |q| < 1, la variance Vₜ de l'écart tend vers

$$
V_\infty = \frac{\eta^2 \sigma^2}{B\,(1 - q^2)}
$$

et, pour que l'écart-type reste sous τ, il faut un mini-lot

$$
B \ge \frac{\eta^2 \sigma^2}{\tau^2 (1 - q^2)}
$$

**L'idée.** Chaque pas fait deux choses : il rétrécit l'ancienne erreur (facteur q) et il ajoute un bruit neuf (η ξ). L'équilibre est atteint quand le bruit ajouté compense exactement ce que le rétrécissement retire. Un pas constant ne s'arrête donc jamais exactement au minimum : il tremble autour.

**La preuve, pas à pas.**

**Étape 1.** On prend la variance des deux membres. Comme ξₜ est indépendant de eₜ, les variances s'ajoutent, parce que Var(X + Y) = Var X + Var Y pour des variables indépendantes, et les constantes sortent au carré :

$$
V_{t+1} = q^2 V_t + \frac{\eta^2 \sigma^2}{B}
$$

**Étape 2.** Un point fixe V vérifie V = q²V + η²σ²/B. On isole V, ce qui est possible parce que 1 − q² > 0 quand |q| < 1 : c'est la formule de V∞.

**Étape 3.** On soustrait l'équation du point fixe à celle de l'étape 1, parce que les deux contiennent le même terme η²σ²/B :

$$
V_{t+1} - V_\infty = q^2 \,(V_t - V_\infty)
$$

L'écart au point fixe est multiplié par q² < 1 à chaque pas, il tend donc vers 0.

**Étape 4.** La condition V∞ ≤ τ² se réécrit, en multipliant par B et en divisant par τ², parce que ces deux nombres sont positifs, en la borne sur B. ∎

**Vérification chiffrée.** Avec a = 5 et η = 0,1, q = 0,5 ; avec σ² = 1 et B = 4 : V∞ = 0,01 × 1/(4 × 0,75) ≈ 0,0033333. Le programme simule le modèle sur 20 000 pas et trouve 0,0033716, à 1,1 % de la théorie. Contre-exemple quand l'hypothèse |q| < 1 manque : avec a = 22 et η = 0,1, q = −1,2, et Vₜ₊₁ = 1,44 Vₜ + … grandit sans limite ; la fonction `bruit_plancher` renvoie `None`, parce qu'il n'y a pas de plancher, seulement une divergence.

**Ce que la preuve révèle du mécanisme.** Le plancher grandit comme η² et rétrécit comme 1/B : un pas plus grand converge plus vite en moyenne mais tremble plus fort. Le facteur 1/(1 − q²) explose quand |q| approche 1, ce qui pénalise les pas proches de la frontière 2/a. Il y a donc un compromis réel entre vitesse (|q| petit) et précision (V∞ petit), que l'on règle avec B.

**Conséquence pour un agent.** Pour une tolérance donnée, on choisit le couple (η, B) qui minimise le coût total, nombre de pas × B exemples (cas 3). On peut aussi faire décroître η en fin d'entraînement pour abaisser le plancher, ce que font les calendriers de pas (montée progressive puis décroissance).

## Exemple simple, à la main

Perte L(θ) = (θ − 3)², donc a = 2 et minimum c = 3. Départ θ₀ = 0, pas η = 0,1, donc q = 1 − 0,1 × 2 = 0,8. Les deux premiers pas, écrits en entier :

$$
\theta_1 = 0 - 0{,}1 \times 2 \times (0 - 3) = 0{,}6, \qquad \theta_2 = 0{,}6 - 0{,}1 \times 2 \times (0{,}6 - 3) = 1{,}08
$$

Les cinq premiers pas, colonne par colonne : gradient 2(θₜ − 3), produit par η, nouveau point, nouvel écart.

| t | θₜ | gradient 2(θₜ − 3) | η × gradient | θₜ₊₁ = θₜ − η × gradient | écart θₜ₊₁ − 3 |
|---|---|---|---|---|---|
| 0 | 0 | −6 | −0,6 | 0,6 | −2,4 |
| 1 | 0,6 | −4,8 | −0,48 | 1,08 | −1,92 |
| 2 | 1,08 | −3,84 | −0,384 | 1,464 | −1,536 |
| 3 | 1,464 | −3,072 | −0,3072 | 1,7712 | −1,2288 |
| 4 | 1,7712 | −2,4576 | −0,24576 | 2,01696 | −0,98304 |

Contrôle par la démonstration 3 : e₅ = −3 × 0,8⁵ = −3 × 0,32768 = −0,98304, donc θ₅ = 3 − 0,98304 = 2,01696. La perte passe de L(θ₀) = 9 à L(θ₅) = 0,98304² ≈ 0,96637 ; par l'étape 4 de la démonstration 1, chaque pas la multiplie par q² = 0,64, et en effet 9 × 0,64⁵ ≈ 0,96637.

## Cas d'usage complexes, démontrés

### Cas 1 — Services publics [PUBLIC] : apprendre la latence de l'assistant bilingue

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, fait répondre un assistant bilingue arabe/anglais. Son équipe d'exploitation veut prédire la latence d'une réponse à partir de sa taille, pour régler le délai d'attente (timeout) de l'agent : trop court, il coupe des réponses valides ; trop long, il laisse l'usager attendre. Elle ajuste le modèle y ≈ w x (y en secondes, x en milliers de tokens) par descente de gradient, dans un petit job relancé à chaque déploiement et limité à 10 pas. Les mesures et les volumes sont illustratifs.

**Données.**

- Mesures (x ; y) : (1 ; 2,1), (2 ; 3,9), (3 ; 6,2), (4 ; 7,8), soit n = 4.
- Départ w₀ = 0 ; tolérance τ = 0,01 seconde par millier de tokens ; budget de 10 pas.
- Pas candidats : η = 0,05 ; 0,1 ; 0,15.
- Requête de référence pour le délai : 6 000 tokens, soit x = 6.

**Calcul pas à pas.**

**Étape 1.** Les deux sommes de la démonstration 4 :

$$
\sum x_i^2 = 1 + 4 + 9 + 16 = 30, \qquad \sum x_i y_i = 2{,}1 + 7{,}8 + 18{,}6 + 31{,}2 = 59{,}7
$$

**Étape 2.** Minimum, courbure et gradient :

$$
w^* = \frac{59{,}7}{30} = 1{,}99, \qquad a = \frac{2 \times 30}{4} = 15, \qquad \nabla L(w) = 15\,w - 29{,}85
$$

**Étape 3.** Facteur q = 1 − 15η pour chaque pas candidat, et frontière 2/a :

$$
q_{0{,}05} = 0{,}25, \qquad q_{0{,}1} = -0{,}5, \qquad q_{0{,}15} = -1{,}25, \qquad \frac{2}{a} \approx 0{,}13333
$$

**Étape 4.** Trajectoires sur 4 pas, par wₜ = 1,99 − 1,99 × qᵗ, arrondies à 4 décimales :

- η = 0,05 : 1,4925 ; 1,8656 ; 1,9589 ; 1,9822 (convergence monotone) ;
- η = 0,1 : 2,985 ; 1,4925 ; 2,2388 ; 1,8656 (oscillation amortie) ;
- η = 0,15 : 4,4775 ; −1,1194 ; 5,8767 ; −2,8684 (divergence).

**Étape 5.** Nombre de pas pour |eₖ| < 0,01 avec |e₀| = 1,99 (démonstration 3) :

$$
k_{0{,}05} > \frac{\ln(0{,}01/1{,}99)}{\ln 0{,}25} = \frac{-5{,}2933}{-1{,}38629} \approx 3{,}818, \qquad k_{0{,}1} > \frac{-5{,}2933}{-0{,}69315} \approx 7{,}637
$$

donc 4 pas pour η = 0,05 et 8 pas pour η = 0,1 ; aucun nombre de pas ne suffit pour η = 0,15.

**Décision de l'agent.** Les deux premiers pas tiennent dans le budget de 10 pas. Le job retient η = 0,05, qui converge en 4 pas et laisse la plus grande marge : il reste stable tant que la courbure ne dépasse pas 2/0,05 = 40, soit 2,67 fois la courbure actuelle. Avec w₄ = 1,9822, la latence prévue d'une requête de 6 000 tokens vaut 6 × 1,9822 ≈ 11,89 s, contre 6 × 1,99 = 11,94 s au minimum exact : l'écart est sans effet sur le réglage du délai.

**Contre-calcul.** L'ancienne version de ce fichier annonçait « une parabole de courbure 30 », donc η < 2/30 ≈ 0,0667 : c'est faux, la courbure vaut 2Σx²/n = 15 (démonstration 4), et cette erreur aurait fait rejeter η = 0,1, qui converge. L'erreur inverse coûte plus cher : un η = 0,15 repris d'un autre job, où il marchait, donne après les 10 pas w₁₀ ≈ −16,5433, soit une latence prévue de −99,26 s pour 6 000 tokens. Un délai calculé sur cette valeur serait négatif : chaque requête serait coupée et renvoyée vers un conseiller humain.

**Sensibilité.** La valeur de bascule est η = 2/a ≈ 0,13333. Côté données, si les réponses s'allongent d'un facteur s, la courbure devient 15s² (démonstration 4), et η = 0,05 diverge dès que 15s² × 0,05 > 2, soit s > √(2/0,75) ≈ 1,633. Avec des réponses 1,5 fois plus longues, a = 33,75 et q = −0,6875 : le job converge encore, en oscillant. Avec des réponses deux fois plus longues, a = 60 et q = −2 : il diverge.

**En production.** L'indicateur suivi est le rapport de deux gradients successifs, qui vaut exactement q sur cette parabole (démonstration 3). Alerte si sa valeur absolue dépasse 0,9 : il faudrait alors 51 pas pour atteindre 0,01, bien plus que le budget de 10. Arrêt du job et division de η par deux s'il dépasse 1. Les journaux de latence ne contiennent ni Emirates ID ni texte des usagers : le régime de protection des données applicable à l'entité (PDPL ou texte propre) est à confirmer avec le texte en vigueur.

### Cas 2 — Assurance [ASSUR] : un montant en AED bruts fait exploser l'entraînement

**Contexte.** Un assureur auto et santé entraîne par descente de gradient un petit modèle de tri qui estime la complexité d'un sinistre (un score entre 0 et 1) et décide s'il part en traitement automatique ou chez un expert. Une nouvelle source de données arrive avec le montant réclamé en AED bruts, alors que le pipeline recevait jusque-là des montants normalisés, et le pas η = 0,5 qui marchait est conservé. Les montants, volumes et coûts sont illustratifs.

**Données.**

- Montants réclamés x : 8 000 ; 15 000 ; 22 000 ; 35 000 AED.
- Scores de complexité y : 0,2 ; 0,35 ; 0,5 ; 0,8 (n = 4).
- Modèle y ≈ w x, départ w₀ = 0, pas η = 0,5, tolérance τ = 0,001.
- Normalisation prévue : division par le plus grand montant, 35 000 AED.
- 2 000 sinistres par jour ; une revue manuelle coûte 45 AED par dossier.

**Calcul pas à pas.**

**Étape 1.** Courbure en AED bruts (démonstration 4) :

$$
\sum x_i^2 = 6{,}4 \times 10^7 + 2{,}25 \times 10^8 + 4{,}84 \times 10^8 + 1{,}225 \times 10^9 = 1{,}998 \times 10^9, \qquad a = \frac{2 \times 1{,}998 \times 10^9}{4} = 9{,}99 \times 10^8
$$

**Étape 2.** Frontière et facteur avec η = 0,5 :

$$
\frac{2}{a} \approx 2{,}002 \times 10^{-9}, \qquad q = 1 - 0{,}5 \times 9{,}99 \times 10^8 = -499\,499\,999 \approx -4{,}995 \times 10^8
$$

Le premier pas, depuis w₀ = 0 : Σxy = 1 600 + 5 250 + 11 000 + 28 000 = 45 850, donc ∇L(0) = −(2/4) × 45 850 = −22 925 et w₁ = 0 − 0,5 × (−22 925) = 11 462,5, alors que le minimum vaut w* = 45 850/(1,998 × 10⁹) ≈ 2,2948 × 10⁻⁵.

**Étape 3.** Courbure après normalisation x′ = x/35 000, soit x′ ≈ 0,22857 ; 0,42857 ; 0,62857 ; 1 :

$$
\sum x_i'^2 = \frac{1{,}998 \times 10^9}{1{,}225 \times 10^9} \approx 1{,}63102, \qquad a' = \frac{2 \times 1{,}63102}{4} \approx 0{,}81551, \qquad q' = 1 - 0{,}5 \times 0{,}81551 \approx 0{,}59224
$$

La nouvelle frontière vaut 2/a′ ≈ 2,45245 : η = 0,5 est loin en dessous.

**Étape 4.** Minimum normalisé et nombre de pas (démonstration 3) :

$$
w'^* = \frac{45\,850 / 35\,000}{1{,}63102} = \frac{1{,}31}{1{,}63102} \approx 0{,}80318, \qquad k > \frac{\ln(0{,}001/0{,}80318)}{\ln 0{,}59224} \approx 12{,}77
$$

donc 13 pas.

**Décision de l'agent.** Le pipeline refuse la colonne brute et la normalise avant l'entraînement ; avec η = 0,5 inchangé, la descente converge en 13 pas, et le seuil de tri garde son sens : un sinistre de 35 000 AED (x′ = 1) reçoit un score prévu de 0,80318.

**Contre-calcul.** Sans normalisation, chaque pas multiplie l'écart par environ −5 × 10⁸ : après 3 pas l'écart vaut déjà environ 2,86 × 10²¹, et au 36ᵉ pas le poids déborde en valeur infinie, puis en NaN. Le modèle exporté ne contient que des NaN, et l'agent de tri envoie tous les dossiers dans la même file. Si c'est la revue manuelle, une journée coûte 2 000 × 45 = 90 000 AED (illustratif), sans compter le retard pris sur les sinistres simples.

**Sensibilité.** Avec η = 0,5, la descente diverge dès que a > 2/0,5 = 4, c'est-à-dire dès que la moyenne des x² dépasse 2 : la valeur de bascule est une moyenne quadratique (RMS) des entrées de √2 ≈ 1,41421. Les données normalisées ont une RMS de √(1,63102/4) ≈ 0,63856, soit une marge de 2,21. Mais un seul sinistre exceptionnel de 120 000 AED, normalisé par l'ancien maximum, vaut 3,42857 ; avec lui, la somme des x² passe à 13,38612, leur moyenne à 13,38612/5 ≈ 2,67722 > 2, a = 5,35445 et q ≈ −1,67722 : la descente diverge à nouveau. Diviser par un maximum figé ne suffit donc pas : il faut recalculer l'échelle à chaque entraînement.

**En production.** Indicateur : la RMS de chaque colonne à l'ingestion, avec une alerte à 1,2 (illustratif) et un blocage à 1,41421 pour η = 0,5 ; second garde-fou, l'arrêt du job si la perte de validation monte trois évaluations de suite (leçon 73). L'assurance est supervisée par la CBUAE ; les exigences précises de gestion du risque de modèle sont à confirmer avec le texte en vigueur.

### Cas 3 — Immobilier [IMMO] : taille du mini-lot pour réestimer le prix au sqft

**Contexte.** Une agence active à Dubaï et à Abu Dhabi réestime chaque nuit, par descente stochastique, le prix au sqft qu'utilise son agent pour présélectionner des biens. Le modèle est y ≈ w x, avec x la surface en milliers de sqft et y le prix en millions d'AED, si bien que w s'exprime en milliers d'AED par sqft. Les transactions de la nuit se répartissent également entre quatre types de biens, tirés au hasard pour former les mini-lots. La question : quel couple (pas η, taille de lot B) atteint une précision de 10 AED/sqft au moindre coût de calcul ? Données illustratives.

**Données.**

- Quatre types (x ; y) : (0,5 ; 1,0), (1 ; 1,8), (1,5 ; 2,9), (2 ; 3,8).
- Modèle de la veille : w₀ = 1,6, soit 1 600 AED/sqft.
- Tolérance τ = 0,01, soit 10 AED/sqft, à la fois sur l'écart moyen et sur l'écart-type du bruit.
- Pas candidats : η = 0,1 ; 0,25 ; 0,4.

**Calcul pas à pas.**

**Étape 1.** Courbure et minimum (démonstration 4) :

$$
\sum x_i^2 = 0{,}25 + 1 + 2{,}25 + 4 = 7{,}5, \qquad a = \frac{2 \times 7{,}5}{4} = 3{,}75, \qquad w^* = \frac{0{,}5 + 1{,}8 + 4{,}35 + 7{,}6}{7{,}5} = \frac{14{,}25}{7{,}5} = 1{,}9
$$

Le marché est à 1 900 AED/sqft ; l'écart de départ vaut |e₀| = 0,3.

**Étape 2.** Bruit d'un exemple au minimum. Résidus 1,9 xᵢ − yᵢ : −0,05 ; 0,1 ; −0,05 ; 0. Gradients individuels 2(1,9 xᵢ − yᵢ)xᵢ : −0,05 ; 0,2 ; −0,15 ; 0, de moyenne nulle comme il se doit au minimum. D'où :

$$
\sigma^2 = \frac{0{,}0025 + 0{,}04 + 0{,}0225 + 0}{4} = 0{,}01625
$$

**Étape 3.** Pour chaque η : le facteur q = 1 − 3,75η, le plancher pour B = 1, V₁ = η²σ²/(1 − q²), le lot minimal (démonstration 6) et le nombre de pas k pour 0,3 × |q|ᵏ < 0,01 (démonstration 3) :

$$
B_{\min} = \left\lceil \frac{\eta^2 \sigma^2}{\tau^2 (1 - q^2)} \right\rceil, \qquad \text{coût} = k \times B_{\min}
$$

| η | q | 1 − q² | V₁ | B minimal | pas k | coût k × B |
|---|---|---|---|---|---|---|
| 0,1 | 0,625 | 0,609375 | 0,0002667 | 3 | 8 | 24 |
| 0,25 | 0,0625 | 0,996094 | 0,0010196 | 11 | 2 | 22 |
| 0,4 | −0,5 | 0,75 | 0,0034667 | 35 | 5 | 175 |

**Étape 4.** Détail de la ligne η = 0,25 : V₁ = 0,0625 × 0,01625/0,996094 ≈ 0,0010196 ; B ≥ 0,0010196/0,0001 ≈ 10,196, donc B = 11 ; un pas donne 0,3 × 0,0625 = 0,01875, encore au-dessus de 0,01, et deux pas 0,3 × 0,0625² ≈ 0,00117, en dessous : k = 2.

**Décision de l'agent.** Le job retient η = 0,25 et B = 11 : 22 gradients d'exemples au total, le moins cher des trois, en seulement 2 pas séquentiels, ce qui compte quand chaque pas attend la lecture d'un lot. L'écart-type prévu du bruit vaut √(0,0010196/11) ≈ 0,009628, soit environ 9,6 AED/sqft, sous la tolérance de 10. Le programme le vérifie par une simulation de 5 000 pas tirés au hasard : écart-type 0,0098, à 1,6 % de la prévision.

**Contre-calcul.** Le réflexe « grand pas, convergence rapide » (η = 0,4) coûte 175 gradients, 8 fois plus, parce que q = −0,5 est négatif : le facteur 1/(1 − q²) ≈ 1,333 amplifie le bruit et impose B = 35. Le réflexe inverse, B = 1 avec η = 0,25, laisse un écart-type de √0,0010196 ≈ 0,03193, soit 32 AED/sqft : sur un appartement de 1 500 sqft, l'estimation affichée tremblerait d'environ 47 900 AED d'une nuit à l'autre (illustratif), assez pour faire entrer ou sortir un bien d'une recherche à budget fixe.

**Sensibilité.** Le lot minimal est proportionnel à σ². Si le marché devient plus hétérogène et que σ augmente de 10 %, σ² est multiplié par 1,21 : pour η = 0,25, la borne passe à 10,196 × 1,21 ≈ 12,34, donc B = 13 et un coût de 2 × 13 = 26 ; pour η = 0,1, elle passe à environ 3,23, donc B = 4 et un coût de 8 × 4 = 32. La décision tient, avec une marge plus faible.

**En production.** Indicateur : l'écart-type de w sur les 30 dernières nuits (illustratif), avec une alerte au-delà de 0,01, soit 10 AED/sqft ; on contrôle aussi que les lots sont mélangés, puisqu'un lot qui ne contient qu'un type de bien est biaisé (démonstration 5). Les prix de référence viennent des transactions enregistrées auprès du DLD, et les surfaces sont en sqft. Une estimation affichée par l'agent n'est pas une évaluation officielle ; la façon de la présenter au client est à confirmer avec les règles de la RERA en vigueur.

### Cas 4 — Construction [BTP] : deux courbures, un seul pas

**Contexte.** Un groupe de construction qui mène de grands chantiers à Dubaï réentraîne chaque semaine un modèle de risque de dépassement à deux poids : θ₁ pour le montant des situations de travaux (en millions d'AED, peu normalisé), θ₂ pour la durée du lot (en mois). Près de son minimum, la perte se comporte comme une somme de deux paraboles indépendantes, de courbures a₁ = 20 et a₂ = 0,5 mesurées par le job. Un pas complet relit 2 millions de lignes de factures et prend 40 s. L'agent de suivi de chantier utilise le score pour décider quels lots montrer en premier au contrôleur de gestion. Valeurs illustratives.

**Données.**

- Courbures a₁ = 20 et a₂ = 0,5 ; écarts de départ e₀ = (1 ; 1) ; tolérance τ = 0,001 sur chaque coordonnée.
- Pas candidats : η = 0,09 ; η* = 2/(a₁ + a₂) ; η = 0,11.
- Durée d'un pas : 40 s ; fenêtre de réentraînement hebdomadaire : 2 heures.

**Calcul pas à pas.**

**Étape 1.** Chaque coordonnée suit la démonstration 3 avec sa propre courbure, et un seul η doit satisfaire les deux conditions :

$$
\eta < \min\left(\frac{2}{a_1}, \frac{2}{a_2}\right) = \min(0{,}1 \,;\, 4) = 0{,}1
$$

**Étape 2.** Avec η = 0,09 : q₁ = 1 − 1,8 = −0,8 et q₂ = 1 − 0,045 = 0,955, donc

$$
k_1 > \frac{\ln 0{,}001}{\ln 0{,}8} \approx 30{,}96, \qquad k_2 > \frac{\ln 0{,}001}{\ln 0{,}955} \approx 150{,}03
$$

soit 31 pas pour θ₁ et 151 pour θ₂. C'est la direction plate qui fixe la durée : 151 × 40 = 6 040 s, soit 100 min 40 s (≈ 100,7 min).

**Étape 3.** Le meilleur pas commun η* = 2/(a₁ + a₂) = 2/20,5 ≈ 0,097561 égalise les deux facteurs en valeur absolue ; avec le conditionnement κ = a₁/a₂ = 40 :

$$
q_1 = 1 - 20 \times 0{,}097561 \approx -0{,}95122, \qquad q_2 = 1 - 0{,}5 \times 0{,}097561 \approx 0{,}95122, \qquad \frac{\kappa - 1}{\kappa + 1} = \frac{39}{41} \approx 0{,}95122
$$

Il faut ln 0,001/ln 0,95122 ≈ 138,13, donc 139 pas, soit 139 × 40 = 5 560 s (≈ 92,7 min).

**Étape 4.** Normalisation : multiplier l'entrée « montant » par s = √(a₂/a₁) = √(0,5/20) ≈ 0,15811 ramène sa courbure à 20 × s² = 0,5 (démonstration 4). Les deux courbures valent alors 0,5, κ = 1, et η = 1/0,5 = 2 donne q = 0 sur les deux coordonnées : 1 pas, 40 s.

**Décision de l'agent.** Le job normalise l'entrée « montant » avant l'entraînement : 1 pas au lieu de 139 ou 151 sur ce modèle quadratique, et la fenêtre de 2 heures n'est plus menacée. Sans normalisation, le meilleur réglage reste η* ≈ 0,0976, avec 139 pas et 92,7 min, qui tient dans la fenêtre, mais sans marge.

**Contre-calcul.** Un pas réglé « pour aller plus vite » à η = 0,11 dépasse la frontière 0,1 : q₁ = 1 − 2,2 = −1,2, et l'écart sur θ₁ est multiplié par 1,2 en valeur absolue à chaque pas ; après 151 pas il vaut 1,2¹⁵¹ ≈ 9,0 × 10¹¹, alors que θ₂ converge (q₂ = 0,945). Le modèle exporté donne des scores absurdes, et l'agent présente au contrôleur de gestion des lots dans un ordre sans rapport avec leur risque pendant une semaine.

**Sensibilité.** La valeur de bascule est η = 2/a₁ = 0,1, et elle bouge avec l'échelle des montants. Si une partie des factures arrive TTC au lieu de HT, la TVA de 5 % multiplie l'échelle des montants par 1,05 et leur courbure par 1,05² = 1,1025 : a₁ = 22,05, et avec η = 0,09 le facteur devient q₁ = 1 − 1,9845 = −0,9845. La descente converge encore, mais θ₁ demande alors ln 0,001/ln 0,9845 ≈ 442,2, donc 443 pas, soit 17 720 s ou 4 h 55 min 20 s : la fenêtre de 2 heures est dépassée. Une variation de 5 % d'une entrée suffit à changer la décision.

**En production.** Indicateurs : le nombre de pas jusqu'à convergence à chaque réentraînement, avec une alerte au-delà de 150 (illustratif), et le rapport des gradients successifs sur chaque coordonnée. Les montants sont contrôlés HT à l'ingestion, la TVA de 5 % étant un champ séparé de la facture. Les retenues de garantie et les montants de sous-traitance, s'ils entrent un jour dans le modèle, passent par la même normalisation.

## Entraînement sur feuille A4

**Exercice 1.** L(θ) = (θ − 3)², θ₀ = 5, η = 0,25. Calculer θ₁ et θ₂.

**Exercice 2.** Même perte, quel pas fait atteindre le minimum en un seul pas ?

**Exercice 3.** L(θ) = 5θ². Pour quels η la descente converge-t-elle ?

**Exercice 4.** Démontrer que pour η = 1 et L = (θ − c)², la descente oscille sans fin.

**Exercice 5.** Dans le cas 1, combien de pas avec η = 0,05 faut-il, en partant de 0, pour que l'erreur soit sous 0,01 ? (Erreur initiale 1,99.)

**Exercice 6 (modifier une donnée).** Dans le cas 2, l'équipe normalise les montants en les divisant par 10 000 AED au lieu de 35 000. Calculer la nouvelle courbure, la frontière 2/a et le facteur q pour η = 0,5. Quelle décision prendre ?

**Exercice 7 (trouver l'erreur).** Un collègue écrit : « L(w) = (1/4) Σ (w xᵢ − yᵢ)² avec Σxᵢ² = 30 est une parabole de courbure 30 ; il faut donc η < 2/30 ≈ 0,0667, et η = 0,1 diverge. » Trouver l'erreur, la corriger, et dire ce que fait vraiment η = 0,1.

**Exercice 8 (redémontrer de mémoire).** Sans regarder, redémontrer que sur L(θ) = a(θ − c)²/2 la descente converge pour tout départ si et seulement si 0 < η < 2/a. Appliquer à L(θ) = 4(θ − 1)² : frontière et pas optimal.

## Corrigé

**Exercice 1.** Gradient en 5 : 2 × (5 − 3) = 4, donc θ₁ = 5 − 0,25 × 4 = 4. Gradient en 4 : 2 × (4 − 3) = 2, donc θ₂ = 4 − 0,25 × 2 = 3,5. Le facteur vaut q = 1 − 0,25 × 2 = 0,5 : l'écart passe de 2 à 1 puis à 0,5.

**Exercice 2.** Il faut q = 1 − 2η = 0, donc η = 0,5, c'est-à-dire η = 1/a avec a = 2. Contrôle : θ₁ = 5 − 0,5 × 4 = 3.

**Exercice 3.** L = 5θ² s'écrit 10θ²/2, donc a = 10 et la descente converge si et seulement si 0 < η < 2/10 = 0,2.

**Exercice 4.** a = 2, donc q = 1 − 1 × 2 = −1 et eₜ = (−1)ᵗ e₀ : l'écart change de signe à chaque pas sans diminuer. Depuis θ₀ = 5 avec c = 3 : 1, 5, 1, 5…

**Exercice 5.** On cherche k tel que 1,99 × 0,25ᵏ < 0,01, soit 0,25ᵏ < 0,01/1,99 ≈ 0,0050251. k = 3 donne 0,015625, trop grand ; k = 4 donne 0,00390625 : 4 pas, avec une erreur finale 1,99 × 0,00390625 ≈ 0,00777.

**Exercice 6.** x/10 000 = 0,8 ; 1,5 ; 2,2 ; 3,5, donc Σx² = 0,64 + 2,25 + 4,84 + 12,25 = 19,98, a = 2 × 19,98/4 = 9,99, 2/a ≈ 0,2002 et q = 1 − 0,5 × 9,99 = −3,995 : divergence. Décision : soit normaliser par 35 000 comme dans le cas 2 (q′ ≈ 0,59224), soit garder cette échelle avec η < 0,2002, par exemple η = 0,1, qui donne q = 1 − 0,999 = 0,001.

**Exercice 7.** La courbure est le coefficient a de a(w − w*)²/2, c'est-à-dire la dérivée seconde de L, qui vaut (2/n)Σxᵢ² = 2 × 30/4 = 15, et non Σxᵢ² = 30 : on a oublié le facteur 2/n. La bonne frontière est 2/15 ≈ 0,13333 ; η = 0,1 donne q = 1 − 1,5 = −0,5, une oscillation amortie qui converge à 0,01 près en 8 pas (cas 1, étape 5).

**Exercice 8.** On refait les étapes 1 à 4 de la démonstration 3 : gradient a eₜ, écart multiplié par q = 1 − ηa, eₜ = qᵗe₀, convergence si et seulement si |q| < 1, soit 0 < η < 2/a. Pour 4(θ − 1)² = 8(θ − 1)²/2 : a = 8 et c = 1, convergence si et seulement si 0 < η < 0,25, pas optimal η = 1/8 = 0,125.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`descente(grad, theta, eta, pas)`** — Cette fonction est le randonneur dans le brouillard qui, à chaque arrêt, tâte la pente sous ses pieds et fait un pas vers le bas : elle reçoit la fonction qui donne le gradient, le point de départ θ, le pas η et le nombre de pas, refuse par une `ValueError` un η nul ou négatif ou un nombre de pas négatif, puis répète θ ← θ − η ∇L(θ) en notant chaque position. Elle renvoie la trajectoire θ₁ … θₙ, sans le point de départ : sur la parabole (θ − 3)² depuis 0 avec η = 0,1, elle donne 0,6, 1,08, 1,464, 1,7712 et 2,01696, l'écart à 3 étant multiplié par 0,8 à chaque pas.

**`courbure(x)`** — On la voit en géomètre qui mesure à quel point la vallée est encaissée, ce qui fixe la longueur de pas tolérable : elle reçoit la liste des entrées x d'une régression y ≈ w x, refuse une liste vide par une `ValueError`, et renvoie a = (2/n) Σ x², la dérivée seconde de la perte quadratique moyenne de la démonstration 4. Pour les entrées 1, 2, 3 et 4, elle vaut 15, donc tout pas au-delà de 2/15 ≈ 0,13333 diverge ; multipliées par 1 000, les mêmes entrées donnent 1,5 × 10⁷.

**`minimum(x, y)`** — Cette fonction est le notaire qui connaît d'avance l'adresse du fond de la vallée : elle reçoit les entrées et les sorties de la régression, calcule Σ x², renvoie `None` s'il est nul, puisque toutes les entrées sont alors nulles et qu'aucune pente ne se dégage, et sinon renvoie w* = Σ xy / Σ x². Elle donne 1,99 pour les mesures de latence du cas 1 et 1,9 pour les prix du cas 3, et ces valeurs servent de cible pour mesurer l'écart de chaque trajectoire.

**`pas_pour_tolerance(e0, q, tau)`** — Celle-ci compte combien de pas il faut à un écart qui se contracte d'un facteur q à chaque pas pour passer sous une tolérance τ : elle reçoit l'écart initial, le facteur et la tolérance, refuse un τ nul ou négatif par une `ValueError`, renvoie 0 si l'écart est déjà assez petit, `None` si |q| ≥ 1, puisque l'écart ne diminue jamais, et 1 si q vaut 0. Sinon, elle estime k par les logarithmes, puis l'ajuste par deux petites boucles pour obtenir le plus petit entier tel que |e₀| × |q|ᵏ < τ, et le renvoie : 26 pas pour un écart de 3 avec q = 0,8 et τ = 0,01.

**`bruit_plancher(eta, a, sigma2, B)`** — Cette fonction raconte le tremblement qui ne s'éteint jamais quand chaque pas suit un gradient bruité : elle reçoit le pas η, la courbure a, la variance σ² du gradient d'un exemple et la taille de lot B, refuse un lot inférieur à 1 ou une variance négative par une `ValueError`, calcule q = 1 − ηa, renvoie `None` si |q| ≥ 1, et sinon renvoie la variance limite η²σ²/(B(1 − q²)) de la démonstration 6. Avec η = 0,1, a = 5, σ² = 1 et B = 4, elle prédit 0,0033333, que la simulation de `main` retrouve à 1,1 % près.

**`lot_minimal(eta, a, sigma2, tau)`** — On l'imagine en chef d'équipe qui décide combien d'exemples tirer à chaque pas pour que le tremblement reste sous un seuil : elle reçoit le pas, la courbure, la variance du gradient et la tolérance τ, calcule le bruit plancher d'un lot d'un seul exemple, renvoie `None` si la descente diverge, et sinon renvoie le plus petit lot entier B, au moins 1, tel que ce bruit divisé par B reste sous τ². Dans le cas 3, elle demande 3, 11 et 35 exemples pour des pas de 0,1, 0,25 et 0,4.

**`cas_1_latence_public()`** — Cette fonction met en scène l'équipe d'exploitation d'un service public qui veut prédire la latence d'une réponse à partir de sa taille, dans un petit job limité à 10 pas : elle ne reçoit rien, prend quatre mesures, calcule la courbure 15 et le minimum 1,99 seconde par millier de tokens, puis essaie trois pas. Avec η = 0,05, le facteur vaut 0,25 et 4 pas suffisent pour une précision de 0,01 ; avec η = 0,1, il vaut −0,5 et il en faut 8 ; avec η = 0,15, il vaut −1,25 et la descente diverge jusqu'à w = −16,5433 au bout de 10 pas, soit une latence absurde de −99,26 s pour 6 000 tokens. Elle calcule aussi la marge de 2,67 et le facteur d'échelle de bascule 1,633, puis renvoie ces résultats.

**`cas_2_montants_assur()`** — On y suit un assureur dont le modèle de tri reçoit soudain des montants réclamés en dirhams bruts au lieu de montants normalisés, avec le même pas de 0,5 : la fonction ne reçoit rien, calcule une courbure de 9,99 × 10⁸, un facteur d'environ −4,995 × 10⁸ et un premier pas qui propulse le poids à 11 462,5, puis montre que le poids devient infini au 36ᵉ pas. Normalisés par 35 000, les montants donnent une courbure de 0,81551, un facteur de 0,59224 et un minimum de 0,80318 atteint à 0,001 près en 13 pas ; elle vérifie la marge sur la racine carrée de la moyenne des carrés, 0,63856 contre la bascule √2, montre qu'un sinistre de 120 000 AED suffit à faire diverger, et renvoie le tout, dont le coût de 90 000 AED d'une journée envoyée en revue.

**`cas_3_minilot_immo()`** — Cette fonction raconte une agence qui réestime chaque nuit le prix au sqft par descente stochastique et cherche le couple pas et taille de lot qui atteint 10 AED/sqft de précision au moindre calcul : elle ne reçoit rien, calcule la courbure 3,75, le minimum 1,9 et la variance 0,01625 des gradients au minimum, puis, pour des pas de 0,1, 0,25 et 0,4, le lot minimal, le nombre de pas et le coût, 8 × 3 = 24, 2 × 11 = 22 et 5 × 35 = 175 gradients. Elle retient η = 0,25 avec B = 11, simule 5 000 pas avec la graine 8 pour retrouver un écart-type de 0,0098 contre 0,009628 prévus, calcule l'écart-type de 0,03193 d'un lot unique et les lots nécessaires si le bruit croît de 21 %, puis renvoie ces résultats.

**`cas_4_deux_courbures_btp()`** — Ici, un groupe de construction réentraîne un modèle de risque à deux poids dont les courbures valent 20 et 0,5, chaque pas complet prenant 40 secondes : la fonction ne reçoit rien et montre qu'un seul pas commun doit rester sous 2/20 = 0,1, qu'avec η = 0,09 le premier poids converge en 31 pas mais le second en 151, soit 6 040 s, et que le pas optimal 2/20,5 ≈ 0,097561 en demande encore 139. En normalisant le premier poids par le facteur 0,15811, les deux courbures deviennent égales et un seul pas suffit ; elle vérifie qu'η = 0,11 diverge et que des factures toutes taxes comprises, multipliées par 1,05, portent la courbure à 22,05 et le travail à 443 pas, soit 17 720 s, puis renvoie ces nombres.

**`main()`** — C'est le chef d'orchestre de la fiche : il suit d'abord la descente sur la parabole (θ − 3)² et vérifie ses gradients et ses écarts, puis rejoue les démonstrations 1 à 6, la baisse de la perte de 9 à 5,76, la direction de plus forte pente de norme 6,32456, les régimes de convergence, la courbure 15 de la régression, le gradient sans biais d'un mini-lot, simulé avec la graine 3, et le bruit plancher, simulé avec la graine 6. Il joue ensuite les quatre cas et le corrigé des exercices, puis s'assure qu'un pas nul est refusé ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

**`grad_w(w)`** — Cette fonction interne vit dans `main`, au milieu de la démonstration 4, comme la règle graduée qu'on sort pour une seule mesure : elle reçoit un poids w et renvoie le gradient (2/n) Σ (w x − y) x de la perte de régression sur les quatre mesures de latence 1, 2, 3, 4 et 2,1, 3,9, 6,2, 7,8. `main` vérifie qu'il vaut exactement 15w − 29,85, donc une courbure de 15 et un minimum en 1,99, et qu'en w = 1 il vaut −14,85, la moyenne exacte que les gradients de mini-lots tirés au hasard approchent à −14,907.

```python
"""Démonstration 08 — descente de gradient : baisse locale, direction, facteur 1 − ηa, courbure d'une régression, mini-lot, bruit plancher, quatre cas aux Émirats."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def descente(grad, theta, eta, pas):
    """θ ← θ − η ∇L(θ), répété `pas` fois ; renvoie la trajectoire θ₁ … θₙ."""
    if eta <= 0 or pas < 0:
        raise ValueError("il faut eta > 0 et pas >= 0")
    trajet = []
    for _ in range(pas):
        theta = theta - eta * grad(theta)
        trajet.append(theta)
    return trajet


def courbure(x):
    """a = (2/n) Σ x² : courbure de L(w) = (1/n) Σ (w x − y)² (démonstration 4)."""
    if not x:
        raise ValueError("il faut au moins un point")
    return 2 * sum(v * v for v in x) / len(x)


def minimum(x, y):
    """w* = Σ x y / Σ x² ; None si toutes les entrées sont nulles (pas de dénominateur)."""
    sxx = sum(v * v for v in x)
    if sxx == 0:
        return None
    return sum(a * b for a, b in zip(x, y)) / sxx


def pas_pour_tolerance(e0, q, tau):
    """Plus petit k tel que |e0| × |q|^k < tau (démonstration 3) ; None si |q| >= 1."""
    if tau <= 0:
        raise ValueError("tau doit être > 0")
    if abs(e0) < tau:
        return 0
    if abs(q) >= 1:
        return None
    if q == 0:
        return 1
    k = max(0, math.ceil(math.log(tau / abs(e0)) / math.log(abs(q))))
    while abs(e0) * abs(q) ** k >= tau:
        k += 1
    while k > 0 and abs(e0) * abs(q) ** (k - 1) < tau:
        k -= 1
    return k


def bruit_plancher(eta, a, sigma2, B):
    """V∞ = η² σ² / (B (1 − q²)) avec q = 1 − ηa (démonstration 6) ; None si |q| >= 1."""
    if B < 1 or sigma2 < 0:
        raise ValueError("il faut B >= 1 et sigma2 >= 0")
    q = 1 - eta * a
    if abs(q) >= 1:
        return None
    return eta * eta * sigma2 / (B * (1 - q * q))


def lot_minimal(eta, a, sigma2, tau):
    """Plus petit B entier tel que V∞ <= τ² (démonstration 6) ; None si |q| >= 1."""
    v1 = bruit_plancher(eta, a, sigma2, 1)
    if v1 is None:
        return None
    return max(1, math.ceil(v1 / (tau * tau) - 1e-9))


def cas_1_latence_public():
    """Services publics : latence y (s) en fonction de x (milliers de tokens), y ≈ w x."""
    x, y = [1, 2, 3, 4], [2.1, 3.9, 6.2, 7.8]
    a, w_star = courbure(x), minimum(x, y)
    res = {"sxx": sum(v * v for v in x), "sxy": sum(p * r for p, r in zip(x, y)), "a": a, "w_star": w_star}
    for eta in (0.05, 0.1, 0.15):
        traj = descente(lambda w: a * (w - w_star), 0.0, eta, 10)
        res[eta] = {"q": 1 - a * eta, "traj4": traj[:4], "w10": traj[-1],
                    "k": pas_pour_tolerance(-w_star, 1 - a * eta, 0.01)}
    res["marge"] = (2 / 0.05) / a
    res["s_bascule"] = math.sqrt(2 / (a * 0.05))
    res["k_09"] = pas_pour_tolerance(-w_star, 0.9, 0.01)
    print(f"Cas 1 [PUBLIC] : a = {a:g}, w* = {w_star:.2f}, 2/a = {2 / a:.5f} ; pas jusqu'à 0,01 :"
          f" η = 0.05 → {res[0.05]['k']}, η = 0.1 → {res[0.1]['k']}, η = 0.15 → {res[0.15]['k']}")
    print(f"  η = 0.05 : {[round(w, 4) for w in res[0.05]['traj4']]} ; η = 0.15 après 10 pas : w = {res[0.15]['w10']:.4f}"
          f" → {6 * res[0.15]['w10']:.2f} s pour 6 000 tokens")
    return res


def cas_2_montants_assur():
    """Assurance : montant réclamé en AED bruts puis normalisé, même pas η = 0.5."""
    x, y = [8_000, 15_000, 22_000, 35_000], [0.2, 0.35, 0.5, 0.8]
    sxx, sxy = sum(v * v for v in x), sum(p * r for p, r in zip(x, y))
    a, w_star = courbure(x), minimum(x, y)
    q = 1 - 0.5 * a
    w1 = descente(lambda w: (2 / len(x)) * (w * sxx - sxy), 0.0, 0.5, 1)[0]
    e3 = -w_star * q ** 3
    w, pas_inf = 0.0, 0
    while math.isfinite(w):
        w = w - 0.5 * (2 / len(x)) * (w * sxx - sxy)
        pas_inf += 1
    xn = [v / 35_000 for v in x]
    an, wn = courbure(xn), minimum(xn, y)
    qn = 1 - 0.5 * an
    rms = math.sqrt(sum(v * v for v in xn) / len(xn))
    x5 = xn + [120_000 / 35_000]
    a5 = courbure(x5)
    res = {"sxx": sxx, "sxy": sxy, "a": a, "borne": 2 / a, "q": q, "grad0": -(2 / len(x)) * sxy, "w1": w1,
           "w_star": w_star, "e3": e3, "pas_inf": pas_inf, "xn": xn, "sxxn": sum(v * v for v in xn),
           "sxyn": sum(p * r for p, r in zip(xn, y)), "an": an, "bornen": 2 / an, "qn": qn, "wn": wn,
           "k": pas_pour_tolerance(-wn, qn, 0.001), "rms": rms, "rms_max": math.sqrt(2), "marge": math.sqrt(2) / rms,
           "x5": x5[-1], "sxx5": sum(v * v for v in x5), "moy5": sum(v * v for v in x5) / 5, "a5": a5,
           "q5": 1 - 0.5 * a5, "cout_jour": 2_000 * 45}
    print(f"Cas 2 [ASSUR] : AED bruts a = {a:.3e}, q = {q:.4e}, w1 = {w1:_} ; normalisé a = {an:.5f},"
          f" q = {qn:.5f}, w* = {wn:.5f}, {res['k']} pas")
    print(f"  RMS {rms:.5f} (bascule {math.sqrt(2):.5f}) ; avec 120 000 AED : a = {a5:.5f}, q = {res['q5']:.5f}"
          f" ; poids infini au pas {pas_inf}")
    return res


def cas_3_minilot_immo():
    """Immobilier : choix du couple (η, B) pour une précision de 10 AED/sqft au moindre coût."""
    x, y = [0.5, 1.0, 1.5, 2.0], [1.0, 1.8, 2.9, 3.8]
    a, w_star = courbure(x), minimum(x, y)
    g_star = [2 * (w_star * p - r) * p for p, r in zip(x, y)]
    sigma2 = sum(g * g for g in g_star) / len(g_star)
    tau, e0 = 0.01, 1.6 - w_star
    options = {}
    for eta in (0.1, 0.25, 0.4):
        q = 1 - eta * a
        B = lot_minimal(eta, a, sigma2, tau)
        k = pas_pour_tolerance(e0, q, tau)
        options[eta] = {"q": q, "1-q2": 1 - q * q, "V1": bruit_plancher(eta, a, sigma2, 1), "B": B, "k": k,
                        "cout": k * B, "ecart_type": math.sqrt(bruit_plancher(eta, a, sigma2, B))}
    choix = min(options, key=lambda e: options[e]["cout"])
    rng = random.Random(8)
    B, eta, w, valeurs = options[choix]["B"], choix, w_star, []
    pente = [2 * p * p for p in x]                      # gradient d'un exemple : 2x² w − 2xy
    decal = [2 * p * r for p, r in zip(x, y)]
    for t in range(5_000):
        s_pente = s_decal = 0.0
        for _ in range(B):
            i = rng.randrange(len(x))
            s_pente, s_decal = s_pente + pente[i], s_decal + decal[i]
        w -= eta * (w * s_pente - s_decal) / B
        if t >= 100:
            valeurs.append(w)
    moy = sum(valeurs) / len(valeurs)
    sim = math.sqrt(sum((v - moy) ** 2 for v in valeurs) / len(valeurs))
    b10 = {e: lot_minimal(e, a, 1.21 * sigma2, tau) for e in (0.1, 0.25)}
    res = {"sxx": sum(v * v for v in x), "a": a, "w_star": w_star, "sxy": sum(p * r for p, r in zip(x, y)),
           "g_star": g_star, "sigma2": sigma2, "options": options, "choix": choix, "sim": sim,
           "ecart_B1": math.sqrt(options[0.25]["V1"]), "b10": b10,
           "b10_brut": {e: bruit_plancher(e, a, 1.21 * sigma2, 1) / tau ** 2 for e in (0.1, 0.25)}}
    print(f"Cas 3 [IMMO] : a = {a:g}, w* = {w_star:g}, σ² = {sigma2:.5f} ; coût k × B :"
          + "".join(f" η = {e} → {o['k']} × {o['B']} = {o['cout']} ;" for e, o in options.items()))
    print(f"  choix η = {choix}, B = {B} : écart-type prévu {options[choix]['ecart_type']:.6f}, simulé {sim:.4f}"
          f" ({100 * (sim / options[choix]['ecart_type'] - 1):+.1f} %)")
    return res


def cas_4_deux_courbures_btp():
    """BTP : deux poids de courbures 20 et 0.5, un seul pas η pour les deux."""
    a1, a2, tau = 20.0, 0.5, 0.001
    res = {"borne": min(2 / a1, 2 / a2), "eta_opt": 2 / (a1 + a2), "kappa": a1 / a2}
    for nom, eta in (("0.09", 0.09), ("opt", 2 / (a1 + a2)), ("0.11", 0.11)):
        q1, q2 = 1 - eta * a1, 1 - eta * a2
        k1, k2 = pas_pour_tolerance(1.0, q1, tau), pas_pour_tolerance(1.0, q2, tau)
        res[nom] = {"q1": q1, "q2": q2, "k1": k1, "k2": k2,
                    "k": None if k1 is None or k2 is None else max(k1, k2)}
    res["s"] = math.sqrt(a2 / a1)
    res["a1_norm"] = a1 * res["s"] ** 2
    res["k_norm"] = pas_pour_tolerance(1.0, 1 - (1 / a2) * a2, tau)
    res["e151_011"] = 1.2 ** 151
    a1_tva = a1 * 1.05 ** 2
    res["a1_tva"], res["q1_tva"] = a1_tva, 1 - 0.09 * a1_tva
    res["k_tva"] = pas_pour_tolerance(1.0, res["q1_tva"], tau)
    print(f"Cas 4 [BTP] : η = 0.09 → {res['0.09']['k1']} et {res['0.09']['k2']} pas ; η* = {res['eta_opt']:.6f}"
          f" → {res['opt']['k']} pas ; normalisé → {res['k_norm']} pas ; η = 0.11 diverge")
    print(f"  factures TTC (×1.05) : a1 = {a1_tva:.2f}, q1 = {res['q1_tva']:.4f}, {res['k_tva']} pas = {res['k_tva'] * 40} s")
    return res


def main() -> None:
    t = descente(lambda th: 2 * (th - 3), 0.0, 0.1, 5)
    print(f"parabole : {[round(x, 5) for x in t]}")
    assert [round(x, 5) for x in t] == [0.6, 1.08, 1.464, 1.7712, 2.01696]
    assert all(math.isclose(3 - b, 0.8 * (3 - a)) for a, b in zip([0.0] + t, t))      # démonstration 3
    grads = [2 * (th - 3) for th in [0.0] + t[:4]]
    assert [round(g, 5) for g in grads] == [-6, -4.8, -3.84, -3.072, -2.4576]
    assert [round(0.1 * g, 5) for g in grads] == [-0.6, -0.48, -0.384, -0.3072, -0.24576]
    assert [round(th - 3, 5) for th in t] == [-2.4, -1.92, -1.536, -1.2288, -0.98304]
    assert round(0.8 ** 5, 5) == 0.32768
    assert round(3 * 0.8 ** 5, 5) == 0.98304 and round((t[4] - 3) ** 2, 5) == 0.96637
    assert math.isclose((t[4] - 3) ** 2, 9 * 0.64 ** 5)

    # démonstration 1 : baisse au premier ordre et égalité exacte
    L = lambda th: (th - 3) ** 2
    assert L(0.0) == 9 and math.isclose(L(0.6), 5.76) and math.isclose(9 - 0.1 * 36, 5.4)
    assert math.isclose(9 - 0.1 * 36 * (1 - 2 * 0.1 / 2), 5.76) and math.isclose(9 - 3.6 * 0.9, 9 - 3.24)
    assert math.isclose(L(0 + 1.1 * 6), 12.96) and math.isclose(9 - 1.1 * 36 * (1 - 1.1), 12.96)
    for th in (0.0, 1.5, 7.0):
        assert L(th - 0.01 * 2 * (th - 3)) < L(th)
    print(f"démonstration 1 : L(0) = 9 ; L(0.6) = {L(0.6):.2f} (premier ordre {9 - 0.1 * 36:.1f}) ;"
          f" η = 1.1 : L(6.6) = {L(6.6):.2f} > 9")
    # démonstration 2 : la pente la plus négative est −‖∇L‖
    g2 = (2.0, 6.0)
    n2 = math.hypot(*g2)
    pentes = [g2[0] * u + g2[1] * v for u, v in ((-1, 0), (0, -1), (-0.6, -0.8), (-g2[0] / n2, -g2[1] / n2))]
    assert round(n2, 5) == 6.32456 and [round(p, 5) for p in pentes] == [-2, -6, -6, -6.32456]
    assert (round(g2[0] / n2, 5), round(g2[1] / n2, 5)) == (0.31623, 0.94868) and min(pentes) == pentes[3]
    print(f"démonstration 2 : pentes {[round(p, 5) for p in pentes]} ; la plus raide suit −∇L")
    # démonstration 3 : régimes et nombre de pas
    assert [round(v, 3) for v in descente(lambda th: 2 * (th - 3), 0.0, 0.9, 2)] == [5.4, 1.08]
    assert [round(v, 3) for v in descente(lambda th: 2 * (th - 3), 0.0, 1.1, 3)] == [6.6, -1.32, 8.184]
    assert round(math.log(0.01 / 3), 5) == -5.70378 and round(math.log(0.8), 5) == -0.22314
    assert round(math.log(0.01 / 3) / math.log(0.8), 2) == 25.56 and pas_pour_tolerance(-3, 0.8, 0.01) == 26
    assert round(3 * 0.8 ** 25, 5) == 0.01133 and round(3 * 0.8 ** 26, 5) == 0.00907
    assert math.isclose(grads[1] / grads[0], 0.8)
    print(f"démonstration 3 : η = 0.9 → {[round(v, 3) for v in descente(lambda th: 2 * (th - 3), 0.0, 0.9, 2)]} ;"
          f" η = 1.1 → {[round(v, 3) for v in descente(lambda th: 2 * (th - 3), 0.0, 1.1, 3)]} ;"
          f" {pas_pour_tolerance(-3, 0.8, 0.01)} pas pour 0,01")
    # démonstration 4 : courbure d'une régression et changement d'échelle
    x, y = [1, 2, 3, 4], [2.1, 3.9, 6.2, 7.8]
    sxx, sxy = sum(a * a for a in x), sum(a * b for a, b in zip(x, y))
    w_star = sxy / sxx

    def grad_w(w):
        return 2 / len(x) * sum((w * a - b) * a for a, b in zip(x, y))

    assert sxx == 30 and math.isclose(sxy, 59.7) and math.isclose(w_star, 1.99) and courbure(x) == 15
    assert all(math.isclose(grad_w(w), 15 * w - 29.85) for w in (0, 1, 2.5))
    assert math.isclose(courbure([1000 * v for v in x]), 1.5e7) and round(2 / 1.5e7, 10) == 1.333e-7
    assert round(2 / courbure(x), 5) == 0.13333 and minimum([0, 0], [1, 2]) is None
    print(f"démonstration 4 : a = {courbure(x):g}, w* = {w_star:.2f} ; tokens un par un : a = {courbure([1000 * v for v in x]):.1e}")
    # démonstration 5 : gradient d'un mini-lot, sans biais, variance σ²/B
    gi = [2 * (1.0 * a - b) * a for a, b in zip(x, y)]
    moy = sum(gi) / len(gi)
    var = sum((g - moy) ** 2 for g in gi) / len(gi)
    assert [round(1.0 * a - b, 5) for a, b in zip(x, y)] == [-1.1, -1.9, -3.2, -3.8]
    assert [round(g, 5) for g in gi] == [-2.2, -7.6, -19.2, -30.4] and math.isclose(moy, grad_w(1.0))
    assert math.isclose(sum(gi), -59.4) and math.isclose(moy, -14.85)
    assert [round(g - moy, 5) for g in gi] == [12.65, 7.25, -4.35, -15.55]
    assert [round((g - moy) ** 2, 4) for g in gi] == [160.0225, 52.5625, 18.9225, 241.8025]
    assert math.isclose(sum((g - moy) ** 2 for g in gi), 473.31)
    assert round(var, 4) == 118.3275 and round(math.sqrt(var), 4) == 10.8778 and round(math.sqrt(var) / 2, 4) == 5.4389
    assert round(sum(gi[:3]) / 3, 4) == -9.6667 and round(1 - 9.6667 / 14.85, 2) == 0.35  # lot biaisé
    rng = random.Random(3)
    lots = []
    for _ in range(20_000):
        i = rng.randrange(4)
        lots.append(2 * (1.0 * x[i] - y[i]) * x[i])
    print(f"gradient moyen des mini-lots en w = 1 : {sum(lots) / len(lots):.3f} ; exact {grad_w(1.0):.3f}")
    assert round(sum(lots) / len(lots), 3) == -14.907 and abs(sum(lots) / len(lots) - grad_w(1.0)) < 0.1
    # démonstration 6 : bruit plancher du modèle e ← q e − η ξ
    v_th = bruit_plancher(0.1, 5.0, 1.0, 4)
    rng6, e, somme, somme2, n6 = random.Random(6), 0.0, 0.0, 0.0, 0
    for k in range(20_000):
        e = 0.5 * e - 0.1 * rng6.gauss(0.0, 0.5)
        if k >= 100:
            somme, somme2, n6 = somme + e, somme2 + e * e, n6 + 1
    v_sim = somme2 / n6 - (somme / n6) ** 2
    print(f"bruit plancher (q = 0.5, η = 0.1, σ² = 1, B = 4) : théorie {v_th:.7f}, simulation {v_sim:.7f}")
    assert round(v_th, 7) == 0.0033333 and round(v_sim, 7) == 0.0033716 and round(100 * (v_sim / v_th - 1), 1) == 1.1
    assert bruit_plancher(0.1, 22.0, 1.0, 4) is None and math.isclose(1 - 0.1 * 22.0, -1.2)
    assert math.isclose((1 - 0.1 * 22.0) ** 2, 1.44) and 1 - 0.1 * 5.0 == 0.5

    c1 = cas_1_latence_public()
    assert c1["sxx"] == 30 and math.isclose(c1["sxy"], 59.7) and c1["a"] == 15 and math.isclose(c1["w_star"], 1.99)
    assert [round(c1[e]["q"], 4) for e in (0.05, 0.1, 0.15)] == [0.25, -0.5, -1.25]
    assert [round(w, 4) for w in c1[0.05]["traj4"]] == [1.4925, 1.8656, 1.9589, 1.9822]
    assert [round(w, 4) for w in c1[0.1]["traj4"]] == [2.985, 1.4925, 2.2388, 1.8656]
    assert [round(w, 4) for w in c1[0.15]["traj4"]] == [4.4775, -1.1194, 5.8767, -2.8684]
    assert round(math.log(0.01 / 1.99), 5) == -5.2933 and round(math.log(0.25), 5) == -1.38629
    assert round(math.log(0.5), 5) == -0.69315
    assert round(math.log(0.01 / 1.99) / math.log(0.25), 3) == 3.818
    assert round(math.log(0.01 / 1.99) / math.log(0.5), 3) == 7.637
    assert (c1[0.05]["k"], c1[0.1]["k"], c1[0.15]["k"]) == (4, 8, None) and c1["k_09"] == 51
    assert round(c1["marge"], 2) == 2.67 and 2 / 0.05 == 40
    assert round(6 * c1[0.05]["traj4"][3], 2) == 11.89 and round(6 * 1.99, 2) == 11.94
    assert round(c1[0.15]["w10"], 4) == -16.5433 and round(6 * c1[0.15]["w10"], 2) == -99.26
    assert round(2 / 30, 4) == 0.0667 and round(c1["s_bascule"], 3) == 1.633
    assert courbure([1.5 * v for v in [1, 2, 3, 4]]) == 33.75 and math.isclose(1 - 33.75 * 0.05, -0.6875)
    assert courbure([2 * v for v in [1, 2, 3, 4]]) == 60 and math.isclose(1 - 60 * 0.05, -2)

    c2 = cas_2_montants_assur()
    assert c2["sxx"] == 1_998_000_000 and c2["a"] == 9.99e8 and round(c2["borne"] * 1e9, 3) == 2.002
    assert [v * v for v in (8_000, 15_000, 22_000, 35_000)] == [64_000_000, 225_000_000, 484_000_000, 1_225_000_000]
    assert c2["q"] == -499_499_999 and round(c2["q"] / 1e8, 3) == -4.995
    assert [round(p * r) for p, r in zip((8_000, 15_000, 22_000, 35_000), (0.2, 0.35, 0.5, 0.8))] == [1_600, 5_250, 11_000, 28_000]
    assert c2["sxy"] == 45_850 and c2["grad0"] == -22_925 and c2["w1"] == 11_462.5
    assert round(c2["w_star"] * 1e5, 4) == 2.2948 and round(c2["e3"] / 1e21, 2) == 2.86
    assert [round(v, 5) for v in c2["xn"]] == [0.22857, 0.42857, 0.62857, 1.0]
    assert round(c2["sxxn"], 5) == 1.63102 and round(c2["an"], 5) == 0.81551 and round(c2["qn"], 5) == 0.59224
    assert math.isclose(c2["sxyn"], 1.31) and round(c2["wn"], 5) == 0.80318 and round(c2["bornen"], 5) == 2.45245
    assert round(math.log(0.001 / c2["wn"]) / math.log(c2["qn"]), 2) == 12.77 and c2["k"] == 13
    assert round(c2["rms"], 5) == 0.63856 and round(c2["rms_max"], 5) == 1.41421 and round(c2["marge"], 2) == 2.21
    assert round(c2["x5"], 5) == 3.42857 and round(c2["sxx5"], 5) == 13.38612 and round(c2["moy5"], 5) == 2.67722
    assert round(c2["a5"], 5) == 5.35445 and round(c2["q5"], 5) == -1.67722 and c2["cout_jour"] == 90_000
    assert c2["pas_inf"] == 36 and 2 / 0.5 == 4

    c3 = cas_3_minilot_immo()
    o = c3["options"]
    assert c3["sxx"] == 7.5 and c3["a"] == 3.75 and math.isclose(c3["sxy"], 14.25) and math.isclose(c3["w_star"], 1.9)
    assert [round(1.9 * p - r, 5) for p, r in zip([0.5, 1.0, 1.5, 2.0], [1.0, 1.8, 2.9, 3.8])] == [-0.05, 0.1, -0.05, 0.0]
    assert [round(g, 5) for g in c3["g_star"]] == [-0.05, 0.2, -0.15, 0.0] and round(c3["sigma2"], 5) == 0.01625
    assert [round(g * g, 4) for g in c3["g_star"]] == [0.0025, 0.04, 0.0225, 0.0] and round(1.6 - 1.9, 5) == -0.3
    assert [round(o[e]["q"], 4) for e in (0.1, 0.25, 0.4)] == [0.625, 0.0625, -0.5]
    assert [round(o[e]["1-q2"], 6) for e in (0.1, 0.25, 0.4)] == [0.609375, 0.996094, 0.75]
    assert [round(o[e]["V1"], 7) for e in (0.1, 0.25, 0.4)] == [0.0002667, 0.0010196, 0.0034667]
    assert [(o[e]["B"], o[e]["k"], o[e]["cout"]) for e in (0.1, 0.25, 0.4)] == [(3, 8, 24), (11, 2, 22), (35, 5, 175)]
    assert c3["choix"] == 0.25 and round(o[0.25]["ecart_type"], 6) == 0.009628 and round(c3["sim"], 4) == 0.0098
    assert round(100 * (c3["sim"] / o[0.25]["ecart_type"] - 1), 1) == 1.6 and round(o[0.25]["V1"] / 0.01 ** 2, 3) == 10.196
    assert round(0.3 * 0.0625, 5) == 0.01875 and round(0.3 * 0.0625 ** 2, 5) == 0.00117
    assert round(c3["ecart_B1"], 5) == 0.03193 and round(c3["ecart_B1"] * 1_500 * 1_000, -2) == 47_900
    assert round(175 / 22) == 8 and round(1 / 0.75, 3) == 1.333 and round(1 - 0.25 * 3.75, 4) == 0.0625
    assert round(c3["b10_brut"][0.25], 2) == 12.34 and round(c3["b10_brut"][0.1], 2) == 3.23
    assert c3["b10"] == {0.1: 4, 0.25: 13} and 2 * 13 == 26 and 8 * 4 == 32
    assert round(1_000 * o[0.25]["ecart_type"], 1) == 9.6 and round(1_000 * c3["ecart_B1"]) == 32

    c4 = cas_4_deux_courbures_btp()
    assert c4["borne"] == 0.1 and round(c4["eta_opt"], 6) == 0.097561 and c4["kappa"] == 40 and 2 / 0.5 == 4
    assert (round(c4["0.09"]["q1"], 4), round(c4["0.09"]["q2"], 4)) == (-0.8, 0.955)
    assert round(math.log(0.001) / math.log(0.8), 2) == 30.96 and round(math.log(0.001) / math.log(0.955), 2) == 150.03
    assert (c4["0.09"]["k1"], c4["0.09"]["k2"], c4["0.09"]["k"]) == (31, 151, 151) and 151 * 40 == 6_040
    assert round(6_040 / 60, 1) == 100.7 and divmod(6_040, 60) == (100, 40)
    assert (round(c4["opt"]["q1"], 5), round(c4["opt"]["q2"], 5), round(39 / 41, 5)) == (-0.95122, 0.95122, 0.95122)
    assert round(math.log(0.001) / math.log(39 / 41), 2) == 138.13 and c4["opt"]["k"] == 139 and 139 * 40 == 5_560
    assert round(5_560 / 60, 1) == 92.7 and round(c4["eta_opt"], 4) == 0.0976
    assert round(c4["s"], 5) == 0.15811 and math.isclose(c4["a1_norm"], 0.5) and c4["k_norm"] == 1
    assert c4["0.11"]["k1"] is None and round(c4["0.11"]["q1"], 4) == -1.2 and round(c4["0.11"]["q2"], 4) == 0.945
    assert round(c4["e151_011"] / 1e11, 1) == 9.0
    assert round(c4["a1_tva"], 2) == 22.05 and round(c4["q1_tva"], 4) == -0.9845 and round(1.05 ** 2, 4) == 1.1025
    assert round(math.log(0.001) / math.log(0.9845), 1) == 442.2 and c4["k_tva"] == 443 and 443 * 40 == 17_720
    assert divmod(17_720, 3_600) == (4, 3_320) and divmod(3_320, 60) == (55, 20)
    assert math.isclose(0.09 * 22.05, 1.9845) and math.isclose(20 * c4["s"] ** 2, 0.5) and 1 / 0.5 == 2

    print("Corrigé")
    e1 = descente(lambda th: 2 * (th - 3), 5.0, 0.25, 2)
    k = next(k for k in range(1, 20) if 1.99 * 0.25 ** k < 0.01)
    x6 = [v / 10_000 for v in (8_000, 15_000, 22_000, 35_000)]
    a6 = courbure(x6)
    print(f"  ex1 {e1} ; ex2 η = 0,5 -> {descente(lambda th: 2 * (th - 3), 5.0, 0.5, 1)} ; ex5 {k} pas ;"
          f" ex6 a = {a6:.2f}, q = {1 - 0.5 * a6:.3f}")
    assert e1 == [4.0, 3.5] and descente(lambda th: 2 * (th - 3), 5.0, 0.5, 1) == [3.0] and k == 4
    assert descente(lambda th: 2 * (th - 3), 5.0, 1.0, 4) == [1.0, 5.0, 1.0, 5.0]         # exercice 4
    assert round(0.01 / 1.99, 7) == 0.0050251 and 0.25 ** 3 == 0.015625 and 0.25 ** 4 == 0.00390625
    assert round(1.99 * 0.25 ** 4, 5) == 0.00777
    assert [round(v, 2) for v in x6] == [0.8, 1.5, 2.2, 3.5] and round(sum(v * v for v in x6), 2) == 19.98
    assert [round(v * v, 2) for v in x6] == [0.64, 2.25, 4.84, 12.25]
    assert round(a6, 2) == 9.99 and round(2 / a6, 4) == 0.2002 and round(1 - 0.5 * a6, 3) == -3.995
    assert round(1 - 0.1 * a6, 3) == 0.001 and round(1 - 0.1 * 15, 2) == -0.5          # exercices 6 et 7
    assert 2 / 8 == 0.25 and 1 / 8 == 0.125                                               # exercice 8
    try:
        descente(lambda th: th, 0.0, 0.0, 3)
    except ValueError:
        print("  η = 0 refusé : ValueError")
    else:
        raise AssertionError("un pas nul aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
parabole : [0.6, 1.08, 1.464, 1.7712, 2.01696]
démonstration 1 : L(0) = 9 ; L(0.6) = 5.76 (premier ordre 5.4) ; η = 1.1 : L(6.6) = 12.96 > 9
démonstration 2 : pentes [-2.0, -6.0, -6.0, -6.32456] ; la plus raide suit −∇L
démonstration 3 : η = 0.9 → [5.4, 1.08] ; η = 1.1 → [6.6, -1.32, 8.184] ; 26 pas pour 0,01
démonstration 4 : a = 15, w* = 1.99 ; tokens un par un : a = 1.5e+07
gradient moyen des mini-lots en w = 1 : -14.907 ; exact -14.850
bruit plancher (q = 0.5, η = 0.1, σ² = 1, B = 4) : théorie 0.0033333, simulation 0.0033716
Cas 1 [PUBLIC] : a = 15, w* = 1.99, 2/a = 0.13333 ; pas jusqu'à 0,01 : η = 0.05 → 4, η = 0.1 → 8, η = 0.15 → None
  η = 0.05 : [1.4925, 1.8656, 1.9589, 1.9822] ; η = 0.15 après 10 pas : w = -16.5433 → -99.26 s pour 6 000 tokens
Cas 2 [ASSUR] : AED bruts a = 9.990e+08, q = -4.9950e+08, w1 = 11_462.5 ; normalisé a = 0.81551, q = 0.59224, w* = 0.80318, 13 pas
  RMS 0.63856 (bascule 1.41421) ; avec 120 000 AED : a = 5.35445, q = -1.67722 ; poids infini au pas 36
Cas 3 [IMMO] : a = 3.75, w* = 1.9, σ² = 0.01625 ; coût k × B : η = 0.1 → 8 × 3 = 24 ; η = 0.25 → 2 × 11 = 22 ; η = 0.4 → 5 × 35 = 175 ;
  choix η = 0.25, B = 11 : écart-type prévu 0.009628, simulé 0.0098 (+1.6 %)
Cas 4 [BTP] : η = 0.09 → 31 et 151 pas ; η* = 0.097561 → 139 pas ; normalisé → 1 pas ; η = 0.11 diverge
  factures TTC (×1.05) : a1 = 22.05, q1 = -0.9845, 443 pas = 17720 s
Corrigé
  ex1 [4.0, 3.5] ; ex2 η = 0,5 -> [3.0] ; ex5 4 pas ; ex6 a = 9.99, q = -3.995
  η = 0 refusé : ValueError
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme cherche le minimum d'une perte en faisant des pas dans la direction opposée au gradient ; deux procédures annexes calculent le nombre de pas nécessaire et la taille de lot qui borne le bruit.

```text
ALGORITHME DescenteDeGradient
ENTRÉES : fonction gradient ∇L, point de départ θ₀, pas η > 0, nombre de pas n ≥ 0
SORTIE  : trajectoire θ₁ … θₙ

  SI η ≤ 0 OU n < 0 ALORS ERREUR « pas invalide »
  θ ← θ₀
  POUR t DE 1 À n FAIRE
      θ ← θ − η × ∇L(θ)
      noter θ
  FIN POUR
  RETOURNER la trajectoire

ALGORITHME DescenteStochastique (variante)
  à chaque pas, remplacer ∇L(θ) par la moyenne des gradients de B exemples tirés au hasard

ALGORITHME PasPourTolérance
ENTRÉES : écart de départ e₀, facteur q = 1 − ηa, tolérance τ > 0
SORTIE  : plus petit k tel que |e₀| × |q|ᵏ < τ, ou RIEN si |q| ≥ 1

  SI |e₀| < τ ALORS RETOURNER 0
  SI |q| ≥ 1 ALORS RETOURNER RIEN
  k ← plafond de ln(τ / |e₀|) / ln |q|, puis ajusté d'une unité si l'arrondi flottant l'exige
  RETOURNER k

ALGORITHME ChoisirPasEtLot
ENTRÉES : courbure a, variance σ² d'un exemple, écart e₀, tolérance τ, pas candidats η₁ … ηₘ
SORTIE  : le couple (η, B) de coût k × B minimal

  POUR CHAQUE η candidat FAIRE
      q ← 1 − η × a
      V₁ ← η² × σ² / (1 − q²)               plancher pour B = 1, RIEN si |q| ≥ 1
      B ← plafond de V₁ / τ²
      k ← PasPourTolérance(e₀, q, τ)
      coût ← k × B
  FIN POUR
  RETOURNER le couple de coût minimal
```

**Complexité.** La descente coûte O(n × C), où C est le coût d'un gradient : pour une régression sur m points, C = O(m), et la version stochastique ramène C à O(B) par pas, au prix d'un pas bruité. PasPourTolérance est en O(1), à l'ajustement d'arrondi près. ChoisirPasEtLot est en O(m) pour m pas candidats ; c'est le calcul que fait le cas 3 avant de lancer l'entraînement, et il coûte infiniment moins que l'entraînement lui-même.

**Du squelette au code.** L'algorithme est la fonction `descente(grad, theta, eta, pas)`, qui lève `ValueError` pour un pas nul ; les gradients sont passés sous forme de fonctions (`lambda th: 2 * (th - 3)` et `grad_w`). La variante stochastique est vérifiée par la liste `lots` de `main` : 20 000 gradients calculés chacun sur un des 4 points tiré au hasard, dont la moyenne retrouve `grad_w(1.0)` (le gradient stochastique est juste en moyenne). PasPourTolérance est `pas_pour_tolerance(e0, q, tau)`, qui renvoie `None` quand la descente ne converge pas. ChoisirPasEtLot est la boucle sur les pas candidats de `cas_3_minilot_immo`, qui appelle `bruit_plancher(eta, a, sigma2, B)` et `lot_minimal(eta, a, sigma2, tau)`. La courbure d'une régression est `courbure(x)` et son minimum `minimum(x, y)`. Les quatre cas sont `cas_1_latence_public`, `cas_2_montants_assur`, `cas_3_minilot_immo` et `cas_4_deux_courbures_btp`, appelés et vérifiés par `main`.
