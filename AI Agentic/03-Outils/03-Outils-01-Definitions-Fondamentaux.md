# 03-Outils — 01-Definitions-Fondamentaux

**Dossier :** 03-Outils  
**Métiers :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers

## Définition

Un outil (tool / function) est une fonction exposée à l’agent avec un schéma d’entrée/sortie strict. L’agent décide quand l’appeler et avec quels arguments.

## Éléments clés

- Nom et description clairs
- Schéma JSON (ou équivalent) des paramètres
- Effets de bord contrôlés
- Idempotence recommandée
- Gestion d’erreurs et timeouts

## Cas d’usage

**Bancaire** : outil `get_credit_score(client_id)`, `check_kyc_status()`.

**Immobilier** : `get_comparables(address, surface)`, `calculate_dpe_impact()`.

**Crypto** : `get_liquidity_pool(token)`, `simulate_transaction()`.

**Finance** : `fetch_market_data(symbol)`, `calculate_var()`.

**Assurance / BTP / RH** : outils métier déjà présents dans tes projets.

Les outils sont des ports sortants dans une architecture hexagonale.
