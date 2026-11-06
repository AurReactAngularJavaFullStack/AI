# 07-Contexte — Inference & Decoding Strategies

**Dossier :** 07-Contexte  
**Métiers :** AI Engineers, AI Agent Ops, Product Engineers

## Stratégies de décodage

- **Greedy** : on prend toujours le token de plus haute probabilité.
- **Top-k** : on échantillonne parmi les k tokens les plus probables.
- **Top-p (Nucleus)** : on échantillonne parmi le plus petit ensemble de tokens dont la probabilité cumulée ≥ p.
- **Beam Search** : on garde les meilleures séquences candidates.

## Processus

1. Tokenize le prompt
2. Ajoute positional encoding
3. Passe dans le modèle → logits
4. Softmax → probabilités
5. Applique la stratégie de décodage
6. Ajoute le token généré et répète

## Cas d’usage métier

- Greedy : réponses déterministes (conformité, extraction).
- Top-p : génération plus naturelle (rapports, explications).
