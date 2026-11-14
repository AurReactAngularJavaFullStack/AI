# Fiche 04e_softmax_politique — Softmax d'une politique

> Image : `04e_softmax_politique.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 2 — Softmax et température](<../../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>)

**La softmax choisit une action, pas seulement un token**

## Ce que montre l'image

Affiche « Softmax, politique probabiliste pour agents IA ». La formule y est écrite pour une politique : π(a | s), la probabilité de choisir l'action a dans l'état s, vaut l'exponentielle du logit de a divisée par la somme des exponentielles des logits. Exemple : logits (2,0 ; 1,0 ; 0,0) → (0,665 ; 0,244 ; 0,091). Un graphique oppose une distribution plate (exploration) à une distribution piquée (exploitation). Un schéma enchaîne observations → politique π(a | s) → actions tirées au hasard selon cette politique.

**Petite imprécision :** les valeurs exactes sont (0,665 ; 0,245 ; 0,090).

**Ce que l'image ajoute à la fiche 04 :** la softmax vue comme une politique stochastique, base de REINFORCE (fiche 19).

## Formule

$$
\pi(a \mid s) = \frac{\exp(z_a)}{\sum_b \exp(z_b)}
$$

## Éléments

$$
\pi(a \mid s)
$$

**π(a | s) (pi)** : la probabilité de choisir l'action a dans l'état s.

$$
z_a
$$

**zₐ** : le score (logit) de cette action.

$$
\sum_{b} \exp(z_b)
$$

**b** : toutes les actions possibles. La somme les normalise.

## Ce que c'est

Ici la softmax n'est plus le prochain mot : c'est la politique de l'agent. Un logit plus grand rend l'action plus probable, sans la rendre certaine.

## Effets et impacts

- Exploration : plusieurs actions gardent une probabilité.
- Exploitation : un logit domine, l'agent répète la même action.
- L'affiche cite des probabilités 0,665, 0,244 et 0,091. Elles correspondent à trois scores 2, 1 et 0, pas à une liste plus longue.

## Exemple chiffré

Scores 2, 1 et 0 :

$$
e^{2} \approx 7{,}389,\quad e^{1} \approx 2{,}718,\quad e^{0} = 1,\quad \text{somme} \approx 11{,}107
$$

$$
\pi \approx (0{,}665,\ 0{,}245,\ 0{,}090)
$$

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z, T)`** — Ici, la fonction devient la roue de loterie d'un agent qui doit choisir une action : chaque action reçoit une part de la roue d'autant plus large que son score est élevé, et la température décide si la roue favorise nettement la meilleure ou laisse leur chance aux autres. Elle reçoit les scores z et la température T, lève `ValueError` pour une température nulle ou négative, retranche le score maximal, prend l'exponentielle de chaque écart divisé par T et divise par la somme. Elle rend la politique π, une distribution qui somme à 1 : pour les scores 2, 1 et 0, environ (0,665 ; 0,245 ; 0,090).

**`main()`** — C'est le croupier qui fait tourner la roue sous plusieurs réglages avant d'ouvrir la partie. Il ne reçoit rien ; il calcule la politique des scores 2, 1 et 0 de cette fiche à T = 1, puis à T = 0,5, où la meilleure action monte à 0,867, et à T = 2, où elle redescend à 0,506, ensuite la distribution des notes 2, 5, 8 et 10 et celle des scores 2 et 1. Chaque roue est vérifiée par un `assert` sur ses valeurs arrondies, puis sur sa somme égale à 1, et un essai avec 1000 et 999 confirme l'absence de débordement ; il ne rend rien.

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
- [Étape 38 — MDP et Bellman](<../../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>)
