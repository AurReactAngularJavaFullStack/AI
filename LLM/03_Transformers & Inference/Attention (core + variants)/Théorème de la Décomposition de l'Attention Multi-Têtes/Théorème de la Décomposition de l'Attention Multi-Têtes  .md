### 18.2. Théorème de la Décomposition de l'Attention Multi-Têtes  

**Pour h têtes :**  

\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h) W^O  

\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)  

**Application LLM :** Permet de paralléliser les calculs et de capturer différents types de dépendances.  
