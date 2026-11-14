# Fiche 00f_neuf_concepts — Neuf concepts de l'IA agentique

> Image : `00f_neuf_concepts.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

**La carte claire : mémoire, orchestration, RAG, harness, évals, MCP, skills, A2A, multi-agents**


## Ce que montre l'image

Neuf cases, dans l'ordre où on les assemble.

| # | Concept | Rôle |
| --- | --- | --- |
| 1 | Mémoire et état | Le passé retenu, et l'état courant. Le modèle, lui, oublie entre deux appels. |
| 2 | Orchestration | Qui fait quoi. Un gestionnaire de code et un environnement, entre des micro-agents. |
| 3 | RAG | Retrouver, injecter, générer. La réponse s'appuie sur une base, pas seulement sur le modèle. |
| 4 | Harness | Ce qui fait agir le modèle : contexte, contrôle, action, persistance. |
| 5 | Évaluations | Comparer la sortie à un résultat attendu, puis améliorer. |
| 6 | MCP | La prise standard entre l'agent, les outils et les données. |
| 7 | Skills | Une capacité réutilisable : nom, entrée, action, sortie. |
| 8 | A2A | Un agent découvre les compétences d'un autre et lui passe une tâche. |
| 9 | Système multi-agents | Des spécialistes partagent tâches, contexte et réponses. |

## Ce que c'est

C'est le sommaire visuel des chapitres 4 à 10. La fiche sœur `00g` dessine les mêmes neuf idées. On lit `00f` d'abord : les schémas y sont plus nets.

## Effets et impacts

- Sauter l'évaluation (case 5) rend les huit autres cases impossibles à régler.
- MCP (case 6) ne remplace pas le schéma d'un outil. Il le transporte.
- A2A (case 8) sans contrat d'entrée et de sortie, c'est une conversation, pas une délégation.

## Exemple

« Prépare le dossier de sinistre » : la mémoire sait qui est le client (1), l'orchestrateur choisit l'agent pièces (2), le RAG retrouve la clause (3), un skill « extraire un montant » est réutilisé (7), un second agent vérifie (8 et 9), l'évaluation dit si le dossier est complet (5).

## Dans le cours

- [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)
