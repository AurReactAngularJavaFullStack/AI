# Fiche 03 — Similarité cosinus

> Image : `03_similarite_cosinus.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)

**Même direction, quelle que soit la longueur**

## Formule

$$
\cos(x, y) = \frac{x \cdot y}{\lVert x \rVert \times \lVert y \rVert}
$$

## Éléments

$$
x \cdot y
$$

**x · y** : le produit scalaire (fiche 01).

$$
\lVert x \rVert,\ \lVert y \rVert
$$

**‖x‖ et ‖y‖** : les normes L2 (fiche 02).

$$
\theta
$$

**θ (thêta)** : l'angle entre les deux vecteurs. Le cosinus de cet angle est la similarité.

$$
-1 \le \cos(x, y) \le 1
$$

**Le résultat est compris entre −1 et 1** (inégalité de Cauchy–Schwarz, démontrée à l'étape 28 bis). 1 : même sens. 0 : orthogonaux. −1 : sens opposés.

## Ce que c'est

Elle compare l'orientation de deux vecteurs et ignore leur échelle. C'est la mesure centrale du RAG et de la mémoire sémantique : la question et chaque passage sont encodés, et on garde les passages dont le cosinus avec la question est le plus haut.

## Effets et impacts

- Elle classe les passages proches d'une question et sert à dédupliquer la mémoire (deux souvenirs de cosinus proche de 1 disent la même chose).
- Un score de 0,8 n'est pas « 80 % de chances » : c'est un angle, pas une probabilité.
- Les scores ne se comparent pas entre deux modèles d'embeddings différents : chacun a sa propre distribution.
- Le vecteur nul rend la formule indéfinie.

## Exemple chiffré

Avec les vecteurs de la fiche 01 :

$$
\lVert x \rVert = \sqrt{0{,}98} \approx 0{,}98995, \qquad \lVert y \rVert = \sqrt{1{,}01} \approx 1{,}00499
$$

$$
\cos(x, y) = \frac{0{,}98}{0{,}98995 \times 1{,}00499} \approx 0{,}98504
$$

Et avec 2x à la place de x : le numérateur et la norme de x doublent tous les deux, le facteur 2 se simplifie, et le cosinus reste 0,98504. La longueur a disparu.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(x, y)`** — Cette fonction se comporte comme un navigateur qui compare deux caps sur sa boussole sans se soucier de la vitesse des navires : seule compte la direction de chaque flèche. Elle reçoit deux vecteurs, lève `ValueError` s'ils n'ont pas la même dimension, calcule leur produit scalaire puis la norme de chacun, lève une seconde `ValueError` si l'une des normes est nulle, et rend le produit scalaire divisé par le produit des normes, un nombre entre −1 et 1. Pour la question et le passage de la fiche, elle rend environ 0,98504 : les deux vecteurs pointent presque dans le même sens.

**`main()`** — C'est l'examinateur qui vérifie la boussole sur trois relevés. Il ne reçoit rien ; il calcule le cosinus de l'exemple de cette fiche, celui de [1 ; 0] et [1 ; 1], commun aux fiches 03a et 03b, puis celui de [2 ; 0] et [1 ; 1], où le premier vecteur est doublé. Il imprime 0,98504, 0,707107 et encore 0,707107, puis vérifie par `assert` la première valeur à 10⁻⁵ près, l'égalité de la deuxième avec 1/√2 et avec la troisième, l'angle de 45° obtenu par l'arc cosinus et l'appartenance à [−1, 1] ; il ne rend rien.

```python
"""Fiches 03, 03a, 03b — similarité cosinus : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cosinus(x: list[float], y: list[float]) -> float:
    """cos(x, y) = (x · y) / (‖x‖ × ‖y‖)."""
    if len(x) != len(y):
        raise ValueError("dimensions différentes")
    produit = sum(a * b for a, b in zip(x, y))
    nx = math.sqrt(sum(a * a for a in x))
    ny = math.sqrt(sum(b * b for b in y))
    if nx == 0 or ny == 0:
        raise ValueError("cosinus non défini pour un vecteur nul")
    return produit / (nx * ny)


def main() -> None:
    c1 = cosinus([0.8, 0.3, 0.5], [0.7, 0.4, 0.6])          # fiche 03
    c2 = cosinus([1.0, 0.0], [1.0, 1.0])                    # fiches 03a et 03b
    c3 = cosinus([2.0, 0.0], [1.0, 1.0])                    # x doublé
    print(f"fiche 03 : {c1:.5f}   fiches 03a/03b : {c2:.6f} (45°)   x doublé : {c3:.6f}")
    assert math.isclose(c1, 0.98504, abs_tol=1e-5)
    assert math.isclose(c2, 1 / math.sqrt(2)) and math.isclose(c2, c3)
    assert math.isclose(math.degrees(math.acos(c2)), 45)
    assert -1 <= c1 <= 1
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
fiche 03 : 0.98504   fiches 03a/03b : 0.707107 (45°)   x doublé : 0.707107
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`cosinus` vérifie d'abord que les deux vecteurs ont la même dimension, puis calcule trois sommes : le produit scalaire (somme des produits de coordonnées de même rang) et les deux normes (racines des sommes de carrés). Elle refuse ensuite le vecteur nul, parce que sa norme vaut zéro et que la division n'aurait pas de sens, et renvoie enfin le produit scalaire divisé par le produit des normes. Diviser par les normes retire toute information de longueur : il ne reste que l'angle entre les deux vecteurs.

`main` vérifie les deux exemples des fiches. Avec les vecteurs de la fiche 03, le cosinus vaut 0,98504, ce qui indique deux vecteurs presque alignés. Avec x = (1, 0) et y = (1, 1), l'exemple des fiches 03a et 03b, il vaut 1 / √2 ≈ 0,707107, et le programme convertit ce cosinus en angle avec `acos` pour retrouver 45 degrés. Il double ensuite x et vérifie que le cosinus ne change pas, puis que le résultat reste bien entre −1 et 1, comme le garantit l'inégalité de Cauchy–Schwarz démontrée à l'étape 28 bis.

## Squelette algorithmique

```text
ALGORITHME SimilaritéCosinus
ENTRÉES : x et y, deux vecteurs de dimension d
SORTIE  : cos(x, y) dans [−1 ; 1]

  SI longueur(x) ≠ longueur(y) ALORS ERREUR
  produit ← Σᵢ xᵢ × yᵢ
  nx ← √(Σᵢ xᵢ²)        ny ← √(Σᵢ yᵢ²)
  SI nx = 0 OU ny = 0 ALORS ERREUR « vecteur nul »
  RETOURNER produit / (nx × ny)

USAGE EN RAG : calculer cos(question, document) pour chaque document, trier par score décroissant, garder les k premiers.
```

**Complexité.** O(d) pour un couple de vecteurs. Classer n documents coûte O(n × d) pour les scores et O(n log n) pour le tri ; si les vecteurs sont normalisés à l'avance, le cosinus se réduit au produit scalaire et les normes ne sont plus recalculées.

**Du squelette au code.** Chaque ligne du squelette est une ligne de `cosinus` : la garde de dimension, le produit, les deux normes, la garde du vecteur nul et la division finale.

## Dans le cours

- [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)
- [Étape 19 — Similarité cosinus](<../../05-RAG/19-RAG-Formule-Similarite-Cosinus.md>)
- [Étape 28 bis — Théorèmes du cosinus et des métriques de classement](<../../05-RAG/28b-Theoremes-Cosinus-et-Metriques-de-Classement.md>)
