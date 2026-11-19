# Processus vertical — classes 1 à 6

> Image : `02_processus_vertical_fondations.jpg` · Lire de haut en bas. Formules corrigées : [sommaire](<00_Sommaire.md>).

## Ce que montre l'image

Six classes UML empilées. La flèche vers le bas veut dire « ensuite seulement ».

| Classe | Formule qui fait foi | Pourquoi elle est ici |
| --- | --- | --- |
| 1. Espérance | 𝔼[X] = Σᵢ xᵢ P(xᵢ) | Tout coût moyen et toute utilité ultérieure sont cette somme. Étape 1. |
| 2. Fiabilité | P = ∏ᵢ pᵢ | L'agent est une chaîne. Ajouter une étape ne peut pas augmenter ce produit. Étape 1. |
| 3. Softmax | P(i) = exp(zᵢ/T) / Σⱼ exp(zⱼ/T) | Avant les prompts : les tokens jugés en sortent. T → 0 est un argmax. Étape 2. |
| 4. Vraisemblance | P(x) = ∏ₜ P(xₜ ∣ x₁ … xₜ₋₁) | La phrase est le produit des softmax successives. Étape 3. |
| 5. Budget | jetons admis ≤ fenêtre | On choisit ce qui entre avant de remplir. Étape 13 ter. |
| 6. Vecteurs | scalaire, norme L2, cosinus | Une fois, avant la mémoire et le RAG. Le cosinus compare la direction. Étape 14. |

La suite est [les classes 7 à 12](<03_processus_vertical_recherche.md>).
