# 06-RAG — Formule 09 — Distance Euclidienne (L2)

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 06-RAG-Formule-09-Euclidean-Distance.md

## Définition complète

La distance euclidienne (L2) mesure la distance géométrique directe entre deux vecteurs. Contrairement à la similarité cosinus, elle est sensible à la magnitude.

$$
d(\mathbf{a}, \mathbf{b}) = \|\mathbf{a} - \mathbf{b}\| = \sqrt{\sum_{i=1}^{n} (a_i - b_i)^2}
$$


### Définition de chaque symbole

- 
  $$
  \mathbf{a}, \mathbf{b}
  $$
   : vecteurs d’embeddings.

- \(a_i - b_i\) : différence sur chaque dimension.

- Plus la distance est petite, plus les vecteurs sont proches.

### Comportement par rapport au cosinus

- Le cosinus ignore la longueur ; la distance L2 en tient compte.
- Deux textes de longueurs très différentes sur le même sujet peuvent avoir un bon cosinus mais une distance L2 plus élevée.
- En pratique, pour le texte, le cosinus est généralement préféré ; la L2 est parfois utilisée après normalisation des vecteurs.

## Code Python

```python
import numpy as np

def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))
```

## Cas d’usage

**Finance, Immobilier, Crypto** : comparaison alternative ou complémentaire au cosinus, notamment quand les embeddings sont déjà normalisés. Utile pour comprendre les différences de comportement des index vectoriels.
