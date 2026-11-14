# Étape 43 — Théorie des Graphes Orientés Acycliques (DAG), Matrices d'Adjacence et Tri Topologique

> Étape 43 du parcours · Prérequis : [Graphes orientés acycliques et matrices d'adjacence](<42-Orchestration-Graphes.md>) · Suite : [Tri topologique : l'algorithme de Kahn](<44-Tri-Topologique-Kahn.md>)

**Dossier :** 08-Orchestration

À l'étape 43, on lit les sections 1 à 7 et le squelette algorithmique qui les suit. Après, le fichier contient des copies d'autres chapitres (évaluation, attention, LoRA, files d'attente, coûts) qui se lisent aux étapes indiquées en fin de section 7.

## 1. Contextualisation et Rôle dans l'Orchestration Multi-Agents

Dans les frameworks d'orchestration multi-agents modernes (LangGraph, CrewAI, AutoGen, Temporal), la coordination entre agents ne peut pas s'effectuer de manière totalement désordonnée sans risquer des **boucles d'exécution infinies**, des **blocages** (deadlocks, où des tâches s'attendent mutuellement) ou des surcoûts d'API imprévus. Ces frameworks autorisent des boucles dans le graphe de contrôle d'un agent, à condition de les borner (par exemple par une limite de récursion) ; c'est le graphe des **dépendances** entre tâches qui doit être acyclique (étape 42).

Un workflow agentique est modélisé comme un **Graphe Orienté (Directed Graph)** G = (V, E), où les nœuds V représentent des agents ou des fonctions d'outils (Tools), et les arêtes E représentent le flux de données ou de contrôle entre eux.

Un **AI Agentic Developer** doit maîtriser la théorie des graphes pour :
* Démontrer formellement qu'un pipeline d'agents est **acyclique (DAG)** et ne peut pas boucler à l'infini.
* Paralléliser l'exécution des tâches d'agents indépendants via un **tri topologique**.
* Détecter dynamiquement les cycles dans les graphes d'état avec des vérifications spectrales sur la matrice d'adjacence.

---

## 2. Définition Mathématique Formelle

Soit G = (V, E) un graphe orienté comportant |V| = n nœuds et |E| = m arêtes.

### A. Matrice d'Adjacence

La **matrice d'adjacence**

$$
A \in \{0, 1\}^{n \times n}
$$

du graphe G est la matrice carrée définie par :

$$
A_{i,j} = \begin{cases} 1 & \text{si } (v_i, v_j) \in E \quad (\text{flux de l'agent } i \text{ vers l'agent } j) \\ 0 & \text{sinon} \end{cases}
$$

### B. Définition d'un DAG (Directed Acyclic Graph)

Un graphe orienté G est dit **acyclique** s'il ne existe aucun chemin orienté non trivial (v₀, v₁, …, vₖ) tel que v₀ = vₖ avec k ≥ 1.

---

## 3. Démonstration Mathématique : Condition d'Acyclicité et Matrice Nilpotente

### Théorème (Caractérisation Spectrale et Nilpotence d'un DAG) :

Un graphe orienté G à n nœuds est un DAG si et seulement si sa matrice d'adjacence A est **nilpotente**, c'est-à-dire qu'il existe un entier k ≤ n tel que :

$$
A^k = 0_{n \times n}
$$

De manière équivalente, toutes les valeurs propres de A sont nulles (Sp(A) = {0}), et la trace de toutes ses puissances est nulle :

$$
\forall k \in \{1, 2, \dots, n\}, \quad \text{Tr}(A^k) = 0
$$

### Démonstration Étape par Étape :

1. **Signification géométrique de (Aᵏ)ᵢ,ⱼ** :
   Par récurrence sur k, le terme (Aᵏ)ᵢ,ⱼ de la k-ième puissance de la matrice d'adjacence correspond exactement au **nombre de marches orientées de longueur k** reliant le nœud vᵢ au nœud vⱼ. Une marche est une suite de k arcs qui s'enchaînent, où l'on a le droit de repasser par un même nœud ; un chemin est une marche qui ne repasse jamais par un nœud.

   * Pour k=1, (A¹)ᵢ,ⱼ = Aᵢ,ⱼ (marches directes de longueur 1, c'est-à-dire les arcs).
   * Supposons le résultat vrai au rang k−1. Alors :

$$
(A^k)_{i,j} = \sum_{l=1}^{n} (A^{k-1})_{i,l} A_{l,j}
$$

Cette somme compte toutes les marches de longueur k−1 allant de i à l, prolongées par une arête de l à j. Le résultat s'étend donc au rang k.

2. **Interprétation de la Trace Tr(Aᵏ)** :
   La trace d'une matrice étant la somme des éléments diagonaux :

$$
\text{Tr}(A^k) = \sum_{i=1}^{n} (A^k)_{i,i}
$$

(Aᵏ)ᵢ,ᵢ représente le nombre de marches de longueur k partant du nœud i et **revenant au nœud i** : ce sont des **marches fermées**, pas forcément des cycles. Une marche fermée peut repasser plusieurs fois par le même nœud : avec un seul cycle 0 → 1 → 0, on trouve Tr(A²) = 2 et aussi Tr(A⁴) = 2, alors qu'il n'existe aucun cycle de longueur 4 (étape 42, démonstration, point 2). La trace dit seulement s'il existe ou non une marche fermée de longueur k.

3. **Condition Nécessaire et Suffisante** :
   * Si G contient un cycle de longueur k (forcément k ≤ n, puisqu'un cycle ne repasse par aucun nœud), alors (Aᵏ)ᵢ,ᵢ ≥ 1 pour tout i dans le cycle, donc Tr(Aᵏ) > 0.
   * Si G est acyclique, aucune marche ne peut revenir à son point de départ, parce qu'une marche fermée contient toujours un cycle (le morceau entre deux passages au premier nœud répété). Par conséquent, pour tout k ≥ 1, Tr(Aᵏ) = 0.
   * De plus, dans un DAG à n nœuds, une marche ne repasse jamais par un nœud : c'est un chemin, et le plus long comporte au maximum n−1 arêtes. Ainsi, aucune marche de longueur k ≥ n ne peut exister. Réciproquement, si G a un cycle, on peut le parcourir indéfiniment : Aᵏ ≠ 0 pour une infinité de k, et A n'est pas nilpotente. Dans un DAG, on a donc

$$
A^n = 0_{n \times n} .
$$

*CQFD.*

---

## 4. Tri Topologique et Algorithme de Kahn (Parallélisation des Agents)

Un **tri topologique** d'un DAG est une permutation

$$
(v_{\pi(1)}, v_{\pi(2)}, \dots, v_{\pi(n)})
$$

des nœuds telle que pour toute arête (vᵢ, vⱼ) ∈ E, i apparaît avant j dans l'ordre (π(i) < π(j)).

### Algorithme de Kahn (Complexité O(|V| + |E|)) :

1. Calculer le degré entrant dᵢₙ(v) de chaque nœud v ∈ V.
2. Initialiser une file d'attente Q contenant tous les nœuds de degré entrant nul (dᵢₙ(v) = 0). Ces nœuds sont les agents indépendants pouvant s'exécuter **en parallèle**.
3. Tant que Q n'est pas vide :
   * Extraire un nœud u de Q.
   * Pour chaque voisin v tel que (u, v) ∈ E :
     * Décrémenter dᵢₙ(v) ← dᵢₙ(v) − 1.
     * Si dᵢₙ(v) == 0, ajouter v à Q.
4. Si le nombre de nœuds traités est inférieur à n, le graphe contient au moins un cycle (ce n'est pas un DAG).

Cette section décrit l'algorithme sans le démontrer. La preuve qu'il ordonne tout DAG (tout DAG fini a une source) et qu'il détecte tout cycle (s'il s'arrête trop tôt, chaque nœud restant a un degré entrant au moins 1, ce qui force un cycle), ainsi que le calcul de sa complexité O(|V| + |E|), sont à l'[étape 44](<44-Tri-Topologique-Kahn.md>). La somme des maxima des vagues n'est qu'une borne supérieure de la durée : le vrai chemin critique se calcule à l'[étape 42](<42-Orchestration-Graphes.md>), démonstration, points 6 et 7.

---

## 5. Cas d'Usage Réels et Quantifiés en Entreprise

### Cas A : Pipeline Multi-Agents d'Analyse Financière (Orchestration LangGraph)

#### Architecture du Workflow :
* **Nœud 1 (Agent Scraper)** : Extrait les rapports 10-K.
* **Nœud 2 (Agent SEC-RAG)** : Analyse les risques réglementaires (dépend de 1).
* **Nœud 3 (Agent Sentiment)** : Analyse le sentiment des conférences téléphoniques (dépend de 1).
* **Nœud 4 (Agent Rédacteur Final)** : Synthétise le rapport (dépend de 2 et 3).

#### Implémentation et Calcul de Gain par Parallélisation :

La matrice d'adjacence de ce pipeline à 4 nœuds est :

$$
A = \begin{pmatrix} 0 & 1 & 1 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 0 \end{pmatrix}
$$

* Vérification d'acyclicité :

$$
A^2 = \begin{pmatrix} 0 & 0 & 0 & 2 \\ 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 \end{pmatrix} ,
$$

et

$$
A^3 = 0_{4 \times 4} .
$$

Le graphe est bien un DAG.
* Les nœuds 2 et 3 ont une dépendance uniquement vers le nœud 1. Une fois le nœud 1 exécuté, les agents 2 et 3 sont lancés simultanément sur des threads distants.

#### Résultat Quantifié :

Les durées sont illustratives. Ici, la somme des maxima des vagues coïncide avec le vrai chemin critique, parce que la plus lente de chaque vague (scraper, SEC-RAG, rédacteur) se trouve sur un même chemin.

* Temps d'exécution séquentiel :

$$
T_{\text{seq}} = t_1 + t_2 + t_3 + t_4 = 4.2\text{ s} + 6.1\text{ s} + 5.8\text{ s} + 3.1\text{ s} = 19.2\text{ s} .
$$

* Temps d'exécution parallèle (DAG) :

$$
T_{\text{DAG}} = t_1 + \max(t_2, t_3) + t_4 = 4.2\text{ s} + 6.1\text{ s} + 3.1\text{ s} = 13.4\text{ s} .
$$

* **Gain de latence global** : **−30.2%** sur chaque rapport généré.

---

## 6. Synthèse des Bonnes Pratiques

| Concept Mathématique | Risque si Ignoré | Implémentation Requise |
| --- | --- | --- |
| **Graphe Cyclique (Aᵏ ≠ 0)** | Agent bloqué dans une boucle infinie d'appels LLM (facturation API incontrôlée). | Ajouter un vérificateur topologique à l'initialisation du workflow. |
| **Degré entrant dᵢₙ = 0** | Sous-utilisation des ressources informatiques. | Exécuter simultanément tous les nœuds de degré entrant nul via `asyncio.gather`. |
| **Max Depth Limit** | Graphique géant entraînant des temps de complétion excessivement longs. | Définir une récurrence maximale kₘₐₓ dans les sous-graphes dynamiques. |

## 7. Du symbole au code : chemins, trace, nilpotence, Kahn

(Aᵏ)ᵢⱼ compte les marches de longueur k. Le déroulé calcule une case de A² à la main, puis la trace, puis les vagues de Kahn. Copiez dans `fondements_dag.py`.

### Déroulé, ligne par ligne

Même pipeline que le chapitre 4 : `scraper=0`, `sec_rag=1`, `sentiment=2`, `redacteur=3`. `A[0] = [0, 1, 1, 0]`, `A[1] = A[2] = [0, 0, 0, 1]`, `A[3] = [0, 0, 0, 0]`.

**`matmul`** — `C[i][j] = sum(A[i][l] * B[l][j] for l in range(n))`. Pour une matrice d'adjacence, ce produit vaut le nombre de façons de faire un pas dans A puis un pas dans B. `puissance(A, k)` appelle ça `k - 1` fois. `trace` somme `M[i][i]`.

**La case (A²)[scraper, redacteur], écrite sans appeler `matmul`.**

- `termes` parcourt `l` de 0 à 3 et retient le couple `(A[0][l], A[l][3])`.
- `l = scraper` : 0 × 0 = 0. Pas d'arête scraper → scraper, et pas d'arête scraper → rédacteur.
- `l = sec_rag` : 1 × 1 = 1. Il y a l'arête scraper → sec_rag et l'arête sec_rag → rédacteur.
- `l = sentiment` : 1 × 1 = 1. Le deuxième chemin.
- `l = redacteur` : 0 × 0 = 0.
- `sum(g * d ...)` vaut 2. C'est exactement ce que la ligne `C[i][j] += ...` de `matmul` ferait pour cette case. La boucle du code est cette somme de quatre termes.

**Les traces.**

- `puissance(A, 1)` renvoie A. Diagonale nulle, trace 0.
- `puissance(A, 2)` a un 2 en haut à droite et des 0 ailleurs, y compris sur la diagonale. Trace 0 : les deux chemins arrivent au rédacteur, ils ne reviennent pas au scraper.
- `puissance(A, 3)` et `puissance(A, 4)` sont des matrices de zéros. Il n'existe aucun chemin de longueur 3. Le plus long chemin simple a 2 arêtes, et n = 4, donc Aⁿ est nulle, comme le dit le théorème.

**Le cycle.** `cycle[0][3] = 1` et `cycle[3][0] = 1` : scraper → rédacteur → scraper.

- `puissance(cycle, 2)` a des 1 sur la diagonale des nœuds 0 et 3. `trace` vaut 2 : deux marches fermées de longueur 2, une en partant de chaque bout, pour un seul cycle. La trace positive est le test : ce graphe n'est pas un DAG.

**`kahn(aretes, n)`.**

- `entrant` compte les arêtes qui arrivent. Au départ `[0, 1, 1, 2]`.
- `vague` garde les indices dont le degré vaut 0. Premier tour : `[0]`, le scraper.
- On décrémente les successeurs. sec_rag et sentiment tombent à 0 et forment la vague suivante. Leurs deux décrémentations font tomber le rédacteur de 2 à 0. Il forme la dernière vague.
- `t_seq = sum(durees)` vaut 4,2+6,1+5,8+3,1 = 19,2.
- `t_dag` somme le `max` de chaque vague : 4,2 + max(6,1 ; 5,8) + 3,1 = 13,4. Le `max` est le temps d'attente de la vague : les deux analystes partent ensemble, on paie le plus lent. Cette somme est en général une borne supérieure du chemin critique ; elle lui est égale ici (voir la section 5).
- `kahn([(0, 3), (3, 0)], 4)` renvoie `(None, None)`. Les nœuds 0 et 3 se pointent l'un l'autre, leur degré ne tombe jamais à 0, et `len(ordre) != n`. Le programme refuse de donner un ordre plutôt que d'en inventer un.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`matmul(A, B)`** — Cette fonction est le recenseur des trajets en deux temps, qui compte pour chaque couple de nœuds toutes les façons de faire un pas dans A puis un pas dans B : elle reçoit deux matrices carrées de même taille n, prépare une matrice de zéros, puis remplit chaque case (i, j) par la somme des produits A[i][l] × B[l][j] sur tous les intermédiaires l. Elle renvoie le produit A B ; sur la matrice d'adjacence du pipeline, la case scraper-rédacteur de A² vaut 2, exactement la somme des quatre termes 0, 1, 1 et 0 que `main` écrit à la main.

**`puissance(A, k)`** — On peut la voir comme un marcheur qui prolonge ses itinéraires d'un pas à chaque tour : la fonction reçoit une matrice d'adjacence A et un entier k, part de A elle-même, puis la multiplie par A encore k − 1 fois grâce à `matmul`. Elle renvoie Aᵏ, dont chaque case compte les marches de longueur k ; sur le pipeline, A² a un 2 en haut à droite et des zéros ailleurs, tandis que A³ et A⁴ sont entièrement nulles, la nilpotence qui prouve l'absence de cycle. Elle ne vérifie pas que k vaut au moins 1.

**`trace(M)`** — Ce petit utilitaire est le gardien qui ne compte que les promeneurs revenus à leur point de départ : il reçoit une matrice carrée M et renvoie la somme de ses coefficients diagonaux. Sur une puissance Aᵏ, ce nombre est celui des marches fermées de longueur k ; il vaut 0 pour A et A² du pipeline, mais 2 pour le carré de la matrice du cycle scraper → rédacteur → scraper, une marche fermée en partant de chaque bout, et cette trace positive suffit à refuser le graphe comme DAG.

**`kahn(aretes, n)`** — C'est le chef d'équipe qui fait partir les agents par vagues, chacun dès que tous ceux qui l'alimentent ont fini : la fonction reçoit la liste des arcs et le nombre n de nœuds, compte les arcs qui arrivent sur chaque nœud, forme la première vague des nœuds sans prérequis, puis, vague après vague, ajoute leurs nœuds à l'ordre et décrémente leurs successeurs, qui rejoignent la vague suivante en tombant à 0. Elle renvoie l'ordre et les vagues, le scraper, puis les deux analystes, puis le rédacteur, ou `(None, None)` quand un cycle empêche de tout ordonner, comme pour les arcs (0, 3) et (3, 0).

**`main()`** — Le chef d'orchestre déroule la démonstration sur le pipeline de quatre agents : il écrit à la main les quatre termes de la case (A²)[scraper, rédacteur] et vérifie qu'ils somment à 2, affiche les traces et les puissances de A pour k de 1 à 4 et constate que A³ et A⁴ sont nulles, puis montre que la trace du carré d'un cycle est positive. Il fait enfin tourner `kahn`, vérifie les trois vagues, calcule 19,2 secondes en séquentiel contre 13,4 secondes par vagues, soit 30,2 % de gain, et s'assure que le cycle est refusé ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Fondements DAG — puissances de la matrice d'adjacence, trace, Kahn par vagues."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def matmul(A, B):
    n = len(A)
    C = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            C[i][j] = sum(A[i][l] * B[l][j] for l in range(n))
    return C


def puissance(A, k):
    R = A
    for _ in range(k - 1):
        R = matmul(R, A)
    return R


def trace(M):
    return sum(M[i][i] for i in range(len(M)))


def kahn(aretes, n):
    """Retourne (ordre, vagues) ou (None, None) si un cycle empêche de tout ordonner."""
    entrant = [0] * n
    suivants = [[] for _ in range(n)]
    for i, j in aretes:
        suivants[i].append(j)
        entrant[j] += 1
    vague = [i for i in range(n) if entrant[i] == 0]
    ordre, vagues = [], []
    while vague:
        vagues.append(list(vague))
        prochaine = []
        for u in vague:
            ordre.append(u)
            for v in suivants[u]:
                entrant[v] -= 1
                if entrant[v] == 0:
                    prochaine.append(v)
        vague = prochaine
    if len(ordre) != n:
        return None, None
    return ordre, vagues


def main():
    noms = ["scraper", "sec_rag", "sentiment", "redacteur"]
    A = [
        [0, 1, 1, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 0],
    ]
    print("=== (A^k)_ij = nombre de marches de longueur k ===")
    # Étape de récurrence du cours, écrite sur i=0, j=3, k=2 :
    # (A²)_03 = Σ_l (A)_0l (A)_l3
    termes = [(l, A[0][l], A[l][3]) for l in range(4)]
    print("  (A²)[scraper, redacteur] = Σ_l A[scraper, l] × A[l, redacteur]")
    for l, gauche, droite in termes:
        print(f"    l = {noms[l]:12s}  {gauche} × {droite} = {gauche * droite}")
    assert sum(g * d for _, g, d in termes) == 2

    print("\n=== Trace de chaque puissance, puis nilpotence ===")
    for k in range(1, 5):
        Ak = puissance(A, k)
        print(f"  k = {k}  Tr(A^k) = {trace(Ak)}   matrice = {Ak}")
    assert trace(puissance(A, 1)) == 0
    assert trace(puissance(A, 2)) == 0
    assert all(v == 0 for ligne in puissance(A, 3) for v in ligne)
    assert all(v == 0 for ligne in puissance(A, 4) for v in ligne)

    print("\n=== Le même test sur un cycle scraper → redacteur → scraper ===")
    cycle = [
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 0, 0, 0],
    ]
    print(f"  Tr(C²) = {trace(puissance(cycle, 2))}  (> 0 : deux marches fermées de 2 pas, un seul cycle)")
    assert trace(puissance(cycle, 2)) > 0

    print("\n=== Kahn : degré entrant nul = agents qui partent dans la même vague ===")
    aretes = [(0, 1), (0, 2), (1, 3), (2, 3)]
    ordre, vagues = kahn(aretes, 4)
    durees = [4.2, 6.1, 5.8, 3.1]
    for vague in vagues:
        print(f"  ensemble {{ {', '.join(noms[i] for i in vague)} }}")
    t_seq = sum(durees)
    t_dag = sum(max(durees[i] for i in vague) for vague in vagues)
    print(f"  T_seq = {t_seq:.1f} s")
    print(f"  T_DAG = {durees[0]} + max({durees[1]}, {durees[2]}) + {durees[3]} = {t_dag:.1f} s")
    print(f"  gain = {(1 - t_dag / t_seq) * 100:.1f} %")
    assert [[noms[i] for i in vague] for vague in vagues] == [
        ["scraper"],
        ["sec_rag", "sentiment"],
        ["redacteur"],
    ]
    assert abs(t_seq - 19.2) < 1e-6 and abs(t_dag - 13.4) < 1e-6
    assert kahn([(0, 3), (3, 0)], 4) == (None, None)
    print("A³ = 0 sur le pipeline, trace non nulle sur le cycle, Kahn refuse le cycle.")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== (A^k)_ij = nombre de marches de longueur k ===
    l = sec_rag       1 × 1 = 1
    l = sentiment     1 × 1 = 1
…
  k = 2  Tr(A^k) = 0   matrice = [[0, 0, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
  k = 3  Tr(A^k) = 0   matrice = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
…
  Tr(C²) = 2  (> 0 : deux marches fermées de 2 pas, un seul cycle)
…
  ensemble { scraper }
  ensemble { sec_rag, sentiment }
  ensemble { redacteur }
  T_seq = 19.2 s
  T_DAG = 4.2 + max(6.1, 5.8) + 3.1 = 13.4 s
  gain = 30.2 %
A³ = 0 sur le pipeline, trace non nulle sur le cycle, Kahn refuse le cycle.
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

Le programme enchaîne deux vérifications sur un graphe d'agents. La **vérification par les puissances** prend la matrice d'adjacence A (n × n) et renvoie, pour chaque k de 1 à n, la trace de Aᵏ, puis conclut : DAG si toutes les traces sont nulles et si Aⁿ = 0. L'idée est la section 3 : (Aᵏ)ᵢ,ⱼ compte les marches de longueur k, la trace compte les marches fermées, et un DAG n'en a aucune. Le **tri de Kahn par vagues** prend la liste des arcs et renvoie les vagues de nœuds qui peuvent partir ensemble, ou un échec s'il y a un cycle ; l'idée est de retirer à chaque tour tous les nœuds dont le degré entrant restant est nul. La durée par vagues additionne la plus lente de chaque vague.

```text
ALGORITHME VerifierParPuissances
ENTRÉES : matrice d'adjacence A de taille n × n
SORTIE : vrai si le graphe est un DAG, faux sinon

P ← A
POUR k DE 1 À n FAIRE
    SI Σ sur i de P[i][i] > 0 ALORS
        RETOURNER faux                          (une marche fermée de longueur k existe)
    FIN SI
    SI k < n ALORS
        P ← P × A                               (P[i][j] ← Σ sur l de P[i][l] × A[l][j])
    FIN SI
FIN POUR
RETOURNER vrai                                  (et alors Aⁿ = 0)
```

```text
ALGORITHME KahnParVagues
ENTRÉES : arcs (i, j), nombre de nœuds n, durées d(v)
SORTIE : vagues et durée par vagues, ou échec si cycle

POUR chaque nœud v FAIRE
    entrant(v) ← 0
    suivants(v) ← liste vide
FIN POUR
POUR chaque arc (i, j) FAIRE
    ajouter j à suivants(i)
    entrant(j) ← entrant(j) + 1
FIN POUR
vague ← { v : entrant(v) = 0 }
vagues ← liste vide ; traités ← 0
TANT QUE vague n'est pas vide FAIRE
    ajouter vague à vagues
    prochaine ← liste vide
    POUR chaque u de vague FAIRE
        traités ← traités + 1
        POUR chaque v de suivants(u) FAIRE
            entrant(v) ← entrant(v) − 1
            SI entrant(v) = 0 ALORS
                ajouter v à prochaine
            FIN SI
        FIN POUR
    FIN POUR
    vague ← prochaine
FIN TANT QUE
SI traités < n ALORS
    RETOURNER échec                             (cycle : des nœuds ne sont jamais prêts)
FIN SI
RETOURNER vagues, Σ sur les vagues W de max sur v ∈ W de d(v)
```

**Complexité :** la vérification par les puissances fait au plus n − 1 produits de matrices n × n ; chaque produit a n² cases, et chaque case est une somme de n termes, d'où O(n³) par produit et O(n⁴) en tout, plus O(n) par trace. Elle garde deux matrices, soit O(n²) en mémoire. Kahn lit chaque arc une fois pour construire `suivants` et `entrant`, puis une fois pour décrémenter, et traite chaque nœud une fois : O(n + m) en temps pour n nœuds et m arcs, et O(n + m) en mémoire pour les listes de suivants, les compteurs et les vagues. La durée par vagues ajoute un passage sur les nœuds, O(n). C'est pourquoi la matrice sert à démontrer et Kahn à vérifier en production.

**Du squelette au code :** « P ← P × A » est la fonction `matmul`, dont la ligne `C[i][j] = sum(A[i][l] * B[l][j] for l in range(n))` est exactement la somme écrite en commentaire. Le programme ne garde pas P d'un tour à l'autre : il appelle `puissance(A, k)` pour chaque k, qui refait les k − 1 produits, et teste `trace(...)` sur le résultat ; le pseudo-code donne la version économe. La conclusion « Aⁿ = 0 » est vérifiée par les deux `assert` sur `puissance(A, 3)` et `puissance(A, 4)`. `KahnParVagues` est la fonction `kahn` : les deux premières boucles sont la construction de `entrant` et `suivants`, la ligne « vague ← … » est `[i for i in range(n) if entrant[i] == 0]`, la boucle « TANT QUE » est `while vague`, la décrémentation est `entrant[v] -= 1`, et le test « traités < n » est `if len(ordre) != n`, qui renvoie `(None, None)`. La durée par vagues est la ligne `t_dag = sum(max(durees[i] for i in vague) for vague in vagues)` de `main`.

> Suite : [Tri topologique : l'algorithme de Kahn](<44-Tri-Topologique-Kahn.md>) — étape 44. La suite de ce fichier n'appartient pas à l'étape 43.

Les sections 5 à 9 recopiées plus bas dans ce fichier ont leur programme exécutable dans les chapitres numérotés du même dossier : `10-Evaluation/50-Precision-Rappel-F1-et-KL.md`, `06-Attention-et-Transformer/33-Transformer-et-Attention-Deroule-Numerique.md`, `12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md`, `12-Production-Couts-Optimisation/69-Files-Attente-et-Goulot.md` et `12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md`. La softmax et Bellman sont dans `02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md`.

# 5. Évaluation des Agents, Divergence de Kullback-Leibler (Dₖₗ) et Théorie des Garde-Fous (Guardrails)

## 1. Contextualisation et Rôle dans la Sécurité et l'Évaluation des Agents

Déployer un agent autonomie en production nécessite de mesurer rigoureusement ses performances et de borner son comportement pour éviter les hallucinations, la fuite de données confidentielles (Data Leakage) ou la dérive de distribution.

Deux piliers mathématiques régissent ce domaine :
1. **Les Métriques de Classification et de Retrieval** (Précision, Rappel, F1-Score) pour quantifier la qualité des outils et des réponses du RAG.
2. **La Théorie de l'Information et la Divergence de Kullback-Leibler**, notée D_KL, pour évaluer la distance entre la distribution des réponses de l'agent et la distribution cible de référence (Guardrails / Alignment).

---

## 2. Définitions Mathématiques Formelles

### A. Matrice de Confusion, Précision, Rappel et Fᵦ-Score

Pour un agent prenant une décision binaire (ex: "Activer l'outil de suppression de compte" : Oui / Non) :

* **Précision (P)** : Proportion de décisions positives correctes parmi toutes les décisions positives prises par l'agent :

$$
P = \frac{TP}{TP + FP}
$$

* **Rappel (R)** : Proportion de cas positifs réels correctement détectés par l'agent :

$$
R = \frac{TP}{TP + FN}
$$

* **F1-Score** : Moyenne harmonique de la Précision et du Rappel (équilibrant les deux métriques) :

$$
F_1 = 2 \cdot \frac{P \cdot R}{P + R} = \frac{2 TP}{2 TP + FP + FN}
$$

---

### B. Divergence de Kullback-Leibler (Dₖₗ)

Soient P et Q deux distributions de probabilité discrètes définies sur un même espace d'états 𝒳.

La **Divergence de Kullback-Leibler** (ou entropie relative) mesurant l'information perdue lorsqu'on utilise la distribution Q (générée par le LLM) pour approximer la distribution vraie P est définie par :

$$
D_{KL}(P \parallel Q) = \sum_{x \in \mathcal{X}} P(x) \log \left( \frac{P(x)}{Q(x)} \right)
$$

---

## 3. Démonstration Mathématique : Non-Négativité de la Divergence KL (Inégalité de Gibbs)

### Théorème :

Pour toutes distributions de probabilité P et Q :

$$
D_{KL}(P \parallel Q) \ge 0
$$

avec égalité

$$
D_{KL}(P \parallel Q) = 0
$$

si et seulement si P(x) = Q(x) pour tout x ∈ 𝒳.

### Démonstration Étape par Étape (Utilisant l'Inégalité de Jensen) :

1. Réexprimons l'opposé de la divergence KL :

$$
-D_{KL}(P \parallel Q) = -\sum_{x \in \mathcal{X}} P(x) \log \left( \frac{P(x)}{Q(x)} \right) = \sum_{x \in \mathcal{X}} P(x) \log \left( \frac{Q(x)}{P(x)} \right)
$$

2. Rappelons l'**Inégalité de Jensen** : Pour une fonction strictement concave f et une variable aléatoire X,

$$
\mathbb{E}[f(X)] \le f(\mathbb{E}[X]) .
$$

   La fonction logarithme népérien f(t) = log(t) est strictement concave sur ]0, +∞[.

3. Appliquons l'inégalité de Jensen avec la probabilité P(x) comme masse de pondération :

$$
\sum_{x \in \mathcal{X}} P(x) \log \left( \frac{Q(x)}{P(x)} \right) \le \log \left( \sum_{x \in \mathcal{X}} P(x) \frac{Q(x)}{P(x)} \right)
$$

4. Simplifions le terme à l'intérieur du logarithme :

$$
\sum_{x \in \mathcal{X}} P(x) \frac{Q(x)}{P(x)} = \sum_{x \in \mathcal{X}} Q(x) = 1
$$

5. Par conséquent :

$$
-D_{KL}(P \parallel Q) \le \log(1) = 0 \implies D_{KL}(P \parallel Q) \ge 0
$$

*CQFD.*

---

## 4. Garde-Fous Basés sur l'Entropie et Dₖₗ

Dans un Guardrail d'agent (une bibliothèque de règles de modération, ou un petit modèle classifieur placé devant l'agent) :
* Si l'agent hésite entre plusieurs réponses dangereuses, la distribution Q(x) devient très diffuse, augmentant son **entropie de Shannon**

$$
H(Q) = -\sum Q(x) \log Q(x) .
$$

* Si l'agent s'éloigne du langage sécurisé d'entreprise P(x), la divergence

$$
D_{KL}(P \parallel Q)
$$

explose.
* **Règle d'activation du Guardrail** :

$$
\text{Si } D_{KL}(P \parallel Q) > \tau_{\text{threshold}} \implies \text{Intercepter la réponse et renvoyer un fallback.}
$$

---

## 5. Cas d'Usage Réels et Quantifiés en Entreprise

### Cas A : Agent Médical de Diagnostic (Arbitrage Précision vs Rappel)

#### Contexte :
Un agent médical analyse des comptes-rendus d'imagerie pour orienter vers un cancérologue.

#### Analyse de Risque :
* Un **Faux Positif (FP)** entraîne un examen complémentaire stressant mais bénin.
* Un **Faux Négatif (FN)** rate une tumeur précoce (conséquence vitale).

#### Solution Mathématique :
L'ingénieur modifie la métrique d'évaluation en utilisant le **Fᵦ-Score** avec β = 2 pour donner 4 fois plus d'importance au Rappel qu'à la Précision :

$$
F_2 = (1 + 2^2) \cdot \frac{P \cdot R}{(2^2 \cdot P) + R} = 5 \cdot \frac{P \cdot R}{4P + R}
$$

#### Résultat Quantifié en Production :

Chiffres illustratifs, non mesurés.

* Seuil d'activation ajusté pour maximiser F₂.
* Le rappel R passe, dans cet exemple, de 89,2 % à **99,4 %**, ce qui élimine presque tous les faux négatifs critiques.

---

### Cas B : Guardrail Anti-Jailbreak pour Agent Bancaire (Dₖₗ In-Flight)

#### Contexte :
Un agent bancaire reçoit des requêtes utilisateur contenant potentiellement des attaques d'injection de prompt (Jailbreaks).

#### Déploiement :
Un petit modèle garde-fou (ex: DeBERTa-v3) calcule la divergence

$$
D_{KL}
$$

entre la probabilité des tokens de sortie de l'agent et la distribution d'un corpus de référence sécurisé.

#### Résultats Chiffrés :

Chiffres illustratifs, non mesurés : un détecteur d'injection se mesure toujours sur son propre jeu étiqueté (étape 66), et il peut être contourné.

* Sur un jeu de test de 10 000 attaques par injection de prompt :
  * Détection basée sur des règles (Mots-clés / Regex) : Taux de détection = 42.1%.
  * Détection basée sur le seuil

$$
D_{KL}(P \parallel Q) > 1.85
$$

Taux de détection = **98.7%** avec seulement 0.3% de faux positifs.

---

## 6. Synthèse pour l'Ingénieur IA

**Métrique / Formule :** **Précision (P)** · **Application Agentique :** Tool Calling / Exécution d'actions irréversibles · **Objectif de Réglage :** Maximiser P (> 0.99) pour éviter les actions erronées.

**Métrique / Formule :** **Rappel (R)** · **Application Agentique :** RAG / Recherche documentaire de sécurité · **Objectif de Réglage :** Maximiser R (> 0.95) pour ne rater aucune clause pertinente.

$$
D_{KL}(P \parallel Q)
$$

**Application Agentique :** Modération et Détection de Dérive (Guardrails) · **Objectif de Réglage :** Bloquer la réponse si (formule ci-dessous) (déviation de la distribution de confiance).

$$
D_{KL} > \tau
$$

# 6. Mécanisme de Self-Attention (Scaled Dot-Product) et Dynamic Context Windows

## 1. Contextualisation et Rôle dans l'Architecture LLM des Agents

Tous les grands modèles de langage actuels sous-jacents aux agents IA reposent sur la couche d'**Attention Croisée et Auto-Attention (Self-Attention)** introduite par Vaswani et al. dans l'architecture Transformer.

Pour un agent IA, le mécanisme d'attention détermine la capacité du modèle à :
* Relier des instructions distantes de plusieurs milliers de tokens dans la fenêtre de contexte (ex: se souvenir d'une contrainte système définie au début du prompt).
* Sélectionner les arguments pertinents lors de l'exécution d'un **Tool Call**.
* Maintenir la cohérence du raisonnement dans de longues chaînes de pensées (Chain-of-Thought).

---

## 2. Définition Mathématique Formelle

Soit

$$
X \in \mathbb{R}^{N \times d_{\text{model}}}
$$

la matrice d'entrée représentant une séquence de N tokens représentés dans un espace de dimension

$$
d_{\text{model}} .
$$

### A. Projections Linéaires Query, Key, Value

On définit trois matrices de poids entraînables

$$
W_Q \in \mathbb{R}^{d_{\text{model}} \times d_k} ,
$$

$$
W_K \in \mathbb{R}^{d_{\text{model}} \times d_k}
$$

et

$$
W_V \in \mathbb{R}^{d_{\text{model}} \times d_v} .
$$

Les matrices de requêtes (Q), de clés (K) et de valeurs (V) sont calculées par :

$$
Q = X W_Q \in \mathbb{R}^{N \times d_k}, \quad K = X W_K \in \mathbb{R}^{N \times d_k}, \quad V = X W_V \in \mathbb{R}^{N \times d_v}
$$

### B. Équation du Scaled Dot-Product Attention

Le mécanisme d'attention pondéré est défini par l'application :

$$
\text{Attention}(Q, K, V) = \text{softmax}\left( \frac{Q K^T}{\sqrt{d_k}} \right) V
$$

Où

$$
A = \text{softmax}\left( \frac{Q K^T}{\sqrt{d_k}} \right) \in \mathbb{R}^{N \times N}
$$

est la **matrice des poids d'attention**.

---

## 3. Démonstration Mathématique : Nécessité du Facteur d'Échelle √dₖ

### Théorème :

Si les composantes de Q et K sont des variables aléatoires indépendantes et identiquement distribuées (i.i.d.) de moyenne nulle et de variance 1, alors le produit scalaire

$$
q_i \cdot k_j = \sum_{l=1}^{d_k} q_{i,l} k_{j,l}
$$

a une moyenne nulle et une variance égale à dₖ.

Le facteur de division par √dₖ est **strictement indispensable** pour maintenir la variance du produit scalaire à 1 et empêcher la fonction Softmax de saturer dans des zones à gradient quasi-nul.

### Démonstration Étape par Étape :

Soient qₗ et kₗ deux composantes scalaires individuelles de Q et K.
Hypothèses :

$$
\mathbb{E}[q_l] = \mathbb{E}[k_l] = 0
$$

et Var(qₗ) = Var(kₗ) = 1.

1. Calcul de l'espérance du produit scalaire

$$
S = \sum_{l=1}^{d_k} q_l k_l
$$

$$
\mathbb{E}[S] = \mathbb{E}\left[ \sum_{l=1}^{d_k} q_l k_l \right] = \sum_{l=1}^{d_k} \mathbb{E}[q_l k_l]
$$

Par indépendance de qₗ et kₗ :

$$
\mathbb{E}[q_l k_l] = \mathbb{E}[q_l] \mathbb{E}[k_l] = 0 \times 0 = 0 .
$$

Donc

$$
\mathbb{E}[S] = 0 .
$$

2. Calcul de la variance du produit scalaire S :
   Puisque les termes de la somme sont indépendants :

$$
\text{Var}(S) = \text{Var}\left( \sum_{l=1}^{d_k} q_l k_l \right) = \sum_{l=1}^{d_k} \text{Var}(q_l k_l)
$$

3. Calcul de la variance du produit de deux variables indépendantes de moyenne nulle :

$$
\text{Var}(q_l k_l) = \mathbb{E}[(q_l k_l)^2] - (\mathbb{E}[q_l k_l])^2 = \mathbb{E}[q_l^2 k_l^2] - 0 = \mathbb{E}[q_l^2] \mathbb{E}[k_l^2]
$$

Or

$$
\mathbb{E}[q_l^2] = \text{Var}(q_l) + (\mathbb{E}[q_l])^2 = 1 + 0 = 1 .
$$

De même,

$$
\mathbb{E}[k_l^2] = 1 .
$$

Donc Var(qₗ kₗ) = 1 × 1 = 1.

4. Sommons sur les dₖ dimensions :

$$
\text{Var}(S) = \sum_{l=1}^{d_k} 1 = d_k
$$

5. **Effet sur la Softmax sans division** :
   Pour de grandes valeurs de dₖ (ex: dₖ = 128), la variance du produit scalaire vaut 128, signifiant que certains éléments de QKᵀ atteignent des valeurs très élevées (ex: +30).
   Or, la dérivée de la Softmax par rapport à son propre logit vaut ∂pᵢ/∂zᵢ = pᵢ(1 − pᵢ), qui tend vers 0 quand pᵢ s'approche de 0 ou de 1, ce qui arrive dès que les écarts entre logits sont grands. Le gradient s'évanouit (**Vanishing Gradient**), ce qui freine fortement l'apprentissage.

6. **Normalisation par √dₖ** :

$$
\text{Var}\left( \frac{S}{\sqrt{d_k}} \right) = \frac{1}{(\sqrt{d_k})^2} \text{Var}(S) = \frac{1}{d_k} \times d_k = 1
$$

*CQFD.*

---

## 4. Analyse de la Complexité Quadratique O(N²)

La multiplication matricielle Q Kᵀ entre

$$
Q \in \mathbb{R}^{N \times d_k}
$$

et

$$
K^T \in \mathbb{R}^{d_k \times N}
$$

génère une matrice d'attention de taille N × N.

* **Complexité Temporelle** : O(N² · dₖ) opérations flottantes.
* **Complexité Mémoire** : O(N²) pour stocker la matrice de scores A.

### Graphique Théorique de l'Explosion Mémoire en Fct de la Fenêtre de Contexte N :

```text
Taille du Contexte (N)   | Complexité Mémoire Attention N²
---------------------------------------------------------
N = 4,000 tokens         | ~ 16,000,000 opérations
N = 32,000 tokens        | ~ 1,024,000,000 opérations (x64)
N = 128,000 tokens       | ~ 16,384,000,000 opérations (x1024)
```

---

## 5. Cas d'Usage Réels et Quantifiés en Entreprise

### Cas A : Optimisation par FlashAttention-2 pour un Agent d'Analyse Juridique (128k Tokens)

#### Contexte :
Un agent lit des liasses juridiques complètes de 100 000 tokens sur des GPU de 80 Go de mémoire.

#### Problème :
Avec l'attention standard PyTorch, le stockage de la matrice N × N pour N = 100 000 requiert :

$$
\text{RAM}_{\text{Attention}} = 100\,000 \times 100\,000 \times 2 \text{ octets (FP16)} = 20 \text{ Go par tête d'attention}
$$

Le système subit un Out-Of-Memory (OOM) immédiat.

#### Implémentation de FlashAttention (Tiling et Softmax en Ligne) :
FlashAttention découpe les matrices Q, K, V en blocs (SRAM) et calcule la Softmax exacte sans écrire la matrice N × N intermédiaire dans la mémoire HBM (High Bandwidth Memory).

#### Résultat Quantifié :

Chiffres illustratifs, non mesurés.

* **Empreinte mémoire GPU** : Réduite de **−85%**, permettant de passer la fenêtre de contexte de 16k à **128k tokens sur une seule carte GPU**.
* **Vitesse de génération (Throughput)** : Augmentée de **+3.4×** (passant de 22 tokens/s à 75 tokens/s).

---

## 6. Synthèse pour l'Ingénieur IA

| Composante Attention | Rôle dans l'Agent | Point d'Attention |
| --- | --- | --- |
| **√dₖ (Scaling)** | Stabilisation numérique de la Softmax | Nécessaire pour éviter la disparition du gradient lors du fine-tuning. |
| **Matrice QKᵀ (N × N)** | Matrice d'association sémantique token-à-token | Origine du surcoût de la fenêtre de contexte long. |
| **KV Cache (Key-Value Cache)** | Stockage des clés/valeurs passées lors du décodage | Évite de recalculer K et V à chaque nouveau token généré par l'agent (O(N) au lieu de O(N²) par token). |

# 7. Descente de Gradient et Low-Rank Adaptation (LoRA)

## 1. Contextualisation et Rôle dans la Spécialisation des Agents

Bien que les prompts et le RAG permettent de guider un agent IA, l'obtention d'un agent hautement spécialisé (ex: respect d'un format JSON propriétaire complexe, maîtrise du jargon médical ou juridique) nécessite souvent un **Fine-Tuning (Spécialisation des Poids)**.

Réentraîner un LLM moderne de 70 milliards de paramètres (

$$
\theta \in \mathbb{R}^{70 \times 10^9}
$$

) par descente de gradient classique avec AdamW demande de l'ordre de 16 octets de mémoire GPU par paramètre en précision mixte (poids, gradients, copie des poids en 32 bits et deux moments), soit 70 × 10⁹ × 16 ≈ 1,1 To, dont 560 Go pour les seuls deux moments de l'optimiseur.

La méthode **LoRA (Low-Rank Adaptation)** résout ce problème grâce au théorème de décomposition matricielle de rang réduit, permettant d'entraîner des agents sur du matériel accessible.

---

## 2. Définition Mathématique Formelle

### A. Descente de Gradient Stochastique avec Optimiseur AdamW

Soit L(θ) la fonction de perte (Cross-Entropy) mesurant l'erreur de l'agent sur un dataset d'apprentissage.
La mise à jour des poids par descente de gradient à l'étape t avec un taux d'apprentissage η s'écrit (on note η le taux d'apprentissage, et α le facteur d'échelle de LoRA plus bas) :

$$
\theta_{t+1} = \theta_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon} - \eta \lambda \theta_t
$$

Où m̂ₜ et v̂ₜ sont les moments d'ordre 1 et 2 corrigés du gradient

$$
\nabla_\theta L(\theta_t) ,
$$

et λ est le coefficient de découplage de la régularisation L2 (Weight Decay).

---

### B. Formulation Mathématique de LoRA (Low-Rank Adaptation)

Soit

$$
W_0 \in \mathbb{R}^{d \times k}
$$

une matrice de poids originale gelée (frozen) d'une couche dense du Transformer.
On modélise la mise à jour des poids Δ W sous la forme d'un produit de deux matrices de bas rang A et B :

$$
W' = W_0 + \Delta W = W_0 + \frac{\alpha}{r} (B \cdot A)
$$

Où :

$$
B \in \mathbb{R}^{d \times r}
$$

initialisée à zéro (B = 0).

$$
A \in \mathbb{R}^{r \times k}
$$

initialisée selon une distribution gaussienne

$$
\mathcal{N}\left(0, \frac{1}{r}\right) .
$$

* r ≪ min(d, k) est le **rang (Rank)** de la décomposition (ex: r = 8 pour d = 4096).
* α est un scalaire de mise à l'échelle (scaling factor) constant.

---

## 3. Démonstration Mathématique : Gain de Complexité Mémoire et Paramétrique

### Théorème :

Soit une couche linéaire avec une matrice de poids

$$
W_0 \in \mathbb{R}^{d \times k} .
$$

La décomposition LoRA de rang r réduit le nombre de paramètres entraînables d'un facteur de :

$$
\text{Facteur de Réduction} = \frac{d \cdot k}{r \cdot (d + k)}
$$

### Démonstration Étape par Étape :

1. Nombre de paramètres dans la matrice complète originale W₀ :

$$
P_{\text{original}} = d \times k
$$

2. Nombre de paramètres dans la décomposition LoRA B · A :
   * Matrice

$$
B \in \mathbb{R}^{d \times r} \implies d \times r
$$

paramètres.
   * Matrice

$$
A \in \mathbb{R}^{r \times k} \implies r \times k
$$

paramètres.

$$
P_{\text{LoRA}} = (d \times r) + (r \times k) = r \cdot (d + k)
$$

3. Calcul du ratio pour un Transformer standard (ex: Llama-3 8B où d = k = 4096) avec un rang LoRA r = 8 :

$$
P_{\text{original}} = 4096 \times 4096 = 16\,777\,216
$$

paramètres (≈ 16.7M).

$$
P_{\text{LoRA}} = 8 \cdot (4096 + 4096) = 8 \times 8192 = 65\,536
$$

paramètres (≈ 65.5K).

4. Calcul du facteur d'économie :

$$
\frac{P_{\text{original}}}{P_{\text{LoRA}}} = \frac{16\,777\,216}{65\,536} = 256
$$

*CQFD.*

> **Résultat analytique** : LoRA réduit le nombre de paramètres à entraîner de **99.61%** pour cette couche sans modifier l'architecture fondamentale.

---

## 4. Propriété de Fusion pour l'Inférence (Zero-Latency Overhead)

Pendant le déploiement de l'agent en production, la présence des deux matrices secondaires A et B risquerait d'ajouter une étape de calcul matriciel supplémentaire.

Grâce à la distributivité de la multiplication matricielle sur l'addition :

$$
h = W' x = \left( W_0 + \frac{\alpha}{r} B A \right) x = W_0 x + \frac{\alpha}{r} B A x
$$

Avant le déploiement en production, l'ingénieur effectue la **fusion explicite des poids** :

$$
W_{\text{déployé}} = W_0 + \frac{\alpha}{r} (B \cdot A)
$$

> La matrice fusionnée

$$
W_{\text{déployé}}
$$

> a exactement les mêmes dimensions

$$
\mathbb{R}^{d \times k}
$$

> que le modèle initial. **Le surcoût en latence à l'inférence est strictement égal à 0 ms.**

---

## 5. Cas d'Usage Réels et Quantifiés en Entreprise

### Cas A : Fine-Tuning d'un Agent Spécialisé en Cybersécurité (Parsing de Logs SIEM)

#### Contexte :
Une entreprise de cybersécurité veut spécialiser Llama-3-70B pour analyser les logs d'attaques réseau et générer des réponses au format YARA.

#### Configuration vs Fine-Tuning Complet :

Chiffres illustratifs, non mesurés.

| Paramètre | Full Fine-Tuning | Fine-Tuning LoRA (r=16, α=32) |
| --- | --- | --- |
| **GPUs requis** | 16 GPU de 80 Go | 2 GPU de 80 Go |
| **Paramètres entraînés** | 70 000 000 000 (100%) | 154 000 000 (0.22%) |
| **Coût d'entraînement** | 18 400 USD | 420 USD |
| **Précision JSON YARA** | 98.1% | 97.9% |

#### Résultat Quantifié :
Réduction du coût de spécialisation de **−97,7 %** ((18 400 − 420) / 18 400) pour une perte d'exactitude de 0,2 point, dans cet exemple illustratif.

---

## 6. Synthèse des Bonnes Pratiques

| Hyperparamètre LoRA | Valeur Recommandée | Impact Mathématique |
| --- | --- | --- |
| **Rang r** | 8 à 16 | Contrôle la dimension du sous-espace d'adaptation. Un r trop élevé réintroduit du surapprentissage. |
| **LoRA Alpha (α)** | 2 × r (ex: α = 32) | Scalaire d'échelle. Maintient le taux d'apprentissage stable lorsque r varie. |
| **Target Modules** | Q, K, V, O + MLP layers | Appliquer LoRA sur toutes les couches linéaires garantit les meilleures performances. |

# 8. Théorie des Files d'Attente (Queueing Theory) et Loi de Little pour le Scalabilitél d'Agents

## 1. Contextualisation et Rôle dans l'Ingénierie Système d'Agents

Lorsqu'un agent IA est déployé au sein d'une architecture d'entreprise (API Backend, microservices, consommateurs Kafka), il doit traiter un flux de requêtes entrantes émanant d'utilisateurs ou d'autres systèmes autonomes.

Chaque appel d'agent implique des traitements lourds (génération de tokens par le LLM, recherches RAG, exécution d'outils externes). 

La **Théorie des Files d'Attente** permet à l'ingénieur agentique de :
* Dimensionner correctement le cluster d'instances d'agents (autoscaling).
* Calculer mathématiquement le temps d'attente moyen 𝒲 d'un utilisateur avant d'obtenir la première réponse (Time To First Token - TTFT).
* Éviter le phénomène de sature chaotique du système (effondrement des performances).

---

## 2. Définition Mathématique Formelle et Loi de Little

### A. La Loi de Little (Théorème fondamental de l'ergodique)

Pour tout système de traitement en régime permanent (stationnaire et stable) :

$$
\mathcal{L} = \lambda \mathcal{W}
$$

Où :
* ℒ : Le nombre moyen de requêtes d'agents présentes dans le système (en cours d'exécution + en attente dans la file).
* λ : Le taux d'arrivée moyen des requêtes (requêtes / seconde).
* 𝒲 : Le temps de séjour moyen d'une requête dans le système (temps d'attente en file + temps d'exécution de l'agent).

---

### B. Modèle de File d'Attente M/M/c (Notation de Kendall)

Soit un pool de c instances parallèles de serveurs d'agents d'IA.
* Les arrivées suivent un **Processus de Poisson** de paramètre λ (inter-arrivées exponentielles).
* Les temps de traitement d'un agent suivent une **loi exponentielle** de paramètre μ (taux de service

$$
\mu = \frac{1}{T_{\text{service}}}
$$

).

#### Facteur d'Utilisation du Système (ρ) :

$$
\rho = \frac{\lambda}{c \cdot \mu}
$$

> **Condition d'Équilibre Strict** : Le système n'est stable que si et seulement si ρ < 1. Si ρ ≥ 1, la file d'attente croît vers l'infini (

$$
\lim_{t \to \infty} \mathcal{L}(t) = +\infty
$$

> ).

---

## 3. Démonstration Mathématique : Temps d'Attente dans une File Single-Server M/M/1

### Théorème :

Dans un système M/M/1 (c = 1 instance d'agent), le temps moyen total passé par une requête dans le système est :

$$
\mathcal{W} = \frac{1}{\mu - \lambda} = \frac{T_{\text{service}}}{1 - \rho}
$$

### Démonstration Étape par Étape :

1. Définissons

$$
p_k = \mathbb{P}(N = k)
$$

la probabilité qu'il y ait exactement k requêtes dans le système en régime permanent.
   Les équations de bilan d'état (Balance Equations) pour la chaîne de Markov à temps continu donnent :

$$
\lambda p_{k-1} = \mu p_k \implies p_k = \left( \frac{\lambda}{\mu} \right) p_{k-1} = \rho^k p_0
$$

2. Utilisons la condition de normalisation

$$
\sum_{k=0}^{\infty} p_k = 1
$$

$$
p_0 \sum_{k=0}^{\infty} \rho^k = 1
$$

La somme d'une série géométrique pour ρ < 1 donne

$$
\sum_{k=0}^{\infty} \rho^k = \frac{1}{1 - \rho} .
$$

Donc :

$$
p_0 = 1 - \rho
$$

$$
p_k = (1 - \rho) \rho^k
$$

3. Calculons le nombre moyen de requêtes ℒ dans le système :

$$
\mathcal{L} = \mathbb{E}[N] = \sum_{k=0}^{\infty} k \cdot p_k = (1 - \rho) \sum_{k=0}^{\infty} k \rho^k
$$

4. Utilisons l'identité algébrique

$$
\sum_{k=0}^{\infty} k \rho^k = \rho \frac{d}{d\rho} \left( \sum_{k=0}^{\infty} \rho^k \right) = \rho \frac{d}{d\rho} \left( \frac{1}{1 - \rho} \right) = \frac{\rho}{(1 - \rho)^2}
$$

$$
\mathcal{L} = (1 - \rho) \cdot \frac{\rho}{(1 - \rho)^2} = \frac{\rho}{1 - \rho}
$$

5. Appliquons la **Loi de Little**

$$
\mathcal{W} = \frac{\mathcal{L}}{\lambda}
$$

$$
\mathcal{W} = \frac{\rho}{\lambda(1 - \rho)} = \frac{\frac{\lambda}{\mu}}{\lambda(1 - \rho)} = \frac{1}{\mu(1 - \rho)} = \frac{1}{\mu - \lambda}
$$

*CQFD.*

---

## 4. Analyse de la Explosion Non-Linéaire de la Latence

Exaltons la relation

$$
\mathcal{W}(\rho) = \frac{T_{\text{service}}}{1 - \rho}
$$

```text
Charge du Serveur (ρ)   | Multiplicateur de Latence (1 / (1 - ρ))
-----------------------------------------------------------------
ρ = 0.50 (50%)          | 2.0x  (Système fluide)
ρ = 0.80 (80%)          | 5.0x  (Ralentissement sensible)
ρ = 0.90 (90%)          | 10.0x (Degradation majeure)
ρ = 0.95 (95%)          | 20.0x (EXPLOSION DE LA LATENCE)
```

> **Leçon d'Ingénierie** : Un pool d'agents IA ne doit **jamais** être exploité à plus de 80% de sa capacité nominale sous peine de voir le temps de réponse exploser à la moindre fluctuation de trafic. La croissance n'est pas exponentielle : elle suit 1/(1 − ρ), qui tend vers l'infini quand ρ approche 1 (multiplicateur 5 à 80 %, 10 à 90 %, 20 à 95 %).

---

## 5. Cas d'Usage Réels et Quantifiés en Entreprise

### Cas A : Autoscaling d'un Agent d'Assistance Téléphonique Voice-AI

#### Contexte :
Un agent vocal traite des appels entrants.
* Taux d'arrivée aux heures de pointe : λ = 12 requêtes/seconde.
* Temps moyen de réponse de l'agent (LLM + TTS) :

$$
T_{\text{service}} = 0.25 \text{ secondes} \implies \mu = 4 \text{ req/s per worker} .
$$

#### Calcul du Nombre Minimal d'Instances (c) :

1. Condition de stabilité

$$
\rho = \frac{\lambda}{c \mu} < 1
$$

$$
\frac{12}{c \cdot 4} < 1 \implies \frac{3}{c} < 1 \implies c > 3 \text{ instances}
$$

2. Objectif SLA : Le temps total 𝒲 ne doit pas dépasser 0.35 secondes (pour conserver la fluidité vocale humaine).

3. En utilisant la formule de la file M/M/c (Erlang-C) :
   * Pour c = 4 workers :

$$
\rho = \frac{12}{16} = 0.75 .
$$

La formule d'Erlang C donne une probabilité d'attente C ≈ 0,509, un temps moyen en file 𝒲_q = C / (cμ − λ) = 0,509 / 4 ≈ 0,127 s, et un temps total 𝒲 = 𝒲_q + 1/μ = 0,127 + 0,25 = 0,377 s : le SLA de 0,35 s **n'est pas respecté**. (L'ancienne version annonçait 𝒲 ≈ 0,33 s et un SLA respecté, ce qui est faux.)
   * Pour c = 5 workers : ρ = 12/20 = 0,6, C ≈ 0,236, 𝒲_q ≈ 0,236 / 8 ≈ 0,030 s et 𝒲 ≈ 0,280 s : le SLA est respecté. Il faut donc au moins 5 instances.
   * Pour c = 3 workers : ρ = 1.0 ⇒ File infinie (SLA violé).

#### Résultat d'Ingénierie :
Les règles d'autoscaling (par exemple un HPA Kubernetes) visent une charge ρ ≤ 0,70, ce qui impose ici au moins 5 instances (ρ = 0,6). Ce réglage tient la moyenne sous le SLA ; le respect d'un engagement en percentile (par exemple 99,9 % des appels sous 0,35 s) ne se déduit pas de la moyenne et se vérifie sur les latences mesurées.

---

## 6. Synthèse pour l'Ingénieur IA

| Variable | Définition dans un système d'agents | Action de Régulation |
| --- | --- | --- |
| **λ (Arrivées)** | Charge de requêtes clients | Appliquer du Rate Limiting / Throttling en amont. |
| **μ (Service)** | Vitesse de génération du LLM (Tokens/s) | Utiliser du Speculative Decoding ou du Tensor Parallelism pour augmenter μ. |
| **ρ (Utilisation)** | Taux d'occupation du pool GPU/CPU | Maintenir ρ ≤ 0.75 via des règles d'Autoscaling. |

# 9. Complexité Algorithmique, Gestion de Contexte (Token Management) et Modélisation des Coûts API

## 1. Contextualisation et Rôle dans la Viabilité Économique des Agents

Dans une architecture agentique industrielle, le modèle économique repose quasi exclusivement sur une facturation au token consommé (Input Tokens Nᵢₙ et Output Tokens Nₒᵤₜ).

Un agent mal conçu effectuant des boucles de réflexion non optimisées ou réinjectant systématiquement la totalité de l'historique de conversation à chaque action (Context Stuffing) peut générer des factures d'API multipliées par un facteur 10 à 100.

Un **AI Agentic Developer** doit modéliser analytiquement les coûts et la complexité des stratégies de gestion du contexte : résumé (summarization), troncature, fenêtre glissante, cache de prompt, et CAG (Cache-Augmented Generation, qui précharge des connaissances dans le cache au lieu de les récupérer à chaque requête).

---

## 2. Formulation Mathématique de la Fonction de Coût

Soit une tâche agentique exécutée en K étapes d'actions (Tool Calls / Chain-of-Thought).

### A. Coût Cumulé d'une Séquence d'Actions Non-Optimisée

À l'étape k ∈ {1, …, K}, la longueur du prompt d'entrée est constituée d'un prompt système de base S, d'un contexte de travail C, et de l'accumulation des k−1 échanges précédents :

$$
N_{\text{in}}^{(k)} = |S| + |C| + \sum_{j=1}^{k-1} \left( |I_j| + |O_j| \right)
$$

Le coût financier total Cₜₒₜₐₗ d'exécution de la tâche est donné par :

$$
C_{\text{total}} = P_{\text{in}} \sum_{k=1}^{K} N_{\text{in}}^{(k)} + P_{\text{out}} \sum_{k=1}^{K} N_{\text{out}}^{(k)}
$$

Où Pᵢₙ et Pₒᵤₜ sont respectivement les prix unitaire par token d'entrée et de sortie.

---

## 3. Démonstration Mathématique : Croissance Quadratique des Coûts sans Compression de Mémoire

### Théorème :

Si à chaque étape de raisonnement k, l'agent génère un nombre constant de tokens Nₒᵤₜ⁽ᵏ⁾ = Δ, alors le coût cumulé d'entrée Cᵢₙ d'un dialogue à K étapes sans élagage croît de manière **quadratique** O(K²) en fonction du nombre d'étapes.

### Démonstration Étape par Étape :

1. Supposons pour simplifier la preuve que |S| + |C| = S₀ (constante) et que chaque étape ajoute un volume fixe de tokens Δ (réponse et appel d'outil).

2. À l'étape k, la taille du prompt d'entrée est :

$$
N_{\text{in}}^{(k)} = S_0 + (k - 1) \Delta
$$

3. Calculons la somme totale des tokens d'entrée injectés sur les K étapes :

$$
N_{\text{in, total}} = \sum_{k=1}^{K} \left( S_0 + (k - 1) \Delta \right) = \sum_{k=1}^{K} S_0 + \Delta \sum_{k=1}^{K} (k - 1)
$$

4. Utilisons la formule de la somme d'une progression arithmétique

$$
\sum_{j=0}^{K-1} j = \frac{(K-1)K}{2}
$$

$$
N_{\text{in, total}} = K \cdot S_0 + \Delta \frac{K(K - 1)}{2} = K \cdot S_0 + \frac{\Delta}{2} K^2 - \frac{\Delta}{2} K
$$

5. Par conséquent, le coût d'entrée est :

$$
C_{\text{in}} = P_{\text{in}} \left( \frac{\Delta}{2} K^2 + \left( S_0 - \frac{\Delta}{2} \right) K \right)
$$

*CQFD.*

> **Résultat d'Ingénierie** : Sans stratégie de gestion de la mémoire, **le coût d'entrée croît comme K²** : doubler le nombre d'étapes multiplie ce coût par un rapport qui tend vers 4 quand K est grand, mais qui reste en dessous de 4 à cause du terme linéaire. Avec S₀ = 2 000 et Δ = 500, passer de 15 à 30 étapes fait passer les tokens d'entrée de 82 500 à 277 500, soit un rapport de 3,36.

---

## 4. Modélisation de la Fenêtre Glissante (Sliding Window) vs Résumé Automatique (Summarization)

Pour ramener la complexité de O(K²) à une complexité **linéaire O(K)**, l'ingénieur applique deux stratégies mathématiques :

### Stratégie A : Fenêtre Glissante de Taille M (Sliding Window)

On ne conserve que les M derniers échanges dans la mémoire de l'agent (M ≪ K) :

$$
N_{\text{in, window}}^{(k)} = S_0 + \min(k-1, M) \cdot \Delta
$$

Le coût d'entrée total devient linéaire :

$$
N_{\text{in, total}} \le K \cdot (S_0 + M \cdot \Delta) \implies O(K)
$$

### Stratégie B : Compression de Contexte par Résumé (Context Summarization)

Tous les M blocs, un sous-agent résume l'historique passé en un vecteur d'information de taille fixe R ≪ M · Δ.

---

## 5. Cas d'Usage Réels et Quantifiés en Entreprise

### Cas A : Agent de Support Client Automatisé (100 000 Sessions / Mois)

#### Contexte :
Un agent de support client résout des incidents en K = 15 étapes de dialogue en moyenne.
* Prix API illustratifs : Pᵢₙ = 3 USD par million de tokens d'entrée, Pₒᵤₜ = 15 USD par million de tokens de sortie. Les tarifs réels changent : on les relit chez le fournisseur avant tout calcul.
* S₀ = 2 000 tokens, Δ = 500 tokens.

#### Comparaison Financière des Architectures :

1. **Architecture Naïve (Sans gestion de mémoire - O(K²))** :
   * Tokens d'entrée totaux par session :

$$
N_{\text{in, total}} = 15 \times 2000 + 500 \times \frac{15 \times 14}{2} = 30\,000 + 52\,500 = 82\,500 \text{ tokens}
$$

* Coût d'entrée par session : 82 500 × 3 × 10⁻⁶ = 0,2475 USD.
* Coût annuel d'entrée sur 100 000 sessions par mois : 0,2475 × 1 200 000 = **297 000 USD par an**, hors tokens de sortie.

2. **Architecture Optimisée (Fenêtre Glissante M=4 + Prompt Caching)** :
   * Tokens d'entrée stabilisés à :

$$
N_{\text{in}}^{(k)} = 2000 + 4 \times 500 = 4\,000 \text{ tokens} .
$$

   * Tokens d'entrée totaux par session : 15 × 4 000 = 60 000 n'est qu'une borne. La fenêtre n'est pleine qu'à partir de l'étape 5 ; la somme exacte vaut 2 000 + 2 500 + 3 000 + 3 500 + 11 × 4 000 = 55 000 tokens.
   * Grâce au **Prompt Caching**, les 2 000 tokens statiques de S₀ sont lus dans le cache à 10 % du prix (en négligeant le surcoût de l'écriture initiale dans le cache) : 15 × 2 000 = 30 000 tokens à 0,3 USD par million, et 25 000 tokens au plein tarif.
   * Coût d'entrée effectif par session : 30 000 × 0,3 × 10⁻⁶ + 25 000 × 3 × 10⁻⁶ = 0,009 + 0,075 = **0,084 USD**, hors tokens de sortie.
   * Coût annuel d'entrée : 0,084 × 1 200 000 = **100 800 USD par an**.

#### Résultat Quantifié :
* **Économie sur les tokens d'entrée** : 297 000 − 100 800 = **196 200 USD par an**, soit **−66,1 %**. (L'ancienne version annonçait 0,0612 USD par session, 73 440 USD par an et −75,2 % : ces nombres ne se retrouvent pas à partir des hypothèses et ignoraient les tokens de sortie.)
* Les tokens de sortie, facturés 15 USD par million, s'ajoutent aux deux architectures. La fenêtre glissante ne change pas le nombre de tokens générés : l'économie absolue reste la même, mais le pourcentage d'économie sur la facture totale est plus faible que −66,1 %.

---

## 6. Synthèse des Bonnes Pratiques pour l'Ingénieur IA

| Technique d'Optimisation | Complexité Temporelle / Coût | Cas d'Usage Privilégié |
| --- | --- | --- |
| **No-Memory Management** | O(K²) | À proscrire en production. |
| **Sliding Window (M)** | O(K · M) → O(K) | Agents conversationnels simples sans dépendance long-terme. |
| **Context Summarization** | O(K) avec surcoût ponctuel | Agents d'analyse complexes opérant sur de longs workflows. |
| **Prompt Caching** | Divise Pᵢₙ par 10 sur les préfixes statiques | Systèmes RAG avec gros prompts système ou documentation fixe. |


> Suite : [Tri topologique : l'algorithme de Kahn](<44-Tri-Topologique-Kahn.md>) — étape 44. La lecture de l'étape 43 s'arrête au squelette algorithmique qui suit la section 7 ; les copies ci-dessus se lisent aux étapes 50, 33, 73, 69 et 72.
