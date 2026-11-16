## 18. Théorèmes des Transformateurs (Transformers)  

### 18.1. Théorème de la Capacité d'Attention  

**Complexité de l'attention :** Pour une séquence de longueur n et dimension d :  

\text{Complexité} = O(n^2 d)  

**Formule de la matrice d'attention :**  

A = \text{softmax}\left(\frac{QK^T}{\sqrt{d}} + M\right)  

**Où M est le masque :**  

M_{ij} = \begin{cases} 0 & \text{si } i \leq j \\ -\infty & \text{sinon} \end{cases}  

**Application LLM :** 

Limitations mémoire pour les longues séquences, optimisation avec Flash Attention.  

---