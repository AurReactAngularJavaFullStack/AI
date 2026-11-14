# Fiche 02 — Norme L2

> Image : `02_norme_L2.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)

**Longueur d'un vecteur**

## Formule

$$
\lVert x \rVert = \sqrt{x_1^2 + x_2^2 + \dots + x_d^2} = \sqrt{x \cdot x}
$$

## Éléments

$$
x
$$

**x** : le vecteur.

$$
x_i
$$

**xᵢ** : chaque coordonnée.

$$
x_i^2
$$

**xᵢ²** : la coordonnée mise au carré. Le carré efface le signe.

$$
\lVert x \rVert
$$

**‖x‖** : la longueur euclidienne du vecteur, toujours positive ou nulle. C'est le théorème de Pythagore en d dimensions.

## Ce que c'est

La norme L2 mesure la magnitude d'un vecteur, pas son sens. Deux vecteurs de même direction peuvent avoir des longueurs très différentes. Diviser un vecteur par sa norme donne un vecteur de longueur 1 dans la même direction : c'est la normalisation.

## Effets et impacts

- Elle sert à normaliser les embeddings avant une recherche. Une fois normalisés, cosinus et produit scalaire donnent le même classement.
- Un vecteur nul a une norme nulle : le cosinus devient indéfini, car on diviserait par zéro.
- Une norme instable (des embeddings de longueurs très variables) fausse les scores de similarité et le classement.

## Exemple chiffré

$$
x = [3\ ;\ 4] \quad\Longrightarrow\quad \lVert x \rVert = \sqrt{9 + 16} = \sqrt{25} = 5
$$

Normaliser x, c'est le diviser par sa norme :

$$
\hat{x} = \frac{x}{\lVert x \rVert} = [0{,}6\ ;\ 0{,}8], \qquad \lVert \hat{x} \rVert = \sqrt{0{,}36 + 0{,}64} = 1
$$

**x̂ (x chapeau)** : le vecteur unitaire de même direction que x.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`norme_l2(x)`** — Cette fonction mesure un vecteur comme un arpenteur mesure la diagonale d'un terrain : il élève au carré chaque côté, additionne, puis prend la racine, à la manière de Pythagore. Elle reçoit la liste des coordonnées, additionne le carré de chacune et rend la racine carrée de cette somme, calculée par `math.sqrt`. Elle ne lève aucune exception et ne dit rien de la direction, seulement de la longueur : pour x = [3 ; 4], elle rend √(9 + 16) = 5, et pour le vecteur normalisé elle rend 1.

**`normaliser(x)`** — Celle-ci est le tailleur qui ramène toutes les flèches à la même longueur sans changer l'endroit où elles pointent. Elle reçoit un vecteur, calcule sa norme avec `norme_l2`, lève `ValueError` si cette norme est nulle, puisqu'un vecteur nul n'a pas de direction, puis rend la liste des coordonnées divisées par la norme. Pour x = [3 ; 4], elle rend [0,6 ; 0,8], un vecteur unitaire de même direction ; c'est l'opération qui rend cosinus et produit scalaire équivalents pour classer des embeddings.

**`main()`** — C'est le vérificateur qui repasse l'exemple de la fiche et tente même une manœuvre interdite. Il ne reçoit rien ; il normalise x = [3 ; 4], imprime la norme 5, le vecteur [0,6 ; 0,8] et la norme 1 du vecteur normalisé, puis contrôle ces trois valeurs par `assert`. Il essaie ensuite de normaliser le vecteur nul et lève une `AssertionError` si aucune `ValueError` n'est venue ; il annonce enfin que toutes les vérifications sont passées et ne rend rien.

```python
"""Fiche 02 — norme L2 : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def norme_l2(x: list[float]) -> float:
    """‖x‖ = √(x₁² + x₂² + … + x_d²)."""
    return math.sqrt(sum(v * v for v in x))


def normaliser(x: list[float]) -> list[float]:
    """x̂ = x / ‖x‖ ; refusé pour le vecteur nul, qui n'a pas de direction."""
    n = norme_l2(x)
    if n == 0:
        raise ValueError("vecteur nul : impossible de normaliser")
    return [v / n for v in x]


def main() -> None:
    x = [3.0, 4.0]
    xh = normaliser(x)
    print(f"‖x‖ = {norme_l2(x):.0f}   x̂ = {[round(v, 2) for v in xh]}   ‖x̂‖ = {norme_l2(xh):.0f}")
    assert norme_l2(x) == 5 and [round(v, 2) for v in xh] == [0.6, 0.8] and math.isclose(norme_l2(xh), 1)
    try:
        normaliser([0.0, 0.0])
        raise AssertionError("le vecteur nul aurait dû être refusé")
    except ValueError:
        pass
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
‖x‖ = 5   x̂ = [0.6, 0.8]   ‖x̂‖ = 1
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`norme_l2` élève chaque coordonnée au carré, ce qui efface son signe, additionne ces carrés puis prend la racine carrée de la somme : c'est le théorème de Pythagore étendu à d dimensions, et pour le vecteur [3 ; 4] il donne √(9 + 16) = 5. Le résultat est toujours positif ou nul, et il n'est nul que pour le vecteur dont toutes les coordonnées valent zéro.

`normaliser` divise chaque coordonnée par la norme, ce qui produit un vecteur de même direction mais de longueur 1 : [3 ; 4] devient [0,6 ; 0,8], et le programme vérifie que la norme de ce nouveau vecteur vaut bien 1. Avant de diviser, la fonction refuse le vecteur nul en levant une `ValueError`, parce qu'une division par zéro n'aurait pas de sens et qu'un vecteur nul n'a de toute façon aucune direction à conserver. La dernière vérification du programme s'assure que ce refus a bien lieu : si la fonction acceptait le vecteur nul, l'`AssertionError` arrêterait le programme.

## Squelette algorithmique

```text
ALGORITHME Normaliser
ENTRÉE  : x, vecteur de dimension d
SORTIE  : x̂ de même direction et de norme 1

  somme ← 0
  POUR i DE 1 À d FAIRE  somme ← somme + xᵢ²  FIN POUR
  n ← √somme
  SI n = 0 ALORS ERREUR « vecteur nul »
  POUR i DE 1 À d FAIRE  x̂ᵢ ← xᵢ / n  FIN POUR
  RETOURNER x̂
```

**Complexité.** Deux passes sur les d coordonnées : O(d) en temps. On normalise les embeddings une seule fois, à l'indexation, ce qui évite ce calcul à chaque requête.

**Du squelette au code.** La première boucle et la racine forment `norme_l2`, la garde et la seconde boucle forment `normaliser`.

## Dans le cours

- [Étape 14 — Produit scalaire, norme, cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>)
- [Étape 20 — Distance euclidienne](<../../05-RAG/20-RAG-Formule-Distance-Euclidienne.md>)
- [Étape 28 bis — Théorèmes du cosinus et des métriques de classement](<../../05-RAG/28b-Theoremes-Cosinus-et-Metriques-de-Classement.md>)
