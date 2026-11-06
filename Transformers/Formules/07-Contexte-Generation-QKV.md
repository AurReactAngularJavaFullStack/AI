# 07-Contexte — Génération de Q, K, V

**Dossier :** 07-Contexte  
**Métiers :** AI Engineers

## Principe

Chaque embedding de token $x$ est projeté en trois vecteurs via des matrices apprises :

$$
Q = X W_Q, \quad K = X W_K, \quad V = X W_V
$$

- $W_Q, W_K, W_V$ sont des paramètres entraînés.
- Dans la Multi-Head Attention, on a des projections différentes par tête.

## Rôle de chacun

- **Query (Q)** : ce que le token cherche.
- **Key (K)** : ce avec quoi on peut matcher.
- **Value (V)** : l’information qui sera agrégée.

## Cas d’usage

Comprendre cette étape aide à diagnostiquer le comportement d’attention dans les longs contextes métier.
