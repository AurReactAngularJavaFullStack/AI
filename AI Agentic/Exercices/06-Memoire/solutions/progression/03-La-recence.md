# Étape 3 — La récence

> Progression du palier 06 · Précédent : [Étape 2 — La normalisation min-max](<02-La-normalisation-min-max.md>) · Suivant : [Étape 4 — Le score de pertinence](<04-Le-score-de-pertinence.md>) · Retour à l'énoncé : [README du palier 06](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Un souvenir vieux de trois mois doit peser moins qu'un souvenir de la veille, sans jamais disparaître tout à fait. L'étape 16 du cours choisit pour cela la décroissance exponentielle : à chaque jour sans accès, le souvenir perd la même **fraction** de ce qui lui reste. La perte est rapide au début, puis de plus en plus lente, et la valeur n'atteint jamais 0.

$$
rec(\Delta t) = e^{-\lambda\,\Delta t}
$$

Un réglage « λ = 0,0231 par jour » ne parle à personne dans une équipe métier. On le règle donc par la **demi-vie** t½, l'âge auquel la récence vaut 1/2 : « une information client vaut moitié moins au bout d'un mois ». La relation entre les deux se démontre en une ligne :

$$
e^{-\lambda t_{1/2}} = \frac{1}{2} \;\Longleftrightarrow\; \lambda = \frac{\ln 2}{t_{1/2}}
$$

La fonction reçoit donc l'âge et la demi-vie. Elle calcule λ, puis l'exponentielle. Avant cela, on se demande quelles entrées n'ont pas de sens.

1. **Une demi-vie nulle ou négative** : la division par t½ est impossible, ou donnerait une récence qui croît avec le temps.
2. **Un âge négatif** : un souvenir « du futur ». e^(−λ × âge) dépasserait 1, et ce souvenir paraîtrait plus frais que neuf. C'est toujours le signe d'une horloge mal réglée.

## Un brouillon qui oublie ln 2

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`recence(age, demi_vie)`** — Dans ce brouillon, la fonction est une horlogère qui règle bien la pente de son sablier mais se trompe de graduation : elle reçoit l'âge du souvenir et la demi-vie, et renvoie l'exponentielle de moins l'âge divisé par la demi-vie, sans le facteur ln 2. Elle décroît bien avec le temps, mais pas au bon rythme : à un âge égal à la demi-vie, elle rend e⁻¹ ≈ 0,3679 au lieu de 0,5, si bien que son paramètre est en réalité une durée de vie moyenne, et elle accepte sans protester un âge négatif ou une demi-vie nulle.

```python
# [extrait] brouillon
import math


def recence(age, demi_vie):
    return math.exp(-age / demi_vie)          # λ = 1 / demi_vie : FAUX, il manque ln 2
```

Ce brouillon décroît bien, mais pas au bon rythme : à l'âge égal à la demi-vie, il rend e⁻¹ ≈ 0,3679 au lieu de 0,5. Le paramètre qu'il utilise est en réalité une « durée de vie moyenne », pas une demi-vie. Le test `test_demi_vie` attend `recence(30, 30) == 0.5` à douze décimales, et le refuse.

```text
# [extrait] console
>>> import math
>>> math.exp(-30 / 30)
0.36787944117144233
```

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`recence(age, demi_vie)`** — C'est la même fonction, corrigée par une horlogère qui gradue son sablier en demi-vies : elle reçoit l'âge du souvenir en jours et la demi-vie, lève `ValueError` (« il faut age >= 0 et demi_vie > 0 ») sur un âge négatif ou une demi-vie nulle ou négative, calcule le taux `lam` égal à ln 2 divisé par la demi-vie, puis renvoie l'exponentielle de moins ce taux fois l'âge. Le résultat vaut exactement 1,0 à l'âge 0, 0,5 à la demi-vie, `0.12500000000000003` à 90 jours pour une demi-vie de 30, et environ 0,8909 à 5 jours : c'est la composante « fraîcheur » du score de chaque souvenir.

```python
# [extrait] agent/memoire.py
def recence(age: float, demi_vie: float) -> float:
    """rec = e^(−λ · âge) avec λ = ln 2 / demi-vie (étape 16) : 1 à l'âge 0, 1/2 à la demi-vie.

    Exemple : avec une demi-vie de 30 jours, `recence(5, 30)` ≈ 0.8909 et `recence(90, 30)` = 1/8 = 0.125.
    """
    if age < 0 or demi_vie <= 0:
        raise ValueError("il faut age >= 0 et demi_vie > 0")
    lam = math.log(2) / demi_vie
    return math.exp(-lam * age)
```

**La garde.** `if age < 0 or demi_vie <= 0: raise ValueError(...)` refuse les deux entrées absurdes en une ligne, avec un message qui dit ce qui est attendu. L'âge 0 est permis : c'est un souvenir relu à l'instant, de récence 1.

**`lam = math.log(2) / demi_vie`.** En Python, `math.log` sans second argument est le logarithme naturel, ln, comme `Math.log` en Java. On nomme la variable `lam` parce que `lambda` est un mot réservé du langage, celui des fonctions anonymes. Avec t½ = 30 jours, λ = 0,693147 / 30 ≈ 0,023105 par jour.

**`return math.exp(-lam * age)`.** L'exponentielle décroissante. On aurait pu écrire `2 ** (-age / demi_vie)`, qui est la même fonction, puisque e^(−λΔt) = (e^(ln 2))^(−Δt/t½) = 2^(−Δt/t½). On garde la forme en λ de l'étape 77, qui se transpose directement au taux de décroissance d'autres signaux.

**Le piège classique.** Comparer le résultat avec `==`. Même un âge « rond » ne donne pas un résultat exact en flottant :

```text
# [extrait] console
>>> from agent.memoire import recence
>>> recence(5, 30)
0.8908987181403393
>>> recence(90, 30)
0.12500000000000003
```

À la main, `recence(90, 30)` vaut 2⁻³ = 1/8 = 0,125 : trois demi-vies divisent par 2 trois fois. `recence(5, 30)` vaut 2^(−1/6), et comme 2^(1/6) ≈ 1,122462, on obtient ≈ 0,8909. Les tests utilisent `assertAlmostEqual`. Le seul résultat exact est `recence(0, 30)`, car `math.exp(-0.0)` vaut exactement 1.0, et le test le compare avec `assertEqual`.

## Le test qui passe maintenant

```text
python -m unittest -v tests.test_06_memoire.TestRecence
```

Les deux tests passent. `test_demi_vie` vérifie 1 à l'âge 0, 0,5 à la demi-vie, 0,125 à trois demi-vies et ≈ 0,8909 à 5 jours. `test_entrees_invalides` vérifie l'âge −1 et la demi-vie 0. Sept tests sur treize sont verts. Les trois signaux bruts savent maintenant se calculer, et l'étape suivante les mélange.
