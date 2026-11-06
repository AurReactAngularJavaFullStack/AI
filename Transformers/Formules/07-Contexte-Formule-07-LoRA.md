# 07-Contexte — Formule 07 — LoRA (Low-Rank Adaptation)

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 07-Contexte-Formule-07-LoRA.md

## Définition complète

LoRA adapte un modèle pré-entraîné en n’entraînant que de petites matrices de bas rang.

$$
W' = W + \Delta W = W + BA
$$

où $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$ et $r \ll \min(d, k)$.

### Définition de chaque symbole

- $W$ : poids originaux (gelés).
- $B$ et $A$ : matrices de bas rang entraînables.
- $r$ : rang (souvent 8, 16, 32…).
- $\Delta W = BA$ : mise à jour de faible rang.

### Comportement

Réduit drastiquement le nombre de paramètres entraînables tout en permettant une bonne adaptation.

## Code Python

```python
# Conceptuel
# delta_W = B @ A
# W_new = W + delta_W
```

## Cas d’usage métier

Fine-tuning efficace de modèles pour des domaines spécifiques (finance, assurance, RH, BTP) sans réentraîner tout le modèle.
