# Étape 19 bis — RAG — Similarité Cosinus (version longue, facultative)

**Dossier :** 05-RAG  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  

**Nom du fichier :** 19b-RAG-Formule-Similarite-Cosinus-Version-Longue.md

## Définition complète de chaque élément de la formule

La similarité cosinus mesure l’angle entre deux vecteurs d’embeddings. Elle est la métrique la plus utilisée pour le retrieval sémantique dans les systèmes RAG parce qu’elle ne dépend pas de la longueur des vecteurs, uniquement de leur direction.

La formule complète est :

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|} = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}}
$$

### Définition de chaque symbole

$$
(\theta) (thêta)
$$

   : l’angle géométrique entre les deux vecteurs 𝐚 et 𝐛. Plus l’angle est petit, plus les deux textes sont sémantiquement proches. Un angle de 0° donne cos = 1 (identiques), un angle de 90° donne cos = 0 (aucune relation).

$$
(\mathbf{a}) et (\mathbf{b})
$$

   : les deux vecteurs d’embeddings (requête et document, ou deux documents). Chaque composante aᵢ représente une dimension de l’espace sémantique appris par le modèle d’embedding.

$$
(\mathbf{a} \cdot \mathbf{b})
$$

  : le produit scalaire. C’est la somme des produits terme à terme. Plus ce nombre est grand (en valeur absolue), plus les vecteurs pointent dans des directions proches.

$$
(\|\mathbf{a}\|)
$$

   : la norme euclidienne (longueur) du vecteur 𝐚. Elle se calcule par √(∑ aᵢ²). Plus le vecteur est long, plus cette valeur est grande. La division par les normes rend la mesure indépendante de la magnitude.

- n : la dimension de l’espace d’embedding (souvent 384, 768, 1536…). Plus n est grand, plus l’espace peut capturer de nuances, mais le calcul est plus coûteux.

- aᵢ, bᵢ : la i-ème composante de chaque vecteur.

### Comportement quand les valeurs changent

- Plus le produit scalaire augmente (vecteurs plus alignés), plus cos(θ) se rapproche de 1 → documents plus pertinents.
- Plus les normes augmentent sans que le produit scalaire augmente proportionnellement, plus le score diminue (effet de normalisation).
- Si un vecteur devient le vecteur nul, la similarité est définie à 0 (division par zéro évitée).
- Plus la dimension n augmente avec des composantes bruitées, plus le score peut baisser si le signal utile n’est pas renforcé.

## Démonstration complète avec interprétation

**Vecteurs :**  

$$
\mathbf{q} = [0.8, 0.3, 0.5] (requête « choc parking »)
$$

$$
\mathbf{d} = [0.7, 0.4, 0.6] (clause de contrat)
$$

1. Produit scalaire = 0.8×0.7 + 0.3×0.4 + 0.5×0.6 = 0.98  
   → Les deux vecteurs partagent beaucoup de « direction » commune.

$$
\|\mathbf{q}\| = \sqrt{0.64 + 0.09 + 0.25} = \sqrt{0.98} \approx 0.990
$$

$$
\|\mathbf{d}\| = \sqrt{0.49 + 0.16 + 0.36} = \sqrt{1.01} \approx 1.005
$$

$$
\cos(\theta) = 0.98 / (0.990 × 1.005) \approx 0.985
$$

**Interprétation du résultat :**  
Un score de 0.985 signifie que les deux textes sont extrêmement proches sémantiquement. Dans un système d’assurance, cela justifie de présenter cette clause en priorité à l’agent. Si le score était de 0.3, on considérerait le document comme peu pertinent et on ne le passerait pas au LLM.

## Code Python complet et commenté

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosine_similarity(a, b)`** — On peut se figurer deux boussoles posées côte à côte, dont on ne compare que la direction des aiguilles et jamais leur taille : la fonction reçoit deux listes de nombres, lève `ValueError` si elles n'ont pas la même longueur, calcule leur produit scalaire en sommant les produits terme à terme, puis la norme de chacune comme la racine de la somme de ses carrés. Si l'une des normes est nulle, elle renvoie 0,0 par convention au lieu de diviser par zéro, puisqu'un vecteur nul ne pointe nulle part ; sinon elle renvoie le produit scalaire divisé par le produit des normes, soit environ 0,985 pour la requête « choc parking » et sa clause de contrat. C'est la seule pièce de calcul du programme, et elle reproduit exactement la formule du haut du fichier.

**`main()`** — Le chef d'orchestre rejoue sur la table le calcul que la démonstration a fait à la main : il pose la requête q = [0,8 ; 0,3 ; 0,5] et la clause d = [0,7 ; 0,4 ; 0,6], demande leur score à `cosine_similarity` et l'imprime avec quatre décimales, 0,9850, suivi d'une phrase d'interprétation. Trois `assert` vérifient ensuite que le produit scalaire vaut bien 0,98, que le score tombe à moins de 0,0005 de 0,985, et qu'un vecteur nul reçoit le score 0 prévu par la convention ; la dernière ligne n'annonce le succès que si ces trois vérifications ont tenu.

```python
"""Étape 19 bis — similarité cosinus, bibliothèque standard uniquement."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Calcule la similarité cosinus.
    Plus le résultat est proche de 1, plus les vecteurs sont alignés.
    """
    if len(a) != len(b):
        raise ValueError("les deux vecteurs doivent avoir la même dimension")
    dot_product = sum(x * y for x, y in zip(a, b))   # produit scalaire
    norm_a = math.sqrt(sum(x * x for x in a))        # ||a||
    norm_b = math.sqrt(sum(y * y for y in b))        # ||b||
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def main() -> None:
    # Démonstration : les nombres calculés à la main plus haut
    q = [0.8, 0.3, 0.5]
    d = [0.7, 0.4, 0.6]
    score = cosine_similarity(q, d)
    print(f"Score : {score:.4f}")
    print("Interprétation : score très élevé → documents très pertinents")
    assert math.isclose(sum(x * y for x, y in zip(q, d)), 0.98)   # produit scalaire
    assert abs(score - 0.985) < 5e-4                              # ≈ 0.985
    assert cosine_similarity([0.0, 0.0, 0.0], d) == 0.0           # vecteur nul : score 0 par convention
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Score : 0.9850
Interprétation : score très élevé → documents très pertinents
OK — toutes les vérifications sont passées.
```

### Comment le code fonctionne

La fonction `cosine_similarity` reçoit deux listes de nombres et commence par vérifier qu'elles ont la même longueur, parce qu'un produit scalaire entre un vecteur de 3 coordonnées et un vecteur de 4 n'a pas de sens : sans cette garde, `zip` couperait silencieusement le plus long. Elle calcule ensuite le produit scalaire avec une somme de produits terme à terme, puis la norme de chaque vecteur comme la racine carrée de la somme des carrés de ses coordonnées. Si l'une des deux normes est nulle, elle renvoie 0 par convention, au lieu de diviser par zéro : un vecteur nul n'a pas de direction, donc il n'est proche de rien. Sinon, elle renvoie le produit scalaire divisé par le produit des normes, ce qui est exactement la formule du haut du fichier.

`main` rejoue le calcul fait à la main dans la démonstration avec q = [0,8 ; 0,3 ; 0,5] et d = [0,7 ; 0,4 ; 0,6]. Les `assert` vérifient le produit scalaire (0,98), le score arrondi (0,985) et le comportement face au vecteur nul. La dernière ligne n'est imprimée que si toutes les vérifications passent, ce qui permet de savoir d'un coup d'œil que les nombres du texte sont justes.

## Squelette algorithmique

```text
ALGORITHME SimilaritéCosinus
ENTRÉES : vecteurs a et b de même dimension n
SORTIE  : cos(a, b) dans [−1 ; 1], ou 0 si l'un des vecteurs est nul

  SI longueur(a) ≠ longueur(b) ALORS ERREUR « dimensions différentes »
  produit ← 0 ; carrés_a ← 0 ; carrés_b ← 0
  POUR i DE 1 À n FAIRE
      produit ← produit + aᵢ × bᵢ
      carrés_a ← carrés_a + aᵢ²
      carrés_b ← carrés_b + bᵢ²
  FIN POUR
  SI carrés_a = 0 OU carrés_b = 0 ALORS RETOURNER 0
  RETOURNER produit / (√carrés_a × √carrés_b)
```

**Complexité.** Une seule passe sur les n coordonnées : O(n) en temps et O(1) en mémoire supplémentaire. Le code Python fait trois passes séparées (produit, norme de a, norme de b), ce qui reste O(n) et se lit plus facilement.

**Du squelette au code.** La garde de dimension, la somme des produits, les deux normes et le cas du vecteur nul sont, dans l'ordre, les lignes de `cosine_similarity`. La décision métier qui suit (poursuivre au-dessus de 0,85, clarifier sous 0,6) est la règle de la section suivante.

## Cas d’usage métier

Dans StaffMind ou un projet d’assurance, un score cosinus > 0.85 sur le meilleur chunk permet souvent de décider automatiquement de poursuivre ; en dessous de 0.6, l’agent demande une clarification ou escalade.
