# 05-Memoire — Formule 02 — Score de pertinence mémoire

**Dossier :** 05-Memoire  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 05-Memoire-Formule-02-Memory-Relevance-Score.md

## Définition

Score combiné pour décider si un souvenir doit être récupéré et avec quel poids.

$$
\text{score} = \alpha \cdot \text{similarité} + \beta \cdot \text{récence} + \gamma \cdot \text{importance}
$$


### Définition de chaque symbole

- $$
  text{similarité}
  $$

   : cosine similarity avec la requête actuelle.

- $$
  \text{récence}
  $$

   : score de fraîcheur (ex. via decay).

- $$
  \text{importance}
  $$

   : poids métier du souvenir.

- $$
  \alpha, \beta, \gamma\
  $$

  : poids (somme souvent = 1).

### Comportement

- Augmenter \(
  $$
  \alpha
  $$
  \) privilégie la pertinence sémantique.

- Augmenter 
  $$
  \beta
  $$
  \) privilégie les souvenirs récents.

- Augmenter \(
  $$
  \gamma\
  $$
  ) force la remontée d’informations critiques même anciennes.

## Code Python

```python
def memory_relevance(similarity: float, recence: float, importance: float,
                     alpha: float = 0.5, beta: float = 0.3, gamma: float = 0.2) -> float:
    return alpha * similarity + beta * recence + gamma * importance
```

## Cas d’usage métier

**Finance** : remonter une ancienne contrainte de risque si elle est marquée importante.  
**Immobilier** : préférer les critères récents de recherche.  
**RH / Assurance** : équilibrer historique et actualité du dossier.
