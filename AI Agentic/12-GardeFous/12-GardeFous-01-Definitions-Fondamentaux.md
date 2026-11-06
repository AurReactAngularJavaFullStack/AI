# 12-GardeFous — 01-Definitions-Fondamentaux

**Dossier :** 12-GardeFous  
**Métiers :** AI Agent Ops, AI Engineers, Forward-Deployed Engineers, AI Platform Team

## Définition

Les garde-fous (guardrails) sont l’ensemble des mécanismes qui empêchent un agent de produire des actions ou des réponses dangereuses, non conformes ou hors périmètre.

## Types principaux

- Validation des entrées/sorties
- Permissions et scopes d’outils
- Détection de prompt injection
- Human-in-the-loop pour actions sensibles
- Filtres de contenu et de données sensibles
- Budgets (tokens, coût, nombre d’appels)

## Cas d’usage métier

**Banque / Finance** : interdiction d’exécuter des données clients sans autorisation, validation humaine avant toute recommandation d’investissement.

**Crypto** : blocage des transactions au-dessus d’un seuil, vérification des adresses.

**Immobilier** : pas de génération de documents juridiques sans revue.

**Assurance / Secteur public** : respect strict des habilitations et traçabilité complète.

**RH** : protection des données personnelles multi-pays.

Les garde-fous s’implémentent souvent comme des interceptors ou des policies autour des ports hexagonaux.
