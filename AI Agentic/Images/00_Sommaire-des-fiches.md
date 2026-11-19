# Fiches des images de formules

Chaque image `NN_nom.jpg` a sa fiche `NN_nom.md` dans le même dossier. Ouvrir l'image à gauche, la fiche à droite, et faire défiler les deux ensemble.

Chaque fiche reprend la formule de l'image (corrigée quand l'image contient une erreur), définit chaque symbole, explique ce que la formule mesure et ses effets, donne un exemple chiffré, puis renvoie vers l'étape du cours où elle est démontrée.

L'ordre de lecture est le numéro du dossier, puis le nom du fichier dans le dossier : `01-Introduction`, `02-Vecteurs`, `03-Modele`, `04-Recherche`, `05-Contexte`, `06-Decision`, `07-Mesure`, `08-Entrainement`, `09-Production`. Dans une ligne, on lit la fiche, puis ses autres affiches dans l'ordre (`NNa`, `NNb`…), puis on refait la démonstration correspondante du dossier `Demonstrations/` sur une feuille A4.

Le dossier `00-Sommaire` ne numérote pas une formule de plus. Il remet les formules déjà vues dans l'ordre de construction de l'agent : cartes mentales, diagramme de classes vertical, synthèse, résumé et bilan. Son sommaire est [00-Sommaire/00_Sommaire.md](<00-Sommaire/00_Sommaire.md>). On l'ouvre après les neuf dossiers, pas à la place.

## Fiches, dans l'ordre de lecture

### 01-Introduction

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [00a — Trois sortes d'IA](<01-Introduction/00a_types_ia.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | — |
| [00b — IA agentique et IA traditionnelle](<01-Introduction/00b_agentique_contre_traditionnelle.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | — |
| [00c — Un agent n'est pas l'IA agentique](<01-Introduction/00c_agent_contre_ia_agentique.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | — |
| [00d — Six architectures](<01-Introduction/00d_six_architectures.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | — |
| [00e — Architecture en dix couches](<01-Introduction/00e_architecture_en_couches.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | — |
| [00f — Neuf concepts](<01-Introduction/00f_neuf_concepts.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | — |
| [00g — Les mêmes neuf concepts, illustrés](<01-Introduction/00g_neuf_concepts_illustre.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | — |
| [29 — Fiabilité en série](<01-Introduction/29_fiabilite_serie.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | [à refaire sur A4](<../Demonstrations/01-Introduction/29_fiabilite_serie.md>) |

### 02-Vecteurs

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [01 — Produit scalaire](<02-Vecteurs/01_produit_scalaire.md>) | — | [Étape 14 — Produit scalaire, norme, cosinus](<../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>) | [à refaire sur A4](<../Demonstrations/02-Vecteurs/01_produit_scalaire.md>) |
| [02 — Norme L2](<02-Vecteurs/02_norme_L2.md>) | — | [Étape 14 — Produit scalaire, norme, cosinus](<../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>) | [à refaire sur A4](<../Demonstrations/02-Vecteurs/02_norme_L2.md>) |
| [03 — Similarité cosinus](<02-Vecteurs/03_similarite_cosinus.md>) | [03a](<02-Vecteurs/03a_similarite_cosinus_affiche.md>), [03b terminale](<02-Vecteurs/03b_similarite_cosinus_terminale.md>) | [Étape 14 — Produit scalaire, norme, cosinus](<../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>) | [à refaire sur A4](<../Demonstrations/02-Vecteurs/03_similarite_cosinus.md>) |

### 03-Modele

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [04 — Softmax et température](<03-Modele/04_softmax_temperature.md>) | [04a en images](<03-Modele/04a_softmax_en_images.md>), [04b](<03-Modele/04b_fonction_softmax.md>), [04c anglais](<03-Modele/04c_softmax_function.md>), [04d terminale](<03-Modele/04d_softmax_terminale.md>), [04e politique](<03-Modele/04e_softmax_politique.md>) | [Étape 2 — Softmax et température](<../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>) | [à refaire sur A4](<../Demonstrations/03-Modele/04_softmax_temperature.md>) |
| [05 — Attention par produit scalaire normalisé](<03-Modele/05_attention_scaled_dot_product.md>) | [05a en images](<03-Modele/05a_attention_en_images.md>), [05b](<03-Modele/05b_attention_ia_agentique.md>), [05c anglais](<03-Modele/05c_attention_agentic_ai.md>), [05d terminale](<03-Modele/05d_attention_terminale.md>), [05e base des LLM](<03-Modele/05e_attention_base_llm.md>) | [Étape 31 — Attention par produit scalaire normalisé](<../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>) | [à refaire sur A4](<../Demonstrations/03-Modele/05_attention_scaled_dot_product.md>) |
| [06 — Entropie croisée](<03-Modele/06_entropie_croisee.md>) | [06a](<03-Modele/06a_entropie_croisee_affiche.md>), [06b terminale](<03-Modele/06b_entropie_croisee_terminale.md>) | [Étape 52 — Perplexité](<../10-Evaluation/52-Perplexite-LLM.md>) | [à refaire sur A4](<../Demonstrations/03-Modele/06_entropie_croisee.md>) |
| [23 — Vraisemblance autorégressive](<03-Modele/23_vraisemblance_autoregressive.md>) | — | [Étape 3 — Fondements de la softmax](<../02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md>) | [à refaire sur A4](<../Demonstrations/03-Modele/23_vraisemblance_autoregressive.md>) |
| [30 — Encodage de position](<03-Modele/30_encodage_position.md>) | — | [Étape 35 — Encodage de position](<../06-Attention-et-Transformer/35-Encodage-de-Position.md>) | [à refaire sur A4](<../Demonstrations/03-Modele/30_encodage_position.md>) |
| [32 — Perplexité](<03-Modele/32_perplexite.md>) | — | [Étape 52 — Perplexité](<../10-Evaluation/52-Perplexite-LLM.md>) | [à refaire sur A4](<../Demonstrations/03-Modele/32_perplexite.md>) |

### 04-Recherche

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [11 — BM25](<04-Recherche/11_bm25.md>) | — | [Étape 22 — BM25](<../05-RAG/22-RAG-Formule-BM25.md>) | [à refaire sur A4](<../Demonstrations/04-Recherche/11_bm25.md>) |
| [12 — Précision](<04-Recherche/12_precision.md>) | — | [Étape 26 — Precision@k](<../05-RAG/26-RAG-Formule-Precision-at-k.md>) | [à refaire sur A4](<../Demonstrations/04-Recherche/12_precision.md>) |
| [13 — Rappel](<04-Recherche/13_rappel.md>) | — | [Étape 25 — Recall@k](<../05-RAG/25-RAG-Formule-Recall-at-k.md>) | [à refaire sur A4](<../Demonstrations/04-Recherche/13_rappel.md>) |
| [14 — Score F1](<04-Recherche/14_score_f1.md>) | — | [Étape 50 — Précision, rappel, F1 et KL](<../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>) | [à refaire sur A4](<../Demonstrations/04-Recherche/14_score_f1.md>) |
| [24 — TF-IDF](<04-Recherche/24_tfidf.md>) | — | [Étape 22 — BM25](<../05-RAG/22-RAG-Formule-BM25.md>) | [à refaire sur A4](<../Demonstrations/04-Recherche/24_tfidf.md>) |
| [25 — Reciprocal Rank Fusion](<04-Recherche/25_rrf.md>) | — | [Étape 24 — Reciprocal Rank Fusion](<../05-RAG/24-RAG-Formule-RRF.md>) | [à refaire sur A4](<../Demonstrations/04-Recherche/25_rrf.md>) |
| [26 — NDCG](<04-Recherche/26_ndcg.md>) | — | [Étape 28 — NDCG](<../05-RAG/28-RAG-Formule-NDCG.md>) | [à refaire sur A4](<../Demonstrations/04-Recherche/26_ndcg.md>) |
| [33 — MRR (Mean Reciprocal Rank)](<04-Recherche/33_mrr.md>) | — | [Étape 27 — MRR](<../05-RAG/27-RAG-Formule-MRR.md>) | [à refaire sur A4](<../Demonstrations/04-Recherche/33_mrr.md>) |

### 05-Contexte

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [15 — Budget de contexte](<05-Contexte/15_budget_contexte.md>) | — | [Étape 13 ter — Ingénierie du contexte](<../04-Contexte-Similarite-et-Memoire/13c-Contexte-Definitions-Fondamentaux.md>) | [à refaire sur A4](<../Demonstrations/05-Contexte/15_budget_contexte.md>) |
| [27 — Score de mémoire](<05-Contexte/27_score_memoire.md>) | — | [Étape 16 — Décroissance d'un souvenir](<../04-Contexte-Similarite-et-Memoire/16-Memoire-Formule-Decroissance-Temporelle.md>) | [à refaire sur A4](<../Demonstrations/05-Contexte/27_score_memoire.md>) |

### 06-Decision

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [09 — Équation de Bellman](<06-Decision/09_equation_bellman.md>) | [09a en images](<06-Decision/09a_bellman_en_images.md>), [09b](<06-Decision/09b_equation_bellman_affiche.md>), [09c terminale](<06-Decision/09c_bellman_terminale.md>), [09d espérance](<06-Decision/09d_bellman_esperance.md>), [09e optimalité](<06-Decision/09e_bellman_optimalite.md>), [09f retour attendu](<06-Decision/09f_retour_attendu.md>) | [Étape 38 — MDP et équation de Bellman](<../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>) | [à refaire sur A4](<../Demonstrations/06-Decision/09_equation_bellman.md>) |
| [10 — Utilité espérée d'une action](<06-Decision/10_utilite_esperee.md>) | [10a EU](<06-Decision/10a_utilite_esperee_eu.md>), [10b terminale](<06-Decision/10b_utilite_esperee_terminale.md>) | [Étape 38 — MDP et équation de Bellman](<../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>) | [à refaire sur A4](<../Demonstrations/06-Decision/10_utilite_esperee.md>) |
| [18 — Q-learning](<06-Decision/18_q_learning.md>) | [18a](<06-Decision/18a_q_learning_affiche.md>), [18b](<06-Decision/18b_q_learning_regle.md>) | [Étape 38 — MDP et équation de Bellman](<../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>) | [à refaire sur A4](<../Demonstrations/06-Decision/18_q_learning.md>) |
| [19 — REINFORCE](<06-Decision/19_reinforce.md>) | [19a avantage](<06-Decision/19a_fonction_avantage.md>), [19b gradient de politique](<06-Decision/19b_gradient_politique_reinforce.md>) | [Étape 38 — MDP et équation de Bellman](<../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>) | [à refaire sur A4](<../Demonstrations/06-Decision/19_reinforce.md>) |
| [22 — Espérance](<06-Decision/22_esperance.md>) | — | [Étape 1 — L'agent et la fiabilité composée](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>) | [à refaire sur A4](<../Demonstrations/06-Decision/22_esperance.md>) |
| [28 — Valeur de l'information](<06-Decision/28_valeur_information.md>) | — | [Étape 38 — MDP et équation de Bellman](<../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>) | [à refaire sur A4](<../Demonstrations/06-Decision/28_valeur_information.md>) |

### 07-Mesure

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [07 — Théorème de Bayes](<07-Mesure/07_theoreme_bayes.md>) | [07a en images](<07-Mesure/07a_bayes_en_images.md>), [07b](<07-Mesure/07b_theoreme_bayes_affiche.md>), [07c anglais](<07-Mesure/07c_bayes_theorem.md>), [07d terminale](<07-Mesure/07d_bayes_terminale.md>) | [Étape 51 — Spécificité, NPV, AUC](<../10-Evaluation/51-Specificite-NPV-AUC.md>) | [à refaire sur A4](<../Demonstrations/07-Mesure/07_theoreme_bayes.md>) |
| [17 — Divergence KL](<07-Mesure/17_divergence_kl.md>) | [17a](<07-Mesure/17a_divergence_kl_affiche.md>), [17b terminale](<07-Mesure/17b_divergence_kl_terminale.md>), [17c RLHF](<07-Mesure/17c_divergence_kl_rlhf.md>) | [Étape 50 — Précision, rappel, F1 et KL](<../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>) | [à refaire sur A4](<../Demonstrations/07-Mesure/17_divergence_kl.md>) |
| [20 — Score de Brier](<07-Mesure/20_score_brier.md>) | — | [Étape 51 — Spécificité, NPV, AUC](<../10-Evaluation/51-Specificite-NPV-AUC.md>) | [à refaire sur A4](<../Demonstrations/07-Mesure/20_score_brier.md>) |
| [21 — Entropie](<07-Mesure/21_entropie.md>) | [21a en images](<07-Mesure/21a_entropie_en_images.md>), [21b Shannon](<07-Mesure/21b_entropie_shannon.md>), [21c terminale](<07-Mesure/21c_entropie_shannon_terminale.md>), [21d exploration](<07-Mesure/21d_entropie_exploration.md>) | [Étape 52 — Perplexité](<../10-Evaluation/52-Perplexite-LLM.md>) | [à refaire sur A4](<../Demonstrations/07-Mesure/21_entropie.md>) |

### 08-Entrainement

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [08 — Descente de gradient](<08-Entrainement/08_descente_de_gradient.md>) | [08a en images](<08-Entrainement/08a_descente_gradient_en_images.md>), [08b](<08-Entrainement/08b_descente_gradient_ia_agentique.md>), [08c anglais](<08-Entrainement/08c_gradient_descent.md>), [08d terminale](<08-Entrainement/08d_descente_gradient_terminale.md>), [08e optimisation](<08-Entrainement/08e_descente_gradient_optimisation.md>) | [Étape 73 — Descente de gradient et LoRA](<../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>) | [à refaire sur A4](<../Demonstrations/08-Entrainement/08_descente_de_gradient.md>) |
| [31 — Adam](<08-Entrainement/31_adam.md>) | — | [Étape 74 — Optimiseur Adam](<../12-Production-Couts-Optimisation/74-Optimiseur-Adam.md>) | [à refaire sur A4](<../Demonstrations/08-Entrainement/31_adam.md>) |
| [34 — Gradient](<08-Entrainement/34_gradient.md>) | [34a règle de la chaîne](<08-Entrainement/34a_regle_de_la_chaine.md>), [34b le schéma](<08-Entrainement/34b_regle_chaine_schema.md>) | [Étape 73 — Descente de gradient et LoRA](<../12-Production-Couts-Optimisation/73-Optimisation-et-Fine-Tuning.md>) | [à refaire sur A4](<../Demonstrations/08-Entrainement/34_gradient.md>) |

### 09-Production

| Fiche | Autres affiches de la même formule | Étape du cours | Démonstrations |
| --- | --- | --- | --- |
| [16 — Coût d'inférence](<09-Production/16_cout_inference.md>) | — | [Étape 72 — Coûts et gestion des tokens](<../12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md>) | [à refaire sur A4](<../Demonstrations/09-Production/16_cout_inference.md>) |
