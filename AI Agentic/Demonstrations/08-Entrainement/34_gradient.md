# 34 — Gradient : démonstrations

> Fiche : [34 — Gradient](<../../Images/08-Entrainement/34_gradient.md>) · Image : `34_gradient.jpg` · Leçon : [Étape 73 — Descente de gradient et LoRA](<../../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\nabla L = \left( \frac{\partial L}{\partial \theta_1},\ \frac{\partial L}{\partial \theta_2},\ \dots,\ \frac{\partial L}{\partial \theta_n} \right)
$$

Le gradient rassemble les dérivées partielles de la perte par rapport à chaque paramètre. Chaque dérivée partielle se calcule en faisant varier un seul paramètre, les autres restant fixes.

## Les symboles, un par un

$$
L
$$

La perte, réel ≥ 0, fonction des paramètres ; la leçon 73 l'écrit ℒ. Dans le programme : `perte(w, b, x, y)` (entropie croisée), `perte_mse(w, b, x, y)` (quadratique), et la fonction `L` de l'exemple simple.

$$
\theta_i
$$

Le paramètre numéro i, réel ; dans les exemples, θ₁ et θ₂, ou le poids w et le biais b d'un neurone. Liste `theta` dans `gradient_numerique`.

$$
n
$$

Le nombre de paramètres, entier ≥ 1 ; c'est aussi la longueur du vecteur gradient.

$$
\frac{\partial L}{\partial \theta_i}
$$

La dérivée partielle : de combien la perte change, par unité de θᵢ, quand seul θᵢ bouge. Son unité est celle de L divisée par celle de θᵢ.

$$
\nabla L
$$

Le vecteur des n dérivées partielles ; il pointe vers la plus forte hausse de la perte (démonstration 2). Couple renvoyé par `gradient(w, b, x, y)`.

$$
u
$$

Une direction, vecteur de longueur ‖u‖ = 1 ; la pente de L dans cette direction vaut ∇L · u (démonstration 1). Fonction `direction_unitaire(v)`.

$$
h
$$

Le petit pas d'une différence finie, réel > 0, par exemple 10⁻⁶ ; il sert à vérifier un gradient calculé à la main. Argument `h`.

$$
z, \; \hat y
$$

Pour un neurone : z = w x + b est le score brut (réel quelconque), ŷ = σ(z) la probabilité prédite, dans ]0 ; 1[. Variables `z` et `yh`.

$$
\sigma(z)
$$

La sigmoïde, σ(z) = 1/(1 + e⁻ᶻ), qui transforme un score en probabilité ; sa dérivée vaut σ(z)(1 − σ(z)). Fonction `sigma`.

$$
x, \; y, \; w, \; b
$$

L'entrée du neurone (réel), l'étiquette attendue (0 ou 1), le poids et le biais (réels). Variables `x`, `y`, `w`, `b` ; après un pas de descente, `w2` et `b2`.

## Le mécanisme, avant les preuves

Le gradient se construit coordonnée par coordonnée : on fige tous les paramètres sauf un, on le pousse d'une quantité infime, et l'on mesure de combien la perte bouge par unité de poussée ; on recommence pour chaque paramètre, et l'on range les n résultats dans un vecteur. La dérivée partielle est donc un rapport « variation de la perte / variation du paramètre », pris à la limite d'une variation nulle. Ranger ces rapports dans un vecteur n'est pas une simple commodité : la pente dans n'importe quelle direction est une combinaison linéaire de ces n nombres, un produit scalaire avec la direction (démonstration 1). C'est ce qui fait du gradient un résumé complet de la pente locale. Sa norme donne la pente maximale, sa direction le chemin de plus forte montée, et l'opposé de sa direction le chemin de plus forte descente (démonstration 2). Quand la perte est une composition (une perte appliquée à une sigmoïde appliquée à un score linéaire), la règle de la chaîne multiplie les dérivées locales le long du chemin : c'est pourquoi un facteur très petit en un point du chemin, comme la pente d'une sigmoïde saturée, peut éteindre tout le gradient (démonstration 5). On n'utilise ni somme ni maximum : seulement des produits de dérivées locales, puis un rangement en vecteur.

Petit film chiffré, sur L(θ₁, θ₂) = θ₁² + 3θ₂² au point (1 ; 1), où L = 4. On pousse θ₁ de 0,001 : L(1,001 ; 1) = 1,002001 + 3 = 4,002001, la perte a bougé de 0,002001, soit 2,001 par unité : la dérivée partielle vaut 2 (le 0,001 de trop disparaît quand la poussée tend vers 0). On pousse θ₂ de 0,001 : L(1 ; 1,001) = 1 + 3 × 1,002001 = 4,006003, soit 6,003 par unité : la dérivée partielle vaut 6. Le gradient est (2 ; 6). Dans la direction (0,6 ; 0,8), la pente vaut 2 × 0,6 + 6 × 0,8 = 1,2 + 4,8 = 6, sans aucune nouvelle évaluation de la perte.

## Démonstration 1 — La dérivée dans une direction quelconque

**Ce qu'on démontre.** Si L est dérivable au point θ et si u est un vecteur de longueur 1, la vitesse de variation de L quand on se déplace de t dans la direction u vaut

$$
\frac{d}{dt} L(\theta + t u)\Big|_{t=0} = \sum_{i=1}^{n} \frac{\partial L}{\partial \theta_i}\, u_i = \nabla L \cdot u
$$

**L'idée.** Se déplacer dans la direction u, c'est bouger tous les paramètres à la fois, θᵢ à la vitesse uᵢ. Chaque paramètre contribue à la variation de L selon sa dérivée partielle multipliée par sa vitesse, et les contributions s'additionnent, parce qu'au premier ordre une fonction dérivable se comporte comme une fonction linéaire.

**La preuve, pas à pas.**

**Étape 1.** On pose φ(t) = L(θ + t u), une fonction d'une seule variable, et chaque coordonnée du point vaut θᵢ + t uᵢ, dont la dérivée en t est uᵢ, parce que θᵢ et uᵢ sont des constantes.

**Étape 2.** La règle de la chaîne pour une fonction de plusieurs variables additionne, sur chaque coordonnée, la dérivée partielle de L multipliée par la dérivée de cette coordonnée :

$$
\varphi'(0) = \sum_{i=1}^{n} \frac{\partial L}{\partial \theta_i}(\theta) \times \frac{d(\theta_i + t u_i)}{dt} = \sum_{i=1}^{n} \frac{\partial L}{\partial \theta_i}\, u_i
$$

**Étape 3.** La somme des produits coordonnée par coordonnée est, par définition, le produit scalaire ∇L · u. ∎

**Vérification chiffrée.** L = θ₁² + 3θ₂² au point (1 ; 1), ∇L = (2 ; 6). Direction (1 ; 0) : pente 2. Direction (0,6 ; 0,8) : pente 6. Direction (−0,8 ; 0,6) : pente −1,6 + 3,6 = 2. Le programme compare chaque valeur à une différence finie (L(θ + h u) − L(θ))/h avec h = 10⁻⁶ : écart inférieur à 10⁻⁴. Contre-exemple quand l'hypothèse « L dérivable » manque : pour L(θ) = |θ| en 0, la pente vaut +1 dans la direction +1 et +1 aussi dans la direction −1, ce qu'aucun produit scalaire g × u ne peut donner (il faudrait g = 1 et g = −1 à la fois).

**Ce que la preuve révèle du mécanisme.** n nombres suffisent pour connaître une infinité de pentes : le gradient est une « table » compacte de la pente locale. La pente dans une direction est linéaire en u : retourner la direction change le signe de la pente.

**Conséquence pour un agent.** Pour prévoir l'effet d'un petit changement de plusieurs paramètres ou de plusieurs entrées à la fois, il suffit du gradient et d'un produit scalaire, sans réévaluer le modèle : c'est la base des explications « quelle entrée a poussé le score » (cas 2).

## Démonstration 2 — Le gradient indique la plus forte montée

**Ce qu'on démontre.** Pour ∇L ≠ 0 et tout u de longueur 1,

$$
\nabla L \cdot u \le \lVert \nabla L \rVert
$$

avec égalité si et seulement si u = ∇L/‖∇L‖. La pente maximale vaut donc ‖∇L‖, atteinte en suivant le gradient ; la pente minimale vaut −‖∇L‖, atteinte en allant à l'opposé.

**L'idée.** Un produit scalaire avec un vecteur de longueur 1 est la projection sur ce vecteur ; une projection est la plus longue quand on projette sur la direction du vecteur lui-même.

**La preuve, pas à pas.**

**Étape 1.** Par l'inégalité de Cauchy–Schwarz (fiche 01), parce que |a · b| ≤ ‖a‖‖b‖ pour tous vecteurs, et que ‖u‖ = 1 :

$$
\nabla L \cdot u \le \lvert \nabla L \cdot u \rvert \le \lVert \nabla L \rVert \, \lVert u \rVert = \lVert \nabla L \rVert
$$

**Étape 2.** Pour u = ∇L/‖∇L‖, qui est de longueur 1 parce qu'on divise un vecteur non nul par sa norme :

$$
\nabla L \cdot \frac{\nabla L}{\lVert \nabla L \rVert} = \frac{\lVert \nabla L \rVert^2}{\lVert \nabla L \rVert} = \lVert \nabla L \rVert
$$

**Étape 3.** L'égalité dans Cauchy–Schwarz n'a lieu que pour des vecteurs colinéaires de même sens, d'où l'unicité ; en remplaçant u par −u, on obtient la pente minimale −‖∇L‖. ∎

**Vérification chiffrée.** ∇L = (2 ; 6), ‖∇L‖ = √(4 + 36) = √40 ≈ 6,32456. La direction du gradient vaut (0,31623 ; 0,94868), de pente 6,32456 ; les directions (1 ; 0), (0,6 ; 0,8) et (−0,8 ; 0,6) donnent 2, 6 et 2, toutes plus petites. Contre-exemple de l'hypothèse « ∇L ≠ 0 » : au point (0 ; 0), le gradient est nul, toutes les pentes valent 0, et la direction ∇L/‖∇L‖ n'existe pas ; la fonction `direction_unitaire` renvoie alors `None`.

**Ce que la preuve révèle du mécanisme.** La norme du gradient mesure à quel point la perte est sensible au point courant ; sa direction mélange les coordonnées en proportion de leurs dérivées partielles. Près d'un minimum, la norme tend vers 0 et la direction perd son sens.

**Conséquence pour un agent.** La descente de gradient (fiche 08) suit −∇L, et la norme ‖∇L‖ est le premier indicateur de santé d'un entraînement : une norme qui explose signale une instabilité, une norme qui s'effondre un plateau ou une saturation. On l'écrête quand elle dépasse un seuil (cas 4).

## Démonstration 3 — Le gradient est perpendiculaire aux lignes de niveau

**Ce qu'on démontre.** Si L est dérivable et si un chemin c(t) reste sur une ligne de niveau, L(c(t)) = constante, avec c(0) = θ et une vitesse c′(0) = u non nulle, alors

$$
\nabla L(\theta) \cdot u = 0
$$

**L'idée.** Le long d'une ligne de niveau, la perte ne change pas : sa pente dans la direction tangente est nulle. Or cette pente vaut ∇L · u (démonstration 1), donc le gradient est orthogonal à la tangente.

**La preuve, pas à pas.**

**Étape 1.** La fonction t ↦ L(c(t)) est constante, donc sa dérivée est nulle, parce que la dérivée d'une constante est nulle.

**Étape 2.** Par la règle de la chaîne, comme dans la démonstration 1, cette dérivée en t = 0 vaut ∇L(θ) · c′(0) = ∇L · u.

**Étape 3.** On égale les deux expressions : ∇L · u = 0, c'est-à-dire ∇L ⊥ u. ∎

**Vérification chiffrée.** Au point (1 ; 1), la ligne de niveau L = 4 de θ₁² + 3θ₂² a pour tangente la direction u = (6 ; −2)/√40 ≈ (0,94868 ; −0,31623), et ∇L · u = 2 × 0,94868 − 6 × 0,31623 ≈ 0. En avançant de t = 0,1 le long de u, la perte ne change que de 0,012, et de 0,00012 pour t = 0,01 : la variation divisée par t (0,12 puis 0,012) tend vers 0, alors que dans la direction du gradient elle tendrait vers 6,32456. Contre-exemple quand le chemin quitte la ligne de niveau : dans la direction (0,6 ; 0,8), la pente vaut 6, pas 0.

**Ce que la preuve révèle du mécanisme.** Sur une carte de la perte, le gradient traverse les courbes de niveau à angle droit, comme la ligne de plus grande pente d'une carte topographique. Quand les courbes de niveau sont des ellipses très allongées, le gradient pointe vers le côté de la vallée et non vers son centre : c'est l'origine du zigzag de la descente de gradient quand les courbures diffèrent (fiche 08, cas 4).

**Conséquence pour un agent.** Le gradient dit comment ne rien changer autant que comment progresser : deux paramètres peuvent bouger ensemble, dans une direction orthogonale au gradient, sans changer la perte au premier ordre. C'est la raison pour laquelle des modèles aux poids différents peuvent avoir la même perte.

## Démonstration 4 — La règle de la chaîne, base de la rétropropagation

**Ce qu'on démontre.** Pour un neurone ŷ = σ(z) avec z = wx + b, et une perte d'entropie croisée L = −[y ln ŷ + (1 − y) ln(1 − ŷ)] :

$$
\frac{\partial L}{\partial w} = \frac{\partial L}{\partial \hat y} \times \frac{\partial \hat y}{\partial z} \times \frac{\partial z}{\partial w}
$$

Avec σ′(z) = σ(z)(1 − σ(z)) et ∂L/∂ŷ = (ŷ − y)/(ŷ(1 − ŷ)), les facteurs se simplifient :

$$
\frac{\partial L}{\partial w} = (\hat y - y)\, x, \qquad \frac{\partial L}{\partial b} = \hat y - y
$$

**L'idée.** Le calcul suit le chemin w → z → ŷ → L ; chaque maillon a une dérivée simple, et la dérivée totale est leur produit. Le dénominateur ŷ(1 − ŷ) de la perte compense exactement la pente σ′ de la sigmoïde : il ne reste que l'erreur ŷ − y.

**La preuve, pas à pas.**

**Étape 1.** Dérivée de la sigmoïde. σ(z) = (1 + e⁻ᶻ)⁻¹, donc, parce que la dérivée de u⁻¹ vaut −u⁻² u′ :

$$
\sigma'(z) = \frac{e^{-z}}{(1 + e^{-z})^2} = \sigma(z) \times \frac{e^{-z}}{1 + e^{-z}} = \sigma(z)\,(1 - \sigma(z))
$$

parce que e⁻ᶻ/(1 + e⁻ᶻ) = 1 − 1/(1 + e⁻ᶻ).

**Étape 2.** Dérivée de la perte par rapport à ŷ, parce que la dérivée de ln u vaut u′/u :

$$
\frac{\partial L}{\partial \hat y} = -\frac{y}{\hat y} + \frac{1 - y}{1 - \hat y} = \frac{\hat y - y}{\hat y (1 - \hat y)}
$$

**Étape 3.** Les deux derniers maillons : ∂z/∂w = x et ∂z/∂b = 1, parce que z = wx + b est linéaire en w et en b.

**Étape 4.** Le produit, où ŷ(1 − ŷ) se simplifie, parce que ŷ = σ(z) :

$$
\frac{\partial L}{\partial w} = \frac{\hat y - y}{\hat y (1 - \hat y)} \times \hat y (1 - \hat y) \times x = (\hat y - y)\, x
$$

et de même ∂L/∂b = ŷ − y. ∎

**Vérification chiffrée.** w = 0,5, b = −0,5, x = 2, y = 1 (cas 1) : z = 0,5, ŷ = σ(0,5) ≈ 0,62246, et la formule donne ∂L/∂w ≈ (0,62246 − 1) × 2 ≈ −0,75508 et ∂L/∂b ≈ −0,37754 ; les différences finies du programme retrouvent ces valeurs à 10⁻⁴ près en relatif. Contre-exemple de l'hypothèse « perte d'entropie croisée » : avec la perte quadratique ½(ŷ − y)², le facteur σ′ ne se simplifie plus, et ∂L/∂w = (ŷ − y) ŷ(1 − ŷ) x ≈ −0,17745 (démonstration 5).

**Ce que la preuve révèle du mécanisme.** Le gradient du neurone est « erreur fois entrée » : il est proportionnel à l'écart entre prédiction et vérité, et nul quand la prédiction est parfaite. L'entrée x joue le rôle d'un amplificateur : à erreur égale, un paramètre attaché à une grande entrée reçoit un grand gradient.

**Conséquence pour un agent.** Un réseau profond enchaîne cette règle couche par couche, de la sortie vers l'entrée : la rétropropagation calcule tout le gradient pour environ le coût de deux évaluations de la perte. Associer sigmoïde et entropie croisée n'est pas un choix de style : c'est ce qui garde un gradient franc quand le modèle se trompe.

## Démonstration 5 — Avec une perte quadratique, le gradient s'éteint quand la sigmoïde sature

**Ce qu'on démontre.** Pour le même neurone et la perte quadratique L = ½(ŷ − y)² :

$$
\frac{\partial L}{\partial w} = (\hat y - y)\, \hat y (1 - \hat y)\, x
$$

Le rapport entre ce gradient et celui de l'entropie croisée vaut ŷ(1 − ŷ) ≤ 1/4, et il tend vers 0 quand |z| devient grand, même si la prédiction est fausse.

**L'idée.** La règle de la chaîne multiplie les maillons. Avec la perte quadratique, le maillon ∂L/∂ŷ = ŷ − y ne contient plus le dénominateur qui compensait σ′ ; il reste le facteur ŷ(1 − ŷ), presque nul quand la sigmoïde est saturée.

**La preuve, pas à pas.**

**Étape 1.** ∂L/∂ŷ = ŷ − y, parce que la dérivée de ½u² vaut u u′.

**Étape 2.** On multiplie par σ′(z) = ŷ(1 − ŷ) (démonstration 4, étape 1) et par ∂z/∂w = x, ce qui donne la formule.

**Étape 3.** Le rapport avec (ŷ − y)x vaut ŷ(1 − ŷ) ; ce produit de deux nombres de somme 1 est maximal en ŷ = 1/2, où il vaut 1/4, parce que p(1 − p) = 1/4 − (p − 1/2)².

**Étape 4.** Quand z → −∞, ŷ → 0 et ŷ(1 − ŷ) → 0 ; quand z → +∞, 1 − ŷ → 0 et le produit tend aussi vers 0. ∎

**Vérification chiffrée.** Neurone saturé dans la mauvaise direction : z = −6, donc ŷ = σ(−6) ≈ 0,0024726, alors que y = 1. Le facteur vaut ŷ(1 − ŷ) ≈ 0,0024665 : avec x = 1,5, le gradient quadratique vaut environ −0,0036906 contre −1,49629 pour l'entropie croisée, 405,4 fois moins. Au point du cas 1 (z = 0,5), le rapport vaut 0,62246 × 0,37754 ≈ 0,23500, proche du maximum 1/4.

**Ce que la preuve révèle du mécanisme.** Un neurone très confiant et faux reçoit presque aucun signal avec la perte quadratique, et un signal maximal avec l'entropie croisée. Le facteur ŷ(1 − ŷ) passe sous 1 % de sa valeur « franche » dès que ŷ < 0,010102, c'est-à-dire z < −4,58486 (ou, symétriquement, z > 4,58486).

**Conséquence pour un agent.** Un classifieur binaire d'agent (escalade, fraude, document complet) s'entraîne avec l'entropie croisée, jamais avec l'erreur quadratique sur une sigmoïde. La contrepartie est réelle : l'entropie croisée donne de gros gradients aux exemples mal étiquetés, qu'il faut donc nettoyer ou adoucir (cas 3).

## Démonstration 6 — Vérifier un gradient par différences finies, et ce que cela coûte

**Ce qu'on démontre.** Si L est trois fois dérivable, on note eᵢ le vecteur qui ne bouge que le paramètre i. La différence avant et la différence centrée approchent la dérivée partielle avec des erreurs d'ordres différents :

$$
\frac{L(\theta + h e_i) - L(\theta)}{h} = \frac{\partial L}{\partial \theta_i} + \frac{h}{2} \frac{\partial^2 L}{\partial \theta_i^2} + O(h^2), \qquad \frac{L(\theta + h e_i) - L(\theta - h e_i)}{2h} = \frac{\partial L}{\partial \theta_i} + O(h^2)
$$

Vérifier les n dérivées coûte n évaluations de la perte (avant) ou 2n (centrée), contre environ deux pour la rétropropagation.

**L'idée.** Le développement de Taylor de L(θ ± h eᵢ) contient les mêmes termes pairs et des termes impairs de signes opposés : dans la différence centrée, les termes en h² de la perte s'annulent, et l'erreur ne commence qu'à l'ordre suivant.

**La preuve, pas à pas.**

**Étape 1.** Taylor à l'ordre 3 dans la direction eᵢ, avec L′, L″, L‴ les dérivées par rapport à θᵢ, parce que L est trois fois dérivable :

$$
L(\theta \pm h e_i) = L(\theta) \pm h L' + \frac{h^2}{2} L'' \pm \frac{h^3}{6} L''' + O(h^4)
$$

**Étape 2.** Différence avant : on retranche L(θ) et l'on divise par h ; il reste L′ + (h/2)L″ + O(h²).

**Étape 3.** Différence centrée : on retranche les deux développements, les termes pairs s'annulent, et l'on divise par 2h, ce qui laisse L′ + (h²/6)L‴ + O(h³).

**Étape 4.** Coût : chaque coordonnée demande une ou deux évaluations nouvelles de la perte, d'où n ou 2n évaluations. ∎

**Vérification chiffrée.** Neurone du cas 1, dérivée par rapport à w : −0,75508. Différence avant : erreur 0,0046923 pour h = 0,01 et 0,00046993 pour h = 0,001, proche de (h/2)L″ avec L″ = x² ŷ(1 − ŷ) ≈ 0,94001, soit 0,0047001 pour h = 0,01 ; l'erreur est divisée par 10 quand h l'est. Différence centrée : erreur 7,674 × 10⁻⁶ puis 7,674 × 10⁻⁸ : divisée par 100. Contre-exemple de l'hypothèse « h petit mais pas trop » : pour h = 10⁻¹², l'erreur d'arrondi des flottants, de l'ordre de 10⁻¹⁶/h, domine et la vérification n'a plus de sens ; on prend h entre 10⁻⁶ et 10⁻⁴ pour une différence centrée.

**Ce que la preuve révèle du mécanisme.** La différence avant se trompe d'un terme de courbure, la différence centrée d'un terme beaucoup plus petit : pour le même nombre de chiffres, la seconde accepte un h plus grand, donc moins sensible aux arrondis. Le coût, lui, croît avec le nombre de paramètres : pour 10⁹ paramètres, 2 × 10⁹ évaluations.

**Conséquence pour un agent.** On vérifie par différences finies un gradient écrit à la main ou une couche personnalisée, sur un petit modèle et quelques coordonnées tirées au hasard, puis on s'en remet à la rétropropagation. C'est le test unitaire standard d'une fonction de perte nouvelle.

## Exemple simple, à la main

Perte à deux paramètres L(θ₁, θ₂) = θ₁² + 3θ₂², au point (1 ; 1), où L = 1 + 3 = 4. Les dérivées partielles sont 2θ₁ (on dérive θ₁², θ₂ étant fixe) et 6θ₂ (on dérive 3θ₂², θ₁ étant fixe) :

$$
\nabla L = (2\theta_1\ ;\ 6\theta_2) = (2\ ;\ 6), \qquad \lVert \nabla L \rVert = \sqrt{4 + 36} = \sqrt{40} \approx 6{,}32456
$$

La perte est trois fois plus sensible à θ₂ qu'à θ₁ : un pas de descente la fera bouger surtout selon θ₂. Avec un pas de 0,1 contre le gradient (fiche 08) :

| coordonnée | valeur | dérivée partielle | 0,1 × dérivée | nouvelle valeur |
|---|---|---|---|---|
| θ₁ | 1 | 2 | 0,2 | 0,8 |
| θ₂ | 1 | 6 | 0,6 | 0,4 |

La perte passe de 4 à 0,8² + 3 × 0,4² = 0,64 + 0,48 = 1,12. Au premier ordre, la démonstration 1 prévoyait une baisse de 0,1 × ‖∇L‖² = 0,1 × 40 = 4, trop grande parce que le pas de 0,1 n'est pas petit pour la courbure 6 de θ₂ ; la baisse réelle vaut 4 − 1,12 = 2,88.

## Cas d'usage complexes, démontrés

### Cas 1 — Banque [BANQUE] : un neurone qui décide d'escalader une réclamation

**Contexte.** Une banque de détail de Dubaï fait trier les réclamations de ses clients, en arabe et en anglais, par un agent qui décide d'escalader ou non chaque message vers un conseiller. Un détecteur d'escalade utilise un seul neurone, ŷ = σ(wx + b), où x est un score de colère du message ; l'agent escalade si ŷ ≥ 0,7. Un message avec x = 2 n'a pas été escaladé alors qu'il aurait dû l'être (y = 1), et l'équipe corrige le modèle par un pas de descente. Les valeurs sont illustratives.

**Données.**

- Paramètres actuels : w = 0,5 ; b = −0,5.
- Message : x = 2 ; étiquette y = 1 (aurait dû être escaladé).
- Seuil d'escalade : ŷ ≥ 0,7 ; pas de descente η = 0,5.
- Perte : entropie croisée (démonstration 4).

**Calcul pas à pas.**

**Étape 1.** Passe avant :

$$
z = 0{,}5 \times 2 - 0{,}5 = 0{,}5, \qquad \hat y = \sigma(0{,}5) \approx 0{,}62246, \qquad L = -\ln 0{,}62246 \approx 0{,}47408
$$

ŷ < 0,7 : le message n'a pas été escaladé.

**Étape 2.** Gradient par la démonstration 4 :

$$
\frac{\partial L}{\partial w} = (0{,}62246 - 1) \times 2 \approx -0{,}75508, \qquad \frac{\partial L}{\partial b} \approx -0{,}37754
$$

**Étape 3.** Un pas de descente avec η = 0,5 :

$$
w_2 = 0{,}5 - 0{,}5 \times (-0{,}75508) \approx 0{,}87754, \qquad b_2 = -0{,}5 - 0{,}5 \times (-0{,}37754) \approx -0{,}31123
$$

**Étape 4.** Nouvelle passe avant sur le même message : z ≈ 0,87754 × 2 − 0,31123 ≈ 1,44385, ŷ ≈ 0,80905, L ≈ 0,21189.

**Décision de l'agent.** Après correction, ŷ ≈ 0,80905 ≥ 0,7 : un message de cette colère est désormais escaladé. Le gradient a indiqué dans quel sens et de combien bouger chaque paramètre : w, attaché à l'entrée x = 2, a bougé deux fois plus que b.

**Contre-calcul.** Avec une erreur de signe (on ajoute le gradient au lieu de le retrancher), w = 0,12246 et b = −0,68877, z ≈ −0,44385, ŷ ≈ 0,39082 et la perte monte à 0,93950 : le modèle escalade encore moins. Sur un flux de réclamations, chaque client en colère non escaladé reste face à l'agent automatique, avec un risque de réclamation formelle (coût illustratif à chiffrer par la banque).

**Sensibilité.** Après un pas, le nouveau score vaut z = 0,5 + η × 0,37754 × (x² + 1) = 0,5 + 1,8877η. Il atteint le seuil logit(0,7) = ln(0,7/0,3) ≈ 0,84730 pour η ≈ 0,18398 : c'est la valeur de bascule du pas. Avec η = 0,1, le même message reste sous le seuil après un pas ; avec η = 0,5, il passe nettement au-dessus.

**En production.** Indicateurs : le taux d'escalade et la part des réclamations formelles venues de messages non escaladés ; la norme du gradient par lot, qui s'effondre si le modèle sature. Le traitement des réclamations de la clientèle bancaire relève des règles de protection du consommateur de la CBUAE, à confirmer avec le texte en vigueur.

### Cas 2 — Assurance [ASSUR] : quel indice a poussé un score de fraude

**Contexte.** Un assureur auto et santé fait signaler par un agent les déclarations de sinistre suspectes, avec un neurone à deux entrées : x₁, le montant réclamé normalisé, et x₂, le nombre de sinistres des 12 derniers mois, normalisé. Le dossier est envoyé à un expert si ŷ ≥ 0,5, et l'agent doit expliquer à l'expert quelle entrée a pesé le plus. Ici, l'expert conclut que le dossier est légitime (y = 0). Les valeurs sont illustratives.

**Données.**

- Poids w₁ = 1,2 (montant), w₂ = 0,8 (historique), biais b = −2.
- Dossier : x₁ = 0,9 ; x₂ = 1,5 ; étiquette de l'expert y = 0.
- Seuil d'envoi à l'expert : ŷ ≥ 0,5 ; pas de correction η = 0,1.

**Calcul pas à pas.**

**Étape 1.** Passe avant :

$$
z = 1{,}2 \times 0{,}9 + 0{,}8 \times 1{,}5 - 2 = 1{,}08 + 1{,}2 - 2 = 0{,}28, \qquad \hat y = \sigma(0{,}28) \approx 0{,}56955
$$

ŷ ≥ 0,5 : le dossier est envoyé à l'expert.

**Étape 2.** Gradient du score par rapport aux entrées (l'explication), par la règle de la chaîne, parce que ∂ŷ/∂xⱼ = σ′(z) wⱼ :

$$
\hat y (1 - \hat y) \approx 0{,}24516, \qquad \frac{\partial \hat y}{\partial x_1} \approx 0{,}29420, \qquad \frac{\partial \hat y}{\partial x_2} \approx 0{,}19613
$$

**Étape 3.** Contribution de chaque entrée au score brut, wⱼxⱼ : 1,08 pour le montant, 1,2 pour l'historique. C'est l'historique qui a le plus poussé ce dossier, alors que le montant a le plus grand poids.

**Étape 4.** Gradient de la perte par rapport aux paramètres, avec l'étiquette y = 0 de l'expert (démonstration 4) :

$$
\frac{\partial L}{\partial w_1} = 0{,}56955 \times 0{,}9 \approx 0{,}51259, \qquad \frac{\partial L}{\partial w_2} = 0{,}56955 \times 1{,}5 \approx 0{,}85432, \qquad \frac{\partial L}{\partial b} \approx 0{,}56955
$$

et la perte vaut L = −ln(1 − 0,56955) ≈ 0,84292. Le programme vérifie ces trois dérivées par différences centrées.

**Étape 5.** Un pas de correction η = 0,1 : w₁ ≈ 1,14874, w₂ ≈ 0,71457, b ≈ −2,05695 ; le même dossier a alors z ≈ 0,04876 et ŷ ≈ 0,51219.

**Décision de l'agent.** Le dossier part chez l'expert (ŷ ≈ 0,57), avec l'explication « historique de sinistres : contribution 1,2 ; montant : 1,08 ». Après le verdict « légitime », un pas de correction baisse le score à 0,51219 : un seul exemple ne fait pas basculer le modèle, ce qui est voulu, parce qu'un verdict isolé peut être une erreur.

**Contre-calcul.** L'explication naïve « l'entrée au plus grand poids a le plus pesé » désignerait le montant (w₁ = 1,2 > 0,8) : c'est faux pour ce dossier, où x₂ = 1,5 amplifie le poids de l'historique (démonstration 4, x comme amplificateur). Un expert orienté vers le mauvais indice perd du temps sur la facture du garage au lieu de regarder l'historique, et l'assuré légitime attend sa réponse.

**Sensibilité.** Une hausse de 1 % du montant (x₁ de 0,9 à 0,909) déplace le score d'environ 0,29420 × 0,009 ≈ 0,0026478 au premier ordre (exact : 0,0026458). La valeur de bascule de l'historique est celle qui annule z : x₂ = (2 − 1,08)/0,8 = 1,15 ; sous 1,15 sinistres normalisés, ce dossier n'aurait pas été envoyé.

**En production.** Indicateurs : la part des dossiers envoyés à l'expert et jugés légitimes (faux positifs), et la part des explications où l'entrée citée est bien celle de plus forte contribution. L'assurance est supervisée par la CBUAE ; ce que l'assureur doit expliquer à l'assuré sur une décision automatisée est à confirmer avec le texte en vigueur.

### Cas 3 — Ressources humaines [RH] : une perte quadratique qui n'apprend plus

**Contexte.** Un cabinet RH présent dans plusieurs émirats entraîne un classifieur qui signale les dossiers de visa incomplets (pièce manquante, contrat MOHRE non signé) avant leur dépôt. La première version utilisait l'erreur quadratique sur une sigmoïde. Un dossier incomplet est scoré avec une grande confiance comme complet, et l'entraînement ne le corrige pas. L'équipe compare les deux pertes. Les valeurs sont illustratives.

**Données.**

- Paramètres w = −2 ; b = −3 ; entrée x = 1,5 ; étiquette y = 1 (incomplet).
- Pas de descente η = 0,5 ; objectif : ŷ ≥ 0,5 sur ce dossier.
- Pertes comparées : quadratique ½(ŷ − y)² et entropie croisée.

**Calcul pas à pas.**

**Étape 1.** Passe avant : z = −2 × 1,5 − 3 = −6, ŷ = σ(−6) ≈ 0,0024726 : le modèle est sûr à 99,75 % que le dossier est complet, et il se trompe.

**Étape 2.** Gradients par rapport à w (démonstrations 4 et 5) :

$$
\text{entropie croisée : } (\hat y - y)\, x \approx -1{,}49629, \qquad \text{quadratique : } (\hat y - y)\, \hat y (1 - \hat y)\, x \approx -0{,}0036906
$$

soit un rapport de 405,4.

**Étape 3.** On répète la descente sur ce dossier jusqu'à ŷ ≥ 0,5 (programme) : 4 pas avec l'entropie croisée, 263 pas avec la perte quadratique.

**Étape 4.** Zone de saturation : le facteur ŷ(1 − ŷ) passe sous 1 % dès que |z| > 4,58486 (démonstration 5). Ce dossier, à z = −6, est au cœur de la zone.

**Décision de l'agent.** L'équipe passe à l'entropie croisée : les dossiers confiants et faux sont corrigés en quelques pas au lieu de centaines. Elle ajoute un contrôle des étiquettes, parce que l'entropie croisée donne justement les plus gros gradients aux exemples dont l'étiquette pourrait être fausse.

**Contre-calcul.** Avec la perte quadratique, le dossier reste scoré « complet » pendant 263 pas ; si les dossiers de ce type passent le contrôle, chacun est déposé incomplet et revient refusé, avec un délai pour le salarié et une nouvelle démarche pour le cabinet. Le rapport 263/4 ≈ 66 mesure le temps d'entraînement gâché sur ce seul exemple.

**Sensibilité.** La valeur de bascule est |z| = 4,58486 : au-delà, le gradient quadratique vaut moins de 1 % du gradient d'entropie croisée. Un dossier moins mal scoré, à z = −2, a un facteur ŷ(1 − ŷ) ≈ 0,10499, soit environ 10 % : la perte quadratique y apprend dix fois plus lentement, mais elle apprend.

**En production.** Indicateurs : la part des exemples d'entraînement à la fois faux et saturés (|z| > 4,6), et le taux de dossiers refusés pour pièce manquante. Les pièces d'un dossier de visa (passeport, Emirates ID, contrat) sont des données personnelles : leur usage pour l'entraînement relève de la PDPL, ou du régime propre au DIFC ou à l'ADGM, à confirmer avec le texte en vigueur.

### Cas 4 — Actifs virtuels [CRYPTO] : écrêter la norme d'un gradient explosif

**Contexte.** Une plateforme d'actifs virtuels agréée par la VARA réentraîne chaque nuit un modèle de score d'alertes de marché. Un lot contenant un pic de prix aberrant produit un gradient explosif. L'équipe compare deux façons de l'écrêter : réduire la norme du vecteur entier, ou couper chaque coordonnée. Les valeurs sont illustratives.

**Données.**

- Gradient du lot aberrant : g = (3 ; −4 ; 12).
- Normes des 10 derniers lots : 2,0 ; 2,2 ; 2,4 ; 2,5 ; 2,5 ; 2,6 ; 2,9 ; 3,1 ; 3,6 ; 13,0.
- Seuil d'écrêtage c = 5 ; pas de descente η = 0,01.
- Règle : au plus 10 % des lots écrêtés.

**Calcul pas à pas.**

**Étape 1.** Norme du gradient :

$$
\lVert g \rVert = \sqrt{9 + 16 + 144} = \sqrt{169} = 13
$$

**Étape 2.** Écrêtage par la norme : on multiplie g par c/‖g‖ = 5/13 ≈ 0,38462, ce qui donne (1,15385 ; −1,53846 ; 4,61538), de norme 5 et de même direction.

**Étape 3.** Écrêtage coordonnée par coordonnée à [−5 ; 5] : (3 ; −4 ; 5), de norme √50 ≈ 7,07107. Le cosinus avec g vaut (9 + 16 + 60)/(13 × 7,07107) ≈ 0,92468, soit un angle d'environ 22,38° : la direction a changé.

**Étape 4.** Taux d'écrêtage : avec c = 5, seul le lot de norme 13 est écrêté, 1 sur 10, soit 10 %. La médiane des normes vaut (2,5 + 2,6)/2 = 2,55.

**Décision de l'agent.** Le job écrête par la norme avec c = 5 : le pas garde la direction du gradient (démonstration 2) et sa longueur est bornée à η × 5 = 0,05, au lieu de η × 13 = 0,13.

**Contre-calcul.** Sans écrêtage, ce lot fait un pas de 0,13, environ 5,1 fois le pas typique de η × 2,55 = 0,0255. Avec l'écrêtage par coordonnée, le pas est plus court mais tourné de 22,38° : il ne suit plus la plus forte descente : la troisième coordonnée, seule écrêtée, passe de 12 à 5 et perd plus de la moitié de sa valeur, alors que les deux autres gardent la leur.

**Sensibilité.** La valeur de bascule du seuil est 3,6 : tout c entre 3,6 et 13 n'écrête que le lot aberrant (10 %) ; un seuil de 3 écrêterait aussi les lots de 3,1 et 3,6, soit 30 % des lots, et fausserait des gradients normaux.

**En production.** Indicateurs : la part des lots écrêtés par nuit, avec une alerte au-delà de 10 %, et la norme médiane du gradient, dont une dérive signale un changement des données de marché. Les obligations de surveillance et de documentation des modèles d'une plateforme agréée par la VARA sont à confirmer avec le texte en vigueur.

## Entraînement sur feuille A4

**Exercice 1.** Calculer le gradient de L = 2θ₁² + θ₁θ₂ + θ₂² au point (1 ; 2).

**Exercice 2.** Avec L = θ₁² + 3θ₂² au point (1 ; 1), calculer la pente dans la direction u = (1 ; 0), puis (0,6 ; 0,8).

**Exercice 3.** Démontrer que σ′(z) = σ(z)(1 − σ(z)).

**Exercice 4.** Dans le cas 1, recalculer les gradients si y = 0 (le message ne devait pas être escaladé).

**Exercice 5.** Pourquoi le gradient est-il nul en un minimum ?

**Exercice 6 (modifier une donnée).** Dans le cas 1, le message a un score de colère x = 3 au lieu de 2. Calculer z, ŷ et les deux dérivées partielles. Le message est-il escaladé sans correction ?

**Exercice 7 (trouver l'erreur).** Un collègue écrit, pour un neurone sigmoïde entraîné à l'entropie croisée : « ∂L/∂w = (ŷ − y) ŷ (1 − ŷ) x ». Trouver l'erreur, et chiffrer ce qu'elle change sur le dossier du cas 3.

**Exercice 8 (redémontrer de mémoire).** Sans regarder, redémontrer que pour ŷ = σ(wx + b) et l'entropie croisée, ∂L/∂w = (ŷ − y)x.

## Corrigé

**Exercice 1.** ∂L/∂θ₁ = 4θ₁ + θ₂ et ∂L/∂θ₂ = θ₁ + 2θ₂ ; au point (1 ; 2) : (4 + 2 ; 1 + 4) = (6 ; 5).

**Exercice 2.** (2 ; 6) · (1 ; 0) = 2 et (2 ; 6) · (0,6 ; 0,8) = 1,2 + 4,8 = 6.

**Exercice 3.** σ(z) = 1/(1 + e⁻ᶻ), σ′(z) = e⁻ᶻ/(1 + e⁻ᶻ)² = σ(z) × e⁻ᶻ/(1 + e⁻ᶻ) = σ(z)(1 − σ(z)), parce que e⁻ᶻ/(1 + e⁻ᶻ) = 1 − σ(z).

**Exercice 4.** (0,62246 − 0) × 2 ≈ 1,24492 et 0,62246 : les deux dérivées sont positives, un pas de descente fait baisser w et b, donc le score.

**Exercice 5.** Si une dérivée partielle était non nulle, bouger un peu ce paramètre dans le sens opposé à son signe ferait baisser la perte (démonstration 1 avec u = ±eᵢ) : ce ne serait pas un minimum.

**Exercice 6.** z = 0,5 × 3 − 0,5 = 1, ŷ = σ(1) ≈ 0,73106 ≥ 0,7 : le message est escaladé sans correction. ∂L/∂w = (0,73106 − 1) × 3 ≈ −0,80682 et ∂L/∂b ≈ −0,26894 : le gradient pousse encore un peu vers l'escalade, parce que la perte n'est pas nulle tant que ŷ < 1.

**Exercice 7.** C'est le gradient de la perte quadratique (démonstration 5) : avec l'entropie croisée, le facteur ŷ(1 − ŷ) se simplifie (démonstration 4). Sur le dossier du cas 3, la formule fausse donne −0,0036906 au lieu de −1,49629, soit 405,4 fois trop peu : le modèle n'apprendrait presque rien de ses erreurs les plus graves.

**Exercice 8.** Étapes 1 à 4 de la démonstration 4 : σ′ = ŷ(1 − ŷ), ∂L/∂ŷ = (ŷ − y)/(ŷ(1 − ŷ)), ∂z/∂w = x, puis le produit, où ŷ(1 − ŷ) se simplifie.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`sigma(z)`** — Cette fonction est le variateur de lumière qui transforme n'importe quel score en une probabilité entre 0 et 1 : elle reçoit un nombre réel z et renvoie 1/(1 + e⁻ᶻ), la sigmoïde, qui vaut 0,5 en z = 0, s'approche de 1 pour les grands z et de 0 pour les très négatifs. Elle donne 0,62246 pour z = 0,5, la probabilité d'escalade du cas 1, et 0,0024726 pour z = −6, le dossier faussement rassurant du cas 3 ; toutes les pertes et tous les gradients du programme passent par elle.

**`perte(w, b, x, y)`** — On la voit en juge sévère qui punit d'autant plus une prédiction qu'elle était sûre d'elle et fausse : elle reçoit le poids w, le biais b, l'entrée x et l'étiquette y, 0 ou 1, calcule la probabilité ŷ = σ(wx + b), puis renvoie l'entropie croisée −(y ln ŷ + (1 − y) ln(1 − ŷ)). Elle vaut 0,47408 pour le neurone du cas 1 avant correction et 0,21189 après un pas de descente, et `main` vérifie par différences finies que sa dérivée est bien celle que donne `gradient`.

**`gradient(w, b, x, y)`** — Cette fonction est la boussole du neurone sigmoïde avec l'entropie croisée : elle reçoit les mêmes quatre nombres, calcule ŷ, puis renvoie le couple ((ŷ − y)x, ŷ − y), où le facteur ŷ(1 − ŷ) de la sigmoïde s'est simplifié par la règle de la chaîne, comme le prouve la démonstration 4. Pour le cas 1, elle donne −0,75508 et −0,37754, et pour le dossier saturé du cas 3, un gradient de −1,49629 encore vigoureux, qui permet de corriger l'erreur en 4 pas.

**`perte_mse(w, b, x, y)`** — Celle-ci est l'ancienne règle du cabinet du cas 3, l'erreur quadratique posée sur une sigmoïde : elle reçoit le poids, le biais, l'entrée et l'étiquette et renvoie ½(σ(wx + b) − y)². Le programme la définit pour la comparaison avec l'entropie croisée et pour nommer la perte dont `gradient_mse` donne la dérivée, mais aucun calcul de `main` ne l'appelle directement : c'est sa dérivée, et non sa valeur, qui révèle la saturation.

**`gradient_mse(w, b, x, y)`** — Cette fonction raconte un professeur qui n'ose plus corriger l'élève dès que celui-ci a l'air très sûr de lui : elle reçoit les quatre mêmes nombres, calcule ŷ et le facteur d = (ŷ − y) ŷ (1 − ŷ), puis renvoie le couple (d x, d), le gradient de la perte quadratique de la démonstration 5. Le facteur ŷ(1 − ŷ) ne se simplifie plus et écrase le gradient quand la sigmoïde sature : −0,17745 contre −0,75508 dans le cas 1, et surtout −0,0036906 contre −1,49629 dans le cas 3, soit 405,4 fois moins, d'où 263 pas au lieu de 4.

**`gradient_numerique(f, theta, h)`** — On l'imagine en arpenteur qui vérifie la pente d'un terrain en posant un piquet un peu devant et un peu derrière : elle reçoit une fonction de plusieurs variables, un point θ et un pas h, 10⁻⁶ par défaut, refuse un h nul ou négatif par une `ValueError`, puis, pour chaque coordonnée, évalue f en θ + h eᵢ et en θ − h eᵢ et divise l'écart par 2h. Elle renvoie la liste de ces dérivées centrées, qui retrouve (6 ; 5) pour l'exercice 1 et le gradient du cas 2 à moins de 10⁻⁶ près.

**`direction_unitaire(v)`** — Cette fonction est le cartographe qui ne garde d'une flèche que son orientation : elle reçoit un vecteur, calcule sa norme, renvoie `None` pour le vecteur nul, qui n'a pas de direction, et sinon divise chaque coordonnée par cette norme. Elle transforme le gradient (2 ; 6) en (0,31623 ; 0,94868), direction de plus forte montée de pente 6,32456, et le vecteur (6 ; −2) en (0,94868 ; −0,31623), tangent à la ligne de niveau de la démonstration 3.

**`ecretage_norme(g, c)`** — Celle-ci est le régulateur qui bride un moteur trop puissant sans changer la direction du véhicule : elle reçoit un gradient et un seuil c, refuse un seuil nul ou négatif par une `ValueError`, calcule la norme du gradient, le renvoie inchangé s'il ne dépasse pas c, et sinon le multiplie par c divisé par cette norme. Dans le cas 4, le gradient (3 ; −4 ; 12), de norme 13, devient (1,15385 ; −1,53846 ; 4,61538), de norme 5 et de même direction.

**`cosinus(a, b)`** — Cette petite fonction mesure si deux flèches pointent dans le même sens, comme un rapporteur posé entre elles : elle reçoit deux vecteurs, renvoie `None` si l'un d'eux est nul, et sinon renvoie leur produit scalaire divisé par le produit de leurs normes. Dans le cas 4, elle donne exactement 1 entre le gradient et sa version écrêtée par la norme, mais 0,92468 avec la version écrêtée coordonnée par coordonnée, soit un angle de 22,38 degrés introduit par cette seconde méthode.

**`cas_1_escalade_banque()`** — Cette fonction met en scène une banque dont l'agent décide d'escalader une réclamation quand un neurone unique donne ŷ ≥ 0,7, et qui n'a pas escaladé un message au score de colère 2 qui aurait dû l'être : elle ne reçoit rien, calcule ŷ = 0,62246 et une perte de 0,47408, puis fait un pas de descente de taille 0,5, qui porte w à 0,87754, b à −0,31123 et ŷ à 0,80905, au-dessus du seuil. Elle montre qu'une erreur de signe ferait au contraire tomber ŷ à 0,39082, calcule le pas de bascule 0,18398 sous lequel la correction ne suffit pas, et le ŷ de 0,66569 qu'on obtiendrait avec un pas de 0,1, puis renvoie ces résultats.

**`cas_2_fraude_assur()`** — On y suit un assureur dont un neurone à deux entrées, le montant réclamé et le nombre de sinistres récents, a envoyé à un expert un dossier finalement légitime : la fonction ne reçoit rien, calcule ŷ = 0,56955, puis les sensibilités 0,2942 et 0,19613 de ŷ à chaque entrée et leurs contributions 1,08 et 1,20, en montrant que c'est le nombre de sinistres qui a le plus pesé. Elle calcule le gradient (0,51259 ; 0,85432 ; 0,56955), le vérifie par `gradient_numerique`, fait un pas de 0,1 qui ramène ŷ à 0,51219, compare l'effet linéaire et exact d'une hausse de 1 % du montant, calcule la valeur de bascule 1,15 de la seconde entrée, et renvoie le tout.

**`cas_3_saturation_rh()`** — Cette fonction raconte un cabinet de recrutement dont le classifieur, entraîné avec l'erreur quadratique, juge complet à 99,75 % un dossier de visa qui ne l'est pas, et ne le corrige pas : elle ne reçoit rien, calcule ŷ = 0,0024726 pour z = −6, puis les deux gradients, −1,49629 avec l'entropie croisée et −0,0036906 avec la perte quadratique. Elle compte, grâce à sa fonction interne, 4 pas de taille 0,5 pour faire passer ŷ au-dessus de 0,5 avec l'entropie croisée contre 263 avec la perte quadratique, montre que le facteur ŷ(1 − ŷ) tombe sous 1 % dès que |z| dépasse 4,58486 et vaut encore 0,10499 en z = −2, puis renvoie ces nombres.

**`pas_jusqu_a_bascule(grad, w, b, x, y, eta)`** — Cette fonction interne vit dans `cas_3_saturation_rh`, comme le chronomètre qu'on déclenche pour une seule course : elle reçoit une fonction de gradient et le dossier de départ, w = −2, b = −3, x = 1,5, y = 1, avec un pas de 0,5, puis répète au plus 100 000 fois la même opération, vérifier si σ(wx + b) atteint 0,5, et sinon faire un pas de descente. Elle renvoie le nombre de pas nécessaires, 4 avec `gradient` et 263 avec `gradient_mse`, ou `None` si la limite était atteinte.

**`cas_4_ecretage_crypto()`** — Ici, une plateforme d'actifs virtuels voit un lot au pic de prix aberrant produire un gradient explosif, (3 ; −4 ; 12), et compare deux écrêtages au seuil 5 : la fonction ne reçoit rien, ramène par `ecretage_norme` la norme de 13 à 5 avec un facteur 0,38462 sans changer la direction, puis coupe chaque coordonnée, ce qui donne (3 ; −4 ; 5), de norme 7,07107, tourné de 22,38 degrés. Sur dix normes de lots, elle compte 10 % de lots écrêtés au seuil 5 et 30 % au seuil 3, calcule la médiane 2,55, puis les pas de taille 0,01 × norme, 0,13 sans écrêtage, 0,05 avec et 0,0255 pour un lot typique, et renvoie ces résultats.

**`main()`** — C'est le chef d'orchestre de la fiche : il calcule d'abord le gradient (2 ; 6), de norme 6,32456, de la perte θ₁² + 3θ₂² au point (1 ; 1), puis vérifie la pente directionnelle dans trois directions, la direction de plus forte montée, la tangente à la ligne de niveau, la règle de la chaîne sur le neurone du cas 1, la saturation de la perte quadratique et l'erreur des différences avant et centrées, qui décroît comme h et comme h². Il joue ensuite les quatre cas et le corrigé des exercices, puis s'assure qu'un pas h nul est refusé ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 34 — gradient : dérivée directionnelle, plus forte pente, lignes de niveau, règle de la chaîne, saturation, différences finies, quatre cas aux Émirats."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def sigma(z):
    return 1 / (1 + math.exp(-z))


def perte(w, b, x, y):
    """Entropie croisée d'un neurone sigmoïde."""
    yh = sigma(w * x + b)
    return -(y * math.log(yh) + (1 - y) * math.log(1 - yh))


def gradient(w, b, x, y):
    """(∂L/∂w, ∂L/∂b) = ((ŷ − y) x, ŷ − y) pour l'entropie croisée (démonstration 4)."""
    yh = sigma(w * x + b)
    return (yh - y) * x, yh - y


def perte_mse(w, b, x, y):
    """Perte quadratique ½ (ŷ − y)² sur une sigmoïde."""
    return 0.5 * (sigma(w * x + b) - y) ** 2


def gradient_mse(w, b, x, y):
    """(∂L/∂w, ∂L/∂b) = ((ŷ − y) ŷ (1 − ŷ) x, (ŷ − y) ŷ (1 − ŷ)) (démonstration 5)."""
    yh = sigma(w * x + b)
    d = (yh - y) * yh * (1 - yh)
    return d * x, d


def gradient_numerique(f, theta, h=1e-6):
    """∂f/∂θᵢ ≈ (f(θ + h eᵢ) − f(θ − h eᵢ)) / 2h, coordonnée par coordonnée (démonstration 6)."""
    if h <= 0:
        raise ValueError("h doit être > 0")
    g = []
    for i in range(len(theta)):
        plus, moins = list(theta), list(theta)
        plus[i] += h
        moins[i] -= h
        g.append((f(plus) - f(moins)) / (2 * h))
    return g


def direction_unitaire(v):
    """v / ‖v‖ ; None pour le vecteur nul (pas de direction)."""
    n = math.sqrt(sum(c * c for c in v))
    if n == 0:
        return None
    return [c / n for c in v]


def ecretage_norme(g, c):
    """Ramène la norme de g à c au plus, sans changer sa direction."""
    if c <= 0:
        raise ValueError("le seuil doit être > 0")
    n = math.sqrt(sum(v * v for v in g))
    return list(g) if n <= c else [v * c / n for v in g]


def cosinus(a, b):
    na, nb = math.sqrt(sum(v * v for v in a)), math.sqrt(sum(v * v for v in b))
    if na == 0 or nb == 0:
        return None
    return sum(p * q for p, q in zip(a, b)) / (na * nb)


def cas_1_escalade_banque():
    """Banque : neurone d'escalade, x = 2, y = 1, un pas η = 0.5, seuil 0.7."""
    w, b, x, y = 0.5, -0.5, 2.0, 1
    gw, gb = gradient(w, b, x, y)
    w2, b2 = w - 0.5 * gw, b - 0.5 * gb
    w_faux, b_faux = w + 0.5 * gw, b + 0.5 * gb
    logit = math.log(0.7 / 0.3)
    pente_z = -gb * (x * x + 1)
    res = {"z": w * x + b, "yh": sigma(w * x + b), "L": perte(w, b, x, y), "gw": gw, "gb": gb, "w2": w2, "b2": b2,
           "z2": w2 * x + b2, "yh2": sigma(w2 * x + b2), "L2": perte(w2, b2, x, y), "w_faux": w_faux, "b_faux": b_faux,
           "z_faux": w_faux * x + b_faux, "yh_faux": sigma(w_faux * x + b_faux), "L_faux": perte(w_faux, b_faux, x, y),
           "logit": logit, "pente_z": pente_z, "eta_bascule": (logit - (w * x + b)) / pente_z,
           "yh_01": sigma((w - 0.1 * gw) * x + (b - 0.1 * gb))}
    print(f"Cas 1 [BANQUE] : ŷ = {res['yh']:.5f} → après un pas ŷ = {res['yh2']:.5f} (seuil 0.7) ;"
          f" erreur de signe ŷ = {res['yh_faux']:.5f} ; η de bascule {res['eta_bascule']:.5f}")
    print(f"  z après un pas = 0.5 + {res['pente_z']:.4f} η ; seuil logit(0.7) = {logit:.5f} ; avec η = 0.1 : ŷ = {res['yh_01']:.5f}")
    return res


def cas_2_fraude_assur():
    """Assurance : neurone à deux entrées, explication par le gradient, correction η = 0.1."""
    w1, w2_, b, x1, x2, y = 1.2, 0.8, -2.0, 0.9, 1.5, 0
    z = w1 * x1 + w2_ * x2 + b
    yh = sigma(z)
    s = yh * (1 - yh)
    f = lambda t: -(y * math.log(sigma(t[0] * x1 + t[1] * x2 + t[2])) + (1 - y) * math.log(1 - sigma(t[0] * x1 + t[1] * x2 + t[2])))
    g = [(yh - y) * x1, (yh - y) * x2, yh - y]
    g_num = gradient_numerique(f, [w1, w2_, b])
    n = [w1 - 0.1 * g[0], w2_ - 0.1 * g[1], b - 0.1 * g[2]]
    zn = n[0] * x1 + n[1] * x2 + n[2]
    res = {"z": z, "yh": yh, "s": s, "dx1": s * w1, "dx2": s * w2_, "c1": w1 * x1, "c2": w2_ * x2, "g": g,
           "ecart_num": max(abs(a - c) for a, c in zip(g, g_num)), "L": f([w1, w2_, b]), "n": n, "zn": zn,
           "yhn": sigma(zn), "un_pct": s * w1 * 0.009, "un_pct_exact": sigma(z + w1 * 0.009) - yh,
           "bascule_x2": (-b - w1 * x1) / w2_}
    print(f"Cas 2 [ASSUR] : ŷ = {yh:.5f} ; ∂ŷ/∂x = ({res['dx1']:.5f} ; {res['dx2']:.5f}) ; contributions"
          f" {res['c1']:.2f} et {res['c2']:.2f} ; après correction ŷ = {res['yhn']:.5f}")
    print(f"  ∇L = {[round(v, 5) for v in g]} (écart aux différences centrées < 1e-6) ; bascule x2 = {res['bascule_x2']:.2f}")
    return res


def cas_3_saturation_rh():
    """RH : dossier confiant et faux (z = −6) ; pas nécessaires pour ŷ ≥ 0.5 selon la perte."""
    def pas_jusqu_a_bascule(grad, w=-2.0, b=-3.0, x=1.5, y=1, eta=0.5):
        for k in range(100_000):
            if sigma(w * x + b) >= 0.5:
                return k
            gw, gb = grad(w, b, x, y)
            w, b = w - eta * gw, b - eta * gb
        return None

    yh = sigma(-6.0)
    p_seuil = (1 - math.sqrt(0.96)) / 2
    res = {"yh": yh, "facteur": yh * (1 - yh), "g_ce": gradient(-2.0, -3.0, 1.5, 1)[0],
           "g_mse": gradient_mse(-2.0, -3.0, 1.5, 1)[0], "pas_ce": pas_jusqu_a_bascule(gradient),
           "pas_mse": pas_jusqu_a_bascule(gradient_mse), "p_seuil": p_seuil,
           "z_seuil": math.log(p_seuil / (1 - p_seuil)), "facteur_z2": sigma(-2.0) * (1 - sigma(-2.0))}
    print(f"Cas 3 [RH] : ŷ = {yh:.7f} ; gradients {res['g_ce']:.5f} (entropie croisée) et {res['g_mse']:.7f}"
          f" (quadratique) ; pas jusqu'à ŷ ≥ 0.5 : {res['pas_ce']} contre {res['pas_mse']}")
    print(f"  saturation : facteur ŷ(1 − ŷ) < 1 % dès que |z| > {-res['z_seuil']:.5f} ; à z = −2 il vaut {res['facteur_z2']:.5f}")
    return res


def cas_4_ecretage_crypto():
    """Actifs virtuels : écrêtage par la norme contre écrêtage par coordonnée, seuil 5."""
    g = [3.0, -4.0, 12.0]
    normes = [2.0, 2.2, 2.4, 2.5, 2.5, 2.6, 2.9, 3.1, 3.6, 13.0]
    g_norme = ecretage_norme(g, 5.0)
    g_coord = [max(-5.0, min(5.0, v)) for v in g]
    triees = sorted(normes)
    res = {"norme": math.sqrt(sum(v * v for v in g)), "facteur": 5 / 13, "g_norme": g_norme,
           "norme_coord": math.sqrt(sum(v * v for v in g_coord)), "g_coord": g_coord,
           "cos_norme": cosinus(g, g_norme), "cos_coord": cosinus(g, g_coord),
           "angle": math.degrees(math.acos(cosinus(g, g_coord))),
           "taux_5": sum(1 for v in normes if v > 5) / len(normes), "taux_3": sum(1 for v in normes if v > 3) / len(normes),
           "mediane": (triees[4] + triees[5]) / 2, "pas_brut": 0.01 * 13, "pas_ecrete": 0.01 * 5}
    res["pas_typique"] = 0.01 * res["mediane"]
    print(f"Cas 4 [CRYPTO] : ‖g‖ = {res['norme']:g} → {[round(v, 5) for v in g_norme]} ; par coordonnée"
          f" {g_coord}, angle {res['angle']:.2f}° ; lots écrêtés {res['taux_5']:.0%} (c = 5), {res['taux_3']:.0%} (c = 3)")
    print(f"  pas brut {res['pas_brut']:.2f}, écrêté {res['pas_ecrete']:.2f}, typique {res['pas_typique']:.4f} (médiane {res['mediane']:.2f})")
    return res


def main() -> None:
    L = lambda t1, t2: t1 ** 2 + 3 * t2 ** 2
    g = (2 * 1, 6 * 1)
    print(f"∇L(1, 1) = {g} ; norme {math.hypot(*g):.5f}")
    assert round(math.hypot(*g), 5) == 6.32456 and L(1, 1) == 4
    # film du mécanisme et exemple simple
    assert round(L(1.001, 1), 6) == 4.002001 and round((L(1.001, 1) - 4) / 0.001, 3) == 2.001
    assert round(L(1, 1.001), 6) == 4.006003 and round((L(1, 1.001) - 4) / 0.001, 3) == 6.003
    assert math.isclose(2 * 0.6 + 6 * 0.8, 6) and math.isclose(L(0.8, 0.4), 1.12) and math.isclose(4 - 1.12, 2.88)
    assert math.isclose(0.8 ** 2, 0.64) and math.isclose(3 * 0.4 ** 2, 0.48) and 0.1 * 40 == 4
    # démonstrations 1 et 2 : pente directionnelle, plus forte montée
    h = 1e-6
    for u in ((1, 0), (0.6, 0.8), (-0.8, 0.6)):
        pente = (L(1 + h * u[0], 1 + h * u[1]) - L(1, 1)) / h
        assert math.isclose(pente, 2 * u[0] + 6 * u[1], abs_tol=1e-4) and pente <= math.hypot(2, 6) + 1e-4
    assert [round(2 * u + 6 * v, 5) for u, v in ((1, 0), (0.6, 0.8), (-0.8, 0.6))] == [2, 6, 2]
    d = direction_unitaire(g)
    assert [round(c, 5) for c in d] == [0.31623, 0.94868] and round(2 * d[0] + 6 * d[1], 5) == 6.32456
    assert direction_unitaire((0, 0)) is None
    print(f"démonstrations 1 et 2 : pentes 2, 6, 2 ; direction du gradient {[round(c, 5) for c in d]}, pente 6.32456")
    # démonstration 3 : tangente à la ligne de niveau
    tan = direction_unitaire((6, -2))
    assert [round(c, 5) for c in tan] == [0.94868, -0.31623] and abs(2 * tan[0] + 6 * tan[1]) < 1e-12
    var = [L(1 + t * tan[0], 1 + t * tan[1]) - 4 for t in (0.1, 0.01)]
    assert [round(v, 5) for v in var] == [0.012, 0.00012] and [round(v / t, 3) for v, t in zip(var, (0.1, 0.01))] == [0.12, 0.012]
    print(f"démonstration 3 : le long de la tangente, ΔL = {[round(v, 5) for v in var]} pour t = 0.1 et 0.01")
    # démonstration 4 : règle de la chaîne sur le neurone du cas 1
    w, b, x, y = 0.5, -0.5, 2.0, 1
    gw, gb = gradient(w, b, x, y)
    print(f"neurone : ŷ = {sigma(w * x + b):.5f} ; L = {perte(w, b, x, y):.5f} ; ∂L/∂w = {gw:.5f} ; ∂L/∂b = {gb:.5f}")
    assert round(sigma(0.5), 5) == 0.62246 and round(perte(w, b, x, y), 5) == 0.47408
    assert (round(gw, 5), round(gb, 5)) == (-0.75508, -0.37754)
    assert math.isclose((perte(w + h, b, x, y) - perte(w, b, x, y)) / h, gw, rel_tol=1e-4)
    assert math.isclose((perte(w, b + h, x, y) - perte(w, b, x, y)) / h, gb, rel_tol=1e-4)
    assert round(gradient_mse(w, b, x, y)[0], 5) == -0.17745
    w2, b2 = w - 0.5 * gw, b - 0.5 * gb
    print(f"après un pas : w = {w2:.5f} ; b = {b2:.5f} ; ŷ = {sigma(w2 * x + b2):.5f} ; L = {perte(w2, b2, x, y):.5f}")
    assert (round(w2, 5), round(b2, 5), round(perte(w2, b2, x, y), 5)) == (0.87754, -0.31123, 0.21189)
    # démonstration 5 : saturation de la perte quadratique
    p6 = sigma(-6.0)
    assert round(p6, 7) == 0.0024726 and round(p6 * (1 - p6), 7) == 0.0024665
    assert round(sigma(0.5) * (1 - sigma(0.5)), 5) == 0.235 and round(0.62246 * 0.37754, 5) == 0.235
    assert all(sigma(z) * (1 - sigma(z)) <= 0.25 for z in (-6, -1, 0, 0.5, 3))
    print(f"démonstration 5 : z = −6 → ŷ(1 − ŷ) = {p6 * (1 - p6):.7f} ; gradient quadratique du cas 1 :"
          f" {gradient_mse(w, b, x, y)[0]:.5f} contre {gw:.5f}")
    # démonstration 6 : différences avant et centrée
    avant = [(perte(w + hh, b, x, y) - perte(w, b, x, y)) / hh - gw for hh in (1e-2, 1e-3)]
    centre = [(perte(w + hh, b, x, y) - perte(w - hh, b, x, y)) / (2 * hh) - gw for hh in (1e-2, 1e-3)]
    l2 = x * x * sigma(0.5) * (1 - sigma(0.5))
    assert round(avant[0], 7) == 0.0046923 and round(avant[1], 8) == 0.00046993
    assert round(l2, 5) == 0.94001 and round(1e-2 / 2 * l2, 7) == 0.0047001
    assert round(abs(centre[0]) * 1e6, 3) == 7.674 and round(abs(centre[1]) * 1e8, 3) == 7.674
    assert round(avant[0] / avant[1]) == 10 and round(centre[0] / centre[1]) == 100
    print(f"démonstration 6 : erreur avant {avant[0]:.7f} puis {avant[1]:.8f} ; centrée {centre[0]:.3e} puis {centre[1]:.3e}")

    c1 = cas_1_escalade_banque()
    assert c1["z"] == 0.5 and round(c1["yh"], 5) == 0.62246 and round(c1["L"], 5) == 0.47408
    assert (round(c1["w2"], 5), round(c1["b2"], 5)) == (0.87754, -0.31123) and round(c1["z2"], 5) == 1.44385
    assert round(c1["yh2"], 5) == 0.80905 and round(c1["L2"], 5) == 0.21189 and c1["yh"] < 0.7 <= c1["yh2"]
    assert (round(c1["w_faux"], 5), round(c1["b_faux"], 5), round(c1["z_faux"], 5)) == (0.12246, -0.68877, -0.44385)
    assert round(c1["yh_faux"], 5) == 0.39082 and round(c1["L_faux"], 5) == 0.9395
    assert round(c1["pente_z"], 4) == 1.8877 and round(c1["logit"], 5) == 0.8473 and round(c1["eta_bascule"], 5) == 0.18398
    assert c1["yh_01"] < 0.7 and math.isclose(abs(c1["gw"]), 2 * abs(c1["gb"]))

    c2 = cas_2_fraude_assur()
    assert math.isclose(c2["z"], 0.28) and round(c2["yh"], 5) == 0.56955 and round(c2["s"], 5) == 0.24516
    assert (round(c2["dx1"], 5), round(c2["dx2"], 5)) == (0.2942, 0.19613)
    assert (round(c2["c1"], 2), round(c2["c2"], 2)) == (1.08, 1.2) and c2["c2"] > c2["c1"]
    assert [round(v, 5) for v in c2["g"]] == [0.51259, 0.85432, 0.56955] and c2["ecart_num"] < 1e-6
    assert round(c2["L"], 5) == 0.84292 and [round(v, 5) for v in c2["n"]] == [1.14874, 0.71457, -2.05695]
    assert round(c2["zn"], 5) == 0.04876 and round(c2["yhn"], 5) == 0.51219 and c2["yhn"] >= 0.5
    assert round(c2["un_pct"], 7) == 0.0026478 and round(c2["un_pct_exact"], 7) == 0.0026458
    assert math.isclose(c2["bascule_x2"], 1.15) and math.isclose(1.08 + 1.2 - 2, 0.28)

    c3 = cas_3_saturation_rh()
    assert round(c3["yh"], 7) == 0.0024726 and round(100 * (1 - c3["yh"]), 2) == 99.75
    assert round(c3["g_ce"], 5) == -1.49629 and round(c3["g_mse"], 7) == -0.0036906
    assert round(c3["g_ce"] / c3["g_mse"], 1) == 405.4 and (c3["pas_ce"], c3["pas_mse"]) == (4, 263)
    assert round(c3["p_seuil"], 6) == 0.010102 and round(c3["z_seuil"], 5) == -4.58486
    assert round(263 / 4) == 66 and round(c3["facteur_z2"], 5) == 0.10499

    c4 = cas_4_ecretage_crypto()
    assert c4["norme"] == 13 and round(c4["facteur"], 5) == 0.38462
    assert [round(v, 5) for v in c4["g_norme"]] == [1.15385, -1.53846, 4.61538] and math.isclose(c4["cos_norme"], 1)
    assert c4["g_coord"] == [3.0, -4.0, 5.0] and round(c4["norme_coord"], 5) == 7.07107
    assert round(c4["cos_coord"], 5) == 0.92468 and round(c4["angle"], 2) == 22.38
    assert c4["taux_5"] == 0.1 and c4["taux_3"] == 0.3 and c4["mediane"] == 2.55
    assert math.isclose(c4["pas_brut"], 0.13) and math.isclose(c4["pas_ecrete"], 0.05) and math.isclose(c4["pas_typique"], 0.0255)
    assert round(c4["pas_brut"] / c4["pas_typique"], 1) == 5.1 and c4["g_coord"][2] / 12 < 0.5
    assert math.isclose(math.sqrt(sum(v * v for v in c4["g_norme"])), 5)

    print("Corrigé")
    z = 0.37
    ex6 = gradient(0.5, -0.5, 3.0, 1)
    print(f"  ex1 (6 ; 5) ; ex2 {2 * 1 + 6 * 0} et {2 * 0.6 + 6 * 0.8:.1f} ; ex4 {[round(v, 5) for v in gradient(w, b, x, 0)]} ;"
          f" ex6 ŷ = {sigma(1.0):.5f}, {[round(v, 5) for v in ex6]}")
    ex1 = gradient_numerique(lambda t: 2 * t[0] ** 2 + t[0] * t[1] + t[1] ** 2, [1.0, 2.0])
    assert all(math.isclose(a, c, abs_tol=1e-6) for a, c in zip(ex1, [6, 5]))           # exercice 1
    assert math.isclose((sigma(z + h) - sigma(z)) / h, sigma(z) * (1 - sigma(z)), rel_tol=1e-4)   # exercice 3
    assert [round(v, 5) for v in gradient(w, b, x, 0)] == [1.24492, 0.62246]
    assert round(sigma(1.0), 5) == 0.73106 and [round(v, 5) for v in ex6] == [-0.80682, -0.26894]
    try:
        gradient_numerique(L, [1.0, 1.0], 0.0)
    except ValueError:
        print("  h = 0 refusé : ValueError")
    else:
        raise AssertionError("h = 0 aurait dû être refusé")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
∇L(1, 1) = (2, 6) ; norme 6.32456
démonstrations 1 et 2 : pentes 2, 6, 2 ; direction du gradient [0.31623, 0.94868], pente 6.32456
démonstration 3 : le long de la tangente, ΔL = [0.012, 0.00012] pour t = 0.1 et 0.01
neurone : ŷ = 0.62246 ; L = 0.47408 ; ∂L/∂w = -0.75508 ; ∂L/∂b = -0.37754
après un pas : w = 0.87754 ; b = -0.31123 ; ŷ = 0.80905 ; L = 0.21189
démonstration 5 : z = −6 → ŷ(1 − ŷ) = 0.0024665 ; gradient quadratique du cas 1 : -0.17745 contre -0.75508
démonstration 6 : erreur avant 0.0046923 puis 0.00046993 ; centrée -7.674e-06 puis -7.674e-08
Cas 1 [BANQUE] : ŷ = 0.62246 → après un pas ŷ = 0.80905 (seuil 0.7) ; erreur de signe ŷ = 0.39082 ; η de bascule 0.18398
  z après un pas = 0.5 + 1.8877 η ; seuil logit(0.7) = 0.84730 ; avec η = 0.1 : ŷ = 0.66569
Cas 2 [ASSUR] : ŷ = 0.56955 ; ∂ŷ/∂x = (0.29420 ; 0.19613) ; contributions 1.08 et 1.20 ; après correction ŷ = 0.51219
  ∇L = [0.51259, 0.85432, 0.56955] (écart aux différences centrées < 1e-6) ; bascule x2 = 1.15
Cas 3 [RH] : ŷ = 0.0024726 ; gradients -1.49629 (entropie croisée) et -0.0036906 (quadratique) ; pas jusqu'à ŷ ≥ 0.5 : 4 contre 263
  saturation : facteur ŷ(1 − ŷ) < 1 % dès que |z| > 4.58486 ; à z = −2 il vaut 0.10499
Cas 4 [CRYPTO] : ‖g‖ = 13 → [1.15385, -1.53846, 4.61538] ; par coordonnée [3.0, -4.0, 5.0], angle 22.38° ; lots écrêtés 10% (c = 5), 30% (c = 3)
  pas brut 0.13, écrêté 0.05, typique 0.0255 (médiane 2.55)
Corrigé
  ex1 (6 ; 5) ; ex2 2 et 6.0 ; ex4 [1.24492, 0.62246] ; ex6 ŷ = 0.73106, [-0.80682, -0.26894]
  h = 0 refusé : ValueError
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme calcule le gradient d'un neurone par la règle de la chaîne, le vérifie par différences finies, fait un pas de descente, et écrête la norme d'un gradient trop grand.

```text
ALGORITHME GradientDUnNeurone
ENTRÉES : poids w, biais b, entrée x, étiquette y, pas η
SORTIE  : (perte, gradients, nouveaux paramètres)

  z ← w × x + b
  ŷ ← 1 / (1 + exp(−z))
  L ← −(y × ln ŷ + (1 − y) × ln(1 − ŷ))
  ∂L/∂w ← (ŷ − y) × x
  ∂L/∂b ← ŷ − y
  w ← w − η × ∂L/∂w
  b ← b − η × ∂L/∂b
  RETOURNER L, (∂L/∂w, ∂L/∂b), (w, b)

ALGORITHME VérifierParDifférencesFinies
ENTRÉES : fonction L, point θ, pas h > 0
SORTIE  : le gradient approché, à comparer au gradient calculé
  SI h ≤ 0 ALORS ERREUR « pas invalide »
  POUR CHAQUE paramètre θᵢ FAIRE
      gᵢ ← (L(θ + h eᵢ) − L(θ − h eᵢ)) / (2h)
  FIN POUR
  RETOURNER g

ALGORITHME ÉcrêterLaNorme
ENTRÉES : gradient g, seuil c > 0
SORTIE  : gradient de même direction et de norme au plus c
  n ← ‖g‖
  SI n ≤ c ALORS RETOURNER g
  RETOURNER g × c / n
```

**Complexité.** O(1) pour un neurone. Pour un réseau de P paramètres, la rétropropagation coûte du même ordre qu'un calcul de la perte, alors que la vérification par différences finies coûte 2P calculs de la perte : on ne l'utilise que pour tester. L'écrêtage par la norme coûte O(P) : une norme et une multiplication par coordonnée.

**Du squelette au code.** Le neurone est `sigma`, la perte `perte(w, b, x, y)`, les gradients `gradient(w, b, x, y)` ; la variante quadratique est `perte_mse(w, b, x, y)` et `gradient_mse(w, b, x, y)`. La vérification est faite dans `main` avec `h = 1e-6`, et en version centrée par `gradient_numerique(f, theta, h)`, puis le pas avec η = 0,5 donne `w2` et `b2`. ÉcrêterLaNorme est `ecretage_norme(g, c)`, et la direction d'un vecteur est `direction_unitaire(v)`, qui renvoie `None` pour le vecteur nul. Les quatre cas sont `cas_1_escalade_banque`, `cas_2_fraude_assur`, `cas_3_saturation_rh` et `cas_4_ecretage_crypto`.
