# Étape 3 — Goal Accuracy et moyenne définie

> [Énoncé du palier 10](<../../README.md>) · Précédent : [Étape 2 — La Tool Call F1](<02-Tool-Call-F1.md>) · Suivant : [Étape 4 — La fidélité approchée](<04-Fidelite-approchee.md>)

## Comment raisonner

Deux moyennes, deux fonctions d'une ligne, et pourtant deux pièges. La Goal Accuracy est la moyenne des notes 0 ou 1 des tâches : le **résultat** de l'agent, quand la Tool Call F1 jugeait son chemin. La moyenne définie agrège des mesures dont certaines valent `None` (une F1 sans appel attendu, une fidélité sans nombre cité) : il faut les **ignorer**, pas les compter comme des zéros.

On écrit d'abord le cas vide de chacune, parce que c'est lui qui distingue une fonction correcte d'une fonction qui plante : une liste vide n'a pas de moyenne.

## La Goal Accuracy

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`goal_accuracy(resultats)`** — Cette fonction ressemble au chef de rayon qui, en fin de journée, compte les clients repartis satisfaits et divise par le nombre de clients servis. Elle reçoit une liste de booléens, un par tâche, rend `None` si cette liste est vide, et sinon additionne les booléens, chaque `True` valant 1, puis divise par la longueur de la liste. Elle ne lève jamais `ZeroDivisionError`, grâce à la garde placée avant la division ; avec 14 tâches réussies sur 18, elle rend 14 / 18 ≈ 0,7778, le taux que le rapport placera à côté de son intervalle de Wilson.

```python
# [extrait] agent/evaluation.py
def goal_accuracy(resultats: list[bool]) -> float | None:
    """Part des tâches dont l'objectif est atteint ; None si aucune tâche. Exemple : 14 sur 18 ≈ 0.7778."""
    return sum(resultats) / len(resultats) if resultats else None
```

**Ligne par ligne.** `if resultats` est faux pour une liste vide : la fonction rend `None` avant toute division. Sinon, `sum(resultats)` additionne des booléens. En Python, `bool` est une sous-classe de `int`, et `True` vaut 1 dans une somme : `sum([True] * 14 + [False] * 4)` vaut 14, et 14 / 18 ≈ 0,7778. L'expression conditionnelle `a if condition else b` est l'opérateur ternaire Java `condition ? a : b`, écrit dans l'autre ordre.

**Analogie Java.** `resultats.stream().mapToDouble(b -> b ? 1 : 0).average()` rend un `OptionalDouble`, vide pour une liste vide : exactement la sémantique de `None`.

**Le piège classique.** Écrire `sum(resultats) / len(resultats)` sans garde : `goal_accuracy([])` lève `ZeroDivisionError`, et c'est toute l'évaluation qui s'arrête parce qu'un jeu de cas était vide.

## La moyenne définie

Un brouillon qui paraît équivalent :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`moyenne_definie(valeurs)`** — Ce brouillon se comporte comme un professeur qui, en voulant écarter les copies des absents, jette aussi à la corbeille toutes les copies notées zéro. Il reçoit une liste de mesures, garde celles qui sont « vraies » au sens de Python, ce qui exclut `None` mais aussi `0.0`, et rend leur moyenne, ou `None` s'il n'en reste aucune. Le pire cas d'une Tool Call F1, 0,0, disparaît donc de l'agrégat : `[0.0, 1.0]` donne 1,0 au lieu de 0,5, et un dossier complètement raté embellit la moyenne au lieu de la faire baisser.

```python
# [extrait] brouillon
def moyenne_definie(valeurs):
    definies = [v for v in valeurs if v]          # filtre aussi 0.0 : erreur
    return sum(definies) / len(definies) if definies else None
```

`if v` est faux pour `None`, mais aussi pour `0.0`. Or une Tool Call F1 de 0,0 est une mesure **définie**, et la pire : l'agent n'a fait aucun des appels attendus. Avec ce brouillon, `[0.0, 1.0]` donne 1,0 au lieu de 0,5, et un cas raté disparaît de la moyenne. La bonne version teste l'identité avec `None` :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`moyenne_definie(valeurs)`** — La version juste est le même professeur, devenu scrupuleux : il ne met de côté que les copies vraiment absentes, et garde soigneusement les zéros. Elle reçoit la liste de mesures, ne retient que les valeurs qui ne sont pas `None`, zéros compris, grâce au test d'identité `is not None`, et rend leur moyenne arithmétique, ou `None` s'il ne reste rien. Ainsi [1 ; None ; 0,5] donne (1 + 0,5) / 2 = 0,75, et une liste composée seulement de `None` donne `None` ; c'est cette moyenne que le rapport utilisera pour les F1 et les fidélités.

```python
# [extrait] agent/evaluation.py
def moyenne_definie(valeurs: list) -> float | None:
    """Moyenne des valeurs définies (les None sont ignorés) ; None si aucune. Exemple : [1, None, 0.5] → 0.75."""
    definies = [v for v in valeurs if v is not None]
    return sum(definies) / len(definies) if definies else None
```

**Ligne par ligne.** `v is not None` ne garde que les valeurs qui existent, zéros compris ; `is` compare l'identité, comme `!= null` en Java (et non `equals`). Puis la même garde qu'au-dessus : aucune valeur définie, `None`.

**Pourquoi ignorer, et pas compter 0 ?** Une réponse sans aucun chiffre n'a rien inventé : lui donner une fidélité de 0 ferait baisser la moyenne et pourrait bloquer la barrière à tort. Lui donner 1 la récompenserait d'une mesure qu'on n'a pas faite. L'exclure dit la vérité : il n'y avait rien à mesurer. C'est la convention de tout le parcours, et le test `test_moyenne_indefinie_ne_bloque_pas` de l'étape 6 en dépend.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_10_evaluation.TestGoalEtFidelite.test_goal_accuracy
python -m unittest -v tests.test_10_evaluation.TestGoalEtFidelite.test_moyenne_definie
```

Le premier vérifie 14 sur 18 ≈ 0,7778 et `None` pour une liste vide. Le second vérifie [1 ; None ; 0,5] → (1 + 0,5) / 2 = 0,75 et `None` quand toutes les valeurs sont indéfinies. Les deux autres tests de la classe, sur les nombres et la fidélité, attendent l'étape 4.
