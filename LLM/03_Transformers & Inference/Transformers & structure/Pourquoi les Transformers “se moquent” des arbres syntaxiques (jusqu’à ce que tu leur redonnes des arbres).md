# 8) Pourquoi les Transformers “se moquent” des arbres syntaxiques (jusqu’à ce que tu leur redonnes des arbres)

## 8.1) NLP classique vs Transformers
Avant : parsing syntaxique → arbres de dépendances/constituants → features.  
Maintenant : Transformer apprend des représentations distribuées avec attention.

### Point clé
Le Transformer n’a pas besoin d’un arbre explicite pour exploiter des relations :
- l’attention peut connecter n’importe quels tokens,
- et les couches empilent des compositions non-linéaires.

---

## 8.2) Mais… les arbres reviennent via les agents
Dès que tu fais :
- planning multi-étapes,
- tool-use,
- self-consistency,
- Tree-of-Thought,
- MCTS avec évaluations LLM,

tu recrées un arbre :
- nœud = état / prompt / trajectoire partielle,
- arêtes = action / token / outil,
- score = log-proba + reward + heuristique.

Mathématiquement, tu combines :
- probabilités de chemins (chain rule),
- exploration bandit (UCB),
- value (Bellman),
- et agrégation (log-sum-exp / marginalisation).