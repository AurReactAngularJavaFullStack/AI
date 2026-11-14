# Fiche 03a_similarite_cosinus_affiche — Similarité cosinus, affiche

> Image : `03a_similarite_cosinus_affiche.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)

**Même formule que la fiche 03, en affiche**

## Ce que montre l'image

Au centre, la formule cos(θ) = A · B / (‖A‖ ‖B‖), avec le produit scalaire en bleu, les normes en vert, et deux vecteurs A et B partant de O, séparés par l'angle θ. À gauche, les trois valeurs repères : 1 pour la même direction, 0 pour des vecteurs orthogonaux, −1 pour des vecteurs opposés. À droite, quatre usages : recherche de similarité, mémoire sémantique, retrieval de passages, et agents qui retrouvent des stratégies ou des outils déjà utilisés dans des contextes proches. En bas : deux vecteurs sont similaires si leur angle est petit, même s'ils n'ont pas la même longueur.

**Ce que l'image ajoute à la fiche 03 :** l'usage « retrouver une stratégie passée », c'est-à-dire la mémoire procédurale d'un agent.

**À lire avec prudence :** l'affiche écrit « vecteurs identiques » pour cos = 1. Il faut lire « même direction » : (1 ; 1) et (5 ; 5) ont un cosinus de 1 sans être identiques.

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

Cette affiche reprend le cosinus de la fiche 03 : l'orientation de deux vecteurs, sans leur longueur. C'est le score du RAG et de la mémoire.

## Effets et impacts

- Elle classe les passages proches d'une question.
- Elle est indéfinie si un vecteur est nul.
- Deux modèles d'embeddings ne partagent pas la même échelle de scores.

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

**`cosinus(x, y)`** — On peut imaginer deux aiguilles d'horloge plantées au même centre : cette fonction ne regarde pas leur longueur, seulement l'ouverture de l'angle qui les sépare. Elle reçoit deux vecteurs de même dimension, faute de quoi elle lève `ValueError`, additionne les produits des coordonnées de même rang, calcule la longueur de chaque aiguille, refuse par une autre `ValueError` une aiguille de longueur nulle, puis rend le quotient du produit scalaire par le produit des deux longueurs. Pour l'affiche, x = (1, 0) et y = (1, 1) donnent 1 / (1 × √2) ≈ 0,707, l'angle de 45 degrés.

**`main()`** — C'est le régleur qui fait tourner les aiguilles devant témoin. Il ne reçoit rien ; il calcule le cosinus de l'exemple de la fiche 03, puis celui de (1, 0) et (1, 1), le cas de cette affiche, puis celui de (2, 0) et (1, 1), l'aiguille rallongée deux fois. Il imprime 0,98504, 0,707107 et 0,707107, et vérifie par `assert` que la valeur de l'affiche égale 1/√2, qu'elle ne bouge pas quand x double, que son arc cosinus vaut 45° et que les scores restent dans [−1, 1] ; il ne rend rien.

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
