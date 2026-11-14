# Étape 44 — Algorithme de Tri Topologique (Kahn) — Ordonnancement Mathématique des Agents

> Étape 44 du parcours · Prérequis : [Fondements : DAG, nilpotence et tri topologique](<43-Fondements-Orchestration-et-DAG.md>) · Suite : [Détection de cycle par DFS](<45-Detection-de-Cycle-DFS.md>)

**Dossier :** 08-Orchestration  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Platform Team, AI Agent Ops  
**Nom du fichier :** 44-Tri-Topologique-Kahn.md

## Définition

Un **ordre topologique** d'un graphe orienté est une façon de ranger tous ses nœuds en ligne de sorte que, pour chaque arc (u, v), le nœud u apparaisse avant le nœud v. Pour un graphe de tâches, c'est un ordre d'exécution où aucune tâche ne démarre avant que tous ses prérequis soient finis. Un tel ordre existe si et seulement si le graphe est sans cycle (un DAG), et il n'est en général pas unique. L'**algorithme de Kahn** le construit en comptant, pour chaque nœud, ses prérequis non encore traités (son degré entrant) : il sort un nœud dont le compte est à zéro, décrémente le compte de ses successeurs, et recommence. S'il s'arrête avant d'avoir sorti tous les nœuds, le graphe contient un cycle, et l'algorithme peut le montrer.

## Rôle dans un agent

Kahn sert à l'orchestrateur avant d'**agir**, au moment où un plan ou un workflow est chargé : il transforme le graphe des dépendances en un ordre d'exécution, et refuse le graphe s'il contient un cycle. Sa version par **vagues** donne les groupes de tâches qui peuvent partir en même temps, que l'ordonnanceur de l'étape 41 répartit ensuite entre les ouvriers. C'est un contrôle déterministe que le code fait lui-même : un framework d'orchestration n'est pas un vérificateur de dépendances. LangGraph, par exemple, accepte des cycles dans son graphe de contrôle et les borne par une limite de récursion (étape 42) ; il ne refuse pas un graphe parce qu'il contient une boucle. L'ancienne phrase « LangGraph détecte les dépendances circulaires avant exécution » était donc inexacte : si vos tâches ont des dépendances, c'est à votre code de les trier et de refuser un cycle.

## Équation complète

Degré entrant d'un nœud v, à partir de la matrice d'adjacence :

$$
d_{\mathrm{in}}(v) = \sum_{u \in V} A_{u,v}
$$

Ensemble initial des nœuds exécutables, les sources :

$$
S_0 = \{\, v \in V \mid d_{\mathrm{in}}(v) = 0 \,\}
$$

Mise à jour quand un nœud u sort de la file :

$$
d_{\mathrm{in}}(v) \leftarrow d_{\mathrm{in}}(v) - 1 \quad \text{pour chaque successeur } v \text{ de } u
$$

Condition de validité :

$$
|\text{ordre}| = |V| \iff G \text{ est un DAG}
$$

Complexité, pour n nœuds et m arcs :

$$
T(n, m) = O(n + m)
$$

## Décryptage des symboles

$$
G = (V, E)
$$

**Sens :** le graphe : V est l'ensemble des nœuds (agents ou tâches), E l'ensemble des arcs (dépendances) · **Type / plage :** graphe orienté fini · **Variable Python :** `n` (nœuds numérotés de 0 à n − 1) et `aretes`

$$
(u, v) \in E
$$

**Sens :** un arc : u doit avoir fini avant que v ait le droit de commencer · **Type / plage :** couple de nœuds · **Variable Python :** un tuple `(u, v)` de `aretes`

$$
A_{u,v}
$$

**Sens :** coefficient de la matrice d'adjacence, 1 si l'arc (u, v) existe · **Type / plage :** 0 ou 1 · **Variable Python :** non construite (le code lit directement les arcs, ce qui évite les n² cases)

$$
d_{\mathrm{in}}(v)
$$

**Sens :** degré entrant restant : nombre de prérequis de v pas encore sortis · **Type / plage :** entier ≥ 0, qui ne fait que baisser · **Variable Python :** `entrant[v]`

$$
S_0
$$

**Sens :** les sources, nœuds sans prérequis, points d'entrée du workflow · **Type / plage :** sous-ensemble de V · **Variable Python :** le contenu initial de `file`

$$
n = |V|,\; m = |E|
$$

**Sens :** nombre de nœuds et nombre d'arcs · **Type / plage :** entiers ≥ 0 · **Variable Python :** `n`, `len(aretes)`

## Démonstration

### 1. Lemme : si chaque nœud a un prédécesseur, il y a un cycle

Soit un graphe fini, non vide, où chaque nœud a un degré entrant au moins 1. On part d'un nœud v₀, on choisit un prédécesseur v₁ de v₀, puis un prédécesseur v₂ de v₁, et ainsi de suite : c'est toujours possible, puisque chaque nœud a au moins un prédécesseur. Le graphe n'a qu'un nombre fini de nœuds, donc la suite v₀, v₁, v₂, … finit par repasser par un nœud déjà vu : vᵢ = vⱼ avec i < j. Les arcs vont de vₖ₊₁ vers vₖ, donc vⱼ → vⱼ₋₁ → … → vᵢ = vⱼ est un cycle. La fonction `remonter_cycle` du code fait exactement cette remontée.

**Conséquence : tout DAG fini non vide a au moins une source.** Sinon, chaque nœud aurait un prédécesseur, et le lemme donnerait un cycle.

### 2. L'invariant de Kahn

À chaque instant, la file contient exactement les nœuds qui ne sont pas encore sortis et dont **tous** les prédécesseurs sont déjà sortis ; et `entrant[v]` vaut le nombre de prédécesseurs de v qui ne sont pas encore sortis. C'est vrai au départ, où rien n'est sorti : `entrant[v]` est le degré entrant complet, et la file contient les sources. C'est conservé à chaque tour : quand u sort, chacun de ses successeurs perd exactement un prédécesseur non sorti, d'où `entrant[v] -= 1` ; un successeur entre dans la file au moment précis où son compte tombe à 0, c'est-à-dire quand son dernier prédécesseur sort. Un compte ne fait que baisser, donc un nœud entre dans la file au plus une fois.

### 3. L'ordre produit est topologique

Un nœud ne sort que s'il est dans la file, donc, par l'invariant, après tous ses prédécesseurs. Pour tout arc (u, v), u sort donc avant v.

### 4. Si G est un DAG, tous les nœuds sortent

Supposons qu'à un moment la file soit vide alors qu'il reste des nœuds. Les nœuds restants forment un sous-graphe de G, donc un DAG (on ne peut pas créer de cycle en retirant des nœuds), non vide : par le point 1, il a une source r, un nœud dont aucun prédécesseur n'est parmi les restants. Tous les prédécesseurs de r sont donc sortis, et par l'invariant r est dans la file : contradiction. La file n'est jamais vide tant qu'il reste des nœuds, et Kahn sort les n nœuds.

### 5. Si Kahn s'arrête trop tôt, G a un cycle, et on peut le montrer

Si la file se vide alors qu'il reste des nœuds, chaque nœud restant a, par l'invariant, au moins un prédécesseur **parmi les restants**. Le lemme du point 1, appliqué au sous-graphe des restants, donne un cycle, qui est aussi un cycle de G. Avec le point 4, on obtient l'équivalence :

$$
\text{Kahn sort les } n \text{ nœuds} \iff G \text{ est un DAG}
$$

Le code ne se contente pas de dire « cycle détecté » : il remonte les prédécesseurs restants et nomme le cycle, ici 2 → 3 → 4 → 2 quand on ajoute l'arc (4, 2) à l'exemple.

### 6. Complexité O(n + m)

On compte les opérations, comme le fait le programme.

- La construction des listes de successeurs et des degrés entrants lit chaque arc une fois et initialise chaque nœud une fois : O(n + m).
- Chaque nœud entre dans la file au plus une fois (point 2) et en sort au plus une fois, en O(1) avec une `deque` : O(n).
- Chaque arc (u, v) est examiné une seule fois, quand u sort : O(m) décréments en tout.

Le total vaut O(n + m) en temps, et O(n + m) en mémoire pour les listes et les compteurs. Sur le DAG de 1 000 nœuds et 1 503 arcs du programme, on mesure exactement 1 000 sorties et 1 503 décréments. À comparer avec les puissances de matrice de l'étape 42, en O(n⁴).

### 7. La version par vagues

Au lieu de sortir un nœud à la fois, on vide la file entière : c'est une vague, et les nœuds dont le compte tombe à 0 pendant ce tour forment la vague suivante. Les points 2 à 6 restent vrais, puisqu'on fait les mêmes décréments dans un autre ordre. Une tâche est dans la vague k exactement quand le plus long chemin qui mène à elle depuis une source a k arcs (étape 42, démonstration, point 6) ; le nombre de vagues vaut donc 1 + la longueur du plus long chemin. Toutes les tâches d'une vague peuvent partir en même temps, puisqu'aucune ne dépend d'une autre de la même vague.

### 8. Exemple fait à la main (le code reprend ces nombres)

Cinq agents : 0 rédige le brief, 1 rassemble les chiffres, 2 rédige le rapport quand le brief et les chiffres sont là, 3 relit le rapport, 4 l'envoie au client. Les arcs sont (0, 2), (1, 2), (2, 3), (3, 4).

| Étape | Nœud sorti | Décréments | Degrés entrants après | File après |
|---|---|---|---|---|
| départ | — | — | [0, 0, 2, 1, 1] | [0, 1] |
| 1 | 0 | 2 : 2 → 1 | [0, 0, 1, 1, 1] | [1] |
| 2 | 1 | 2 : 1 → 0 | [0, 0, 0, 1, 1] | [2] |
| 3 | 2 | 3 : 1 → 0 | [0, 0, 0, 0, 1] | [3] |
| 4 | 3 | 4 : 1 → 0 | [0, 0, 0, 0, 0] | [4] |
| 5 | 4 | aucun | [0, 0, 0, 0, 0] | [] |

L'ordre est [0, 1, 2, 3, 4], avec 5 sorties et 4 décréments. La force brute sur les 120 permutations trouve exactement deux ordres légaux, [0, 1, 2, 3, 4] et [1, 0, 2, 3, 4] : le brief et les chiffres peuvent s'échanger. Les vagues sont {0, 1}, {2}, {3}, {4}. Avec l'arc (4, 2) en plus, le degré entrant de 2 vaut 3 ; après la sortie de 0 et de 1, il vaut encore 1, la file est vide, seuls 2 nœuds sur 5 sont sortis, et la remontée depuis 2 passe par 4, puis 3, puis revient à 2.

## Effets et comportement

- **Plusieurs sources : plusieurs ordres légaux.** Kahn en renvoie un, déterminé par l'ordre de la file ; avec `range(n)` et une `deque`, c'est le plus petit indice d'abord. Si l'ordre compte, on remplace la file par le tas de priorité de l'étape 41.
- **Un seul arc de trop peut tout bloquer.** L'arc (4, 2) ne gêne que trois nœuds, mais il suffit à rendre le graphe invalide : Kahn s'arrête avec 2 nœuds sur 5.
- **Le coût est linéaire** : doubler le nombre de tâches et de dépendances double à peu près le temps de vérification, alors qu'il serait multiplié par 16 avec les puissances de matrice.
- **Les vagues donnent le parallélisme, pas le calendrier.** Leur nombre est fixé par le plus long chemin ; pour la durée réelle, il faut le chemin critique pondéré de l'étape 42.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| successeurs, prédécesseurs, d_in(v) | `construire(n, aretes)`, qui renvoie `succ`, `pred`, `entrant` |
| S₀ | `deque(i for i in range(n) if entrant[i] == 0)` |
| d_in(v) ← d_in(v) − 1 | `entrant[voisin] -= 1` |
| \|ordre\| = \|V\| | `len(ordre) != n`, qui lève `ValueError` |
| cycle exhibé (point 5) | `remonter_cycle(restants, pred)` |
| vagues (point 7) | `vagues_kahn(n, aretes)` |
| vérification d'un ordre | `est_ordre_topologique(ordre, aretes)` |

Copiez le bloc dans `kahn_agents.py` et lancez `python kahn_agents.py`.

### Déroulé, ligne par ligne

**`construire(n, aretes)`** prépare tout en un seul passage sur les arcs. `succ[u]` liste les agents que u débloque, `pred[v]` ceux dont v dépend, et `entrant[v] += 1` compte une dépendance de plus pour v. Une arête qui cite un nœud hors de 0..n − 1 lève une `ValueError`, au lieu de planter plus loin sur un index. Après les quatre arcs de l'exemple, `entrant` vaut `[0, 0, 2, 1, 1]` : on a additionné la colonne v de la matrice d'adjacence sans la construire, ce qui coûte une opération par arc au lieu d'une par case.

**`tri_topologique_kahn(n, aretes, compteur)`**, le cœur.

- `file = deque(i for i in range(n) if entrant[i] == 0)` construit S₀ : `[0, 1]`. Une `deque` retire par la gauche en O(1), donc le premier entré est le premier traité.
- `while file` : on retire `noeud = file.popleft()`, on l'ajoute à `ordre`, puis, pour chaque `voisin` de `succ[noeud]`, on fait `entrant[voisin] -= 1`. Quand le compte tombe à 0, le dernier prérequis du voisin vient de finir et il entre dans la file. Au premier tour, la sortie de 0 fait passer 2 de 2 à 1 : 2 reste bloqué, parce qu'il attend encore les chiffres. Au deuxième tour, la sortie de 1 le fait tomber à 0.
- `sorties` et `decrements` comptent les opérations du point 6 ; si l'on passe un dictionnaire `compteur`, la fonction y écrit ces deux nombres.
- `if len(ordre) != n` : la file s'est vidée trop tôt. `restants` est l'ensemble des nœuds jamais sortis ; `remonter_cycle` en extrait un cycle, et le message de la `ValueError` le nomme.

**`remonter_cycle(restants, pred)`** est la preuve du point 1, exécutée.

- On part du plus petit nœud restant, pour un résultat stable d'une exécution à l'autre.
- `v = min(p for p in pred[v] if p in restants)` choisit un prédécesseur parmi les restants ; il existe toujours, parce que chaque restant a un degré entrant restant au moins 1.
- `vus` retient la position de chaque nœud dans `chemin`. Dès que `v` est déjà vu, `chemin[vus[v]:]` est la boucle, parcourue à rebours des arcs ; on l'inverse, on la fait commencer par son plus petit nœud, et on referme en répétant le premier. Avec l'arc (4, 2), la remontée visite 2, 4, 3, puis retombe sur 2 : le cycle est 2 → 3 → 4 → 2.

**`vagues_kahn(n, aretes)`** applique le point 7 : `vague` contient tous les nœuds prêts en même temps, et `suivante` ceux qui le deviennent pendant le tour. On trie chaque vague pour une sortie déterministe. Le contrôle `total != n` joue le même rôle que dans la version à une file.

**`est_ordre_topologique(ordre, aretes)`** construit la position de chaque nœud et vérifie `position[u] < position[v]` pour chaque arc : c'est la définition, testée directement.

**`main()`**, bloc par bloc.

1. Les degrés entrants `[0, 0, 2, 1, 1]` et les sources `[0, 1]`.
2. L'ordre `[0, 1, 2, 3, 4]`, avec 5 sorties et 4 décréments ; la force brute sur les 120 permutations trouve 2 ordres légaux, dont celui de Kahn.
3. Les vagues `[[0, 1], [2], [3], [4]]`.
4. L'arc (4, 2) : la `ValueError` dit « 2/5 nœuds ordonnés » et nomme le cycle 2 → 3 → 4 → 2.
5. Un DAG aléatoire de 1 000 nœuds (graine 7, arcs tirés avec u < v puis renumérotés au hasard, pour que l'ordre des indices ne trahisse pas l'ordre topologique) : 1 000 sorties et exactement un décrément par arc.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`remonter_cycle(restants, pred)`** — Cette fonction est l'enquêteur qui, face à des dossiers bloqués, remonte la chaîne des responsabilités jusqu'à retomber sur un nom déjà noté : elle reçoit l'ensemble des nœuds que Kahn n'a jamais pu sortir et la liste des prédécesseurs de chaque nœud, part du plus petit restant, puis passe à chaque fois au plus petit de ses prédécesseurs restants, qui existe toujours, en notant la position de chaque nœud visité. Dès qu'elle retombe sur un nœud déjà vu, elle découpe la boucle, la remet dans le sens des arcs, la fait commencer par son plus petit nœud et la referme ; elle renvoie cette liste, `[2, 3, 4, 2]` quand l'arc (4, 2) ferme le cycle.

**`tri_topologique_kahn(n, aretes, compteur)`** — C'est le guichetier d'une file d'attente où un dossier n'est appelé que lorsque toutes ses pièces préalables sont arrivées : la fonction reçoit le nombre n de nœuds, la liste des arcs et, facultativement, un dictionnaire où noter ses comptes, construit successeurs, prédécesseurs et degrés entrants avec `construire`, met les sources dans une `deque`, puis sort un nœud à la fois et décrémente ses successeurs, qui entrent dans la file en tombant à 0. Elle renvoie l'ordre, `[0, 1, 2, 3, 4]` pour l'exemple, avec 5 sorties et 4 décréments notés dans le compteur ; si la file se vide trop tôt, elle appelle `remonter_cycle` et lève une `ValueError` qui donne le nombre de nœuds ordonnés, « 2/5 », et nomme le cycle 2 → 3 → 4 → 2.

**`est_ordre_topologique(ordre, aretes)`** — Cette fonction est le contrôleur qui relit un planning et vérifie que personne n'est convoqué avant ceux dont il dépend : elle reçoit un ordre de nœuds et la liste des arcs, construit un dictionnaire qui donne la position de chaque nœud dans l'ordre, et renvoie vrai si, pour chaque arc (u, v), u apparaît avant v. C'est la définition même, testée sans aucune astuce ; `main` s'en sert pour valider l'ordre de Kahn, pour trouver par force brute les 2 ordres légaux parmi les 120 permutations, et pour vérifier l'ordre du graphe aléatoire de 1 000 nœuds.

**`main()`** — Le chef d'orchestre déroule les cinq tableaux du chapitre sur un petit flux de cinq agents, du brief à l'envoi : il affiche les degrés entrants `[0, 0, 2, 1, 1]` et les sources, fait tourner Kahn et vérifie l'ordre, les 5 sorties et les 4 décréments, compare au résultat de la force brute, puis calcule les vagues `[[0, 1], [2], [3], [4]]`. Il ajoute ensuite l'arc (4, 2) pour faire nommer le cycle, et tire enfin, avec la graine 7, un graphe sans cycle de 1 000 nœuds et 1 503 arcs pour constater 1 000 sorties et exactement un décrément par arc ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 44 — tri topologique de Kahn : ordre, vagues parallèles, cycle exhibé, coût O(n + m) compté."""
import itertools
import random
import sys
from collections import deque

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def construire(n: int, aretes: list[tuple[int, int]]):
    """Listes de successeurs, de prédécesseurs, et degrés entrants (une opération par arête)."""
    succ = [[] for _ in range(n)]
    pred = [[] for _ in range(n)]
    entrant = [0] * n
    for u, v in aretes:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"arête ({u}, {v}) hors des nœuds 0..{n - 1}")
        succ[u].append(v)
        pred[v].append(u)
        entrant[v] += 1
    return succ, pred, entrant


def remonter_cycle(restants: set[int], pred: list[list[int]]) -> list[int]:
    """Preuve constructive : chaque nœud restant a un prédécesseur restant. En remontant, on retombe
    forcément sur un nœud déjà vu (ensemble fini) : le morceau parcouru est un cycle."""
    v = min(restants)
    vus = {}
    chemin = []
    while v not in vus:
        vus[v] = len(chemin)
        chemin.append(v)
        v = min(p for p in pred[v] if p in restants)     # existe : degré entrant restant >= 1
    boucle = chemin[vus[v]:]                              # suivi à rebours des arcs
    boucle.reverse()                                      # remis dans le sens des arcs
    k = boucle.index(min(boucle))
    boucle = boucle[k:] + boucle[:k]                      # commence par son plus petit nœud : message stable
    return boucle + [boucle[0]]


def tri_topologique_kahn(n: int, aretes: list[tuple[int, int]], compteur: dict | None = None) -> list[int]:
    """Renvoie un ordre où chaque arête (u, v) a u avant v ; lève ValueError en nommant un cycle."""
    succ, pred, entrant = construire(n, aretes)
    file = deque(i for i in range(n) if entrant[i] == 0)  # S0 : les sources
    ordre = []
    sorties = decrements = 0
    while file:
        noeud = file.popleft()
        sorties += 1
        ordre.append(noeud)
        for voisin in succ[noeud]:
            decrements += 1
            entrant[voisin] -= 1
            if entrant[voisin] == 0:                      # son dernier prérequis vient de finir
                file.append(voisin)
    if compteur is not None:
        compteur.update(sorties=sorties, decrements=decrements)
    if len(ordre) != n:
        restants = set(range(n)) - set(ordre)
        cycle = remonter_cycle(restants, pred)
        raise ValueError(f"cycle détecté : {len(ordre)}/{n} nœuds ordonnés ; cycle {' → '.join(map(str, cycle))}")
    return ordre


def vagues_kahn(n: int, aretes: list[tuple[int, int]]) -> list[list[int]]:
    """Version parallèle : on vide toute la file d'un coup ; les nouveaux degrés nuls forment la vague suivante."""
    succ, _, entrant = construire(n, aretes)
    vague = [i for i in range(n) if entrant[i] == 0]
    vagues, total = [], 0
    while vague:
        vagues.append(vague)
        total += len(vague)
        suivante = []
        for u in vague:
            for v in succ[u]:
                entrant[v] -= 1
                if entrant[v] == 0:
                    suivante.append(v)
        vague = sorted(suivante)
    if total != n:
        raise ValueError("cycle détecté : certaines tâches ne deviennent jamais prêtes")
    return vagues


def est_ordre_topologique(ordre: list[int], aretes: list[tuple[int, int]]) -> bool:
    position = {v: k for k, v in enumerate(ordre)}
    return all(position[u] < position[v] for u, v in aretes)


def main() -> None:
    noms = ["brief", "chiffres", "rapport", "relecture", "envoi"]
    aretes = [(0, 2), (1, 2), (2, 3), (3, 4)]

    print("1. Degrés entrants et sources")
    _, _, entrant = construire(5, aretes)
    print(f"  degrés entrants = {entrant} ; sources S0 = {[i for i in range(5) if entrant[i] == 0]}")
    assert entrant == [0, 0, 2, 1, 1]

    print("2. Kahn, une sortie à la fois")
    compteur = {}
    ordre = tri_topologique_kahn(5, aretes, compteur)
    print(f"  ordre = {ordre} = {[noms[i] for i in ordre]}")
    print(f"  {compteur['sorties']} sorties de file (n = 5), {compteur['decrements']} décréments (m = 4)")
    assert ordre == [0, 1, 2, 3, 4] and est_ordre_topologique(ordre, aretes)
    assert compteur == {"sorties": 5, "decrements": 4}
    legaux = [list(p) for p in itertools.permutations(range(5)) if est_ordre_topologique(list(p), aretes)]
    print(f"  ordres légaux par force brute : {legaux}")
    assert ordre in legaux and len(legaux) == 2

    print("3. Vagues parallèles")
    vagues = vagues_kahn(5, aretes)
    print(f"  {[[noms[i] for i in v] for v in vagues]}")
    assert vagues == [[0, 1], [2], [3], [4]]

    print("4. Une arête (4, 2) ferme un cycle")
    try:
        tri_topologique_kahn(5, aretes + [(4, 2)])
    except ValueError as e:
        print(f"  ValueError : {e}")
        assert "2/5" in str(e) and "2 → 3 → 4 → 2" in str(e)
    else:
        raise AssertionError("le cycle aurait dû être détecté")

    print("5. Coût linéaire : on compte les opérations sur un DAG de 1 000 nœuds")
    random.seed(7)
    n_grand = 1000
    grandes = sorted({(u, v) for u, v in ((random.randrange(n_grand), random.randrange(n_grand)) for _ in range(3000)) if u < v})
    perm = list(range(n_grand))
    random.shuffle(perm)                                  # on renumérote : l'ordre des indices ne trahit plus rien
    grandes = [(perm[u], perm[v]) for u, v in grandes]
    compteur = {}
    ordre = tri_topologique_kahn(n_grand, grandes, compteur)
    print(f"  m = {len(grandes)} arêtes ; {compteur['sorties']} sorties, {compteur['decrements']} décréments")
    assert est_ordre_topologique(ordre, grandes)
    assert compteur["sorties"] == n_grand and compteur["decrements"] == len(grandes)
    assert sum(len(v) for v in vagues_kahn(n_grand, grandes)) == n_grand
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Degrés entrants et sources
  degrés entrants = [0, 0, 2, 1, 1] ; sources S0 = [0, 1]
2. Kahn, une sortie à la fois
  ordre = [0, 1, 2, 3, 4] = ['brief', 'chiffres', 'rapport', 'relecture', 'envoi']
  5 sorties de file (n = 5), 4 décréments (m = 4)
  ordres légaux par force brute : [[0, 1, 2, 3, 4], [1, 0, 2, 3, 4]]
3. Vagues parallèles
  [['brief', 'chiffres'], ['rapport'], ['relecture'], ['envoi']]
4. Une arête (4, 2) ferme un cycle
  ValueError : cycle détecté : 2/5 nœuds ordonnés ; cycle 2 → 3 → 4 → 2
5. Coût linéaire : on compte les opérations sur un DAG de 1 000 nœuds
  m = 1503 arêtes ; 1000 sorties, 1503 décréments
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : Kahn ordonne en comptant, refuse un cycle en le nommant, donne le parallélisme par vagues, et fait exactement une sortie par nœud et un décrément par arc.

## Squelette algorithmique

Deux algorithmes partagent la même idée. **Kahn** prend le nombre de nœuds n et la liste des arcs (u, v), et renvoie un ordre topologique, ou un échec qui nomme un cycle. L'idée est de tenir, pour chaque nœud, le nombre de prérequis non encore sortis, de sortir un nœud dont ce nombre est nul, puis de décrémenter ses successeurs ; si la file se vide trop tôt, on remonte les prédécesseurs des nœuds restants jusqu'à retomber sur un nœud déjà vu (point 1). **Kahn par vagues** prend les mêmes entrées et renvoie la liste des vagues : on vide la file entière à chaque tour, et les nœuds libérés pendant ce tour forment la vague suivante.

```text
ALGORITHME Kahn
ENTRÉES : nombre de nœuds n, arcs (u, v)
SORTIE : ordre topologique, ou échec avec un cycle

POUR v DE 0 À n − 1 FAIRE
    succ(v) ← liste vide ; pred(v) ← liste vide ; entrant(v) ← 0
FIN POUR
POUR chaque arc (u, v) FAIRE
    ajouter v à succ(u) ; ajouter u à pred(v)
    entrant(v) ← entrant(v) + 1
FIN POUR
file ← les v tels que entrant(v) = 0, par indice croissant
ordre ← liste vide
TANT QUE file n'est pas vide FAIRE
    u ← retirer le premier élément de file
    ajouter u à ordre
    POUR chaque v de succ(u) FAIRE
        entrant(v) ← entrant(v) − 1
        SI entrant(v) = 0 ALORS
            ajouter v à la fin de file                (son dernier prérequis vient de sortir)
        FIN SI
    FIN POUR
FIN TANT QUE
SI longueur(ordre) = n ALORS
    RETOURNER ordre
SINON
    restants ← les nœuds absents de ordre
    v ← le plus petit des restants ; vus ← ensemble vide ; chemin ← liste vide
    TANT QUE v ∉ vus FAIRE
        ajouter v à vus et à chemin
        v ← un prédécesseur de v qui est dans restants   (il en existe toujours un)
    FIN TANT QUE
    RETOURNER échec avec le cycle formé par chemin depuis v, remis dans le sens des arcs
FIN SI
```

```text
ALGORITHME KahnParVagues
ENTRÉES : nombre de nœuds n, arcs (u, v)
SORTIE : liste des vagues, ou échec si cycle

calculer succ et entrant comme dans Kahn
vague ← les v tels que entrant(v) = 0
vagues ← liste vide ; total ← 0
TANT QUE vague n'est pas vide FAIRE
    ajouter vague à vagues ; total ← total + taille(vague)
    suivante ← liste vide
    POUR chaque u de vague FAIRE
        POUR chaque v de succ(u) FAIRE
            entrant(v) ← entrant(v) − 1
            SI entrant(v) = 0 ALORS ajouter v à suivante FIN SI
        FIN POUR
    FIN POUR
    vague ← suivante triée
FIN TANT QUE
SI total < n ALORS RETOURNER échec (cycle) FIN SI
RETOURNER vagues
```

**Complexité :** la construction lit chaque arc une fois et initialise chaque nœud une fois, soit O(n + m). Dans la boucle principale, chaque nœud entre et sort de la file au plus une fois, en O(1) avec une file à double entrée, soit O(n), et chaque arc est décrémenté une seule fois, au moment où son origine sort, soit O(m) : le tri coûte O(n + m) en temps (point 6). La remontée de cycle visite au plus n nœuds, et pour chacun parcourt sa liste de prédécesseurs, soit O(n + m) au pire. La mémoire vaut O(n + m) : les listes `succ` et `pred` contiennent chacune m entrées, les compteurs, la file et l'ordre n entrées. La version par vagues fait les mêmes décréments ; le tri de chaque vague ajoute O(w log w) pour une vague de taille w, soit O(n log n) au pire, que l'on peut supprimer si l'on n'a pas besoin d'une sortie triée.

**Du squelette au code :** les deux premières boucles sont la fonction `construire`, avec en plus la vérification des indices. La ligne « file ← … » est `deque(i for i in range(n) if entrant[i] == 0)`. La boucle « TANT QUE file n'est pas vide » est le `while file` de `tri_topologique_kahn`, où « retirer le premier élément » s'écrit `file.popleft()` et où les compteurs `sorties` et `decrements` mesurent le point 6. La branche « SINON » est le bloc `if len(ordre) != n`, et la remontée est la fonction `remonter_cycle`, qui choisit le plus petit prédécesseur restant pour un résultat déterministe puis fait commencer le cycle par son plus petit nœud. `KahnParVagues` est la fonction `vagues_kahn`, avec `vague = sorted(suivante)` pour la ligne « vague ← suivante triée ». La fonction `est_ordre_topologique` ne fait pas partie de l'algorithme : elle vérifie la sortie contre la définition.

## Cas d'usage réels aux Émirats

Les étapes, délais et volumes ci-dessous sont illustratifs : chaque équipe décrit ses propres dépendances, et les règles citées sont à confirmer avec les textes en vigueur.

### Banque — l'ordre d'un financement Murabaha

Une banque de détail de Dubaï fait instruire ses financements islamiques par un agent. Dans une Murabaha, la banque achète le bien, en devient propriétaire, puis le revend au client avec une marge connue d'avance : la revente avant l'achat est exclue par la structure même du contrat. Le workflow a pour tâches le KYC, l'évaluation de la capacité de remboursement (avec le ratio d'endettement de la CBUAE, toutes mensualités comprises, sous 50 % du revenu), l'achat du bien par la banque, le transfert de propriété à la banque, puis la revente et l'échéancier, avec les arcs correspondants. Kahn produit un ordre où la revente vient toujours après le transfert de propriété, et l'orchestrateur n'exécute que dans cet ordre ; une modification du workflow qui créerait une dépendance circulaire est refusée au chargement, avec le cycle nommé dans le message. Sans ce contrôle, un agent qui « optimise » l'enchaînement pourrait préparer le contrat de revente en parallèle de l'achat et le faire signer trop tôt, ce qui rendrait le contrat non conforme aux exigences validées par le comité de conformité islamique de la banque. On suit le nombre de dossiers où une étape a été tentée hors ordre, avec un objectif de zéro.

### Immobilier — d'une signature de bail à l'emménagement

Une agence de Dubaï accompagne des locataires de la signature du bail jusqu'à l'emménagement. Les tâches sont : signature du contrat, enregistrement du bail dans Ejari, ouverture des compteurs d'eau et d'électricité (qui demande le bail enregistré), assurance habitation, état des lieux et remise des clés. L'assurance et l'enregistrement n'ont pas de dépendance entre eux : la version par vagues les lance ensemble, puis l'ouverture des compteurs et l'état des lieux, puis la remise des clés. Kahn donne trois vagues au lieu de six étapes en file, et l'agent envoie au locataire une liste d'actions groupées par vague plutôt qu'une suite de relances. Sans l'ordre topologique, l'agent demanderait l'ouverture des compteurs avant l'enregistrement Ejari, et la demande serait rejetée. On suit le délai moyen entre la signature et la remise des clés.

### RH — le fichier de paie WPS, chaque mois

Un cabinet RH présent dans plusieurs émirats produit chaque mois, pour ses clients, le fichier de salaires à transmettre par le WPS. Les tâches s'enchaînent : collecte des feuilles de temps, calcul des heures supplémentaires, calcul des salaires, provisions d'indemnité de fin de service (21 jours de salaire de base par année pendant les cinq premières années, 30 jours au-delà, plafond de 24 mois, outil déterministe `gratuite_fin_de_service`), génération du fichier, contrôle, puis envoi à la banque. Pour 40 clients, le graphe compte quelques centaines de tâches et Kahn le trie en un passage linéaire. Une règle mal écrite (« le contrôle du fichier exige l'envoi bancaire », alors que l'envoi exige le contrôle) crée un cycle : Kahn s'arrête et nomme le cycle contrôle → envoi → contrôle, au lieu de laisser la paie bloquée jusqu'à l'échéance. Le WPS impose de payer dans les délais, ce qui rend ce contrôle au chargement précieux. On suit le nombre de fichiers transmis à temps et le nombre de workflows refusés au chargement.

### BTP — vérifier un planning de 4 000 tâches en un instant

Un groupe de construction à Dubaï tient le planning d'un grand chantier : environ 4 000 tâches et 12 000 dépendances entre lots, sous-traitants et livraisons. À chaque modification, un agent revérifie que le planning reste sans cycle. Kahn fait environ 4 000 sorties et 12 000 décréments, soit quelques dizaines de milliers d'opérations ; le test par les puissances de matrice de l'étape 42 en demanderait de l'ordre de 4 000⁴ ≈ 2,6 × 10¹⁴, hors de portée. Quand un conducteur de travaux ajoute par erreur « la dalle du niveau 3 attend le coffrage du niveau 4 », Kahn s'arrête et la remontée nomme les lots pris dans la boucle, que l'agent signale avec la modification responsable. Les vagues indiquent aussi quels sous-traitants peuvent intervenir en même temps sur le chantier. On suit le nombre de modifications de planning refusées et le délai de leur correction.

### Secteur public — un formulaire dont les étapes se débloquent

Une entité de services publics en ligne, accessible par UAE Pass, guide les usagers en arabe et en anglais dans une démarche en plusieurs étapes : connexion, vérification de l'identité, choix du service, pièces justificatives, paiement des frais, dépôt. Certaines étapes en débloquent plusieurs autres, et l'agent affiche à chaque instant les étapes de la vague courante, celles que l'usager peut faire maintenant, au lieu d'une liste figée. Kahn sur le graphe des étapes garantit que le paiement ne s'ouvre pas avant que les pièces exigées soient fournies. La minimisation des données de la PDPL se traduit dans le graphe : une pièce qui ne débloque aucune étape n'a pas de raison d'être demandée, et le contrôle au chargement le signale. On suit le taux d'abandon par étape et le temps médian de la démarche.

### Crypto — déployer des règles de surveillance qui dépendent les unes des autres

Une plateforme d'actifs virtuels agréée par la VARA calcule ses alertes de surveillance à partir d'indicateurs qui dépendent les uns des autres : volume par adresse, puis volume anormal par rapport à l'historique, puis score de risque combinant plusieurs indicateurs, puis règle d'alerte. Chaque nouvelle règle passe par l'intégration continue, où un agent ajoute ses dépendances au graphe et lance Kahn : l'ordre de calcul des indicateurs en sort, et une règle qui ferait dépendre le score de risque de l'alerte qu'il déclenche est refusée avant la mise en production. Sans ce contrôle, la règle circulaire ne serait jamais calculée, et des transactions passeraient sans surveillance, ce que les obligations de lutte contre le blanchiment de la plateforme ne permettent pas. Les vagues donnent les indicateurs que le moteur peut calculer en parallèle. On suit le nombre de règles refusées en intégration continue et la latence de calcul des alertes.

## Pièges et limites

- **Croire que le framework vérifie à votre place.** Un orchestrateur qui accepte des boucles bornées dans son graphe de contrôle ne trie pas vos dépendances : c'est votre code qui lance Kahn au chargement.
- **Se contenter de « cycle détecté ».** Un message qui ne nomme pas les nœuds du cycle fait perdre des heures ; la remontée du point 1 coûte O(n + m) et donne le cycle.
- **Supposer que l'ordre est unique.** Deux exécutions sur des données équivalentes peuvent produire deux ordres légaux différents si l'ordre de la file change ; si l'ordre doit être reproductible, on fixe la règle de départage (indice, ou priorité de l'étape 41).
- **Prendre les vagues pour un calendrier.** Les vagues disent qui peut partir ensemble ; la durée minimale vient du chemin critique pondéré (étape 42).
- **Construire la matrice d'adjacence.** Elle coûte n² cases pour quelques arcs ; Kahn lit les arcs directement.

### Exercice feuille blanche

1. Sans regarder le code, écrire `tri_topologique_kahn` avec une `deque` et un tableau de degrés entrants, puis vérifier l'ordre [0, 1, 2, 3, 4] et le refus de l'arc (4, 2).
2. Prédire, puis vérifier : on ajoute l'arc (1, 0). Quels sont l'ordre, les vagues et le nombre d'ordres légaux ? (Réponse : ordre [1, 0, 2, 3, 4], vagues {1}, {0}, {2}, {3}, {4}, un seul ordre légal, puisque chaque vague n'a plus qu'un nœud.)
3. Trouver le bug : une variante met `file.append(voisin)` à chaque décrément, sans tester `entrant[voisin] == 0`. Que produit-elle sur l'exemple ? (Réponse : le rapport entre dans la file dès que le brief sort, avant les chiffres, puis une deuxième fois quand les chiffres sortent ; chaque nœud entre autant de fois qu'il a de prérequis. L'ordre devient [0, 1, 2, 2, 3, 3, 4, 4], de longueur 8 au lieu de 5. Le test `len(ordre) != n` le signale, mais en accusant à tort un cycle.)

## Pour aller plus loin

- **Unicité.** L'ordre topologique est unique si et seulement si la file ne contient jamais plus d'un nœud, c'est-à-dire si le graphe contient un chemin qui passe par tous les nœuds.
- **Tri topologique par DFS.** L'ordre inverse des fins de visite d'un parcours en profondeur est aussi un ordre topologique : c'est l'objet de l'étape 45, qui détecte en plus les cycles par les couleurs.
- **Graphes dynamiques.** Quand on ajoute des arcs un par un, des algorithmes de tri topologique incrémental évitent de tout recalculer.
- **Outils.** Les systèmes de build et les gestionnaires de paquets trient leurs dépendances de la même façon.

> Suite : [Détection de cycle par DFS](<45-Detection-de-Cycle-DFS.md>) — étape 45.
