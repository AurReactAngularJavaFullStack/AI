# Étape 73 — Descente de Gradient et Low-Rank Adaptation (LoRA)

> Étape 73 du parcours · Prérequis : [Budget de raisonnement](<72e-Budget-de-Raisonnement.md>) · Suite : [Quantification INT8 et INT4](<73b-Quantification-INT8-INT4.md>)

## Définition

La **descente de gradient** est l'algorithme qui fait apprendre un modèle : à chaque pas, elle calcule dans quelle direction la perte (l'erreur mesurée sur des exemples) augmente le plus vite, puis déplace les paramètres d'un petit pas dans la direction opposée. La longueur de ce pas s'appelle le **taux d'apprentissage**, noté η ; trop court, l'apprentissage traîne ; trop long, il diverge, et la démonstration dit exactement où passe la frontière. **LoRA** (*Low-Rank Adaptation*) est une façon de spécialiser (*fine-tuner*) un grand modèle sans toucher à ses poids : on gèle chaque grande matrice W₀ et on n'entraîne qu'une correction ΔW, écrite comme le produit de deux matrices étroites B et A, multiplié par une échelle α_LoRA / r. LoRA réduit fortement le nombre de paramètres **entraînés** et la mémoire de l'optimiseur ; elle ne réduit pas la mémoire occupée par le modèle gelé, qui reste chargé en entier.

## Rôle dans un agent

Le fine-tuning ne tourne pas pendant la boucle percevoir → décider → agir → observer : il se fait hors ligne, avant le déploiement, et il change le composant qui **décide**, c'est-à-dire le modèle lui-même ou un petit modèle auxiliaire (routeur d'intentions, classifieur de garde-fou, reranker). On s'en sert quand le prompt et le RAG ne suffisent plus : un format de sortie très strict à respecter à chaque appel, un dialecte, un style maison, ou un prompt d'exemples devenu si long qu'il pèse sur la facture (étape 72). Les faits qui changent (taux, règlements, prix) restent dans le RAG et dans les outils : un adaptateur appris une fois ne se met pas à jour tout seul. En production, un même modèle de base peut servir plusieurs adaptateurs LoRA, un par client ou par langue, que le routeur de l'agent choisit à chaque requête. La descente de gradient, elle, est le moteur commun de tous ces entraînements ; l'étape 74 la remplace par Adam, qui adapte le pas à chaque poids.

## Équation complète

Descente de gradient :

$$
\theta_{t+1} = \theta_t - \eta \, \nabla_\theta \mathcal{L}(\theta_t)
$$

Garantie de descente quand le gradient est L-lipschitzien :

$$
0 < \eta < \frac{2}{L}
$$

Correction LoRA d'une matrice gelée :

$$
W' = W_0 + \Delta W, \qquad \Delta W = \frac{\alpha_{\text{LoRA}}}{r} \, B A
$$

Formes des matrices :

$$
W_0 \in \mathbb{R}^{d \times k}, \qquad B \in \mathbb{R}^{d \times r}, \qquad A \in \mathbb{R}^{r \times k}, \qquad r \ll \min(d, k)
$$

Calcul d'une sortie, sans fusionner :

$$
h = W' x = W_0 x + \frac{\alpha_{\text{LoRA}}}{r} \, B (A x)
$$

Rang et nombre de paramètres entraînés :

$$
\operatorname{rang}(\Delta W) \le r, \qquad P_{\text{plein}} = d\,k, \qquad P_{\text{LoRA}} = r\,(d + k)
$$

## Décryptage des symboles

$$
\theta_t
$$

**Sens :** les paramètres du modèle après t pas d'apprentissage · **Type / plage :** nombre réel, ou vecteur de réels · **Variable Python :** `theta`

$$
\eta
$$

**Sens :** taux d'apprentissage, la longueur du pas · **Type / plage :** réel > 0, souvent entre 10⁻⁵ et 10⁻¹ · **Variable Python :** `eta`

$$
\mathcal{L}(\theta)
$$

**Sens :** la perte, l'erreur moyenne du modèle sur les exemples d'entraînement · **Type / plage :** réel ≥ 0 · **Variable Python :** `perte(theta)`, `perte_lora(...)`

$$
\nabla_\theta \mathcal{L}
$$

**Sens :** le gradient, vecteur des dérivées partielles de la perte ; il pointe vers la plus forte hausse de la perte · **Type / plage :** même forme que θ · **Variable Python :** `gradient(theta)`, `gradients_lora(...)`

$$
L
$$

**Sens :** constante de régularité : le gradient ne change pas plus vite que L fois le déplacement ; pour une fonction d'une variable, c'est la plus grande courbure ℒ'' · **Type / plage :** réel > 0 · **Variable Python :** pas de variable, L = 2 et L = 20 dans les exemples

$$
W_0
$$

**Sens :** la matrice de poids d'origine d'une couche, **gelée** pendant le fine-tuning · **Type / plage :** matrice d × k · **Variable Python :** `W0`

$$
d, \; k
$$

**Sens :** nombre de lignes (taille de la sortie) et de colonnes (taille de l'entrée) de W₀ · **Type / plage :** entiers > 0, 4096 dans l'exemple du cours · **Variable Python :** `d`, `k`

$$
B, \; A
$$

**Sens :** les deux matrices étroites entraînées ; A comprime l'entrée de k nombres vers r nombres, B la redéploie vers d nombres · **Type / plage :** B est d × r, initialisée à 0 ; A est r × k, initialisée au hasard · **Variable Python :** `B`, `A`

$$
r
$$

**Sens :** le rang LoRA, la largeur du goulet entre A et B · **Type / plage :** entier, 1 ≤ r ≪ min(d, k), souvent 8 ou 16 · **Variable Python :** `r`

$$
\alpha_{\text{LoRA}}
$$

**Sens :** l'échelle LoRA, constante choisie avant l'entraînement ; la correction est multipliée par s = α_LoRA / r · **Type / plage :** réel > 0, souvent 2r · **Variable Python :** `alpha_lora`

$$
\Delta W, \; W'
$$

**Sens :** la correction apprise, et la matrice effective W₀ + ΔW · **Type / plage :** matrices d × k · **Variable Python :** `fusionner(W0, B, A, alpha_lora, r)` renvoie W′

$$
x, \; h
$$

**Sens :** le vecteur d'entrée de la couche, et sa sortie W′x · **Type / plage :** vecteurs de k et de d réels · **Variable Python :** `x`, `h`

Deux changements de notation par rapport à l'ancienne version de ce fichier. Le taux d'apprentissage s'y notait α, et le code appelait aussi `alpha` l'échelle LoRA : un même symbole avait deux sens dans un même calcul. Il s'écrit désormais η, et l'échelle α_LoRA. La perte s'écrit ℒ, pour laisser la lettre L à la constante de régularité. Enfin, l'ancienne équation W′ = W + A × B, avec A de taille 4096 × 8 et sans échelle, contredisait le code, qui calculait W₀ + (α/r) BA avec B de taille d × r : c'est la seconde forme qui est la bonne, celle de l'article d'origine.

## Démonstration

### 1. Pourquoi on soustrait le gradient

Notons g le gradient au point θ. Le développement de Taylor au premier ordre donne

$$
\mathcal{L}(\theta - \eta g) = \mathcal{L}(\theta) - \eta \, \lVert g \rVert^2 + o(\eta)
$$

parce que la variation d'une fonction dérivable, pour un petit déplacement u, vaut ∇ℒ · u plus un reste négligeable devant ‖u‖, et qu'ici u = −ηg donne ∇ℒ · u = −η‖g‖². Comme ‖g‖² > 0 dès que g ≠ 0, la perte baisse pour un η assez petit. C'est aussi la meilleure direction : pour tout vecteur unitaire u, l'inégalité de Cauchy-Schwarz (étape 14) donne ∇ℒ · u ≥ −‖∇ℒ‖, avec égalité seulement pour u = −g / ‖g‖. Aucune autre direction ne fait baisser la perte aussi vite au premier ordre.

### 2. La condition exacte sur une parabole

Prenons ℒ(θ) = (θ − 3)², dont la vallée est en θ = 3, et notons eₜ = θₜ − 3 l'écart à la vallée. Le gradient vaut 2(θ − 3) = 2eₜ, donc

$$
e_{t+1} = e_t - 2\eta\, e_t = (1 - 2\eta)\, e_t
\quad\Longrightarrow\quad
e_t = (1 - 2\eta)^t \, e_0
$$

parce que chaque pas multiplie l'écart par le même facteur. L'écart tend vers 0 si et seulement si ce facteur est de valeur absolue strictement inférieure à 1 :

$$
\lvert 1 - 2\eta \rvert < 1 \iff -1 < 1 - 2\eta < 1 \iff 0 < \eta < 1
$$

Trois régimes en découlent. Pour 0 < η < 0,5, le facteur est positif : θ monte vers 3 sans jamais le dépasser. Pour η = 0,5, le facteur vaut 0 et un seul pas suffit. Pour 0,5 < η < 1, le facteur est négatif : θ saute d'un côté à l'autre de la vallée, mais de moins en moins loin. Au-delà de 1, chaque saut est plus long que le précédent. En partant de θ₀ = 0, donc e₀ = −3 : avec η = 0,1, le facteur vaut 0,8 et, après 50 pas, θ = 3 − 3 × 0,8⁵⁰ = 2,99996 ; avec η = 1,05, le facteur vaut −1,1 et, après 20 pas, θ = 3 − 3 × 1,1²⁰ = −17,18, pour une perte de 407,3.

### 3. Le cas général : η < 2/L

On suppose le gradient L-lipschitzien : ‖∇ℒ(a) − ∇ℒ(b)‖ ≤ L‖a − b‖ pour tous a et b. Le **lemme de descente** affirme alors

$$
\mathcal{L}(b) \le \mathcal{L}(a) + \nabla\mathcal{L}(a) \cdot (b - a) + \frac{L}{2} \lVert b - a \rVert^2
$$

Preuve : la formule de Taylor avec reste intégral écrit l'écart à la tangente comme une intégrale,

$$
\mathcal{L}(b) - \mathcal{L}(a) - \nabla\mathcal{L}(a)\cdot(b-a) = \int_0^1 \bigl(\nabla\mathcal{L}(a + s(b-a)) - \nabla\mathcal{L}(a)\bigr)\cdot(b-a)\, ds
$$

et chaque terme de l'intégrale est au plus L s ‖b − a‖², par Cauchy-Schwarz puis par la condition de Lipschitz ; l'intégrale de L s de 0 à 1 vaut L/2. On applique le lemme au pas de descente, b = a − ηg :

$$
\mathcal{L}(a - \eta g) \le \mathcal{L}(a) - \eta \Bigl(1 - \frac{L\eta}{2}\Bigr) \lVert g \rVert^2
$$

La parenthèse est positive si et seulement si 0 < η < 2/L : dans cet intervalle, chaque pas fait baisser la perte d'au moins une quantité proportionnelle à ‖g‖². Le choix η = 1/L maximise la baisse garantie, qui vaut alors ‖g‖² / (2L). Sur la parabole du point 2, ℒ'' = 2, donc L = 2 et 2/L = 1 : on retrouve exactement la condition 0 < η < 1, et l'inégalité y devient une égalité, ce que le code vérifie.

Quand le modèle a plusieurs paramètres, c'est la direction la plus courbée qui fixe L. Sur ℒ(x, y) = x² + 10y², les courbures valent 2 en x et 20 en y, donc L = 20 et il faut η < 0,1. Avec η = 0,09, les deux coordonnées convergent, mais x ne gagne qu'un facteur 0,82 par pas ; avec η = 0,11, y est multiplié par −1,2 à chaque pas et explose. Un seul η pour tous les poids est donc réglé sur le pire d'entre eux : c'est le défaut que corrige Adam (étape 74).

### 4. « Trop petit » veut dire lent, pas piégé

Avec η = 0,001, le facteur vaut 0,998 : après 20 pas, θ n'est qu'à 0,118, alors que la vallée est à 3. La direction est la bonne, le pas est trop court. L'ancienne version affirmait qu'un pas trop petit « bloque dans un minimum local ». C'est inexact : un minimum local est une propriété de la fonction, pas du pas. Un petit pas y arrive lentement, un grand pas peut parfois en sauter, mais la parabole n'en a pas, et la lenteur suffit à expliquer ce qu'on observe.

### 5. Le rang de BA est au plus r

La colonne j du produit BA vaut B multipliée par la colonne j de A. C'est donc une combinaison linéaire des r colonnes de B. Toutes les colonnes de BA vivent ainsi dans l'espace engendré par les colonnes de B, qui est de dimension au plus r, d'où

$$
\operatorname{rang}(BA) \le \operatorname{rang}(B) \le r
$$

LoRA ne peut donc apprendre que des corrections de rang au plus r. Sur une couche 4 × 4 avec r = 2, la correction ne pourra jamais valoir l'identité I₄, de rang 4. Le code mesure ce rang par élimination de Gauss.

### 6. Le compte des paramètres

B contient d × r nombres et A en contient r × k, soit r(d + k) en tout, contre d × k pour la matrice pleine. Le facteur de réduction vaut

$$
\frac{d\,k}{r\,(d + k)} \;\overset{d = k}{=}\; \frac{d}{2r}
$$

Pour d = k = 4096 et r = 8 : 16 777 216 paramètres pleins, 8 × 8192 = 65 536 paramètres LoRA, facteur 4096 / 16 = 256, soit 99,61 % de paramètres entraînés en moins.

### 7. Ce que LoRA économise vraiment en mémoire

L'ancienne version annonçait « la mémoire GPU nécessaire diminue de 99 % ». C'est faux, parce que W₀ reste en mémoire : on la gèle, on ne la supprime pas. Comptons les nombres stockés pour une couche entraînée avec Adam (étape 74), qui garde, pour chaque poids entraîné, le poids, son gradient et deux moyennes m et v. En entraînement complet, cela fait 4dk nombres. Avec LoRA, on garde W₀ (dk nombres, sans gradient ni moments) plus quatre copies de r(d + k) :

$$
\frac{d\,k + 4\,r\,(d+k)}{4\,d\,k} = \frac{16\,777\,216 + 262\,144}{67\,108\,864} = 0{,}2539
$$

La baisse vaut donc 74,61 % sur ce compte, pas 99 %. Et ce compte ignore encore les activations, que l'entraînement doit garder pour la rétropropagation (étape 75) et que LoRA ne réduit pas. Pour réduire aussi la place de W₀, il faut la quantifier (QLoRA, voir « Pour aller plus loin »).

### 8. Pourquoi B part de zéro, et pas A aussi

Avec B = 0, ΔW = 0 : le premier appel répond exactement comme le modèle d'origine. Il faut encore que l'apprentissage puisse démarrer. Prenons la perte ℒ = ½‖h − y‖² et notons δ = h − y. Comme hᵢ = (W₀x)ᵢ + s ∑ⱼ Bᵢⱼ (Ax)ⱼ, avec s = α_LoRA / r, la dérivée de hᵢ par rapport à Bᵢⱼ vaut s(Ax)ⱼ. En dérivant de même par rapport à Aⱼₗ, on obtient

$$
\frac{\partial \mathcal{L}}{\partial B} = s \, \delta \, (A x)^\top,
\qquad
\frac{\partial \mathcal{L}}{\partial A} = s \, (B^\top \delta) \, x^\top
$$

Avec B = 0, le gradient de A est nul, mais celui de B ne l'est pas tant que Ax ≠ 0 et δ ≠ 0 : B bouge au premier pas, et A suit dès que B n'est plus nulle. Si l'on mettait aussi A à zéro, les deux gradients seraient nuls et rien n'apprendrait jamais. Le code vérifie les deux formules contre une différence finie centrée. Remarque : partant de B = 0, un pas de gradient donne B = −ηs δ (Ax)ᵀ, un produit d'une colonne par une ligne ; la correction sBA est alors de rang 1, ce que le code affiche aussi.

### 9. La fusion est exacte

Par distributivité puis associativité du produit matriciel,

$$
\Bigl(W_0 + \frac{\alpha_{\text{LoRA}}}{r} B A\Bigr) x = W_0 x + \frac{\alpha_{\text{LoRA}}}{r} B (A x)
$$

On peut donc, après l'entraînement, calculer une fois W′ et ne plus garder ni A ni B : la latence redevient celle de la couche d'origine. Si l'on garde l'adaptateur séparé pour pouvoir en changer à chaque requête, le surcoût vaut r(d + k) multiplications par vecteur, contre dk : 65 536 / 16 777 216 = 0,39 % pour l'exemple du cours.

### 10. Exemple fait à la main (le code reprend ces nombres)

On prend W₀ = I₄, r = 2, α_LoRA = 4, donc s = 2, et

$$
A = \begin{pmatrix} 1 & 0 & 0 & 1 \\ 0 & 1 & 1 & 0 \end{pmatrix},
\qquad
x = \begin{pmatrix} 1 \\ 2 \\ -1 \\ 0{,}5 \end{pmatrix},
\qquad
y = \begin{pmatrix} 1 \\ 2{,}5 \\ -1{,}5 \\ 1 \end{pmatrix}
$$

On calcule Ax = (1 + 0,5 ; 2 − 1) = (1,5 ; 1). Avec B = 0, h = x, donc δ = (0 ; −0,5 ; 0,5 ; −0,5) et ℒ = ½ × 3 × 0,25 = 0,375. Le gradient de B vaut s δ (Ax)ᵀ :

$$
\frac{\partial \mathcal{L}}{\partial B} = 2 \begin{pmatrix} 0 \\ -0{,}5 \\ 0{,}5 \\ -0{,}5 \end{pmatrix} \begin{pmatrix} 1{,}5 & 1 \end{pmatrix} = \begin{pmatrix} 0 & 0 \\ -1{,}5 & -1 \\ 1{,}5 & 1 \\ -1{,}5 & -1 \end{pmatrix}
$$

Un pas η = 0,1 donne B = −0,1 fois ce gradient, soit les lignes (0 ; 0), (0,15 ; 0,1), (−0,15 ; −0,1), (0,15 ; 0,1). Alors B(Ax) = (0 ; 0,325 ; −0,325 ; 0,325), la correction vaut le double, et h = (1 ; 2,65 ; −1,65 ; 1,15). Le nouvel écart vaut δ = (0 ; 0,15 ; −0,15 ; 0,15), et la perte tombe de 0,375 à ½ × 3 × 0,0225 = 0,03375. La matrice fusionnée I₄ + 2BA donne le même h.

## Effets et comportement

- **η trop grand diverge, η trop petit traîne.** Sur une parabole de courbure L, la frontière exacte est 2/L ; η = 1/L est le pas qui garantit la plus grande baisse.
- **Le poids le plus courbé fixe le pas de tous.** Avec un seul η, les directions plates avancent lentement : c'est la motivation d'Adam (étape 74).
- **Le rang r règle la capacité de l'adaptateur.** Trop petit, la correction n'a pas la place d'exprimer la spécialisation ; trop grand, on se rapproche d'un entraînement complet, avec son coût et son risque de surapprentissage (étape 76).
- **α_LoRA règle l'amplitude de la correction.** À B et A fixés, l'effet est proportionnel à α_LoRA / r : si l'on double r sans toucher à α_LoRA, l'échelle s est divisée par deux.
- **Un adaptateur se retire.** Tant qu'il n'est pas fusionné, enlever B et A redonne exactement W₀ : c'est un retour arrière gratuit.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| θₜ, η | `theta`, `eta` |
| ℒ(θ) = (θ − 3)², ℒ′(θ) | `perte(theta)`, `gradient(theta)` |
| θₜ₊₁ = θₜ − η ℒ′(θₜ) | `descente(theta, eta, pas)` |
| ℒ(x, y) = x² + 10y² | `descente_2d(x, y, eta, pas)` |
| W₀, B, A, x, y | `W0`, `B`, `A`, `x`, `y` |
| r, α_LoRA, s = α_LoRA / r | `r`, `alpha_lora`, `s` |
| rang(M) | `rang(M)` |
| dk, r(d + k) | `nombre_de_parametres(d, k, r)` |
| 4dk, dk + 4r(d + k) | `nombres_stockes_adam(d, k, r)` |
| h = W₀x + s B(Ax) | `forward_lora(W0, B, A, x, alpha_lora, r)` |
| W′ = W₀ + s BA | `fusionner(W0, B, A, alpha_lora, r)` |
| ∂ℒ/∂B, ∂ℒ/∂A | `gradients_lora(W0, B, A, x, y, alpha_lora, r)` |

### Déroulé, ligne par ligne

Le code exécute la descente sur la parabole et sur la fonction à deux courbures, puis LoRA sur une couche 4 × 4. Les tailles 4096 du cours ne sont pas allouées : un tableau de 16 millions de flottants n'apprend rien de plus que le compte d × k, et la mécanique est la même sur 4 × 4.

**`perte(theta)` et `gradient(theta)`.** La vallée est en θ = 3.

- `perte` renvoie `(theta - cible) ** 2`. À θ = 0, la perte vaut 9 ; à θ = 3, elle vaut 0.
- `gradient` renvoie `2.0 * (theta - cible)`. À θ = 0, la pente vaut −6 : la perte baisse si l'on augmente θ. Le 2 vient de la dérivée de u², qui vaut 2u, avec u = θ − 3.

**`descente(theta, eta, pas)`.**

- `if eta <= 0 or pas < 0` : un pas nul ou négatif n'a pas de sens, on lève `ValueError`.
- `historique = [theta]` garde le point de départ.
- `theta = theta - eta * gradient(theta)` est la formule, mot pour mot. Avec `eta = 0.1` et θ = 0 : 0 − 0,1 × (−6) = 0,6. Soustraire une pente négative fait monter θ vers la vallée.
- Dans `main`, la boucle `for t, theta in enumerate(hist)` compare chaque point à la forme fermée `3 - 3 * (1 - 2 * eta) ** t` démontrée au point 2, pour les cinq valeurs de η. Avec `eta = 1.05`, θ₁ = 6,3 : on a sauté de l'autre côté de la vallée, et θ₂₀ = −17,182.
- Le lemme de descente est vérifié en égalité : `perte(0.0 - eta * g)` vaut `perte(0.0) - eta * (1 - 2 * eta / 2) * g * g`, où le premier 2 est L.

**`descente_2d(x, y, eta, pas)`.** Le gradient de x² + 10y² vaut (2x, 20y). La ligne `x, y = x - eta * 2.0 * x, y - eta * 20.0 * y` met à jour les deux coordonnées en même temps. Après 50 pas depuis (1, 1) : avec `eta = 0.09`, x = 0,82⁵⁰ ≈ 4,91 × 10⁻⁵ et y = (−0,8)⁵⁰ ≈ 1,43 × 10⁻⁵ ; avec `eta = 0.11`, x converge encore (4,02 × 10⁻⁶) mais y = (−1,2)⁵⁰ ≈ 9 100.

**`matmul`, `matvec`, `addition`, `echelle`, `zeros`.** Les opérations de matrices sur des listes de listes. Dans `matmul(A, B)`, la case (i, j) vaut `sum(A[i][k] * B[k][j] for k in range(m))`, le produit scalaire de la ligne i de A et de la colonne j de B ; si `len(A[0]) != len(B)`, ce produit n'a pas de sens et on lève `ValueError`.

**`rang(M)`.** Élimination de Gauss. Pour chaque colonne `c`, on prend comme pivot la ligne restante de plus grande valeur absolue ; si elle est sous `tol = 1e-9`, la colonne n'apporte rien et on passe. Sinon on soustrait aux lignes du dessous le multiple `f = R[i][c] / R[r][c]` de la ligne pivot, et le rang augmente de 1. Sur I₄, on trouve 4 ; sur BA, jamais plus que 2.

**`nombre_de_parametres(d, k, r)`.** `plein = d * k` vaut 16 777 216 pour 4096 × 4096 ; `lora = r * (d + k)` vaut 8 × 8192 = 65 536 ; le rapport vaut 256,0. C'est le compte des poids **entraînés** ; le mot « gèlerait » de l'ancienne version était inversé : c'est `plein` qu'on entraînerait dans un fine-tuning complet, et W₀ qu'on gèle avec LoRA.

**`nombres_stockes_adam(d, k, r)`.** Renvoie `4 * d * k` (poids, gradient, m et v pour chaque poids) et `d * k + 4 * lora` (W₀ gelé, plus poids, gradient, m et v pour A et B) : 67 108 864 contre 17 039 360, un rapport de 0,25390625 exactement.

**`forward_lora(W0, B, A, x, alpha_lora, r)`.** La sortie pendant l'entraînement, sans fusion.

- La garde vérifie que B a `r` colonnes et A `r` lignes ; avec `r = 3` alors que B est 4 × 2, on lève `ValueError`.
- `s = alpha_lora / r` vaut 4 / 2 = 2.
- `base = matvec(W0, x)` : ce que le modèle gelé répond ; avec W₀ = I₄, c'est x lui-même, `[1.0, 2.0, -1.0, 0.5]`.
- `compresse = matvec(A, x)` : de 4 nombres à 2, `[1.5, 1.0]`. C'est le goulet.
- `delta = matvec(B, compresse)` : de 2 nombres à 4, la même forme que `base`.
- `return [b + s * dl ...]` ajoute la correction multipliée par 2.

**`fusionner(W0, B, A, alpha_lora, r)`.** `matmul(B, A)` produit une matrice 4 × 4, `echelle(..., alpha_lora / r)` la multiplie par 2, `addition(W0, ...)` l'ajoute à W₀. On obtient W′, de la même forme que W₀.

**`perte_lora` et `gradients_lora`.** `perte_lora` renvoie ½‖h − y‖². `gradients_lora` calcule `delta = h - y`, puis `g_b[i][j] = s * delta[i] * ax[j]` et `g_a[i][j] = s * bt_delta[i] * x[j]`, où `bt_delta` est Bᵀδ : ce sont les deux formules du point 8. Avec B = 0, `delta` vaut `[0.0, -0.5, 0.5, -0.5]`, `g_b` vaut `[[0.0, 0.0], [-1.5, -1.0], [1.5, 1.0], [-1.5, -1.0]]` et `g_a` est entièrement nul.

**`ecart_gradient_numerique(...)`.** Pour chaque case de B puis de A, on ajoute puis retranche `h = 1e-6`, on recalcule la perte, on forme `(plus - moins) / (2 * h)` et on garde le plus grand écart avec le gradient analytique. On remet la case à sa valeur d'origine après chaque essai, sinon les essais suivants seraient faussés. L'écart reste sous `1e-6` avant et après le pas.

**`main()`, bloc par bloc.**

1. Les cinq valeurs de η, comparées à la forme fermée, puis quatre `assert` sur les nombres de la démonstration : un pas suffit pour η = 0,5 ; 2,99996 après 50 pas pour η = 0,1 ; 0,118 pour η = 0,001 ; −17,18 et une perte de 407,3 pour η = 1,05.
2. Les deux η sur x² + 10y² : 0,09 converge, 0,11 fait exploser y au-delà de 1 000.
3. Les deux comptes de LoRA : paramètres (facteur 256) et mémoire (−74,61 %).
4. La couche 4 × 4 : avec B = 0, la sortie égale W₀x ; les gradients valent ceux du point 10 ; avec A et B tous deux nuls, tout gradient est nul. Après un pas η = 0,1 sur B, la perte vaut 0,03375 et h vaut `[1.0, 2.65, -1.65, 1.15]`, exactement comme la matrice fusionnée. La correction issue d'un seul pas est de rang 1 ; avec une matrice B quelconque, `B_main`, elle est de rang 2, la sortie vaut `[0.9, 2.6, -2.0, 1.1]`, et l'identité, de rang 4, reste hors d'atteinte.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`perte(theta, cible)`** — Cette fonction dessine le paysage dans lequel le randonneur de la descente cherche le fond de la vallée : elle reçoit une position θ et la cible, 3 par défaut, et renvoie le carré de leur écart, (θ − 3)², sans aucun contrôle. La perte vaut 9 au point de départ θ = 0 et 0 au fond de la vallée ; `main` s'en sert pour afficher la perte atteinte après vingt pas, 407,3 quand le pas η = 1,05 fait diverger la descente, et pour vérifier le lemme de descente en égalité.

**`gradient(theta, cible)`** — Celle-ci est la boussole du randonneur, qui lui indique dans quel sens le terrain monte et avec quelle pente : elle reçoit θ et la cible, 3 par défaut, et renvoie la dérivée 2(θ − 3), le facteur 2 venant de la dérivée de u², qui vaut 2u. À θ = 0, elle renvoie −6 : la pente est négative, si bien que la perte baisse quand on augmente θ, et c'est ce nombre que `descente` multiplie par η avant de le soustraire.

**`descente(theta, eta, pas)`** — Cette fonction est le randonneur lui-même, qui fait un pas contre la pente à chaque instant : elle reçoit le point de départ, le pas d'apprentissage η et le nombre de pas, lève une `ValueError` si η n'est pas positif ou si le nombre de pas est négatif, puis applique `pas` fois la règle θ ← θ − η ℒ′(θ) en gardant chaque position dans un historique. Elle renvoie toute la trajectoire, point de départ compris ; partie de 0 avec η = 0,1, elle passe par 0,6 puis atteint 2,99996 au bout de 50 pas, tandis qu'avec η = 1,05 elle saute de l'autre côté de la vallée, à 6,3, et finit à −17,182 après 20 pas.

**`matvec(M, x)`** — Celle-ci est l'ouvrier du produit matrice-vecteur, qui applique une transformation à une liste de nombres : elle reçoit une matrice sous forme de liste de lignes et un vecteur, lève une `ValueError` si le nombre de colonnes ne correspond pas à la longueur du vecteur, puis renvoie, pour chaque ligne, le produit scalaire de cette ligne avec le vecteur. Avec W₀ = I₄, elle rend x lui-même, 1 ; 2 ; −1 ; 0,5, et avec la matrice A de l'exemple elle compresse ces quatre nombres en deux, 1,5 et 1, le goulet de LoRA.

**`addition(A, B)`** — Cette fonction est le comptable qui superpose deux grilles de même forme case par case : elle reçoit deux matrices et renvoie la matrice dont chaque case est la somme des cases correspondantes, sans vérifier que les formes coïncident, puisqu'elle lit les dimensions sur la première. Elle ne sert qu'à `fusionner`, où elle ajoute à la matrice gelée W₀ la correction mise à l'échelle s × BA pour produire la matrice fusionnée W′, de la même forme 4 × 4 que W₀.

**`echelle(M, s)`** — Celle-ci est le photocopieur réglé sur un facteur d'agrandissement : elle reçoit une matrice et un nombre s, et renvoie une nouvelle matrice dont chaque case est multipliée par s, la matrice d'origine restant intacte. Dans `fusionner`, elle multiplie le produit BA par l'échelle s = α_LoRA / r, qui vaut 4/2 = 2 dans l'exemple, avant que `addition` ne l'ajoute à W₀.

**`zeros(lignes, colonnes)`** — Cette fonction est le menuisier qui fabrique une étagère vide aux dimensions demandées : elle reçoit un nombre de lignes et de colonnes, et renvoie une matrice de cette forme entièrement remplie de 0,0, chaque ligne étant une liste distincte pour qu'on puisse en modifier une case sans toucher aux autres. Elle fournit la matrice B nulle de départ, 4 × 2, grâce à laquelle le modèle gelé reste intact au début de l'entraînement, ainsi que les matrices A et B toutes deux nulles qui montrent que tous les gradients s'annulent alors.

**`nombres_stockes_adam(d, k, r)`** — Celle-ci est l'intendant qui compte les cases mémoire qu'exige l'entraînement d'une couche avec l'optimiseur Adam : elle reçoit les dimensions d et k de la couche et le rang r, et renvoie deux nombres, 4dk pour un entraînement complet, qui garde le poids, son gradient et les deux moments m et v, puis dk + 4r(d + k) pour LoRA, qui garde W₀ gelée et quatre copies seulement des petites matrices A et B. Pour 4 096 × 4 096 et r = 8, cela fait 67 108 864 contre 17 039 360 nombres, un rapport de 0,25390625, soit une baisse de 74,61 % et non de 99 %.

**`forward_lora(W0, B, A, x, alpha_lora, r)`** — Cette fonction calcule la réponse de la couche pendant l'entraînement, comme un orchestre où l'on ajoute au son de l'ensemble celui d'un petit pupitre de solistes : elle reçoit la matrice gelée, les matrices B et A, l'entrée x, α_LoRA et le rang r, lève une `ValueError` si B n'a pas r colonnes ou A pas r lignes, puis calcule W₀x, compresse x en r nombres par A, les redéploie par B et ajoute cette correction multipliée par s = α_LoRA / r. Elle renvoie la sortie h ; avec B nulle, elle égale exactement W₀x, et après un pas de descente elle vaut 1 ; 2,65 ; −1,65 ; 1,15.

**`fusionner(W0, B, A, alpha_lora, r)`** — Celle-ci est le fondeur qui coule définitivement la correction apprise dans le métal du modèle : elle reçoit W₀, B, A, α_LoRA et r, calcule le produit BA, le multiplie par α_LoRA / r grâce à `echelle` et l'ajoute à W₀ par `addition`. Elle renvoie la matrice fusionnée W′, de la même forme que W₀, si bien qu'un seul produit matrice-vecteur suffit au moment de répondre ; `main` vérifie que W′x redonne exactement la sortie de `forward_lora`, 1 ; 2,65 ; −1,65 ; 1,15.

**`perte_lora(W0, B, A, x, y, alpha_lora, r)`** — Cette fonction mesure l'écart entre ce que la couche répond et ce qu'on attendait d'elle : elle reçoit les mêmes matrices et réglages que `forward_lora`, plus la sortie voulue y, calcule la sortie h par `forward_lora` et renvoie la moitié de la somme des carrés des écarts, ½‖h − y‖². Avec B nulle, elle vaut 0,375 ; après un seul pas de descente de η = 0,1 sur B, elle tombe à 0,03375, et `ecart_gradient_numerique` l'appelle en boucle pour former les différences centrées.

**`gradients_lora(W0, B, A, x, y, alpha_lora, r)`** — Celle-ci est le géomètre qui indique à chaque petite matrice dans quel sens tourner ses boutons : elle reçoit les mêmes arguments que `perte_lora`, calcule l'erreur δ = h − y, la compression Ax et le produit Bᵀδ, puis renvoie le couple des gradients, s × δ × (Ax)ᵀ pour B et s × Bᵀδ × xᵀ pour A. Avec B nulle, δ vaut 0 ; −0,5 ; 0,5 ; −0,5, le gradient de B a pour lignes 0 et 0, −1,5 et −1, 1,5 et 1, puis −1,5 et −1, tandis que celui de A est entièrement nul, puisque Bᵀδ s'annule.

**`main()`** — C'est le moniteur qui fait faire au programme quatre exercices : il lance d'abord la descente sur la parabole avec cinq pas η, compare chaque point à la forme fermée 3 − 3(1 − 2η)ᵗ et vérifie le lemme de descente, puis montre sur x² + 10y² que η = 0,09 converge et que η = 0,11 fait exploser y. Il compte ensuite les paramètres et la mémoire de LoRA pour une couche 4 096 × 4 096, facteur 256 et −74,61 %, et termine sur la couche 4 × 4 : gradients exacts contrôlés par différences centrées, un pas de descente, la fusion, les rangs 1, 2 et 4, et le refus d'un rang incohérent.

```python
"""Étape 73 — descente de gradient (condition sur η) et LoRA (rang, paramètres, mémoire, gradients, fusion)."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- descente de gradient
def perte(theta: float, cible: float = 3.0) -> float:
    """ℒ(θ) = (θ − 3)² : la vallée est en θ = 3, où la perte vaut 0."""
    return (theta - cible) ** 2


def gradient(theta: float, cible: float = 3.0) -> float:
    """dℒ/dθ = 2(θ − 3)."""
    return 2.0 * (theta - cible)


def descente(theta: float, eta: float, pas: int) -> list[float]:
    """θ_{t+1} = θ_t − η ∇ℒ(θ_t) ; renvoie toute la trajectoire, point de départ compris."""
    if eta <= 0 or pas < 0:
        raise ValueError("il faut eta > 0 et pas >= 0")
    historique = [theta]
    for _ in range(pas):
        theta = theta - eta * gradient(theta)
        historique.append(theta)
    return historique


def descente_2d(x: float, y: float, eta: float, pas: int) -> tuple[float, float]:
    """ℒ(x, y) = x² + 10 y² : gradient (2x, 20y). Courbures 2 et 20, donc L = 20 et 2/L = 0.1."""
    for _ in range(pas):
        x, y = x - eta * 2.0 * x, y - eta * 20.0 * y
    return x, y


# ---------------------------------------------------------------- matrices (listes de listes)
def matmul(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    n, m, p = len(A), len(B), len(B[0])
    if len(A[0]) != m:
        raise ValueError("dimensions incompatibles")
    return [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]


def matvec(M: list[list[float]], x: list[float]) -> list[float]:
    if len(M[0]) != len(x):
        raise ValueError("dimensions incompatibles")
    return [sum(M[i][j] * x[j] for j in range(len(x))) for i in range(len(M))]


def addition(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def echelle(M: list[list[float]], s: float) -> list[list[float]]:
    return [[s * v for v in ligne] for ligne in M]


def zeros(lignes: int, colonnes: int) -> list[list[float]]:
    return [[0.0 for _ in range(colonnes)] for _ in range(lignes)]


def rang(M: list[list[float]], tol: float = 1e-9) -> int:
    """Rang par élimination de Gauss avec pivot partiel."""
    R = [ligne[:] for ligne in M]
    n_lignes, n_col = len(R), len(R[0])
    r = 0
    for c in range(n_col):
        pivot = max(range(r, n_lignes), key=lambda i: abs(R[i][c]), default=None)
        if pivot is None or abs(R[pivot][c]) < tol:
            continue
        R[r], R[pivot] = R[pivot], R[r]
        for i in range(r + 1, n_lignes):
            f = R[i][c] / R[r][c]
            R[i] = [a - f * b for a, b in zip(R[i], R[r])]
        r += 1
        if r == n_lignes:
            break
    return r


# ---------------------------------------------------------------- LoRA
def nombre_de_parametres(d: int, k: int, r: int) -> tuple[int, int, float]:
    """Plein : d·k. LoRA : B (d×r) + A (r×k) = r(d + k). Facteur = d·k / (r(d + k))."""
    if min(d, k, r) <= 0:
        raise ValueError("d, k et r doivent être > 0")
    plein = d * k
    lora = r * (d + k)
    return plein, lora, plein / lora


def nombres_stockes_adam(d: int, k: int, r: int) -> tuple[int, int]:
    """Nombres gardés en mémoire pour UNE couche entraînée avec Adam (hors activations).
    Plein : poids + gradient + m + v = 4dk. LoRA : W0 gelé (dk) + 4 copies de r(d + k)."""
    lora = r * (d + k)
    return 4 * d * k, d * k + 4 * lora


def forward_lora(W0, B, A, x, alpha_lora: float, r: int) -> list[float]:
    """h = W0 x + (α_LoRA / r) · B (A x). B est d×r, A est r×k."""
    if r <= 0 or len(B[0]) != r or len(A) != r:
        raise ValueError("B doit être d×r et A r×k, avec r > 0")
    s = alpha_lora / r
    base = matvec(W0, x)              # ce que répond le modèle gelé
    compresse = matvec(A, x)          # k nombres → r nombres : le goulet
    delta = matvec(B, compresse)      # r nombres → d nombres
    return [b + s * dl for b, dl in zip(base, delta)]


def fusionner(W0, B, A, alpha_lora: float, r: int) -> list[list[float]]:
    """W' = W0 + (α_LoRA / r) · B A : même forme d×k que W0, un seul produit au moment de répondre."""
    return addition(W0, echelle(matmul(B, A), alpha_lora / r))


def perte_lora(W0, B, A, x, y, alpha_lora: float, r: int) -> float:
    """ℒ = ½ ‖h − y‖²."""
    h = forward_lora(W0, B, A, x, alpha_lora, r)
    return 0.5 * sum((hi - yi) ** 2 for hi, yi in zip(h, y))


def gradients_lora(W0, B, A, x, y, alpha_lora: float, r: int):
    """∂ℒ/∂B = s · δ (A x)ᵀ et ∂ℒ/∂A = s · Bᵀ δ xᵀ, avec δ = h − y et s = α_LoRA / r."""
    s = alpha_lora / r
    h = forward_lora(W0, B, A, x, alpha_lora, r)
    delta = [hi - yi for hi, yi in zip(h, y)]
    ax = matvec(A, x)
    bt_delta = [sum(B[i][j] * delta[i] for i in range(len(B))) for j in range(r)]
    g_b = [[s * delta[i] * ax[j] for j in range(r)] for i in range(len(B))]
    g_a = [[s * bt_delta[i] * x[j] for j in range(len(x))] for i in range(r)]
    return g_b, g_a


def ecart_gradient_numerique(W0, B, A, x, y, alpha_lora, r, g_b, g_a, h=1e-6) -> float:
    """Plus grand écart entre le gradient analytique et la différence centrée (ℒ(+h) − ℒ(−h)) / 2h."""
    pire = 0.0
    for M, G in ((B, g_b), (A, g_a)):
        for i in range(len(M)):
            for j in range(len(M[0])):
                ancien = M[i][j]
                M[i][j] = ancien + h
                plus = perte_lora(W0, B, A, x, y, alpha_lora, r)
                M[i][j] = ancien - h
                moins = perte_lora(W0, B, A, x, y, alpha_lora, r)
                M[i][j] = ancien
                pire = max(pire, abs((plus - moins) / (2 * h) - G[i][j]))
    return pire


def main() -> None:
    print("1. Le pas η sur ℒ(θ) = (θ − 3)², départ θ = 0 : l'écart à 3 est multiplié par 1 − 2η")
    for eta in (0.001, 0.1, 0.5, 0.9, 1.05):
        hist = descente(0.0, eta, 20)
        print(f"  η = {eta:<5}  facteur {1 - 2 * eta:+.3f}  θ1 = {hist[1]:7.3f}  θ20 = {hist[-1]:8.3f}  ℒ = {perte(hist[-1]):.4f}")
        for t, theta in enumerate(hist):           # forme fermée démontrée : θt = 3 − 3(1 − 2η)^t
            assert abs(theta - (3 - 3 * (1 - 2 * eta) ** t)) < 1e-9
    assert descente(0.0, 0.5, 1)[1] == 3.0                         # η = 1/L : un seul pas
    assert round(descente(0.0, 0.1, 50)[-1], 5) == 2.99996
    assert round(descente(0.0, 0.001, 20)[-1], 3) == 0.118
    assert round(descente(0.0, 1.05, 20)[-1], 2) == -17.18 and round(perte(descente(0.0, 1.05, 20)[-1]), 1) == 407.3
    # Lemme de descente, L = 2 : ℒ(θ − ηg) = ℒ(θ) − η(1 − Lη/2)g² (égalité pour une quadratique)
    for eta in (0.1, 0.9, 1.05):
        g = gradient(0.0)
        assert abs(perte(0.0 - eta * g) - (perte(0.0) - eta * (1 - 2 * eta / 2) * g * g)) < 1e-9

    print("2. ℒ(x, y) = x² + 10y² : la courbure la plus forte (L = 20) impose η < 2/L = 0.1")
    for eta in (0.09, 0.11):
        x, y = descente_2d(1.0, 1.0, eta, 50)
        print(f"  η = {eta}   après 50 pas : x = {x:.2e}   y = {y:.2e}")
    x, y = descente_2d(1.0, 1.0, 0.09, 50)
    assert abs(x) < 1e-4 and abs(y) < 1e-4
    x, y = descente_2d(1.0, 1.0, 0.11, 50)
    assert abs(y) > 1e3 and abs(x) < 1e-4                        # x converge, y explose

    print("3. LoRA sur une couche 4096 × 4096, rang r = 8")
    plein, lora, facteur = nombre_de_parametres(4096, 4096, 8)
    print(f"  paramètres entraînés : {plein:,} → {lora:,}  (facteur {facteur:.0f}, −{100 * (1 - lora / plein):.2f} %)")
    assert (plein, lora, facteur) == (16_777_216, 65_536, 256.0)
    m_plein, m_lora = nombres_stockes_adam(4096, 4096, 8)
    print(f"  nombres stockés avec Adam : {m_plein:,} → {m_lora:,}  (−{100 * (1 - m_lora / m_plein):.2f} %, pas −99 %)")
    assert (m_plein, m_lora) == (67_108_864, 17_039_360) and m_lora / m_plein == 0.25390625

    print("4. Couche 4 × 4, r = 2, α_LoRA = 4 (échelle s = α_LoRA / r = 2)")
    r, alpha_lora = 2, 4.0
    W0 = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
    A = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 1.0, 0.0]]
    B = zeros(4, r)                                    # B = 0 : au départ, le modèle gelé est intact
    x = [1.0, 2.0, -1.0, 0.5]
    y = [1.0, 2.5, -1.5, 1.0]                          # sortie voulue pour cet exemple
    assert forward_lora(W0, B, A, x, alpha_lora, r) == matvec(W0, x)
    g_b, g_a = gradients_lora(W0, B, A, x, y, alpha_lora, r)
    print(f"  B = 0 : ℒ = {perte_lora(W0, B, A, x, y, alpha_lora, r)}  ∂ℒ/∂B = {g_b}  ∂ℒ/∂A nul : {all(v == 0 for l in g_a for v in l)}")
    assert g_b == [[0.0, 0.0], [-1.5, -1.0], [1.5, 1.0], [-1.5, -1.0]]
    assert all(v == 0.0 for ligne in g_a for v in ligne)
    assert ecart_gradient_numerique(W0, B, A, x, y, alpha_lora, r, g_b, g_a) < 1e-6
    A0, B0 = zeros(r, 4), zeros(4, r)                  # A = 0 ET B = 0 : les deux gradients sont nuls
    assert all(v == 0.0 for M in gradients_lora(W0, B0, A0, x, y, alpha_lora, r) for l in M for v in l)

    eta = 0.1
    B = [[B[i][j] - eta * g_b[i][j] for j in range(r)] for i in range(4)]   # un pas de descente sur B seul
    h = forward_lora(W0, B, A, x, alpha_lora, r)
    W_fus = fusionner(W0, B, A, alpha_lora, r)
    h_fus = matvec(W_fus, x)
    print(f"  après un pas (η = 0.1) : ℒ = {perte_lora(W0, B, A, x, y, alpha_lora, r):.5f}  h = {[round(v, 4) for v in h]}")
    print(f"  après fusion W' = W0 + sBA : h = {[round(v, 4) for v in h_fus]}  rang(BA) = {rang(matmul(B, A))}")
    assert abs(perte_lora(W0, B, A, x, y, alpha_lora, r) - 0.03375) < 1e-12
    assert all(abs(a - b) < 1e-12 for a, b in zip(h, [1.0, 2.65, -1.65, 1.15]))
    assert all(abs(a - b) < 1e-12 for a, b in zip(h, h_fus))
    g_b, g_a = gradients_lora(W0, B, A, x, y, alpha_lora, r)   # B ≠ 0 : on vérifie aussi ∂ℒ/∂A
    assert ecart_gradient_numerique(W0, B, A, x, y, alpha_lora, r, g_b, g_a) < 1e-6

    B_main = [[0.1, -0.2], [0.0, 0.3], [-0.4, 0.1], [0.2, 0.0]]
    print(f"  B quelconque : rang(BA) = {rang(matmul(B_main, A))} ≤ r = {r} ; rang(I₄) = {rang(W0)} : hors d'atteinte")
    assert rang(matmul(B, A)) == 1 and rang(matmul(B_main, A)) == 2 and rang(W0) == 4
    h_main = forward_lora(W0, B_main, A, x, alpha_lora, r)
    assert all(abs(a - b) < 1e-12 for a, b in zip(h_main, [0.9, 2.6, -2.0, 1.1]))

    try:
        forward_lora(W0, B_main, A, x, alpha_lora, 3)
    except ValueError:
        print("  r incohérent avec les formes de B et A → ValueError")
    else:
        raise AssertionError("un rang incohérent aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Le pas η sur ℒ(θ) = (θ − 3)², départ θ = 0 : l'écart à 3 est multiplié par 1 − 2η
  η = 0.001  facteur +0.998  θ1 =   0.006  θ20 =    0.118  ℒ = 8.3074
  η = 0.1    facteur +0.800  θ1 =   0.600  θ20 =    2.965  ℒ = 0.0012
  η = 0.5    facteur +0.000  θ1 =   3.000  θ20 =    3.000  ℒ = 0.0000
  η = 0.9    facteur -0.800  θ1 =   5.400  θ20 =    2.965  ℒ = 0.0012
  η = 1.05   facteur -1.100  θ1 =   6.300  θ20 =  -17.182  ℒ = 407.3333
2. ℒ(x, y) = x² + 10y² : la courbure la plus forte (L = 20) impose η < 2/L = 0.1
  η = 0.09   après 50 pas : x = 4.91e-05   y = 1.43e-05
  η = 0.11   après 50 pas : x = 4.02e-06   y = 9.10e+03
3. LoRA sur une couche 4096 × 4096, rang r = 8
  paramètres entraînés : 16,777,216 → 65,536  (facteur 256, −99.61 %)
  nombres stockés avec Adam : 67,108,864 → 17,039,360  (−74.61 %, pas −99 %)
4. Couche 4 × 4, r = 2, α_LoRA = 4 (échelle s = α_LoRA / r = 2)
  B = 0 : ℒ = 0.375  ∂ℒ/∂B = [[0.0, 0.0], [-1.5, -1.0], [1.5, 1.0], [-1.5, -1.0]]  ∂ℒ/∂A nul : True
  après un pas (η = 0.1) : ℒ = 0.03375  h = [1.0, 2.65, -1.65, 1.15]
  après fusion W' = W0 + sBA : h = [1.0, 2.65, -1.65, 1.15]  rang(BA) = 1
  B quelconque : rang(BA) = 2 ≤ r = 2 ; rang(I₄) = 4 : hors d'atteinte
  r incohérent avec les formes de B et A → ValueError
OK — toutes les vérifications sont passées.
```

Deux nombres à savoir citer en entretien : pour une couche 4096 × 4096 et un rang 8, on entraîne 65 536 valeurs au lieu de 16 777 216, mais la mémoire de l'entraînement ne baisse que d'environ trois quarts, parce que W₀ reste chargée ; et une fois B fondue dans W, le coût d'un appel d'agent ne bouge pas.

## Squelette algorithmique

Deux squelettes résument le fichier. Le premier est la boucle d'entraînement par descente de gradient : en entrée, des paramètres de départ, une fonction qui renvoie le gradient, un pas η et un nombre maximal de pas ; en sortie, les paramètres après la descente. Le second est l'entraînement LoRA d'une couche : en entrée, la matrice gelée W₀, le rang r, l'échelle α_LoRA, des exemples et un pas ; en sortie, la matrice fusionnée W′, prête à servir sans surcoût. L'idée commune : on ne touche qu'aux paramètres entraînables, on recule à chaque pas dans la direction opposée au gradient, et, pour LoRA, on ne fusionne qu'à la fin.

```text
ALGORITHME DescenteDeGradient
ENTRÉES : paramètres θ, fonction gradient, pas η > 0, nombre maximal de pas T, tolérance τ ≥ 0
SORTIE : paramètres θ après au plus T pas, et leur trajectoire

SI η ≤ 0 OU T < 0 ALORS
    RETOURNER ERREUR « pas invalide »
FIN SI
trajectoire ← [θ]
POUR t DE 1 À T FAIRE
    g ← gradient(θ)
    SI ‖g‖ ≤ τ ALORS
        RETOURNER θ, trajectoire              point presque stationnaire : inutile de continuer
    FIN SI
    θ ← θ − η · g                             converge si 0 < η < 2/L (lemme de descente)
    ajouter θ à trajectoire
FIN POUR
RETOURNER θ, trajectoire

ALGORITHME EntraînementLoRA
ENTRÉES : W₀ (d × k, gelée), rang r, échelle α_LoRA, exemples (x, y), pas η > 0, nombre de pas T
SORTIE : W′ = W₀ + (α_LoRA / r) · B · A, de taille d × k

A ← matrice r × k tirée au hasard
B ← matrice d × r remplie de 0                au départ, la couche répond exactement comme W₀
s ← α_LoRA / r
POUR t DE 1 À T FAIRE
    (x, y) ← exemple suivant
    u ← A · x                                  r nombres : le goulet
    h ← W₀ · x + s · (B · u)                   d nombres
    δ ← h − y                                  gradient de ½ ‖h − y‖² par rapport à h
    gB ← s · δ · uᵀ                            d × r
    gA ← s · (Bᵀ · δ) · xᵀ                     r × k, calculé avec l'ANCIEN B
    B ← B − η · gB
    A ← A − η · gA                             W₀ ne change jamais
FIN POUR
W′ ← W₀ + s · (B · A)                          fusion, faite une seule fois
RETOURNER W′
```

**Complexité :** la descente coûte O(T · G) en temps, où G est le coût d'un calcul de gradient, plus O(p) par pas pour la soustraction sur p paramètres ; en mémoire, O(p) pour θ et g, et O(T · p) si l'on garde toute la trajectoire, comme le programme le fait pour l'afficher. Pour un pas LoRA, les produits A · x et Bᵀ · δ coûtent O(r k) et O(d r), B · u et gB coûtent O(d r), gA coûte O(r k), mais le produit gelé W₀ · x coûte O(d k) et domine : un pas vaut O(d k + r (d + k)) en temps. En mémoire, W₀ occupe O(d k) et ne reçoit ni gradient ni état d'optimiseur ; A, B et leurs gradients occupent O(r (d + k)), c'est le compte du point 7 de la démonstration. La fusion finale coûte O(d r k) une seule fois, puis chaque réponse coûte O(d k), comme la couche d'origine.

**Du squelette au code :** la garde « SI η ≤ 0 OU T < 0 » est celle de `descente(theta, eta, pas)`. La boucle « POUR t », la ligne « θ ← θ − η · g » et l'ajout à la trajectoire sont les trois lignes de la boucle de `descente`, avec `gradient(theta)` pour la fonction gradient ; le programme n'a pas le test « ‖g‖ ≤ τ » : il fait toujours `pas` itérations, pour pouvoir comparer les trajectoires à la forme fermée. Dans EntraînementLoRA, les lignes « u ← A · x » et « h ← W₀ · x + s · (B · u) » sont `forward_lora`, « δ », « gB » et « gA » sont `gradients_lora`, et la mise à jour de B est la ligne `B = [[B[i][j] - eta * g_b[i][j] ...]]` de `main`, qui ne fait qu'un pas et laisse A fixe. La dernière ligne, « W′ ← W₀ + s · (B · A) », est `fusionner(W0, B, A, alpha_lora, r)`, vérifiée contre `forward_lora` par le programme.

## Cas d'usage réels aux Émirats

Les tailles de modèle, les rangs, les volumes et les prix ci-dessous sont illustratifs : ils servent à faire le calcul, pas à décrire un déploiement réel.

### Banque — un JSON de KYC qui doit passer le schéma à chaque fois

Une banque de détail de Dubaï fait lire à un agent les attestations de salaire et les relevés que ses clients déposent pour une demande de prêt personnel, en arabe comme en anglais. L'agent doit en extraire un JSON strict (employeur, salaire mensuel, date d'embauche) que l'outil `ratio_endettement` consomme ensuite pour vérifier que toutes les mensualités, la nouvelle comprise, restent sous 50 % du revenu, comme le demande la CBUAE. Avec un modèle ouvert hébergé dans les centres de données de la banque, l'équipe entraîne un adaptateur LoRA de rang 16 sur les quatre matrices d'attention de 32 couches de dimension 4096 : 128 matrices × 16 × 8192 = 16 777 216 paramètres entraînés, la taille d'une seule matrice du modèle, contre 2 147 483 648 pour ces mêmes matrices en entraînement complet. La décision de l'agent ne change pas, mais le JSON qu'il produit passe le validateur de schéma (étape 11) beaucoup plus souvent qu'avec un prompt d'exemples. Sans adaptateur, chaque appel transporte deux pages d'exemples, et un JSON mal formé bloque le dossier ou, pire, laisse passer un salaire mal lu dans le calcul d'endettement. La politique interne de gestion du risque de modèle demande de pouvoir revenir en arrière : tant que l'adaptateur n'est pas fusionné, le retirer redonne exactement W₀ (démonstration, point 9). On suit le taux de validation du schéma et la part des dossiers renvoyés à un analyste.

### Secteur public — un adaptateur par langue, choisi par le routeur

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais, et une part des usagers écrit en dialecte émirien plutôt qu'en arabe standard. L'équipe part d'un modèle arabe ouvert comme Jais ou Falcon et entraîne deux adaptateurs LoRA de rang 8 : l'un sur des échanges en dialecte, l'autre sur le vocabulaire administratif anglais. Sur 128 matrices 4096 × 4096, chaque adaptateur compte 128 × 8 × 8192 = 8 388 608 paramètres ; le modèle de base est chargé une fois, et le routeur de l'agent active l'adaptateur qui correspond à la langue détectée dans la question. Gardé séparé, l'adaptateur coûte 0,39 % de multiplications en plus par matrice et par token (démonstration, point 9), un prix faible pour éviter de déployer deux modèles complets. Les données d'entraînement relèvent de la PDPL : on retire les numéros d'Emirates ID (15 chiffres commençant par 784) et les noms avant l'entraînement, parce qu'un adaptateur peut mémoriser ce qu'on lui montre. Sans cette spécialisation, l'agent répond en arabe standard à une question en dialecte, et l'usager finit par demander un conseiller humain. On suit le taux de demandes résolues sans transfert et la part des réponses données dans la langue de la question.

### Assurance — un pas qui marchait diverge quand l'échelle des entrées change

Un assureur auto et santé entraîne par descente de gradient un petit modèle de tri qui estime la complexité d'un sinistre et décide s'il part en traitement automatique ou chez un expert. Une des entrées est le montant réclamé : normalisé entre 0 et 1, il donne une courbure de l'ordre de 1, et η = 0,5 converge ; laissé en AED bruts, autour de 20 000, la courbure 2E[x²] approche 8 × 10⁸, et la démonstration du point 3 impose alors η < 2,5 × 10⁻⁹. Un jour, une nouvelle source de données arrive sans normalisation : avec le même η = 0,5, le facteur |1 − ηL| dépasse 10⁸, la perte devient infinie en quelques pas, et le modèle exporté ne contient plus que des valeurs NaN. Le pipeline d'entraînement de l'assureur applique désormais deux garde-fous : il refuse toute colonne dont l'échelle sort de la plage attendue, et il arrête le job si la perte de validation monte trois évaluations de suite. Sans eux, l'agent de tri aurait reçu un modèle cassé et aurait envoyé tous les dossiers dans la même file. On suit la perte de validation à chaque entraînement et le nombre de jobs interrompus par le garde-fou.

### RH — un adaptateur de style par entreprise cliente

Un cabinet RH présent dans plusieurs émirats rédige, pour une trentaine d'entreprises clientes, des lettres d'offre, des avenants et des attestations, chacune dans le style et la langue de son client. Plutôt que trente modèles, le cabinet sert un seul modèle de base et trente adaptateurs de rang 8 : 30 × 8 388 608 = 251 658 240 paramètres en tout, contre 64 424 509 440 pour trente copies des 128 matrices concernées. Le routeur charge l'adaptateur selon l'identifiant du client, et seuls les deux plus gros clients, servis sur des instances dédiées, reçoivent un modèle fusionné. L'adaptateur apprend le ton et la mise en page, pas le droit : l'indemnité de fin de service (21 jours de salaire de base par an pendant les cinq premières années, 30 au-delà, plafond de 24 mois, selon le décret-loi fédéral 33/2021) reste calculée par l'outil `gratuite_fin_de_service`, jamais de mémoire par le modèle. Sans cette séparation, un adaptateur entraîné sur d'anciennes lettres reproduirait une règle périmée avec beaucoup d'assurance. On suit le taux de lettres validées par le juriste sans correction.

### Immobilier — quand l'adaptateur coûte moins cher que le prompt

Une agence active à Dubaï et à Abu Dhabi fait extraire par un agent les champs de ses annonces : surface en sqft, prix en AED, nombre de chambres, numéro Ejari quand il existe. Le prompt contient 1 800 tokens d'exemples ; sur 150 000 annonces par mois, cela fait 270 millions de tokens d'entrée par mois rien que pour les exemples. Avec un adaptateur LoRA entraîné sur quelques milliers d'annonces corrigées, le prompt tombe à 300 tokens, soit 45 millions par mois, une économie de 225 millions de tokens. L'agent décide de fine-tuner seulement si cette économie, à son tarif par million de tokens, dépasse le coût de l'entraînement et de l'hébergement du modèle ; sinon, il garde le prompt et le met en cache (étape 72). Sans ce calcul, l'équipe fine-tune par réflexe et paie un serveur de GPU pour un volume qu'un cache de prompt aurait absorbé. On suit l'exactitude des champs extraits (correspondance exacte, étape 64) et le coût complet par annonce.

### Crypto — arrêter un entraînement qui diverge

Une plateforme d'actifs virtuels agréée par la VARA spécialise un modèle pour classer les messages de son support : tentative d'hameçonnage, demande de retrait, réclamation, question générale. Personne ne connaît la constante L d'un grand modèle : la garantie η < 2/L ne se calcule pas, elle se cherche. L'équipe commence donc par un pas petit qu'elle augmente progressivement (*warmup*), et surveille la perte sur un jeu de validation toutes les 200 itérations. Si la perte remonte trois fois de suite, le job recharge le dernier point de sauvegarde et divise η par deux, ce qui revient à repasser sous la frontière que la démonstration a montrée. Sans ce garde-fou, une divergence en pleine nuit produit un adaptateur qui classe mal les tentatives d'hameçonnage, précisément les messages que la plateforme doit traiter en priorité. On suit le rappel sur la classe « hameçonnage » (étape 56) et le nombre de redémarrages par entraînement.

## Pièges et limites

- **Écrire α pour le taux d'apprentissage.** Dans un code LoRA, `alpha` désigne déjà l'échelle α_LoRA. Un même nom pour deux grandeurs donne des réglages faux et silencieux ; on écrit `eta` (ou `lr`) et `alpha_lora`.
- **Croire que LoRA divise la mémoire par 256.** Le facteur 256 porte sur les poids entraînés ; W₀ et les activations restent en mémoire, et la baisse réelle est d'environ trois quarts sur le compte de la démonstration.
- **Changer r sans regarder α_LoRA.** L'effet de l'adaptateur est proportionnel à α_LoRA / r ; doubler r à α_LoRA fixe divise l'échelle par deux, et l'ancien η ne convient plus.
- **Initialiser A et B à zéro.** Les deux gradients sont alors nuls et l'adaptateur n'apprend jamais (point 8).
- **Demander au fine-tuning de retenir des faits qui changent.** Les taux, les règlements et les prix évoluent ; ils restent dans le RAG et dans les outils, sinon l'agent les récite périmés.

### Exercice feuille blanche

1. Sans regarder le code, écrire `descente(theta, eta, pas)`, puis prédire θ₃ pour θ₀ = 0, cible 3 et η = 0,25. (Réponse : le facteur vaut 0,5, donc θ₃ = 3 − 3 × 0,125 = 2,625.)
2. Pour une couche d = 4096, k = 11 008 et r = 16, calculer le nombre de paramètres LoRA, le facteur de réduction et la baisse du nombre de valeurs stockées avec Adam. (Réponse : 241 664 paramètres, facteur 186,6, baisse de 74,46 %.)
3. Trouver le bug : `return addition(W0, echelle(matmul(B, A), alpha_lora))`. Quelle vérification du programme échoue, et pourquoi ?

## Pour aller plus loin

QLoRA quantifie W₀ sur 4 bits pour réduire aussi sa place en mémoire, et entraîne l'adaptateur en précision normale. La variante rsLoRA remplace l'échelle α_LoRA / r par α_LoRA / √r, pour que l'effet de l'adaptateur ne s'effondre pas quand r grandit. La méthode de Newton choisit, pour une parabole, le pas η = 1/L exactement, qui arrive en un pas ; Adam (étape 74) en approche l'idée poids par poids, sans calculer de dérivée seconde.

> Suite : [Quantification INT8 et INT4](<73b-Quantification-INT8-INT4.md>) — étape 73 bis.
