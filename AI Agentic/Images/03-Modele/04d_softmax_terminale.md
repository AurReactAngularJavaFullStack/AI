# Fiche 04d_softmax_terminale — Softmax, niveau terminale

> Image : `04d_softmax_terminale.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 2 — Softmax et température](<../../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>)

**La softmax lue terme à terme**

## Ce que montre l'image

Fiche de niveau terminale. La formule, le schéma « vecteur de scores z → softmax → vecteur p dont la somme vaut 1 », puis l'exemple complet z = (2 ; 1 ; 0) en trois étapes : exponentielles (7,39 ; 2,72 ; 1,00), somme 11,11, probabilités (0,665 ; 0,245 ; 0,090), vérification de la somme. À droite, trois usages avec des scores et un camembert chacun : sélection d'actions, attention, classification.

**Erreur dans l'image :** les camemberts ne correspondent pas aux scores affichés. Actions (1,2 ; 0,5 ; −0,8) : environ 61 %, 30 % et 8 %. Attention (1,5 ; 0,3 ; 2,1) : 32 %, 10 % et 58 %. Classification (0,7 ; 2,3 ; −1,1) : 16 %, 81 % et 3 % (l'affiche écrit deux fois 76 %).

**Ce que l'image ajoute à la fiche 04 :** l'exemple (2 ; 1 ; 0) présenté comme un calcul de lycée, à refaire à la main sur une feuille.

## Formule

$$
p_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}
$$

## Éléments

$$
z_i
$$

**zᵢ** : le score brut, ou logit, du choix i.

$$
T > 0
$$

**T** : la température, strictement positive. Absente de certaines affiches : alors T = 1.

$$
\exp
$$

**exp** : l'exponentielle. Elle rend chaque terme positif.

$$
\sum_{j} \exp(z_j / T)
$$

**La somme** : elle force les pᵢ à totaliser 1.

## Ce que c'est

Version terminale : chaque symbole est nommé. C'est la fiche 04, avec le vocabulaire du lycée (exponentielle, somme, proportion).

## Effets et impacts

- La part d'un score grandit vite, parce que l'exponentielle amplifie les écarts.
- Avec T = 1, les notes 2 et 1 donnent environ 0,731 et 0,269.

## Exemple chiffré

$$
z = (2, 1),\ T = 1,\quad p_1 = \frac{e^{2}}{e^{2}+e^{1}} \approx 0{,}731,\quad p_2 \approx 0{,}269
$$

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z, T)`** — Cette fonction joue l'arbitre d'un duel aux points, qui transforme l'écart de score entre deux escrimeurs en chances de victoire. Elle reçoit les scores z et la température T, lève `ValueError` si T n'est pas strictement positive, retranche le meilleur score de chacun, calcule e à la puissance de chaque écart divisé par T, puis divise par la somme des exponentielles. Elle rend une distribution qui somme à 1 ; pour le duel de la fiche, z = (2, 1) à T = 1, elle donne p₁ = e² / (e² + e¹) ≈ 0,731 et p₂ ≈ 0,269, un point d'avance valant un peu moins de trois chances sur quatre.

**`main()`** — C'est le juge de touche qui rejoue plusieurs assauts pour vérifier le tableau. Il ne reçoit rien ; il calcule la softmax des scores 2, 1 et 0 à T = 1, à T = 0,5 et à T = 2, celle des notes 2, 5, 8 et 10, puis celle du duel 2 et 1 de cette fiche, imprimé en 0,731 et 0,269. Après chaque calcul, un `assert` compare les valeurs arrondies aux attendues ; il vérifie que chaque distribution somme à 1 et que les scores 1000 et 999 donnent bien plus de 0,7 au premier sans débordement, puis il ne rend rien.

```python
"""Fiches 04, 04a à 04e — softmax et température : calcul et vérification des exemples chiffrés."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def softmax(z: list[float], T: float = 1.0) -> list[float]:
    """pᵢ = exp(zᵢ / T) / Σⱼ exp(zⱼ / T), calculée en retranchant d'abord le maximum."""
    if T <= 0:
        raise ValueError("T doit être strictement positive (T = 0 est un argmax)")
    m = max(z)
    e = [math.exp((zi - m) / T) for zi in z]
    s = sum(e)
    return [ei / s for ei in e]


def main() -> None:
    p = softmax([2, 1, 0])                                   # fiches 04 et 04e
    print("scores (2, 1, 0) :", [round(x, 3) for x in p])
    assert [round(x, 3) for x in p] == [0.665, 0.245, 0.09]
    for T, attendu in ((0.5, [0.867, 0.117, 0.016]), (2.0, [0.506, 0.307, 0.186])):
        q = softmax([2, 1, 0], T)
        print(f"T = {T} :", [round(x, 3) for x in q])
        assert [round(x, 3) for x in q] == attendu
    notes = softmax([2, 5, 8, 10])                           # fiches 04a, 04b, 04c
    print("notes (2, 5, 8, 10) en % :", [round(100 * x, 2) for x in notes])
    assert [round(100 * x, 1) for x in notes] == [0.0, 0.6, 11.8, 87.5]
    deux = softmax([2, 1])                                   # fiche 04d
    print("scores (2, 1) :", [round(x, 3) for x in deux])
    assert [round(x, 3) for x in deux] == [0.731, 0.269]
    assert all(math.isclose(sum(v), 1.0) for v in (p, notes, deux))
    assert softmax([1000, 999])[0] > 0.7                     # pas de débordement grâce au maximum retranché
    print("OK — toutes les vérifications sont passées.")

if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
scores (2, 1, 0) : [0.665, 0.245, 0.09]
T = 0.5 : [0.867, 0.117, 0.016]
T = 2.0 : [0.506, 0.307, 0.186]
notes (2, 5, 8, 10) en % : [0.03, 0.59, 11.85, 87.53]
scores (2, 1) : [0.731, 0.269]
OK — toutes les vérifications sont passées.
```

## Comment le code fonctionne

`softmax` refuse d'abord une température nulle ou négative : à T = 0, la formule n'est plus définie, et le comportement attendu est un argmax, qui se code à part. Elle cherche ensuite le plus grand score m et calcule l'exponentielle de chaque score diminué de m, divisé par la température. Retrancher m ne change pas le résultat, puisque le facteur exp(−m / T) se retrouve au numérateur et au dénominateur et se simplifie, mais il garantit que la plus grande exponentielle vaut 1 : sans cette précaution, exp(1 000) dépasserait la capacité d'un nombre flottant, ce que vérifie la dernière ligne du programme. La fonction divise enfin chaque exponentielle par leur somme, ce qui donne des probabilités strictement positives dont le total vaut 1.

`main` vérifie les exemples de toutes les fiches de la famille : les scores (2, 1, 0) donnent (0,665 ; 0,245 ; 0,090), une température de 0,5 concentre la masse sur le premier score (86,7 %) et une température de 2 l'aplatit (50,6 %) ; les notes (2, 5, 8, 10) des fiches 04a à 04c donnent environ 0,03 %, 0,6 %, 11,8 % et 87,5 %, la note la plus haute prenant presque toute la part ; et les deux scores (2, 1) de la fiche 04d donnent 0,731 et 0,269. La fiche 04e applique la même fonction aux scores des actions d'une politique.

## Squelette algorithmique

```text
ALGORITHME Softmax
ENTRÉES : scores z₁ … z_n, température T > 0
SORTIE  : probabilités p₁ … p_n, strictement positives, de somme 1

  m ← max(z)
  POUR i DE 1 À n FAIRE  eᵢ ← exp((zᵢ − m) / T)  FIN POUR
  S ← Σ eᵢ
  POUR i DE 1 À n FAIRE  pᵢ ← eᵢ / S  FIN POUR
  RETOURNER p

USAGE : choisir le prochain token (tirage selon p), pondérer l'attention, ou choisir une action d'une politique.
```

**Complexité.** Trois passes sur les n scores : O(n) en temps, O(n) en mémoire pour le vecteur de probabilités. Pour un modèle de langage, n est la taille du vocabulaire, des dizaines de milliers de tokens, à chaque token généré.

**Du squelette au code.** La recherche de m, la boucle des exponentielles, la somme et la division sont, dans l'ordre, les quatre lignes de `softmax` après la garde sur T.

## Dans le cours

- [Étape 2 — Softmax et température](<../../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>)
- [Fiche 04 — Softmax et température](<04_softmax_temperature.md>)
