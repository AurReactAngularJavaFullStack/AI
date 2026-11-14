# Palier 08 — Planification DAG : ordonner, paralléliser, chemin critique

> Palier 08 sur 12 · Précédent : [Palier 07 — Recherche hybride](<../07-Recherche-Hybride/README.md>) · Suivant : [Palier 09 — Garde-fous](<../09-Garde-Fous/README.md>) · Leçons à relire : [Étape 37 bis — Planifier](<../../07-Planification/37b-Planification-Definitions-Fondamentaux.md>) · [Étape 38 — MDP et Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>) · [Étape 40 bis — Orchestration](<../../08-Orchestration/40b-Orchestration-Definitions-Fondamentaux.md>) · [Étape 42 — Graphes, vagues et chemin critique](<../../08-Orchestration/42-Orchestration-Graphes.md>) · [Étape 43 — DAG et tri topologique](<../../08-Orchestration/43-Fondements-Orchestration-et-DAG.md>) · [Étape 44 — Kahn](<../../08-Orchestration/44-Tri-Topologique-Kahn.md>) · [Étape 45 — Détection de cycle](<../../08-Orchestration/45-Detection-de-Cycle-DFS.md>) · Démonstrations : [09 — Équation de Bellman](<../../Demonstrations/06-Decision/09_equation_bellman.md>)

## Où en est l'agent

Après sept paliers, l'agent sait parler au modèle (01), valider (02), calculer juste (03), appeler ses outils derrière une porte (04), boucler sans fin impossible (05), se souvenir (06) et chercher dans les règles (07). Sa boucle ReAct décide **une action à la fois** : elle agit, observe, puis choisit la suivante. C'est souple, mais l'agent ne voit jamais le dossier en entier : il ne sait pas ce qui peut partir en parallèle, ni combien de temps prendra le tout, ni si l'enchaînement qu'il improvise est seulement possible.

Ce palier ajoute l'autre façon de travailler, **planifier puis exécuter** (étape 37 bis) : on décompose d'abord la demande en tâches, chacune avec sa durée et ses prérequis, puis on exécute ce plan. Un plan n'est utile que si l'on peut le vérifier et l'ordonner sans modèle, avec du code ordinaire : c'est le rôle du module `agent/planification.py`.

```text
demande du client C-6 : « mon dossier de crédit est-il recevable ? »
   │
   ▼  DÉCOMPOSER   le modèle propose un plan structuré (ou le code fixe un workflow)
   ★ agent/planification.py ★                                             palier 08
   │   Tache(nom, durée, prérequis)
   │   _graphe ─► tri_topologique (Kahn) ─► vagues ─► calendrier ─► chemin_critique
   │   doublon, prérequis inconnu ou cycle : ValueError, le plan repart au modèle
   ▼  EXÉCUTER vague par vague, chaque tâche par la porte des outils        palier 04
   vague 1 : lire_memoire (06)   rechercher_regles (07)   verifier_identite (03)
   vague 2 : calculer_mensualite (03)
   vague 3 : calculer_ratio (03)   convertir_usd (03)
   vague 4 : evaluer_risque (09)
   vague 5 : rediger_reponse (modèle, 01 et 05)
```

Dans la boucle percevoir → décider → agir → observer, la planification se place **entre décider et agir** : le modèle décide d'un plan, le code le valide et l'ordonne, puis les outils agissent tâche par tâche. Un plan refusé (un cycle, une tâche en double, un prérequis qui n'existe pas) repart vers le modèle avec un message d'erreur précis, exactement comme un argument invalide au palier 02.

**Ce module est NOUVEAU par rapport à l'étape 77.** Le programme de 77 est un agent purement ReAct, sans planification. Les étapes 42 à 45 du cours expliquent les graphes de tâches, Kahn et le chemin critique sur des pipelines d'agents ; ce palier les applique à un cas métier : la décomposition d'un dossier de crédit à Dubaï en huit tâches dépendantes (durées illustratives, en secondes simulées).

| Tâche | Durée (s) | Prérequis | Qui la réalise |
| --- | --- | --- | --- |
| `verifier_identite` | 1,5 | aucun | format de l'Emirates ID (palier 03), liste de sanctions |
| `lire_memoire` | 0,5 | aucun | salaire et crédits en cours (palier 06) |
| `rechercher_regles` | 2,0 | aucun | recherche hybride sur les règles CBUAE (palier 07) |
| `calculer_mensualite` | 0,8 | `lire_memoire` | outil `mensualite` (palier 03) |
| `calculer_ratio` | 0,6 | `calculer_mensualite` | outil `ratio_endettement` (palier 03) |
| `convertir_usd` | 0,4 | `calculer_mensualite` | conversion à 3,6725 AED pour 1 USD (palier 03) |
| `evaluer_risque` | 1,2 | `verifier_identite`, `calculer_ratio`, `rechercher_regles` | score de risque (palier 09) |
| `rediger_reponse` | 2,5 | `evaluer_risque`, `convertir_usd` | le modèle, dans la boucle (paliers 01 et 05) |

Exécuté tâche après tâche, le dossier prend 9,5 s. Planifié, il en prend 5,7 : c'est tout l'enjeu du palier. Au palier 12, l'agent assemblé restera ReAct ; la planification y est une brique à part, que l'on utilise quand le dossier a une forme connue d'avance.

## Ce que tu vas coder

- `Tache` : une tâche du plan (nom, durée, prérequis), qui refuse un nom vide et une durée négative.
- `tri_topologique(taches)` : l'ordre d'exécution de Kahn, unique grâce au départage alphabétique, et une `ValueError` qui **nomme** le cycle quand il y en a un.
- `vagues(taches)` : les groupes de tâches qui peuvent partir en même temps.
- `calendrier(taches)` : la date de début et de fin au plus tôt de chaque tâche.
- `chemin_critique(taches)` : la durée minimale du plan et la chaîne de tâches qui la fixe.
- `duree_par_vagues(taches)` : la durée d'une exécution synchronisée vague par vague, toujours au moins égale au chemin critique.
- Deux fonctions privées sont proposées dans le squelette : `_graphe` (successeurs, degrés entrants, contrôles) et `_nommer_cycle`. `dossier_credit()` est fourni : ce sont les données du tableau ci-dessus.

## Rappel de cours

Un plan est un graphe orienté G = (V, E) : les nœuds sont les tâches, et un arc u → v signifie « u doit finir avant que v commence », c'est-à-dire « u est un prérequis de v ». Un plan exécutable est un graphe **sans cycle** (DAG). L'algorithme de Kahn compte, pour chaque tâche, ses prérequis non encore traités :

$$
d_{\mathrm{in}}(v) = \sum_{u \in V} A_{u,v} = \lvert \text{prérequis}(v) \rvert
$$

Il part des tâches sans prérequis, les sources :

$$
S_0 = \{\, v \in V \mid d_{\mathrm{in}}(v) = 0 \,\}
$$

À chaque tâche u qui sort, il met à jour ses successeurs :

$$
d_{\mathrm{in}}(v) \leftarrow d_{\mathrm{in}}(v) - 1 \quad \text{pour chaque successeur } v \text{ de } u
$$

et le plan est valide si et seulement si toutes les tâches sortent :

$$
\lvert \text{ordre} \rvert = \lvert V \rvert \iff G \text{ est un DAG}
$$

Le niveau d'une tâche, c'est-à-dire le numéro de sa vague à partir de 0, est la longueur en arcs du plus long chemin qui mène à elle :

$$
\text{niveau}(v) = \begin{cases} 0 & \text{si } v \text{ n'a pas de prérequis} \\ 1 + \max_{u \to v} \text{niveau}(u) & \text{sinon} \end{cases}
$$

Avec des exécutants en nombre illimité, une tâche démarre dès que tous ses prérequis sont finis :

$$
\text{début}(v) = \max_{u \to v} \text{fin}(u) \quad (0 \text{ sans prérequis}) \qquad \text{fin}(v) = \text{début}(v) + d(v)
$$

La durée minimale du plan est la plus grande date de fin, la longueur du chemin critique :

$$
T_{\mathrm{CP}} = \max_{v \in V} \text{fin}(v)
$$

Et les trois durées se comparent toujours dans cet ordre :

$$
T_{\mathrm{seq}} = \sum_{v \in V} d(v) \;\ge\; T_{\mathrm{vagues}} = \sum_{W} \max_{v \in W} d(v) \;\ge\; T_{\mathrm{CP}}
$$

### Les symboles, un par un

$$
G = (V, E)
$$

Le plan : V est l'ensemble des tâches, E l'ensemble des dépendances.

$$
u \to v
$$

Un arc : u est un prérequis de v. Dans le code, `u in tache_v.prerequis`, et `v in succ[u]`.

$$
A_{u,v}
$$

Le coefficient de la matrice d'adjacence, 1 si l'arc u → v existe ; le code ne construit jamais la matrice, il lit directement les prérequis.

$$
d_{\mathrm{in}}(v)
$$

Le degré entrant restant : le nombre de prérequis de v pas encore sortis, `entrant[v]`.

$$
S_0
$$

Les sources, tâches sans prérequis, qui peuvent partir tout de suite : le contenu initial du tas `pretes`.

$$
d(v)
$$

La durée de la tâche v, `Tache.duree`, en secondes simulées.

$$
\text{début}(v),\; \text{fin}(v)
$$

Les dates au plus tôt de v, le couple rendu par `calendrier` pour cette tâche.

$$
\text{niveau}(v)
$$

Le numéro de la vague de v, à partir de 0 : la démo affiche « vague 1 » pour le niveau 0.

$$
W
$$

Une vague : l'ensemble des tâches de même niveau. Aucune ne dépend d'une autre de la même vague.

$$
T_{\mathrm{seq}}
$$

La durée si l'on exécute les tâches une par une : la somme des durées, 9,5 s pour le dossier.

$$
T_{\mathrm{vagues}}
$$

La durée si chaque vague attend la plus lente de la vague précédente : 7,1 s, `duree_par_vagues`.

$$
T_{\mathrm{CP}}
$$

La durée du chemin critique, la vraie durée minimale avec assez d'exécutants : 5,7 s, `chemin_critique`.

**Pourquoi Kahn est juste (étape 44).** À tout moment, `entrant[v]` vaut le nombre de prérequis de v pas encore sortis, et une tâche entre dans le tas au moment exact où ce nombre tombe à 0, donc après tous ses prérequis : l'ordre produit respecte chaque arc. Si le tas se vide alors qu'il reste des tâches, chacune d'elles a encore au moins un prérequis **parmi les restantes**. En remontant de prérequis en prérequis, on ne peut donc jamais s'arrêter, et comme il n'y a qu'un nombre fini de tâches, on finit par repasser par une tâche déjà vue : c'est un cycle. Cette remontée est exactement ce que fait `_nommer_cycle` pour l'afficher.

**Pourquoi le départage alphabétique.** Quand plusieurs tâches sont prêtes, Kahn peut prendre n'importe laquelle : il existe en général plusieurs ordres valides. Prendre toujours le plus petit nom, grâce à un tas binaire (`heapq`), rend l'ordre **unique**, donc reproductible et testable.

**Pourquoi les vagues surestiment.** Prenons un chemin de durée maximale v₁ → v₂ → … → vₚ. Le niveau croît strictement le long d'un arc, donc ses tâches sont dans des vagues toutes différentes, et chaque vague qui en contient une a un maximum au moins égal à sa durée. En additionnant, T_vagues ≥ T_CP. L'égalité n'a lieu que si les tâches les plus lentes de chaque vague se suivent sur un même chemin. De même, le maximum d'une vague est au plus la somme de ses durées, d'où T_seq ≥ T_vagues. Pour le dossier de crédit :

$$
T_{\mathrm{seq}} = 9{,}5 \;\ge\; T_{\mathrm{vagues}} = 7{,}1 \;\ge\; T_{\mathrm{CP}} = 5{,}7
$$

**Le lien avec Bellman.** fin(v) se calcule à partir des fins de ses prérequis, déjà connues si l'on suit l'ordre topologique : c'est de la programmation dynamique. La plus longue chaîne qui finit en v prolonge la plus longue chaîne qui finit en l'un de ses prérequis ; c'est le principe d'optimalité de l'équation de Bellman (étape 38), avec un maximum sur les prérequis à la place d'une espérance sur les états suivants.

## Spécification

Toutes les valeurs ci-dessous sont reprises par `tests/test_08_planification.py`.

### Tache

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Tache.__post_init__()`** — Cette méthode doit jouer le contrôleur qui tamponne chaque fiche de travail avant qu'elle n'entre au planning, sachant qu'une fois tamponnée la fiche ne changera plus : elle ne reçoit que la tâche que la dataclass gelée vient de construire avec son nom, sa durée et ses prérequis, et doit lever `ValueError` si le nom est vide ou si la durée est négative, une durée nulle restant permise. Elle doit aussi ranger les prérequis en tuple, sans doublon et dans l'ordre de leur première apparition, même s'ils ont été donnés sous forme de liste ; elle ne renvoie rien, et `Tache("v", 1, ("a", "a", "z"))` doit ainsi avoir pour prérequis `("a", "z")`, tandis que `Tache("a", -1.0)` et `Tache("", 1.0)` sont refusées.

```python
# [extrait] spécification
@dataclass(frozen=True)
class Tache:
    nom: str
    duree: float
    prerequis: tuple[str, ...] = ()

    def __post_init__(self) -> None: ...
```

Une classe de données **gelée** : une fois créée, une tâche ne change plus, ce qui permet de la partager sans risque entre le plan, le calendrier et les tests. `__post_init__` lève `ValueError` si le nom est vide ou si la durée est négative ; une durée nulle est permise (une tâche instantanée, comme un simple contrôle). Les prérequis peuvent être donnés sous forme de liste : ils sont rangés en tuple, sans doublon, dans l'ordre de leur première apparition (un plan écrit par un modèle répète parfois une dépendance).

**Exemple chiffré.** `Tache("calculer_ratio", 0.6, ["calculer_mensualite"])` a pour prérequis `("calculer_mensualite",)`, et `tri_topologique([t, Tache("calculer_mensualite", 0)])` vaut `["calculer_mensualite", "calculer_ratio"]` : 0 prérequis pour la mensualité, qui sort d'abord, puis le ratio. `Tache("a", -1.0)` et `Tache("", 1.0)` lèvent `ValueError`. `Tache("v", 1, ("a", "a", "z")).prerequis` vaut `("a", "z")`. Tests : `TestTache.test_creation`, `TestTache.test_entrees_invalides` et `TestTriTopologique.test_prerequis_inconnu_et_doublon`.

### tri_topologique

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tri_topologique(taches)`** — Cette fonction doit être le chef de chantier qui fixe l'ordre de passage des corps de métier, sans jamais faire entrer un artisan avant ceux dont il dépend : elle reçoit la liste des tâches et renvoie la liste de leurs noms dans l'ordre de Kahn, en prenant toujours, parmi les tâches prêtes, la plus petite par ordre alphabétique, ce qui rend l'ordre unique. Elle lève `ValueError` pour une tâche en double, un prérequis inconnu ou un cycle, ce dernier nommé dans le sens des arcs à partir de son plus petit nom, comme « cycle détecté : a → b → c → a », et renvoie `[]` pour un plan vide. Le dossier de crédit doit commencer par `lire_memoire` et `calculer_mensualite` et finir par `rediger_reponse`, et les tâches c, b et a, où a attend c, doivent sortir dans l'ordre b, c, a.

```python
# [extrait] spécification
def tri_topologique(taches: list[Tache]) -> list[str]: ...
```

Rend l'ordre de Kahn, en prenant toujours, parmi les tâches prêtes, la plus petite par ordre alphabétique. Lève `ValueError` pour une tâche en double, pour un prérequis qui ne correspond à aucune tâche, et pour un cycle, avec le message `cycle détecté : a → b → c → a` : le cycle commence et finit par son plus petit nom, et se lit dans le sens des arcs. Un plan vide donne `[]`.

**Exemple chiffré, Kahn pas à pas sur le dossier de crédit.** Les degrés entrants de départ sont 0 pour `verifier_identite`, `lire_memoire` et `rechercher_regles`, 1 pour `calculer_mensualite`, `calculer_ratio` et `convertir_usd`, 3 pour `evaluer_risque` et 2 pour `rediger_reponse`.

| Pas | Tâche sortie | Degrés qui baissent | Tâches prêtes après le pas |
| --- | --- | --- | --- |
| départ | aucune | aucun | `lire_memoire`, `rechercher_regles`, `verifier_identite` |
| 1 | `lire_memoire` | `calculer_mensualite` 1 → 0 | `calculer_mensualite`, `rechercher_regles`, `verifier_identite` |
| 2 | `calculer_mensualite` | `calculer_ratio` 1 → 0, `convertir_usd` 1 → 0 | `calculer_ratio`, `convertir_usd`, `rechercher_regles`, `verifier_identite` |
| 3 | `calculer_ratio` | `evaluer_risque` 3 → 2 | `convertir_usd`, `rechercher_regles`, `verifier_identite` |
| 4 | `convertir_usd` | `rediger_reponse` 2 → 1 | `rechercher_regles`, `verifier_identite` |
| 5 | `rechercher_regles` | `evaluer_risque` 2 → 1 | `verifier_identite` |
| 6 | `verifier_identite` | `evaluer_risque` 1 → 0 | `evaluer_risque` |
| 7 | `evaluer_risque` | `rediger_reponse` 1 → 0 | `rediger_reponse` |
| 8 | `rediger_reponse` | aucun | aucune |

L'ordre est donc `["lire_memoire", "calculer_mensualite", "calculer_ratio", "convertir_usd", "rechercher_regles", "verifier_identite", "evaluer_risque", "rediger_reponse"]` : 8 tâches sorties sur 8, le plan est valide. Au pas 2, `calculer_mensualite` passe avant `rechercher_regles` parce que « c » précède « r ».

**Exemple chiffré, le départage.** Avec `[Tache("c", 1), Tache("b", 1), Tache("a", 1, ("c",))]`, les tâches prêtes au départ sont b et c (a attend c) : b sort, puis c, qui libère a. Résultat : `["b", "c", "a"]`, alors que a est le plus petit nom : un prérequis passe toujours avant l'ordre alphabétique.

**Exemple chiffré, le cycle.** Avec a ← c, b ← a, c ← b (a attend c, b attend a, c attend b), d ← c et e sans prérequis : seule e sort, et il reste a, b, c, d. On part du plus petit, a ; son prérequis restant est c ; celui de c est b ; celui de b est a, déjà vu. La remontée a ← c ← b ← a, remise dans le sens des arcs et commencée par le plus petit nom, donne le message `cycle détecté : a → b → c → a` ; d, bloqué **derrière** le cycle, n'en fait pas partie. Une tâche qui s'attend elle-même donne `cycle détecté : x → x`.

**Exemple chiffré, un prérequis répété.** Avec `[Tache("a", 1), Tache("z", 5), Tache("v", 1, ("a", "a", "z"))]`, v a deux prérequis distincts, a et z, donc un degré entrant de 2. a sort : 2 → 1 ; z sort : 1 → 0 ; v sort en dernier. Résultat : `["a", "z", "v"]`. Si l'on gardait le doublon dans les successeurs de a tout en comptant 2 prérequis, la sortie de a ferait deux décréments, 2 → 1 → 0, et v partirait **avant** z : c'est pourquoi `Tache` dédoublonne ses prérequis. Tests : `TestTriTopologique` (4 tests).

### vagues

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`vagues(taches)`** — Cette fonction doit regrouper les équipes qui peuvent partir ensemble, comme un régisseur qui fait monter sur scène, vague après vague, tous les figurants dont l'entrée ne dépend plus de personne : elle reçoit la liste des tâches, valide d'abord le plan par `tri_topologique`, avec les mêmes erreurs, puis renvoie la liste des vagues, chacune triée par nom, la vague d'indice 0 contenant les sources et chaque tâche se trouvant dans la vague de son niveau. Un plan vide donne `[]` ; le dossier de crédit doit donner cinq vagues, de `lire_memoire`, `rechercher_regles` et `verifier_identite` jusqu'à `rediger_reponse` seule, et deux tâches b et a sans prérequis une seule vague `["a", "b"]`.

```python
# [extrait] spécification
def vagues(taches: list[Tache]) -> list[list[str]]: ...
```

Rend la liste des vagues, chacune triée par nom : la vague d'indice 0 contient les sources, et une tâche est dans la vague d'indice niveau(v). Valide d'abord le plan par `tri_topologique` (mêmes erreurs). Un plan vide donne `[]`.

**Exemple chiffré.** En suivant l'ordre de Kahn : `lire_memoire`, `rechercher_regles` et `verifier_identite` sont au niveau 0 ; `calculer_mensualite` au niveau 1 ; `calculer_ratio` et `convertir_usd` au niveau 2 ; `evaluer_risque` au niveau 1 + max(0, 2, 0) = 3 ; `rediger_reponse` au niveau 1 + max(3, 2) = 4. D'où `[["lire_memoire", "rechercher_regles", "verifier_identite"], ["calculer_mensualite"], ["calculer_ratio", "convertir_usd"], ["evaluer_risque"], ["rediger_reponse"]]`. `vagues([Tache("b", 1), Tache("a", 1)])` vaut `[["a", "b"]]`. Tests : `TestVagues.test_dossier_de_credit` et `TestVagues.test_cas_limites`.

### calendrier

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`calendrier(taches)`** — Cette fonction doit tenir l'agenda d'un atelier qui disposerait d'autant d'ouvriers qu'il le faut, si bien que chaque tâche démarre dès que son dernier prérequis est fini : elle reçoit la liste des tâches et renvoie un dictionnaire qui associe à chaque nom le couple (début, fin) au plus tôt, en parcourant l'ordre topologique pour que les fins des prérequis soient toujours déjà connues. Une tâche sans prérequis démarre à 0 ; sur le dossier de crédit, `evaluer_risque` attend le plus tardif de ses trois prérequis et démarre à 2,0 pour finir à 3,2, et `rediger_reponse` finit à 5,7.

```python
# [extrait] spécification
def calendrier(taches: list[Tache]) -> dict[str, tuple[float, float]]: ...
```

Rend, pour chaque tâche, le couple (début, fin) au plus tôt, en supposant assez d'exécutants pour lancer en même temps toutes les tâches prêtes. Parcourt l'ordre topologique, si bien que les fins des prérequis sont toujours déjà calculées.

**Exemple chiffré.**

| Tâche | Fins des prérequis | Début | Durée | Fin |
| --- | --- | --- | --- | --- |
| `lire_memoire` | aucune | 0,0 | 0,5 | 0,5 |
| `calculer_mensualite` | 0,5 | 0,5 | 0,8 | 1,3 |
| `calculer_ratio` | 1,3 | 1,3 | 0,6 | 1,9 |
| `convertir_usd` | 1,3 | 1,3 | 0,4 | 1,7 |
| `rechercher_regles` | aucune | 0,0 | 2,0 | 2,0 |
| `verifier_identite` | aucune | 0,0 | 1,5 | 1,5 |
| `evaluer_risque` | 1,5 ; 1,9 ; 2,0 | 2,0 | 1,2 | 3,2 |
| `rediger_reponse` | 3,2 ; 1,7 | 3,2 | 2,5 | 5,7 |

`evaluer_risque` attend le plus tardif de ses trois prérequis, la recherche des règles, et démarre à max(1,5 ; 1,9 ; 2,0) = 2,0. Test : `TestCheminCritique.test_calendrier_au_plus_tot`.

### chemin_critique

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`chemin_critique(taches)`** — Cette fonction doit être l'enquêteur qui, sur un chantier terminé, remonte le fil des retards pour désigner la chaîne de tâches qui a fixé la date de livraison : elle reçoit la liste des tâches et renvoie le couple formé de la durée minimale du plan et de la liste des tâches de ce chemin, dans l'ordre d'exécution. Elle part de la tâche qui finit le plus tard, remonte à chaque pas vers le prérequis qui finit le plus tard, les égalités étant départagées par le plus petit nom, jusqu'à une tâche sans prérequis ; un plan vide donne `(0.0, [])`. Le dossier de crédit doit donner 5,7 s par `rechercher_regles`, `evaluer_risque` et `rediger_reponse`, et une tâche seule de 4 s le couple `(4.0, ["seule"])`.

```python
# [extrait] spécification
def chemin_critique(taches: list[Tache]) -> tuple[float, list[str]]: ...
```

Rend la durée minimale du plan et la chaîne de tâches qui la réalise, dans l'ordre d'exécution. On part de la tâche qui finit le plus tard (égalité : le plus petit nom), puis on remonte, à chaque pas, vers le prérequis qui finit le plus tard (égalité : le plus petit nom), jusqu'à une tâche sans prérequis. Un plan vide donne `(0.0, [])`.

**Exemple chiffré.** `rediger_reponse` finit le plus tard, à 5,7. Ses prérequis finissent à 3,2 (`evaluer_risque`) et 1,7 (`convertir_usd`) : on remonte vers `evaluer_risque`. Les siens finissent à 1,5, 1,9 et 2,0 : on remonte vers `rechercher_regles`, qui n'a pas de prérequis. Le chemin, remis à l'endroit, est `["rechercher_regles", "evaluer_risque", "rediger_reponse"]` :

$$
T_{\mathrm{CP}} = 2{,}0 + 1{,}2 + 2{,}5 = 5{,}7 \text{ s}
$$

Une tâche seule de 4 s donne `(4.0, ["seule"])` ; `Tache("a", 0)` seule donne une durée 0 et le chemin `["a"]`. Tests : `TestCheminCritique.test_chemin_et_duree`, `TestCheminCritique.test_plan_vide_et_tache_seule` et `TestTache.test_entrees_invalides`.

### duree_par_vagues

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`duree_par_vagues(taches)`** — Cette fonction doit chronométrer un atelier trop discipliné, où personne ne commence la vague suivante avant que le plus lent de la vague en cours ait posé ses outils : elle reçoit la liste des tâches et renvoie la somme, sur les vagues, de la plus grande durée de chaque vague. Sur le dossier de crédit, elle doit donner 2,0 + 0,8 + 0,6 + 1,2 + 2,5 = 7,1 s, mieux que les 9,5 s du séquentiel mais moins bien que les 5,7 s du chemin critique, puisque `calculer_mensualite` y attend inutilement la fin de `rechercher_regles`.

```python
# [extrait] spécification
def duree_par_vagues(taches: list[Tache]) -> float: ...
```

Rend la somme, sur les vagues, de la plus grande durée de chaque vague : la durée d'une exécution où aucune tâche d'une vague ne démarre avant la fin de toute la vague précédente.

**Exemple chiffré.** Les maxima des cinq vagues valent max(0,5 ; 2,0 ; 1,5) = 2,0, puis 0,8, max(0,6 ; 0,4) = 0,6, puis 1,2 et 2,5 :

$$
T_{\mathrm{vagues}} = 2{,}0 + 0{,}8 + 0{,}6 + 1{,}2 + 2{,}5 = 7{,}1 \text{ s}
$$

C'est mieux que les 9,5 s du séquentiel (1,5 + 0,5 + 2,0 + 0,8 + 0,6 + 0,4 + 1,2 + 2,5), mais moins bien que les 5,7 s du chemin critique : `calculer_mensualite` attend inutilement la fin de `rechercher_regles`, dont il ne dépend pas. Le parallélisme du chemin critique fait gagner 1 − 5,7 / 9,5 = 40 % sur le séquentiel. Test : `TestCheminCritique.test_sequentiel_vagues_critique`.

### dossier_credit

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`dossier_credit()`** — Cette fonction, fournie dans le squelette, joue le rôle du classeur de référence qu'un conseiller ouvre au début de chaque dossier de crédit : elle ne reçoit rien et renvoie la liste des 8 tâches du tableau de la section « Où en est l'agent », dans cet ordre, de `verifier_identite`, longue de 1,5 s, à `rediger_reponse`, longue de 2,5 s, chacune avec ses prérequis. Comme elle crée des objets `Tache`, elle ne fonctionne qu'une fois `Tache.__post_init__` écrit ; c'est sur elle que reposent les exemples chiffrés des tests et de la démo.

```python
# [extrait] spécification
def dossier_credit() -> list[Tache]: ...
```

Fournie dans le squelette : rend les 8 tâches du tableau de la section « Où en est l'agent », dans cet ordre. Elle ne fonctionne qu'une fois `Tache.__post_init__` écrit, puisqu'elle crée des `Tache`.

## Squelette algorithmique

```text
ALGORITHME TriTopologique (Kahn, départage alphabétique)
ENTRÉES : tâches, chacune (nom, durée ≥ 0, prérequis)
SORTIE  : ordre d'exécution, ou ERREUR qui nomme un cycle

  par_nom ← dictionnaire vide
  POUR CHAQUE tâche t FAIRE
      SI t.nom DANS par_nom ALORS ERREUR « tâche en double »
      par_nom[t.nom] ← t
  succ[n] ← liste vide POUR CHAQUE nom n
  POUR CHAQUE tâche t, POUR CHAQUE prérequis p DE t FAIRE
      SI p n'est pas DANS par_nom ALORS ERREUR « prérequis inconnu »
      ajouter t.nom à succ[p]
  entrant[n] ← nombre de prérequis distincts de n
  prêtes ← tas des noms n tels que entrant[n] = 0
  ordre ← liste vide
  TANT QUE prêtes n'est pas vide FAIRE
      n ← retirer le plus petit nom de prêtes ; ajouter n à ordre
      POUR CHAQUE v DANS succ[n] FAIRE
          entrant[v] ← entrant[v] − 1
          SI entrant[v] = 0 ALORS ajouter v à prêtes
  FIN TANT QUE
  SI |ordre| < |par_nom| ALORS ERREUR « cycle détecté : » + NommerCycle(tâches restantes)
  RETOURNER ordre

ALGORITHME NommerCycle(restants)
  v ← plus petit nom de restants ; chemin ← liste vide ; vus ← dictionnaire vide
  TANT QUE v n'est pas DANS vus FAIRE
      vus[v] ← position de v dans chemin ; ajouter v à chemin
      v ← plus petit prérequis de v qui est DANS restants          (il en existe toujours un)
  boucle ← chemin à partir de vus[v], à l'envers                     (sens des arcs)
  faire tourner boucle pour qu'elle commence par son plus petit nom
  RETOURNER boucle suivie de son premier nom

ALGORITHME Vagues
  POUR CHAQUE n DANS TriTopologique(tâches) FAIRE
      niveau[n] ← 1 + max(niveau[p] POUR p prérequis de n), ou 0 sans prérequis
  RETOURNER, pour k de 0 au niveau maximal, les noms de niveau k triés

ALGORITHME CheminCritique
  POUR CHAQUE n DANS TriTopologique(tâches) FAIRE
      début[n] ← max(fin[p] POUR p prérequis de n), ou 0 sans prérequis
      fin[n] ← début[n] + durée[n]
  n ← la tâche de plus grande fin (égalité : plus petit nom) ; chemin ← [n]
  TANT QUE n a des prérequis FAIRE
      n ← le prérequis de plus grande fin (égalité : plus petit nom) ; ajouter n à chemin
  RETOURNER (fin du premier élément de chemin, chemin à l'envers)
```

**Complexité.** Pour n tâches et m dépendances, la construction du graphe lit chaque tâche et chaque arc une fois : O(n + m). Kahn sort chaque tâche une fois et décrémente une fois par arc ; avec le tas binaire, chaque entrée et chaque sortie coûtent O(log n), d'où O(m + n log n) au lieu du O(n + m) d'une simple file : c'est le prix de l'ordre unique. Les vagues et le calendrier ajoutent un passage en O(n + m), et la remontée du chemin critique lit au plus une fois les prérequis de chaque tâche, en O(n + m). Le nommage du cycle visite au plus n tâches et lit leurs prérequis : O(n + m). La mémoire est O(n + m) pour les successeurs et les compteurs.

**Du squelette au code.** `TriTopologique` est `tri_topologique`, qui délègue la construction et les deux premières erreurs à `_graphe` et le nommage à `_nommer_cycle`. Le tas des tâches prêtes est la liste `pretes`, gérée par `heapq.heapify`, `heapq.heappop` et `heapq.heappush`. `Vagues` est `vagues`. La première boucle de `CheminCritique` est `calendrier`, et la remontée est `chemin_critique`. La somme des maxima des vagues est `duree_par_vagues`, et une tâche est une instance de `Tache`.

## Cas d'usage aux Émirats

**Banque — le dossier de crédit du client C-6.** C'est le scénario de la démo. Le dossier passe de 9,5 s en séquentiel à 5,7 s planifié, soit 40 % de gain. Le chemin critique dit **où** optimiser : il passe par `rechercher_regles`. Si l'équipe accélère la recherche de 2,0 s à 0,8 s (un index inversé, par exemple), le dossier ne gagne que 0,1 s, à 5,6 s : la chaîne `lire_memoire` → `calculer_mensualite` → `calculer_ratio` (1,9 s) devient critique à son tour. Optimiser hors du chemin critique ne sert à rien, et l'optimiser au-delà de la marge de la deuxième chaîne non plus.

**Immobilier — un transfert de propriété à Dubaï.** Un plan illustratif, en jours ouvrés : `verifier_identite` (1,5), `verifier_titre` (2,0), `calculer_frais_dld` (0,3, après le titre), `obtenir_noc` (3,0, le certificat de non-objection du promoteur, après le titre), `preparer_virement` (0,5, après les frais et l'identité) et `signer_transfert` (1,0, après le certificat et le virement). Kahn rend `verifier_identite`, `verifier_titre`, `calculer_frais_dld`, `obtenir_noc`, `preparer_virement`, `signer_transfert`. Le chemin critique est `verifier_titre` → `obtenir_noc` → `signer_transfert`, 6,0 jours, contre 6,5 par vagues et 8,3 en séquentiel. Les frais DLD de 4 % sur un bien de 2 000 000 AED (montant illustratif), soit 80 000 AED, sont calculés hors du chemin critique : ce n'est pas eux qui retardent la signature, c'est le certificat.

**RH — un permis de travail mal planifié.** Le modèle propose un plan d'embauche où `obtenir_permis` attend `signer_contrat` et `signer_contrat` attend `obtenir_permis`. `tri_topologique` refuse le plan avec `cycle détecté : obtenir_permis → signer_contrat → obtenir_permis`, un message que le modèle peut lire et corriger, comme une erreur de schéma. Le plan corrigé (séquence illustrative) sépare l'offre du contrat : `signer_offre` (0,5 jour), puis `obtenir_permis` (5,0), puis `signer_contrat` (1,0) et `visite_medicale` (2,0) en parallèle, puis `emettre_visa` (3,0). Chemin critique : `signer_offre` → `obtenir_permis` → `visite_medicale` → `emettre_visa`, 10,5 jours, contre 11,5 en séquentiel.

## Travail à faire

1. Ouvre `projet/agent/planification.py`. La classe `Tache` et ses champs sont déclarés, `dossier_credit()` est fourni ; tout le reste lève `NotImplementedError`.
2. Place-toi dans `projet/` et lance tous les tests : ceux des paliers 01 à 07 passent, les 12 du palier 08 échouent par `NotImplementedError`.

   ```powershell
   cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\08-Planification-DAG\projet"
   python -m unittest -v
   ```

   Si `python` n'est pas dans le PATH, remplace-le par `& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe"`.
3. Code `Tache.__post_init__`. Aucun test ne passe encore (ils ont tous besoin d'un algorithme), mais `python -c "from agent.planification import Tache; print(Tache('calculer_ratio', 0.6, ['calculer_mensualite']))"` doit afficher `Tache(nom='calculer_ratio', duree=0.6, prerequis=('calculer_mensualite',))`.
4. Code `_graphe`, puis `tri_topologique`. Lance `python -m unittest -v tests.test_08_planification.TestTriTopologique` : 3 tests sur 4 sont verts (le cycle n'est pas encore nommé), et `TestTache.test_creation` aussi.
5. Code `_nommer_cycle`. Lance `python -m unittest -v tests.test_08_planification.TestTriTopologique.test_cycle_nomme`.
6. Code `vagues`, puis lance `python -m unittest -v tests.test_08_planification.TestVagues` : 2 tests verts.
7. Code `calendrier`, `chemin_critique` et `duree_par_vagues`, puis lance `python -m unittest -v tests.test_08_planification` : les 12 tests du palier sont verts.
8. Lance toute la suite, puis la démo, et compare avec la sortie attendue ci-dessous.

## Critères de réussite

- `python -m unittest -v` depuis `projet/` : tous les tests verts, paliers 01 à 08.
- `python demo.py` depuis `projet/` affiche exactement la sortie ci-dessous.
- Tu sais dérouler Kahn à la main sur le dossier de crédit, et justifier 5,7 s contre 7,1 s par vagues et 9,5 s en séquentiel.

### Sortie attendue de demo.py

```text
Palier 08 — dossier de crédit du client C-6 à l'agence A-3 (durées illustratives, en secondes)
1. Ordre de Kahn (départage alphabétique) : lire_memoire → calculer_mensualite → calculer_ratio → convertir_usd → rechercher_regles → verifier_identite → evaluer_risque → rediger_reponse
2. Vagues parallèles :
   vague 1 : lire_memoire, rechercher_regles, verifier_identite
   vague 2 : calculer_mensualite
   vague 3 : calculer_ratio, convertir_usd
   vague 4 : evaluer_risque
   vague 5 : rediger_reponse
3. Calendrier au plus tôt, exécutants illimités :
   evaluer_risque   de 2.0 s à 3.2 s
   rediger_reponse  de 3.2 s à 5.7 s
4. Chemin critique : rechercher_regles → evaluer_risque → rediger_reponse = 5.7 s
   séquentiel 9.5 s ; vagues synchronisées 7.1 s ; gain du parallélisme 40.0%
5. Recherche accélérée à 0.8 s : 5.6 s, le chemin critique devient lire_memoire → calculer_mensualite → calculer_ratio → evaluer_risque → rediger_reponse
6. Plan circulaire refusé : cycle détecté : evaluer_risque → rediger_reponse → relancer_client → verifier_identite → evaluer_risque
OK — palier 08 terminé.
```

La ligne 6 vient d'un plan où l'on a voulu relancer le client avant de vérifier son identité : `verifier_identite` attend `relancer_client`, qui attend `rediger_reponse`, qui attend `evaluer_risque`, qui attend `verifier_identite`. Le message nomme les quatre tâches de la boucle, en commençant par la plus petite.

## Pour aller plus loin

1. **Les marges (méthode du chemin critique).** Calcule, à rebours depuis 5,7 s, la date de début au plus tard de chaque tâche, puis sa marge (début au plus tard moins début au plus tôt). Réponse attendue : marge nulle pour `rechercher_regles`, `evaluer_risque` et `rediger_reponse` (le chemin critique), 0,1 s pour `lire_memoire`, `calculer_mensualite` et `calculer_ratio`, 0,5 s pour `verifier_identite` et 1,5 s pour `convertir_usd` ; c'est la marge de 0,1 s qui explique la ligne 5 de la démo.
2. **Un contrôle de plus.** Ajoute `verifier_sanctions` (1,0 s) après `verifier_identite` et avant `evaluer_risque`, et prédis le nouveau chemin critique avant de le calculer. Réponse attendue : 6,2 s par `verifier_identite` → `verifier_sanctions` → `evaluer_risque` → `rediger_reponse`, et 7,3 s par vagues.
3. **La détection de cycle par parcours en profondeur (étape 45).** Écris une version à trois couleurs (blanc, gris, noir) qui détecte un cycle sans Kahn. Réponse attendue : sur le plan circulaire de la démo, elle trouve les quatre mêmes tâches, `evaluer_risque`, `rediger_reponse`, `relancer_client` et `verifier_identite`, à une rotation près selon la tâche de départ.

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/` ; ouvre seulement l'étape qui te manque.

- [01 — La tâche et le dossier de crédit](<solutions/progression/01-Tache-et-dossier-de-credit.md>) : une classe de données gelée qui se valide elle-même, et le plan d'exemple.
- [02 — Le graphe et les degrés entrants](<solutions/progression/02-Graphe-et-degres-entrants.md>) : des prérequis aux successeurs, avec les doublons et les prérequis inconnus refusés.
- [03 — Le tri topologique de Kahn](<solutions/progression/03-Tri-topologique-de-Kahn.md>) : une file naïve, puis le tas qui rend l'ordre unique.
- [04 — Nommer le cycle](<solutions/progression/04-Nommer-le-cycle.md>) : remonter les prérequis jusqu'à repasser par une tâche déjà vue.
- [05 — Les vagues parallèles](<solutions/progression/05-Vagues-paralleles.md>) : le niveau de chaque tâche, en un passage sur l'ordre de Kahn.
- [06 — Calendrier et chemin critique](<solutions/progression/06-Calendrier-et-chemin-critique.md>) : les dates au plus tôt, la remontée du chemin critique, et la borne par vagues.
- [07 — Assemblage et vérification](<solutions/progression/07-Assemblage-et-verification.md>) : le module complet, tous les tests, la démo, et la suite.

En dernier recours, la solution entière est dans `solutions/agent/planification.py`, et `solutions/` se lance comme `projet/`.
