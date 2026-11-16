## Optimalité (intuition) du codage de Huffman (greedy)

### Énoncé (version pratique)

Le codage de Huffman construit un code préfixe qui minimise la longueur moyenne :
$$
\mathbb{E}[\ell] = \sum_i p_i \ell_i
$$

### Idée de démonstration

Dans un code optimal :

- Les deux symboles de plus faible probabilité doivent être **frères** (même parent) au niveau le plus profond.
   On peut les fusionner en un “super-symbole” et appliquer une récurrence. Le greedy de Huffman reproduit exactement ce raisonnement.

### Rôle LLM

Ce n’est pas le cœur des Transformers, mais ça éclaire :

- Pourquoi des structures d’arbres et des heuristiques greedy apparaissent en NLP.
- Pourquoi “préfixe” et “probabilités” vont souvent ensemble.