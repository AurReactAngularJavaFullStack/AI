# 09-Orchestration — Formule 01 — Score de priorité de tâche

**Dossier :** 09-Orchestration  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Platform Team, AI Agent Ops  

**Nom du fichier :** 09-Orchestration-Formule-01-Task-Priority-Score.md

## Définition

Dans une orchestration multi-agents ou un workflow, on peut calculer un score de priorité pour décider quelle tâche ou quel agent exécuter en premier.

$$
\text{priorité} = w_1 \cdot \text{urgence} + w_2 \cdot \text{impact} - w_3 \cdot \text{coût}
$$


### Définition de chaque symbole

- $$
  \text{urgence}
  $$

   : à quel point la tâche doit être faite rapidement (0-1).

- $$
  \text{impact}
  $$

  : importance métier du résultat (0-1).

- $$
  \text{coût}
  $$

   : coût estimé (tokens, temps, appels d’outils).

- \(w_1, w_2, w_3\) : poids configurables. Plus \(w_1\) est grand, plus l’urgence domine.

### Comportement

- Augmenter le poids de l’urgence fait passer les tâches critiques en premier.
- Un coût élevé réduit la priorité.

## Code Python

```python
def task_priority(urgence: float, impact: float, cout: float,
                  w1: float = 0.5, w2: float = 0.3, w3: float = 0.2) -> float:
    return w1 * urgence + w2 * impact - w3 * cout
```

## Cas d’usage métier maximum

**Finance / Banque** : prioriser une alerte de conformité sur une tâche de reporting routine.

**Immobilier** : traiter d’abord les estimations urgentes.

**Crypto** : alerte de liquidité critique avant une analyse de fond.

**Plateforme / Orchestration** : ordonnancement des agents spécialisés.

Cette formule simple structure la prise de décision dans les systèmes multi-agents.
