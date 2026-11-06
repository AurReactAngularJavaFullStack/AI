# 06-RAG — Formule 03 — Precision@k

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 06-RAG-Formule-03-Precision-at-k.md

## Définition complète

La Precision@k mesure la proportion de documents pertinents parmi les k premiers résultats. C’est une métrique de pureté : parmi ce que j’ai récupéré, combien est vraiment utile ?

$$
\text{Precision@}k = \frac{|\{\text{documents pertinents}\} \cap \{\text{top-}k\}|}{k}
$$


### Définition de chaque symbole

- \(k\) : nombre de résultats considérés.
- Numérateur : documents pertinents présents dans le top-k.
- Dénominateur : toujours \(k\).

### Comportement

- Plus le numérateur augmente, plus la précision augmente.
- Un \(k\) trop grand fait souvent baisser la précision (plus de bruit).

## Code Python

```python
def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    if k == 0:
        return 0.0
    top_k = set(retrieved[:k])
    return len(top_k & relevant) / k
```

## Cas d’usage métier maximum

**Finance** : parmi les 5 documents récupérés pour une analyse de risque, combien sont réellement utiles ? Une précision basse noie l’agent dans du bruit.

**Immobilier** : les comparables remontés sont-ils vraiment comparables ?

**Crypto** : les passages de documentation récupérés parlent-ils vraiment du sujet demandé ?

**Banque, Assurance, RH, BTP** : même logique — éviter de passer trop de contexte non pertinent au LLM.

Precision et Recall se complètent : on veut les deux élevés.
