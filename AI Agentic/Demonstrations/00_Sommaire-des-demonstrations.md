# Démonstrations des formules

Chaque formule du dossier `Images/` a ici son fichier de démonstrations, au même nom et dans le même sous-dossier : `Images/02-Vecteurs/03_similarite_cosinus.md` ↔ `Demonstrations/02-Vecteurs/03_similarite_cosinus.md`. On ouvre la fiche (ou l'image) à gauche et la démonstration à droite.

Chaque fichier contient, dans cet ordre :

1. la formule, en bloc, puis **ses symboles, un par un** (un bloc par symbole, suivi de sa définition) ;
2. **le mécanisme, avant les preuves** : ce que la formule fait aux nombres qu'on lui donne, déroulé sur un petit exemple chiffré ;
3. quatre à six **démonstrations** pas à pas (d'où vient la formule, ses propriétés, ses cas limites, sa sensibilité). Chacune dit dans l'ordre ce qu'on démontre, l'idée, la preuve étape par étape, une vérification chiffrée, ce que la preuve révèle du mécanisme et sa conséquence pour un agent ;
4. un **exemple simple**, calculable à la main, avec tous les calculs intermédiaires écrits ;
5. **quatre cas d'usage complexes, démontrés**, situés aux Émirats (banque, immobilier, crypto, assurance, RH, BTP, secteur public). Chaque cas donne le contexte, les données, le calcul pas à pas, la décision de l'agent, un contre-calcul (ce que donnerait l'erreur naïve), la sensibilité (la valeur à partir de laquelle la décision bascule) et ce qu'on surveille en production. Les montants et volumes non réglementaires sont illustratifs ;
6. des **exercices sur feuille A4**, puis leur **corrigé** détaillé étape par étape ;
7. un **programme Python** (bibliothèque standard seulement) dont les vérifications recalculent tous les nombres du fichier, cas d'usage compris (une fonction par cas), et sa sortie attendue ;
8. le **squelette algorithmique** de la formule : le pseudo-code en français (ENTRÉES, SORTIE, boucles), sa complexité, et le lien ligne à ligne avec les fonctions du programme.

## Méthode feuille blanche

1. Lire la fiche de la formule et la démonstration une première fois, sans rien écrire.
2. Fermer les deux fichiers. Sur une feuille A4, réécrire la formule, définir chaque symbole, puis refaire chaque démonstration de mémoire.
3. Rouvrir le fichier et comparer, ligne par ligne. Corriger en rouge ce qui manquait.
4. Faire les exercices sur la feuille, sans calculatrice sauf mention contraire, puis vérifier avec le corrigé. Pour chaque cas d'usage, cacher le calcul, le refaire à partir des seules données, puis retrouver la valeur de bascule de la rubrique « Sensibilité ».
5. Recopier le programme dans un fichier, le lancer, et vérifier qu'il affiche « OK — toutes les vérifications sont passées. ». Le modifier : changer un nombre de l'exemple, prédire le résultat sur la feuille, puis relancer. Enfin, réécrire le squelette algorithmique de mémoire et le traduire en Python sans regarder le programme.
6. Recommencer le lendemain, sans regarder, jusqu'à tout refaire seul.

Pour lancer un programme dans PowerShell :

```text
& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" demo.py
```

## Dans l'ordre des dossiers, comme Images/

| Dossier | Démonstrations |
| --- | --- |
| 01-Introduction | [29 — Fiabilité en série](<01-Introduction/29_fiabilite_serie.md>) |
| 02-Vecteurs | [01 — Produit scalaire](<02-Vecteurs/01_produit_scalaire.md>) · [02 — Norme L2](<02-Vecteurs/02_norme_L2.md>) · [03 — Similarité cosinus](<02-Vecteurs/03_similarite_cosinus.md>) |
| 03-Modele | [04 — Softmax et température](<03-Modele/04_softmax_temperature.md>) · [05 — Attention](<03-Modele/05_attention_scaled_dot_product.md>) · [06 — Entropie croisée](<03-Modele/06_entropie_croisee.md>) · [23 — Vraisemblance autorégressive](<03-Modele/23_vraisemblance_autoregressive.md>) · [30 — Encodage de position](<03-Modele/30_encodage_position.md>) · [32 — Perplexité](<03-Modele/32_perplexite.md>) |
| 04-Recherche | [11 — BM25](<04-Recherche/11_bm25.md>) · [12 — Précision](<04-Recherche/12_precision.md>) · [13 — Rappel](<04-Recherche/13_rappel.md>) · [14 — Score F1](<04-Recherche/14_score_f1.md>) · [24 — TF-IDF](<04-Recherche/24_tfidf.md>) · [25 — RRF](<04-Recherche/25_rrf.md>) · [26 — NDCG](<04-Recherche/26_ndcg.md>) · [33 — MRR](<04-Recherche/33_mrr.md>) |
| 05-Contexte | [15 — Budget de contexte](<05-Contexte/15_budget_contexte.md>) · [27 — Score de mémoire](<05-Contexte/27_score_memoire.md>) |
| 06-Decision | [09 — Équation de Bellman](<06-Decision/09_equation_bellman.md>) · [10 — Utilité espérée](<06-Decision/10_utilite_esperee.md>) · [18 — Q-learning](<06-Decision/18_q_learning.md>) · [19 — REINFORCE](<06-Decision/19_reinforce.md>) · [22 — Espérance](<06-Decision/22_esperance.md>) · [28 — Valeur de l'information](<06-Decision/28_valeur_information.md>) |
| 07-Mesure | [07 — Théorème de Bayes](<07-Mesure/07_theoreme_bayes.md>) · [17 — Divergence KL](<07-Mesure/17_divergence_kl.md>) · [20 — Score de Brier](<07-Mesure/20_score_brier.md>) · [21 — Entropie](<07-Mesure/21_entropie.md>) |
| 08-Entrainement | [08 — Descente de gradient](<08-Entrainement/08_descente_de_gradient.md>) · [31 — Adam](<08-Entrainement/31_adam.md>) · [34 — Gradient](<08-Entrainement/34_gradient.md>) |
| 09-Production | [16 — Coût d'inférence](<09-Production/16_cout_inference.md>) |

## Dans l'ordre du cours

Pour suivre le parcours de lecture, on fait les démonstrations au moment où la leçon les utilise.

| Étape du cours | Démonstrations à faire |
| --- | --- |
| 1 — L'agent | [29 Fiabilité en série](<01-Introduction/29_fiabilite_serie.md>), [22 Espérance](<06-Decision/22_esperance.md>) |
| 2 — Softmax | [04 Softmax et température](<03-Modele/04_softmax_temperature.md>) |
| 3 — Fondements du LLM | [23 Vraisemblance autorégressive](<03-Modele/23_vraisemblance_autoregressive.md>) |
| 13 ter — Contexte | [15 Budget de contexte](<05-Contexte/15_budget_contexte.md>) |
| 14 — Similarité | [01 Produit scalaire](<02-Vecteurs/01_produit_scalaire.md>), [02 Norme L2](<02-Vecteurs/02_norme_L2.md>), [03 Similarité cosinus](<02-Vecteurs/03_similarite_cosinus.md>) |
| 16 — Mémoire | [27 Score de mémoire](<05-Contexte/27_score_memoire.md>) |
| 22 — BM25 | [24 TF-IDF](<04-Recherche/24_tfidf.md>), puis [11 BM25](<04-Recherche/11_bm25.md>) |
| 24 — RRF | [25 RRF](<04-Recherche/25_rrf.md>) |
| 25 à 28 — Métriques du RAG | [13 Rappel](<04-Recherche/13_rappel.md>), [12 Précision](<04-Recherche/12_precision.md>), [33 MRR](<04-Recherche/33_mrr.md>), [26 NDCG](<04-Recherche/26_ndcg.md>) |
| 31 et 35 — Attention | [05 Attention](<03-Modele/05_attention_scaled_dot_product.md>), [30 Encodage de position](<03-Modele/30_encodage_position.md>) |
| 38 — Décision | [09 Bellman](<06-Decision/09_equation_bellman.md>), [10 Utilité espérée](<06-Decision/10_utilite_esperee.md>), [28 Valeur de l'information](<06-Decision/28_valeur_information.md>), [18 Q-learning](<06-Decision/18_q_learning.md>), [19 REINFORCE](<06-Decision/19_reinforce.md>) |
| 50 à 52 — Évaluation | [14 F1](<04-Recherche/14_score_f1.md>), [17 KL](<07-Mesure/17_divergence_kl.md>), [07 Bayes](<07-Mesure/07_theoreme_bayes.md>), [20 Brier](<07-Mesure/20_score_brier.md>), [21 Entropie](<07-Mesure/21_entropie.md>), [06 Entropie croisée](<03-Modele/06_entropie_croisee.md>), [32 Perplexité](<03-Modele/32_perplexite.md>) |
| 72 — Coûts | [16 Coût d'inférence](<09-Production/16_cout_inference.md>) |
| 73 et 74 — Entraînement | [34 Gradient](<08-Entrainement/34_gradient.md>), [08 Descente de gradient](<08-Entrainement/08_descente_de_gradient.md>), [31 Adam](<08-Entrainement/31_adam.md>) |

## Les liens entre les démonstrations

Certaines démonstrations s'appuient sur d'autres. Les refaire dans cet ordre évite les trous :

- Cauchy–Schwarz (01) sert à la norme (02), au cosinus (03), à la descente de gradient (08) et au gradient (34).
- ln u ≤ u − 1 (06) sert à la KL (17), qui sert à l'entropie (21).
- La linéarité de l'espérance (22) sert à l'utilité (10), au coût (16) et à la descente stochastique (08).
- La somme arithmétique (15) sert au coût d'une boucle (16).
- La softmax (04) sert à l'attention (05), à l'entropie croisée (06) et à REINFORCE (19).
- Bayes (07) sert à la valeur de l'information (28).
