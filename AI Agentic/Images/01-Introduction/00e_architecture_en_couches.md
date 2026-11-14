# Fiche 00e_architecture_en_couches — L'architecture en dix couches

> Image : `00e_architecture_en_couches.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

**Du but de l'utilisateur à l'action, avec une couche pour chaque risque**


## Ce que montre l'image

Une pile, lue de haut en bas.

1. Utilisateurs et canaux (web, mobile, voix, messagerie).
2. Passerelle : authentification, quotas, journal, conformité.
3. Orchestrateur : comprendre le but, planifier, découper, router, réfléchir, replanifier. En dessous, des agents spécialisés (recherche, données, code, métier, action, revue).
4. Couche modèle : plusieurs modèles, routage, repli, coût.
5. Outils : recherche, API, bases, code, MCP.
6. RAG : documents, découpage, embeddings, base vectorielle.
7. Mémoire : court terme, travail en cours, épisodes, long terme.
8. Garde-fous : injection de prompt, filtrage, données personnelles, humain, permissions d'outils.
9. Observation et évaluation : traces, métriques, coût, qualité, erreurs, retours.
10. Déploiement : cloud, conteneurs, livraison, mise à l'échelle.

## Ce que c'est

L'affiche dit où vit chaque chapitre une fois le système en production. Le modèle (couche 4) ne voit le monde que par les couches 5, 6 et 7. Il n'est pas l'architecture.

## Effets et impacts

- Sans couche 2, un agent interne est exposé comme une API ouverte.
- Sans couche 8, un outil d'écriture peut être appelé par une instruction cachée dans un document.
- Sans couche 9, on ne sait pas si un changement de prompt a amélioré ou cassé le but. C'est l'étape 13 bis.

## Exemple

Une demande « résilie ce contrat » traverse la passerelle (qui a le droit), l'orchestrateur (quel agent), les outils (le système de contrats), le garde-fou (montant et identité), puis la trace (qui a validé).

## Dans le cours

- [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)
- [Étape 13 bis — Évaluer avant d'améliorer](<../../03-Schemas-Outils-et-Premiere-Evaluation/13b-Evaluation-Definitions-Fondamentaux.md>)
