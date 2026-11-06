# 11-Evaluation — Formule 06 — Context Recall

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 11-Evaluation-Formule-06-Context-Recall.md

## Définition complète de chaque élément

Le Context Recall mesure si le contexte récupéré contient bien les informations nécessaires pour répondre à la question (par rapport à une réponse de référence ou ground truth).

$$
\text{Context Recall} = \frac{|\text{claims de la ground truth supportées par le contexte}|}{|\text{claims totales de la ground truth}|}
$$


### Définition de chaque symbole

- Ground truth : réponse de référence correcte et complète.
- Claims : affirmations atomiques extraites de cette ground truth.
- Numérateur : claims qui peuvent être déduites du contexte récupéré.
- Dénominateur : nombre total de claims dans la ground truth.

### Comportement

- Plus le contexte récupéré couvre les informations nécessaires, plus le score augmente.
- Un score bas signifie que des informations importantes manquent dans le retrieval, même si la génération est bonne.

## Code Python

```python
def context_recall(gt_claims: list[str], is_supported_by_context) -> float:
    if not gt_claims:
        return 0.0
    supported = sum(1 for c in gt_claims if is_supported_by_context(c))
    return supported / len(gt_claims)
```

## Cas d’usage métier maximum

**Finance / Banque** : la ground truth contient toutes les obligations réglementaires ; le contexte récupéré les couvre-t-il toutes ?

**Immobilier** : toutes les caractéristiques déterminantes du prix sont-elles présentes dans les chunks ?

**Crypto** : les mécanismes de risque clés du whitepaper sont-ils récupérés ?

**Assurance, RH, BTP** : couverture complète des règles applicables.

Context Recall complète la Context Precision : l’un mesure la pureté, l’autre la couverture.
