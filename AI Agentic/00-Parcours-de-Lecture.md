# Parcours de lecture — AI Agentic

Ce cours se lit dans l’ordre de ses dossiers. Chaque dossier, de `01-Agent` à `14-Synthese-et-Revision`, est un chapitre, et les chapitres sont numérotés dans l’ordre où l’on apprend. Dans un dossier, chaque fichier commence par son numéro d’étape, de 1 à 79 : l’ordre alphabétique de l’explorateur de fichiers est l’ordre de lecture.

Une étape intermédiaire porte une lettre après son numéro (b = bis, c = ter, d = quater, e = quinquies, f = sexies, g = septies) et se lit dans l’ordre alphabétique, juste après l’étape de même numéro.

Les mathématiques ne sont pas rangées à part. Chaque chapitre de maths est placé juste avant la première formule qui l’utilise, dans le dossier où on le lit.

Le dossier `Images/` rassemble les fiches illustrées. Chaque image a sa fiche du même nom : on ouvre l’image à gauche, la fiche à droite, et on fait défiler les deux ensemble. L’ordre de lecture est le numéro du dossier : `01-Introduction`, `02-Vecteurs`, `03-Modele`, `04-Recherche`, `05-Contexte`, `06-Decision`, `07-Mesure`, `08-Entrainement`, `09-Production`. Dans un dossier, la fiche `NN` précède ses affiches `NNa`, `NNb`. Chaque fiche renvoie vers l’étape du cours qui démontre la formule. Le sommaire est `Images/00_Sommaire-des-fiches.md`.

Le dossier `Demonstrations/` donne à chaque fiche de `Images/` son fichier de démonstrations, au même nom et dans le même sous-dossier : 34 fichiers rangés dans l’ordre des étapes. Chacun explique d’abord le mécanisme de la formule, puis donne quatre à six démonstrations pas à pas et un exemple simple. Viennent ensuite quatre cas d’usage complexes aux Émirats, chiffrés et démontrés jusqu’à la valeur où la décision de l’agent bascule, des exercices sur feuille A4 avec leur corrigé, et un programme Python qui revérifie tous les nombres. Le sommaire et la méthode feuille blanche sont dans `Demonstrations/00_Sommaire-des-demonstrations.md`.

Dans chaque chapitre, l’ordre interne est toujours le même : définition, exemples, applications, formule. La formule sans les mots d’avant ne dit pas à quoi sert le nombre.

## Ce que cet ordre respecte

Une requête traverse l’agent dans un ordre fixe : prompt, schéma, outil, boucle, mémoire et RAG, attention, plan, orchestration, MCP, évaluation, garde-fou. C’est l’ordre du système en marche.

La lecture suit un autre ordre, celui de la compréhension : la softmax avant le prompt, une première évaluation dès que l’agent a des outils, le contexte puis le cosinus avant la mémoire et le RAG, l’attention après le RAG, Bellman avant A*, le graphe après le score de priorité, les files d’attente avant de relire la disponibilité MCP. Les exemples d’un chapitre se lisent après sa définition et, quand la formule éclaire l’exemple, après la formule.

## Ce que contient un fichier enrichi

Chaque fichier de formule suit le même ordre. La ligne du haut donne le numéro d’étape, le fichier d’avant et celui d’après. Viennent ensuite la définition, le rôle de la formule dans la boucle de l’agent, l’équation, le tableau des symboles, puis la **démonstration**. Le passage au code suit, avec un **déroulé ligne par ligne**, le programme et sa **sortie attendue**. Le fichier se termine par des **cas d’usage réels aux Émirats**, les pièges, et un **exercice feuille blanche**.

Chaque programme se suffit à lui-même et n’utilise que la bibliothèque standard de Python. Ses `assert` reprennent les nombres calculés à la main dans la démonstration. S’il imprime sa dernière ligne, « OK — toutes les vérifications sont passées. », chaque nombre du texte a été vérifié.

Les fichiers de définitions des étapes 1, 4, 8, 12, 46, 49 bis et 66 contiennent une section « Construire depuis une feuille blanche » : le code complet de la pièce, sans framework. Le faux LLM scripté y remplace le modèle pour que tout tourne hors ligne. L’étape 13 montre le même code branché sur l’API Claude.

## Exécuter un programme

Copier le bloc Python dans un fichier, par exemple `decay.py`, puis lancer dans PowerShell :

```text
& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" decay.py
```

Le chemin complet évite les alias `python` de Windows, qui ouvrent le Microsoft Store au lieu de l’interpréteur.

Pour revérifier d’un coup tous les programmes du cours, utiliser `verifier_programmes.py`, à la racine du dossier. Il exécute chaque bloc Python et contrôle ses `assert`, la ligne finale et la « Sortie attendue ». Il vérifie aussi les formules au format Typora et les liens. Depuis le dossier « AI Agentic », dans PowerShell :

```text
& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" verifier_programmes.py .
& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" verifier_programmes.py 05-RAG\22-RAG-Formule-BM25.md
& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" verifier_programmes.py --status .
```

La dernière ligne affichée résume le résultat, par exemple « RÉSUMÉ : … PASS, 0 FAIL ». Un FAIL désigne le bloc en cause et l’erreur Python. `--status` affiche, pour chaque leçon, les sections présentes.

## Rythme proposé : quatre semaines

| Semaine | Étapes | Ce qu’on sait faire à la fin |
| --- | --- | --- |
| 1 | 1 à 17 | Écrire une boucle d’agent, un prompt, un schéma validé, un outil fiable avec relances, une mémoire qui oublie. |
| 2 | 18 à 37 | Construire un RAG hybride (BM25, cosinus, RRF), le mesurer (rappel, MRR, NDCG), le renforcer (reranking, index ANN, RAG correctif, GraphRAG), expliquer l’attention, le cache KV et le MoE. |
| 3 | 38 à 60 bis | Planifier (Bellman, A*), ordonner un graphe d’agents, le déclencher par événement, exposer des outils en MCP, évaluer un agent, même sur peu d’essais. |
| 4 | 61 à 77 | Finir l’évaluation, poser les garde-fous et la sandbox, servir, observer et chiffrer la production, spécialiser le modèle, assembler le projet final. |

À la fin de chaque semaine, refaire de tête les exercices « feuille blanche » des fichiers de la semaine.

## Parcours express : sept jours

Pour qui doit être opérationnel tout de suite (entretien, première mission), voici le chemin minimal pour construire un agent et le défendre :

| Jour | Étapes | Objectif |
| --- | --- | --- |
| 1 | 1, 2, 4, 8, 12 | La boucle, la softmax, le prompt, le schéma, l’outil. |
| 2 | 11, 13 | Les relances, la boucle complète sur six cas, le branchement sur Claude. |
| 3 | 14, 16, 17, 22, 24 | Cosinus, mémoire, BM25, fusion RRF. |
| 4 | 25, 27, 28, 30 bis, 31 | Rappel, MRR, NDCG, reranking, attention. |
| 5 | 46, 49, 66, 67, 67 bis | MCP, disponibilité, garde-fous, score de risque, sandbox. |
| 6 | 54, 59, 60, 65, 72, 72 quater | Fidélité, Tool Call F1, réussite de la tâche, barrière CI, coût des tokens, traces. |
| 7 | 77 | Le projet final, refait de tête. |

---

## Le fil en une page

1. `01-Agent` : ce qu’est un agent, et pourquoi sa fiabilité se multiplie d’une étape à l’autre.
2. `02-LLM-Softmax-et-Prompts` : comment le modèle choisit un token (softmax), ce qu’est un token (BPE), puis comment on lui parle (prompts).
3. `03-Schemas-Outils-et-Premiere-Evaluation` : comment on force une forme (schémas), ce qu’est un outil, la boucle qui l’appelle, et comment on la mesure dès le premier jour.
4. `04-Contexte-Similarite-et-Memoire` : ce qui entre dans la fenêtre de contexte, le cosinus, puis la mémoire.
5. `05-RAG` : le RAG qui classe des documents, les métriques qui jugent ce classement, puis le RAG avancé (reranking, requêtes, découpage, index ANN, RAG correctif, GraphRAG).
6. `06-Attention-et-Transformer` : comment le modèle lit le contexte qu’on vient de lui donner, génère token par token avec un cache, et d’où viennent les embeddings.
7. `07-Planification` : comment il choisit la prochaine étape (Bellman, puis A*).
8. `08-Orchestration` : comment plusieurs tâches s’ordonnent (priorité, puis graphe sans cycle).
9. `09-MCP` : comment les outils sont exposés.
10. `10-Evaluation` : comment on mesure (précision, fidélité, perplexité).
11. `11-GardeFous` : comment on bloque.
12. `12-Production-Couts-Optimisation` : comment ça tient en production (files d’attente, batching, décodage spéculatif, traces, coût des tokens, budget de raisonnement) et comment on spécialise le modèle (LoRA, quantification, distillation, alignement).
13. `13-Projet-Final` : comment tout s’assemble dans un agent écrit depuis une feuille blanche.
14. `14-Synthese-et-Revision` : les diapositives de synthèse et l’index des équations, pour réviser.

Le support en diapositives `14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md` peut se garder ouvert à côté : ses sections 01 à 45 suivent à peu près ce fil. Ce n’est pas le cours détaillé.

## Par métier

| Métier | Chapitres prioritaires |
| --- | --- |
| Product Engineers | 01 Agent, 02 Prompts, 03 Schémas et outils, 07 Planification, 10 Évaluation |
| AI Engineers | Tout, surtout 04 Contexte, 05 RAG, 06 Attention, 08 Orchestration, 10 Évaluation |
| AI Agent Ops | 03 Outils, 04 Mémoire, 09 MCP, 10 Évaluation, 11 Garde-fous |
| Forward-Deployed Engineers | Tout le parcours, puis 13 Projet final, refait de tête |
| AI Platform Team | 08 Orchestration, 09 MCP, 10 Évaluation, 11 Garde-fous, 12 Production |

---

## 1. L’agent — dossier `01-Agent`

On commence par la définition. Sans elle, un prompt n’est qu’un texte, et un outil n’est qu’une fonction. Le fichier contient déjà une formule, démontrée : la fiabilité composée. Un agent ne va au bout que si toutes ses étapes réussissent, donc sa fiabilité est le produit de celles de ses étapes.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 1 | `01-Agent/01-Agent-Definitions-Fondamentaux.md` | Un agent perçoit, décide, agit, observe, et s’arrête. Ce n’est pas un chatbot. ReAct, Plan-and-Execute et Reflexion sont nommés ici. On y reviendra quand les pièces existeront. |

Les images d’ensemble se lisent ici, dans `Images/01-Introduction/` : fiches `00a` à `00g`, avec la fiabilité composée `29_fiabilite_serie.md`. On ne lit pas encore `03-Schemas-Outils-et-Premiere-Evaluation/13-Agent-Exemples-Cas-Usage.md`. Les exemples nomment des outils, une mémoire et un RAG qui ne sont pas encore définis.

---

## 2. Le modèle choisit un mot, puis on lui parle — dossier `02-LLM-Softmax-et-Prompts`

Le score de conformité d’un prompt juge des tokens produits. Ces tokens sortent d’une softmax. On lit la softmax avant les prompts.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 2 | `02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md` | Logits, température, argmax, top-p. `T = 0` n’est pas une softmax : c’est un argmax. |
| 2 bis | `02-LLM-Softmax-et-Prompts/02b-Tokenisation-BPE.md` | Comment un texte devient des tokens : fusions BPE apprises, encodage, décodage exact. Le nombre de tokens fixe le coût d’un appel et la place prise dans la fenêtre. |
| 3 | `02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md` | La même fonction, avec la dérivée et la preuve que retrancher le max ne change pas les probabilités. À lire juste après, pas plus tard. |
| 4 | `02-LLM-Softmax-et-Prompts/04-Prompts-Definitions-Fondamentaux.md` | Rôle, system prompt, few-shot. |
| 5 | `02-LLM-Softmax-et-Prompts/05-Prompts-Exemples-Cas-Usage.md` | Des system prompts concrets. |
| 6 | `02-LLM-Softmax-et-Prompts/06-Prompts-Applications-Domaines.md` | Les mêmes idées par métier. |
| 7 | `02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md` | Le taux de consignes respectées. Il ne veut rien dire si l’on ne sait pas que le modèle peut encore tirer un token interdit quand `T` n’est pas nul. |

---

## 3. Une forme, un outil, une première mesure — dossier `03-Schemas-Outils-et-Premiere-Evaluation`

Un outil n’est appelable que si ses arguments ont un schéma. Le schéma vient donc avant l’outil, et l’outil avant les patterns qui l’appellent. Dès que l’agent a des outils, on le mesure : l’évaluation commence ici, pas à la fin.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 8 | `03-Schemas-Outils-et-Premiere-Evaluation/08-Schemas-Definitions-Fondamentaux.md` | Sortie structurée. |
| 9 | `03-Schemas-Outils-et-Premiere-Evaluation/09-Schemas-Exemples-Cas-Usage.md` | Exemples de schémas. |
| 10 | `03-Schemas-Outils-et-Premiere-Evaluation/10-Schemas-Applications-Domaines.md` | Domaines. |
| 11 | `03-Schemas-Outils-et-Premiere-Evaluation/11-Schemas-Formule-Taux-de-Validation.md` | Part des réponses qui passent le schéma. |
| 12 | `03-Schemas-Outils-et-Premiere-Evaluation/12-Outils-Definitions-Fondamentaux.md` | Nom, description, schéma, effets de bord, idempotence, timeout. Les outils n’ont pas de formule propre : la décision d’appeler ou non se mesure avec Tool Call F1 (étape 59). |
| 13 | `03-Schemas-Outils-et-Premiere-Evaluation/13-Agent-Exemples-Cas-Usage.md` | Maintenant les exemples d’agents sont lisibles : crédit, estimation, sinistre. |
| 13 bis | `03-Schemas-Outils-et-Premiere-Evaluation/13b-Evaluation-Definitions-Fondamentaux.md` | Mesurer avant d’améliorer : jeu d’évaluation, juges, barrière de déploiement. Sans jeu d’évaluation, chaque changement de prompt, de modèle ou d’outil est un pari. |

---

## 4. Le contexte, puis se souvenir — dossier `04-Contexte-Similarite-et-Memoire`

Avant de remplir la fenêtre de contexte, on décide ce qui a le droit d’y entrer. La mémoire et le RAG comparent ensuite des vecteurs : le cosinus se lit une fois, au bon endroit, puis on ne le répète plus.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 13 ter | `04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md` | L’ingénierie du contexte : ce qui entre dans la fenêtre, dans quel ordre et sous quelle forme. Un agent qui empile tout paie un coût qui croît comme un carré. |
| 14 | `04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md` | Produit scalaire, norme, cosinus, top-k. |
| 15 | `04-Contexte-Similarite-et-Memoire/15-Fondements-RAG-et-Memoire.md` | Pourquoi la normalisation rend le cosinus égal au produit scalaire, et pourquoi un vieux souvenir doit décroître. |
| 15 bis | `04-Contexte-Similarite-et-Memoire/15b-Memoire-Definitions-Fondamentaux.md` | Ce qu’un agent retient : quoi garder d’une conversation, comment le ranger, quand le ressortir. Le modèle, lui, ne retient rien d’un appel à l’autre. |
| 16 | `04-Contexte-Similarite-et-Memoire/16-Memoire-Formule-Decroissance-Temporelle.md` | La décroissance seule : un souvenir vieux pèse moins. |
| 17 | `04-Contexte-Similarite-et-Memoire/17-Memoire-Formule-Score-de-Pertinence.md` | Le score qui mélange similarité, récence et importance. La récence est le decay de l’étape d’avant. La similarité est le cosinus. |

---

## 5. Retrouver des documents — dossier `05-RAG`

Le RAG se lit dans l’ordre où un moteur de recherche se construit : une distance, une deuxième distance lexicale, un mélange, une fusion de classements, puis les métriques qui disent si le classement est bon. Les cas d’usage suivent. Six étapes de RAG avancé ferment le chapitre : chacune corrige une faiblesse que les métriques ont rendue visible.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 18 | `05-RAG/18-RAG-Formules-Theoremes-Algorithmes.md` | Le récit du retrieval. Point d’entrée du dossier. |
| 19 | `05-RAG/19-RAG-Formule-Similarite-Cosinus.md` | La version courte du cosinus, côté métier. |
| 19 bis | `05-RAG/19b-RAG-Formule-Similarite-Cosinus-Version-Longue.md` | Facultatif : une version plus longue du même cosinus, conservée telle quelle. |
| 20 | `05-RAG/20-RAG-Formule-Distance-Euclidienne.md` | L’autre distance. Elle ne classe comme le cosinus que si les vecteurs sont déjà de longueur 1. |
| 21 | `05-RAG/21-RAG-Formule-Distance-Cosinus.md` | `1 - cosinus`. Une distance, plus une similarité. |
| 22 | `05-RAG/22-RAG-Formule-BM25.md` | Le classement par mots, quand le sens vectoriel rate un numéro de clause ou un identifiant. |
| 23 | `05-RAG/23-RAG-Formule-Score-Hybride.md` | Cosinus et BM25 dans un seul score. Les deux précédents sont ses ingrédients. |
| 24 | `05-RAG/24-RAG-Formule-RRF.md` | Fusionner deux classements par leur rang, sans mélanger des scores qui n’ont pas la même échelle. |
| 25 | `05-RAG/25-RAG-Formule-Recall-at-k.md` | Parmi les documents utiles, combien le top-k a retrouvés. |
| 26 | `05-RAG/26-RAG-Formule-Precision-at-k.md` | Parmi les k sortis, combien étaient utiles. |
| 27 | `05-RAG/27-RAG-Formule-MRR.md` | À quel rang tombe le premier document utile. |
| 28 | `05-RAG/28-RAG-Formule-NDCG.md` | Le rang compte : un bon document en position 1 vaut plus qu’en position 10. |
| 28 bis | `05-RAG/28b-Theoremes-Cosinus-et-Metriques-de-Classement.md` | Les démonstrations : produit scalaire et angle, Cauchy–Schwarz, cosinus ≡ L2 sur vecteurs normalisés, bornes de Recall@k, Precision@k et MRR, score hybride borné. |
| 29 | `05-RAG/29-RAG-Exemples-Cas-Usage.md` | Banque, immobilier, crypto, assurance, RH, BTP. |
| 30 | `05-RAG/30-RAG-Applications-Domaines.md` | Les mêmes idées, par domaine. |
| 30 bis | `05-RAG/30b-RAG-Reranking-Cross-Encodeur.md` | Un second modèle reclasse les candidats du premier étage. Il ne peut rien ajouter : le rappel du premier étage est son plafond, et un mauvais reranker fait baisser le score. |
| 30 ter | `05-RAG/30c-RAG-Transformations-de-Requete.md` | Réécrire, décomposer ou multiplier la requête, puis fusionner. L’union des requêtes domine chacune, mais une fusion tronquée à k peut perdre une facette. |
| 30 quater | `05-RAG/30d-RAG-Decoupage-Avance-et-Compression.md` | Taille fixe, recouvrement, découpage récursif, morceaux contextualisés, compression du contexte. Ce que le recouvrement garantit, et ce qu’il ne garantit pas. |
| 30 quinquies | `05-RAG/30e-RAG-Index-ANN-HNSW-IVF-PQ.md` | Trouver des voisins sans comparer tous les vecteurs : graphe HNSW, listes IVF construites par k-means, compression PQ. On cède un peu de rappel contre beaucoup de vitesse. |
| 30 sexies | `05-RAG/30f-RAG-Corrective-et-Agentic-RAG.md` | L’agent juge ce qu’il a retrouvé et, si c’est faible, reformule ou change de source. Les fausses alarmes peuvent rendre la correction nuisible ; un budget de replis borne le coût. |
| 30 septies | `05-RAG/30g-RAG-GraphRAG-et-Memoire-en-Graphe.md` | Des entités et des relations au lieu de morceaux de texte : voisinages, plus court chemin, communautés par modularité, faits datés qui se remplacent sans se contredire. |

---

## 6. Le modèle lit le contexte qu’on vient de remplir — dossier `06-Attention-et-Transformer`

Le RAG a gonflé le prompt. L’attention est le mécanisme qui décide quels tokens de ce prompt pèsent sur le token en cours. On la lit ici, pas au début : elle répond à une question qu’on ne se pose qu’une fois le contexte construit.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 31 | `06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md` | La formule et un code court. |
| 32 | `06-Attention-et-Transformer/32-Attention-Formules-et-Role-de-Racine-dk.md` | Le même mécanisme raconté, avec le rôle de √dₖ. |
| 32 bis | `06-Attention-et-Transformer/32b-Theoremes-Attention-et-Softmax.md` | Les démonstrations : la softmax somme à 1 et ignore un décalage, Var(q·k) = d_k justifie √d_k, le gradient s’annule quand la softmax sature, la sortie est une moyenne des valeurs, l’attention ignore l’ordre. |
| 33 | `06-Attention-et-Transformer/33-Transformer-et-Attention-Deroule-Numerique.md` | Le déroulé numérique : scores, échelle, mélange des valeurs, coût n². |
| 33 bis | `06-Attention-et-Transformer/33b-Generation-Prefill-Decode-Cache-KV-Streaming.md` | Le prompt est lu en un passage (prefill), puis la réponse sort token par token (decode). Le cache KV est exact grâce au masque causal ; il rend chaque pas linéaire au lieu de quadratique et se paie en mémoire. |
| 34 | `06-Attention-et-Transformer/34-Attention-Multi-Tetes.md` | Plusieurs questions en parallèle, même budget de calcul. |
| 35 | `06-Attention-et-Transformer/35-Encodage-de-Position.md` | Sans position, l’attention ne distingue pas l’ordre des mots. |
| 36 | `06-Attention-et-Transformer/36-Normalisation-de-Couche.md` | Pourquoi les couches suivantes ne saturent pas. |
| 36 bis | `06-Attention-et-Transformer/36b-Melange-d-Experts-MoE.md` | Un routeur n’active que k experts par token : beaucoup de paramètres, peu de calcul. Poids renormalisés, perte d’équilibrage, paramètres actifs contre paramètres totaux. |
| 36 ter | `06-Attention-et-Transformer/36c-Encodeur-Attention-Croisee-et-Embeddings.md` | Encodeur, décodeur, encodeur-décodeur : seuls le masque et l’origine de K et V changent. D’où viennent les embeddings du RAG : moyenne masquée, puis normalisation. |
| 37 | `06-Attention-et-Transformer/37-Transformer-Formules-de-Liaison.md` | Le pont entre les étapes 34, 35 et 36. Il ne remplace pas leur déroulé. |

---

## 7. Choisir la prochaine étape — dossier `07-Planification`

A* classe des étapes par `f = g + h`. Ce nombre ne dit pas si une étape vaut le coup dans un environnement incertain. Bellman le dit. On lit Bellman, puis A*.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 37 bis | `07-Planification/37b-Planification-Definitions-Fondamentaux.md` | Planifier, c’est décider de la suite avant de la faire : quelles étapes, dans quel ordre, avec quels outils, et quoi faire si une étape échoue. |
| 38 | `07-Planification/38-Agent-et-Planification-MDP-Bellman.md` | γ change l’action. Le vol pas cher gagne à γ = 0,10. Le vol direct gagne à γ = 0,95. |
| 39 | La seconde moitié de `02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md` | La contraction : deux estimations de valeur se rejoignent. Déjà ouvert à l’étape 3. On y revient pour Bellman seulement. |
| 40 | `07-Planification/40-Planification-Formule-A-Star.md` | `g` est le coût déjà payé, `h` le coût restant estimé, `f` leur somme. Si `h` vaut 0, A* devient Dijkstra. `h` ne doit pas surestimer (admissible). Avec un ensemble fermé qu’on ne rouvre pas, elle doit aussi être consistante. Sinon, l’optimalité du chemin n’est plus garantie. |

---

## 8. Ordonner plusieurs tâches — dossier `08-Orchestration`

Un score de priorité dit qui est urgent. Il ne dit pas qui a le droit de commencer. Un graphe le dit, à condition qu’il n’y ait pas de cycle.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 40 bis | `08-Orchestration/40b-Orchestration-Definitions-Fondamentaux.md` | Workflow ou agent, les cinq motifs d’orchestration, l’état partagé, la reprise après panne, l’intervention humaine. |
| 41 | `08-Orchestration/41-Orchestration-Formule-Score-de-Priorite.md` | `urgence` et `impact` poussent vers le haut, `coût` tire vers le bas. Les poids `w` disent lequel commande. |
| 42 | `08-Orchestration/42-Orchestration-Graphes.md` | Matrice d’adjacence, trace, vagues parallèles. |
| 43 | `08-Orchestration/43-Fondements-Orchestration-et-DAG.md` | Pourquoi A³ = 0 prouve qu’il n’y a pas de chemin assez long pour boucler. Le fichier continue avec d’autres chapitres collés : on s’arrête à la section Kahn. |
| 44 | `08-Orchestration/44-Tri-Topologique-Kahn.md` | L’ordre d’exécution. Le degré entrant tombe à 0 quand les prérequis sont finis. |
| 45 | `08-Orchestration/45-Detection-de-Cycle-DFS.md` | Kahn dit qu’un cycle existe. DFS donne le nom des agents pris dedans. |
| 45 bis | `08-Orchestration/45b-Journal-d-Evenements-Partitionne.md` | Des agents qui communiquent par un journal découpé en partitions : l’ordre est garanti par clé, pas globalement ; le parallélisme ne dépasse pas le nombre de partitions ; changer ce nombre déplace la plupart des clés. |
| 45 ter | `08-Orchestration/45c-Declencheurs-Webhooks-et-Taches-Longues.md` | Un agent démarré par un événement extérieur : signature HMAC, horodatage, rejet des rejeux, comparaison en temps constant, tâche longue suivie par son statut. |

---

## 9. Exposer les outils — dossier `09-MCP`

MCP arrive après les outils et après l’orchestration. C’est le protocole qui rend un outil disponible à plusieurs agents, pas la définition de l’outil.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 46 | `09-MCP/46-MCP-Definitions-Fondamentaux.md` | Ce qu’est un serveur MCP. |
| 47 | `09-MCP/47-MCP-Exemples-Cas-Usage.md` | Des exemples. |
| 48 | `09-MCP/48-MCP-Applications-Domaines.md` | Des domaines. |
| 49 | `09-MCP/49-MCP-Formule-Score-de-Disponibilite.md` | Un serveur souvent en panne ne doit pas être choisi. Le score se lit après avoir vu, dans les files d’attente plus loin, ce que « disponible » veut dire sous charge. On y revient après l’étape 71. |
| 49 bis | `09-MCP/49b-A2A-et-Edition-par-Diff.md` | Deux agents qui se délèguent une tâche (A2A), et un agent qui modifie un fichier en remplaçant une occurrence unique plutôt qu’en le réécrivant. Construit depuis une feuille blanche. |

---

## 10. Mesurer — dossier `10-Evaluation`

On mesure d’abord si la réponse colle aux documents (fidélité), puis si elle répond à la question, puis si le retrieval et les outils étaient justes, puis si la tâche est réussie, puis si le modèle était surpris. La précision et le rappel généraux viennent avant leurs variantes RAG, parce que Context Precision et Tool Call F1 en sont des cas particuliers.

Les étapes 50 à 52 ouvrent ce chapitre : elles donnent la matrice de confusion, la KL et la perplexité, dont les formules métier sont des spécialisations. Le vocabulaire de l’évaluation (jeu de test, juges, barrière de déploiement) a déjà été posé à l’étape 13 bis.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 50 | `10-Evaluation/50-Precision-Rappel-F1-et-KL.md` | Précision, rappel, F1, KL. |
| 51 | `10-Evaluation/51-Specificite-NPV-AUC.md` | Spécificité, NPV, accuracy, AUC. L’accuracy félicite un agent qui ne fait rien sur un événement rare. |
| 52 | `10-Evaluation/52-Perplexite-LLM.md` | Perplexité : à quel point le modèle est surpris par le token réel. |
| 53 | `10-Evaluation/53-Evaluation-Formules-Theoremes-Algorithmes.md` | Le récit du dossier évaluation. |
| 54 | `10-Evaluation/54-Evaluation-Formule-Faithfulness.md` | Les affirmations de la réponse sont-elles dans le contexte. |
| 55 | `10-Evaluation/55-Evaluation-Formule-Answer-Relevancy.md` | La réponse parle-t-elle de la question. |
| 56 | `10-Evaluation/56-Evaluation-Formule-Precision-Recall-F1.md` | Les trois taux, version évaluation. |
| 57 | `10-Evaluation/57-Evaluation-Formule-Context-Precision.md` | Precision@k appliquée au contexte injecté. |
| 58 | `10-Evaluation/58-Evaluation-Formule-Context-Recall.md` | Recall du contexte. On le lit après Context Precision, comme Recall@k après Precision@k. |
| 59 | `10-Evaluation/59-Evaluation-Formule-Tool-Call-F1.md` | F1 sur les outils appelés. Il suppose l’étape 12. |
| 60 | `10-Evaluation/60-Evaluation-Formule-Agent-Goal-Accuracy.md` | La tâche est-elle finie, pas seulement la phrase juste. |
| 60 bis | `10-Evaluation/60b-Loi-Beta-et-Petits-Echantillons.md` | Un taux mesuré sur dix essais reste incertain. La loi bêta, mise à jour par Bayes, donne cette incertitude ; règle de Laplace et prédiction de pass^k. |
| 61 | `10-Evaluation/61-Evaluation-Formule-MAP.md` | Moyenne des précisions le long du classement. Après MRR et Precision@k. |
| 62 | `10-Evaluation/62-Evaluation-Formule-Perplexite.md` | La version métier de l’étape 52. |
| 63 | `10-Evaluation/63-Evaluation-Formule-Answer-Correctness.md` | Justesse de la réponse : la F1 des affirmations comparées à la référence (poids 0,75), mélangée à la similarité sémantique (poids 0,25). |
| 64 | `10-Evaluation/64-Evaluation-Formule-Exact-Match.md` | Égalité stricte. Le cas le plus dur de la justesse, donc après. |
| 64 bis | `10-Evaluation/64b-Theoremes-Fidelite-Pertinence-et-F1.md` | Les démonstrations : monotonie de Faithfulness, Answer Relevancy comme produit avec un centroïde, F1 = 2TP/(2TP+FP+FN), F1 encadrée par min(P, R) et (P+R)/2, F-bêta, Context Precision = 1 ssi les pertinents sont devant, Tool Call F1. |
| 65 | `10-Evaluation/65-Evaluation-Exemples-Cas-Usage.md` | Les métriques sur des cas métier. |
| 65 bis | `10-Evaluation/65b-Classement-par-Duels-Elo-Bradley-Terry.md` | Comparer deux versions d’agent par duels jugés plutôt que par une note absolue : Elo, Bradley-Terry, gradient « victoires observées moins victoires attendues », optimum unique. |
| 65 ter | `10-Evaluation/65c-Complaisance-et-Horizon-de-Tache.md` | L’agent abandonne-t-il une bonne réponse quand l’utilisateur conteste ? Taux de bascule, exactitude après contestation. Et jusqu’à quelle longueur de tâche il réussit encore. |

---

## 11. Bloquer — dossier `11-GardeFous`

Le garde-fou consomme des signaux qu’on ne sait lire qu’après l’évaluation : une réponse peu fidèle, un outil dangereux, un score de risque au-dessus d’un seuil.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 66 | `11-GardeFous/66-GardeFous-Definitions-Fondamentaux.md` | Les types de garde-fous. |
| 67 | `11-GardeFous/67-GardeFous-Formule-Score-de-Risque.md` | Le score qui décide de laisser passer ou d’arrêter. La KL de l’étape 50 est le cas où le signal est une distribution, pas un compteur. |
| 67 bis | `11-GardeFous/67b-Sandbox-d-Execution.md` | Exécuter le code écrit par le modèle dans un processus séparé, avec un temps et une sortie bornés. Un filtre sur le texte du code n’est pas une frontière : l’isolement vient du processus. |

---

## 12. Tenir une fois que l’agent répond — dossier `12-Production-Couts-Optimisation`

Ces chapitres ne changent pas le sens d’une réponse. Ils disent si le service reste debout, ce qu’il coûte, et comment on le spécialise. On les lit quand la boucle de l’étape 1 existe vraiment.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 68 | `12-Production-Couts-Optimisation/68-Notation-de-Kendall.md` | Les lettres M/M/1, M/M/c, M/G/1. À lire avant les formules, sinon M ne veut rien dire. |
| 69 | `12-Production-Couts-Optimisation/69-Files-Attente-et-Goulot.md` | Little, et pourquoi ρ = 0,95 fait exploser l’attente. |
| 70 | `12-Production-Couts-Optimisation/70-File-MM1.md` | Un seul agent. Séjour, attente, service, séparés. |
| 71 | `12-Production-Couts-Optimisation/71-Erlang-C.md` | Plusieurs instances. On ne fait attendre que les requêtes qui trouvent tout le monde occupé. |
| 72 | `12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md` | Sans fenêtre, le coût d’entrée croît comme le carré du nombre d’étapes. |
| 72 bis | `12-Production-Couts-Optimisation/72b-Batching-Continu-et-PagedAttention.md` | Servir plusieurs requêtes à la fois sans attendre la plus longue, et allouer le cache KV par pages. La loi de Little fixe la capacité. |
| 72 ter | `12-Production-Couts-Optimisation/72c-Decodage-Speculatif.md` | Un petit modèle propose, le grand vérifie en un passage. La sortie suit exactement la loi du grand modèle ; acceptation 1 − TV(p, q), tokens moyens par passe. |
| 72 quater | `12-Production-Couts-Optimisation/72d-Observabilite-Traces-Couts-et-Derive.md` | Traces et spans, coût d’une exécution sans double comptage, percentiles qui ne s’additionnent pas, budget d’erreur, dérive mesurée par le PSI. |
| 72 quinquies | `12-Production-Couts-Optimisation/72e-Budget-de-Raisonnement.md` | Plus de calcul au moment de répondre : best-of-N, vote majoritaire, niveau d’effort. Les rendements sont décroissants, et un vérificateur imparfait plafonne le gain. |
| 73 | `12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md` | Descente de gradient et LoRA, si l’on spécialise le modèle au lieu de seulement le prompter. |
| 73 bis | `12-Production-Couts-Optimisation/73b-Quantification-INT8-INT4.md` | Stocker les poids sur 8 ou 4 bits : erreur d’arrondi au plus s/2, erreur quadratique moyenne s²/12, valeurs aberrantes isolées par groupes ou par canaux. |
| 73 ter | `12-Production-Couts-Optimisation/73c-Distillation-Maitre-Eleve.md` | Un petit modèle apprend les probabilités adoucies d’un grand : rôle de la température, facteur T², lien avec la régression des logits. |
| 74 | `12-Production-Couts-Optimisation/74-Optimiseur-Adam.md` | Pourquoi le même pas ne convient pas à tous les poids. |
| 74 bis | `12-Production-Couts-Optimisation/74b-Alignement-SFT-RLHF-PPO-GRPO-DPO.md` | Comment un modèle de base devient un assistant : imitation (SFT), modèle de récompense de Bradley-Terry, RLHF avec PPO ou GRPO, puis DPO qui se passe du modèle de récompense. |
| 75 | `12-Production-Couts-Optimisation/75-Optimisation-Formules.md` | Adam, rétropropagation, L1/L2. La rétropropagation y est corrigée : la sigmoïde de sortie a sa dérivée. |
| 75 bis | `12-Production-Couts-Optimisation/75b-Mini-Lots-et-Generalisation.md` | Pourquoi on apprend sur des mini-lots : gradient sans biais, variance en 1/B, époques et accumulation de gradient, plancher de bruit d’un pas constant. |
| 76 | `12-Production-Couts-Optimisation/76-Regularisation-L1-L2.md` | L2 rapetisse. L1 peut éteindre un poids. |

Après l’étape 71, revenir à `09-MCP/49-MCP-Formule-Score-de-Disponibilite.md` : « disponible » se mesure maintenant comme une file qui n’est pas saturée, pas comme un booléen.

---

## 13. Assembler : un agent depuis une feuille blanche — dossier `13-Projet-Final`

Toutes les pièces existent. Le projet final les assemble dans un seul programme : prompt, schéma, outils, mémoire, RAG hybride, boucle ReAct, garde-fou et évaluation. Chaque bloc du programme renvoie à l’étape qui l’explique.

| Ordre | Fichier | Ce qu’il fixe |
| --- | --- | --- |
| 77 | `13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md` | Un agent complet, hors ligne avec un faux LLM, puis branché sur un vrai modèle. À refaire de tête : c’est l’exercice d’entretien. |

---

## 14. Synthèse et révision — dossier `14-Synthese-et-Revision`

Ce chapitre n’est pas un deuxième cours. Il sert à réviser, une fois le parcours fait.

| Ordre | Fichier | Rôle |
| --- | --- | --- |
| 78 | `14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md` | Diapositives. Section 41 : un plan de quatre semaines. Section 45 : renvoi vers les déroulés. |
| 79 | `14-Synthese-et-Revision/79-Index-des-Equations.md` | Liste courte des équations, puis la table « où l’algorithme est raconté ». |

Pour réviser avec les images, ouvrir `Images/00_Sommaire-des-fiches.md` : 34 fiches, une par formule, chacune avec son image. Les fiches 07 (Bayes) et 22 (espérance) couvrent deux notions qui servent dans tout le cours sans avoir d’étape à elles.

`08-Orchestration/43-Fondements-Orchestration-et-DAG.md` contient, après le DAG, une copie des chapitres évaluation, attention, LoRA, files et coûts. Ces copies ne se lisent pas là. Elles se lisent aux étapes 50, 33, 73, 69 et 72.

---

## Exercices : construire l’agent pas à pas — dossier `Exercices`

Ce dossier est à part du parcours, comme `Images/` et `Demonstrations/` : le cours est lu, les exercices le font pratiquer. En douze paliers, on code soi-même l’agent de l’étape 77, une pièce par palier, dans l’ordre du cours. Chaque palier contient un énoncé (`README.md` : rappel de cours, spécification chiffrée, cas d’usage aux Émirats, sortie attendue), un dossier `projet/` avec le squelette à compléter et les tests à faire passer, et un dossier `solutions/` avec la solution entière et, dans `solutions/progression/`, la solution construite pas à pas, chaque bloc de code suivi de ses explications. Le mode d’emploi est dans `Exercices/README.md`. Un palier peut se faire juste après les étapes qu’il cite, ou tous à la suite après l’étape 77.

| Palier | Énoncé | Ce qu’on code | Étapes du cours |
| --- | --- | --- | --- |
| 01 | `Exercices/01-Modele-et-Prompt/README.md` | Le faux modèle scripté, les messages, le prompt qui isole les données non fiables. | 1 à 7 |
| 02 | `Exercices/02-Schemas-et-Validation/README.md` | Un validateur de schéma JSON et la boucle de réparation. | 8 à 11 |
| 03 | `Exercices/03-Outils-Metier-EAU/README.md` | Mensualité, endettement CBUAE, fin de service, TVA, IBAN AE, Emirates ID. | 8 à 12 |
| 04 | `Exercices/04-Registre-d-Outils/README.md` | Le registre d’outils, la porte qui valide, l’enveloppe d’erreur. | 12, 46 à 49 |
| 05 | `Exercices/05-Boucle-d-Agent/README.md` | La boucle ReAct et ses trois arrêts. | 1, 13 |
| 06 | `Exercices/06-Memoire/README.md` | Récence, score de pertinence, rappel des souvenirs. | 14 à 17 |
| 07 | `Exercices/07-Recherche-Hybride/README.md` | BM25, cosinus, RRF, citations. | 18 à 30 |
| 08 | `Exercices/08-Planification-DAG/README.md` | Tri topologique, vagues parallèles, chemin critique. | 38 à 45 |
| 09 | `Exercices/09-Garde-Fous/README.md` | Politique, masquage, score de risque, veto, approbation humaine, journal chaîné. | 66, 67 |
| 10 | `Exercices/10-Evaluation/README.md` | Tool Call F1, Goal Accuracy, Wilson, fidélité, barrière CI. | 50 à 65 |
| 11 | `Exercices/11-Production-et-Couts/README.md` | Coût d’une tâche, seau à jetons, relances, p95, budget. | 68 à 72 |
| 12 | `Exercices/12-Assemblage-Agent-Complet/README.md` | L’agent complet, puis l’adaptateur qui branche Claude. | 77 |

---
