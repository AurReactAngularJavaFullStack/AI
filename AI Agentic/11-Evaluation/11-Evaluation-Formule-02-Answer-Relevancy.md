# 11-Evaluation — Formule 02 — Answer Relevancy

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers  

**Nom du fichier :** 11-Evaluation-Formule-02-Answer-Relevancy.md

## Définition complète de chaque élément

Answer Relevancy mesure si la réponse générée répond vraiment à la question posée, et non à une question proche ou hors sujet.

$$
\text{Answer Relevancy} = \frac{1}{n} \sum_{i=1}^{n} \cos(E_{g_i}, E_o) = \frac{1}{n} \sum_{i=1}^{n} \frac{E_{g_i} \cdot E_o}{\|E_{g_i}\| \|E_o\|}
$$


### Définition de chaque symbole

- \(n\) : le nombre de questions hypothétiques générées à partir de la réponse (souvent 3 à 5). Plus \(n\) est grand, plus l’estimation est stable mais plus le coût augmente.

- \(E_{g_i}\) : l’embedding de la i-ème question générée à partir de la réponse.

- \(E_o\) : l’embedding de la question originale de l’utilisateur.

- \(
  $$
  \cos(\cdot)
  $$
  \) : similarité cosinus entre les deux embeddings. Plus elle est proche de 1, plus les deux questions sont sémantiquement proches.

- La moyenne sur \(n\) donne un score entre -1 et 1 (en pratique 0 à 1).

### Comportement

- Plus les questions générées sont proches de la question originale, plus le score augmente → la réponse est bien dans le sujet.
- Si la réponse parle d’autre chose, les questions générées s’éloignent et le score baisse.
- Un score < 0.7 indique souvent une réponse hors sujet ou trop vague.

## Démonstration et interprétation

(Voir calculs numériques déjà détaillés dans les versions précédentes ; score moyen ≈ 0.74 signifie une pertinence correcte mais perfectible.)

## Code Python

```python
import numpy as np
from typing import List

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def answer_relevancy(original: np.ndarray, generated: List[np.ndarray]) -> float:
    if not generated:
        return 0.0
    sims = [cosine_similarity(original, g) for g in generated]
    return float(np.mean(sims))
```

## Cas d’usage

Dans un agent RH, si Answer Relevancy est bas, l’utilisateur a posé une question sur les congés et l’agent a répondu sur la paie → on détecte le dérapage.
