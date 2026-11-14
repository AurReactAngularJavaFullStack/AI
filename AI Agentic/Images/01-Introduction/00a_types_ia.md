# Fiche 00a_types_ia — Trois sortes d'IA

> Image : `00a_types_ia.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

**Du modèle qui prévoit à l'agent qui agit**


## Ce que montre l'image

Trois étages, du plus fermé au plus autonome.

1. **IA traditionnelle** : prévision, classement, détection d'anomalies. Elle lit des données passées et rend un score.
2. **IA générative** : rédaction, automatisation de tâches, systèmes de connaissance (RAG). Elle produit un texte, mais elle ne décide pas d'agir.
3. **IA agentique** : agents qui appellent des outils, plusieurs agents qui se répartissent le travail, intégration dans un produit.

Le bas de l'affiche compare trois effets métier : automatiser une tâche, augmenter le travail humain, transformer le processus. Seul l'étage agentique est noté « haut » sur les trois.

## Ce que c'est

Ce n'est pas une formule. C'est la carte de lecture du dossier. Les fiches `01` à `34` sont les mathématiques des étages 2 et 3 : le cosinus et BM25 servent le RAG, la softmax et l'attention servent le modèle, Bellman et l'utilité servent la boucle qui agit.

## Effets et impacts

- Un chatbot qui répond une fois reste à l'étage génératif, même s'il est grand.
- Un agent qui appelle un outil, observe le résultat et recommence est à l'étage agentique.
- L'automatisation « haute » de l'affiche (mémoire, logique, escalade) n'existe que si la fiabilité de chaque étape est mesurée. C'est la fiche 29.

## Exemple

« Classe ce ticket » est un classement (étage 1). « Rédige la réponse » est une génération (étage 2). « Lis le ticket, cherche la clause, rédige, envoie, et escalade si le montant dépasse le seuil » est une boucle d'agent (étage 3).

## Dans le cours

- [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)
- [Fiche 29 — Fiabilité en série](<29_fiabilite_serie.md>)
