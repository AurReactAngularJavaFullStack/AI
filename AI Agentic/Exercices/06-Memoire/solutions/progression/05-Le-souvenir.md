# Étape 5 — Le souvenir

> Progression du palier 06 · Précédent : [Étape 4 — Le score de pertinence](<04-Le-score-de-pertinence.md>) · Suivant : [Étape 6 — Rappeler](<06-Rappeler.md>) · Retour à l'énoncé : [README du palier 06](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Avant d'écrire `rappeler`, il faut l'objet qu'elle manipule. On part des trois composantes du score et de ce que chacune demande de stocker.

- La **similarité** se calcule à partir du **texte** : on le plonge au moment du rappel, avec la fonction injectée.
- La **récence** se calcule à partir de l'âge, donc du **jour du dernier accès**. On ne stocke pas l'âge : il change chaque jour, alors que le jour d'accès ne change qu'à la relecture.
- L'**importance** est une note fixée à l'écriture du souvenir, de 1 à 10.

Trois champs, donc. Le souvenir est une donnée, sans comportement. En Java, on penserait à un `record`, et Python a l'équivalent : la `dataclass`. Mais une question décide de sa forme exacte : **le souvenir change-t-il après sa création ?** Oui. `rappeler` le relit, et son jour d'accès passe au jour courant. Il ne peut donc pas être immuable.

Enfin, l'importance a un domaine : de 1 à 10. On la vérifie à la construction, pour qu'un souvenir invalide ne puisse jamais exister. C'est le rôle que joue le constructeur compact d'un `record` Java.

## Un brouillon immuable

```python
# [extrait] brouillon
from dataclasses import dataclass


@dataclass(frozen=True)                    # comme un record Java : immuable
class Souvenir:
    texte: str
    jour_acces: float
    importance: int
```

Ce brouillon a l'air propre, et c'est le réflexe d'un développeur Java, pour qui un `record` est immuable. Mais au moment de la relecture, `s.jour_acces = jour` lève `dataclasses.FrozenInstanceError` : le souvenir ne peut pas être remis à neuf. Il faudrait alors fabriquer une copie avec `dataclasses.replace(s, jour_acces=jour)`, puis remplacer l'ancien souvenir dans la mémoire de l'appelant, ce que `rappeler` ne peut pas faire : elle ne reçoit qu'une liste. Le test `test_relire_remet_l_horloge_a_zero` vérifie justement que les objets **de l'appelant** ont changé. Le brouillon oublie aussi de contrôler l'importance.

## La dataclass et son contrôle

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Souvenir.__post_init__()`** — Cette méthode est l'archiviste qui, au moment où la fiche entre dans le classeur, vérifie que la note d'importance griffonnée en haut est lisible : elle ne reçoit rien d'autre que le souvenir que le constructeur généré par `@dataclass` vient de remplir avec son texte, son jour de dernier accès et son importance, et lève `ValueError` (« importance de 1 (banal) à 10 (crucial) ») si cette importance n'est pas comprise entre 1 et 10, bornes incluses. Elle ne renvoie rien et ne contrôle pas le jour d'accès, qui ne peut être jugé que par rapport au jour courant ; le souvenir du salaire, au jour 85 et d'importance 9, est accepté, et `Souvenir("x", 0.0, 11)` échoue dès sa construction.

```python
# [extrait] agent/memoire.py
@dataclass
class Souvenir:
    """Un souvenir : son texte, le jour de son dernier accès (horloge simulée), son importance de 1 à 10.

    Exemple : `Souvenir("Salaire mensuel déclaré : 40 000 AED", 85.0, 9)`.
    """
    texte: str
    jour_acces: float
    importance: int

    def __post_init__(self) -> None:
        if not 1 <= self.importance <= 10:
            raise ValueError("importance de 1 (banal) à 10 (crucial)")
```

**`@dataclass`.** Le décorateur lit les annotations de la classe et génère `__init__`, `__repr__` et `__eq__`. C'est ce que fait un `record` Java, ou Lombok avec `@Data`. `Souvenir("…", 85.0, 9)` appelle le `__init__` généré, qui range les trois valeurs dans `self.texte`, `self.jour_acces` et `self.importance`.

**Les trois champs.** `texte: str`, `jour_acces: float` et `importance: int`, dans cet ordre : c'est l'ordre des arguments positionnels du constructeur. `jour_acces` est un `float`, parce que l'horloge simulée du palier 01 compte en jours fractionnaires : `Horloge.jour()` rend t / 86 400.

**`__post_init__`.** La dataclass appelle cette méthode juste après le `__init__` généré, une fois les champs remplis. C'est le seul endroit où l'on peut ajouter une validation sans réécrire le constructeur, l'équivalent du constructeur compact d'un `record` Java :

```text
# [extrait] console
>>> from agent.memoire import Souvenir
>>> Souvenir("Salaire mensuel déclaré : 40 000 AED", 85.0, 9)
Souvenir(texte='Salaire mensuel déclaré : 40 000 AED', jour_acces=85.0, importance=9)
>>> Souvenir("x", 0.0, 11)
Traceback (most recent call last):
  ...
ValueError: importance de 1 (banal) à 10 (crucial)
```

**`if not 1 <= self.importance <= 10`.** L'encadrement chaîné, bornes incluses : 1 et 10 sont permis, 0 et 11 ne le sont pas. Le message rappelle l'échelle, et dit à celui qui écrit le souvenir ce que veulent dire les bornes.

**Pourquoi ne pas valider `jour_acces` ici ?** Parce qu'un jour d'accès n'est faux que **par rapport** au jour courant, que le souvenir ne connaît pas. C'est `recence` qui refuse un âge négatif au moment du rappel (étape 3).

**Le piège classique.** Écrire la validation dans un `__init__` à la main. On perd alors le constructeur généré, et il faut tout réécrire. Avec une `dataclass`, la validation va dans `__post_init__`. L'autre piège est celui du brouillon : geler la dataclass alors que la relecture la modifie.

## Le test qui passe maintenant

Aucune classe de tests ne porte sur le souvenir seul : le refus de l'importance 11 est la dernière vérification de `TestRappeler.test_cas_limites_et_erreurs`, qui commence par appeler `rappeler`. La vérification de cette étape est donc la console ci-dessus. Lance quand même la classe pour voir l'état :

```text
python -m unittest -v tests.test_06_memoire.TestRappeler
```

Les quatre tests échouent encore par `NotImplementedError`, mais plus dans `souvenirs()` : ils échouent maintenant dans `rappeler`. Les souvenirs se construisent, et il ne reste qu'une fonction à écrire.
