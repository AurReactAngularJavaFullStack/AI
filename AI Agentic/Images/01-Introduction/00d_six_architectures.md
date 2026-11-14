# Fiche 00d_six_architectures — Six architectures, du chatbot à l'entreprise

> Image : `00d_six_architectures.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

**Choisir le niveau d'autonomie, pas le framework**


## Ce que montre l'image

Six niveaux, du plus simple au plus gouverné.

| Niveau | Architecture | Ce qui s'ajoute |
| --- | --- | --- |
| 01 | Chatbot | Un prompt, une réponse. Pas d'outil, pas de mémoire. |
| 02 | RAG | Découpage, embeddings, base vectorielle, rerank, réponse ancrée. |
| 03 | Agent seul | But, plan, boucle raisonner-agir, outils, mémoire. |
| 04 | Multi-agents | Un orchestrateur délègue à des spécialistes et fusionne. |
| 05 | Flux autonome | Déclencheur, file de tâches, exécution parallèle, validateur, accord humain. |
| 06 | Agent d'entreprise | Passerelle, garde-fous, traces, coût, évaluation, connecteurs. |

La consigne du bas : la meilleure architecture est la plus simple qui résout le problème sans risque. On ne commence pas par « quel framework », on commence par « de quelle autonomie a-t-on besoin ? ».

## Ce que c'est

C'est le plan du parcours, dessiné comme une montée. Les chapitres 2 et 6 couvrent le niveau 01. Le chapitre 5 couvre le niveau 02. Les chapitres 1, 3, 4 et 7 couvrent le niveau 03. Le chapitre 8 couvre le niveau 04. Les chapitres 10, 11 et 12 couvrent les niveaux 05 et 06.

## Effets et impacts

- Partir au niveau 06 pour une FAQ ferme le projet dans la gouvernance avant d'avoir une réponse juste.
- Un RAG sans mesure (rappels, MRR, NDCG) reste un niveau 02 qui a l'air d'un niveau 03.
- L'accord humain du niveau 05 n'est pas un échec de l'agent. C'est le garde-fou quand l'action est irréversible.

## Exemple

Une question sur le règlement intérieur : niveau 02. « Traite les factures de la nuit, et arrête-toi si le montant dépasse le seuil » : niveau 05, avec une porte humaine.

## Dans le cours

- [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)
