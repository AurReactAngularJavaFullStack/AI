# 11-Evaluation — Formule 10 — Answer Correctness (simplifiée)

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers  

**Nom du fichier :** 11-Evaluation-Formule-10-Answer-Correctness.md

## Définition

Answer Correctness combine souvent similarité sémantique et exactitude factuelle par rapport à une ground truth.

Une version simplifiée courante est :

$$
\text{Answer Correctness} = \alpha \cdot \text{sim}(E_{\text{réponse}}, E_{\text{gt}}) + (1-\alpha) \cdot \text{F1}_{\text{facts}}
$$


### Définition de chaque symbole

- \(
  $$
  \text{sim}
  $$
  \) : similarité cosinus entre l’embedding de la réponse et celui de la ground truth.

- $$
  \text{F1}_{\text{facts}}
  $$

   : F1 calculé sur les faits/claims partagés.

- $$
  \alpha
  $$

  \) : poids (souvent autour de 0.5 à 0.75).

### Comportement

- Plus la réponse est proche sémantiquement et factuellement de la référence, plus le score augmente.

## Code Python

```python
def answer_correctness(semantic_sim: float, fact_f1: float, alpha: float = 0.5) -> float:
    return alpha * semantic_sim + (1 - alpha) * fact_f1
```

## Cas d’usage métier maximum

**Finance / Banque** : la réponse de conformité est-elle à la fois proche et factuellement correcte par rapport à la référence ?

**Immobilier** : l’estimation textuelle est-elle correcte ?

**Crypto / Assurance / RH** : même logique d’évaluation de la qualité globale de la réponse.
