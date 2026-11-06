# 07-Contexte — Formule 01 — Scaled Dot-Product Attention

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 07-Contexte-Formule-01-Scaled-Dot-Product-Attention.md

## Définition complète

C’est le mécanisme central des Transformers. Il calcule des scores d’attention entre toutes les queries et toutes les keys, les scale, les transforme en probabilités, puis fait la somme pondérée des values.

$$
\text{Attention}(Q, K, V) = \text{softmax}\left( \frac{QK^\top}{\sqrt{d_k}} \right) V
$$

### Définition de chaque symbole

- $Q$ : matrice des Queries ($n \times d_k$).
- $K$ : matrice des Keys ($n \times d_k$).
- $V$ : matrice des Values ($n \times d_v$).
- $d_k$ : dimension des keys/queries.
- $\sqrt{d_k}$ : facteur de scaling pour éviter que les produits scalaires deviennent trop grands.
- $\text{softmax}$ : convertit les scores en probabilités (chaque ligne somme à 1).

### Comportement

Sans le scaling par $\sqrt{d_k}$, le softmax sature et l’apprentissage devient difficile. Plus un score est élevé relativement aux autres, plus le poids correspondant se rapproche de 1.

## Code Python

```python
import numpy as np

def scaled_dot_product_attention(Q, K, V):
    d_k = Q.shape[-1]
    scores = (Q @ K.T) / np.sqrt(d_k)
    weights = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    weights = weights / np.sum(weights, axis=-1, keepdims=True)
    return weights @ V
```

## Cas d’usage métier

Permet aux agents de se concentrer sur les passages pertinents d’un long contrat, d’un dossier de crédit ou d’un historique de conversation.
