## 10. **Théorème de Perron-Frobenius (pour les chaînes de Markov et l'attention)**

*Fondement de l'analyse des processus stochastiques et des matrices de transition.*

- **Énoncé formel** : 

  Soit A une matrice carrée à coefficients strictement positifs. Alors :

  1. A admet une valeur propre réelle positive λPF (valeur propre de Perron-Frobenius) telle que ∣λ∣<λPF pour toute autre valeur propre λ.
  2. La valeur propre λPF est simple (multiplicité algébrique 1).
  3. Il existe des vecteurs propres à gauche et à droite strictement positifs associés à λPF.

- **Définition** : 

  Ce théorème caractérise les valeurs propres et vecteurs propres des matrices à coefficients positifs, crucial pour l'analyse des chaînes de Markov et des processus stochastiques.

- **Démonstration (esquisse)** : 

  Utilise le théorème du point fixe de Brouwer pour montrer l'existence d'un vecteur propre positif, puis des arguments d'analyse pour établir les propriétés de dominance.

- **Exemple** : 

  Pour une matrice de transition d'une chaîne de Markov irréductible et apériodique, λPF=1, et le vecteur propre correspondant donne la distribution stationnaire.

- **Rôle dans les LLMs** :

  - **Mécanismes d'attention** : 

    Les matrices d'attention sont stochastiques (chaque ligne somme à 1). Le théorème de Perron-Frobenius permet d'analyser le comportement limite des itérations d'attention, comme dans les Transformers avec autorécurrence.

  - **Analyse de convergence** : 

    Dans les méthodes de diffusion ou les modèles markoviens, ce théorème garantit l'existence d'une distribution stationnaire et la convergence vers celle-ci.