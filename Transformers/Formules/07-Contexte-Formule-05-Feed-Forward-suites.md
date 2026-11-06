# 07-Contexte — Formule 05 — Feed-Forward Network (Position-wise)

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers  

**Nom du fichier :** 07-Contexte-Formule-05-Feed-Forward.md

## Définition complète

Après l’attention, chaque position passe indépendamment par le même réseau feed-forward.

$$
\text{FFN}(x) = \max(0, x W_1 + b_1) W_2 + b_2
$$

(ou GELU dans les modèles modernes)

### Définition de chaque symbole

- $W_1$, $W_2$ : matrices de poids.
- $b_1$, $b_2$ : biais.
- La dimension intermédiaire est généralement $4 \times d_{\text{model}}$.
- $\max(0, \cdot)$ : activation ReLU.

### Comportement

Apporte la non-linéarité et une grande partie de la capacité de transformation du modèle. Appliqué de façon identique à chaque position.

## Code Python

```python
import numpy as np

def feed_forward(x, W1, b1, W2, b2):
    return np.maximum(0, x @ W1 + b1) @ W2 + b2
```

## Cas d’usage métier

Contribue fortement à la capacité de raisonnement des modèles utilisés par les agents.
