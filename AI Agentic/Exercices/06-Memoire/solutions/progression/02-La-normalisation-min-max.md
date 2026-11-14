# Étape 2 — La normalisation min-max

> Progression du palier 06 · Précédent : [Étape 1 — Le cosinus](<01-Le-cosinus.md>) · Suivant : [Étape 3 — La récence](<03-La-recence.md>) · Retour à l'énoncé : [README du palier 06](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Le score mélange trois signaux qui n'ont pas la même échelle : un cosinus, une récence dans ]0, 1] et une importance de 1 à 10. Si on les pondère tels quels, l'importance, qui varie de 9 points, écrase le cosinus, qui varie d'au plus 1. Avant d'écrire le score, il faut une fonction qui ramène chaque signal à la même échelle. C'est min-max :

$$
\widetilde{x}_j = \frac{x_j - \min_i x_i}{\max_i x_i - \min_i x_i}
$$

Le plus petit des candidats reçoit 0, le plus grand reçoit 1, et les autres se placent entre les deux, dans le même ordre. La formule ne demande que deux nombres, calculés une fois pour toute la liste : le minimum lo et le maximum hi. Ensuite, chaque valeur se transforme seule.

On cherche, comme pour le cosinus, ce qui peut casser la formule :

1. **Une liste vide** : il n'y a ni minimum ni maximum.
2. **Des valeurs toutes égales** : hi − lo = 0, et la formule divise par zéro. C'est fréquent en pratique : trois souvenirs qui parlent tous de crédit ont le même cosinus, ou deux souvenirs relus le même jour ont la même récence.

## Un brouillon qui oublie le signal constant

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`min_max(valeurs)`** — Dans ce brouillon, la fonction est un arbitre qui ramène toutes les notes sur une échelle de 0 à 1 sans prévoir le jour où tous les candidats ont la même note : elle reçoit une liste de nombres, calcule leur minimum et leur maximum, puis renvoie la liste où chaque valeur, diminuée du minimum, est divisée par l'écart entre les deux. Sur des valeurs différentes, le résultat est juste ; mais sur `[3, 3]`, l'écart vaut zéro et la fonction lève `ZeroDivisionError`, alors que trois souvenirs qui parlent tous de crédit ont souvent le même cosinus.

```python
# [extrait] brouillon
def min_max(valeurs):
    lo, hi = min(valeurs), max(valeurs)
    return [(v - lo) / (hi - lo) for v in valeurs]     # ZeroDivisionError si toutes les valeurs sont égales
```

Sur `[3, 3]`, ce brouillon lève `ZeroDivisionError`. Quelle valeur rendre à la place ? Deux réponses viennent à l'esprit.

- **Rendre 1 partout** : le signal compterait comme « maximal » pour tout le monde. L'ordre du classement ne changerait pas, puisque chaque score gagnerait le même poids w, mais tous les scores seraient gonflés de w. Un seuil du type « n'injecter qu'au-dessus de 0,6 » changerait alors de sens selon que le signal est constant ou non.
- **Rendre 0 partout** : le signal ne départage personne, alors il ne compte pour personne. C'est la convention du cours (étape 17) et de l'étape 77, et c'est ce que vérifie `test_valeurs_egales_et_liste_vide`.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`min_max(valeurs)`** — C'est la même fonction, devenue l'arbitre prévoyant qui sait qu'une épreuve où tout le monde fait le même score ne départage personne : elle reçoit une liste de nombres, lève `ValueError` (« liste vide : min-max n'est pas défini ») si elle est vide, calcule le minimum et le maximum, renvoie une liste de zéros de même longueur s'ils sont égaux, et sinon la liste des valeurs ramenées dans [0, 1], dans le même ordre. Ce rang conservé permet à `rappeler` de lire ensemble les trois composantes d'un même souvenir ; les importances [9, 8, 4, 2] deviennent 1,0, 0,8571428571428571, 0,2857142857142857 et 0,0, et `[3, 3]` donne deux zéros.

```python
# [extrait] agent/memoire.py
def min_max(valeurs: list[float]) -> list[float]:
    """x' = (x − min) / (max − min) ; si toutes les valeurs sont égales, le signal ne départage rien : 0.0.

    Exemple : `min_max([9, 8, 4, 2])` = [1.0, 0.857143, 0.285714, 0.0] ; `min_max([3, 3])` = [0.0, 0.0].
    """
    if not valeurs:
        raise ValueError("liste vide : min-max n'est pas défini")
    lo, hi = min(valeurs), max(valeurs)
    if hi == lo:
        return [0.0 for _ in valeurs]
    return [(v - lo) / (hi - lo) for v in valeurs]
```

**`if not valeurs: raise ValueError(...)`.** Une liste vide est « fausse » en Python, donc `not valeurs` vaut `True` pour `[]`. Sans cette garde, `min([])` lèverait déjà `ValueError`, mais avec le message obscur `min() iterable argument is empty`. On préfère un message qui dit ce qui n'est pas défini.

**`lo, hi = min(valeurs), max(valeurs)`.** L'affectation multiple calcule les deux bornes ; c'est deux passages sur la liste, en O(n).

**`if hi == lo: return [0.0 for _ in valeurs]`.** Le signal constant donne une liste de zéros **de la même longueur**, car `rappeler` lira ces listes rang par rang, avec le même indice j pour les trois composantes. `_` est le nom conventionnel d'une variable de boucle qu'on n'utilise pas. Le test `hi == lo` est exact : si toutes les valeurs sont égales, `min` et `max` rendent le même objet flottant.

**Le `return` final.** Une compréhension de liste applique la formule à chaque valeur, dans l'ordre. En Java, ce serait `valeurs.stream().map(v -> (v - lo) / (hi - lo)).toList()`. La liste rendue a la même longueur et le même ordre que la liste reçue : le rang j désigne toujours le même souvenir.

**Pourquoi l'ordre est conservé.** L'application x ↦ (x − lo) / (hi − lo) est affine, de pente 1 / (hi − lo), strictement positive : elle est donc strictement croissante. Elle ne change le classement d'aucune composante prise seule. Elle ne fait que mettre les trois composantes à la même étendue, 1, pour que les poids redeviennent les vraies influences.

**Le piège classique.** Normaliser seulement les k souvenirs gardés, après le tri. Le min-max se calcule sur **tous** les candidats, avant le score : c'est l'ensemble des candidats qui définit le 0 et le 1.

## Vérification à la main et à la console

Les importances du scénario du crédit, [9, 8, 4, 2], ont lo = 2 et hi = 9, soit une étendue de 7. On obtient 7/7 = 1, 6/7 ≈ 0,857143, 2/7 ≈ 0,285714 et 0/7 = 0.

```text
# [extrait] console
>>> from agent.memoire import min_max
>>> min_max([9, 8, 4, 2])
[1.0, 0.8571428571428571, 0.2857142857142857, 0.0]
>>> min_max([3, 3])
[0.0, 0.0]
```

## Le test qui passe maintenant

```text
python -m unittest -v tests.test_06_memoire.TestMinMax
```

Les deux tests passent : les importances [9, 8, 4, 2], comparées à six décimales, puis le signal constant `[3, 3]` et la liste vide. Avec les trois tests de l'étape 1, cinq tests sur treize sont verts.
