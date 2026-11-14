# Étape 1 — Le cosinus

> Progression du palier 06 · Précédent : [Énoncé du palier](<../../README.md>) · Suivant : [Étape 2 — La normalisation min-max](<02-La-normalisation-min-max.md>) · Retour à l'énoncé : [README du palier 06](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Le module a six noms publics, et `rappeler` les utilise tous. On l'écrit donc en dernier. On commence par les briques sans dépendance, dans l'ordre des trois signaux du score : le sens (le cosinus), puis la mise à l'échelle (min-max), la fraîcheur (la récence), le mélange (le score), et enfin l'objet souvenir. Chaque brique a sa classe de tests, ce qui permet de valider pas à pas.

Pour le cosinus, on part de la formule et on la lit comme une recette :

$$
\cos(a, b) = \frac{\sum_{i=1}^{d} a_i b_i}{\sqrt{\sum_{i=1}^{d} a_i^{2}} \; \sqrt{\sum_{i=1}^{d} b_i^{2}}}
$$

Elle contient trois sommes, toutes sur le même indice i : celle du numérateur, et une sous chaque racine. On se demande ensuite ce qui peut casser la formule, avant d'écrire le calcul :

1. **Deux vecteurs de longueurs différentes** : la somme sur i n'a pas de sens. En Python, `zip` s'arrêterait en silence au plus court, sans aucune erreur.
2. **Un vecteur nul** : sa norme vaut 0, et la formule divise par zéro. Un vecteur nul n'a pas de direction, donc pas d'angle avec un autre.
3. **Les arrondis** : le quotient calculé peut sortir de [−1, 1] d'un cheveu.

Les deux premiers cas sont des erreurs d'entrée : on lève `ValueError`, comme partout dans le cours. Le troisième est un défaut du calcul flottant : on borne le résultat.

## Un brouillon qui masque les erreurs

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — Dans ce brouillon, la fonction est un navigateur qui, faute de boussole, inscrit tranquillement « cap nul » dans le journal de bord au lieu de signaler la panne : elle reçoit deux vecteurs, calcule leurs normes, puis renvoie le produit scalaire, obtenu en appariant les composantes avec `zip`, divisé par le produit des normes augmenté de 10⁻⁹. Elle ne plante jamais, et c'est son défaut : un vecteur nul donne 0,0 comme un texte simplement hors sujet, deux vecteurs de longueurs différentes sont tronqués en silence au plus court, et deux vecteurs identiques ne donnent plus exactement 1.

```python
# [extrait] brouillon
import math


def cosinus(a, b):
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb + 1e-9)    # epsilon « pour éviter la division par 0 »
```

Ce brouillon ne plante jamais, et c'est justement le problème.

- **L'epsilon cache le vecteur nul.** Pour un texte dont aucun mot n'est connu du plongement, le vecteur est nul et le brouillon rend 0.0, comme pour un texte simplement hors sujet. Le souvenir finit dernier du classement, et personne ne voit que le plongement a échoué. La règle du cours est claire : pas d'epsilon qui masque un vecteur nul. On lève une erreur, qui sera visible.
- **`zip` tronque.** Le brouillon accepte [1, 2] et [1, 2, 3] et calcule un nombre sans signification. En Java, une boucle sur des tableaux de tailles différentes lèverait au moins une `ArrayIndexOutOfBoundsException` ; `zip` ne lève rien.
- **L'epsilon fausse aussi les bons cas.** Le cosinus de deux vecteurs identiques ne vaut plus exactement 1.

Le test `test_vecteur_nul_et_dimensions` exige `ValueError` dans les deux premiers cas.

## Les imports et la fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — C'est la même fonction, confiée cette fois à un navigateur qui vérifie ses instruments avant de lire le cap : elle reçoit deux vecteurs, lève `ValueError` (« dimensions différentes ») si leurs longueurs diffèrent, calcule les deux normes, lève `ValueError` (« vecteur nul : le cosinus n'est pas défini ») si l'une d'elles vaut exactement 0, puis divise le produit scalaire par le produit des normes. Elle renvoie ce quotient borné à [−1, 1], parce que l'arrondi peut le faire déborder d'un cheveu, comme le 1,0000000000000002 des vecteurs [1, 1, 1] et [2, 2, 2] ; la question du crédit et le souvenir du salaire donnent 0,7499999999999999, soit 0,75 à la main, et le souvenir du change 0,35355339059327373.

```python
# [extrait] agent/memoire.py
import math
from collections.abc import Callable
from dataclasses import dataclass


def cosinus(a: list[float], b: list[float]) -> float:
    """cos(a, b) = a · b / (‖a‖ ‖b‖), borné à [−1, 1] ; un vecteur nul lève `ValueError` (pas d'epsilon).

    Exemple : `cosinus([1, 1, 2, 1, 0, 1, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0])` = 3 / (√8 × √2) = 3 / 4 = 0.75.
    """
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))
```

**Les imports.** `math` donne `sqrt`, `log` et `exp`. `Callable` servira à annoter le paramètre `plonger_texte` de `rappeler` (étape 6) ; on l'importe depuis `collections.abc`, la forme moderne, et non depuis `typing`. `dataclass` servira au `Souvenir` (étape 5). Le module ne dépend d'aucun palier antérieur : la mémoire est un composant autonome.

**`if len(a) != len(b): raise ValueError(...)`.** La garde des dimensions, avant tout calcul. C'est la précondition qu'on écrirait en Java avec `if (a.length != b.length) throw new IllegalArgumentException(...)`.

**Les deux normes.** `math.sqrt(sum(x * x for x in a))` est la racine de la somme des carrés. L'argument de `sum` est une expression génératrice, l'équivalent de `Arrays.stream(a).map(x -> x * x).sum()`. On calcule les normes avant le produit scalaire pour pouvoir tester le vecteur nul tout de suite.

**`if na == 0.0 or nb == 0.0: raise ValueError(...)`.** Une norme est nulle si et seulement si toutes les composantes sont nulles, car une somme de carrés ne s'annule que si chaque carré est nul. Le test d'égalité exacte à 0.0 est donc juste ici : on ne compare pas deux résultats de calcul approchés, on détecte des zéros exacts.

**Le `return`.** `sum(x * y for x, y in zip(a, b))` est le produit scalaire : `zip` associe les composantes de même rang, comme une boucle `for (int i = 0; i < d; i++)` sur deux tableaux. On divise par le produit des normes, puis `max(-1.0, min(1.0, …))` borne le résultat : `min` coupe ce qui dépasse 1, `max` ce qui passe sous −1. Sans cette borne, la mesure suivante sortirait de [−1, 1] :

```text
# [extrait] console
>>> import math
>>> from agent.memoire import cosinus
>>> a, b = [1, 1, 1], [2, 2, 2]
>>> sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b)))
1.0000000000000002
>>> cosinus(a, b)
1.0
```

Mathématiquement, l'inégalité de Cauchy-Schwarz garantit |a · b| ≤ ‖a‖ ‖b‖ ; c'est l'arrondi des deux racines qui fait déborder le quotient. Un cosinus de 1,0000000000000002 ne gênerait pas le classement, mais il casserait toute vérification « le score est dans [0, 1] » écrite plus loin.

**Le piège classique.** Mettre la borne trop tôt, sur le produit scalaire au lieu du quotient, ou comparer le résultat avec `==` dans un test. Le cosinus du scénario du crédit, calculé en flottant, ne vaut pas exactement 0.75 :

```text
# [extrait] console
>>> cosinus([1, 1, 2, 1, 0, 1, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0])
0.7499999999999999
>>> cosinus([1, 1, 2, 1, 0, 1, 0, 0], [0, 0, 0, 0, 0, 3, 0, 0])
0.35355339059327373
```

À la main, 3 / (√8 × √2) = 3 / 4 = 0,75 et 3 / (3 × √8) = 1 / √8 ≈ 0,3536. Les tests comparent donc avec `assertAlmostEqual(…, places=12)`, et non avec `assertEqual`.

## Le test qui passe maintenant

```text
python -m unittest -v tests.test_06_memoire.TestCosinus
```

Les trois tests passent : l'exemple chiffré (0,75 et 1/√8), les cas limites (orthogonaux 0, colinéaires 1, opposés −1) et les deux erreurs (vecteur nul, dimensions différentes). La brique « sens » est en place ; la suivante met les trois signaux à la même échelle.
