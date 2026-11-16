# Carte mentale — créer l'agent

> Image : `01_carte_mentale_creation.jpg` · Les équations exactes sont dans [le sommaire](<00_Sommaire.md>).

## Ce que montre l'image

Un centre, « Créer un agent », et huit branches dans le sens des aiguilles, de 1 à 8. Chaque branche est un moment de la construction, pas une couche d'architecture.

1. **Boucle.** Espérance, puis fiabilité en produit. On prévoit le coût moyen et on sait qu'une étape ratée annule la chaîne (étape 1).
2. **Jeton.** Softmax, puis la phrase entière. Le modèle choisit un token avant qu'on juge un prompt (étapes 2 et 3).
3. **Fenêtre.** Budget, produit scalaire, norme, cosinus. On décide ce qui entre, puis on compare des directions (étapes 13 ter et 14).
4. **Mémoire.** Récence, importance, pertinence. Le cosinus est déjà connu ; la décroissance le pondère (étapes 16 et 17).
5. **Preuves.** BM25, puis fusion par les rangs. Les mots exacts rattrapent le sens ; RRF n'additionne pas des scores d'échelles différentes (étapes 22 et 24).
6. **Lecture.** Attention, puis la position. Le prompt est déjà rempli ; sans position, l'attention ignore l'ordre (étapes 31 et 35).
7. **Choix.** Utilité, Bellman, quand s'arrêter. L'action d'aujourd'hui change la valeur de demain (étape 38).
8. **Confiance.** Mesurer, chiffrer, puis apprendre. F1, KL, Bayes, Brier et perplexité, puis le coût des jetons, puis le gradient et Adam (étapes 50 à 74). Sur l'affiche, lire « Mesurer » avec l'accent.

## Justification

Cet ordre est celui du parcours et des exercices. Une branche n'existe que parce que la précédente a fourni son ingrédient : le cosinus avant la mémoire, deux classements avant RRF, un contexte plein avant l'attention, une boucle qui marche avant Adam.
