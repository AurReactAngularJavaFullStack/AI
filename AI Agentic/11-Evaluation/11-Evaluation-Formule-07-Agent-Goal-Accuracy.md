# 11-Evaluation — Formule 07 — Agent Goal Accuracy

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers, Forward-Deployed Engineers  

**Nom du fichier :** 11-Evaluation-Formule-07-Agent-Goal-Accuracy.md

## Définition

L’Agent Goal Accuracy est une métrique binaire (ou taux) qui indique si l’agent a atteint l’objectif métier final, indépendamment du chemin emprunté.

$$
\text{Agent Goal Accuracy} = \frac{\text{nombre de tâches où l'objectif est atteint}}{\text{nombre total de tâches évaluées}}
$$


### Définition

- Objectif atteint : critère métier satisfait (facture générée conforme, décision de crédit correcte, estimation dans la fourchette, etc.).
- C’est souvent 0 ou 1 par exemple, puis moyenné.

### Comportement

Plus le taux est élevé, plus l’agent est fiable sur le résultat final.

## Code Python

```python
def agent_goal_accuracy(successes: list[bool]) -> float:
    if not successes:
        return 0.0
    return sum(successes) / len(successes)
```

## Cas d’usage métier maximum

**Finance / Banque** : le crédit a-t-il été correctement accordé ou refusé selon les règles ?

**Immobilier** : l’estimation finale est-elle dans la fourchette acceptable ?

**Crypto** : l’alerte de risque a-t-elle été correctement déclenchée ?

**Assurance** : la couverture a-t-elle été correctement décidée ?

**RH / BTP** : l’onboarding ou la facture est-il conforme et complet ?

Cette métrique regarde le résultat métier, pas seulement les étapes intermédiaires.
