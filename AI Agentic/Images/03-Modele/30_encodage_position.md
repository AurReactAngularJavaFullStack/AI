# Fiche 30 — Encodage de position

> Image : `30_encodage_position.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 35 — Encodage de position](<../../06-Attention-et-Transformer/35-Encodage-de-Position.md>)

**Donner l'ordre à un Transformer**

## Formule

$$
PE(pos, 2i) = \sin\left( \frac{pos}{10000^{2i/d}} \right), \qquad PE(pos, 2i+1) = \cos\left( \frac{pos}{10000^{2i/d}} \right)
$$

## Éléments

$$
pos
$$

**pos** : la place du token dans la séquence.

$$
i
$$

**i** : l'indice de la paire de coordonnées.

$$
d
$$

**d** : la dimension du modèle.

$$
10000
$$

**10000** : la base des fréquences.

$$
\sin,\ \cos
$$

**sin et cos** : une fréquence différente par paire de coordonnées.

## Ce que c'est

L'attention seule ne voit pas l'ordre : elle traite les tokens comme un ensemble (démontré à l'étape 32 bis). L'encodage ajoute une signature de position, additionnée à l'embedding du token. Un décalage de k positions est une rotation dans chaque paire (sin, cos), lisible par le modèle.

## Effets et impacts

- « A a heurté B » n'est pas « B a heurté A ». Sans position, ces phrases se confondent.
- Les fréquences basses portent les longs écarts, les hautes les écarts courts.
- Au-delà des longueurs vues à l'entraînement, l'ordre devient moins fiable.

## Exemple chiffré

Dimension d = 4, position pos = 1. Paire i = 0 (fréquence 1) et paire i = 1 (fréquence 1/100) :

$$
PE(1) = \left[ \sin 1\ ;\ \cos 1\ ;\ \sin 0{,}01\ ;\ \cos 0{,}01 \right] \approx [0{,}841\ ;\ 0{,}540\ ;\ 0{,}010\ ;\ 1{,}000]
$$

La première paire tourne vite d'une position à l'autre, la seconde à peine : chacune distingue des écarts d'une taille différente.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`encodage(pos, d)`** — Cette fonction fabrique pour chaque place d'une phrase une signature d'horloger : un cadran à plusieurs aiguilles, l'une qui tourne très vite, d'autres de plus en plus lentement, si bien que la combinaison de leurs positions ne se répète pas. Elle reçoit la position pos et la dimension d, lève `ValueError` si d est impair, puisque chaque fréquence occupe une paire, puis, pour chaque indice i de 0 à d/2 − 1, calcule l'angle pos / 10000^(2i/d) et ajoute son sinus et son cosinus. Elle rend la liste des d coordonnées : pour pos = 1 et d = 4, environ [0,841 ; 0,540 ; 0,010 ; 1,000].

**`decaler(pe, k, d)`** — Celle-ci est l'horloger qui avance toutes les aiguilles de k crans d'un seul geste, chacune à sa propre vitesse, sans avoir besoin de savoir l'heure qu'il était. Elle reçoit un encodage pe, un décalage k et la dimension d, et pour chaque paire (sin, cos) applique la rotation d'angle k × ωᵢ, avec ωᵢ = 1 / 10000^(2i/d), grâce aux formules d'addition du sinus et du cosinus. Elle rend le nouvel encodage, qui est exactement celui de la position pos + k : c'est ce qui rend un écart de positions lisible par le modèle comme une simple rotation.

**`main()`** — C'est le contrôleur qui vérifie le cadran et le mécanisme d'avance. Il ne reçoit rien ; il calcule l'encodage de la position 1 en dimension 4, l'imprime et vérifie par `assert` les valeurs arrondies [0,841 ; 0,54 ; 0,01 ; 1,0]. Il décale ensuite l'encodage de la position 7, en dimension 8, de 5 positions, vérifie coordonnée par coordonnée, à 10⁻¹² près, qu'il retrouve l'encodage de la position 12, imprime ce constat et ne rend rien.

```python
"""Fiche 30 — encodage de position : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def encodage(pos: int, d: int) -> list[float]:
    """PE(pos, 2i) = sin(pos / 10000^(2i/d)), PE(pos, 2i+1) = cos(pos / 10000^(2i/d))."""
    if d % 2:
        raise ValueError("d doit être pair : une paire (sin, cos) par fréquence")
    pe = []
    for i in range(d // 2):
        angle = pos / 10000 ** (2 * i / d)
        pe += [math.sin(angle), math.cos(angle)]
    return pe


def decaler(pe: list[float], k: int, d: int) -> list[float]:
    """Applique à chaque paire la rotation d'angle k × ωᵢ : on obtient PE(pos + k)."""
    sortie = []
    for i in range(d // 2):
        w = 1 / 10000 ** (2 * i / d)
        s, c = pe[2 * i], pe[2 * i + 1]
        sortie += [s * math.cos(k * w) + c * math.sin(k * w), c * math.cos(k * w) - s * math.sin(k * w)]
    return sortie


def main() -> None:
    pe1 = encodage(1, 4)
    print("PE(1), d = 4 :", [round(x, 3) for x in pe1])
    assert [round(x, 3) for x in pe1] == [0.841, 0.54, 0.01, 1.0]
    assert all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(decaler(encodage(7, 8), 5, 8), encodage(12, 8)))
    print("décaler PE(7) de 5 positions redonne exactement PE(12)")
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
PE(1), d = 4 : [0.841, 0.54, 0.01, 1.0]
décaler PE(7) de 5 positions redonne exactement PE(12)
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`encodage` refuse une dimension impaire, puisque chaque fréquence occupe une paire de coordonnées, un sinus et un cosinus. Pour chaque paire i, elle calcule l'angle pos / 10000^(2i/d) : la première paire tourne d'un radian par position, les suivantes de plus en plus lentement, si bien que chaque position reçoit une signature unique, faite de rotations rapides pour distinguer les voisins et de rotations lentes pour distinguer les positions éloignées. Elle range ensuite le sinus et le cosinus de cet angle dans le vecteur.

`decaler` vérifie la propriété annoncée par la fiche : un décalage de k positions est une rotation. Pour chaque paire, elle applique les formules d'addition du sinus et du cosinus avec l'angle k × ωᵢ, et le programme vérifie que le résultat est exactement l'encodage de la position décalée, ce qui permet au modèle de lire des positions relatives avec une simple transformation linéaire.

`main` vérifie aussi l'exemple de la fiche : en dimension 4, la position 1 donne [sin 1 ; cos 1 ; sin 0,01 ; cos 0,01] ≈ [0,841 ; 0,540 ; 0,010 ; 1,000].

## Squelette algorithmique

```text
ALGORITHME TableDEncodageDePosition
ENTRÉES : longueur maximale L, dimension d (paire)
SORTIE  : une table PE de L lignes et d colonnes, ajoutée aux embeddings des tokens

  POUR pos DE 0 À L − 1 FAIRE
      POUR i DE 0 À d/2 − 1 FAIRE
          angle ← pos / 10000^(2i / d)
          PE[pos][2i] ← sin(angle) ; PE[pos][2i + 1] ← cos(angle)
      FIN POUR
  FIN POUR
  entrée du token à la position pos ← embedding(token) + PE[pos]
```

**Complexité.** O(L × d) pour la table, calculée une seule fois. Ajouter la position à un embedding coûte O(d) par token.

**Du squelette au code.** La double boucle est `encodage` appelée pour chaque position, et la propriété de rotation est vérifiée par `decaler`.

## Dans le cours

- [Étape 35 — Encodage de position](<../../06-Attention-et-Transformer/35-Encodage-de-Position.md>)
- [Étape 32 bis — Théorèmes de l'attention et de la softmax](<../../06-Attention-et-Transformer/32b-Theoremes-Attention-et-Softmax.md>)
