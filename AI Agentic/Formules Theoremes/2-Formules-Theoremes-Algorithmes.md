# 06-RAG — 02-Formules, Théorèmes et Algorithmes

**Version enrichie — Démonstrations détaillées + code Python pour chaque formule**

## Similarité cosinus — Formule, démonstrations multiples et code

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}}
$$



### Démonstration 1 (vecteurs 3D — déjà vue, répétée pour clarté)

$$
(\mathbf{q} = [0.8, 0.3, 0.5]), (\mathbf{d} = [0.7, 0.4, 0.6])
$$

Produit scalaire = 0.98  
$$
(\|\mathbf{q}\| \approx 0.990), (\|\mathbf{d}\| \approx 1.005)  
(\cos \approx 0.985)
$$


### Démonstration 2 (vecteurs 4D — cas plus réaliste)

$$
(\mathbf{q} = [0.6, 0.2, 0.8, 0.1])  
(\mathbf{d} = [0.5, 0.3, 0.7, 0.2])
$$



1. Dot = 0.6*0.5 + 0.2*0.3 + 0.8*0.7 + 0.1*0.2 = 0.30 + 0.06 + 0.56 + 0.02 = 0.94

2. $$
   1. (\|\mathbf{q}\| = \sqrt{0.36 + 0.04 + 0.64 + 0.01} = \sqrt{1.05} \approx 1.025)
   2. (\|\mathbf{d}\| = \sqrt{0.25 + 0.09 + 0.49 + 0.04} = \sqrt{0.87} \approx 0.933)
   3. (\cos = 0.94 / (1.025 * 0.933) \approx 0.94 / 0.956 \approx 0.983)
   $$

   

### Code Python complet

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calcule la similarité cosinus entre deux vecteurs."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("Les vecteurs doivent avoir la même dimension")
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))

# Tests
q = np.array([0.8, 0.3, 0.5])
d = np.array([0.7, 0.4, 0.6])
print(cosine_similarity(q, d))  # ≈ 0.985

q2 = np.array([0.6, 0.2, 0.8, 0.1])
d2 = np.array([0.5, 0.3, 0.7, 0.2])
print(cosine_similarity(q2, d2))  # ≈ 0.983
```

## Recall@k, Precision@k, MRR — avec code

### Formules

$$
[\text{Recall@}k = \frac{|\text{pertinents} \cap \text{top-}k|}{|\text{pertinents}|}]

[\text{Precision@}k = \frac{|\text{pertinents} \cap \text{top-}k|}{k}]

[text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}]
$$



### Code Python

```python
from typing import List, Set

def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    top_k = set(retrieved[:k])
    if not relevant:
        return 0.0
    return len(top_k & relevant) / len(relevant)

def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    top_k = set(retrieved[:k])
    return len(top_k & relevant) / k if k > 0 else 0.0

def mean_reciprocal_rank(ranks: List[int]) -> float:
    """ranks : liste des rangs du premier document pertinent (1-based). 0 si aucun."""
    if not ranks:
        return 0.0
    return sum(1.0 / r if r > 0 else 0.0 for r in ranks) / len(ranks)

# Exemple
retrieved = ["docA", "docB", "docC", "docD"]
relevant = {"docB", "docE"}
print(recall_at_k(retrieved, relevant, 3))     # 0.5
print(precision_at_k(retrieved, relevant, 3))  # 0.333
print(mean_reciprocal_rank([2, 1, 5]))         # moyenne des 1/rank
```

## Hybrid score

$$
[\text{score final} = \alpha \cdot \text{cosine} + (1 - \alpha) \cdot\text{BM25\_normalized}]
$$

Code :

```python
def hybrid_score(cosine: float, bm25_norm: float, alpha: float = 0.7) -> float:
    return alpha * cosine + (1 - alpha) * bm25_norm
```

Ces implémentations sont directement utilisables pour prototyper un retriever ou pour écrire des tests unitaires sur tes métriques de retrieval.
