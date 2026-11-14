# Étape 50 — Précision, Rappel, F1-Score et Divergence de Kullback-Leibler

> Étape 50 du parcours · Prérequis : [A2A et édition par diff](<../09-MCP/49b-A2A-et-Edition-par-Diff.md>) · Suite : [Spécificité, VPN et AUC](<51-Specificite-NPV-AUC.md>)

**Dossier :** 10-Evaluation  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers

## Définition

La précision, le rappel et le F1 évaluent une **décision binaire** de l'agent : signaler ou non, appeler un outil ou non, ramener un document ou non. On compte les décisions dans quatre cases. La **précision** répond à la question « quand l'agent dit oui, a-t-il raison ? ». Le **rappel** répond à « parmi les vrais oui, combien l'agent en a-t-il trouvé ? ». Le **F1** résume les deux par leur moyenne harmonique, et le **Fβ** permet de donner plus de poids à l'un des deux. La **divergence de Kullback-Leibler** (KL) mesure autre chose : l'écart entre deux distributions de probabilité, par exemple la distribution de référence des issues et celle que l'agent produit. Elle est nulle si et seulement si les deux distributions sont identiques, et elle devient très grande quand l'agent est sûr de lui sur une mauvaise issue.

## Rôle dans un agent

Ces mesures servent surtout au moment **observer** de la boucle percevoir → décider → agir → observer : on rejoue l'agent sur un jeu étiqueté (étape 13 bis) et on compte. Elles jugent chaque composant qui prend une décision oui/non : le **détecteur d'un garde-fou** (bloquer ou laisser passer), le **routeur** qui décide d'appeler un outil, le **retriever** qui place un document dans le top-k (étapes 25 et 26), le **juge** qui déclare une affirmation fidèle (étape 54). La KL intervient à deux endroits. Hors ligne, elle surveille une **dérive** : la répartition des décisions de la semaine s'éloigne-t-elle de celle du trimestre de référence ? En ligne, elle sert de **garde-fou** au moment **décider** : si la distribution produite par l'agent s'écarte trop d'une référence, la réponse part en revue humaine avant d'**agir**. C'est aussi la KL qui se cache dans la perte d'entropie croisée de l'entraînement (démonstration, point 6) et dans la perplexité de l'étape 52.

## Équation complète

Dans ce fichier, P et Q désignent toujours des distributions. La précision s'écrit Préc et le rappel Rap.

La matrice de confusion range chaque décision dans l'une des quatre cases. Les lignes donnent la réalité, les colonnes la prédiction, comme dans scikit-learn et à l'étape 51 :

$$
\begin{array}{c|cc}
 & \text{prédit positif} & \text{prédit négatif} \\ \hline
\text{réel positif} & TP & FN \\
\text{réel négatif} & FP & TN
\end{array}
$$

La précision se lit dans la colonne « prédit positif », le rappel dans la ligne « réel positif ».

Précision et rappel :

$$
\text{Préc} = \frac{TP}{TP + FP}
\qquad
\text{Rap} = \frac{TP}{TP + FN}
$$

F1, sous ses deux formes (taux, puis comptes) :

$$
F_1 = \frac{2 \cdot \text{Préc} \cdot \text{Rap}}{\text{Préc} + \text{Rap}} = \frac{2\,TP}{2\,TP + FP + FN}
$$

Fβ, sous ses deux formes :

$$
F_\beta = \frac{(1 + \beta^2)\,\text{Préc}\cdot\text{Rap}}{\beta^2\,\text{Préc} + \text{Rap}} = \frac{(1 + \beta^2)\,TP}{(1 + \beta^2)\,TP + \beta^2\,FN + FP}
$$

Divergence de Kullback-Leibler, entropie et entropie croisée (logarithme népérien) :

$$
D_{KL}(P \parallel Q) = \sum_{x} P(x) \ln \frac{P(x)}{Q(x)}
$$

$$
H(P) = -\sum_x P(x) \ln P(x)
\qquad
H(P, Q) = -\sum_x P(x) \ln Q(x) = H(P) + D_{KL}(P \parallel Q)
$$

## Décryptage des symboles

$$
TP,\; FP,\; FN,\; TN
$$

**Sens :** vrais positifs (l'agent dit oui, c'était oui), faux positifs (il dit oui, c'était non : fausse alerte), faux négatifs (il dit non, c'était oui : cas raté), vrais négatifs (il dit non, c'était non) · **Type / plage :** entiers ≥ 0 · **Variable Python :** `tp`, `fp`, `fn` (TN ne sert pas ici ; il revient à l'étape 51).

$$
\text{Préc}
$$

**Sens :** part des oui de l'agent qui étaient justes · **Type / plage :** réel dans [0, 1], non défini si l'agent n'a jamais dit oui · **Variable Python :** `precision(tp, fp)`, qui renvoie `None` dans ce cas.

$$
\text{Rap}
$$

**Sens :** part des vrais oui que l'agent a trouvés · **Type / plage :** réel dans [0, 1], non défini s'il n'y avait aucun positif · **Variable Python :** `rappel(tp, fn)`.

$$
F_1,\; F_\beta
$$

**Sens :** moyenne harmonique de Préc et Rap, simple (F1) ou pondérée (Fβ) · **Type / plage :** réel dans [0, 1] · **Variable Python :** `f_beta(p, r, beta)` à partir des taux, `f_beta_comptes(tp, fp, fn, beta)` à partir des comptes.

$$
\beta
$$

**Sens :** réglage du poids du rappel ; β > 1 favorise le rappel (F2 : un oubli coûte quatre fausses alertes), β < 1 favorise la précision · **Type / plage :** réel > 0 · **Variable Python :** `beta`.

$$
P,\; Q
$$

**Sens :** P est la distribution de référence (la « vérité » ou la période de référence), Q celle que produit l'agent, sur les mêmes issues et dans le même ordre · **Type / plage :** listes de réels ≥ 0 de somme 1 · **Variable Python :** `P`, `Q`.

$$
D_{KL}(P \parallel Q)
$$

**Sens :** information perdue quand on utilise Q à la place de P ; se lit « divergence de P par rapport à Q » · **Type / plage :** réel ≥ 0, éventuellement +∞ ; pas symétrique · **Variable Python :** `divergence_kl(P, Q)`.

$$
H(P),\; H(P, Q)
$$

**Sens :** entropie de P (incertitude propre de la référence) et entropie croisée (surprise moyenne quand on code P avec Q) · **Type / plage :** réels ≥ 0, en nats · **Variable Python :** `entropie(P)`, `entropie_croisee(P, Q)`.

$$
\tau
$$

**Sens :** seuil du garde-fou ; au-dessus, la réponse part en revue humaine · **Type / plage :** réel > 0, à calibrer · **Variable Python :** `seuil` (2.5 dans l'exemple, valeur illustrative).

## Démonstration

### 1. Le F1 en comptes : 2TP / (2TP + FP + FN)

La moyenne harmonique de deux nombres est l'inverse de la moyenne de leurs inverses :

$$
F_1 = \frac{2}{\dfrac{1}{\text{Préc}} + \dfrac{1}{\text{Rap}}}
$$

On remplace chaque inverse par sa définition, parce que 1/Préc = (TP + FP)/TP et 1/Rap = (TP + FN)/TP :

$$
F_1 = \frac{2}{\dfrac{TP + FP}{TP} + \dfrac{TP + FN}{TP}} = \frac{2\,TP}{2\,TP + FP + FN}
$$

Ce calcul suppose TP > 0. La forme en comptes a un avantage : elle reste définie quand la précision ne l'est pas. Un agent qui n'a rien signalé alors qu'il y avait 10 positifs a TP = FP = 0 : sa précision n'existe pas, mais son F1 en comptes vaut 0 / (0 + 0 + 10) = 0, ce qui est le bon verdict. Le F1 n'est indéfini que si TP = FP = FN = 0 : il n'y avait rien à trouver et rien n'a été signalé. Le programme renvoie alors `None`.

### 2. Le F1 est coincé entre min(Préc, Rap) et la moyenne arithmétique

**Majoration.** On veut montrer que F1 ≤ (Préc + Rap)/2. Les deux taux sont positifs, donc on peut multiplier par 2(Préc + Rap) sans changer le sens :

$$
\frac{2\,\text{Préc}\,\text{Rap}}{\text{Préc} + \text{Rap}} \le \frac{\text{Préc} + \text{Rap}}{2}
\iff 4\,\text{Préc}\,\text{Rap} \le (\text{Préc} + \text{Rap})^2
\iff 0 \le (\text{Préc} - \text{Rap})^2
$$

La dernière inégalité est vraie parce qu'un carré est positif. L'égalité a lieu si et seulement si Préc = Rap.

**Minoration.** Supposons Préc ≤ Rap. Alors Préc + Rap ≤ 2 Rap, donc

$$
F_1 = \frac{2\,\text{Préc}\,\text{Rap}}{\text{Préc} + \text{Rap}} \ge \frac{2\,\text{Préc}\,\text{Rap}}{2\,\text{Rap}} = \text{Préc} = \min(\text{Préc}, \text{Rap})
$$

C'est pour cela qu'on prend la moyenne harmonique et non la moyenne arithmétique : avec Préc = 1 et Rap = 0, la moyenne arithmétique vaudrait 0,5 et féliciterait un agent qui ne trouve rien ; le F1 vaut 0. Avec Préc = 1 et Rap = 0,2, la moyenne arithmétique vaut 0,6, le F1 0,333 : il reste près du plus faible des deux.

### 3. Fβ est une moyenne harmonique pondérée, et β² multiplie la précision

On donne le poids 1/(1 + β²) à 1/Préc et le poids β²/(1 + β²) à 1/Rap :

$$
\frac{1}{F_\beta} = \frac{1}{1+\beta^2}\cdot\frac{1}{\text{Préc}} + \frac{\beta^2}{1+\beta^2}\cdot\frac{1}{\text{Rap}} = \frac{\text{Rap} + \beta^2\,\text{Préc}}{(1+\beta^2)\,\text{Préc}\,\text{Rap}}
$$

En retournant la fraction, on retrouve la formule du fichier :

$$
F_\beta = \frac{(1+\beta^2)\,\text{Préc}\,\text{Rap}}{\beta^2\,\text{Préc} + \text{Rap}}
$$

Le poids du rappel est β² fois celui de la précision : avec β = 2, il pèse quatre fois plus. Au dénominateur, c'est pourtant la **précision** que β² multiplie. Les deux affirmations ne se contredisent pas : le dénominateur vient de 1/Rap pondéré par β², multiplié par Préc·Rap. L'ancien commentaire du code (« le coefficient du rappel dans le dénominateur est β² ») était donc faux, et l'erreur inverse, écrire `p + b2 * r`, calcule en réalité F₁/β, qui favorise la précision (exercice 3).

En comptes, le même calcul que le point 1 donne

$$
F_\beta = \frac{(1+\beta^2)\,TP}{(1+\beta^2)\,TP + \beta^2\,FN + FP}
$$

La lecture est directe : un faux négatif coûte β² fois un faux positif. Avec Préc = 0,70 et Rap = 0,99, F1 = 1,386 / 1,69 = 0,8201 et F2 = 3,465 / 3,79 = 0,9142. Le F2 monte parce que le rappel, déjà excellent, pèse plus.

### 4. La KL n'est pas symétrique

Avec P = (0,70 ; 0,20 ; 0,10) et Q = (0,01 ; 0,01 ; 0,98), un agent sûr de lui et faux :

$$
D_{KL}(P \parallel Q) = 0{,}70 \ln 70 + 0{,}20 \ln 20 + 0{,}10 \ln\frac{0{,}10}{0{,}98} = 2{,}9739 + 0{,}5991 - 0{,}2282 = 3{,}3449
$$

$$
D_{KL}(Q \parallel P) = 0{,}01 \ln\frac{0{,}01}{0{,}70} + 0{,}01 \ln\frac{0{,}01}{0{,}20} + 0{,}98 \ln\frac{0{,}98}{0{,}10} = 2{,}1643
$$

Les deux valeurs diffèrent, donc la KL n'est pas une distance. D(P‖Q) punit surtout une issue que P rend fréquente et que Q rend rare ; D(Q‖P) punit une issue que Q rend fréquente et que P rend rare. Le choix du sens est une décision d'ingénierie, à écrire dans la documentation du garde-fou.

### 5. Le terme qui explose

Quand Q(x) → 0 alors que P(x) > 0 reste fixe, le rapport P(x)/Q(x) tend vers +∞, donc son logarithme aussi :

$$
\ln\frac{P(x)}{Q(x)} \xrightarrow[Q(x) \to 0]{} +\infty
$$

L'ancienne phrase « le logarithme tend vers moins l'infini » se trompait de signe : c'est ln(Q/P) qui tend vers −∞, et ln(P/Q) vers +∞. Avec P(x) = 0,9 et Q(x) = 10⁻⁶, le terme vaut 0,9 × ln(900 000) ≈ 12,34. Il n'y a pas de plafond, et si Q(x) = 0 exactement, la divergence vaut +∞.

### 6. Entropie croisée = entropie + KL

On ajoute et on retranche ∑ P ln P, ce qui ne change rien :

$$
H(P, Q) = -\sum_x P(x)\ln Q(x) = -\sum_x P(x)\ln P(x) + \sum_x P(x)\ln\frac{P(x)}{Q(x)} = H(P) + D_{KL}(P \parallel Q)
$$

Deux conséquences. D'abord, comme la KL est positive (point 7), H(P, Q) ≥ H(P) : aucun modèle ne descend sous l'incertitude propre des données. Ensuite, H(P) ne dépend pas de Q : minimiser la perte d'entropie croisée d'un modèle revient exactement à minimiser sa KL par rapport aux données. Sur l'exemple, H(P) = 0,2497 + 0,3219 + 0,2303 = 0,8018 et H(P, Q) = 0,8018 + 3,3449 = 4,1467. L'étape 52 prend l'exponentielle de cette quantité : c'est la perplexité.

### 7. Inégalité de Gibbs : la KL est positive, nulle seulement si P = Q

**Théorème.** Pour deux distributions P et Q sur le même ensemble fini, D_KL(P‖Q) ≥ 0, avec égalité si et seulement si P = Q.

La source de l'étape 43 (section « 3. Démonstration Mathématique : Non-Négativité de la Divergence KL ») applique Jensen sur toutes les issues. Elle divise alors par P(x) même là où P(x) = 0, et elle oublie le cas Q(x) = 0. Voici la preuve complète.

**Étape 1 — se restreindre au support de P.** On note S l'ensemble des issues où P(x) > 0. Les termes où P(x) = 0 valent 0 par convention, parce que t ln t → 0 quand t → 0. Si une issue x de S a Q(x) = 0, son terme vaut +∞ et D_KL = +∞ ≥ 0 : c'est fini. Sinon, tous les termes sont finis et

$$
-D_{KL}(P \parallel Q) = \sum_{x \in S} P(x) \ln\frac{Q(x)}{P(x)}
$$

**Étape 2 — Jensen.** Le logarithme est concave sur ]0, +∞[ et les poids P(x), x ∈ S, sont positifs de somme 1. L'inégalité de Jensen dit qu'une moyenne de logarithmes est inférieure au logarithme de la moyenne :

$$
\sum_{x \in S} P(x) \ln\frac{Q(x)}{P(x)} \le \ln\left(\sum_{x \in S} P(x)\,\frac{Q(x)}{P(x)}\right) = \ln\left(\sum_{x \in S} Q(x)\right)
$$

**Étape 3 — la masse de Q hors du support.** Q est positive partout et somme à 1 sur toutes les issues, donc sa somme sur S est au plus 1. Le logarithme étant croissant :

$$
\ln\left(\sum_{x \in S} Q(x)\right) \le \ln 1 = 0
$$

En enchaînant les étapes 2 et 3, −D_KL ≤ 0, donc D_KL ≥ 0.

**Étape 4 — le cas d'égalité.** D_KL = 0 exige l'égalité dans les deux inégalités. Le logarithme étant strictement concave, l'égalité de Jensen exige que Q(x)/P(x) soit une constante c sur S. L'égalité de l'étape 3 exige que la somme de Q sur S vaille 1, donc que Q soit nulle hors de S. Alors 1 = ∑ Q = c ∑ P = c sur S, donc c = 1 : Q = P sur S, et Q = 0 = P ailleurs. Réciproquement, si P = Q, chaque terme vaut P ln 1 = 0.

**Contre-exemple qui montre que l'étape 3 est indispensable.** Avec P = (0,5 ; 0,5 ; 0) et Q = (0,4 ; 0,4 ; 0,2), le rapport Q/P vaut 0,8 sur tout le support : Jensen est une égalité, les deux membres valent ln 0,8 = −0,2231. C'est l'étape 3 qui rend l'ensemble strictement négatif, parce que Q met 0,2 hors du support. La divergence vaut ln 1,25 = 0,2231 > 0. L'ancien code calculait `math.log(q / p)` sur chaque issue : il plantait (`ValueError`) dès que Q(x) = 0 avec P(x) > 0, et sa variable `interieur` était calculée puis écrasée sans servir.

**Variante sans Jensen.** On peut aussi utiliser ln t ≤ t − 1. Pour le prouver, on pose g(t) = t − 1 − ln t ; sa dérivée 1 − 1/t est négative sur ]0, 1[ et positive au-delà, donc g a son minimum en t = 1, où elle vaut 0. Alors

$$
-D_{KL}(P \parallel Q) = \sum_{x \in S} P(x)\ln\frac{Q(x)}{P(x)} \le \sum_{x \in S} P(x)\left(\frac{Q(x)}{P(x)} - 1\right) = \sum_{x \in S} Q(x) - 1 \le 0
$$

avec égalité seulement si Q(x)/P(x) = 1 partout sur S.

### 8. Exemple fait à la main (le code reprend ces nombres)

Dix documents sont vraiment utiles. Extraction large : TP = 2, FP = 8, FN = 8, donc Préc = 2/10 = 0,20, Rap = 2/10 = 0,20, F1 = 4/20 = 0,20. Extraction serrée : TP = 2, FP = 0, FN = 8, donc Préc = 1, Rap = 0,20, F1 = 4/12 = 0,333.

Choix d'un seuil d'alerte : le seuil A donne (TP, FP, FN) = (48, 80, 2), le seuil B (35, 15, 15). F1(A) = 96/178 = 0,539 et F1(B) = 70/100 = 0,700 : le F1 choisit B. F2(A) = 240/328 = 0,732 et F2(B) = 175/250 = 0,700 : le F2 choisit A, qui rate 2 cas au lieu de 15.

KL avec P = (0,70 ; 0,20 ; 0,10) et Q proche = (0,65 ; 0,25 ; 0,10) :

$$
0{,}70\ln\frac{0{,}70}{0{,}65} + 0{,}20\ln\frac{0{,}20}{0{,}25} + 0{,}10\ln 1 = 0{,}05188 - 0{,}04463 + 0 = 0{,}0072
$$

Avec un seuil de 2,5, la réponse proche (0,0072) passe et la réponse sûre d'elle et fausse (3,345) part en revue humaine.

## Effets et comportement

- **Le compromis précision / rappel.** Baisser le seuil fait dire oui plus souvent : le rappel ne peut que monter (les vrais positifs déjà trouvés le restent), la précision baisse en général, mais pas forcément à chaque pas. Un agent réglé pour être sûr à 100 % (Préc = 1) répond « je ne sais pas » très souvent et son rappel s'effondre.
- **Le F1 est nul dès qu'un des deux taux est nul**, et il reste proche du plus faible des deux (démonstration, point 2).
- **Si Q(x) se rapproche de 0 alors que P(x) est grand**, ln(P/Q) tend vers +∞ et la divergence devient gigantesque : l'agent a été très confiant dans une erreur, le pire scénario pour un garde-fou.
- **La température agit dans les deux sens.** Une température trop élevée aplatit Q et éloigne Q d'une référence P concentrée. Une température trop basse concentre Q sur sa première issue : si cette issue est la mauvaise, la KL explose.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| TP, FP, FN | `tp`, `fp`, `fn` |
| Préc, Rap | `precision(tp, fp)`, `rappel(tp, fn)` |
| Fβ à partir des taux | `f_beta(p, r, beta)` |
| Fβ à partir des comptes | `f_beta_comptes(tp, fp, fn, beta)` |
| P, Q | listes `P`, `Q` de même longueur |
| D_KL(P‖Q) | `divergence_kl(P, Q)` |
| H(P), H(P, Q) | `entropie(P)`, `entropie_croisee(P, Q)` |
| les deux inégalités de Gibbs | `gibbs_par_jensen(P, Q)` |
| τ | `seuil` dans `garde_fou(P, Q, seuil)` |

### Déroulé, ligne par ligne

On part de 10 documents vraiment utiles.

**`precision(tp, fp)`** et **`rappel(tp, fn)`**.

- `if tp < 0 or fp < 0` : un compteur négatif est une erreur de programme ; on lève `ValueError`.
- `if tp + fp == 0: return None` : si l'agent n'a jamais dit oui, la division n'a pas de sens. L'ancien code renvoyait 0, ce qui faisait entrer un « zéro » imaginaire dans les moyennes. La convention du parcours est `None` : non défini, et exclu des moyennes.
- Sinon `return tp / (tp + fp)` : extraction large, `tp = 2`, `fp = 8`, donc 2 / 10 = 0,20.
- `rappel` fait `tp / (tp + fn)` : 2 / (2 + 8) = 0,20.
- Extraction serrée : `tp = 2`, `fp = 0`, `fn = 8`. Précision 2/2 = 1. Rappel toujours 0,20, parce que les 8 documents ratés le sont toujours. Changer le top-k déplace un compteur, pas les deux.

**`f_beta(p, r, beta)`**.

- `if p is None or r is None: return None` : on ne moyenne pas un taux qui n'existe pas.
- `if p + r == 0.0: return 0.0` : les deux taux sont nuls, le F1 vaut 0 ; sans cette garde, la formule diviserait 0 par 0. Aucun `assert` du programme ne passe par cette branche : `f_beta(1.0, 0.0)`, testé en section 2, vaut bien 0, mais par la formule générale, puisque p + r = 1.
- `b2 = beta * beta` : 1 pour le F1, 4 pour le F2.
- `return (1.0 + b2) * p * r / (b2 * p + r)` : `b2` multiplie `p`, la précision. Avec p = 0,70 et r = 0,99 : F1 = 1,386 / 1,69 = 0,8201 ; F2 = 3,465 / 3,79 = 0,9142.

**`f_beta_comptes(tp, fp, fn, beta)`**.

- `den = (1 + b2) * tp + b2 * fn + fp` : le dénominateur de la forme en comptes, où `fn` est multiplié par `b2`.
- `if den == 0: return None` : rien à trouver, rien signalé.
- Agent muet, `tp = 0`, `fp = 0`, `fn = 10` : `den = 10`, le résultat vaut 0.0, alors que `f_beta(precision(0, 0), rappel(0, 10))` renvoie `None`. C'est pourquoi la forme en comptes est la référence pour le F1.

**`verifier_distribution(D)`** refuse une liste qui a une valeur négative ou dont la somme s'écarte de 1 de plus de 1e-9.

**`divergence_kl(P, Q)`** — la somme ∑ P ln(P/Q).

- `if len(P) != len(Q)` : les deux listes doivent parler des mêmes issues, dans le même ordre, sinon `zip` associerait « acceptable » avec « rejet ».
- `if p == 0.0: continue` : le terme 0 × ln(…) vaut 0 par continuité, et on n'appelle pas `log` sur 0.
- `if q == 0.0: return math.inf` : P > 0 et Q = 0, la divergence est infinie. C'est le cas `divergence_kl([0.9, 0.1], [0.0, 1.0])`.
- `total += p * math.log(p / q)` : `math.log` est le logarithme népérien ln. Sur Q proche, les trois termes valent 0,05188, −0,04463 et 0 : total 0,0072.

**`entropie(P)`** renvoie −∑ p ln p sur les p > 0 : 0,8018 pour la référence. **`entropie_croisee(P, Q)`** renvoie −∑ p ln q, ou +∞ si un q est nul là où p ne l'est pas : 4,1467 pour Q faux.

**`gibbs_par_jensen(P, Q)`** — les deux inégalités de la preuve.

- `support` garde les couples où `p > 0.0` : c'est l'ensemble S de l'étape 1.
- `masse_q` additionne Q sur ce support : 1 pour Q proche, 0,8 pour le contre-exemple « hors support ».
- Si un `q` du support est nul, `gauche = -math.inf` : pas d'exception, contrairement à l'ancien code.
- Sinon `gauche` vaut ∑ P ln(Q/P), l'opposé de la KL : −0,0072 pour Q proche.
- `milieu = math.log(masse_q)` : ln 1 = 0 pour Q proche, ln 0,8 = −0,2231 pour le contre-exemple, où `gauche` et `milieu` sont égaux.

**`garde_fou(P, Q, seuil)`** calcule `score = divergence_kl(P, Q)` puis renvoie `score, score > seuil`. Le seuil n'est pas dans la somme : c'est la comparaison d'après.

**`main()`**, bloc par bloc.

1. Les deux extractions et l'agent muet. Les `assert` vérifient 0,2, 0,2 et 1,0, puis l'égalité des formes en taux et en comptes : 4/12 et 4/20.
2. Trois couples (P, R) : (1, 0), (1 ; 0,2), (0,6 ; 0,6). Pour chacun, `min(p, r) <= f1 <= (p + r) / 2`. Le dernier couple montre l'égalité quand P = R.
3. F1 et F2 pour 0,70 et 0,99, arrondis à 0,8201 et 0,9142. La forme en comptes et la forme en taux donnent le même F2 pour (8, 2, 4) : 40/58. La moyenne harmonique pondérée, avec les poids 1/5 et 4/5, redonne le même nombre. Puis les seuils A et B : le F1 choisit B, le F2 choisit A.
4. La KL de P avec elle-même vaut 0 ; avec Q proche, 0,0072 ; avec Q faux, 3,345 ; dans l'autre sens, 2,164.
5. Le terme isolé 0,9 × ln(0,9 / 10⁻⁶) = 12,34, puis la divergence infinie quand Q = 0.
6. H(P, faux) = H(P) + D(P‖faux), à 1e-12 près.
7. Les trois cas de Gibbs : proche, hors support, Q = 0. Pour chacun, `gauche <= milieu <= 0`, et `gauche` vaut l'opposé de la KL.
8. Le seuil 2,5 laisse passer Q proche et envoie Q faux en revue humaine. Enfin, deux entrées invalides (un compteur négatif, une distribution de somme 1,1) doivent lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`precision(tp, fp)`** — Cette fonction est le contrôleur qui ne regarde que ce que l'agent a affirmé : elle reçoit le nombre de vrais positifs et de faux positifs, lève `ValueError` si l'un des deux compteurs est négatif, renvoie `None` si leur somme est nulle, parce qu'un agent qui n'a jamais dit oui n'a pas de précision, et sinon renvoie TP ÷ (TP + FP). Avec l'extraction large du RAG, 2 documents utiles parmi 10 renvoyés, elle donne 0,20, et avec l'extraction serrée, 2 sur 2, elle donne 1 ; c'est la première brique de toutes les sections de `main`, des documents retrouvés jusqu'aux seuils A et B.

**`rappel(tp, fn)`** — Celle-ci est l'inspectrice qui part du terrain plutôt que des déclarations : elle reçoit les vrais positifs et les faux négatifs, refuse par une `ValueError` un compteur négatif, renvoie `None` s'il n'y avait aucun cas positif à trouver, et sinon renvoie TP ÷ (TP + FN), la part des cas réels que l'agent a bien attrapés. Sur les 10 documents vraiment utiles, l'agent en retrouve 2 et en manque 8, d'où 0,20 dans les deux extractions, large comme serrée : changer le top-k a déplacé les faux positifs, pas les oublis. L'agent muet, qui ne trouve rien sur 10, obtient un rappel de 0.

**`f_beta(p, r, beta)`** — Cette fonction est la balance de l'évaluateur, qui pèse précision et rappel selon un réglage β, valant 1 par défaut : elle refuse par une `ValueError` un β nul ou négatif, renvoie `None` si l'un des deux taux n'existe pas, 0 si tous deux sont nuls, et sinon (1 + β²) P R ÷ (β² P + R), où β² multiplie la précision au dénominateur, si bien que le rappel pèse β² fois plus. Pour P = 0,70 et R = 0,99, elle renvoie 0,8201 en F1 et 0,9142 en F2 ; `main` s'en sert aussi pour montrer que le F1 reste coincé entre le plus petit des deux taux et leur moyenne arithmétique, avec égalité quand P = R = 0,6.

**`f_beta_comptes(tp, fp, fn, beta)`** — Celle-ci fait le même travail que `f_beta`, mais comme un comptable qui préfère les pièces du dossier aux pourcentages : elle reçoit directement les trois compteurs et β, refuse un β non positif, calcule le dénominateur (1 + β²) TP + β² FN + FP, où chaque oubli coûte β² fausses alertes, et renvoie `None` seulement si ce dénominateur est nul, sinon (1 + β²) TP divisé par lui. L'agent muet (0, 0, 10) reçoit ainsi 0 au lieu du `None` de la forme en taux, et (8, 2, 4) donne 40/58 en F2 ; c'est elle qui départage les seuils A et B, le F1 choisissant B et le F2 choisissant A.

**`verifier_distribution(D)`** — Cette fonction est le douanier posté à l'entrée de toute comparaison de distributions : elle reçoit une liste de probabilités, vérifie qu'aucune valeur n'est négative et que leur somme ne s'écarte pas de 1 de plus de 10⁻⁹, et lève une `ValueError` dans le cas contraire. Elle ne renvoie rien quand tout est en règle ; `divergence_kl` l'appelle sur ses deux arguments, ce qui permet à `main` de vérifier, à la toute fin, qu'une pseudo-distribution [0,5 ; 0,6], de somme 1,1, est bien refusée au lieu de produire un score absurde.

**`divergence_kl(P, Q)`** — Celle-ci mesure la surprise d'un juge qui croyait à la distribution Q et découvre la distribution P : elle vérifie que les deux listes ont la même longueur et sont de vraies distributions, puis additionne, issue par issue, P ln(P/Q), en sautant les termes où P vaut 0 par la convention 0 × ln(…) = 0 et en renvoyant aussitôt `math.inf` dès qu'une issue a P > 0 et Q = 0. Elle renvoie ce total, exactement 0 pour D(P‖P), 0,0072 pour Q proche, 3,345 pour Q faux et 2,164 dans l'autre sens, ce qui prouve qu'elle n'est pas symétrique ; c'est aussi le score que `garde_fou` compare au seuil 2,5.

**`entropie(P)`** — Cette fonction est le météorologue qui chiffre l'incertitude d'une prévision : elle reçoit une distribution P, ignore les issues de probabilité nulle et renvoie −Σ p ln p sur les autres, en nats puisque `math.log` est le logarithme népérien. Elle ne vérifie pas que P est une distribution, ce rôle étant laissé à l'appelant. Pour la distribution de référence 0,70, 0,20 et 0,10 (acceptable, limite, rejet), elle renvoie 0,8018, et `main` s'en sert à la section 6 pour vérifier l'identité H(P, Q) = H(P) + D(P‖Q).

**`entropie_croisee(P, Q)`** — Celle-ci mesure le coût moyen qu'on paie quand on code les issues réelles, tirées de P, avec le dictionnaire prévu pour Q : elle parcourt les deux listes côte à côte, saute les issues où P vaut 0, renvoie `math.inf` dès qu'une issue réelle reçoit une probabilité nulle de Q, et sinon accumule −p ln q. Elle renvoie ce total, 4,1467 pour la référence face à la distribution fausse, soit exactement 0,8018 + 3,3449, l'entropie plus la divergence ; c'est précisément ce que la section 6 de `main` vérifie à 10⁻¹² près.

**`gibbs_par_jensen(P, Q)`** — Cette fonction rejoue la preuve de l'inégalité de Gibbs comme un professeur qui écrit au tableau les deux marches de l'escalier : elle garde le support de P, les couples où p > 0, additionne Q sur ce support, puis calcule le terme de gauche Σ P ln(Q/P), qu'elle fixe à −∞ sans lever d'exception si un q du support est nul, et le terme du milieu ln(Σ Q). Elle renvoie le couple (gauche, milieu), que `main` contrôle sur trois cas : Q proche, où gauche vaut −0,0072 et milieu 0 ; Q hors support, où les deux valent −0,2231 ; Q nul, où gauche vaut −∞ et milieu 0 ; à chaque fois, gauche ≤ milieu ≤ 0.

**`garde_fou(P, Q, seuil)`** — Celle-ci est la sentinelle qui décide si une réponse peut sortir seule ou doit passer devant un humain : elle reçoit la distribution de référence, celle que propose l'agent et un seuil, calcule la divergence avec `divergence_kl`, et renvoie un couple formé de ce score et d'un booléen qui vaut vrai quand le score dépasse le seuil. Le seuil n'entre pas dans la somme, il ne sert qu'à la comparaison d'après ; avec 2,5, la distribution proche, à 0,007, est laissée passer, tandis que la distribution fausse, à 3,345, part en revue humaine.

**`main()`** — C'est le chef d'orchestre des huit vérifications du fichier : il compare d'abord les extractions large et serrée d'un RAG à 10 documents utiles (F1 de 0,200 et 0,333) et l'agent muet, montre ensuite que le F1 est une moyenne harmonique encadrée par min(P, R) et (P + R) ÷ 2, calcule F1 = 0,8201 et F2 = 0,9142, puis départage les seuils A et B. Il passe alors aux distributions, avec les divergences 0, 0,0072, 3,345 et 2,164, le terme isolé qui vaut 12,34, l'identité entre entropie croisée et entropie plus KL, les trois cas de Gibbs et le garde-fou à 2,5 ; il finit par deux entrées invalides qui doivent lever `ValueError`, et n'imprime « OK » que si chaque `assert` est passé.

```python
"""Étape 50 — précision, rappel, F1, F-bêta, divergence KL, inégalité de Gibbs, seuil de blocage."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def precision(tp: int, fp: int) -> float | None:
    """TP / (TP + FP). None si l'agent n'a jamais dit oui : la précision n'est pas définie."""
    if tp < 0 or fp < 0:
        raise ValueError("compteurs négatifs")
    if tp + fp == 0:
        return None
    return tp / (tp + fp)


def rappel(tp: int, fn: int) -> float | None:
    """TP / (TP + FN). None s'il n'y avait aucun cas positif à trouver."""
    if tp < 0 or fn < 0:
        raise ValueError("compteurs négatifs")
    if tp + fn == 0:
        return None
    return tp / (tp + fn)


def f_beta(p: float | None, r: float | None, beta: float = 1.0) -> float | None:
    """(1 + β²) P R / (β² P + R). Au dénominateur, β² multiplie la précision ; le rappel pèse β² fois plus."""
    if beta <= 0:
        raise ValueError("beta > 0")
    if p is None or r is None:
        return None
    if p + r == 0.0:
        return 0.0
    b2 = beta * beta
    return (1.0 + b2) * p * r / (b2 * p + r)


def f_beta_comptes(tp: int, fp: int, fn: int, beta: float = 1.0) -> float | None:
    """(1 + β²) TP / ((1 + β²) TP + β² FN + FP) : un oubli coûte β² fois une fausse alerte."""
    if beta <= 0:
        raise ValueError("beta > 0")
    b2 = beta * beta
    den = (1 + b2) * tp + b2 * fn + fp
    if den == 0:
        return None
    return (1 + b2) * tp / den


def verifier_distribution(D: list[float]) -> None:
    if any(x < 0 for x in D) or abs(sum(D) - 1.0) > 1e-9:
        raise ValueError("une distribution a des valeurs >= 0 de somme 1")


def divergence_kl(P: list[float], Q: list[float]) -> float:
    """D_KL(P || Q) = Σ P(x) ln(P(x) / Q(x)). Convention 0 · ln(0 / q) = 0 ; P(x) > 0 et Q(x) = 0 donnent +∞."""
    if len(P) != len(Q):
        raise ValueError("P et Q doivent porter sur les mêmes issues")
    verifier_distribution(P)
    verifier_distribution(Q)
    total = 0.0
    for p, q in zip(P, Q):
        if p == 0.0:
            continue
        if q == 0.0:
            return math.inf
        total += p * math.log(p / q)
    return total


def entropie(P: list[float]) -> float:
    """H(P) = −Σ P ln P."""
    return -sum(p * math.log(p) for p in P if p > 0.0)


def entropie_croisee(P: list[float], Q: list[float]) -> float:
    """H(P, Q) = −Σ P ln Q ; +∞ si Q met 0 là où P met de la masse."""
    total = 0.0
    for p, q in zip(P, Q):
        if p == 0.0:
            continue
        if q == 0.0:
            return math.inf
        total -= p * math.log(q)
    return total


def gibbs_par_jensen(P: list[float], Q: list[float]) -> tuple[float, float]:
    """Les deux inégalités de la preuve, sur le support S de P :
    Σ_S P ln(Q/P)  ≤  ln(Σ_S Q)  ≤  ln 1 = 0.   Renvoie (gauche, milieu)."""
    support = [(p, q) for p, q in zip(P, Q) if p > 0.0]
    masse_q = sum(q for _, q in support)
    if any(q == 0.0 for _, q in support):
        gauche = -math.inf          # un terme ln(0) : la KL vaut +∞, aucune exception
    else:
        gauche = sum(p * math.log(q / p) for p, q in support)
    milieu = math.log(masse_q) if masse_q > 0.0 else -math.inf
    return gauche, milieu


def garde_fou(P: list[float], Q: list[float], seuil: float) -> tuple[float, bool]:
    """Si la divergence dépasse le seuil, la réponse part en revue humaine."""
    score = divergence_kl(P, Q)
    return score, score > seuil


def main() -> None:
    print("1. RAG : le top-k déplace un compteur à la fois (10 documents utiles)")
    p_l, r_l = precision(2, 8), rappel(2, 8)
    p_s, r_s = precision(2, 0), rappel(2, 8)
    print(f"  large  P = {p_l:.2f}  R = {r_l:.2f}  F1 = {f_beta(p_l, r_l):.3f}")
    print(f"  serré  P = {p_s:.2f}  R = {r_s:.2f}  F1 = {f_beta(p_s, r_s):.3f}")
    assert (p_l, r_l, p_s) == (0.2, 0.2, 1.0)
    assert abs(f_beta(p_s, r_s) - f_beta_comptes(2, 0, 8)) < 1e-12    # 2TP / (2TP + FP + FN) = 4/12
    assert abs(f_beta(p_l, r_l) - f_beta_comptes(2, 8, 8)) < 1e-12    # 4/20
    muet = (precision(0, 0), rappel(0, 10), f_beta(precision(0, 0), rappel(0, 10)), f_beta_comptes(0, 0, 10))
    print(f"  agent muet  P = {muet[0]}  R = {muet[1]}  F1(taux) = {muet[2]}  F1(comptes) = {muet[3]}")
    assert muet == (None, 0.0, None, 0.0) and f_beta_comptes(0, 0, 0) is None

    print("2. F1 est une moyenne harmonique : min(P, R) ≤ F1 ≤ (P + R) / 2")
    for p, r in ((1.0, 0.0), (1.0, 0.2), (0.6, 0.6)):
        f1 = f_beta(p, r)
        print(f"  P = {p}  R = {r}  F1 = {f1:.3f}  moyenne arithmétique = {(p + r) / 2:.3f}")
        assert min(p, r) - 1e-12 <= f1 <= (p + r) / 2 + 1e-12
    assert f_beta(0.6, 0.6) == 0.6    # égalité si et seulement si P = R

    print("3. F-bêta : β² multiplie la précision au dénominateur")
    f1, f2 = f_beta(0.70, 0.99), f_beta(0.70, 0.99, beta=2)
    print(f"  P = 0.70  R = 0.99  F1 = {f1:.4f}  F2 = {f2:.4f}")
    assert (round(f1, 4), round(f2, 4)) == (0.8201, 0.9142)
    p, r = precision(8, 2), rappel(8, 4)
    assert abs(f_beta(p, r, 2) - f_beta_comptes(8, 2, 4, 2)) < 1e-12              # 40 / 58
    harmonique = 1 / ((1 / 5) * (1 / p) + (4 / 5) * (1 / r))                      # poids 1/5 et 4/5
    assert abs(harmonique - f_beta(p, r, 2)) < 1e-12
    seuils = {"A": (48, 80, 2), "B": (35, 15, 15)}                                 # (TP, FP, FN)
    for nom, (tp, fp, fn) in seuils.items():
        print(f"  seuil {nom}  P = {precision(tp, fp):.3f}  R = {rappel(tp, fn):.2f}"
              f"  F1 = {f_beta_comptes(tp, fp, fn):.3f}  F2 = {f_beta_comptes(tp, fp, fn, 2):.3f}")
    assert f_beta_comptes(*seuils["B"]) > f_beta_comptes(*seuils["A"])            # F1 choisit B
    assert f_beta_comptes(*seuils["A"], 2) > f_beta_comptes(*seuils["B"], 2)      # F2 choisit A

    print("4. KL = 0 si et seulement si Q = P ; elle n'est pas symétrique")
    P = [0.70, 0.20, 0.10]          # acceptable, limite, rejet
    proche = [0.65, 0.25, 0.10]
    faux = [0.01, 0.01, 0.98]       # sûr de lui, et faux
    kl_p, kl_f, kl_inv = divergence_kl(P, proche), divergence_kl(P, faux), divergence_kl(faux, P)
    print(f"  D(P || P) = {divergence_kl(P, P):.4f}   D(P || proche) = {kl_p:.4f}")
    print(f"  D(P || faux) = {kl_f:.4f}   D(faux || P) = {kl_inv:.4f}")
    assert divergence_kl(P, P) == 0.0
    assert (round(kl_p, 4), round(kl_f, 3), round(kl_inv, 3)) == (0.0072, 3.345, 2.164)

    print("5. Le terme qui explose : ln(P/Q) → +∞ quand Q → 0")
    terme = 0.9 * math.log(0.9 / 1e-6)
    print(f"  0.9 · ln(0.9 / 1e-6) = {terme:.2f}   ;   Q = 0 et P > 0 : D = {divergence_kl([0.9, 0.1], [0.0, 1.0])}")
    assert round(terme, 2) == 12.34 and divergence_kl([0.9, 0.1], [0.0, 1.0]) == math.inf

    print("6. Entropie croisée = entropie + KL")
    h, hc = entropie(P), entropie_croisee(P, faux)
    print(f"  H(P) = {h:.4f}   H(P, faux) = {hc:.4f}   H(P) + D(P || faux) = {h + kl_f:.4f}")
    assert abs(hc - (h + kl_f)) < 1e-12 and round(h, 4) == 0.8018

    print("7. Gibbs sur le support de P : gauche ≤ milieu ≤ 0")
    cas = (("proche", P, proche), ("hors support", [0.5, 0.5, 0.0], [0.4, 0.4, 0.2]),
           ("Q = 0", [0.9, 0.1], [0.0, 1.0]))
    for nom, A, B in cas:
        gauche, milieu = gibbs_par_jensen(A, B)
        print(f"  {nom:12s}  Σ P ln(Q/P) = {gauche:.4f}   ln(Σ_S Q) = {milieu:.4f}   D = {divergence_kl(A, B):.4f}")
        assert gauche <= milieu + 1e-12 and milieu <= 0.0
        d = divergence_kl(A, B)
        assert gauche == -math.inf if d == math.inf else abs(gauche + d) < 1e-12
    assert abs(divergence_kl([0.5, 0.5, 0.0], [0.4, 0.4, 0.2]) - math.log(1 / 0.8)) < 1e-12

    print("8. Le seuil 2.5 bloque ou laisse passer")
    for nom, Q in (("proche", proche), ("faux", faux)):
        score, bloque = garde_fou(P, Q, seuil=2.5)
        print(f"  {nom:7s} D = {score:.3f}  →  {'revue humaine' if bloque else 'laissé passer'}")
    assert garde_fou(P, proche, 2.5)[1] is False and garde_fou(P, faux, 2.5)[1] is True

    for mauvais in (lambda: precision(-1, 2), lambda: divergence_kl([0.5, 0.6], [0.5, 0.5])):
        try:
            mauvais()
        except ValueError:
            pass
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. RAG : le top-k déplace un compteur à la fois (10 documents utiles)
  large  P = 0.20  R = 0.20  F1 = 0.200
  serré  P = 1.00  R = 0.20  F1 = 0.333
  agent muet  P = None  R = 0.0  F1(taux) = None  F1(comptes) = 0.0
…
3. F-bêta : β² multiplie la précision au dénominateur
  P = 0.70  R = 0.99  F1 = 0.8201  F2 = 0.9142
  seuil A  P = 0.375  R = 0.96  F1 = 0.539  F2 = 0.732
  seuil B  P = 0.700  R = 0.70  F1 = 0.700  F2 = 0.700
4. KL = 0 si et seulement si Q = P ; elle n'est pas symétrique
  D(P || P) = 0.0000   D(P || proche) = 0.0072
  D(P || faux) = 3.3449   D(faux || P) = 2.1643
…
  H(P) = 0.8018   H(P, faux) = 4.1467   H(P) + D(P || faux) = 4.1467
7. Gibbs sur le support de P : gauche ≤ milieu ≤ 0
  hors support  Σ P ln(Q/P) = -0.2231   ln(Σ_S Q) = -0.2231   D = 0.2231
  Q = 0         Σ P ln(Q/P) = -inf   ln(Σ_S Q) = 0.0000   D = inf
  proche  D = 0.007  →  laissé passer
  faux    D = 3.345  →  revue humaine
OK — toutes les vérifications sont passées.
```

Deux réglages, deux formules. Pour un outil qui supprime un compte ou qui approuve un paiement, on pousse la précision. Pour un filtre de conformité ou un retrieval de clauses, on pousse le rappel avec un Fβ de β > 1. La KL ne remplace pas ces compteurs : elle mesure un autre échec, celui où l'agent est sûr d'une distribution qui n'est pas la bonne.

## Squelette algorithmique

Le fichier contient deux algorithmes. Le premier transforme une liste de décisions en trois taux ; le second compare deux distributions et décide s'il faut une revue humaine.

### Précision, rappel et Fβ à partir des décisions

Entrées : N décisions, chacune un couple (réel, prédit) de 0 et de 1, et un réglage β > 0. Sorties : Préc, Rap et Fβ, chacun pouvant être indéfini. L'idée : un seul passage pour remplir les cases de la matrice de confusion, puis trois divisions dont on teste le dénominateur. Le Fβ est calculé en comptes, parce que cette forme reste définie quand la précision ne l'est pas.

```text
ALGORITHME PrecisionRappelFBeta
ENTRÉES : décisions (réel, prédit) au nombre de N, β > 0
SORTIE : Préc, Rap, Fβ (chacun peut valoir INDÉFINI)
  TP ← 0 ; FP ← 0 ; FN ← 0
  POUR chaque décision (réel, prédit) FAIRE
    SI prédit = 1 ET réel = 1 ALORS
      TP ← TP + 1
    SINON SI prédit = 1 ET réel = 0 ALORS
      FP ← FP + 1
    SINON SI prédit = 0 ET réel = 1 ALORS
      FN ← FN + 1
    FIN SI
  FIN POUR
  SI TP + FP > 0 ALORS Préc ← TP / (TP + FP) SINON Préc ← INDÉFINI FIN SI
  SI TP + FN > 0 ALORS Rap ← TP / (TP + FN) SINON Rap ← INDÉFINI FIN SI
  dén ← (1 + β²)·TP + β²·FN + FP
  SI dén = 0 ALORS
    RETOURNER Préc, Rap, INDÉFINI                 (rien à trouver, rien signalé)
  FIN SI
  RETOURNER Préc, Rap, (1 + β²)·TP / dén
```

**Complexité :** O(N) en temps, parce que chaque décision est lue une fois et ne coûte qu'une comparaison et une addition ; les trois divisions finales coûtent O(1). La mémoire est en O(1) : trois compteurs, quelle que soit la taille du jeu, ce qui permet de calculer ces taux en flux sur des millions de décisions sans les garder.

**Du squelette au code :** la boucle de comptage n'est pas dans ce programme, qui reçoit directement `tp`, `fp` et `fn` ; elle est écrite à l'étape 51 dans `matrice_confusion`. La ligne de Préc est `precision(tp, fp)`, celle de Rap est `rappel(tp, fn)`, avec leur `return None` pour INDÉFINI. Les trois dernières lignes sont `f_beta_comptes(tp, fp, fn, beta)` : `den = (1 + b2) * tp + b2 * fn + fp`, le test `den == 0`, puis la division. `f_beta(p, r, beta)` est la variante qui part des taux au lieu des comptes.

### Divergence KL et décision du garde-fou

Entrées : deux distributions P et Q sur les mêmes m issues, dans le même ordre, et un seuil τ. Sorties : la divergence D, éventuellement infinie, et la décision « passer » ou « revue humaine ». L'idée : sommer P ln(P/Q) sur le support de P seulement, et s'arrêter dès qu'une issue possible pour P est impossible pour Q.

```text
ALGORITHME DivergenceKLEtGardeFou
ENTRÉES : P[1..m], Q[1..m], seuil τ
SORTIE : D ∈ [0, ∞], décision
  SI longueur(P) ≠ longueur(Q) ALORS
    SIGNALER UNE ERREUR « P et Q ne portent pas sur les mêmes issues »
  FIN SI
  SI une valeur de P ou de Q est < 0, OU |Σ P − 1| > 10⁻⁹, OU |Σ Q − 1| > 10⁻⁹ ALORS
    SIGNALER UNE ERREUR « ce ne sont pas des distributions »
  FIN SI
  D ← 0
  POUR x DE 1 À m FAIRE
    SI P[x] > 0 ALORS                                (sinon le terme 0 · ln(0/q) vaut 0)
      SI Q[x] = 0 ALORS
        RETOURNER ∞, « revue humaine »
      FIN SI
      D ← D + P[x] · ln(P[x] / Q[x])
    FIN SI
  FIN POUR
  SI D > τ ALORS
    RETOURNER D, « revue humaine »
  SINON
    RETOURNER D, « passer »
  FIN SI
```

**Complexité :** O(m) en temps, parce que les vérifications (deux sommes et un parcours des valeurs) et la boucle de calcul lisent chacune les m issues une fois, et que chaque terme coûte une division et un logarithme. La mémoire supplémentaire est en O(1) : un accumulateur. Le coût est négligeable devant l'appel au modèle qui a produit Q.

**Du squelette au code :** le test de longueur est la première ligne de `divergence_kl` ; le test de distribution est `verifier_distribution`, appelé sur P et sur Q. La boucle `POUR` est la boucle `for p, q in zip(P, Q)` : `if p == 0.0: continue` est le test « P[x] > 0 » écrit à l'envers, `if q == 0.0: return math.inf` est le retour infini, et `total += p * math.log(p / q)` est l'accumulation. La comparaison finale au seuil est `garde_fou(P, Q, seuil)`, qui renvoie `score, score > seuil`.

## Cas d'usage réels aux Émirats

Les compteurs et les seuils ci-dessous sont illustratifs : en production, on les mesure sur un jeu étiqueté propre à chaque métier, avec son intervalle de Wilson (étape 7).

### Banque — le F2 choisit le seuil des alertes anti-blanchiment

Une banque de détail de Dubaï fait trier les virements sortants par un agent qui ouvre une alerte pour l'équipe conformité quand un schéma ressemble à du blanchiment : virements fractionnés, bénéficiaire tout juste créé, pays à risque. Sur un mois de virements déjà instruits par les analystes, l'équipe compare deux seuils de score : le seuil A donne TP = 48, FP = 80, FN = 2 ; le seuil B donne TP = 35, FP = 15, FN = 15. Le F1 préfère B (0,700 contre 0,539), parce qu'il traite une fausse alerte et un oubli comme deux erreurs de même prix. Or un virement suspect non signalé expose la banque à une remarque de la CBUAE et à une déclaration de soupçon manquée, alors qu'une fausse alerte ne coûte qu'un temps d'analyste. L'équipe retient donc le F2, qui fait payer chaque oubli comme quatre fausses alertes : il préfère A (0,732 contre 0,700), avec un rappel de 0,96 au lieu de 0,70. Sans cette pondération, l'agent aurait été réglé pour le confort de l'équipe et non pour le risque réel. L'indicateur suivi en production est le rappel mesuré chaque mois sur un échantillon de virements revus à l'aveugle, avec la charge d'alertes par analyste comme garde-fou opérationnel.

### Immobilier — combien de clauses ramener d'un contrat de location

Une agence de Dubaï propose aux locataires un assistant qui répond à partir de leur contrat enregistré dans Ejari et des règles de location, indexés dans un RAG. Pour la question « puis-je partir avant la fin du bail, et avec quel préavis ? », dix clauses du jeu de test sont pertinentes. Avec un top-k de 10, le retriever ramène 2 bonnes clauses et 8 hors sujet : précision 0,20, rappel 0,20. En resserrant à un top-k de 2 et en gardant les deux bonnes, la précision monte à 1, mais le rappel reste à 0,20 : les huit clauses manquées le sont toujours, et le F1 n'atteint que 0,333. La leçon est que le top-k déplace un compteur, pas les deux : pour gagner du rappel, il faut un meilleur retriever (BM25, cosinus et fusion RRF, étapes 22 à 24), pas un k plus petit. Une clause de préavis manquée produit une réponse fausse sur un droit du locataire, ce qui est le pire résultat pour l'agence comme pour le client. L'équipe suit le rappel@k (étape 25) sur le jeu de test et la précision du contexte injecté (étape 57).

### Crypto — la KL surveille la dérive des décisions de retrait

Une plateforme d'actifs virtuels agréée par la VARA fait classer chaque demande de retrait en trois issues : acceptable, limite (revue manuelle), rejet. Sur le trimestre de référence, la répartition observée est P = (0,70 ; 0,20 ; 0,10). Chaque semaine, l'agent de surveillance calcule la répartition Q des décisions de la semaine et la divergence D_KL(P‖Q). Une semaine à (0,65 ; 0,25 ; 0,10) donne 0,0072 : rien à signaler. Une semaine où une mise à jour du prompt fait presque tout rejeter, (0,01 ; 0,01 ; 0,98), donne 3,345 et déclenche une alerte à l'équipe risque, au-dessus du seuil illustratif de 2,5. Le sens de la divergence est un choix documenté : D(P‖Q) punit surtout une issue fréquente qui disparaît, D(Q‖P) une issue rare qui envahit tout ; ici la seconde vaut 2,164, et l'équipe calcule les deux. Sans cette mesure, un rejet massif passerait pour de la prudence jusqu'aux premières plaintes de clients bloqués. On suit la KL hebdomadaire et le délai entre une mise à jour et la détection de la dérive.

### Assurance — approuver sans humain exige une précision très haute

Un assureur auto laisse l'agent approuver seul les petits sinistres, sous un montant fixé par sa politique interne, quand le dossier est complet et cohérent. Le « positif » est ici la décision « approuver sans humain » : un faux positif paie un sinistre frauduleux ou mal documenté, et cet argent ne revient presque jamais. Sur 400 dossiers de test déjà instruits, dont 300 légitimes, l'agent en approuve 120, dont 119 légitimes : précision 0,992 et rappel 119/300 = 0,397. Le F1, à 0,567, serait un mauvais guide : il pousserait à approuver davantage pour gagner du rappel, ce que l'assureur refuse. La bonne lecture est un Fβ avec β < 1 (F₀,₅ = 0,763 ici), ou mieux une contrainte, « précision au moins égale au seuil fixé », puis le rappel maximal sous cette contrainte. Un dossier légitime non approuvé automatiquement part simplement chez un gestionnaire : c'est un coût de délai, pas une perte. On suit la précision de l'approbation automatique et le montant des sinistres approuvés à tort, revus chaque mois par l'équipe fraude.

### RH — les pièces manquantes d'un dossier de permis de travail

Un cabinet RH présent dans plusieurs émirats fait vérifier par un agent la complétude des dossiers de permis de travail avant le dépôt auprès du MOHRE : passeport, photo, contrat, attestation de diplôme, visite médicale. Le positif est « une pièce manque ». Un faux négatif envoie un dossier incomplet, qui revient refusé et retarde de plusieurs jours l'arrivée du salarié ; un faux positif réclame au candidat une pièce qu'il a déjà fournie, ce qui agace mais ne coûte qu'un échange. Sur 200 dossiers de contrôle, l'équipe mesure TP = 38, FP = 12, FN = 2 : précision 0,76, rappel 0,95, F1 0,844 et F2 0,905. Elle règle l'agent sur le F2 et ajoute une règle dure : aucun dépôt tant qu'une pièce obligatoire est douteuse. Sans mesure par type de pièce, une moyenne globale « 95 % de dossiers corrects » cacherait que l'attestation de diplôme est la pièce la plus souvent oubliée. On suit le taux de dossiers retournés par l'administration, ventilé par type de pièce.

### Secteur public — un routeur de référence qui contredit l'agent

Une entité de services publics en ligne, accessible par UAE Pass, reçoit des demandes en arabe et en anglais et les route vers trois services : état civil, permis, réclamations. L'agent principal produit une distribution Q sur ces trois services ; un petit classifieur de référence, entraîné sur des demandes déjà routées par des agents humains, produit une distribution P. Quand l'agent place 0,98 sur « réclamations » alors que la référence place 0,70 sur « état civil », la divergence vaut 3,345, au-dessus du seuil de 2,5, et la demande est relue par un humain avant le routage : ce sont les nombres du programme. Ce garde-fou attrape le cas le plus dangereux, celui d'un agent très sûr de lui sur une mauvaise issue, que son propre score de confiance ne signalerait jamais. Sans lui, une demande urgente d'acte d'état civil pourrait attendre des jours dans la mauvaise file. On suit le taux de demandes relues, le taux de reroutage après relecture et, pour la PDPL, l'absence de données personnelles dans les journaux de comparaison.

## Pièges et limites

- **Confondre « non défini » et « zéro ».** Une précision sans aucune prédiction positive n'est pas 0 : on renvoie `None`, on l'exclut des moyennes, et on calcule le F1 en comptes, qui reste défini.
- **Publier un F1 seul.** Il cache lequel des deux taux est faible, et il dépend du seuil : un F1 sans sa précision, son rappel et son seuil ne se compare à rien.
- **Une KL infinie sur des fréquences.** Une issue jamais observée dans la semaine donne Q(x) = 0 et une divergence infinie. On lisse les comptes de façon explicite (ajouter 1 à chaque issue, lissage de Laplace) et on le documente, au lieu d'ajouter un epsilon caché dans la formule.
- **Prendre la KL pour une distance.** Elle n'est pas symétrique et ne vérifie pas l'inégalité triangulaire. Son seuil n'a pas de valeur universelle, et l'unité compte : en bits (log₂), elle vaut la valeur en nats divisée par ln 2.
- **Oublier les vrais négatifs.** Précision, rappel et F1 ignorent TN, ce qui est voulu sur un événement rare ; la spécificité et l'accuracy de l'étape 51 les regardent.

### Exercice feuille blanche

1. Sans regarder le code, écrire `f_beta_comptes` à partir de la formule, puis vérifier que pour TP = 3, FP = 1, FN = 2, le F1 vaut 6/9 ≈ 0,667, et que la forme en taux (Préc = 0,75, Rap = 0,60) donne le même nombre.
2. Prédire, puis vérifier : pour P = (0,5 ; 0,5) et Q = (0,9 ; 0,1), quelle divergence est la plus grande, D(P‖Q) ou D(Q‖P) ? (Réponse : D(P‖Q) = 0,511 et D(Q‖P) = 0,368.)
3. Trouver le bug : `return (1.0 + b2) * p * r / (p + b2 * r)`. Que renvoie cette variante pour P = 0,70, R = 0,99 et β = 2 ? (Réponse : 0,7436, qui est le F₀,₅ : elle favorise la précision au lieu du rappel.)

## Pour aller plus loin

- La divergence de Jensen-Shannon, moyenne des KL de P et Q vers leur mélange (P + Q)/2, est symétrique et bornée par ln 2 : on la préfère pour comparer deux périodes sans choisir de sens.
- La courbe précision-rappel, tracée en faisant varier le seuil, et l'aire sous cette courbe complètent l'AUC-ROC de l'étape 51 sur les événements rares.
- Dans l'entraînement par renforcement à partir de préférences humaines, une pénalité de KL entre le modèle entraîné et le modèle de départ l'empêche de s'éloigner trop vite de son comportement initial.
- Micro- et macro-moyenne des F1 sur plusieurs classes : étape 56.

> Suite : [Spécificité, VPN et AUC](<51-Specificite-NPV-AUC.md>) — étape 51.
