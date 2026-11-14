# Étape 41 — Orchestration — Score de priorité de tâche

> Étape 41 du parcours · Prérequis : [Orchestration : définitions fondamentales](<40b-Orchestration-Definitions-Fondamentaux.md>) · Suite : [Graphes orientés acycliques et matrices d'adjacence](<42-Orchestration-Graphes.md>)

**Dossier :** 08-Orchestration  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Platform Team, AI Agent Ops  
**Nom du fichier :** 41-Orchestration-Formule-Score-de-Priorite.md

## Définition

Dans une orchestration multi-agents ou un workflow, plusieurs tâches attendent en même temps et un nombre limité d'agents ou d'ouvriers peut les traiter. Le score de priorité résume chaque tâche en un nombre, pour décider laquelle part en premier : il augmente avec l'urgence et l'impact métier, et il baisse avec le coût. Pour que les trois signaux soient comparables, chacun est ramené dans [0, 1] ; en particulier, le coût est divisé par un plafond fixé à l'avance, sinon un coût exprimé en tokens écrase tout le reste. Le score ne sait rien des dépendances entre tâches : il classe seulement les tâches **prêtes**, celles dont tous les prérequis sont finis. Enfin, un score figé peut faire attendre indéfiniment une tâche peu prioritaire ; on lui ajoute donc un terme de **vieillissement**, qui fait monter l'urgence avec le temps d'attente.

## Rôle dans un agent

Le score sert dans l'**ordonnanceur** de l'orchestrateur, au moment de **décider** quel travail lancer, à chaque fois qu'un ouvrier se libère ou qu'une tâche arrive. Le routeur de l'étape 40 bis décide *qui* traite une demande ; le score de priorité décide *quand*. Il ne remplace ni le graphe des dépendances (étapes 42 à 45), ni les garde-fous : une tâche bloquée par une approbation humaine n'est pas prête, quel que soit son score. Dans le code, c'est une fonction pure, testable sans modèle, que l'ordonnanceur appelle pour construire la clé de son tas.

## Équation complète

Score de priorité, coût normalisé :

$$
P = w_1\, u + w_2\, i - w_3\, \hat{c} , \qquad \hat{c} = \frac{c}{c_{\max}}
$$

Hypothèses :

$$
u,\; i,\; \hat{c} \in [0, 1] , \qquad w_1,\; w_2,\; w_3 \ge 0
$$

Bornes qui en découlent :

$$
-w_3 \le P \le w_1 + w_2
$$

Vieillissement linéaire, pour une tâche arrivée au temps tₐ et regardée au temps t :

$$
P(t) = w_1 \big( u + a\,(t - t_a) \big) + w_2\, i - w_3\, \hat{c}
$$

Clé fixe équivalente pour le tas, à l'instant t :

$$
P(t) = \underbrace{P_0 - w_1 a\, t_a}_{\text{clé de la tâche}} + \underbrace{w_1 a\, t}_{\text{commun à toutes}}
$$

## Décryptage des symboles

$$
u
$$

**Sens :** urgence de la tâche : à quel point elle doit être faite vite · **Type / plage :** réel dans [0, 1] · **Variable Python :** `urgence`

$$
i
$$

**Sens :** impact métier du résultat · **Type / plage :** réel dans [0, 1] · **Variable Python :** `impact`

$$
c,\; c_{\max}
$$

**Sens :** coût estimé de la tâche (tokens, secondes, appels d'outils) et plafond de coût par tâche, fixé par la politique de la plateforme · **Type / plage :** réels, 0 ≤ c ≤ cₘₐₓ, cₘₐₓ > 0 · **Variable Python :** `cout`, `cout_max` (constante `COUT_MAX = 8000`)

$$
\hat{c}
$$

**Sens :** coût normalisé, sans unité · **Type / plage :** réel dans [0, 1] · **Variable Python :** `cout / cout_max`

$$
w_1,\; w_2,\; w_3
$$

**Sens :** poids de l'urgence, de l'impact et du coût ; ils disent quel signal commande · **Type / plage :** réels ≥ 0, souvent de somme 1 · **Variable Python :** `w`, par défaut `W = (0.5, 0.3, 0.2)`

$$
P
$$

**Sens :** score de priorité ; la plus grande valeur passe en premier · **Type / plage :** réel dans [−w₃, w₁ + w₂] sans vieillissement · **Variable Python :** valeur renvoyée par `priorite(...)`

$$
a,\; t_a,\; t
$$

**Sens :** taux de vieillissement (urgence gagnée par top d'horloge), instant d'arrivée de la tâche, instant présent · **Type / plage :** a ≥ 0 ; tₐ et t sont des tops d'une horloge simulée · **Variable Python :** `a`, `Tache.arrivee`, `top`

## Démonstration

### 1. Pourquoi normaliser le coût : le contre-exemple de l'ancienne formule

L'ancienne version écrivait P = w₁ u + w₂ i − w₃ c avec un coût brut. Pour une tâche parfaitement urgente et importante (u = i = 1) de 5 000 tokens, avec les poids par défaut :

$$
0{,}5 \times 1 + 0{,}3 \times 1 - 0{,}2 \times 5000 = 0{,}8 - 1000 = -999{,}2
$$

Le coût, exprimé en milliers, écrase les deux autres signaux, qui sont au plus 1 : le classement devient « la moins chère d'abord ». Une reformulation de 50 tokens sans enjeu (u = i = 0,1) obtient −9,92, devant une alerte critique. En divisant par cₘₐₓ = 8 000, le même calcul donne :

$$
0{,}5 + 0{,}3 - 0{,}2 \times \frac{5000}{8000} = 0{,}8 - 0{,}125 = 0{,}675
$$

Le plafond cₘₐₓ est une règle de la plateforme (« aucune tâche ne dépasse 8 000 tokens sans être découpée »). Une tâche au-delà est refusée par une `ValueError` plutôt que tronquée en silence.

### 2. Bornes : P est dans [−w₃, w₁ + w₂]

Parce que u ∈ [0, 1] et w₁ ≥ 0, le terme w₁ u est dans [0, w₁]. De même, w₂ i est dans [0, w₂], et −w₃ ĉ est dans [−w₃, 0]. En additionnant les bornes inférieures, puis les bornes supérieures :

$$
0 + 0 - w_3 \;\le\; w_1 u + w_2 i - w_3 \hat{c} \;\le\; w_1 + w_2 - 0
$$

Les deux bornes sont atteintes : −w₃ pour (u, i, ĉ) = (0, 0, 1), une tâche sans urgence, sans impact et au plafond de coût ; w₁ + w₂ pour (1, 1, 0). Avec les poids par défaut, l'intervalle est [−0,2 ; 0,8]. Il a pour longueur w₁ + w₂ + w₃, soit 1 quand les poids somment à 1. Le programme le vérifie sur une grille de 125 combinaisons. Avec le vieillissement, la borne haute ne tient plus, puisque P(t) croît sans limite : c'est voulu (point 6).

### 3. Multiplier tous les poids par un même nombre positif ne change pas le classement

Pour λ > 0, le score calculé avec les poids λw₁, λw₂, λw₃ vaut :

$$
P_{\lambda w} = \lambda w_1 u + \lambda w_2 i - \lambda w_3 \hat{c} = \lambda \, P_w
$$

Pour deux tâches A et B, on a donc P_λw(A) − P_λw(B) = λ (P_w(A) − P_w(B)), qui a le même signe que P_w(A) − P_w(B) parce que λ > 0. L'ordre est le même, et les égalités restent des égalités, donc le départage aussi. Conséquence pratique : des poids (5, 3, 2) écrits en « points » par une équipe métier et des poids (0,5 ; 0,3 ; 0,2) écrits par l'équipe plateforme donnent le même ordre ; on peut toujours normaliser les poids à une somme de 1 sans rien perdre. En revanche, changer **un seul** poids change en général l'ordre : avec (0,5 ; 0,3 ; 2), le coût domine et le classement du programme change.

### 4. Le plafond cₘₐₓ doit être fixe, pas recalculé sur le lot

Diviser par cₘₐₓ revient à remplacer w₃ par w₃ / cₘₐₓ dans un score en coût brut. Changer cₘₐₓ, c'est donc changer **un seul** poids, ce que le point 3 n'autorise pas. Si l'on prend pour cₘₐₓ le plus gros coût du lot en attente, le départ d'une tâche sans rapport peut inverser deux autres tâches. Avec A = (0,6 ; 0,5 ; 3 000 tokens) et B = (0,4 ; 0,5 ; 1 000 tokens) :

- tant qu'une tâche de 5 000 tokens attend, cₘₐₓ = 5 000 : P(A) = 0,30 + 0,15 − 0,2 × 0,6 = 0,33 et P(B) = 0,20 + 0,15 − 0,2 × 0,2 = 0,31, donc A passe d'abord ;
- dès qu'elle part, cₘₐₓ = 3 000 : P(A) = 0,45 − 0,2 = 0,25 et P(B) = 0,35 − 0,0667 = 0,2833, donc B passe d'abord.

Un classement qui dépend de tâches qui n'ont rien à voir est impossible à expliquer en audit. Le code fixe donc `COUT_MAX = 8000`.

### 5. Le score ne voit pas les dépendances : un tas sur les seules tâches prêtes

Trier toutes les tâches par score peut lancer une tâche avant son prérequis. Dans l'exemple du programme, `offre_pret` (P = 0,60) dépend de `kyc_client` (P = 0,565) : le tri seul la place avant. L'ordonnanceur ne met dans le tas que les tâches dont tous les prérequis sont finis, et y ajoute une tâche au moment où son dernier prérequis se termine. C'est l'algorithme de Kahn de l'étape 44, avec un tas à la place d'une file : chaque tâche entre une fois dans le tas et en sort une fois, en O(log n) chaque fois, et chaque dépendance est lue une fois, en O(1), d'où un coût total O(n log n + m) pour n tâches et m dépendances. Si des tâches ne deviennent jamais prêtes, c'est qu'il y a un cycle de dépendances (étapes 42 et 45) : le code lève une `ValueError` au lieu de les oublier.

### 6. Le vieillissement empêche la famine

Sans vieillissement, une tâche de score faible peut attendre pour toujours si des tâches de meilleur score arrivent sans arrêt : c'est la **famine**. Avec un vieillissement linéaire non plafonné, on montre qu'elle ne peut être doublée que par un nombre fini de tâches.

Soit X une tâche arrivée au temps t_X et Y une tâche arrivée plus tard, au temps t_Y > t_X. À l'instant t, le score de X vaut au moins −w₃ + w₁ a (t − t_X), parce que les autres termes sont au moins −w₃ (point 2). Le score de Y vaut au plus w₁ + w₂ + w₁ a (t − t_Y). Y ne peut passer avant X que si :

$$
w_1 + w_2 + w_1 a (t - t_Y) \ge -w_3 + w_1 a (t - t_X) \;\Longleftrightarrow\; t_Y - t_X \le \frac{w_1 + w_2 + w_3}{w_1\, a}
$$

Les termes en t s'annulent, d'où la condition, qui ne dépend plus de l'instant t. Une tâche arrivée plus de D = (w₁ + w₂ + w₃) / (w₁ a) tops après X ne peut donc jamais la doubler. Si le nombre d'arrivées par top est borné et que l'on sert au moins une tâche par top, seul un nombre fini de tâches peut passer avant X, et X finit par être servie. Avec w = (0,5 ; 0,3 ; 0,2) et a = 0,08, D = 1 / 0,04 = 25 tops.

Le plafond tue cette garantie. Si l'on écrit min(1, u + a(t − tₐ)), une tâche vieillie d'impact nul et au plafond de coût plafonne à w₁ − w₃ = 0,3, alors qu'une nouvelle tâche peut valoir jusqu'à 0,8 : un flux continu de tâches parfaites l'affame. Le vieillissement doit donc rester non plafonné, ou basculer en premier arrivé, premier servi au-delà d'une attente maximale.

### 7. Avec un vieillissement uniforme, la clé du tas ne bouge pas

Le score à l'instant t s'écrit P(t) = P₀ − w₁ a tₐ + w₁ a t. Le dernier terme est le même pour toutes les tâches à l'instant t : il ne change pas leur ordre. On peut donc ranger chaque tâche dans le tas avec la clé fixe P₀ − w₁ a tₐ, calculée une fois à son arrivée, sans jamais réorganiser le tas. Le programme vérifie sur 20 tâches que cette clé donne le même ordre que le score recalculé à l'instant t = 30.

### 8. Départage déterministe

Deux tâches de même score doivent sortir toujours dans le même ordre, sinon deux exécutions du même lot divergent et l'audit ne peut pas rejouer une décision. La règle est : score décroissant, puis arrivée la plus ancienne (équité), puis nom (unicité). Le score est arrondi à 10⁻⁹ dans la clé, pour que deux calculs qui ne diffèrent que par une erreur d'arrondi de flottant soient traités comme une égalité.

### 9. Exemple fait à la main (le code reprend ces nombres)

Cinq tâches d'un back-office bancaire, poids (0,5 ; 0,3 ; 0,2), cₘₐₓ = 8 000 tokens :

| Tâche | u | i | c (tokens) | Calcul | P |
|---|---|---|---|---|---|
| alerte_aml | 0,9 | 0,9 | 2 000 | 0,45 + 0,27 − 0,2 × 0,25 | 0,67 |
| kyc_client | 0,7 | 0,8 | 1 000 | 0,35 + 0,24 − 0,2 × 0,125 | 0,565 |
| offre_pret (après kyc_client) | 0,8 | 1,0 | 4 000 | 0,40 + 0,30 − 0,2 × 0,5 | 0,60 |
| rapport_mensuel | 0,2 | 0,4 | 6 000 | 0,10 + 0,12 − 0,2 × 0,75 | 0,07 |
| resume_reunion | 0,3 | 0,2 | 800 | 0,15 + 0,06 − 0,2 × 0,1 | 0,19 |

Au départ, le tas contient les quatre tâches prêtes ; `offre_pret` attend. On sort `alerte_aml` (0,67), puis `kyc_client` (0,565) ; sa fin rend `offre_pret` prête, qui entre dans le tas et sort aussitôt (0,60). Viennent ensuite `resume_reunion` (0,19) et `rapport_mensuel` (0,07).

Famine : une tâche d'archivage (u = 0,1, i = 0,2, c = 4 000) vaut 0,05 + 0,06 − 0,1 = 0,01. À chaque top arrive une tâche de routine (u = 0,5, i = 0,5, c = 1 600) qui vaut 0,25 + 0,15 − 0,04 = 0,36, et l'on exécute une tâche par top. Sans vieillissement, la routine gagne toujours. Avec a = 0,08, l'archivage vaut 0,01 + 0,5 × 0,08 × t au top t : il dépasse 0,36 quand 0,04 t > 0,35, soit au top 9, où il vaut 0,37.

## Effets et comportement

- **w₁ grand : l'urgence commande.** Les alertes passent devant tout, y compris devant des tâches à fort impact mais sans échéance.
- **w₃ grand : la plateforme devient économe.** Les tâches chères reculent ; au-delà d'un certain point, elles ne passent plus qu'aux heures creuses.
- **Seuls les rapports entre poids comptent** (point 3). Doubler tous les poids ne change rien ; doubler un seul poids change l'ordre.
- **Le vieillissement transforme un ordre de priorité en garantie de service.** Plus a est grand, plus la fenêtre D est courte et plus l'ordonnanceur ressemble à « premier arrivé, premier servi » ; avec a = 0, c'est un tri pur par score, exposé à la famine.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| u, i, c | `urgence`, `impact`, `cout` (champs de `Tache`) |
| cₘₐₓ | `COUT_MAX = 8000`, paramètre `cout_max` |
| w₁, w₂, w₃ | `W = (0.5, 0.3, 0.2)`, paramètre `w` |
| P | `priorite(urgence, impact, cout)` |
| a, tₐ | paramètre `a`, champ `arrivee` |
| clé fixe P₀ − w₁ a tₐ et départage | `cle(t, a)` |
| tas des tâches prêtes | `ordonnancer(taches, a)` |

Copiez le bloc dans `priorite_taches.py` et lancez `python priorite_taches.py`.

### Déroulé, ligne par ligne

**`priorite(urgence, impact, cout, cout_max, w)`**. C'est P = w₁ u + w₂ i − w₃ c / cₘₐₓ.

- Trois gardes lèvent `ValueError` : un poids négatif (le sens d'un signal s'inverserait), une urgence ou un impact hors de [0, 1], un coût négatif ou au-delà du plafond.
- `return w1 * urgence + w2 * impact - w3 * (cout / cout_max)`. Pour `alerte_aml` : `0.5 * 0.9 + 0.3 * 0.9 - 0.2 * (2000 / 8000)` donne 0,45 + 0,27 − 0,05 = 0,67.

**`priorite_brute`** garde l'ancienne formule pour montrer son défaut : `priorite_brute(1.0, 1.0, 5000)` vaut −999,2.

**`Tache`** est une `dataclass` : nom, urgence, impact, coût, liste des prérequis et top d'arrivée sur l'horloge simulée.

**`cle(t, a)`** renvoie le triplet que le tas compare.

- `p0 = priorite(...)` : le score sans vieillissement.
- `-round(p0 - w[0] * a * t.arrivee, 9)` : la clé fixe du point 7, avec un signe moins parce que `heapq` sort le plus **petit** élément et que l'on veut le plus grand score. L'arrondi à 9 décimales applique le point 8.
- `t.arrivee`, puis `t.nom` : le départage.

**`ordonnancer(taches, a)`**, l'ordonnanceur à tas.

- `restants[nom]` compte les prérequis pas encore finis ; `suivants[p]` liste les tâches qui attendent `p`.
- `tas = [cle(t, a) for t in taches if restants[t.nom] == 0]`, puis `heapq.heapify(tas)` : seules les tâches prêtes entrent.
- À chaque tour, `heapq.heappop(tas)` sort la meilleure tâche. Pour chacun de ses suivants, `restants[s] -= 1` ; quand le compteur tombe à 0, le dernier prérequis vient de finir et la tâche entre dans le tas.
- `if len(ordre) != len(taches)` : des tâches ne sont jamais devenues prêtes, il y a un cycle, d'où une `ValueError`.

**`famine(a, tops)`** simule le point 6 : une tâche d'archivage à 0,01 attend, une tâche de routine à 0,36 arrive à chaque top, et l'on exécute à chaque top la tâche de plus petite clé. La fonction renvoie le top où l'archivage passe, ou `None` s'il ne passe jamais.

**`main()`**, bloc par bloc.

1. Coût brut contre coût normalisé : −999,2 contre 0,675.
2. Bornes : sur 125 combinaisons de la grille {0 ; 0,25 ; 0,5 ; 0,75 ; 1}³, le minimum vaut exactement −0,2 et le maximum 0,8.
3. Invariance d'échelle : les poids (0,5 ; 0,3 ; 0,2) et (5, 3, 2) donnent le classement `[0, 1, 3, 2]` ; les poids (0,5 ; 0,3 ; 2) en donnent un autre.
4. Plafond recalculé : A passe avant B avec cₘₐₓ = 5 000, après B avec cₘₐₓ = 3 000.
5. Tas sur les tâches prêtes : le tri seul met `offre_pret` avant `kyc_client`, l'ordonnanceur non. Un cycle x ↔ y lève une `ValueError`.
6. Trois factures de même score : `c_facture`, arrivée au top 1, passe d'abord, puis `a_facture` et `b_facture`, arrivées au top 3, par ordre de nom.
7. Famine : jamais servie sans vieillissement, servie au top 9 avec a = 0,08, sous la fenêtre D = 25. Le dernier `assert` vérifie le point 7 sur 20 tâches.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`priorite(urgence, impact, cout, cout_max, w)`** — Cette fonction est le régulateur d'un central d'appels qui attribue à chaque dossier une note unique avant de le placer dans la file : elle reçoit l'urgence et l'impact, tous deux entre 0 et 1, le coût en tokens, le plafond de coût, 8 000 par défaut, et les trois poids, (0,5 ; 0,3 ; 0,2) par défaut. Elle lève une `ValueError` pour un poids négatif, une urgence ou un impact hors de [0, 1], ou un coût négatif ou supérieur au plafond, puis renvoie w₁ u + w₂ i − w₃ c / cₘₐₓ : 0,67 pour l'alerte de lutte anti-blanchiment, 0,675 pour une tâche parfaite à 5 000 tokens, et toujours une valeur comprise entre −0,2 et 0,8.

**`priorite_brute(urgence, impact, cout, w)`** — Voici l'ancien régulateur, conservé comme pièce à conviction : la fonction reçoit l'urgence, l'impact, le coût en tokens bruts et les poids, et renvoie w₁ u + w₂ i − w₃ c sans diviser le coût par aucun plafond ni vérifier aucune entrée. Comme le coût se compte en milliers alors que les deux autres signaux tiennent entre 0 et 1, il écrase tout le reste : `priorite_brute(1.0, 1.0, 5000)` vaut −999,2, contre 0,675 pour la formule normalisée, et c'est exactement le défaut que `main` affiche au bloc 1.

**`cle(t, a, w)`** — Cette fonction fabrique le ticket que l'on remet à chaque tâche à l'entrée de la salle d'attente, et que le tas comparera ensuite : elle reçoit une tâche, le taux de vieillissement a et les poids, calcule le score P₀ de la tâche avec `priorite`, retranche w₁ × a × arrivée, arrondit à 9 décimales et prend l'opposé, parce que `heapq` sort le plus petit élément alors qu'on veut le plus grand score. Elle renvoie le triplet formé de cette valeur, du top d'arrivée et du nom, si bien que deux tâches de même score passent par ordre d'arrivée, puis par ordre alphabétique ; cette clé reste fixe dans le temps, car le terme de vieillissement commun à toutes les tâches ne change pas leur classement.

**`ordonnancer(taches, a)`** — C'est l'aiguilleur qui ne laisse partir un train que lorsque tous ceux dont il dépend sont arrivés : la fonction reçoit la liste des tâches et le taux de vieillissement, nul par défaut, compte pour chaque tâche ses prérequis non finis, note pour chaque tâche celles qui l'attendent, puis met dans un tas les seules tâches prêtes. À chaque tour, elle sort la meilleure, l'ajoute à l'ordre, décrémente le compteur de ses suivantes et pousse dans le tas celles dont le compteur tombe à 0 ; elle renvoie l'ordre d'exécution, ici l'alerte, puis le KYC avant l'offre de prêt, et lève une `ValueError` si des tâches ne deviennent jamais prêtes, signe d'un cycle comme x ↔ y.

**`main()`** — Le chef d'orchestre déroule les sept tableaux du chapitre : il oppose le coût brut, −999,2, au coût normalisé, 0,675, vérifie sur 125 combinaisons que le score reste entre −0,2 et 0,8, montre que multiplier tous les poids par 10 ne change pas le classement `[0, 1, 3, 2]` alors que changer un seul poids le change, et qu'un plafond recalculé sur le lot inverse deux tâches. Il fait ensuite ordonnancer un petit graphe de cinq tâches, refuse un cycle, départage trois factures de même score, constate la famine sans vieillissement et le service au top 9 avec a = 0,08, puis vérifie sur 20 tâches que la clé fixe donne le même ordre que le score recalculé ; il ne renvoie rien et n'imprime le message final que si tout concorde.

```python
"""Étape 41 — score de priorité : coût normalisé, bornes, invariance d'échelle, tas de tâches prêtes, vieillissement."""
import heapq
import itertools
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

W = (0.5, 0.3, 0.2)        # w1 (urgence), w2 (impact), w3 (coût)
COUT_MAX = 8000            # plafond de tokens par tâche, FIXÉ par la politique (pas le max du lot courant)


def priorite(urgence: float, impact: float, cout: float, cout_max: float = COUT_MAX,
             w: tuple[float, float, float] = W) -> float:
    """P = w1·u + w2·i − w3·(c / c_max), avec u, i, c/c_max dans [0, 1] et des poids >= 0."""
    w1, w2, w3 = w
    if min(w) < 0:
        raise ValueError("poids négatif : le sens des signaux s'inverserait")
    if not (0 <= urgence <= 1 and 0 <= impact <= 1):
        raise ValueError("urgence et impact doivent être dans [0, 1]")
    if cout_max <= 0 or not 0 <= cout <= cout_max:
        raise ValueError("il faut 0 <= coût <= coût_max : découper la tâche ou relever le plafond")
    return w1 * urgence + w2 * impact - w3 * (cout / cout_max)


def priorite_brute(urgence: float, impact: float, cout: float, w=W) -> float:
    """L'ancienne formule, coût en tokens bruts : à ne pas utiliser."""
    w1, w2, w3 = w
    return w1 * urgence + w2 * impact - w3 * cout


@dataclass
class Tache:
    nom: str
    urgence: float
    impact: float
    cout: int
    prerequis: list[str] = field(default_factory=list)
    arrivee: int = 0       # top d'horloge simulée


def cle(t: Tache, a: float, w=W) -> tuple:
    """Clé du tas. Vieillissement linéaire : P(t) = P0 + w1·a·(t − arrivée).
    Le terme w1·a·t est commun à toutes les tâches à l'instant t : le classement ne dépend que de
    P0 − w1·a·arrivée, une clé FIXE. Départage : arrivée la plus ancienne, puis nom."""
    p0 = priorite(t.urgence, t.impact, t.cout, w=w)
    return (-round(p0 - w[0] * a * t.arrivee, 9), t.arrivee, t.nom)


def ordonnancer(taches: list[Tache], a: float = 0.0) -> list[str]:
    """Une tâche par top. Seules les tâches PRÊTES (tous les prérequis finis) entrent dans le tas."""
    par_nom = {t.nom: t for t in taches}
    restants = {t.nom: len(t.prerequis) for t in taches}
    suivants = {t.nom: [] for t in taches}
    for t in taches:
        for p in t.prerequis:
            suivants[p].append(t.nom)
    tas = [cle(t, a) for t in taches if restants[t.nom] == 0]
    heapq.heapify(tas)
    ordre = []
    while tas:
        _, _, nom = heapq.heappop(tas)
        ordre.append(nom)
        for s in suivants[nom]:
            restants[s] -= 1
            if restants[s] == 0:                       # le dernier prérequis vient de finir
                heapq.heappush(tas, cle(par_nom[s], a))
    if len(ordre) != len(taches):
        raise ValueError("dépendances circulaires : certaines tâches ne deviennent jamais prêtes")
    return ordre


def famine(a: float, tops: int = 40) -> int | None:
    """Une tâche faible attend ; à chaque top arrive une tâche de routine, et l'on exécute une tâche.
    Renvoie le top où la tâche faible passe enfin, ou None si elle n'est jamais servie."""
    faible = Tache("archivage", 0.1, 0.2, 4000, arrivee=0)          # P0 = 0.05 + 0.06 − 0.10 = 0.01
    file = [faible]
    for top in range(tops):
        file.append(Tache(f"routine_{top}", 0.5, 0.5, 1600, arrivee=top))   # P0 = 0.25 + 0.15 − 0.04 = 0.36
        choisie = min(file, key=lambda t: cle(t, a))
        file.remove(choisie)
        if choisie is faible:
            return top
    return None


def main() -> None:
    print("1. Coût brut contre coût normalisé (u = i = 1, 5 000 tokens)")
    brute = priorite_brute(1.0, 1.0, 5000)
    norm = priorite(1.0, 1.0, 5000)
    print(f"  brut : 0.5 + 0.3 − 0.2 × 5000 = {brute:.1f}   normalisé : 0.5 + 0.3 − 0.2 × 5000/8000 = {norm:.3f}")
    assert round(brute, 1) == -999.2 and round(norm, 3) == 0.675

    print("2. Bornes : P est dans [−w3, w1 + w2] = [−0.2, 0.8]")
    grille = [0.0, 0.25, 0.5, 0.75, 1.0]
    scores = [priorite(u, i, c * COUT_MAX) for u, i, c in itertools.product(grille, repeat=3)]
    print(f"  {len(scores)} combinaisons : min = {min(scores):.2f}, max = {max(scores):.2f}")
    assert abs(min(scores) + 0.2) < 1e-12 and abs(max(scores) - 0.8) < 1e-12

    print("3. Multiplier tous les poids par 10 ne change pas le classement")
    lot = [(0.9, 0.9, 2000), (0.7, 0.8, 1000), (0.2, 0.4, 6000), (0.3, 0.2, 800)]
    rang = lambda w: sorted(range(len(lot)), key=lambda k: -priorite(*lot[k], w=w))
    print(f"  poids (0.5, 0.3, 0.2) : {rang(W)}   poids (5, 3, 2) : {rang((5.0, 3.0, 2.0))}")
    assert rang(W) == rang((5.0, 3.0, 2.0)) == [0, 1, 3, 2]
    assert rang((0.5, 0.3, 2.0)) != rang(W)                         # changer UN seul poids, si

    print("4. c_max recalculé sur le lot courant : A et B s'inversent quand une autre tâche part")
    a_, b_ = (0.6, 0.5, 3000), (0.4, 0.5, 1000)
    for cmax in (5000, 3000):
        pa, pb = priorite(*a_, cout_max=cmax), priorite(*b_, cout_max=cmax)
        print(f"  c_max = {cmax} : P(A) = {pa:.4f}  P(B) = {pb:.4f}  → {'A' if pa > pb else 'B'} d'abord")
    assert priorite(*a_, cout_max=5000) > priorite(*b_, cout_max=5000)
    assert priorite(*a_, cout_max=3000) < priorite(*b_, cout_max=3000)

    print("5. Tas sur les seules tâches prêtes d'un DAG")
    taches = [
        Tache("alerte_aml", 0.9, 0.9, 2000),
        Tache("kyc_client", 0.7, 0.8, 1000),
        Tache("offre_pret", 0.8, 1.0, 4000, prerequis=["kyc_client"]),
        Tache("rapport_mensuel", 0.2, 0.4, 6000),
        Tache("resume_reunion", 0.3, 0.2, 800),
    ]
    for t in taches:
        print(f"  {t.nom:16s} P = {priorite(t.urgence, t.impact, t.cout):.4f}   prérequis = {t.prerequis}")
    ordre = ordonnancer(taches)
    naif = [t.nom for t in sorted(taches, key=lambda t: cle(t, 0.0))]
    print(f"  tri par score seul : {naif}")
    print(f"  ordonnanceur       : {ordre}")
    assert naif.index("offre_pret") < naif.index("kyc_client")      # le tri seul viole la dépendance
    assert ordre == ["alerte_aml", "kyc_client", "offre_pret", "resume_reunion", "rapport_mensuel"]
    try:
        ordonnancer([Tache("x", 0.5, 0.5, 100, ["y"]), Tache("y", 0.5, 0.5, 100, ["x"])])
    except ValueError as e:
        print(f"  cycle x ↔ y : ValueError ({e})")
    else:
        raise AssertionError("un cycle aurait dû être refusé")

    print("6. Départage déterministe : même score → la plus ancienne, puis le nom")
    jumeaux = [Tache("b_facture", 0.5, 0.5, 800, arrivee=3), Tache("a_facture", 0.5, 0.5, 800, arrivee=3),
               Tache("c_facture", 0.5, 0.5, 800, arrivee=1)]
    print(f"  {ordonnancer(jumeaux, a=0.0)}")
    assert ordonnancer(jumeaux, a=0.0) == ["c_facture", "a_facture", "b_facture"]

    print("7. Vieillissement : sans lui, la tâche faible attend pour toujours")
    sans, avec = famine(a=0.0), famine(a=0.08)
    fenetre = sum(W) / (W[0] * 0.08)
    print(f"  a = 0    : {'jamais servie en 40 tops' if sans is None else sans}")
    print(f"  a = 0.08 : servie au top {avec} (0.01 + 0.5 × 0.08 × 9 = 0.37 > 0.36)")
    print(f"  aucune tâche arrivée plus de (w1 + w2 + w3) / (w1·a) = {fenetre:.0f} tops après elle ne peut la doubler")
    assert sans is None and avec == 9 and avec <= fenetre

    # La clé fixe P0 − w1·a·arrivée donne le même ordre que le score recalculé à chaque instant.
    t_now = 30
    file = [Tache(f"t{k}", (k * 37 % 10) / 10, (k * 53 % 10) / 10, (k * 71 % 8) * 1000, arrivee=k) for k in range(20)]
    recalcule = sorted(file, key=lambda t: (-round(priorite(t.urgence, t.impact, t.cout) + W[0] * 0.08 * (t_now - t.arrivee), 9),
                                           t.arrivee, t.nom))
    assert [t.nom for t in recalcule] == [t.nom for t in sorted(file, key=lambda t: cle(t, 0.08))]
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Coût brut contre coût normalisé (u = i = 1, 5 000 tokens)
  brut : 0.5 + 0.3 − 0.2 × 5000 = -999.2   normalisé : 0.5 + 0.3 − 0.2 × 5000/8000 = 0.675
2. Bornes : P est dans [−w3, w1 + w2] = [−0.2, 0.8]
  125 combinaisons : min = -0.20, max = 0.80
…
  c_max = 5000 : P(A) = 0.3300  P(B) = 0.3100  → A d'abord
  c_max = 3000 : P(A) = 0.2500  P(B) = 0.2833  → B d'abord
…
  tri par score seul : ['alerte_aml', 'offre_pret', 'kyc_client', 'resume_reunion', 'rapport_mensuel']
  ordonnanceur       : ['alerte_aml', 'kyc_client', 'offre_pret', 'resume_reunion', 'rapport_mensuel']
…
  ['c_facture', 'a_facture', 'b_facture']
7. Vieillissement : sans lui, la tâche faible attend pour toujours
  a = 0    : jamais servie en 40 tops
  a = 0.08 : servie au top 9 (0.01 + 0.5 × 0.08 × 9 = 0.37 > 0.36)
  aucune tâche arrivée plus de (w1 + w2 + w3) / (w1·a) = 25 tops après elle ne peut la doubler
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un score de priorité utile a des entrées sur la même échelle, un plafond de coût fixe, un départage écrit, un terme de vieillissement, et il ne classe que des tâches prêtes.

## Squelette algorithmique

Deux algorithmes travaillent ensemble. Le **calcul de la clé** prend une tâche (urgence, impact, coût, instant d'arrivée, nom), le plafond de coût, les poids et le taux de vieillissement ; il renvoie le triplet que le tas compare. L'idée est de vérifier les entrées, de calculer le score P₀ sur des signaux ramenés dans [0, 1], puis de retrancher w₁ a tₐ pour obtenir une clé fixe qui intègre le vieillissement (point 7). L'**ordonnancement des tâches prêtes** prend la liste des tâches avec leurs prérequis et renvoie un ordre d'exécution. L'idée est celle de Kahn (étape 44) avec un tas à la place d'une file : on compte les prérequis non finis de chaque tâche, on ne met dans le tas que les tâches à zéro, on sort toujours la meilleure clé, et la fin d'une tâche libère ses suivantes.

```text
ALGORITHME CleDePriorite
ENTRÉES : tâche (u, i, c, tₐ, nom), plafond c_max, poids w₁, w₂, w₃, taux a
SORTIE : clé (nombre, arrivée, nom), la plus petite clé passant en premier

SI min(w₁, w₂, w₃) < 0 OU u ∉ [0, 1] OU i ∉ [0, 1] OU c ∉ [0, c_max] ALORS
    échouer : entrée invalide
FIN SI
P₀ ← w₁ × u + w₂ × i − w₃ × c / c_max
RETOURNER (−arrondi(P₀ − w₁ × a × tₐ, 9 décimales), tₐ, nom)
```

```text
ALGORITHME OrdonnancerTachesPretes
ENTRÉES : tâches T, prérequis(t) pour chaque t, taux de vieillissement a
SORTIE : ordre d'exécution

POUR chaque tâche t de T FAIRE
    restants(t) ← nombre de prérequis de t
    suivants(t) ← liste vide
FIN POUR
POUR chaque tâche t de T FAIRE
    POUR chaque p de prérequis(t) FAIRE
        ajouter t à suivants(p)
    FIN POUR
FIN POUR
tas ← { CleDePriorite(t) pour chaque t tel que restants(t) = 0 }
ordre ← liste vide
TANT QUE tas n'est pas vide FAIRE
    t ← extraire la plus petite clé du tas
    ajouter t à la fin de ordre
    POUR chaque s de suivants(t) FAIRE
        restants(s) ← restants(s) − 1
        SI restants(s) = 0 ALORS
            insérer CleDePriorite(s) dans le tas         (le dernier prérequis de s vient de finir)
        FIN SI
    FIN POUR
FIN TANT QUE
SI longueur(ordre) < |T| ALORS
    échouer : cycle de dépendances
FIN SI
RETOURNER ordre
```

**Complexité :** le calcul d'une clé coûte O(1) en temps et en mémoire : trois produits, une somme, un arrondi. Pour l'ordonnancement, on note n le nombre de tâches et m le nombre de dépendances. Construire `restants` et `suivants` lit chaque tâche et chaque dépendance une fois : O(n + m). Construire le tas initial coûte O(n). Chaque tâche est insérée au plus une fois et extraite une fois, en O(log n) chaque fois : O(n log n). Chaque dépendance est décrémentée une fois, en O(1) : O(m). Le temps total vaut donc O(n log n + m). La mémoire vaut O(n + m) : les compteurs et le tas tiennent en O(n), les listes de suivants en O(m). Grâce à la clé fixe du point 7, le vieillissement ne coûte rien de plus ; un vieillissement non uniforme obligerait à recalculer les clés, en O(n) à chaque décision.

**Du squelette au code :** `CleDePriorite` est la composition de deux fonctions Python : `priorite`, qui porte les gardes et la ligne « P₀ ← … », et `cle`, qui renvoie le triplet `(-round(p0 - w[0] * a * t.arrivee, 9), t.arrivee, t.nom)`. `OrdonnancerTachesPretes` est la fonction `ordonnancer` : les deux premières boucles sont les dictionnaires `restants` et `suivants`, la ligne « tas ← … » est la compréhension de liste suivie de `heapq.heapify(tas)`, l'extraction est `heapq.heappop(tas)`, la décrémentation est `restants[s] -= 1` et l'insertion `heapq.heappush(tas, cle(par_nom[s], a))`. Le test final « longueur(ordre) < |T| » est `if len(ordre) != len(taches)`, qui lève une `ValueError`. La fonction `famine` n'est pas un algorithme de production : c'est la simulation qui vérifie la preuve du point 6.

## Cas d'usage réels aux Émirats

Les urgences, impacts, coûts, poids et taux de vieillissement ci-dessous sont illustratifs : chaque équipe les fixe par écrit et les révise à partir de ses journaux.

### Banque — une alerte anti-blanchiment avant le reporting

Une banque de détail de Dubaï fait tourner un orchestrateur qui répartit entre plusieurs agents les tâches de son back-office : alertes de surveillance anti-blanchiment, contrôles KYC, préparation d'offres de prêt, rapports mensuels, résumés de réunions. C'est le lot de l'exemple : l'alerte (0,67) passe d'abord, puis le KYC (0,565), puis l'offre (0,60) qui attendait ce KYC, puis le résumé et le rapport. Sans l'ordonnanceur sur les tâches prêtes, l'agent de crédit lancerait la préparation de l'offre sur un client non vérifié, ce qui est exactement ce que les obligations KYC de la CBUAE interdisent. Le poids w₁ de l'urgence est volontairement le plus fort, parce qu'une alerte de surveillance a des délais de traitement internes à tenir, et l'urgence d'une alerte se calcule à partir de son échéance. Le plafond de 8 000 tokens oblige à découper les analyses longues, ce qui garde les scores comparables. On suit le délai moyen de traitement des alertes et le nombre de tâches lancées avant leur prérequis, avec un objectif de zéro.

### Crypto — une alerte de liquidité avant une analyse de fond

Une plateforme d'actifs virtuels agréée par la VARA fait traiter par des agents les alertes de liquidité, les analyses de marché et des tâches de rédaction. Une alerte (u = 1, i = 0,9, 1 200 tokens) vaut 0,5 + 0,27 − 0,03 = 0,74 ; une analyse de fond (u = 0,2, i = 0,7, 7 200 tokens) vaut 0,10 + 0,21 − 0,18 = 0,13. Avec l'ancienne formule en tokens bruts, l'alerte valait −239,23 et une reformulation de 50 tokens sans enjeu −9,92 : l'orchestrateur aurait traité la reformulation d'abord, pendant que les retraits risquaient d'être bloqués. La correction tient en une division par le plafond, mais elle change complètement l'ordre. La VARA attend une gestion documentée des risques opérationnels (à confirmer avec le règlement en vigueur) : la fonction de score, ses poids et son plafond sont versionnés, et chaque décision d'ordonnancement est journalisée avec sa clé. On suit le délai entre une alerte de liquidité et sa prise en charge par un agent.

### RH — un certificat de salaire qui ne doit pas attendre indéfiniment

Un cabinet RH présent dans plusieurs émirats reçoit en continu des demandes : dossiers de visa, préparation des fichiers de paie pour le WPS, calculs d'indemnité de fin de service, attestations diverses. Les demandes de visa, plus urgentes, arrivent sans arrêt, et une demande de certificat de salaire de faible score pourrait rester au fond de la file pendant des semaines. Avec un vieillissement de a = 0,08 par heure et les poids par défaut, la fenêtre D vaut 25 heures : aucune demande arrivée plus de 25 heures après le certificat ne peut passer devant lui. Le calcul d'indemnité de fin de service a un impact élevé, parce qu'une erreur ou un retard engage l'employeur : il reçoit i = 0,9, et l'agent appelle l'outil déterministe `gratuite_fin_de_service` au lieu de laisser le modèle calculer. Les échéances de paie WPS se traduisent en urgence croissante à l'approche de la date. On suit le temps d'attente maximal par type de demande, pas seulement la moyenne.

### BTP — des poids écrits par la finance, appliqués par la plateforme

Un groupe de construction à Dubaï fait vérifier par des agents les factures de ses sous-traitants : contrôle de la TVA à 5 %, des retenues de garantie, des quantités livrées. La direction financière a écrit ses poids en points, (5, 3, 2), pour l'urgence (échéance de paiement), l'impact (montant rapporté au plus gros lot du marché) et le coût de vérification ; l'équipe plateforme les a saisis en (0,5 ; 0,3 ; 0,2). Le point 3 garantit que les deux écritures donnent exactement le même ordre, ce qui évite un débat inutile en comité. Une facture de 1 200 000 AED hors taxe, avec 60 000 AED de TVA, arrive en tête de file dès que son échéance approche. Si quelqu'un modifie un seul des poids, l'ordre change, et c'est voulu : un tel changement passe en revue comme une modification de code. On suit le nombre de factures payées en retard et le montant des pénalités évitées.

### Assurance — départager les sinistres de même score

Un assureur auto et santé trie les déclarations de sinistres par un score où l'urgence vient de la gravité médicale ou de l'immobilisation du véhicule. Beaucoup de sinistres simples ont exactement le même score : le départage décide alors seul de l'ordre. La règle du programme (le plus ancien d'abord, puis l'identifiant) rend l'ordre reproductible : rejouer la journée donne le même ordre, et un assuré qui se plaint d'avoir été servi après un autre reçoit une explication vérifiable. Sans règle écrite, l'ordre dépendrait de l'implémentation du tas ou de l'ordre de lecture de la base, et changerait d'un déploiement à l'autre. L'assurance est supervisée par la CBUAE, qui attend un traitement équitable des réclamations : « le plus ancien d'abord » à score égal en est la traduction directe. On suit l'écart entre le délai de traitement des sinistres de même catégorie.

### Secteur public — des demandes bilingues traitées dans un délai garanti

Une entité de services publics en ligne, accessible par UAE Pass, reçoit des demandes en arabe et en anglais, triées par un orchestrateur entre des agents spécialisés. Les demandes en lien avec une échéance légale ont une urgence forte ; les autres, comme une demande d'information générale, ont un score faible et risquent d'attendre. Avec a = 0,05 par heure et w₁ = 0,5, la fenêtre vaut D = 1 / 0,025 = 40 heures, que l'entité traduit en engagement de service écrit. Comme le vieillissement est le même pour toutes les demandes, la clé du tas se calcule une fois à l'arrivée (point 7), et l'ordonnanceur tient la charge sans recalcul. La PDPL impose de ne pas garder les données plus longtemps que nécessaire : une demande servie sort de la file avec ses données. On suit le percentile 95 du délai de réponse, qui doit rester sous l'engagement.

## Pièges et limites

- **Mélanger des échelles.** Un coût en tokens bruts écrase l'urgence et l'impact (−999,2). Chaque signal doit être ramené dans [0, 1].
- **Recalculer le plafond de coût sur le lot courant.** Le départ d'une tâche sans rapport peut alors inverser deux autres tâches (point 4).
- **Croire que le score gère les dépendances.** Il ne les voit pas : seules les tâches prêtes entrent dans le tas, et le graphe se vérifie à part (étapes 42 à 45).
- **Plafonner le vieillissement, ou l'oublier.** Sans lui, ou avec min(1, …), une tâche faible peut attendre pour toujours sous un flux continu de tâches meilleures.
- **Laisser les égalités au hasard.** Sans départage écrit, deux exécutions du même lot divergent, et l'audit ne peut pas rejouer une décision.

### Exercice feuille blanche

1. Sans regarder le code, écrire `priorite` avec ses trois gardes, puis `ordonnancer` avec un tas et un compteur de prérequis, et retrouver l'ordre alerte, KYC, offre, résumé, rapport.
2. Prédire, puis vérifier : avec a = 0,06, à quel top l'archivage passe-t-il, et que vaut la fenêtre D ? (Réponse : il faut 0,01 + 0,03 t > 0,36, soit t > 11,7 : au top 12. D = 1 / (0,5 × 0,06) ≈ 33,3 tops.)
3. Trouver le bug : `return w1 * urgence + w2 * impact + w3 * (cout / cout_max)`. Que devient l'ordre de l'ordonnanceur sur le lot de l'exemple ? (Réponse : le coût devient un bonus. Les scores valent 0,77, 0,615, 0,80, 0,37 et 0,23, et l'ordre devient alerte, KYC, offre, rapport, résumé : le rapport mensuel, la tâche la plus chère, passe maintenant avant le résumé. Plus une tâche coûte, plus elle monte, et aucun `assert` sur les bornes ne le voit, puisque le score reste dans [0, 1].)

## Pour aller plus loin

**WSJF (Weighted Shortest Job First).** Quand chaque tâche j a une durée dⱼ et un coût du retard cⱼ par unité de temps, et qu'un seul ouvrier les traite, l'ordre qui minimise le coût total des retards ∑ cⱼ Cⱼ (Cⱼ étant l'instant où j se termine) est l'ordre décroissant de cⱼ / dⱼ. La preuve est un échange de deux tâches voisines j et k qui commencent à l'instant t :

$$
\big[ c_j (t + d_j) + c_k (t + d_j + d_k) \big] - \big[ c_k (t + d_k) + c_j (t + d_k + d_j) \big] = c_k d_j - c_j d_k
$$

Cette différence est négative ou nulle exactement quand cⱼ / dⱼ ≥ c_k / d_k : mettre d'abord la tâche de plus grand rapport ne coûte jamais plus. En répétant l'échange, on trie tout le lot. C'est la règle de Smith ; le score linéaire de ce fichier en est une approximation commode quand on ne connaît pas les durées.

> Suite : [Graphes orientés acycliques et matrices d'adjacence](<42-Orchestration-Graphes.md>) — étape 42.
