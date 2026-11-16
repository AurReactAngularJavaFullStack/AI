## 26. Formules Complémentaires Essentielles  

### 26.1. Attention Échelonnée (Sparse Attention)  

**Pour une séquence de longueur n avec fenêtre w :**  

\text{Complexité} = O(n \cdot w \cdot d) 

**Formule :**  

A_{ij} = \begin{cases} \text{softmax}(Q_i K_j^T / \sqrt{d}) & \text{si } |i-j| \leq w \\ -\infty & \text{sinon} \end{cases}