# 07-Contexte — Architecture Encoder / Decoder

**Dossier :** 07-Contexte  
**Métiers :** AI Engineers, AI Agent Ops

## Encoder

L’encodeur prend les embeddings de tokens + positional encoding et produit des représentations contextualisées.

Structure d’une couche d’encodeur :
1. Multi-Head Self-Attention
2. Add & Norm (connexion résiduelle + LayerNorm)
3. Feed-Forward Network
4. Add & Norm

Empilé N fois (ex. 6, 12, 24).

## Decoder

Le décodeur génère le texte token par token. Il contient :
1. Masked Multi-Head Self-Attention (ne voit pas les tokens futurs)
2. Add & Norm
3. Cross-Attention (sur les sorties de l’encodeur)
4. Add & Norm
5. Feed-Forward
6. Add & Norm

## Différences clés

- L’encodeur voit toute la séquence.
- Le décodeur est causal (masqué) pendant la génération.

## Cas d’usage métier

Les modèles encoder-only (BERT) sont souvent utilisés pour le retrieval et la classification.  
Les modèles decoder-only (GPT) sont utilisés pour la génération dans les agents.
