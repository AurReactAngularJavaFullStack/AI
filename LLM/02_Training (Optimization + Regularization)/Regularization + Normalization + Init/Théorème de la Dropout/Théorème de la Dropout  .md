## 20. Théorèmes de Régularisation  

### 20.1. Théorème de la Dropout  

**Pour une probabilité de rétention p :**  

\hat{x}_i = \frac{x_i \cdot r_i}{p}, \quad r_i \sim \text{Bernoulli}(p)  

**Entraînement équivalent :**  

\mathbb{E}[y] = x  

**Application LLM :** 

Prévention du sur-apprentissage dans les couches fully-connected.  