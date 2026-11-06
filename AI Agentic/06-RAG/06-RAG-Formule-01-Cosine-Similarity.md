# 06-RAG — Formule 01 — Similarité Cosinus

**Dossier :** 06-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  

**Nom du fichier :** 06-RAG-Formule-01-Cosine-Similarity.md

## Définition complète de chaque élément de la formule

La similarité cosinus mesure l’angle entre deux vecteurs d’embeddings. Elle est la métrique la plus utilisée pour le retrieval sémantique dans les systèmes RAG parce qu’elle ne dépend pas de la longueur des vecteurs, uniquement de leur direction.

La formule complète est :

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}}
$$

### Définition de chaque symbole

- $$
  (\theta) (thêta)
  $$

   : l’angle géométrique entre les deux vecteurs \(\mathbf{a}\) et \(\mathbf{b}\). Plus l’angle est petit, plus les deux textes sont sémantiquement proches. Un angle de 0° donne \(\cos = 1\) (identiques), un angle de 90° donne \(\cos = 0\) (aucune relation).

- $$
  (\mathbf{a}) et (\mathbf{b})
  $$

   : les deux vecteurs d’embeddings (requête et document, ou deux documents). Chaque composante \(a_i\) représente une dimension de l’espace sémantique appris par le modèle d’embedding.

- $$
  (\mathbf{a} \cdot \mathbf{b})
  $$

  : le produit scalaire. C’est la somme des produits terme à terme. Plus ce nombre est grand (en valeur absolue), plus les vecteurs pointent dans des directions proches.

- $$
  (\|\mathbf{a}\|)
  $$

   : la norme euclidienne (longueur) du vecteur \(\mathbf{a}\). Elle se calcule par \(\sqrt{\sum a_i^2}\). Plus le vecteur est long, plus cette valeur est grande. La division par les normes rend la mesure indépendante de la magnitude.

- \(n\) : la dimension de l’espace d’embedding (souvent 384, 768, 1536…). Plus \(n\) est grand, plus l’espace peut capturer de nuances, mais le calcul est plus coûteux.

- \(a_i, b_i\) : la i-ème composante de chaque vecteur.

### Comportement quand les valeurs changent

- Plus le produit scalaire augmente (vecteurs plus alignés), plus \(\cos(\theta)\) se rapproche de 1 → documents plus pertinents.
- Plus les normes augmentent sans que le produit scalaire augmente proportionnellement, plus le score diminue (effet de normalisation).
- Si un vecteur devient le vecteur nul, la similarité est définie à 0 (division par zéro évitée).
- Plus la dimension \(n\) augmente avec des composantes bruitées, plus le score peut baisser si le signal utile n’est pas renforcé.

## Démonstration complète avec interprétation

**Vecteurs :**  
$$
\mathbf{q} = [0.8, 0.3, 0.5]\) (requête « choc parking »)
$$
 
$$
\mathbf{d} = [0.7, 0.4, 0.6]\) (clause de contrat)
$$


1. Produit scalaire = 0.8×0.7 + 0.3×0.4 + 0.5×0.6 = 0.98  
   → Les deux vecteurs partagent beaucoup de « direction » commune.

2. $$
   \|\mathbf{q}\| = \sqrt{0.64 + 0.09 + 0.25} = \sqrt{0.98} \approx 0.990
   $$

   

3. $$
   \|\mathbf{d}\| = \sqrt{0.49 + 0.16 + 0.36} = \sqrt{1.01} \approx 1.005
   $$

   

4. $$
   \cos(\theta) = 0.98 / (0.990 × 1.005) \approx 0.985
   $$

   

**Interprétation du résultat :**  
Un score de 0.985 signifie que les deux textes sont extrêmement proches sémantiquement. Dans un système d’assurance, cela justifie de présenter cette clause en priorité à l’agent. Si le score était de 0.3, on considérerait le document comme peu pertinent et on ne le passerait pas au LLM.

## Code Python complet et commenté

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calcule la similarité cosinus.
    Plus le résultat est proche de 1, plus les vecteurs sont alignés.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    dot_product = np.dot(a, b)           # produit scalaire
    norm_a = np.linalg.norm(a)           # ||a||
    norm_b = np.linalg.norm(b)           # ||b||
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))

# Démonstration
q = np.array([0.8, 0.3, 0.5])
d = np.array([0.7, 0.4, 0.6])
score = cosine_similarity(q, d)
print(f"Score : {score:.4f}")
print("Interprétation : score très élevé → documents très pertinents")
```

## Cas d’usage métier

Dans StaffMind ou un projet d’assurance, un score cosinus > 0.85 sur le meilleur chunk permet souvent de décider automatiquement de poursuivre ; en dessous de 0.6, l’agent demande une clarification ou escalade.
