# Étape 75 bis — Optimisation — Mini-lots et généralisation

**Dossier :** 12-Production-Couts-Optimisation

> Étape 75 bis du parcours · Prérequis : [Optimisation : formules manquantes](<75-Optimisation-Formules.md>) · Suite : [Régularisation L1 et L2](<76-Regularisation-L1-L2.md>)

## Définition

Les étapes 73 à 75 calculent le gradient de la perte sur **tous** les exemples avant chaque pas. En pratique, on ne le fait presque jamais : on tire un **mini-lot** de B exemples, on fait la moyenne de leurs gradients, et on avance. Ce gradient de mini-lot est une estimation **sans biais** du vrai gradient, dont le bruit diminue comme 1/B ; c'est la descente de gradient stochastique (SGD), base de tous les optimiseurs, Adam compris. Une **époque** est un passage complet sur les données. Le pas η suit un **calendrier** : une montée progressive au début (*warmup*, échauffement), puis une décroissance, souvent en cosinus. La **généralisation** est la capacité du modèle à bien prédire des exemples qu'il n'a jamais vus ; on la mesure sur un jeu de **validation** séparé, on arrête l'entraînement quand cette mesure cesse de progresser (**arrêt précoce**), et l'on **écrête** le gradient par sa norme pour qu'un exemple aberrant ne puisse pas faire faire au modèle un pas démesuré.

## Rôle dans un agent

Rien de tout cela ne tourne dans la boucle percevoir → décider → agir → observer : c'est le quotidien des jobs d'entraînement hors ligne qui produisent les composants de l'agent, adaptateur LoRA (étape 73), routeur d'intentions, classifieur de garde-fou, reranker, élève distillé (étape 73 ter). L'ingénieur agentique y prend des décisions concrètes. La taille du lot est d'abord limitée par la mémoire du GPU, et l'accumulation de gradient permet de simuler un lot plus grand. Le pas et son calendrier décident si l'entraînement converge, diverge ou stagne. Le jeu de validation, construit à partir des traces de l'agent, dit quand s'arrêter, et la façon de le séparer décide si le chiffre annoncé est honnête : c'est la discipline d'évaluation de l'étape 13 bis, appliquée à l'entraînement. Enfin, l'écrêtage du gradient est l'assurance qui empêche un exemple aberrant de détruire en un pas un modèle entraîné pendant des heures.

## Équation complète

Gradient d'un mini-lot ℬ de B exemples, et vrai gradient sur les n exemples :

$$
g_{\mathcal{B}}(\theta) = \frac{1}{B} \sum_{i \in \mathcal{B}} \nabla \ell_i(\theta), \qquad \nabla \mathcal{L}(\theta) = \frac{1}{n} \sum_{i=1}^{n} \nabla \ell_i(\theta)
$$

Absence de biais :

$$
\mathbb{E}\bigl[g_{\mathcal{B}}(\theta)\bigr] = \nabla \mathcal{L}(\theta)
$$

Variance, avec la dispersion des gradients individuels σ² :

$$
\sigma^2 = \frac{1}{n} \sum_{i=1}^{n} \bigl\lVert \nabla \ell_i(\theta) - \nabla \mathcal{L}(\theta) \bigr\rVert^2
$$

$$
\mathbb{E}\bigl\lVert g_{\mathcal{B}} - \nabla \mathcal{L} \bigr\rVert^2 = \frac{\sigma^2}{B} \;\; \text{(tirage avec remise)}, \qquad \mathbb{E}\bigl\lVert g_{\mathcal{B}} - \nabla \mathcal{L} \bigr\rVert^2 = \frac{\sigma^2}{B} \cdot \frac{n - B}{n - 1} \;\; \text{(sans remise)}
$$

Pas de SGD, et nombre de pas pour K époques :

$$
\theta_{t+1} = \theta_t - \eta_t \, g_{\mathcal{B}_t}(\theta_t), \qquad t_{max} = K \left\lceil \frac{n}{B} \right\rceil
$$

Calendrier : échauffement linéaire sur W pas, puis cosinus jusqu'au pas t_max :

$$
\eta_t = \eta_{max} \, \frac{t}{W} \quad (0 \le t < W), \qquad \eta_t = \eta_{min} + \frac{\eta_{max} - \eta_{min}}{2} \left( 1 + \cos\left( \pi \, \frac{t - W}{t_{max} - W} \right) \right) \quad (W \le t \le t_{max})
$$

Écrêtage par la norme, de seuil c :

$$
\tilde{g} = g \cdot \min\left(1, \frac{c}{\lVert g \rVert}\right), \qquad \lVert \tilde{g} \rVert = \min\bigl(\lVert g \rVert, c\bigr) \le c
$$

Arrêt précoce de patience P : on garde le meilleur point et l'on s'arrête dès qu'il a P époques d'âge :

$$
t^{*} = \mathop{\mathrm{arg\,min}}_{t \le t_{arr}} \mathcal{L}_{val}(\theta_t), \qquad t_{arr} = \min\{\, t : t - t^{*}(t) \ge P \,\}
$$

## Décryptage des symboles

$$
n, \; B
$$

Le nombre d'exemples d'entraînement et la taille du mini-lot : des entiers, 1 ≤ B ≤ n ; `len(X)` et `B`.

$$
\mathcal{B}
$$

L'ensemble des indices du mini-lot, tiré au hasard ; en pratique, une tranche d'une permutation des exemples refaite à chaque époque ; `ordre[debut:debut + B]`.

$$
\ell_i, \; \nabla \ell_i
$$

La perte de l'exemple i, ici ½(w·xᵢ − yᵢ)², et son gradient (w·xᵢ − yᵢ)xᵢ ; `gradient_exemple(w, x, y)`.

$$
\mathcal{L}, \; \mathcal{L}_{val}
$$

La perte moyenne sur l'entraînement, et la même perte calculée sur le jeu de validation, jamais utilisé pour calculer un gradient ; `perte(w, X, Y)`. Le programme affiche son gradient sous le nom ∇L.

$$
\theta
$$

Les paramètres du modèle ; dans la régression du programme, le vecteur de poids `w`.

$$
g_{\mathcal{B}}
$$

Le gradient du mini-lot, moyenne des gradients des B exemples : un vecteur de même taille que θ ; `gradient_lot(w, X, Y, indices)`.

$$
\sigma^2
$$

La dispersion des gradients individuels autour du vrai gradient, au point θ considéré : un réel ≥ 0 ; `sigma2`.

$$
K, \; t_{max}
$$

Le nombre d'époques et le nombre total de pas ; `epoques` et `total`.

$$
\eta_t, \; \eta_{max}, \; \eta_{min}, \; W
$$

Le pas au pas t, sa valeur de crête, sa valeur finale, et la durée de l'échauffement en pas ; `pas_calendrier(t, total, eta_max, eta_min, echauffement)`.

$$
c
$$

Le seuil d'écrêtage : la norme maximale autorisée pour le gradient, un réel > 0, souvent 1 ; `seuil`.

$$
P, \; t^{*}, \; t_{arr}
$$

La patience, l'époque du meilleur score de validation, et l'époque où l'entraînement s'arrête ; `patience`, `ep_best`, `ep_arret`.

$$
h, \; \lambda
$$

La courbure de la perte le long d'une direction (une valeur propre de la matrice XᵀX/n), et le coefficient de régularisation L2 de l'étape 76, utilisés pour comparer arrêt précoce et ridge.

## Démonstration

### 1. Le gradient d'un mini-lot est sans biais

**Avec remise**, le lot est formé de B indices I₁, …, I_B tirés indépendamment et uniformément dans {1, …, n}. Pour chacun, l'espérance de ∇ℓ_I vaut (1/n) ∑ᵢ ∇ℓᵢ = ∇ℒ, puisque chaque exemple a la probabilité 1/n. L'espérance étant linéaire, la moyenne de B termes d'espérance ∇ℒ a pour espérance ∇ℒ. **Sans remise**, le lot est un sous-ensemble de B indices tiré uniformément parmi les C(n, B) possibles. Par symétrie, chaque exemple i appartient au lot avec la probabilité C(n − 1, B − 1) / C(n, B) = B/n, donc

$$
\mathbb{E}\bigl[g_{\mathcal{B}}\bigr] = \frac{1}{B} \sum_{i=1}^{n} \Pr(i \in \mathcal{B}) \, \nabla \ell_i = \frac{1}{B} \cdot \frac{B}{n} \sum_{i=1}^{n} \nabla \ell_i = \nabla \mathcal{L}
$$

Le programme le vérifie sans aucun hasard : sur n = 10 exemples, il énumère les 10, 45, 252 et 1 lots possibles pour B = 1, 2, 5 et 10, et les 10, 100 et 1 000 lots ordonnés avec remise pour B = 1, 2, 3 ; la moyenne des gradients de lots retombe chaque fois sur ∇ℒ à 10⁻¹² près. C'est ce qui justifie la SGD : en moyenne, chaque pas va dans la bonne direction.

### 2. La variance décroît en 1/B

On note cᵢ = ∇ℓᵢ − ∇ℒ les écarts individuels, de somme nulle. **Avec remise**, les B termes sont indépendants et centrés, donc l'espérance de leurs produits croisés est nulle, et

$$
\mathbb{E}\Bigl\lVert \frac{1}{B} \sum_{k=1}^{B} c_{I_k} \Bigr\rVert^2 = \frac{1}{B^2} \sum_{k=1}^{B} \mathbb{E}\lVert c_{I_k} \rVert^2 = \frac{1}{B^2} \cdot B \sigma^2 = \frac{\sigma^2}{B}
$$

**Sans remise**, on écrit g_ℬ − ∇ℒ = (1/B) ∑ᵢ Zᵢ cᵢ, où Zᵢ vaut 1 si i est dans le lot. On a E[Zᵢ] = B/n, Var(Zᵢ) = (B/n)(1 − B/n), et, pour i ≠ j, Cov(Zᵢ, Zⱼ) = B(B − 1)/(n(n − 1)) − (B/n)² = −(B/n)(1 − B/n)/(n − 1) : savoir que i est dans le lot rend j un peu moins probable. Comme les cᵢ somment à 0, ∑ᵢ≠ⱼ cᵢ·cⱼ = ‖∑ cᵢ‖² − ∑ ‖cᵢ‖² = −nσ². En développant le carré :

$$
\mathbb{E}\bigl\lVert g_{\mathcal{B}} - \nabla \mathcal{L} \bigr\rVert^2 = \frac{1}{B^2} \cdot \frac{B}{n}\Bigl(1 - \frac{B}{n}\Bigr) \Bigl( n\sigma^2 + \frac{n\sigma^2}{n - 1} \Bigr) = \frac{\sigma^2}{B} \cdot \frac{n - B}{n - 1}
$$

Le facteur (n − B)/(n − 1), la correction de population finie, annule la variance quand B = n : le lot complet n'a plus de bruit. Sur l'exemple, σ² = 10,7368 au point w = (0 ; 0) ; pour B = 2, la formule donne 10,7368 / 2 × 8/9 = 4,7719, exactement la moyenne obtenue sur les 45 lots. Conséquence pratique : l'écart-type du bruit varie comme 1/√B. Pour n = 64, il vaut, relativement à B = 1, 0,488 pour B = 4, 0,218 pour B = 16 et 0 pour B = 64. Diviser le bruit par deux demande un lot quatre fois plus grand, donc quatre fois plus de calcul par pas : les rendements sont décroissants.

### 3. Époques, nombre de pas et accumulation de gradient

Une époque compte ⌈n/B⌉ pas : pour n = 70 et B = 8, 9 pas, dont un dernier lot de 6 exemples, qu'on garde ou qu'on jette (option *drop_last* des chargeurs de données). Quand un lot de 32 ne tient pas en mémoire, on **accumule** : on calcule les gradients de k = 4 micro-lots de 8, on en fait la moyenne, et l'on fait un seul pas. Si les micro-lots ont la même taille b, la moyenne de leurs moyennes est la moyenne globale :

$$
\frac{1}{k} \sum_{m=1}^{k} \frac{1}{b} \sum_{i \in \mathcal{B}_m} \nabla \ell_i = \frac{1}{k\,b} \sum_{i \in \mathcal{B}_1 \cup \dots \cup \mathcal{B}_k} \nabla \ell_i
$$

Le programme retrouve le gradient du lot de 32 à 0 près. Si les tailles diffèrent, cette égalité tombe : avec des micro-lots de 8, 8, 8 et 2 exemples, la moyenne naïve des quatre moyennes donne (−0,7073 ; 1,6126), alors que le vrai gradient des 26 exemples vaut (−0,5010 ; 1,4622). Il faut pondérer chaque moyenne par la taille de son micro-lot, ce qui redonne exactement le vrai gradient. C'est la même règle que celle de l'étape 75 : un gradient de lot est une **moyenne**, pas une somme, sinon son échelle change avec B.

### 4. Un pas constant laisse un plancher de bruit

Près du minimum, le vrai gradient s'annule, mais pas celui du mini-lot. Prenons une direction de courbure h, l'écart eₜ = θₜ − θ* et un bruit ξₜ centré de variance s²/B. Un pas donne eₜ₊₁ = (1 − ηh)eₜ − ηξₜ. En régime stationnaire, la variance v de l'écart vérifie v = (1 − ηh)²v + η²s²/B, d'où

$$
v = \frac{\eta^2 s^2 / B}{1 - (1 - \eta h)^2} = \frac{\eta \, s^2}{B \, h \, (2 - \eta h)}, \qquad \text{excès de perte moyen} = \frac{h}{2} v = \frac{\eta \, s^2}{2B\,(2 - \eta h)}
$$

parce que la perte d'une parabole dépasse son minimum de ½h e². Le plancher est proportionnel à η/B : on l'abaisse en **réduisant le pas** à la fin, ou en **agrandissant le lot**. Le programme le montre sur une régression à 3 poids et 64 exemples, après 40 époques : 2,21 × 10⁻⁴ d'excès de perte avec B = 4 et η = 0,1 constant, 1,42 × 10⁻⁵ avec B = 16, et 8,6 × 10⁻⁷ avec B = 4 et un calendrier qui finit à η = 0,001. L'écart entre B = 4 et B = 16 dépasse le facteur 4 de la formule, parce que chaque chiffre est une seule valeur d'une grandeur qui fluctue, alors que la formule en donne la moyenne. Le même calcul explique une règle empirique (Goyal et al., 2017) : quand on multiplie B par k, multiplier η par k garde le même rapport η/B, donc le même niveau de bruit, avec k fois moins de pas par époque. Elle cesse de valoir quand η approche la limite de stabilité 2/L de l'étape 73, d'où la nécessité d'un échauffement.

### 5. Échauffement, puis cosinus

Le calendrier est continu au pas W : la montée y atteint η_max × W/W = η_max, et la phase cosinus y commence à η_min + (η_max − η_min)(1 + cos 0)/2 = η_max. Au dernier pas, cos π = −1 et il reste η_min. Entre les deux, le cosinus décroît sur [0 ; π], donc le pas aussi. La valeur moyenne de la phase cosinus vaut exactement (η_max + η_min)/2, parce que l'intégrale de cos(πu) entre 0 et 1 est nulle ; sur une grille régulière de pas, la somme des cosinus est nulle aussi, par la symétrie cos(π − x) = −cos x. Avec η_max = 0,1, η_min = 0,001, W = 10 et t_max = 100 : η(5) = 0,05, η(10) = 0,1, η(55) = 0,001 + 0,0495 = 0,0505, η(100) = 0,001, et la moyenne des 91 pas de la phase cosinus vaut 0,0505. Pourquoi monter d'abord ? Au premier pas, les poids sont aléatoires, les gradients souvent grands, et les moments d'Adam (étape 74) reposent sur très peu d'échantillons : un grand pas immédiat peut envoyer le modèle dans une zone dont il ne revient pas. L'échauffement est une pratique empirique, qu'on règle, en général entre 1 et 10 % des pas.

### 6. Séparer entraînement et validation, et s'arrêter à temps

Avec un pas sous la limite 2/L, la perte d'entraînement d'une descente de gradient ne fait que baisser (étape 73). La perte de validation, elle, peut remonter : c'est le **surapprentissage**. Dans le programme, 24 exemples d'entraînement pour 20 poids, dont 15 sont inutiles, et un bruit d'écart-type 1. La validation atteint son meilleur score, 0,841, à l'époque 5 ; à l'époque 200, l'entraînement est tombé à 0,0189 mais la validation est montée à 3,679, plus de quatre fois pire. Le modèle a appris le bruit des 24 exemples. Avec une patience de 10, l'arrêt précoce s'arrête à l'époque 15 = 5 + 10 et rend les poids de l'époque 5 : il paie 10 époques pour s'assurer que le minimum n'était pas un creux passager, et il ne rend **jamais** les derniers poids, mais les meilleurs.

Pourquoi cela marche-t-il ? Sur une perte quadratique, partons de θ = 0 et suivons une direction de courbure h, de cible θ*ₕ. Le point 2 de l'étape 73 donne l'écart (1 − ηh)ᵗ après t pas, donc la coordonnée atteinte vaut

$$
\theta_h(t) = \bigl(1 - (1 - \eta h)^t\bigr)\, \theta^{*}_h, \qquad \text{à comparer au ridge de l'étape 76 :} \quad \theta_h = \frac{h}{h + \lambda}\, \theta^{*}_h
$$

Pour h petit, 1 − (1 − ηh)ᵗ ≈ ηht et h/(h + λ) ≈ h/λ : les deux coïncident quand λ = 1/(ηt). Avec η = 0,1 et t = 50, donc λ = 0,2 : une direction de courbure 0,02 garde 0,0953 de sa cible par arrêt précoce et 0,0909 par ridge ; une direction de courbure 2 en garde 1,0000 et 0,9091. Les directions plates, où vit le bruit, sont rétrécies presque pareil : arrêter tôt est une régularisation L2 implicite, de force environ 1/(ηt). Dernière condition : le jeu de validation doit ressembler aux données de production et ne rien partager avec l'entraînement. Un même client, un même employeur, ou des dates mélangées des deux côtés, et le chiffre de validation devient optimiste ; le jeu de test, lui, reste à part jusqu'à la mesure finale (étape 13 bis).

### 7. L'écrêtage par la norme garde la direction et borne le pas

Si ‖g‖ ≤ c, rien ne change. Sinon, g̃ = (c/‖g‖) g est g multiplié par un nombre strictement positif : sa direction est la même, son cosinus avec g vaut 1, et sa norme vaut exactement c. Dans tous les cas, ‖g̃‖ = min(‖g‖, c), donc le déplacement d'un pas vérifie ‖θₜ₊₁ − θₜ‖ = ηₜ‖g̃‖ ≤ ηₜ c. Pour g = (3 ; 4), de norme 5, et c = 1, on obtient (0,6 ; 0,8). L'écrêtage **par valeur**, qui coupe chaque coordonnée à [−1 ; 1], donne (1 ; 1) : un cosinus de 7/(5√2) = 0,9899 avec g, donc une autre direction. Sur des données qui contiennent un point aberrant x = (25 ; 0), la perte de ce seul exemple a une courbure 25² = 625 : avec η = 0,05, chaque passage sur ce point multiplie l'écart par |1 − 0,05 × 625| ≈ 30, et la SGD diverge en quelques époques. Avec c = 1, chaque pas reste sous 0,05 : l'entraînement converge vers (1,057 ; −1,831), près des vrais poids (1 ; −2), avec 71 pas écrêtés sur 640. L'écrêtage ne corrige pas le biais que le point aberrant introduit : il empêche seulement qu'un pas détruise le modèle. Nettoyer les données reste nécessaire.

### 8. Exemple fait à la main (le code reprend ces nombres)

- Variance d'un lot de 2 parmi 10 sans remise : σ²/B × (n − B)/(n − 1) = 10,7368 / 2 × 8/9 = 4,7719 ; pour B = 5, 10,7368 / 5 × 5/9 = 1,1930.
- Écart-type relatif pour n = 64 et B = 4 : √(60 / (4 × 63)) = √0,2381 = 0,488.
- Calendrier au pas 55 : 0,001 + (0,1 − 0,001)/2 × (1 + cos(π/2)) = 0,001 + 0,0495 = 0,0505.
- Écrêtage de (3 ; 4) à c = 1 : (3 ; 4) × 1/5 = (0,6 ; 0,8).

## Effets et comportement

- **Petit lot, beaucoup de bruit, beaucoup de pas.** Pour le même nombre d'époques, B = 4 fait quatre fois plus de pas que B = 16, chacun deux fois plus bruité.
- **Le bruit ne disparaît qu'avec le pas.** Un η constant laisse un plancher proportionnel à η/B ; le calendrier qui décroît vers η_min l'abaisse.
- **La validation dit quand s'arrêter.** La perte d'entraînement baisse toujours ; seule la validation révèle le surapprentissage.
- **L'écrêtage par la norme est une assurance.** Il ne change rien tant que les gradients sont normaux et borne le pas quand l'un d'eux explose ; s'il se déclenche à presque chaque pas, le seuil est trop bas ou le pas trop grand.
- **L'accumulation remplace la mémoire par du temps.** k micro-lots de b exemples donnent exactement le gradient d'un lot de kb, à condition de pondérer par les tailles.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| ∇ℓᵢ = (w·xᵢ − yᵢ)xᵢ | `gradient_exemple(w, x, y)` |
| g_ℬ, moyenne sur le lot | `gradient_lot(w, X, Y, indices)` |
| ℒ, ℒ_val | `perte(w, X, Y)` sur l'entraînement ou la validation |
| E[g_ℬ] et E‖g_ℬ − ∇ℒ‖², par énumération | `moments_exacts(grads, B, remise)` |
| σ²/B et (σ²/B)(n − B)/(n − 1) | `variance_theorique(sigma2, n, B, remise)` |
| ηₜ, échauffement puis cosinus | `pas_calendrier(t, total, eta_max, eta_min, echauffement)` |
| g̃ = g·min(1, c/‖g‖) | `ecreter(g, c)` |
| θₜ₊₁ = θₜ − ηₜ g_ℬ | `sgd(X, Y, B, epoques, calendrier, graine, seuil)` |
| t*, t_arr, patience P | `entrainer_avec_arret(Xtr, Ytr, Xva, Yva, eta, max_epoques, patience)` |
| solution exacte θ* | `resoudre(A, b)` |

### Déroulé, ligne par ligne

**`gradient_exemple(w, x, y)`** calcule le résidu r = w·x − y, puis renvoie r·x. **`gradient_lot(w, X, Y, indices)`** additionne les gradients des exemples du lot, puis divise par leur nombre ; un lot vide lève `ValueError`. **`perte`** renvoie la moyenne de ½(w·x − y)². **`donnees(rng, n, w_vrai, bruit)`** tire des entrées gaussiennes et des cibles w_vrai·x plus un bruit gaussien.

**`resoudre(A, b)`** résout les équations normales par élimination de Gauss avec pivot partiel : à chaque colonne, on remonte la ligne au plus grand coefficient, puis on annule cette colonne dans toutes les autres lignes. Le programme s'en sert pour connaître la perte minimale exacte et mesurer l'excès de perte de la SGD.

**`moments_exacts(grads, B, remise)`.** Avec `remise=False`, `itertools.combinations(range(n), B)` énumère tous les sous-ensembles de taille B ; avec `remise=True`, `itertools.product(range(n), repeat=B)` énumère tous les tirages ordonnés. Pour chaque lot, on calcule g_ℬ, on l'ajoute à `somme` et l'on ajoute ‖g_ℬ − ∇ℒ‖² à `ecart2`. Comme tous les lots sont équiprobables, les moyennes simples sont les espérances exactes. **`variance_theorique`** applique les deux formules du point 2.

**`pas_calendrier(t, total, eta_max, eta_min, echauffement)`.** Refuse un échauffement qui ne finit pas avant `total`, ou un t hors de [0 ; total]. Avant `echauffement`, renvoie `eta_max * t / echauffement` ; ensuite, calcule la phase u = (t − W)/(t_max − W) entre 0 et 1 et renvoie η_min + (η_max − η_min)(1 + cos πu)/2.

**`ecreter(g, c)`.** Refuse c ≤ 0. Si la norme dépasse c, renvoie g multiplié par c/‖g‖ et `True` ; sinon, g inchangé et `False`.

**`sgd(X, Y, B, epoques, calendrier, graine, seuil)`.**

- `total` = époques × ⌈n/B⌉ : le calendrier a besoin de connaître la longueur totale.
- À chaque époque, `rng.shuffle(ordre)` mélange les indices avec un générateur à graine fixe : chaque époque voit tous les exemples, dans un ordre nouveau mais reproductible.
- Les lots sont les tranches successives de `ordre` ; le dernier peut être plus court.
- Si un seuil est donné, le gradient passe par `ecreter`, et `ecretes` compte les pas écrêtés.
- Si un poids dépasse 10⁸ en valeur absolue, la fonction s'arrête et signale la divergence, avant que les flottants ne deviennent infinis.

**`entrainer_avec_arret(Xtr, Ytr, Xva, Yva, eta, max_epoques, patience)`.**

- `meilleur` garde le triplet (perte de validation, époque, poids) du meilleur point vu ; au départ, celui des poids nuls.
- À chaque époque : un pas de gradient sur tout l'entraînement, puis la perte de validation, notée avec celle d'entraînement dans `historique`.
- Si la validation s'améliore, `meilleur` est remplacé ; sinon, si l'époque du meilleur a `patience` époques de retard, on s'arrête et l'on renvoie `meilleur`, donc les meilleurs poids.
- Avec `patience=None`, l'entraînement va jusqu'au bout : c'est la courbe « sans arrêt ».

**`main()`, bloc par bloc.**

1. Dix exemples, w = (0 ; 0) : ∇ℒ = (−1,4901 ; 1,9614) et σ² = 10,7368. Pour B = 1, 2, 5 et 10, l'énumération de tous les lots redonne ∇ℒ et la variance de la formule sans remise ; pour B = 1, 2 et 3 avec remise, la variance σ²/B (points 1, 2 et 8).
2. Les écarts-types relatifs pour n = 64 (point 2).
3. Le nombre de pas pour n = 70 et B = 8, puis l'accumulation : 4 micro-lots de 8 redonnent le lot de 32 ; avec des micro-lots de 8, 8, 8 et 2, la moyenne naïve est fausse et la moyenne pondérée juste (point 3).
4. Le calendrier aux pas 0, 5, 10, 55 et 100, sa décroissance de 10 à 100 et sa moyenne 0,0505 (point 5).
5. Trois SGD de 40 époques sur 64 exemples à 3 poids, mélangées avec la graine 75, comparées à la solution exacte : l'excès de perte décroît de B = 4 constant à B = 16 constant, puis au calendrier (point 4).
6. Les 20 poids, dont 5 non nuls, puis 24 exemples d'entraînement et 50 de validation. L'arrêt précoce de patience 10 ; puis la même descente sans arrêt jusqu'à 200 époques. Les `assert` vérifient que l'arrêt tombe à t* + 10, que la perte d'entraînement baisse à chaque époque, et que la validation finale est plus de deux fois pire que la meilleure. Puis la comparaison entre arrêt précoce et ridge (point 6).
7. L'écrêtage de (3 ; 4), l'écrêtage par valeur pour comparaison, puis la SGD sur des données à point aberrant, sans écrêtage puis avec c = 1 (point 7).
8. Quatre entrées invalides : B = 0, un seuil nul, un échauffement aussi long que l'entraînement, une patience nulle.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`produit(a, b)`** — Cette petite fonction est l'outil de base de tout le programme, le produit scalaire qui mesure combien deux listes de nombres vont dans le même sens : elle reçoit deux vecteurs, multiplie leurs composantes deux à deux et renvoie la somme de ces produits, sans vérifier que les longueurs coïncident. Elle sert à la prédiction w·x de la régression linéaire, dans `gradient_exemple`, `perte` et `donnees`, et au cosinus qui compare l'écrêtage par la norme à l'écrêtage par valeur dans la section 7.

**`gradient_exemple(w, x, y)`** — Celle-ci dit à un seul exemple comment il voudrait voir bouger les poids, comme un client unique qui donne son avis sur un produit : elle reçoit les poids, une entrée et sa cible, calcule le résidu r = w·x − y par `produit`, et renvoie r·x, le gradient de la perte ½(w·x − y)² pour cet exemple. Avec des poids nuls, ce gradient vaut simplement −y·x ; la moyenne des dix gradients de la section 1 donne ∇ℒ ≈ (−1,4901 ; 1,9614).

**`gradient_lot(w, X, Y, indices)`** — Cette fonction est le sondage qui interroge un échantillon de clients au lieu de toute la population : elle reçoit les poids, toutes les entrées et cibles, et les indices du lot, lève une `ValueError` si le lot est vide, additionne les gradients des exemples choisis et renvoie leur moyenne, et non leur somme, si bien que la taille du lot ne change pas l'échelle du pas. Quatre micro-lots de 8 moyennés redonnent exactement le gradient du lot de 32, ce que `main` vérifie avant de montrer que la moyenne naïve de micro-lots inégaux est fausse.

**`perte(w, X, Y)`** — Celle-ci est le bulletin de notes du modèle sur un jeu de données : elle reçoit les poids, des entrées et leurs cibles, et renvoie la moyenne de ½(w·x − y)². Elle sert aussi bien sur l'entraînement que sur la validation : dans la section 6, la meilleure perte de validation vaut 0,841 à l'époque 5, alors qu'après 200 époques sans arrêt la perte d'entraînement est tombée à 0,0189 et celle de validation est remontée à 3,679.

**`donnees(rng, n, w_vrai, bruit)`** — Cette fonction est la fabrique de données synthétiques, un laboratoire qui génère des mesures dont on connaît la loi exacte : elle reçoit un générateur à graine, le nombre d'exemples, les vrais poids et l'écart-type du bruit, tire des entrées gaussiennes centrées réduites, puis calcule chaque cible comme w_vrai·x plus un bruit gaussien. Elle renvoie les entrées et les cibles ; `main` l'appelle pour 10, 70, 64, puis 24 et 50 exemples, avec les poids vrais 1 et −2, ou 20 poids dont 5 seulement sont non nuls.

**`variance_theorique(sigma2, n, B, remise)`** — Celle-ci est la formule que l'énumération exhaustive vient confirmer : elle reçoit la variance σ² des gradients individuels, le nombre d'exemples n, la taille de lot B et le mode de tirage, et renvoie σ²/B avec remise, ou σ²/B × (n − B)/(n − 1) sans remise, la correction de population finie. Pour σ² = 10,7368, n = 10 et B = 2 sans remise, elle donne 4,7719, exactement ce que trouve `moments_exacts` sur les 45 lots possibles, et elle tombe à 0 quand le lot contient tous les exemples.

**`ecreter(g, c)`** — Cette fonction est le limiteur de vitesse du gradient, qui raccourcit le pas sans en changer la direction : elle reçoit un gradient et un seuil c, lève une `ValueError` si c n'est pas positif, calcule la norme du gradient et, si elle dépasse c, renvoie le gradient multiplié par c/‖g‖ avec `True`, sinon le gradient inchangé avec `False`. Le gradient (3 ; 4), de norme 5, devient (0,6 ; 0,8) pour c = 1 ; dans la section 7, c'est elle qui sauve la SGD d'un point aberrant, avec 71 pas écrêtés.

**`sgd(X, Y, B, epoques, calendrier, graine, seuil)`** — Celle-ci est la boucle d'entraînement par mini-lots, un entraîneur qui fait faire à l'équipe plusieurs tours de piste en changeant chaque fois l'ordre des coureurs : elle reçoit les données, la taille de lot, le nombre d'époques, une fonction de calendrier du pas, une graine et un seuil d'écrêtage facultatif, lève une `ValueError` si B n'est pas entre 1 et n, puis, à chaque époque, mélange les indices, parcourt les tranches successives, écrête le gradient si un seuil est donné et retire η fois ce gradient aux poids. Elle renvoie les poids, un drapeau de divergence levé dès qu'un poids dépasse 10⁸ en valeur absolue, et le nombre de pas écrêtés ; sur 64 exemples et 40 époques, l'excès de perte passe de 2,21 × 10⁻⁴ avec B = 4 à 8,60 × 10⁻⁷ avec le calendrier en cosinus.

**`entrainer_avec_arret(Xtr, Ytr, Xva, Yva, eta, max_epoques, patience)`** — Cette fonction est l'entraîneur prudent qui garde la meilleure performance en mémoire et arrête la saison quand l'équipe ne progresse plus : elle reçoit les données d'entraînement et de validation, le pas η, le nombre maximal d'époques et la patience, lève une `ValueError` pour une patience inférieure à 1, puis fait à chaque époque un pas de gradient sur tout l'entraînement, note les deux pertes et remplace le meilleur triplet quand la validation s'améliore, ou s'arrête quand le meilleur a `patience` époques de retard. Elle renvoie le meilleur triplet, perte de validation, époque et poids, l'époque d'arrêt et l'historique ; avec une patience de 10, le meilleur tombe à l'époque 5 et l'arrêt à l'époque 15.

**`main()`** — C'est le chef d'expérience qui vérifie, une à une, toutes les règles de l'entraînement par mini-lots : il énumère d'abord tous les lots de dix exemples pour montrer que le gradient de lot est sans biais et que sa variance suit la formule, avec et sans remise, puis calcule les écarts-types relatifs pour n = 64, compte les pas d'une époque et contrôle l'accumulation de micro-lots. Il trace ensuite le calendrier échauffement plus cosinus, compare trois SGD à la solution exacte, montre l'arrêt précoce à l'époque 15 face au surapprentissage de 200 époques, illustre l'écrêtage contre un point aberrant, et termine par quatre entrées invalides qui doivent lever `ValueError`.

```python
"""Étape 75 bis — mini-lots (sans biais, variance en 1/B), époques et accumulation, calendrier warmup + cosinus,
arrêt précoce avec patience, écrêtage du gradient par la norme ; régression linéaire sur données synthétiques."""
import itertools
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- régression linéaire : perte ½(w·x − y)²
def produit(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def gradient_exemple(w: list[float], x: list[float], y: float) -> list[float]:
    """∇ℓᵢ(w) = (w·xᵢ − yᵢ) xᵢ."""
    r = produit(w, x) - y
    return [r * a for a in x]


def gradient_lot(w: list[float], X, Y, indices) -> list[float]:
    """g_B = (1/B) Σ_{i ∈ B} ∇ℓᵢ(w) : la MOYENNE du lot, pas la somme."""
    if not indices:
        raise ValueError("lot vide")
    g = [0.0] * len(w)
    for i in indices:
        g = [a + b for a, b in zip(g, gradient_exemple(w, X[i], Y[i]))]
    return [a / len(indices) for a in g]


def perte(w: list[float], X, Y) -> float:
    return sum(0.5 * (produit(w, x) - y) ** 2 for x, y in zip(X, Y)) / len(X)


def donnees(rng: random.Random, n: int, w_vrai: list[float], bruit: float):
    X = [[rng.gauss(0, 1) for _ in w_vrai] for _ in range(n)]
    return X, [produit(w_vrai, x) + rng.gauss(0, bruit) for x in X]


def resoudre(A: list[list[float]], b: list[float]) -> list[float]:
    """Élimination de Gauss avec pivot partiel : solution exacte des équations normales (XᵀX) w = Xᵀy."""
    n = len(A)
    M = [ligne[:] + [v] for ligne, v in zip(A, b)]
    for c in range(n):
        pivot = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[pivot] = M[pivot], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [a - f * p for a, p in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


# ---------------------------------------------------------------- statistiques du gradient de mini-lot
def moments_exacts(grads: list[list[float]], B: int, remise: bool) -> tuple[list[float], float]:
    """Énumère TOUS les lots de taille B : renvoie E[g_B] et E‖g_B − ∇L‖² (loi uniforme sur les lots)."""
    n = len(grads)
    if not 1 <= B <= n:
        raise ValueError("il faut 1 <= B <= n")
    plein = [sum(g[j] for g in grads) / n for j in range(len(grads[0]))]
    lots = itertools.product(range(n), repeat=B) if remise else itertools.combinations(range(n), B)
    somme, ecart2, nombre = [0.0] * len(plein), 0.0, 0
    for lot in lots:
        g_b = [sum(grads[i][j] for i in lot) / B for j in range(len(plein))]
        somme = [a + b for a, b in zip(somme, g_b)]
        ecart2 += sum((a - b) ** 2 for a, b in zip(g_b, plein))
        nombre += 1
    return [a / nombre for a in somme], ecart2 / nombre


def variance_theorique(sigma2: float, n: int, B: int, remise: bool) -> float:
    """σ²/B avec remise ; (σ²/B)·(n − B)/(n − 1) sans remise (correction de population finie)."""
    return sigma2 / B if remise else sigma2 / B * (n - B) / (n - 1)


# ---------------------------------------------------------------- calendrier du pas, écrêtage, SGD
def pas_calendrier(t: int, total: int, eta_max: float, eta_min: float, echauffement: int) -> float:
    """Montée linéaire de 0 à η_max sur W pas, puis décroissance en cosinus jusqu'à η_min au pas T."""
    if not 0 <= echauffement < total or not 0 <= t <= total:
        raise ValueError("il faut 0 <= W < T et 0 <= t <= T")
    if t < echauffement:
        return eta_max * t / echauffement
    phase = (t - echauffement) / (total - echauffement)
    return eta_min + 0.5 * (eta_max - eta_min) * (1 + math.cos(math.pi * phase))


def ecreter(g: list[float], c: float) -> tuple[list[float], bool]:
    """g ← g · min(1, c/‖g‖) : même direction, norme au plus c."""
    if c <= 0:
        raise ValueError("le seuil d'écrêtage doit être > 0")
    norme = math.sqrt(sum(a * a for a in g))
    return ([a * c / norme for a in g], True) if norme > c else (g, False)


def sgd(X, Y, B: int, epoques: int, calendrier, graine: int, seuil: float | None = None):
    """SGD par mini-lots, mélange à chaque époque ; renvoie (w, a_diverge, nombre de pas écrêtés)."""
    if not 1 <= B <= len(X):
        raise ValueError("il faut 1 <= B <= n")
    rng = random.Random(graine)
    w = [0.0] * len(X[0])
    ordre = list(range(len(X)))
    total = epoques * math.ceil(len(X) / B)
    t = ecretes = 0
    for _ in range(epoques):
        rng.shuffle(ordre)
        for debut in range(0, len(ordre), B):
            g = gradient_lot(w, X, Y, ordre[debut:debut + B])
            if seuil is not None:
                g, coupe = ecreter(g, seuil)
                ecretes += coupe
            eta = calendrier(t, total)
            w = [a - eta * b for a, b in zip(w, g)]
            t += 1
            if max(abs(a) for a in w) > 1e8:
                return w, True, ecretes
    return w, False, ecretes


# ---------------------------------------------------------------- généralisation : arrêt précoce
def entrainer_avec_arret(Xtr, Ytr, Xva, Yva, eta: float, max_epoques: int, patience: int | None):
    """Descente de gradient sur tout l'entraînement ; évalue la validation à chaque époque.
    Arrêt après `patience` époques sans amélioration ; renvoie les MEILLEURS poids, pas les derniers."""
    if patience is not None and patience < 1:
        raise ValueError("la patience doit être >= 1")
    w = [0.0] * len(Xtr[0])
    tous = list(range(len(Xtr)))
    meilleur = (perte(w, Xva, Yva), 0, w)
    historique = []
    for epoque in range(1, max_epoques + 1):
        g = gradient_lot(w, Xtr, Ytr, tous)
        w = [a - eta * b for a, b in zip(w, g)]
        val = perte(w, Xva, Yva)
        historique.append((perte(w, Xtr, Ytr), val))
        if val < meilleur[0]:
            meilleur = (val, epoque, w)
        elif patience is not None and epoque - meilleur[1] >= patience:
            return meilleur, epoque, historique
    return meilleur, max_epoques, historique


def main() -> None:
    print("1. Le gradient d'un mini-lot : sans biais, variance (σ²/B)(n − B)/(n − 1), vérifiées sur TOUS les lots")
    rng = random.Random(75)
    X10, Y10 = donnees(rng, 10, [1.0, -2.0], 0.5)
    w0 = [0.0, 0.0]
    grads = [gradient_exemple(w0, x, y) for x, y in zip(X10, Y10)]
    plein = [sum(g[j] for g in grads) / 10 for j in range(2)]
    sigma2 = sum(sum((a - b) ** 2 for a, b in zip(g, plein)) for g in grads) / 10
    print(f"  n = 10, w = (0, 0) : ∇L = {[round(a, 4) for a in plein]} ; σ² = {sigma2:.4f}")
    for B in (1, 2, 5, 10):
        moyenne, var = moments_exacts(grads, B, remise=False)
        print(f"  sans remise, B = {B:>2} : {math.comb(10, B):>3} lot{'s' if B < 10 else ' '}, E[g_B] = ∇L, E‖g_B − ∇L‖² = {var:.4f}"
              f" = formule {variance_theorique(sigma2, 10, B, False):.4f}")
        assert max(abs(a - b) for a, b in zip(moyenne, plein)) < 1e-12
        assert abs(var - variance_theorique(sigma2, 10, B, False)) < 1e-12
    for B in (1, 2, 3):
        moyenne, var = moments_exacts(grads, B, remise=True)
        assert max(abs(a - b) for a, b in zip(moyenne, plein)) < 1e-12 and abs(var - sigma2 / B) < 1e-12
    print(f"  avec remise, B = 1, 2, 3 : {10}, {10 ** 2}, {10 ** 3} lots ordonnés ; variance = σ²/B exactement")

    print("2. Écart-type relatif du gradient de mini-lot, n = 64 (sans remise)")
    rel = {B: math.sqrt(variance_theorique(1.0, 64, B, False)) for B in (1, 4, 16, 64)}
    print("  " + " ; ".join(f"B = {B} : {r:.3f}" for B, r in rel.items()))
    assert rel[1] == 1.0 and rel[64] == 0.0 and abs(rel[4] - math.sqrt(60 / 252)) < 1e-12

    print("3. Époques, pas et accumulation de gradient")
    X64, Y64 = donnees(rng, 70, [1.0, -2.0], 0.5)
    print(f"  n = 70, B = 8 : {math.ceil(70 / 8)} pas par époque, dernier lot de {70 - 8 * (70 // 8)} exemples")
    w1 = [0.3, 0.1]
    accumule = [sum(c) / 4 for c in zip(*(gradient_lot(w1, X64, Y64, range(8 * k, 8 * k + 8)) for k in range(4)))]
    direct = gradient_lot(w1, X64, Y64, range(32))
    assert max(abs(a - b) for a, b in zip(accumule, direct)) < 1e-12
    tailles = [(0, 8), (8, 16), (16, 24), (24, 26)]       # le dernier micro-lot n'a que 2 exemples
    moyennes = [gradient_lot(w1, X64, Y64, range(a, b)) for a, b in tailles]
    naif = [sum(c) / 4 for c in zip(*moyennes)]
    pondere = [sum((b - a) * m[j] for (a, b), m in zip(tailles, moyennes)) / 26 for j in range(2)]
    vrai = gradient_lot(w1, X64, Y64, range(26))
    print(f"  4 micro-lots de 8 = 1 lot de 32 (écart {max(abs(a - b) for a, b in zip(accumule, direct)):.0e}) ;"
          f" micro-lots 8 + 8 + 8 + 2 : moyenne naïve {[round(a, 4) for a in naif]}, pondérée {[round(a, 4) for a in pondere]},"
          f" vraie {[round(a, 4) for a in vrai]}")
    assert max(abs(a - b) for a, b in zip(pondere, vrai)) < 1e-12 and max(abs(a - b) for a, b in zip(naif, vrai)) > 0.05

    print("4. Calendrier : échauffement linéaire sur 10 pas, puis cosinus de 0.1 à 0.001 jusqu'au pas 100")
    cal = [pas_calendrier(t, 100, 0.1, 0.001, 10) for t in range(101)]
    print("  " + " ; ".join(f"η({t}) = {cal[t]:.4f}" for t in (0, 5, 10, 55, 100)))
    moyenne_cos = sum(cal[10:]) / 91
    print(f"  moyenne de la phase cosinus = {moyenne_cos:.4f} = (η_max + η_min) / 2")
    assert cal[0] == 0.0 and cal[10] == 0.1 and abs(cal[100] - 0.001) < 1e-15 and abs(cal[55] - 0.0505) < 1e-12
    assert all(a >= b for a, b in zip(cal[10:], cal[11:])) and abs(moyenne_cos - 0.0505) < 1e-12

    print("5. SGD : un pas constant laisse un plancher de bruit, que réduisent un grand B ou la décroissance")
    rng5 = random.Random(75)
    X5, Y5 = donnees(rng5, 64, [1.0, -2.0, 0.5], 0.5)
    A = [[sum(x[i] * x[j] for x in X5) for j in range(3)] for i in range(3)]
    w_opt = resoudre(A, [sum(x[i] * y for x, y in zip(X5, Y5)) for i in range(3)])
    exces = {}
    for nom, B, cal_fn in (("B = 4, η = 0.1 constant", 4, lambda t, T: 0.1), ("B = 16, η = 0.1 constant", 16, lambda t, T: 0.1),
                           ("B = 4, échauffement + cosinus", 4, lambda t, T: pas_calendrier(t, T, 0.1, 0.001, T // 20))):
        w, _, _ = sgd(X5, Y5, B, 40, cal_fn, graine=75)
        exces[nom] = perte(w, X5, Y5) - perte(w_opt, X5, Y5)
        print(f"  {nom:<30} : excès de perte après 40 époques = {exces[nom]:.2e}")
    e4, e16, ecos = exces.values()
    assert ecos < e16 < e4 < 1e-3

    print("6. Arrêt précoce : 20 traits, 24 exemples d'entraînement, 50 de validation")
    rng6 = random.Random(75)
    w_vrai = [rng6.gauss(0, 1) if j < 5 else 0.0 for j in range(20)]
    Xtr, Ytr = donnees(rng6, 24, w_vrai, 1.0)
    Xva, Yva = donnees(rng6, 50, w_vrai, 1.0)
    (val_best, ep_best, w_best), ep_arret, _ = entrainer_avec_arret(Xtr, Ytr, Xva, Yva, 0.2, 200, patience=10)
    _, _, hist = entrainer_avec_arret(Xtr, Ytr, Xva, Yva, 0.2, 200, patience=None)
    print(f"  avec patience 10 : meilleure validation {val_best:.3f} à l'époque {ep_best}, arrêt à l'époque {ep_arret}")
    print(f"  sans arrêt, époque 200 : entraînement {hist[-1][0]:.4f}, validation {hist[-1][1]:.3f}")
    assert ep_arret == ep_best + 10 and hist[ep_best - 1][1] == val_best
    assert hist[-1][0] < hist[ep_best - 1][0] and hist[-1][1] > 2 * val_best
    assert all(a[0] >= b[0] for a, b in zip(hist, hist[1:]))           # l'entraînement baisse toujours
    eta, t = 0.1, 50
    for h in (2.0, 0.02):
        arret = 1 - (1 - eta * h) ** t
        ridge = h / (h + 1 / (eta * t))
        print(f"  direction de courbure {h} : arrêt après {t} pas garde {arret:.4f} de w*, ridge λ = 1/(ηt) garde {ridge:.4f}")
    assert abs((1 - (1 - 0.002) ** 50) - 0.0953) < 1e-4 and abs(0.02 / 0.22 - 0.0909) < 1e-4

    print("7. Écrêtage par la norme : même direction, pas borné")
    g, coupe = ecreter([3.0, 4.0], 1.0)
    par_valeur = [max(-1.0, min(1.0, a)) for a in (3.0, 4.0)]
    cos_valeur = produit(par_valeur, [3.0, 4.0]) / (math.sqrt(produit(par_valeur, par_valeur)) * 5.0)
    print(f"  g = (3, 4), c = 1 : par la norme {[round(a, 4) for a in g]} (cosinus 1) ; par valeur {par_valeur} (cosinus {cos_valeur:.4f})")
    assert coupe and g == [0.6, 0.8] and abs(cos_valeur - 7 / (5 * math.sqrt(2))) < 1e-12
    rng7 = random.Random(75)
    X7 = [[rng7.gauss(0, 1), rng7.gauss(0, 1)] for _ in range(31)] + [[25.0, 0.0]]   # une valeur aberrante
    Y7 = [produit([1.0, -2.0], x) + rng7.gauss(0, 0.3) for x in X7[:31]] + [0.0]
    for seuil in (None, 1.0):
        w, diverge, n_ecretes = sgd(X7, Y7, 1, 20, lambda t, T: 0.05, graine=75, seuil=seuil)
        etat = "diverge (|w| > 1e8)" if diverge else f"w = {[round(a, 3) for a in w]}, perte sur les 31 points normaux = {perte(w, X7[:31], Y7[:31]):.4f}"
        print(f"  B = 1, η = 0.05, seuil {seuil} : {etat} ; pas écrêtés : {n_ecretes}")
        if seuil is None:
            assert diverge
        else:
            assert not diverge and abs(w[0] - 1.0) < 0.1 and abs(w[1] + 2.0) < 0.2 and n_ecretes > 0

    for appel in (lambda: sgd(X5, Y5, 0, 1, lambda t, T: 0.1, 0), lambda: ecreter([1.0], 0.0),
                  lambda: pas_calendrier(5, 10, 0.1, 0.0, 10), lambda: entrainer_avec_arret(Xtr, Ytr, Xva, Yva, 0.1, 5, 0)):
        try:
            appel()
        except ValueError:
            pass
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("  B = 0, seuil 0, échauffement ≥ T, patience 0 → ValueError")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Le gradient d'un mini-lot : sans biais, variance (σ²/B)(n − B)/(n − 1), vérifiées sur TOUS les lots
  n = 10, w = (0, 0) : ∇L = [-1.4901, 1.9614] ; σ² = 10.7368
  sans remise, B =  2 :  45 lots, E[g_B] = ∇L, E‖g_B − ∇L‖² = 4.7719 = formule 4.7719
  sans remise, B =  5 : 252 lots, E[g_B] = ∇L, E‖g_B − ∇L‖² = 1.1930 = formule 1.1930
…
  B = 1 : 1.000 ; B = 4 : 0.488 ; B = 16 : 0.218 ; B = 64 : 0.000
…
  η(0) = 0.0000 ; η(5) = 0.0500 ; η(10) = 0.1000 ; η(55) = 0.0505 ; η(100) = 0.0010
…
  B = 4, η = 0.1 constant        : excès de perte après 40 époques = 2.21e-04
  B = 16, η = 0.1 constant       : excès de perte après 40 époques = 1.42e-05
  B = 4, échauffement + cosinus  : excès de perte après 40 époques = 8.60e-07
…
  avec patience 10 : meilleure validation 0.841 à l'époque 5, arrêt à l'époque 15
  sans arrêt, époque 200 : entraînement 0.0189, validation 3.679
…
  B = 1, η = 0.05, seuil None : diverge (|w| > 1e8) ; pas écrêtés : 0
  B = 1, η = 0.05, seuil 1.0 : w = [1.057, -1.831], perte sur les 31 points normaux = 0.0425 ; pas écrêtés : 71
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : chaque règle de l'entraînement par mini-lots se vérifie à la main. Le gradient d'un lot vise juste en moyenne, son bruit suit (σ²/B)(n − B)/(n − 1), le calendrier finit par l'écraser, la validation dit quand s'arrêter, et l'écrêtage sauve l'entraînement d'un seul point aberrant.

### La même boucle en PyTorch (extrait)

```python
# [extrait] — boucle d'entraînement PyTorch, non exécutée par le harnais (PyTorch hors bibliothèque standard)
import torch
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.data import DataLoader

chargeur = DataLoader(jeu_entrainement, batch_size=32, shuffle=True, drop_last=False)
optimiseur = torch.optim.AdamW(modele.parameters(), lr=3e-4, weight_decay=0.01)
total = epoques_max * len(chargeur)
planif = LambdaLR(optimiseur, lambda t: pas_calendrier(t, total, 1.0, 0.01, total // 20))   # facteur multiplicatif
meilleure, attente = float("inf"), 0
for epoque in range(epoques_max):
    modele.train()
    for xb, yb in chargeur:
        perte = critere(modele(xb), yb)                         # moyenne sur le lot (reduction="mean" par défaut)
        optimiseur.zero_grad()
        perte.backward()
        torch.nn.utils.clip_grad_norm_(modele.parameters(), max_norm=1.0)   # écrêtage par la NORME globale
        optimiseur.step()
        planif.step()
    modele.eval()
    with torch.no_grad():
        val = sum(critere(modele(xb), yb).item() for xb, yb in chargeur_validation) / len(chargeur_validation)
    if val < meilleure:
        meilleure, attente = val, 0
        torch.save(modele.state_dict(), "meilleur.pt")         # on garde le MEILLEUR point, pas le dernier
    else:
        attente += 1
        if attente >= 10:
            break
```

`shuffle=True` refait la permutation à chaque époque, comme `rng.shuffle(ordre)`. `LambdaLR` multiplie le pas de base par la valeur renvoyée : on y passe donc `pas_calendrier` avec η_max = 1, ce qui donne une montée jusqu'à 3 × 10⁻⁴ puis une décroissance jusqu'à 1 % de cette valeur. `clip_grad_norm_` écrête la norme de **tous** les gradients du modèle réunis en un seul vecteur, ce qui garde la direction globale ; `clip_grad_value_` serait l'écrêtage par valeur du point 7. `modele.eval()` et `torch.no_grad()` coupent le *dropout* et le calcul de gradient pendant la validation. Sans framework, `sgd` et `entrainer_avec_arret` font la même chose en quelques dizaines de lignes : c'est ce qui permet de lire, de vérifier et de reproduire un entraînement sans dépendre d'une bibliothèque ni d'un service d'entraînement hébergé.

## Squelette algorithmique

Deux algorithmes résument le fichier. Le premier est l'entraînement par mini-lots, avec mélange, calendrier, écrêtage et accumulation : en entrée, les données, B, le nombre d'époques, le calendrier et le seuil ; en sortie, les paramètres. Le second l'enveloppe d'un arrêt précoce : en entrée, une fonction qui fait une époque, un jeu de validation et une patience ; en sortie, les meilleurs paramètres.

```text
ALGORITHME EntraînementParMiniLots
ENTRÉES : n exemples, taille de lot B, micro-lots k (accumulation), K époques, calendrier η(t), seuil c
SORTIE  : θ

  θ ← θ₀ ;  t ← 0 ;  t_max ← K × ⌈n / (k × B)⌉
  POUR époque DE 1 À K FAIRE
      ordre ← permutation aléatoire de 1 … n                  graine fixée : reproductible
      POUR CHAQUE groupe de k micro-lots consécutifs de ordre FAIRE
          G ← 0 ;  m ← 0
          POUR CHAQUE micro-lot ℬ DU groupe FAIRE
              G ← G + |ℬ| × moyenne des ∇ℓᵢ(θ) sur ℬ           pondérer par la taille
              m ← m + |ℬ|
          FIN POUR
          g ← G / m                                          gradient moyen du groupe
          SI ‖g‖ > c ALORS g ← g × c / ‖g‖                    même direction, norme c
          θ ← θ − η(t) × g ;  t ← t + 1
      FIN POUR
  FIN POUR
  RETOURNER θ

ALGORITHME ArrêtPrécoce
ENTRÉES : une époque d'entraînement, perte de validation, patience P, époques maximales K
SORTIE  : meilleurs paramètres θ*, époque t*

  θ* ← θ₀ ;  meilleure ← ℒ_val(θ₀) ;  t* ← 0
  POUR t DE 1 À K FAIRE
      θ ← une époque d'entraînement à partir de θ
      SI ℒ_val(θ) < meilleure ALORS
          meilleure ← ℒ_val(θ) ;  θ* ← θ ;  t* ← t             sauvegarder ce point
      SINON SI t − t* ≥ P ALORS
          RETOURNER θ*, t*                                  P époques sans progrès
      FIN SI
  FIN POUR
  RETOURNER θ*, t*
```

**Complexité :** une époque calcule n gradients individuels, soit O(n × d) pour un modèle linéaire à d paramètres, quelle que soit la taille du lot ; B ne change que le nombre de mises à jour, ⌈n/B⌉ par époque, chacune en O(d). La mémoire de travail d'un pas est O(B × d) pour les activations d'un réseau, d'où la limite de B imposée par le GPU ; l'accumulation la ramène à O(b × d) pour un micro-lot de b exemples sans changer le gradient. L'écrêtage ajoute O(d) par pas pour la norme. L'arrêt précoce ajoute une évaluation de validation par époque, O(n_val × d), et une copie des paramètres à chaque amélioration, O(d) ; il gaspille au plus P époques après le meilleur point. Le programme a aussi une partie qui ne passe pas à l'échelle, par construction : `moments_exacts` énumère C(n, B) ou nᴮ lots, ce qui n'est possible que pour n = 10.

**Du squelette au code :** EntraînementParMiniLots est `sgd` avec k = 1 : la permutation est `rng.shuffle(ordre)`, les tranches `ordre[debut:debut + B]` sont les lots, la moyenne est `gradient_lot`, la ligne « SI ‖g‖ > c » est `ecreter`, et η(t) est l'argument `calendrier`, `pas_calendrier` dans la partie 5. La boucle sur les micro-lots, avec sa pondération par |ℬ|, est faite à la main dans la partie 3 de `main` (`accumule`, puis `pondere`). ArrêtPrécoce est `entrainer_avec_arret` : « une époque d'entraînement » y est un pas de gradient sur le lot complet, `meilleur` contient (meilleure, t*, θ*), et le test `epoque - meilleur[1] >= patience` est la ligne « t − t* ≥ P ».

## Cas d'usage réels aux Émirats

Les tailles de lot, les volumes, les seuils et les durées ci-dessous sont illustratifs ; les nombres qui sortent d'une formule sont ceux du programme.

### Banque — un lot de 64 sur un GPU qui n'en tient que 16

Une banque de détail de Dubaï affine chaque trimestre, sur ses propres serveurs, un adaptateur LoRA qui extrait un JSON des attestations de salaire déposées pour les demandes de prêt personnel. Le réglage validé utilise des lots de 64 documents, mais le GPU disponible n'en tient que 16 à la fois. L'équipe accumule donc 4 micro-lots de 16 avant chaque pas, ce qui redonne exactement le gradient d'un lot de 64 (point 3). Un trimestre, le jeu compte 1 000 documents : le dernier groupe d'une époque ne contient que 40 documents, répartis en micro-lots de 16, 16 et 8. Le script d'origine faisait la moyenne simple des trois moyennes, qui donne au micro-lot de 8 le même poids qu'aux deux autres ; comme dans le programme, où la moyenne naïve donne (−0,7073 ; 1,6126) au lieu de (−0,5010 ; 1,4622), le gradient de ce pas était faux. L'équipe pondère désormais par la taille, ou jette le dernier lot incomplet. Sans cette correction, l'erreur reste petite mais revient à chaque époque, et elle complique la reproduction d'un entraînement que la politique de gestion du risque de modèle exige de pouvoir rejouer. L'indicateur suivi est l'écart entre deux entraînements rejoués avec la même graine, qui doit être nul.

### Assurance — une validation dans le temps, pas au hasard

Un assureur auto et santé, supervisé par la CBUAE, entraîne un classifieur de sinistres suspects sur deux ans de déclarations. La première version tirait la validation au hasard parmi les deux ans : la perte de validation était excellente, et l'arrêt précoce s'arrêtait tard. En production, les performances ont chuté, parce que les schémas de fraude changent, et qu'un tirage au hasard laissait le modèle « voir le futur » de chaque déclaration de validation. L'équipe sépare désormais dans le temps : entraînement sur les dix-huit premiers mois, validation sur les trois suivants, test sur les trois derniers, jamais utilisés avant la mesure finale. Avec cette séparation, la validation remonte bien plus tôt, et l'arrêt précoce de patience 5 rend les poids d'une époque antérieure, comme dans le point 6, où la validation est déjà plus de quatre fois pire à l'époque 200 qu'à l'époque 5. Sans la séparation temporelle, l'assureur aurait annoncé un taux de détection qu'il ne pouvait pas atteindre. L'indicateur suivi est l'écart entre la perte de validation et la perte mesurée sur le premier mois de production.

### Crypto — l'écrêtage pendant une journée de krach

Une plateforme d'actifs virtuels agréée par la VARA réentraîne chaque nuit un petit modèle qui prédit le risque de liquidité de ses pools à partir des volumes et des écarts de prix de la journée. Lors d'une journée de mouvements extrêmes, quelques fenêtres présentent des volumes des dizaines de fois supérieurs à la normale : leur perte a une courbure énorme, et, comme pour le point aberrant x = (25 ; 0) du programme, un seul pas les multipliait par une trentaine. Le modèle de la nuit a divergé et n'a pu être exporté. La plateforme écrête désormais la norme du gradient à 1 : chaque pas est borné par η (point 7), et le programme montre qu'avec ce seuil la même situation converge. L'équipe journalise aussi la part des pas écrêtés : 71 pas sur 640 dans le programme ; une part qui grimpe d'une nuit à l'autre signale un changement dans les données, pas un simple réglage. L'écrêtage ne règle pas le fond, et les fenêtres aberrantes sont aussi examinées séparément par l'équipe de surveillance. Sans lui, l'agent de surveillance aurait travaillé le lendemain avec le modèle de la veille, précisément le jour où le marché avait changé. On suit la part des pas écrêtés par entraînement et le nombre d'entraînements nocturnes non exportés.

### RH — 300 dossiers, un employeur de chaque côté

Un cabinet RH présent dans plusieurs émirats entraîne un modèle qui estime le délai de traitement d'un dossier de permis de travail auprès du MOHRE, à partir de 300 dossiers passés. Avec si peu d'exemples et des dizaines de traits, le surapprentissage est la règle : la perte d'entraînement descend sans fin, et seule la validation dit quand s'arrêter (point 6). La première validation, tirée au hasard, plaçait des dossiers du même employeur des deux côtés ; le modèle reconnaissait l'employeur plutôt que d'apprendre le délai, et la validation était trop optimiste. Le cabinet sépare désormais par employeur : tous les dossiers d'un employeur sont soit dans l'entraînement, soit dans la validation. Il garde une patience de 10 époques et restaure les meilleurs poids, et il vérifie que l'estimation n'utilise aucune donnée que la PDPL ou le contrat client interdisent de traiter, ce qui se confirme avec le texte en vigueur. L'estimation reste indicative : l'agent la présente au candidat comme une fourchette, jamais comme un engagement. On suit l'erreur absolue moyenne sur les dossiers des employeurs absents de l'entraînement.

### Immobilier — passer de 1 à 8 GPU sans tout casser

Une agence et un promoteur à Dubaï et Abu Dhabi entraînent un reranker qui ordonne les annonces proposées par leur agent. Sur un GPU, le réglage était B = 32 et η = 10⁻⁴. En passant à 8 GPU, chacun traite 32 exemples, donc le lot effectif devient 256 et chaque époque compte 8 fois moins de pas. L'équipe applique la règle empirique du point 4 : η multiplié par 8, soit 8 × 10⁻⁴, pour garder le même rapport η/B. Le premier essai a divergé dès les premiers pas : un pas de cette taille, appliqué à des poids encore désordonnés, dépassait la limite de stabilité. L'ajout d'un échauffement sur 5 % des pas, puis d'une décroissance en cosinus jusqu'à 1 % du pas de crête (point 5), a réglé le problème. Sans échauffement, l'équipe aurait conclu à tort que le passage à 8 GPU dégradait le modèle. On suit le NDCG@10 (étape 28) sur un jeu de validation fixe, comparé à celui de l'entraînement sur un seul GPU.

### Secteur public — des lots qui gardent la proportion des langues

Une entité de services publics en ligne accessible par UAE Pass entraîne un classifieur de demandes à partir de messages en arabe et en anglais, dont environ un quart en arabe dans le jeu d'entraînement. Avec des lots de 16 tirés au hasard, la part de l'arabe varie fortement d'un lot à l'autre : certains lots n'en contiennent presque pas, et le gradient de ces pas ne dit rien des messages arabes. Le gradient reste sans biais en moyenne (point 1), mais son bruit est plus grand qu'il ne pourrait l'être. L'équipe stratifie les lots : chaque lot de 16 contient 4 messages arabes et 12 anglais, tirés sans remise dans chaque langue, ce qui supprime la part du bruit due au mélange des langues. Elle stratifie aussi la validation, pour mesurer séparément les deux langues, et entraîne sur des messages pseudonymisés dont les numéros d'Emirates ID sont masqués, comme l'exige la PDPL. Sans stratification, le classifieur progresse par à-coups sur l'arabe et l'arrêt précoce, déclenché par la langue majoritaire, peut s'arrêter avant que la langue minoritaire soit apprise. L'indicateur suivi est l'exactitude par langue sur la validation, avec un écart maximal toléré entre les deux.

## Pièges et limites

- **Additionner au lieu de moyenner.** Le gradient grandit alors avec B, et un η réglé pour un petit lot devient trop grand ; même erreur avec une accumulation non pondérée.
- **Ne pas mélanger les données.** Des données triées par date, par classe ou par client donnent des lots biaisés : le gradient de chaque lot n'est plus une estimation sans biais du vrai gradient.
- **Laisser fuir la validation.** Un même client, un même employeur ou des dates futures des deux côtés rendent la validation optimiste ; on sépare par groupe ou dans le temps, et le test reste intouché jusqu'à la fin.
- **Rendre les derniers poids.** L'arrêt précoce doit restaurer le meilleur point, sinon il rend les P époques de surapprentissage qu'il devait éviter.
- **Écrêter trop bas.** Si presque tous les pas sont écrêtés, tous les pas ont la même longueur ηc et l'entraînement devient une marche de longueur fixe ; on règle c d'après la distribution des normes observées.
- **Agrandir le lot sans échauffement.** La règle « η proportionnel à B » est empirique, et elle exige un échauffement dès que le pas devient grand.

### Exercice feuille blanche

1. Sans regarder le code, écrire `gradient_lot`, `variance_theorique` et `pas_calendrier`, puis retrouver 4,7719 pour B = 2 et 0,0505 pour η(55).
2. Prédire, puis vérifier : pour n = 64 et B = 32, que vaut l'écart-type relatif du gradient de mini-lot sans remise, et avec remise ? (Réponse : √(32 / (32 × 63)) = √(1/63) ≈ 0,126 sans remise ; 1/√32 ≈ 0,177 avec remise.)
3. Trouver le bug : `ecreter` devient `return [max(-c, min(c, a)) for a in g], True`. Que vaut le résultat pour g = (3 ; 4) et c = 1, et quelle propriété du point 7 est perdue ?

## Pour aller plus loin

Le rapport entre le bruit du gradient et sa norme définit une « taille de lot critique » au-delà de laquelle agrandir B n'accélère presque plus l'entraînement (McCandlish et al., 2018). LARS et LAMB adaptent le pas couche par couche pour les très grands lots. Le cosinus avec redémarrages (SGDR, Loshchilov et Hutter, 2016) remonte périodiquement le pas, et les calendriers « échauffement, plateau, décroissance » gardent un pas constant pendant la plus grande partie de l'entraînement. Le lien entre petits lots et meilleure généralisation, souvent attribué au bruit qui éviterait les minima étroits, reste discuté. Enfin, la « double descente » montre qu'au-delà du seuil où le modèle interpole ses données, l'erreur de test peut redescendre : la courbe en U du point 6 n'est pas toute l'histoire.

> Étape 75 bis du parcours · Prérequis : [Optimisation : formules manquantes](<75-Optimisation-Formules.md>) · Suite : [Régularisation L1 et L2](<76-Regularisation-L1-L2.md>)
