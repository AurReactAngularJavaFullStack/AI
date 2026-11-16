## E3) A* : admissibilité → optimalité (best-first sur arbre/graphe)

### Définitions

- Coût réel depuis départ : $g(n)$
- Heuristique vers objectif : $h(n)$
- Score : $f(n)=g(n)+h(n)$

Heuristique **admissible** :
$$
h(n)\le h^\*(n)
$$
où $h^*(n)$ est le vrai coût minimal restant.

### Théorème

Si $h$ est admissible, A* trouve un chemin optimal (dans les conditions usuelles : coûts non négatifs, etc.).

### Rôle LLM

Moins “standard” que MCTS, mais utile dès que tu fais :

- planification symbolique,
- recherche de séquence optimale (dans l’arbre des tokens) avec contraintes.