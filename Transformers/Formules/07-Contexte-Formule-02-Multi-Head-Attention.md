# 07-Contexte — Formule 02 — Multi-Head Attention

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 07-Contexte-Formule-02-Multi-Head-Attention.md

## Définition complète de chaque élément

La Multi-Head Attention permet au modèle de calculer plusieurs attentions en parallèle (les têtes) afin de capturer différents types de relations dans le contexte.

$$
\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h) W^O
$$

$$
\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)
$$

### Définition de chaque symbole

- $h$ : le nombre de têtes. Plus il est élevé, plus le modèle peut se spécialiser.
- $W_i^Q$, $W_i^K$, $W_i^V$ : matrices de projection spécifiques à la tête $i$.
- $W^O$ : matrice de sortie qui recombine les têtes.
- $\text{Attention}$ : la Scaled Dot-Product Attention.

### Comportement

Chaque tête peut apprendre à se concentrer sur des aspects différents (syntaxe, sémantique longue portée, entités, etc.).

## Code Python

```python
import numpy as np

def multi_head_attention_simplified(Q, K, V, n_heads):
    # Implémentation réelle découpe et projette
    heads = [scaled_dot_product_attention(Q, K, V) for _ in range(n_heads)]
    return np.concatenate(heads, axis=-1)
```

## Cas d’usage métier

Dans l’analyse d’un long contrat d’assurance ou d’un dossier de crédit, différentes têtes peuvent se spécialiser respectivement sur les montants, les dates et les conditions.
