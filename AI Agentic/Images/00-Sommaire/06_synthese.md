# Synthèse

> Image : `06_synthese.jpg` · Texte exact ci-dessous. L'image peut couper un accent ; cette fiche prime.

## Texte de l'affiche

**Synthèse — construire l'agent**

1. Le succès est un produit : une étape ratée annule la chaîne.
2. Le modèle choisit un token par la softmax, puis une phrase par le produit de ces choix.
3. On décide ce qui entre dans la fenêtre, puis on compare des vecteurs par le cosinus.
4. La mémoire mélange ce cosinus, la récence et l'importance, sur une même échelle de 0 à 1.
5. BM25 rattrape les mots exacts. RRF fusionne les rangs, pas les scores.
6. On mesure le classement, rappel, précision, MRR, NDCG, avant de l'injecter.
7. L'attention lit ce contexte. La position lui rend l'ordre des mots.
8. Bellman choisit en regardant la suite. On s'arrête quand l'information ne vaut plus son coût.
9. On mesure la réponse, on chiffre les jetons, et seulement alors on descend le gradient.

La formule sans les mots d'avant ne dit pas à quoi sert le nombre.
