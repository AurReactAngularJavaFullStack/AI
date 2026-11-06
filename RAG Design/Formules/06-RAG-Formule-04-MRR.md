# 06-RAG — Formule 04 — Mean Reciprocal Rank (MRR)

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 06-RAG-Formule-04-MRR.md

## Définition complète

Le MRR mesure à quel point le premier document pertinent est bien classé. Plus il est haut dans le classement, mieux c’est.

$$
\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}
$$


### Définition de chaque symbole

- \(Q\) : l’ensemble des requêtes de test.

- $$
  \text{rank}_i
  $$

  : le rang (1-based) du premier document pertinent pour la requête \(i\). Si aucun, on considère souvent 0.

- $$
  1/\text{rank}_i
  $$

   : reciprocal rank. Rang 1 → 1.0, rang 2 → 0.5, rang 5 → 0.2.

### Comportement

- Plus le premier document pertinent est haut (rank petit), plus le MRR augmente.
- Un MRR proche de 1 signifie que le bon document est presque toujours en première position.

## Code Python

```python
def mean_reciprocal_rank(ranks: List[int]) -> float:
    if not ranks:
        return 0.0
    return sum(1.0 / r if r > 0 else 0.0 for r in ranks) / len(ranks)
```

## Cas d’usage métier maximum

**Finance / Banque** : pour une question de conformité urgente, le document clé doit être en tête. Un MRR bas = l’utilisateur ou l’agent doit scroller.

**Immobilier** : le comparable le plus proche doit apparaître en premier.

**Crypto** : la clause de risque la plus pertinente en position 1.

**Autres domaines** : même exigence de ranking de qualité.

Le MRR est particulièrement utile quand on ne récupère que peu de documents (top-3 ou top-5).
