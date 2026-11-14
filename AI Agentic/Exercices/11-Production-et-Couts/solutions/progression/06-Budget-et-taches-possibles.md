# Étape 6 — Le budget et les tâches possibles

> Palier 11 · Étape 6 sur 7 · Précédent : [Étape 5 — Les percentiles et le p95](<05-Percentiles-et-p95.md>) · Suivant : [Étape 7 — Assembler, lancer et retenir](<07-Assembler-et-lancer.md>) · Énoncé : [README du palier 11](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Le coût d'une tâche (étape 1) ne sert à rien s'il n'est comparé à rien. L'équipe fixe un budget, par exemple un budget du jour en AED, et deux questions reviennent après chaque tâche : combien reste-t-il, et combien de tâches peut-on encore payer ? Ce sont deux fonctions courtes, mais chacune a un piège, et les deux pièges vont dans le même sens : ils rendent la situation plus belle qu'elle n'est.

Refais l'exemple de `TestPercentilesEtBudget.test_budget` : 50 − (12,5 + 20,25 + 7,0) = 50 − 39,75 = 10,25 AED. Puis 10,25 / 0,141024 = 72,68, et l'on ne peut pas payer 0,68 tâche : 72. Le test vérifie aussi qu'un budget de 10 AED et une dépense de 12 AED donnent −2, et qu'un reste négatif ne finance aucune tâche.

## Une première version, trop optimiste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`budget_restant(budget_aed, depenses_aed)`** — Ce brouillon est un comptable complaisant qui, découvrant un découvert, efface le chiffre rouge et écrit « zéro » à la place. Il reçoit le budget et la liste des dépenses, soustrait la somme des dépenses du budget et rend le plus grand de ce résultat et de 0,0. Il ne refuse ni un budget ni une dépense négatifs, et un dépassement de 2 AED, celui d'un budget de 10 AED face à une dépense de 12 AED, s'affiche comme une journée bouclée au centime près : l'information la plus utile de la journée disparaît.

**`taches_possibles(reste_aed, cout_tache_aed)`** — Ce second brouillon est le même comptable, qui promet une commande de plus qu'il ne peut en payer parce qu'il arrondit au plus proche. Il reçoit le reste et le coût d'une tâche, divise l'un par l'autre et rend `round` du quotient. Avec 10,25 AED à 0,141024 AED la tâche, il rend 73 au lieu de 72, alors que 73 tâches coûteraient 10,294752 AED ; et un coût nul fait lever une division par zéro au lieu d'un message clair.

```python
# [extrait] brouillon
def budget_restant(budget_aed, depenses_aed):
    return max(0.0, budget_aed - sum(depenses_aed))   # un dépassement devient « il reste 0 »


def taches_possibles(reste_aed, cout_tache_aed):
    return round(reste_aed / cout_tache_aed)          # 72.68 devient 73
```

**Ramener un dépassement à 0** efface l'information la plus importante de la journée : de combien on a dépassé. Avec −2 AED, le tableau de bord afficherait « reste 0 », exactement comme une journée bouclée au centime près, et personne ne chercherait la boucle emballée qui a dépensé 2 AED de trop. Le test attend −2 et échoue. **Arrondir au plus proche** promet 73 tâches alors que 73 × 0,141024 = 10,294752 AED dépasse les 10,25 AED disponibles : la 73e tâche serait lancée sans financement. Et le brouillon ne refuse ni une dépense négative (qui ferait remonter le budget) ni un coût nul (qui ferait une division par zéro).

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`budget_restant(budget_aed, depenses_aed)`** — La version juste tient la caisse comme un trésorier scrupuleux, qui inscrit le solde tel qu'il est, en rouge s'il le faut. Elle reçoit le budget et la liste des dépenses, lève `ValueError` si le budget est négatif ou si une seule dépense l'est, la recherche s'arrêtant à la première fautive, puis rend la simple soustraction du budget et de la somme des dépenses, sans `max` ni arrondi. Elle rend 10,25 AED pour un budget de 50 AED et des dépenses de 12,5, 20,25 et 7,0 AED, et −2 AED pour un budget de 10 AED face à 12 AED dépensés : le signe du résultat est l'information.

**`taches_possibles(reste_aed, cout_tache_aed)`** — Cette fonction est le même trésorier qui ne promet que les commandes qu'il peut régler en entier. Elle reçoit le reste en AED et le coût d'une tâche, lève `ValueError` si ce coût est nul ou négatif, puis rend le plus grand de 0 et de la partie entière inférieure du quotient, obtenue par `math.floor`. Avec 10,25 AED et 0,141024 AED la tâche, elle rend 72, car 72 tâches coûtent 10,153728 AED et 73 dépasseraient ; avec un reste de −2 AED, le quotient tombe à −15 et elle rend 0, puisqu'on ne lance pas un nombre négatif de tâches.

```python
# [extrait] agent/production.py
def budget_restant(budget_aed: float, depenses_aed: list[float]) -> float:
    """Budget moins la somme des dépenses ; négatif en cas de dépassement.

    Exemple : budget journalier de 50 AED, dépenses [12.5, 20.25, 7.0] : 50 − 39.75 = 10.25 AED.
    """
    if budget_aed < 0 or any(d < 0 for d in depenses_aed):
        raise ValueError("budget et dépenses sont >= 0")
    return budget_aed - sum(depenses_aed)


def taches_possibles(reste_aed: float, cout_tache_aed: float) -> int:
    """Nombre de tâches encore finançables : ⌊reste / coût⌋, 0 si le reste est négatif ou nul.

    Exemple : 10.25 AED à 0.141024 AED la tâche : ⌊72.68…⌋ = 72 tâches.
    """
    if cout_tache_aed <= 0:
        raise ValueError("coût d'une tâche > 0")
    return max(0, math.floor(reste_aed / cout_tache_aed))
```

**La garde de `budget_restant`.** `any(d < 0 for d in depenses_aed)` parcourt les dépenses et s'arrête à la première négative : c'est le `stream().anyMatch(d -> d < 0)` de Java. Une dépense négative serait un remboursement déguisé, qui ferait remonter le budget sans que personne ne l'ait décidé ; un remboursement réel s'enregistre ailleurs, explicitement.

**Le calcul** est une soustraction, et c'est tout : `budget_aed - sum(depenses_aed)`. Aucun `max`, aucun arrondi. Le signe du résultat **est** l'information : positif, il reste de quoi travailler ; négatif, on a dépassé, et la valeur dit de combien.

**La garde de `taches_possibles`.** Un coût nul ou négatif n'a pas de sens pour une tâche facturée, et il ferait diviser par zéro, ou rendre un nombre de tâches négatif à partir d'un reste positif. On refuse avant de diviser.

**La partie entière inférieure.** `math.floor` arrondit vers le bas : ⌊72,68⌋ = 72. On peut toujours payer 72 tâches (72 × 0,141024 = 10,153728 ≤ 10,25), jamais 73. Le `max(0, …)` traite le reste négatif : ⌊−2 / 0,141024⌋ = ⌊−14,18⌋ = −15, ramené à 0 tâche. Ici, et ici seulement, ramener à 0 est juste : on ne peut pas lancer un nombre négatif de tâches, alors qu'un budget peut, lui, être négatif.

**Le piège de `int`.** Pour un quotient positif, `int(72.68)` et `math.floor(72.68)` donnent tous deux 72. Pour un quotient négatif, ils diffèrent : `int` tronque vers zéro, `floor` descend.

```text
# [extrait] console
>>> import math
>>> round(10.25 / 0.141024), math.floor(10.25 / 0.141024)
(73, 72)
>>> int(-14.2), math.floor(-14.2)
(-14, -15)
>>> from agent.production import budget_restant, taches_possibles
>>> budget_restant(50, [12.5, 20.25, 7.0]), budget_restant(10, [12]), taches_possibles(-2, 0.141024)
(10.25, -2, 0)
```

Avec le `max(0, …)`, les deux donnent 0 sur un reste négatif ; mais `floor` est l'opération qui correspond à la définition (le plus grand entier qui ne dépasse pas le quotient), et c'est elle qu'on écrit pour ne pas avoir à se demander, le jour où le `max` disparaît d'une variante, si le résultat est encore juste. En Java, la même distinction sépare la division entière `/`, qui tronque, de `Math.floorDiv`.

## Le test qui passe maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_11_production.TestPercentilesEtBudget
```

Les deux tests de la classe passent : le p95 de l'étape 5 et le budget (10,25 AED, −2 AED, 72 tâches, 0 tâche, un coût nul et une dépense négative refusés). Tous les tests du palier 11 sont maintenant verts.
