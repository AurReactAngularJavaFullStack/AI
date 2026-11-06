# 11-Evaluation — Formule 03 — Precision, Recall et F1

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 11-Evaluation-Formule-03-Precision-Recall-F1.md

## Définitions complètes

$$
\text{Precision} = \frac{TP}{TP + FP}, \quad
\text{Recall} = \frac{TP}{TP + FN}, \quad
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
$$



### Définition de chaque symbole

- TP (True Positive) : éléments correctement identifiés comme positifs.
- FP (False Positive) : éléments incorrectement identifiés comme positifs.
- FN (False Negative) : éléments positifs manqués.
- F1 : moyenne harmonique qui équilibre précision et recall.

### Comportement

- Plus de FP → précision baisse.
- Plus de FN → recall baisse.
- F1 pénalise les déséquilibres.

## Code Python

```python
def precision_recall_f1(tp: int, fp: int, fn: int):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1
```

## Cas d’usage métier maximum

**Finance / Banque** : évaluation des appels d’outils de scoring ou de conformité. F1 élevé = bons outils appelés avec les bons paramètres.

**Immobilier** : détection correcte des caractéristiques pertinentes d’un bien.

**Crypto** : identification correcte des risques dans un audit.

**Assurance, RH, BTP** : même logique pour les tool calls et les classifications.

Ces métriques s’appliquent aussi bien au retrieval qu’aux décisions d’agents.
