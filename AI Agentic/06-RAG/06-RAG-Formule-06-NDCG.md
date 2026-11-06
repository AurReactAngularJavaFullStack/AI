# 06-RAG — Formule 06 — NDCG (Normalized Discounted Cumulative Gain)

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 06-RAG-Formule-06-NDCG.md

## Définition complète

Le NDCG évalue la qualité du ranking en donnant plus de poids aux documents pertinents placés en tête, avec une décote logarithmique pour les rangs inférieurs.
$$
\text{DCG@}k = \sum_{i=1}^{k} \frac{2^{rel_i} - 1}{\log_2(i + 1)}
$$

$$
\text{NDCG@}k = \frac{\text{DCG@}k}{\text{IDCG@}k}
$$

où IDCG est le DCG idéal (meilleur ranking possible).

### Définition de chaque symbole

- \(rel_i\) : pertinence du document au rang \(i\) (souvent 0/1 ou graduée).

- $$
  \log_2(i+1)
  $$

   : facteur de décote. Plus le rang \(i\) est élevé, plus la contribution est réduite.

- IDCG : DCG du ranking parfait.

### Comportement

- Plus les documents très pertinents sont haut, plus le NDCG augmente.
- La normalisation par IDCG ramène le score entre 0 et 1.

## Code Python (version binaire simplifiée)

```python
import math

def dcg_at_k(relevances: list[int], k: int) -> float:
    return sum((2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(relevances[:k]))

def ndcg_at_k(relevances: list[int], k: int) -> float:
    dcg = dcg_at_k(relevances, k)
    ideal = sorted(relevances, reverse=True)
    idcg = dcg_at_k(ideal, k)
    return dcg / idcg if idcg > 0 else 0.0
```

## Cas d’usage métier maximum

**Finance, Immobilier, Crypto, Banque** : mesurer la qualité fine du ranking des documents récupérés, au-delà du simple Recall ou Precision. Utile quand l’ordre compte vraiment pour l’agent.
