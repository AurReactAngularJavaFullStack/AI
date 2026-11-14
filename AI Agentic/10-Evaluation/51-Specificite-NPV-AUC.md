# Étape 51 — Spécificité, NPV et AUC-ROC — Métriques Complètes d'Évaluation Agentique

> Étape 51 du parcours · Prérequis : [Précision, rappel, F1 et KL](<50-Precision-Rappel-F1-et-KL.md>) · Suite : [Perplexité](<52-Perplexite-LLM.md>)

**Dossier :** 10-Evaluation  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers

## Définition

La **spécificité** (taux de vrais négatifs) mesure la part des cas réellement négatifs que l'agent laisse tranquilles : sur les paiements honnêtes, combien ne sont pas accusés. La **NPV**, en français **VPN** (valeur prédictive négative), mesure la fiabilité d'un verdict négatif : quand l'agent dit « pas de fraude », a-t-il raison ? L'**accuracy** compte toutes les bonnes réponses sans distinguer les classes, ce qui la rend trompeuse sur un événement rare. La **courbe ROC** trace le taux de vrais positifs contre le taux de faux positifs quand le seuil de décision varie, et l'**AUC** est l'aire sous cette courbe : elle juge l'ordre des scores, avant tout choix de seuil. La précision (VPP) et la VPN dépendent de la **prévalence**, la part de vrais positifs dans la population, et le théorème de Bayes dit exactement comment.

## Rôle dans un agent

Ces mesures complètent l'étape 50 au moment **observer** de la boucle, pour tout composant qui produit un score puis une décision : détecteur de fraude, détecteur d'injection d'un garde-fou, filtre de données personnelles, juge qui déclare une réponse fidèle. La spécificité compte quand un faux positif a un coût humain : un client honnête bloqué, un citoyen dont le dossier est refusé. L'AUC sert **avant** de décider : elle compare deux modèles de score sans dépendre du seuil, puis on choisit le seuil sur la courbe ROC. La formule de Bayes sert au moment de **déployer** : un détecteur mesuré sur une population doit être recalculé pour une autre population où la prévalence n'est pas la même (un autre produit, un autre émirat, une période de fraude massive).

## Équation complète

La matrice de confusion a les lignes pour la réalité et les colonnes pour la prédiction, comme dans scikit-learn et à l'étape 50 :

$$
\begin{array}{c|cc}
 & \text{prédit positif} & \text{prédit négatif} \\ \hline
\text{réel positif} & TP & FN \\
\text{réel négatif} & FP & TN
\end{array}
$$

Les sept formules :

$$
\text{Spécificité} = \frac{TN}{TN + FP} = 1 - \text{FPR}
$$

$$
\text{NPV} = \frac{TN}{TN + FN}
$$

$$
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
$$

$$
\text{FPR} = \frac{FP}{FP + TN} = 1 - \text{Spécificité}
$$

$$
\text{TPR} = \frac{TP}{TP + FN} = \text{Rappel}
$$

$$
\text{AUC} = \int_{0}^{1} \text{TPR}\bigl(\text{FPR}^{-1}(t)\bigr) \, dt
$$

Interprétation probabiliste, avec le terme des égalités :

$$
\text{AUC} = P\bigl(s^+ > s^-\bigr) + \tfrac{1}{2}\,P\bigl(s^+ = s^-\bigr)
$$

VPP (précision) et VPN en fonction de la sensibilité Se, de la spécificité Sp et de la prévalence π :

$$
\text{VPP} = \frac{Se\,\pi}{Se\,\pi + (1 - Sp)(1 - \pi)}
\qquad
\text{VPN} = \frac{Sp\,(1 - \pi)}{Sp\,(1 - \pi) + (1 - Se)\,\pi}
$$

## Décryptage des symboles

$$
TP,\; FP,\; FN,\; TN
$$

**Sens :** les quatre cases de la matrice de confusion (étape 50) ; TN compte les négatifs réels laissés tranquilles · **Type / plage :** entiers ≥ 0 · **Variable Python :** les clés `"TP"`, `"FP"`, `"FN"`, `"TN"` du dictionnaire renvoyé par `matrice_confusion`.

$$
Se = \text{TPR} = \text{Rappel}
$$

**Sens :** sensibilité, part des positifs réels détectés · **Type / plage :** réel dans [0, 1] · **Variable Python :** `rappel(m)`.

$$
Sp
$$

**Sens :** spécificité, part des négatifs réels laissés tranquilles · **Type / plage :** réel dans [0, 1] · **Variable Python :** `specificite(m)`.

$$
\text{FPR}
$$

**Sens :** taux de faux positifs, part des négatifs réels accusés à tort ; c'est l'abscisse de la courbe ROC · **Type / plage :** réel dans [0, 1] · **Variable Python :** `fpr(m)`.

$$
\text{VPP},\; \text{NPV} = \text{VPN}
$$

**Sens :** fiabilité d'un verdict positif (c'est la précision) et d'un verdict négatif · **Type / plage :** réels dans [0, 1], `None` si l'agent n'a jamais rendu ce verdict · **Variable Python :** `precision(m)`, `vpn(m)`, et `vpp_bayes`, `vpn_bayes` pour une autre prévalence.

$$
\pi
$$

**Sens :** prévalence, part des positifs réels dans la population (ici, π ne désigne rien d'autre) · **Type / plage :** réel dans [0, 1] · **Variable Python :** `prevalence`.

$$
s^+,\; s^-
$$

**Sens :** score d'un positif tiré au hasard et score d'un négatif tiré au hasard · **Type / plage :** réels, dans n'importe quelle échelle : seul l'ordre compte · **Variable Python :** les listes `scores_pos` et `scores_neg`.

$$
n^+,\; n^-
$$

**Sens :** nombres de positifs et de négatifs réels du jeu d'évaluation · **Type / plage :** entiers > 0 pour que la ROC existe · **Variable Python :** `n_pos`, `n_neg`.

$$
\text{AUC}
$$

**Sens :** aire sous la courbe ROC ; 1 = scores parfaitement ordonnés, 0,5 = ordre aléatoire, 0 = ordre parfaitement inversé · **Type / plage :** réel dans [0, 1] · **Variable Python :** `auc_paires(...)` ou `auc_trapezes(courbe_roc(...))`.

## Démonstration

### 1. Spécificité et FPR se complètent, TPR est le rappel

Spécificité et FPR ont le même dénominateur, TN + FP, le nombre de négatifs réels. Leurs numérateurs se partagent ces négatifs, donc

$$
\text{Spécificité} + \text{FPR} = \frac{TN}{TN + FP} + \frac{FP}{FP + TN} = \frac{TN + FP}{TN + FP} = 1
$$

TPR et rappel sont la même fraction, TP / (TP + FN). La courbe ROC porte donc en abscisse 1 − Sp et en ordonnée Se.

### 2. L'accuracy est une moyenne pondérée par la prévalence

On note N le nombre total de cas et π = (TP + FN)/N la prévalence observée. On multiplie et on divise chaque terme par son nombre de cas réels :

$$
\text{Accuracy} = \frac{TP}{N} + \frac{TN}{N} = \frac{TP + FN}{N}\cdot\frac{TP}{TP + FN} + \frac{TN + FP}{N}\cdot\frac{TN}{TN + FP} = \pi\,Se + (1 - \pi)\,Sp
$$

Sur un événement rare, π est petit et l'accuracy vaut presque Sp, quelle que soit la sensibilité. L'agent qui dit toujours « pas de fraude » a Se = 0 et Sp = 1, donc une accuracy de 1 − π : 0,990 quand une transaction sur cent est frauduleuse. L'accuracy félicite celui qui ne fait rien.

### 3. VPP et VPN par Bayes : l'effet du taux de base

On cherche la probabilité qu'un paiement soit frauduleux sachant qu'il a déclenché une alerte. Le théorème de Bayes donne

$$
P(\text{fraude} \mid \text{alerte}) = \frac{P(\text{alerte} \mid \text{fraude})\,P(\text{fraude})}{P(\text{alerte})}
$$

Le numérateur vaut Se·π. Une alerte vient soit d'une fraude détectée, soit d'un honnête accusé, d'où la loi des probabilités totales :

$$
P(\text{alerte}) = Se\,\pi + (1 - Sp)(1 - \pi)
$$

On obtient la formule de la VPP. Le même raisonnement sur « pas d'alerte », dont la probabilité vaut Sp(1 − π) + (1 − Se)π, donne la VPN.

**Sens de variation.** En divisant numérateur et dénominateur par Se·π :

$$
\text{VPP} = \frac{1}{1 + \dfrac{1 - Sp}{Se}\cdot\dfrac{1 - \pi}{\pi}}
\qquad
\text{VPN} = \frac{1}{1 + \dfrac{1 - Se}{Sp}\cdot\dfrac{\pi}{1 - \pi}}
$$

Le rapport (1 − π)/π diminue quand π augmente, donc la VPP **augmente** avec la prévalence ; le rapport π/(1 − π) augmente, donc la VPN **diminue**. À détecteur identique (Se et Sp fixes), la fiabilité de ses verdicts change avec la population. C'est l'**effet du taux de base** : l'ancienne version de ce fichier l'appelait « paradoxe de la précision », ce qui désigne autre chose. Un bon rappel et une bonne spécificité peuvent donc coexister avec une précision faible quand la prévalence est faible.

**Avec les nombres de l'exemple.** Se = 5/10 = 0,5 et Sp = 987/990 = 0,99697. À π = 0,01, la VPP vaut 0,005 / (0,005 + 0,00303 × 0,99) = 0,005 / 0,008 = 0,625 : on retrouve exactement la précision comptée. À π = 0,001, la VPP tombe à 0,142 : six alertes sur sept accusent un honnête. À π = 0,5, la VPN tombe de 0,995 à 0,666 : le même « pas de fraude » ne vaut plus grand-chose quand une transaction sur deux est frauduleuse.

### 4. L'AUC est la probabilité qu'un positif batte un négatif

On trie les scores par ordre décroissant et on fait descendre le seuil. Chaque fois que le seuil franchit une valeur v portée par a positifs et b négatifs, le point de la courbe passe de (x, y) à (x + b/n⁻, y + a/n⁺). Si a = 0, on avance à l'horizontale ; si b = 0, à la verticale ; si les deux sont non nuls (des scores égaux), en diagonale.

L'aire sous ce segment est celle d'un trapèze de largeur b/n⁻ et de hauteurs y et y + a/n⁺ :

$$
\frac{b}{n^-}\cdot\frac{y + \left(y + \dfrac{a}{n^+}\right)}{2} = \frac{1}{n^+ n^-}\; b\left(n^+ y + \frac{a}{2}\right)
$$

Or n⁺·y est le nombre de positifs dont le score est **strictement supérieur** à v, parce que ce sont exactement ceux déjà franchis. Le segment contribue donc, pour chacun des b négatifs de score v, le nombre de positifs qui le battent, plus la moitié des positifs à égalité avec lui. En additionnant tous les segments :

$$
\text{AUC} = \frac{1}{n^+ n^-} \sum_{\text{négatifs } j} \Bigl( \#\{i : s_i^+ > s_j^-\} + \tfrac{1}{2}\,\#\{i : s_i^+ = s_j^-\} \Bigr)
$$

Il y a n⁺n⁻ paires (positif, négatif). La somme compte une victoire pour chaque paire bien ordonnée et une demi-victoire pour chaque égalité : c'est P(s⁺ > s⁻) + ½ P(s⁺ = s⁻). Le numérateur est la statistique U de Mann-Whitney. L'ancienne formule oubliait le terme ½ P(s⁺ = s⁻) : elle n'est juste que si aucun score n'est égal entre un positif et un négatif.

### 5. Ce que l'AUC voit et ne voit pas

- **Seul l'ordre compte.** Une transformation strictement croissante des scores (les mettre au cube, appliquer une sigmoïde) ne change aucune comparaison s⁺ > s⁻, donc ne change pas l'AUC.
- **Inverser l'ordre donne 1 − AUC.** Avec les scores 1 − s, chaque victoire devient une défaite et inversement ; les égalités restent des demi-points. La somme passe de U à n⁺n⁻ − U.
- **Un score au hasard vaut 0,5.** Si les scores des positifs et des négatifs ont la même loi, P(s⁺ > s⁻) = P(s⁻ > s⁺) par symétrie, et les deux probabilités, plus celle de l'égalité, somment à 1 : l'AUC vaut ½.
- **L'AUC ne dépend pas de la prévalence**, parce qu'elle compare un positif à un négatif ; la VPP en dépend (point 3). Un détecteur garde son AUC d'un produit à l'autre, pas sa précision.

### 6. Exemple fait à la main (le code reprend ces nombres)

Un agent de fraude regarde 1 000 paiements : 10 sont frauduleux, 990 ne le sont pas. Il en marque 8, dont 5 vraies fraudes. Il laisse donc passer 5 fraudes et accuse 3 honnêtes : TP = 5, FP = 3, FN = 5, TN = 987.

- Précision = 5 / 8 = 0,625 : quand il crie « fraude », il a raison un peu plus d'une fois sur deux.
- Rappel = 5 / 10 = 0,50 : il voit la moitié des fraudes.
- Spécificité = 987 / 990 = 0,997 : sur les paiements honnêtes, il se tait presque toujours.
- VPN = 987 / 992 = 0,995 : son « pas de fraude » est presque toujours juste, surtout parce que les fraudes sont rares.
- Accuracy = 992 / 1 000 = 0,992, à peine mieux que l'agent paresseux (0,990).

Ces nombres ne parlent pas de la même chose, et c'est pour cela qu'ils peuvent être vrais en même temps. La spécificité se lit sur la **ligne** des négatifs réels (TN et FP). La précision se lit sur la **colonne** des positifs annoncés (TP et FP). L'ancienne version inversait lignes et colonnes par rapport à la matrice de scikit-learn qu'elle utilisait.

Pour l'AUC, quatre paiements : honnête 0,1, fraude 0,4, honnête 0,6, fraude 0,9. Il y a 2 × 2 = 4 paires fraude contre honnête : 0,9 bat 0,1 et 0,6 ; 0,4 bat 0,1 et perd contre 0,6. L'AUC vaut 3/4 = 0,75. Si l'honnête à 0,6 avait le score 0,4, la paire (0,4 ; 0,4) serait une égalité : (3 + 0,5)/4 = 0,875. La courbe ROC passe alors par (0 ; 0), (0 ; 0,5), (0,5 ; 1) et (1 ; 1), et ses trapèzes donnent 0 + 0,5 × 1,5/2 + 0,5 × 1 = 0,875. À un seuil de 0,3 sur le premier exemple, l'agent marque les trois plus hauts scores : TPR = 1, FPR = 0,5 ; à 0,7, il ne marque que 0,9 : TPR = 0,5, FPR = 0.

## Effets et comportement

- **Baisser le seuil** déplace le point de fonctionnement vers le haut et la droite de la courbe ROC : plus de fraudes vues (TPR monte), plus d'honnêtes accusés (FPR monte, spécificité baisse).
- **Une prévalence qui baisse** fait chuter la VPP et monter la VPN, sans que le modèle change.
- **Un excellent rappel et une excellente spécificité** peuvent coexister avec une précision faible quand la prévalence est faible : c'est l'effet du taux de base, pas un défaut du calcul.
- **L'AUC reste indépendante du seuil** et de la prévalence ; elle ne dit rien du coût d'une erreur au seuil retenu.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| TP, FP, FN, TN | `matrice_confusion(y_vrai, y_pred)` |
| Spécificité, FPR | `specificite(m)`, `fpr(m)` |
| NPV (VPN), VPP | `vpn(m)`, `precision(m)` |
| Accuracy | `accuracy(m)` |
| TPR = Se | `rappel(m)` |
| courbe ROC | `courbe_roc(y_vrai, scores)` |
| AUC (intégrale) | `auc_trapezes(points)` |
| AUC (probabilité) | `auc_paires(scores_pos, scores_neg)` |
| VPP, VPN selon π | `vpp_bayes(se, sp, prevalence)`, `vpn_bayes(se, sp, prevalence)` |

### Déroulé, ligne par ligne

**`matrice_confusion(y_vrai, y_pred)`**.

- La garde de longueur refuse deux listes de tailles différentes, que `zip` tronquerait en silence.
- Chaque étiquette doit valoir 0 ou 1, sinon `ValueError`.
- `cle = ("T" if v == p else "F") + ("P" if p == 1 else "N")` : la première lettre dit si la prédiction est juste, la seconde ce qui a été prédit. Un honnête accusé (v = 0, p = 1) donne `"FP"`.
- Sur les 1 000 paiements, le dictionnaire vaut `{'TP': 5, 'FP': 3, 'FN': 5, 'TN': 987}`.

**`ratio(num, den)`** renvoie `None` si le dénominateur est nul : c'est la convention du parcours. Les six métriques de base l'appellent avec la bonne ligne ou la bonne colonne : `specificite` fait 987 / 990 = 0,99697, `vpn` 987 / 992 = 0,99496, `fpr` 3 / 990 = 0,00303, `accuracy` 992 / 1 000.

**`courbe_roc(y_vrai, scores)`**.

- `n_pos` et `n_neg` comptent les deux classes. Si l'une est vide, la fonction renvoie `None` : sans positif ou sans négatif, aucun taux ne se calcule.
- `par_score` regroupe les cas par valeur de score : pour chaque score, `[a, b]` compte les positifs et les négatifs qui le portent. Sur l'exemple à égalité, le score 0,4 porte `[1, 1]`.
- La boucle parcourt les scores du plus haut au plus bas, ajoute `a` à `tp` et `b` à `fp`, et pose le point `(fp / n_neg, tp / n_pos)`. Le score 0,9 donne (0 ; 0,5), le score 0,4 donne (0,5 ; 1) d'un seul pas en diagonale, le score 0,1 donne (1 ; 1).

**`auc_trapezes(points)`** additionne `(x1 - x0) * (y0 + y1) / 2` sur chaque segment : 0 pour le segment vertical, 0,5 × 1,5 / 2 = 0,375 pour la diagonale, 0,5 × 2 / 2 = 0,5 pour le dernier, total 0,875.

**`auc_paires(scores_pos, scores_neg)`** renvoie `None` si une liste est vide. La double boucle fabrique les n⁺n⁻ paires : `sp > sn` ajoute 1, `sp == sn` ajoute 0,5. La division par `len(scores_pos) * len(scores_neg)` donne la probabilité.

**`vpp_bayes` et `vpn_bayes`** écrivent les deux formules de Bayes ; `None` si le dénominateur est nul (prévalence et taux qui ne laissent aucune alerte possible).

**`main()`**, bloc par bloc.

1. On construit les 1 000 étiquettes : 10 fraudes puis 990 honnêtes, et les 1 000 prédictions dans le même ordre. Les `assert` vérifient les quatre compteurs, puis 0,625, 0,50, 0,997, 0,995 et 0,992 arrondis à trois décimales, et Sp + FPR = 1.
2. L'agent paresseux : accuracy 0,990, rappel 0, précision `None`. Puis l'identité accuracy = π·Se + (1 − π)·Sp, à 1e-12 près.
3. Les prévalences 0,001, 0,01 et 0,5. À 0,01, `vpp_bayes` et `vpn_bayes` retrouvent exactement les comptes ; à 0,5, la VPN vaut 0,666 ; à 0,001, la VPP vaut 0,142.
4. L'AUC par les paires (0,75 sans égalité, 0,875 avec), la même valeur par les trapèzes, puis les deux seuils 0,3 et 0,7.
5. Cent dossiers tirés avec `random.seed(7)` : les positifs ont un score décalé de 0,3, et l'arrondi à une décimale crée beaucoup d'égalités. Les paires et les trapèzes donnent la même AUC à 1e-12 près ; les scores au cube aussi ; les scores inversés donnent 1 − AUC.
6. Une seule classe donne `None` ; une étiquette 2 lève `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`matrice_confusion(y_vrai, y_pred)`** — Cette fonction est le greffier du tribunal des paiements, qui range chaque verdict dans l'une des quatre cases de son registre : elle reçoit la liste des étiquettes réelles et celle des prédictions, refuse par une `ValueError` deux listes de longueurs différentes ou une étiquette autre que 0 ou 1, puis, pour chaque couple, forme une clé de deux lettres, T ou F selon que la prédiction est juste, P ou N selon ce qui a été prédit, et incrémente le compteur correspondant. Elle renvoie le dictionnaire des quatre compteurs, `{'TP': 5, 'FP': 3, 'FN': 5, 'TN': 987}` pour les 1 000 paiements dont 10 fraudes, et c'est de ce registre que partent toutes les métriques du fichier.

**`precision(m)`** — Cette fonction, qu'on appelle aussi valeur prédictive positive, est l'enquêtrice qui relit seulement les dossiers où l'agent a sonné l'alarme : elle reçoit le dictionnaire de la matrice de confusion et confie à `ratio` la division de TP par TP + FP, la colonne des alertes. Elle renvoie donc la part des alertes qui étaient de vraies fraudes, 5 sur 8, soit 0,625 pour l'agent de fraude, ou `None` quand l'agent n'a jamais rien signalé, comme l'agent paresseux de la section 2 qui répond toujours « pas de fraude » ; `main` la compare ensuite à la VPP calculée par Bayes.

**`rappel(m)`** — Celle-ci, la sensibilité ou TPR, est le chasseur qui compte combien de loups il a ramenés sur tous ceux qui rôdaient dans la forêt : elle reçoit la matrice et renvoie, par `ratio`, TP ÷ (TP + FN), la part des vraies fraudes que l'agent a attrapées, ou `None` s'il n'y en avait aucune. L'agent de fraude en voit 5 sur 10 et obtient 0,50, l'agent paresseux 0 sur 10 ; `main` l'utilise aussi comme sensibilité dans les formules de Bayes et comme ordonnée TPR quand il vérifie les points de la courbe ROC aux seuils 0,3 et 0,7.

**`specificite(m)`** — Cette fonction est le pendant de la précédente du côté des innocents : comme un portier qui compte les clients honnêtes qu'il a laissés entrer sans les fouiller, elle reçoit la matrice et renvoie, par `ratio`, TN ÷ (TN + FP), la part des paiements honnêtes que l'agent a bien laissés passer, ou `None` sans aucun cas négatif. Pour l'agent de fraude, 987 honnêtes sur 990 sont épargnés, ce qui donne 0,99697, arrondi à 0,997 ; `main` vérifie que spécificité et FPR somment à 1 et s'en sert comme Sp dans `vpp_bayes` et `vpn_bayes`.

**`vpn(m)`** — Celle-ci, la valeur prédictive négative, répond à la question du client rassuré : « l'agent m'a dit que tout allait bien, puis-je le croire ? » Elle reçoit la matrice et renvoie, par `ratio`, TN ÷ (TN + FN), la part des « pas de fraude » qui étaient vraiment des paiements honnêtes, ou `None` si l'agent n'a jamais prononcé ce verdict. Avec 987 vrais négatifs sur 992 réponses négatives, elle vaut 0,99496, arrondi à 0,995, et `main` vérifie que `vpn_bayes` retrouve exactement ce nombre à la prévalence 0,01.

**`fpr(m)`** — Cette fonction est le registre des fausses accusations : elle reçoit la matrice et renvoie, par `ratio`, FP ÷ (FP + TN), la part des paiements honnêtes que l'agent a pris à tort pour des fraudes, ou `None` s'il n'y a aucun négatif. Ici, 3 honnêtes accusés sur 990 donnent 0,00303, exactement le complément à 1 de la spécificité, ce que `main` vérifie à 10⁻¹² près ; c'est aussi l'abscisse de chaque point de la courbe ROC, et `main` contrôle qu'elle vaut 0,5 au seuil 0,3 et 0 au seuil 0,7 sur le petit exemple à quatre dossiers.

**`accuracy(m)`** — Celle-ci est le bulletin de notes global, qui compte les bonnes réponses sans regarder de quel côté elles tombent : elle reçoit la matrice, additionne TP et TN et les divise, par `ratio`, par le total des quatre compteurs, en renvoyant `None` pour une matrice vide. L'agent de fraude obtient 992 sur 1 000, soit 0,992, mais l'agent paresseux qui ne signale jamais rien obtient 0,99 sans attraper une seule fraude : c'est tout l'avertissement de la section 2, où `main` vérifie aussi l'identité accuracy = π·Se + (1 − π)·Sp avec π = 0,01.

**`courbe_roc(y_vrai, scores)`** — Cette fonction promène un curseur de seuil du haut vers le bas, comme un douanier qui deviendrait de moins en moins exigeant : elle reçoit les étiquettes et les scores, refuse deux listes de longueurs différentes, renvoie `None` si l'une des deux classes est absente, puis regroupe les dossiers par valeur de score en comptant positifs et négatifs pour chacune. Parcourant les scores du plus haut au plus bas, elle cumule vrais et faux positifs et ajoute à chaque palier le point (FPR, TPR), en partant de (0, 0) ; les dossiers à égalité avancent ensemble en diagonale. Sur l'exemple à quatre dossiers, elle renvoie les points (0, 0), (0 ; 0,5), (0,5 ; 1) et (1, 1), que `auc_trapezes` transforme en aire.

**`auc_trapezes(points)`** — Celle-ci est l'arpenteur qui mesure la surface d'un champ bordé d'une clôture en ligne brisée : elle reçoit la liste ordonnée des points de la courbe ROC, prend chaque segment entre deux points consécutifs et additionne l'aire du trapèze qu'il délimite au-dessus de l'axe, (x₁ − x₀)(y₀ + y₁) ÷ 2. Elle renvoie cette somme sans aucune vérification ; sur l'exemple à égalité, le segment vertical vaut 0, la diagonale 0,375 et le dernier 0,5, total 0,875, exactement l'AUC que `auc_paires` obtient en comptant les paires, et sur les 100 dossiers tirés au hasard les deux méthodes donnent 0,7977.

**`auc_paires(scores_pos, scores_neg)`** — Cette fonction organise un tournoi où chaque vraie fraude affronte chaque paiement honnête : elle reçoit les scores des positifs et ceux des négatifs, renvoie `None` si l'une des listes est vide, puis parcourt toutes les paires, accorde un point quand le positif a le score le plus haut et un demi-point en cas d'égalité, et divise le total par le nombre de paires. Elle renvoie ainsi la probabilité qu'un positif tiré au hasard soit mieux noté qu'un négatif, la statistique de Mann-Whitney : 0,75 sans égalité, 0,875 avec une égalité, et `main` vérifie qu'elle ne change pas quand on élève les scores au cube et devient 1 − AUC quand on les inverse.

**`vpp_bayes(se, sp, prevalence)`** — Celle-ci répond à la question que pose un enquêteur dans une autre ville, où la fraude est plus rare ou plus fréquente : avec la même machine, quelle part des alertes sera juste ? Elle reçoit la sensibilité, la spécificité et la prévalence π, calcule le numérateur Se·π et le dénominateur Se·π + (1 − Sp)(1 − π), renvoie `None` si ce dénominateur est nul et sinon leur rapport. À π = 0,01, elle retrouve exactement la précision 0,625 des comptes ; à π = 0,001, la même machine ne voit plus juste que dans 0,1418 de ses alertes, et à π = 0,5 dans 0,9940.

**`vpn_bayes(se, sp, prevalence)`** — Cette fonction est la jumelle de la précédente pour les verdicts rassurants : elle reçoit les mêmes trois nombres, calcule Sp(1 − π) au numérateur et Sp(1 − π) + (1 − Se)π au dénominateur, renvoie `None` si celui-ci est nul et sinon la probabilité qu'un « pas de fraude » soit vrai. À π = 0,01 elle redonne la VPN 0,995 des comptes, à π = 0,001 elle monte à 0,9995, mais à π = 0,5 elle tombe à 0,6660, parce qu'une machine qui rate la moitié des fraudes devient peu rassurante quand la fraude est partout.

**`main()`** — C'est le chef d'orchestre des six démonstrations du fichier : il construit les 1 000 paiements, dont 10 fraudes, et vérifie la matrice et les six taux, puis montre que l'agent paresseux atteint 0,99 d'accuracy avec un rappel nul et une précision `None`. Il fait ensuite varier la prévalence de 0,001 à 0,5 dans les formules de Bayes, calcule l'AUC par les paires et par les trapèzes sur le petit exemple, puis sur 100 dossiers tirés avec la graine 7, où l'arrondi crée des égalités, et contrôle l'invariance par les scores au cube et le complément par les scores inversés ; il finit par les cas limites, une seule classe et une étiquette 2, et n'affiche « OK » que si tous les `assert` sont passés.

```python
"""Étape 51 — spécificité, VPN, accuracy, FPR, TPR, courbe ROC et AUC, VPP et VPN par Bayes."""
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def matrice_confusion(y_vrai: list[int], y_pred: list[int]) -> dict[str, int]:
    """Compte TP, FP, FN, TN. Lignes = réalité, colonnes = prédiction (convention scikit-learn)."""
    if len(y_vrai) != len(y_pred):
        raise ValueError("y_vrai et y_pred doivent avoir la même longueur")
    m = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
    for v, p in zip(y_vrai, y_pred):
        if v not in (0, 1) or p not in (0, 1):
            raise ValueError("étiquettes attendues : 0 ou 1")
        cle = ("T" if v == p else "F") + ("P" if p == 1 else "N")
        m[cle] += 1
    return m


def ratio(num: int, den: int) -> float | None:
    """Une métrique sans dénominateur est indéfinie : None, et elle n'entre pas dans les moyennes."""
    return None if den == 0 else num / den


def precision(m: dict[str, int]) -> float | None:      # VPP : valeur prédictive positive
    return ratio(m["TP"], m["TP"] + m["FP"])


def rappel(m: dict[str, int]) -> float | None:         # TPR, sensibilité
    return ratio(m["TP"], m["TP"] + m["FN"])


def specificite(m: dict[str, int]) -> float | None:    # TNR
    return ratio(m["TN"], m["TN"] + m["FP"])


def vpn(m: dict[str, int]) -> float | None:            # valeur prédictive négative
    return ratio(m["TN"], m["TN"] + m["FN"])


def fpr(m: dict[str, int]) -> float | None:            # taux de faux positifs = 1 − spécificité
    return ratio(m["FP"], m["FP"] + m["TN"])


def accuracy(m: dict[str, int]) -> float | None:
    return ratio(m["TP"] + m["TN"], sum(m.values()))


def courbe_roc(y_vrai: list[int], scores: list[float]) -> list[tuple[float, float]] | None:
    """Points (FPR, TPR) quand le seuil descend ; les scores égaux avancent ensemble (segment en diagonale)."""
    if len(y_vrai) != len(scores):
        raise ValueError("longueurs différentes")
    n_pos = sum(y_vrai)
    n_neg = len(y_vrai) - n_pos
    if n_pos == 0 or n_neg == 0:
        return None                                  # une seule classe : ROC et AUC indéfinies
    par_score: dict[float, list[int]] = {}
    for y, s in zip(y_vrai, scores):
        par_score.setdefault(s, [0, 0])[0 if y == 1 else 1] += 1
    tp = fp = 0
    points = [(0.0, 0.0)]
    for s in sorted(par_score, reverse=True):
        a, b = par_score[s]                          # a positifs et b négatifs ont ce score
        tp, fp = tp + a, fp + b
        points.append((fp / n_neg, tp / n_pos))
    return points


def auc_trapezes(points: list[tuple[float, float]]) -> float:
    """Aire sous la ligne brisée : somme des trapèzes (x1 − x0)(y0 + y1)/2."""
    return sum((x1 - x0) * (y0 + y1) / 2 for (x0, y0), (x1, y1) in zip(points, points[1:]))


def auc_paires(scores_pos: list[float], scores_neg: list[float]) -> float | None:
    """P(s+ > s−) + ½ P(s+ = s−), par comptage des n+ × n− paires (statistique de Mann-Whitney)."""
    if not scores_pos or not scores_neg:
        return None
    gagnees = 0.0
    for sp in scores_pos:
        for sn in scores_neg:
            if sp > sn:
                gagnees += 1.0
            elif sp == sn:
                gagnees += 0.5                      # égalité : demi-point, le segment diagonal de la courbe
    return gagnees / (len(scores_pos) * len(scores_neg))


def vpp_bayes(se: float, sp: float, prevalence: float) -> float | None:
    """P(positif | alerte) = Se·π / (Se·π + (1 − Sp)(1 − π))."""
    num = se * prevalence
    den = num + (1 - sp) * (1 - prevalence)
    return None if den == 0 else num / den


def vpn_bayes(se: float, sp: float, prevalence: float) -> float | None:
    """P(négatif | pas d'alerte) = Sp(1 − π) / (Sp(1 − π) + (1 − Se)π)."""
    num = sp * (1 - prevalence)
    den = num + (1 - se) * prevalence
    return None if den == 0 else num / den


def main() -> None:
    print("1. Agent de fraude : 1 000 paiements, 10 fraudes")
    y_vrai = [1] * 10 + [0] * 990
    y_pred = [1] * 5 + [0] * 5 + [1] * 3 + [0] * 987   # 5 fraudes vues, 5 ratées, 3 honnêtes accusés
    m = matrice_confusion(y_vrai, y_pred)
    print(f"  {m}")
    valeurs = {"précision": precision(m), "rappel": rappel(m), "spécificité": specificite(m),
               "VPN": vpn(m), "accuracy": accuracy(m), "FPR": fpr(m)}
    for nom, v in valeurs.items():
        print(f"  {nom:12s} = {v:.4f}")
    assert m == {"TP": 5, "FP": 3, "FN": 5, "TN": 987}
    assert [round(valeurs[k], 3) for k in ("précision", "rappel", "spécificité", "VPN", "accuracy")] \
        == [0.625, 0.50, 0.997, 0.995, 0.992]
    assert abs(specificite(m) + fpr(m) - 1) < 1e-12

    print("2. L'agent qui dit toujours « pas de fraude »")
    paresseux = matrice_confusion(y_vrai, [0] * 1000)
    print(f"  accuracy = {accuracy(paresseux):.3f}   rappel = {rappel(paresseux)}   précision = {precision(paresseux)}")
    assert accuracy(paresseux) == 0.99 and rappel(paresseux) == 0.0 and precision(paresseux) is None
    pi = 10 / 1000                                      # accuracy = π·Se + (1 − π)·Sp
    assert abs(accuracy(m) - (pi * rappel(m) + (1 - pi) * specificite(m))) < 1e-12

    print("3. Bayes : la même machine, trois prévalences")
    se, sp = rappel(m), specificite(m)
    for prev in (0.001, 0.01, 0.5):
        print(f"  π = {prev:<5}  VPP = {vpp_bayes(se, sp, prev):.4f}   VPN = {vpn_bayes(se, sp, prev):.4f}")
    assert abs(vpp_bayes(se, sp, 0.01) - precision(m)) < 1e-12     # retrouve les comptes
    assert abs(vpn_bayes(se, sp, 0.01) - vpn(m)) < 1e-12
    assert round(vpn_bayes(se, sp, 0.5), 3) == 0.666 and round(vpp_bayes(se, sp, 0.001), 3) == 0.142

    print("4. AUC par les paires, avec et sans égalité")
    a1 = auc_paires([0.4, 0.9], [0.1, 0.6])
    a2 = auc_paires([0.4, 0.9], [0.1, 0.4])
    pts = courbe_roc([1, 1, 0, 0], [0.4, 0.9, 0.1, 0.4])
    print(f"  sans égalité : {a1}   avec une égalité : {a2}   trapèzes : {auc_trapezes(pts)}")
    print(f"  points ROC : {pts}")
    assert a1 == 0.75 and a2 == 0.875 and auc_trapezes(pts) == 0.875
    for seuil, attendu in ((0.3, (0.5, 1.0)), (0.7, (0.0, 0.5))):
        mm = matrice_confusion([0, 1, 0, 1], [int(s >= seuil) for s in (0.1, 0.4, 0.6, 0.9)])
        print(f"  seuil {seuil} : FPR = {fpr(mm)}  TPR = {rappel(mm)}")
        assert (fpr(mm), rappel(mm)) == attendu

    print("5. 100 dossiers tirés au hasard (graine 7), scores arrondis : beaucoup d'égalités")
    random.seed(7)
    y = [1] * 40 + [0] * 60
    s = [round(random.random() * 0.6 + (0.3 if v else 0.0), 1) for v in y]
    pos = [x for x, v in zip(s, y) if v == 1]
    neg = [x for x, v in zip(s, y) if v == 0]
    a_paires, a_trap = auc_paires(pos, neg), auc_trapezes(courbe_roc(y, s))
    a_cube = auc_paires([x ** 3 for x in pos], [x ** 3 for x in neg])
    a_inverse = auc_paires([1 - x for x in pos], [1 - x for x in neg])
    print(f"  paires = {a_paires:.4f}   trapèzes = {a_trap:.4f}   scores au cube = {a_cube:.4f}   scores inversés = {a_inverse:.4f}")
    assert abs(a_paires - a_trap) < 1e-12 and abs(a_cube - a_paires) < 1e-12
    assert abs(a_inverse - (1 - a_paires)) < 1e-12

    print("6. Cas limites")
    assert courbe_roc([1, 1], [0.2, 0.9]) is None and auc_paires([0.5], []) is None
    try:
        matrice_confusion([0, 2], [0, 1])
    except ValueError:
        print("  étiquette 2 → ValueError ; une seule classe → AUC None")
    else:
        raise AssertionError("une étiquette invalide aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Agent de fraude : 1 000 paiements, 10 fraudes
  {'TP': 5, 'FP': 3, 'FN': 5, 'TN': 987}
  précision    = 0.6250
  rappel       = 0.5000
  spécificité  = 0.9970
  VPN          = 0.9950
  accuracy     = 0.9920
…
  accuracy = 0.990   rappel = 0.0   précision = None
3. Bayes : la même machine, trois prévalences
  π = 0.001  VPP = 0.1418   VPN = 0.9995
  π = 0.01   VPP = 0.6250   VPN = 0.9950
  π = 0.5    VPP = 0.9940   VPN = 0.6660
4. AUC par les paires, avec et sans égalité
  sans égalité : 0.75   avec une égalité : 0.875   trapèzes : 0.875
  points ROC : [(0.0, 0.0), (0.0, 0.5), (0.5, 1.0), (1.0, 1.0)]
…
  paires = 0.7977   trapèzes = 0.7977   scores au cube = 0.7977   scores inversés = 0.2023
OK — toutes les vérifications sont passées.
```

### La même chose avec scikit-learn

L'ancienne version de ce fichier utilisait scikit-learn et importait NumPy sans s'en servir. Voici l'extrait corrigé, à titre de comparaison ; il n'est pas exécuté par le harnais.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`metriques_completes(y_true, y_pred, y_scores)`** — Cette fonction est le même greffier que dans le programme précédent, mais qui confie le comptage à scikit-learn : elle reçoit les étiquettes réelles, les prédictions et, facultativement, des scores, demande à `confusion_matrix` une matrice forcée en 2 × 2 grâce à `labels=[0, 1]`, pour que le déballage en quatre compteurs tienne même sur un lot à une seule classe, puis remplit un dictionnaire avec TP, TN, FP, FN, la précision, le rappel, la spécificité, la NPV et l'accuracy. Elle n'ajoute l'AUC-ROC, calculée par `roc_auc_score`, que si des scores sont fournis et que les deux classes sont présentes, et renvoie ce dictionnaire ; l'extrait sert de comparaison et n'est pas exécuté par le harnais.

**`ratio(num, den)`** — Cette fonction interne, qui vit dans `metriques_completes`, est la même petite règle de prudence que la fonction `ratio` du programme précédent : comme un caissier qui refuse de diviser une addition entre zéro convive, elle reçoit un numérateur et un dénominateur, renvoie `None` si le dénominateur est nul et sinon le quotient. Elle ne lève jamais d'exception et sert à chacun des cinq taux du dictionnaire, si bien qu'un lot sans aucune alerte donne une précision indéfinie plutôt qu'un zéro trompeur qui entrerait dans les moyennes.

```python
# [extrait] — version scikit-learn, non exécutée par le harnais (pip install scikit-learn)
from sklearn.metrics import confusion_matrix, roc_auc_score


def metriques_completes(y_true, y_pred, y_scores=None):
    # labels=[0, 1] force une matrice 2 × 2 même si le lot ne contient qu'une seule classe :
    # sans lui, ravel() ne renvoie qu'un nombre et le déballage en quatre variables plante.
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    def ratio(num, den):
        return None if den == 0 else num / den

    resultats = {
        "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "Précision": ratio(tp, tp + fp),
        "Rappel (TPR)": ratio(tp, tp + fn),
        "Spécificité (TNR)": ratio(tn, tn + fp),
        "NPV": ratio(tn, tn + fn),
        "Accuracy": ratio(tp + tn, tp + tn + fp + fn),
    }
    if y_scores is not None and 0 < sum(y_true) < len(y_true):   # l'AUC exige les deux classes
        resultats["AUC-ROC"] = roc_auc_score(y_true, y_scores)   # gère les égalités avec le demi-point
    return resultats
```

## Squelette algorithmique

Trois algorithmes portent ce fichier : le comptage de la matrice et des taux, le tracé de la courbe ROC avec son aire, et le comptage des paires qui donne la même aire par un autre chemin.

### Matrice de confusion et les taux qui en sortent

Entrées : deux listes de même longueur N, les étiquettes réelles et les prédictions, en 0 et 1. Sorties : les quatre compteurs et les six taux, chacun indéfini si son dénominateur est nul. L'idée : un passage pour compter, puis des divisions qui lisent chacune une ligne, une colonne ou le total de la matrice.

```text
ALGORITHME MatriceEtTaux
ENTRÉES : y_vrai[1..N], y_pred[1..N], valeurs dans {0, 1}
SORTIE : TP, FP, FN, TN et les taux
  SI longueur(y_vrai) ≠ longueur(y_pred) ALORS
    SIGNALER UNE ERREUR « longueurs différentes »
  FIN SI
  TP ← 0 ; FP ← 0 ; FN ← 0 ; TN ← 0
  POUR i DE 1 À N FAIRE
    SI y_vrai[i] ∉ {0, 1} OU y_pred[i] ∉ {0, 1} ALORS
      SIGNALER UNE ERREUR « étiquette invalide »
    FIN SI
    SI y_pred[i] = 1 ALORS
      SI y_vrai[i] = 1 ALORS TP ← TP + 1 SINON FP ← FP + 1 FIN SI
    SINON
      SI y_vrai[i] = 1 ALORS FN ← FN + 1 SINON TN ← TN + 1 FIN SI
    FIN SI
  FIN POUR
  Spécificité ← TN / (TN + FP)          VPN ← TN / (TN + FN)
  FPR ← FP / (FP + TN)                  TPR ← TP / (TP + FN)
  VPP ← TP / (TP + FP)                  Accuracy ← (TP + TN) / N
  (chaque taux vaut INDÉFINI si son dénominateur est nul)
  RETOURNER les compteurs et les taux
```

**Complexité :** O(N) en temps, parce que chaque couple est lu une fois et range un seul compteur ; les six divisions coûtent O(1). La mémoire est en O(1) en plus des listes d'entrée : quatre compteurs.

**Du squelette au code :** la garde de longueur, la garde d'étiquette et la boucle de comptage sont `matrice_confusion`, où la clé `("T" if v == p else "F") + ("P" if p == 1 else "N")` remplace les quatre branches du `SI` par une seule ligne. Chaque taux est une fonction d'une ligne (`specificite`, `vpn`, `fpr`, `rappel`, `precision`, `accuracy`) qui appelle `ratio`, et c'est `ratio` qui renvoie `None` pour INDÉFINI.

### Courbe ROC et AUC par les trapèzes

Entrées : N étiquettes réelles et N scores. Sorties : la liste des points (FPR, TPR) et l'aire sous la courbe, ou indéfini s'il manque une classe. L'idée : faire descendre le seuil d'un score distinct au suivant ; les cas qui portent le même score avancent ensemble, ce qui trace un segment en diagonale et compte automatiquement les égalités pour moitié.

```text
ALGORITHME CourbeROCEtAUC
ENTRÉES : y[1..N] ∈ {0, 1}, s[1..N] réels
SORTIE : points, AUC, ou INDÉFINI
  n⁺ ← Σ y[i] ; n⁻ ← N − n⁺
  SI n⁺ = 0 OU n⁻ = 0 ALORS
    RETOURNER INDÉFINI
  FIN SI
  groupes ← dictionnaire vide                       (score → [nombre de positifs, nombre de négatifs])
  POUR i DE 1 À N FAIRE
    SI y[i] = 1 ALORS groupes[s[i]].positifs ← +1 SINON groupes[s[i]].négatifs ← +1 FIN SI
  FIN POUR
  TP ← 0 ; FP ← 0 ; points ← [(0, 0)] ; AUC ← 0
  POUR chaque score v de groupes, du plus grand au plus petit FAIRE
    (a, b) ← groupes[v]
    (x₀, y₀) ← dernier point de points
    TP ← TP + a ; FP ← FP + b
    (x₁, y₁) ← (FP / n⁻, TP / n⁺)
    ajouter (x₁, y₁) à points
    AUC ← AUC + (x₁ − x₀) · (y₀ + y₁) / 2            (aire du trapèze sous ce segment)
  FIN POUR
  RETOURNER points, AUC
```

**Complexité :** le regroupement coûte O(N) en moyenne, parce que chaque cas fait une insertion dans un dictionnaire ; le tri des D scores distincts coûte O(D log D), au plus O(N log N) ; la dernière boucle coûte O(D). Le temps total est donc O(N log N). La mémoire est en O(D) pour les groupes et les points, avec D ≤ N.

**Du squelette au code :** n⁺, n⁻ et le retour INDÉFINI sont le début de `courbe_roc`. La première boucle est `par_score.setdefault(s, [0, 0])[0 if y == 1 else 1] += 1`. La seconde est `for s in sorted(par_score, reverse=True)`, qui ajoute `a` et `b` puis le point `(fp / n_neg, tp / n_pos)`. Le programme fait l'accumulation des trapèzes dans une fonction séparée, `auc_trapezes(points)`, qui repasse sur la liste des points : même résultat, un second passage en O(D).

### AUC par le comptage des paires

Entrées : les scores des n⁺ positifs et des n⁻ négatifs. Sortie : l'AUC, ou indéfini si une liste est vide. L'idée : comparer chaque positif à chaque négatif, compter une victoire pour un positif mieux noté et une demi-victoire pour une égalité.

```text
ALGORITHME AUCParPaires
ENTRÉES : s⁺[1..n⁺], s⁻[1..n⁻]
SORTIE : AUC ∈ [0, 1] ou INDÉFINI
  SI n⁺ = 0 OU n⁻ = 0 ALORS
    RETOURNER INDÉFINI
  FIN SI
  gagnées ← 0
  POUR i DE 1 À n⁺ FAIRE
    POUR j DE 1 À n⁻ FAIRE
      SI s⁺[i] > s⁻[j] ALORS
        gagnées ← gagnées + 1
      SINON SI s⁺[i] = s⁻[j] ALORS
        gagnées ← gagnées + 1/2
      FIN SI
    FIN POUR
  FIN POUR
  RETOURNER gagnées / (n⁺ · n⁻)
```

**Complexité :** O(n⁺ · n⁻) en temps, parce que chaque paire est comparée une fois ; la mémoire supplémentaire est en O(1). Sur un jeu de 10 000 positifs et un million de négatifs, cela fait 10¹⁰ comparaisons : trop lent. On passe alors par les rangs, en O(N log N) : on trie tous les scores, on donne aux ex aequo leur rang moyen, et l'AUC vaut (R⁺ − n⁺(n⁺ + 1)/2) / (n⁺n⁻), où R⁺ est la somme des rangs des positifs. C'est la statistique de Mann-Whitney, et elle donne exactement le même nombre.

**Du squelette au code :** le test de liste vide est le `return None` de `auc_paires` ; les deux boucles `POUR` sont les deux `for` imbriqués ; les deux branches du `SI` sont `gagnees += 1.0` et `gagnees += 0.5` ; la division finale est `gagnees / (len(scores_pos) * len(scores_neg))`. Le bloc 5 de `main()` vérifie que cet algorithme et le précédent donnent la même aire à 10⁻¹² près.

## Cas d'usage réels aux Émirats

Les taux et les volumes ci-dessous sont illustratifs ; seule la mécanique (Bayes, paires, trapèzes) est exacte.

### Banque — l'accuracy qui félicite le détecteur paresseux

Une banque de détail de Dubaï fait surveiller les paiements par carte par un agent qui bloque une transaction quand son score de fraude dépasse un seuil, puis envoie un SMS de confirmation au client sur son numéro en +971. Sur un échantillon de 1 000 paiements revus par l'équipe fraude, 10 sont frauduleux. L'agent en bloque 8, dont 5 fraudes : précision 0,625, rappel 0,50, spécificité 0,997, VPN 0,995, accuracy 0,992. Un fournisseur qui présenterait « 99,2 % d'exactitude » vendrait un détecteur à peine meilleur que celui qui ne bloque jamais rien (0,990). L'équipe fixe donc ses objectifs sur le rappel (la moitié des fraudes passe encore) et sur la spécificité (3 clients honnêtes bloqués sur 990, soit environ 3 appels au centre de contact pour 1 000 paiements). Sans la matrice complète, la direction aurait cru le problème réglé. On suit chaque semaine le rappel, la spécificité et le montant des fraudes non détectées, en AED.

### Assurance — le même détecteur sur deux produits

Un assureur auto et santé utilise le même modèle de détection de fraude sur ses deux lignes, avec une sensibilité de 0,80 et une spécificité de 0,98 mesurées sur l'ensemble. En santé, la fraude touche environ 0,5 % des demandes de remboursement ; en auto, environ 3 %. Par Bayes, la VPP vaut 0,004 / (0,004 + 0,02 × 0,995) = 0,167 en santé et 0,553 en auto : en santé, cinq alertes sur six visent un assuré honnête. La VPN reste au-dessus de 0,99 dans les deux cas, ce qui ne dit presque rien puisque la fraude est rare. L'assureur décide donc que l'alerte santé ne déclenche jamais un refus, seulement une demande de pièce complémentaire, alors que l'alerte auto ouvre une enquête. Sans ce calcul, le même seuil aurait produit, en santé, une file d'enquêtes presque toutes inutiles et des assurés mécontents. On suit la VPP observée par ligne de produit, recalculée chaque trimestre avec la prévalence du moment.

### Crypto — choisir un modèle par l'AUC, puis le seuil sur la courbe

Une plateforme d'actifs virtuels agréée par la VARA hésite entre deux modèles de score pour repérer les retraits liés à des comptes compromis. Sur trois mois de retraits étiquetés après enquête, le modèle A a une AUC de 0,91 et le modèle B de 0,87 : tiré au hasard, un retrait frauduleux reçoit un score plus haut qu'un retrait légitime 91 fois sur 100 avec A. Mais l'équipe opère à un taux de faux positifs d'au plus 1 %, parce que chaque blocage gèle les fonds d'un client. Elle lit donc la courbe ROC dans cette zone seulement, où B atteint un TPR de 0,62 contre 0,55 pour A : l'AUC globale récompensait A pour une partie de la courbe que la plateforme n'utilisera jamais. L'équipe retient B et fixe le seuil au point FPR = 1 % de sa courbe. Sans cette lecture, elle aurait déployé le modèle qui gagne le concours et perd sur le terrain. On suit le TPR au point de fonctionnement et le nombre de comptes gelés à tort par semaine.

### Secteur public — la spécificité protège le citoyen honnête

Une entité de services publics en ligne, accessible par UAE Pass, fait contrôler par un agent les documents joints aux demandes (actes, attestations) pour repérer les falsifications. Le positif est « document falsifié » ; un faux positif suspend la demande d'un citoyen honnête et l'oblige à se déplacer. Avec 20 000 demandes authentiques par mois, une spécificité de 0,995 suspend 100 citoyens honnêtes, une spécificité de 0,999 en suspend 20. L'entité fixe donc un objectif de spécificité avant tout objectif de rappel, et fait relire par un humain toute suspension avant de prévenir le demandeur. Sans cet objectif, l'agent aurait été réglé pour « attraper le plus de faux possible », et la charge serait retombée sur les guichets. Le traitement des pièces respecte la PDPL : les journaux de contrôle ne gardent que le verdict et le motif. On suit la spécificité mensuelle, mesurée sur un échantillon de demandes revues, et le délai de levée d'une suspension injustifiée.

### RH — beaucoup d'alertes WPS, peu de vraies anomalies

Un cabinet RH multi-émirats fait surveiller par un agent les fichiers de paie transmis par le système WPS pour repérer un salaire non versé ou versé en retard. Sur 5 000 employeurs clients, environ 2 % (100) sont réellement en anomalie un mois donné. Avec une sensibilité de 0,90 et une spécificité de 0,95, l'agent signale 90 vraies anomalies et 245 fausses : la précision vaut 90 / 335 = 0,269. Le cabinet ne peut pas appeler 335 employeurs : il trie les alertes par score, traite d'abord les plus hautes, et suit l'AUC pour savoir si cet ordre est bon. Il travaille aussi la spécificité, parce que chaque fausse alerte entame la confiance d'un client qui paie à l'heure. Sans ce calcul, l'équipe aurait conclu que l'agent « se trompe trois fois sur quatre » et l'aurait abandonné alors qu'il trouve neuf anomalies sur dix. On suit la précision des 50 alertes les mieux classées et le délai de régularisation des salaires.

### Immobilier — une VPN haute qui ne prouve rien

Une agence de Dubaï publie automatiquement les annonces que son agent juge saines (prix cohérent avec le marché en AED par sqft, propriétaire vérifié, pas de doublon) et met les autres en revue. Les annonces frauduleuses sont rares, de l'ordre d'une sur mille. Un agent qui jugerait toutes les annonces saines aurait déjà une VPN de 0,999 : la valeur prédictive négative élevée vient de la rareté, pas du modèle. L'agence exige donc aussi un rappel minimal sur les fraudes connues, mesuré sur un jeu d'annonces piégées construit par son équipe conformité. Sans ce second chiffre, l'agent pourrait passer tous les contrôles en ne détectant rien. On suit le rappel sur le jeu piégé et le nombre d'annonces frauduleuses signalées après publication par des acheteurs.

## Pièges et limites

- **Lire l'accuracy sur un événement rare.** Elle vaut presque la spécificité ; publier la matrice complète, ou au moins rappel et spécificité.
- **Transposer une précision d'une population à une autre.** La VPP et la VPN dépendent de la prévalence : on les recalcule par Bayes avec la prévalence de la nouvelle population.
- **Oublier le demi-point des égalités.** Avec des scores arrondis ou des juges qui notent sur 5, les égalités sont nombreuses ; sans le terme ½, l'AUC est sous-estimée (0,75 au lieu de 0,875 dans l'exemple).
- **Choisir un modèle sur l'AUC seule.** Elle intègre toute la courbe, y compris des seuils qu'on n'utilisera jamais ; regarder le TPR au taux de faux positifs autorisé.
- **Calculer une AUC sur une seule classe.** Elle n'existe pas : `None`, pas 0,5.

### Exercice feuille blanche

1. Sans regarder le code, écrire `auc_paires`, puis vérifier à la main que les positifs (0,3 ; 0,8) et les négatifs (0,3 ; 0,5) donnent (0,5 + 0 + 1 + 1)/4 = 0,625.
2. Prédire, puis vérifier avec `vpp_bayes` et `vpn_bayes` : avec Se = Sp = 0,9 et une prévalence de 10 %, que valent VPP et VPN ? (Réponse : VPP = 0,5 et VPN ≈ 0,988.)
3. Trouver le bug : `return ratio(m["TN"], m["TN"] + m["FN"])` dans une fonction nommée `specificite`. Que calcule-t-elle vraiment, et sur l'exemple des 1 000 paiements, quelle valeur renvoie-t-elle ? (Réponse : la VPN, 0,995 au lieu de 0,997.)

## Pour aller plus loin

- L'AUC partielle, restreinte à une plage de FPR, formalise la lecture du cas crypto.
- Sur les événements très rares, la courbe précision-rappel et son aire sont plus parlantes que la ROC, parce qu'elles dépendent de la prévalence.
- Le score de Brier mesure la calibration : un score de 0,8 correspond-il à 80 % de positifs ? L'AUC, qui ne voit que l'ordre, ne le dit pas.

> Suite : [Perplexité](<52-Perplexite-LLM.md>) — étape 52.
