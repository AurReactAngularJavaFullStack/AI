# Fiche 04 — Softmax et température

> Image : `04_softmax_temperature.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 2 — Softmax et température](<../../02-LLM-Softmax-et-Prompts/02-Softmax-Temperature-Prochain-Token.md>)

**Des scores bruts deviennent des probabilités**

## Formule

$$
p_i = \frac{\exp(z_i / T)}{\sum_{j} \exp(z_j / T)}
$$

## Éléments

$$
z_i
$$

**zᵢ** : le score brut, ou logit, du choix i (par exemple un token du vocabulaire).

$$
T > 0
$$

**T** : la température, strictement positive.

$$
\exp
$$

**exp** : l'exponentielle. Elle rend chaque score strictement positif.

$$
\sum_{j}
$$

**Σⱼ** : la somme sur tous les choix possibles. Diviser par elle force le total à 1.

$$
p_i \in\ ]0, 1[, \qquad \sum_i p_i = 1
$$

**pᵢ** : la probabilité du choix i, entre 0 et 1. Les probabilités somment à 1.

## Ce que c'est

La softmax transforme des scores en distribution de probabilité. Une température basse concentre la masse sur le meilleur score. Une température haute aplatit la distribution.

## Effets et impacts

- Elle choisit le prochain token et pondère l'attention (fiche 05).
- T proche de 0 donne un choix presque déterministe, utile pour le JSON et les appels d'outils.
- T élevée augmente la diversité, pas la vérité.
- Baisser T ne garantit ni l'exactitude ni la reproductibilité : tant que T > 0, chaque token garde une probabilité strictement positive.

## Exemple chiffré

Trois tokens de logits 2, 1 et 0 :

$$
T = 1 : \quad p = \frac{(e^{2},\ e^{1},\ e^{0})}{e^{2} + e^{1} + e^{0}} = \frac{(7{,}389\ ;\ 2{,}718\ ;\ 1)}{11{,}107} \approx (0{,}665\ ;\ 0{,}245\ ;\ 0{,}090)
$$

$$
T = 0{,}5 : \quad p \approx (0{,}867\ ;\ 0{,}117\ ;\ 0{,}016) \qquad\qquad T = 2 : \quad p \approx (0{,}506\ ;\ 0{,}307\ ;\ 0{,}186)
$$

Diviser par T = 0,5 double l'écart entre les logits : le premier token passe de 66,5 % à 86,7 %.

## Code Python équivalent

Le programme ci-dessous calcule la formule de cette fiche et vérifie les nombres de son exemple chiffré, ainsi que ceux des autres fiches de la même formule. Il n'utilise que la bibliothèque standard de Python.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z, T)`** — Cette fonction fonctionne comme le thermostat d'une salle de vote : à basse température, presque toutes les voix se rassemblent sur le favori ; à haute température, elles s'éparpillent entre les candidats. Elle reçoit la liste des scores z et la température T, 1 par défaut, lève `ValueError` si T est nulle ou négative, retranche d'abord le plus grand score pour éviter tout débordement, calcule l'exponentielle de chaque écart divisé par T, puis divise chacune par leur somme. Elle rend une liste de probabilités qui somment à 1 : (0,665 ; 0,245 ; 0,090) pour les logits 2, 1 et 0 à T = 1, et (0,867 ; 0,117 ; 0,016) à T = 0,5.

**`main()`** — C'est le technicien qui fait varier le thermostat et note chaque relevé. Il ne reçoit rien ; il applique la softmax aux logits 2, 1 et 0 à T = 1, puis à T = 0,5 et T = 2, où il attend (0,506 ; 0,307 ; 0,186), ensuite aux notes 2, 5, 8 et 10, qui donnent en pourcentage environ 0,03, 0,59, 11,85 et 87,53, et aux deux scores 2 et 1, qui donnent 0,731 et 0,269. Chaque résultat est imprimé puis vérifié par `assert`, comme la somme égale à 1 et l'absence de débordement sur les scores 1000 et 999 ; il ne rend rien.

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
- [Étape 3 — Fondements de la softmax](<../../02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md>)
- [Étape 7 — Taux de conformité et intervalle de Wilson](<../../02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md>)
