# 07-Contexte — 02-Formules et Mécanisme d’Attention

**Version enrichie avec démonstration numérique et code Python**

## Formule principale

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V
$$



## Démonstration numérique simplifiée (1 query, 3 keys, d_k = 2)

Soit :
- Query 
  $$
  \mathbf{q} = [1.0, 0.0]
  $$

- Keys :
  $$
  \mathbf{k1}=[0.9, 0.1]),(\mathbf{k2} = [0.1, 0.9]),(\mathbf{k3} = [0.5, 0.5])
  $$
  

- Values associées (pour simplifier, on prend les keys comme values)

1. Scores bruts (dot products) :
   - q·k1 = 0.9
   - q·k2 = 0.1
   - q·k3 = 0.5

2. Scaling (
   $$
   (\sqrt{2} \approx 1.414)
   $$
   ) :
   - 0.9 / 1.414 ≈ 0.636
   - 0.1 / 1.414 ≈ 0.071
   - 0.5 / 1.414 ≈ 0.354
   
3. Softmax :
   - exp(0.636) ≈ 1.889
   - exp(0.071) ≈ 1.074
   - exp(0.354) ≈ 1.425
   - Somme ≈ 4.388
   - Poids : 0.430, 0.245, 0.325

4. Sortie = somme pondérée des values.

## Code Python (version simplifiée + version matricielle)

```python
import numpy as np

def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x))  # stabilité numérique
    return e_x / e_x.sum()

def scaled_dot_product_attention(q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
    """
    q : shape (d_k,)
    K : shape (n_k, d_k)
    V : shape (n_k, d_v)
    """
    d_k = q.shape[0]
    scores = K @ q / np.sqrt(d_k)
    weights = softmax(scores)
    return weights @ V

# Exemple
q = np.array([1.0, 0.0])
K = np.array([[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]])
V = K.copy()  # simplification
print(scaled_dot_product_attention(q, K, V))
```

Ce code permet de comprendre concrètement le mécanisme et de l’adapter pour des expérimentations sur la gestion de contexte long dans tes agents.
