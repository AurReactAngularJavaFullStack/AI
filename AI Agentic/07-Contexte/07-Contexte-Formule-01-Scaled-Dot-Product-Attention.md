# 07-Contexte — Formule 01 — Scaled Dot-Product Attention

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  

**Nom du fichier :** 07-Contexte-Formule-01-Scaled-Dot-Product-Attention.md

## Définition complète de chaque élément de la formule

La formule du Scaled Dot-Product Attention est fondamentale pour comprendre comment les LLM gèrent le contexte dans tes agents. Elle détermine quelles parties du prompt, de l’historique ou des documents récupérés reçoivent le plus d’attention.

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V
$$


### Définition détaillée de chaque symbole

- \(Q\) (Query) : la matrice des requêtes. Chaque ligne représente ce que le modèle cherche à un moment donné dans le contexte. Plus une query est proche d’une key, plus elle « attire » l’attention vers cette partie du texte.

- \(K\) (Key) : la matrice des clés. Chaque ligne représente un élément disponible dans le contexte (un token, un chunk, un message précédent).

- \(V\) (Value) : la matrice des valeurs. C’est l’information concrète qui sera pondérée et mélangée. Sans V, on n’aurait que des scores, pas de contenu.

- \(d_k\) : la dimension des vecteurs query et key. Plus \(d_k\) est élevé, plus le risque de saturation du softmax augmente si on ne scale pas.

- \(Q K^\top\) : produit matriciel qui calcule tous les scores de similarité bruts entre queries et keys.

- $$
  \sqrt{d_k}
  $$

   : facteur de scaling critique. Sans lui, les scores deviennent trop grands, le softmax produit des valeurs extrêmes (presque 0 ou 1), et le modèle ne peut plus apprendre de nuances fines.

- $$
  \operatorname{softmax}
  $$

   : normalise les scores en probabilités (chaque ligne somme à 1). Plus un score est élevé relativement aux autres, plus son poids se rapproche de 1.

- Le résultat est une combinaison pondérée des values selon ces poids d’attention.

### Comportement quand les valeurs changent

- Plus \(d_k\) augmente sans le facteur \(\sqrt{d_k}\), plus les scores explosent et le softmax sature → le modèle se concentre de manière trop exclusive sur un seul élément et perd la capacité à combiner des informations.
- Plus un score particulier (après scaling) est grand par rapport aux autres, plus le poids correspondant se rapproche de 1 et les autres de 0 → concentration forte sur une partie du contexte.
- Si tous les scores sont proches, les poids deviennent uniformes → mélange équilibré de tout le contexte.

## Code Python complet

```python
import numpy as np

def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / e_x.sum(axis=-1, keepdims=True)

def scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
    d_k = Q.shape[-1]
    scores = (Q @ K.T) / np.sqrt(d_k)
    weights = softmax(scores)
    return weights @ V

# Exemple
Q = np.array([[1.0, 0.0]])
K = np.array([[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]])
V = K.copy()
print(scaled_dot_product_attention(Q, K, V))
```

## Cas d’usage métier détaillés (maximum)

**1. Finance / Banque (Banque de France, trading, conformité)**  
Un agent qui analyse un long historique de transactions et de rapports réglementaires. L’attention permet au modèle de se concentrer sur les passages critiques (seuils de risque, dates de reporting) plutôt que de diluer l’information dans des centaines de pages. Si l’attention se disperse trop, l’agent peut rater une obligation de déclaration.

**2. Immobilier**  
Agent qui aide à l’estimation ou à la rédaction d’annonces. Le contexte contient des dizaines de caractéristiques (surface, DPE, travaux, comparables de marché). L’attention permet de pondérer fortement les éléments les plus déterminants pour le prix (localisation + état) plutôt que des détails secondaires.

**3. Crypto / DeFi**  
Agent qui surveille des smart contracts ou des whitepapers longs. Il doit « faire attention » aux clauses de liquidité, aux risques de rug-pull ou aux mécanismes de gouvernance. Une mauvaise gestion d’attention peut faire ignorer une phrase critique sur les droits des tokens.

**4. Bancaire / Crédit**  
Dans un processus d’octroi de crédit, l’agent analyse un dossier client long (revenus, historique, garanties). L’attention se concentre sur les ratios d’endettement et les incidents de paiement. Trop de dispersion = risque de sous-estimer un signal d’alerte.

**5. Assurance (ton projet auto)**  
Conversation longue avec l’assuré + documents de contrat. L’attention doit rester forte sur les clauses de franchise et de plafond même après de nombreux échanges. Sinon l’agent « oublie » une condition importante.

**6. RH multi-pays (StaffMind)**  
Onboarding long avec documents fiscaux, contrats, exceptions. L’attention permet de ne pas perdre une information sur le statut fiscal double au milieu de la conversation.

**7. BTP / Facturation (VerifactureBTP)**  
Contexte contenant des marchés publics, des normes et des exemples de factures. L’attention aide à extraire les mentions légales obligatoires sans se noyer dans le reste.

Ces exemples montrent que la formule n’est pas abstraite : elle explique concrètement pourquoi certains agents « oublient » des informations critiques dans des domaines réglementés ou à fort enjeu financier.
