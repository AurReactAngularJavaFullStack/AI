# Étape 32 — Attention — Formules et mécanisme d'attention

> Étape 32 du parcours · Prérequis : [Attention par produit scalaire mis à l'échelle](<31-Attention-Formule-Produit-Scalaire-Normalise.md>) · Suite : [Transformer et attention](<33-Transformer-et-Attention-Deroule-Numerique.md>)

**Leçon longue — le facteur d'échelle √dₖ, la saturation de la softmax et ce que l'attention explique (ou non) des contextes longs**

## Introduction narrative

Même si tu n'entraînes pas de modèles depuis zéro, comprendre le mécanisme d'attention t'aide à diagnostiquer les problèmes de contexte long. Prends l'agent d'onboarding d'un cabinet RH multi-émirats. Au fil d'une conversation de 40 messages, une nouvelle recrue envoie son passeport, pose une question sur son indemnité de fin de service, précise au message 12 que son employeur est une entité de la DIFC, puis demande un récapitulatif au message 40. Il arrive que ce récapitulatif oublie l'exception du message 12 et applique le barème fédéral de fin de service, qui ne concerne pas la DIFC.

La formule d'attention explique une partie du problème, et une partie seulement. Elle implique une **dilution** : chaque message ajouté prend sa part d'un budget de poids qui somme toujours à 1, donc une information utile pèse moins dans un long contexte que dans un court. Elle n'explique pas, en revanche, pourquoi une information placée **au milieu** est plus souvent manquée qu'au début ou à la fin : cet « oubli du milieu » est un effet observé sur les modèles entraînés, que la formule seule ne produit pas, puisqu'elle est insensible à l'ordre (étape 31, point 4). L'ancienne version de ce fichier présentait la formule comme la cause de cet oubli ; c'est corrigé ici (démonstration, point 8). Les techniques d'ingénierie de contexte — compaction, résumé, récupération sélective, bloc de faits établis — répondent aux deux phénomènes : elles réduisent la dilution, et elles évitent de dépendre de la position.

Ce fichier démontre le résultat que l'étape 31 a seulement annoncé : pourquoi diviser les scores par √dₖ, et ce qui arrive quand on l'oublie.

## Définition

Le facteur d'échelle √dₖ divise chaque produit scalaire requête-clé avant la softmax. Si les composantes des requêtes et des clés sont indépendantes, de moyenne 0 et de variance 1, le produit scalaire a une variance égale à dₖ, la dimension des clés : son écart-type vaut 8 pour dₖ = 64 et 16 pour dₖ = 256. Diviser par √dₖ ramène cette variance à 1, quelle que soit la dimension. Sans cette division, les scores sont si dispersés que la softmax met presque tout le poids sur une seule clé ; elle **sature**, et la pente p(1−p) par laquelle le gradient remonte devient presque nulle, si bien que l'apprentissage s'arrête. Le facteur n'est donc pas décoratif : c'est une température fixe,

$$
T = \sqrt{d_k} ,
$$

choisie pour que la softmax travaille dans sa zone utile.

## Rôle dans un agent

Comme à l'étape 31, ce calcul se passe à l'intérieur du LLM, pendant l'étape **décider** de la boucle percevoir → décider → agir → observer. Il concerne le développeur d'agent dans trois situations. Quand il **réimplémente** une couche d'attention (un petit modèle interne, un noyau optimisé, un modèle exporté pour une exécution sur site), oublier le facteur est une erreur silencieuse qui fait caler l'entraînement. Quand il **code lui-même** une moyenne pondérée par softmax — pondérer des comparables, des souvenirs, des passages récupérés —, il doit choisir une température avec le même raisonnement que √dₖ. Et quand il **diagnostique** un agent qui « oublie » une information, il doit distinguer ce que la formule implique (la dilution) de ce qui est un effet observé du modèle (la position), qui se mesure.

## Équation complète

Attention, rappel de l'étape 31 :

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V
$$

Score brut d'une requête 𝐪 et d'une clé 𝐤 :

$$
S = \mathbf{q} \cdot \mathbf{k} = \sum_{l=1}^{d_k} q_l\, k_l
$$

Théorème, sous les hypothèses H1, H2 et H3 de la démonstration :

$$
\mathbb{E}[S] = 0 \qquad \text{et} \qquad \operatorname{Var}(S) = d_k
$$

Effet de la division :

$$
\operatorname{Var}\left( \frac{S}{\sqrt{d_k}} \right) = 1
$$

Pente de la softmax (étape 2), qui tend vers 0 quand un poids tend vers 1 :

$$
\frac{\partial p_i}{\partial z_i} = p_i \,(1 - p_i)
$$

## Décryptage des symboles

$$
Q,\quad K,\quad V
$$

**Sens :** matrices des requêtes, des clés et des valeurs (étape 31) · **Type / plage :** voir le bloc ci-dessous · **Variable Python :** `K`, `V`

$$
n_q \times d_k,\quad n_k \times d_k,\quad n_k \times d_v
$$

$$
\mathbf{q},\quad \mathbf{k}
$$

**Sens :** une requête, une clé · **Type / plage :** vecteurs de taille dₖ · **Variable Python :** `q`, `k`

$$
q_l,\quad k_l
$$

**Sens :** composante numéro l de 𝐪 et de 𝐤 · **Type / plage :** réels · **Variable Python :** `q[l]`, `k[l]`

$$
d_k
$$

**Sens :** dimension des requêtes et des clés ; en multi-têtes, (formule ci-dessous) (étape 34) · **Type / plage :** entier ≥ 1, souvent 64 ou 128 · **Variable Python :** `d_k`

$$
d_k = d_{model}/h
$$

$$
S
$$

**Sens :** score brut 𝐪 · 𝐤, avant division · **Type / plage :** réel · **Variable Python :** `produit_scalaire(q, k)`

$$
\mathbb{E}[X]
$$

**Sens :** espérance (moyenne théorique) de la variable aléatoire X · **Type / plage :** réel · **Variable Python :** estimée par `moyenne_variance`

$$
\operatorname{Var}(X)
$$

**Sens :** variance : 𝔼[X²] − 𝔼[X]² · **Type / plage :** réel ≥ 0 · **Variable Python :** estimée par `moyenne_variance`

$$
\operatorname{Cov}(X, Y)
$$

**Sens :** covariance : 𝔼[XY] − 𝔼[X] 𝔼[Y], nulle si X et Y sont indépendantes · **Type / plage :** réel · **Variable Python :** —

$$
z_i,\quad p_i
$$

**Sens :** score d'entrée et poids de sortie de la softmax · **Type / plage :** réel ; réel dans [0, 1] · **Variable Python :** `z`, `p`

$$
T
$$

**Sens :** température de la softmax (étape 2) ; ici T = √dₖ · **Type / plage :** réel > 0 · **Variable Python :** `T`

$$
\delta_{ik}
$$

**Sens :** vaut 1 si i = k, 0 sinon · **Type / plage :** 0 ou 1 · **Variable Python :** —

Sur les notations : la littérature écrit souvent αᵢⱼ pour les poids d'attention. Ce parcours écrit aᵢⱼ, parce que α y désigne le poids du score hybride (étape 23) ; un même symbole ne doit pas avoir deux sens. La softmax s'applique ligne par ligne, une ligne par requête.

## Démonstration

### 1. Les hypothèses, écrites en entier

On note

$$
\mathbf{q} = (q_1, \dots, q_{d_k}) ,
$$

$$
\mathbf{k} = (k_1, \dots, k_{d_k})
$$

et

$$
S = \sum_{l=1}^{d_k} q_l k_l .
$$

On suppose :

- **H1 (indépendance).** Les 2 dₖ composantes

$$
q_1, \dots, q_{d_k}, k_1, \dots, k_{d_k}
$$

sont des variables aléatoires indépendantes.
- **H2 (moyenne nulle).** Pour tout l,

$$
\mathbb{E}[q_l] = \mathbb{E}[k_l] = 0 .
$$

- **H3 (variance unité).** Pour tout l, Var(qₗ) = Var(kₗ) = 1.

L'ancienne version de ce fichier énonçait le résultat avec H2 et H3 seulement ; sans H1, il est faux (point 6). Ces hypothèses sont celles de la note de bas de page de Vaswani et al. (2017). Elles décrivent à peu près un modèle à l'initialisation, quand les poids sont tirés au hasard — le moment où l'entraînement démarre ou cale. Dans un modèle entraîné, les composantes ne sont plus indépendantes ; le facteur reste alors la convention d'échelle avec laquelle le modèle a appris.

### 2. L'espérance du produit scalaire est nulle

$$
\mathbb{E}[S] = \mathbb{E}\left[ \sum_{l=1}^{d_k} q_l k_l \right] = \sum_{l=1}^{d_k} \mathbb{E}[q_l k_l] = \sum_{l=1}^{d_k} \mathbb{E}[q_l]\, \mathbb{E}[k_l] = 0
$$

La deuxième égalité tient parce que l'espérance est linéaire, ce qui est vrai sans aucune hypothèse. La troisième tient parce que l'espérance d'un produit de deux variables indépendantes est le produit de leurs espérances (H1). La dernière tient parce que chaque espérance est nulle (H2).

### 3. Chaque terme a une variance 1

$$
\operatorname{Var}(q_l k_l) = \mathbb{E}\left[ q_l^2 k_l^2 \right] - \left( \mathbb{E}[q_l k_l] \right)^2 = \mathbb{E}\left[ q_l^2 \right] \mathbb{E}\left[ k_l^2 \right] - 0 = 1 \times 1 = 1
$$

La première égalité est la définition de la variance. La deuxième tient parce que qₗ² et kₗ² sont indépendantes, comme fonctions de variables indépendantes (H1), et parce que

$$
\mathbb{E}[q_l k_l] = 0
$$

(point 2). La troisième tient parce que

$$
\mathbb{E}[q_l^2] = \operatorname{Var}(q_l) + \mathbb{E}[q_l]^2 = 1 + 0 = 1
$$

(H2 et H3), et de même pour kₗ.

### 4. La somme a une variance dₖ

Pour une somme quelconque de variables Xₗ :

$$
\operatorname{Var}\left( \sum_{l=1}^{d_k} X_l \right) = \sum_{l=1}^{d_k} \operatorname{Var}(X_l) + \sum_{l \ne l'} \operatorname{Cov}(X_l, X_{l'})
$$

Avec Xₗ = qₗ kₗ, deux termes différents Xₗ et

$$
X_{l'}
$$

dépendent de composantes disjointes (qₗ et kₗ d'un côté,

$$
q_{l'}
$$

et

$$
k_{l'}
$$

de l'autre) ; ils sont donc indépendants (H1) et leur covariance est nulle. Il reste, avec le point 3 :

$$
\operatorname{Var}(S) = \sum_{l=1}^{d_k} \operatorname{Var}(q_l k_l) = \sum_{l=1}^{d_k} 1 = d_k
$$

L'écart-type du score brut vaut donc √dₖ : 4 pour dₖ = 16, 8 pour dₖ = 64, 16 pour dₖ = 256.

### 5. Après division par √dₖ, la variance vaut 1

$$
\operatorname{Var}\left( \frac{S}{\sqrt{d_k}} \right) = \frac{1}{\left( \sqrt{d_k} \right)^2} \operatorname{Var}(S) = \frac{d_k}{d_k} = 1
$$

L'égalité tient parce que Var(cX) = c² Var(X) pour toute constante c. Quelle que soit la dimension, les scores mis à l'échelle ont la même dispersion : la softmax travaille dans le même régime pour dₖ = 64 que pour dₖ = 128. Le programme le vérifie par Monte-Carlo sur 3 000 couples (𝐪, 𝐤) tirés au hasard : il estime des variances de 16,1, 62,9 et 131,0 pour dₖ = 16, 64 et 128, puis 1,008, 0,983 et 1,024 après division. Avec des composantes uniformes sur [−√3, √3], qui ont aussi une moyenne 0 et une variance 1, il trouve 61,1 pour dₖ = 64 : la loi exacte ne compte pas, seules H1 à H3 comptent. Ces nombres sont des estimations ; une autre graine les ferait varier de quelques pour cent.

### 6. Contre-exemple : sans indépendance, le résultat tombe

Prenons le cas extrême de dépendance, 𝐤 = 𝐪. Alors S = ∑ₗ qₗ² et

$$
\mathbb{E}[S] = \sum_l \mathbb{E}[q_l^2] = d_k ,
$$

et non 0. Pour des composantes gaussiennes,

$$
\mathbb{E}[q_l^4] = 3 ,
$$

donc Var(qₗ²) = 3 − 1 = 2 ; les qₗ² étant indépendants entre eux, Var(S) = 2 dₖ. Avec dₖ = 64, on attend une moyenne de 64 et une variance de 128 ; le programme estime 63,8 et 126,3. Énoncer « la variance vaut dₖ » sans l'hypothèse d'indépendance est donc faux en général : c'est la correction apportée à l'ancien texte.

### 7. Pourquoi une grande variance bloque l'apprentissage

L'étape 2 a établi la dérivée de la softmax, ∂ pᵢ / ∂ zₖ = pᵢ (δᵢₖ − pₖ). Sa diagonale vaut :

$$
\frac{\partial p_i}{\partial z_i} = p_i \,(1 - p_i) \qquad \text{qui tend vers 0 quand } p_i \to 1
$$

Quand un score domine, son poids pᵢ tend vers 1, donc pᵢ(1 − pᵢ) tend vers 0. Pour les autres clés, pₖ tend vers 0, donc pₖ(1 − pₖ) tend vers 0, et les termes croisés −pᵢ pₖ aussi. Toute la matrice des dérivées tend vers zéro : le gradient qui devrait remonter à travers la softmax jusqu'aux requêtes et aux clés s'évanouit, et l'apprentissage de ces poids s'arrête.

En chiffres, pour dₖ = 64 l'écart-type du score brut vaut 8. Deux clés séparées d'un écart-type ont, sans division, les scores [8 ; 0] : le poids de la première vaut 1/(1 + e⁻⁸) ≈ 0,99966 et la pente 0,000335. Avec la division par

$$
\sqrt{64} = 8 ,
$$

les scores deviennent [1 ; 0] : le poids vaut 1/(1 + e⁻¹) ≈ 0,73106 et la pente 0,19661, soit 586,5 fois plus. Sur des tirages aléatoires (une requête, 8 clés, dₖ = 64, 600 tirages), le plus grand poids vaut en moyenne 0,869 sans division et 0,356 avec : sans le facteur, l'attention est presque « tout sur une clé » dès le départ. La variante fautive qui divise par dₖ au lieu de √dₖ tombe dans l'excès inverse : la variance devient 1/dₖ, les scores sont presque égaux et le plus grand poids vaut en moyenne 0,148, à peine plus que le plancher 1/8 = 0,125 d'une distribution uniforme.

### 8. Ce que la formule implique pour un long contexte, et ce qu'elle n'implique pas

Elle implique la **dilution**. Les poids d'une ligne somment à 1 (étape 31, point 1) : une clé utile d'avance 2 sur ses concurrentes pèse e²/(e² + 3) ≈ 0,7112 parmi 4 clés, mais e²/(e² + 39) ≈ 0,1593 parmi 40.

Elle n'implique **aucun effet de position**. Placée en position 1, 20 ou 40 parmi 40 clés, la même clé utile pèse exactement 0,1593 à chaque fois, parce que le poids ne dépend que des scores et que la somme du dénominateur ne dépend pas de l'ordre de ses termes (étape 31, point 4). Le fait que des modèles entraînés exploitent souvent moins bien une information placée au milieu d'un long contexte qu'au début ou à la fin est un résultat **expérimental** (Liu et al., 2023, « Lost in the Middle ») ; ses causes tiennent à ce que le modèle a appris — encodage de position (étape 35), données et procédure d'entraînement — et font encore l'objet de recherches. L'introduction et la conclusion de l'ancienne version présentaient cet oubli comme une conséquence de la formule ; c'est faux, et la conséquence pratique est importante : l'effet de position se **mesure** sur le modèle visé, il ne se déduit pas.

### 9. L'algorithme sur un exemple fait à la main

Cet exemple vient d'un ancien fichier de formules du dossier, désormais fusionné ici ; son LaTeX était cassé (parenthèses orphelines dans la ligne des clés, blocs de formule centrés coupés au milieu d'une phrase) et qui s'arrêtait avant la sortie. Une requête 𝐪 = [1 ; 0], trois clés 𝐤₁ = [0,9 ; 0,1], 𝐤₂ = [0,1 ; 0,9], 𝐤₃ = [0,5 ; 0,5], des valeurs égales aux clés, et dₖ = 2.

1. Scores bruts : 𝐪 · 𝐤₁ = 0,9, 𝐪 · 𝐤₂ = 0,1, 𝐪 · 𝐤₃ = 0,5.
2. Mise à l'échelle par

$$
\sqrt{2} \approx 1{,}41421
$$

0,636, 0,071 et 0,354.
3. Softmax : e⁰,⁶³⁶⁴⁰ ≈ 1,88966, e⁰,⁰⁷⁰⁷¹ ≈ 1,07327, e⁰,³⁵³⁵⁵ ≈ 1,42412, de somme 4,38705 ; les poids valent 0,4307, 0,2446 et 0,3246.
4. Sortie, que l'ancien fichier ne calculait pas :

$$
\mathbf{o} = 0{,}4307\,\mathbf{k}_1 + 0{,}2446\,\mathbf{k}_2 + 0{,}3246\,\mathbf{k}_3 = [0{,}5744 ; 0{,}4256] .
$$

L'ancien fichier arrondissait chaque étape intermédiaire à trois décimales et obtenait 0,430 pour le premier poids ; arrondi correctement, 0,43074 donne 0,431. On garde ici quatre décimales sur le résultat et cinq sur les étapes.

## Effets et comportement

- **Sans le facteur, la dispersion des scores croît comme √dₖ.** Doubler la dimension multiplie la variance par 2 et rapproche la softmax de la saturation.
- **Avec le facteur, la dispersion ne dépend plus de la dimension.** C'est ce qui permet de garder la même softmax, sans retoucher sa température, dans des modèles de tailles très différentes.
- **Une division trop forte écrase tout.** Diviser par dₖ rend les poids presque uniformes : l'attention ne choisit plus rien (point 7).
- **La saturation tue le gradient.** La pente p(1−p) passe de 0,19661 à 0,000335 dans l'exemple : 586,5 fois moins de signal pour apprendre.
- **Le long contexte dilue, il ne « désavantage » pas une position.** La formule seule donne le même poids à la même clé où qu'elle soit (point 8).

## Algorithme détaillé (une seule requête)

1. Calculer les scores bruts : pour chaque clé j, sⱼ = 𝐪 · 𝐤ⱼ.
2. Mettre à l'échelle :

$$
s'_j = s_j / \sqrt{d_k} .
$$

3. Appliquer la softmax :

$$
p_j = e^{s'_j} / \sum_l e^{s'_l} .
$$

4. Calculer la sortie : 𝐨 = ∑ⱼ pⱼ 𝐯ⱼ.

En matrices, ces quatre étapes deviennent deux produits matriciels et une softmax par ligne, pour toutes les requêtes à la fois (étape 31).

## Du symbole au code Python

$$
\mathbf{q} \cdot \mathbf{k}
$$

**Variable ou fonction :** `produit_scalaire(q, k)`

**Symbole :** softmax à température T · **Variable ou fonction :** `softmax(z, T)`

**Symbole :** les quatre étapes de l'algorithme · **Variable ou fonction :** `attention_une_requete(q, K, V)`

**Symbole :** 𝔼[S] et Var(S), estimées · **Variable ou fonction :** `moyenne_variance(xs)`

**Symbole :** tirages de S sous H1 à H3 · **Variable ou fonction :** `tirer_produits(d_k, n, rng)`

$$
p\,(1 - p)
$$

**Variable ou fonction :** `pente_softmax(p)`

**Symbole :** moyenne du plus grand poids · **Variable ou fonction :** `poids_max_moyen(d_k, n_cles, n_tirages, rng, echelle)`

### Déroulé, ligne par ligne

**`produit_scalaire(q, k)`**. Elle refuse deux vecteurs de longueurs différentes (`ValueError`), puis renvoie `sum(a * b for a, b in zip(q, k))`. Pour `q = [1.0, 0.0]` et `k = [0.9, 0.1]`, cela donne 0,9.

**`softmax(z, T)`**. C'est la softmax de l'étape 2, avec température.

- `if T <= 0` : une température nulle ou négative n'a pas de sens ; `ValueError`.
- `exps = [math.exp((x - m) / T) for x in z]` : on retire le maximum `m` avant de diviser par `T`, ce qui ne change pas les poids et empêche tout débordement. Pour `z = [8.0, 0.0]` et `T = 1`, on obtient `[1.0, 0.000335]`, d'où les poids `[0.99966, 0.00034]`.

**`attention_une_requete(q, K, V)`**. Les quatre étapes de l'algorithme, numérotées en commentaire. Sur l'exemple : `bruts = [0.9, 0.1, 0.5]`, `mis_a_echelle` vaut environ `[0.636, 0.071, 0.354]`, `poids` environ `[0.4307, 0.2446, 0.3246]`, et `sortie` additionne, coordonnée par coordonnée, `p * v[c]` : `[0.5744, 0.4256]`.

**`moyenne_variance(xs)`**. Elle calcule la moyenne `m = sum(xs) / n`, puis la variance `sum((x - m) ** 2 for x in xs) / (n - 1)`. Le diviseur N − 1 donne une estimation sans biais ; avec N = 3 000, il ne diffère de N que de 0,033 %. Elle refuse moins de deux tirages.

**`tirer_produits(d_k, n, rng, loi, k_egal_q)`**. Elle tire `n` couples `(q, k)` dont chaque composante est un nouvel appel au générateur, donc indépendante des autres (H1), de moyenne 0 et de variance 1 (H2, H3).

- `rng.gauss(0.0, 1.0)` tire selon une loi normale ; `rng.uniform(-a, a)` avec `a = math.sqrt(3)` tire selon une loi uniforme de variance

$$
(2\sqrt{3})^2/12 = 1 .
$$

- `k = q if k_egal_q else [...]` : avec `k_egal_q=True`, la clé est la même liste que la requête, c'est le contre-exemple du point 6.

**`pente_softmax(p)`** renvoie `p * (1 - p)`, la diagonale de la dérivée de la softmax.

**`poids_max_moyen(d_k, n_cles, n_tirages, rng, echelle)`**. À chaque tirage, elle crée une requête et `n_cles` clés aléatoires, divise les scores bruts par `echelle` (1 pour « sans division », 8 pour √64, 64 pour la variante fautive), applique la softmax et garde le plus grand poids ; elle renvoie la moyenne sur les tirages.

**`main()`**, bloc par bloc.

1. L'exemple du point 9 : les `assert` vérifient les scores arrondis `[0.636, 0.071, 0.354]`, les poids `[0.4307, 0.2446, 0.3246]`, leur arrondi correct à trois décimales `[0.431, 0.245, 0.325]` (et non 0,430), puis la sortie `[0.5744, 0.4256]`.
2. `rng = random.Random(2026)` crée un générateur privé à graine fixe : les mêmes tirages à chaque exécution, donc une sortie reproductible. Pour chaque dₖ, 3 000 produits donnent une moyenne et une variance. Les `assert` exigent une moyenne à moins de 4 écarts-types √(dₖ / N) de 0, et une variance à moins de 10 % de dₖ, puis de 1 après division. La tolérance est large devant la fluctuation attendue (environ 3 %) : le test n'échoue que si la théorie ou le code est faux, par exemple si l'on oublie la division.
3. Le contre-exemple 𝐤 = 𝐪 donne une moyenne de 63,8 et une variance de 126,3, vérifiées à 1 près de 64 et à 10 % près de 128.
4. Les poids 0,99966 et 0,73106, les pentes 0,000335 et 0,19661 et leur rapport 586,5 du point 7.
5. Les moyennes du plus grand poids sur 600 tirages : 0,869 sans division, 0,356 avec √64, 0,148 avec 64, toujours au moins égale à 1/8.
6. La même clé utile placée en position 1, 20 ou 40 parmi 40 reçoit `[0.1593, 0.1593, 0.1593]` : aucun effet de position (point 8).
7. Les nombres des cas d'usage : 0,28 pour 20 clés au lieu de 40, les poids et les estimations des comparables immobiliers, les probabilités d'alerte 0,9756 et 0,8214.
8. Deux entrées invalides doivent lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`produit_scalaire(q, k)`** — Comme un contrôleur qui s'assure que deux bordereaux comptent le même nombre de lignes avant de les comparer, cette fonction reçoit une requête q et une clé k, et lève une `ValueError` si leurs longueurs diffèrent, car un produit scalaire n'a de sens qu'entre deux vecteurs de même dimension dₖ. Sinon, elle multiplie les coordonnées deux à deux, additionne ces produits et renvoie ce seul nombre, le score brut de l'étape 1 : 0,9 pour q = `[1.0, 0.0]` et k = `[0.9, 0.1]`. Tout le reste du programme, de l'attention aux tirages de Monte-Carlo, repose sur ce petit geste répété des milliers de fois.

**`softmax(z, T)`** — On peut l'imaginer en arbitre chargé de répartir cent pour cent de l'attention entre des candidats selon leurs scores : elle reçoit la liste z des scores et une température T, qui vaut 1 par défaut, et refuse par une `ValueError` toute température nulle ou négative. Elle retranche d'abord le plus grand score à chacun, divise par T, prend l'exponentielle de chaque terme et le divise par la somme de tous, si bien que les poids renvoyés sont positifs, totalisent 1 et ne débordent jamais. Le programme s'en sert pour l'étape 3 de l'attention, pour mesurer la saturation (0,99966 pour les scores `[8.0, 0.0]`, 0,73106 après division par 8) et pour pondérer les comparables immobiliers à T = 1 puis T = 0,05.

**`attention_une_requete(q, K, V)`** — Cette fonction met en scène une lectrice qui pose une question à une bibliothèque : elle reçoit la requête q, la liste K des clés et la liste V des valeurs, puis enchaîne les quatre étapes de l'algorithme, en calculant le score brut de q avec chaque clé par `produit_scalaire`, en divisant chaque score par √dₖ, en changeant ces scores en poids par `softmax`, enfin en additionnant les valeurs pondérées coordonnée par coordonnée. Elle renvoie les quatre résultats à la fois, scores bruts, scores mis à l'échelle, poids et sortie, pour que `main` puisse contrôler chacun : sur l'exemple, les scores `[0.9, 0.1, 0.5]` deviennent environ `[0.636, 0.071, 0.354]`, puis les poids `[0.4307, 0.2446, 0.3246]` et la sortie `[0.5744, 0.4256]`.

**`tirer_produits(d_k, n, rng, loi, k_egal_q)`** — C'est le croupier de l'expérience de Monte-Carlo : elle reçoit la dimension dₖ, le nombre n de tirages, le générateur `rng`, le nom de la loi (gaussienne par défaut, ou uniforme sur [−√3 ; √3], de variance 1 elle aussi) et un drapeau `k_egal_q`. Pour chacun des n tirages, elle fabrique une requête de dₖ coordonnées indépendantes, de moyenne 0 et de variance 1, puis une clé tirée de la même façon, ou bien, si le drapeau est levé, la requête elle-même, ce qui casse volontairement l'indépendance ; elle renvoie la liste des n produits scalaires et lève une `ValueError` si la loi demandée est inconnue. `main` lui en demande 3 000 par dimension pour constater que la variance vaut environ dₖ, puis s'en sert pour le contre-exemple k = q, où la moyenne approche 64 et la variance 128.

**`pente_softmax(p)`** — Cette petite fonction est le thermomètre du gradient : elle reçoit un poids p sorti de la softmax et renvoie p (1 − p), la dérivée de ce poids par rapport à son propre score, c'est-à-dire la pente par laquelle le signal d'apprentissage peut encore remonter. Plus p s'approche de 1, plus cette pente s'écrase vers 0 : `main` l'utilise pour montrer qu'elle tombe à 0,000335 quand le poids sature à 0,99966 sans division, alors qu'elle vaut 0,19661 pour un poids de 0,73106 après division par √64, soit une pente 586,5 fois plus grande.

**`main()`** — C'est le metteur en scène qui fait jouer, dans l'ordre, les huit tableaux du fichier en confrontant chaque nombre imprimé à un `assert` : il déroule l'attention sur l'exemple q = [1, 0] avec trois clés, lance avec un générateur à graine fixe 2026 les tirages de Monte-Carlo pour dₖ = 16, 64 et 128 puis le contre-exemple k = q, mesure la saturation et la pente de la softmax, compare le plus grand poids moyen sans division, avec √64 et avec 64, vérifie que la position d'une clé utile parmi 40 ne change rien (0,1593 partout), recalcule les nombres des cas d'usage et s'assure que deux entrées invalides lèvent bien une `ValueError`. Il ne renvoie rien ; sa dernière ligne n'annonce que toutes les vérifications sont passées que si aucun `assert` n'a échoué.

```python
"""Étape 32 — pourquoi diviser par √d_k : variance du produit scalaire, saturation de la softmax, dilution."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

N_TIRAGES = 3000


def produit_scalaire(q: list[float], k: list[float]) -> float:
    if len(q) != len(k):
        raise ValueError("q et k doivent avoir la même dimension d_k")
    return sum(a * b for a, b in zip(q, k))


def softmax(z: list[float], T: float = 1.0) -> list[float]:
    """Softmax stable à température T (étape 2)."""
    if T <= 0:
        raise ValueError("la température doit être > 0")
    m = max(z)
    exps = [math.exp((x - m) / T) for x in z]
    total = sum(exps)
    return [e / total for e in exps]


def attention_une_requete(q: list[float], K: list[list[float]], V: list[list[float]]):
    """Les quatre étapes de l'algorithme : scores bruts, mise à l'échelle, softmax, moyenne pondérée."""
    d_k = len(q)
    bruts = [produit_scalaire(q, k) for k in K]                                    # 1. s_j = q · k_j
    mis_a_echelle = [s / math.sqrt(d_k) for s in bruts]                           # 2. s'_j = s_j / √d_k
    poids = softmax(mis_a_echelle)                                                # 3. p_j
    sortie = [sum(p * v[c] for p, v in zip(poids, V)) for c in range(len(V[0]))]  # 4. o = Σ p_j v_j
    return bruts, mis_a_echelle, poids, sortie


def moyenne_variance(xs: list[float]) -> tuple[float, float]:
    """Moyenne et variance empiriques (diviseur N − 1)."""
    n = len(xs)
    if n < 2:
        raise ValueError("il faut au moins deux tirages")
    m = sum(xs) / n
    return m, sum((x - m) ** 2 for x in xs) / (n - 1)


def tirer_produits(d_k: int, n: int, rng: random.Random, loi: str = "gauss", k_egal_q: bool = False) -> list[float]:
    """n produits q · k ; composantes indépendantes, de moyenne 0 et de variance 1, sauf si k_egal_q."""
    a = math.sqrt(3)  # la loi uniforme sur [−√3, √3] a une variance (2√3)² / 12 = 1
    if loi == "gauss":
        tirer = lambda: rng.gauss(0.0, 1.0)
    elif loi == "uniforme":
        tirer = lambda: rng.uniform(-a, a)
    else:
        raise ValueError("loi inconnue")
    produits = []
    for _ in range(n):
        q = [tirer() for _ in range(d_k)]
        k = q if k_egal_q else [tirer() for _ in range(d_k)]
        produits.append(produit_scalaire(q, k))
    return produits


def pente_softmax(p: float) -> float:
    """∂p_i/∂z_i = p_i (1 − p_i) : la pente par laquelle le gradient remonte (étape 2)."""
    return p * (1 - p)


def poids_max_moyen(d_k: int, n_cles: int, n_tirages: int, rng: random.Random, echelle: float) -> float:
    """Moyenne, sur des tirages aléatoires, du plus grand poids d'attention d'une requête."""
    total = 0.0
    for _ in range(n_tirages):
        q = [rng.gauss(0.0, 1.0) for _ in range(d_k)]
        scores = [produit_scalaire(q, [rng.gauss(0.0, 1.0) for _ in range(d_k)]) / echelle for _ in range(n_cles)]
        total += max(softmax(scores))
    return total / n_tirages


def main() -> None:
    print("1. L'algorithme sur l'exemple : q = [1, 0], trois clés, V = K")
    K = [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]]
    bruts, s, p, o = attention_une_requete([1.0, 0.0], K, K)
    print(f"  scores bruts = {[round(x, 4) for x in bruts]} ; après √2 = {[round(x, 3) for x in s]}")
    print(f"  poids = {[round(x, 4) for x in p]} ; sortie = {[round(x, 4) for x in o]}")
    assert [round(x, 3) for x in s] == [0.636, 0.071, 0.354]
    assert [round(x, 4) for x in p] == [0.4307, 0.2446, 0.3246] and [round(x, 3) for x in p] == [0.431, 0.245, 0.325]
    assert [round(x, 4) for x in o] == [0.5744, 0.4256] and abs(sum(p) - 1) < 1e-12

    rng = random.Random(2026)
    print(f"2. Monte-Carlo, {N_TIRAGES} tirages : Var(q·k) ≈ d_k, puis Var(q·k / √d_k) ≈ 1")
    for d_k in (16, 64, 128):
        prods = tirer_produits(d_k, N_TIRAGES, rng)
        m, v = moyenne_variance(prods)
        _, v_ech = moyenne_variance([x / math.sqrt(d_k) for x in prods])
        print(f"  gauss    d_k = {d_k:>3} : moyenne = {m:+.2f}  variance = {v:6.1f}  après division : {v_ech:.3f}")
        assert abs(m) < 4 * math.sqrt(d_k / N_TIRAGES)  # 4 écarts-types de la moyenne empirique
        assert abs(v / d_k - 1) < 0.1 and abs(v_ech - 1) < 0.1
    prods = tirer_produits(64, N_TIRAGES, rng, loi="uniforme")
    m, v = moyenne_variance(prods)
    print(f"  uniforme d_k =  64 : moyenne = {m:+.2f}  variance = {v:6.1f}  (la loi exacte ne compte pas)")
    assert abs(m) < 4 * math.sqrt(64 / N_TIRAGES) and abs(v / 64 - 1) < 0.1

    print("3. Contre-exemple sans indépendance : k = q, d_k = 64")
    m, v = moyenne_variance(tirer_produits(64, N_TIRAGES, rng, k_egal_q=True))
    print(f"  moyenne = {m:.1f} (théorie 64) ; variance = {v:.1f} (théorie 2 × 64 = 128)")
    assert abs(m - 64) < 1.0 and abs(v / 128 - 1) < 0.1

    print("4. Saturation : deux clés séparées d'un écart-type, d_k = 64 (écart-type √64 = 8)")
    p_brut, p_ech = softmax([8.0, 0.0])[0], softmax([8.0 / 8, 0.0])[0]
    print(f"  sans division : p = {p_brut:.5f}  pente p(1 − p) = {pente_softmax(p_brut):.6f}")
    print(f"  avec division : p = {p_ech:.5f}  pente p(1 − p) = {pente_softmax(p_ech):.5f}")
    rapport = pente_softmax(p_ech) / pente_softmax(p_brut)
    print(f"  la pente est {rapport:.1f} fois plus grande avec le facteur d'échelle")
    assert round(p_brut, 5) == 0.99966 and round(pente_softmax(p_brut), 6) == 0.000335
    assert round(p_ech, 5) == 0.73106 and round(pente_softmax(p_ech), 5) == 0.19661
    assert round(rapport, 1) == 586.5

    print("5. Poids maximal moyen d'une requête face à 8 clés aléatoires, d_k = 64 (600 tirages)")
    sans = poids_max_moyen(64, 8, 600, rng, echelle=1.0)
    avec = poids_max_moyen(64, 8, 600, rng, echelle=8.0)
    trop = poids_max_moyen(64, 8, 600, rng, echelle=64.0)
    print(f"  sans division : {sans:.3f} ; divisé par √64 : {avec:.3f} ; divisé par 64 : {trop:.3f}")
    assert sans > 0.8 and avec < 0.5 and 1 / 8 <= trop < 0.2  # 1/8 : le poids maximal ne descend jamais sous 1/n

    print("6. Dilution sans effet de position : la clé utile (avance 2) en position 1, 20 ou 40 parmi 40")
    poids_par_position = []
    for position in (1, 20, 40):
        scores = [0.0] * 40
        scores[position - 1] = 2.0
        poids_par_position.append(softmax(scores)[position - 1])
    print(f"  poids de la clé utile = {[round(x, 4) for x in poids_par_position]}")
    assert all(abs(x - math.exp(2) / (math.exp(2) + 39)) < 1e-12 for x in poids_par_position)
    assert round(poids_par_position[0], 4) == 0.1593

    print("7. Nombres des cas d'usage")
    assert round(math.exp(2) / (math.exp(2) + 19), 4) == 0.28  # 20 clés au lieu de 40
    prix = [1450.0, 1520.0, 1700.0]
    for T, poids_att, estim_att in ((1.0, [0.3556, 0.3383, 0.3061], 1550.2), (0.05, [0.7054, 0.2595, 0.0351], 1476.9)):
        w = softmax([0.95, 0.90, 0.80], T)
        estimation = sum(a * b for a, b in zip(w, prix))
        print(f"  comparables, T = {T} : poids = {[round(x, 4) for x in w]}  estimation = {estimation:.1f} AED/sqft")
        assert [round(x, 4) for x in w] == poids_att and round(estimation, 1) == estim_att
        assert min(prix) <= estimation <= max(prix)  # combinaison convexe (étape 31)
    for T, p_max in ((1.0, 0.9756), (2.0, 0.8214)):
        assert round(softmax([6.0, 2.0, 1.0], T)[0], 4) == p_max

    print("8. Entrées invalides refusées")
    for appel in (lambda: produit_scalaire([1.0], [1.0, 2.0]), lambda: softmax([1.0], T=0.0)):
        try:
            appel()
        except ValueError as e:
            print(f"  ValueError : {e}")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. L'algorithme sur l'exemple : q = [1, 0], trois clés, V = K
  scores bruts = [0.9, 0.1, 0.5] ; après √2 = [0.636, 0.071, 0.354]
  poids = [0.4307, 0.2446, 0.3246] ; sortie = [0.5744, 0.4256]
2. Monte-Carlo, 3000 tirages : Var(q·k) ≈ d_k, puis Var(q·k / √d_k) ≈ 1
  gauss    d_k =  16 : moyenne = +0.12  variance =   16.1  après division : 1.008
  gauss    d_k =  64 : moyenne = +0.12  variance =   62.9  après division : 0.983
  gauss    d_k = 128 : moyenne = +0.08  variance =  131.0  après division : 1.024
  uniforme d_k =  64 : moyenne = +0.14  variance =   61.1  (la loi exacte ne compte pas)
3. Contre-exemple sans indépendance : k = q, d_k = 64
  moyenne = 63.8 (théorie 64) ; variance = 126.3 (théorie 2 × 64 = 128)
4. Saturation : deux clés séparées d'un écart-type, d_k = 64 (écart-type √64 = 8)
  sans division : p = 0.99966  pente p(1 − p) = 0.000335
  avec division : p = 0.73106  pente p(1 − p) = 0.19661
  la pente est 586.5 fois plus grande avec le facteur d'échelle
…
  sans division : 0.869 ; divisé par √64 : 0.356 ; divisé par 64 : 0.148
…
  poids de la clé utile = [0.1593, 0.1593, 0.1593]
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la variance dₖ n'est pas une affirmation à croire, c'est un calcul de quatre lignes sous trois hypothèses, que 3 000 tirages confirment et qu'un seul contre-exemple suffit à faire tomber quand on retire l'indépendance.

### La même chose avec NumPy

La version NumPy du fichier d'origine, corrigée et complétée d'un Monte-Carlo vectorisé, en extrait :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(x)`** — Dans cette version NumPy, le même arbitre répartit l'attention sur un tableau entier d'un seul geste : la fonction reçoit le tableau x des scores, retranche son maximum pour la stabilité numérique, prend l'exponentielle de chaque case, puis divise par la somme afin de renvoyer un tableau de poids positifs qui totalisent 1. Contrairement à la version en Python pur du programme précédent, elle n'a pas de paramètre de température et ne vérifie aucune entrée ; elle sert uniquement à l'étape softmax de `attention_une_requete`, juste en dessous.

**`attention_une_requete(q, K, V)`** — C'est la même lectrice que dans le programme précédent, mais elle consulte toute la bibliothèque en une seule multiplication matricielle : elle reçoit la requête q de forme (dₖ,), la matrice K des clés et la matrice V des valeurs, calcule tous les scores d'un coup par `K @ q`, les divise par √dₖ, les passe à `softmax`, puis renvoie directement la sortie `poids @ V`, sans conserver les étapes intermédiaires. Sur l'exemple q = [1, 0] avec trois clés et des valeurs égales aux clés, elle doit afficher environ `[0.5744 0.4256]`, comme l'annonce le commentaire, avant que le script ne vérifie sur 100 000 couples que la variance passe d'environ 64 à environ 1.

```python
# [extrait] — version NumPy, non exécutée par le harnais (NumPy n'est pas dans la bibliothèque standard)
import numpy as np


def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x))                  # stabilité numérique
    return e_x / e_x.sum()


def attention_une_requete(q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
    """q : (d_k,) ; K : (n_k, d_k) ; V : (n_k, d_v)."""
    d_k = q.shape[0]
    poids = softmax(K @ q / np.sqrt(d_k))
    return poids @ V


q = np.array([1.0, 0.0])
K = np.array([[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]])
print(attention_une_requete(q, K, K.copy()))     # environ [0.5744 0.4256]

rng = np.random.default_rng(2026)                # 100 000 couples (q, k) en dimension 64
Qr, Kr = rng.standard_normal((2, 100_000, 64))
s = (Qr * Kr).sum(axis=1)
print(s.var(), (s / 8).var())                    # environ 64 et 1
```

## Squelette algorithmique

Le programme de ce fichier fait deux choses : il calcule l'attention pour une requête, et il vérifie par simulation pourquoi on divise les scores par √dₖ. Le second algorithme est une expérience de Monte-Carlo : tirer de nombreux vecteurs aléatoires et mesurer la variance de leurs produits scalaires.

```text
ALGORITHME AttentionUneRequête
ENTRÉES : requête q, clés k₁ … k_n, valeurs v₁ … v_n, température T (√dₖ par défaut)
SORTIE  : sortie o et poids a

  POUR j DE 1 À n FAIRE  zⱼ ← (q · kⱼ) / T  FIN POUR
  a ← Softmax(z)                                  (avec le maximum retranché)
  o ← Σⱼ aⱼ × vⱼ
  RETOURNER o, a

ALGORITHME VérifierLaVariance
ENTRÉES : dimension dₖ, nombre de tirages N, loi des coordonnées (gaussienne ou uniforme sur [−√3 ; √3])
SORTIE  : moyenne et variance de q · k, avant et après division par √dₖ

  POUR i DE 1 À N FAIRE
      tirer q et k, coordonnées indépendantes de moyenne 0 et de variance 1
      xᵢ ← q · k
  FIN POUR
  RETOURNER moyenne(x), variance(x), variance(x / √dₖ)          (attendus : 0, dₖ, 1)

ALGORITHME EffetDeSaturation
  POUR CHAQUE échelle ∈ {1, √dₖ} FAIRE
      moyenne, sur des tirages, du plus grand poids de la softmax des scores divisés par l'échelle
  FIN POUR
  sans division, ce poids s'approche de 1 et la pente p (1 − p) de la softmax s'approche de 0
```

**Complexité.** L'attention d'une requête coûte O(n × dₖ) pour les scores, O(n) pour la softmax et O(n × d_v) pour la sortie. La vérification de variance coûte O(N × dₖ) tirages et produits, et l'expérience de saturation O(tirages × n_clés × dₖ). Ces simulations ne servent qu'à vérifier la démonstration : en production, la division par √dₖ ne coûte qu'une multiplication par score.

**Du squelette au code.** `AttentionUneRequête` correspond à `attention_une_requete`, avec `produit_scalaire` et `softmax`. `VérifierLaVariance` correspond à `tirer_produits` (et à son option `k_egal_q`, qui casse l'indépendance pour le contre-exemple du point 6) suivi de `moyenne_variance`. `EffetDeSaturation` correspond à `poids_max_moyen` et à `pente_softmax`, qui donne la pente p (1 − p) par laquelle le gradient remonte.

## Cas d'usage réels aux Émirats

Les volumes, les montants non réglementaires et les seuils internes ci-dessous sont illustratifs ; les nombres calculés par une formule sont vérifiés par le programme (bloc 7).

### RH — l'exception DIFC du message 12

Un cabinet RH multi-émirats accompagne la nouvelle recrue de l'introduction sur une conversation de 40 messages : passeport, contrat, question sur l'indemnité de fin de service, puis, au message 12, la précision que son employeur est une entité de la DIFC. Cette précision change le calcul : le barème du décret-loi fédéral 33/2021 (21 jours de salaire de base par année de service les cinq premières années, 30 jours au-delà) ne s'applique pas dans la DIFC, qui a son propre régime d'épargne, le DEWS. Dans le modèle simplifié, une phrase d'avance 2 pèse 0,1593 parmi 40, qu'elle soit au message 1, 20 ou 40 : si l'agent manque l'exception plus souvent au message 12 qu'au message 40, ce n'est pas la formule qui l'explique, mais un effet de position appris par le modèle, qu'il faut mesurer. L'équipe fait donc deux choses : un outil `regime_fin_de_service(employeur)` détermine le régime dès que l'employeur est connu et l'écrit dans un bloc « Faits établis » réinjecté à chaque tour, et un jeu de tests place la même exception au début, au milieu et à la fin de conversations de 40 messages. Le bloc réduit la dilution et rend la réponse indépendante de la position ; les tests vérifient que c'est bien le cas sur le modèle utilisé. Sans ce travail, le récapitulatif peut annoncer une indemnité calculée sur le mauvais régime, ce que la recrue ne découvrira qu'à son départ. L'indicateur suivi est le taux de récapitulatifs qui citent le bon régime, ventilé par position de l'exception.

### Secteur public — le même document en arabe et en anglais

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais sur les démarches administratives. Son retriever renvoyait les deux versions linguistiques de chaque fiche, si bien que 20 fiches utiles occupaient 40 blocs du contexte. Deux versions d'une même fiche ont des clés très proches pour une question donnée : elles obtiennent des scores voisins et se partagent le poids, et chaque fiche différente affronte deux fois plus de concurrents. L'équipe ne garde que la version dans la langue de la question, après normalisation de l'arabe (alef, ta marbuta, diacritiques), et passe de 40 à 20 blocs : dans le modèle simplifié, la clé utile d'avance 2 passe de 0,1593 à 0,2800, et le calcul de l'attention sur cette partie du prompt est divisé par 4. La version écartée reste accessible par un outil si l'usager change de langue en cours de session. Sans ce dédoublonnage, chaque réponse coûte deux fois plus de tokens et mélange parfois les formulations des deux versions ; et comme le contexte transporte des données personnelles, garder moins de texte sert aussi la minimisation des données qu'exige la PDPL. L'indicateur suivi est la justesse des réponses sur un jeu de questions bilingues, avec le nombre moyen de tokens par réponse.

### Banque — une couche d'attention réécrite sans le facteur d'échelle

L'équipe data d'une banque de détail de Dubaï entraîne un petit modèle Transformer interne qui classe les libellés de transactions, en arabe et en anglais, pour le contrôle anti-blanchiment. Pour l'exécuter sur ses propres serveurs, un développeur réécrit la couche d'attention et oublie la division par √dₖ, avec dₖ = 64. Dès l'initialisation, les scores ont un écart-type de 8 au lieu de 1 : deux clés séparées d'un écart-type reçoivent les poids 0,99966 et 0,00034, et la pente p(1−p) qui transmet le gradient tombe à 0,000335 au lieu de 0,19661, soit 586,5 fois moins. La perte ne descend presque plus, et l'équipe peut perdre des jours à soupçonner les données ou le taux d'apprentissage. Le correctif tient en une ligne, mais la vraie leçon est un test : la couche réécrite est comparée, sur des entrées fixes, à une implémentation de référence comme celle de l'étape 31, et un second test vérifie par Monte-Carlo que la variance des scores mis à l'échelle reste proche de 1 à l'initialisation. Sans ces tests, une erreur de ce type peut atteindre la production si le modèle finit par apprendre quand même, mais moins bien, et un classement anti-blanchiment dégradé se voit rarement avant un audit. L'indicateur suivi est la norme du gradient des matrices

$$
W_Q
$$

et

$$
W_K
$$

(étape 33) pendant les premiers pas d'entraînement, comparée à celle de la référence.

### Immobilier — une moyenne pondérée de comparables, avec une température à choisir

Une agence et un promoteur à Dubaï et Abu Dhabi estiment le prix d'un appartement par une moyenne de ventes comparables pondérée par softmax : c'est une attention à une seule requête, codée cette fois par le développeur lui-même. La requête est l'embedding du bien à estimer, les clés sont les embeddings des comparables, les valeurs sont leurs prix en AED/sqft, et les poids valent softmax(cos / T). Avec trois comparables de similarités 0,95, 0,90 et 0,80 et de prix 1 450, 1 520 et 1 700 AED/sqft, une température T = 1 donne des poids presque uniformes, 0,3556, 0,3383 et 0,3061, et une estimation de 1 550,2 AED/sqft qui ne distingue presque pas le bien le plus proche du plus éloigné. Les cosinus ne s'écartent que de 0,15 entre eux, ce qui est minuscule à l'échelle de T = 1 ; avec T = 0,05, les scores divisés deviennent 19, 18 et 16, les poids 0,7054, 0,2595 et 0,0351, et l'estimation 1 476,9 AED/sqft. C'est le raisonnement de √dₖ appliqué à la main : on choisit l'échelle pour que les scores divisés s'écartent d'environ une unité, ni écrasés (poids uniformes), ni démesurés (un seul comparable). Quel que soit T, l'estimation reste entre le plus petit et le plus grand prix, parce que c'est une combinaison convexe (étape 31, point 2). L'indicateur suivi est l'écart médian entre l'estimation et le prix de vente final, qui sert aussi à régler T sur l'historique des transactions enregistrées au DLD.

### Crypto — des probabilités d'alerte trop sûres d'elles

Une plateforme d'actifs virtuels agréée par la VARA classe ses alertes de liquidité en trois catégories — incident, maintenance, bruit — avec un modèle qui sort trois logits, par exemple [6 ; 2 ; 1]. La softmax donne 0,9756 à « incident », et la règle d'escalade envoie directement à l'astreinte toute alerte au-dessus de 0,9. En comparant ces probabilités à l'historique, l'équipe constate que les alertes annoncées vers 0,97 sont des incidents bien moins souvent que ce chiffre ne le promet : le modèle est trop sûr de lui, comme une attention saturée. Elle applique la même idée que le facteur d'échelle : diviser les logits par une température T réglée sur un jeu de validation (calibration par température) ; avec T = 2, la même alerte passe à 0,8214 et part en revue humaine au lieu de l'escalade automatique. Le classement des catégories ne change pas, parce que diviser par T > 0 conserve l'ordre des logits ; seule la confiance affichée change. Sans calibration, l'astreinte reçoit des escalades qui n'auraient pas dû l'être et finit par les ignorer, ce qui affaiblit la surveillance que l'agrément exige. L'indicateur suivi est l'écart de calibration : pour chaque tranche de probabilité annoncée, l'écart entre cette probabilité et la fréquence réelle des incidents.

### BTP — mesurer l'effet de position au lieu de le supposer

Un groupe de construction à Dubaï fait extraire par un agent les clauses de retenue de garantie et de TVA à 5 % dans des contrats de sous-traitance d'environ 80 pages. Avant de choisir entre « contrat entier dans le prompt » et « clauses récupérées », l'équipe mesure l'effet de position sur le modèle qu'elle utilise : elle place la même clause de retenue au début, au milieu et à la fin de 50 contrats, soit 150 tests, et compte les extractions correctes à chaque position. Elle sait que la formule ne prédit aucun effet de position (point 8) : si un écart apparaît, il vient du modèle et peut changer à chaque nouvelle version, d'où un test à rejouer à chaque changement de modèle. Si le taux d'extraction au milieu est nettement plus bas, l'équipe passe à la récupération des clauses (étape 23) et les place près des lignes de la facture ; sinon, elle garde le contrat entier, plus simple à auditer. Pour juger si un écart entre deux positions est réel ou dû au hasard, elle calcule un intervalle de Wilson (étape 7) sur chaque taux mesuré avec 50 contrats. Sans cette mesure, le choix reposerait sur une intuition ou sur un article qui ne porte pas sur son modèle ni sur ses documents. L'indicateur suivi est le taux d'extraction correcte par position, rejoué à chaque changement de modèle.

## Pièges et limites

- **Oublier l'hypothèse d'indépendance.** Var(𝐪 · 𝐤) = dₖ ne vaut que sous H1 à H3 ; avec 𝐤 = 𝐪, la moyenne vaut déjà dₖ (point 6).
- **Diviser par dₖ au lieu de √dₖ.** La variance tombe à 1/dₖ et les poids deviennent presque uniformes : le plus grand poids vaut en moyenne 0,148 pour 8 clés, contre un plancher de 0,125.
- **Attribuer l'oubli du milieu à la formule.** La formule implique la dilution, pas un effet de position ; celui-ci se mesure sur le modèle visé, et se remesure quand le modèle change.
- **Croire que le facteur règle tout.** Il fixe l'échelle au départ ; pendant l'entraînement, les normes des requêtes et des clés peuvent grandir et l'attention saturer quand même, ce qui conduit certaines architectures à normaliser aussi 𝐪 et 𝐤.
- **Prendre la simulation pour une preuve.** Le Monte-Carlo vérifie un résultat démontré ; il ne le démontre pas. Ses estimations fluctuent de quelques pour cent, d'où les tolérances de 10 % des `assert`.

### Exercice feuille blanche

1. Sans regarder, refaire la démonstration de Var(𝐪 · 𝐤) = dₖ en citant, à chaque égalité, l'hypothèse utilisée (H1, H2 ou H3).
2. Prédire, puis vérifier avec `tirer_produits` modifiée : si les composantes ont une variance σ² au lieu de 1, que vaut Var(𝐪 · 𝐤), et par quoi faut-il diviser ? (Réponse : dₖ σ⁴, donc diviser par σ² √dₖ.)
3. Trouver le bug : `mis_a_echelle = [s / d_k for s in bruts]`. Quelle est la variance des scores pour dₖ = 64, et que deviennent les poids ? (Réponse : 1/64 ; ils deviennent presque uniformes.)

## À retenir

La formule d'attention explique deux comportements des LLM face à un long contexte : la **dilution**, parce que les poids somment à 1, et le **coût quadratique** (étape 31). Le facteur √dₖ, lui, garde les scores à variance 1 sous les hypothèses d'indépendance, de moyenne nulle et de variance unité, ce qui évite la saturation de la softmax et l'arrêt de l'apprentissage. L'« oubli du milieu » n'est pas une conséquence de la formule : c'est un effet observé, à mesurer sur le modèle visé. Les stratégies d'ingénierie de contexte — compaction, récupération sélective, bloc de faits établis, mémoire externe — répondent à la dilution et évitent de dépendre de la position.

## Pour aller plus loin

Le découpage en têtes, où

$$
d_k = d_{model}/h ,
$$

est l'objet de l'étape 34. L'étude « Lost in the Middle » (Liu et al., 2023) décrit le protocole de mesure de l'effet de position ; les tests « aiguille dans une botte de foin » en sont une version simplifiée. La calibration par température (Guo et al., 2017) généralise le cas crypto : une seule constante, réglée sur un jeu de validation, corrige la confiance excessive d'un classifieur sans changer ses décisions de classement.

> Suite : [Transformer et attention](<33-Transformer-et-Attention-Deroule-Numerique.md>) — étape 33.
