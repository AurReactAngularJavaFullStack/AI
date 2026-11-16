## 11. **Théorème de Décomposition de Rao-Blackwell**

*Fondement de la réduction de variance dans les méthodes d'estimation.*

- **Énoncé formel** : 

  Soit δ(X) un estimateur sans biais d'un paramètre θ, et soit T(X) une statistique exhaustive pour θ. Alors l'estimateur δ∗(X)=E[δ(X)∣T(X)] est :

  1. Sans biais : E[δ∗(X)]=θ*E*[*δ*∗(*X*)]=*θ*
  2. De variance inférieure ou égale : Var(δ∗(X))≤Var(δ(X))

- **Définition** : 

  Ce théorème montre comment améliorer un estimateur en le conditionnant par une statistique exhaustive, réduisant ainsi sa variance sans introduire de biais.

- **Démonstration (esquisse)** : 

  Utilise l'inégalité de Jensen pour la fonction convexe carré et les propriétés de l'espérance conditionnelle.

- **Exemple** : 

  Si on veut estimer la moyenne μ d'une distribution normale avec variance connue, la moyenne conditionnelle par rapport à la statistique exhaustive (la somme des observations) donne le même estimateur mais avec variance potentiellement réduite.

- **Rôle dans les LLMs / Arbres** :

  - **Méthodes ensemblistes** : 

    Le théorème justifie théoriquement pourquoi le bagging (bootstrap aggregating) améliore la stabilité des prédictions : chaque arbre est un estimateur, et leur moyenne conditionnellement aux données réduit la variance.

  - **Inférence Bayésienne** : 

    Dans les approches variationnelles, le théorème guide la construction d'estimateurs à variance réduite pour les gradients.