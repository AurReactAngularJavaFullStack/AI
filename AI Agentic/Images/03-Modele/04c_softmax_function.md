# Fiche 04c_softmax_function — The softmax function

> Image : `04c_softmax_function.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 2 — Softmax et température](<../../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>)

**La même fonction, légendes en anglais**

## Ce que montre l'image

Affiche en anglais « The softmax function for agentic AI ». La formule, puis un mode d'emploi visuel en deux temps : les logits de cinq actions d'un agent (Walk 2,1 ; Search 1,3 ; Pick Up 0,7 ; Attack −0,5 ; Wait −1,2), puis leurs probabilités. Quatre usages (sélection d'actions, attention, prédiction du prochain token, exploration) et quatre conséquences : entraînement stable avec l'entropie croisée, décisions à plusieurs classes, sorties « interprétables et calibrées », meilleure généralisation.

**Erreurs dans l'image :** les probabilités affichées (0,57 ; 0,26 ; 0,14 ; 0,04 ; 0,02) font 1,03 ; les vraies valeurs sont environ (0,553 ; 0,249 ; 0,136 ; 0,041 ; 0,020). La barre de « Wait » (−1,2) est dessinée vers la droite, comme un score positif. Enfin, « outputs are true probabilities… calibrated » est faux en général : une softmax donne des nombres positifs qui somment à 1, pas des probabilités calibrées. La calibration se mesure (fiche 20).

**Ce que l'image ajoute à la fiche 04 :** le lien explicite entre la softmax et l'entropie croisée pour l'entraînement (fiche 06).

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

Même objet que `04b` et que la fiche 04. Les mots de l'affiche sont en anglais (logits, temperature, probabilities). La formule ne change pas.

## Effets et impacts

- On s'en sert pour le prochain token et pour les poids d'attention.
- Une température basse ne rend pas la réponse vraie.

## Exemple chiffré

Notes de l'image `04a` : 2, 5, 8 et 10, avec T = 1.

$$
e^{2} \approx 7{,}39,\quad e^{5} \approx 148{,}4,\quad e^{8} \approx 2\,981,\quad e^{10} \approx 22\,026
$$

Somme ≈ 25 163. Les chances valent environ 0,03 %, 0,6 %, 11,8 % et 87,5 %. La plus haute note prend presque toute la part. Baisser T écarte encore plus les parts. Monter T les rapproche.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z, T)`** — Cette fonction ressemble à la table de mixage d'un ingénieur du son : elle reçoit plusieurs pistes de volumes différents et rend un mélange où les pistes fortes écrasent les faibles, le bouton de température réglant à quel point. Elle prend les scores z et la température T, 1 par défaut, refuse par `ValueError` toute température nulle ou négative, retranche le score le plus élevé, applique l'exponentielle à chaque écart divisé par T et normalise par la somme. Elle rend des probabilités qui totalisent 1 : pour les notes 2, 5, 8 et 10, la piste la plus forte occupe environ 87,5 % du mélange et la plus faible environ 0,03 %.

**`main()`** — C'est l'ingénieur qui teste sa console avant le concert. Il ne reçoit rien ; il passe les scores 2, 1 et 0 à T = 1, puis tourne le bouton à 0,5 et à 2, envoie ensuite les notes 2, 5, 8 et 10 de cette fiche, imprimées en pourcentage, 0,03, 0,59, 11,85 et 87,53, et enfin le duo 2 et 1, qui donne 0,731 et 0,269. Chaque mélange est vérifié par un `assert` sur ses valeurs arrondies et sur sa somme égale à 1 ; un dernier essai avec 1000 et 999 confirme qu'aucun débordement ne sature la console, et il ne rend rien.

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
