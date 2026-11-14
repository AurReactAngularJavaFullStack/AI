# Étape 45 bis — Orchestration — Journal d'événements partitionné (à la manière de Kafka)

**Dossier :** 08-Orchestration

> Étape 45 bis du parcours · Prérequis : [Détection de cycle par DFS](<45-Detection-de-Cycle-DFS.md>) · Suite : [Déclencheurs, webhooks et tâches longues](<45c-Declencheurs-Webhooks-et-Taches-Longues.md>)

**Métiers concernés :** AI Engineers, AI Platform Team, AI Agent Ops, Forward-Deployed Engineers

Les étapes 42 à 45 ont ordonné des tâches à l'intérieur d'un orchestrateur : un graphe sans cycle, un tri topologique, une exécution durable (étape 40 bis). Dès que plusieurs agents et plusieurs services doivent se passer du travail **sans s'attendre**, survivre aux pannes et garder une trace rejouable de ce qui s'est passé, il faut une autre pièce : un journal d'événements partitionné. Apache Kafka en est l'exemple le plus connu du marché ; ce fichier n'en dépend pas. Il construit le mécanisme depuis une feuille blanche en bibliothèque standard, démontre ce qu'il garantit (l'ordre par clé, un parallélisme borné par le nombre de partitions, un effet « exactement une fois » obtenu à partir d'une livraison « au moins une fois »), puis le chiffre avec la loi de Little de l'étape 69.

## Définition

Un **journal d'événements** est une suite d'enregistrements immuables que l'on ne fait que prolonger (*append-only*) : on écrit à la fin, on ne modifie ni n'insère jamais rien. Il est découpé en P **partitions** indépendantes ; dans chaque partition, un événement reçoit un **offset**, son rang 0, 1, 2… dans cette partition. Un producteur choisit la partition à partir de la **clé** de l'événement (un numéro de compte, un identifiant de sinistre), par un hachage stable pris modulo P, de sorte que tous les événements d'une même clé tombent dans la même partition, dans leur ordre d'écriture. Les consommateurs lisent à leur rythme et retiennent où ils en sont par un **offset validé** (*committed offset*) : le prochain offset à lire. Les membres d'un même **groupe de consommateurs** se partagent les partitions, chacune étant lue par un seul membre à la fois, tandis que deux groupes différents lisent le même journal sans se gêner. Enfin, la **rétention** supprime les événements les plus anciens, et la **relecture** consiste à repositionner un groupe sur un offset plus ancien pour retraiter l'histoire.

## Rôle dans un agent

Le journal intervient à trois moments de la boucle percevoir → décider → agir → observer. Pour **percevoir**, un agent de production n'est pas toujours appelé par un utilisateur : il est souvent déclenché par un événement (un document KYC déposé, un virement signalé, un sinistre déclaré) qu'il lit dans le journal, au lieu d'interroger une base toutes les minutes. Pour **agir**, la décision de l'agent devient elle-même un événement publié, que d'autres agents ou services consomment : une chaîne triage → fraude → indemnisation se construit ainsi sans qu'aucun maillon n'appelle directement le suivant. Pour **observer**, la relecture permet de rejouer une semaine d'événements dans une nouvelle version de l'agent, dans un groupe séparé, et de comparer ses décisions à celles de la production sans rien toucher (étape 13 bis). Le composant concerné est l'**ordonnanceur** au sens large : le journal décide de l'ordre dans lequel le travail arrive à chaque agent, et le groupe de consommateurs décide qui le fait. Un point est propre aux agents : un appel au LLM coûte des tokens et ne rend pas toujours la même réponse ; un événement livré deux fois ne doit donc ni payer deux fois ni produire deux décisions différentes, d'où l'idempotence de l'étape 12, appliquée ici au consommateur.

## Équation complète

Choix de la partition d'un événement de clé k, avec un hachage h stable :

$$
p(k) = h(k) \bmod P
$$

Offset de fin d'une partition : l'offset que recevra le prochain événement écrit, égal au premier offset conservé plus le nombre d'événements conservés :

$$
\mathrm{LEO}_p = \mathrm{LSO}_p + n_p
$$

Retard (*lag*) d'un groupe g, somme sur les partitions de ce qui reste à lire :

$$
\mathrm{lag}_g = \sum_{p=0}^{P-1} \left( \mathrm{LEO}_p - c_{g,p} \right)
$$

Parallélisme d'un groupe de C membres, et charge du membre le plus chargé :

$$
N_{actifs} = \min(C, P) \qquad m_{max} = \left\lceil \frac{P}{C} \right\rceil
$$

Débit soutenable par le groupe, quand chaque membre traite μ événements par seconde et que les clés se répartissent uniformément :

$$
\lambda_{max} = \frac{\mu\, P}{\lceil P / C \rceil}
$$

Livraison au moins une fois, puis déduplication atomique par identifiant : chaque événement produit son effet exactement une fois.

$$
n_e \ge 1 \quad \text{et} \quad \text{déduplication atomique par } \mathrm{id}(e) \quad \Longrightarrow \quad \text{effets}(e) = 1
$$

Part des clés qui gardent leur partition quand on passe de P à P + 1 partitions, puis de P à mP :

$$
\Pr(\text{la clé reste}) = \frac{1}{P+1} \qquad \Pr(\text{la clé reste}) = \frac{1}{m}
$$

Loi de Little sur le journal (étape 69), et durée de vidange d'un retard accumulé :

$$
\bar{L} = \lambda\, \bar{W}
$$

$$
T_{vid} = \frac{\mathrm{lag}_0}{\mu_{eff} - \lambda} \qquad \text{si} \qquad \mu_{eff} > \lambda
$$

## Décryptage des symboles

$$
k
$$

La clé d'un événement, une chaîne qui désigne l'entité dont l'ordre compte (un compte, un sinistre, un bien) ; variable Python `cle`.

$$
h(k)
$$

Un hachage stable de la clé, un entier qui ne dépend que des octets de la clé, identique dans tous les processus ; ici `zlib.crc32(cle.encode("utf-8"))`.

$$
P
$$

Le nombre de partitions du sujet, un entier supérieur ou égal à 1 ; variable `n_partitions`, ou `Journal.n`.

$$
p,\; p(k)
$$

L'indice d'une partition, un entier de 0 à P − 1 ; p(k) est la partition de la clé k, renvoyée par `partition_de(cle, n_partitions)`.

$$
o
$$

L'offset d'un événement, son rang dans sa partition, un entier positif ou nul ; champ `Evenement.offset`.

$$
\mathrm{LSO}_p,\; \mathrm{LEO}_p
$$

Le premier offset encore conservé (*log start offset*) et l'offset de fin (*log end offset*) de la partition p, des entiers avec LSO ≤ LEO ; `Journal.debut[p]` et `Journal.fin(p)`.

$$
n_p
$$

Le nombre d'événements encore conservés dans la partition p, un entier positif ou nul ; `len(Journal.segments[p])`.

$$
g,\; c_{g,p}
$$

Un groupe de consommateurs, désigné par son nom, et son offset validé sur la partition p, c'est-à-dire le prochain offset qu'il lira, un entier entre LSO et LEO ; `groupe` et `Journal.position(groupe, p)`.

$$
\mathrm{lag}_g
$$

Le retard du groupe g, en nombre d'événements écrits mais pas encore validés, un entier positif ou nul ; `Journal.retard(groupe)`.

$$
C,\; N_{actifs},\; m_{max}
$$

Le nombre de membres du groupe, le nombre de membres qui reçoivent au moins une partition et le nombre maximal de partitions confiées à un même membre, des entiers ; `len(membres)`, `actifs`, `charge_max`.

$$
\mu,\; \lambda,\; \lambda_{max}
$$

Le débit de traitement d'un membre, le débit d'arrivée des événements et le débit d'arrivée maximal que le groupe peut suivre, en événements par seconde ; `mu`, `lam`, `capacites[c]`. Comme aux étapes 69 à 71, λ désigne ici un débit d'arrivée.

$$
n_e,\; \mathrm{id}(e)
$$

Le nombre de livraisons de l'événement e à un consommateur, un entier supérieur ou égal à 1 en « au moins une fois », et son identifiant métier unique, fixé par le producteur ; `GrandLivre.livraisons` (cumulé) et `Evenement.id_evt`.

$$
\text{effets}(e)
$$

Le nombre de fois où l'effet métier de e (ici, créditer un compte) a été appliqué ; `GrandLivre.effets` (cumulé sur tous les événements).

$$
\bar{L},\; \bar{W}
$$

Le retard moyen dans le temps, en événements, et l'attente moyenne d'un événement entre sa production et son traitement, en secondes ; `L` et `W` dans la section 7 du programme.

$$
\mathrm{lag}_0,\; \mu_{eff},\; T_{vid}
$$

Le retard accumulé au moment où le groupe redémarre, la capacité totale du groupe et la durée nécessaire pour revenir à un retard nul ; `max(retards)`, 6 événements par seconde dans l'exemple, et `vidange`.

## Démonstration

### 1. Même clé, même partition, à condition que le hachage soit stable

La partition ne dépend que de h(k) et de P. Si h est une fonction des seuls octets de la clé, deux événements de même clé ont le même h(k), donc le même reste modulo P, donc la même partition, quel que soit le producteur qui les écrit et quel que soit le moment. La condition n'est pas décorative : en Python, `hash()` d'une chaîne est salé au démarrage de chaque processus (variable `PYTHONHASHSEED`), si bien que deux producteurs, ou le même après un redémarrage, enverraient la même clé dans deux partitions différentes. Le programme utilise donc CRC-32, qui donne toujours 2 916 032 025 pour `CPT-1001`, et 2 916 032 025 mod 3 = 0. Selon sa documentation, le partitionneur par défaut de Kafka applique de la même façon un hachage murmur2 aux octets de la clé, modulo le nombre de partitions.

### 2. L'ordre est garanti par clé, pas globalement

Trois faits s'enchaînent. Dans une partition, l'offset d'un nouvel événement vaut LEO, puis LEO augmente de 1 : les offsets sont donc strictement croissants dans l'ordre d'écriture, parce que l'écriture se fait toujours à la fin. Dans un groupe, une partition n'est lue que par un membre à la fois, et ce membre lit les offsets dans l'ordre croissant à partir de son offset validé. Enfin, si un producteur écrit e₁ puis e₂ de même clé, les deux vont dans la même partition (point 1) et o(e₁) < o(e₂). Donc le premier traitement de e₁ précède celui de e₂. Dans le programme, `CPT-2002` reçoit les offsets 0, 2 et 4 de la partition 1, et le grand livre applique EVT-002, EVT-006, EVT-010 dans cet ordre.

Rien de tel entre deux clés de partitions différentes. EVT-001 (`CPT-1001`, partition 0) a été écrit avant EVT-002 (`CPT-2002`, partition 1), mais si le membre qui lit la partition 1 est plus rapide, EVT-002 est traité le premier. On choisit donc la clé de façon que tout ce qui doit rester ordonné partage la même clé : le numéro de compte pour des mouvements bancaires, la référence du bien pour des changements de statut immobiliers.

### 3. Changer P déplace la plupart des clés

Supposons h uniforme sur une plage dont la taille est un multiple de P(P + 1). Comme P et P + 1 sont premiers entre eux, le théorème chinois des restes dit que le couple (h mod P, h mod (P + 1)) prend chacune des P(P + 1) valeurs possibles avec la même probabilité. La clé reste dans sa partition si et seulement si les deux restes sont égaux ; or le couple (a, a) n'est possible que pour a de 0 à P − 1, soit P couples. Donc :

$$
\Pr(\text{la clé reste}) = \frac{P}{P(P+1)} = \frac{1}{P+1}
$$

De 4 à 5 partitions, il ne reste que 20 % des clés : 80 % changent de partition. Pour un passage de P à mP, on écrit h mod mP = (h mod P) + jP avec j uniforme entre 0 et m − 1, et la clé reste seulement si j = 0 : une probabilité 1/m, soit la moitié des clés quand on double P. Le programme mesure 0,2017 et 0,5000 sur 10 000 clés. La conséquence pratique est qu'un journal ne redistribue pas l'histoire : les anciens événements d'une clé restent dans l'ancienne partition, les nouveaux vont dans la nouvelle, et l'ordre par clé n'est plus garanti pendant la transition. On dimensionne donc P pour le pic prévisible dès la création du sujet.

### 4. Le parallélisme d'un groupe ne dépasse jamais P

Chaque partition est confiée à exactement un membre du groupe. Un membre actif possède au moins une partition, et deux membres ne possèdent jamais la même : le nombre de membres actifs est donc au plus P, et au plus C par définition, d'où N_actifs = min(C, P) ; avec C = 8 et P = 6, deux membres restent inactifs. Par le principe des tiroirs, si P partitions sont réparties entre C membres, l'un d'eux en reçoit au moins ⌈P/C⌉ ; l'affectation par plages en donne ⌊P/C⌋ ou ⌈P/C⌉ à chacun, donc elle atteint ce minimum. Si les clés sont uniformes, chaque partition reçoit λ/P événements par seconde, et le membre le plus chargé reçoit ⌈P/C⌉ λ/P. Il suit le rythme si cette charge reste au plus μ :

$$
\left\lceil \frac{P}{C} \right\rceil \frac{\lambda}{P} \le \mu
\quad\Longleftrightarrow\quad
\lambda \le \frac{\mu\, P}{\lceil P / C \rceil}
$$

Avec P = 6 et μ = 100 événements par seconde : 100, 200, 300 pour C = 1, 2, 3 ; encore 300 pour C = 4, parce qu'un membre garde deux partitions ; 600 pour C = 6 ; toujours 600 pour C = 8. Ajouter un quatrième consommateur ne sert à rien ici, et un neuvième non plus : le plafond est P.

### 5. Valider après traitement donne « au moins une fois », valider avant donne « au plus une fois »

Un consommateur fait deux choses pour chaque lot : traiter les événements, valider l'offset. Une panne peut survenir entre les deux, et le successeur reprend à l'offset validé. Si l'on **traite puis valide**, une panne entre les deux laisse des événements traités mais non validés : le successeur les relit et les retraite. Aucun événement n'est perdu, parce que l'offset validé ne dépasse jamais un événement non traité ; certains sont livrés deux fois, au plus la taille d'un lot par panne. Si l'on **valide puis traite**, une panne entre les deux laisse un offset validé au-delà d'événements jamais traités : ils sont perdus, mais aucun n'est traité deux fois. Dans le programme, la panne survient après 6 traitements : 3 de la partition 0, validés, puis 3 d'un lot de 4 de la partition 1. En validant après, les 3 derniers sont relivrés, d'où 12 + 3 = 15 livraisons ; en validant avant, EVT-008, le quatrième événement du lot, n'est jamais traité.

### 6. Au moins une fois + consommateur idempotent = effet exactement une fois

On note D l'ensemble des identifiants déjà appliqués, mémorisé avec l'état métier. Le consommateur fait, pour chaque livraison de e : si id(e) ∈ D, ne rien faire ; sinon, appliquer l'effet **et** ajouter id(e) à D, les deux dans la même transaction. On montre par récurrence sur les livraisons l'invariant suivant : id(e) ∈ D si et seulement si l'effet de e a été appliqué exactement une fois. Au départ, D est vide et rien n'est appliqué. À la première livraison de e, id(e) ∉ D, donc l'effet est appliqué et id(e) entre dans D, ensemble, parce que la transaction est atomique. À chaque livraison suivante, id(e) ∈ D, donc rien ne change. Comme la livraison « au moins une fois » garantit nₑ ≥ 1, la première livraison existe toujours, et l'effet de e est appliqué une fois et une seule.

Deux conditions portent la preuve. La première est l'**atomicité** : si l'effet est écrit dans une base et l'identifiant dans une autre, une panne entre les deux écritures produit un effet sans identifiant, et la relivraison l'applique une seconde fois. La seconde est la **portée** de D. Le programme compare deux mémoires. Un filigrane par partition (le prochain offset attendu) ne coûte que P entiers et suffit contre les relivraisons après panne, puisqu'un événement relivré garde son offset. Mais un producteur qui relance après un timeout alors que sa première écriture avait réussi écrit le **même** identifiant à un **nouvel** offset : le filigrane l'applique deux fois, l'ensemble des identifiants le reconnaît.

| Déduplication | Relivraison après panne | Doublon du producteur | Mémoire |
|---|---|---|---|
| aucune | effet doublé (9 000 AED crédités au lieu de 7 800) | effet doublé | rien |
| filigrane d'offset par partition | correcte | effet doublé (2 500 AED au lieu de 2 000) | P entiers |
| ensemble des identifiants | correcte | correcte | un identifiant par événement conservé |

Kafka traite le doublon du producteur de son côté, selon sa documentation, par un producteur idempotent (numéros de séquence par partition, vérifiés par le serveur), et propose des transactions qui valident l'offset et l'écriture de sortie ensemble. Le principe reste celui de la démonstration : une livraison répétée, plus une déduplication atomique.

### 7. Le retard se lit avec la loi de Little

Le temps avance par pas d'une seconde. À chaque pas, le producteur écrit 4 événements ; le consommateur est en panne pendant les pas 0 à 9, puis traite jusqu'à 6 événements par pas. On note lagₜ le retard à la fin du pas t et wₑ l'attente de l'événement e, du pas de sa production à celui de son traitement. Un événement produit au pas a et traité au pas b est compté dans le retard à la fin des pas a, a + 1, …, b − 1, soit exactement b − a = wₑ fois. En additionnant sur tous les pas, on compte donc chaque événement autant de fois que son attente, et si tout est traité avant la fin de l'horizon :

$$
\sum_{t} \mathrm{lag}_t = \sum_{e} w_e
$$

On divise par la durée T de l'horizon, puis on fait apparaître le nombre N d'événements :

$$
\bar{L} = \frac{1}{T}\sum_t \mathrm{lag}_t = \frac{N}{T} \cdot \frac{1}{N}\sum_e w_e = \lambda\, \bar{W}
$$

C'est la loi de Little de l'étape 69, ici exacte parce que le journal est vide au début et à la fin. Les nombres : pendant la panne, le retard monte de 4 par pas, 4, 8, …, 40, dont la somme vaut 4 × 55 = 220 ; ensuite, il descend de 6 − 4 = 2 par pas, 38, 36, …, 0, dont la somme vaut 2 × 190 = 380. Au total, 600 événements-secondes sur 60 s, donc L̄ = 10 ; 240 événements ont attendu 600 s en tout, donc W̄ = 2,5 s ; et λ W̄ = 4 × 2,5 = 10. La vidange du retard de 40 dure 40 / (6 − 4) = 20 s, parce que le retard diminue de μ_eff − λ à chaque seconde. Le retard en nombre d'événements ne dit rien de l'expérience de l'utilisateur ; divisé par λ, il donne l'attente, en secondes, que l'on compare à un objectif.

### 8. La relecture reconstruit l'état, tant que la rétention le permet

Un consommateur déterministe calcule son état par sᵢ = f(sᵢ₋₁, eᵢ) à partir d'un état initial s₀. Par récurrence, deux exécutions qui partent du même s₀ et lisent la même suite d'événements obtiennent le même état à chaque pas, parce que f appliquée deux fois aux mêmes arguments rend le même résultat. Le programme relit tout le journal dans un groupe neuf et retrouve exactement les soldes du grand livre. Deux limites suivent. Si f appelle un LLM, elle n'est plus déterministe : il faut alors journaliser la **décision** comme un événement, et relire les décisions plutôt que de les recalculer. Si la rétention a supprimé le début du journal, la relecture depuis l'offset 0 est impossible ; on garde donc des instantanés (l'état et les offsets atteints), et l'on relit seulement la fin, ce qui suppose que l'offset de l'instantané soit encore au moins égal au LSO de chaque partition.

### 9. Exemple fait à la main (le code reprend ces nombres)

| Grandeur | Calcul | Résultat |
|---|---|---|
| partition de CPT-1001 | 2 916 032 025 mod 3 | 0 |
| offsets de fin après 12 événements | 4 clés, 3 événements chacune | 3, 6, 3 |
| livraisons après la panne | 12 + 3 relivrés | 15 |
| crédit total sans déduplication | 7 800 + 200 + 400 + 600 | 9 000 AED |
| perte en « au plus une fois » | 4ᵉ événement du lot de la partition 1 | EVT-008 |
| débit soutenable, P = 6, C = 4 | 100 × 6 / ⌈6/4⌉ | 300 év/s |
| clés qui restent, de 4 à 5 partitions | 1 / 5 | 0,20 |
| Σ lag pendant puis après la panne | 220 + 380 | 600 |
| L̄ et W̄ | 600 / 60 et 600 / 240 | 10 et 2,5 s |
| vidange du retard | 40 / (6 − 4) | 20 s |

## Effets et comportement

- **Plus de partitions, plus de parallélisme possible, mais pas gratuitement.** Le plafond de débit d'un groupe vaut μP ; chaque partition coûte cependant des fichiers, de la mémoire chez le serveur et un rééquilibrage plus long.
- **Une clé chaude plafonne tout.** Si une clé reçoit 40 % du trafic, sa partition reçoit au moins 0,4 λ, et le membre qui la lit doit suivre seul : au-delà de λ = μ / 0,4, aucun nombre de consommateurs ne suffit.
- **Le retard monte linéairement pendant une panne et redescend à la vitesse μ_eff − λ.** Une capacité à peine supérieure au trafic vide un retard très lentement : avec μ_eff = 1,1 λ, la vidange dure dix fois la panne.
- **Plus le lot est grand, plus une panne relivre d'événements**, au plus un lot par partition non validée, mais moins on paie de validations.
- **Deux groupes ne se voient pas.** Le grand livre, l'agent de fraude et une relecture d'évaluation lisent le même journal, chacun avec ses propres offsets.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| k, h(k), P | `cle`, `zlib.crc32(...)`, `n_partitions` |
| p(k) | `partition_de(cle, n_partitions)` |
| o, LSO, LEO | `Evenement.offset`, `Journal.debut[p]`, `Journal.fin(p)` |
| c(g, p) | `Journal.position(groupe, p)`, écrit par `Journal.valider` |
| lag(g) | `Journal.retard(groupe)` |
| affectation des partitions | `affecter_par_plages(n_partitions, membres)` |
| nₑ, effets | `GrandLivre.livraisons`, `GrandLivre.effets` |
| D | `GrandLivre.vus` (identifiants) ou `GrandLivre.prochain` (filigranes) |
| L̄, W̄, λ | `L`, `W`, `lam` |

### Déroulé, ligne par ligne

**`Horloge`** est un compteur `t` en secondes simulées. Aucune heure réelle n'est lue : la production et le traitement datent leurs événements avec ce compteur, ce qui rend la section 7 exacte et reproductible.

**`partition_de(cle, n_partitions)`** lève `ValueError` pour P < 1, puis renvoie `zlib.crc32(cle.encode("utf-8")) % n_partitions`. Pour `CPT-1001`, `CPT-2002`, `CPT-1003` et `CPT-2004`, elle renvoie 0, 1, 2 et 1.

**`Evenement`** est une `dataclass` gelée (`frozen=True`) : une fois écrit, un événement ne peut plus être modifié, ce qui traduit l'immuabilité du journal dans le code. Elle porte la partition, l'offset, la clé, l'identifiant métier, le montant en AED et l'instant de production.

**`Journal`** tient trois structures : `segments[p]`, la liste des événements conservés de la partition p ; `debut[p]`, le LSO ; `valides`, un dictionnaire `(groupe, partition) -> prochain offset`.

- `produire` calcule `p`, crée l'événement avec `offset = self.fin(p)` et l'ajoute à la fin de la liste. Au douzième événement, les offsets de fin valent 3, 6 et 3.
- `fin(p)` renvoie `debut[p] + len(segments[p])`.
- `lire(p, depuis, max_n)` refuse un offset inférieur au LSO (« hors rétention »), puis découpe la liste à partir de `depuis - debut[p]`.
- `position(groupe, p)` renvoie l'offset validé, ou le LSO si le groupe n'a encore rien validé : un groupe neuf commence au début conservé.
- `valider` refuse un offset hors de [LSO ; LEO] et enregistre le prochain offset à lire.
- `retard(groupe)` additionne `fin(p) - position(groupe, p)` sur les partitions.
- `appliquer_retention(garder)` retire les plus anciens événements de chaque partition et avance `debut[p]` d'autant ; les offsets des événements restants ne changent pas.

**`affecter_par_plages(n_partitions, membres)`** trie les membres pour que tous calculent la même affectation, puis `divmod(n_partitions, len(tries))` donne la part de base et le reste. Pour P = 3 et les membres A et B : `divmod(3, 2) = (1, 1)`, A reçoit 2 partitions `[0, 1]` et B une, `[2]`. Pour P = 6 et 4 membres : `(1, 2)`, soit 2, 2, 1, 1.

**`Consommateur.sonder(partitions, panne_apres, budget, valider_avant)`** parcourt ses partitions. Pour chacune, il lit un lot à partir de l'offset validé, d'au plus `taille_lot` événements, ou de ce qui reste du `budget` du pas de temps. Par défaut, il traite chaque événement puis valide `lot[-1].offset + 1` : c'est « au moins une fois ». Avec `valider_avant=True`, il valide avant de traiter : « au plus une fois ». `panne_apres` lève `Panne` après un nombre donné de traitements, avant la validation du lot en cours.

**`GrandLivre(mode)`** est l'effet métier : créditer des comptes. `appliquer(e)` compte d'abord une livraison. En mode `"ids"`, il sort si `e.id_evt` est dans `vus` ; en mode `"offsets"`, il sort si `e.offset` est inférieur au filigrane `prochain[e.partition]` ; en mode `"naif"`, il ne filtre rien. Il crédite ensuite le solde, ajoute l'identifiant, avance le filigrane et compte un effet, dans un bloc sans point de panne : c'est la transaction atomique de la démonstration. `ordre` garde, par clé, la suite des identifiants appliqués.

**`vider(journal, groupe, consommateur, partitions)`** sonde tant que le retard du groupe n'est pas nul.

**`main()`**, section par section.

1. Douze crédits de 100 à 1 200 AED sur quatre comptes. Chaque clé n'occupe qu'une partition, avec des offsets croissants.
2. Pour chacun des trois modes, un groupe distinct, donc des offsets distincts sur le même journal. A reçoit `[0, 1]`, traite 3 événements de la partition 0 et les valide, en traite 3 de la partition 1 et plante. Après le départ de A, B reçoit les trois partitions et relit la partition 1 depuis l'offset 0. Les trois grands livres ont reçu 15 livraisons ; le naïf a crédité 9 000 AED, les deux autres 7 800 AED, le vrai total, et l'ordre par clé est celui de la production.
3. En validant avant de traiter, la même panne fait perdre EVT-008 : 11 effets sur 12.
4. Le producteur relance l'écriture de EVT-013 (500 AED sur `CPT-1001`) : deux événements, offsets 3 et 4 de la partition 0. Seul le mode `"ids"` garde le bon solde, 1 500 + 500 = 2 000 AED.
5. Pour P = 6, la boucle vérifie `actifs == min(c, 6)` et `charge_max == math.ceil(6 / c)`, puis calcule le débit soutenable `mu * 6 // charge_max`.
6. Sur 10 000 clés, 20,17 % gardent leur partition de 4 à 5 partitions, et 50 % de 4 à 8.
7. Un second journal, sur sa propre horloge : 4 événements par seconde pendant 60 s, une panne de 10 s, une capacité de 6 par seconde. `noter_fin` date chaque traitement. Σ lag et Σ attentes valent toutes deux 600, L̄ = λ W̄ = 10, W̄ = 2,5 s, et le retard maximal de 40 se vide en 20 s.
8. Un groupe neuf relit tout et retrouve les soldes. On prend un instantané (soldes, identifiants, offsets), on écrit trois crédits de 1 000 AED, puis la rétention ne garde que 2 événements par partition : relire depuis 0 lève `ValueError`. Un grand livre restauré depuis l'instantané, repositionné sur ses offsets, ne lit que les 3 nouveaux événements et rejoint exactement l'état du grand livre principal.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Horloge.__init__()`** — Le constructeur pose sur la table une horloge de théâtre dont les aiguilles ne bougent que lorsque le régisseur les pousse : il ne reçoit rien d'autre que l'objet lui-même et met son compteur `t` à zéro seconde simulée. Il ne renvoie rien ; le journal date chaque événement produit avec ce compteur, et `noter_fin` date chaque traitement de la même façon, si bien que les attentes de la section 7 sont exactes et identiques à chaque exécution, sans jamais lire l'heure réelle.

**`Horloge.avancer(secondes)`** — Cette méthode est le geste du régisseur qui pousse l'aiguille : elle reçoit un nombre de secondes et l'ajoute au compteur `t`, sans rien renvoyer. `main` l'appelle une fois par seconde simulée, d'abord après chacun des douze crédits de la section 1, puis à chaque tour de la boucle de 60 secondes de la section 7, où l'on produit 4 événements par seconde ; c'est le seul endroit du programme où le temps avance.

**`partition_de(cle, n_partitions)`** — Cette fonction est l'agent de tri postal qui envoie toujours le courrier d'un même destinataire dans le même casier : elle reçoit une clé, ici un numéro de compte, et le nombre P de partitions, lève une `ValueError` si P est inférieur à 1, puis calcule le hachage CRC-32 des octets de la clé et renvoie son reste modulo P. Ce hachage est stable d'un processus à l'autre, contrairement au `hash` de Python ; avec P = 3, `CPT-1001`, `CPT-2002`, `CPT-1003` et `CPT-2004` tombent dans les partitions 0, 1, 2 et 1, et la section 6 mesure qu'en passant de 4 à 5 partitions, seules 20 % environ des clés gardent la leur.

**`Journal.__init__(n_partitions, horloge)`** — Le constructeur ouvre un registre à P cahiers dont on ne peut qu'ajouter des lignes à la fin : il reçoit le nombre de partitions et l'horloge, crée une liste vide d'événements par partition, met à 0 le premier offset conservé de chacune, celui que la rétention fera avancer, et prépare le dictionnaire `valides` qui associera à chaque couple (groupe, partition) le prochain offset à lire. Il ne renvoie rien ; `main` crée ainsi un journal de 3 partitions pour le grand livre, puis un second, sur sa propre horloge, pour mesurer le retard.

**`Journal.produire(cle, id_evt, montant_aed)`** — Cette méthode est le greffier qui inscrit un nouvel acte au bas du bon cahier : elle reçoit la clé, l'identifiant métier et le montant en dirhams, choisit la partition avec `partition_de`, crée un `Evenement` gelé qui porte cette partition, l'offset de fin actuel, la clé, l'identifiant, le montant et l'instant de l'horloge, puis l'ajoute à la fin de la liste. Elle renvoie l'événement ; après les douze crédits de la section 1, les offsets de fin des trois partitions valent 3, 6 et 3, et la relance du producteur en section 4 écrit deux fois `EVT-013`, aux offsets 3 et 4 de la partition 0.

**`Journal.fin(p)`** — Cette petite méthode répond à la question « quel numéro portera la prochaine ligne de ce cahier ? » : elle reçoit le numéro de partition p et renvoie le premier offset conservé augmenté du nombre d'événements encore présents, c'est-à-dire l'offset de fin, le LEO. `produire` s'en sert pour numéroter chaque nouvel événement, `valider` pour refuser un offset au-delà, et `retard` pour mesurer combien d'événements un groupe n'a pas encore validés.

**`Journal.lire(p, depuis, max_n)`** — C'est l'archiviste qui sort du cahier une liasse de lignes consécutives : la méthode reçoit le numéro de partition, l'offset à partir duquel lire et le nombre maximal d'événements, lève une `ValueError` « hors rétention » si l'offset demandé est antérieur au premier offset conservé, puis découpe la liste à partir de la bonne position. Elle renvoie au plus `max_n` événements, peut-être moins s'il n'en reste pas ; après la rétention de la section 8, relire la partition 0 depuis l'offset 0 déclenche précisément cette erreur.

**`Journal.position(groupe, p)`** — Cette méthode est le marque-page de chaque groupe de lecteurs : elle reçoit le nom d'un groupe et un numéro de partition, et renvoie le prochain offset à lire, celui que le groupe a validé, ou, s'il n'a encore rien validé, le premier offset conservé. Ainsi, un groupe neuf commence au début de ce qui reste du journal ; c'est ce qui permet en section 8 à un nouveau grand livre de tout relire et de retrouver les mêmes soldes, chaque groupe ayant ses propres marque-pages.

**`Journal.valider(groupe, p, prochain)`** — C'est le geste du lecteur qui déplace son marque-page après avoir lu : la méthode reçoit le groupe, la partition et le prochain offset à lire, lève une `ValueError` s'il sort de l'intervalle entre le premier offset conservé et l'offset de fin, puis enregistre cette valeur dans `valides`. Elle ne renvoie rien ; le consommateur l'appelle après le traitement d'un lot, ou avant dans le mode « au plus une fois », et `main` l'utilise pour repositionner le grand livre restauré depuis l'instantané.

**`Journal.retard(groupe)`** — Cette méthode est le chef de quai qui compte les colis pas encore enlevés : elle reçoit le nom d'un groupe et renvoie, sommée sur toutes les partitions, la différence entre l'offset de fin et la position validée du groupe, le lag. `vider` sonde tant que ce nombre n'est pas nul, et la section 7 l'enregistre à chaque seconde : il monte jusqu'à 40 pendant la panne de 10 secondes, sa somme vaut 600, comme celle des attentes, et il se vide en 20 secondes.

**`Journal.appliquer_retention(garder)`** — C'est l'archiviste qui, faute de place, brûle les plus vieilles pages de chaque cahier sans renuméroter les autres : la méthode reçoit le nombre d'événements à garder par partition, retire de chaque partition les plus anciens en trop et avance d'autant son premier offset conservé. Elle ne renvoie rien ; les offsets des événements restants ne changent pas, et en section 8 les premiers offsets conservés deviennent `[3, 6, 2]`, si bien qu'un groupe ne peut plus relire depuis 0 et doit repartir d'un instantané.

**`Consommateur.__init__(nom, journal, groupe, traiter, taille_lot)`** — Le constructeur engage un lecteur et lui remet son badge : il reçoit le nom du membre, le journal à lire, le nom du groupe dont il porte les marque-pages, la fonction `traiter` à appliquer à chaque événement et la taille des lots, 4 par défaut, et range le tout dans l'objet. Il ne renvoie rien ; deux consommateurs du même groupe partagent ainsi les mêmes offsets validés, ce qui permet à B de reprendre exactement là où A s'est arrêté, alors que deux groupes différents ne se voient pas.

**`GrandLivre.__init__(mode)`** — Le constructeur ouvre le grand livre d'un comptable et lui fixe sa règle contre les doublons : il reçoit le mode, `"naif"`, `"offsets"` ou `"ids"`, lève une `ValueError` pour tout autre mode, puis initialise les soldes par compte, l'ensemble des identifiants déjà appliqués, le filigrane par partition, les compteurs de livraisons et d'effets, et l'ordre d'application par clé. Il ne renvoie rien ; `main` en crée un par mode pour montrer que seul le mode `"ids"` résiste à la fois à la relivraison après une panne et au doublon écrit par le producteur.

**`GrandLivre.appliquer(e)`** — Cette méthode est le comptable qui reçoit un ordre de crédit : elle reçoit un événement, compte une livraison, puis, en mode `"ids"`, s'arrête si l'identifiant a déjà été appliqué, et en mode `"offsets"`, si l'offset est inférieur au filigrane de sa partition ; en mode `"naif"`, elle ne filtre rien. Sinon, d'un seul bloc sans point de panne, elle crédite le compte, retient l'identifiant, avance le filigrane, compte un effet et note l'ordre d'application. Elle ne renvoie rien ; après la panne de la section 2, les trois livres ont reçu 15 livraisons, mais seuls `"offsets"` et `"ids"` ont crédité le vrai total de 7 800 AED.

**`vider(journal, groupe, consommateur, partitions)`** — Cette fonction est la consigne donnée à un lecteur de ne pas quitter son poste tant qu'il reste du courrier : elle reçoit le journal, le nom du groupe, un consommateur et la liste des partitions qu'il doit lire, puis appelle `sonder` encore et encore tant que le retard du groupe n'est pas nul. Elle ne renvoie rien ; `main` s'en sert après chaque panne et chaque rééquilibrage, avec toujours la liste complète des partitions, car le retard est compté sur toutes les partitions du groupe.

**`main()`** — Le chef d'orchestre déroule les huit sections du chapitre : il écrit douze crédits sur quatre comptes et vérifie que chaque clé reste dans une seule partition, fait planter le consommateur A avant une validation dans les trois modes, puis montre que valider avant de traiter perd `EVT-008` et que seul le mode `"ids"` reconnaît le doublon du producteur. Il calcule ensuite le parallélisme d'un groupe sur 6 partitions, la part des clés déplacées quand P change, le retard et la loi de Little sur un second journal, et termine par la relecture complète, l'instantané et la rétention ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

**`noter_fin(e)`** — Cette fonction interne vit dans `main`, à la section 7, comme un chronométreur posté au bout de la chaîne : elle reçoit un événement et inscrit, dans le dictionnaire `fini_a`, l'instant de l'horloge simulée `h2` auquel il a été traité, indexé par son identifiant. Elle ne renvoie rien et sert de fonction `traiter` au consommateur de la section 7 ; en retranchant l'instant de production de chaque événement, `main` obtient les attentes, dont la somme vaut 600 secondes et la moyenne 2,5 secondes, ce qui vérifie L̄ = λ W̄ = 10.

```python
"""Étape 45 bis — journal d'événements partitionné : partitions, offsets, groupes, au moins une fois + idempotence."""
import math
import sys
import zlib
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- horloge simulée
class Horloge:
    """Le temps, en secondes simulées, n'avance que lorsque le programme l'avance."""

    def __init__(self) -> None:
        self.t = 0.0

    def avancer(self, secondes: float) -> None:
        self.t += secondes


# ---------------------------------------------------------------- le journal
def partition_de(cle: str, n_partitions: int) -> int:
    """p(k) = h(k) mod P, avec un hachage STABLE (CRC-32) : même clé, même partition, dans tout processus."""
    if n_partitions < 1:
        raise ValueError("il faut au moins une partition")
    return zlib.crc32(cle.encode("utf-8")) % n_partitions


@dataclass(frozen=True)
class Evenement:
    partition: int
    offset: int
    cle: str
    id_evt: str
    montant_aed: int
    produit_a: float


class Panne(Exception):
    """Plantage simulé d'un consommateur."""


class Journal:
    """Un sujet (topic) de P partitions ; chaque partition est une liste qu'on ne fait que prolonger."""

    def __init__(self, n_partitions: int, horloge: Horloge) -> None:
        self.n = n_partitions
        self.horloge = horloge
        self.segments: list[list[Evenement]] = [[] for _ in range(n_partitions)]
        self.debut = [0] * n_partitions                  # premier offset encore conservé (rétention)
        self.valides: dict[tuple[str, int], int] = {}    # (groupe, partition) -> prochain offset à lire

    def produire(self, cle: str, id_evt: str, montant_aed: int) -> Evenement:
        p = partition_de(cle, self.n)
        e = Evenement(p, self.fin(p), cle, id_evt, montant_aed, self.horloge.t)
        self.segments[p].append(e)                       # append-only : rien n'est jamais modifié ni inséré
        return e

    def fin(self, p: int) -> int:
        """Offset de fin (log end offset) : l'offset que recevra le prochain événement."""
        return self.debut[p] + len(self.segments[p])

    def lire(self, p: int, depuis: int, max_n: int) -> list[Evenement]:
        if depuis < self.debut[p]:
            raise ValueError(f"offset {depuis} hors rétention : la partition {p} commence à {self.debut[p]}")
        i = depuis - self.debut[p]
        return self.segments[p][i:i + max_n]

    def position(self, groupe: str, p: int) -> int:
        """Prochain offset à lire pour ce groupe ; sans validation, on part du début conservé."""
        return self.valides.get((groupe, p), self.debut[p])

    def valider(self, groupe: str, p: int, prochain: int) -> None:
        if not self.debut[p] <= prochain <= self.fin(p):
            raise ValueError("offset validé hors du journal")
        self.valides[(groupe, p)] = prochain

    def retard(self, groupe: str) -> int:
        """lag = Σ (offset de fin − offset validé) sur les partitions."""
        return sum(self.fin(p) - self.position(groupe, p) for p in range(self.n))

    def appliquer_retention(self, garder: int) -> None:
        for p in range(self.n):
            surplus = len(self.segments[p]) - garder
            if surplus > 0:
                self.segments[p] = self.segments[p][surplus:]
                self.debut[p] += surplus


# ---------------------------------------------------------------- groupe de consommateurs
def affecter_par_plages(n_partitions: int, membres: list[str]) -> dict[str, list[int]]:
    """Membres triés ; chacun reçoit ⌊P/C⌋ partitions consécutives, les (P mod C) premiers une de plus."""
    if not membres:
        raise ValueError("un groupe sans membre ne lit rien")
    tries = sorted(membres)
    base, reste = divmod(n_partitions, len(tries))
    affectation, p = {}, 0
    for i, m in enumerate(tries):
        k = base + (1 if i < reste else 0)
        affectation[m] = list(range(p, p + k))
        p += k
    return affectation


class Consommateur:
    def __init__(self, nom: str, journal: Journal, groupe: str, traiter, taille_lot: int = 4) -> None:
        self.nom, self.journal, self.groupe = nom, journal, groupe
        self.traiter, self.taille_lot = traiter, taille_lot

    def sonder(self, partitions: list[int], panne_apres: int | None = None, budget: int | None = None,
               valider_avant: bool = False) -> list[Evenement]:
        """Lit un lot par partition et le traite. Par défaut, valide APRÈS traitement : au moins une fois."""
        traites: list[Evenement] = []
        for p in partitions:
            reste = self.taille_lot if budget is None else min(self.taille_lot, budget - len(traites))
            if reste <= 0:
                break
            lot = self.journal.lire(p, self.journal.position(self.groupe, p), reste)
            if lot and valider_avant:                                # au plus une fois : on valide d'abord
                self.journal.valider(self.groupe, p, lot[-1].offset + 1)
            for e in lot:
                self.traiter(e)
                traites.append(e)
                if panne_apres is not None and len(traites) == panne_apres:
                    raise Panne(f"{self.nom} plante après {len(traites)} traitements")
            if lot and not valider_avant:
                self.journal.valider(self.groupe, p, lot[-1].offset + 1)
        return traites


# ---------------------------------------------------------------- l'effet métier : un grand livre
class GrandLivre:
    """Crédite des comptes. mode : « naif » (aucune déduplication), « offsets » (filigrane par partition), « ids »."""

    def __init__(self, mode: str) -> None:
        if mode not in ("naif", "offsets", "ids"):
            raise ValueError("mode inconnu")
        self.mode = mode
        self.soldes: dict[str, int] = {}
        self.vus: set[str] = set()                 # mode « ids » : identifiants déjà appliqués
        self.prochain: dict[int, int] = {}         # mode « offsets » : prochain offset attendu par partition
        self.livraisons = 0
        self.effets = 0
        self.ordre: dict[str, list[str]] = {}      # ordre d'application par clé

    def appliquer(self, e: Evenement) -> None:
        self.livraisons += 1
        if self.mode == "ids" and e.id_evt in self.vus:
            return
        if self.mode == "offsets" and e.offset < self.prochain.get(e.partition, 0):
            return
        # L'effet et la mémoire de déduplication changent ENSEMBLE : aucun point de panne entre les deux lignes.
        self.soldes[e.cle] = self.soldes.get(e.cle, 0) + e.montant_aed
        self.vus.add(e.id_evt)
        self.prochain[e.partition] = e.offset + 1
        self.effets += 1
        self.ordre.setdefault(e.cle, []).append(e.id_evt)


def vider(journal: Journal, groupe: str, consommateur: Consommateur, partitions: list[int]) -> None:
    while journal.retard(groupe) > 0:
        consommateur.sonder(partitions)


def main() -> None:
    horloge = Horloge()
    comptes = ["CPT-1001", "CPT-2002", "CPT-1003", "CPT-2004"]

    print("1. Partition = crc32(clé) mod 3 : même clé, même partition")
    j = Journal(3, horloge)
    produits = []
    for i in range(12):
        produits.append(j.produire(comptes[i % 4], f"EVT-{i + 1:03d}", 100 * (i + 1)))
        horloge.avancer(1.0)
    for c in comptes:
        evts = [e for e in produits if e.cle == c]
        print(f"  {c} -> partition {partition_de(c, 3)} ; offsets {[e.offset for e in evts]}")
        assert len({e.partition for e in evts}) == 1
        assert [e.offset for e in evts] == sorted(e.offset for e in evts)
    print(f"  offsets de fin par partition : {[j.fin(p) for p in range(3)]}")
    assert zlib.crc32(b"CPT-1001") == 2916032025 and [j.fin(p) for p in range(3)] == [3, 6, 3]

    print("2. Panne avant validation, puis rééquilibrage : la livraison recommence")
    livres = {m: GrandLivre(m) for m in ("naif", "offsets", "ids")}
    for mode, livre in livres.items():
        groupe = f"grand-livre-{mode}"
        aff = affecter_par_plages(3, ["A", "B"])
        a = Consommateur("A", j, groupe, livre.appliquer)
        try:
            a.sonder(aff["A"], panne_apres=6)          # 3 de p0 (validés), puis 3 de p1 (non validés)
        except Panne:
            pass
        aff = affecter_par_plages(3, ["B"])           # A a disparu : B reprend toutes les partitions
        vider(j, groupe, Consommateur("B", j, groupe, livre.appliquer), aff["B"])
    verite = {c: sum(e.montant_aed for e in produits if e.cle == c) for c in comptes}
    for mode, livre in livres.items():
        print(f"  {mode:<8} livraisons = {livre.livraisons}  effets = {livre.effets}  "
              f"total crédité = {sum(livre.soldes.values())} AED")
    assert affecter_par_plages(3, ["B", "A"]) == {"A": [0, 1], "B": [2]}
    assert all(livre.livraisons == 15 for livre in livres.values())
    assert livres["naif"].effets == 15 and livres["naif"].soldes != verite
    assert livres["offsets"].soldes == verite and livres["ids"].soldes == verite and livres["ids"].effets == 12
    for c in comptes:                                  # l'ordre par clé est celui de la production
        assert livres["ids"].ordre[c] == [e.id_evt for e in produits if e.cle == c]

    print("3. Au plus une fois : valider avant de traiter perd un événement")
    livre_apuf = GrandLivre("ids")
    a = Consommateur("A", j, "au-plus-une-fois", livre_apuf.appliquer)
    try:
        a.sonder([0, 1], panne_apres=6, valider_avant=True)
    except Panne:
        pass
    vider(j, "au-plus-une-fois", Consommateur("B", j, "au-plus-une-fois", livre_apuf.appliquer), [0, 1, 2])
    perdus = sorted({e.id_evt for e in produits} - livre_apuf.vus)
    print(f"  effets = {livre_apuf.effets} sur 12 ; perdu(s) : {perdus}")
    assert livre_apuf.effets == 11 and perdus == ["EVT-008"]

    print("4. Doublon du producteur (relance après timeout) : seul le mode « ids » le reconnaît")
    for _ in range(2):                                 # même identifiant, deux offsets différents
        doublon = j.produire("CPT-1001", "EVT-013", 500)
    print(f"  EVT-013 écrit deux fois dans la partition {doublon.partition}, offsets 3 et {doublon.offset}")
    for mode, livre in livres.items():
        groupe = f"grand-livre-{mode}"
        vider(j, groupe, Consommateur("B", j, groupe, livre.appliquer), [0, 1, 2])
    verite["CPT-1001"] += 500
    tableau = {m: (livre.soldes["CPT-1001"], livre.soldes == verite) for m, livre in livres.items()}
    for mode, (solde, juste) in tableau.items():
        print(f"  {mode:<8} solde CPT-1001 = {solde} AED ; grand livre juste : {juste}")
    assert tableau == {"naif": (2500, False), "offsets": (2500, False), "ids": (2000, True)}

    print("5. Parallélisme d'un groupe : au plus P consommateurs actifs (P = 6, μ = 100 év/s)")
    mu, capacites = 100, {}
    for c in (1, 2, 3, 4, 6, 8):
        aff = affecter_par_plages(6, [f"C{i}" for i in range(c)])
        actifs = sum(1 for parts in aff.values() if parts)
        charge_max = max(len(parts) for parts in aff.values())
        capacites[c] = mu * 6 // charge_max
        print(f"  C = {c} : actifs = {actifs}, partitions max par membre = {charge_max}, "
              f"débit soutenable = {capacites[c]} év/s")
        assert actifs == min(c, 6) and charge_max == math.ceil(6 / c)
    assert capacites == {1: 100, 2: 200, 3: 300, 4: 300, 6: 600, 8: 600}

    print("6. Changer P déplace les clés : de 4 à 5 partitions")
    cles = [f"CPT-{i:05d}" for i in range(10_000)]
    restent = sum(1 for k in cles if partition_de(k, 4) == partition_de(k, 5)) / len(cles)
    restent_x2 = sum(1 for k in cles if partition_de(k, 4) == partition_de(k, 8)) / len(cles)
    print(f"  part des clés qui restent : {restent:.4f} (théorie 1/5 = 0.2) ; de 4 à 8 : {restent_x2:.4f} (théorie 0.5)")
    assert abs(restent - 0.2) < 0.02 and abs(restent_x2 - 0.5) < 0.02

    print("7. Retard (lag) et loi de Little : panne de 10 s, λ = 4 év/s, capacité 6 év/s")
    h2 = Horloge()
    j2 = Journal(3, h2)
    fini_a: dict[str, float] = {}

    def noter_fin(e: Evenement) -> None:
        fini_a[e.id_evt] = h2.t                        # instant de traitement, sur l'horloge simulée

    conso = Consommateur("C", j2, "suivi", noter_fin, taille_lot=6)
    retards, n = [], 0
    for tick in range(60):
        for _ in range(4):
            j2.produire(comptes[n % 4], f"T-{n:04d}", 1)
            n += 1
        if tick >= 10:                                 # le consommateur est en panne de 0 à 9
            conso.sonder([0, 1, 2], budget=6)
        retards.append(j2.retard("suivi"))
        h2.avancer(1.0)
    evts = [e for p in range(3) for e in j2.segments[p]]
    attentes = [fini_a[e.id_evt] - e.produit_a for e in evts]
    L, W, lam = sum(retards) / 60, sum(attentes) / len(evts), len(evts) / 60
    vidange = next(t for t in range(10, 60) if retards[t] == 0) - 10 + 1
    print(f"  lag max = {max(retards)} ; Σ lag = {sum(retards)} ; Σ attentes = {sum(attentes):.0f} s")
    print(f"  L = {L:.1f} ; W = {W:.2f} s ; λ W = {lam * W:.1f} ; vidange en {vidange} s = 40 / (6 − 4)")
    assert sum(retards) == sum(attentes) == 600 and L == lam * W == 10.0 and W == 2.5
    assert max(retards) == 40 and vidange == 20

    print("8. Relecture, instantané et rétention")
    relu = GrandLivre("ids")
    vider(j, "relecture", Consommateur("R", j, "relecture", relu.appliquer), [0, 1, 2])
    assert relu.soldes == livres["ids"].soldes          # même journal, même fonction : même état
    instantane = (dict(livres["ids"].soldes), set(livres["ids"].vus),
                  {p: j.position("grand-livre-ids", p) for p in range(3)})
    for i in range(3):
        j.produire(comptes[(i + 1) % 4], f"EVT-{14 + i:03d}", 1000)
    j.appliquer_retention(garder=2)
    try:
        j.lire(0, 0, 4)
    except ValueError as ex:
        print(f"  relire depuis 0 : ValueError ({ex})")
    else:
        raise AssertionError("la rétention aurait dû interdire la relecture complète")
    repris = GrandLivre("ids")
    repris.soldes, repris.vus = dict(instantane[0]), set(instantane[1])
    for p, pos in instantane[2].items():
        j.valider("reprise", p, pos)
    vider(j, "reprise", Consommateur("R", j, "reprise", repris.appliquer), [0, 1, 2])
    vider(j, "grand-livre-ids", Consommateur("B", j, "grand-livre-ids", livres["ids"].appliquer), [0, 1, 2])
    print(f"  début conservé par partition = {j.debut} ; instantané + fin du journal = état complet : "
          f"{repris.soldes == livres['ids'].soldes}")
    assert j.debut == [3, 6, 2] and repris.soldes == livres["ids"].soldes and repris.effets == 3

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
…
2. Panne avant validation, puis rééquilibrage : la livraison recommence
  naif     livraisons = 15  effets = 15  total crédité = 9000 AED
  offsets  livraisons = 15  effets = 12  total crédité = 7800 AED
  ids      livraisons = 15  effets = 12  total crédité = 7800 AED
3. Au plus une fois : valider avant de traiter perd un événement
  effets = 11 sur 12 ; perdu(s) : ['EVT-008']
…
  naif     solde CPT-1001 = 2500 AED ; grand livre juste : False
  offsets  solde CPT-1001 = 2500 AED ; grand livre juste : False
  ids      solde CPT-1001 = 2000 AED ; grand livre juste : True
…
  C = 3 : actifs = 3, partitions max par membre = 2, débit soutenable = 300 év/s
  C = 4 : actifs = 4, partitions max par membre = 2, débit soutenable = 300 év/s
…
  lag max = 40 ; Σ lag = 600 ; Σ attentes = 600 s
  L = 10.0 ; W = 2.50 s ; λ W = 10.0 ; vidange en 20 s = 40 / (6 − 4)
…
  début conservé par partition = [3, 6, 2] ; instantané + fin du journal = état complet : True
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : « exactement une fois » n'est pas une propriété du transport. Le journal livre au moins une fois ; c'est le consommateur, en mémorisant atomiquement ce qu'il a déjà appliqué, qui rend l'effet unique.

## Squelette algorithmique

Trois algorithmes forment la pièce : écrire un événement, consommer un lot en « au moins une fois », appliquer un effet de manière idempotente. Un quatrième reconstruit l'état après une perte, à partir d'un instantané. Entrées : la clé et la charge d'un événement, les partitions d'un membre, l'état du consommateur. Sorties : un offset, un état métier à jour, des offsets validés.

```text
ALGORITHME Produire(clé, identifiant, charge)
  p ← h(clé) mod P                         (h stable : CRC-32, murmur2, jamais un hachage salé)
  o ← LEO[p]
  ajouter (o, clé, identifiant, charge, instant) à la fin de segment[p]
  LEO[p] ← LEO[p] + 1
  RETOURNER (p, o)

ALGORITHME ConsommerAuMoinsUneFois(groupe, partitions du membre, taille du lot b)
  POUR CHAQUE p DANS partitions FAIRE
      lot ← lire(p, depuis c[groupe, p], au plus b événements)
      POUR CHAQUE e DANS lot FAIRE
          AppliquerIdempotent(e)
      FIN POUR
      SI lot non vide ALORS c[groupe, p] ← dernier offset du lot + 1     (valider APRÈS traitement)
  FIN POUR
  après une panne ou un départ : réaffecter les partitions ; le successeur repart de c[groupe, p]

ALGORITHME AppliquerIdempotent(e)
  SI id(e) ∈ D ALORS RETOURNER                  (déjà appliqué : livraison répétée)
  DÉBUT TRANSACTION
      appliquer l'effet de e à l'état
      D ← D ∪ { id(e) }
  FIN TRANSACTION

ALGORITHME ReprendreDepuisInstantané(instantané, groupe)
  SI pour une partition p, instantané.offset[p] < LSO[p] ALORS ERREUR « instantané trop ancien »
  état, D ← instantané.état, instantané.D
  POUR CHAQUE p FAIRE c[groupe, p] ← instantané.offset[p]
  TANT QUE lag(groupe) > 0 FAIRE ConsommerAuMoinsUneFois(groupe, toutes les partitions, b)
```

**Complexité :** produire coûte O(1) : un hachage de la clé, de longueur bornée, et un ajout en fin de liste. Consommer N événements coûte O(N) traitements plus O(N / b) validations ; une panne ajoute au plus b relivraisons par partition non validée. La déduplication coûte O(1) en moyenne avec un ensemble haché, et une mémoire d'un identifiant par événement pendant la fenêtre où un doublon peut arriver ; le filigrane coûte O(P) en mémoire. L'affectation par plages coûte O(C log C) pour trier les membres, plus O(P). La relecture complète coûte O(N) ; depuis un instantané, seulement le nombre d'événements écrits depuis.

**Du squelette au code :** `Produire` est `Journal.produire`, avec `partition_de` pour la première ligne et `Journal.fin` pour LEO. `ConsommerAuMoinsUneFois` est `Consommateur.sonder` avec `valider_avant=False`, et la boucle « tant que le retard est positif » est `vider` ; la réaffectation après panne est l'appel à `affecter_par_plages` avec la nouvelle liste de membres. `AppliquerIdempotent` est `GrandLivre.appliquer` en mode `"ids"`, où la transaction est le bloc de quatre lignes sans point de panne. `ReprendreDepuisInstantané` est la fin de la section 8 de `main` : restauration de `soldes` et `vus`, `Journal.valider` sur les offsets de l'instantané, puis `vider` ; le contrôle « instantané trop ancien » est la garde de `Journal.valider`, qui refuse un offset inférieur à `debut[p]`.

## Cas d'usage réels aux Émirats

Les volumes, nombres de partitions, débits et durées ci-dessous sont illustratifs ; on les mesure sur le trafic réel de chaque système.

### Banque — des virements entrants crédités une seule fois

Une banque de détail de Dubaï publie chaque virement entrant dans un journal de 12 partitions, avec pour clé le numéro de compte du bénéficiaire ; un agent de lutte anti-blanchiment et le service qui tient les soldes consomment ce journal dans deux groupes séparés. Un soir de fin de mois, un consommateur du service des soldes est redémarré par l'orchestrateur de conteneurs après avoir traité 3 virements d'un lot de 4, sans avoir validé : son successeur relit ces 3 virements, exactement comme la section 2 du programme. Sans déduplication, les 3 clients sont crédités deux fois, et le rapprochement du lendemain doit annuler des écritures, avec un risque d'avoir laissé un client dépenser de l'argent qui n'existe pas. Avec la référence unique du virement mémorisée dans la même transaction que l'écriture comptable, la relivraison ne fait rien. La clé « compte » garantit aussi que le débit et le crédit d'un même compte sont traités dans leur ordre d'arrivée. La banque étant supervisée par la CBUAE, le journal et ses offsets servent de piste d'audit : on peut montrer quel événement a produit quelle écriture. On suit le nombre de doublons détectés au rapprochement, avec un objectif de zéro, et le retard exprimé en secondes.

### Crypto — rejouer l'histoire d'un portefeuille pour un audit

Une plateforme d'actifs virtuels agréée par la VARA écrit chaque dépôt, retrait et changement de limite dans un journal dont la clé est l'identifiant du portefeuille. Après un incident, l'équipe de conformité doit expliquer comment un solde a atteint une valeur donnée : un groupe neuf relit les événements du portefeuille et reconstruit l'état pas à pas, ce qui marche parce que le consommateur est déterministe (démonstration, point 8). La rétention du journal est en revanche courte, par exemple sept jours, alors que les obligations de conservation se comptent en années : le journal n'est pas l'archive. La plateforme copie donc les événements dans un stockage d'archive et prend un instantané quotidien des soldes avec les offsets atteints, pour pouvoir reprendre la lecture même après la rétention. Sans instantané, un événement supprimé par la rétention rend la reconstruction impossible et l'audit impossible à prouver. On suit la durée de reconstruction d'un portefeuille et l'âge du plus ancien instantané encore utilisable.

### Assurance — une chaîne d'agents qui doit absorber un pic

Un assureur auto et santé fait passer chaque sinistre par trois agents reliés par des journaux : triage, détection de fraude, proposition d'indemnité, avec pour clé la référence du sinistre. Après un orage de grêle, le nombre de déclarations est multiplié par huit en quelques heures. L'équipe veut multiplier les consommateurs de l'agent de fraude, mais le sujet n'a que 6 partitions : avec μ = 100 sinistres par minute par consommateur, le plafond est de 600 sinistres par minute, et un septième consommateur reste inactif (démonstration, point 4). Augmenter le nombre de partitions en urgence déplacerait 80 % des clés en passant de 4 à 5, ou la moitié en doublant, et deux événements d'un même sinistre pourraient être traités dans le désordre pendant la transition. L'assureur dimensionne donc P à la création du sujet pour le pic prévisible, et non pour le trafic moyen. Le retard, divisé par le débit d'arrivée, donne l'attente moyenne d'un sinistre avant d'être examiné, que l'on compare au délai de prise en charge promis aux assurés. On suit le retard en minutes et la part de sinistres traités dans le délai.

### RH — le pic de fin de mois de la paie

Un cabinet RH multi-émirats prépare les fichiers de salaires transmis par le système de protection des salaires (WPS) : chaque ligne de salaire validée est un événement, avec pour clé l'identifiant de l'employeur, de sorte que toutes les lignes d'un employeur arrivent dans l'ordre à l'agent qui contrôle les écarts. Le dernier jour ouvré du mois, le trafic monte à λ = 200 lignes par seconde, et une mise à jour du consommateur l'interrompt une minute : le retard atteint 12 000 lignes. Avec une capacité de 300 lignes par seconde, la vidange dure 12 000 / (300 − 200) = 120 s, alors qu'avec une capacité de 220, elle durerait 600 s (démonstration, point 7). Le cabinet ne regarde donc pas le retard en lignes, qui ne parle à personne, mais l'attente W = L / λ, en secondes, qu'il compare à l'heure limite de transmission des fichiers. Sans cette lecture, l'équipe voit un retard « qui baisse » et ne sait pas s'il sera résorbé à temps. On suit le retard en secondes et la marge restante avant l'heure limite.

### Secteur public — évaluer une nouvelle version d'agent sur la semaine écoulée

Une entité de services publics en ligne, accessible par UAE Pass, publie chaque demande bilingue arabe-anglais dans un journal. Avant de déployer une nouvelle version de son agent de pré-instruction, l'équipe la fait lire la semaine écoulée dans un groupe de consommateurs séparé, qui ne produit aucun effet visible et écrit ses décisions dans un sujet d'évaluation. Comme deux groupes ne partagent pas leurs offsets, la production ne voit rien, et l'on compare les décisions des deux versions demande par demande (étape 13 bis). La PDPL impose la minimisation des données : les événements portent des références vers les dossiers, pas les pièces d'identité elles-mêmes, et la rétention du journal est limitée à ce dont l'évaluation a besoin. Sans journal, l'équipe ne pourrait évaluer la nouvelle version que sur un échantillon reconstitué à la main, moins représentatif du trafic réel. On suit le taux d'accord entre versions et la part des désaccords tranchés en faveur de la nouvelle.

### Immobilier — la bonne clé pour un statut de bien

Une agence de Dubaï et d'Abu Dhabi publie les changements de statut de ses biens (disponible, réservé, vendu, contrat Ejari enregistré) que consomment le site d'annonces et un agent qui répond aux prospects. Dans la première version, la clé était l'identifiant du commercial : la réservation et la vente d'un même appartement, saisies par deux commerciaux différents, tombaient dans deux partitions, et l'annonce repassait parfois à « réservé » après la vente. En prenant pour clé la référence du bien, les deux événements tombent dans la même partition, et leur ordre d'écriture est leur ordre de traitement (démonstration, point 2). La même règle vaut pour l'agent : il ne doit jamais proposer un bien dont le dernier statut lu est « vendu ». Sans la bonne clé, un prospect visite un bien déjà vendu, et l'agence perd sa crédibilité. On suit le nombre d'inversions de statut détectées, avec un objectif de zéro.

## Pièges et limites

- **Une clé mal choisie.** Une clé trop fine (le commercial au lieu du bien) casse l'ordre de l'entité qui compte ; une clé trop grossière (l'émirat au lieu du compte) crée une partition chaude que lit un seul consommateur, quelle que soit la taille du groupe.
- **Valider ce qui a été lu, pas ce qui a été traité.** La validation automatique périodique de nombreux clients valide les offsets lus ; si le traitement part dans un autre fil d'exécution, elle peut valider des événements encore en cours, et une panne les perd. On valide après le traitement, explicitement (avec Spring Kafka, par exemple, en mode d'acquittement manuel et en appelant `acknowledge()` après le traitement).
- **Une déduplication en deux temps.** Écrire l'effet dans une base, puis l'identifiant dans une autre, laisse une fenêtre où une panne produit un effet sans mémoire ; l'identifiant et l'effet s'écrivent dans la même transaction, ou l'effet est lui-même idempotent par sa clé métier.
- **Un LLM dans le consommateur.** Chaque relivraison repaie des tokens et peut produire une décision différente de la première : on enregistre la décision avec l'identifiant de l'événement et l'on renvoie la décision enregistrée.
- **Prendre le journal pour une archive.** La rétention supprime l'histoire ; ce qui doit être conservé des années va dans un stockage d'archive, avec des instantanés datés par leurs offsets.

### Exercice feuille blanche

1. Sans regarder le code, écrire `Journal.produire`, `Journal.lire`, `Journal.valider` et `Consommateur.sonder` (validation après traitement), puis simuler une panne après 2 traitements : combien d'événements sont relivrés ?
2. Prédire, puis vérifier avec `affecter_par_plages` : pour P = 8 et C = 3, quelles charges reçoivent les membres, et quel débit le groupe soutient-il avec μ = 100 ? (Réponse : 3, 3 et 2 partitions ; 100 × 8 / 3 ≈ 266,7 événements par seconde. Avec C = 5 : ⌈8/5⌉ = 2, donc 400.)
3. Trouver le bug : une variante de `GrandLivre.appliquer` ajoute l'identifiant à `vus` **avant** de créditer le solde, et une panne survient entre les deux lignes. Que devient l'événement à la relivraison ? (Réponse : il est ignoré, donc perdu : on est revenu à « au plus une fois ».)

## Pour aller plus loin

Le **compactage** du journal (*log compaction*) ne garde que le dernier événement de chaque clé, ce qui transforme le journal en table d'état rejouable. Le **hachage cohérent** et le *jump consistent hash* ne déplacent qu'environ 1/(P + 1) des clés quand on ajoute une partition, au lieu de P/(P + 1) avec le modulo. Le motif **outbox transactionnelle** écrit l'événement dans la même transaction que l'état métier, dans une table de la base, puis un relais le publie : il permet de se passer d'un serveur de journal, avec une table `evenements(partition, offset, cle, id_evt, charge)` et une table `offsets_valides(groupe, partition, prochain)` dans PostgreSQL. Comme exemples du marché, Apache Kafka, Redpanda, Apache Pulsar, Amazon Kinesis, Azure Event Hubs, Google Pub/Sub (avec ses clés d'ordre) et Redis Streams (avec `XREADGROUP` et `XACK`) offrent des variantes du même modèle ; les noms exacts des garanties diffèrent et se vérifient dans leur documentation. L'étape 45 ter branche ce journal sur le monde extérieur : webhooks signés, planificateur et tâches longues.

> Étape 45 bis du parcours · Prérequis : [Détection de cycle par DFS](<45-Detection-de-Cycle-DFS.md>) · Suite : [Déclencheurs, webhooks et tâches longues](<45c-Declencheurs-Webhooks-et-Taches-Longues.md>)
