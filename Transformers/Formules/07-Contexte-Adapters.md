# 07-Contexte — Adapters

**Dossier :** 07-Contexte  
**Métiers :** AI Engineers, AI Agent Ops

## Principe

Les Adapters sont de petits modules insérés dans les couches Transformer. On gèle le modèle original et on n’entraîne que les adapters.

Typiquement : down-projection → non-linéarité → up-projection + connexion résiduelle.

## Avantages

- Peu de paramètres entraînables
- Possibilité d’avoir plusieurs adapters pour différentes tâches

## Cas d’usage métier

Adaptation légère de modèles à des domaines spécifiques (finance, RH, assurance) sans full fine-tuning.
