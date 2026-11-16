## 14. **Théorème de la Dynamique des Gradients Stochastiques (SGD)**

*Fondement de l'entraînement à grande échelle.*

- **Énoncé formel** : Sous certaines conditions de régularité (fonction objectif L-lisse, gradients bornés), SGD avec taux d'apprentissage décroissant ηt=O(1/t) converge :

  min ⁡k=1,...,T   E[∥∇f(xk)∥²]≤O(1/square root(T)

  Pour les fonctions fortement convexes, on a convergence à taux O(1/T).

- **Définition** : 

  Ce théorème garantit la convergence de SGD même avec du bruit dans l'estimation du gradient, ce qui est essentiel pour l'entraînement sur grands jeux de données.

- **Démonstration (esquisse)** : 

  Utilise des martingales et des inégalités de concentration pour contrôler le bruit, combinées avec l'analyse de la descente de gradient déterministe.

- **Exemple** : 

  L'entraînement de LLMs avec des batchs de quelques centaines d'exemples parmi des milliards converge vers un bon minimum malgré le bruit important.

- **Rôle dans les LLMs** :

  - **Optimisation pratique** : 

    Tous les LLMs modernes sont entraînés avec des variantes de SGD (Adam, AdaGrad, etc.). Ces théorèmes garantissent que l'algorithme converge malgré le bruit.

  - **Sélection d'hyperparamètres** : 

    Les conditions sur le taux d'apprentissage proviennent directement de ces analyses théoriques.