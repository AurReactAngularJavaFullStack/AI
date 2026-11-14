# 19 — REINFORCE : démonstrations

> Fiche : [19 — REINFORCE](<../../Images/06-Decision/19_reinforce.md>) · Image : `19_reinforce.jpg` · Leçon : [Étape 38 — MDP et équation de Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)

Ouvrir la fiche ou l'image à gauche, ce fichier à droite. Chaque démonstration se refait sur une feuille A4.

## La formule

$$
\nabla_\theta J(\theta) = \mathbb{E}\left[ \nabla_\theta \log \pi_\theta(a \mid s) \times R \right]
$$

La politique πθ donne une probabilité à chaque action, selon des paramètres θ. J(θ) est la récompense moyenne obtenue. La formule dit comment changer θ pour que J monte, en n'utilisant que des actions jouées et leurs récompenses. On **monte** le gradient (θ ← θ + η × estimation), à l'inverse de la descente de gradient sur une perte.

## Les symboles, un par un

$$
\theta
$$

Les paramètres de la politique : ici un nombre réel par action (un « logit »), sans borne ; la liste `theta` du programme.

$$
\pi_\theta(a \mid s)
$$

La probabilité que la politique choisisse l'action a dans l'état s ; un nombre de ]0 ; 1[ pour une softmax, de somme 1 sur les actions ; la liste `pi = softmax(theta)`.

$$
\log \pi_\theta(a \mid s)
$$

Le logarithme de cette probabilité, la log-vraisemblance de l'action jouée ; un réel ≤ 0 ; son gradient est `grad_log(theta, a)`.

$$
\nabla_\theta
$$

Le gradient par rapport aux paramètres : la liste des dérivées partielles, une par coordonnée de θ (fiche 34) ; une liste de même longueur que `theta`.

$$
R
$$

La récompense, ou le retour, reçu après l'action ; un réel, en points ; la liste `RECOMPENSES` (1 pour l'outil 1, 0,2 pour l'outil 2) ou les récompenses de chaque cas.

$$
J(\theta)
$$

L'objectif à maximiser : la récompense moyenne sous la politique, J(θ) = Σₐ πθ(a) R(a) dans un seul état ; même unité que R ; la quantité `J` de `demo_1_log`.

$$
\mathbb{E}
$$

L'espérance sur les actions tirées par la politique (fiche 22) ; un opérateur ; dans le programme, une somme pondérée par `pi`, comme dans `gradient_exact`.

$$
b
$$

La ligne de base : une constante retirée de R, qui ne change pas le gradient moyen mais réduit sa variance ; un réel ; l'argument `b` de `gradient_exact` et la variable `moy` (récompense moyenne) de la boucle d'apprentissage.

$$
\eta
$$

Le pas de la montée de gradient ; un réel > 0 (0,1 ou 0,5 ici) ; le facteur `0.5` ou `0.1` des mises à jour, l'argument `eta` d'`entrainer`.

$$
A = R - b
$$

L'avantage : de combien la récompense dépasse la ligne de base ; positif, l'action est renforcée ; négatif, elle est affaiblie (fiche 19a) ; l'expression `RECOMPENSES[a] - moy` du programme.

## Le mécanisme, avant les preuves

La formule reçoit des paramètres θ, une action a tirée selon la politique et la récompense R qui a suivi. La softmax transforme θ en probabilités : elle prend l'exponentielle de chaque paramètre, ce qui rend tout positif, puis divise par la somme, ce qui donne un total de 1. Le gradient de log π(a) vaut, pour une softmax, « 1 sur l'action jouée, 0 ailleurs » moins le vecteur π : il pousse vers le haut le paramètre de l'action jouée et vers le bas les autres, chacune d'autant plus qu'elle était probable. La multiplication par R (ou par R − b) décide du sens et de la force : une récompense au-dessus de la ligne de base renforce l'action, une récompense en dessous l'affaiblit. La moyenne de ces produits sur beaucoup de tirages donne le vrai gradient de J ; une seule estimation est très bruitée. On met un logarithme parce que ∇log π = ∇π/π : une action souvent tirée reçoit beaucoup de petites poussées, une action rare en reçoit peu mais de grandes, et ce rapport 1/π compense exactement la fréquence de tirage, ce qui rend l'estimation sans biais (démonstration 1). On retire une ligne de base parce que seule la différence entre les récompenses des actions compte : la partie commune n'apporte que du bruit (démonstrations 3 et 5). Enfin, on ajoute η fois l'estimation à θ, car on cherche à monter. Ce qui sort, ce sont de nouveaux paramètres, donc une nouvelle politique, un peu plus portée sur ce qui a bien marché. L'agent n'a jamais besoin de connaître les règles de l'environnement : seulement les actions qu'il a jouées et les récompenses reçues.

**Petit film chiffré** (exemple simple : θ = (0 ; 0), l'agent joue l'action 1 et reçoit R = 1, pas η = 0,1).

| Opération | Coordonnée 1 | Coordonnée 2 |
|---|---|---|
| θ | 0 | 0 |
| softmax : π | e⁰/(e⁰ + e⁰) = 0,5 | 0,5 |
| ∇log π(1) = (1 ; 0) − π | 1 − 0,5 = 0,5 | 0 − 0,5 = −0,5 |
| × R = 1 | 0,5 | −0,5 |
| × η = 0,1 | 0,05 | −0,05 |
| θ + pas | 0,05 | −0,05 |
| nouvelle π | 1,05127/2,00250 = 0,52498 | 0,47502 |

Une seule récompense a déplacé 2,5 points de probabilité vers l'action 1.

## Démonstration 1 — L'astuce du logarithme

**Ce qu'on démontre.** Dans un seul état, avec J(θ) = Σₐ πθ(a) R(a), le gradient de J est une espérance sous la politique, donc estimable en jouant :

$$
\nabla J = \sum_a \nabla \pi_\theta(a)\, R(a) = \sum_a \pi_\theta(a)\, \nabla \log \pi_\theta(a)\, R(a) = \mathbb{E}_{a \sim \pi_\theta}\left[ \nabla \log \pi_\theta(a)\, R(a) \right]
$$

**L'idée.** Le gradient de J est une somme sur toutes les actions, impossible à calculer quand les actions sont des phrases. En multipliant et divisant par π(a), on la transforme en moyenne sous π : il suffit alors de tirer des actions et de faire la moyenne de ∇log π(a) × R.

**La preuve, pas à pas.**

**Étape 1.** On dérive J terme à terme, parce que la dérivée d'une somme est la somme des dérivées et que R(a) ne dépend pas de θ : ∇J = Σₐ ∇π(a) R(a).

**Étape 2.** On utilise la dérivée du logarithme, ∇log π = ∇π/π, donc ∇π = π ∇log π (permis parce que π(a) > 0 pour une softmax) :

$$
\nabla \pi_\theta(a) = \pi_\theta(a)\, \nabla \log \pi_\theta(a)
$$

**Étape 3.** On remplace dans l'étape 1 : la somme pondérée par π(a) est, par définition, l'espérance sous π (fiche 22). ∎

**Vérification chiffrée.** Deux outils, R = (1 ; 0,2), θ = (0 ; 0). Par la formule : 0,5 × 0,5 × 1 + 0,5 × (−0,5) × 0,2 = 0,25 − 0,05 = 0,2. Directement : J = π₁ × 1 + π₂ × 0,2 et ∂J/∂θ₁ = π₁π₂ × (1 − 0,2) = 0,25 × 0,8 = 0,2 ; le programme le confirme par différences finies (0,2000). **Contre-exemple sans le logarithme :** si l'on fait la moyenne sous π de ∇π(a) × R au lieu de ∇log π(a) × R, on obtient 0,5 × 0,25 × 1 + 0,5 × (−0,25) × 0,2 = 0,125 − 0,025 = 0,1 : la moitié seulement du vrai gradient, parce que chaque terme est compté une fois de trop avec le poids π.

**Ce que la preuve révèle du mécanisme.** Le facteur 1/π caché dans ∇log π corrige la fréquence de tirage : sans lui, les actions fréquentes compteraient deux fois, par leur fréquence et par leur poids. La formule n'utilise ni les probabilités de l'environnement ni la dérivée de R : R peut venir d'un humain, d'un test ou d'un juge.

**Conséquence pour un agent.** On peut améliorer une politique avec des récompenses non dérivables (succès d'un appel d'outil, note d'un relecteur), à condition de connaître log π(a) de l'action jouée, ce que fournit un modèle de langage pour chaque jeton généré.

## Démonstration 2 — Le gradient du log pour une politique softmax

**Ce qu'on démontre.** Si πθ = softmax(θ), la dérivée de log π(a) par rapport au paramètre de l'action b vaut :

$$
\log \pi(a) = \theta_a - \log \sum_{c} e^{\theta_c}, \qquad \frac{\partial \log \pi(a)}{\partial \theta_b} = \mathbb{1}[a = b] - \pi(b)
$$

et la somme des coordonnées de ce gradient est nulle.

**L'idée.** log π(a) est le paramètre de a moins un terme commun à toutes les actions. Le premier se dérive en 1 ou 0 ; le terme commun se dérive en π(b), la part de l'action b dans la somme.

**La preuve, pas à pas.**

**Étape 1.** On prend le logarithme de π(a), quotient de exp(θₐ) par la somme des exponentielles de tous les paramètres ; le logarithme d'un quotient est la différence des logarithmes, et log exp(θₐ) = θₐ : on obtient l'égalité de gauche.

**Étape 2.** La dérivée de θₐ par rapport au paramètre de b vaut 1 si a = b, 0 sinon : c'est l'indicatrice 𝟙[a = b].

**Étape 3.** La dérivée de log S, avec S = Σ e^θ꜀, vaut S′/S (dérivée du logarithme), et seule l'exponentielle de b dépend du paramètre de b :

$$
\frac{\partial}{\partial \theta_b} \log \sum_{c} e^{\theta_c} = \frac{e^{\theta_b}}{\sum_{c} e^{\theta_c}} = \pi(b)
$$

**Étape 4.** On soustrait : 𝟙[a = b] − π(b). En sommant sur b : 1 − Σ π(b) = 1 − 1 = 0. ∎

**Vérification chiffrée.** θ = (0,3 ; −0,4 ; 0,8) : exp(0,3) + exp(−0,4) + exp(0,8) = 4,2457, d'où π = (0,31793 ; 0,15788 ; 0,52418). Pour l'action 1 : ∇log π(1) = (1 − 0,31793 ; −0,15788 ; −0,52418) = (0,68207 ; −0,15788 ; −0,52418), de somme 0. Le programme compare chaque coordonnée à une dérivée numérique.

**Ce que la preuve révèle du mécanisme.** L'action jouée voit son paramètre monter de 1 − π(a), les autres descendre de leur probabilité : une action déjà très probable n'est presque plus poussée (1 − π(a) proche de 0). Comme la somme est nulle, ajouter une même constante à tous les paramètres ne change pas π : seuls les écarts entre paramètres comptent.

**Conséquence pour un agent.** Le terme 1 − π(a) freine naturellement une politique qui devient déterministe, mais il freine aussi la sortie d'une mauvaise politique trop sûre d'elle (démonstration 6) : on garde une part d'exploration, ou une borne sur π.

## Démonstration 3 — Une ligne de base ne biaise pas le gradient

**Ce qu'on démontre.** Pour toute constante b qui ne dépend pas de l'action tirée :

$$
\mathbb{E}\left[ \nabla \log \pi(a)\, b \right] = b \sum_a \nabla \pi(a) = b\, \nabla \sum_a \pi(a) = b\, \nabla 1 = 0
$$

On peut donc remplacer R par R − b sans changer le gradient moyen.

**L'idée.** Les probabilités somment toujours à 1, quelle que soit θ : leur somme ne peut pas avoir de pente. Une récompense constante ne dit rien sur quelle action est meilleure.

**La preuve, pas à pas.**

**Étape 1.** On écrit l'espérance comme une somme pondérée par π et on sort la constante b, parce qu'elle ne dépend pas de a : b Σₐ π(a) ∇log π(a).

**Étape 2.** On remplace π ∇log π par ∇π (démonstration 1, étape 2), puis on échange somme et gradient, parce que la somme est finie : b ∇ Σₐ π(a).

**Étape 3.** Σₐ π(a) = 1 pour tout θ, donc son gradient est nul, et le produit aussi. Par linéarité, 𝔼[∇log π (R − b)] = 𝔼[∇log π R] − 0. ∎

**Vérification chiffrée.** Deux outils, R = (1 ; 0,2), θ = (0 ; 0), première coordonnée. Sans ligne de base, une estimation à un tirage vaut 0,5 × 1 = 0,5 (outil 1 joué) ou −0,5 × 0,2 = −0,1 (outil 2) : moyenne 0,2, variance 0,5 × 0,3² + 0,5 × 0,3² = 0,09. Avec b = 0,6, elle vaut 0,5 × 0,4 = 0,2 ou −0,5 × (−0,4) = 0,2 : toujours 0,2, variance nulle. Avec b = 0,2 : 0,4 ou 0, moyenne 0,2, variance 0,04. **Contre-exemple si b dépend de l'action :** avec b(a) = R(a), chaque estimation vaut 0 et la moyenne aussi, au lieu de 0,2 : l'hypothèse « b ne dépend pas de a » est indispensable.

**Ce que la preuve révèle du mécanisme.** La ligne de base déplace toutes les récompenses ensemble ; elle ne change donc pas leur classement, mais elle change le signe des poussées. Sans ligne de base, avec des récompenses toutes positives, chaque action jouée est renforcée, même la moins bonne ; seule la différence de fréquence de renforcement fait le tri.

**Conséquence pour un agent.** On retire toujours une ligne de base qui ne dépend que de l'état : la récompense moyenne récente, ou mieux la ligne de base de la démonstration 5. Le terme R − b est l'avantage (fiche 19a).

## Démonstration 4 — La mise à jour renforce ce qui a bien marché

**Ce qu'on démontre.** Avec la mise à jour θ ← θ + η ∇log π(a)(R − b), η > 0 : si R > b, la probabilité de l'action jouée augmente ; si R < b, elle diminue ; si R = b, rien ne change.

$$
\theta \leftarrow \theta + \eta\, (R - b)\, \nabla_\theta \log \pi_\theta(a)
$$

**L'idée.** ∇log π(a) est la direction qui augmente le plus vite log π(a). Avancer dans cette direction, avec un coefficient positif, rend a plus probable ; avec un coefficient négatif, moins probable.

**La preuve, pas à pas.**

**Étape 1.** Au premier ordre, la variation de log π(a) vaut le produit scalaire du gradient et du déplacement, parce qu'un gradient donne la pente dans chaque direction :

$$
\Delta \log \pi(a) \approx \nabla \log \pi(a) \cdot \Delta\theta = \eta\, (R - b)\, \lVert \nabla \log \pi(a) \rVert^2
$$

**Étape 2.** η > 0 et ‖∇log π(a)‖² > 0 tant que π(a) < 1 (démonstration 2), donc le signe de Δlog π(a) est celui de R − b ; et log est croissant, donc π(a) varie dans le même sens. ∎

**Vérification chiffrée.** Exemple simple : R − b = 1 − 0 > 0, et π(1) passe de 0,5 à 0,52498. Si l'agent joue l'action 2 depuis θ = (0,05 ; −0,05) et reçoit 0 sans ligne de base, R − b = 0 et θ ne change pas (exercice 4). Sur les deux outils, 200 pas de taille 0,5 avec la ligne de base moyenne portent la probabilité de l'outil 1 à 0,9934 (cas 1).

**Ce que la preuve révèle du mécanisme.** L'agent n'a pas besoin de connaître les règles de l'environnement, seulement les récompenses. Mais il renforce exactement ce que la récompense mesure : si elle mesure autre chose que la tâche, il renforce l'autre chose (cas 3).

**Conséquence pour un agent.** Le barème de récompense se relit et se teste comme du code, avec des cas où l'on connaît la bonne action. On suit aussi un indicateur indépendant de la récompense, pour détecter un raccourci appris.

## Démonstration 5 — La meilleure ligne de base constante, à deux actions

**Ce qu'on démontre.** À deux actions, pour la coordonnée 1 de l'estimation à un tirage X = ∂log π(a)/∂θ₁ × (R(a) − b), la variance vaut :

$$
\operatorname{Var}(X) = \pi_1 \pi_2 \left( b^{*} - b \right)^2, \qquad b^{*} = \pi_2 R_1 + \pi_1 R_2
$$

La meilleure ligne de base est b*, la moyenne des récompenses avec les probabilités **inversées** ; elle annule la variance. Elle ne coïncide avec la récompense moyenne π₁R₁ + π₂R₂ que si π₁ = π₂.

**L'idée.** X ne prend que deux valeurs, une par action. La variance d'une variable à deux valeurs est p(1 − p) fois le carré de leur écart, et cet écart est une fonction affine de b, qui s'annule en b*.

**La preuve, pas à pas.**

**Étape 1.** Par la démonstration 2 : si l'action 1 est jouée, X = (1 − π₁)(R₁ − b) = π₂(R₁ − b) ; si l'action 2 est jouée, X = −π₁(R₂ − b).

**Étape 2.** Une variable qui vaut x₁ avec la probabilité π₁ et x₂ avec π₂ a pour variance π₁π₂(x₁ − x₂)², parce que sa moyenne est π₁x₁ + π₂x₂ et que x₁ − moyenne = π₂(x₁ − x₂), x₂ − moyenne = −π₁(x₁ − x₂).

**Étape 3.** On calcule l'écart, en utilisant π₁ + π₂ = 1 :

$$
x_1 - x_2 = \pi_2 (R_1 - b) + \pi_1 (R_2 - b) = \pi_2 R_1 + \pi_1 R_2 - b = b^{*} - b
$$

**Étape 4.** La variance π₁π₂(b* − b)² est un carré, minimal et nul en b = b*. ∎

**Vérification chiffrée.** Avec π = (0,5 ; 0,5) : b* = 0,5 × 1 + 0,5 × 0,2 = 0,6, la récompense moyenne, et l'on retrouve 0,25 × 0,6² = 0,09 pour b = 0 et 0,25 × 0,4² = 0,04 pour b = 0,2. **Contre-exemple : la récompense moyenne n'est pas toujours une bonne ligne de base.** Avec π = (0,8 ; 0,2) : b* = 0,2 × 1 + 0,8 × 0,2 = 0,36, alors que la moyenne vaut 0,8 × 1 + 0,2 × 0,2 = 0,84. Variances : sans ligne de base, 0,16 × 0,36² = 0,020736 ; avec la moyenne, 0,16 × (0,36 − 0,84)² = 0,16 × 0,48² = 0,036864, pire que sans ; avec b*, 0.

**Ce que la preuve révèle du mécanisme.** L'action rare reçoit une grande poussée (−π₁ = −0,8 sur la coordonnée 1) et l'action fréquente une petite (π₂ = 0,2) : la meilleure ligne de base est celle qui égalise les deux poussées, ce qui donne plus de poids à la récompense de l'action rare. Toute ligne de base entre 0 et 2b* fait mieux que l'absence de ligne de base, puisque |b* − b| < b* exactement sur cet intervalle.

**Conséquence pour un agent.** La récompense moyenne est un bon choix par défaut quand la politique est encore équilibrée ; quand elle devient très déséquilibrée, on estime la ligne de base pondérée par ‖∇log π‖² (à deux actions, b*), ou l'on apprend une fonction de valeur V(s) qui joue ce rôle.

## Démonstration 6 — La dynamique à deux actions : rapide au milieu, lente aux bords

**Ce qu'on démontre.** À deux actions, avec le gradient exact (quelle que soit la ligne de base, d'après la démonstration 3), l'écart d = θ₁ − θ₂ augmente à chaque pas de :

$$
\Delta d = 2\, \eta\, (R_1 - R_2)\, \pi_1\, \pi_2, \qquad \pi_1 = \frac{1}{1 + e^{-d}}
$$

L'apprentissage est le plus rapide à π₁ = 0,5 et ralentit sans fin près de 0 et de 1 : la politique ne devient jamais tout à fait déterministe, et une politique presque sûre de la mauvaise action en sort aussi lentement qu'une bonne politique s'en approche.

**L'idée.** Le gradient exact vaut π₁π₂(R₁ − R₂) sur la coordonnée 1 et l'opposé sur la coordonnée 2. Le produit π₁π₂ est maximal à 0,5 × 0,5 et tend vers 0 quand une action prend toute la probabilité.

**La preuve, pas à pas.**

**Étape 1.** J = π₁R₁ + π₂R₂ ; par la démonstration 1, ∂J/∂θ₁ = π₁(1 − π₁)R₁ − π₁π₂R₂ = π₁π₂(R₁ − R₂), parce que 1 − π₁ = π₂.

**Étape 2.** Par symétrie, ∂J/∂θ₂ = −π₁π₂(R₁ − R₂) ; un pas de montée ajoute η fois ces valeurs, donc d augmente de 2ηπ₁π₂(R₁ − R₂).

**Étape 3.** Pour une softmax à deux actions, π₁ = exp(θ₁)/(exp(θ₁) + exp(θ₂)) = 1/(1 + exp(−d)), la fonction logistique de d ; π₁π₂ ≤ 1/4, avec égalité en π₁ = 0,5, et π₁π₂ → 0 quand d → ±∞. ∎

**Vérification chiffrée.** R = (1 ; 0,2), η = 0,5 : au départ, Δd = 2 × 0,5 × 0,8 × 0,25 = 0,2, donc θ = (0,1 ; −0,1) et π₁ = 1/(1 + exp(−0,2)) = 0,54983. À π₁ = 0,99, Δd = 2 × 0,5 × 0,8 × 0,99 × 0,01 = 0,00792 seulement. Il faut 134 pas pour aller de π₁ = 0,5 à 0,99, et 137 pour remonter de π₁ = 0,01, une politique presque sûre de la mauvaise action, jusqu'à 0,5.

**Ce que la preuve révèle du mécanisme.** Le facteur π₁π₂ est le même que la variance d'un tirage de Bernoulli : quand la politique ne tire presque plus une action, elle n'apprend presque plus rien sur elle. C'est le lien entre exploration et apprentissage.

**Conséquence pour un agent.** On ne laisse pas une politique s'effondrer trop tôt : on garde une part d'exploration (une probabilité minimale par action, ou un bonus d'entropie, fiche 21) et l'on surveille π de chaque action.

## Exemple simple, à la main

Deux actions, θ = (0 ; 0), donc π = (0,5 ; 0,5). L'agent joue l'action 1 et reçoit R = 1.

**Étape 1.** Probabilités : e⁰ = 1 pour chaque action, donc π = (1/2 ; 1/2) = (0,5 ; 0,5).

**Étape 2.** Gradient du log (démonstration 2) : (1 − 0,5 ; 0 − 0,5) = (0,5 ; −0,5).

$$
\nabla \log \pi(1) = (1 - 0{,}5\ ;\ -0{,}5) = (0{,}5\ ;\ -0{,}5)
$$

**Étape 3.** Pas : η × R × gradient = 0,1 × 1 × (0,5 ; −0,5) = (0,05 ; −0,05), donc θ devient (0,05 ; −0,05).

**Étape 4.** Nouvelle probabilité : exp(0,05) ≈ 1,05127 et exp(−0,05) ≈ 0,95123, de somme 2,00250, d'où :

$$
\pi(1) = \frac{e^{0{,}05}}{e^{0{,}05} + e^{-0{,}05}} \approx 0{,}52498
$$

| Quantité | Calcul | Valeur |
|---|---|---|
| π avant | 1/(1 + 1) | 0,5 et 0,5 |
| ∇log π(1) | (1 ; 0) − (0,5 ; 0,5) | 0,5 et −0,5 |
| pas | 0,1 × 1 × (0,5 ; −0,5) | 0,05 et −0,05 |
| π(1) après | 1,05127/2,00250 | 0,52498 |

## Cas d'usage complexes, démontrés

Les récompenses, probabilités, coûts et volumes des quatre cas sont illustratifs. Tous les calculs sont exacts (espérances calculées sur toutes les actions) : le programme n'a pas besoin de tirage aléatoire.

### Cas 1 — Banque de détail [BANQUE] : apprendre à router les pièces d'identité vers le bon outil d'extraction

**Contexte.** Une banque de détail de Dubaï reçoit environ 20 000 pièces d'identité par mois pour l'ouverture de comptes et la mise à jour KYC (volume illustratif). Un agent choisit, pour chaque document, l'un de deux outils d'extraction. L'outil 1 extrait tous les champs (récompense 1) ; l'outil 2 n'en extrait qu'une partie (récompense 0,2), et un employé complète le reste à la main. La politique est une softmax entraînée par REINFORCE sur un jeu de documents de test anonymisés.

**Données.**

- Récompenses : outil 1, 1 ; outil 2, 0,2. Politique de départ θ = (0 ; 0), soit 50/50.
- Précision voulue pour une estimation du gradient : ±0,02 à deux écarts-types.
- Apprentissage : 200 pas de gradient exact, η = 0,5, ligne de base égale à la récompense moyenne.
- Complétion manuelle : (1 − R) × 15 AED par document, soit 12 AED quand l'outil 2 est utilisé.
- Volume : 20 000 documents par mois.

**Calcul pas à pas.**

**Étape 1.** Gradient exact au départ (démonstration 1) : 0,2 sur la coordonnée 1.

**Étape 2.** Écart-type d'une estimation à un tirage (démonstrations 3 et 5) : 0,3 sans ligne de base, 0,2 avec b = 0,2, 0 avec b = 0,6. Nombre de tirages pour atteindre ±0,02 à deux écarts-types :

$$
N = \left( \frac{2\, \sigma}{0{,}02} \right)^2 : \quad \sigma = 0{,}3 \Rightarrow N = 30^2 = 900, \qquad \sigma = 0{,}2 \Rightarrow N = 20^2 = 400
$$

et un seul tirage suffit avec b = 0,6.

**Étape 3.** 200 pas de montée avec la ligne de base moyenne : π(outil 1) = 0,9934, et J = 0,2 + 0,8 × 0,9934 = 0,99475 (0,99 est atteint au 134ᵉ pas, démonstration 6).

**Étape 4.** Coût de complétion manuelle : politique 50/50, 0,5 × 12 × 20 000 = 120 000 AED par mois ; politique apprise, environ 0,0066 × 12 = 0,079 AED par document, soit 1 574 AED par mois.

**Décision de l'agent.** Le seuil de décision est π(outil 1) ≥ 0,99 : la politique apprise route 99,34 % des documents vers l'outil 1, et l'outil 2 ne sert plus qu'en secours.

**Contre-calcul.** Sans ligne de base, chaque pas de gradient fiable demande 900 documents au lieu d'un seul (b = 0,6 au départ) : pour 134 pas, plus de 120 000 documents de test, six mois de volume. Garder la politique 50/50 coûterait 120 000 − 1 574 = 118 426 AED par mois de saisie manuelle (illustratif).

**Sensibilité.** Avec un pas η = 0,25 au lieu de 0,5, il faut 269 pas au lieu de 134 pour atteindre 0,99 : le nombre de pas est inversement proportionnel à η, au premier ordre. Une ligne de base mal choisie (b = 0,2 au lieu de 0,6) multiplie par 400 le nombre de tirages par pas précis.

**En production.** Indicateur : le taux de complétion manuelle ; alerte au-dessus de 2 %. Contrôle déterministe : un Emirates ID extrait doit avoir 15 chiffres et commencer par 784, sinon la récompense vaut 0 quelle que soit l'opinion du modèle. Contraintes : les exigences KYC et de lutte contre le blanchiment de la CBUAE s'appliquent ; l'entraînement se fait sur des documents de test anonymisés, et les données réelles relèvent de la PDPL, sauf en zone DIFC ou ADGM, qui ont leurs propres lois.

### Cas 2 — Assureur auto et santé [ASSUR] : choisir la ligne de base d'une politique déjà déséquilibrée

**Contexte.** Un assureur auto de Dubaï a entraîné un agent qui, pour chaque petit sinistre, demande des photos par l'application (action 1, récompense 1 : dossier complet vite) ou propose un rendez-vous dans un garage partenaire (action 2, récompense 0,2). La politique joue déjà l'action 1 dans 80 % des cas. L'équipe veut continuer l'entraînement et se demande quelle ligne de base utiliser, et combien de sinistres collecter par mise à jour. Volume illustratif : 60 sinistres par jour.

**Données.**

- Récompenses : R = (1 ; 0,2).
- Politique actuelle : θ = (ln 4 ; 0), soit π = (4/5 ; 1/5) = (0,8 ; 0,2).
- Précision voulue : ±10 % du gradient, à deux écarts-types.
- Lignes de base candidates : aucune (b = 0), la récompense moyenne, la ligne de base optimale b*.
- Volume : 60 sinistres par jour.

**Calcul pas à pas.**

**Étape 1.** Gradient exact (démonstration 6) : π₁π₂(R₁ − R₂) = 0,8 × 0,2 × 0,8 = 0,128 ; précision voulue ±0,0128.

**Étape 2.** Lignes de base (démonstration 5) : moyenne 0,8 × 1 + 0,2 × 0,2 = 0,84 ; b* = 0,2 × 1 + 0,8 × 0,2 = 0,36.

**Étape 3.** Écarts-types d'un tirage : sans ligne de base, √(0,16 × 0,36²) = √0,020736 = 0,144 ; avec la moyenne, √0,036864 = 0,192 ; avec b*, 0.

**Étape 4.** Sinistres nécessaires par mise à jour précise :

$$
N = \left( \frac{2\, \sigma}{0{,}0128} \right)^2 : \quad \sigma = 0{,}144 \Rightarrow N = 22{,}5^2 = 506{,}25, \qquad \sigma = 0{,}192 \Rightarrow N = 30^2 = 900
$$

soit 507 sinistres (8,45 jours de collecte) sans ligne de base, et 900 (15 jours) avec la récompense moyenne.

**Décision de l'agent.** L'équipe utilise une ligne de base estimée près de b* = 0,36, pas la récompense moyenne : la variance d'un tirage devient presque nulle, et la collecte ne sert plus qu'à estimer b* lui-même, au lieu de 507 ou 900 sinistres par mise à jour.

**Contre-calcul.** Le réflexe « ligne de base = récompense moyenne » ferait collecter 15 jours de sinistres par mise à jour au lieu de 8,45 sans aucune ligne de base : 6,55 jours perdus à chaque pas, pour une variance 1,78 fois plus grande (0,036864/0,020736).

**Sensibilité.** Valeur de bascule : une ligne de base b fait mieux que l'absence de ligne de base si et seulement si |0,36 − b| < 0,36, soit b ∈ ]0 ; 0,72[. La moyenne 0,84 est hors de cet intervalle ; si la politique revenait à 50/50, b* et la moyenne coïncideraient (0,6).

**En production.** Indicateur : la variance empirique des estimations de gradient par lot ; alerte si elle dépasse celle obtenue sans ligne de base. Contrainte : l'assurance est supervisée par la CBUAE, qui attend un traitement équitable des sinistres ; la politique apprise ne fait que choisir le canal de collecte, et tout refus de prise en charge reste une décision humaine.

### Cas 3 — Entité de services publics en ligne [PUBLIC] : une récompense mal écrite renforce un raccourci

**Contexte.** Une entité de services publics en ligne, accessible par UAE Pass, entraîne par REINFORCE la politique de son agent de support bilingue arabe et anglais. Deux actions : résoudre la demande, ou la clore en envoyant un lien vers la foire aux questions. La première version de la récompense (v1) vaut 1 dès que le ticket est clos et accepté par l'usager. Volume illustratif : 10 000 tickets par mois.

**Données.**

- Résoudre : ticket clos et accepté avec la probabilité 0,85 (récompense 1), sinon 0 ; espérance 0,85.
- Clore avec un lien : récompense v1 de 1, toujours ; mais 40 % de ces tickets sont rouverts dans les 7 jours, ce que v1 ne voit pas.
- Version v2 : pénalité de 1,5 par ticket rouvert.
- Apprentissage : 200 pas de gradient exact, η = 0,5, ligne de base moyenne, départ 50/50.
- Volume : 10 000 tickets par mois.

**Calcul pas à pas.**

**Étape 1.** Avec v1, R = (0,85 ; 1). Gradient au départ sur « résoudre » (démonstration 6) : 0,25 × (0,85 − 1) = −0,0375 : REINFORCE pousse vers le raccourci.

**Étape 2.** Après 200 pas avec v1 : π(résoudre) = 0,0403.

**Étape 3.** Avec v2, « clore » vaut 1 − 0,4 × 1,5 = 0,4 ; gradient au départ 0,25 × (0,85 − 0,4) = 0,1125 ; après 200 pas, π(résoudre) = 0,9879.

**Étape 4.** Valeur de bascule de la pénalité p : 1 − 0,4p = 0,85, soit p = 0,15/0,4 = 0,375.

**Décision de l'agent.** L'entité déploie la politique entraînée avec v2, dont la pénalité 1,5 est bien au-dessus de la bascule 0,375 : l'agent résout 98,79 % des demandes.

**Contre-calcul.** La politique entraînée avec v1 clôt 1 − 0,0403 = 95,97 % des tickets par un lien : 10 000 × 0,9597 × 0,4 ≈ 3 839 tickets rouverts par mois, autant d'usagers qui reviennent, alors que le tableau de bord de v1 affiche une récompense presque parfaite.

**Sensibilité.** Avec la pénalité 1,5, la bascule sur le taux de réouverture r vaut 1 − 1,5r = 0,85, soit r = 0,10 : si les liens ne provoquaient que 10 % de réouvertures ou moins, le raccourci redeviendrait compétitif, et il faudrait vérifier que la réponse par lien est vraiment suffisante.

**En production.** Indicateur indépendant de la récompense : le taux de réouverture à 7 jours ; alerte au-dessus de 10 %. Le barème est versionné et testé comme du code. Contraintes : la réponse ne demande aucune donnée personnelle inutile (minimisation ; le régime applicable, PDPL ou règles propres à l'entité publique, est à confirmer avec le texte en vigueur) et elle est donnée dans la langue de l'usager.

### Cas 4 — Groupe de construction [BTP] : choisir le créneau de coulage du béton en été

**Contexte.** Un groupe de construction qui mène un grand chantier à Dubaï coule environ 120 dalles par mois (volume illustratif). En été, un agent choisit le créneau de chaque coulage : nuit, aube ou après-midi. La chaleur augmente le risque de fissuration ; la nuit coûte plus cher (éclairage, primes). La récompense vaut 1 point de base par coulage réalisé, plus 1 si la dalle est sans fissure, moins le surcoût du créneau : toutes les récompenses sont positives.

**Données.**

- Probabilité de dalle sans fissure : nuit 0,8 ; aube 0,6 ; après-midi 0,1.
- Surcoûts : nuit 0,2 ; aube 0,05 ; après-midi 0.
- Politique de départ : θ = (0 ; 0 ; 0), soit 1/3 par créneau ; pas η = 0,1.
- Précision voulue : écart-type de l'estimation du gradient sous 10 % de sa norme.
- Volume : 120 coulages par mois.

**Calcul pas à pas.**

**Étape 1.** Récompenses moyennes : nuit 1 + 0,8 − 0,2 = 1,6 ; aube 1 + 0,6 − 0,05 = 1,55 ; après-midi 1 + 0,1 = 1,1 ; moyenne 4,25/3 = 1,41667. Gradient exact : π(k)(μ(k) − 1,41667), soit (0,061111 ; 0,044444 ; −0,105556), de norme au carré 0,016852.

**Étape 2.** Variance totale d'une estimation à un tirage. Sous la politique uniforme, ‖∇log π(a)‖² = (2/3)² + (1/3)² + (1/3)² = 2/3 pour chaque action, et les variances des récompenses sont 0,8 × 0,2 + 0,6 × 0,4 + 0,1 × 0,9 = 0,16 + 0,24 + 0,09 = 0,49 au total :

$$
\mathbb{E}\lVert X \rVert^2 = \frac{2}{9} \sum_{a} \left[ \operatorname{Var}(r \mid a) + (\mu_a - b)^2 \right]
$$

Sans ligne de base : (2/9)(0,49 + 6,1725) = 1,480556, moins 0,016852, soit 1,463704. Avec b = 1,41667 : (2/9)(0,49 + 0,151667) = 0,142593, moins 0,016852, soit 0,125741.

**Étape 3.** Tirages pour un écart-type sous 10 % de la norme : N = variance/(0,01 × 0,016852), soit 8 686 coulages sans ligne de base (72,4 mois) et 746 avec (6,2 mois), 11,64 fois moins.

**Étape 4.** Ce que fait un tirage : une aube réussie (r = 1,95) pousse sans ligne de base (−0,065 ; 0,13 ; −0,065), avec la ligne de base (−0,017778 ; 0,035556 ; −0,017778). Un après-midi raté (r = 1) pousse sans ligne de base (−0,033333 ; −0,033333 ; 0,066667) : le pire créneau est **renforcé** ; avec la ligne de base, (0,013889 ; 0,013889 ; −0,027778) : il est affaibli.

**Décision de l'agent.** L'agent apprend avec la ligne de base moyenne, par lots d'environ 750 coulages, et en attendant il planifie de nuit, le créneau de meilleure espérance (1,6), sous validation du conducteur de travaux.

**Contre-calcul.** Sans ligne de base, il faudrait 72,4 mois de coulages pour un seul pas fiable, et chaque après-midi raté rendrait l'après-midi plus probable : la politique dériverait au gré du bruit.

**Sensibilité.** Nuit et aube sont proches : la nuit reste en tête tant que son surcoût est sous 0,8 − 0,55 = 0,25. Si la réussite de nuit baissait de 10 % (0,72), sa récompense moyenne tomberait à 1 + 0,52 = 1,52 < 1,55 : l'aube passerait devant.

**En production.** Indicateur : le taux de fissuration par créneau, mesuré sur chaque lot ; alerte si celui de la nuit dépasse 22 % (réussite sous 0,78), avant la bascule à 0,75, où la nuit vaut 1 + 0,75 − 0,2 = 1,55, autant que l'aube. Contraintes : les horaires de travail en extérieur en été sont encadrés par le MOHRE (pause de mi-journée, à confirmer avec le texte en vigueur) ; la décision de coulage reste validée par un humain.

## Entraînement sur feuille A4

**Exercice 1.** Trois actions, θ = (0 ; 0 ; 0). L'agent joue l'action 2. Donner ∇log π(2).

**Exercice 2.** Démontrer que ∇log π = ∇π / π.

**Exercice 3.** Dans le cas 1, refaire le calcul de variance avec b = 0,2.

**Exercice 4.** Avec θ = (0,05 ; −0,05), l'agent joue l'action 2 et reçoit 0. Sans ligne de base, θ change-t-il ?

**Exercice 5.** Pourquoi un agent qui ne reçoit que des récompenses positives (0,8 ou 1) apprend-il mal sans ligne de base ?

**Exercice 6 (modifier une donnée).** Dans le cas 3, la pénalité par ticket rouvert n'est que de 0,3. Que vaut « clore » en v2, et vers quoi l'entraînement pousse-t-il ?

**Exercice 7 (trouver l'erreur).** Un collègue code la mise à jour θ ← θ − η ∇log π(a)(R − b), « comme en descente de gradient ». Refaire l'exemple simple avec ce code et dire ce qui ne va pas.

**Exercice 8 (redémontrer de mémoire).** Redémontrer la formule Var = π₁π₂(b* − b)² de la démonstration 5, puis calculer la variance au départ du cas 1 avec b = 0,3.

## Corrigé

**Exercice 1.** Démonstration 2 avec π = (1/3 ; 1/3 ; 1/3) : (0 − 1/3 ; 1 − 1/3 ; 0 − 1/3) = (−1/3 ; 2/3 ; −1/3), soit environ (−0,3333 ; 0,6667 ; −0,3333).

**Exercice 2.** Dérivée du logarithme d'une fonction : (log π)′ = π′/π, appliquée à chaque dérivée partielle ; c'est la règle de la chaîne avec log′(u) = 1/u.

**Exercice 3.** Outil 1 : 0,5 × (1 − 0,2) = 0,4 ; outil 2 : −0,5 × (0,2 − 0,2) = 0. Moyenne 0,2, variance 0,5 × 0,2² + 0,5 × 0,2² = 0,04 ; la formule de la démonstration 5 donne aussi 0,25 × (0,6 − 0,2)² = 0,04.

**Exercice 4.** Non : le pas vaut η × R × ∇log π(2) = η × 0 × … = 0 ; une récompense nulle sans ligne de base ne déplace rien.

**Exercice 5.** Toute action jouée est renforcée, même la moins bonne (démonstration 3) : seule la différence de récompense guide l'apprentissage, et elle est noyée dans un bruit important, comme l'après-midi raté du cas 4, renforcé sans ligne de base. La ligne de base ne garde que cette différence.

**Exercice 6.** « Clore » vaut 1 − 0,4 × 0,3 = 0,88 > 0,85 : la pénalité 0,3 est sous la bascule 0,375 du cas 3, le raccourci reste plus récompensé, et après 200 pas π(résoudre) ne vaut que 0,2139.

**Exercice 7.** θ devient (0 ; 0) − 0,1 × 1 × (0,5 ; −0,5) = (−0,05 ; 0,05), et π(1) tombe à 0,47502 : l'action qui a été récompensée devient moins probable. On maximise J, donc on monte le gradient : le signe doit être +.

**Exercice 8.** Preuve : X vaut π₂(R₁ − b) avec la probabilité π₁ et −π₁(R₂ − b) avec π₂ ; la variance d'une variable à deux valeurs est π₁π₂(x₁ − x₂)², et x₁ − x₂ = π₂R₁ + π₁R₂ − b = b* − b. Cas 1 au départ : b* = 0,6, donc Var = 0,25 × (0,6 − 0,3)² = 0,25 × 0,09 = 0,0225.

## Vérification en Python

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`proche(x, y, tol)`** — Cette petite fonction est le contrôleur des poids et mesures qui tolère une poussière sur le plateau : elle reçoit deux nombres et une tolérance, un milliardième par défaut, mesure la valeur absolue de leur écart et renvoie vrai s'il ne dépasse pas cette tolérance, faux sinon. Elle ne porte aucune théorie, mais elle permet aux `assert` de `main` de comparer des flottants sans tomber dans le piège des arrondis, par exemple pour constater que le gradient exact vaut 0,2 ou que la somme des coordonnées de ∇log π vaut bien 0.

**`softmax(theta)`** — Cette fonction est le répartiteur qui transforme des scores bruts en parts d'un même gâteau : elle reçoit la liste des préférences θ, soustrait d'abord la plus grande pour que l'exponentielle ne déborde jamais, exponentie chaque écart, puis divise chaque terme par leur somme. Elle renvoie une liste de probabilités positives de somme 1, la politique π de l'agent, soit 0,31793, 0,15788 et 0,52418 pour θ = (0,3 ; −0,4 ; 0,8) dans la démonstration 2, et presque toutes les autres fonctions du programme l'appellent.

**`grad_log(theta, a)`** — On la voit en boussole qui indique dans quelle direction tourner les préférences pour rendre une action plus probable : elle reçoit les préférences θ et l'indice de l'action a, calcule la politique par `softmax`, puis renvoie pour chaque coordonnée b la valeur 1[a = b] − π(b), dérivée du logarithme de π(a) établie dans la démonstration 2. Au départ θ = (0 ; 0), elle donne (0,5 ; −0,5) pour la première action, et ses coordonnées somment toujours à 0, ce que vérifie `main` ; elle alimente les gradients et les estimations de tout le programme.

**`gradient_exact(theta, recompenses, b)`** — Cette fonction est l'oracle qui connaît toutes les issues et calcule le vrai gradient, sans tirage : elle reçoit les préférences, la récompense de chaque action et une ligne de base constante b, nulle par défaut, puis additionne, pour chaque coordonnée, les termes π(a) × ∇log π(a) × (R(a) − b) sur toutes les actions. Elle renvoie le gradient ∇J, qui ne dépend pas de b, comme le prouve la démonstration 3 : il vaut 0,2 sur la première coordonnée au départ avec les récompenses 1 et 0,2, et c'est lui que suivent les pas de la démonstration 6 et de `entrainer`.

**`estimations(theta, recompenses, b, c)`** — Celle-ci décrit tout ce qu'un seul tirage pourrait raconter à l'agent, comme un tableau des issues d'un dé pipé : elle reçoit les préférences, les récompenses, une ligne de base b et l'indice c de la coordonnée étudiée, 0 par défaut, et renvoie, pour chaque action a, le couple formé de sa probabilité π(a) et de la valeur de l'estimation ∇log π(a) × (R(a) − b) sur cette coordonnée. Au départ, elle donne 0,5 et −0,1 sans ligne de base, 0,2 et 0,2 avec b = 0,6, 0,4 et 0 avec b = 0,2, et `moyenne_variance` en tire la moyenne et la dispersion.

**`moyenne_variance(loi)`** — Cette fonction est le statisticien de poche qui résume une loi discrète en deux chiffres : elle reçoit une liste de couples probabilité et valeur, calcule la moyenne pondérée des valeurs, puis la moyenne pondérée des carrés de leurs écarts à cette moyenne. Elle renvoie le couple moyenne et variance, ce qui permet à la démonstration 3 de montrer que la moyenne reste 0,2 quelle que soit la ligne de base, tandis que la variance passe de 0,09 à 0 puis à 0,04, et aux cas 1 et 2 de chiffrer combien de tirages un pas précis demande.

**`ligne_base_optimale(pi, recompenses)`** — On l'imagine en régleur qui trouve la hauteur exacte où le bruit de l'estimation disparaît : elle reçoit les probabilités et les récompenses de deux actions, refuse par une `ValueError` toute autre taille, la formule n'étant écrite que pour deux actions, puis renvoie b* = π₂R₁ + π₁R₂, la moyenne des récompenses pondérée par les probabilités croisées. Elle vaut 0,6 pour une politique 50/50 et 0,36 pour une politique 80/20, et la démonstration 5 vérifie qu'avec elle la variance tombe à zéro, alors que la moyenne ordinaire, 0,84, l'augmente.

**`pas_pour_atteindre(cible, depart, eta, ecart)`** — Cette fonction est l'alpiniste qui compte ses pas sur une pente qui s'aplatit à l'approche du sommet : elle reçoit la probabilité visée, la probabilité de départ de la première action, le pas η et l'écart de récompense entre les deux actions, 0,8 par défaut, refuse par une `ValueError` des probabilités hors de ]0 ; 1[, puis passe en log-cote et ajoute à chaque pas 2η × écart × π₁(1 − π₁) tant que la cible n'est pas atteinte. Elle renvoie le nombre de pas, 134 pour aller de 0,5 à 0,99 avec η = 0,5, 269 avec η = 0,25, et 137 pour remonter de 0,01 à 0,5.

**`demo_1_log()`** — Celle-ci vérifie l'astuce du logarithme par deux témoins indépendants : elle ne reçoit rien, part de θ = (0 ; 0), calcule le gradient exact par `gradient_exact`, puis le retrouve par différences finies centrées sur la récompense moyenne J, avec un écart de 10⁻⁶, et obtient 0,2 dans les deux cas. Elle calcule enfin une estimation fautive qui oublie de diviser par π, c'est-à-dire qui pondère ∂π par π au lieu d'utiliser le logarithme, et trouve 0,1, la moitié de la vraie valeur ; elle imprime ces trois nombres et les renvoie.

**`demo_2_softmax()`** — Cette fonction met la formule de `grad_log` à l'épreuve sur trois actions : elle ne reçoit rien, prend θ = (0,3 ; −0,4 ; 0,8), calcule la politique 0,31793, 0,15788 et 0,52418, puis compare, pour chacune des neuf paires action et coordonnée, la dérivée numérique du logarithme de π à la formule, en exigeant leur accord par un `assert`. Elle imprime la politique et le vecteur ∇log π(1) = (0,68207 ; −0,15788 ; −0,52418), dont la somme vaut 0, et renvoie les deux.

**`demo_3_ligne_de_base()`** — On y voit trois versions d'un même gradient, servies avec trois lignes de base différentes : la fonction ne reçoit rien, part de θ = (0 ; 0) et, pour b valant 0, 0,6 et 0,2, dresse la loi de l'estimation à un tirage, puis en calcule la moyenne, toujours 0,2, et la variance, 0,09, 0 et 0,04. Elle montre ensuite qu'une ligne de base qui dépend de l'action, b(a) = R(a), ramène la moyenne à 0 au lieu de 0,2, donc biaise le gradient, imprime ces résultats et les renvoie dans un dictionnaire.

**`demo_5_ligne_base_optimale()`** — Cette fonction cherche la meilleure ligne de base pour une politique déjà penchée à 80/20 : elle ne reçoit rien, prend θ = (ln 4 ; 0), calcule b* = 0,36 et la récompense moyenne 0,84, puis la variance de l'estimation pour b = 0, b = 0,84 et b = b*, soit 0,020736, 0,036864 et 0. Elle vérifie aussi que ces variances égalent la formule π₁π₂(b* − b)², imprime la comparaison et renvoie le tout, montrant que la moyenne des récompenses n'est pas toujours la meilleure ligne de base.

**`demo_6_dynamique()`** — Celle-ci filme les premiers pas d'un apprentissage et sa lenteur finale : elle ne reçoit rien, fait un pas de taille 0,5 avec la ligne de base 0,6 depuis θ = (0 ; 0), qui mène à θ = (0,1 ; −0,1) et à π₁ = 0,54983, puis calcule l'incrément minuscule de 0,00792 qui reste quand π₁ vaut déjà 0,99. Elle demande à `pas_pour_atteindre` les 134 pas qui mènent de 0,5 à 0,99 et les 137 qui sortent une politique de 0,01 jusqu'à 0,5, imprime ces nombres et les renvoie.

**`cas_1_kyc_banque()`** — Cette fonction raconte une banque de détail qui reçoit environ 20 000 pièces d'identité par mois et choisit, pour chacune, entre un outil d'extraction complet, de récompense 1, et un outil partiel, de récompense 0,2, qui laisse un employé compléter à la main : elle ne reçoit rien et calcule d'abord le nombre de tirages qu'un pas précis à ±0,02 exige, 900 sans ligne de base et 400 avec b = 0,2. Elle entraîne ensuite la politique pendant 200 pas de gradient exact de taille 0,5, avec la moyenne comme ligne de base, et atteint π = 0,9934 et J = 0,99475, ce qui ramène la complétion manuelle de 120 000 à 1 574 AED par mois ; elle compte aussi 134 et 269 pas jusqu'à 0,99 selon η, puis renvoie ces résultats.

**`cas_2_sinistres_assur()`** — On y suit un assureur dont la politique demande déjà des photos dans 80 % des petits sinistres et qui se demande quelle ligne de base garder pour continuer l'entraînement : la fonction ne reçoit rien, calcule le vrai gradient 0,128 et la précision visée de ±0,0128, puis l'écart-type de l'estimation, 0,144 sans ligne de base et 0,192 avec la moyenne. Elle en déduit qu'un pas précis demande 506,25 dossiers sans ligne de base contre 900 avec la moyenne, soit 8,45 et 15 jours de collecte à 60 sinistres par jour, calcule b* = 0,36 et montre que toute ligne de base entre 0 et 0,72 fait mieux que rien, puis renvoie le tout.

**`entrainer(recompenses, eta)`** — Cette fonction est l'entraîneur infatigable qui fait faire 200 tours de piste à une politique partie de zéro : elle reçoit la récompense de chaque action et le pas η, 0,5 par défaut, initialise toutes les préférences à 0, puis, à chaque tour, calcule la récompense moyenne sous la politique courante et avance θ de η fois le gradient exact obtenu avec cette moyenne pour ligne de base. Elle renvoie la probabilité finale de la première action, 0,0403 avec la récompense v1 du cas 3 et 0,9879 avec la récompense corrigée v2.

**`cas_3_recompense_public(penalite, afficher)`** — Ici, une entité de services publics en ligne entraîne son agent de support à choisir entre résoudre une demande, qui vaut 0,85, et la clore avec un lien vers la foire aux questions : la fonction reçoit la pénalité appliquée aux tickets rouverts, 1,5 par défaut, et un drapeau d'affichage. Avec la récompense v1, où clore vaut 1, le gradient de départ, −0,0375, pousse vers le raccourci et `entrainer` laisse π(résoudre) à 0,0403, soit 3 839 tickets rouverts par mois sur 10 000 ; avec v2, clore ne vaut plus que 1 − 0,4 × 1,5 = 0,4, le gradient devient 0,1125 et π(résoudre) monte à 0,9879. Elle calcule les bascules 0,375 et 0,10 et renvoie ces nombres ; avec une pénalité de 0,3, clore vaut encore 0,88.

**`variance_totale(theta, issues, b)`** — Celle-ci est le comptable du bruit quand chaque action a elle-même plusieurs issues possibles : elle reçoit les préférences, puis, pour chaque action, la liste des couples probabilité et récompense de ses issues, et une ligne de base b. Elle calcule le gradient exact à partir de la récompense moyenne de chaque action, puis le moment d'ordre deux de l'estimation à un tirage, somme sur les actions de π(a) × ‖∇log π(a)‖² × l'espérance de (r − b)², et renvoie le gradient avec la variance totale, ce moment moins le carré de la norme du gradient ; le cas 4 l'appelle avec b = 0 et avec la moyenne.

**`cas_4_coulage_btp()`** — Cette fonction met en scène un chantier qui coule environ 120 dalles par mois en été et dont l'agent choisit le créneau, nuit, aube ou après-midi, avec des chances de réussite de 0,8, 0,6 et 0,1 et des surcoûts de 0,2, 0,05 et 0 : elle ne reçoit rien, calcule les récompenses moyennes 1,6, 1,55 et 1,1, toutes positives, leur moyenne 1,41667 et le gradient de départ. Sans ligne de base, la variance totale vaut 1,463704 et un gradient précis à 10 % exige 8 686 coulages, soit 72,4 mois ; avec la moyenne, 0,125741 et 746 coulages, soit 6,2 mois. Elle montre aussi qu'un après-midi raté est renforcé sans ligne de base, calcule la bascule de 0,25 sur le surcoût de nuit et la marge de 0,52 d'une nuit moins sûre, puis renvoie ces résultats.

**`main()`** — C'est le chef d'orchestre de la fiche : il refait d'abord l'exemple simple, où ∇log π(1) = (0,5 ; −0,5) et un pas de 0,1 porte π(1) à 0,52498, puis appelle les démonstrations 1, 2, 3, 5 et 6 et vérifie leurs nombres, de l'accord du gradient exact avec les différences finies jusqu'aux 134 et 137 pas de la dynamique. Il joue ensuite les quatre cas et recalcule le corrigé des exercices, dont la descente fautive qui fait tomber π(1) à 0,47502 et la variance 0,0225 de l'exercice 8 ; chaque nombre est confronté par un `assert` à la valeur de la fiche, et la dernière ligne n'annonce le succès que si tout concorde.

```python
"""Démonstration 19 — REINFORCE : astuce du log, softmax, ligne de base, renforcement, ligne de base optimale, dynamique, quatre cas aux Émirats."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RECOMPENSES = [1.0, 0.2]


def proche(x: float, y: float, tol: float = 1e-9) -> bool:
    return abs(x - y) <= tol


def softmax(theta):
    m = max(theta)
    e = [math.exp(t - m) for t in theta]
    s = sum(e)
    return [x / s for x in e]


def grad_log(theta, a):
    """∂ log π(a) / ∂θ_b = 1[a = b] − π(b) pour une politique softmax (démonstration 2)."""
    pi = softmax(theta)
    return [(1.0 if b == a else 0.0) - pi[b] for b in range(len(theta))]


def gradient_exact(theta, recompenses, b=0.0):
    """∇J = Σ_a π(a) ∇log π(a) (R(a) − b), la même valeur pour toute constante b (démonstration 3)."""
    pi = softmax(theta)
    k = len(theta)
    return [sum(pi[a] * grad_log(theta, a)[c] * (recompenses[a] - b) for a in range(k)) for c in range(k)]


def estimations(theta, recompenses, b, c=0):
    """Valeurs possibles de l'estimation à un tirage (coordonnée c), avec leurs probabilités."""
    pi = softmax(theta)
    return [(pi[a], grad_log(theta, a)[c] * (recompenses[a] - b)) for a in range(len(theta))]


def moyenne_variance(loi):
    m = sum(p * x for p, x in loi)
    return m, sum(p * (x - m) ** 2 for p, x in loi)


def ligne_base_optimale(pi: list[float], recompenses: list[float]) -> float:
    """À deux actions : b* = π₂ R₁ + π₁ R₂, la moyenne des récompenses aux probabilités inversées (démonstration 5)."""
    if len(pi) != 2:
        raise ValueError("formule écrite pour deux actions")
    return pi[1] * recompenses[0] + pi[0] * recompenses[1]


def pas_pour_atteindre(cible: float, depart: float, eta: float, ecart: float = 0.8) -> int:
    """Nombre de pas de gradient exact (ligne de base = moyenne) pour faire passer π₁ de depart à cible."""
    if not 0 < depart < 1 or not 0 < cible < 1:
        raise ValueError("probabilités dans ]0 ; 1[")
    d, n = math.log(depart / (1 - depart)), 0
    while 1 / (1 + math.exp(-d)) < cible:
        p1 = 1 / (1 + math.exp(-d))
        d += 2 * eta * ecart * p1 * (1 - p1)
        n += 1
    return n


def demo_1_log() -> dict:
    theta = [0.0, 0.0]
    exact = gradient_exact(theta, RECOMPENSES)[0]
    J = lambda t: sum(p * r for p, r in zip(softmax(t), RECOMPENSES))
    h = 1e-6
    numerique = (J([h, 0.0]) - J([-h, 0.0])) / (2 * h)
    pi = softmax(theta)
    d_pi = [pi[0] * (1 - pi[0]), -pi[0] * pi[1]]            # ∂π(a)/∂θ₁, sans le logarithme
    sans_log = sum(pi[a] * d_pi[a] * RECOMPENSES[a] for a in range(2))
    print(f"démo 1 : ∇J exact {exact:.4f} ; différences finies {numerique:.4f} ; estimation sans le log {sans_log:.4f}")
    return {"exact": exact, "numerique": numerique, "sans_log": sans_log}


def demo_2_softmax() -> dict:
    th = [0.3, -0.4, 0.8]
    pi = softmax(th)
    g = grad_log(th, 0)
    h = 1e-6
    for a in range(3):
        for k in range(3):
            tp = list(th)
            tp[k] += h
            num = (math.log(softmax(tp)[a]) - math.log(softmax(th)[a])) / h
            assert math.isclose(num, grad_log(th, a)[k], rel_tol=1e-4, abs_tol=1e-6)
    print(f"démo 2 : π = {[round(p, 5) for p in pi]} ; ∇log π(1) = {[round(x, 5) for x in g]} ; somme {sum(g):.1f}")
    return {"pi": pi, "g": g}


def demo_3_ligne_de_base() -> dict:
    theta = [0.0, 0.0]
    res = {}
    for b in (0.0, 0.6, 0.2):
        loi = estimations(theta, RECOMPENSES, b)
        m, v = moyenne_variance(loi)
        res[b] = ([round(x, 4) for _, x in loi], m, v)
        print(f"ligne de base {b} : estimations {res[b][0]}, moyenne {m:.2f}, variance {v:.2f}")
    biaisee = [(p, grad_log(theta, a)[0] * (RECOMPENSES[a] - RECOMPENSES[a])) for a, p in enumerate(softmax(theta))]
    m_biais, _ = moyenne_variance(biaisee)
    print(f"démo 3 : ligne de base qui dépend de l'action, b(a) = R(a) → moyenne {m_biais:.2f} au lieu de 0.20")
    return {"res": res, "m_biais": m_biais}


def demo_5_ligne_base_optimale() -> dict:
    theta = [math.log(4), 0.0]
    pi = softmax(theta)
    b_etoile = ligne_base_optimale(pi, RECOMPENSES)
    moyenne_r = sum(p * r for p, r in zip(pi, RECOMPENSES))
    var = {b: moyenne_variance(estimations(theta, RECOMPENSES, b))[1] for b in (0.0, moyenne_r, b_etoile)}
    formule = {b: pi[0] * pi[1] * (b_etoile - b) ** 2 for b in var}
    print(f"démo 5 : π = ({pi[0]:.1f} ; {pi[1]:.1f}) ; b* = {b_etoile:.2f}, moyenne {moyenne_r:.2f} ; variances "
          f"b = 0 : {var[0.0]:.6f}, b = {moyenne_r:.2f} : {var[moyenne_r]:.6f}, b* : {var[b_etoile]:.6f}")
    return {"pi": pi, "b_etoile": b_etoile, "moyenne_r": moyenne_r, "var": var, "formule": formule}


def demo_6_dynamique() -> dict:
    theta = [t + 0.5 * g for t, g in zip([0.0, 0.0], gradient_exact([0.0, 0.0], RECOMPENSES, 0.6))]
    p1 = softmax(theta)[0]
    inc_099 = 2 * 0.5 * 0.8 * 0.99 * 0.01
    monte = pas_pour_atteindre(0.99, 0.5, 0.5)
    sortie = pas_pour_atteindre(0.5, 0.01, 0.5)
    print(f"démo 6 : premier pas θ = {[round(t, 2) for t in theta]}, π₁ = {p1:.5f} ; incrément à π₁ = 0.99 : {inc_099:.5f} ;"
          f" pas de 0.5 à 0.99 : {monte} ; de 0.01 à 0.5 : {sortie}")
    return {"theta": theta, "p1": p1, "inc_099": inc_099, "monte": monte, "sortie": sortie}


def cas_1_kyc_banque() -> dict:
    """[BANQUE] deux outils d'extraction KYC (récompenses 1 et 0,2) : ligne de base, précision, apprentissage."""
    n_requis = {b: math.ceil((2 * math.sqrt(moyenne_variance(estimations([0.0, 0.0], RECOMPENSES, b))[1]) / 0.02) ** 2 - 1e-9)
                for b in (0.0, 0.2)}
    theta = [0.0, 0.0]
    for _ in range(200):                                     # gradient exact, b = moyenne
        pi = softmax(theta)
        moy = sum(p * r for p, r in zip(pi, RECOMPENSES))
        grad = [sum(pi[a] * grad_log(theta, a)[k] * (RECOMPENSES[a] - moy) for a in range(2)) for k in range(2)]
        theta = [t + 0.5 * gk for t, gk in zip(theta, grad)]
    p_final = softmax(theta)[0]
    J_final = p_final * 1.0 + (1 - p_final) * 0.2
    cout = {nom: (1 - p1) * 12 * 20000 for nom, p1 in (("50/50", 0.5), ("appris", p_final))}
    k05, k025 = pas_pour_atteindre(0.99, 0.5, 0.5), pas_pour_atteindre(0.99, 0.5, 0.25)
    print(f"cas 1 : échantillons pour ±0.02 : b = 0 → {n_requis[0.0]}, b = 0.2 → {n_requis[0.2]}, b = 0.6 → 1 ;"
          f" après 200 pas : π(outil 1) = {p_final:.4f}, J = {J_final:.5f}")
    print(f"        complétion manuelle : 50/50 {cout['50/50']:,.0f} AED/mois, appris {cout['appris']:,.0f} AED/mois ;"
          f" pas jusqu'à 0.99 : η = 0.5 → {k05}, η = 0.25 → {k025}")
    return {"n_requis": n_requis, "p_final": p_final, "J_final": J_final, "cout": cout, "k05": k05, "k025": k025}


def cas_2_sinistres_assur() -> dict:
    """[ASSUR] politique déjà à 80/20 : quelle ligne de base, combien de dossiers par pas précis ?"""
    theta = [math.log(4), 0.0]
    pi = softmax(theta)
    vrai = gradient_exact(theta, RECOMPENSES)[0]
    b_etoile = ligne_base_optimale(pi, RECOMPENSES)
    moyenne_r = sum(p * r for p, r in zip(pi, RECOMPENSES))
    precision = 0.1 * vrai
    sigma = {nom: math.sqrt(moyenne_variance(estimations(theta, RECOMPENSES, b))[1])
             for nom, b in (("sans", 0.0), ("moyenne", moyenne_r))}
    n = {nom: (2 * s / precision) ** 2 for nom, s in sigma.items()}
    jours = {nom: math.ceil(math.ceil(v - 1e-9) / 60 * 100) / 100 for nom, v in n.items()}
    b_egal = 2 * b_etoile
    print(f"cas 2 : ∇J = {vrai:.3f} ; précision ±{precision:.4f} ; σ sans ligne de base {sigma['sans']:.3f},"
          f" avec la moyenne {sigma['moyenne']:.3f} ; dossiers {n['sans']:.2f} et {n['moyenne']:.2f}")
    print(f"        jours de collecte à 60 dossiers/jour : {jours['sans']:.2f} et {jours['moyenne']:.2f} ;"
          f" b* = {b_etoile:.2f} ; toute ligne de base dans ]0 ; {b_egal:.2f}[ bat l'absence de ligne de base")
    return {"vrai": vrai, "precision": precision, "sigma": sigma, "n": n, "jours": jours, "b_etoile": b_etoile,
            "b_egal": b_egal, "moyenne_r": moyenne_r}


def entrainer(recompenses: list[float], eta: float = 0.5) -> float:
    """200 pas de gradient exact avec la ligne de base moyenne ; renvoie π de la première action."""
    theta = [0.0] * len(recompenses)
    for _ in range(200):
        pi = softmax(theta)
        moy = sum(p * r for p, r in zip(pi, recompenses))
        theta = [t + eta * g for t, g in zip(theta, gradient_exact(theta, recompenses, moy))]
    return softmax(theta)[0]


def cas_3_recompense_public(penalite: float = 1.5, afficher: bool = True) -> dict:
    """[PUBLIC] « résoudre » ou « clore avec un lien » : une récompense mal écrite renforce le raccourci."""
    v1 = [0.85, 1.0]
    v2 = [0.85, 1.0 - 0.4 * penalite]
    g1 = gradient_exact([0.0, 0.0], v1)[0]
    g2 = gradient_exact([0.0, 0.0], v2)[0]
    p_v1, p_v2 = entrainer(v1), entrainer(v2)
    reouverts = 10000 * (1 - p_v1) * 0.4
    p_bascule = (1.0 - 0.85) / 0.4
    r_bascule = (1.0 - 0.85) / 1.5
    if afficher:
        print(f"cas 3 : v1 = {v1} → gradient {g1:.4f}, π(résoudre) après 200 pas {p_v1:.4f} ;"
              f" v2 = [0.85, {v2[1]:.2f}] → gradient {g2:.4f}, π(résoudre) {p_v2:.4f}")
        print(f"        tickets rouverts par mois avec v1 : {reouverts:,.0f} ; bascules pénalité {p_bascule:.3f},"
              f" taux de réouverture {r_bascule:.2f}")
    return {"v2": v2, "g1": g1, "g2": g2, "p_v1": p_v1, "p_v2": p_v2, "reouverts": reouverts,
            "p_bascule": p_bascule, "r_bascule": r_bascule}


def variance_totale(theta: list[float], issues: list[list[tuple[float, float]]], b: float) -> tuple[list[float], float]:
    """Gradient exact et variance totale (somme sur les coordonnées) de l'estimation à un tirage ∇log π(a) (r − b)."""
    pi = softmax(theta)
    k = len(theta)
    grad = [sum(pi[a] * grad_log(theta, a)[c] * sum(p * r for p, r in issues[a]) for a in range(k)) for c in range(k)]
    m2 = sum(pi[a] * sum(g * g for g in grad_log(theta, a)) * sum(p * (r - b) ** 2 for p, r in issues[a]) for a in range(k))
    return grad, m2 - sum(g * g for g in grad)


def cas_4_coulage_btp() -> dict:
    """[BTP] créneau de coulage du béton en été (nuit, aube, après-midi) : récompenses toutes positives."""
    p_ok, couts = [0.8, 0.6, 0.1], [0.2, 0.05, 0.0]
    issues = [[(p, 1.0 + 1.0 - c), (1 - p, 1.0 - c)] for p, c in zip(p_ok, couts)]   # 1 point de base par coulage
    mu = [sum(p * r for p, r in loi) for loi in issues]
    theta = [0.0, 0.0, 0.0]
    moyenne = sum(mu) / 3
    grad, v0 = variance_totale(theta, issues, 0.0)
    _, vm = variance_totale(theta, issues, moyenne)
    norme2 = sum(g * g for g in grad)
    n0, nm = v0 / (0.1 ** 2 * norme2), vm / (0.1 ** 2 * norme2)
    pas_aube = [round(0.1 * (1.95 - 0.0) * g, 6) for g in grad_log(theta, 1)]
    pas_aube_b = [round(0.1 * (1.95 - moyenne) * g, 6) for g in grad_log(theta, 1)]
    pas_echec = [round(0.1 * (1.0 - 0.0) * g, 6) for g in grad_log(theta, 2)]
    pas_echec_b = [round(0.1 * (1.0 - moyenne) * g, 6) for g in grad_log(theta, 2)]
    c_bascule = 0.8 - (0.6 - 0.05)
    mu_nuit_moins_10 = 0.8 * 0.9 - 0.2
    print(f"cas 4 : moyennes {[round(m, 2) for m in mu]} (moyenne {moyenne:.5f}) ; ∇J = {[round(g, 6) for g in grad]}")
    print(f"        variance totale b = 0 : {v0:.6f}, b = moyenne : {vm:.6f} ; coulages pour ±10 % : {n0:,.0f} et {nm:,.0f}"
          f" ({n0 / 120:.1f} et {nm / 120:.1f} mois)")
    print(f"        aube réussie : {pas_aube} puis {pas_aube_b} ; après-midi raté : {pas_echec} puis {pas_echec_b} ;"
          f" bascule surcoût de nuit {c_bascule:.2f} ; nuit à −10 % {mu_nuit_moins_10:.2f}")
    return {"mu": mu, "moyenne": moyenne, "grad": grad, "v0": v0, "vm": vm, "norme2": norme2, "n0": n0, "nm": nm,
            "pas_aube": pas_aube, "pas_aube_b": pas_aube_b, "pas_echec": pas_echec, "pas_echec_b": pas_echec_b,
            "c_bascule": c_bascule, "mu_nuit_moins_10": mu_nuit_moins_10}


def main() -> None:
    g = grad_log([0.0, 0.0], 0)
    theta = [0.1 * x for x in g]
    print(f"∇log π(1) = {g} ; θ = {theta} ; π(1) = {softmax(theta)[0]:.5f}")
    assert g == [0.5, -0.5] and round(softmax(theta)[0], 5) == 0.52498
    assert round(math.exp(0.05), 5) == 1.05127 and round(math.exp(-0.05), 5) == 0.95123
    assert round(math.exp(0.05) + math.exp(-0.05), 5) == 2.0025

    d1 = demo_1_log()
    assert proche(d1["exact"], 0.2) and abs(d1["numerique"] - 0.2) < 1e-6 and proche(d1["sans_log"], 0.1)
    assert proche(0.25 * 0.8, 0.2) and proche(0.5 * 0.25 * 1 - 0.5 * 0.25 * 0.2, 0.1)
    d2 = demo_2_softmax()
    assert [round(p, 5) for p in d2["pi"]] == [0.31793, 0.15788, 0.52418]
    assert [round(x, 5) for x in d2["g"]] == [0.68207, -0.15788, -0.52418] and proche(sum(d2["g"]), 0)
    assert round(math.exp(0.3) + math.exp(-0.4) + math.exp(0.8), 4) == 4.2457
    d3 = demo_3_ligne_de_base()
    for b, (_, m, v) in d3["res"].items():
        assert math.isclose(m, 0.2)                                                    # démonstration 3
    assert [round(d3["res"][b][2], 2) for b in (0.0, 0.6, 0.2)] == [0.09, 0.0, 0.04] and proche(d3["m_biais"], 0)
    assert d3["res"][0.0][0] == [0.5, -0.1] and d3["res"][0.6][0] == [0.2, 0.2] and d3["res"][0.2][0] == [0.4, 0.0]
    d5 = demo_5_ligne_base_optimale()
    assert [round(p, 6) for p in d5["pi"]] == [0.8, 0.2] and round(d5["b_etoile"], 2) == 0.36 and round(d5["moyenne_r"], 2) == 0.84
    v5 = [round(d5["var"][b], 6) for b in d5["var"]]
    assert v5 == [0.020736, 0.036864, 0.0] and all(proche(d5["var"][b], d5["formule"][b], 1e-12) for b in d5["var"])
    assert proche(ligne_base_optimale([0.5, 0.5], RECOMPENSES), 0.6) and proche(0.25 * 0.6 ** 2, 0.09)
    assert proche(0.25 * 0.4 ** 2, 0.04) and proche(0.16 * 0.36 ** 2, 0.020736) and proche(0.16 * 0.48 ** 2, 0.036864)
    d6 = demo_6_dynamique()
    assert [round(t, 2) for t in d6["theta"]] == [0.1, -0.1] and round(d6["p1"], 5) == 0.54983
    assert round(d6["inc_099"], 5) == 0.00792 and (d6["monte"], d6["sortie"]) == (134, 137)
    assert proche(2 * 0.5 * 0.8 * 0.25, 0.2)

    c1 = cas_1_kyc_banque()
    assert c1["n_requis"] == {0.0: 900, 0.2: 400} and round(c1["p_final"], 4) == 0.9934
    assert 0.99 < c1["p_final"] < 1.0 and round(c1["J_final"], 5) == 0.99475
    assert round(c1["cout"]["50/50"]) == 120000 and round(c1["cout"]["appris"]) == 1574
    assert 134 * 900 == 120600 and 120000 - 1574 == 118426 and 0.5 * 12 * 20000 == 120000 and proche(0.8 * 15, 12)
    assert c1["k05"] == 134 and c1["k025"] == 269 and round((1 - c1["p_final"]) * 12, 3) == 0.079
    c2 = cas_2_sinistres_assur()
    assert round(c2["vrai"], 3) == 0.128 and round(c2["precision"], 4) == 0.0128
    assert round(c2["sigma"]["sans"], 3) == 0.144 and round(c2["sigma"]["moyenne"], 3) == 0.192
    assert round(c2["n"]["sans"], 2) == 506.25 and round(c2["n"]["moyenne"], 2) == 900.0
    assert c2["jours"] == {"sans": 8.45, "moyenne": 15.0} and round(c2["b_egal"], 2) == 0.72
    assert round(15 - 8.45, 2) == 6.55 and round(0.036864 / 0.020736, 2) == 1.78 and round(1 - 0.0403, 4) == 0.9597
    assert round(0.8 * 0.2 * 1 - 0.2 * 0.8 * 0.2, 3) == 0.128 and round(math.sqrt(0.020736), 3) == 0.144
    c3 = cas_3_recompense_public()
    assert round(c3["g1"], 4) == -0.0375 and round(c3["g2"], 4) == 0.1125 and round(c3["v2"][1], 2) == 0.4
    assert round(c3["p_v1"], 4) == 0.0403 and round(c3["p_v2"], 4) == 0.9879
    assert round(c3["reouverts"]) == 3839 and round(c3["p_bascule"], 3) == 0.375 and round(c3["r_bascule"], 2) == 0.1
    c4 = cas_4_coulage_btp()
    assert [round(m, 2) for m in c4["mu"]] == [1.6, 1.55, 1.1] and round(c4["moyenne"], 5) == 1.41667
    assert [round(g, 6) for g in c4["grad"]] == [0.061111, 0.044444, -0.105556]
    assert round(c4["v0"], 6) == 1.463704 and round(c4["vm"], 6) == 0.125741 and round(c4["norme2"], 6) == 0.016852
    assert round(c4["n0"]) == 8686 and round(c4["nm"]) == 746 and round(c4["n0"] / c4["nm"], 2) == 11.64
    assert c4["pas_aube"] == [-0.065, 0.13, -0.065] and c4["pas_aube_b"] == [-0.017778, 0.035556, -0.017778]
    assert c4["pas_echec"] == [-0.033333, -0.033333, 0.066667] and c4["pas_echec_b"] == [0.013889, 0.013889, -0.027778]
    assert round(c4["c_bascule"], 2) == 0.25 and round(c4["mu_nuit_moins_10"], 2) == 0.52
    assert round(1.6 ** 2 + 1.55 ** 2 + 1.1 ** 2, 4) == 6.1725 and round(sum((m - 4.25 / 3) ** 2 for m in c4["mu"]), 6) == 0.151667
    assert round((2 / 9) * 6.6625, 6) == 1.480556 and round((2 / 9) * 0.641667, 6) == 0.142593 and proche(1.6 + 1.55 + 1.1, 4.25)
    assert proche(1 + 0.75 - 0.2, 1.55) and round(0.8 * 0.2 + 0.6 * 0.4 + 0.1 * 0.9, 2) == 0.49
    assert proche(0.16 + 0.24 + 0.09, 0.49) and proche((2 / 9) * (0.49 + 6.1725), c4["v0"] + c4["norme2"], 1e-9)

    print("Corrigé")
    ex6 = cas_3_recompense_public(penalite=0.3, afficher=False)
    descente = [-0.1 * x for x in g]
    v_b03 = moyenne_variance(estimations([0.0, 0.0], RECOMPENSES, 0.3))[1]
    print(f"  ex1 {[round(x, 4) for x in grad_log([0, 0, 0], 1)]} ; ex3 b = 0.2 → variance 0.04 ;"
          f" ex6 clore vaut {ex6['v2'][1]:.2f} → π(résoudre) {ex6['p_v2']:.4f}")
    print(f"  ex7 descente : θ = {[round(t, 2) for t in descente]}, π(1) = {softmax(descente)[0]:.5f} ;"
          f" ex8 b = 0.3 → variance {v_b03:.4f}")
    assert [round(x, 4) for x in grad_log([0, 0, 0], 1)] == [-0.3333, 0.6667, -0.3333]
    assert round(ex6["v2"][1], 2) == 0.88 and ex6["p_v2"] < 0.5 and round(ex6["p_v2"], 4) == 0.2139
    assert round(softmax(descente)[0], 5) == 0.47502 and round(v_b03, 4) == 0.0225
    assert all(t + 0.1 * 0.0 * x == t for t, x in zip([0.05, -0.05], grad_log([0.05, -0.05], 1)))   # exercice 4
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
∇log π(1) = [0.5, -0.5] ; θ = [0.05, -0.05] ; π(1) = 0.52498
démo 1 : ∇J exact 0.2000 ; différences finies 0.2000 ; estimation sans le log 0.1000
démo 2 : π = [0.31793, 0.15788, 0.52418] ; ∇log π(1) = [0.68207, -0.15788, -0.52418] ; somme 0.0
ligne de base 0.0 : estimations [0.5, -0.1], moyenne 0.20, variance 0.09
ligne de base 0.6 : estimations [0.2, 0.2], moyenne 0.20, variance 0.00
ligne de base 0.2 : estimations [0.4, -0.0], moyenne 0.20, variance 0.04
démo 3 : ligne de base qui dépend de l'action, b(a) = R(a) → moyenne 0.00 au lieu de 0.20
démo 5 : π = (0.8 ; 0.2) ; b* = 0.36, moyenne 0.84 ; variances b = 0 : 0.020736, b = 0.84 : 0.036864, b* : 0.000000
démo 6 : premier pas θ = [0.1, -0.1], π₁ = 0.54983 ; incrément à π₁ = 0.99 : 0.00792 ; pas de 0.5 à 0.99 : 134 ; de 0.01 à 0.5 : 137
cas 1 : échantillons pour ±0.02 : b = 0 → 900, b = 0.2 → 400, b = 0.6 → 1 ; après 200 pas : π(outil 1) = 0.9934, J = 0.99475
        complétion manuelle : 50/50 120,000 AED/mois, appris 1,574 AED/mois ; pas jusqu'à 0.99 : η = 0.5 → 134, η = 0.25 → 269
cas 2 : ∇J = 0.128 ; précision ±0.0128 ; σ sans ligne de base 0.144, avec la moyenne 0.192 ; dossiers 506.25 et 900.00
        jours de collecte à 60 dossiers/jour : 8.45 et 15.00 ; b* = 0.36 ; toute ligne de base dans ]0 ; 0.72[ bat l'absence de ligne de base
cas 3 : v1 = [0.85, 1.0] → gradient -0.0375, π(résoudre) après 200 pas 0.0403 ; v2 = [0.85, 0.40] → gradient 0.1125, π(résoudre) 0.9879
        tickets rouverts par mois avec v1 : 3,839 ; bascules pénalité 0.375, taux de réouverture 0.10
cas 4 : moyennes [1.6, 1.55, 1.1] (moyenne 1.41667) ; ∇J = [0.061111, 0.044444, -0.105556]
        variance totale b = 0 : 1.463704, b = moyenne : 0.125741 ; coulages pour ±10 % : 8,686 et 746 (72.4 et 6.2 mois)
        aube réussie : [-0.065, 0.13, -0.065] puis [-0.017778, 0.035556, -0.017778] ; après-midi raté : [-0.033333, -0.033333, 0.066667] puis [0.013889, 0.013889, -0.027778] ; bascule surcoût de nuit 0.25 ; nuit à −10 % 0.52
Corrigé
  ex1 [-0.3333, 0.6667, -0.3333] ; ex3 b = 0.2 → variance 0.04 ; ex6 clore vaut 0.88 → π(résoudre) 0.2139
  ex7 descente : θ = [-0.05, 0.05], π(1) = 0.47502 ; ex8 b = 0.3 → variance 0.0225
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

L'algorithme améliore une politique softmax en suivant le gradient de la récompense moyenne, avec une ligne de base qui réduit la variance sans biaiser le gradient.

```text
ALGORITHME REINFORCE
ENTRÉES : paramètres θ, pas η, nombre d'itérations n, récompenses des actions
SORTIE  : paramètres θ appris

  POUR itération DE 1 À n FAIRE
      π ← Softmax(θ)
      tirer une action a selon π ; observer R
      b ← récompense moyenne (ligne de base), ou b* = π₂ R₁ + π₁ R₂ à deux actions
      POUR CHAQUE paramètre θ_c FAIRE
          g_c ← (1 si c = a, sinon 0) − π(c)        (gradient de ln π(a))
          θ_c ← θ_c + η × g_c × (R − b)
      FIN POUR
  FIN POUR
  RETOURNER θ

ALGORITHME VarianceDUnTirage
ENTRÉES : θ, issues (probabilité, récompense) de chaque action, ligne de base b
  gradient ← Σ sur a de π(a) × ∇ln π(a) × E[r | a]
  m2 ← Σ sur a de π(a) × ‖∇ln π(a)‖² × E[(r − b)² | a]
  RETOURNER gradient, m2 − ‖gradient‖²
```

**Complexité.** O(K) par itération pour K actions avec un tirage (softmax et gradient). Le programme remplace le tirage par l'espérance exacte, somme sur les K actions de gradients de taille K, soit au moins O(K²) par itération : sans importance pour 2 ou 3 actions, impossible quand les actions sont des phrases, d'où le tirage en pratique. Le calcul exact de la variance coûte aussi O(K²) ; le nombre de tirages par mise à jour fiable est proportionnel à cette variance (900 contre 1 au cas 1, 8 686 contre 746 au cas 4).

**Du squelette au code.** La politique est `softmax(theta)` et le gradient du logarithme `grad_log(theta, a)`. La boucle `for _ in range(200)` de `cas_1_kyc_banque` applique la mise à jour avec la ligne de base `moy`, mais en moyennant exactement sur les deux actions (pondération par `pi`) au lieu de tirer : même direction en moyenne, sans hasard, donc une sortie reproductible ; `entrainer(recompenses, eta)` fait de même pour le cas 3. Le gradient exact est `gradient_exact(theta, recompenses, b)`, les estimations à un tirage `estimations(theta, recompenses, b, c)`, leur variance `moyenne_variance(loi)`, la ligne de base optimale `ligne_base_optimale(pi, recompenses)` et la variance totale du cas 4 `variance_totale(theta, issues, b)`. Le calcul des variances pour b = 0, 0,6 et 0,2 illustre la démonstration 3 dans `demo_3_ligne_de_base` ; la dynamique est mesurée par `pas_pour_atteindre(cible, depart, eta, ecart)`. Les quatre cas sont `cas_1_kyc_banque`, `cas_2_sinistres_assur`, `cas_3_recompense_public` et `cas_4_coulage_btp`.
