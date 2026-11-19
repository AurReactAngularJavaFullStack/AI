# Processus vertical — classes 7 à 12

> Image : `03_processus_vertical_recherche.jpg` · Suite de [1 à 6](<02_processus_vertical_fondations.md>). Formules : [sommaire](<00_Sommaire.md>).

## Ce que montre l'image

| Classe | Formule qui fait foi | Pourquoi elle est ici |
| --- | --- | --- |
| 7. Mémoire | `score = w_sim·sim + w_rec·rec + w_imp·imp` (composantes ramenées dans [0, 1]), récence 2^(−Δt / t½) | Le cosinus existe déjà. Un vieux souvenir pèse moins. Poids ≥ 0, somme 1. Étapes 16 et 17. |
| 8. BM25 | classement par mots exacts ; TF-IDF en est l'ancêtre | Le cosinus rate un numéro de clause. Étape 22. |
| 9. RRF | Σ 1/(60 + rang) | Après les deux listes. On fusionne des rangs, pas des scores. Étape 24. |
| 10. Rappel et précision | utiles retrouvés / utiles ; utiles dans le top k / k | On juge le classement avant de l'injecter. Étapes 25 et 26. |
| 11. MRR et NDCG | rang du premier utile ; un bon document en tête vaut plus | Le rang compte, pas seulement la présence. Étapes 27 et 28. |
| 12. Attention | softmax(QKᵀ / √dₖ) V | Le contexte est construit. √dₖ empêche la softmax de saturer. Étape 31. |

La suite est [les classes 13 à 18](<04_processus_vertical_decision.md>).
