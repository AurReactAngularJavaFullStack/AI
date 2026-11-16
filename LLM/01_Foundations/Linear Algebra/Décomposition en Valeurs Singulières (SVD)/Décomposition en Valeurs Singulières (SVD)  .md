### 6.1. Décomposition en Valeurs Singulières (SVD)  

**Définition :** Pour toute matrice A \in \mathbb{R}^{m \times n}, il existe des matrices orthogonales U et V telles que :  

A = U \Sigma V^T..  

**Où :**  
- .\Sigma. : matrice diagonale des valeurs singulières .\sigma_1 \geq \sigma_2 \geq \dots \geq \sigma_r > 0.  
- .U. : vecteurs propres de .AA^T.  
- .V. : vecteurs propres de .A^TA.  
  

**Application LLM :**   
- Réduction de dimension dans les embeddings  
- Compression de matrices d'attention  
- Initialisation des poids (*Xavier/Glorot*)  