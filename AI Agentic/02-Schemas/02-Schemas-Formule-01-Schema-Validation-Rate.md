# 02-Schemas — Formule 01 — Taux de validation de schéma

**Dossier :** 02-Schemas  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers  

**Nom du fichier :** 02-Schemas-Formule-01-Schema-Validation-Rate.md

## Définition

$$
\text{taux de validation} = \frac{\text{nombre d'appels / réponses valides selon le schéma}}{\text{nombre total d'appels / réponses}}
$$



### Définition

- Numérateur : éléments qui passent la validation JSON Schema / Pydantic.
- Dénominateur : total des tentatives.
- Plus le taux est proche de 1, plus les échanges sont fiables.

### Comportement

- Un taux qui baisse indique une dérive du modèle ou un schéma trop strict / mal conçu.

## Code Python

```python
def schema_validation_rate(valid: int, total: int) -> float:
    return valid / total if total else 0.0
```

## Cas d’usage métier

**Bancaire, Immobilier, Crypto, Finance, Assurance, BTP** : surveiller que les tool calls et les sorties structurées restent conformes aux schémas en production.
