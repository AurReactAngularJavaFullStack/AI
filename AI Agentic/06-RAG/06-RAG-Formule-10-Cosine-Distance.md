# 06-RAG — Formule 10 — Cosine Distance

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 06-RAG-Formule-10-Cosine-Distance.md

## Définition complète

La distance cosinus est simplement le complément de la similarité cosinus. Elle est parfois utilisée comme métrique de distance dans les index vectoriels.

$$
\text{cosine distance} = 1 - \cos(\theta) = 1 - \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|}
$$


### Définition de chaque symbole

- \(
  $$
  \cos(\theta)
  $$
  \) : similarité cosinus (entre -1 et 1, souvent 0 à 1 pour les embeddings de texte).

- Plus la distance est proche de 0, plus les vecteurs sont proches.

- Plus elle se rapproche de 1 (ou 2), plus les vecteurs sont éloignés.

### Comportement

- Distance = 0 → vecteurs identiques en direction.
- Distance = 1 → orthogonalité (aucune similarité).
- Certains moteurs (ex. certains index) optimisent sur la distance plutôt que sur la similarité.

## Code Python

```python
import numpy as np

def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)
    return float(1.0 - sim)
```

## Cas d’usage métier

**Finance, Immobilier, Crypto, Banque** : utilisée en interne par certains vector stores. Comprendre la relation avec la similarité cosinus aide à interpréter les scores renvoyés par l’index.
