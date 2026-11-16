# Affiches unitaires — 09 à 45

Chaque fichier `NN_….jpg` est une affiche sur fond blanc. Le texte ci-dessous est celui de l'affiche. L'équation développée, les symboles et l'étape du parcours sont dans [00_Sommaire.md](<00_Sommaire.md>), classes 1 à 18.

On les lit dans l'ordre des numéros, après `08_bilan.jpg`.

## Une formule par affiche

| Image | Titre sur l'affiche | Ligne de formule | Phrase |
| --- | --- | --- | --- |
| `09_esperance.jpg` | 1. Espérance | E[X] = somme de x fois P(x) | Prévoir le coût moyen, en comptant les cas rares. Étape 1. |
| `10_fiabilite.jpg` | 2. Fiabilité | P = p1 × p2 × ... × pn | Une étape ratée annule toute la chaîne. Étape 1. |
| `11_softmax.jpg` | 3. Softmax | haut : exp(zi / T) ; bas : somme exp(zj / T) | Le haut est le token i. Le bas additionne tous les tokens. T vers 0 est un argmax. Étape 2. |
| `12_vraisemblance.jpg` | 4. Vraisemblance | P(texte) = produit P(token donné le passé) | La phrase est cette chaîne de choix. Étape 3. |
| `13_budget.jpg` | 5. Budget | jetons admis ≤ fenêtre | Choisir ce qui entre avant de remplir. Étape 13 ter. |
| `14_produit_scalaire.jpg` | 6a. Produit scalaire | x · y = somme de xi fois yi | Mesure l'alignement de deux vecteurs. Étape 14. |
| `15_norme.jpg` | 6b. Norme | norme(x) = racine de la somme des carrés | Mesure la longueur. Un vecteur nul n'a pas de direction. Étape 14. |
| `16_cosinus.jpg` | 6c. Cosinus | haut : x · y ; bas : norme(x) × norme(y) | Le cosinus est le haut divisé par le bas. Étape 14. |
| `17_memoire.jpg` | 7. Mémoire | score = poids × similarité + récence + importance | Poids positifs, somme 1. Un vieux souvenir pèse moins. Étapes 16 et 17. |
| `18_bm25.jpg` | 8. BM25 | les mots rares et exacts comptent | Un numéro de clause n'est pas un vecteur. TF-IDF en est l'ancêtre. Étape 22. |
| `19_rrf.jpg` | 9. RRF | somme de 1 / (60 + rang) | On fusionne des rangs, pas des scores. Étape 24. |
| `20_rappel.jpg` | 10a. Rappel | utiles retrouvés / utiles | Quelles preuves manquent dans le top k. Étape 25. |
| `21_precision.jpg` | 10b. Précision | utiles dans le top k / k | Combien de résultats sont utiles. Étape 26. |
| `22_mrr.jpg` | 11a. MRR | 1 / rang du premier document utile | Le premier bon passage arrive-t-il tôt. Étape 27. |
| `23_ndcg.jpg` | 11b. NDCG | un bon document en tête vaut plus | Le rang compte, pas seulement la présence. Étape 28. |
| `24_f1.jpg` | F1 | 2 × P × R / (P + R) | Un seul taux quand précision et rappel comptent ensemble. Étape 50. |
| `25_attention.jpg` | 12. Attention | softmax( (Q · K) / racine(d) ) puis mélange de V | Lire le contexte déjà rempli. Étape 31. |
| `26_position.jpg` | 13. Position | sinus et cosinus de la place du token | Sans position, l'attention ignore l'ordre. Étape 35. |
| `27_utilite.jpg` | 14a. Utilité | somme de P(issue) fois utilité(issue) | Choisir l'action dont le gain moyen est le plus haut. Étape 38. |
| `28_bellman.jpg` | 14b. Bellman | valeur = max (gain + suite actualisée) | L'action d'aujourd'hui change la valeur de demain. Avant A*. Étape 38. |
| `29_q_learning.jpg` | 14c. Q-learning | nouvelle Q = ancienne Q + pas × (cible − ancienne Q) | La cible est la récompense plus la meilleure Q suivante. Étape 38. |
| `30_reinforce.jpg` | 14d. REINFORCE | gradient du log de la politique × retour | On renforce les actions qui ont précédé un bon retour. Étape 38. |
| `31_information.jpg` | 15. Information | chercher si le gain espéré dépasse le coût | Savoir quand arrêter la boucle. Étape 38. |
| `32_bayes.jpg` | 16a. Bayes | P(cause donnée l'alerte) proportionnelle à P(alerte donnée la cause) × P(cause) | Sans le taux de base, une alerte rare est surévaluée. Étape 51. |
| `33_kl.jpg` | 16b. KL | somme de P × log(P / Q) | Écart entre deux lois. Nulle seulement si elles sont égales. Étape 50. |
| `34_brier.jpg` | 16c. Brier | moyenne des (probabilité − issue) au carré | Juge la probabilité annoncée, pas seulement l'étiquette. Étape 51. |
| `35_entropie.jpg` | 16d. Entropie | H = − somme de p × log(p) | Dispersion d'une loi. Maximale quand tout est équiprobable. Étape 52. |
| `36_perplexite.jpg` | 16e. Perplexité | PPL = exp(entropie croisée) | À quel point le modèle est surpris par le token réel. Étape 52. |
| `37_cout.jpg` | 17. Coût | jetons entrée × prix entrée + jetons sortie × prix sortie | L'appel est linéaire. L'historique cumulé ne l'est pas. Étape 72. |
| `38_gradient.jpg` | 18a. Gradient | direction de plus forte pente de la perte | La règle de la chaîne la propage à travers les couches. Étape 73. |
| `39_descente.jpg` | 18b. Descente | nouveau theta = theta − pas × gradient | On marche à l'opposé de la pente. Étape 73. |
| `40_adam.jpg` | 18c. Adam | un pas différent pour chaque poids | Le même pas ne convient pas à tous les poids. Étape 74. |
| `45_risque.jpg` | Garde-fou | score = somme de poids × signaux, puis veto | Il lit la mesure. Il ne la précède pas. Étape 67. |

## Cartes et processus en plus

| Image | Ce qu'elle montre |
| --- | --- |
| `41_requete_verticale.jpg` | L'ordre d'une demande déjà en marche, de haut en bas : prompt, schéma, outil, boucle, mémoire et RAG, attention, plan, orchestration, MCP, évaluation, garde-fou. |
| `42_carte_recherche.jpg` | Du cosinus à la confiance : cosinus, BM25, RRF, rappel, précision, MRR, NDCG. |
| `43_carte_mesure.jpg` | F1, KL, Bayes, Brier, entropie, perplexité, puis le score de risque. |
| `44_carte_decision.jpg` | Utilité, Bellman, Q-learning, REINFORCE, valeur de l'information. A* vient après Bellman. |

## Lecture

Une affiche unitaire ne remplace pas la démonstration du dossier `Demonstrations/`. Elle dit où la formule se place quand on construit l'agent.
