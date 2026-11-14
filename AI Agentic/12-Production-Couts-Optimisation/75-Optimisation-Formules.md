# Étape 75 — Optimisation — Formules Manquantes

> Étape 75 du parcours · Prérequis : [Alignement : SFT, RLHF, PPO, GRPO, DPO](<74b-Alignement-SFT-RLHF-PPO-GRPO-DPO.md>) · Suite : [Mini-lots et généralisation](<75b-Mini-Lots-et-Generalisation.md>)

Ce chapitre réunit trois formules de l'optimisation : Adam, la rétropropagation, et les régularisations L1 et L2. Adam est démontré à l'étape 74, L1 et L2 le sont à l'étape 76 ; ils ne sont ici que rappelés, avec leur résultat chiffré. Le cœur de ce fichier est la **rétropropagation** : c'est elle qui calcule le gradient que la descente de gradient (étape 73) et Adam (étape 74) consomment. L'ancienne version contenait trois blocs NumPy séparés ; ils sont remplacés par un seul programme en bibliothèque standard, vérifié contre des différences finies. Ses deux « démonstrations quantifiées » sont retirées : les durées « 1000, 500 et 150 epochs » n'avaient ni source ni protocole, et la ligne « un poids de 2.0 devient ≈ 1.9 (L2) ou 1.9 (L1) » ne précisait ni η ni la convention de la pénalité ; elle est refaite, chiffres vérifiés, dans la section des rappels.

## Définition

La **rétropropagation** (*backpropagation*) calcule, en un seul passage de la sortie vers l'entrée, la dérivée de la perte par rapport à **chaque** poids d'un réseau. Elle applique la règle de dérivation des fonctions composées (la règle de la chaîne) couche par couche, en réutilisant les valeurs intermédiaires calculées pendant la propagation avant. Pour chaque couche, elle forme un **signal d'erreur** δ, la dérivée de la perte par rapport à l'entrée de la fonction d'activation ; le gradient des poids de la couche s'en déduit par un simple produit, et le δ de la couche précédente s'en déduit en remontant les poids. Son coût est du même ordre que celui d'une propagation avant, alors qu'une estimation par différences finies demande deux propagations par poids : c'est ce qui rend possible l'entraînement de réseaux de millions ou de milliards de poids.

## Rôle dans un agent

L'agent ne rétropropage rien pendant sa boucle percevoir → décider → agir → observer : la rétropropagation tourne hors ligne, dans le job qui entraîne un adaptateur LoRA (étape 73), un routeur d'intentions, un classifieur de garde-fou ou un reranker. Dans ces jobs, une bibliothèque comme PyTorch la calcule automatiquement. L'ingénieur agentique doit pourtant savoir l'écrire et la vérifier, pour trois raisons : une perte personnalisée (pondération des classes, terme métier) se dérive à la main ou se contrôle ; un modèle qui n'apprend pas vient souvent d'un gradient qui s'éteint (saturation de la sigmoïde) ou qui explose ; et un test de gradient par différences finies, sur un petit lot, attrape une erreur de dérivation avant qu'elle ne coûte une nuit de GPU. C'est exactement l'erreur que portait l'ancienne version de ce fichier : la sigmoïde de sortie n'avait pas sa dérivée.

## Équation complète

Propagation avant d'un réseau à une couche cachée et une sortie :

$$
z^{(1)} = W^{(1)} x + b^{(1)}, \qquad a^{(1)} = \sigma\bigl(z^{(1)}\bigr)
$$

$$
z^{(2)} = W^{(2)} a^{(1)} + b^{(2)}, \qquad \hat{y} = \sigma\bigl(z^{(2)}\bigr)
$$

Sigmoïde et sa dérivée :

$$
\sigma(z) = \frac{1}{1 + e^{-z}}, \qquad \sigma'(z) = \sigma(z)\,\bigl(1 - \sigma(z)\bigr)
$$

Deux pertes pour un exemple, quadratique et entropie croisée :

$$
\mathcal{L}_{\text{quad}} = \tfrac{1}{2} (\hat{y} - y)^2, \qquad \mathcal{L}_{\text{EC}} = -\bigl[\, y \ln \hat{y} + (1 - y) \ln(1 - \hat{y}) \,\bigr]
$$

Signal d'erreur de la sortie :

$$
\delta^{(2)} = \frac{\partial \mathcal{L}}{\partial z^{(2)}} = (\hat{y} - y)\, \sigma'\bigl(z^{(2)}\bigr) \;\text{(quadratique)}, \qquad \delta^{(2)} = \hat{y} - y \;\text{(entropie croisée)}
$$

Gradients de la couche de sortie :

$$
\frac{\partial \mathcal{L}}{\partial W^{(2)}} = \delta^{(2)} \, \bigl(a^{(1)}\bigr)^{\top}, \qquad \frac{\partial \mathcal{L}}{\partial b^{(2)}} = \delta^{(2)}
$$

Retour vers la couche cachée :

$$
\delta^{(1)} = \Bigl( \bigl(W^{(2)}\bigr)^{\top} \delta^{(2)} \Bigr) \odot \sigma'\bigl(z^{(1)}\bigr)
$$

$$
\frac{\partial \mathcal{L}}{\partial W^{(1)}} = \delta^{(1)} \, x^{\top}, \qquad \frac{\partial \mathcal{L}}{\partial b^{(1)}} = \delta^{(1)}
$$

Sur un lot de m exemples, chaque gradient est la moyenne des gradients des exemples. Avec un réseau plus profond, la même récurrence se répète : δ⁽ˡ⁾ = ((W⁽ˡ⁺¹⁾)ᵀ δ⁽ˡ⁺¹⁾) ⊙ σ′(z⁽ˡ⁾). L'ancienne version écrivait δ⁽ˡ⁺¹⁾ · (W⁽ˡ⁺¹⁾)ᵀ, la même formule avec des vecteurs en ligne (un exemple par ligne, comme `delta @ W.T` en NumPy).

## Décryptage des symboles

$$
x, \; y
$$

**Sens :** le vecteur d'entrée d'un exemple, et la réponse attendue · **Type / plage :** x vecteur de réels ; y dans {0 ; 1} pour une classification · **Variable Python :** `x`, `y`

$$
W^{(1)}, \; b^{(1)}
$$

**Sens :** poids et biais de la couche cachée ; W⁽¹⁾ a une ligne par neurone caché et une colonne par entrée · **Type / plage :** matrice et vecteur de réels · **Variable Python :** `p["W1"]`, `p["b1"]`

$$
W^{(2)}, \; b^{(2)}
$$

**Sens :** poids et biais de la sortie ; avec une seule sortie, W⁽²⁾ est une ligne d'autant de nombres que de neurones cachés · **Type / plage :** liste de réels et réel · **Variable Python :** `p["W2"]`, `p["b2"]`

$$
z^{(1)}, \; a^{(1)}
$$

**Sens :** pré-activation et activation de la couche cachée · **Type / plage :** vecteurs ; a⁽¹⁾ dans ]0 ; 1[ · **Variable Python :** `c["z1"]`, `c["a1"]`

$$
z^{(2)}, \; \hat{y}
$$

**Sens :** pré-activation de la sortie, et prédiction ŷ = σ(z⁽²⁾), lue comme une probabilité · **Type / plage :** réel ; ŷ dans ]0 ; 1[ · **Variable Python :** `c["z2"]`, `c["y_hat"]`

$$
\sigma, \; \sigma'
$$

**Sens :** la sigmoïde, qui écrase un réel dans ]0 ; 1[, et sa dérivée · **Type / plage :** σ′ dans ]0 ; 1/4] · **Variable Python :** `sigmoide(z)`, `sigmoide_derivee(z)`

$$
\mathcal{L}
$$

**Sens :** la perte d'un exemple, ou sa moyenne sur un lot · **Type / plage :** réel ≥ 0 · **Variable Python :** `perte(p, donnees, cout)`, avec `cout = "mse"` ou `"bce"`

$$
\delta^{(2)}, \; \delta^{(1)}
$$

**Sens :** signaux d'erreur, dérivées de la perte par rapport à z⁽²⁾ et à z⁽¹⁾ · **Type / plage :** réel, puis vecteur · **Variable Python :** `delta2`, `delta1`

$$
\odot
$$

**Sens :** produit case par case de deux vecteurs de même taille (produit de Hadamard) · **Type / plage :** opération · **Variable Python :** la compréhension `[... * sigmoide_derivee(c["z1"][i]) for i in range(h)]`

$$
\eta
$$

**Sens :** taux d'apprentissage de la descente qui utilise ces gradients (étape 73) · **Type / plage :** réel > 0 · **Variable Python :** `eta`

## Démonstration

### 1. La dérivée de la sigmoïde

On écrit σ(z) = (1 + e⁻ᶻ)⁻¹ et on dérive une puissance −1 d'une fonction, puis l'exponentielle :

$$
\sigma'(z) = -\bigl(1 + e^{-z}\bigr)^{-2} \cdot \bigl(-e^{-z}\bigr) = \frac{e^{-z}}{\bigl(1 + e^{-z}\bigr)^2} = \frac{1}{1 + e^{-z}} \cdot \frac{e^{-z}}{1 + e^{-z}}
$$

Le second facteur vaut 1 − σ(z), parce que

$$
\frac{e^{-z}}{1 + e^{-z}} = \frac{(1 + e^{-z}) - 1}{1 + e^{-z}} = 1 - \frac{1}{1 + e^{-z}}
$$

d'où σ′ = σ(1 − σ). Comme s(1 − s) = 1/4 − (s − 1/2)², cette dérivée vaut au plus 1/4, atteint en z = 0 où σ = 1/2. Elle s'effondre quand la sigmoïde sature : σ′(2) = 0,10499 et σ′(5) = 0,00665, près de 38 fois moins qu'en 0. Une conséquence pour les réseaux profonds : traverser dix couches sigmoïdes multiplie le signal d'erreur par au plus 0,25¹⁰ ≈ 9,5 × 10⁻⁷, sans compter les poids. C'est le gradient qui s'évanouit, et la raison pour laquelle les couches cachées modernes utilisent plutôt ReLU ou GELU.

### 2. Le signal d'erreur de la sortie, et l'erreur de l'ancienne version

La perte quadratique dépend de z⁽²⁾ à travers ŷ = σ(z⁽²⁾). La règle de la chaîne donne

$$
\delta^{(2)} = \frac{\partial \mathcal{L}}{\partial \hat{y}} \cdot \frac{\partial \hat{y}}{\partial z^{(2)}} = (\hat{y} - y) \cdot \sigma'\bigl(z^{(2)}\bigr)
$$

parce que la dérivée de ½(ŷ − y)² par rapport à ŷ vaut ŷ − y, et que celle de ŷ par rapport à z⁽²⁾ vaut σ′(z⁽²⁾) (point 1). Une version antérieure du code oubliait ce second facteur à la sortie : elle traitait la sortie comme si elle était linéaire, alors que les couches cachées avaient bien leur σ′. Sur l'exemple du point 6, elle donne ∂ℒ/∂b⁽²⁾ = ŷ − y = −0,51556 au lieu de −0,12876, soit 1 / σ′(z⁽²⁾) ≈ 4,0 fois trop ; le test de gradient du programme la rejette avec un écart relatif de 0,75, alors que la version juste passe à 10⁻¹⁰.

### 3. Les gradients des poids de sortie

Comme

$$
z^{(2)} = \sum_i W^{(2)}_i \, a^{(1)}_i + b^{(2)}
$$

la dérivée de z⁽²⁾ par rapport à W⁽²⁾ᵢ vaut a⁽¹⁾ᵢ, et par rapport à b⁽²⁾ elle vaut 1. La règle de la chaîne donne donc ∂ℒ/∂W⁽²⁾ᵢ = δ⁽²⁾ a⁽¹⁾ᵢ et ∂ℒ/∂b⁽²⁾ = δ⁽²⁾ : un poids est corrigé en proportion de l'erreur qui arrive et de l'activation qui l'a traversé. Un neurone caché éteint (a⁽¹⁾ᵢ ≈ 0) ne fait presque pas bouger son poids de sortie.

### 4. Le retour vers la couche cachée

L'activation a⁽¹⁾ᵢ influence la perte à travers chaque sortie qu'elle alimente. La règle de la chaîne à plusieurs variables additionne les chemins :

$$
\frac{\partial \mathcal{L}}{\partial a^{(1)}_i} = \sum_j \frac{\partial \mathcal{L}}{\partial z^{(2)}_j} \cdot \frac{\partial z^{(2)}_j}{\partial a^{(1)}_i} = \sum_j \delta^{(2)}_j \, W^{(2)}_{ji} = \Bigl(\bigl(W^{(2)}\bigr)^\top \delta^{(2)}\Bigr)_i
$$

Puis on traverse la sigmoïde de la couche cachée, ce qui multiplie par σ′(z⁽¹⁾ᵢ) : on obtient δ⁽¹⁾ᵢ. Multiplier par (W⁽²⁾)ᵀ répartit la faute sur les neurones d'en dessous au prorata des poids qui les relient à la sortie ; multiplier par σ′ dit si ce neurone pouvait encore bouger. Le gradient de W⁽¹⁾ s'obtient comme au point 3 : ∂ℒ/∂W⁽¹⁾ᵢⱼ = δ⁽¹⁾ᵢ xⱼ. Point d'attention : δ⁽¹⁾ doit être calculé avec l'**ancienne** valeur de W⁽²⁾, avant de la mettre à jour.

### 5. Avec l'entropie croisée, le σ′ de la sortie disparaît

La dérivée de l'entropie croisée par rapport à ŷ vaut

$$
\frac{\partial \mathcal{L}_{\text{EC}}}{\partial \hat{y}} = -\frac{y}{\hat{y}} + \frac{1 - y}{1 - \hat{y}} = \frac{\hat{y} - y}{\hat{y}\,(1 - \hat{y})}
$$

en réduisant au même dénominateur. En la multipliant par σ′(z⁽²⁾) = ŷ(1 − ŷ), le dénominateur se simplifie :

$$
\delta^{(2)} = \frac{\hat{y} - y}{\hat{y}(1 - \hat{y})} \cdot \hat{y}(1 - \hat{y}) = \hat{y} - y
$$

Le signal d'erreur de la sortie ne s'éteint donc plus quand la sigmoïde sature sur une mauvaise réponse : si ŷ = 0,99 alors que y = 0, δ⁽²⁾ vaut 0,99 avec l'entropie croisée, mais 0,99 × 0,0099 ≈ 0,0098 avec la perte quadratique. C'est la même simplification que le gradient p − y de la softmax avec l'entropie croisée (étapes 2 et 3), et la raison pour laquelle un classifieur associe la sigmoïde à l'entropie croisée.

### 6. Vérifier un gradient par différences finies

Le développement de Taylor de la perte autour d'un poids w donne

$$
\mathcal{L}(w \pm h) = \mathcal{L}(w) \pm h\, \mathcal{L}'(w) + \frac{h^2}{2} \mathcal{L}''(w) \pm \frac{h^3}{6} \mathcal{L}'''(w) + \dots
$$

En soustrayant les deux lignes, les termes pairs s'annulent :

$$
\frac{\mathcal{L}(w + h) - \mathcal{L}(w - h)}{2h} = \mathcal{L}'(w) + \frac{h^2}{6} \mathcal{L}'''(w) + \dots
$$

La différence centrée a donc une erreur en h², contre h pour la différence avant (ℒ(w + h) − ℒ(w)) / h. Avec h = 10⁻⁵, l'erreur de troncature est de l'ordre de 10⁻¹¹ ; un h beaucoup plus petit ferait dominer les erreurs d'arrondi des flottants. On compare un écart **relatif**, |a − b| / max(|a|, |b|), pour que les petits gradients comptent autant que les grands. Ce test coûte deux propagations par poids : 2 × 17 = 34 propagations pour le réseau 2 → 4 → 1 du programme, qui a 17 poids, contre une seule rétropropagation. Il sert à vérifier le code sur un petit réseau, jamais à entraîner un grand modèle.

### 7. Exemple fait à la main (le code reprend ces nombres)

Réseau 2 → 2 → 1, x = (1 ; 2), y = 1, biais nuls, perte quadratique, avec

$$
W^{(1)} = \begin{pmatrix} 0{,}1 & 0{,}2 \\ -0{,}3 & 0{,}4 \end{pmatrix}, \qquad W^{(2)} = \begin{pmatrix} 0{,}5 & -0{,}6 \end{pmatrix}
$$

| Étape | Calcul | Valeur |
|---|---|---|
| z⁽¹⁾ | (0,1 + 0,4 ; −0,3 + 0,8) | (0,5 ; 0,5) |
| a⁽¹⁾ | σ(0,5) | (0,62246 ; 0,62246) |
| z⁽²⁾ | (0,5 − 0,6) × 0,62246 | −0,062246 |
| ŷ | σ(−0,062246) | 0,48444 |
| ℒ | ½ (0,48444 − 1)² | 0,13290 |
| σ′(z⁽²⁾) | 0,48444 × 0,51556 | 0,24976 |
| δ⁽²⁾ = ∂ℒ/∂b⁽²⁾ | (0,48444 − 1) × 0,24976 | −0,12876 |
| ∂ℒ/∂W⁽²⁾ | δ⁽²⁾ × a⁽¹⁾ | (−0,08015 ; −0,08015) |
| (W⁽²⁾)ᵀδ⁽²⁾ | (0,5 ; −0,6) × (−0,12876) | (−0,06438 ; 0,07726) |
| σ′(z⁽¹⁾) | 0,62246 × 0,37754 | (0,23500 ; 0,23500) |
| δ⁽¹⁾ | produit case par case | (−0,01513 ; 0,01816) |
| ∂ℒ/∂W⁽¹⁾ | δ⁽¹⁾ xᵀ, lignes | (−0,01513 ; −0,03026) et (0,01816 ; 0,03631) |

Les deux poids de sortie ont le même gradient parce que les deux neurones cachés ont la même activation ; les poids de la couche cachée, eux, sont poussés en sens contraires, parce que leurs poids de sortie sont de signes opposés.

## Rappels : Adam et régularisation L1 et L2

Adam (démontré à l'étape 74) remplace le gradient brut par le rapport de ses deux moyennes mobiles corrigées :

$$
\theta_t = \theta_{t-1} - \eta \, \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}, \qquad \hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}
$$

Avec un gradient g = 2 au premier pas, m̂ = 2, v̂ = 4 et le pas vaut 0,001 pour η = 0,001. Les pénalités L1 et L2 (démontrées à l'étape 76) s'ajoutent à la perte ; l'ancien bloc utilisait la convention

$$
\mathcal{L}_{L1} = \mathcal{L} + \lambda \sum_i \lvert w_i \rvert, \qquad \mathcal{L}_{L2} = \mathcal{L} + \lambda \sum_i w_i^2, \qquad \mathcal{L}_{EN} = \mathcal{L} + \lambda_1 \sum_i \lvert w_i \rvert + \lambda_2 \sum_i w_i^2
$$

Pour les poids (0,1 ; 0,5 ; 2,0 ; −1,5 ; 0,01) et λ = 0,01, la pénalité L1 vaut 0,01 × 4,11 = 0,0411 et la pénalité L2 vaut 0,01 × 6,5101 = 0,0651. L'exemple refait de l'ancienne ligne, avec η = 0,5, λ = 0,1 et un gradient des données nul : sous la pénalité λw²/2 (convention de l'étape 76), un pas multiplie le poids par 1 − ηλ = 0,95, donc 2,0 devient 1,9 ; sous la pénalité λ|w| avec un pas proximal (seuillage doux, étape 76), on retranche ηλ = 0,05, donc 2,0 devient 1,95. La différence se voit sur un petit poids : 0,04 devient 0,038 sous L2, mais exactement 0 sous L1.

## Effets et comportement

- **Sans le σ′ de la sortie, le gradient est faux d'un facteur 1/σ′(z⁽²⁾)**, 4 sur l'exemple, et ce facteur change d'un exemple à l'autre : ce n'est pas un simple changement de η.
- **La saturation éteint l'apprentissage.** Avec la perte quadratique, une sortie très sûre d'elle et fausse ne reçoit presque aucun gradient ; l'entropie croisée garde δ⁽²⁾ = ŷ − y.
- **La profondeur multiplie les σ′.** Chaque couche sigmoïde multiplie le signal par au plus 1/4 ; les couches cachées utilisent donc ReLU ou GELU, et la sigmoïde reste en sortie.
- **XOR passe par un plateau.** La perte d'entropie croisée reste près de ln 2 ≈ 0,6931, celle d'un réseau qui répond 0,5 partout (0,6926 à l'époque 100), puis tombe à 0,0133 à l'époque 1 000 quand les neurones cachés se spécialisent.
- **Le gradient d'un lot est une moyenne.** Diviser par m garde la même échelle de pas quand on change la taille du lot.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| σ, σ′ | `sigmoide(z)`, `sigmoide_derivee(z)` |
| W⁽¹⁾, b⁽¹⁾, W⁽²⁾, b⁽²⁾ | `p["W1"]`, `p["b1"]`, `p["W2"]`, `p["b2"]` |
| z⁽¹⁾, a⁽¹⁾, z⁽²⁾, ŷ | `propagation(p, x)` renvoie `z1`, `a1`, `z2`, `y_hat` |
| ℒ quadratique, ℒ entropie croisée | `perte(p, donnees, "mse")`, `perte(p, donnees, "bce")` |
| δ⁽²⁾, δ⁽¹⁾ et les quatre gradients | `retropropagation(p, donnees, cout)` |
| (ℒ(w + h) − ℒ(w − h)) / 2h | `gradient_numerique(p, donnees, cout)` |
| θ ← θ − η ∇ℒ | `descente(p, donnees, cout, eta, epoques)` |
| premier pas d'Adam | `premier_pas_adam(g)` |
| λ∑\|w\|, λ∑w² | `penalites(poids, lam)` |
| pas L2, pas L1 proximal | `pas_l2(w, eta, lam)`, `pas_l1(w, eta, lam)` |

### Déroulé, ligne par ligne

**`sigmoide(z)`.** Pour z ≥ 0, on calcule `1.0 / (1.0 + math.exp(-z))` ; pour z < 0, on calcule `e / (1.0 + e)` avec `e = math.exp(z)`. Les deux formules sont égales, mais la seconde évite `math.exp(1000)`, qui lève `OverflowError` en Python : une sigmoïde écrite naïvement ferait planter le programme sur une pré-activation de −1 000.

**`sigmoide_derivee(z)`** renvoie `s * (1.0 - s)` avec `s = sigmoide(z)` : la formule démontrée au point 1. Pour z = 0, `s = 0.5` et le résultat vaut 0,25.

**`nouveau_reseau(n, h, graine)`.** Tire W⁽¹⁾ (h lignes, n colonnes) et W⁽²⁾ (h nombres) uniformément dans [−1 ; 1] avec `random.Random(graine)`, et met les biais à 0. Des poids aléatoires sont indispensables : si tous les neurones cachés partaient identiques, ils recevraient le même gradient et resteraient identiques.

**`propagation(p, x)`.**

- La garde vérifie que `x` a autant de cases que W⁽¹⁾ a de colonnes.
- `z1` : pour chaque ligne de W⁽¹⁾, le produit scalaire avec `x` plus le biais. Sur l'exemple, 0,1 × 1 + 0,2 × 2 = 0,5 et −0,3 × 1 + 0,4 × 2 = 0,5.
- `a1 = [sigmoide(z) for z in z1]` donne 0,62246 deux fois.
- `z2` vaut 0,5 × 0,62246 − 0,6 × 0,62246 = −0,062246, et `y_hat` vaut σ(−0,062246) = 0,48444.
- Le dictionnaire renvoyé garde `x`, `z1`, `a1` et `z2` : la rétropropagation a besoin de l'entrée de chaque couche et de l'endroit où chaque sigmoïde a été calculée.

**`perte(p, donnees, cout)`.** Moyenne, sur les exemples, de `0.5 * (y_hat - y) ** 2` ou de l'entropie croisée. Sur l'exemple, ½ × 0,51556² = 0,13290. Un `cout` inconnu lève `ValueError`.

**`retropropagation(p, donnees, cout, fautive=False)`.**

- `g` est initialisé à zéro, de la même forme que `p`.
- Pour chaque exemple : `c = propagation(p, x)`, puis `delta2`. En perte quadratique, `(c["y_hat"] - y) * sigmoide_derivee(c["z2"])` vaut (0,48444 − 1) × 0,24976 = −0,12876 ; avec `fautive=True`, le facteur σ′ est remplacé par 1 et l'on obtient −0,51556, l'erreur du point 2. En entropie croisée, `delta2 = c["y_hat"] - y` (point 5).
- `delta1` : pour chaque neurone caché i, `p["W2"][i] * delta2 * sigmoide_derivee(c["z1"][i])`, c'est-à-dire ((W⁽²⁾)ᵀδ⁽²⁾) ⊙ σ′(z⁽¹⁾). Il est calculé avant toute mise à jour des poids : la fonction ne modifie pas `p`.
- Les accumulations : `g["W2"][i] += delta2 * c["a1"][i]`, `g["W1"][i][j] += delta1[i] * x[j]`, et les biais reçoivent δ directement.
- À la fin, tout est divisé par `m = len(donnees)` : on renvoie le gradient de la perte **moyenne**.

**`emplacements`, `aplatir` et `gradient_numerique`.** `emplacements` énumère chaque paramètre comme un couple (conteneur, indice), y compris `(p, "b2")` pour le biais de sortie, afin de pouvoir le modifier sur place. `aplatir` range les quatre gradients dans le même ordre. `gradient_numerique` ajoute puis retranche `h = 1e-5` à chaque paramètre, recalcule la perte, forme `(plus - moins) / (2 * h)` et remet la valeur d'origine.

**`ecart_relatif(a, b)`** renvoie le plus grand |aᵢ − bᵢ| / max(|aᵢ|, |bᵢ|, 10⁻⁸). Sur l'exemple, il vaut 1,1 × 10⁻¹⁰ pour le bon gradient et 0,75 pour la version fautive.

**`descente(p, donnees, cout, eta, epoques)`.** À chaque époque, on note la perte, on calcule le gradient du lot complet, puis on applique θ ← θ − η∇ℒ à W⁽¹⁾, b⁽¹⁾, W⁽²⁾ et b⁽²⁾. Les quatre mises à jour utilisent le même `g`, calculé avant de toucher aux poids.

**`premier_pas_adam`, `penalites`, `pas_l2`, `pas_l1`.** Les rappels : un pas d'Adam depuis m = v = 0, les deux pénalités de l'ancien bloc, un pas L2 `(1 - eta * lam) * w` et un pas L1 `math.copysign(max(abs(w) - eta * lam, 0.0), w)`. Avec `eta = 0.5` et `lam = 0.1` : 1,9 et 1,95 pour w = 2,0 ; 0,038 et 0,0 pour w = 0,04.

**`main()`, bloc par bloc.**

1. σ′ comparée à une différence finie en z = 0, 2 et 5, la borne 1/4 sur 201 points, l'absence de débordement en ±1 000, et 0,25¹⁰.
2. Le réseau du point 7 : chaque valeur du tableau est vérifiée par `assert`, puis le gradient est comparé aux différences finies (écart 1,1 × 10⁻¹⁰), et la variante fautive est rejetée (0,75).
3. La même chose en entropie croisée : ∂ℒ/∂b⁽²⁾ vaut exactement ŷ − y = −0,51556.
4. XOR avec un réseau 2 → 4 → 1 tiré avec la graine 75 : test de gradient avant l'entraînement, 3 000 époques à η = 1, perte strictement décroissante aux époques notées, sorties au-dessus de 0,9 pour les 1 et sous 0,1 pour les 0, puis nouveau test de gradient sur le réseau entraîné.
5. Les rappels d'Adam et de L1/L2, puis une entrée de trois nombres refusée par `propagation`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`sigmoide_derivee(z)`** — Cette fonction mesure la sensibilité d'un neurone sigmoïde, comme un ingénieur qui note de combien la sortie d'un amplificateur bouge quand on tourne légèrement le bouton d'entrée : elle reçoit une pré-activation z, calcule s = σ(z) avec la version stable de `sigmoide`, et renvoie s(1 − s). Elle vaut au plus 0,25, atteint en z = 0, puis 0,10499 en z = 2 et seulement 0,00665 en z = 5, quand le neurone sature ; c'est ce facteur que la rétropropagation multiplie à chaque couche, d'où la borne 0,25¹⁰ pour dix couches.

**`propagation(p, x)`** — Celle-ci fait traverser le réseau à une entrée, du rez-de-chaussée jusqu'au dernier étage, en notant ce qui se passe à chaque palier : elle reçoit le dictionnaire des paramètres et une entrée, lève une `ValueError` si la taille de l'entrée ne correspond pas au nombre de colonnes de W⁽¹⁾, calcule z⁽¹⁾ = W⁽¹⁾x + b⁽¹⁾, son activation a⁽¹⁾, puis z⁽²⁾ et la sortie ŷ = σ(z⁽²⁾). Elle renvoie un dictionnaire qui garde l'entrée et toutes ces valeurs intermédiaires, dont la rétropropagation a besoin ; sur l'exemple x = (1, 2), z⁽¹⁾ vaut 0,5 et 0,5, a⁽¹⁾ vaut 0,62246 deux fois et ŷ vaut 0,48444.

**`perte(p, donnees, cout)`** — Cette fonction est le correcteur qui note la copie du réseau sur tout le lot : elle reçoit les paramètres, la liste des exemples et le nom du coût, fait passer chaque exemple par `propagation`, ajoute ½(ŷ − y)² pour le coût « mse » ou l'entropie croisée −[y ln ŷ + (1 − y) ln(1 − ŷ)] pour « bce », lève une `ValueError` pour tout autre nom, puis renvoie la moyenne. Sur l'exemple, ½ × 0,51556² = 0,13290 ; sur le XOR, l'entropie croisée tombe de 0,7680 à 0,0026 en 3 000 époques.

**`retropropagation(p, donnees, cout, fautive)`** — Celle-ci remonte le réseau de la sortie vers l'entrée, comme un enquêteur qui reconstitue à rebours la part de chaque témoin dans l'erreur finale : elle reçoit les paramètres, le lot, le coût et un drapeau qui, s'il vaut vrai, oublie volontairement le facteur σ′(z⁽²⁾) de la sortie, puis, pour chaque exemple, calcule δ⁽²⁾, en déduit δ⁽¹⁾ avec les poids de sortie encore intacts, et accumule les gradients de W⁽²⁾, b⁽¹⁾, W⁽¹⁾ et b⁽²⁾. Elle renvoie leur moyenne sur le lot sans modifier les paramètres ; sur l'exemple, δ⁽²⁾ vaut −0,12876, ou −0,51556 dans la version fautive, et chaque composante du gradient de W⁽²⁾ vaut −0,08015.

**`emplacements(p)`** — Cette fonction génératrice est l'inventaire qui désigne chaque paramètre du réseau par son tiroir et son numéro, pour qu'on puisse le modifier sur place : elle reçoit le dictionnaire des paramètres et produit, l'un après l'autre, les couples (conteneur, indice) de chaque poids de W⁽¹⁾ ligne par ligne, de chaque biais de b⁽¹⁾, de chaque poids de W⁽²⁾, et enfin le couple formé du dictionnaire lui-même et de la clé « b2 », car un nombre seul ne peut pas être modifié par référence. `gradient_numerique` la parcourt pour perturber chaque paramètre dans le même ordre que `aplatir`.

**`aplatir(g)`** — Celle-ci range les quatre gradients sur une seule étagère, dans un ordre fixé, pour qu'on puisse les comparer case à case : elle reçoit un dictionnaire de gradients de même forme que les paramètres, et renvoie une liste plate qui met bout à bout les lignes de W⁽¹⁾, puis b⁽¹⁾, W⁽²⁾ et enfin b⁽²⁾, exactement l'ordre que suit `emplacements`. Elle permet à `ecart_relatif` de confronter, composante par composante, le gradient de `retropropagation` au gradient obtenu par différences finies.

**`gradient_numerique(p, donnees, cout, h)`** — Cette fonction est le contre-expert qui ne croit aucune formule et mesure la pente en tâtant le terrain des deux côtés : elle reçoit les paramètres, le lot, le coût et un petit pas h de 10⁻⁵ par défaut, puis, pour chaque paramètre désigné par `emplacements`, lui ajoute h, recalcule la perte, lui retranche h, la recalcule, remet la valeur d'origine et note (ℒ(w + h) − ℒ(w − h)) / 2h. Elle renvoie la liste de ces dérivées dans l'ordre de `aplatir`, qui sert de référence pour vérifier la rétropropagation avant et après l'entraînement du XOR.

**`ecart_relatif(a, b)`** — Celle-ci est l'arbitre qui dit si deux gradients concordent, sans se laisser tromper par l'échelle de chaque composante : elle reçoit deux listes de même longueur et renvoie le plus grand des rapports |aᵢ − bᵢ| / max(|aᵢ|, |bᵢ|, 10⁻⁸), le plancher de 10⁻⁸ évitant de diviser par zéro. Sur l'exemple, elle vaut 1,1 × 10⁻¹⁰ pour la bonne rétropropagation et 0,75 pour la version qui oublie σ′(z⁽²⁾), ce qui suffit à démasquer l'ancienne erreur.

**`premier_pas_adam(g, eta, beta1, beta2, eps)`** — Cette fonction est un rappel de l'étape 74, qui rejoue le tout premier pas d'Adam depuis des moments nuls : elle reçoit un gradient et les réglages par défaut, η = 0,001, β₁ = 0,9, β₂ = 0,999 et ε = 10⁻⁸, calcule les moments corrigés, qui valent g et g² au premier pas, puis le pas η m̂ / (√v̂ + ε). Elle renvoie ces trois nombres ; pour g = 2, m̂ = 2, v̂ = 4 et le pas vaut 0,001, soit η fois le signe du gradient.

**`penalites(poids, lam)`** — Celle-ci est le percepteur qui calcule les deux taxes de régularisation de l'ancien bloc : elle reçoit une liste de poids et λ, et renvoie le couple λ Σ|w| pour L1 et λ Σ w² pour L2, la convention de l'ancien bloc, alors que l'étape 76 utilise λ/2 Σ w². Pour les poids 0,1 ; 0,5 ; 2,0 ; −1,5 ; 0,01 et λ = 0,01, elle donne 0,0411 et 0,0651.

**`pas_l2(w, eta, lam)`** — Cette fonction fait un pas de régularisation L2 seule, comme un ressort qui ramène chaque poids vers zéro d'une fraction fixe de sa valeur : elle reçoit un poids, le pas η et λ, et renvoie (1 − ηλ)w, le pas de descente sur la pénalité λ/2 w² quand le gradient des données est nul. Avec η = 0,5 et λ = 0,1, un poids de 2,0 devient 1,9 et un poids de 0,04 devient 0,038 : la L2 rétrécit tout, mais n'annule jamais rien.

**`pas_l1(w, eta, lam)`** — Celle-ci fait le pas proximal de la L1, un seuillage doux, comme un douanier qui prélève la même somme fixe sur chaque colis et confisque ceux qui valent moins : elle reçoit un poids, η et λ, et renvoie le signe du poids multiplié par max(|w| − ηλ, 0). Avec η = 0,5 et λ = 0,1, le seuil vaut 0,05 : un poids de 2,0 devient 1,95, tandis qu'un poids de 0,04, sous le seuil, tombe exactement à 0, ce que la L2 ne fait jamais.

**`main()`** — C'est l'examinateur qui fait passer à la rétropropagation cinq épreuves : il compare d'abord σ′ à des différences finies en z = 0, 2 et 5 et vérifie la borne 1/4 et l'absence de débordement, puis déroule le réseau 2 → 2 → 1 de l'exemple, vérifie chaque valeur, confronte le gradient aux différences finies, à 1,1 × 10⁻¹⁰ près, et rejette la version fautive à 0,75. Il refait la vérification en entropie croisée, entraîne un réseau 2 → 4 → 1 sur le XOR pendant 3 000 époques jusqu'à des sorties de 0,003 et 0,997, rappelle Adam, L1 et L2, et termine en vérifiant qu'une entrée de trois nombres est refusée.

```python
"""Étape 75 — rétropropagation d'un petit réseau, vérifiée par différences finies ; rappels Adam (étape 74) et L1/L2 (étape 76)."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- sigmoïde
def sigmoide(z: float) -> float:
    """σ(z) = 1 / (1 + e^(−z)), écrite sans débordement pour les grands |z|."""
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def sigmoide_derivee(z: float) -> float:
    """σ'(z) = σ(z)(1 − σ(z))."""
    s = sigmoide(z)
    return s * (1.0 - s)


# ---------------------------------------------------------------- réseau n → h → 1
def nouveau_reseau(n: int, h: int, graine: int) -> dict:
    rng = random.Random(graine)
    return {
        "W1": [[rng.uniform(-1.0, 1.0) for _ in range(n)] for _ in range(h)],   # h × n
        "b1": [0.0] * h,
        "W2": [rng.uniform(-1.0, 1.0) for _ in range(h)],                       # 1 × h, rangé en liste
        "b2": 0.0,
    }


def propagation(p: dict, x: list[float]) -> dict:
    """z¹ = W¹x + b¹, a¹ = σ(z¹), z² = W²a¹ + b², ŷ = σ(z²). On garde tout pour le retour."""
    if len(x) != len(p["W1"][0]):
        raise ValueError("x n'a pas la taille attendue par W1")
    z1 = [sum(w * xi for w, xi in zip(ligne, x)) + b for ligne, b in zip(p["W1"], p["b1"])]
    a1 = [sigmoide(z) for z in z1]
    z2 = sum(w * a for w, a in zip(p["W2"], a1)) + p["b2"]
    return {"x": x, "z1": z1, "a1": a1, "z2": z2, "y_hat": sigmoide(z2)}


def perte(p: dict, donnees: list[tuple[list[float], float]], cout: str) -> float:
    """Moyenne sur les exemples de ½(ŷ − y)² (cout = "mse") ou de −[y ln ŷ + (1 − y) ln(1 − ŷ)] ("bce")."""
    total = 0.0
    for x, y in donnees:
        y_hat = propagation(p, x)["y_hat"]
        if cout == "mse":
            total += 0.5 * (y_hat - y) ** 2
        elif cout == "bce":
            total += -(y * math.log(y_hat) + (1 - y) * math.log(1 - y_hat))
        else:
            raise ValueError("cout = 'mse' ou 'bce'")
    return total / len(donnees)


def retropropagation(p: dict, donnees: list[tuple[list[float], float]], cout: str, fautive: bool = False) -> dict:
    """Gradients moyens de la perte par rapport à W¹, b¹, W², b².
    fautive=True reproduit l'ancienne erreur : σ'(z²) oublié à la sortie avec la perte quadratique."""
    h, n = len(p["W1"]), len(p["W1"][0])
    g = {"W1": [[0.0] * n for _ in range(h)], "b1": [0.0] * h, "W2": [0.0] * h, "b2": 0.0}
    for x, y in donnees:
        c = propagation(p, x)
        if cout == "mse":
            delta2 = (c["y_hat"] - y) * (1.0 if fautive else sigmoide_derivee(c["z2"]))
        else:
            delta2 = c["y_hat"] - y                  # σ' se simplifie avec la dérivée de l'entropie croisée
        delta1 = [p["W2"][i] * delta2 * sigmoide_derivee(c["z1"][i]) for i in range(h)]   # (W²)ᵀδ² ⊙ σ'(z¹)
        for i in range(h):
            g["W2"][i] += delta2 * c["a1"][i]
            g["b1"][i] += delta1[i]
            for j in range(n):
                g["W1"][i][j] += delta1[i] * x[j]
        g["b2"] += delta2
    m = len(donnees)
    return {"W1": [[v / m for v in ligne] for ligne in g["W1"]], "b1": [v / m for v in g["b1"]],
            "W2": [v / m for v in g["W2"]], "b2": g["b2"] / m}


def emplacements(p: dict):
    """Liste (conteneur, indice) de chaque paramètre, pour les modifier un par un."""
    for ligne in p["W1"]:
        for j in range(len(ligne)):
            yield ligne, j
    for nom in ("b1", "W2"):
        for j in range(len(p[nom])):
            yield p[nom], j
    yield p, "b2"


def aplatir(g: dict) -> list[float]:
    return [v for ligne in g["W1"] for v in ligne] + list(g["b1"]) + list(g["W2"]) + [g["b2"]]


def gradient_numerique(p: dict, donnees, cout: str, h: float = 1e-5) -> list[float]:
    """Différence centrée (ℒ(w + h) − ℒ(w − h)) / 2h pour chaque paramètre, dans l'ordre d'aplatir()."""
    resultat = []
    for conteneur, cle in emplacements(p):
        ancien = conteneur[cle]
        conteneur[cle] = ancien + h
        plus = perte(p, donnees, cout)
        conteneur[cle] = ancien - h
        moins = perte(p, donnees, cout)
        conteneur[cle] = ancien
        resultat.append((plus - moins) / (2 * h))
    return resultat


def ecart_relatif(a: list[float], b: list[float]) -> float:
    """max |aᵢ − bᵢ| / max(|aᵢ|, |bᵢ|, 1e-8) : un écart sans unité, comparable d'un poids à l'autre."""
    return max(abs(x - y) / max(abs(x), abs(y), 1e-8) for x, y in zip(a, b))


def descente(p: dict, donnees, cout: str, eta: float, epoques: int) -> list[float]:
    """Descente de gradient (étape 73) sur tout le lot ; renvoie la perte avant chaque époque, puis à la fin."""
    historique = []
    for _ in range(epoques):
        historique.append(perte(p, donnees, cout))
        g = retropropagation(p, donnees, cout)
        for i, ligne in enumerate(p["W1"]):
            for j in range(len(ligne)):
                ligne[j] -= eta * g["W1"][i][j]
        p["b1"] = [b - eta * gb for b, gb in zip(p["b1"], g["b1"])]
        p["W2"] = [w - eta * gw for w, gw in zip(p["W2"], g["W2"])]
        p["b2"] -= eta * g["b2"]
    historique.append(perte(p, donnees, cout))
    return historique


# ---------------------------------------------------------------- rappels des deux autres formules
def premier_pas_adam(g: float, eta: float = 1e-3, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8):
    """Un pas d'Adam depuis m = v = 0 (étape 74) : m̂ = g, v̂ = g², pas ≈ η · signe(g)."""
    m_hat = (1 - beta1) * g / (1 - beta1)
    v_hat = (1 - beta2) * g * g / (1 - beta2)
    return m_hat, v_hat, eta * m_hat / (math.sqrt(v_hat) + eps)


def penalites(poids: list[float], lam: float) -> tuple[float, float]:
    """λ Σ|w| et λ Σ w² (convention de l'ancien bloc ; l'étape 76 utilise λ/2 Σ w²)."""
    return lam * sum(abs(w) for w in poids), lam * sum(w * w for w in poids)


def pas_l2(w: float, eta: float, lam: float) -> float:
    """Pénalité λ/2 · w², gradient des données nul : w ← (1 − ηλ) w."""
    return (1 - eta * lam) * w


def pas_l1(w: float, eta: float, lam: float) -> float:
    """Pénalité λ|w|, pas proximal (seuillage doux, démontré à l'étape 76) : w ← signe(w) max(|w| − ηλ, 0)."""
    return math.copysign(max(abs(w) - eta * lam, 0.0), w)


def main() -> None:
    print("1. σ' = σ(1 − σ) : vaut au plus 1/4, et presque 0 quand σ sature")
    for z in (0.0, 2.0, 5.0):
        num = (sigmoide(z + 1e-5) - sigmoide(z - 1e-5)) / 2e-5
        print(f"  z = {z}   σ = {sigmoide(z):.5f}   σ' = {sigmoide_derivee(z):.5f}   différence finie = {num:.5f}")
        assert abs(num - sigmoide_derivee(z)) < 1e-9
    assert sigmoide_derivee(0.0) == 0.25 and all(sigmoide_derivee(z / 10) <= 0.25 for z in range(-100, 101))
    assert sigmoide(-1000.0) == 0.0 and sigmoide(1000.0) == 1.0          # pas de débordement de math.exp
    print(f"  dix couches sigmoïdes : gradient multiplié par au plus 0.25^10 = {0.25 ** 10:.2e}")

    print("2. Réseau 2 → 2 → 1, x = (1, 2), y = 1, perte ½(ŷ − y)²")
    p = {"W1": [[0.1, 0.2], [-0.3, 0.4]], "b1": [0.0, 0.0], "W2": [0.5, -0.6], "b2": 0.0}
    donnees = [([1.0, 2.0], 1.0)]
    c = propagation(p, donnees[0][0])
    g = retropropagation(p, donnees, "mse")
    print(f"  z¹ = {c['z1']}   a¹ = {[round(a, 5) for a in c['a1']]}   z² = {c['z2']:.6f}   ŷ = {c['y_hat']:.5f}")
    print(f"  ℒ = {perte(p, donnees, 'mse'):.5f}   δ² = ∂ℒ/∂b² = {g['b2']:.5f}   ∂ℒ/∂W² = {[round(v, 5) for v in g['W2']]}")
    print(f"  ∂ℒ/∂W¹ = {[[round(v, 5) for v in ligne] for ligne in g['W1']]}")
    assert c["z1"] == [0.5, 0.5] and round(c["y_hat"], 5) == 0.48444 and round(perte(p, donnees, "mse"), 5) == 0.1329
    assert round(g["b2"], 5) == -0.12876 and [round(v, 5) for v in g["W2"]] == [-0.08015, -0.08015]
    assert [[round(v, 5) for v in ligne] for ligne in g["W1"]] == [[-0.01513, -0.03026], [0.01816, 0.03631]]
    ecart = ecart_relatif(aplatir(g), gradient_numerique(p, donnees, "mse"))
    fautif = retropropagation(p, donnees, "mse", fautive=True)
    ecart_fautif = ecart_relatif(aplatir(fautif), gradient_numerique(p, donnees, "mse"))
    print(f"  écart relatif aux différences finies : {ecart:.1e} ; sans σ'(z²) à la sortie : {ecart_fautif:.2f} (∂ℒ/∂b² = {fautif['b2']:.5f})")
    assert ecart < 1e-7 and ecart_fautif > 0.5

    print("3. Entropie croisée : δ² = ŷ − y, le σ' de la sortie se simplifie")
    g_bce = retropropagation(p, donnees, "bce")
    assert abs(g_bce["b2"] - (c["y_hat"] - 1.0)) < 1e-15
    assert ecart_relatif(aplatir(g_bce), gradient_numerique(p, donnees, "bce")) < 1e-7
    print(f"  ∂ℒ/∂b² = {g_bce['b2']:.5f} = ŷ − y ; gradient vérifié par différences finies")

    print("4. XOR, réseau 2 → 4 → 1, entropie croisée, descente de gradient η = 1, 3000 époques")
    xor = [([0.0, 0.0], 0.0), ([0.0, 1.0], 1.0), ([1.0, 0.0], 1.0), ([1.0, 1.0], 0.0)]
    reseau = nouveau_reseau(2, 4, graine=75)
    assert ecart_relatif(aplatir(retropropagation(reseau, xor, "bce")), gradient_numerique(reseau, xor, "bce")) < 1e-6
    historique = descente(reseau, xor, "bce", eta=1.0, epoques=3000)
    print("  perte :" + "".join(f"   époque {e} → {historique[e]:.4f}" for e in (0, 100, 1000, 3000)))
    sorties = [propagation(reseau, x)["y_hat"] for x, _ in xor]
    print(f"  sorties pour (0,0) (0,1) (1,0) (1,1) : {[round(s, 3) for s in sorties]}")
    assert historique[-1] < historique[1000] < historique[100] < historique[0]
    assert all((s > 0.9) if y == 1.0 else (s < 0.1) for s, (_, y) in zip(sorties, xor))
    assert ecart_relatif(aplatir(retropropagation(reseau, xor, "bce")), gradient_numerique(reseau, xor, "bce")) < 1e-5

    print("5. Rappels : Adam (étape 74) et L1/L2 (étape 76)")
    m_hat, v_hat, pas = premier_pas_adam(2.0)
    assert abs(m_hat - 2) < 1e-12 and abs(v_hat - 4) < 1e-12 and abs(pas - 0.001) < 1e-11
    l1, l2 = penalites([0.1, 0.5, 2.0, -1.5, 0.01], lam=0.01)
    print(f"  Adam, g = 2 : m̂ = {m_hat:.1f}, v̂ = {v_hat:.1f}, pas = {pas:.6f}   pénalités : L1 = {l1:.4f}   L2 = {l2:.4f}")
    assert round(l1, 4) == 0.0411 and round(l2, 4) == 0.0651
    print(f"  η = 0.5, λ = 0.1 : w = 2.0 → L2 {pas_l2(2.0, 0.5, 0.1):.3f}, L1 {pas_l1(2.0, 0.5, 0.1):.3f} ;"
          f" w = 0.04 → L2 {pas_l2(0.04, 0.5, 0.1):.3f}, L1 {pas_l1(0.04, 0.5, 0.1):.3f}")
    assert abs(pas_l2(2.0, 0.5, 0.1) - 1.9) < 1e-12 and abs(pas_l1(2.0, 0.5, 0.1) - 1.95) < 1e-12
    assert abs(pas_l2(0.04, 0.5, 0.1) - 0.038) < 1e-12 and pas_l1(0.04, 0.5, 0.1) == 0.0

    try:
        propagation(p, [1.0, 2.0, 3.0])
    except ValueError:
        print("  entrée de mauvaise taille → ValueError")
    else:
        raise AssertionError("une entrée de mauvaise taille aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. σ' = σ(1 − σ) : vaut au plus 1/4, et presque 0 quand σ sature
  z = 0.0   σ = 0.50000   σ' = 0.25000   différence finie = 0.25000
  z = 2.0   σ = 0.88080   σ' = 0.10499   différence finie = 0.10499
  z = 5.0   σ = 0.99331   σ' = 0.00665   différence finie = 0.00665
  dix couches sigmoïdes : gradient multiplié par au plus 0.25^10 = 9.54e-07
2. Réseau 2 → 2 → 1, x = (1, 2), y = 1, perte ½(ŷ − y)²
  z¹ = [0.5, 0.5]   a¹ = [0.62246, 0.62246]   z² = -0.062246   ŷ = 0.48444
  ℒ = 0.13290   δ² = ∂ℒ/∂b² = -0.12876   ∂ℒ/∂W² = [-0.08015, -0.08015]
  ∂ℒ/∂W¹ = [[-0.01513, -0.03026], [0.01816, 0.03631]]
  écart relatif aux différences finies : 1.1e-10 ; sans σ'(z²) à la sortie : 0.75 (∂ℒ/∂b² = -0.51556)
3. Entropie croisée : δ² = ŷ − y, le σ' de la sortie se simplifie
  ∂ℒ/∂b² = -0.51556 = ŷ − y ; gradient vérifié par différences finies
4. XOR, réseau 2 → 4 → 1, entropie croisée, descente de gradient η = 1, 3000 époques
  perte :   époque 0 → 0.7680   époque 100 → 0.6926   époque 1000 → 0.0133   époque 3000 → 0.0026
  sorties pour (0,0) (0,1) (1,0) (1,1) : [0.003, 0.997, 0.998, 0.003]
5. Rappels : Adam (étape 74) et L1/L2 (étape 76)
  Adam, g = 2 : m̂ = 2.0, v̂ = 4.0, pas = 0.001000   pénalités : L1 = 0.0411   L2 = 0.0651
  η = 0.5, λ = 0.1 : w = 2.0 → L2 1.900, L1 1.950 ; w = 0.04 → L2 0.038, L1 0.000
  entrée de mauvaise taille → ValueError
OK — toutes les vérifications sont passées.
```

La version NumPy de l'ancien fichier, corrigée, pour des lots entiers ; elle n'est pas exécutée par le harnais. Elle ajoute les biais, absents de l'ancienne version : sans eux, l'entrée (0, 0) donne z⁽¹⁾ = 0 pour tous les neurones cachés, et le réseau répond toujours la même chose à cette entrée, quels que soient ses poids d'entrée.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`sigmoide(z)`** — C'est la même sigmoïde que dans le programme précédent, mais appliquée d'un coup à tout un tableau NumPy, comme une presse qui estampe une plaque entière au lieu d'une pièce à la fois : elle reçoit un tableau de pré-activations et renvoie 1/(1 + e⁻ᶻ) élément par élément. Elle utilise la formule directe, sans la distinction de signe de la version en bibliothèque standard ; pour une pré-activation très négative, NumPy ne plante pas mais l'exponentielle déborde vers l'infini avec un simple avertissement, et le résultat tombe à 0.

**`ReseauNumpy.__init__(couches, graine)`** — Le constructeur monte la charpente d'un réseau de profondeur quelconque, étage par étage : il reçoit la liste des tailles de couches, par exemple entrée, cachée et sortie, et une graine, 0 par défaut, crée un générateur NumPy à cette graine, tire pour chaque paire de couches consécutives une matrice de poids de loi normale centrée réduite, de forme taille d'entrée × taille de sortie, et met chaque vecteur de biais à zéro. Il ne renvoie rien ; contrairement à l'ancienne version, il prévoit les biais, sans lesquels l'entrée (0, 0) donnerait la même réponse quels que soient les poids.

**`ReseauNumpy.propagation(X)`** — Cette méthode fait traverser le réseau à tout un lot d'exemples, un par ligne de la matrice X, en gardant la trace de chaque étage : elle commence la liste `self.a` par X, puis, pour chaque couche, applique la sigmoïde au produit de l'activation précédente par la matrice de poids, plus le biais, et ajoute le résultat à la liste. Elle renvoie la dernière activation, la sortie du réseau pour chaque exemple, et laisse dans l'objet toutes les activations intermédiaires dont la rétropropagation a besoin.

**`ReseauNumpy.retropropagation(y, eta)`** — Celle-ci remonte le réseau couche par couche et corrige les poids en chemin, avec la même rigueur que `retropropagation` du programme précédent : elle reçoit les sorties voulues et le pas η, part de δ = sortie − y, l'erreur de l'entropie croisée où le σ′ de la sortie se simplifie, puis, de la dernière couche à la première, calcule le gradient moyen des poids et des biais, propage δ vers la couche précédente avec l'ancien W avant de le modifier, et applique la descente de gradient. Elle ne renvoie rien et met à jour les poids sur place ; elle suppose que `propagation` vient d'être appelée sur le même lot.

```python
# [extrait] — rétropropagation vectorisée avec NumPy, un exemple par ligne (non exécuté : NumPy hors bibliothèque standard)
import numpy as np


def sigmoide(z):
    return 1 / (1 + np.exp(-z))


class ReseauNumpy:
    def __init__(self, couches, graine=0):
        rng = np.random.default_rng(graine)
        self.W = [rng.normal(0, 1, (a, b)) for a, b in zip(couches[:-1], couches[1:])]
        self.b = [np.zeros(b) for b in couches[1:]]

    def propagation(self, X):
        self.a = [X]
        for W, b in zip(self.W, self.b):
            self.a.append(sigmoide(self.a[-1] @ W + b))
        return self.a[-1]

    def retropropagation(self, y, eta):
        m = y.shape[0]
        delta = self.a[-1] - y                      # entropie croisée : le σ' de la sortie se simplifie
        for l in reversed(range(len(self.W))):
            dW = self.a[l].T @ delta / m
            db = delta.mean(axis=0)
            if l > 0:                               # avec l'ANCIEN W[l], avant la mise à jour
                delta = (delta @ self.W[l].T) * self.a[l] * (1 - self.a[l])
            self.W[l] -= eta * dW
            self.b[l] -= eta * db
```

## Squelette algorithmique

Deux squelettes résument le fichier. Le premier est la rétropropagation d'un réseau à une couche cachée de h neurones, n entrées et une sortie : en entrée, les poids, un lot de m exemples et le choix de la perte ; en sortie, les quatre gradients moyens. Le second est le test de gradient qui la vérifie : en entrée, les paramètres, la perte, le gradient à contrôler et un pas h ; en sortie, VRAI si le plus grand écart relatif reste sous un seuil. L'idée : propager vers l'avant en gardant les valeurs intermédiaires, puis remonter de la sortie vers l'entrée en multipliant par la dérivée locale de chaque étape, sans modifier aucun poids avant d'avoir fini.

```text
ALGORITHME Rétropropagation
ENTRÉES : W¹ (h × n), b¹ (h nombres), W² (h nombres), b², lot de m exemples (x, y),
          perte « quadratique » ou « entropie croisée »
SORTIE : gradients moyens gW¹, gb¹, gW², gb²

gW¹ ← 0 ;  gb¹ ← 0 ;  gW² ← 0 ;  gb² ← 0
POUR CHAQUE exemple (x, y) DU lot FAIRE
    POUR i DE 1 À h FAIRE                                   propagation avant, valeurs gardées
        z¹[i] ← Σⱼ W¹[i][j] · x[j] + b¹[i] ;  a¹[i] ← σ(z¹[i])
    FIN POUR
    z² ← Σᵢ W²[i] · a¹[i] + b² ;  ŷ ← σ(z²)
    SI perte = « quadratique » ALORS
        δ² ← (ŷ − y) · σ(z²) · (1 − σ(z²))                  le σ' de la sortie est indispensable
    SINON
        δ² ← ŷ − y                                          le σ' se simplifie avec l'entropie croisée
    FIN SI
    POUR i DE 1 À h FAIRE
        δ¹[i] ← W²[i] · δ² · σ(z¹[i]) · (1 − σ(z¹[i]))      avec l'ANCIEN W², avant toute mise à jour
        gW²[i] ← gW²[i] + δ² · a¹[i]
        gb¹[i] ← gb¹[i] + δ¹[i]
        POUR j DE 1 À n FAIRE
            gW¹[i][j] ← gW¹[i][j] + δ¹[i] · x[j]
        FIN POUR
    FIN POUR
    gb² ← gb² + δ²
FIN POUR
RETOURNER gW¹ / m, gb¹ / m, gW² / m, gb² / m

ALGORITHME TestDeGradient
ENTRÉES : paramètres θ (P nombres), fonction perte, gradient analytique g, pas h, seuil s
SORTIE : VRAI si le gradient analytique est juste à s près

pire ← 0
POUR k DE 1 À P FAIRE
    ancien ← θ[k]
    θ[k] ← ancien + h ;  plus ← perte(θ)
    θ[k] ← ancien − h ;  moins ← perte(θ)
    θ[k] ← ancien                                           remettre la valeur, sinon les essais suivants sont faussés
    num ← (plus − moins) / (2h)                             erreur de troncature en h²
    pire ← max(pire, |num − g[k]| / max(|num|, |g[k]|, 10⁻⁸))
FIN POUR
RETOURNER pire ≤ s
```

**Complexité :** pour un exemple, la propagation avant coûte O(h n) (les h produits scalaires de longueur n) plus O(h) pour la sortie, et le retour coûte autant : O(h n) pour gW¹, O(h) pour δ¹, gW² et gb¹. Une rétropropagation sur le lot vaut donc O(m h n) en temps, le même ordre que la propagation avant. En mémoire, il faut O(h n) pour les gradients, plus O(h) pour les valeurs gardées d'un exemple, puisqu'on traite les exemples un par un ; une version vectorisée qui garde tout le lot paie O(m h) pour ces valeurs. Le test de gradient, lui, fait deux propagations complètes par paramètre : avec P = h n + 2h + 1 paramètres, il coûte O(P · m h n), soit O(m h² n²), quadratique dans la taille du réseau au lieu de linéaire. Pour le réseau 2 → 4 → 1 (P = 17), c'est 34 propagations contre une rétropropagation ; pour un modèle d'un milliard de poids, c'est impossible, d'où son usage limité à la vérification.

**Du squelette au code :** les deux boucles de la propagation avant sont `propagation(p, x)`, qui renvoie `z1`, `a1`, `z2` et `y_hat`. Le corps de Rétropropagation est `retropropagation(p, donnees, cout)` : le test « SI perte = quadratique » est la branche `if cout == "mse"`, le facteur σ(z²)(1 − σ(z²)) est `sigmoide_derivee(c["z2"])` (remplacé par 1 quand `fautive=True`), la ligne δ¹ est la compréhension `delta1 = [...]`, les accumulations sont les `+=` sur `g`, et la division finale par m est le dictionnaire renvoyé. TestDeGradient est `gradient_numerique(p, donnees, cout)`, qui parcourt les paramètres grâce à `emplacements(p)`, suivi de `ecart_relatif(aplatir(g), ...)` pour le calcul de « pire » ; le seuil s est la borne des `assert`, 10⁻⁷ sur l'exemple et 10⁻⁶ ou 10⁻⁵ sur XOR. La boucle d'entraînement qui utilise ces gradients est `descente(p, donnees, cout, eta, epoques)`, le squelette DescenteDeGradient de l'étape 73.

## Cas d'usage réels aux Émirats

Les tailles de réseau, les volumes et les seuils ci-dessous sont illustratifs : ils servent à faire le calcul, pas à décrire un déploiement réel.

### Banque — un test de gradient avant chaque entraînement du routeur

Une banque de détail de Dubaï fait passer chaque message de son assistant par un petit routeur d'intentions, un réseau à une couche cachée qui lit l'embedding du message et choisit entre consultation de solde, virement, réclamation et demande de crédit. Comme les demandes de virement sont rares mais sensibles, l'équipe a écrit une perte pondérée par classe, et donc sa propre rétropropagation. Avant chaque entraînement, le pipeline lance le test de gradient du point 6 sur un lot de huit messages et refuse de continuer si l'écart relatif dépasse 10⁻⁶ ; un jour, il a bloqué une modification qui avait perdu le facteur σ′ de la sortie, avec un écart de l'ordre de 0,75 comme dans le programme. Sans ce test, le routeur aurait appris avec un gradient faux d'un facteur variable, et une part des virements aurait été routée vers les réclamations. L'outil de virement garde de toute façon son approbation humaine à l'intérieur de l'outil : un routeur mal entraîné ne peut pas déclencher de paiement à lui seul. On suit l'exactitude du routage sur un jeu de référence et la Tool Call F1 (étape 59).

### Assurance — une sortie saturée qui n'apprend plus

Un assureur auto et santé entraîne un modèle de score de fraude dont la sortie est une sigmoïde. La première version utilisait la perte quadratique et des montants en AED non normalisés : les pré-activations atteignaient plusieurs dizaines, et la sigmoïde de sortie, saturée, renvoyait des gradients presque nuls. À z = 5, σ′ vaut déjà 0,00665, près de 38 fois moins qu'en 0 ; un dossier frauduleux noté 0,01 recevait ainsi un signal d'erreur divisé par cent, et le modèle restait sûr de lui en se trompant. L'équipe a normalisé les montants et adopté l'entropie croisée, qui donne δ⁽²⁾ = ŷ − y, soit 0,99 de signal pour ce même dossier (point 5). L'agent de tri, qui envoie à un expert les sinistres au-dessus d'un seuil de score, a cessé de laisser passer les fraudes les plus évidentes. On suit le rappel sur les fraudes confirmées et la perte de validation par époque.

### Secteur public — un détecteur d'injection trop profond pour la sigmoïde

Une entité de services publics en ligne, accessible par UAE Pass, entraîne un classifieur qui repère les tentatives d'injection de prompt (étape 66) dans les messages des usagers, en arabe et en anglais. Une première architecture empilait dix couches cachées à sigmoïde : les premières couches ne bougeaient presque pas, parce que le signal d'erreur qui leur parvenait était multiplié par au plus 0,25¹⁰ ≈ 9,5 × 10⁻⁷ (point 1). L'équipe a remplacé les sigmoïdes cachées par des ReLU et ne garde la sigmoïde qu'en sortie, avec l'entropie croisée. Les messages d'entraînement relèvent de la PDPL : ils sont pseudonymisés et les numéros d'Emirates ID sont masqués avant de servir d'exemples. Sans ce changement, le classifieur se réduisait à sa dernière couche et manquait les injections reformulées. On suit la précision et le rappel du détecteur sur un jeu étiqueté, en sachant qu'un tel détecteur se contourne et ne remplace pas la politique de refus par défaut.

### Crypto — une sigmoïde qui fait planter le service

Une plateforme d'actifs virtuels agréée par la VARA calcule en continu un score d'anomalie de liquidité avec un petit réseau entraîné chaque nuit. Pendant un mouvement de marché brutal, une entrée mal bornée a produit une pré-activation de −800, et la sigmoïde écrite naïvement, `1 / (1 + math.exp(-z))`, a levé `OverflowError` : `math.exp(800)` dépasse le plus grand flottant. Le service de score s'est arrêté au moment précis où l'agent de surveillance en avait le plus besoin. La version stable du programme, qui calcule `e / (1 + e)` avec `e = math.exp(z)` quand z est négatif, renvoie simplement une valeur proche de 0. La plateforme borne aussi ses entrées et journalise la norme du gradient de chaque couche pendant l'entraînement, pour repérer une valeur infinie ou NaN avant d'exporter le modèle. On suit le nombre d'erreurs du service de score et le délai de prise en charge des alertes critiques.

### RH — un gradient qui grandissait avec la taille du lot

Un cabinet RH présent dans plusieurs émirats entraîne un modèle qui ordonne les candidatures reçues pour un poste, à partir des décisions passées des recruteurs. Sa rétropropagation maison additionnait les gradients des exemples sans les diviser par m. En passant de lots de 32 à des lots de 256 candidatures, l'équipe a vu l'entraînement diverger : le gradient était devenu huit fois plus grand, et η, réglé pour des lots de 32, était désormais trop long (étape 73, point 3). Le test de gradient, fait contre la perte **moyenne**, signalait un écart d'un facteur m ; la division finale par `len(donnees)` l'a corrigé. Les décisions de l'agent restent soumises à un recruteur humain, et le cabinet vérifie avec ses juristes quelles données il a le droit d'utiliser comme entrée, à confirmer avec le texte en vigueur. On suit le taux d'entretiens obtenus par les candidatures classées en tête.

### Immobilier — mettre à jour les poids trop tôt

Une agence active à Dubaï et à Abu Dhabi entraîne un reranker qui ordonne les biens proposés par son agent. Une réécriture de la boucle d'entraînement mettait à jour W⁽²⁾ avant de calculer δ⁽¹⁾ : la couche cachée recevait une faute calculée avec des poids qui avaient déjà bougé. L'écart restait petit à chaque pas, donc l'entraînement « marchait », mais la perte de validation plafonnait plus haut qu'avant et le classement favorisait toujours les mêmes quartiers. Le test de gradient, lancé sur cette boucle, a montré un écart relatif très au-dessus du seuil de 10⁻⁶, alors que la version juste reste vers 10⁻¹⁰ ; l'ordre des opérations du point 4 a été rétabli : on calcule tous les gradients, puis on met à jour tous les poids. Sans ce test, l'erreur serait passée pour un réglage d'hyperparamètres. On suit le taux de visites programmées par proposition et la perte de validation finale.

## Pièges et limites

- **Oublier σ′ à la sortie avec la perte quadratique.** Le gradient est faux d'un facteur 1/σ′(z⁽²⁾) qui change d'un exemple à l'autre ; avec l'entropie croisée, ce facteur disparaît légitimement, et c'est souvent ce qui crée la confusion.
- **Mettre à jour une couche avant d'avoir rétropropagé à travers elle.** δ⁽¹⁾ doit utiliser l'ancien W⁽²⁾.
- **Choisir mal le pas du test de gradient.** Un h trop grand laisse une erreur en h², un h trop petit fait dominer l'arrondi ; 10⁻⁵ en double précision, et un écart relatif plutôt qu'absolu.
- **Faire le test de gradient avec un élément aléatoire actif.** Avec du *dropout* ou des données mélangées entre les deux appels, la perte change d'un appel à l'autre et le test ne veut plus rien dire.
- **Empiler des sigmoïdes en couches cachées.** Chaque couche divise le signal par au moins 4 ; on garde la sigmoïde pour la sortie.

### Exercice feuille blanche

1. Sans regarder le code, écrire `sigmoide`, `sigmoide_derivee` et `retropropagation` pour un réseau n → h → 1, puis vérifier σ′(0) = 0,25 et σ′(2) = 0,10499.
2. Dans l'exemple du point 7, on remplace y = 1 par y = 0. Prédire δ⁽²⁾ avec la perte quadratique, puis avec l'entropie croisée. (Réponse : 0,48444 × 0,24976 ≈ 0,12099 ; puis 0,48444.)
3. Trouver le bug : dans une boucle qui parcourt les couches de la sortie vers l'entrée, la ligne `self.W[l] -= eta * dW` est placée **avant** la ligne qui calcule le `delta` de la couche précédente. Que mesure le test de gradient, et pourquoi l'entraînement semble-t-il quand même fonctionner ?

## Pour aller plus loin

La rétropropagation est un cas particulier de la différentiation automatique en mode inverse : elle calcule le gradient d'une fonction à une sortie en un seul passage arrière, quel que soit le nombre d'entrées. Pour des réseaux profonds, l'initialisation des poids (Xavier pour la tanh et la sigmoïde, He pour ReLU) choisit l'échelle de départ pour que la variance des activations et des gradients reste stable d'une couche à l'autre.

> Suite : [Mini-lots et généralisation](<75b-Mini-Lots-et-Generalisation.md>) — étape 75 bis.
