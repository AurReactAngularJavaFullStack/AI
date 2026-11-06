# 11-Evaluation — Formule 10 — Exact Match

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers  

**Nom du fichier :** 11-Evaluation-Formule-10-Exact-Match.md

## Définition

L’Exact Match est une métrique binaire stricte : la réponse générée correspond-elle exactement à la réponse attendue (après normalisation éventuelle) ?

$$
\text{Exact Match} = \frac{\text{nombre de réponses exactement correctes}}{\text{nombre total de réponses}}
$$


### Définition

- 1 si la réponse est identique (après lowercasing, suppression des espaces superflus, etc.).
- 0 sinon.
- Très sévère : une réponse correcte mais formulée différemment échoue.

### Comportement

- Score élevé uniquement si le format et le contenu sont parfaitement contrôlés (structured output).
- Souvent complété par des métriques plus souples (F1, Faithfulness…).

## Code Python

```python
def exact_match(predictions: list[str], references: list[str]) -> float:
    if not predictions:
        return 0.0
    matches = sum(p.strip().lower() == r.strip().lower() for p, r in zip(predictions, references))
    return matches / len(predictions)
```

## Cas d’usage métier

**Finance / Banque** : extraction de valeurs exactes (montants, dates, codes).  
**Immobilier** : codes DPE, surfaces exactes.  
**Crypto** : adresses, noms de fonctions.  
**Assurance / BTP** : références de clauses ou numéros de normes.

Utile quand on exige une précision absolue.
