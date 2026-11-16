## **Théorème de la Dynamique du Gradient (Descente de Gradient)**

*Fondement de l'optimisation des modèles d'apprentissage automatique.*

- **Énoncé formel** : 

  Soit f:Rd→R:R^d→R une fonction L-lisse (gradient Lipschitz-continu) et μ-fortement convexe. 

  Alors la descente de gradient avec taux d'apprentissage η≤1/L converge linéairement vers le minimum global x∗*x*∗ :

  f(xk+1)−f(x∗)≤(1−μ/L)*(f(xk)−f(x∗))

  De plus, ∥xk−x∗∥²≤(1−μη)^k∥x0−x∗∥²

- **Définition** : 

  Ce théorème garantit la convergence de l'algorithme de descente de gradient pour les fonctions convexes lisses et fortement convexes, avec des bornes explicites sur le taux de convergence.

- **Démonstration (esquisse)** : 

  Utilise l'inégalité de descente fondamentale : f(xk+1)≤f(xk)−η/2∥∇f(xk)∥² pour η≤1/L, puis exploite la convexité forte pour établir la convergence linéaire.

- **Exemple** : 

  Pour une fonction quadratique f(x)=((1/2)x^T) Ax−(b^T)*x avec A définie positive, la descente de gradient converge exponentiellement vite vers la solution.

- **Rôle dans les LLMs** :

  - **Entraînement** : 

    Les variantes de descente de gradient (SGD, Adam) sont utilisées pour optimiser les centaines de milliards de paramètres des LLMs. Ce théorème fournit l'intuition fondamentale sur comment la mise à jour des paramètres réduit la fonction de perte.

  - **Analyse de convergence** : 

    Même si les fonctions de perte des LLMs ne sont pas convexes (elles sont hautement non-convexes), les résultats pour le cas convexe servent de point de référence et inspirent les méthodes d'optimisation pratiques.