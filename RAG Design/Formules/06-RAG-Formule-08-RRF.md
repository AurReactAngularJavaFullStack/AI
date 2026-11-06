# 06-RAG — Formule 08 — Reciprocal Rank Fusion (RRF)

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 06-RAG-Formule-08-RRF.md

## Définition complète

Le Reciprocal Rank Fusion est une méthode simple et efficace pour fusionner plusieurs classements (par exemple cosine et BM25) sans avoir à normaliser les scores.

$$
\text{RRF}(d) = \sum_{r \in R} \frac{1}{k + \text{rank}_r(d)}
$$


### Définition de chaque symbole

- \( R \) : l’ensemble des rankings à fusionner (ex. ranking cosine + ranking BM25).

- \( 
  $$
  \text{rank}_r(d)
  $$
   \) : le rang du document \( d \) dans le ranking \( r \) (1 = meilleur).

- \( k \) : constante de lissage (souvent 60). Plus \( k \) est grand, moins les différences de rang en tête sont amplifiées.

### Comportement

- Un document bien classé dans plusieurs rankings obtient un score RRF élevé.
- La méthode est robuste car elle ne dépend pas de l’échelle des scores originaux.

## Code Python

```python
from collections import defaultdict

def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, 1):
            scores[doc_id] += 1.0 / (k + rank)
    return dict(scores)
```

## Cas d’usage métier maximum

**Finance, Immobilier, Crypto, Banque, Assurance** : fusionner proprement les résultats d’une recherche sémantique et d’une recherche lexicale sans avoir à calibrer des poids \(\alpha\). Très utilisé en production pour les systèmes hybrides.
