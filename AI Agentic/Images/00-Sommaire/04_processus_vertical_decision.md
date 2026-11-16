# Processus vertical — classes 13 à 18

> Image : `04_processus_vertical_decision.jpg` · Suite de [7 à 12](<03_processus_vertical_recherche.md>). Formules : [sommaire](<00_Sommaire.md>).

## Ce que montre l'image

| Classe | Formule qui fait foi | Pourquoi elle est ici |
| --- | --- | --- |
| 13. Position | sinus et cosinus de la place du token | L'attention seule ignore l'ordre des mots. Étape 35. |
| 14. Décision | utilité espérée, puis \(V^{*}(s) = \max_a \mathbb{E}[R + \gamma V^{*}(s')]\). L'affiche le dit en mots : valeur = max (gain + suite actualisée). | Bellman avant A*. Q-learning et REINFORCE apprennent cette valeur, ils ne la précèdent pas. Étape 38. |
| 15. Information | chercher seulement si le gain espéré dépasse le coût | Critère d'arrêt de la boucle. Étape 38. |
| 16. Mesure | F1, KL, Bayes, Brier, entropie, perplexité | Croire un score s'il est calibré. Le score de risque (étape 67) lit ces signaux ensuite. Étapes 50 à 52. |
| 17. Coût | \(N_{in} P_{in} + N_{out} P_{out}\) | Prix linéaire par appel ; sans élagage, l'historique cumulé croît comme \(K^2\). Étape 72. |
| 18. Apprentissage | gradient, règle de la chaîne, \(\theta \leftarrow \theta - \eta \nabla L\), Adam | On spécialise un agent qui sait déjà s'arrêter. Étapes 73 et 74. |

L'étape 77 assemble ces dix-huit classes. Elle n'en ajoute pas.
