# 07-Contexte — Formule 03 — Positional Encoding

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 07-Contexte-Formule-03-Positional-Encoding.md

## Définition complète de chaque élément

Le Positional Encoding ajoute l’information de position aux embeddings car le Transformer n’a pas d’ordre naturel.

$$
PE_{(pos, 2i)} = \sin\left( \frac{pos}{10000^{2i/d_{\text{model}}}} \right)
$$

$$
PE_{(pos, 2i+1)} = \cos\left( \frac{pos}{10000^{2i/d_{\text{model}}}} \right)
$$

### Définition de chaque symbole

- $pos$ : position du token dans la séquence.
- $i$ : indice de la dimension.
- $d_{\text{model}}$ : dimension du modèle.
- $\sin$ et $\cos$ : permettent de représenter des positions relatives facilement.

### Comportement

Les basses fréquences capturent les grandes distances, les hautes fréquences les positions fines.

## Code Python

```python
import numpy as np

def positional_encoding(position, d_model):
    pe = np.zeros((position, d_model))
    for pos in range(position):
        for i in range(0, d_model, 2):
            pe[pos, i] = np.sin(pos / (10000 ** ((2 * i) / d_model)))
            if i + 1 < d_model:
                pe[pos, i + 1] = np.cos(pos / (10000 ** ((2 * i) / d_model)))
    return pe
```

## Cas d’usage métier

Permet aux agents de comprendre l’ordre des clauses dans un document réglementaire ou l’ordre chronologique des messages.
