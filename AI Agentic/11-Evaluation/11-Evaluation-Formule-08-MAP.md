# 11-Evaluation — Formule 08 — Mean Average Precision (MAP)

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 11-Evaluation-Formule-08-MAP.md

## Définition

La Mean Average Precision moyenne les Average Precision sur un ensemble de requêtes. Elle prend en compte à la fois la précision et le ranking.

$$
\text{AP} = \frac{\sum_{k=1}^{n} (P(k) \cdot rel(k))}{\text{nombre de documents pertinents}}
$$

$$
\text{MAP} = \frac{1}{|Q|} \sum_{q \in Q} \text{AP}(q)
$$



### Définition

- \( P(k) \) : Precision@k
- \( rel(k) \) : 1 si le document au rang k est pertinent, 0 sinon
- AP récompense les systèmes qui placent les documents pertinents tôt.

## Code Python

```python
def average_precision(relevances: list[bool]) -> float:
    if not any(relevances):
        return 0.0
    precisions = []
    relevant_so_far = 0
    for i, rel in enumerate(relevances, 1):
        if rel:
            relevant_so_far += 1
            precisions.append(relevant_so_far / i)
    return sum(precisions) / relevant_so_far

def mean_average_precision(list_of_relevances: list[list[bool]]) -> float:
    if not list_of_relevances:
        return 0.0
    return sum(average_precision(r) for r in list_of_relevances) / len(list_of_relevances)
```

## Cas d’usage

**Finance, Immobilier, Crypto, Banque** : évaluation globale de la qualité du ranking sur un jeu de tests métier. Complète Recall, Precision et NDCG.
