## 15. **Théorème de la Matrice de Covariance et ACP (Analyse en Composantes Principales)**

*Fondement de la réduction de dimensionnalité.*

- **Énoncé formel** : Soit X∈R^n×d une matrice de données centrées. La matrice de covariance Σ=(1/n)*X^T*X admet une décomposition spectrale :

  Σ=VΛV^T=∑i=1 vers d (λi vi vi vers T)

  avec λ1≥λ2≥...≥λd≥0 et V*V* orthogonale. La projection sur les k premières composantes principales minimise l'erreur de reconstruction au sens des moindres carrés.

- **Définition** : 

  L'ACP identifie les directions orthogonales de plus grande variance dans les données, permettant une réduction de dimension optimale.

- **Démonstration** : 

  Résulte du théorème spectral pour les matrices symétriques et de l'optimisation sous contrainte pour prouver l'optimalité.

- **Exemple** : 

  Réduction de dimensions de 768 (embedding BERT) à 50 pour visualisation, en préservant 90% de la variance.

- **Rôle dans les LLMs** :

  - **Visualisation d'embeddings** : 

    L'ACP est utilisée pour projeter les embeddings de haute dimension en 2D/3D pour visualisation.

  - **Compression** : 

    Réduction de la dimension des couches feed-forward ou des embeddings pour des modèles plus légers.

  - **Analyse** : 

    Compréhension de la structure des espaces d'embeddings appris.