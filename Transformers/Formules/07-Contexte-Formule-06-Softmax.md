# 07-Contexte — Formule 06 — Softmax (Inference)

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 07-Contexte-Formule-06-Softmax.md

## Définition complète

Lors de l’inférence, les logits sont convertis en probabilités via le softmax.

$$
P(w_i) = \frac{e^{\text{logit}_i}}{\sum_{j=1}^{V} e^{\text{logit}_j}}
$$

### Définition de chaque symbole

- $\text{logit}_i$ : score brut du modèle pour le token $i$.
- $V$ : taille du vocabulaire.
- $e^{\cdot}$ : exponentielle.
- Le dénominateur normalise pour que la somme des probabilités fasse 1.

### Comportement

Plus un logit est grand par rapport aux autres, plus sa probabilité se rapproche de 1.

## Code Python

```python
import numpy as np

def softmax(logits):
    exp = np.exp(logits - np.max(logits))
    return exp / np.sum(exp)
```

## Cas d’usage métier

Utilisé à chaque étape de génération de texte par les agents (greedy, top-k, top-p).
