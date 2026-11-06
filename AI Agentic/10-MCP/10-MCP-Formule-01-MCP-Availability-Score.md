# 10-MCP — Formule 01 — Score de disponibilité d’un serveur MCP

**Dossier :** 10-MCP  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Agent Ops, Forward-Deployed Engineers, AI Platform Team  

**Nom du fichier :** 10-MCP-Formule-01-MCP-Availability-Score.md

## Définition

$$
\text{disponibilité} = \frac{\text{nombre de requêtes réussies}}{\text{nombre total de requêtes}} \times (1 - \text{taux d'erreur timeout})
$$



### Définition de chaque symbole

- Requêtes réussies : appels MCP qui ont retourné une réponse valide.
- Taux d’erreur timeout : proportion de requêtes qui ont expiré.
- Plus le score est proche de 1, plus le serveur MCP est fiable pour les agents.

### Comportement

- Augmentation des timeouts → score baisse → risque pour les agents en production.
- Utilisé pour le monitoring et les alertes.

## Code Python

```python
def mcp_availability(success: int, total: int, timeout_rate: float) -> float:
    if total == 0:
        return 0.0
    return (success / total) * (1 - timeout_rate)
```

## Cas d’usage métier

**Banque, Immobilier, Crypto, Finance, Plateforme** : surveiller la fiabilité des serveurs MCP exposés aux agents ou aux clients (Forward-Deployed).
