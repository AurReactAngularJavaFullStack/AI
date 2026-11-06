# 07-Contexte — Formule 02 — Multi-Head Attention

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 07-Contexte-Formule-02-Multi-Head-Attention.md

## Définition complète

On calcule plusieurs attentions en parallèle (les têtes), on les concatène, puis on projette.

$$
\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W^O
$$

$$
\text{head}_i = \text{Attention}(Q W_i^Q, K W_i^K, V W_i^V)
$$

### Définition de chaque symbole

- $h$ : nombre de têtes.
- $W_i^Q, W_i^K, W_i^V$ : matrices de projection de la tête $i$.
- $W^O$ : matrice de sortie.
- Chaque tête a généralement une dimension $d_k = d_{\text{model}} / h$.

### Comportement

Différentes têtes peuvent se spécialiser sur des relations locales ou longues portées.

## Code Python

```python
# Voir implémentations PyTorch / TensorFlow
# Dimension typique BERT : d_model=768, h=12, d_k=64
```

## Cas d’usage métier

Permet une représentation plus riche du contexte dans les agents qui analysent des documents complexes.
