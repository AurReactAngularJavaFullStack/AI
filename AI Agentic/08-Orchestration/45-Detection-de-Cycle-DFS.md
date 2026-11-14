# Étape 45 — Détection de Cycle par DFS (Parcours en Profondeur)

> Étape 45 du parcours · Prérequis : [Tri topologique : l'algorithme de Kahn](<44-Tri-Topologique-Kahn.md>) · Suite : [Journal d'événements partitionné (à la manière de Kafka)](<45b-Journal-d-Evenements-Partitionne.md>)

**Dossier :** 08-Orchestration  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Platform Team, AI Agent Ops  
**Nom du fichier :** 45-Detection-de-Cycle-DFS.md

## Définition

Le parcours en profondeur, ou **DFS** (Depth-First Search), visite un graphe en suivant un arc aussi loin que possible avant de revenir en arrière. Pour détecter un cycle dans un graphe orienté, on peint chaque nœud d'une de trois couleurs : **blanc** s'il n'a jamais été visité, **gris** si sa visite a commencé et n'est pas finie, **noir** si sa visite est finie, c'est-à-dire si tous ses successeurs ont été traités. À chaque instant, les nœuds gris sont exactement ceux du chemin en cours, de la racine jusqu'au nœud que l'on visite. Un **arc arrière** est un arc (u, v) tel que, **au moment où il est examiné pendant la visite de u, v est gris** : il remonte vers un nœud du chemin en cours, et ce chemin plus cet arc forment un cycle. Le graphe a un cycle si et seulement si le DFS trouve un arc arrière ; et s'il n'en a pas, l'ordre inverse des fins de visite est un ordre topologique.

## Rôle dans un agent

Comme Kahn (étape 44), la détection de cycle sert à l'orchestrateur avant d'**agir**, au chargement d'un workflow ou d'un plan, et aussi comme garde-fou sur des données : un graphe de transactions, d'approbations ou de règles. Kahn est naturel quand on veut l'ordre d'exécution et les vagues ; DFS est naturel quand on veut le cycle lui-même, au moment où on le croise, pour un message d'erreur qui nomme les agents en cause. Les deux lisent chaque arc une fois, en O(n + m). En production, on utilise la version **à pile explicite** : la version récursive, plus lisible, s'effondre dès que le graphe a un chemin plus long que la limite de récursion de Python, 1 000 appels par défaut.

## Équation complète

Couleurs :

$$
\mathrm{couleur}(v) \in \{ \mathrm{Blanc}, \mathrm{Gris}, \mathrm{Noir} \}
$$

Transitions, une seule fois chacune par nœud :

$$
\mathrm{Blanc} \xrightarrow{\text{début de visite}} \mathrm{Gris} \xrightarrow{\text{fin de visite}} \mathrm{Noir}
$$

Arc arrière, condition **datée** (et non une photo des couleurs) :

$$
(u, v) \in E \text{ est un arc arrière} \iff \mathrm{couleur}(v) = \mathrm{Gris} \text{ au moment où } (u, v) \text{ est examiné pendant } \mathrm{dfs}(u)
$$

Théorème :

$$
G \text{ a un cycle} \iff \text{le DFS rencontre un arc arrière}
$$

Ordre topologique d'un DAG, par les fins de visite f(v) :

$$
(u, v) \in E \implies f(v) < f(u) , \qquad \text{ordre} = \text{nœuds rangés par } f \text{ décroissant}
$$

Complexité : O(n + m) en temps, O(n + m) en mémoire.

## Décryptage des symboles

$$
\mathrm{couleur}(v)
$$

**Sens :** état de la visite de v : jamais vu, en cours, fini · **Type / plage :** l'une des trois constantes · **Variable Python :** `couleur[v]`, avec `BLANC, GRIS, NOIR = 0, 1, 2`

$$
(u, v)
$$

**Sens :** un arc examiné pendant la visite de u ; selon la couleur de v à cet instant, c'est un arc d'arbre (v blanc), un arc arrière (v gris) ou un arc vers une branche finie (v noir) · **Type / plage :** élément de E · **Variable Python :** `u` et `v = succ[u][k]`

$$
\mathrm{parent}(v)
$$

**Sens :** le nœud depuis lequel v a été découvert ; les parents des nœuds gris forment le chemin en cours · **Type / plage :** nœud, ou −1 pour une racine · **Variable Python :** `parent[v]`

$$
f(v)
$$

**Sens :** instant de fin de visite de v, c'est-à-dire son rang dans le postordre · **Type / plage :** entier de 1 à n · **Variable Python :** position de v dans `postordre`

$$
n,\; m
$$

**Sens :** nombre de nœuds et nombre d'arcs · **Type / plage :** entiers ≥ 0 · **Variable Python :** `n`, `len(aretes)`

## Démonstration

### 1. Les nœuds gris sont exactement le chemin en cours

Un nœud devient gris quand sa visite commence, c'est-à-dire quand on l'empile (appel `dfs(u)`, ou `pile.append`), et noir quand sa visite finit, c'est-à-dire quand on le dépile. Les nœuds gris sont donc exactement ceux de la pile, dans l'ordre où ils ont été empilés. Chaque nœud de la pile, sauf la racine, a été empilé depuis le nœud juste en dessous, qui est son `parent` : la pile est un chemin parent → enfant de la racine jusqu'au nœud courant.

### 2. Parenthésage : ce qui commence pendant la visite de v finit avant v

Si w devient gris alors que v est gris, w est empilé au-dessus de v. Il sera donc dépilé avant v : la visite de w commence et finit à l'intérieur de celle de v, et w est un **descendant** de v dans l'arbre des parents. Les intervalles de visite de deux nœuds sont donc soit emboîtés, soit disjoints, comme des parenthèses bien formées.

### 3. Arc arrière ⇒ cycle

Supposons que, pendant la visite de u, l'arc (u, v) soit examiné alors que v est gris. Par le point 1, v est sur la pile, au-dessous de u : en remontant les parents depuis u, on atteint v. On a donc un chemin v → … → u formé d'arcs d'arbre, et l'arc u → v le referme : c'est un cycle. La fonction `reconstruire` fait exactement cette remontée.

### 4. Lemme du chemin blanc

Si, à l'instant où v devient gris, il existe un chemin de v vers w dont tous les nœuds (sauf v) sont blancs, alors w devient un descendant de v. Preuve par récurrence le long du chemin v = x₀ → x₁ → … → xₚ = w. Supposons que x₍ᵢ₋₁₎ soit un descendant de v ; sa visite a donc lieu pendant celle de v. Pendant la visite de x₍ᵢ₋₁₎, l'arc (x₍ᵢ₋₁₎, xᵢ) est examiné. Si xᵢ est encore blanc à cet instant, il est découvert depuis x₍ᵢ₋₁₎ et devient un descendant de v. Sinon, xᵢ a été découvert entre le début de la visite de v (où il était blanc) et cet instant, donc pendant que v était gris : par le point 2, c'est aussi un descendant de v.

### 5. Cycle ⇒ arc arrière

Soit C un cycle, et v le **premier** de ses nœuds à devenir gris. À cet instant, tous les autres nœuds de C sont blancs. Soit u le nœud de C qui précède v, avec l'arc u → v. Le chemin v → … → u le long de C est blanc (sauf v) : par le lemme du point 4, u devient un descendant de v, et sa visite a lieu pendant que v est gris. Quand la visite de u examine l'arc (u, v), v est donc gris : c'est un arc arrière. (Le DFS peut s'arrêter avant sur un autre arc arrière ; il a alors trouvé un autre cycle, par le point 3.)

Les points 3 et 5 donnent le théorème : le graphe a un cycle si et seulement si le DFS rencontre un arc arrière. Ignorer un voisin noir ne fait donc rater aucun cycle : si ce voisin appartenait à un cycle, le point 5 garantit qu'un arc de ce cycle a été, ou sera, vu avec un gris.

### 6. Pourquoi la condition doit être datée

L'ancienne version écrivait la condition comme une photo : « il existe un arc (u, v) avec u gris et v gris ». Lue ainsi, elle est fausse. Sur le DAG à un seul arc 0 → 1, au moment où l'on entre dans la visite de 1, les couleurs valent [Gris, Gris] et l'arc (0, 1) a ses deux bouts gris, alors qu'il n'y a aucun cycle : c'est un arc d'arbre, examiné quand 1 était encore blanc. Ce qui compte, c'est la couleur de v **au moment où l'arc est examiné**, pendant la visite de u. Le programme prend cette photo et vérifie que l'ancienne condition se déclenche à tort.

### 7. Sans cycle, le postordre inversé est un ordre topologique

Supposons le graphe sans cycle et prenons un arc (u, v). Il est examiné pendant la visite de u. À cet instant, v ne peut pas être gris, sinon le point 3 donnerait un cycle. S'il est blanc, il est découvert depuis u et finit avant u (point 2). S'il est noir, il a déjà fini. Dans les deux cas, f(v) < f(u). En rangeant les nœuds par fin de visite décroissante, u passe donc avant v pour chaque arc : c'est un ordre topologique.

### 8. Complexité, et la limite de la récursion

Chaque nœud devient gris une fois et noir une fois. La liste des successeurs d'un nœud n'est parcourue que pendant sa visite, qui a lieu une seule fois : chaque arc est examiné au plus une fois. Le temps vaut O(n + m). La mémoire vaut O(n) pour les couleurs, les parents et la pile, plus O(m) pour les listes de successeurs. La pile peut contenir jusqu'à n nœuds, sur un graphe en chaîne. Dans la version récursive, cette pile est la pile d'appels de Python, limitée par défaut à 1 000 appels : une chaîne de 5 000 agents lève `RecursionError`. La version itérative garde la même pile dans une liste, dont la taille n'est limitée que par la mémoire.

### 9. Exemple fait à la main (le code reprend ces nombres)

Trois agents, recherche (0), rédaction (1), validation (2), et les arcs (0, 1), (1, 2), (2, 0).

| Instant | Action | Couleurs | Pile (chemin gris) |
|---|---|---|---|
| 1 | début de 0 | [G, B, B] | 0 |
| 2 | (0, 1) examiné, 1 blanc : parent(1) = 0 | [G, G, B] | 0, 1 |
| 3 | (1, 2) examiné, 2 blanc : parent(2) = 1 | [G, G, G] | 0, 1, 2 |
| 4 | (2, 0) examiné, 0 **gris** : arc arrière | [G, G, G] | 0, 1, 2 |

La reconstruction part de u = 2, remonte parent(2) = 1 puis parent(1) = 0 = v, inverse pour obtenir 0 → 1 → 2, et referme par l'arc 2 → 0 : le cycle est [0, 1, 2, 0]. Sur le graphe (0, 1), (1, 2), (2, 3), (3, 4), (4, 2), (0, 5), l'arc arrière est (4, 2) et le cycle nommé est [2, 3, 4, 2] : les nœuds 0, 1 et 5 n'y figurent pas. Sur le pipeline (0, 2), (1, 2), (2, 3), (3, 4) de l'étape 44, les fins de visite sont 4, 3, 2, 0, puis 1 : le postordre inversé [1, 0, 2, 3, 4] est l'un des deux ordres légaux, avec 4 arcs examinés et 5 fins de visite.

## Effets et comportement

- **Un cycle quelque part, un seul nommé.** Le DFS s'arrête au premier arc arrière : il donne un cycle, pas tous. Après correction, on relance.
- **Les noirs sont ignorés sans risque** (point 5) : c'est ce qui garde le coût linéaire, puisque chaque nœud n'est visité qu'une fois.
- **La profondeur dépend de la forme du graphe**, pas seulement de sa taille : 5 000 agents en chaîne font 5 000 niveaux de pile, 5 000 agents en éventail un seul.
- **DFS ou Kahn ?** Les deux détectent un cycle en O(n + m). DFS nomme le cycle au moment où il le croise et donne un ordre topologique par les fins de visite ; Kahn donne en plus les vagues parallèles.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| couleurs Blanc, Gris, Noir | `BLANC, GRIS, NOIR = 0, 1, 2`, tableau `couleur` |
| successeurs | `successeurs(n, aretes)` |
| parent(v) | `parent[v]` |
| arc arrière, condition datée | `if couleur[v] == GRIS` au moment où `v = succ[u][k]` est examiné |
| cycle exhibé (point 3) | `reconstruire(u, v, parent)` |
| version récursive | `detecter_cycle_dfs(n, aretes)` |
| version à pile, postordre | `detecter_cycle_iteratif(n, aretes, compteur, photos)` |
| ancienne condition, lue comme une photo | `condition_statique(couleur, aretes)` |

Copiez le bloc dans `cycle_dfs.py` et lancez `python cycle_dfs.py`.

### Déroulé, ligne par ligne

**`successeurs(n, aretes)`** construit la liste des successeurs de chaque nœud, en un passage sur les arcs. L'ordre des successeurs suit l'ordre des arcs, ce qui rend le parcours, et donc le cycle nommé, reproductible.

**`reconstruire(u, v, parent)`** est la preuve du point 3. On part de `chemin = [u]` et l'on ajoute `parent[chemin[-1]]` jusqu'à atteindre v ; la boucle s'arrête forcément, puisque v est un ancêtre de u. On inverse pour lire v → … → u, puis on ajoute v à la fin pour refermer le cycle par l'arc u → v.

**`detecter_cycle_dfs(n, aretes)`**, la version récursive, gardée pour sa lisibilité ; l'ancienne version du fichier la définissait sans jamais l'appeler, `main()` l'appelle maintenant et la vérifie.

- `dfs(u)` peint u en gris, puis parcourt `succ[u]`. `if couleur[v] == GRIS` est la condition datée : on est pendant la visite de u, au moment précis où l'arc (u, v) est examiné. On appelle `reconstruire`, on range le cycle dans `trouve`, et l'on renvoie `True` jusqu'en haut.
- `if couleur[v] == BLANC` : on descend, après avoir noté `parent[v] = u`. Un voisin noir est ignoré (point 5).
- Quand tous les successeurs sont traités, `couleur[u] = NOIR`.
- La boucle `for i in range(n)` relance une visite depuis chaque nœud encore blanc, parce qu'un graphe peut avoir plusieurs morceaux.

Sur la boucle (0, 1), (1, 2), (2, 0) : `dfs(0)` peint 0 en gris et descend vers 1, qui descend vers 2 ; le chemin gris est 0 → 1 → 2. L'arc (2, 0) trouve 0 gris, et la reconstruction donne [0, 1, 2, 0].

**`detecter_cycle_iteratif(n, aretes, compteur, photos)`**, la version de production.

- La pile contient des couples `(nœud, k)`, où `k` est le rang du prochain successeur à examiner. C'est ce que la version récursive garde implicitement dans chaque appel : l'endroit où la boucle `for v in succ[u]` s'est arrêtée.
- `u, k = pile[-1]` regarde le sommet sans le retirer. S'il reste un successeur, on écrit d'abord `pile[-1] = (u, k + 1)`, pour reprendre au suivant la prochaine fois, puis on examine `v = succ[u][k]` : gris, c'est un arc arrière et l'on renvoie le cycle ; blanc, on note le parent, on peint v en gris et on l'empile.
- S'il ne reste aucun successeur, la visite de u est finie : `couleur[u] = NOIR`, u est ajouté au `postordre`, et on le dépile.
- `examens` compte les arcs examinés, et `photos` reçoit une copie des couleurs à chaque nœud qui devient gris, pour la démonstration du point 6.
- Sans cycle, la fonction renvoie `postordre[::-1]`, l'ordre topologique du point 7.

**`condition_statique(couleur, aretes)`** applique l'ancienne formule à une photo des couleurs : « existe-t-il un arc dont les deux bouts sont gris ? ». Elle sert seulement à montrer son défaut.

**`main()`**, bloc par bloc.

1. La boucle de trois agents : les deux versions trouvent [0, 1, 2, 0].
2. Un cycle (2, 3, 4) plus loin dans un graphe de six nœuds : seuls les nœuds du cycle sont nommés, [2, 3, 4, 2].
3. Le pipeline de l'étape 44 : pas de cycle, l'ordre [1, 0, 2, 3, 4] est topologique, avec 4 arcs examinés et 5 fins de visite.
4. Le DAG 0 → 1 : la photo prise à l'entrée dans 1 vaut [1, 1], soit [Gris, Gris], et l'ancienne condition se déclenche alors qu'il n'y a pas de cycle.
5. Une chaîne de 5 000 agents : la version récursive lève `RecursionError` (limite 1 000), la version à pile examine 4 999 arcs et renvoie l'ordre 0, 1, 2, … ; avec l'arc (4999, 0) en plus, elle nomme le cycle complet de 5 000 nœuds.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`successeurs(n, aretes)`** — Cette fonction est le standardiste qui dresse, pour chaque agent, la liste de ceux à qui il passe le relais : elle reçoit le nombre n de nœuds et la liste des arcs, prépare une liste vide par nœud, puis, en un seul passage sur les arcs, ajoute chaque destination à la liste de sa source. Elle renvoie ces listes de successeurs, rangées dans l'ordre même des arcs, ce qui rend le parcours en profondeur, et donc le cycle nommé, identique d'une exécution à l'autre ; les deux détecteurs commencent par l'appeler.

**`detecter_cycle_dfs(n, aretes)`** — C'est l'explorateur d'un labyrinthe qui déroule un fil derrière lui et sait qu'il tourne en rond dès qu'il retombe sur son propre fil : la fonction reçoit le nombre de nœuds et les arcs, construit les successeurs, peint tous les nœuds en blanc, prépare le tableau des parents et une liste `trouve` pour le cycle, puis lance la visite récursive `dfs` depuis chaque nœud encore blanc, parce qu'un graphe peut avoir plusieurs morceaux. Elle renvoie `(True, cycle)` dès qu'un arc arrière est trouvé, `[0, 1, 2, 0]` sur la boucle de trois agents, ou `(False, None)` sans cycle ; sur une chaîne de 5 000 agents, elle dépasse la limite de récursion de 1 000 et lève une `RecursionError`.

**`dfs(u)`** — Cette fonction interne vit dans `detecter_cycle_dfs` et représente l'explorateur entrant dans une salle : elle reçoit un nœud u, le peint en gris pour dire qu'il est sur le fil en cours, puis examine chacun de ses successeurs. Si un successeur est gris, l'arc qui y mène est un arc arrière : elle reconstruit le cycle avec `reconstruire`, le range dans `trouve` et renvoie vrai jusqu'en haut ; s'il est blanc, elle note u comme son parent et descend dans ce successeur ; un successeur noir, déjà fini, est ignoré. Une fois tous les successeurs traités, elle peint u en noir et renvoie faux.

**`detecter_cycle_iteratif(n, aretes, compteur, photos)`** — Voici le même explorateur, mais qui tient son fil dans un carnet au lieu de compter sur sa mémoire : la fonction reçoit le nombre de nœuds, les arcs, un dictionnaire facultatif pour ses comptes et une liste facultative de photos, puis gère une pile explicite de couples (nœud, rang du prochain successeur à examiner). À chaque tour, elle regarde le sommet : s'il reste un successeur, elle avance le rang puis l'examine, renvoie `(True, cycle, None)` sur un successeur gris, ou empile un successeur blanc en le peignant en gris et en prenant une photo des couleurs ; sinon, elle peint le nœud en noir, l'ajoute au postordre et le dépile. Sans cycle, elle renvoie `(False, None, ordre)`, avec le postordre inversé comme ordre topologique, et tient sur la chaîne de 5 000 agents.

**`condition_statique(couleur, aretes)`** — Cette fonction est le témoin qui juge sur une seule photo, sans savoir à quel moment elle a été prise : elle reçoit un tableau de couleurs et la liste des arcs, et renvoie vrai s'il existe un arc dont les deux extrémités sont grises au moment de la photo. C'est l'ancienne formule du fichier, conservée seulement pour montrer son défaut : sur le graphe sans cycle 0 → 1, la photo prise à l'entrée dans 1 montre les couleurs `[1, 1]`, deux gris, et la condition se déclenche à tort, parce qu'elle ne regarde pas quand l'arc est examiné.

**`est_ordre_topologique(ordre, aretes)`** — On peut la voir comme le contrôleur qui relit le planning final et vérifie que chaque fournisseur passe avant ceux qu'il alimente : la fonction reçoit un ordre de nœuds et la liste des arcs, construit la position de chaque nœud dans cet ordre et renvoie vrai si, pour chaque arc (u, v), u vient avant v. C'est la même fonction qu'à l'étape 44 ; ici, `main` s'en sert pour vérifier que le postordre inversé de `detecter_cycle_iteratif`, `[1, 0, 2, 3, 4]` sur le pipeline, est bien un ordre topologique.

**`main()`** — Le chef d'orchestre déroule les cinq tableaux du chapitre : il fait trouver par les deux versions le cycle `[0, 1, 2, 0]` de la boucle recherche, rédaction, validation, puis le seul cycle `[2, 3, 4, 2]` caché dans un graphe de six nœuds, et vérifie sur le pipeline sans cycle l'ordre obtenu, avec 4 arcs examinés et 5 fins de visite. Il montre ensuite, sur le graphe 0 → 1, que l'ancienne condition se trompe, puis lance une chaîne de 5 000 agents qui fait tomber la version récursive mais pas la version à pile, laquelle nomme aussi le cycle complet quand on ajoute l'arc (4999, 0) ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 45 — détection de cycle par DFS : trois couleurs, arc arrière, version récursive et version à pile."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BLANC, GRIS, NOIR = 0, 1, 2


def successeurs(n: int, aretes: list[tuple[int, int]]) -> list[list[int]]:
    succ = [[] for _ in range(n)]
    for u, v in aretes:
        succ[u].append(v)
    return succ


def reconstruire(u: int, v: int, parent: list[int]) -> list[int]:
    """L'arc (u, v) arrive sur v, gris, donc ancêtre de u : on remonte les parents de u jusqu'à v."""
    chemin = [u]
    while chemin[-1] != v:
        chemin.append(parent[chemin[-1]])
    chemin.reverse()                                     # v → … → u
    return chemin + [v]                                  # on referme par l'arc u → v


def detecter_cycle_dfs(n: int, aretes: list[tuple[int, int]]):
    """Version récursive, la plus lisible. Limite : une profondeur > sys.getrecursionlimit() la fait tomber."""
    succ = successeurs(n, aretes)
    couleur = [BLANC] * n
    parent = [-1] * n
    trouve = []

    def dfs(u: int) -> bool:
        couleur[u] = GRIS                                # u entre sur le chemin en cours
        for v in succ[u]:
            if couleur[v] == GRIS:                       # arc examiné pendant dfs(u) et v GRIS : arc arrière
                trouve.extend(reconstruire(u, v, parent))
                return True
            if couleur[v] == BLANC:
                parent[v] = u
                if dfs(v):
                    return True
        couleur[u] = NOIR                                # tous les successeurs sont traités
        return False

    for i in range(n):
        if couleur[i] == BLANC and dfs(i):
            return True, trouve
    return False, None


def detecter_cycle_iteratif(n: int, aretes: list[tuple[int, int]], compteur: dict | None = None, photos=None):
    """Même parcours avec une pile explicite de (nœud, rang du prochain successeur).
    Renvoie (True, cycle, None) ou (False, None, ordre topologique = postordre inversé)."""
    succ = successeurs(n, aretes)
    couleur = [BLANC] * n
    parent = [-1] * n
    postordre = []
    examens = 0
    for racine in range(n):
        if couleur[racine] != BLANC:
            continue
        couleur[racine] = GRIS
        pile = [(racine, 0)]
        while pile:
            u, k = pile[-1]
            if k < len(succ[u]):
                pile[-1] = (u, k + 1)                    # au prochain passage, on examinera le successeur suivant
                v = succ[u][k]
                examens += 1
                if couleur[v] == GRIS:                   # arc arrière : v est sur la pile, donc ancêtre de u
                    return True, reconstruire(u, v, parent), None
                if couleur[v] == BLANC:
                    parent[v] = u
                    couleur[v] = GRIS
                    pile.append((v, 0))
                    if photos is not None:
                        photos.append(couleur[:])
            else:
                couleur[u] = NOIR                        # fin de visite de u
                postordre.append(u)
                pile.pop()
    if compteur is not None:
        compteur.update(examens=examens, fins=len(postordre))
    return False, None, postordre[::-1]


def condition_statique(couleur: list[int], aretes: list[tuple[int, int]]) -> bool:
    """L'ancienne formule lue comme une photo : « il existe (u, v) avec u et v gris ». Elle ne regarde pas QUAND."""
    return any(couleur[u] == GRIS and couleur[v] == GRIS for u, v in aretes)


def est_ordre_topologique(ordre: list[int], aretes: list[tuple[int, int]]) -> bool:
    position = {v: k for k, v in enumerate(ordre)}
    return all(position[u] < position[v] for u, v in aretes)


def main() -> None:
    print("1. Le cycle recherche → rédaction → validation → recherche")
    boucle = [(0, 1), (1, 2), (2, 0)]
    a_cycle, cycle = detecter_cycle_dfs(3, boucle)
    print(f"  récursif : cycle = {a_cycle}, chemin = {cycle}")
    a_cycle_it, cycle_it, _ = detecter_cycle_iteratif(3, boucle)
    print(f"  à pile   : cycle = {a_cycle_it}, chemin = {cycle_it}")
    assert a_cycle and cycle == [0, 1, 2, 0] and (a_cycle_it, cycle_it) == (True, [0, 1, 2, 0])

    print("2. Un cycle plus loin dans le graphe : seuls les nœuds du cycle sont nommés")
    graphe = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 2), (0, 5)]
    print(f"  récursif : {detecter_cycle_dfs(6, graphe)[1]}   à pile : {detecter_cycle_iteratif(6, graphe)[1]}")
    assert detecter_cycle_dfs(6, graphe)[1] == detecter_cycle_iteratif(6, graphe)[1] == [2, 3, 4, 2]

    print("3. Sans cycle : aucun gris retrouvé, et le postordre inversé est un ordre topologique")
    pipeline = [(0, 2), (1, 2), (2, 3), (3, 4)]
    compteur = {}
    a_cycle, _, ordre = detecter_cycle_iteratif(5, pipeline, compteur)
    print(f"  cycle = {a_cycle} ; ordre = {ordre} ; {compteur['examens']} arcs examinés, {compteur['fins']} fins de visite")
    assert not a_cycle and detecter_cycle_dfs(5, pipeline) == (False, None)
    assert est_ordre_topologique(ordre, pipeline) and compteur == {"examens": 4, "fins": 5}

    print("4. La condition dépend du moment : sur le DAG 0 → 1, une photo montre 0 et 1 gris")
    photos = []
    detecter_cycle_iteratif(2, [(0, 1)], photos=photos)
    print(f"  photo prise à l'entrée dans 1 : couleurs = {photos[-1]} ; condition statique = {condition_statique(photos[-1], [(0, 1)])}")
    assert condition_statique(photos[-1], [(0, 1)]) and not detecter_cycle_iteratif(2, [(0, 1)])[0]
    print("  la bonne condition : quand l'arc (u, v) est EXAMINÉ pendant dfs(u), v est GRIS")

    print("5. Une chaîne de 5 000 agents dépasse la limite de récursion")
    n = 5000
    chaine = [(i, i + 1) for i in range(n - 1)]
    print(f"  limite de récursion de Python : {sys.getrecursionlimit()}")
    try:
        detecter_cycle_dfs(n, chaine)
    except RecursionError:
        print("  récursif : RecursionError")
    else:
        raise AssertionError("la version récursive aurait dû dépasser la limite")
    compteur = {}
    a_cycle, _, ordre = detecter_cycle_iteratif(n, chaine, compteur)
    print(f"  à pile   : cycle = {a_cycle}, {compteur['examens']} arcs examinés, ordre[:3] = {ordre[:3]}")
    assert not a_cycle and ordre == list(range(n)) and compteur["examens"] == n - 1
    a_cycle, cycle, _ = detecter_cycle_iteratif(n, chaine + [(n - 1, 0)])
    print(f"  avec l'arc ({n - 1}, 0) : cycle de {len(cycle) - 1} nœuds, de {cycle[0]} à {cycle[-2]} puis retour à {cycle[-1]}")
    assert a_cycle and cycle == list(range(n)) + [0]
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Le cycle recherche → rédaction → validation → recherche
  récursif : cycle = True, chemin = [0, 1, 2, 0]
  à pile   : cycle = True, chemin = [0, 1, 2, 0]
2. Un cycle plus loin dans le graphe : seuls les nœuds du cycle sont nommés
  récursif : [2, 3, 4, 2]   à pile : [2, 3, 4, 2]
3. Sans cycle : aucun gris retrouvé, et le postordre inversé est un ordre topologique
  cycle = False ; ordre = [1, 0, 2, 3, 4] ; 4 arcs examinés, 5 fins de visite
4. La condition dépend du moment : sur le DAG 0 → 1, une photo montre 0 et 1 gris
  photo prise à l'entrée dans 1 : couleurs = [1, 1] ; condition statique = True
…
  limite de récursion de Python : 1000
  récursif : RecursionError
  à pile   : cycle = False, 4999 arcs examinés, ordre[:3] = [0, 1, 2]
  avec l'arc (4999, 0) : cycle de 5000 nœuds, de 0 à 4999 puis retour à 0
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un gris retrouvé au moment où l'on examine l'arc est une preuve de cycle, et le programme sait la montrer ; l'absence de gris donne un ordre topologique ; et la version à pile tient là où la récursion s'effondre.

## Squelette algorithmique

L'algorithme principal est le **DFS à pile explicite**, qui prend le nombre de nœuds n et la liste des arcs, et renvoie soit un cycle, soit un ordre topologique. L'idée est de simuler la récursion avec une pile de couples (nœud, rang du prochain successeur) : un nœud est gris tant qu'il est sur la pile, un arc qui mène à un gris referme un cycle que l'on reconstruit en remontant les parents, et l'ordre des fins de visite, inversé, ordonne un graphe sans cycle. La **version récursive** suit le même squelette, la pile étant celle des appels.

```text
ALGORITHME DetecterCycleAPile
ENTRÉES : nombre de nœuds n, arcs (u, v)
SORTIE : (vrai, cycle) ou (faux, ordre topologique)

succ(v) ← successeurs de v, dans l'ordre des arcs, pour chaque v
POUR v DE 0 À n − 1 FAIRE
    couleur(v) ← Blanc ; parent(v) ← aucun
FIN POUR
postordre ← liste vide
POUR racine DE 0 À n − 1 FAIRE
    SI couleur(racine) = Blanc ALORS
        couleur(racine) ← Gris
        pile ← [(racine, 0)]
        TANT QUE pile n'est pas vide FAIRE
            (u, k) ← sommet de pile
            SI k < taille(succ(u)) ALORS
                remplacer le sommet de pile par (u, k + 1)
                v ← succ(u)[k]                          (l'arc (u, v) est examiné maintenant)
                SI couleur(v) = Gris ALORS
                    RETOURNER (vrai, Reconstruire(u, v, parent))
                SINON SI couleur(v) = Blanc ALORS
                    parent(v) ← u ; couleur(v) ← Gris
                    empiler (v, 0)
                FIN SI                                  (v noir : rien à faire)
            SINON
                couleur(u) ← Noir
                ajouter u à postordre
                dépiler
            FIN SI
        FIN TANT QUE
    FIN SI
FIN POUR
RETOURNER (faux, postordre inversé)
```

```text
ALGORITHME Reconstruire
ENTRÉES : arc arrière (u, v), tableau parent
SORTIE : cycle v → … → u → v

chemin ← [u]
TANT QUE dernier(chemin) ≠ v FAIRE
    ajouter parent(dernier(chemin)) à chemin
FIN TANT QUE
inverser chemin                                     (v → … → u)
RETOURNER chemin suivi de v
```

**Complexité :** construire les listes de successeurs lit chaque arc une fois, et l'initialisation des couleurs touche chaque nœud une fois : O(n + m). Dans la boucle, chaque nœud est empilé une fois (quand il passe de Blanc à Gris) et dépilé une fois (quand il passe de Gris à Noir), et chaque passage au sommet de la pile soit examine un arc nouveau, soit dépile : il y a donc au plus n + m tours de la boucle « TANT QUE », chacun en O(1). Le temps total vaut O(n + m). La reconstruction remonte au plus n parents, en O(n). La mémoire vaut O(n) pour les couleurs, les parents, la pile et le postordre, et O(m) pour les successeurs, soit O(n + m) ; la pile atteint n couples sur un graphe en chaîne, ce qui est sans danger dans une liste mais dépasse la limite de récursion dans la version récursive.

**Du squelette au code :** `DetecterCycleAPile` est la fonction `detecter_cycle_iteratif`. La première ligne est l'appel à `successeurs(n, aretes)`. La boucle sur les racines est `for racine in range(n)` avec `if couleur[racine] != BLANC: continue`. « (u, k) ← sommet de pile » est `u, k = pile[-1]`, et « remplacer le sommet » est `pile[-1] = (u, k + 1)`. Le test « couleur(v) = Gris » renvoie `True, reconstruire(u, v, parent), None`, et la branche blanche fait `parent[v] = u`, `couleur[v] = GRIS`, `pile.append((v, 0))`. La branche « SINON » est le bloc `couleur[u] = NOIR`, `postordre.append(u)`, `pile.pop()`. Le retour final est `False, None, postordre[::-1]`. `Reconstruire` est la fonction `reconstruire`. La version récursive `detecter_cycle_dfs` suit le même squelette, la pile étant remplacée par les appels de `dfs(u)` et le rang k par la position de la boucle `for v in succ[u]`.

## Cas d'usage réels aux Émirats

Les volumes, montants et règles ci-dessous sont illustratifs ; les obligations citées par leur nom sont à confirmer avec les textes en vigueur.

### Banque — une double validation qui tourne en rond

Une banque de détail de Dubaï applique le principe des quatre yeux aux virements de plus de 50 000 AED : un agent prépare, un validateur approuve, un contrôleur contre-signe. Les règles sont écrites sous forme de dépendances entre étapes, et un paramétrage ajoute par erreur « le validateur attend la contre-signature du contrôleur », alors que le contrôleur attend déjà le validateur. Au chargement, le DFS examine l'arc contrôleur → validateur au moment où le validateur est gris : il nomme le cycle [validateur, contrôleur, validateur] dans le message d'erreur, et la règle est refusée avant d'atteindre la production. Sans ce contrôle, chaque virement concerné resterait en attente indéfiniment, et les clients verraient des paiements bloqués sans explication. Le message qui nomme les deux étapes permet à l'équipe de corriger en minutes une erreur qui, signalée par un simple « cycle détecté », aurait demandé de relire tout le paramétrage. On suit le nombre de règles refusées au chargement et le délai de leur correction.

### Assurance — une référence circulaire dans les règles de calcul

Un assureur auto et santé calcule ses indemnités par des règles qui dépendent les unes des autres, comme les cellules d'un tableur : la franchise dépend du montant indemnisable, le montant indemnisable de la vétusté, et une nouvelle règle fait dépendre la vétusté de la franchise. Le graphe des règles contient alors une référence circulaire. Le DFS sur le graphe des formules la trouve et la nomme, franchise → vétusté → montant indemnisable → franchise, comme le ferait un tableur, et l'outil de publication refuse la règle. Sans cette vérification, le moteur de calcul tournerait sans fin ou, pire, prendrait une valeur intermédiaire arbitraire et verserait un montant faux. L'assurance est supervisée par la CBUAE, qui attend des règles d'indemnisation documentées et appliquées de façon cohérente : chaque version du graphe de règles est vérifiée et archivée. On suit le nombre de règles refusées et l'écart entre les montants calculés et les montants recalculés à la main sur un échantillon.

### Crypto — repérer des allers-retours dans un graphe de transferts

Une plateforme d'actifs virtuels agréée par la VARA analyse chaque jour le graphe de ses transferts internes : environ 200 000 adresses et 1,2 million de transferts sur 24 heures, dans cet exemple. Un aller-retour A → B → C → A en quelques heures est un signal classique de transactions circulaires, qui peut masquer l'origine des fonds. Le DFS à pile explicite parcourt ce graphe en O(n + m), soit de l'ordre de 1,4 million d'opérations, et nomme un cycle dans chaque composante analysée ; la version récursive tomberait dès qu'une chaîne de transferts dépasse 1 000 adresses. Un cycle n'est pas une preuve : c'est une alerte que l'agent transmet à un analyste avec les montants et les horodatages, et que l'analyste qualifie. Les obligations de lutte contre le blanchiment de la plateforme imposent de documenter cette surveillance et ses suites. On suit le nombre d'alertes de cycle par jour et la part d'entre elles que les analystes confirment.

### RH — une chaîne d'approbation qui revient sur elle-même

Un cabinet RH présent dans plusieurs émirats achemine les demandes de congé et les attestations par la chaîne hiérarchique enregistrée dans son système : chaque salarié a un responsable, qui approuve. Une erreur de saisie déclare A responsable de B alors que B est déjà responsable de A : une demande de A part vers B, qui la renvoie vers A, et ainsi de suite. Le DFS sur le graphe « est approuvé par » détecte le cycle [A, B, A] au moment de l'import des données, et l'agent bloque l'import de ces deux fiches au lieu de laisser des demandes tourner en boucle. Pour un organigramme de 10 000 salariés, la profondeur reste petite, mais les chaînes de délégation temporaire peuvent s'allonger : la version à pile évite toute surprise. Les demandes liées aux visas et aux démarches du MOHRE ont des délais à tenir, ce qui rend une boucle silencieuse coûteuse. On suit le nombre de fiches bloquées à l'import et le délai moyen d'approbation.

### Secteur public — deux certificats qui s'exigent l'un l'autre

Une entité de services publics en ligne, accessible par UAE Pass, publie un catalogue de démarches en arabe et en anglais, chacune avec ses pièces exigées. Une mise à jour du catalogue fait exiger, pour obtenir un certificat A, le certificat B, et pour obtenir B, le certificat A : un usager qui n'a aucun des deux ne peut en obtenir aucun. Le DFS lancé à chaque publication du catalogue trouve le cycle [A, B, A] et bloque la publication de la mise à jour, avec les deux démarches nommées dans le rapport. Sans ce contrôle, l'agent conversationnel répondrait en boucle « il vous faut d'abord le certificat B », puis « il vous faut d'abord le certificat A », et l'usager abandonnerait. La PDPL impose de ne demander que les pièces nécessaires : le même graphe sert à vérifier qu'aucune pièce n'est exigée sans raison. On suit le nombre de publications bloquées et le taux d'abandon des démarches concernées.

## Pièges et limites

- **Lire la condition comme une photo des couleurs.** Un arc d'arbre a ses deux bouts gris pendant la visite de son extrémité ; seule compte la couleur de v au moment où l'arc (u, v) est examiné.
- **Déployer la version récursive.** Elle tombe sur `RecursionError` au-delà de 1 000 niveaux ; relever la limite avec `sys.setrecursionlimit` déplace le problème vers un plantage de l'interpréteur. La version à pile est la seule sûre.
- **Oublier de relancer depuis chaque nœud blanc.** Un graphe peut avoir plusieurs morceaux : une seule visite depuis le nœud 0 rate les cycles des autres morceaux.
- **Confondre un cycle et tous les cycles.** Le DFS en nomme un ; le nombre de cycles d'un graphe peut être exponentiel, et les énumérer tous demande d'autres algorithmes.
- **Croire qu'un cycle est toujours une erreur.** Dans un graphe de contrôle d'agent, une boucle bornée est voulue (étape 42) ; dans des données de transactions, un cycle est un signal à qualifier, pas une preuve.

### Exercice feuille blanche

1. Sans regarder le code, écrire `detecter_cycle_iteratif` avec une pile de couples (nœud, rang), puis vérifier le cycle [0, 1, 2, 0] et l'ordre [1, 0, 2, 3, 4] du pipeline.
2. Prédire, puis vérifier : sur le graphe (0, 1), (0, 2), (2, 1), quels arcs sont des arcs d'arbre, et l'arc (2, 1) est-il un arc arrière ? Quel ordre topologique sort ? (Réponse : (0, 1) et (0, 2) sont des arcs d'arbre ; quand (2, 1) est examiné, 1 est déjà noir, donc ce n'est pas un arc arrière et il n'y a pas de cycle. Les fins de visite sont 1, 2, 0, et l'ordre est [0, 2, 1].)
3. Trouver le bug : une variante teste `if couleur[v] != BLANC` au lieu de `if couleur[v] == GRIS` pour signaler un cycle. Que répond-elle sur le graphe de l'exercice 2 ? (Réponse : elle signale un cycle à tort, parce qu'elle prend le voisin noir 1 pour un gris.)

## Pour aller plus loin

- **Composantes fortement connexes.** Les algorithmes de Tarjan et de Kosaraju, construits sur le DFS, regroupent en O(n + m) tous les nœuds qui appartiennent à un même cycle : utile pour signaler en une fois tous les agents pris dans des boucles, et pas seulement le premier cycle trouvé.
- **Énumérer les cycles.** L'algorithme de Johnson énumère tous les cycles élémentaires en un temps proportionnel à leur nombre ; en surveillance de transactions, on se limite aux cycles courts et rapides.
- **Classification des arcs.** Pendant un DFS, un arc est d'arbre, arrière, avant (vers un descendant déjà fini) ou transverse (vers une autre branche finie) ; seuls les arcs arrière signalent un cycle.

> Suite : [Journal d'événements partitionné (à la manière de Kafka)](<45b-Journal-d-Evenements-Partitionne.md>) — étape 45 bis.
