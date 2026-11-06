# 07-Contexte — Formule 04 — Layer Normalization

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers  

**Nom du fichier :** 07-Contexte-Formule-04-Layer-Normalization.md

## Définition complète

La Layer Normalization normalise les activations sur la dimension des features pour stabiliser l’entraînement des réseaux profonds.

$$
\text{LayerNorm}(x) = \gamma \odot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta
$$

### Définition de chaque symbole

- $\mu$ : moyenne des activations du token courant.
- $\sigma^2$ : variance des activations.
- $\epsilon$ : petite constante pour la stabilité numérique.
- $\gamma$ : paramètre de scale (appris).
- $\beta$ : paramètre de shift (appris).
- $\odot$ : produit élément par élément.

### Comportement

Réduit les problèmes de gradients qui explosent ou disparaissent. Utilisée après l’attention et après le feed-forward (Add & Norm).

## Code Python

```python
import numpy as np

def layer_norm(x, gamma, beta, eps=1e-5):
    mean = np.mean(x, axis=-1, keepdims=True)
    var = np.var(x, axis=-1, keepdims=True)
    return gamma * (x - mean) / np.sqrt(var + eps) + beta
```

## Cas d’usage métier

Indispensable pour la stabilité des modèles utilisés dans des agents critiques (conformité bancaire, assurance, etc.).
