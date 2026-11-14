# Fiche 03b_similarite_cosinus_terminale — Similarité cosinus, niveau terminale

> Image : `03b_similarite_cosinus_terminale.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)

**Le cosinus lu comme en terminale : un rapport de longueurs**

## Ce que montre l'image

Fiche de niveau terminale, titrée « Algèbre vectorielle ». La formule, un schéma de A et B avec l'angle θ compris entre 0 et π, puis deux encadrés de calcul en dimension 2 : le produit scalaire en coordonnées (on multiplie les abscisses, on multiplie les ordonnées, on additionne) et la norme (racine de la somme des carrés des coordonnées), avec la mention « se généralise à toute dimension ». En bas, trois usages : comparer une requête aux documents (les plus proches ont un cosinus proche de 1), mémoire vectorielle, chaîne question → base vectorielle → réponse.

**Ce que l'image ajoute à la fiche 03 :** les formules en coordonnées, à refaire à la main en dimension 2 avant de passer en dimension d (voir `Demonstrations/02-Vecteurs/01_produit_scalaire.md`).

**À lire avec prudence :** même remarque que pour 03a, « vecteurs identiques » signifie « même direction ».

## Formule

$$
\cos(x, y) = \frac{x \cdot y}{\|x\| \,\|y\|}
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
-1 \le \cos(x, y) \le 1
$$

**Le résultat est compris entre −1 et 1.** 1 : même sens. 0 : orthogonaux. −1 : sens opposés.

## Ce que c'est

La version terminale nomme le cosinus comme le rapport entre le produit scalaire et le produit des longueurs. Même objet que la fiche 03, symboles détaillés un par un.

## Effets et impacts

- Sur des vecteurs déjà de norme 1, le cosinus et le produit scalaire classent de la même façon.
- Le classement d'un RAG se fait avec ce nombre, puis on coupe un top-k.

## Exemple chiffré

$$
x = (1, 0),\quad y = (1, 1)
$$

$$
x \cdot y = 1,\quad \|x\| = 1,\quad \|y\| = \sqrt{2},\quad \cos = 1/\sqrt{2} \approx 0{,}707
$$

Les deux vecteurs sont à 45 degrés. Doubler x ne change pas le cosinus. Un score de 0,8 n'est pas « 80 % de chances ».

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(x, y)`** — Cette fonction agit comme un bibliothécaire qui range deux livres selon leur sujet et non selon leur épaisseur : un pavé et un fascicule qui parlent de la même chose doivent se retrouver côte à côte. Elle reçoit deux vecteurs, refuse par `ValueError` des dimensions différentes, calcule le produit scalaire, puis la longueur de chaque vecteur comme la racine de la somme de ses carrés, refuse par `ValueError` un vecteur de longueur nulle, et rend le rapport du produit scalaire au produit des longueurs. C'est exactement la définition terminale de la fiche : pour x = (1, 0) et y = (1, 1), elle rend 1/√2 ≈ 0,707, et le même nombre pour 2x.

**`main()`** — C'est le correcteur du baccalauréat qui reprend la copie avec trois couples de vecteurs. Il ne reçoit rien ; il calcule le cosinus de l'exemple en trois dimensions de la fiche 03, celui de (1, 0) et (1, 1) étudié ici, et celui de (2, 0) et (1, 1). Il imprime 0,98504, 0,707107 et 0,707107, puis vérifie par `assert` la valeur 0,98504, l'égalité avec 1/√2, l'invariance quand x double, l'angle de 45° retrouvé par `math.acos` et le fait que le cosinus reste entre −1 et 1 ; il ne rend rien et termine par le message de réussite.

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
- [Fiche 03 — Similarité cosinus](<03_similarite_cosinus.md>)
