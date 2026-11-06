# 07-Contexte — Training Pipeline & Optimizer

**Dossier :** 07-Contexte  
**Métiers :** AI Engineers

## Pipeline d’entraînement

1. Tokenization (BPE, WordPiece…)
2. Ajout du Positional Encoding
3. Passage dans les couches Transformer
4. Calcul de la Cross-Entropy Loss (next token prediction)
5. Backpropagation
6. Mise à jour des poids (Adam + learning rate schedule)

## Optimiseur

Adam est le plus courant, souvent avec warmup + decay.

Hyperparamètres typiques :
- Learning rate avec warmup
- Weight decay
- Dropout
- Gradient clipping

## Cas d’usage métier

Base du pré-entraînement et du fine-tuning des modèles utilisés dans les agents.
