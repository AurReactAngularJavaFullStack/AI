# 04-Agents — 01-Definitions-Fondamentaux

**Dossier :** 04-Agents  
**Métiers :** AI Engineers, Product Engineers, Forward-Deployed Engineers, AI Agent Ops

## Définition d’un agent IA

Un agent IA est un système qui perçoit un état (conversation, données métier, outils disponibles), raisonne, décide d’une action (appel d’outil, réponse, planification), observe le résultat, et boucle jusqu’à atteindre un objectif ou un critère d’arrêt.

Contrairement à un simple chatbot, l’agent a :
- Un objectif explicite
- La capacité d’utiliser des outils
- Une mémoire (courte ou longue)
- Des traces de ses décisions

## Boucle fondamentale

1. Perception de l’état actuel
2. Raisonnement / planification
3. Action (tool call ou réponse)
4. Observation du résultat
5. Mise à jour de l’état
6. Répétition ou arrêt

## Patterns principaux

- **ReAct** : Reason + Act en alternance
- **Plan-and-Execute** : plan global puis exécution
- **Reflexion** : auto-critique après action

## Cas d’usage métier

**Finance / Banque** : agent qui analyse un dossier de crédit, appelle des outils de scoring et de vérification de conformité, puis propose une décision argumentée.

**Immobilier** : agent qui qualifie une demande d’estimation, récupère des comparables, calcule une fourchette et génère un rapport.

**Crypto** : agent qui surveille un protocole, détecte une anomalie de liquidité et alerte ou propose une action.

**Assurance / RH / BTP** : qualification de sinistre, onboarding, génération de facture conforme.

Dans une architecture hexagonale, l’agent runtime vit dans l’infrastructure ; les règles métier restent dans le domaine.
