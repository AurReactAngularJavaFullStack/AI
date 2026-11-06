# 11-Evaluation — Formule 09 — Perplexité (et lien avec la confiance)

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 11-Evaluation-Formule-09-Perplexity.md

## Définition

La perplexité mesure à quel point le modèle est « surpris » par une séquence. Elle est liée à l’entropie croisée.

$$
\text{Perplexity} = \exp\left( -\frac{1}{N} \sum_{i=1}^{N} \log p(w_i | w_{<i}) \right)
$$


### Définition de chaque symbole

- \( N \) : longueur de la séquence.
- \( p(w_i | w_{<i}) \) : probabilité assignée par le modèle au token \( w_i \) étant donné le contexte précédent.
- Plus la perplexité est basse, plus le modèle est confiant et cohérent avec la séquence.

### Comportement

- Perplexité élevée → le modèle hésite beaucoup → souvent corrélé à des réponses moins fiables.
- Utilisée parfois comme signal de confiance ou pour détecter des sorties dégénérées.

## Code Python (conceptuel)

```python
import math

def perplexity(log_probs: list[float]) -> float:
    """log_probs : liste des log-probabilités des tokens générés."""
    if not log_probs:
        return float('inf')
    return math.exp(-sum(log_probs) / len(log_probs))
```

## Cas d’usage

**Finance, Banque, Crypto, Assurance** : un agent qui génère une analyse avec une perplexité anormalement haute peut être flaggé pour revue humaine. Complète les métriques de Faithfulness.
