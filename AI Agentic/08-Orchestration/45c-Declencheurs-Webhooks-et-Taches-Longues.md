# Étape 45 ter — Orchestration — Déclencheurs, webhooks et tâches longues

**Dossier :** 08-Orchestration

> Étape 45 ter du parcours · Prérequis : [Journal d'événements partitionné](<45b-Journal-d-Evenements-Partitionne.md>) · Suite : [MCP : définitions fondamentales](<../09-MCP/46-MCP-Definitions-Fondamentaux.md>)

**Métiers concernés :** AI Engineers, AI Platform Team, AI Agent Ops, Forward-Deployed Engineers

Un agent de production démarre rarement parce qu'un humain tape une question. Il est réveillé par un **déclencheur** : un service extérieur qui l'appelle par un webhook (« le paiement est passé »), une horloge qui le lance à heure fixe (« chaque nuit à 2 h »), ou la fin d'une **tâche longue** qu'il a lui-même lancée et qui dure des minutes ou des heures. L'étape 45 bis a construit le journal où ces événements se rangent ; ce fichier construit, depuis une feuille blanche et en bibliothèque standard, les trois portes d'entrée : un récepteur de webhooks qui vérifie une signature HMAC-SHA256 et refuse les rejeux, un planificateur de type cron qui calcule la prochaine exécution, et un gestionnaire de tâches longues avec états, sondage à intervalles croissants, rappel signé, point de reprise et reprise après panne. Chaque mécanisme est démontré, puis chiffré sur une horloge simulée.

## Définition

Un **webhook** est une requête HTTP qu'un service envoie de lui-même à une adresse que vous lui avez donnée, pour vous prévenir d'un événement. Comme n'importe qui peut envoyer une requête à cette adresse, l'émetteur la **signe** : il calcule un HMAC-SHA256 de l'horodatage et des octets du corps avec un secret partagé, et le récepteur refait le calcul avant de croire quoi que ce soit. Une **tolérance d'horodatage** (300 s ici) rejette une requête signée trop ancienne, ce qui empêche de rejouer plus tard une requête capturée. Un **planificateur de type cron** déclenche un travail aux instants décrits par une expression à cinq champs (minute, heure, jour du mois, mois, jour de la semaine). Une **tâche longue** est un travail qui ne tient pas dans le délai d'une requête : on la **soumet**, on reçoit un **identifiant**, puis on suit son **état** (pending, running, succeeded, failed), soit en **sondant** à intervalles croissants, soit en attendant un **rappel** (*callback*). Un **point de reprise** enregistre ce qui est fait, pour qu'un autre travailleur reprenne au bon endroit après une panne.

## Rôle dans un agent

Ces trois mécanismes sont l'étape « percevoir » des agents qui travaillent sans humain en face. Le récepteur de webhooks est la frontière de confiance : c'est le **garde-fou** d'entrée qui décide si un événement extérieur est authentique avant qu'il n'atteigne le journal (étape 45 bis) et donc la boucle de l'agent ; une signature mal vérifiée laisse n'importe qui déclencher l'agent, ou lui faire créditer un paiement fictif. Le planificateur est l'**ordonnanceur** des travaux récurrents : rapprochements nocturnes, rapports hebdomadaires, rafraîchissement d'un index. Le gestionnaire de tâches longues sert à l'étape « agir » quand l'outil appelé ne répond pas tout de suite : traitement par lots d'un fournisseur de modèle, extraction d'un dossier de 300 pages, validation humaine qui prend deux jours. La boucle d'agent de l'étape 13 ne doit pas rester bloquée pendant ce temps : elle reçoit un identifiant, rend la main, et reprend quand l'état devient terminal.

## Équation complète

Signature d'un webhook d'horodatage t avec le secret K, et définition de HMAC :

$$
\sigma = \mathrm{HMAC}_{\mathrm{SHA256}}\left(K,\; t \,\|\, \text{"."} \,\|\, \text{corps}\right)
$$

$$
\mathrm{HMAC}(K, m) = H\Big( (K' \oplus \mathrm{opad}) \,\|\, H\big( (K' \oplus \mathrm{ipad}) \,\|\, m \big) \Big)
$$

Règle d'acceptation, avec S l'ensemble des secrets en vigueur, τ la tolérance et D les identifiants déjà reçus :

$$
\text{accepter} \iff \big(\exists\, K \in S,\; \sigma_K = \sigma_{\text{reçue}}\big) \;\wedge\; |t_{now} - t| \le \tau \;\wedge\; \mathrm{id} \notin D
$$

Taille du cache anti-rejeu, pour un débit de webhooks λ_w :

$$
|D| \lesssim \lambda_w \cdot 2\tau
$$

Nombre d'essais d'une attaque par mesure du temps sur une comparaison qui s'arrête au premier écart, pour une signature de L caractères dans un alphabet A, contre une recherche exhaustive :

$$
N_{essais} \le |A| \cdot L \qquad \text{contre} \qquad |A|^{L}
$$

Prochaine exécution d'une expression cron après t₀ :

$$
t^{*} = \min \big\{\, t > t_0 \;:\; \mathrm{min}(t) \in M,\; \mathrm{h}(t) \in H,\; \mathrm{mois}(t) \in O,\; \mathrm{jour}(t) \,\big\}
$$

$$
\mathrm{jour}(t) = \big(\mathrm{j}(t) \in J\big) \vee \big(\mathrm{js}(t) \in W\big) \quad \text{si les deux champs sont restreints, sinon} \quad \big(\mathrm{j}(t) \in J\big) \wedge \big(\mathrm{js}(t) \in W\big)
$$

Sondage d'une tâche de durée T avec un intervalle qui double à partir de b (série géométrique de l'étape 12) :

$$
W_k = b\,(2^{k} - 1) \qquad k^{*} = \left\lceil \log_2\left(\frac{T}{b} + 1\right) \right\rceil \qquad W_{k^{*}} - T < T + b
$$

Même sondage avec un plafond D, puis avec un intervalle fixe d :

$$
k^{*} = j + \left\lceil \frac{T - W_j}{D} \right\rceil \quad \text{avec} \quad j = \left\lfloor \log_2 \frac{D}{b} \right\rfloor + 1 \quad (T > W_j)
\qquad\qquad
k^{*}_{fixe} = \left\lceil \frac{T}{d} \right\rceil
$$

Travail exécuté par une tâche de n éléments, avec un point de reprise tous les m éléments et c pannes :

$$
E \le n + c\, m
$$

## Décryptage des symboles

$$
K,\; S
$$

Le secret partagé entre l'émetteur et le récepteur, une suite d'octets, et l'ensemble des secrets acceptés pendant une rotation (le nouveau et l'ancien) ; `secret`, et `RecepteurWebhook.secrets`.

$$
t,\; t_{now}
$$

L'horodatage signé par l'émetteur, un entier de secondes, et l'instant de réception sur l'horloge du récepteur ; `t` dans `recevoir` et `self.horloge.t`.

$$
\sigma,\; \sigma_{\text{reçue}}
$$

La signature attendue, 64 caractères hexadécimaux, et celle que porte l'en-tête `v1=` ; `attendues` et `signatures`.

$$
H,\; K',\; \mathrm{ipad},\; \mathrm{opad}
$$

La fonction de hachage (SHA-256, blocs de 64 octets), la clé complétée par des zéros à 64 octets (ou d'abord hachée si elle est plus longue), et les octets constants 0x36 et 0x5C répétés ; dans `hmac_sha256_a_la_main`.

$$
\tau
$$

La tolérance d'horodatage, en secondes, 300 ici ; `tolerance`.

$$
D,\; \mathrm{id}
$$

L'ensemble des identifiants d'événements déjà acceptés et encore dans la fenêtre de tolérance, et l'identifiant de l'événement reçu ; `RecepteurWebhook.vus` et `evt["id"]`.

$$
\lambda_w
$$

Le débit de webhooks reçus, en requêtes par seconde ; il ne sert qu'à dimensionner `vus`.

$$
A,\; L,\; N_{essais}
$$

L'alphabet de la signature (16 chiffres hexadécimaux), sa longueur (64 caractères) et le nombre de requêtes d'un attaquant ; `alphabet`, `longueur`, `essais`.

$$
M,\; H,\; J,\; O,\; W
$$

Les ensembles de minutes, d'heures, de jours du mois, de mois et de jours de la semaine (0 = dimanche) décrits par l'expression cron ; `minutes`, `heures`, `jours`, `mois`, `jours_semaine` dans le dictionnaire de `analyser_cron`. Dans cette formule, H désigne un ensemble d'heures, pas la fonction de hachage.

$$
t_0,\; t^{*}
$$

L'instant à partir duquel on cherche, et la prochaine exécution, la plus petite date strictement postérieure qui correspond ; `apres` et la date renvoyée par `prochaine_execution`.

$$
T,\; b,\; D,\; d
$$

La durée réelle de la tâche, le premier intervalle de sondage, le plafond d'intervalle et l'intervalle d'un sondage fixe, en secondes ; `fin_tache`, `base`, `plafond`, et `base` avec `fixe=True`. Ici D désigne un plafond, comme à l'étape 12 ; le contexte le distingue de l'ensemble D des identifiants.

$$
W_k,\; k^{*},\; j
$$

L'instant du k-ième sondage, le nombre de sondages nécessaires pour voir la fin, et le nombre d'intervalles avant le plafond ; `t` et `n` dans `sonder_jusqu_a`.

$$
n,\; m,\; c,\; E
$$

Le nombre d'éléments d'une tâche, l'écart entre deux points de reprise, le nombre de pannes et le nombre total d'exécutions d'éléments ; `len(elements)`, 1 dans le programme, le nombre d'exceptions `Panne`, et `GestionnaireTaches.executions`.

## Démonstration

### 1. Pourquoi HMAC, et pas un simple hachage du secret suivi du message

L'idée naïve est de signer par H(K ∥ m). Elle est fausse avec SHA-256. Cette fonction découpe son entrée en blocs, et son empreinte finale n'est autre que l'état interne après le dernier bloc (construction de Merkle-Damgård). Qui connaît H(K ∥ m) et la longueur de K ∥ m peut donc repartir de cet état et calculer H(K ∥ m ∥ bourrage ∥ m′) pour un m′ de son choix, sans connaître K : c'est l'attaque par extension de longueur, qui forge une signature valide pour un message prolongé. HMAC l'empêche en emboîtant deux hachages : le hachage externe porte sur la clé masquée par opad, suivie d'une empreinte interne de taille fixe, et un attaquant ne peut pas prolonger une entrée dont il ne connaît pas le début. Sous des hypothèses standard sur la fonction de compression, HMAC se comporte comme une fonction pseudo-aléatoire, résultat établi par Bellare, Canetti et Krawczyk (1996), puis Bellare (2006). Le programme réécrit HMAC à la main à partir de la définition, avec le cas d'une clé de plus de 64 octets, d'abord hachée, et retrouve exactement le résultat du module `hmac` pour trois longueurs de clé.

### 2. Ce que couvre la signature : l'horodatage et les octets bruts

Le récepteur recalcule σ sur `t` suivi de « . » et des octets reçus, puis compare. Si un seul octet du corps change, le message signé change, et produire la nouvelle signature sans K reviendrait à casser HMAC : le corps modifié de 1 250 à 9 250 AED est refusé (401). Si l'émetteur change l'horodatage pour faire passer une vieille requête, la signature ne correspond plus non plus, parce que t est dans le message signé. Le piège le plus courant n'est pas une attaque : c'est de vérifier la signature sur un JSON **re-sérialisé** par le framework web. Le même objet écrit avec des espaces après les deux-points n'a pas les mêmes octets, donc pas la même signature : le programme le refuse aussi. On vérifie toujours sur le corps brut, avant de le désérialiser.

### 3. Tolérance + cache des identifiants : un message signé est accepté au plus une fois

On veut montrer qu'un même message signé (t, id) n'est jamais accepté deux fois, alors que le récepteur oublie les identifiants dont l'horodatage a plus de τ secondes. Supposons-le accepté à l'instant u. Alors |u − t| ≤ τ et id entre dans D avec l'horodatage t. Considérons une nouvelle présentation du même message à un instant u′ > u. Si t ≥ u′ − τ, la purge n'a pas retiré id, qui est encore dans D : réponse « déjà reçu ». Sinon, t < u′ − τ, donc u′ − t > τ, et la tolérance le refuse. Dans les deux cas, il n'est pas accepté une seconde fois. La purge est donc sûre, et la mémoire bornée : les identifiants conservés ont un horodatage dans [t_now − τ ; t_now + τ], une fenêtre de 2τ secondes, d'où |D| ≲ λ_w · 2τ ; à 50 webhooks par seconde et τ = 300 s, environ 30 000 identifiants. Dans le programme, la requête capturée rejouée 600 s plus tard est refusée par la tolérance, alors même que evt_0001 a déjà été purgé.

Ce résultat porte sur un message **identique**. Un émetteur qui relance après un échec signe souvent à nouveau, avec un horodatage neuf : le message est différent, et s'il arrive après la purge, il est accepté une seconde fois (« relance tardive », 750 s après la première livraison). Le cache anti-rejeu est une protection de **sécurité**, de courte durée ; l'**idempotence métier** est une autre mémoire, durable, tenue en aval par le consommateur du journal (étape 45 bis), qui ne produit qu'un effet par identifiant. Le programme montre la file avec evt_0001 deux fois, et une seule fois après déduplication durable.

### 4. Pourquoi `hmac.compare_digest` : une comparaison qui s'arrête au premier écart parle

Une comparaison ordinaire de chaînes s'arrête au premier caractère différent : son temps croît avec la longueur du préfixe commun. Un attaquant qui mesure ce temps essaie les 16 premiers caractères possibles, garde celui qui prend le plus longtemps, et passe au suivant. Quand les i premiers caractères sont justes, un mauvais candidat pour la position i coûte i + 1 comparaisons, et le bon en coûte au moins i + 2 : le maximum désigne le bon caractère sans ambiguïté. Il faut donc au plus |A| essais par position, soit au plus 16 × 64 = 1 024 requêtes, contre 16⁶⁴ = 2²⁵⁶ ≈ 1,16 × 10⁷⁷ pour une recherche exhaustive. Le programme simule ce « temps » par le nombre de caractères comparés et retrouve la vraie signature en 1 011 essais. Avec une comparaison à temps constant, qui parcourt toujours les 64 caractères, tous les candidats coûtent pareil, l'attaquant n'apprend rien et repart bredouille après 1 024 essais. Sur un vrai réseau, la mesure est bruitée, et l'attaquant compense en répétant ses mesures ; le principe ne change pas. `hmac.compare_digest` est la comparaison conçue pour ce cas.

### 5. La prochaine exécution d'une expression cron : sauter sans rien manquer

`prochaine_execution` part de t₀ + 1 minute et teste dans l'ordre le mois, le jour, l'heure, puis la minute. Le lemme qui la justifie : si le mois de la date courante n'appartient pas à O, **aucune** minute de ce mois ne convient, puisque le mois est le même pour toutes ; sauter au 1er du mois suivant à 0 h 00 ne fait donc manquer aucune solution. Même raisonnement pour un jour qui ne convient pas (on saute au lendemain 0 h 00) et pour une heure (on saute à l'heure suivante, minute 0). Comme chaque pas avance strictement la date et ne saute que des instants qui ne conviennent pas, la première date qui passe les quatre tests est la plus petite solution postérieure à t₀. Le nombre de pas reste petit : 27 pour aller du vendredi 17 h 50 au lundi 9 h 00 avec « */15 9-17 * * 1-5 », 71 pour atteindre le 29 février 2028. Une expression impossible, comme le 31 février, épuiserait la recherche : l'horizon de cinq ans, qui couvre un cycle bissextile complet, la fait échouer par `ValueError` au lieu de boucler.

Deux règles se vérifient dans le programme. D'abord, la règle historique de cron : quand le jour du mois **et** le jour de la semaine sont restreints, l'un **ou** l'autre suffit ; « 0 8 1 * 1 » s'exécute le lundi 16 novembre 2026, et non au prochain lundi qui serait aussi un 1er du mois, le 1er février 2027. Ensuite, le fuseau : Dubaï est à UTC+4 sans heure d'été, si bien qu'aucune heure locale n'est sautée ni répétée dans l'année, contrairement aux fuseaux européens. En revanche, une expression écrite pour 9 h mais interprétée par un serveur réglé en UTC part à 13 h, heure de Dubaï.

### 6. Sonder avec un intervalle qui double : peu de requêtes, au plus deux fois la durée

Le k-ième sondage a lieu à Wₖ = b + 2b + … + 2ᵏ⁻¹b = b(2ᵏ − 1), la série géométrique démontrée à l'étape 12. La tâche, de durée T, est vue au premier k tel que Wₖ ≥ T, c'est-à-dire 2ᵏ ≥ T/b + 1 ; en passant au logarithme, k* = ⌈log₂(T/b + 1)⌉. Le retard de détection est borné, parce que le sondage précédent tombait avant la fin, Wₖ₋₁ < T :

$$
W_{k} - T < W_{k} - W_{k-1} = b\,2^{k-1} = W_{k-1} + b < T + b
$$

On voit donc la fin avant 2T + b : au pire un peu plus du double de la durée, avec seulement O(log T) requêtes. Pour T = 41 s et b = 1 s : 6 sondages, aux instants 1, 3, 7, 15, 31 et 63, et un retard de 22 s, inférieur à 42. Un intervalle fixe d demande ⌈T/d⌉ sondages, 21 toutes les 2 s, pour un retard inférieur à d. Le plafond D combine les deux : la série double tant que l'intervalle ne dépasse pas D, puis avance de D en D, et le retard devient inférieur à D. Avec D = 16 : j = 5 intervalles avant le plafond, W₅ = 31, puis un sondage de plus à 47, soit un retard de 6 s. Sur une heure, le doublement seul donne 12 sondages mais une détection à 4 095 s ; avec un plafond de 60 s, 65 sondages et une détection à 3 603 s ; toutes les 2 s, 1 800 sondages. Le rappel, quand l'émetteur sait en envoyer un, ramène le retard à zéro sans aucun sondage, mais il dépend d'une adresse joignable et d'une signature : on le double d'un sondage lent qui sert de filet.

### 7. La machine à états termine, et ses états terminaux ne se rouvrent pas

La table `TRANSITIONS` n'autorise que pending → running ou failed, et running → succeeded, failed ou pending ; succeeded et failed n'ont aucune transition sortante. Un état terminal est donc **absorbant** : la tentative de passer de succeeded à running lève `ValueError`. La terminaison se montre par un compteur. Chaque passage à running augmente `tentatives` de 1 ; un retour de running à pending n'a lieu que si le bail a expiré, et seulement si `tentatives` est encore inférieur au maximum R ; sinon, la tâche passe à failed. Une tâche fait donc au plus R tentatives, et chacune finit en succeeded ou par une expiration de bail, à condition que la surveillance tourne. Après R expirations, la tâche est en failed : elle ne tourne jamais indéfiniment. La tâche qui plante à chaque essai le vérifie : failed après 3 tentatives.

Le bail est ce qui révèle un travailleur mort. Il plante à t = 14 s ; son dernier battement de cœur datait de t = 12 s, donc son bail courait jusqu'à 42 s. Entre les deux, le client qui interroge à 31 s voit « running » pour un travailleur qui n'existe plus. La détection a lieu au premier passage de la surveillance après l'expiration, ici à 45 s. Un bail plus court détecte plus vite, mais un élément légitimement lent qui dépasse le bail ferait reprendre la tâche par un second travailleur pendant que le premier travaille encore.

### 8. Le point de reprise borne le travail refait

Le point de reprise est écrit **après** l'effet de chaque élément. Une panne interrompt au plus le travail fait depuis le dernier point de reprise, soit au plus m éléments si l'on enregistre tous les m éléments ; le successeur reprend à ce point. Avec c pannes, le nombre total d'exécutions vérifie E ≤ n + c m. L'élément interrompu est exécuté deux fois : une fois avant la panne, une fois à la reprise. Il doit donc être **idempotent**, ce que garantit ici le rangement du résultat sous la clé de l'élément, comme la clé d'idempotence de l'étape 12. Dans le programme : n = 10 dossiers, m = 1, c = 1, d'où E = 11 exécutions pour 10 résultats. Enregistrer le point de reprise **avant** l'effet serait l'erreur inverse : une panne entre les deux ferait sauter un élément jamais traité (voir l'étape 40 bis).

### 9. Exemple fait à la main (le code reprend ces nombres)

| Grandeur | Calcul | Résultat |
|---|---|---|
| relance de la même requête 30 s après | id déjà dans D | 200, « déjà reçu » |
| requête capturée rejouée 600 s après | 600 > τ = 300 | 400 |
| essais maximum de l'attaque par temps | 16 × 64 | 1 024 (mesuré : 1 011) |
| prochaine exécution de « */15 9-17 * * 1-5 » après vendredi 17 h 50 | samedi et dimanche exclus, 18 h exclu | lundi 9 h 00 |
| « 0 8 1 * 1 », règle OU puis règle ET | lundi 16 novembre ; 1er février 2027 | 2026-11-16 ; 2027-02-01 |
| sondages pour T = 41 s, b = 1 s | ⌈log₂ 42⌉ | 6, détection à 63 s |
| avec un plafond de 16 s | 5 + ⌈(41 − 31)/16⌉ | 6, détection à 47 s |
| sondage fixe toutes les 2 s | ⌈41/2⌉ | 21 |
| une heure, plafond de 60 s | 6 + ⌈(3 600 − 63)/60⌉ | 65 |
| détection du travailleur mort | dernier battement à 12 s + bail de 30 s | après 42 s, vue à 45 s |
| exécutions pour 10 dossiers et une panne | 10 + 1 × 1 | 11 |

## Effets et comportement

- **Une tolérance plus large accepte des horloges mal réglées, mais élargit la fenêtre de rejeu** et grossit le cache, en proportion de τ.
- **La rotation d'un secret se fait sans coupure** si le récepteur accepte l'ancien et le nouveau pendant la transition ; on retire l'ancien une fois que l'émetteur n'utilise plus que le nouveau.
- **Doubler l'intervalle de sondage divise la charge sur le serveur de tâches**, au prix d'un retard de détection qui peut atteindre la durée de la tâche ; un plafond borne ce retard.
- **Un point de reprise plus fréquent réduit le travail refait** après une panne, mais chaque enregistrement coûte une écriture.
- **Un bail court détecte vite les pannes et provoque plus de reprises à tort** ; un bail long laisse une tâche morte affichée « running ».

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| HMAC(K, m) | `hmac_sha256_a_la_main(cle, message)`, et `hmac.new(...)` en production |
| t ∥ « . » ∥ corps | `message_signe(horodatage, corps)` |
| σ, en-tête | `signer(secret, horodatage, corps)`, `lire_entete(entete)` |
| S, τ, D | `RecepteurWebhook.secrets`, `tolerance`, `vus` |
| règle d'acceptation | `RecepteurWebhook.recevoir` |
| N essais, A, L | `attaque_par_temps(oracle, longueur, alphabet)` |
| M, H, J, O, W | `analyser_cron(expression)` |
| t* | `prochaine_execution(expression, apres)` |
| Wₖ, k* | `sonder_jusqu_a(fin_tache, base, plafond, fixe)` |
| états et transitions | `TRANSITIONS`, `GestionnaireTaches.transition` |
| n, m, c, E | `len(elements)`, un point de reprise par élément, `Panne`, `executions` |

### Déroulé, ligne par ligne

**`Horloge`** est un compteur de secondes simulées, que l'on peut faire démarrer à une valeur quelconque : `Horloge(1_000_000.0)` donne au récepteur un « maintenant » de 1 000 000 s. Aucune heure réelle n'est lue.

**`hmac_sha256_a_la_main(cle, message)`** suit la définition. Une clé de plus de 64 octets est d'abord remplacée par son SHA-256 ; `cle.ljust(bloc, b"\x00")` la complète par des zéros à 64 octets ; `bytes(b ^ 0x36 for b in cle)` calcule K′ ⊕ ipad, et 0x5C donne opad. Le hachage interne porte sur `ipad + message`, le hachage externe sur `opad + interne`.

**`message_signe(horodatage, corps)`** fabrique les octets signés : `b"1000000." + corps`. **`signer`** calcule le HMAC avec le module `hmac` et renvoie l'en-tête `t=1000000,v1=0cee2ae3…`. **`lire_entete`** découpe l'en-tête sur les virgules, garde `t` s'il est numérique et toutes les valeurs `v1` (un émetteur en rotation peut en envoyer deux), et lève `ValueError` s'il manque l'un ou l'autre.

**`RecepteurWebhook.recevoir(entete, corps)`**, dans l'ordre des contrôles.

1. `purger()` retire de `vus` les identifiants dont l'horodatage est antérieur à `t_now - tolerance`.
2. Un en-tête illisible donne 400.
3. Les signatures attendues sont calculées pour chaque secret de `self.secrets` ; `hmac.compare_digest` les compare aux signatures reçues. Aucune correspondance : 401. La signature passe **avant** la tolérance, parce que l'horodatage n'est digne de confiance qu'une fois signé.
4. Un écart de plus de 300 s entre `t` et l'horloge : 400.
5. Le corps n'est désérialisé qu'ensuite. Un identifiant déjà dans `vus` donne 200 « déjà reçu » : on répond 200 pour que l'émetteur cesse de relancer, mais on ne refait rien.
6. Sinon, l'identifiant entre dans `vus`, l'événement part dans `file` (le journal de l'étape 45 bis) et la réponse est 200 « accepté ». Le traitement lourd se fait plus tard : un récepteur qui traite avant de répondre dépasse le délai de l'émetteur, qui relance.

**`comparer_naif`** renvoie le résultat et le nombre de caractères comparés jusqu'au premier écart ; **`comparer_temps_constant`** accumule `ord(x) ^ ord(y)` sur tous les caractères et renvoie toujours un coût de 64. **`attaque_par_temps`** construit, pour chaque position, 16 candidats `trouve + c + "000…"`, et garde celui dont le coût est maximal.

**`analyser_champ(texte, lo, hi)`** accepte `*`, une valeur, une plage `a-b`, un pas `/n` et des listes séparées par des virgules ; `*/15` sur les minutes donne `{0, 15, 30, 45}`, `9-17` donne les heures 9 à 17, et 7 est accepté comme dimanche. Une valeur hors bornes lève `ValueError`. **`analyser_cron`** exige cinq champs et note si le jour du mois et le jour de la semaine sont restreints. **`jour_correspond`** convertit `weekday()` (lundi = 0 en Python) en numérotation cron (dimanche = 0) par `(d.weekday() + 1) % 7`, puis applique la règle OU si les deux champs sont restreints.

**`prochaine_execution(expression, apres)`** part de la minute suivante et applique les quatre sauts de la démonstration. Le saut de mois utilise `d.replace(day=1) + timedelta(days=32)`, qui tombe toujours dans le mois suivant, puis revient au 1er à 0 h 00. Elle renvoie la date et le nombre de pas, ou lève `ValueError` au-delà de 5 × 366 jours.

**`sonder_jusqu_a(fin_tache, base, plafond, fixe)`** avance `t` de l'intervalle courant, compte un sondage, s'arrête dès que `t >= fin_tache`, puis double l'intervalle (borné par `plafond`), sauf en mode fixe.

**`GestionnaireTaches`** tient les tâches et le compteur `executions`.

- `soumettre` crée une `Tache` en pending, note la date dans `historique` et renvoie aussitôt l'identifiant `tache-0001`.
- `transition` refuse toute transition absente de `TRANSITIONS`, puis ajoute `(instant, ancien, nouveau)` à l'historique.
- `etat_a(id_, t)` renvoie l'état vu par un client qui interroge à l'instant t : la dernière transition datée au plus t.
- `prendre` passe la tâche à running, compte une tentative et ouvre un bail de 30 s.
- `surveiller` passe à pending (ou à failed après 3 tentatives) toute tâche running dont le bail a expiré.
- `executer` reprend à `point_de_reprise`. Pour chaque élément, elle avance l'horloge de 2 s, range le résultat sous la clé de l'élément, compte une exécution, puis écrit le point de reprise et renouvelle le bail. `panne_sur=6` lève `Panne` après l'effet de l'élément 6 et avant son point de reprise. À la fin, la tâche passe à succeeded et le rappel part.

**`main()`**, section par section.

1. HMAC écrit à la main et module `hmac` coïncident pour des clés de 10, 64 et 100 octets.
2. Huit livraisons au récepteur, qui accepte le nouveau et l'ancien secret : 200 accepté, 200 déjà reçu (re-signée 30 s plus tard), 401 pour le corps modifié, 401 pour le JSON ré-sérialisé, 401 pour un mauvais secret, 400 pour la requête capturée rejouée 600 s plus tard, 200 pour une requête signée avec l'ancien secret, et 200 pour une relance re-signée 750 s après la première. La file contient evt_0001 deux fois, et la déduplication durable `dict.fromkeys` n'en garde qu'un effet.
3. L'attaque retrouve la signature de 64 caractères en 1 011 essais avec la comparaison naïve, et échoue après 1 024 essais avec la comparaison à temps constant.
4. Cinq expressions cron à partir du vendredi 13 novembre 2026 à 17 h 50, heure locale de Dubaï, puis la règle ET, le 31 février et la conversion de 9 h UTC en 13 h à Dubaï.
5. Les quatre stratégies de sondage pour T = 41 s, puis la vérification de k* = ⌈log₂(T + 1)⌉ et de la borne du retard pour T = 5, 41, 600 et 3 600 s.
6. Une tâche de 10 dossiers : panne à 14 s pendant le dossier 6, client qui voit « running » à 31 s, bail expiré constaté à 45 s, reprise par un second travailleur, fin à 53 s et rappel signé accepté par le client. Les sondages du client aux instants 1, 3, 7, 15, 31, 47 et 63 voient « succeeded » au dernier. Une tâche terminale refuse de se rouvrir, et une tâche qui plante à chaque essai finit en failed après 3 tentatives.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Horloge.__init__(t)`** — Le constructeur installe une horloge de théâtre que personne ne remonte en cachette : il reçoit l'instant de départ en secondes, 0 par défaut, et le range dans le compteur `t`. Il ne renvoie rien ; `main` fait démarrer le récepteur de webhooks à 1 000 000 de secondes, pour que les horodatages signés ressemblent à de vrais instants, et la tâche longue à 0, si bien qu'aucune heure réelle n'est jamais lue et que la sortie reste identique d'une exécution à l'autre.

**`Horloge.avancer(secondes)`** — Cette méthode est le régisseur qui pousse l'aiguille d'un cran choisi : elle reçoit un nombre de secondes et l'ajoute au compteur, sans rien renvoyer. Le récepteur la subit à travers `envoyer`, qui fait passer 30 secondes avant la relance, 600 avant la requête rejouée et 120 avant la relance tardive ; le gestionnaire de tâches l'appelle, lui, pour faire durer chaque dossier 2 secondes, et `main` s'en sert pour laisser expirer le bail de la tâche qui plante à chaque essai.

**`RecepteurWebhook.__init__(secrets, horloge, tolerance)`** — Le constructeur ouvre le guichet d'un récepteur méfiant : il reçoit la liste des secrets acceptés, le nouveau et l'ancien pendant une rotation, l'horloge et la tolérance d'horodatage, 300 secondes par défaut, et prépare le dictionnaire `vus`, qui associe chaque identifiant d'événement déjà accepté à son horodatage signé, ainsi que la liste `file`, qui part vers le journal de l'étape 45 bis. Il ne renvoie rien ; `main` en crée un pour le webhook de paiement et un autre, côté client, pour recevoir le rappel signé de la tâche longue.

**`RecepteurWebhook.purger()`** — Cette méthode est l'archiviste qui jette les fiches devenues inutiles : elle ne reçoit rien, calcule la limite égale à l'instant présent moins la tolérance, puis retire de `vus` tout identifiant dont l'horodatage signé est antérieur à cette limite. Elle ne renvoie rien ; c'est sans danger, car un message plus ancien que la limite sera de toute façon refusé pour horodatage hors tolérance, et `main` vérifie qu'après 630 secondes seul `evt_0002` reste en mémoire, ce qui explique qu'une relance tardive re-signée de `evt_0001` soit de nouveau acceptée.

**`RecepteurWebhook.recevoir(entete, corps)`** — C'est le guichetier qui contrôle chaque pli dans un ordre immuable avant de le mettre dans le panier : la méthode reçoit l'en-tête de signature et les octets bruts du corps, purge d'abord les vieux identifiants, renvoie 400 si l'en-tête est illisible, recalcule la signature attendue pour chaque secret et renvoie 401 si aucune ne correspond par `hmac.compare_digest`, puis 400 si l'horodatage, désormais digne de confiance, s'écarte de plus de 300 secondes. Elle ne désérialise le JSON qu'ensuite et renvoie 200 « déjà reçu » pour un identifiant connu, ou bien l'enregistre, le met en file et renvoie 200 « accepté » ; les huit livraisons de `main` donnent ainsi 200, 200, 401, 401, 401, 400, 200 et 200.

**`sonder_jusqu_a(fin_tache, base, plafond, fixe)`** — Cette fonction met en scène un client impatient qui passe la tête par la porte pour savoir si son dossier est prêt : elle reçoit l'instant où la tâche finit, l'attente de base, un plafond facultatif et un drapeau pour un intervalle fixe, puis, à chaque tour, avance le temps de l'attente courante, compte un sondage, s'arrête dès que le temps atteint la fin de la tâche, et sinon double l'attente, bornée par le plafond, sauf en mode fixe. Elle renvoie le nombre de sondages et l'instant de détection : pour une tâche de 41 secondes, 21 sondages à 42 s toutes les 2 s, 5 à 50 s toutes les 10 s, 6 à 63 s en géométrique, et 6 à 47 s avec un plafond de 16 s.

**`GestionnaireTaches.__init__(horloge, duree_bail, tentatives_max, rappel)`** — Le constructeur ouvre le bureau qui suit les longs travaux : il reçoit l'horloge, la durée d'un bail, 30 secondes par défaut, le nombre maximal de tentatives, 3 par défaut, et une fonction de rappel facultative, puis crée le dictionnaire des tâches et met à 0 le compteur `executions`, qui compte les appels réels au traitement, reprises comprises. Il ne renvoie rien ; dans `main`, le rappel est la fonction `rappeler`, qui prévient le client par un webhook signé quand la tâche aboutit.

**`GestionnaireTaches.soumettre(elements)`** — Cette méthode est le guichet de dépôt qui rend un ticket sans faire attendre : elle reçoit la liste des éléments à traiter, fabrique un identifiant numéroté, `tache-0001` pour la première, crée une `Tache` à l'état pending avec une copie de la liste, inscrit dans son historique l'instant du dépôt et l'état pending, puis renvoie aussitôt l'identifiant. Le client repart avec ce numéro et reviendra demander l'état plus tard ; `main` soumet ainsi dix dossiers, puis une tâche d'un seul dossier qui plantera à chaque essai.

**`GestionnaireTaches.transition(tache, nouvel)`** — C'est l'huissier qui vérifie que chaque changement d'état figure bien au règlement : la méthode reçoit une tâche et le nouvel état, lève une `ValueError` « transition interdite » si ce passage n'est pas prévu dans `TRANSITIONS`, puis ajoute à l'historique le triplet formé de l'instant, de l'ancien état et du nouveau, avant de changer l'état. Elle ne renvoie rien ; les états succeeded et failed n'ont aucune sortie, si bien que `main` constate qu'une tâche terminée refuse de repasser à running.

**`GestionnaireTaches.etat_a(id_, t)`** — Cette méthode répond comme un registre daté à la question « où en était ce dossier à telle heure ? » : elle reçoit l'identifiant d'une tâche et un instant t, parcourt l'historique et renvoie l'état de la dernière transition datée au plus tard à t. Elle permet de rejouer après coup ce qu'un client aurait vu en interrogeant à différents moments ; dans `main`, les sondages aux instants 1, 3, 7, 15, 31, 47 et 63 voient running à 31 secondes et succeeded seulement au dernier.

**`GestionnaireTaches.prendre(id_)`** — C'est le travailleur qui décroche un dossier du tableau et signe le registre : la méthode reçoit l'identifiant de la tâche, la fait passer à running par `transition`, ajoute 1 à ses tentatives et lui ouvre un bail qui court jusqu'à l'instant présent plus la durée du bail. Elle renvoie la tâche, prête à être passée à `executer` ; si le travailleur disparaît sans renouveler ce bail, `surveiller` le constatera et remettra la tâche en attente ou la déclarera en échec.

**`GestionnaireTaches.surveiller()`** — Cette méthode est le contremaître qui fait sa ronde et déclare absent tout ouvrier dont le badge a expiré : elle ne reçoit rien, parcourt toutes les tâches et, pour chacune qui est running alors que l'horloge a dépassé la fin de son bail, la fait passer à failed si elle a déjà épuisé ses tentatives, ou à pending sinon. Elle ne renvoie rien ; dans `main`, la ronde de 31 secondes ne voit rien d'anormal, car le bail court jusqu'à 42 secondes, mais celle de 45 secondes remet la tâche en pending, et la tâche qui plante toujours finit en failed après 3 tentatives.

**`GestionnaireTaches.executer(tache, traiter, panne_sur, duree_element)`** — C'est le travailleur à l'ouvrage, qui note sa progression après chaque pièce pour qu'un collègue puisse reprendre : la méthode reçoit la tâche, la fonction de traitement, un indice facultatif où simuler une panne et la durée d'un élément, 2 secondes par défaut, puis repart du point de reprise et, pour chaque élément, avance l'horloge, range le résultat sous la clé de l'élément, compte une exécution, lève `Panne` si c'est l'élément désigné, et sinon avance le point de reprise et renouvelle le bail. À la fin, elle passe la tâche à succeeded et appelle le rappel ; elle ne renvoie rien, et `main` vérifie 11 traitements pour 10 dossiers, l'élément 6 ayant été traité deux fois sans doublon de résultat.

**`main()`** — Le chef d'orchestre déroule les six sections du chapitre : il vérifie que le HMAC écrit à la main coïncide avec le module `hmac` pour trois tailles de clé, envoie huit livraisons au récepteur de webhooks et contrôle leurs codes et la déduplication en aval, puis montre qu'une attaque par mesure du temps retrouve la signature avec une comparaison naïve mais échoue avec une comparaison à temps constant. Il calcule ensuite les prochaines exécutions de cinq expressions cron à partir du vendredi 13 novembre 2026 à 17 h 50, compare les stratégies de sondage pour une tâche de 41 secondes, et rejoue enfin la tâche longue avec panne, bail expiré, reprise et rappel signé ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

**`envoyer(nom, attente, fabriquer)`** — Cette fonction interne vit dans `main`, à la section 2, et joue l'émetteur de webhooks qui poste un pli au guichet : elle reçoit un libellé pour l'affichage, un délai en secondes et une petite fonction qui fabrique le couple (en-tête, corps), avance d'abord l'horloge du délai, pour que la signature soit fabriquée à l'instant de l'envoi, appelle cette fabrique, transmet le résultat à `recepteur.recevoir`, ajoute le code obtenu à la liste `codes` et imprime le libellé avec le code et le motif. Elle ne renvoie rien ; `main` l'appelle huit fois, de la livraison normale à la relance tardive re-signée.

**`rappeler(tache)`** — Cette autre fonction interne vit dans `main`, à la section 6, et joue le coursier qui prévient le client que son dossier est prêt : elle reçoit la tâche terminée, fabrique un corps JSON compact qui contient un identifiant de rappel, l'identifiant de la tâche et son état, le signe avec le secret partagé avec le client à l'instant présent de l'horloge `h3`, puis l'envoie au récepteur du client et imprime l'instant et la réponse. Elle ne renvoie rien ; le gestionnaire l'appelle à 53 secondes, et `main` vérifie que la file du client contient un seul rappel, à l'état succeeded.

```python
"""Étape 45 ter — déclencheurs : webhook signé (HMAC-SHA256), planificateur cron, tâche longue avec reprise."""
import datetime as dt
import hashlib
import hmac
import json
import math
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class Horloge:
    """Horloge simulée, en secondes : aucune heure réelle n'est lue."""

    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def avancer(self, secondes: float) -> None:
        self.t += secondes


# ---------------------------------------------------------------- 1. webhook signé
def hmac_sha256_a_la_main(cle: bytes, message: bytes) -> str:
    """HMAC(K, m) = H((K' ⊕ opad) ∥ H((K' ⊕ ipad) ∥ m)), avec K' = K complétée à 64 octets."""
    bloc = 64
    if len(cle) > bloc:
        cle = hashlib.sha256(cle).digest()
    cle = cle.ljust(bloc, b"\x00")
    ipad = bytes(b ^ 0x36 for b in cle)
    opad = bytes(b ^ 0x5C for b in cle)
    interne = hashlib.sha256(ipad + message).digest()
    return hashlib.sha256(opad + interne).hexdigest()


def message_signe(horodatage: int, corps: bytes) -> bytes:
    """On signe l'horodatage ET les octets bruts du corps : changer l'un ou l'autre casse la signature."""
    return str(horodatage).encode("ascii") + b"." + corps


def signer(secret: bytes, horodatage: int, corps: bytes) -> str:
    signature = hmac.new(secret, message_signe(horodatage, corps), hashlib.sha256).hexdigest()
    return f"t={horodatage},v1={signature}"


def lire_entete(entete: str) -> tuple[int, list[str]]:
    t, signatures = None, []
    for morceau in entete.split(","):
        nom, _, valeur = morceau.partition("=")
        if nom == "t" and valeur.isdigit():
            t = int(valeur)
        elif nom == "v1":
            signatures.append(valeur)
    if t is None or not signatures:
        raise ValueError("en-tête de signature illisible")
    return t, signatures


class RecepteurWebhook:
    """Vérifie, déduplique, met en file et répond tout de suite ; le traitement lourd se fait plus tard."""

    def __init__(self, secrets: list[bytes], horloge: Horloge, tolerance: int = 300) -> None:
        self.secrets, self.horloge, self.tolerance = secrets, horloge, tolerance
        self.vus: dict[str, int] = {}          # identifiant d'événement -> horodatage signé
        self.file: list[dict] = []             # ce qui part vers le journal de l'étape 45 bis

    def purger(self) -> None:
        """Un message d'horodatage t n'est plus acceptable après t + tolérance : son identifiant peut être oublié."""
        limite = self.horloge.t - self.tolerance
        for id_evt in [i for i, t in self.vus.items() if t < limite]:
            del self.vus[id_evt]

    def recevoir(self, entete: str, corps: bytes) -> tuple[int, str]:
        self.purger()
        try:
            t, signatures = lire_entete(entete)
        except ValueError:
            return 400, "en-tête illisible"
        attendues = [hmac.new(s, message_signe(t, corps), hashlib.sha256).hexdigest() for s in self.secrets]
        if not any(hmac.compare_digest(a, s) for a in attendues for s in signatures):
            return 401, "signature invalide"
        if abs(self.horloge.t - t) > self.tolerance:
            return 400, "horodatage hors tolérance"
        evt = json.loads(corps)
        if evt["id"] in self.vus:
            return 200, "déjà reçu"            # 200 : l'émetteur cesse de relancer, rien n'est refait
        self.vus[evt["id"]] = t
        self.file.append(evt)
        return 200, "accepté"


def comparer_naif(a: str, b: str) -> tuple[bool, int]:
    """Comparaison qui s'arrête au premier écart ; renvoie aussi le nombre de caractères comparés (le « temps »)."""
    n = 0
    for x, y in zip(a, b):
        n += 1
        if x != y:
            return False, n
    return len(a) == len(b), n


def comparer_temps_constant(a: str, b: str) -> tuple[bool, int]:
    """Compare toujours tous les caractères : le « temps » ne dépend pas de l'endroit du premier écart."""
    ecart = len(a) ^ len(b)
    for x, y in zip(a, b):
        ecart |= ord(x) ^ ord(y)
    return ecart == 0, len(a)


def attaque_par_temps(oracle, longueur: int = 64, alphabet: str = "0123456789abcdef") -> tuple[str, int]:
    """Devine une signature caractère par caractère en gardant le candidat qui « prend le plus de temps »."""
    trouve, essais = "", 0
    for i in range(longueur):
        meilleur, cout_max = alphabet[0], -1
        for c in alphabet:
            candidat = trouve + c + alphabet[0] * (longueur - i - 1)
            ok, cout = oracle(candidat)
            essais += 1
            if ok:
                return candidat, essais
            if cout > cout_max:
                meilleur, cout_max = c, cout
        trouve += meilleur
    return trouve, essais


# ---------------------------------------------------------------- 2. planificateur de type cron
BORNES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]     # minute, heure, jour, mois, jour de semaine (0 = dimanche)


def analyser_champ(texte: str, lo: int, hi: int) -> set[int]:
    valeurs: set[int] = set()
    for partie in texte.split(","):
        plage, _, pas = partie.partition("/")
        pas_n = int(pas) if pas else 1
        if plage == "*":
            debut, fin = lo, hi
        elif "-" in plage:
            debut, fin = (int(x) for x in plage.split("-"))
        else:
            debut = fin = int(plage)
        if hi == 6 and fin == 7:                             # 7 = dimanche, comme 0
            valeurs.add(0)
            fin = 6
        if pas_n < 1 or debut < lo or fin > hi or debut > fin:
            raise ValueError(f"champ cron invalide : {partie!r}")
        valeurs.update(range(debut, fin + 1, pas_n))
    return valeurs


def analyser_cron(expression: str) -> dict:
    champs = expression.split()
    if len(champs) != 5:
        raise ValueError("une expression cron a 5 champs")
    m, h, j, mo, js = (analyser_champ(c, lo, hi) for c, (lo, hi) in zip(champs, BORNES))
    return {"minutes": m, "heures": h, "jours": j, "mois": mo, "jours_semaine": js,
            "jour_restreint": champs[2] != "*", "semaine_restreinte": champs[4] != "*"}


JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]   # indexés par weekday()


def jour_correspond(c: dict, d: dt.datetime, regle_ou: bool = True) -> bool:
    """Règle historique de cron : si le jour du mois ET le jour de semaine sont restreints, l'un OU l'autre suffit."""
    dans_mois = d.day in c["jours"]
    dans_semaine = (d.weekday() + 1) % 7 in c["jours_semaine"]   # Python : lundi = 0 ; cron : dimanche = 0
    if regle_ou and c["jour_restreint"] and c["semaine_restreinte"]:
        return dans_mois or dans_semaine
    return dans_mois and dans_semaine


def prochaine_execution(expression: str, apres: dt.datetime, horizon_jours: int = 5 * 366,
                        regle_ou: bool = True) -> tuple[dt.datetime, int]:
    """Plus petit instant > apres qui correspond ; saute un mois, un jour ou une heure entière dès qu'ils ne conviennent pas."""
    c = analyser_cron(expression)
    d = apres.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)
    fin, pas = apres + dt.timedelta(days=horizon_jours), 0
    while d <= fin:
        pas += 1
        if d.month not in c["mois"]:
            d = (d.replace(day=1) + dt.timedelta(days=32)).replace(day=1, hour=0, minute=0)
        elif not jour_correspond(c, d, regle_ou):
            d = (d + dt.timedelta(days=1)).replace(hour=0, minute=0)
        elif d.hour not in c["heures"]:
            d = (d + dt.timedelta(hours=1)).replace(minute=0)
        elif d.minute not in c["minutes"]:
            d += dt.timedelta(minutes=1)
        else:
            return d, pas
    raise ValueError(f"aucune exécution de {expression!r} dans les {horizon_jours} jours")


# ---------------------------------------------------------------- 3. tâche longue : sondage, états, reprise
def sonder_jusqu_a(fin_tache: float, base: float, plafond: float | None = None, fixe: bool = False) -> tuple[int, float]:
    """Sondages successifs (attente b, puis 2b, 4b… ou b constant) ; renvoie (nombre de sondages, instant de détection)."""
    t, n, attente = 0.0, 0, base
    while True:
        t += attente
        n += 1
        if t >= fin_tache:
            return n, t
        if not fixe:
            attente = attente * 2 if plafond is None else min(plafond, attente * 2)


TRANSITIONS = {"pending": {"running", "failed"},
               "running": {"succeeded", "failed", "pending"},     # running -> pending : bail expiré, on reprend
               "succeeded": set(), "failed": set()}               # états terminaux : on n'en sort plus


class Panne(Exception):
    """Plantage simulé d'un travailleur."""


@dataclass
class Tache:
    id: str
    elements: list[str]
    etat: str = "pending"
    point_de_reprise: int = 0                  # nombre d'éléments terminés ET enregistrés
    resultats: dict = field(default_factory=dict)
    tentatives: int = 0
    bail_jusqu_a: float = 0.0
    historique: list = field(default_factory=list)


class GestionnaireTaches:
    def __init__(self, horloge: Horloge, duree_bail: float = 30.0, tentatives_max: int = 3, rappel=None) -> None:
        self.horloge, self.duree_bail, self.tentatives_max, self.rappel = horloge, duree_bail, tentatives_max, rappel
        self.taches: dict[str, Tache] = {}
        self.executions = 0                    # appels réels au traitement, reprises comprises

    def soumettre(self, elements: list[str]) -> str:
        id_ = f"tache-{len(self.taches) + 1:04d}"
        self.taches[id_] = Tache(id_, list(elements))
        self.taches[id_].historique.append((self.horloge.t, None, "pending"))
        return id_                             # le client repart tout de suite avec un identifiant

    def transition(self, tache: Tache, nouvel: str) -> None:
        if nouvel not in TRANSITIONS[tache.etat]:
            raise ValueError(f"transition interdite : {tache.etat} -> {nouvel}")
        tache.historique.append((self.horloge.t, tache.etat, nouvel))
        tache.etat = nouvel

    def etat_a(self, id_: str, t: float) -> str:
        """État vu par un client qui interroge à l'instant t : la dernière transition datée au plus t."""
        return [e for (instant, _, e) in self.taches[id_].historique if instant <= t][-1]

    def prendre(self, id_: str) -> Tache:
        tache = self.taches[id_]
        self.transition(tache, "running")
        tache.tentatives += 1
        tache.bail_jusqu_a = self.horloge.t + self.duree_bail
        return tache

    def surveiller(self) -> None:
        """Un travailleur qui ne renouvelle plus son bail est présumé mort : la tâche repart, ou échoue."""
        for tache in self.taches.values():
            if tache.etat == "running" and self.horloge.t > tache.bail_jusqu_a:
                self.transition(tache, "failed" if tache.tentatives >= self.tentatives_max else "pending")

    def executer(self, tache: Tache, traiter, panne_sur: int | None = None, duree_element: float = 2.0) -> None:
        for i in range(tache.point_de_reprise, len(tache.elements)):
            element = tache.elements[i]
            self.horloge.avancer(duree_element)
            tache.resultats[element] = traiter(element)     # idempotent : rangé sous la clé de l'élément
            self.executions += 1
            if panne_sur == i:
                raise Panne(f"panne pendant l'élément {i}, avant le point de reprise")
            tache.point_de_reprise = i + 1                  # point de reprise APRÈS l'effet
            tache.bail_jusqu_a = self.horloge.t + self.duree_bail     # battement de cœur
        self.transition(tache, "succeeded")
        if self.rappel is not None:
            self.rappel(tache)


def main() -> None:
    print("1. HMAC-SHA256 écrit à la main = module hmac")
    for cle in (b"cle-courte", b"k" * 64, b"x" * 100):
        assert hmac_sha256_a_la_main(cle, b"message") == hmac.new(cle, b"message", hashlib.sha256).hexdigest()
    print("  identique pour une clé courte, une clé de 64 octets et une clé de 100 octets")

    print("2. Webhook signé : tolérance de 300 s, déduplication, rotation du secret")
    h = Horloge(1_000_000.0)
    ancien, nouveau = b"secret-webhook-2025", b"secret-webhook-2026"
    recepteur = RecepteurWebhook([nouveau, ancien], h)
    evt = {"id": "evt_0001", "type": "paiement.reussi", "montant_aed": 1250}
    corps = json.dumps(evt, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    entete = signer(nouveau, int(h.t), corps)
    print(f"  en-tête : {entete[:30]}…")
    corps2 = json.dumps({"id": "evt_0002", "type": "paiement.reussi", "montant_aed": 80},
                        separators=(",", ":")).encode("utf-8")
    codes = []

    def envoyer(nom: str, attente: float, fabriquer) -> None:
        h.avancer(attente)                              # l'en-tête est fabriqué à l'instant de l'envoi
        ent, c = fabriquer()
        code, motif = recepteur.recevoir(ent, c)
        codes.append(code)
        print(f"  {nom:<40} -> {code} {motif}")

    envoyer("livraison normale", 0, lambda: (entete, corps))
    envoyer("relance de l'émetteur 30 s après", 30, lambda: (signer(nouveau, int(h.t), corps), corps))
    envoyer("corps modifié (montant 9250)", 0, lambda: (entete, corps.replace(b"1250", b"9250")))
    envoyer("même JSON, ré-sérialisé avec espaces", 0, lambda: (entete, json.dumps(evt).encode("utf-8")))
    envoyer("mauvais secret", 0, lambda: (signer(b"devine", int(h.t), corps), corps))
    envoyer("requête capturée rejouée 10 min après", 600, lambda: (entete, corps))
    envoyer("signée avec l'ancien secret (rotation)", 0, lambda: (signer(ancien, int(h.t), corps2), corps2))
    assert sorted(recepteur.vus) == ["evt_0002"]       # evt_0001 a été purgé : sa signature a expiré
    envoyer("relance tardive re-signée (12 min 30 s)", 120, lambda: (signer(nouveau, int(h.t), corps), corps))
    assert codes == [200, 200, 401, 401, 401, 400, 200, 200]
    assert recepteur.recevoir("v1=abc", corps) == (400, "en-tête illisible")
    ids_en_file = [e["id"] for e in recepteur.file]
    effets = list(dict.fromkeys(ids_en_file))          # déduplication durable, en aval (étape 45 bis)
    print(f"  file = {ids_en_file} ; effets métier après déduplication durable = {effets}")
    assert ids_en_file == ["evt_0001", "evt_0002", "evt_0001"] and effets == ["evt_0001", "evt_0002"]

    print("3. Pourquoi hmac.compare_digest : attaque par mesure du temps sur une comparaison naïve")
    vraie = hmac.new(nouveau, message_signe(1_000_000, corps), hashlib.sha256).hexdigest()
    trouvee, essais = attaque_par_temps(lambda s: comparer_naif(s, vraie))
    print(f"  comparaison naïve : signature retrouvée = {trouvee == vraie} en {essais} essais (≤ 16 × 64 = 1024)")
    assert trouvee == vraie and essais <= 16 * 64
    trouvee, essais = attaque_par_temps(lambda s: comparer_temps_constant(s, vraie))
    print(f"  temps constant : signature retrouvée = {trouvee == vraie} après {essais} essais ; il en faudrait 16^64")
    assert trouvee != vraie and essais == 1024 and hmac.compare_digest(vraie, vraie)

    print("4. Planificateur : prochaine exécution, heure de Dubaï (UTC+4, sans heure d'été)")
    depart = dt.datetime(2026, 11, 13, 17, 50)          # un vendredi, 17 h 50, heure locale
    attendus = {"*/15 9-17 * * 1-5": dt.datetime(2026, 11, 16, 9, 0),
                "0 2 * * *": dt.datetime(2026, 11, 14, 2, 0),
                "30 18 * * 5": dt.datetime(2026, 11, 13, 18, 30),
                "0 8 1 * 1": dt.datetime(2026, 11, 16, 8, 0),
                "0 0 29 2 *": dt.datetime(2028, 2, 29, 0, 0)}
    for expression, attendu in attendus.items():
        suivante, pas = prochaine_execution(expression, depart)
        print(f"  {expression:<18} -> {suivante:%Y-%m-%d %H:%M} ({JOURS[suivante.weekday()]}) en {pas} pas")
        assert suivante == attendu and pas < 500
    avec_et, _ = prochaine_execution("0 8 1 * 1", depart, regle_ou=False)
    print(f"  0 8 1 * 1, si l'on exigeait « le 1er ET un lundi » -> {avec_et:%Y-%m-%d} ({JOURS[avec_et.weekday()]})")
    assert avec_et == dt.datetime(2027, 2, 1, 8, 0)
    try:
        prochaine_execution("0 0 31 2 *", depart)
    except ValueError as e:
        print(f"  0 0 31 2 *         -> ValueError ({e})")
    else:
        raise AssertionError("le 31 février n'existe pas")
    dubai = dt.timezone(dt.timedelta(hours=4))
    neuf_h_utc = dt.datetime(2026, 11, 16, 9, 0, tzinfo=dt.timezone.utc)
    print(f"  « 0 9 * * * » sur un serveur réglé en UTC part à {neuf_h_utc.astimezone(dubai):%H:%M} à Dubaï")
    assert neuf_h_utc.astimezone(dubai).hour == 13

    print("5. Sonder une tâche de 41 s : intervalle fixe ou backoff géométrique (b = 1 s)")
    resultats = {"fixe 2 s": sonder_jusqu_a(41, 2, fixe=True), "fixe 10 s": sonder_jusqu_a(41, 10, fixe=True),
                 "géométrique": sonder_jusqu_a(41, 1), "géométrique, plafond 16 s": sonder_jusqu_a(41, 1, 16)}
    for nom, (n, t) in resultats.items():
        print(f"  {nom:<26} {n:>2} sondages, détection à {t:>4.0f} s, retard {t - 41:>3.0f} s")
    assert resultats == {"fixe 2 s": (21, 42), "fixe 10 s": (5, 50), "géométrique": (6, 63),
                         "géométrique, plafond 16 s": (6, 47)}
    for T in (5, 41, 600, 3600):                       # k = ⌈log2(T/b + 1)⌉ et retard < T + b
        n, t = sonder_jusqu_a(T, 1)
        assert n == math.ceil(math.log2(T + 1)) and t - T < T + 1
    print(f"  une heure : {sonder_jusqu_a(3600, 1)[0]} sondages géométriques, "
          f"{sonder_jusqu_a(3600, 1, 60)[0]} avec un plafond de 60 s, {sonder_jusqu_a(3600, 2, fixe=True)[0]} toutes les 2 s")

    print("6. Tâche longue : panne, bail expiré, reprise au point de reprise, rappel signé")
    h3 = Horloge()
    secret_client = b"secret-rappel-client"
    client = RecepteurWebhook([secret_client], h3)

    def rappeler(tache: Tache) -> None:
        corps_r = json.dumps({"id": f"rappel-{tache.id}", "tache": tache.id, "etat": tache.etat},
                             separators=(",", ":")).encode("utf-8")
        print(f"  t = {h3.t:>4.0f} s  rappel au client -> {client.recevoir(signer(secret_client, int(h3.t), corps_r), corps_r)}")

    g = GestionnaireTaches(h3, duree_bail=30.0, rappel=rappeler)
    dossiers = [f"DOS-{i:03d}" for i in range(10)]
    id_ = g.soumettre(dossiers)
    tache = g.prendre(id_)
    try:
        g.executer(tache, lambda d: d.lower(), panne_sur=6)
    except Panne as e:
        print(f"  t = {h3.t:>4.0f} s  {e} ; point de reprise = {tache.point_de_reprise}")
    h3.t = 31.0
    g.surveiller()
    print(f"  t = {h3.t:>4.0f} s  état vu par le client : {g.etat_a(id_, h3.t)} (bail jusqu'à {tache.bail_jusqu_a:.0f} s)")
    h3.t = 45.0
    g.surveiller()
    print(f"  t = {h3.t:>4.0f} s  bail expiré -> {tache.etat} ; un second travailleur reprend")
    g.executer(g.prendre(id_), lambda d: d.lower())
    sondages = [(t, g.etat_a(id_, t)) for t in (1, 3, 7, 15, 31, 47, 63)]
    print(f"  sondages du client (backoff, plafond 16 s) : {sondages}")
    print(f"  traitements exécutés = {g.executions} pour {len(dossiers)} dossiers ; résultats = {len(tache.resultats)}")
    assert [e for (_, _, e) in tache.historique] == ["pending", "running", "pending", "running", "succeeded"]
    assert g.executions == 11 and len(tache.resultats) == 10 and tache.tentatives == 2 and h3.t == 53.0
    assert sondages[4] == (31, "running") and sondages[-1] == (63, "succeeded") and [e["etat"] for e in client.file] == ["succeeded"]
    try:
        g.transition(tache, "running")
    except ValueError as e:
        print(f"  {e}")
    else:
        raise AssertionError("un état terminal ne doit pas se rouvrir")
    id_mauvais = g.soumettre(["DOS-999"])
    for _ in range(3):
        t_mauvais = g.prendre(id_mauvais)
        try:
            g.executer(t_mauvais, lambda d: d, panne_sur=0)
        except Panne:
            pass
        h3.avancer(31.0)
        g.surveiller()
    print(f"  tâche qui plante à chaque fois : {g.taches[id_mauvais].etat} après {g.taches[id_mauvais].tentatives} tentatives")
    assert g.taches[id_mauvais].etat == "failed" and g.taches[id_mauvais].tentatives == 3

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
…
  livraison normale                        -> 200 accepté
  relance de l'émetteur 30 s après         -> 200 déjà reçu
  corps modifié (montant 9250)             -> 401 signature invalide
…
  requête capturée rejouée 10 min après    -> 400 horodatage hors tolérance
…
  comparaison naïve : signature retrouvée = True en 1011 essais (≤ 16 × 64 = 1024)
…
  0 0 29 2 *         -> 2028-02-29 00:00 (mardi) en 71 pas
  0 8 1 * 1, si l'on exigeait « le 1er ET un lundi » -> 2027-02-01 (lundi)
…
  géométrique, plafond 16 s   6 sondages, détection à   47 s, retard   6 s
  une heure : 12 sondages géométriques, 65 avec un plafond de 60 s, 1800 toutes les 2 s
…
  t =   14 s  panne pendant l'élément 6, avant le point de reprise ; point de reprise = 6
…
  traitements exécutés = 11 pour 10 dossiers ; résultats = 10
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un déclencheur ne se croit pas sur parole. La signature prouve l'origine, la tolérance borne le rejeu, l'identifiant évite le double effet, et l'état d'une tâche longue se lit dans une machine à états qui ne ment que pendant la durée d'un bail.

## Squelette algorithmique

Trois algorithmes : recevoir un webhook, calculer la prochaine exécution d'une expression cron, exécuter une tâche longue avec reprise. Le sondage côté client complète le troisième. Entrées : en-tête et corps bruts ; expression et instant de départ ; liste d'éléments et bail. Sorties : une réponse HTTP et un événement en file ; une date ; un état terminal et des résultats.

```text
ALGORITHME RecevoirWebhook(en-tête, corps brut)
  purger D des identifiants d'horodatage < maintenant − τ
  (t, signatures) ← lire l'en-tête        SI illisible ALORS RETOURNER 400
  SI aucune paire (secret ∈ S, signature reçue) ne vérifie
       ComparerTempsConstant(HMAC(secret, t ∥ "." ∥ corps), signature) ALORS RETOURNER 401
  SI |maintenant − t| > τ ALORS RETOURNER 400
  évt ← désérialiser(corps)                (seulement maintenant)
  SI évt.id ∈ D ALORS RETOURNER 200 « déjà reçu »
  D[évt.id] ← t ; mettre évt dans le journal ; RETOURNER 200 « accepté »

ALGORITHME ProchaineExécution(expression, t₀)
  (M, H, J, O, W) ← analyser(expression)
  d ← t₀ arrondi à la minute + 1 minute
  TANT QUE d ≤ t₀ + horizon FAIRE
      SI mois(d) ∉ O ALORS d ← 1er du mois suivant, 0 h 00
      SINON SI non Jour(d) ALORS d ← lendemain, 0 h 00          (règle OU si J et W restreints)
      SINON SI heure(d) ∉ H ALORS d ← heure suivante, minute 0
      SINON SI minute(d) ∉ M ALORS d ← d + 1 minute
      SINON RETOURNER d
  FIN TANT QUE
  ERREUR « aucune exécution dans l'horizon »

ALGORITHME ExécuterTâche(tâche, travailleur)
  tâche.état ← running ; tâche.tentatives ← tâche.tentatives + 1 ; bail ← maintenant + Δ
  POUR i DE tâche.reprise À n − 1 FAIRE
      résultat[élément i] ← traiter(élément i)      (idempotent : rangé sous la clé de l'élément)
      tâche.reprise ← i + 1 ; bail ← maintenant + Δ    (point de reprise APRÈS l'effet, puis battement)
  FIN POUR
  tâche.état ← succeeded ; envoyer un rappel signé

ALGORITHME Surveiller()                         (exécuté périodiquement)
  POUR CHAQUE tâche running dont le bail est dépassé FAIRE
      SI tâche.tentatives ≥ R ALORS tâche.état ← failed SINON tâche.état ← pending
  FIN POUR

ALGORITHME SonderClient(identifiant, b, D)
  attente ← b
  RÉPÉTER
      attendre attente ; état ← statut(identifiant)
      attente ← min(D, 2 × attente)
  JUSQU'À état ∈ { succeeded, failed }
```

**Complexité :** la réception coûte O(|S| × |corps|) pour les HMAC, plus O(|D|) pour la purge écrite ici par balayage (O(1) amorti avec une file triée par horodatage) ; la mémoire de D est d'environ λ_w × 2τ identifiants. La prochaine exécution coûte au plus quelques sauts par mois, jour et heure de l'horizon, plus au plus 60 pas de minute : quelques dizaines de pas en pratique, 71 pour atteindre un 29 février à quinze mois. Une tâche de n éléments coûte E ≤ n + c m exécutions et n écritures de point de reprise ; la surveillance coûte O(nombre de tâches) par passage. Le sondage coûte ⌈log₂(T/b + 1)⌉ requêtes sans plafond, j + ⌈(T − Wⱼ)/D⌉ avec plafond.

**Du squelette au code :** `RecevoirWebhook` est `RecepteurWebhook.recevoir`, avec `purger`, `lire_entete`, `message_signe` et `hmac.compare_digest` pour la comparaison à temps constant (simulée par `comparer_temps_constant` dans la section 3). `ProchaineExécution` est `prochaine_execution`, appuyée sur `analyser_cron`, `analyser_champ` et `jour_correspond`. `ExécuterTâche` est `GestionnaireTaches.prendre` suivi de `executer`, avec `transition` pour chaque changement d'état et `rappel` pour le rappel signé. `Surveiller` est `surveiller`. `SonderClient` est modélisé par `sonder_jusqu_a` pour le décompte, et par les appels à `etat_a` aux instants 1, 3, 7, 15, 31, 47 et 63 dans la section 6.

## Cas d'usage réels aux Émirats

Les débits, durées, tolérances et volumes ci-dessous sont illustratifs ; les fonctionnalités de produits citées sont celles annoncées par leurs éditeurs, à vérifier dans leur documentation.

### Banque — la notification de paiement d'un prestataire de cartes

Une banque de détail de Dubaï reçoit de son prestataire d'acquisition un webhook à chaque paiement par carte d'un commerçant, signé par HMAC-SHA256 sur l'horodatage et le corps. Le récepteur vérifie la signature sur le corps brut, applique une tolérance de 300 s, met l'événement dans le journal de l'étape 45 bis et répond 200 en quelques millisecondes ; l'agent de rapprochement et l'agent anti-fraude le consomment ensuite. Un jour, une requête capturée sur un environnement de test mal protégé est renvoyée vers l'adresse de production vingt minutes plus tard : la signature est valide, mais l'horodatage dépasse la tolérance, et la requête est refusée (démonstration, point 3). Le prestataire relance par ailleurs pendant des heures en cas de réponse lente, avec une signature neuve à chaque fois : le cache anti-rejeu ne suffit plus, et c'est la déduplication durable par référence de paiement, en aval, qui évite un double crédit. Lors de la rotation annuelle du secret, le récepteur accepte l'ancien et le nouveau pendant une semaine. La banque, supervisée par la CBUAE, journalise chaque refus avec son motif. On suit le taux de 401 et de 400, dont une hausse soudaine signale une attaque ou un secret désynchronisé.

### Crypto — des dépôts annoncés par un fournisseur de nœuds

Une plateforme d'actifs virtuels agréée par la VARA reçoit d'un fournisseur d'infrastructure un webhook à chaque dépôt confirmé sur la chaîne, avec le montant, l'adresse et l'empreinte de la transaction. Un attaquant qui pourrait forger ou rejouer ce webhook ferait créditer un dépôt fictif, puis retirerait les fonds : la signature et la tolérance sont donc la première défense, et la comparaison se fait avec `hmac.compare_digest`, car une comparaison naïve permettrait de reconstituer une signature valide en environ 1 000 requêtes au lieu de 16⁶⁴ (démonstration, point 4). La seconde défense est métier : avant de créditer, l'agent revérifie le dépôt auprès de son propre nœud, et le crédit est idempotent par empreinte de transaction. Sans ces contrôles, le webhook devient un guichet de crédit ouvert à quiconque connaît l'adresse. La VARA attend une traçabilité des opérations ; chaque webhook accepté ou refusé est conservé avec sa signature et son horodatage. On suit le nombre de dépôts annoncés non confirmés par le nœud, avec un objectif de zéro crédit à tort.

### Immobilier — le rafraîchissement nocturne des prix au sqft

Une agence de Dubaï et d'Abu Dhabi recalcule chaque nuit la médiane des prix au sqft par quartier à partir des transactions enregistrées, pour que son agent de conseil ne cite jamais un prix de la semaine dernière. L'expression « 0 2 * * * » doit s'exécuter à 2 h, heure de Dubaï, quand le trafic est au plus bas ; sur un serveur réglé en UTC, la même expression part à 6 h à Dubaï, en pleine reprise d'activité (démonstration, point 5). L'équipe fixe donc explicitement le fuseau du planificateur ; avec Spring, l'annotation `@Scheduled` accepte un attribut `zone`, mais attention, ses expressions cron ont six champs, dont un premier champ pour les secondes. Comme Dubaï n'a pas d'heure d'été, aucun déclenchement n'est sauté ni doublé dans l'année. Le travail lui-même est une tâche longue avec point de reprise par quartier : une panne au milieu ne relance pas les quartiers déjà calculés. On suit l'heure de fin du calcul et l'âge des prix cités par l'agent.

### Assurance — l'analyse par lots de milliers de sinistres

Un assureur auto et santé fait relire chaque nuit par un modèle de langage les 5 000 sinistres déclarés dans la journée, pour signaler les incohérences entre photos, devis et déclaration. Les traitements par lots des fournisseurs de modèles sont des tâches longues : selon la documentation de l'éditeur, l'API Message Batches de Claude reçoit les requêtes, renvoie un identifiant, expose un `processing_status` qui passe à `ended` quand tout est traité, termine la plupart des lots en moins d'une heure et au plus en 24 heures, à moitié prix. L'agent suit le lot par sondage : avec un intervalle qui double depuis 1 s et un plafond de 60 s, une heure de traitement coûte 65 sondages, contre 1 800 avec un sondage toutes les 2 s (démonstration, point 6). Les résultats arrivent dans un ordre quelconque et se rangent par identifiant de requête, jamais par position. Sans tâche longue, l'agent attendrait en bloquant un fil d'exécution pendant une heure, ou appellerait le modèle sinistre par sinistre, au prix fort. On suit la durée des lots, le taux de requêtes en erreur et le coût par sinistre relu.

### RH — un fichier de salaires qui doit partir même après une panne

Un cabinet RH multi-émirats prépare chaque mois, pour ses clients, les fichiers de salaires du système de protection des salaires (WPS). Le planificateur lance la préparation le 25 du mois à 6 h ; la tâche contrôle 2 000 lignes de salaires avec un agent, par paquets de 100, et enregistre un point de reprise après chaque paquet. Un redéploiement interrompt le travailleur au paquet 14 : le bail expire, un second travailleur reprend au paquet 14, et seuls 100 contrôles sont refaits au lieu de 1 400 (démonstration, point 8, avec m = 100). Les contrôles sont idempotents, rangés par identifiant de salarié, si bien que la ligne contrôlée deux fois ne produit qu'un résultat. Si la tâche échoue trois fois, elle passe en failed et une personne est alertée, au lieu de boucler jusqu'à l'heure limite de dépôt. On suit l'heure de fin de préparation et le nombre de reprises par mois.

### Secteur public — une démarche longue suivie par l'usager

Une entité de services publics en ligne, accessible par UAE Pass, instruit des demandes qui durent plusieurs jours : collecte de pièces, contrôle, validation par un agent humain. Pour l'usager, la demande est une tâche longue avec un identifiant, et son espace personnel affiche l'état, en arabe et en anglais, à partir de la même machine à états que celle du programme : en attente, en cours, acceptée, refusée. L'application mobile sonde avec un intervalle qui double jusqu'à un plafond, puis reçoit une notification quand l'état devient terminal ; un état terminal ne se rouvre pas, et une nouvelle démarche crée une nouvelle tâche. Sans machine à états, deux agents pourraient marquer la même demande acceptée puis refusée, et l'usager verrait des messages contradictoires. Les notifications ne contiennent que l'identifiant et l'état, conformément à la minimisation des données de la PDPL ; le détail se consulte après authentification. On suit le délai d'instruction et la part des usagers qui rappellent le centre de contact pour connaître l'état de leur demande.

## Pièges et limites

- **Vérifier la signature sur un corps re-sérialisé.** Le framework a déjà transformé le JSON, et des octets différents donnent une signature différente : on lit le corps brut, on vérifie, puis on désérialise.
- **Comparer les signatures avec `==`.** La comparaison s'arrête au premier écart et fuit le préfixe commun ; on utilise `hmac.compare_digest`, ou l'équivalent à temps constant du langage (`MessageDigest.isEqual` en Java).
- **Confondre anti-rejeu et idempotence.** Le cache anti-rejeu dure τ secondes et protège contre un attaquant ; les relances légitimes d'un émetteur s'étalent sur des heures, avec des signatures neuves, et seule une déduplication durable par identifiant métier les absorbe.
- **Traiter avant de répondre.** Un récepteur qui appelle un LLM avant de répondre dépasse le délai de l'émetteur, qui relance, et chaque relance relance l'appel ; on met en file, on répond 200, on traite ensuite.
- **Un bail sans délai global.** Un travailleur bloqué qui continue d'émettre des battements de cœur sans avancer garde la tâche indéfiniment ; on ajoute une échéance globale, et un jeton de version (*fencing token*) pour qu'un travailleur déclaré mort ne puisse plus écrire de résultat.

### Exercice feuille blanche

1. Sans regarder le code, écrire `signer`, `lire_entete` et `RecepteurWebhook.recevoir` (signature, tolérance, déduplication), puis vérifier qu'une requête signée il y a 301 s est refusée et qu'une requête signée il y a 299 s est acceptée.
2. Prédire, puis vérifier avec `sonder_jusqu_a` : pour une tâche de 100 s, combien de sondages font un intervalle qui double depuis 1 s, puis le même avec un plafond de 10 s ? (Réponse : ⌈log₂ 101⌉ = 7 sondages, détection à 127 s ; avec plafond, j = 4, W₄ = 15, puis 4 + ⌈85/10⌉ = 13 sondages, détection à 105 s.)
3. Trouver le bug : une variante de `executer` écrit `tache.point_de_reprise = i + 1` **avant** `traiter(element)`. Que devient l'élément en cours si la panne survient entre les deux lignes ? (Réponse : il est sauté à la reprise et n'est jamais traité.)

## Pour aller plus loin

Les moteurs d'exécution durable (Temporal, AWS Step Functions, ou Quartz côté Java, cités comme exemples du marché) fournissent tout ce que ce fichier construit à la main : minuteries persistantes, états, reprises, baux, rappels. On peut s'en passer avec une table `taches(id, etat, point_de_reprise, bail_jusqu_a, tentatives)` et une requête `UPDATE … WHERE etat = 'pending' … FOR UPDATE SKIP LOCKED` pour que deux travailleurs ne prennent pas la même tâche. Le *jitter* de l'étape 12 s'ajoute au sondage quand des milliers de clients suivent la même tâche. Les signatures asymétriques (Ed25519) évitent de partager un secret : le récepteur ne détient que la clé publique de l'émetteur. La spécification ouverte Standard Webhooks décrit un schéma de signature commun à plusieurs fournisseurs ; ses détails se vérifient dans son texte. L'étape 46 passe des déclencheurs aux outils : le protocole MCP, qui standardise la façon dont un agent découvre et appelle des outils distants.

> Étape 45 ter du parcours · Prérequis : [Journal d'événements partitionné](<45b-Journal-d-Evenements-Partitionne.md>) · Suite : [MCP : définitions fondamentales](<../09-MCP/46-MCP-Definitions-Fondamentaux.md>)
