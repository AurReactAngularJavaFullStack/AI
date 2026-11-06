# 11-Evaluation — Formule 04 — Context Precision

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 11-Evaluation-Formule-04-Context-Precision.md

## Définition

La Context Precision évalue si les chunks pertinents sont bien classés en tête des résultats récupérés.

Une version simplifiée courante est :

$$
\text{Context Precision} = \frac{\sum_{k=1}^{K} (\text{Precision@}k \cdot v_k)}{\sum_{k=1}^{K} v_k}
$$
où \(v_k = 1\) si le chunk au rang \(k\) est pertinent, 0 sinon.

### Comportement

Plus les chunks pertinents sont haut dans le classement, plus le score augmente.

## Code Python (version simplifiée)

```python
def context_precision(relevances: list[bool]) -> float:
    """relevances[i] = True si le chunk au rang i+1 est pertinent."""
    if not any(relevances):
        return 0.0
    precisions = []
    relevant_count = 0
    for i, is_rel in enumerate(relevances, 1):
        if is_rel:
            relevant_count += 1
            precisions.append(relevant_count / i)
    return sum(precisions) / relevant_count if relevant_count else 0.0
```

## Cas d’usage

**Finance, Immobilier, Crypto, Banque, Assurance** : garantir que le contexte le plus utile arrive en premier pour le LLM, réduisant le bruit et les hallucinations.
