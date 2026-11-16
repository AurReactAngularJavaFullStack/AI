## E1) Équation d’optimalité de Bellman (RL / planification)

### Setup

Valeur d’un état $s$ sous une politique optimale :

- récompense immédiate $r$
- facteur d’actualisation $\gamma \in (0,1)$

### Théorème (Bellman optimalité)

$$
V^\*(s) = \max_{a}\Big( R(s,a) + \gamma \sum_{s'} P(s' \mid s,a) V^\*(s') \Big)
$$

### Interprétation arbre

Choisir une action $a$ ouvre des branches $s'$ avec probas $P(s'|s,a)$.
 Bellman dit : “la meilleure décision locale combine reward immédiat + valeur future attendue”.

### Rôle LLM

Dès que tu fais des **agents** (tool-use, navigation, planification), tu retombes sur :

- arbre de décisions,
- estimations de valeur,
- recherche (MCTS, best-first).