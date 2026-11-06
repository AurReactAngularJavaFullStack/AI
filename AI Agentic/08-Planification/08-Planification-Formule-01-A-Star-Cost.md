# 08-Planification — Formule 01 — Coût dans A* (heuristique)

**Dossier :** 08-Planification  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, Product Engineers  

**Nom du fichier :** 08-Planification-Formule-01-A-Star-Cost.md

## Définition

Dans l’algorithme A* utilisé pour la planification, le coût estimé d’un chemin passant par un nœud \( n \) est :

$$
f(n) = g(n) + h(n)
$$


### Définition de chaque symbole

- \( g(n) \) : coût réel du chemin depuis le départ jusqu’à \( n \).
- \( h(n) \) : estimation heuristique du coût restant de \( n \) jusqu’à l’objectif. Pour que A* soit optimal, \( h \) doit être admissible (ne jamais surestimer).
- \( f(n) \) : estimation du coût total. A* développe en priorité les nœuds avec le plus petit \( f \).

### Comportement

- Une heuristique \( h \) plus précise (mais toujours admissible) accélère la recherche.
- Si \( h = 0 \), A* devient Dijkstra (exploration plus large).

## Code Python (conceptuel)

```python
def f_cost(g: float, h: float) -> float:
    return g + h
```

## Cas d’usage métier

**Finance** : planification d’une séquence d’analyses (collecte → calcul → validation) avec coûts estimés.

**Immobilier / BTP** : décomposition de tâches d’estimation ou de conformité avec priorisation.

**RH / Assurance** : workflows multi-étapes où certaines actions ont un coût (appels d’outils, validations humaines).

Cette formule simple structure de nombreux planificateurs d’agents.
