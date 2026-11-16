## 4. **Théorème d'Approximation des Priors (pour les LLMs)**

*Permet de représenter des croyances a priori complexes de manière calculable.*

- **Énoncé formel (Théorème 2)** : 

  Toute distribution a priori continue et bornée sur des probabilités multinomiales peut être approximée par un mélange fini de distributions de Dirichlet.

- **Définition** : 

  Ce théorème fournit un outil mathématique pour représenter des croyances initiales complexes sur les distributions de mots (les *priors*) en utilisant une combinaison de distributions de Dirichlet, qui sont bien comprises et manipulables.

- **Démonstration (esquisse)** : 

  Il s'appuie sur des résultats de densité en théorie de l'approximation. 

  L'ensemble des mélanges finis de distributions de Dirichlet est dense dans l'espace des distributions continues et bornées sur le simplexe des probabilités multinomiales.

- **Exemple** : 

  Avant de voir un prompt, un LLM peut avoir une croyance a priori complexe sur la fréquence des différents mots. Ce théorème permet d'approcher cette croyance par un mélange de quelques distributions de Dirichlet standard.

- **Rôle dans les LLMs** : 

  Ce théorème rend l'inférence Bayésienne **calculatoirement réalisable** dans les LLMs. La distribution de Dirichlet étant le *conjugué a priori* de la distribution multinomiale, si le prior est un mélange de Dirichlets, le posterior (croyance mise à jour) reste dans la même famille et peut être calculé analytiquement, simplifiant énormément les mises à jour du modèle.