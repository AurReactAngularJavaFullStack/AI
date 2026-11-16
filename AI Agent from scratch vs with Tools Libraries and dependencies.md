```
Du coup est-ce que l'on a tout ce qu'il faut pour savoir construire un agent ia à partie d'une feuille blanche 

Et est-ce que c'est primordiale ou intéressant de faire la m chose pour jev et aussi mais ça je sais pas si les entreprises seront enclins à ça mais construire des agents ia à partir des outils technologies dépendances existante genre comme ds l images screenshots uploaded right here 

Et est-ce que c nécessaires à utiliser m si ça créé des dépendances à quel point c nécessaire ou pas 

Donne moi ton avis sur la question actuellement qu'est-ce qui est le plus used parmi tout es c root techniques tu peux décortiquer liter par ordre d'importance
```

Oui. Le parcours, les douze exercices et l'étape 77 suffisent pour construire un agent depuis une feuille blanche, et pour le refaire sans regarder. Les affiches `01` à `45` rangent les formules de cette construction. Elles n'ajoutent pas une deuxième méthode.

Ce qui reste à faire, c'est la main : effacer un palier et le récrire, tests verts du premier coup. Le palier 12 branche ensuite Claude à la place du faux modèle, sans toucher à la boucle, aux outils, à la mémoire, au RAG, aux garde-fous ni à l'évaluation.

Si « jev » veut dire Java, la même chose est utile dans une équipe qui vit déjà dans Spring. Le projet final est déjà dessiné comme ça : le domaine possède la boucle et les refus, le modèle n'est qu'un port. Google ADK existe en Java pour les équipes qui veulent un cadre sur ce port. Réécrire les formules dans un framework n'apprend rien de plus.

## Les dépendances

Une entreprise accepte volontiers une dépendance qu'elle a déjà : le modèle qu'elle paie, son annuaire, sa base, ses journaux. Elle est beaucoup plus lente à laisser un framework devenir l'endroit où vivent la boucle, le schéma et le veto.

| Degré                                                  | Quoi                                                         | Pourquoi                                                     |
| :----------------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| Indispensable dès qu'un utilisateur réel arrive        | Un modèle (API ou modèle local), l'identité déjà en place, un journal, un jeu d'évaluation | Sans ça, l'agent ne répond pas, ne sait pas qui appelle, et chaque changement est un pari. |
| Utile, et la dépendance est saine                      | MCP pour les outils hors du processus, OpenTelemetry pour les traces, Postgres si la mémoire et les documents doivent survivre à un redémarrage | Ce sont des contrats. On peut changer l'implémentation derrière. |
| Utile seulement quand le corpus ou la charge l'exigent | Un index vectoriel dédié, une file, plusieurs instances      | En dessous, un parcours en mémoire et un scan suffisent, comme dans l'étape 77. |
| Facultatif                                             | LangGraph, LlamaIndex, CrewAI, le catalogue de logos         | Ils rempaquet la boucle, le graphe et la recherche. Ils valent le coup quand l'équipe ne veut plus maintenir ce code. Ils gênent quand on ne voit plus pourquoi l'agent s'arrête. |
| Hors sujet pour l'agent                                | React, Kafka, Redis, Kubernetes, l'affiche « system design » | C'est l'hébergement de n'importe quel service. Ça ne rend pas une réponse fidèle. |

Les six captures mélangent trois genres. L'usine (LLM, RAG, base vectorielle, agent, MCP, garde-fous, évaluation) et le carnet manuscrit (RAG, contexte, mémoire, agent, outils, MCP, orchestration, évaluation) décrivent les mêmes pièces que le cours. Les murs de logos sont une liste d'achats. L'affiche à zéro dollar est la même pile, en outils locaux. L'affiche « system design » est un backend général.

## Ce qui est le plus utilisé, par importance

Il n'y a pas un gagnant unique en 2026. La composition la plus citée en production est LangGraph pour l'orchestration, plus MCP pour les outils. Les équipes qui veulent voir chaque arrêt restent en code simple, souvent Pydantic AI ou l'équivalent de l'étape 77. Les kits du cloud (Azure, Google ADK, Bedrock, OpenAI Agents SDK) suivent le contrat déjà signé avec le fournisseur.

1. La boucle et ses arrêts. C'est l'agent. LangGraph est le cadre le plus répandu pour l'écrire de façon durable, avec reprise et pause humaine. Le code du cours fait la même chose en plus petit.
2. Les outils, le schéma, les permissions. Dans un seul programme, un registre suffit. Dès que l'outil est ailleurs, MCP est devenu le protocole supposé, pas une option parmi d'autres.
3. L'évaluation. Tool Call F1, réussite de la tâche, fidélité, barrière avant déploiement. LangSmith est le nom le plus visible côté LangGraph. Le palier 10 le fait sans lui.
4. Les garde-fous. Refus par défaut, veto, approbation. Peu présents sur les murs de logos, décisifs dans une banque. Le palier 09 les a.
5. Le contexte et la mémoire. Ce qui a le droit d'entrer dans la fenêtre. Tous les cadres le proposent. La formule reste celle du cours.
6. La recherche. Hybride : mots exacts et sens. LlamaIndex est le nom le plus associé au pipeline documentaire. La base vectorielle est un choix de stockage : Postgres là où Postgres existe déjà, Qdrant, Milvus ou FAISS quand l'index est le produit.
7. Le modèle. Interchangeable. API en entreprise, modèle local sur l'affiche à zéro dollar. Il n'est pas l'architecture.
8. L'orchestration de plusieurs étapes. Un graphe, comme le palier 08, ou LangGraph. CrewAI quand on veut des rôles. La plupart des systèmes en production restent un agent et un workflow, pas une foule d'agents.
9. Les traces et le coût. OpenTelemetry, puis Grafana ou l'outil du cloud. Nécessaire avec de vrais utilisateurs. Même famille que n'importe quel service.
10. Le déploiement. Docker et le cloud déjà payé. Nécessaire pour servir. Sans effet sur la justesse de la réponse.

L'ordre d'apprentissage reste celui du parcours. L'ordre d'une entreprise qui a déjà Java, Postgres et un cloud est : garder le domaine chez soi, brancher le modèle et les outils par des ports, adopter MCP et les traces, et ne prendre un framework que pour la reprise après panne et la pause humaine, une fois que la feuille blanche tient.