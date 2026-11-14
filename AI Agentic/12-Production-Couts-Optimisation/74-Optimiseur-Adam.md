# Étape 74 — Optimiseur Adam (Adaptive Moment Estimation)

> Étape 74 du parcours · Prérequis : [Distillation maître-élève](<73c-Distillation-Maitre-Eleve.md>) · Suite : [Alignement : SFT, RLHF, PPO, GRPO, DPO](<74b-Alignement-SFT-RLHF-PPO-GRPO-DPO.md>)

## Définition

Adam est la version de la descente de gradient (étape 73) qu'on utilise presque toujours pour entraîner et fine-tuner les Transformers. Il garde, pour **chaque poids**, deux moyennes mobiles : le premier moment mₜ, moyenne des gradients récents, qui lisse la direction (c'est l'idée du *momentum*) ; le second moment vₜ, moyenne des gradients au carré, qui mesure leur amplitude (c'est l'idée de RMSProp). Comme ces deux moyennes partent de zéro, elles sont biaisées vers zéro au début ; Adam les corrige en les divisant par 1 − β₁ᵗ et 1 − β₂ᵗ. Le pas vaut alors le taux d'apprentissage η multiplié par m̂ / √v̂ : la direction moyenne, divisée par l'amplitude typique, ce qui rend la longueur du pas presque indépendante de l'échelle du gradient. **AdamW** ajoute une décroissance des poids (*weight decay*) appliquée à part, hors des moyennes, ce qui n'est pas la même chose qu'une pénalité L2 ajoutée à la perte.

## Rôle dans un agent

Comme la descente de gradient, Adam ne tourne pas pendant la boucle percevoir → décider → agir → observer : il sert hors ligne, dans le job qui entraîne un adaptateur LoRA (étape 73), un routeur d'intentions, un classifieur de garde-fou ou un reranker. Ses hyperparamètres η, β₁, β₂, ε et λ font partie de la configuration de ce job, au même titre que les données, et ils se versionnent avec elles. L'ingénieur agentique doit savoir lire une courbe de perte produite par Adam, reconnaître un pas trop grand, un poids rare qui s'emballe ou une reprise d'entraînement mal faite. Il doit aussi compter sa mémoire : Adam stocke deux nombres de plus par poids entraîné, et c'est une grande partie de ce que LoRA économise (étape 73, point 7).

## Équation complète

Gradient au pas t (t = 1, 2, 3…) :

$$
g_t = \nabla_\theta \mathcal{L}(\theta_{t-1})
$$

Premier et second moments, partis de m₀ = v₀ = 0 :

$$
m_t = \beta_1 m_{t-1} + (1 - \beta_1)\, g_t
$$

$$
v_t = \beta_2 v_{t-1} + (1 - \beta_2)\, g_t^2
$$

Correction de biais :

$$
\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}
$$

Pas d'Adam :

$$
\theta_t = \theta_{t-1} - \eta \, \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
$$

Pas d'AdamW, décroissance découplée :

$$
\theta_t = \theta_{t-1} - \eta \, \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon} - \eta \, \lambda \, \theta_{t-1}
$$

Valeurs par défaut usuelles :

$$
\beta_1 = 0{,}9, \qquad \beta_2 = 0{,}999, \qquad \epsilon = 10^{-8}
$$

Résultat démontré plus bas, qui justifie la correction :

$$
\mathbb{E}[m_t] = (1 - \beta_1^t)\, \mathbb{E}[g]
$$

## Décryptage des symboles

$$
t
$$

**Sens :** numéro du pas, compté à partir de 1 ; il sert à la correction de biais · **Type / plage :** entier ≥ 1 · **Variable Python :** `self.t`

$$
\theta_t
$$

**Sens :** les poids après t pas · **Type / plage :** vecteur de réels · **Variable Python :** `theta`

$$
g_t
$$

**Sens :** le gradient de la perte au pas t, calculé par rétropropagation (étape 75) · **Type / plage :** même forme que θ · **Variable Python :** `grads`

$$
m_t, \; v_t
$$

**Sens :** moyenne mobile des gradients, et moyenne mobile des gradients au carré, poids par poids · **Type / plage :** réels ; vₜ ≥ 0 · **Variable Python :** `self.m`, `self.v`

$$
\beta_1, \; \beta_2
$$

**Sens :** taux d'oubli des deux moyennes ; plus β est proche de 1, plus la mémoire est longue · **Type / plage :** réels dans [0 ; 1[, 0,9 et 0,999 par défaut · **Variable Python :** `beta1`, `beta2`

$$
\hat{m}_t, \; \hat{v}_t
$$

**Sens :** les deux moments corrigés du biais de départ · **Type / plage :** réels ; v̂ₜ ≥ 0 · **Variable Python :** `self.m_hat`, `self.v_hat`

$$
\eta
$$

**Sens :** taux d'apprentissage ; chez Adam, c'est presque la longueur du pas de chaque poids · **Type / plage :** réel > 0, 10⁻³ par défaut, souvent 10⁻⁴ en fine-tuning · **Variable Python :** `eta`

$$
\epsilon
$$

**Sens :** petite constante qui évite la division par zéro quand v̂ₜ = 0 · **Type / plage :** réel ≥ 0, 10⁻⁸ par défaut · **Variable Python :** `eps`

$$
\lambda
$$

**Sens :** coefficient de décroissance des poids d'AdamW (ou coefficient L2 dans la variante couplée) · **Type / plage :** réel ≥ 0, souvent 0,01 · **Variable Python :** `lam`

L'ancienne version de ce fichier notait le taux d'apprentissage α. Il s'écrit η dans tout le parcours, parce que α désigne ailleurs un poids de mélange ou l'échelle LoRA (étape 73).

## Démonstration

### 1. Le premier moment est une somme pondérée des gradients passés

On montre par récurrence que

$$
m_t = (1 - \beta_1) \sum_{i=1}^{t} \beta_1^{\,t-i} \, g_i
$$

Pour t = 1 : m₁ = β₁ × 0 + (1 − β₁) g₁, ce qui est bien la formule. Si elle vaut au rang t − 1, alors

$$
m_t = \beta_1 (1 - \beta_1) \sum_{i=1}^{t-1} \beta_1^{\,t-1-i} g_i + (1 - \beta_1) g_t = (1 - \beta_1) \sum_{i=1}^{t} \beta_1^{\,t-i} g_i
$$

parce que multiplier par β₁ ajoute 1 à chaque exposant, et que le terme gₜ arrive avec l'exposant 0. Le gradient d'il y a j pas pèse donc (1 − β₁)β₁ʲ : un poids qui décroît comme dans la mémoire de l'étape 16. La même preuve vaut pour vₜ, avec β₂ et gᵢ².

### 2. Pourquoi il faut diviser par 1 − β₁ᵗ

Supposons que les gradients aient tous la même espérance E[g] (le problème ne change pas trop vite). L'espérance est linéaire, donc

$$
\mathbb{E}[m_t] = (1 - \beta_1) \sum_{j=0}^{t-1} \beta_1^{\,j} \; \mathbb{E}[g] = (1 - \beta_1) \cdot \frac{1 - \beta_1^t}{1 - \beta_1} \cdot \mathbb{E}[g] = (1 - \beta_1^t)\, \mathbb{E}[g]
$$

parce que la somme d'une série géométrique de raison β₁ et de t termes vaut (1 − β₁ᵗ) / (1 − β₁). La somme des poids vaut donc 1 − β₁ᵗ et non 1 : la part manquante, β₁ᵗ, est celle qu'on a donnée à m₀ = 0. Diviser par 1 − β₁ᵗ renormalise les poids, et m̂ₜ a pour espérance E[g] exactement. De même, E[vₜ] = (1 − β₂ᵗ) E[g²], et v̂ₜ estime E[g²] sans biais. Au pas 1, 1 − β₁ vaut 0,1 et 1 − β₂ vaut 0,001 : sans correction, m₁ serait dix fois trop petit et v₁ mille fois trop petit. Le code vérifie la formule sur 20 000 suites tirées au hasard d'espérance 1 : la moyenne de m₅ vaut 0,4103, pour 1 − 0,9⁵ = 0,4095.

### 3. Avec un gradient constant, la correction est exacte et le pas vaut η

Si gᵢ = g pour tout i, la formule du point 1 donne mₜ = (1 − β₁ᵗ) g et vₜ = (1 − β₂ᵗ) g², donc

$$
\hat{m}_t = g, \qquad \hat{v}_t = g^2, \qquad \theta_{t-1} - \theta_t = \eta \, \frac{g}{\lvert g \rvert + \epsilon} \approx \eta \cdot \operatorname{signe}(g)
$$

Le pas ne dépend plus de la taille du gradient : un gradient de 2, de 0,001 ou de −300 donne un pas de ±0,001 quand η = 0,001. C'est la différence avec la descente simple, où un gradient cent fois plus grand donne un pas cent fois plus long.

### 4. Sans correction, les premiers pas sont trop grands, pas trop petits

L'ancienne version disait : « sans correction, on avancerait avec 0,2 alors que le vrai gradient vaut 2, donc les premiers pas sont trop petits ». C'est vrai pour m seul, mais faux pour le pas, parce que v est encore plus biaisé que m et qu'il est au dénominateur. Avec un gradient constant, le pas non corrigé vaut, en unités de η,

$$
\frac{m_t}{\sqrt{v_t}} = \frac{1 - \beta_1^t}{\sqrt{1 - \beta_2^t}}
$$

Au pas 1, cela fait 0,1 / √0,001 = √10 ≈ 3,162 : un pas plus de trois fois trop long. Le rapport monte encore à 6,528 au pas 10, vaut 3,241 au pas 100 et 1,258 au pas 1 000 : il faut des milliers de pas pour que le biais disparaisse de lui-même. C'est la raison d'être de la correction : sans elle, l'entraînement commence par une série de pas trop longs, au moment où les poids sont les plus fragiles.

### 5. Le pas reste de l'ordre de η

Si β₁ = β₂ = β, notons wᵢ = (1 − β)βᵗ⁻ⁱ ≥ 0 et c = ∑ wᵢ = 1 − βᵗ. L'inégalité de Cauchy-Schwarz (étape 14) appliquée aux vecteurs (√wᵢ) et (√wᵢ gᵢ) donne

$$
m_t^2 = \Bigl(\sum_i w_i g_i\Bigr)^2 \le \Bigl(\sum_i w_i\Bigr)\Bigl(\sum_i w_i g_i^2\Bigr) = c \, v_t
$$

En divisant par c², on obtient m̂ₜ² ≤ v̂ₜ, donc |m̂ₜ| ≤ √v̂ₜ et chaque pas est au plus η : Adam se comporte comme une **région de confiance** de rayon η autour du poids actuel. Avec les valeurs par défaut, β₁ ≠ β₂ et cette borne ne tient plus exactement. Le cas le plus défavorable est celui d'un poids **rare** : resté 100 pas sans gradient, puis touché dix fois de suite par un gradient de 1, il a une moyenne courte déjà grande et une moyenne longue encore petite, et son pas vaut 2,11 η. L'article d'origine annonce (1 − β₁) / √(1 − β₂) ≈ 3,16 comme borne dans ce régime, et η quand (1 − β₁) ≤ √(1 − β₂). Ce n'est qu'un ordre de grandeur, tiré d'un raisonnement approché, pas une borne démontrée : avec β₂ = 0,99, ce rapport vaut 0,1 / 0,1 = 1, mais le même poids rare fait encore un pas de 1,72 η (1,44 η avec β₂ = 0,98, 1,03 η avec β₂ = 0,95). La seule garantie exacte est celle de la preuve ci-dessus : avec β₁ = β₂, aucun pas ne dépasse η (0,81 η pour ce poids rare avec β₁ = β₂ = 0,9).

### 6. AdamW n'est pas Adam avec une pénalité L2

Ajouter une pénalité L2 à la perte revient à remplacer gₜ par gₜ + λθ **avant** les moments. Mais Adam divise ensuite par √v̂, qui contient aussi λθ : la pénalité est normalisée comme le reste. Contre-exemple chiffré, un seul pas depuis l'état initial, avec θ = (1 ; 1), des gradients de données (1 ; 0), λ = 0,01 et η = 0,001. Pour le premier poids, le gradient total vaut 1,01, le pas vaut toujours η × 1,01 / 1,01 = η, et la part due à λ ne dépasse pas 10⁻¹³ : ce poids n'est pas régularisé du tout. Pour le second, le gradient total vaut 0,01, le pas vaut η × 0,01 / 0,01 = η = 10⁻³ : ce poids est tiré vers 0 à pleine vitesse, et le serait encore avec λ = 10⁻⁴, puisque le pas ne dépend plus de la taille du gradient (point 3). Le coefficient λ ne règle donc plus la force de la régularisation. AdamW retire à part ηλθ = 10⁻⁵ à chacun des deux poids, proportionnellement à leur taille, comme une vraie décroissance des poids. L'équivalence entre L2 et décroissance des poids ne tient que pour la descente de gradient simple (étape 76).

### 7. Exemple fait à la main (le code reprend ces nombres)

Un seul poids, gradient constant g = 2, β₁ = 0,9, β₂ = 0,999, η = 0,001, ε = 10⁻⁸.

| t | mₜ | vₜ | 1 − β₁ᵗ | 1 − β₂ᵗ | m̂ₜ | v̂ₜ | pas |
|---|---|---|---|---|---|---|---|
| 1 | 0,9 × 0 + 0,1 × 2 = 0,2 | 0,001 × 4 = 0,004 | 0,1 | 0,001 | 2 | 4 | 0,001 × 2 / 2 = 0,001 |
| 2 | 0,9 × 0,2 + 0,2 = 0,38 | 0,999 × 0,004 + 0,004 = 0,007996 | 0,19 | 0,001999 | 2 | 4 | 0,001 |
| 3 | 0,9 × 0,38 + 0,2 = 0,542 | 0,011988 | 0,271 | 0,002997 | 2 | 4 | 0,001 |

Le pas exact vaut 0,001 × 2 / (2 + 10⁻⁸) = 0,000999999995 : ε ne change rien tant que le gradient n'est pas minuscule.

## Effets et comportement

- **β₁ règle la mémoire de la direction, β₂ celle de l'amplitude.** Le poids d'un gradient vieux de j pas vaut (1 − β)βʲ, et l'âge moyen de la mémoire vaut β / (1 − β) : environ 9 pas pour β₁ = 0,9, environ 999 pas pour β₂ = 0,999. Un gradient aberrant gonfle v pour longtemps, et les pas suivants rapetissent : après un choc, on avance moins.
- **η devient une longueur de pas.** Avec un gradient régulier, chaque poids avance d'environ η par pas, quelle que soit la taille de son gradient (point 3).
- **Un seul η ne pénalise plus les directions plates.** Sur ℒ = x² + 1000y², la descente simple doit garder η < 2/L = 0,001 à cause de y, et x n'est encore qu'à 0,70 après 200 pas ; Adam, avec η = 0,01, ramène les deux coordonnées vers 0,016 en 200 pas, puis oscille autour du minimum avec une amplitude de l'ordre de η.
- **ε compte quand les gradients sont minuscules.** Si |g| = ε = 10⁻⁸, le pas tombe à η / 2.
- **La mémoire double.** Adam garde m et v pour chaque poids entraîné : deux nombres de plus par poids.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| η, β₁, β₂, ε, λ | `eta`, `beta1`, `beta2`, `eps`, `lam` |
| t, mₜ, vₜ | `self.t`, `self.m`, `self.v` |
| m̂ₜ, v̂ₜ | `self.m_hat`, `self.v_hat` |
| pas d'Adam, pas d'AdamW | `Adam(n, mode="adamw").step(theta, grads)` |
| gₜ + λθ dans le gradient | `Adam(n, lam=..., mode="l2")` |
| moments sans correction | `Adam(n, corriger=False)` |
| (1 − β) ∑ βᵗ⁻ⁱ gᵢ | `moment_deroule(grads, beta)` |
| (1 − β₁ᵗ) / √(1 − β₂ᵗ) | `rapport_sans_correction(t)` |

### Déroulé, ligne par ligne

**`Adam.__init__(n, eta, beta1, beta2, eps, lam, mode, corriger)`.**

- La garde refuse η ≤ 0, un β hors de [0 ; 1[, un ε ou un λ négatif. β₂ = 1 est refusé parce que la correction diviserait par 1 − 1ᵗ = 0.
- `self.m = [0.0] * n` et `self.v = [0.0] * n` : une moyenne de chaque sorte **par poids**, toutes à zéro. C'est ce départ à zéro qui crée le biais du point 2.
- `self.t = 0` : le compteur de pas. Il n'est pas décoratif, la correction en dépend.

**`Adam.step(theta, grads)`.** Un pas complet, dans l'ordre des équations.

- `self.t += 1` : le premier appel travaille avec t = 1.
- `if self.mode == "l2"` : la variante couplée ajoute `self.lam * th` au gradient avant les moments. C'est elle que le point 6 met en défaut.
- `self.m = [self.beta1 * m + (1 - self.beta1) * g ...]` : au pas 1 avec g = 2, m = 0,9 × 0 + 0,1 × 2 = 0,2.
- `self.v = [self.beta2 * v + (1 - self.beta2) * g * g ...]` : v = 0,001 × 4 = 0,004.
- `c1 = 1 - self.beta1 ** self.t` vaut 0,1 et `c2` vaut 0,001 au pas 1 ; avec `corriger=False`, les deux valent 1.
- `self.m_hat` vaut 0,2 / 0,1 = 2 et `self.v_hat` vaut 0,004 / 0,001 = 4.
- `pas_adam = self.eta * mh / (math.sqrt(vh) + self.eps)` : 0,001 × 2 / (2 + 10⁻⁸), soit 0,001.
- `decroissance = self.eta * self.lam * th` en mode `"adamw"`, calculée sur l'ancien poids θₜ₋₁, en dehors de m et de v ; 0 sinon.
- `nouveau.append(th - pas_adam - decroissance)` : la liste renvoyée est la nouvelle valeur des poids ; l'objet garde seulement l'état m, v, t.

**`moment_deroule(grads, beta)`.** Calcule la somme du point 1, (1 − β) ∑ βᵗ⁻ⁱ gᵢ, avec `enumerate(grads, start=1)` pour que i commence à 1 comme dans la formule. Le code la compare à `opt.m[0]` après cinq pas : la récurrence et la somme donnent le même nombre, à 10⁻¹² près.

**`rapport_sans_correction(t)`.** Renvoie (1 − 0,9ᵗ) / √(1 − 0,999ᵗ) : 3,162 pour t = 1, 6,528 pour t = 10, 3,241 pour t = 100, 1,258 pour t = 1 000 (point 4).

**`descente_simple` et `adam_sur_quadratique`.** Les deux optimiseurs sur ℒ = x² + 1000y², de gradient (2x, 2000y), depuis (1, 1). La descente simple utilise η = 0,0009, juste sous la limite 2/L = 0,001 imposée par y ; Adam utilise η = 0,01.

**`main()`, bloc par bloc.**

1. Trois pas avec g = 2 : le tableau de la démonstration, et trois `assert` par pas (m̂ = 2, v̂ = 4, pas = 0,001 à 10⁻¹¹ près). Puis un pas depuis un état neuf avec g = 2, 0,001 et −300 : le pas vaut toujours ±0,001, du signe du gradient.
2. Cinq gradients tirés avec `random.Random(74)` : récurrence et somme coïncident. La série géométrique (1 − 0,9) × ∑ 0,9ʲ vaut bien 1 − 0,9⁵. Puis 20 000 suites de cinq gradients d'espérance 1 : la moyenne de m₅ vaut 0,4103, à moins de 0,01 de 0,4095.
3. Le rapport sans correction, puis un vrai pas non corrigé : 0,001 × √10.
4. 500 suites de longueur et d'échelle tirées au hasard avec β₁ = β₂ = 0,9 et ε = 0 : aucun pas ne dépasse η (point 5). Puis le poids rare avec les valeurs par défaut : `rapport` vaut 2,11, entre 2 et la borne 3,16.
5. Les trois variantes sur θ = (1 ; 1) et des gradients (1 ; 0). `decr_l2` vaut environ (9,9 × 10⁻¹⁴ ; 10⁻³) et `decr_w` vaut (10⁻⁵ ; 10⁻⁵). Avec λ = 10⁻⁴ en mode `"l2"`, le poids sans gradient perd encore 10⁻³ : λ ne règle plus rien.
6. La comparaison sur x² + 1000y² : x = 0,6975 pour la descente simple, 0,0156 pour Adam. Enfin, `Adam(1, beta2=1.0)` doit lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Adam.__init__(n, eta, beta1, beta2, eps, lam, mode, corriger)`** — Le constructeur équipe chaque poids de deux carnets de bord vierges, comme un capitaine qui distribue à chaque marin un journal des vents et un journal des tempêtes : il reçoit le nombre de poids n, le pas η de 0,001, β₁ = 0,9, β₂ = 0,999, ε = 10⁻⁸, λ nul, le mode « adamw » et la correction de biais activée, tous par défaut, lève une `ValueError` si η n'est pas positif, si un β sort de [0 ; 1[, si ε ou λ est négatif, ou si le mode n'est ni « adamw » ni « l2 ». Il range ensuite les réglages, met à zéro les listes m et v, une case par poids, le compteur de pas t, et prépare des listes vides pour les moments corrigés ; il ne renvoie rien, et c'est ce départ à zéro qui crée le biais que la correction répare.

**`Adam.step(theta, grads)`** — Cette méthode fait faire un pas à tout l'équipage, dans l'ordre exact des équations : elle reçoit les poids et leurs gradients, lève une `ValueError` si leurs tailles diffèrent de celle de l'état, avance le compteur t, ajoute λθ au gradient en mode « l2 », met à jour la moyenne mobile m des gradients et la moyenne mobile v de leurs carrés, les divise par 1 − β₁ᵗ et 1 − β₂ᵗ quand la correction est active, puis retire à chaque poids η m̂ / (√v̂ + ε) et, en mode « adamw », la décroissance découplée ηλθ calculée sur l'ancien poids. Elle renvoie la liste des nouveaux poids, l'objet ne gardant que m, v et t ; au premier pas avec g = 2, m = 0,2, v = 0,004, m̂ = 2, v̂ = 4 et le pas vaut 0,001, et il vaut encore ±0,001 pour g = 0,001 ou g = −300.

**`rapport_sans_correction(t, beta1, beta2)`** — Celle-ci montre ce qui arriverait si l'on oubliait de corriger les carnets partis de zéro : elle reçoit le numéro du pas t et les deux coefficients, 0,9 et 0,999 par défaut, et renvoie (1 − β₁ᵗ) / √(1 − β₂ᵗ), la longueur du pas sans correction pour un gradient constant, en unités de η. Elle vaut √10 ≈ 3,162 au premier pas, monte à 6,528 au pas 10, redescend à 3,241 au pas 100 et à 1,258 au pas 1 000, ce qui prouve que le pas non corrigé est trop grand au début de l'entraînement.

**`descente_simple(x, y, eta, pas)`** — Cette fonction est la randonneuse sans boussole adaptative de l'étape 73, lâchée dans une vallée cent fois plus raide dans une direction que dans l'autre : elle reçoit le point de départ, le pas η et le nombre de pas, puis applique à chaque pas la descente de gradient sur ℒ = x² + 1000y², dont le gradient vaut (2x, 2000y), en mettant à jour les deux coordonnées en même temps. Elle renvoie le point atteint ; avec η = 0,0009, juste sous la limite 2/L = 0,001 imposée par y, et 200 pas depuis (1, 1), y s'effondre à 4,1 × 10⁻²⁰ mais x n'a parcouru qu'environ 30 % du chemin et vaut encore 0,6975.

**`adam_sur_quadratique(x, y, eta, pas)`** — Celle-ci lance Adam dans la même vallée, avec son pas réglé séparément pour chaque coordonnée, comme un randonneur qui ajuste sa foulée à la pente sous chaque pied : elle reçoit le point de départ, le pas η et le nombre de pas, crée un optimiseur `Adam` pour deux poids avec ce pas, puis appelle `step` à chaque pas avec le gradient (2x, 2000y) du point courant. Elle renvoie le point atteint ; avec η = 0,01 et 200 pas depuis (1, 1), x tombe à 0,0156 et y à environ 0,016, alors que la descente simple laissait x à 0,6975.

**`main()`** — C'est le chef mécanicien qui démonte l'optimiseur pièce par pièce, en six essais : il vérifie d'abord trois pas avec g = 2, où m̂ = 2, v̂ = 4 et le pas vaut 0,001, puis compare la récurrence du premier moment à sa somme déroulée et retrouve par 20 000 tirages l'espérance 1 − 0,9⁵ ≈ 0,4095. Il montre ensuite le pas trop grand sans correction, la borne du pas par η sur 500 suites tirées au hasard et le poids rare réveillé à 2,11 η, compare la décroissance couplée et découplée sur θ = (1 ; 1), oppose Adam à la descente simple sur x² + 1000y², et termine en vérifiant que β₂ = 1 est refusé.

```python
"""Étape 74 — Adam et AdamW en bibliothèque standard : moments, correction de biais, pas borné, décroissance découplée."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class Adam:
    """Adam (Kingma et Ba, 2015) et AdamW (Loshchilov et Hutter, 2019), un état (m, v) par poids.

    mode = "adamw" : la décroissance ηλθ est retirée à part, après le pas d'Adam (découplée).
    mode = "l2"    : λθ est ajouté au gradient AVANT les moments, comme une pénalité L2 classique.
    """

    def __init__(self, n: int, eta: float = 1e-3, beta1: float = 0.9, beta2: float = 0.999,
                 eps: float = 1e-8, lam: float = 0.0, mode: str = "adamw", corriger: bool = True):
        if eta <= 0 or not 0 <= beta1 < 1 or not 0 <= beta2 < 1 or eps < 0 or lam < 0:
            raise ValueError("il faut eta > 0, 0 <= beta < 1, eps >= 0 et lam >= 0")
        if mode not in ("adamw", "l2"):
            raise ValueError("mode = 'adamw' ou 'l2'")
        self.eta, self.beta1, self.beta2, self.eps = eta, beta1, beta2, eps
        self.lam, self.mode, self.corriger = lam, mode, corriger
        self.m = [0.0] * n
        self.v = [0.0] * n
        self.t = 0
        self.m_hat: list[float] = []
        self.v_hat: list[float] = []

    def step(self, theta: list[float], grads: list[float]) -> list[float]:
        if len(theta) != len(grads) or len(theta) != len(self.m):
            raise ValueError("theta, grads et l'état doivent avoir la même taille")
        self.t += 1
        if self.mode == "l2":
            grads = [g + self.lam * th for g, th in zip(grads, theta)]
        self.m = [self.beta1 * m + (1 - self.beta1) * g for m, g in zip(self.m, grads)]
        self.v = [self.beta2 * v + (1 - self.beta2) * g * g for v, g in zip(self.v, grads)]
        c1 = 1 - self.beta1 ** self.t if self.corriger else 1.0
        c2 = 1 - self.beta2 ** self.t if self.corriger else 1.0
        self.m_hat = [m / c1 for m in self.m]
        self.v_hat = [v / c2 for v in self.v]
        nouveau = []
        for th, mh, vh in zip(theta, self.m_hat, self.v_hat):
            pas_adam = self.eta * mh / (math.sqrt(vh) + self.eps)
            decroissance = self.eta * self.lam * th if self.mode == "adamw" else 0.0   # ηλθ_{t−1}, hors moments
            nouveau.append(th - pas_adam - decroissance)
        return nouveau


def moment_deroule(grads: list[float], beta: float) -> float:
    """m_t écrit comme une somme : (1 − β) Σ_{i=1..t} β^(t−i) g_i."""
    t = len(grads)
    return (1 - beta) * sum(beta ** (t - i) * g for i, g in enumerate(grads, start=1))


def rapport_sans_correction(t: int, beta1: float = 0.9, beta2: float = 0.999) -> float:
    """Gradient constant, sans correction : m_t / √v_t = (1 − β1^t) / √(1 − β2^t), en unités de η."""
    return (1 - beta1 ** t) / math.sqrt(1 - beta2 ** t)


def descente_simple(x: float, y: float, eta: float, pas: int) -> tuple[float, float]:
    """Descente de gradient (étape 73) sur ℒ = x² + 1000 y² : gradient (2x, 2000y)."""
    for _ in range(pas):
        x, y = x - eta * 2 * x, y - eta * 2000 * y
    return x, y


def adam_sur_quadratique(x: float, y: float, eta: float, pas: int) -> tuple[float, float]:
    opt = Adam(2, eta=eta)
    theta = [x, y]
    for _ in range(pas):
        theta = opt.step(theta, [2 * theta[0], 2000 * theta[1]])
    return theta[0], theta[1]


def main() -> None:
    print("1. Gradient constant g = 2, β1 = 0.9, β2 = 0.999, η = 0.001")
    opt = Adam(1)
    theta = [0.0]
    for _ in range(3):
        avant = theta[0]
        theta = opt.step(theta, [2.0])
        pas = avant - theta[0]
        print(f"  t = {opt.t}   m = {opt.m[0]:.6f}   v = {opt.v[0]:.6f}   m̂ = {opt.m_hat[0]:.6f}   v̂ = {opt.v_hat[0]:.6f}   pas = {pas:.9f}")
        assert abs(opt.m_hat[0] - 2) < 1e-12 and abs(opt.v_hat[0] - 4) < 1e-12 and abs(pas - 0.001) < 1e-11
    for g in (2.0, 0.001, -300.0):                     # la taille du gradient ne fixe plus la longueur du pas
        pas = 0.0 - Adam(1).step([0.0], [g])[0]
        assert abs(abs(pas) - 0.001) < 1e-8 and (pas > 0) == (g > 0)
    print("  g = 0.001 ou g = −300 : le pas vaut encore ±0.001 (au signe du gradient près)")

    print("2. Le moment déroulé : m_t = (1 − β1) Σ β1^(t−i) g_i, et E[m_t] = (1 − β1^t) E[g]")
    rng = random.Random(74)
    grads = [rng.gauss(1.0, 1.0) for _ in range(5)]
    opt = Adam(1)
    for g in grads:
        opt.step([0.0], [g])
    assert abs(opt.m[0] - moment_deroule(grads, 0.9)) < 1e-12
    assert abs((1 - 0.9) * sum(0.9 ** j for j in range(5)) - (1 - 0.9 ** 5)) < 1e-12   # série géométrique
    moyenne = sum(moment_deroule([rng.gauss(1.0, 1.0) for _ in range(5)], 0.9) for _ in range(20_000)) / 20_000
    print(f"  E[g] = 1, t = 5 : moyenne simulée de m_5 = {moyenne:.4f}   formule 1 − 0.9^5 = {1 - 0.9 ** 5:.4f}")
    assert abs(moyenne - (1 - 0.9 ** 5)) < 0.01

    print("3. Sans correction de biais, le pas est TROP GRAND au début (en unités de η)")
    print("  m_t / √v_t :" + "".join(f"   t = {t} → {rapport_sans_correction(t):.3f}" for t in (1, 10, 100, 1000)))
    assert abs(rapport_sans_correction(1) - math.sqrt(10)) < 1e-12
    brut = Adam(1, corriger=False)
    assert abs((0.0 - brut.step([0.0], [2.0])[0]) - 0.001 * math.sqrt(10)) < 1e-8

    print("4. Le pas reste de l'ordre de η")
    for _ in range(500):                               # β1 = β2 : |m̂| ≤ √v̂ (Cauchy-Schwarz), donc |pas| ≤ η
        opt = Adam(1, beta1=0.9, beta2=0.9, eps=0.0)
        th = [0.0]
        for _ in range(rng.randint(1, 30)):
            avant = th[0]
            th = opt.step(th, [rng.gauss(0.0, 1.0) * rng.choice((0.01, 1.0, 100.0))])
            assert abs(avant - th[0]) <= 0.001 * (1 + 1e-12)
    opt = Adam(1)
    th = [0.0]
    for t in range(1, 111):                            # 100 pas sans gradient, puis 10 gradients de 1
        avant = th[0]
        th = opt.step(th, [0.0 if t <= 100 else 1.0])
    rapport = (avant - th[0]) / 0.001
    print(f"  β1 = β2 : |pas| ≤ η sur 500 suites tirées au hasard ; valeurs par défaut, poids rare réveillé : pas = {rapport:.2f} η")
    assert 2.0 < rapport < (1 - 0.9) / math.sqrt(1 - 0.999)
    for b2, attendu in ((0.99, 1.72279), (0.98, 1.43799), (0.95, 1.02639), (0.9, 0.80705)):
        opt, th = Adam(1, beta2=b2), [0.0]                # même poids rare, autre β2
        for t in range(1, 111):
            avant = th[0]
            th = opt.step(th, [0.0 if t <= 100 else 1.0])
        assert abs((avant - th[0]) / 0.001 - attendu) < 1e-4   # β2 = 0,99 : rapport (1 − β1)/√(1 − β2) = 1, pas = 1,72 η

    print("5. AdamW contre Adam + L2 : θ = (1, 1), gradients des données (1, 0), λ = 0.01, un pas")
    sans = Adam(2).step([1.0, 1.0], [1.0, 0.0])
    l2 = Adam(2, lam=0.01, mode="l2").step([1.0, 1.0], [1.0, 0.0])
    adamw = Adam(2, lam=0.01, mode="adamw").step([1.0, 1.0], [1.0, 0.0])
    decr_l2 = [s - a for s, a in zip(sans, l2)]
    decr_w = [s - a for s, a in zip(sans, adamw)]
    print(f"  part due à λ, Adam + L2 : {decr_l2[0]:.2e} et {decr_l2[1]:.2e}   AdamW : {decr_w[0]:.2e} et {decr_w[1]:.2e}")
    assert decr_l2[0] < 1e-12 and abs(decr_l2[1] - 0.001) < 1e-8
    assert all(abs(d - 0.001 * 0.01 * 1.0) < 1e-15 for d in decr_w)
    faible = Adam(1, lam=1e-4, mode="l2").step([1.0], [0.0])[0]
    assert abs((1.0 - faible) - 0.001) < 1e-7            # λ divisé par 100 : même retrait, λ ne règle plus rien

    print("6. ℒ = x² + 1000y² depuis (1, 1), 200 pas")
    xg, yg = descente_simple(1.0, 1.0, 0.0009, 200)    # η < 2/L = 0.001 : imposé par la direction y
    xa, ya = adam_sur_quadratique(1.0, 1.0, 0.01, 200)
    print(f"  descente simple, η = 0.0009 : x = {xg:.4f}   y = {yg:.1e}")
    print(f"  Adam, η = 0.01             : x = {xa:.4f}   y = {ya:.1e}")
    assert xg > 0.6 and abs(yg) < 1e-6
    assert abs(xa) < 0.05 and abs(ya) < 0.05

    try:
        Adam(1, beta2=1.0)
    except ValueError:
        print("  β2 = 1 refusé : la correction diviserait par 1 − 1^t = 0")
    else:
        raise AssertionError("β2 = 1 aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Gradient constant g = 2, β1 = 0.9, β2 = 0.999, η = 0.001
  t = 1   m = 0.200000   v = 0.004000   m̂ = 2.000000   v̂ = 4.000000   pas = 0.001000000
  t = 2   m = 0.380000   v = 0.007996   m̂ = 2.000000   v̂ = 4.000000   pas = 0.001000000
  t = 3   m = 0.542000   v = 0.011988   m̂ = 2.000000   v̂ = 4.000000   pas = 0.001000000
  g = 0.001 ou g = −300 : le pas vaut encore ±0.001 (au signe du gradient près)
2. Le moment déroulé : m_t = (1 − β1) Σ β1^(t−i) g_i, et E[m_t] = (1 − β1^t) E[g]
  E[g] = 1, t = 5 : moyenne simulée de m_5 = 0.4103   formule 1 − 0.9^5 = 0.4095
3. Sans correction de biais, le pas est TROP GRAND au début (en unités de η)
  m_t / √v_t :   t = 1 → 3.162   t = 10 → 6.528   t = 100 → 3.241   t = 1000 → 1.258
4. Le pas reste de l'ordre de η
  β1 = β2 : |pas| ≤ η sur 500 suites tirées au hasard ; valeurs par défaut, poids rare réveillé : pas = 2.11 η
5. AdamW contre Adam + L2 : θ = (1, 1), gradients des données (1, 0), λ = 0.01, un pas
  part due à λ, Adam + L2 : 9.90e-14 et 1.00e-03   AdamW : 1.00e-05 et 1.00e-05
6. ℒ = x² + 1000y² depuis (1, 1), 200 pas
  descente simple, η = 0.0009 : x = 0.6975   y = 4.1e-20
  Adam, η = 0.01             : x = 0.0156   y = 1.6e-02
  β2 = 1 refusé : la correction diviserait par 1 − 1^t = 0
OK — toutes les vérifications sont passées.
```

La même classe en NumPy, pour des tableaux de poids, et l'appel équivalent dans PyTorch. Ces extraits ne sont pas exécutés par le harnais.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`AdamNumpy.__init__(params, eta, beta1, beta2, eps, lam)`** — Ce constructeur est le même que celui de la classe `Adam` du programme précédent, mais il range ses carnets dans des tableaux NumPy au lieu de listes, comme un intendant qui remplace ses fiches par un registre relié : il reçoit le tableau des poids, qu'il copie pour ne pas modifier l'original, puis η = 0,001, β₁ = 0,9, β₂ = 0,999, ε = 10⁻⁸ et λ = 0 par défaut, crée deux tableaux m et v de zéros de la même forme que les poids et met le compteur t à zéro. Il ne renvoie rien ; à la différence de la version en bibliothèque standard, il ne vérifie aucun réglage et ne connaît pas le mode « l2 », la décroissance étant toujours découplée.

**`AdamNumpy.step(grads)`** — Cette méthode fait le même pas que `Adam.step`, mais d'un seul geste sur tout le tableau, comme une moissonneuse qui fauche le champ entier là où l'on passait épi par épi : elle reçoit le tableau des gradients, avance t, met à jour m et v par les mêmes moyennes mobiles, les corrige par 1 − β₁ᵗ et 1 − β₂ᵗ, puis retire aux poids η m̂ / (√v̂ + ε) et la décroissance découplée ηλθ calculée sur les poids avant le pas. Elle garde les nouveaux poids dans l'objet et les renvoie, alors que la version en bibliothèque standard recevait les poids en argument et laissait l'appelant les conserver.

```python
# [extrait] — Adam / AdamW vectorisé avec NumPy (non exécuté : NumPy n'est pas dans la bibliothèque standard)
import numpy as np


class AdamNumpy:
    def __init__(self, params, eta=1e-3, beta1=0.9, beta2=0.999, eps=1e-8, lam=0.0):
        self.params = params.copy()
        self.eta, self.beta1, self.beta2, self.eps, self.lam = eta, beta1, beta2, eps, lam
        self.m = np.zeros_like(params)
        self.v = np.zeros_like(params)
        self.t = 0

    def step(self, grads):
        self.t += 1
        self.m = self.beta1 * self.m + (1 - self.beta1) * grads
        self.v = self.beta2 * self.v + (1 - self.beta2) * grads ** 2
        m_hat = self.m / (1 - self.beta1 ** self.t)
        v_hat = self.v / (1 - self.beta2 ** self.t)
        decroissance = self.eta * self.lam * self.params          # AdamW : hors de m et de v
        self.params = self.params - self.eta * m_hat / (np.sqrt(v_hat) + self.eps) - decroissance
        return self.params
```

```python
# [extrait] — PyTorch : AdamW découplé ; attention, Adam(weight_decay=...) est la variante L2 couplée du point 6
import torch

optimiseur = torch.optim.AdamW(modele.parameters(), lr=2e-4, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.01)
# à chaque lot : perte.backward() ; optimiseur.step() ; optimiseur.zero_grad()
# reprise : sauvegarder et recharger optimiseur.state_dict() (m, v et t), pas seulement les poids
```

## Squelette algorithmique

Le squelette décrit une boucle d'entraînement avec Adam, en mode AdamW ou en mode L2 couplé. En entrée : les poids de départ, une fonction qui renvoie le gradient des données, les hyperparamètres η, β₁, β₂, ε, λ et un nombre de pas. En sortie : les poids entraînés **et** l'état de l'optimiseur (m, v, t), qu'il faut sauvegarder avec eux pour pouvoir reprendre. L'idée : à chaque pas, mettre à jour deux moyennes mobiles par poids, les corriger de leur départ à zéro, avancer de η fois leur rapport, puis, pour AdamW seulement, retirer à part une fraction ηλ du poids.

```text
ALGORITHME Adam
ENTRÉES : poids θ (p nombres), fonction gradient, η > 0, β₁ et β₂ dans [0 ; 1[, ε ≥ 0, λ ≥ 0,
          mode « adamw » ou « l2 », nombre de pas T
SORTIE : poids θ et état (m, v, t)

SI η ≤ 0 OU β₁ ∉ [0 ; 1[ OU β₂ ∉ [0 ; 1[ OU ε < 0 OU λ < 0 ALORS
    RETOURNER ERREUR « hyperparamètres invalides »
FIN SI
m ← p zéros ;  v ← p zéros ;  t ← 0
POUR k DE 1 À T FAIRE
    g ← gradient(θ)
    t ← t + 1
    SI mode = « l2 » ALORS
        g ← g + λ · θ                          la pénalité entre dans les moments (variante couplée)
    FIN SI
    c₁ ← 1 − β₁ᵗ ;  c₂ ← 1 − β₂ᵗ                corrections de biais, communes à tous les poids
    POUR i DE 1 À p FAIRE
        m[i] ← β₁ · m[i] + (1 − β₁) · g[i]
        v[i] ← β₂ · v[i] + (1 − β₂) · g[i]²
        m̂ ← m[i] / c₁ ;  v̂ ← v[i] / c₂
        pas ← η · m̂ / (√v̂ + ε)                  au plus de l'ordre de η, quelle que soit la taille de g[i]
        SI mode = « adamw » ALORS
            θ[i] ← θ[i] − pas − η · λ · θ[i]    décroissance découplée, calculée sur l'ancien θ[i]
        SINON
            θ[i] ← θ[i] − pas
        FIN SI
    FIN POUR
FIN POUR
RETOURNER θ, (m, v, t)
```

**Complexité :** un pas coûte le calcul du gradient, G, plus O(p) pour la boucle sur les p poids, parce que chaque poids demande un nombre fixe d'opérations (deux moyennes, deux divisions, une racine, une soustraction) ; les deux puissances β₁ᵗ et β₂ᵗ se calculent une fois par pas, pas une fois par poids. Le total vaut O(T (G + p)) en temps. En mémoire, Adam garde m et v, soit 2p nombres en plus des p poids et des p gradients : c'est cet état, et non le calcul, qui pèse dans un entraînement complet (étape 73, point 7). La descente simple de l'étape 73 a le même coût en temps à une constante près, mais ne garde aucun état.

**Du squelette au code :** la garde des hyperparamètres et l'initialisation « m ← p zéros ; v ← p zéros ; t ← 0 » sont `Adam.__init__`, qui refuse aussi β₂ = 1. Le corps de la boucle « POUR k » est `Adam.step(theta, grads)` : « t ← t + 1 » est `self.t += 1`, la ligne du mode « l2 » est la compréhension `grads = [g + self.lam * th ...]`, les deux moyennes sont les listes `self.m` et `self.v`, « c₁ » et « c₂ » sont `c1` et `c2` (égaux à 1 quand `corriger=False`), « m̂ » et « v̂ » sont `self.m_hat` et `self.v_hat`, et la branche finale est la boucle sur `pas_adam` et `decroissance`. La boucle externe « POUR k DE 1 À T » est celle de `adam_sur_quadratique`, qui appelle `opt.step` deux cents fois avec le gradient (2x, 2000y). Le programme rend θ et garde l'état dans l'objet `opt` : c'est l'objet entier qu'il faudrait sauvegarder pour reprendre.

## Cas d'usage réels aux Émirats

Les taux d'apprentissage, les volumes et les seuils ci-dessous sont illustratifs : ils servent à faire le calcul, pas à décrire un déploiement réel.

### Banque — reprendre un entraînement sans casser la correction de biais

Une banque de détail de Dubaï entraîne avec AdamW un adaptateur LoRA qui classe les réclamations de ses clients, rédigées en arabe, en anglais ou dans un mélange des deux, avec η = 2 × 10⁻⁴ et λ = 0,01. L'entraînement dure plusieurs heures et doit pouvoir reprendre après une interruption du serveur. Un premier script de reprise rechargeait les poids mais recréait l'optimiseur : m = v = 0 et t = 0, au milieu d'un entraînement. D'après le point 3, chaque poids repart alors avec un pas d'environ η dans la direction de son gradient du moment, y compris les poids qu'Adam avait ralentis parce que leurs gradients étaient bruités : la perte de validation fait un saut visible juste après chaque reprise. Un second script, qui rechargeait m et v mais pas t, faisait l'erreur inverse : la correction redivisait par 1 − 0,9 et 1 − 0,999, et le pas tombait à √0,001 / 0,1 ≈ 0,32 fois sa valeur normale au premier pas, puis restait nettement trop court pendant des centaines de pas (l'inverse exact du rapport du point 4). La banque sauvegarde désormais m, v et t avec les poids, et vérifie qu'un entraînement interrompu puis repris produit la même courbe qu'un entraînement continu, à la graine près. Cette reproductibilité sert aussi à l'audit interne du modèle, qui doit pouvoir rejouer un entraînement à l'identique. On suit l'écart de perte entre une reprise et un entraînement continu, et la F1 macro sur les classes de réclamations (étape 56).

### Immobilier — un quartier rare qui s'emballe

Une agence active à Dubaï et à Abu Dhabi entraîne avec Adam un reranker qui ordonne les biens proposés par son agent, à partir des visites programmées. Chaque quartier a son propre poids, et certains quartiers ne reçoivent presque aucune demande pendant des semaines. Quand une petite vague de demandes arrive sur l'un d'eux, son poids se comporte comme le poids rare du point 5 : après 100 pas sans gradient et dix pas de gradient, il avance de 2,11 η par pas au lieu d'environ η, et le reranker propose soudain ce quartier à tous les acheteurs. L'équipe passe β₂ de 0,999 à 0,95 pour ce modèle : le calcul du point 5 donne alors un pas de 1,03 η au lieu de 2,11 η. Passer seulement à 0,99 ne suffirait pas : le rapport (1 − β₁) / √(1 − β₂) vaut alors 1, mais le pas du poids réveillé reste de 1,72 η. L'équipe ajoute aussi une décroissance AdamW qui ramène lentement vers 0 les poids peu nourris. Sans ces deux réglages, l'agent pousse des biens qui ne correspondent pas aux critères des clients, et le taux de visites baisse. On suit le taux de visites programmées par proposition et la part des propositions concentrées sur un seul quartier.

### Crypto — des entrées d'échelles très différentes

Une plateforme d'actifs virtuels agréée par la VARA met à jour chaque nuit un modèle de score qui aide son agent de surveillance à classer les alertes de liquidité. Ses entrées ont des échelles sans rapport : des volumes en millions d'AED, des écarts de prix en points de base, des nombres d'ordres. Avec la descente simple, le pas commun est réglé sur l'entrée la plus courbée, et les autres poids avancent à peine : c'est la situation de x² + 1000y², où x n'est qu'à 0,70 après 200 pas. Adam donne à chaque poids un pas de l'ordre de η, et le modèle converge en une seule nuit sur toutes ses entrées. Le même mécanisme a un revers : si un flux de données arrive corrompu, le gradient explose mais le pas reste de l'ordre de η, si bien que la perte ne s'envole pas et que l'erreur passe inaperçue plus longtemps. La plateforme valide donc chaque flux avant l'entraînement au lieu de compter sur la perte pour signaler le problème. On suit la précision des alertes classées critiques et le nombre de flux rejetés par la validation.

### Assurance — une décroissance qui touche tous les poids pareil

Un assureur auto et santé ré-entraîne chaque mois son modèle d'aide à la détection de fraude, qui a beaucoup de poids pour des entrées rares (un garage, un code d'acte) et quelques poids pour des entrées fréquentes (le montant, l'ancienneté du contrat). Une première version utilisait Adam avec une pénalité L2 dans la perte. Le point 6 montre l'effet : les poids des entrées fréquentes, qui ont de gros gradients, n'étaient presque pas régularisés, tandis que ceux des entrées rares, sans gradient la plupart du temps, étaient tirés vers 0 d'un pas η à chaque mise à jour, quel que soit λ. Le modèle oubliait ainsi d'un mois à l'autre les garages suspects qu'il venait d'apprendre. Avec AdamW et λ = 0,01, chaque poids perd ηλθ par pas, une fraction de lui-même, et λ redevient un vrai réglage. On suit le rappel sur les dossiers frauduleux confirmés et l'écart moyen des scores entre deux versions mensuelles.

### Secteur public — compter la mémoire d'un entraînement

Une entité de services publics en ligne, accessible par UAE Pass, entraîne un adaptateur en dialecte émirien de 8 388 608 paramètres (étape 73). Adam garde, pour chacun, m et v : 16 777 216 nombres de plus, deux fois la taille de l'adaptateur, auxquels s'ajoutent les gradients. Pour un adaptateur, c'est peu ; pour un entraînement complet du modèle, ces deux moyennes pèseraient deux fois le modèle entier, ce qui explique une bonne part de l'écart de mémoire calculé à l'étape 73. L'entité doit aussi pouvoir montrer, au titre de la PDPL, sur quelles données l'adaptateur a été entraîné : la configuration complète (données, graine, η, β₁, β₂, λ) est conservée avec chaque version, pour qu'un entraînement puisse être refait à l'identique. Sans ce compte, l'équipe découvre au lancement du job que la machine réservée n'a pas assez de mémoire. On suit le pic de mémoire par entraînement et la part des versions reproductibles à l'identique.

### BTP — prévoir un dépassement de coût avec des montants et des durées

Un groupe de construction qui mène de grands chantiers à Dubaï entraîne un petit modèle qui estime, à partir des factures de sous-traitance (TVA de 5 %), des retenues de garantie et des durées, le risque de dépassement d'un lot. Les montants se comptent en millions d'AED et les durées en mois : leurs courbures diffèrent d'un facteur de l'ordre de mille. Avec la descente simple, le pas maximal est fixé par les montants, et le poids de la durée n'apprend presque rien ; avec Adam, les deux poids progressent au même rythme, comme dans la sixième partie du programme. La meilleure correction reste de normaliser les entrées avant l'entraînement : Adam compense une mauvaise échelle, il ne la rend pas souhaitable. L'agent de suivi de chantier utilise ce score pour décider quels lots montrer en premier au contrôleur de gestion. On suit l'erreur absolue moyenne sur les chantiers clos et le taux de dépassements signalés à temps.

## Pièges et limites

- **Reprendre un entraînement sans m, v et t.** Remettre l'état à zéro au milieu d'un entraînement fausse la correction de biais et les premiers pas après la reprise. On sauvegarde l'état de l'optimiseur avec les poids.
- **Prendre Adam avec pénalité L2 pour AdamW.** Dans la variante couplée, la pénalité est normalisée par √v̂ : λ ne règle plus la force de la régularisation (point 6). Dans PyTorch, `Adam(weight_decay=...)` est cette variante couplée ; la décroissance découplée s'appelle `AdamW`.
- **Garder β₂ = 0,999 pour un entraînement très court.** La mémoire de l'amplitude dure environ mille pas ; sur trois cents pas, v̂ reste dominé par les premiers gradients.
- **Oublier ε quand les gradients sont minuscules.** Avec |g| = 10⁻⁸, le pas est divisé par deux ; certains entraînements en faible précision demandent un ε plus grand.
- **Croire qu'Adam protège des mauvaises données.** Le pas reste de l'ordre de η même quand le gradient explose : la perte ne signale pas toujours un flux corrompu.

### Exercice feuille blanche

1. Sans regarder le code, écrire `step` à partir des cinq équations, puis calculer à la main le premier pas pour g = −4. (Réponse : m = −0,4, v = 0,016, m̂ = −4, v̂ = 16 ; le poids **augmente** de 0,001.)
2. Prédire le premier pas sans correction de biais avec β₂ = 0,99, puis avec β₂ = 0,9999, à β₁ = 0,9. (Réponse : 0,1 / √0,01 = 1, soit η ; 0,1 / √0,0001 = 10, soit 10η.)
3. Trouver le bug : `self.m_hat = [m / (1 - self.beta1) for m in self.m]`. Que vaut le pas après une centaine de pas à gradient constant ? (Réponse : m̂ tend vers 10g et le pas vers 10η.)

## Pour aller plus loin

AMSGrad remplace v̂ₜ par son maximum passé, pour que le pas ne puisse jamais grandir après coup. Adafactor ne garde, pour une matrice, que les moyennes de ses lignes et de ses colonnes au lieu de v entier, ce qui réduit fortement la mémoire de l'optimiseur. En pratique, η suit un calendrier : une montée progressive au début (*warmup*), puis une décroissance, souvent en cosinus.

> Suite : [Alignement : SFT, RLHF, PPO, GRPO, DPO](<74b-Alignement-SFT-RLHF-PPO-GRPO-DPO.md>) — étape 74 bis.
