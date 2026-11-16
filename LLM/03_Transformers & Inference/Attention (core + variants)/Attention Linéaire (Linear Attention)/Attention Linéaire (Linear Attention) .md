### 26.2. Attention Linéaire (Linear Attention)  

**Formule :**  

\text{Attention}(Q,K,V) = \phi(Q) \phi(K)^T V 

**Où \phi est une fonction de noyau :**  

\phi(x) = \text{elu}(x) + 1  

**Complexité :** 

O(n d^2)$ au lieu de $O(n^2 d).  