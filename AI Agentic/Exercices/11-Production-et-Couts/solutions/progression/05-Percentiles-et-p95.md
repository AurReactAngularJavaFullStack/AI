# Étape 5 — Les percentiles et le p95

> Palier 11 · Étape 5 sur 7 · Précédent : [Étape 4 — Les relances sur erreur transitoire](<04-Relances-sur-erreur-transitoire.md>) · Suivant : [Étape 6 — Le budget et les tâches possibles](<06-Budget-et-taches-possibles.md>) · Énoncé : [README du palier 11](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Un contrat de service ne dit pas « la latence moyenne est de 1,8 s », il dit « 95 % des réponses arrivent en moins de 3 s ». Le chiffre à calculer est donc le p95 : une valeur telle qu'au moins 95 % des mesures lui sont inférieures ou égales. La méthode du **rang le plus proche** (étape 72 quater) rend toujours une valeur réellement observée : on trie les n mesures, on calcule le rang k = ⌈p n / 100⌉, et l'on prend la k-ième plus petite.

Refais l'exemple du test avant de coder. Les 20 latences vont de 1,0 à 2,9 s par pas de 0,1. Le rang du p95 vaut ⌈95 × 20 / 100⌉ = 19, et la 19e plus petite vaut 2,8 s ; la médiane a le rang 10 et vaut 1,9 s. Note tout de suite le décalage : le rang 19 est l'**indice** 18 d'une liste Python, qui compte à partir de 0.

L'ordre d'écriture : `percentile` d'abord (les gardes, le tri, le rang, la lecture), puis `p95`, qui n'est qu'un cas particulier.

## Une première version, avec trois erreurs

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`percentile(valeurs, p)`** — Ce brouillon ressemble à un huissier qui, pour désigner le dix-neuvième coureur, réaligne de force les coureurs de l'organisateur et compte à partir de zéro sans le savoir. Il reçoit la liste des valeurs et l'ordre p, trie sur place la liste de l'appelant, calcule l'indice `int(p / 100 * len(valeurs))` en tronquant, et rend la valeur à cet indice. Sur les 20 latences, il rend la 20e valeur, 2,9 s, le maximum, au lieu du p95 de 2,8 s ; avec p = 100, il lève `IndexError`, et dans tous les cas il laisse la liste d'origine triée, un effet de bord que personne n'a demandé.

```python
# [extrait] brouillon
def percentile(valeurs, p):
    valeurs.sort()                                   # trie la liste de l'appelant
    return valeurs[int(p / 100 * len(valeurs))]      # rang tronqué, décalé d'un cran
```

Sur les 20 latences, `int(95 / 100 * 20)` vaut 19, et `valeurs[19]` est la **20e** valeur, 2,9 s : le maximum, pas le p95. Le brouillon confond le rang (qui commence à 1) et l'indice (qui commence à 0), et il tronque au lieu d'arrondir au-dessus. Avec p = 100, il lirait `valeurs[20]` et lèverait `IndexError`. Enfin, `valeurs.sort()` trie **sur place** la liste de l'appelant : après un calcul de p95, la liste de latences que le tableau de bord affichait dans l'ordre d'arrivée se retrouve triée, un effet de bord que personne n'a demandé.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`percentile(valeurs, p)`** — La version juste est un juge de course qui photographie l'arrivée, aligne les coureurs sur une copie du cliché sans déranger personne, puis montre du doigt celui qui occupe le rang demandé. Elle reçoit la liste et l'ordre p, lève `ValueError` si la liste est vide ou si p sort de ]0, 100], trie une copie avec `sorted`, calcule le rang `math.ceil(p * n / 100)` en multipliant avant de diviser pour qu'un flottant comme 7,000000000000001 ne fasse pas passer le rang de 7 à 8, et rend la valeur d'indice rang − 1. Sur les 20 latences, elle rend 2,8 s pour p = 95, 1,9 s pour la médiane et 2,9 s pour p = 100, quel que soit l'ordre d'arrivée des valeurs.

**`p95(valeurs)`** — Cette fonction est l'étiquette posée sur le cadran que l'équipe d'astreinte surveille : une seule aiguille, celle qu'une requête sur vingt dépasse. Elle reçoit une liste de latences et rend simplement `percentile(valeurs, 95)`, donc lève la même `ValueError` pour une liste vide. Elle rend 2,8 s pour les latences 1,0 à 2,9 s, 2,8 s encore pour la même liste renversée, et 0,7 s pour une liste réduite à 0,7 s ; donner un nom à ce chiffre évite de recopier 95 partout et rend l'alerte du contrat de service lisible.

```python
# [extrait] agent/production.py
def percentile(valeurs: list[float], p: float) -> float:
    """Percentile au rang le plus proche : la valeur de rang ⌈p × n / 100⌉ dans la liste triée.

    Toujours une valeur observée, jamais une interpolation. Exemple : pour 20 latences, le p95 est la
    19e plus petite (⌈95 × 20 / 100⌉ = 19) ; la médiane (p = 50) est la 10e. On multiplie AVANT de
    diviser : `7 / 100 * 100` vaut 7.000000000000001 en flottant, et son plafond 8 au lieu de 7.
    """
    if not valeurs:
        raise ValueError("liste vide : le percentile n'est pas défini")
    if not 0 < p <= 100:
        raise ValueError("p est dans ]0, 100]")
    triees = sorted(valeurs)
    rang = math.ceil(p * len(triees) / 100)   # p × n est exact pour des entiers : pas de 7,000…01
    return triees[rang - 1]


def p95(valeurs: list[float]) -> float:
    """Le 95e percentile au rang le plus proche : une requête sur vingt est plus lente que lui.

    Exemple : les latences 1.0, 1.1, …, 2.9 s (20 valeurs, pas de 0.1) ont un p95 de 2.8 s.
    """
    return percentile(valeurs, 95)
```

**Les deux gardes.** Une liste vide n'a pas de percentile : on lève `ValueError` plutôt que de rendre 0, qui ressemblerait à une latence parfaite. C'est la même convention que pour toutes les métriques du cours : ce qui n'est pas défini n'est pas déguisé en nombre. Le test `0 < p <= 100` s'écrit en Python comme en mathématiques, en une seule comparaison chaînée. p = 0 est refusé parce qu'il donnerait le rang 0, qui n'existe pas ; p = 100 est permis et donne le maximum.

**Le tri.** `sorted(valeurs)` rend une **nouvelle** liste triée et laisse celle de l'appelant intacte, comme `stream().sorted().toList()` en Java, à la différence de `Collections.sort`, qui trie sur place.

**Le rang.** `math.ceil` arrondit au-dessus : ⌈19⌉ = 19, ⌈0,95⌉ = 1. Le rang est toujours entre 1 et n, ce que le README démontre : si 0 < p ≤ 100, alors 0 < p n / 100 ≤ n. Une liste d'une seule valeur, 0,7 s, a donc un p95 de 0,7 s, et non une erreur.

**Le piège du flottant, et pourquoi on multiplie d'abord.** La formule naturelle `p / 100 * n` passe par 0,07, qui n'a pas d'écriture exacte en binaire :

```text
# [extrait] console
>>> import math
>>> 7 / 100 * 100, math.ceil(7 / 100 * 100)
(7.000000000000001, 8)
>>> 7 * 100 / 100, math.ceil(7 * 100 / 100)
(7.0, 7)
```

Le plafond de 7,000000000000001 vaut 8, et le 7e percentile des entiers de 1 à 100 deviendrait 8. En multipliant d'abord, `p * len(triees)` est un produit d'entiers, exact ; s'il est multiple de 100, sa division par 100 tombe exactement sur un entier, et sinon le quotient est à au moins 0,01 de tout entier, si bien qu'un arrondi minuscule ne peut pas le faire passer de l'autre côté. Le test `percentile(list(range(1, 101)), 7) == 7` verrouille ce cas. En Java, on éviterait le problème avec des entiers, `Math.ceilDiv(p * n, 100)`.

**La lecture** : `triees[rang - 1]`, parce que le rang 1 est l'indice 0. C'est l'endroit où l'on se trompe le plus souvent ; relis-le en pensant « rang 19, indice 18 ».

**`p95`** tient en une ligne : il appelle `percentile` avec 95. Écrire une seconde fonction plutôt qu'un appel `percentile(x, 95)` partout donne un nom au chiffre que l'on surveille, comme une méthode `p95()` sur un objet de métriques.

```text
# [extrait] console
>>> from agent.production import p95, percentile
>>> latences = [round(1.0 + 0.1 * i, 1) for i in range(20)]
>>> p95(latences), percentile(latences, 50), percentile(latences, 100)
(2.8, 1.9, 2.9)
>>> p95(list(reversed(latences))), p95([0.7])
(2.8, 0.7)
```

**Pourquoi pas la moyenne ?** Sur les 20 latences de `demo.py`, la moyenne vaut 1,775 s et le p95 3,4 s. Une moyenne sous 3 s ne garantit rien : la queue de la distribution, celle des clients qui attendent, n'y pèse presque pas. L'étape 70 montre que, dans une file M/M/1, le p95 vaut environ trois fois le temps moyen : dimensionner sur la moyenne laisse une requête sur vingt attendre plus du triple.

## Le test qui passe maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_11_production.TestPercentilesEtBudget.test_p95_au_rang_le_plus_proche
```

Le test vérifie le p95 (2,8 s), la médiane (1,9 s), l'indépendance à l'ordre, une liste d'une seule valeur, le 7e percentile des entiers de 1 à 100, et les deux erreurs (liste vide, p = 0). Le second test de la classe, sur le budget, attend l'étape suivante.
