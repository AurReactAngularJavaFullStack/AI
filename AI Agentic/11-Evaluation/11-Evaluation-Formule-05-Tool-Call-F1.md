# 11-Evaluation — Formule 05 — Tool Call F1

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 11-Evaluation-Formule-05-Tool-Call-F1.md

## Définition

Le Tool Call F1 mesure la qualité des appels d’outils (nom + paramètres) indépendamment de l’ordre, via précision et recall ensemblistes.

$$
\text{Precision}_{\text{tools}} = \frac{|\text{appels corrects}|}{|\text{appels corrects}| + |\text{appels en trop}|}
$$

$$
\text{Recall}_{\text{tools}} = \frac{|\text{appels corrects}|}{|\text{appels corrects}| + |\text{appels manquants}|}
$$

Puis F1 classique.

### Comportement

- Appels en trop → précision baisse.
- Appels manquants → recall baisse.

## Code Python

```python
def tool_call_f1(expected: set, actual: set) -> float:
    tp = len(expected & actual)
    fp = len(actual - expected)
    fn = len(expected - actual)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
```

## Cas d’usage métier maximum

**Finance / Banque** : l’agent a-t-il appelé les bons outils de scoring et de conformité avec les bons identifiants ?

**Immobilier** : bons appels aux bases de comparables et de DPE.

**Crypto** : bons appels aux explorers ou simulateurs.

**Assurance, RH, BTP** : outils métier correctement invoqués.

Un F1 élevé sur les tool calls est critique pour la fiabilité des agents en production.
