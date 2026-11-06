# 07-Contexte — Formule 04 — Layer Normalization

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers  

**Nom du fichier :** 07-Contexte-Formule-04-Layer-Normalization.md

## Définition complète de chaque élément

La Layer Normalization normalise les activations pour stabiliser l’entraînement.

$$
\text{LayerNorm}(x) = \gamma \odot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta
$$

### Définition de chaque symbole

- $\mu$ : moyenne des features du token.
- $\sigma^2$ : variance.
- $\epsilon$ : petite constante de stabilité numérique.
- $\gamma$ et $\beta$ : paramètres appris (scale et shift).

### Comportement

Réduit fortement les problèmes de gradients instables dans les réseaux profonds.

## Code Python

```python
import numpy as np

def layer_norm(x, gamma, beta, eps=1e-5):
    mean = np.mean(x, axis=-1, keepdims=True)
    var = np.var(x, axis=-1, keepdims=True)
    return gamma * (x - mean) / np.sqrt(var + eps) + beta
```

## Cas d’usage métier

Indispensable pour la stabilité des modèles utilisés dans des agents critiques (banque, assurance, conformité).
