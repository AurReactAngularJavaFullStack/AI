# 06-RAG — Formule 02 — Recall@k

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  

**Nom du fichier :** 06-RAG-Formule-02-Recall-at-k.md

## Définition complète de chaque élément de la formule

Le Recall@k mesure la proportion des documents réellement pertinents qui ont été récupérés parmi les k premiers résultats. C’est une métrique de couverture : est-ce que le retriever a ramené ce qu’il fallait ?
$$
\text{Recall@}k = \frac{|\{\text{documents pertinents}\} \cap \{\text{top-}k\}|}{|\{\text{documents pertinents}\}|}
$$


### Définition de chaque symbole

- \(k\) : le nombre de résultats que l’on considère (souvent 3, 5 ou 10). Plus \(k\) est grand, plus le recall a de chances d’être élevé, mais on risque d’introduire plus de bruit.

- $$
  \{\text{documents pertinents}\}
  $$

   : l’ensemble des documents jugés utiles pour répondre à la question (ground truth).

- $$
  \{\text{top-}k\}
  $$

   : les k premiers documents retournés par le retriever, ordonnés par score de similarité.

- L’intersection : les documents qui sont à la fois pertinents et présents dans le top-k.

- Le dénominateur est le nombre total de documents pertinents. Si ce nombre est 0, le recall est indéfini ou conventionnellement 0.

### Comportement quand les valeurs changent

- Plus le numérateur augmente (plus de documents pertinents récupérés dans le top-k), plus le Recall@k augmente.
- Plus le dénominateur est grand (beaucoup de documents pertinents existants) sans que le numérateur suive, plus le score baisse.
- Augmenter \(k\) fait généralement monter le recall, mais au détriment de la précision.

## Démonstration et interprétation

Supposons 4 documents pertinents pour une question, et un top-5 qui en contient 2.  
Recall@5 = 2/4 = 0.5  

**Interprétation :** la moitié des informations utiles ont été récupérées. Dans un contexte réglementaire, cela peut être insuffisant.

## Code Python

```python
from typing import List, Set

def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = set(retrieved[:k])
    return len(top_k & relevant) / len(relevant)
```

## Cas d’usage métier maximum

**Finance / Banque** : pour une question de conformité (« quelles sont les obligations de reporting sur cette position ? »), un Recall@5 faible signifie que des règles importantes n’ont pas été récupérées → risque réglementaire.

**Immobilier** : estimation d’un bien. Si les comparables les plus proches ne sont pas dans le top-k, l’estimation sera biaisée.

**Crypto** : recherche de clauses de risque dans un whitepaper. Un mauvais recall peut faire ignorer un mécanisme dangereux.

**Bancaire / Crédit** : récupération des règles internes d’octroi. Recall insuffisant = décision mal fondée.

**Assurance** : clauses de sinistre.  
**RH** : politiques multi-pays.  
**BTP** : normes de facturation.

Un Recall@k élevé est souvent exigé avant de faire confiance au RAG dans ces domaines.
