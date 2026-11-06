# 11-Evaluation — Formule 11 — Cross-Entropy Loss (Next Token)

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers  

**Nom du fichier :** 11-Evaluation-Formule-11-Cross-Entropy.md

## Définition complète

Fonction de perte utilisée pour entraîner le modèle à prédire le token suivant.

$$
\mathcal{L} = -\frac{1}{N} \sum_{i=1}^{N} \log P(x_{i+1} | x_1, \ldots, x_i)
$$

### Définition de chaque symbole

- $N$ : nombre de tokens.
- $P(x_{i+1} | \ldots)$ : probabilité assignée par le modèle au vrai token suivant.
- Plus la perte est basse, meilleure est la prédiction.

### Comportement

Liée à la perplexité. Pénalise fortement les erreurs confiantes.

## Code Python

```python
import numpy as np

def cross_entropy_loss(log_probs):
    return -np.mean(log_probs)
```

## Cas d’usage métier

Base de l’entraînement et du fine-tuning des modèles utilisés dans les agents métier.
