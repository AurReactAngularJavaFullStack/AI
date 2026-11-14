# Étape 1 — L'outil et les exceptions

> Palier 04, étape 1 sur 7 · Précédent : [Énoncé du palier 04](<../../README.md>) · Suivant : [Étape 2 — Le registre et son décorateur](<02-Registre-et-decorateur.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Avant d'écrire un registre, décide ce qu'il range. Un outil, pour le modèle, c'est trois choses qu'il lit (un nom, une description, un schéma) ; pour le programme, c'est une quatrième chose qu'il exécute (une fonction). Ces quatre champs forment la donnée centrale du module : on l'écrit en premier.

Décide ensuite comment un appel peut échouer, et **qui** dit non. La politique d'accès (ce rôle n'a pas le droit), le schéma (ces arguments sont mal formés), l'outil lui-même (outil inconnu, refus d'un humain). Trois familles, donc trois exceptions. Les distinguer dès maintenant coûte trois lignes ; les confondre empêcherait plus tard de mesurer séparément les erreurs du modèle et celles des outils (palier 10), et de traiter un refus de politique autrement qu'un argument faux (palier 09).

Ces pièces sont fournies dans le squelette : cette étape est une étape de lecture, mais lis-la vraiment, tout le reste s'appuie dessus.

## Bloc 1 — Les imports et la donnée `Outil`

```python
# [extrait] agent/outils.py
import json
from collections.abc import Callable
from dataclasses import dataclass

from agent.metier import AED_PAR_USD, gratuite_fin_de_service, mensualite, ratio_endettement, tva
from agent.schemas import objet, schema_pour_api_strict, validate


@dataclass
class Outil:
    """Un outil enregistré : son nom public, sa description pour le modèle, son schéma, sa fonction."""
    nom: str
    description: str
    schema: dict
    fonction: Callable
```

**Les imports, en trois groupes.** D'abord la bibliothèque standard : `json` pour sérialiser les sorties (étape 6), `Callable` pour annoter « une fonction », `dataclass` pour la donnée. Ensuite les paliers antérieurs, et seulement eux : les calculs du palier 03, et trois pièces du palier 02 (`objet` pour écrire les schémas, `validate` pour la porte, `schema_pour_api_strict` pour l'API). Les dépendances vont toujours vers un palier plus ancien : `outils` connaît `metier`, jamais l'inverse. C'est la règle de dépendance de l'architecture hexagonale, que Maven ou Gradle t'imposeraient entre modules.

**`Callable` vient de `collections.abc`.** C'est l'emplacement recommandé depuis Python 3.9 ; `typing.Callable` existe encore mais n'est plus qu'un alias. Le cours n'utilise jamais les anciennes formes de `typing` (`List`, `Dict`) : on écrit `list[int]`, `dict[str, Outil]`.

**`@dataclass`.** Le décorateur lit les champs annotés de la classe et génère `__init__`, `__repr__` et `__eq__`. `Outil("tva", "TVA de 5 %", schema, outil_tva)` construit un objet dont `o.nom` vaut « tva ». C'est l'équivalent d'un `record` Java (ou d'une classe Lombok `@Value`), sans l'immutabilité par défaut ; on aurait pu écrire `@dataclass(frozen=True)`, mais personne ne modifie un `Outil` après sa création.

**Les quatre champs.** `nom` est l'identifiant stable que le modèle écrit dans son bloc `tool_use` ; `description` est la seule documentation qu'il lit avant de choisir ; `schema` est le contrat complet, bornes comprises, que la porte appliquera ; `fonction` est le code exécuté. Dans 77, ce dernier champ est annoté `object` ; `Callable` dit mieux ce qu'on attend.

## Bloc 2 — Trois exceptions, trois responsables

```python
# [extrait] agent/outils.py
class RefusPolitique(PermissionError):
    """La politique a dit non : l'outil n'est pas atteint (levée par les garde-fous, palier 09)."""


class ArgumentsInvalides(ValueError):
    """Le schéma a dit non : l'outil n'est pas atteint."""


class ErreurOutil(Exception):
    """L'outil lui-même refuse (outil inconnu, garde-fou interne, refus humain)."""
```

**Une classe sans corps.** La docstring suffit à former le corps d'une classe : pas besoin de `pass`. Chaque classe hérite tout de sa mère, y compris le constructeur qui prend un message : `ArgumentsInvalides("$.n : …")` fonctionne tel quel.

**Le choix des classes mères.** C'est la décision importante du bloc.

| Exception | Mère | Qui la lève, et quand | Analogie Java / Spring |
| --- | --- | --- | --- |
| `RefusPolitique` | `PermissionError` | les garde-fous, au palier 09, avant la validation | `AccessDeniedException` |
| `ArgumentsInvalides` | `ValueError` | la porte, quand le schéma refuse les arguments | `IllegalArgumentException`, ou `MethodArgumentNotValidException` derrière `@Valid` |
| `ErreurOutil` | `Exception` | `executer_appel` pour un outil inconnu, l'outil de virement au palier 09 | une exception métier maison |

Hériter de `ValueError` n'est pas décoratif : un code qui attrape déjà les erreurs de valeur (`except ValueError`) attrape aussi les arguments invalides, et le test `test_hierarchie_des_exceptions` vérifie cette parenté. Et comme le nom de la classe partira au modèle en tête du message d'erreur (étape 6), le modèle lira `ArgumentsInvalides: $.n_mois : …` et saura que c'est **son** appel qu'il doit corriger, et non l'outil qui est en panne.

**Le piège.** Lever partout `Exception("erreur")`. Le message part bien au modèle, mais plus personne ne peut distinguer, dans les journaux ou dans les métriques, une erreur de l'agent d'une panne de l'outil. L'étape 49 du cours en fait un cas d'usage : compter les erreurs de l'agent contre la disponibilité du serveur fait chercher une panne qui n'existe pas.

**Vérifier à la console.** Aucun test ne passe encore en entier : `test_hierarchie_des_exceptions` vérifie aussi la forme de l'erreur renvoyée par `executer_appel`, qui viendra à l'étape 6. Depuis `projet/` :

```text
python
>>> from agent.outils import ArgumentsInvalides, RefusPolitique, ErreurOutil
>>> issubclass(ArgumentsInvalides, ValueError), issubclass(RefusPolitique, PermissionError)
(True, True)
>>> str(ArgumentsInvalides("$.n : type attendu integer, reçu string"))
'$.n : type attendu integer, reçu string'
```

**Ce qu'il faut retenir.** Un outil, ce sont quatre champs : trois pour le modèle, un pour le programme. Chaque façon d'échouer a sa classe, rangée sous la bonne mère, parce que le nom de la classe est une information pour le modèle et pour l'exploitation.
