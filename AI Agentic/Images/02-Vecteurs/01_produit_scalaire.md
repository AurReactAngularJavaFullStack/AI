# Fiche 01 — Produit scalaire

> Image : `01_produit_scalaire.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)

**Alignement de deux vecteurs**

## Formule

$$
x \cdot y = x_1 y_1 + x_2 y_2 + \dots + x_d y_d = \sum_{i=1}^{d} x_i \, y_i
$$

## Éléments

$$
x,\ y
$$

**x et y** : deux vecteurs, souvent des embeddings (une question encodée, un passage encodé).

$$
x_i,\ y_i
$$

**xᵢ et yᵢ** : la coordonnée numéro i de chaque vecteur.

$$
d
$$

**d** : le nombre de dimensions de l'embedding (384, 768, 1 536, 3 072 selon le modèle).

$$
\sum_{i=1}^{d}
$$

**Σ (sigma)** : la somme pour i allant de 1 à d.

$$
x \cdot y
$$

**x · y** : le produit scalaire, une somme de produits. Le résultat est un seul nombre.

## Ce que c'est

Il mesure à quel point deux vecteurs pointent ensemble. Plus le score est élevé, plus ils sont alignés. Mais la longueur des vecteurs compte aussi : à direction égale, un vecteur deux fois plus long donne un score deux fois plus grand. C'est pour retirer cet effet de longueur qu'on passe ensuite à la similarité cosinus (fiche 03).

## Effets et impacts

- Il calcule les scores de l'attention, le classement d'un RAG et les projections d'un réseau de neurones.
- Un score élevé n'est pas une probabilité : il n'est pas borné entre 0 et 1.
- Sans normalisation, un vecteur long peut dominer un vecteur mieux orienté.

## Exemple chiffré

Une question et un passage, encodés en 3 dimensions :

$$
x = [0{,}8\ ;\ 0{,}3\ ;\ 0{,}5], \qquad y = [0{,}7\ ;\ 0{,}4\ ;\ 0{,}6]
$$

$$
x \cdot y = 0{,}8 \times 0{,}7 + 0{,}3 \times 0{,}4 + 0{,}5 \times 0{,}6 = 0{,}56 + 0{,}12 + 0{,}30 = 0{,}98
$$

On double la longueur de x sans changer sa direction :

$$
(2x) \cdot y = 2 \times 0{,}98 = 1{,}96
$$

Le score double, alors que le sens du texte n'a pas changé. C'est exactement le défaut que corrige le cosinus.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`produit_scalaire(x, y)`** — Cette fonction ressemble à un caissier de marché qui tient deux colonnes côte à côte, les quantités d'un côté, les prix de l'autre, et additionne ligne après ligne quantité fois prix. Elle reçoit deux vecteurs sous forme de listes, lève `ValueError` s'ils n'ont pas la même longueur, plutôt que de laisser `zip` tronquer le plus long en silence, puis parcourt les deux listes en parallèle, multiplie les coordonnées de même rang et ajoute chaque produit à un total parti de zéro. Elle rend ce total, x₁y₁ + x₂y₂ + … : 0,98 pour la question et le passage de la fiche.

**`main()`** — C'est l'inspecteur qui rejoue l'exemple chiffré pour vérifier que l'addition tombe juste. Il ne reçoit rien ; il prend x = [0,8 ; 0,3 ; 0,5] et y = [0,7 ; 0,4 ; 0,6], calcule leur produit scalaire, puis celui de 2x avec y, imprime les deux scores 0,98 et 1,96 et vérifie par `assert`, avec `math.isclose`, que le premier vaut 0,98 et que le second en est exactement le double. Il annonce enfin que les vérifications sont passées et ne rend rien : la démonstration montre que doubler la longueur d'un vecteur double le score, défaut que corrigera le cosinus.

```python
"""Fiche 01 — produit scalaire : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def produit_scalaire(x: list[float], y: list[float]) -> float:
    """x · y = x₁y₁ + x₂y₂ + … + x_d y_d."""
    if len(x) != len(y):
        raise ValueError("les deux vecteurs doivent avoir la même dimension")
    total = 0.0
    for xi, yi in zip(x, y):
        total += xi * yi
    return total


def main() -> None:
    x, y = [0.8, 0.3, 0.5], [0.7, 0.4, 0.6]
    s = produit_scalaire(x, y)
    s2 = produit_scalaire([2 * v for v in x], y)
    print(f"x · y = {s:.2f}   (2x) · y = {s2:.2f}")
    assert math.isclose(s, 0.98) and math.isclose(s2, 2 * s)
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
x · y = 0.98   (2x) · y = 1.96
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

La fonction `produit_scalaire` commence par comparer les longueurs des deux listes : un produit scalaire n'existe qu'entre deux vecteurs de même dimension, et sans cette garde la fonction `zip` couperait silencieusement le vecteur le plus long, ce qui donnerait un nombre faux sans aucun message d'erreur. Elle parcourt ensuite les deux vecteurs en parallèle, coordonnée par coordonnée, multiplie les deux coordonnées de même rang et ajoute ce produit à un total qui part de zéro : c'est exactement la somme x₁y₁ + x₂y₂ + … + x_d y_d de la formule, écrite sous forme de boucle pour que chaque terme soit visible.

`main` reprend l'exemple chiffré de la fiche. Avec x = [0,8 ; 0,3 ; 0,5] et y = [0,7 ; 0,4 ; 0,6], les trois produits valent 0,56, 0,12 et 0,30, et leur somme 0,98. Le programme double ensuite chaque coordonnée de x sans changer sa direction et vérifie que le score double lui aussi : c'est la propriété qui rend le produit scalaire sensible à la longueur des vecteurs, et qui justifie de passer au cosinus quand seule la direction compte.

## Squelette algorithmique

```text
ALGORITHME ProduitScalaire
ENTRÉES : x et y, deux vecteurs de dimension d
SORTIE  : le nombre x · y

  SI longueur(x) ≠ longueur(y) ALORS ERREUR « dimensions différentes »
  total ← 0
  POUR i DE 1 À d FAIRE
      total ← total + xᵢ × yᵢ
  FIN POUR
  RETOURNER total
```

**Complexité.** Une seule passe sur les d coordonnées : O(d) multiplications et additions, O(1) en mémoire supplémentaire. Pour comparer une question à n documents, on répète ce calcul n fois : O(n × d).

**Du squelette au code.** La garde correspond au `if len(x) != len(y)`, la variable `total` à l'accumulateur, et la boucle `POUR` à la boucle `for xi, yi in zip(x, y)` de `produit_scalaire`.

## Dans le cours

- [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)
- [Étape 28 bis — Théorèmes du cosinus et des métriques de classement](<../../05-RAG/28b-Theoremes-Cosinus-et-Metriques-de-Classement.md>)
- [Étape 31 — Attention par produit scalaire normalisé](<../../06-Attention-et-Transformer/31-Attention-Formule-Produit-Scalaire-Normalise.md>)
