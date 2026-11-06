# 07-Contexte — Formule 03 — Positional Encoding (Sinusoïdal)

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 07-Contexte-Formule-03-Positional-Encoding.md

## Définition complète

Les Transformers n’ayant pas de récurrence, on ajoute un encodage de position fixe basé sur des sinus et cosinus de différentes fréquences.

$$
PE_{(pos, 2i)} = \sin\left( \frac{pos}{10000^{2i/d_{\text{model}}}} \right)
$$

$$
PE_{(pos, 2i+1)} = \cos\left( \frac{pos}{10000^{2i/d_{\text{model}}}} \right)
$$

### Définition de chaque symbole

- $pos$ : position du token (0, 1, 2…).
- $i$ : indice de dimension.
- $d_{\text{model}}$ : dimension des embeddings.
- $\sin$ et $\cos$ : fonctions de fréquences différentes.

### Comportement

Chaque position obtient un vecteur unique. Les fréquences basses capturent les grandes distances, les hautes les détails fins. L’addition se fait élément par élément avec l’embedding du token.

## Code Python

```python
import numpy as np

def sinusoidal_positional_encoding(max_len, d_model):
    pe = np.zeros((max_len, d_model))
    position = np.arange(0, max_len)[:, np.newaxis]
    div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
    pe[:, 0::2] = np.sin(position * div_term)
    pe[:, 1::2] = np.cos(position * div_term)
    return pe
```

## Cas d’usage métier

Indispensable pour que le modèle comprenne l’ordre des clauses dans un document ou l’ordre des messages dans une conversation d’agent.
