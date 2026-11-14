# Étape 67 — Garde-fous — Score de risque

> Étape 67 du parcours · Prérequis : [Garde-fous : définitions et boîte à outils](<66-GardeFous-Definitions-Fondamentaux.md>) · Suite : [Sandbox d'exécution](<67b-Sandbox-d-Execution.md>)

**Dossier :** 11-GardeFous  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Agent Ops, AI Engineers, Forward-Deployed Engineers, AI Platform Team  

**Nom du fichier :** 67-GardeFous-Formule-Score-de-Risque.md

## Définition

Un score de risque agrège plusieurs signaux sur une action que l'agent s'apprête à faire, pour décider s'il faut la laisser passer, la soumettre à une revue humaine ou la bloquer. Ici, trois signaux suffisent : la sensibilité des données touchées, la gravité de l'action et l'incertitude du modèle, chacun ramené dans [0 ; 1], combinés par une moyenne pondérée dont les poids sont positifs et de somme 1. Le score n'est pas une probabilité : c'est un indice d'ordre, que l'on calibre sur l'historique pour en tirer une probabilité de dommage quand on veut raisonner en coût espéré. L'ancienne version de ce fichier utilisait un seul seuil (0,7) pour deux décisions différentes et laissait passer une action irréversible ; on ajoute deux seuils, un veto dur et deux règles de coût, le seuil de coût espéré et le seuil de Bayes.

## Rôle dans un agent

Le score intervient à l'étape « agir » de la boucle percevoir → décider → agir → observer, juste après la porte de politique de l'étape 66 et avant l'exécution de l'outil. La politique dit si l'agent **a le droit** d'appeler l'outil ; le score dit si **cet appel-là**, avec ces arguments, sur ces données, avec cette confiance, peut partir seul. Il lit des signaux produits ailleurs : la classe des données (étiquetage interne), le type et le montant de l'action (arguments validés), la fidélité de la réponse (étape 54), la perplexité (étape 52), une dérive de distribution mesurée par la KL (étape 50) ou un signal d'injection (étape 66). Sa sortie choisit le chemin : exécution directe, approbation humaine dans l'outil, ou refus avec un message au modèle.

## Équation complète

Le score, une moyenne pondérée de trois entrées dans [0 ; 1] :

$$
R = w_s\, s + w_g\, g + w_u\, u
$$

$$
s,\; g,\; u \in [0\,;\,1] \qquad w_s,\; w_g,\; w_u \ge 0 \qquad w_s + w_g + w_u = 1
$$

La décision, avec deux seuils et un veto v qui vaut 1 pour une action irréversible ou un montant au moins égal à M* :

$$
d(R, v) =
\begin{cases}
\text{bloquer} & \text{si } R \ge \tau_{blocage} \\
\text{revue} & \text{si } R \ge \tau_{revue} \text{ ou } v = 1 \\
\text{autoriser} & \text{sinon}
\end{cases}
\qquad 0 \le \tau_{revue} < \tau_{blocage} \le 1
$$

La gravité tient compte du type d'action et du montant, rapporté à un montant de référence et plafonné :

$$
g = \max\left(g_{type},\; \min\left(1,\; \frac{\text{montant}}{M_{ref}}\right)\right)
$$

Trois façons de ramener un signal d'incertitude dans [0 ; 1] :

$$
u = 1 - F \qquad u = 1 - \frac{1}{\mathrm{PPL}} \qquad u = 1 - e^{-D_{KL}}
$$

Les deux règles de coût, une fois le score calibré en probabilité de dommage p :

$$
\text{revue si} \quad p\; C_{dommage} > C_{revue}
$$

$$
\text{bloquer si} \quad p > t^{*} = \frac{C_{FP}}{C_{FP} + C_{FN}}
$$

## Décryptage des symboles

$$
s
$$

La sensibilité des données touchées par l'action, un réel dans [0 ; 1] : 0 pour des données publiques, 0,3 internes, 0,7 personnelles, 1 sensibles (santé, identité, données financières détaillées) ; table `SENSIBILITE`, argument `s`.

$$
g
$$

La gravité de l'action, un réel dans [0 ; 1] : 0 pour une lecture, 0,5 pour une écriture réversible, 1 pour une action irréversible, relevée par le montant ; fonction `gravite(type_action, montant_aed)`, argument `g`.

$$
u
$$

L'incertitude du modèle sur cette action, un réel dans [0 ; 1] : 1 − Faithfulness, 1 − 1/PPL ou 1 − e^(−KL) ; fonctions `depuis_fidelite`, `depuis_perplexite`, `depuis_kl`, argument `u`.

$$
w_s,\quad w_g,\quad w_u
$$

Les poids des trois entrées, des réels ≥ 0 de somme 1 ; ici 0,4, 0,4 et 0,2, dans le tuple `POIDS`. L'ancienne version les notait w₁, w₂, w₃.

$$
R
$$

Le score de risque, un réel dans [0 ; 1] ; valeur renvoyée par `score_risque(s, g, u)`.

$$
\tau_{revue},\quad \tau_{blocage}
$$

Le seuil à partir duquel une revue humaine est demandée et le seuil à partir duquel l'action est bloquée, avec τ_revue < τ_blocage ; ici 0,5 et 0,75, illustratifs ; constantes `TAU_REVUE` et `TAU_BLOCAGE`.

$$
v
$$

Le veto, un booléen qui vaut vrai pour une action irréversible ou un montant ≥ M* ; fonction `veto(type_action, montant_aed)`.

$$
M^{*},\quad M_{ref}
$$

Le montant à partir duquel la revue est obligatoire (25 000 AED, `MONTANT_VETO_AED`) et le montant de référence de la gravité (50 000 AED, `montant_ref_aed`), tous deux illustratifs.

$$
F,\quad \mathrm{PPL},\quad D_{KL}
$$

La fidélité de la réponse aux documents (étape 54, dans [0 ; 1]), la perplexité (étape 52, ≥ 1) et la divergence de Kullback-Leibler entre la distribution observée et la distribution de référence (étape 50, ≥ 0) ; arguments `faithfulness`, `ppl`, `d`.

$$
p
$$

La probabilité que l'action cause un dommage, obtenue en calibrant R sur l'historique ; un réel dans [0 ; 1] ; valeurs renvoyées par `calibrer`. Dans ce fichier, p désigne une probabilité de **dommage**, et non la probabilité de succès d'une étape comme à l'étape 1.

$$
C_{dommage},\quad C_{revue}
$$

Le coût d'un dommage s'il survient (ici le montant en jeu, en AED) et le coût d'une revue humaine (25 AED, illustratif) ; arguments `c_dommage`, `c_revue`.

$$
C_{FP},\quad C_{FN},\quad t^{*}
$$

Le coût d'un faux positif (bloquer une action saine), le coût d'un faux négatif (laisser passer une action nuisible) et le seuil de Bayes qui en découle ; arguments `c_fp`, `c_fn`, valeur renvoyée par `seuil_bayes`.

## Démonstration

### 1. Le score est dans [0 ; 1], et croît avec chaque entrée

Chaque terme est le produit d'un poids positif et d'une entrée dans [0 ; 1]. Comme multiplier une inégalité par un nombre positif en conserve le sens, 0 ≤ s ≤ 1 donne 0 ≤ w_s s ≤ w_s, et de même pour g et u. En additionnant les trois encadrements :

$$
0 \le w_s s + w_g g + w_u u \le w_s + w_g + w_u = 1
$$

Le minimum 0 est atteint pour s = g = u = 0, le maximum 1 pour s = g = u = 1, et le programme le vérifie sur les 125 combinaisons de la grille {0 ; 0,25 ; 0,5 ; 0,75 ; 1}³. Les deux hypothèses sont nécessaires. Si une entrée sort de [0 ; 1], par exemple une perplexité brute de 40, le score dépasse 1 et les seuils perdent leur sens. Si les poids ne sont pas de somme 1, par exemple (0,5 ; 0,5 ; 0,5), le maximum vaut 1,5. La fonction refuse les deux cas par `ValueError`. Enfin, la dérivée partielle de R par rapport à chaque entrée est son poids, positif ou nul : augmenter un signal ne peut jamais faire baisser le risque.

### 2. Ramener un signal dans [0 ; 1] sans changer son ordre

Les trois transformations de l'équation complète gardent l'ordre des signaux et tombent dans [0 ; 1]. Pour la fidélité, F ∈ [0 ; 1] donne 1 − F ∈ [0 ; 1], et une réponse moins fidèle donne une incertitude plus grande : F = 0,85 donne u = 0,15. Pour la perplexité, PPL ≥ 1 (démontré à l'étape 52) donne 1/PPL ∈ ]0 ; 1], donc 1 − 1/PPL ∈ [0 ; 1[, croissante en PPL : PPL = 4 donne 0,75. Pour la divergence KL, D ≥ 0 (inégalité de Gibbs, étape 50) donne e^(−D) ∈ ]0 ; 1], donc 1 − e^(−D) ∈ [0 ; 1[, croissante en D :

$$
1 - e^{-0{,}5} \approx 1 - 0{,}6065 = 0{,}3935
$$

Le choix de la transformation reste une décision de calibrage : 1 − 1/PPL monte vite (0,75 dès PPL = 4) et sature ensuite, ce qui convient si l'on veut réagir tôt à une perplexité anormale. L'ancienne version de ce fichier listait la perplexité et la fidélité comme signaux sans dire comment les ramener à la même échelle que les autres.

### 3. Un seuil pour deux décisions ne suffit pas

L'ancienne règle disait : au-dessus de 0,7, l'action est « bloquée ou escaladée ». Ce sont deux décisions de nature différente : une revue coûte quelques minutes d'un humain et laisse l'action possible, un blocage l'interdit. Un seul seuil oblige à choisir entre trop bloquer (si on le place bas) et laisser passer sans regard des actions douteuses (si on le place haut). Deux seuils, τ_revue < τ_blocage, découpent [0 ; 1] en trois zones : en dessous de τ_revue, l'action part seule ; entre les deux, un humain regarde ; au-dessus de τ_blocage, elle est refusée. La condition τ_revue < τ_blocage est nécessaire pour que la zone de revue existe ; la fonction `decider` refuse des seuils égaux ou inversés.

### 4. La somme pondérée compense : contre-exemple chiffré

L'ancienne version donnait les poids (0,4 ; 0,4 ; 0,2) et le seuil 0,7. Prenons une action irréversible (g = 1) sur des données internes (s = 0,3), avec un modèle sûr de lui (u = 0,1) :

$$
R = 0{,}4 \times 0{,}3 + 0{,}4 \times 1 + 0{,}2 \times 0{,}1 = 0{,}12 + 0{,}40 + 0{,}02 = 0{,}54 < 0{,}7
$$

L'ancienne règle l'autorise sans regard humain. Avec deux seuils (0,5 et 0,75), elle passe en revue, mais le défaut n'est que déplacé. Le cas général se démontre ainsi : si s = u = 0, alors R = w_g g ≤ w_g. Une entrée seule ne peut donc atteindre un seuil τ que si son poids est au moins τ :

$$
R \ge \tau \text{ avec } s = u = 0 \quad \Longrightarrow \quad w_g \ge \tau
$$

Avec w_g = 0,4 < τ_revue = 0,5, **aucune action irréversible ne peut déclencher une revue par sa seule gravité** ; il lui faut l'aide des autres signaux. Un retrait de cryptoactifs, irréversible sur la chaîne, vers une adresse publique (s = 0,1), avec un modèle confiant (u = 0,1), donne R = 0,04 + 0,40 + 0,02 = 0,46 et passe sans revue. Relever w_g jusqu'à τ_revue réglerait ce cas, mais ferait passer en revue toute écriture réversible un peu sensible, et déformerait le score pour tous les autres. La bonne réponse est de **sortir l'irréversibilité de la somme** : c'est le veto, une règle non compensatoire, appliquée avant le score. Avec le veto, le retrait passe en revue, et une action déjà au-dessus de τ_blocage reste bloquée : le veto ne peut que durcir la décision, jamais l'adoucir.

### 5. Le seuil de coût espéré : revoir si p C_dommage > C_revue

Supposons connue la probabilité p que l'action cause un dommage de coût C_dommage, et supposons qu'une revue, de coût C_revue, arrête le dommage. Sans revue, le coût espéré vaut p C_dommage ; avec revue, il vaut C_revue. La revue est rentable exactement quand :

$$
p\; C_{dommage} > C_{revue} \quad \Longleftrightarrow \quad p > \frac{C_{revue}}{C_{dommage}}
$$

Avec une revue à 25 AED (illustratif, quelques minutes d'un analyste), un virement de 50 000 AED justifie une revue dès que p > 0,0005, alors qu'un paiement de 200 AED ne la justifie qu'au-delà de p = 0,125. Le seuil de probabilité baisse quand le montant monte : c'est la justification du veto sur le montant. Si l'on estime qu'aucun modèle ne garantit une probabilité de dommage inférieure à p_min = 0,001, alors toute action dont le montant dépasse

$$
M^{*} = \frac{C_{revue}}{p_{min}} = \frac{25}{0{,}001} = 25\,000 \text{ AED}
$$

justifie une revue quel que soit son score. C'est la valeur de `MONTANT_VETO_AED`.

### 6. Le seuil de Bayes : t* = C_FP / (C_FP + C_FN)

Considérons maintenant le choix entre bloquer et laisser passer, sans revue possible. Bloquer une action saine coûte C_FP (un client mécontent, un délai) ; laisser passer une action nuisible coûte C_FN. Si p est la probabilité que l'action soit nuisible, les coûts espérés valent :

$$
\mathbb{E}[\text{coût} \mid \text{laisser passer}] = p\, C_{FN}
\qquad
\mathbb{E}[\text{coût} \mid \text{bloquer}] = (1 - p)\, C_{FP}
$$

On bloque quand le premier dépasse le second. En développant et en regroupant les termes en p :

$$
p\, C_{FN} > (1 - p)\, C_{FP}
\;\Longleftrightarrow\;
p\,(C_{FN} + C_{FP}) > C_{FP}
\;\Longleftrightarrow\;
p > \frac{C_{FP}}{C_{FP} + C_{FN}} = t^{*}
$$

La division est permise parce que C_FP + C_FN > 0. Si les deux erreurs coûtent autant, t* = 1/2 : on bloque dès que la nuisance est plus probable que l'innocuité. Si un faux négatif coûte 50 000 AED et un faux positif 25 AED, t* = 25 / 50 025 ≈ 0,0004998 : on bloque dès qu'une chance sur deux mille de dommage est présente. Quand C_FP est petit devant C_FN, t* ≈ C_FP / C_FN, la même forme qu'au point 5 : les deux règles disent qu'une action chère se contrôle à une probabilité très faible.

### 7. Du score à une probabilité : le calibrage

Les règles des points 5 et 6 demandent une probabilité, et R n'en est pas une : un score de 0,54 ne veut pas dire « 54 % de chances de dommage ». On le **calibre** sur un historique d'actions déjà jugées : on découpe [0 ; 1] en tranches de score et l'on compte, dans chaque tranche, la proportion d'actions qui se sont révélées nuisibles. Sur l'historique de 20 actions du programme, la tranche [0 ; 0,4[ contient 10 actions dont 1 nuisible, la tranche [0,4 ; 0,7[ en contient 6 dont 3, et la tranche [0,7 ; 1] en contient 4 dont 3 :

$$
\hat{p}_1 = \frac{1}{10} = 0{,}1 \qquad \hat{p}_2 = \frac{3}{6} = 0{,}5 \qquad \hat{p}_3 = \frac{3}{4} = 0{,}75
$$

Les proportions croissent avec le score, ce qui est la première chose à vérifier : sinon le score classe mal. Avec si peu d'exemples, chaque proportion a un intervalle de Wilson très large (étape 7) : 3 sur 4 laisse une incertitude de plusieurs dizaines de points. Une tranche vide renvoie `None`, et l'on n'y applique pas de règle de coût.

### 8. Exemple fait à la main (le code reprend ces nombres)

| Action | s | g | u | R | Veto | Décision |
|---|---|---|---|---|---|---|
| ancienne règle, irréversible | 0,3 | 1 | 0,1 | 0,54 | — | autorisée par l'ancienne règle, revue avec deux seuils |
| retrait crypto de 8 000 AED | 0,1 | 1 | 0,1 | 0,46 | oui | autoriser sans veto, revue avec veto |
| score maximal de la gravité seule | 0 | 1 | 0 | 0,40 | — | toujours sous τ_revue = 0,5 |

| Règle de coût | Calcul | Résultat |
|---|---|---|
| seuil de Bayes, C_FP = 25, C_FN = 50 000 | 25 / 50 025 | 0,0004998 |
| seuil de Bayes, coûts égaux | 1 / 2 | 0,5 |
| p = 0,001 et 50 000 AED | 0,001 × 50 000 = 50 > 25 | revue |
| p = 0,001 et 200 AED | 0,001 × 200 = 0,2 < 25 | pas de revue |
| p = 0,2 et 200 AED | 0,2 × 200 = 40 > 25 | revue |
| R = 0,2 (p = 0,1) et 50 000 AED | 0,1 × 50 000 = 5 000 > 25 | revue |
| R = 0,54 (p = 0,5) et 3 000 AED | 0,5 × 3 000 = 1 500 > 25 | revue |

## Effets et comportement

- **Augmenter un poids rend le score plus sensible à ce signal, et moins aux autres**, puisque la somme des poids reste 1. Les poids disent quel signal commande.
- **Abaisser τ_revue augmente la charge des relecteurs.** Chaque dixième de point retiré fait passer en revue toutes les actions de la tranche ; on suit le nombre de revues par jour avant de bouger le seuil.
- **Le veto rend le score non compensatoire sur une dimension.** Aucune combinaison de signaux rassurants ne fait passer seule une action irréversible ou un gros montant.
- **Le seuil de coût dépend du montant, pas du score.** Pour une même probabilité de dommage, un montant cent fois plus grand rend la revue cent fois plus rentable.
- **Un score non calibré ne se compare pas à un coût.** On calibre d'abord, puis l'on applique p C_dommage > C_revue.

## Du symbole au code Python

$$
R = w_s s + w_g g + w_u u
$$

**Variable ou fonction :** `score_risque(s, g, u, poids=POIDS)`, qui refuse les entrées hors de [0 ; 1] et les poids invalides

$$
u = 1 - F, \qquad 1 - 1/\mathrm{PPL}, \qquad 1 - e^{-D_{KL}}
$$

**Variable ou fonction :** `depuis_fidelite(faithfulness)`, `depuis_perplexite(ppl)`, `depuis_kl(d)`

$$
g = \max\left(g_{type},\, \min(1,\, \text{montant} / M_{ref})\right)
$$

**Variable ou fonction :** `gravite(type_action, montant_aed, montant_ref_aed)`

$$
v
$$

**Variable ou fonction :** `veto(type_action, montant_aed)`

$$
d(R, v)
$$

**Variable ou fonction :** `decider(r, veto_actif, tau_revue, tau_blocage)`, et `decision_ancienne(r)` pour le contre-exemple

$$
p\, C_{dommage} > C_{revue}, \qquad t^{*}
$$

**Variable ou fonction :** `escalader(p, c_dommage, c_revue)`, `seuil_bayes(c_fp, c_fn)`

$$
\hat{p}_k
$$

**Variable ou fonction :** `calibrer(historique, bornes)` et `tranche(r, bornes)`

### Déroulé, ligne par ligne

**Les constantes.** `POIDS = (0.4, 0.4, 0.2)` reprend les poids de l'ancienne version. `TAU_REVUE, TAU_BLOCAGE = 0.5, 0.75` sont les deux seuils, illustratifs. `MONTANT_VETO_AED = 25_000` est le montant du veto, déduit au point 5 de la démonstration. `SENSIBILITE` et `GRAVITE` traduisent des classes métier en nombres dans [0 ; 1].

**`depuis_fidelite`, `depuis_perplexite` et `depuis_kl`** vérifient d'abord le domaine du signal (F ∈ [0 ; 1], PPL ≥ 1, KL ≥ 0) et lèvent `ValueError` sinon, puis appliquent la transformation : `1 - 0.85` donne 0,15, `1 - 1 / 4.0` donne 0,75, `1 - math.exp(-0.5)` donne 0,3935.

**`gravite(type_action, montant_aed, montant_ref_aed)`** prend le maximum entre la gravité du type et le montant rapporté à 50 000 AED, plafonné à 1 : une écriture réversible de 40 000 AED donne `max(0.5, 0.8) = 0.8`, une lecture donne 0.

**`score_risque(s, g, u, poids)`** contrôle les deux hypothèses de la démonstration, point 1 : `all(0 <= x <= 1 ...)` pour les entrées, puis des poids positifs dont la somme vaut 1 à 10⁻⁹ près (la somme flottante 0,4 + 0,4 + 0,2 n'est pas forcément exactement 1). Elle renvoie ensuite la somme pondérée : pour (0,3 ; 1 ; 0,1), 0,12 + 0,40 + 0,02 = 0,54.

**`veto(type_action, montant_aed)`** est la règle dure : vrai pour une action irréversible ou un montant d'au moins 25 000 AED.

**`decider(r, veto_actif, tau_revue, tau_blocage)`** vérifie `0 <= tau_revue < tau_blocage <= 1`, puis teste les zones de la plus grave à la moins grave : `r >= tau_blocage` donne « bloquer », quel que soit le veto ; sinon `r >= tau_revue or veto_actif` donne « revue » ; sinon « autoriser ». L'ordre des tests garantit que le veto ne peut que durcir la décision. **`decision_ancienne(r)`** reproduit l'ancienne règle à un seuil, pour le contre-exemple.

**`seuil_bayes(c_fp, c_fn)`** renvoie `c_fp / (c_fp + c_fn)` après avoir refusé des coûts négatifs ou tous nuls : 25 / 50 025 ≈ 0,0004998. **`escalader(p, c_dommage, c_revue)`** renvoie `p * c_dommage > c_revue`.

**`calibrer(historique, bornes)`** parcourt les tranches `[bas ; haut[` formées par deux bornes consécutives, la dernière étant fermée à droite pour inclure le score 1. Dans chaque tranche, elle calcule la proportion d'actions nuisibles ; `sum(tranche)` compte les `True`, qui valent 1. Une tranche vide donne `None`. **`tranche(r, bornes)`** renvoie l'indice de la tranche d'un score.

**`main()`**, section par section.

1. Les trois transformations, et la gravité d'une écriture réversible de 40 000 AED.
2. Les 125 combinaisons de la grille donnent un minimum de 0 et un maximum de 1 ; des poids de somme 1,5 et une entrée de 1,2 sont refusés.
3. Le contre-exemple : 0,54, autorisé par l'ancienne règle, en revue avec deux seuils.
4. Le retrait crypto : 0,46, autorisé sans veto, en revue avec veto ; la gravité seule plafonne à w_g = 0,4 < τ_revue ; un score de 0,80 avec veto reste bloqué.
5. Les seuils de Bayes et de coût espéré, et le montant du veto, 25 / 0,001 = 25 000 AED.
6. Le calibrage sur 20 actions, puis trois décisions au coût espéré : 200 AED en tranche basse (20 AED de perte espérée, pas de revue), 50 000 AED en tranche basse (5 000 AED, revue), 3 000 AED en tranche moyenne (1 500 AED, revue).
7. Des seuils égaux sont refusés.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`depuis_fidelite(faithfulness)`** — Cette fonction est le premier des trois traducteurs qui ramènent un signal brut à une incertitude comprise entre 0 et 1, comme un interprète qui convertit une note de confiance en note de doute : elle reçoit le score de fidélité F de l'étape 54, vérifie qu'il tombe bien dans [0 ; 1] et lève `ValueError` dans le cas contraire, puis renvoie simplement 1 − F. Une réponse fidèle à 0,85 devient ainsi une incertitude de 0,15, et c'est ce nombre qui peut alimenter la composante u du score de risque.

**`depuis_perplexite(ppl)`** — Deuxième traducteur, celui-ci parle la langue de la perplexité de l'étape 52 : il reçoit une perplexité, refuse par une `ValueError` toute valeur inférieure à 1, puisqu'une perplexité ne descend jamais sous ce plancher, puis renvoie 1 − 1/PPL, un nombre de [0 ; 1[ qui grandit à mesure que le modèle hésite. Un modèle qui hésite comme entre quatre mots, PPL = 4, reçoit ainsi une incertitude de 0,75, que `main` affiche et vérifie dans sa première section.

**`depuis_kl(d)`** — Le troisième traducteur mesure la dérive, comme un garde-côte qui note de combien le navire s'est écarté de sa route : il reçoit une divergence de Kullback-Leibler de l'étape 50, lève `ValueError` si elle est négative, puis renvoie 1 − exp(−d), une valeur de [0 ; 1[ qui part de 0 pour une dérive nulle et s'approche de 1 quand la dérive grandit. Pour une divergence de 0,5, elle rend 0,3935 au dix-millième près, le chiffre contrôlé par l'`assert` de la section 1 de `main`.

**`gravite(type_action, montant_aed, montant_ref_aed)`** — Cette fonction joue l'expert en sinistres qui juge la portée d'un geste avant qu'on le commette : elle reçoit le type d'action, cherche sa gravité de base dans la table `GRAVITE` (0 pour une lecture, 0,5 pour une écriture réversible, 1 pour une action irréversible), puis la compare au montant rapporté à un montant de référence de 50 000 AED par défaut, plafonné à 1, et renvoie le plus grand des deux. Une écriture réversible de 40 000 AED monte ainsi à 0,8, car le montant pèse plus que le type, tandis qu'une simple lecture sans montant reste à 0 ; ce nombre devient la composante g du score.

**`veto(type_action, montant_aed)`** — Voici le portier inflexible qui ne regarde jamais le score : il reçoit le type d'action et le montant en AED, et renvoie `True` dès que l'action est irréversible ou que le montant atteint au moins `MONTANT_VETO_AED`, soit 25 000 AED, `False` sinon. Ce booléen, tenu hors de la somme pondérée, est transmis à `decider` pour qu'aucune combinaison de signaux rassurants ne puisse, à elle seule, laisser passer sans humain un retrait crypto irréversible comme celui de la section 4.

**`decision_ancienne(r)`** — Cette petite fonction ressuscite, pour le seul besoin du contre-exemple, l'ancien règlement du fichier, comme un archiviste qui ressort une vieille circulaire pour montrer pourquoi on l'a abrogée : elle reçoit un score et renvoie « bloquer ou escalader » s'il dépasse strictement 0,7, « autoriser » sinon, confondant ainsi deux décisions différentes sous un seul seuil. Dans la section 3 de `main`, elle autorise une action irréversible notée 0,54, là où `decider` et ses deux seuils l'envoient en revue.

**`seuil_bayes(c_fp, c_fn)`** — Cette fonction est le comptable qui trace la ligne de partage entre bloquer et laisser passer : elle reçoit le coût d'un faux positif, une action saine bloquée, et celui d'un faux négatif, une action nuisible acceptée, refuse par une `ValueError` des coûts négatifs ou tous deux nuls, puis renvoie C_FP / (C_FP + C_FN). Avec 25 AED contre 50 000 AED, le seuil tombe à 0,0004998, si bien qu'une probabilité de dommage minuscule suffit déjà à justifier le blocage ; avec des coûts égaux, on retrouve 0,5.

**`escalader(p, c_dommage, c_revue)`** — Celle-ci tranche une question de bon sens économique, comme un assureur qui se demande si une expertise vaut son prix : elle reçoit la probabilité de dommage p, le montant du dommage possible et le coût d'une revue humaine, et renvoie `True` si le dommage espéré p × C_dommage dépasse strictement le coût de la revue. Avec une revue à 25 AED, p = 0,001 sur 50 000 AED donne 50 AED et déclenche la revue, le même p sur 200 AED ne donne que 0,2 AED et n'en déclenche pas, tandis que p = 0,2 sur 200 AED donne 40 AED et la déclenche.

**`tranche(r, bornes)`** — Cette fonction est l'huissier qui indique à un score dans quelle salle il doit attendre : elle reçoit un score et la liste croissante des bornes, parcourt les indices des tranches et renvoie le premier indice k pour lequel le score est strictement inférieur à la borne suivante, la dernière tranche servant de refuge, ce qui y range aussi le score 1. Avec les bornes 0 ; 0,4 ; 0,7 ; 1, un score de 0,2 tombe dans la tranche 0 et un score de 0,54 dans la tranche 1, ce qui permet à `main` de lire la probabilité calibrée correspondante dans la liste rendue par `calibrer`.

**`main()`** — C'est le metteur en scène qui fait passer au programme ses sept épreuves, dans l'ordre de la fiche : il traduit d'abord les trois signaux et la gravité, balaie les 125 combinaisons de la grille pour montrer que le score reste entre 0 et 1 et que des poids de somme 1,5 ou une entrée de 1,2 sont refusés, puis oppose l'ancienne règle aux deux seuils sur le score 0,54 et montre le veto à l'œuvre sur le retrait crypto noté 0,46. Il calcule ensuite les seuils de Bayes et de coût espéré, retrouve le montant du veto, 25 / 0,001 = 25 000 AED, calibre l'historique de 20 actions en probabilités 0,1, 0,5 et 0,75, et termine en vérifiant que des seuils égaux sont refusés ; chaque résultat est confronté à un `assert`, et la ligne finale « OK » ne s'imprime que si tout concorde.

```python
"""Étape 67 — score de risque d'une action d'agent : entrées dans [0, 1], deux seuils, veto, coût espéré, Bayes."""
import itertools
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

POIDS = (0.4, 0.4, 0.2)            # (w_s, w_g, w_u) : sensibilité, gravité de l'action, incertitude
TAU_REVUE, TAU_BLOCAGE = 0.5, 0.75  # seuils illustratifs, à calibrer sur l'historique
MONTANT_VETO_AED = 25_000           # au-delà, revue humaine obligatoire (voir la démonstration, point 6)
SENSIBILITE = {"publique": 0.0, "interne": 0.3, "personnelle": 0.7, "sensible": 1.0}
GRAVITE = {"lecture": 0.0, "ecriture_reversible": 0.5, "irreversible": 1.0}


# ---------------------------------------------------------------- ramener chaque signal dans [0, 1]
def depuis_fidelite(faithfulness: float) -> float:
    """Étape 54 : Faithfulness ∈ [0, 1] ; l'incertitude vaut 1 − F."""
    if not 0 <= faithfulness <= 1:
        raise ValueError("Faithfulness hors de [0, 1]")
    return 1 - faithfulness


def depuis_perplexite(ppl: float) -> float:
    """Étape 52 : PPL ≥ 1 ; 1 − 1/PPL est dans [0, 1[ et croît avec la perplexité."""
    if ppl < 1:
        raise ValueError("une perplexité est toujours >= 1")
    return 1 - 1 / ppl


def depuis_kl(d: float) -> float:
    """Étape 50 : KL ≥ 0 ; 1 − e^(−KL) est dans [0, 1[ et croît avec la dérive."""
    if d < 0:
        raise ValueError("une divergence KL est toujours >= 0")
    return 1 - math.exp(-d)


def gravite(type_action: str, montant_aed: float = 0.0, montant_ref_aed: float = 50_000) -> float:
    """Gravité : le type d'action, relevé par le montant s'il est grand (plafonné à 1)."""
    return max(GRAVITE[type_action], min(1.0, montant_aed / montant_ref_aed))


# ---------------------------------------------------------------- le score et la décision
def score_risque(s: float, g: float, u: float, poids: tuple = POIDS) -> float:
    """R = w_s·s + w_g·g + w_u·u, avec des entrées dans [0, 1] et des poids >= 0 de somme 1 : R ∈ [0, 1]."""
    if not all(0 <= x <= 1 for x in (s, g, u)):
        raise ValueError("chaque entrée doit être dans [0, 1]")
    if any(w < 0 for w in poids) or abs(sum(poids) - 1) > 1e-9:
        raise ValueError("les poids doivent être >= 0 et de somme 1")
    w_s, w_g, w_u = poids
    return w_s * s + w_g * g + w_u * u


def veto(type_action: str, montant_aed: float) -> bool:
    """Règle dure, hors du score : irréversible ou gros montant ⇒ jamais sans humain."""
    return type_action == "irreversible" or montant_aed >= MONTANT_VETO_AED


def decider(r: float, veto_actif: bool, tau_revue: float = TAU_REVUE, tau_blocage: float = TAU_BLOCAGE) -> str:
    if not 0 <= tau_revue < tau_blocage <= 1:
        raise ValueError("il faut 0 <= tau_revue < tau_blocage <= 1")
    if r >= tau_blocage:
        return "bloquer"
    if r >= tau_revue or veto_actif:
        return "revue"
    return "autoriser"


def decision_ancienne(r: float) -> str:
    """Ancienne règle du fichier : un seul seuil de 0,7 pour deux décisions différentes."""
    return "bloquer ou escalader" if r > 0.7 else "autoriser"


# ---------------------------------------------------------------- seuils de coût
def seuil_bayes(c_fp: float, c_fn: float) -> float:
    """Bloquer si p > C_FP / (C_FP + C_FN) : le coût espéré de bloquer devient inférieur à celui de laisser passer."""
    if c_fp < 0 or c_fn < 0 or c_fp + c_fn == 0:
        raise ValueError("coûts >= 0, pas tous nuls")
    return c_fp / (c_fp + c_fn)


def escalader(p: float, c_dommage: float, c_revue: float) -> bool:
    """Demander une revue si le dommage espéré évité dépasse le coût de la revue : p · C_dommage > C_revue."""
    return p * c_dommage > c_revue


def calibrer(historique: list[tuple[float, bool]], bornes: list[float]) -> list[float | None]:
    """Probabilité de dommage observée par tranche de score [b_k ; b_k+1[ ; None pour une tranche vide."""
    probas = []
    for bas, haut in zip(bornes, bornes[1:]):
        tranche = [nuisible for r, nuisible in historique if bas <= r < haut or (haut == bornes[-1] and r == haut)]
        probas.append(sum(tranche) / len(tranche) if tranche else None)
    return probas


def tranche(r: float, bornes: list[float]) -> int:
    return next(k for k in range(len(bornes) - 1) if r < bornes[k + 1] or k == len(bornes) - 2)


def main() -> None:
    print("1. Entrées ramenées à [0, 1]")
    u_f, u_p, u_k = depuis_fidelite(0.85), depuis_perplexite(4.0), depuis_kl(0.5)
    print(f"  Faithfulness 0.85 → u = {u_f:.2f} ; PPL 4 → {u_p:.2f} ; KL 0.5 → {u_k:.4f}")
    assert round(u_f, 2) == 0.15 and u_p == 0.75 and round(u_k, 4) == 0.3935
    assert gravite("lecture") == 0.0 and gravite("ecriture_reversible", 40_000) == 0.8

    print("2. Le score est toujours dans [0, 1]")
    grille = [x / 4 for x in range(5)]
    valeurs = [score_risque(s, g, u) for s, g, u in itertools.product(grille, repeat=3)]
    print(f"  {len(valeurs)} combinaisons : min = {min(valeurs):.2f}, max = {max(valeurs):.2f}")
    assert min(valeurs) == 0.0 and abs(max(valeurs) - 1.0) < 1e-12
    for mauvais in ((0.5, 0.5, 0.5, (0.5, 0.5, 0.5)), (1.2, 0.0, 0.0, POIDS)):
        try:
            score_risque(*mauvais)
        except ValueError as e:
            print(f"  refusé : {e}")
        else:
            raise AssertionError("entrée invalide acceptée")

    print("3. L'ancienne règle laisse passer une action irréversible")
    r = score_risque(0.3, 1.0, 0.1)
    print(f"  (0.3 ; 1.0 ; 0.1) → R = {r:.2f} ; ancienne règle : {decision_ancienne(r)} ; "
          f"deux seuils : {decider(r, False)}")
    assert round(r, 2) == 0.54 and decision_ancienne(r) == "autoriser" and decider(r, False) == "revue"

    print("4. La compensation : un retrait crypto irréversible, données peu sensibles, modèle sûr de lui")
    r = score_risque(0.1, 1.0, 0.1)
    print(f"  (0.1 ; 1.0 ; 0.1) → R = {r:.2f} ; sans veto : {decider(r, False)} ; avec veto : {decider(r, veto('irreversible', 8_000))}")
    assert round(r, 2) == 0.46 and decider(r, False) == "autoriser" and decider(r, True) == "revue"
    assert score_risque(0, 1.0, 0) == POIDS[1] < TAU_REVUE                        # la gravité seule plafonne à w_g
    assert decider(0.80, True) == "bloquer"                                         # le veto n'adoucit jamais

    print("5. Seuils de coût (coûts illustratifs en AED)")
    t_star = seuil_bayes(25, 50_000)
    print(f"  seuil de Bayes, C_FP = 25, C_FN = 50 000 : t* = {t_star:.7f} ; coûts égaux : {seuil_bayes(1, 1)}")
    assert round(t_star, 7) == 0.0004998 and seuil_bayes(1, 1) == 0.5
    for p, montant in ((0.001, 50_000), (0.001, 200), (0.2, 200)):
        print(f"  p = {p}, dommage = {montant} AED : p × C = {p * montant:g} AED → "
              f"{'revue' if escalader(p, montant, 25) else 'pas de revue'} (revue = 25 AED)")
    assert escalader(0.001, 50_000, 25) and not escalader(0.001, 200, 25) and escalader(0.2, 200, 25)
    assert round(25 / 0.001) == MONTANT_VETO_AED                                     # montant du veto : C_revue / p_min

    print("6. Calibrer le score en probabilité sur l'historique, puis décider au coût espéré")
    historique = ([(0.1, False)] * 5 + [(0.2, False)] * 3 + [(0.3, True), (0.35, False)]
                  + [(0.45, True), (0.5, False), (0.55, True), (0.6, False), (0.65, True), (0.68, False)]
                  + [(0.75, True), (0.8, True), (0.9, False), (1.0, True)])
    bornes = [0.0, 0.4, 0.7, 1.0]
    probas = calibrer(historique, bornes)
    print(f"  tranches {bornes} → p = {probas}")
    assert probas == [0.1, 0.5, 0.75]
    for r, montant in ((0.2, 200), (0.2, 50_000), (0.54, 3_000)):
        p = probas[tranche(r, bornes)]
        print(f"  R = {r}, montant {montant} AED : p = {p} ; perte espérée p × G = {p * montant:g} AED → "
              f"{'revue' if escalader(p, montant, 25) else 'autoriser'}")
    assert not escalader(0.1, 200, 25) and escalader(0.1, 50_000, 25) and escalader(0.5, 3_000, 25)
    assert calibrer([], bornes) == [None, None, None]

    print("7. Garde-fous de la fonction de décision")
    try:
        decider(0.5, False, tau_revue=0.7, tau_blocage=0.7)
    except ValueError as e:
        print(f"  refusé : {e}")
    else:
        raise AssertionError("seuils incohérents acceptés")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Entrées ramenées à [0, 1]
  Faithfulness 0.85 → u = 0.15 ; PPL 4 → 0.75 ; KL 0.5 → 0.3935
2. Le score est toujours dans [0, 1]
  125 combinaisons : min = 0.00, max = 1.00
…
3. L'ancienne règle laisse passer une action irréversible
  (0.3 ; 1.0 ; 0.1) → R = 0.54 ; ancienne règle : autoriser ; deux seuils : revue
4. La compensation : un retrait crypto irréversible, données peu sensibles, modèle sûr de lui
  (0.1 ; 1.0 ; 0.1) → R = 0.46 ; sans veto : autoriser ; avec veto : revue
5. Seuils de coût (coûts illustratifs en AED)
  seuil de Bayes, C_FP = 25, C_FN = 50 000 : t* = 0.0004998 ; coûts égaux : 0.5
…
6. Calibrer le score en probabilité sur l'historique, puis décider au coût espéré
  tranches [0.0, 0.4, 0.7, 1.0] → p = [0.1, 0.5, 0.75]
  R = 0.2, montant 200 AED : p = 0.1 ; perte espérée p × G = 20 AED → autoriser
  R = 0.2, montant 50000 AED : p = 0.1 ; perte espérée p × G = 5000 AED → revue
  R = 0.54, montant 3000 AED : p = 0.5 ; perte espérée p × G = 1500 AED → revue
7. Garde-fous de la fonction de décision
  refusé : il faut 0 <= tau_revue < tau_blocage <= 1
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un score de risque utile tient en trois règles. Des entrées et des poids qui le gardent dans [0 ; 1] ; deux seuils pour deux décisions ; et, pour ce qui ne doit jamais se compenser, un veto hors de la somme, dont le montant se déduit du coût d'une revue.

## Squelette algorithmique

Le fichier contient deux algorithmes. Le premier évalue une action : il ramène les signaux dans [0 ; 1], calcule le score, applique le veto et choisit entre autoriser, revue et bloquer. Le second calibre le score sur un historique, puis décide au coût espéré. Les entrées sont les signaux d'une action et, pour le second, un historique de n actions jugées ; les sorties sont une décision, ou une probabilité par tranche.

### Évaluer une action : score, veto, décision

```text
ALGORITHME EvaluerAction
ENTRÉES : classe des données ; type d'action ; montant ; F (ou PPL, ou KL)
          poids (w_s, w_g, w_u) ; seuils τ_revue < τ_blocage ; M* ; M_ref
SORTIE  : "autoriser", "revue" ou "bloquer"
  SI les poids ne sont pas ≥ 0 de somme 1 OU NON (τ_revue < τ_blocage) ALORS ERREUR FIN SI
  s ← SENSIBILITÉ[classe]
  g ← max(GRAVITÉ[type], min(1, montant / M_ref))
  u ← 1 − F                                  ▷ ou 1 − 1/PPL, ou 1 − e^(−KL)
  SI s, g ou u ∉ [0 ; 1] ALORS ERREUR FIN SI
  R ← w_s × s + w_g × g + w_u × u              ▷ R ∈ [0 ; 1]
  v ← (type = irréversible) OU (montant ≥ M*)
  SI R ≥ τ_blocage ALORS
    RETOURNER "bloquer"
  SINON SI R ≥ τ_revue OU v ALORS
    RETOURNER "revue"
  SINON
    RETOURNER "autoriser"
  FIN SI
```

**Complexité :** O(k) en temps et en mémoire pour k signaux combinés, ici k = 3, donc O(1) : quelques multiplications, un maximum et trois comparaisons par action. Le coût réel est en amont, dans la production des signaux (calcul de la fidélité, de la perplexité ou de la KL), qui relève des étapes 50 à 54.

**Du squelette au code :** le contrôle des poids et des entrées et le calcul de R sont dans `score_risque` ; s vient de la table `SENSIBILITE`, g de `gravite`, u de `depuis_fidelite`, `depuis_perplexite` ou `depuis_kl` ; v est `veto(type_action, montant_aed)` ; le contrôle des seuils et la cascade SI sont dans `decider`, dans le même ordre que le squelette.

### Calibrer le score, puis décider au coût espéré

```text
ALGORITHME CalibrerEtDecider
ENTRÉES : historique (Rᵢ, nuisibleᵢ) pour i de 1 à n ; bornes b₀ < b₁ < … < b_K
          action à évaluer : score R, montant C_dommage ; coût d'une revue C_revue
SORTIE  : "revue" ou "autoriser"
  POUR k DE 1 À K FAIRE
    Tₖ ← { i : b_(k−1) ≤ Rᵢ < b_k }  (la dernière tranche inclut b_K)
    SI Tₖ = ∅ ALORS p̂ₖ ← INDÉFINI
    SINON p̂ₖ ← (nombre de nuisibles dans Tₖ) / |Tₖ|
    FIN SI
  FIN POUR
  k ← tranche de R
  SI p̂ₖ = INDÉFINI ALORS RETOURNER "revue"        ▷ pas de donnée : prudence
  SI p̂ₖ × C_dommage > C_revue ALORS RETOURNER "revue" FIN SI
  RETOURNER "autoriser"
```

**Complexité :** O(n × K) en temps pour le calibrage tel qu'il est écrit, parce que chaque tranche parcourt tout l'historique ; un seul parcours qui range chaque action dans sa tranche le ramènerait à O(n + K), ou O(n log K) si l'on cherche la tranche par dichotomie. La décision coûte O(K) pour trouver la tranche, O(1) ensuite. En mémoire, O(K) pour les probabilités, plus la liste temporaire d'une tranche, O(n) au pire.

**Du squelette au code :** la boucle sur les tranches est `calibrer(historique, bornes)`, avec `zip(bornes, bornes[1:])` pour les paires de bornes et la condition `haut == bornes[-1] and r == haut` pour fermer la dernière tranche ; la recherche de la tranche est `tranche(r, bornes)` ; la règle de coût est `escalader(p, c_dommage, c_revue)`. Le programme n'a pas de tranche vide sur son historique ; la règle « pas de donnée, donc revue » est la convention à appliquer en production, et `calibrer([], bornes)` vérifie que la valeur `None` est bien renvoyée.

## Cas d'usage réels aux Émirats

Les poids, seuils, coûts et montants sont illustratifs ; on les calibre sur l'historique de chaque métier.

### Banque — une recommandation d'investissement peu fidèle à ses sources

L'assistant d'investissement d'une banque de détail de Dubaï propose à un client un fonds, en s'appuyant sur les fiches produits et sur le profil de risque déclaré. L'action touche des données personnelles (s = 0,7), elle est une écriture réversible, puisque la recommandation peut être retirée avant souscription (g = 0,5), et la réponse n'est fidèle qu'à 60 % aux documents cités (F = 0,6, donc u = 0,4). Le score vaut 0,4 × 0,7 + 0,4 × 0,5 + 0,2 × 0,4 = 0,28 + 0,20 + 0,08 = 0,56, entre les deux seuils : un conseiller relit avant envoi. L'ancienne version de ce fichier le formulait déjà, il faut une validation humaine avant toute recommandation d'investissement douteuse ; le score dit lesquelles le sont. Un virement de 50 000 AED, lui, passe en revue par le veto sur le montant, quel que soit son score. Sans revue, une recommandation fondée sur une fiche mal lue exposerait la banque à une plainte pour défaut d'adéquation. On suit la part des recommandations envoyées en revue et la part de celles que le conseiller modifie.

### Crypto — un retrait irréversible que la somme laissait passer

Une plateforme d'actifs virtuels agréée par la VARA laisse son agent préparer les retraits de ses clients vers des adresses externes. Un retrait de 8 000 AED vers une adresse publique, avec un modèle confiant, donne s = 0,1, g = 1 et u = 0,1, soit R = 0,46 : sous τ_revue = 0,5, la somme pondérée l'autoriserait seule (démonstration, point 4). Or un transfert sur la chaîne ne se rattrape pas. Le veto sur l'irréversibilité l'envoie en revue : un opérateur vérifie l'adresse, son ancienneté pour ce client et l'historique de retraits, ce que l'ancienne version résumait par « confirmation humaine pour toute transaction au-dessus d'un certain risque ». La plateforme doit pouvoir justifier chaque retrait approuvé : la décision, le score et ses trois entrées sont inscrits dans le journal chaîné de l'étape 66. On suit le nombre de retraits vers une adresse nouvelle et le délai médian de revue.

### Assurance — une indemnité sur un dossier de santé

Un assureur auto et santé, supervisé par la CBUAE, laisse son agent proposer des indemnités calculées par l'outil de l'étape 12. Une indemnité de 13 900 AED sur un dossier qui contient des données de santé donne s = 1, g = max(0,5 ; 13 900 / 50 000) = 0,5, et, avec une réponse fidèle à 92 %, u = 0,08 : R = 0,40 + 0,20 + 0,016 = 0,616, en revue. Une même indemnité sur un sinistre auto sans donnée de santé (s = 0,3) donnerait 0,12 + 0,20 + 0,016 = 0,336, sous τ_revue : elle partirait directement, ce qui est le but du score, réserver l'attention humaine aux cas qui la méritent. Au coût espéré, avec une probabilité de dommage calibrée de 0,1 pour la tranche basse, une indemnité de 13 900 AED vaut 1 390 AED de perte espérée, plus que les 25 AED d'une revue : l'assureur peut décider de revoir aussi ces cas, et c'est le calcul du point 5 qui tranche. On suit le taux d'indemnités modifiées en revue, par tranche de score.

### RH — une lecture autorisée, un dépôt sous veto

Un cabinet RH multi-émirats laisse son agent lire les contrats des salariés pour répondre aux gestionnaires : données personnelles (s = 0,7), lecture (g = 0), réponse fidèle à 90 % (u = 0,1), soit R = 0,28 + 0 + 0,02 = 0,30. L'action est autorisée sans revue, ce qui garde l'agent utile au quotidien. Le dépôt mensuel du fichier de salaires dans le système WPS, lui, est irréversible une fois transmis : le veto l'envoie toujours en revue, même quand le score est bas, et l'approbation se fait dans l'outil avec un délai qui vaut refus (étape 66). Le cabinet a choisi d'appliquer aussi le veto sur le montant aux indemnités communiquées aux salariés : celle de fin de service calculée par l'outil canonique (55 000 AED pour 10 000 AED de base et sept ans) dépasse 25 000 AED, et un gestionnaire la relit avant l'envoi. Sans veto, un fichier WPS erroné partirait dès que le modèle serait sûr de lui. On suit le nombre de dépôts corrigés en revue.

### Immobilier — un document juridique toujours relu

Une agence et un promoteur de Dubaï et d'Abu Dhabi laissent leur agent préparer des brouillons de contrats de location. Un brouillon pour un locataire identifié (s = 0,7, écriture réversible g = 0,5), avec une réponse fidèle à 95 % au modèle de contrat (u = 0,05), donne R = 0,28 + 0,20 + 0,01 = 0,49, juste sous τ_revue. L'agence ne veut pourtant aucun document juridique sans relecture, comme le disait l'ancienne version de ce fichier : elle ajoute le type « document juridique » à la liste des types sous veto, plutôt que de baisser τ_revue pour toutes les actions. C'est la bonne façon d'exprimer une règle métier absolue : un veto par type, et non un réglage de poids. Le prix au sqft et les frais DLD de 4 % viennent d'outils, ce qui garde l'incertitude basse. On suit le nombre de clauses modifiées par les juristes par brouillon.

### Secteur public — un dépôt bloqué après un signal d'injection

Une entité de services publics en ligne, accessible par UAE Pass, laisse son assistant déposer des démarches au nom de l'usager. Une demande touche des données d'identité (s = 1) et constitue une écriture réversible tant que la démarche n'est pas instruite (g = 0,5). Quand une pièce jointe a déclenché un signal d'injection à l'étape 66, l'incertitude est relevée à 0,9, quelle que soit la fidélité : R = 0,40 + 0,20 + 0,18 = 0,78 ≥ τ_blocage = 0,75, le dépôt est bloqué et l'usager est invité à vérifier sa pièce. Sans le signal, avec u = 0,1, le score aurait valu 0,62 et la démarche serait passée en revue. Le score combine ainsi un signal de sécurité et des signaux métier dans une seule décision, sans que le détecteur, peu précis en production, ne bloque seul. On suit le nombre de dépôts bloqués et la part de ceux qui étaient réellement piégés.

## Pièges et limites

- **Lire le score comme une probabilité.** 0,54 n'est pas « 54 % de risque ». Pour comparer à un coût, on calibre d'abord sur l'historique (démonstration, point 7).
- **Mettre l'irréversibilité dans la somme.** Une moyenne pondérée compense : avec w_g < τ_revue, aucune action irréversible ne déclenche seule une revue (point 4). Ce qui ne doit jamais se compenser va dans un veto.
- **Utiliser un seul seuil pour bloquer et pour faire relire.** On bloque trop, ou l'on ne relit rien. Deux seuils, τ_revue < τ_blocage.
- **Mélanger des signaux bruts.** Une perplexité de 40 ou un montant en AED ne s'additionnent pas à une probabilité. Chaque entrée est ramenée dans [0 ; 1] par une transformation croissante, choisie et documentée.
- **Fixer les seuils une fois pour toutes.** La distribution des scores change avec le modèle, le prompt et le trafic. On recalibre après chaque changement, et l'on suit la charge de revue.

### Exercice feuille blanche

1. Sans regarder le code, écrire `score_risque` et `decider`, avec leurs contrôles, puis vérifier (0,3 ; 1 ; 0,1) avec et sans veto.
2. Prédire, puis vérifier : avec les poids (0,3 ; 0,5 ; 0,2) et τ_revue = 0,5, le retrait crypto (0,1 ; 1 ; 0,1) passe-t-il encore sans veto ? (Réponse : R = 0,03 + 0,50 + 0,02 = 0,55 ≥ 0,5, il passe en revue ; c'est le cas w_g ≥ τ du point 4, au prix d'un score déformé pour les autres actions.)
3. Trouver le bug : une variante de `decider` teste `if r >= tau_revue or veto_actif: return "revue"` **avant** le test du blocage. Que devient une action de score 0,80 sous veto ? (Réponse : « revue » au lieu de « bloquer » ; le veto adoucit alors la décision, ce qu'il ne doit jamais faire.)
4. Calculer : une revue coûte 40 AED et l'on estime p_min = 0,002. Quel est le montant du veto ? Et le seuil de Bayes pour C_FP = 40 et C_FN = 20 000 ? (Réponse : 40 / 0,002 = 20 000 AED ; 40 / 20 040 ≈ 0,001996.)

## Pour aller plus loin

D'autres agrégations évitent la compensation sans veto : le maximum pondéré, ou le produit probabilité × gravité, p × G, qui est directement la perte espérée en AED et se compare au coût d'une revue (c'est la section 6 du programme). Les poids eux-mêmes peuvent s'apprendre par une régression logistique sur l'historique, qui produit d'emblée un score calibré. Quand le signal est une distribution plutôt qu'un compteur, par exemple la répartition des montants des virements d'une journée comparée à celle du mois précédent, la divergence KL de l'étape 50 le résume, et 1 − e^(−KL) le ramène dans [0 ; 1] pour entrer dans le score.

> Suite : [Sandbox d'exécution](<67b-Sandbox-d-Execution.md>) — étape 67 bis.
