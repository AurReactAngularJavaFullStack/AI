# 07-Contexte — Formule 01 — Scaled Dot-Product Attention (version soignée)

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 07-Contexte-Formule-01-Scaled-Dot-Product-Attention.md

## Définition complète

$$
\text{Attention}(Q, K, V) = \text{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V
$$

### Définition de chaque symbole

- $Q$ : matrice des queries.
- $K$ : matrice des keys.
- $V$ : matrice des values.
- $d_k$ : dimension des keys/queries.
- $\sqrt{d_k}$ : facteur de scaling.
- $\text{softmax}$ : normalisation en probabilités.

### Comportement

Sans le $\sqrt{d_k}$, les valeurs deviennent trop grandes et le softmax sature.

## Code Python

```python
import numpy as np

def scaled_dot_product_attention(Q, K, V):
    d_k = Q.shape[-1]
    scores = (Q @ K.T) / np.sqrt(d_k)
    weights = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    weights /= weights.sum(axis=-1, keepdims=True)
    return weights @ V
```

## Cas d’usage métier

Cœur du mécanisme qui permet aux agents de se concentrer sur les parties importantes d’un long contexte métier.
