# Étape 76 — Régularisation L1 (Lasso) et L2 (Ridge)

> Étape 76 du parcours · Prérequis : [Mini-lots et généralisation](<75b-Mini-Lots-et-Generalisation.md>) · Suite : [Projet final : un agent depuis une feuille blanche](<../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>)

## Définition

La régularisation ajoute à la perte un prix pour les poids grands, payé à chaque pas d'entraînement, que l'exemple soit bien prédit ou non. La pénalité **L2** (*Ridge*) vaut λ/2 fois la somme des carrés des poids : sa dérivée λw retire à chaque pas une **fraction** du poids, si bien que les poids rapetissent sans jamais devenir exactement nuls. La pénalité **L1** (*Lasso*) vaut λ fois la somme des valeurs absolues : elle retire une **quantité constante**, et peut mettre un poids exactement à zéro, ce qui sélectionne les entrées utiles. Cette propriété demande le bon algorithme : une descente de sous-gradient fait osciller le poids autour de zéro sans l'atteindre ; il faut un pas **proximal**, le seuillage doux, démontré plus bas. **Elastic net** additionne les deux pénalités. La **décroissance des poids** (*weight decay*) multiplie chaque poids par un facteur un peu inférieur à 1 à chaque pas ; elle équivaut à L2 pour la descente de gradient simple, mais pas pour Adam (étape 74).

## Rôle dans un agent

La régularisation agit hors ligne, dans l'entraînement des composants qui aident l'agent à décider : un adaptateur LoRA (étape 73), un routeur d'intentions, un modèle de score appelé comme outil (crédit, fraude, prix au sqft). Un agent fine-tuné sur 200 tickets peut apprendre leurs phrases exactes, y compris un numéro de dossier ; un grand poids permet une règle très pointue, et la pénalité rend ces règles plus chères que des règles générales. L1 sert aussi à l'**explicabilité** : un modèle qui n'utilise que douze entrées sur quarante se justifie plus facilement devant un comité de risque, et l'outil de l'agent peut citer les entrées qui ont pesé. Le coefficient λ se choisit sur un jeu de validation, jamais sur les données d'entraînement, parce que sur celles-ci la meilleure perte est toujours obtenue avec λ = 0.

## Équation complète

Les trois pertes régularisées (convention de ce fichier : λ/2 devant la somme des carrés) :

$$
\mathcal{L}_{L1} = \mathcal{L} + \lambda \sum_i \lvert w_i \rvert
$$

$$
\mathcal{L}_{L2} = \mathcal{L} + \frac{\lambda}{2} \sum_i w_i^2
$$

$$
\mathcal{L}_{EN} = \mathcal{L} + \lambda_1 \sum_i \lvert w_i \rvert + \frac{\lambda_2}{2} \sum_i w_i^2
$$

Pas de descente avec L2, et forme équivalente de la décroissance des poids :

$$
w_{t+1} = w_t - \eta \bigl( \nabla \mathcal{L}(w_t) + \lambda w_t \bigr) = (1 - \eta\lambda)\, w_t - \eta \, \nabla \mathcal{L}(w_t)
$$

Même pas avec la convention λ ∑ wᵢ² sans le ½, celle de l'ancienne version :

$$
w_{t+1} = w_t - \eta \bigl( \nabla \mathcal{L}(w_t) + 2\lambda w_t \bigr)
$$

Seuillage doux de seuil τ ≥ 0, puis pas proximal pour L1 :

$$
S_\tau(z) = \operatorname{signe}(z) \cdot \max\bigl(\lvert z \rvert - \tau,\; 0\bigr)
$$

$$
w_{t+1} = S_{\eta\lambda}\bigl( w_t - \eta \, \nabla \mathcal{L}(w_t) \bigr)
$$

Solutions exactes quand les colonnes des données sont orthogonales, avec ŵ la solution sans pénalité :

$$
w^{\text{lasso}}_j = S_\lambda(\hat{w}_j), \qquad w^{\text{ridge}}_j = \frac{\hat{w}_j}{1 + \lambda}, \qquad w^{EN}_j = \frac{S_{\lambda_1}(\hat{w}_j)}{1 + \lambda_2}
$$

## Décryptage des symboles

$$
w_i, \; w_t
$$

**Sens :** les poids du modèle (wᵢ le i-ème, wₜ le vecteur après t pas) · **Type / plage :** réels · **Variable Python :** `w`

$$
\mathcal{L}
$$

**Sens :** la perte des données seules, avant pénalité ; ici (1/2n) ‖y − Xw‖² · **Type / plage :** réel ≥ 0 · **Variable Python :** son gradient est `gradient_donnees(w)`

$$
\lambda, \; \lambda_1, \; \lambda_2
$$

**Sens :** coefficients de régularisation : la force de la pénalité, L1 et L2 dans elastic net · **Type / plage :** réels ≥ 0 ; λ = 0 supprime la pénalité · **Variable Python :** `lam`

$$
\eta
$$

**Sens :** taux d'apprentissage (étape 73) · **Type / plage :** réel > 0 · **Variable Python :** `eta`

$$
z, \; \tau
$$

**Sens :** la valeur à seuiller (le poids après le pas des données) et le seuil · **Type / plage :** z réel, τ ≥ 0, égal à ηλ dans un pas proximal · **Variable Python :** `z`, `seuil`

$$
S_\tau
$$

**Sens :** le seuillage doux : met à 0 tout ce qui est dans [−τ ; τ] et rapproche le reste de 0 de τ · **Type / plage :** fonction de ℝ dans ℝ · **Variable Python :** `seuillage_doux(z, seuil)`

$$
X, \; y, \; n
$$

**Sens :** la matrice des entrées (une ligne par exemple), les réponses, le nombre d'exemples · **Type / plage :** matrice n × d, vecteur de n réels, entier · **Variable Python :** `X`, `Y`, `len(X)`

$$
\hat{w}
$$

**Sens :** la solution des moindres carrés, sans pénalité · **Type / plage :** vecteur de d réels · **Variable Python :** `moindres_carres()`

L'ancienne version notait le taux d'apprentissage α ; il s'écrit η dans tout le parcours. Elle écrivait la pénalité L2 sous la forme λ ∑ wᵢ², de dérivée 2λw, tout en parlant ailleurs de « décroissance λ » ; ce fichier adopte λ/2 ∑ wᵢ², de dérivée λw, qui fait correspondre λ au coefficient de décroissance, et indique la conversion quand c'est utile.

## Démonstration

### 1. L2 retire une fraction du poids, et ne l'annule jamais

La dérivée de λw²/2 vaut λw. Un pas de descente donne donc

$$
w_{t+1} = w_t - \eta(g_t + \lambda w_t) = (1 - \eta\lambda)\, w_t - \eta\, g_t
$$

parce qu'on regroupe les deux termes en wₜ. Quand le gradient des données gₜ est nul, il reste wₜ = (1 − ηλ)ᵗ w₀ : le poids est multiplié par le même facteur à chaque pas. Si 0 < ηλ < 1, ce facteur est dans ]0 ; 1[ et le poids tend vers 0 sans jamais l'atteindre en un nombre fini de pas. Avec w₀ = 3, η = 0,1 et λ = 0,01, le facteur vaut 0,999 : le premier pas retire 0,003 et, après 1 000 pas, il reste 3 × 0,999¹⁰⁰⁰ = 1,1031. L'ancienne version annonçait un retrait de 0,006 : c'est le bon chiffre dans la convention λw², de dérivée 2λw, pas dans celle-ci. Comme à l'étape 73, la stabilité demande |1 − ηλ| < 1, soit 0 < ηλ < 2 : avec ηλ = 1, le poids tombe à 0 en un pas ; avec ηλ = 2,5, le facteur vaut −1,5 et le poids diverge en changeant de signe.

### 2. L2 et décroissance des poids : égaux pour la descente simple, différents pour Adam

La décroissance des poids s'écrit w ← (1 − d)w − ηg. En posant d = ηλ, c'est exactement le pas du point 1 : pour la descente de gradient simple, ajouter λw²/2 à la perte ou rétrécir les poids de ηλ à chaque pas, c'est la même chose. Ce n'est plus vrai avec Adam, parce qu'Adam divise le gradient par √v̂, pénalité comprise (étape 74, point 6). Avec un gradient des données nul, w = 1, λ = 0,01 et η = 0,001, Adam avec L2 dans le gradient retire 0,001, soit η, quel que soit λ ; AdamW retire ηλw = 0,00001. L'ancienne version disait à la fois que la décroissance d'AdamW « est » la régularisation L2 et que les deux idées « divergent dès que l'optimiseur divise par √v » : la seconde phrase est la bonne, et la première ne vaut que pour la descente simple.

### 3. Le seuillage doux est le minimum exact d'un problème à une variable

On cherche le w qui minimise, pour un z donné et λ ≥ 0,

$$
f(w) = \tfrac{1}{2}(w - z)^2 + \lambda \lvert w \rvert
$$

f est strictement convexe (somme d'une parabole et d'une valeur absolue), donc son minimum est unique. Premier cas, |z| ≤ λ : pour tout w, −zw ≥ −|z||w|, donc

$$
f(w) - f(0) = \tfrac{1}{2} w^2 - z w + \lambda \lvert w \rvert \ge \tfrac{1}{2} w^2 + (\lambda - \lvert z \rvert)\, \lvert w \rvert \ge 0
$$

avec égalité seulement en w = 0 : le minimum est 0. Deuxième cas, z > λ : sur w > 0, f′(w) = w − z + λ s'annule en w = z − λ, qui est bien positif ; sur w ≤ 0, f′(w) = w − z − λ < 0, donc f y décroît et son minimum n'y est pas. Le minimum est z − λ. Le cas z < −λ est symétrique et donne z + λ. Les trois cas s'écrivent d'une seule formule :

$$
\arg\min_w \; \tfrac{1}{2}(w - z)^2 + \lambda \lvert w \rvert = \operatorname{signe}(z)\, \max(\lvert z \rvert - \lambda, 0) = S_\lambda(z)
$$

L'intervalle [−λ ; λ] est une **zone morte** : toute valeur qui y tombe sort exactement nulle. Avec λ = 0,1 : S(−0,3) = −0,2, S(−0,05) = 0, S(0,07) = 0, S(2,0) = 1,9. Le programme vérifie ces quatre valeurs en essayant tous les w d'une grille de pas 10⁻⁴.

### 4. Pourquoi le sous-gradient oscille, et ce que fait le pas proximal

La dérivée de λ|w| vaut λ pour w > 0 et −λ pour w < 0 : un pas de sous-gradient ajoute ou retranche **toujours la même quantité** ηλ. Prenons un gradient des données nul, w = 0,03, η = 0,1 et λ = 0,5, donc ηλ = 0,05. Le premier pas donne 0,03 − 0,05 = −0,02, le second −0,02 + 0,05 = 0,03, et le poids alterne entre 0,03 et −0,02 sans jamais valoir 0 : il ne tomberait exactement sur 0 que si 0,03 était un multiple exact de 0,05. L'ancienne version affirmait qu'« un petit poids est poussé jusqu'à 0 et y reste » : c'est vrai du pas proximal, faux du sous-gradient. Le pas proximal fait d'abord le pas des données, z = wₜ − ηgₜ, puis résout exactement le problème du point 3 avec le seuil ηλ :

$$
w_{t+1} = \arg\min_w \; \tfrac{1}{2}\bigl(w - z\bigr)^2 + \eta\lambda \lvert w \rvert = S_{\eta\lambda}\bigl(w_t - \eta\, g_t\bigr)
$$

Ici, S₀,₀₅(0,03) = 0 dès le premier pas, et S₀,₀₅(0) = 0 ensuite : le poids s'éteint et reste éteint. Itérer ce pas s'appelle ISTA (*Iterative Shrinkage-Thresholding Algorithm*) ; on admet qu'il converge vers le minimum de la perte pénalisée dès que η ≤ 1/L, la condition de l'étape 73.

### 5. Avec des colonnes orthogonales, chaque poids se règle seul

Supposons (1/n) XᵀX = I et notons ŵ = (1/n) Xᵀy la solution sans pénalité. On écrit y − Xw = (y − Xŵ) + X(ŵ − w) et on développe le carré :

$$
\lVert y - Xw \rVert^2 = \lVert y - X\hat{w} \rVert^2 + 2\,(y - X\hat{w})^\top X (\hat{w} - w) + (\hat{w} - w)^\top X^\top X (\hat{w} - w)
$$

Le terme du milieu est nul, parce que Xᵀ(y − Xŵ) = Xᵀy − XᵀXŵ = nŵ − nŵ = 0, et le dernier vaut n‖ŵ − w‖². En divisant par 2n :

$$
\frac{1}{2n} \lVert y - Xw \rVert^2 = \text{constante} + \frac{1}{2} \sum_j (w_j - \hat{w}_j)^2
$$

La perte pénalisée se sépare donc en un problème à une variable par poids. Avec L1, chaque problème est celui du point 3 : wⱼ = S_λ(ŵⱼ). Avec L2, la dérivée de ½(w − ŵ)² + λw²/2 vaut w − ŵ + λw, nulle en w = ŵ / (1 + λ) : un rétrécissement, jamais un zéro tant que ŵ ≠ 0. Avec elastic net, on regroupe les deux termes quadratiques :

$$
\tfrac{1}{2}(w - \hat{w})^2 + \tfrac{\lambda_2}{2} w^2 = \tfrac{1 + \lambda_2}{2}\Bigl(w - \tfrac{\hat{w}}{1 + \lambda_2}\Bigr)^2 + \text{constante}
$$

Après division par 1 + λ₂, c'est le problème du point 3 avec z = ŵ / (1 + λ₂) et le seuil λ₁ / (1 + λ₂), dont la solution vaut S_λ₁(ŵ) / (1 + λ₂). Elastic net éteint donc les mêmes poids que le lasso, et rétrécit les autres comme le ridge.

### 6. Exemple fait à la main (le code reprend ces nombres)

Les quatre exemples ont trois entrées, dont les colonnes (1 ; 1 ; −1 ; −1), (1 ; −1 ; 1 ; −1) et (1 ; −1 ; −1 ; 1) sont orthogonales, de carré 4 = n, et de somme nulle (pas besoin de biais). Les réponses valent y = (2,34 ; 1,66 ; −1,74 ; −2,26). Les produits avec les colonnes valent 8,0, puis 1,2, puis 0,16 ; divisés par n = 4, ils donnent ŵ = (2,0 ; 0,3 ; 0,04).

| Méthode, λ = 0,1 | Calcul | w₁ | w₂ | w₃ |
|---|---|---|---|---|
| Moindres carrés | ŵ | 2,0 | 0,3 | 0,04 |
| Lasso | S₀,₁(ŵⱼ) | 1,9 | 0,2 | 0 |
| Ridge | ŵⱼ / 1,1 | 1,81818 | 0,27273 | 0,03636 |
| Elastic net, λ₁ = λ₂ = 0,1 | S₀,₁(ŵⱼ) / 1,1 | 1,72727 | 0,18182 | 0 |

Avec η = 0,5, un pas d'ISTA s'écrit w ← S₀,₀₅(0,5 w + 0,5 ŵ). Pour w₃, partie de 0 : 0,5 × 0,04 = 0,02 ≤ 0,05, donc w₃ reste exactement 0 à chaque pas. Pour w₁, le point fixe vérifie w = 0,5w + 1,0 − 0,05, soit w = 1,9. La descente de sous-gradient atteint les mêmes w₁ et w₂, mais laisse w₃ osciller : après 100 pas, il vaut −0,02774. La pénalité L1 du lasso vaut 0,1 × (1,9 + 0,2) = 0,21.

## Effets et comportement

- **L2 rétrécit en proportion.** Un grand poids perd beaucoup, un petit poids perd peu ; aucun n'est éteint. Avec des entrées corrélées, L2 répartit le poids entre elles au lieu d'en choisir une.
- **L1 retire une constante et éteint les petits poids.** Tout poids dont la valeur avant seuillage reste dans [−ηλ ; ηλ] sort exactement nul, à condition d'utiliser le pas proximal.
- **λ trop grand sous-apprend.** Avec λ ≥ max |ŵⱼ|, le lasso éteint tout ; avec un très grand λ, le ridge ramène tous les poids près de 0.
- **La pénalité dépend de l'échelle des entrées.** Une entrée exprimée en AED a des poids minuscules, une entrée en millions d'AED des poids énormes : sans normalisation, la même pénalité ne les traite pas de la même façon.
- **Des zéros dans une matrice dense n'accélèrent rien.** Éteindre des poids épars au milieu d'une matrice de LLM ne rend pas le produit matriciel plus rapide ; L1 sert surtout aux petits modèles et à la sélection d'entrées.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| λ ∑\|wᵢ\|, (λ/2) ∑wᵢ² | `penalite_l1(poids, lam)`, `penalite_l2(poids, lam)` |
| S_τ(z) | `seuillage_doux(z, seuil)` |
| argmin de ½(w − z)² + λ\|w\| sur une grille | `minimum_par_grille(z, lam)` |
| (1 − ηλ)w − ηg | `pas_sgd_l2(w, g, eta, lam)` |
| (1 − d)w − ηg | `pas_decroissance(w, g, eta, d)` |
| w − η(g + λ signe(w)) | `pas_sous_gradient_l1(w, g, eta, lam)` |
| S_ηλ(w − ηg) | `pas_proximal_l1(w, g, eta, lam)` |
| X, y, ∇ℒ = −(1/n)Xᵀ(y − Xw) | `X`, `Y`, `gradient_donnees(w)` |
| ŵ = (1/n)Xᵀy | `moindres_carres()` |
| T pas d'une règle depuis w = 0 | `entrainer(regle, lam, eta, iterations)` |
| conditions d'optimalité du lasso | `conditions_lasso(w, w_ols, lam)` |

### Déroulé, ligne par ligne

**`penalite_l1` et `penalite_l2`.** La première renvoie `lam * sum(abs(w) for w in poids)` ; la seconde `0.5 * lam * sum(w * w for w in poids)`, avec le ½ de la convention de ce fichier. Sur les poids du lasso (1,9 ; 0,2 ; 0) et λ = 0,1, la pénalité L1 vaut 0,21 ; sur ceux du ridge, la pénalité L2 vaut 0,16907.

**`seuillage_doux(z, seuil)`.** La garde refuse un seuil négatif, qui n'a pas de sens pour une pénalité. Si |z| dépasse le seuil, on renvoie `math.copysign(abs(z) - seuil, z)` : la distance à 0 diminue du seuil, et le signe de z est conservé ; sinon on renvoie `0.0`. Ce `else` écrit explicitement 0.0, parce que `math.copysign(0.0, -0.05)` donnerait −0.0, un zéro signé qui s'affiche mal et trompe un test d'égalité de chaînes. Avec un seuil de 0,1 : −0,3 donne −0,2, et 0,07 donne 0.

**`minimum_par_grille(z, lam)`.** Essaie les 60 001 valeurs k × 10⁻⁴ entre −3 et 3 et garde celle qui minimise ½(w − z)² + λ|w|. C'est une vérification par force brute de la formule démontrée au point 3 : sur les quatre z du programme, la grille et `seuillage_doux` coïncident à 10⁻⁴ près.

**`pas_sgd_l2` et `pas_decroissance`.** La première calcule `w - eta * (g + lam * w)`, la seconde `(1 - d) * w - eta * g`. Dans `main`, on les fait tourner vingt pas côte à côte avec le même gradient `math.sin(t)` et `d = eta * lam` : elles restent égales à 10⁻¹² près (point 2). Avec w = 3, η = 0,1 et λ = 0,01, un pas sans gradient des données retire 0,003 ; en passant `2 * lam`, ce qui revient à la convention λw², il retire 0,006.

**`pas_sous_gradient_l1(w, g, eta, lam)`.** `signe = (w > 0) - (w < 0)` vaut 1, −1 ou 0 (le sous-gradient choisi en 0). Le pas retranche `eta * (g + lam * signe)`. Depuis 0,03 avec ηλ = 0,05, il donne −0,02, puis 0,03, puis −0,02 : la boucle de 1 000 pas vérifie que |w| reste au-dessus de 0,019, donc que le poids n'atteint jamais 0.

**`pas_proximal_l1(w, g, eta, lam)`** renvoie `seuillage_doux(w - eta * g, eta * lam)` : le pas des données, puis le seuil ηλ. Depuis 0,03, il donne 0 au premier pas, puis 0 pour toujours.

**`X`, `Y`, `gradient_donnees(w)` et `moindres_carres()`.** `X` contient les quatre lignes de l'exemple et `Y` les quatre réponses. `gradient_donnees` calcule les résidus y − Xw puis −(1/n)Xᵀ(résidus) ; comme (1/n)XᵀX = I, ce gradient vaut simplement w − ŵ. `moindres_carres` renvoie (1/n)Xᵀy = (2,0 ; 0,3 ; 0,04).

**`entrainer(regle, lam, eta, iterations)`.** Part de w = (0 ; 0 ; 0) et applique `iterations` fois la règle choisie à chaque coordonnée, avec le gradient des données recalculé à chaque pas. Avec `pas_proximal_l1`, η = 0,5 et 100 itérations, c'est ISTA : le résultat vaut (1,9 ; 0,2 ; 0,0), et `lasso[2] == 0.0` est vrai au sens strict. Avec `pas_sous_gradient_l1`, la troisième coordonnée vaut −0,02774. Avec `pas_sgd_l2`, on retrouve la formule fermée du ridge à 10⁻¹² près.

**`conditions_lasso(w, w_ols, lam)`.** Vérifie les conditions d'optimalité qui découlent du point 3 : pour un poids non nul, w − ŵ + λ signe(w) = 0 ; pour un poids nul, |ŵ| ≤ λ. Sur le résultat d'ISTA, les deux sont satisfaites : 1,9 − 2,0 + 0,1 = 0, 0,2 − 0,3 + 0,1 = 0, et |0,04| ≤ 0,1.

**`main()`, bloc par bloc.**

1. Le seuillage doux comparé à la grille, sur les quatre valeurs du point 3.
2. Six pas de sous-gradient et six pas proximaux depuis 0,03 : les deux traces du point 4, puis 1 000 pas de sous-gradient qui n'atteignent jamais 0.
3. L2 contre décroissance des poids sur vingt pas, les retraits 0,003 et 0,006, 1,1031 après 1 000 pas, puis ηλ = 1 (zéro en un pas) et ηλ = 2,5 (−4,5 : divergence).
4. La régression à colonnes orthogonales : les cinq vecteurs du tableau du point 6, les conditions d'optimalité du lasso, et la pénalité 0,21.
5. Le retrait d'un pas d'Adam avec L2 dans le gradient (0,001) contre celui d'AdamW (0,00001), puis un seuil négatif refusé.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`penalite_l2(poids, lam)`** — Cette fonction est la jumelle de `penalite_l1`, le percepteur qui taxe chaque poids au carré de sa taille plutôt qu'à sa valeur absolue : elle reçoit une liste de poids et λ, et renvoie (λ/2) Σ w², avec le facteur ½ de la convention de ce fichier, choisi pour que la dérivée vaille simplement λw. Sur les poids du ridge, environ 1,8182, 0,2727 et 0,0364, et avec λ = 0,1, elle donne 0,16907, la valeur que `main` affiche à côté de la pénalité L1 du lasso.

**`pas_decroissance(w, g, eta, d)`** — Celle-ci est l'autre façon d'écrire la régularisation L2, comme un jardinier qui taille d'abord une fraction fixe de chaque branche avant d'arroser : elle reçoit un poids, le gradient des données, le pas η et la fraction d, et renvoie (1 − d)w − ηg, le poids rétréci puis le pas des données. Avec d = ηλ, elle coïncide exactement avec `pas_sgd_l2`, ce que `main` vérifie sur vingt pas avec le gradient sin(t), à 10⁻¹² près, ce qui montre que décroissance des poids et L2 ne font qu'un pour la SGD.

**`pas_proximal_l1(w, g, eta, lam)`** — Cette fonction fait le pas de l'algorithme ISTA, comme un douanier qui laisse d'abord passer le colis puis prélève une taxe fixe, et confisque tout colis qui vaut moins que la taxe : elle reçoit un poids, le gradient des données, η et λ, fait le pas des données w − ηg, puis lui applique `seuillage_doux` avec le seuil ηλ. Elle renvoie le nouveau poids ; depuis 0,03 avec ηλ = 0,05, elle donne 0 dès le premier pas et 0 pour toujours, et, répétée cent fois avec η = 0,5 et λ = 0,1, elle amène le lasso à exactement (1,9 ; 0,2 ; 0,0).

**`gradient_donnees(w)`** — Celle-ci mesure la pente de la perte des moindres carrés sur la petite régression de quatre exemples : elle reçoit les poids, calcule pour chaque ligne de `X` le résidu y − Xw, puis renvoie −(1/n)Xᵀ fois ces résidus, le gradient de (1/2n)‖y − Xw‖². Comme les colonnes de `X` sont orthogonales et que (1/n)XᵀX = I, ce gradient vaut simplement w − ŵ ; `entrainer` l'appelle à chaque itération avant d'appliquer la règle choisie à chaque coordonnée.

**`moindres_carres()`** — Cette fonction donne la solution sans pénalité, le point vers lequel la régression tirerait si rien ne la retenait : elle ne reçoit rien, lit les tableaux `X` et `Y` du module, et renvoie (1/n)Xᵀy, qui suffit ici parce que (1/n)XᵀX = I. Elle rend (2,0 ; 0,3 ; 0,04), le vecteur ŵ dont `Y` a été construit, et c'est par rapport à lui que `main` compare le lasso, le sous-gradient, le ridge et l'elastic net, et que `conditions_lasso` vérifie l'optimalité.

**`main()`** — C'est le comparateur qui met les régularisations côte à côte en cinq essais : il confronte d'abord le seuillage doux à une recherche sur grille pour quatre valeurs, puis montre que le sous-gradient L1 oscille entre −0,02 et 0,03 sans jamais atteindre 0, tandis que le pas proximal tombe à 0 dès le premier pas. Il vérifie ensuite l'égalité de L2 et de la décroissance des poids, les retraits 0,003 et 0,006 et la divergence quand ηλ = 2,5, résout la régression à colonnes orthogonales par moindres carrés, lasso, sous-gradient, ridge et elastic net, et termine en opposant le retrait d'Adam avec L2, 0,001, à celui d'AdamW, 0,00001, avant de refuser un seuil négatif.

```python
"""Étape 76 — régularisation L1 et L2 : seuillage doux, décroissance des poids, lasso, ridge et elastic net."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- pénalités et opérateurs à une variable
def penalite_l1(poids: list[float], lam: float) -> float:
    """λ Σ |w|."""
    return lam * sum(abs(w) for w in poids)


def penalite_l2(poids: list[float], lam: float) -> float:
    """(λ/2) Σ w² : convention de ce fichier, dont la dérivée vaut λw."""
    return 0.5 * lam * sum(w * w for w in poids)


def seuillage_doux(z: float, seuil: float) -> float:
    """S(z) = signe(z) · max(|z| − seuil, 0) : le minimiseur de ½(w − z)² + seuil·|w|."""
    if seuil < 0:
        raise ValueError("le seuil doit être >= 0")
    return math.copysign(abs(z) - seuil, z) if abs(z) > seuil else 0.0   # 0.0 et non −0.0 dans la zone morte


def minimum_par_grille(z: float, lam: float, pas: float = 1e-4, borne: float = 3.0) -> float:
    """Minimise ½(w − z)² + λ|w| en essayant tous les w d'une grille : sert à vérifier la formule fermée."""
    n = int(round(borne / pas))
    return min((k * pas for k in range(-n, n + 1)), key=lambda w: 0.5 * (w - z) ** 2 + lam * abs(w))


# ---------------------------------------------------------------- un pas de descente
def pas_sgd_l2(w: float, g: float, eta: float, lam: float) -> float:
    """Descente sur ℒ + (λ/2)w² : w − η(g + λw) = (1 − ηλ)w − ηg."""
    return w - eta * (g + lam * w)


def pas_decroissance(w: float, g: float, eta: float, d: float) -> float:
    """Décroissance des poids : on rétrécit w d'une fraction d, puis on fait le pas des données."""
    return (1 - d) * w - eta * g


def pas_sous_gradient_l1(w: float, g: float, eta: float, lam: float) -> float:
    """w − η(g + λ·signe(w)), avec signe(0) = 0 : ne tombe presque jamais exactement sur 0."""
    signe = (w > 0) - (w < 0)
    return w - eta * (g + lam * signe)


def pas_proximal_l1(w: float, g: float, eta: float, lam: float) -> float:
    """Pas proximal (ISTA) : d'abord le pas des données, puis le seuillage doux de seuil ηλ."""
    return seuillage_doux(w - eta * g, eta * lam)


# ---------------------------------------------------------------- régression à colonnes orthogonales
X = [[1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, -1.0, 1.0]]   # (1/n) XᵀX = I
Y = [2.34, 1.66, -1.74, -2.26]                                                    # = X · (2.0, 0.3, 0.04)


def gradient_donnees(w: list[float]) -> list[float]:
    """Gradient de (1/2n) ‖y − Xw‖² : −(1/n) Xᵀ(y − Xw)."""
    n = len(X)
    residus = [y - sum(xi * wi for xi, wi in zip(ligne, w)) for ligne, y in zip(X, Y)]
    return [-sum(X[i][j] * residus[i] for i in range(n)) / n for j in range(len(w))]


def moindres_carres() -> list[float]:
    """Avec (1/n) XᵀX = I, la solution sans pénalité vaut (1/n) Xᵀy."""
    n = len(X)
    return [sum(X[i][j] * Y[i] for i in range(n)) / n for j in range(len(X[0]))]


def entrainer(regle, lam: float, eta: float, iterations: int) -> list[float]:
    w = [0.0, 0.0, 0.0]
    for _ in range(iterations):
        g = gradient_donnees(w)
        w = [regle(wj, gj, eta, lam) for wj, gj in zip(w, g)]
    return w


def conditions_lasso(w: list[float], w_ols: list[float], lam: float) -> bool:
    """Optimalité du lasso (plan orthogonal) : w − ŵ + λ·signe(w) = 0 si w ≠ 0, et |ŵ| ≤ λ si w = 0."""
    for wj, oj in zip(w, w_ols):
        if wj != 0.0 and abs(wj - oj + lam * math.copysign(1.0, wj)) > 1e-9:
            return False
        if wj == 0.0 and abs(oj) > lam + 1e-12:
            return False
    return True


def main() -> None:
    print("1. Seuillage doux, seuil 0.1 : minimiseur de ½(w − z)² + 0.1|w|")
    zs = (-0.3, -0.05, 0.07, 2.0)
    s = [seuillage_doux(z, 0.1) for z in zs]
    grille = [minimum_par_grille(z, 0.1) for z in zs]
    print(f"  z = {list(zs)}   S(z) = {[round(v, 4) for v in s]}   minimum sur une grille de pas 1e-4 = {[round(v, 4) for v in grille]}")
    assert all(abs(a - b) < 1e-12 for a, b in zip(s, [-0.2, 0.0, 0.0, 1.9]))
    assert all(abs(a - b) < 1e-4 for a, b in zip(s, grille))

    print("2. L1 seul (gradient des données nul), w = 0.03, η = 0.1, λ = 0.5 : ηλ = 0.05")
    w_sg, w_px = 0.03, 0.03
    trace_sg, trace_px = [], []
    for _ in range(6):
        w_sg = pas_sous_gradient_l1(w_sg, 0.0, 0.1, 0.5)
        w_px = pas_proximal_l1(w_px, 0.0, 0.1, 0.5)
        trace_sg.append(round(w_sg, 4))
        trace_px.append(w_px)
    print(f"  sous-gradient : {trace_sg}")
    print(f"  proximal      : {trace_px}")
    assert trace_sg == [-0.02, 0.03, -0.02, 0.03, -0.02, 0.03] and trace_px == [0.0] * 6
    w = 0.03
    for _ in range(1000):
        w = pas_sous_gradient_l1(w, 0.0, 0.1, 0.5)
        assert abs(w) > 0.019                         # oscille autour de 0 sans jamais l'atteindre

    print("3. L2 : (λ/2)w² donne le facteur 1 − ηλ ; c'est exactement la décroissance des poids pour SGD")
    eta, lam = 0.1, 0.01
    w_l2 = w_wd = 3.0
    for t in range(20):
        g = math.sin(t)                               # un gradient des données quelconque, le même pour les deux
        w_l2 = pas_sgd_l2(w_l2, g, eta, lam)
        w_wd = pas_decroissance(w_wd, g, eta, eta * lam)
    assert abs(w_l2 - w_wd) < 1e-12
    retrait = 3.0 - pas_sgd_l2(3.0, 0.0, eta, lam)
    retrait_2lam = 3.0 - pas_sgd_l2(3.0, 0.0, eta, 2 * lam)   # convention λw², dérivée 2λw
    w = 3.0
    for _ in range(1000):
        w = pas_sgd_l2(w, 0.0, eta, lam)
    print(f"  w = 3 : retrait par pas {retrait:.4f} (convention λw² : {retrait_2lam:.4f}) ; après 1000 pas w = {w:.4f}")
    assert abs(retrait - 0.003) < 1e-12 and abs(retrait_2lam - 0.006) < 1e-12
    assert abs(w - 3.0 * 0.999 ** 1000) < 1e-9 and w > 0
    print(f"  ηλ = 1 : {pas_sgd_l2(3.0, 0.0, 1.0, 1.0)} en un pas ; ηλ = 2.5 : {pas_sgd_l2(3.0, 0.0, 1.0, 2.5)} (|1 − ηλ| > 1, diverge)")
    assert pas_sgd_l2(3.0, 0.0, 1.0, 1.0) == 0.0 and abs(pas_sgd_l2(3.0, 0.0, 1.0, 2.5)) > 3.0

    print("4. Régression à colonnes orthogonales, ŵ = (2.0, 0.3, 0.04), λ = 0.1")
    w_ols = moindres_carres()
    lasso = entrainer(pas_proximal_l1, lam=0.1, eta=0.5, iterations=100)
    sous_g = entrainer(pas_sous_gradient_l1, lam=0.1, eta=0.5, iterations=100)
    ridge = [o / (1 + 0.1) for o in w_ols]
    ridge_gd = entrainer(pas_sgd_l2, lam=0.1, eta=0.5, iterations=100)
    elastic = [seuillage_doux(o, 0.1) / (1 + 0.1) for o in w_ols]
    for nom, v in (("moindres carrés", w_ols), ("lasso (ISTA)", lasso), ("sous-gradient L1", sous_g),
                   ("ridge", ridge), ("elastic net", elastic)):
        print(f"  {nom:<17} w = {[round(x, 5) for x in v]}")
    assert all(abs(a - b) < 1e-12 for a, b in zip(w_ols, [2.0, 0.3, 0.04]))
    assert all(abs(a - b) < 1e-12 for a, b in zip(lasso, [1.9, 0.2, 0.0])) and lasso[2] == 0.0
    assert conditions_lasso(lasso, w_ols, 0.1)
    assert sous_g[2] != 0.0 and abs(sous_g[2]) < 0.1     # près de 0, jamais exactement 0
    assert all(abs(a - b) < 1e-12 for a, b in zip(ridge, ridge_gd)) and min(abs(x) for x in ridge) > 0
    assert all(abs(a - b) < 1e-12 for a, b in zip(elastic, [1.9 / 1.1, 0.2 / 1.1, 0.0]))
    print(f"  pénalités du lasso : L1 = {penalite_l1(lasso, 0.1):.3f}   L2 du ridge = {penalite_l2(ridge, 0.1):.5f}")
    assert abs(penalite_l1(lasso, 0.1) - 0.21) < 1e-12

    print("5. Avec Adam, L2 ≠ décroissance : un pas, gradient des données nul, w = 1, λ = 0.01, η = 0.001")
    g_l2 = 0.01 * 1.0                                 # λw ajouté au gradient, puis normalisé par Adam (étape 74)
    retrait_adam_l2 = 0.001 * g_l2 / (math.sqrt(g_l2 * g_l2) + 1e-8)
    retrait_adamw = 0.001 * 0.01 * 1.0
    print(f"  Adam + L2 retire {retrait_adam_l2:.6f} ; AdamW retire {retrait_adamw:.6f}")
    assert abs(retrait_adam_l2 - 0.001) < 1e-8 and retrait_adamw == 1e-05

    try:
        seuillage_doux(1.0, -0.1)
    except ValueError:
        print("  seuil négatif → ValueError")
    else:
        raise AssertionError("un seuil négatif aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Seuillage doux, seuil 0.1 : minimiseur de ½(w − z)² + 0.1|w|
  z = [-0.3, -0.05, 0.07, 2.0]   S(z) = [-0.2, 0.0, 0.0, 1.9]   minimum sur une grille de pas 1e-4 = [-0.2, 0.0, 0.0, 1.9]
2. L1 seul (gradient des données nul), w = 0.03, η = 0.1, λ = 0.5 : ηλ = 0.05
  sous-gradient : [-0.02, 0.03, -0.02, 0.03, -0.02, 0.03]
  proximal      : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
3. L2 : (λ/2)w² donne le facteur 1 − ηλ ; c'est exactement la décroissance des poids pour SGD
  w = 3 : retrait par pas 0.0030 (convention λw² : 0.0060) ; après 1000 pas w = 1.1031
  ηλ = 1 : 0.0 en un pas ; ηλ = 2.5 : -4.5 (|1 − ηλ| > 1, diverge)
4. Régression à colonnes orthogonales, ŵ = (2.0, 0.3, 0.04), λ = 0.1
  moindres carrés   w = [2.0, 0.3, 0.04]
  lasso (ISTA)      w = [1.9, 0.2, 0.0]
  sous-gradient L1  w = [1.9, 0.2, -0.02774]
  ridge             w = [1.81818, 0.27273, 0.03636]
  elastic net       w = [1.72727, 0.18182, 0.0]
  pénalités du lasso : L1 = 0.210   L2 du ridge = 0.16907
5. Avec Adam, L2 ≠ décroissance : un pas, gradient des données nul, w = 1, λ = 0.01, η = 0.001
  Adam + L2 retire 0.001000 ; AdamW retire 0.000010
  seuil négatif → ValueError
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

Le squelette ci-dessous est celui d'ISTA, la descente proximale pour L1, puis celui de la descente avec décroissance des poids pour L2. En entrée : des poids de départ, une fonction qui renvoie le gradient des **données seules** (sans la pénalité), un pas η, un coefficient λ et un nombre d'itérations. En sortie : les poids régularisés, dont certains sont exactement nuls avec L1. L'idée tient en une phrase : on fait le pas ordinaire des données, puis on applique la pénalité sous sa forme exacte (un seuil pour L1, un facteur pour L2) au lieu de la dériver.

```text
ALGORITHME DescenteProximaleL1
ENTRÉES : poids w (d nombres), fonction gradient_données, pas η > 0, coefficient λ ≥ 0, nombre d'itérations T
SORTIE : poids w, dont certains exactement nuls

SI η ≤ 0 OU λ < 0 ALORS
    RETOURNER ERREUR « paramètres invalides »
FIN SI
τ ← η · λ                                        seuil de la zone morte
POUR k DE 1 À T FAIRE
    g ← gradient_données(w)                      gradient de la perte des données, sans la pénalité
    POUR j DE 1 À d FAIRE
        z ← w[j] − η · g[j]                       pas ordinaire de descente
        SI |z| ≤ τ ALORS
            w[j] ← 0                              le poids s'éteint exactement
        SINON
            w[j] ← signe(z) · (|z| − τ)           on retranche une constante, pas une fraction
        FIN SI
    FIN POUR
FIN POUR
RETOURNER w

ALGORITHME DescenteAvecDécroissanceL2
ENTRÉES : poids w, fonction gradient_données, pas η > 0, coefficient λ ≥ 0 avec η · λ < 2, itérations T
SORTIE : poids w rétrécis, jamais exactement nuls si 0 < η · λ < 1

POUR k DE 1 À T FAIRE
    g ← gradient_données(w)
    POUR j DE 1 À d FAIRE
        w[j] ← (1 − η · λ) · w[j] − η · g[j]     même résultat que le gradient de ℒ + (λ/2) Σ w²
    FIN POUR
FIN POUR
RETOURNER w
```

**Complexité :** une itération coûte le calcul du gradient des données, G, plus O(d) pour parcourir les d poids, parce que le seuillage et le facteur 1 − ηλ ne coûtent qu'une opération par poids. Pour la régression linéaire du programme, G = O(n d) : chaque résidu est un produit scalaire de d termes, et chaque coordonnée du gradient une somme sur n résidus. Le total vaut O(T (n d + d)) = O(T n d) en temps. En mémoire, il faut O(d) pour w et g, en plus des données X (O(n d)) qu'on ne recopie pas. La pénalité ne change donc pas l'ordre de grandeur du coût : c'est le gradient des données qui domine.

**Du squelette au code :** la garde « SI η ≤ 0 OU λ < 0 » n'existe qu'en partie dans le programme : `seuillage_doux` refuse un seuil τ = ηλ négatif, mais aucune fonction ne vérifie η > 0 à part ; une version de production ajouterait ce test dans `entrainer`. La boucle « POUR k » et l'appel à gradient_données sont la boucle de `entrainer`, qui appelle `gradient_donnees(w)` à chaque itération. La boucle « POUR j » est la compréhension `[regle(wj, gj, eta, lam) for wj, gj in zip(w, g)]`. Les lignes « z ← w[j] − η · g[j] » puis « SI |z| ≤ τ … SINON … » sont `pas_proximal_l1`, qui calcule `w - eta * g` et le passe à `seuillage_doux(z, eta * lam)`. La ligne de mise à jour de DescenteAvecDécroissanceL2 est `pas_sgd_l2` (ou `pas_decroissance` avec `d = eta * lam`), passée à `entrainer` comme règle.

## Cas d'usage réels aux Émirats

Les nombres d'entrées, les coefficients et les volumes ci-dessous sont illustratifs : ils servent à faire le calcul, pas à décrire un déploiement réel.

### Banque — un score de crédit qui se justifie en douze entrées

Une banque de détail de Dubaï expose à son agent de crédit un outil de score qui estime le risque d'impayé d'un prêt personnel, en plus des règles fixes de la CBUAE : toutes les mensualités, la nouvelle comprise, doivent rester sous 50 % du revenu, et un prêt personnel ne dépasse ni 20 fois le salaire ni 48 mois. Le modèle de score est une régression logistique sur quarante entrées (ancienneté chez l'employeur, historique de remboursement, ratio d'endettement, etc.). Entraîné avec une pénalité L1 et des pas proximaux, il éteint exactement 28 de ces entrées et n'en garde que douze ; le comité de risque peut ainsi relire chaque poids, et l'agent cite à l'analyste les trois entrées qui ont le plus pesé dans un dossier. Avec une simple descente de sous-gradient, les 28 poids auraient oscillé autour de 0 sans s'éteindre (point 4), et le modèle n'aurait pas été plus lisible qu'avant. Le coefficient λ est choisi sur un jeu de validation de dossiers plus récents que ceux de l'entraînement. Sans régularisation, le modèle s'accroche à des entrées rares qui expliquent quelques impayés du passé, et sa performance chute sur les nouveaux dossiers. On suit l'aire sous la courbe ROC sur les dossiers récents (étape 51) et le nombre d'entrées actives.

### Immobilier — des entrées corrélées qui se disputent le poids

Une agence active à Dubaï et à Abu Dhabi expose à son agent un outil qui estime le prix au sqft d'un bien à partir de sa surface en sqft, de son nombre de chambres, de son étage et de son quartier. Surface et nombre de chambres sont fortement corrélés : sans pénalité, la régression leur donne des poids énormes et de signes opposés qui se compensent, et l'estimation change de plusieurs centaines d'AED par sqft quand on ajoute une poignée de ventes. Une pénalité L2 répartit le poids entre les deux entrées au lieu de les laisser se battre : la solution ridge rétrécit chaque poids, comme ŵ / (1 + λ) dans le plan orthogonal du point 5, et l'estimation devient stable. L'agent utilise cette estimation pour décider si une annonce est très au-dessus du marché et doit être signalée au négociateur avant publication. Le calcul des frais de transfert, 4 % de la valeur du bien à Dubaï, reste hors du modèle, dans un outil de calcul exact. On suit l'erreur relative entre le prix estimé et le prix de vente réel, et sa variation d'un réentraînement à l'autre.

### RH — un adaptateur qui ne doit pas réciter des dossiers

Un cabinet RH présent dans plusieurs émirats fine-tune un adaptateur LoRA sur 200 lettres types validées par ses juristes, pour que son agent rédige les avenants de contrat dans le style maison. Sur si peu d'exemples, l'adaptateur peut apprendre par cœur des passages entiers, y compris un nom ou un numéro d'Emirates ID resté dans une lettre. L'équipe entraîne avec AdamW et une décroissance des poids de 0,01, qui rétrécit chaque poids de ηλ par pas sans passer par les moyennes d'Adam (point 2), et arrête l'entraînement dès que la perte de validation remonte. La régularisation réduit la mémorisation, mais ne la supprime pas : la PDPL impose de toute façon de pseudonymiser les lettres avant l'entraînement, et le cabinet le fait en premier. Sans ces deux protections, l'agent risquerait de recopier, dans la lettre d'un employé, un fragment du dossier d'un autre. On suit la perte de validation et un test automatique qui cherche, dans un échantillon de lettres générées, des chaînes recopiées mot pour mot depuis le jeu d'entraînement.

### Assurance — elastic net pour des garages qui se ressemblent

Un assureur auto et santé entraîne un modèle d'aide à la détection de fraude avec une entrée par garage partenaire, soit plusieurs centaines d'entrées rarement actives. Plusieurs garages appartiennent au même réseau et apparaissent ensemble dans les mêmes dossiers suspects. Le lasso seul choisit souvent un garage du groupe et éteint les autres, ce qui rend le modèle fragile si ce garage change de nom ; le ridge seul garde tous les garages avec de petits poids, sans en éteindre aucun. Elastic net, avec λ₁ = λ₂ = 0,1 dans l'exemple du point 6, éteint les garages sans signal et partage le poids entre les garages corrélés, en les rétrécissant d'un facteur 1 / (1 + λ₂). L'agent de tri envoie à un expert les sinistres dont le score dépasse un seuil, et cite les garages qui y ont contribué. On suit le rappel sur les fraudes confirmées et la stabilité de la liste des garages actifs entre deux versions du modèle.

### Crypto — éteindre des flux de données inutiles

Une plateforme d'actifs virtuels agréée par la VARA alimente son agent de surveillance avec un modèle linéaire de score de liquidité, construit sur une soixantaine de flux de marché. Chaque flux a un coût d'exploitation : il faut le surveiller, le valider et l'archiver. Le modèle est entraîné avec ISTA, le pas proximal du squelette, et une pénalité L1 réglée sur un jeu de validation : les flux dont le poids sort exactement nul sont retirés du pipeline, ce qu'une pénalité L2 ou un sous-gradient n'auraient jamais permis de décider proprement. La plateforme vérifie aussi que retirer un flux ne fait pas baisser le rappel sur les incidents passés avant de l'éteindre en production. Sans cette sélection, l'équipe d'astreinte doit surveiller des dizaines de flux dont aucun ne change le score. On suit le nombre de flux actifs, le rappel sur les incidents de liquidité et le délai de détection.

### Secteur public — choisir λ sur la validation, pas sur l'entraînement

Une entité de services publics en ligne, accessible par UAE Pass, entraîne un classifieur d'intentions bilingue qui oriente les demandes des usagers vers le bon service, avec peu d'exemples par intention. L'équipe compare cinq valeurs de λ pour une pénalité L2 : sur les données d'entraînement, la meilleure perte est toujours obtenue avec λ = 0, parce que la pénalité ne peut qu'augmenter la perte d'entraînement. Le choix se fait donc sur un jeu de validation séparé, composé de demandes réelles pseudonymisées au titre de la PDPL, en arabe et en anglais. La valeur retenue sacrifie un peu de précision sur l'entraînement pour gagner sur des demandes jamais vues, ce qui est exactement le but. Sans cette discipline, l'équipe aurait déployé le modèle le plus sur-appris, et l'agent aurait mal orienté les reformulations. On suit l'exactitude du routage sur des demandes récentes et le taux de transfert vers un conseiller humain.

## Pièges et limites

- **Implémenter L1 par un simple sous-gradient.** Les poids oscillent dans une bande de largeur ηλ autour de 0 sans jamais s'éteindre ; il faut le pas proximal (seuillage doux).
- **Mélanger les conventions λw² et λw²/2.** La première retire 2ηλw par pas, la seconde ηλw : un λ recopié d'un article à l'autre peut être deux fois trop fort.
- **Croire que la décroissance des poids est toujours de la L2.** Ce n'est vrai que pour la descente de gradient simple ; avec Adam, il faut AdamW (point 2).
- **Régulariser sans normaliser les entrées.** La même pénalité écrase les poids des entrées à petite échelle et épargne ceux des entrées à grande échelle ; on normalise d'abord, et on ne pénalise généralement pas le biais.
- **Choisir λ sur les données d'entraînement.** Le meilleur λ y vaut toujours 0 ; on le choisit sur un jeu de validation.

### Exercice feuille blanche

1. Sans regarder le code, écrire `seuillage_doux(z, seuil)` à partir de la formule, puis prédire S₀,₁(−0,3) et S₀,₁(0,07). (Réponse : −0,2 et 0.)
2. Avec ŵ = (2,0 ; 0,3 ; 0,04) et des colonnes orthogonales, prédire les poids du lasso pour λ = 0,35. (Réponse : (1,65 ; 0 ; 0).)
3. Trouver le bug : `return max(abs(z) - seuil, 0.0)`. Pour quelles valeurs de z le résultat est-il faux, et quel `assert` du programme échoue ?

## Pour aller plus loin

L2 correspond à une loi a priori gaussienne sur les poids et L1 à une loi de Laplace : minimiser la perte pénalisée revient à chercher le maximum a posteriori. La géométrie explique la sparsité : la boule L1 a des coins sur les axes, où l'optimum tombe souvent, alors que la boule L2 est ronde. FISTA accélère ISTA en ajoutant un terme d'inertie, et la descente par coordonnées, qui applique le seuillage doux à un poids à la fois, est l'algorithme le plus courant pour le lasso.

> Suite : [Projet final : un agent depuis une feuille blanche](<../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) — étape 77.
