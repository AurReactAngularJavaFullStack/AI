# Fiche 00c_agent_contre_ia_agentique — Un agent n'est pas l'IA agentique

> Image : `00c_agent_contre_ia_agentique.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

**Le travailleur, et le système qui le fait travailler**


## Ce que montre l'image

Deux colonnes.

**AI Agent, le travailleur.** Un système qui comprend un but, raisonne, utilise des outils, agit, observe, et continue jusqu'à la fin. L'exemple tient en une ligne : trouver la dernière plainte et rédiger une réponse. Quatre pas : chercher, retrouver, générer, rendre.

**Agentic AI, le système.** Plusieurs agents, un plan, une mémoire, une orchestration d'outils, des messages entre agents, des boucles de retour, des décisions qui changent, un humain dans la boucle. L'exemple est un objectif durable : surveiller les plaintes et réduire le délai. Le flux classifie, délègue, appelle des outils, escalade, évalue, puis améliore le flux.

Le bas de l'affiche résume : l'agent est un composant. L'IA agentique est l'architecture qui permet à ces composants d'atteindre un but tout seuls.

## Ce que c'est

La question utile n'est pas « le modèle peut-il appeler un outil ? ». C'est « le système peut-il choisir la bonne action, se reprendre après un échec, et finir le but de façon fiable ? ».

## Effets et impacts

- Nommer « agent » un simple appel d'outil cache l'absence de plan, de mémoire et d'évaluation.
- Le système de droite a besoin de presque tout le parcours : outils (étape 12), mémoire (étape 15 bis), RAG (chapitre 5), orchestration (chapitre 8), évaluation (chapitre 10), garde-fous (chapitre 11).
- La fiabilité du système est le produit des fiabilités de ses agents (fiche 29), pas la fiabilité du meilleur d'entre eux.

## Exemple

Un agent « support » qui rédige une réponse est le travailleur. Le dispositif qui surveille la boîte, route les cas critiques vers un humain, mesure le délai et modifie le routage est l'IA agentique.

## Dans le cours

- [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)
- [Étape 12 — Les outils](<../../03-Schemas-Outils-et-Premiere-Evaluation/12-Outils-Definitions-Fondamentaux.md>)
