## 📂 Fichier 04 - Orchestration Graphes : Formules Manquantes

### Leçon 4.1 : Algorithme de Tri Topologique (Kahn's Algorithm)

**Définition** Le tri topologique est un algorithme qui ordonne linéairement les sommets d'un graphe orienté acyclique (DAG) tel que pour chaque arête (u,v)(*u*,*v*), le sommet u*u* apparaît avant v*v* dans l'ordre.

**Rôle** Garantir l'ordre d'exécution mathématique des tâches dans un système multi-agents. Sans cela, un agent pourrait tenter d'exécuter une tâche avant que ses dépendances ne soient résolues.

**Équation Mathématique**

$$
InDegree(v)=∑u∈VAu,v InDegree(v)=u∈V∑Au,v
$$

$$
TopologicalOrder={v∈V∣InDegree(v)=0}∪resteTopologicalOrder={v∈V∣InDegree(v)=0}∪reste
$$

**Complexité** : O(∣V∣+∣E∣)*O*(∣*V*∣+∣*E*∣) où ∣V∣∣*V*∣ est le nombre de nœuds et ∣E∣∣*E*∣ le nombre d'arêtes.

**Code Python**

```python
from collections import deque, defaultdict

def topological_sort_kahn(n, edges):
    """
    n: nombre de nœuds
    edges: liste de tuples (u, v) représentant u -> v
    Retourne l'ordre topologique ou lève une exception si cycle détecté
    """
    # Construction du graphe et calcul des degrés entrants
    adj = defaultdict(list)
    in_degree = [0] * n
    
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
    
    # File des nœuds sans dépendance (degré entrant = 0)
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    order = []
    
    while queue:
        node = queue.popleft()
        order.append(node)
        
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Détection de cycle : si tous les nœuds ne sont pas dans l'ordre
    if len(order) != n:
        raise ValueError("Cycle détecté : le graphe n'est pas un DAG")
    
    return order

# Exemple : Agent Architecte (0) -> Dev (1) -> Testeur (2)
#                    Agent Spec (3) -> Dev (1)
edges = [(0, 1), (3, 1), (1, 2)]
print(topological_sort_kahn(4, edges))  # [0, 3, 1, 2] ou [3, 0, 1, 2]
```

**Démonstration Quantifiée** 

Prenons un DAG de 5 agents : A→B*A*→*B*, A→C*A*→*C*, B→D*B*→*D*, C→D*C*→*D*, D→E*D*→*E*.

- Degrés entrants initiaux : A=0,B=1,C=1,D=2,E=1*A*=0,*B*=1,*C*=1,*D*=2,*E*=1
- Itération 1 : A*A* traité (degré 0) → B*B* et C*C* passent à degré 0
- Itération 2 : B*B* et C*C* traités → D*D* passe à degré 0
- Itération 3 : D*D* traité → E*E* passe à degré 0
- **Résultat** : [A,B,C,D,E][*A*,*B*,*C*,*D*,*E*] — 5 itérations pour 5 nœuds, confirmant O(V+E)*O*(*V*+*E*)

**Cas d'usage réels** Orchestration de pipelines MLOps : Data Ingestion → Feature Engineering → Training → Evaluation → Deployment. Chaque étape doit attendre ses dépendances.

### Leçon 4.2 : Détection de Cycle par DFS (Parcours en Profondeur)

**Définition** Algorithme qui détecte la présence d'un cycle dans un graphe orienté en utilisant une coloration des nœuds (Blanc = non visité, Gris = en cours, Noir = terminé).

**Rôle** Garde-fou essentiel pour valider qu'un workflow multi-agents est bien un DAG avant déploiement en production.

**Équation Mathématique**

Cycle  ⟺  ∃(u,v)∈E∣color(v)=Gris∧color(u)=GrisCycle⟺∃(*u*,*v*)∈*E*∣color(*v*)=Gris∧color(*u*)=Gris

**Code Python**

```python
def detect_cycle_dfs(n, edges):
    """Détecte un cycle dans un graphe orienté via DFS"""
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    
    def dfs(node):
        color[node] = GRAY  # Marque comme "en cours de traitement"
        for neighbor in adj[node]:
            if color[neighbor] == GRAY:
                return True  # Cycle détecté !
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK  # Traitement terminé
        return False
    
    for i in range(n):
        if color[i] == WHITE:
            if dfs(i):
                return True
    return False
```

**Démonstration Quantifiée** 

Graphe : A→B→C→A*A*→*B*→*C*→*A* (cycle)

- DFS sur A*A* : A*A* devient GRIS
- DFS sur B*B* : B*B* devient GRIS
- DFS sur C*C* : C*C* devient GRIS, puis visite A*A* qui est déjà GRIS → **Cycle détecté** en 3 étapes

**Cas d'usage réels**

 Validation de workflows LangGraph avant exécution. Si un agent "Rédacteur" appelle un agent "Relecteur" qui renvoie vers "Rédacteur", le système doit bloquer.

## Lecture

Les formules de ce fichier sont recopié deux fois de suite dans la même ligne, et le LaTeX ne se compile pas. Le récit qui suit vraiment l'algorithme est ailleurs.

Dans `04a_Tri_Topologique_Kahn.md`, cinq agents et les arêtes `(0, 2), (1, 2), (2, 3), (3, 4)`. Le degré entrant devient `[0, 0, 2, 1, 1]`. Kahn retire d'abord 0 et 1, et l'agent 2 ne part que lorsque son compte est tombé de 2 à 0. Si l'ordre final n'a pas 5 noms, un cycle a empêché un compte d'atteindre zéro.

Dans `04b_Detection_Cycle_DFS.md`, les couleurs disent où en est la visite. Blanc : pas vu. Gris : sur le chemin en cours. Noir : terminé. Retrouver un gris, c'est une arête qui remonte vers un ancêtre. Sur `(0, 1), (1, 2), (2, 0)`, le chemin reconstruit par les parents vaut `[0, 1, 2, 0]`. Kahn dit seulement qu'un cycle existe. DFS donne les noms des agents pris dedans.