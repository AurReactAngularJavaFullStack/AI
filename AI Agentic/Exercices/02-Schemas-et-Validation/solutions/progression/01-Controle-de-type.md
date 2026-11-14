# Étape 1 — Le contrôle de type

> Palier 02, étape 1 sur 8 · Précédent : aucun · Suivant : [Étape 2 — Nombres et chaînes](<02-Nombres-et-chaines.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** poser les constantes du module, puis écrire le début de `validate` : le refus d'un mot-clé inconnu et le contrôle de type. Les tests `test_booleen_n_est_pas_un_entier` et `test_mot_cle_inconnu_refuse` passent à la fin.

## Comment raisonner

Avant d'écrire `validate`, on fixe son **contrat de sortie**, parce que tout le reste en découle. Deux choix sont possibles :

- lever une exception à la première erreur, comme un `if` qui jette `IllegalArgumentException` ;
- rendre la **liste de toutes les erreurs**, chacune avec l'endroit où elle se trouve.

On choisit la liste. La raison est propre aux agents : les erreurs repartent vers le modèle, dans la boucle de réparation. Si l'on n'en signale qu'une à la fois, un JSON qui a trois défauts coûte trois relances ; avec la liste complète, une seule relance peut tout corriger. C'est aussi ce que fait Bean Validation en Java : `validator.validate(objet)` rend un `Set<ConstraintViolation>`, chaque violation portant son chemin (`propertyPath`).

Le chemin a une syntaxe : `$` désigne la racine, `$.duree_mois` le champ `duree_mois`. D'où la signature : `validate(instance, schema, path="$")` rend une `list[str]`, vide si tout va bien. Le paramètre `path` a une valeur par défaut parce que l'appelant ne le donne jamais ; c'est la récursion de l'étape 3 qui le prolongera.

Ensuite, on écrit les contrôles dans l'ordre où ils **coupent court** : d'abord ce qui rend le schéma inutilisable (un mot-clé inconnu), puis ce qui rend l'instance incomparable (un type faux), et seulement après les contraintes fines (bornes, longueurs, champs), aux étapes 2 et 3.

## L'en-tête et les constantes

```python
# [extrait] agent/schemas.py
import json
import math
import re

MOTS_CLES = {"type", "properties", "required", "additionalProperties", "minimum", "maximum", "exclusiveMinimum",
             "minLength", "maxLength", "pattern", "description"}
TYPES = {"object": (dict,), "string": (str,), "number": (int, float), "integer": (int,)}
NOMS_JSON = {bool: "boolean", int: "integer", float: "number", str: "string", list: "array", dict: "object"}
```

Ces lignes sont fournies dans le squelette ; il faut pourtant savoir les réécrire de tête.

**Les imports.** `json` lira le texte du modèle (étape 5), `math` refusera NaN (étape 2), `re` appliquera les motifs (étape 2).

**`MOTS_CLES`** est un `set` (accolades sans deux-points) : les onze mots-clés que le validateur sait appliquer. `description` y figure alors qu'il ne contraint rien, parce que les schémas en contiennent (l'étape 4 en ajoute) et qu'il ne doit pas être pris pour un mot-clé inconnu.

**`TYPES`** associe chaque type JSON aux classes Python qui le représentent après `json.loads`. Un `number` JSON devient un `int` ou un `float` ; un `integer` JSON, seulement un `int`. Les valeurs sont des tuples parce que `isinstance` accepte un tuple de classes : `isinstance(x, (int, float))` veut dire « x est un `int` ou un `float` ».

**`NOMS_JSON`** fait le chemin inverse, pour les messages : la classe Python exacte d'une valeur donne son nom JSON. `None` n'y est pas : on le traitera par une valeur par défaut, `"null"`.

## Le piège du booléen

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`validate(instance, schema, path)`** — Dans ce brouillon, la fonction est un contrôleur qui ne regarde que la couleur du badge sans vérifier la photo : elle reçoit l'instance, le schéma et le chemin, `"$"` par défaut, lit le `type` éventuellement imposé et, si l'instance n'est d'aucune des classes Python que `TYPES` associe à ce type, renvoie une liste d'une seule erreur qui nomme le type attendu et le type reçu ; sinon elle renvoie la liste vide. Comme `bool` est une sous-classe de `int`, elle laisse passer `True` pour un entier, et elle ignore en silence tout mot-clé inconnu, comme `multipleOf`, deux défauts que corrige la version suivante.

```python
# [extrait] brouillon
def validate(instance, schema: dict, path: str = "$") -> list[str]:
    attendu = schema.get("type")
    if attendu and not isinstance(instance, TYPES[attendu]):
        return [f"{path} : type attendu {attendu}, reçu {NOMS_JSON.get(type(instance), 'null')}"]
    return []
```

Ce brouillon a l'air complet pour le type. Il laisse pourtant passer `true` comme un entier :

```text
# [extrait] console
>>> isinstance(True, int)
True
>>> True + 1
2
>>> validate(True, {"type": "integer"})          # avec le brouillon
[]
```

En Python, `bool` est une sous-classe de `int` : `True` vaut 1 et `False` vaut 0. Pour `isinstance`, un booléen **est** un entier. En Java, `boolean` et `int` sont des types sans rapport et le compilateur refuserait le mélange ; ici, rien ne le signale. Pour un agent bancaire, la conséquence est concrète : un modèle qui écrit `"revenu_mensuel_aed": true` produirait un revenu de 1 AED. Le brouillon a un second défaut : il ignore en silence un mot-clé qu'il ne connaît pas, comme `multipleOf`, si bien qu'une contrainte écrite dans le schéma ne serait jamais vérifiée.

## Le début de validate

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`validate(instance, schema, path)`** — C'est la même fonction que dans le brouillon, mais elle commence désormais comme un douanier qui vérifie d'abord que son propre règlement est lisible : elle reçoit l'instance, le schéma et le chemin, calcule l'ensemble des clés du schéma absentes de `MOTS_CLES` et lève `ValueError` avec leur liste triée s'il y en a, puis, quand le schéma impose un type, refuse aussitôt un booléen ou une instance d'une autre classe en renvoyant une liste d'une seule erreur. Sinon elle prépare la liste `erreurs`, que les étapes 2 et 3 rempliront, et la renvoie ; à ce stade, `validate(True, {"type": "integer"})` signale un booléen reçu là où l'on attendait un entier, et `None` contre `number` donne « reçu null ».

```python
# [extrait] agent/schemas.py
def validate(instance, schema: dict, path: str = "$") -> list[str]:
    ...
    inconnus = set(schema) - MOTS_CLES
    if inconnus:
        raise ValueError(f"mots-clés non pris en charge : {sorted(inconnus)}")   # refuser plutôt qu'ignorer
    attendu = schema.get("type")
    if attendu and (isinstance(instance, bool) or not isinstance(instance, TYPES[attendu])):   # True n'est pas 1
        return [f"{path} : type attendu {attendu}, reçu {NOMS_JSON.get(type(instance), 'null')}"]
    erreurs = []
    ...
    return erreurs
```

Les lignes `...` remplacent la docstring (en haut) et les branches des étapes 2 et 3 (au milieu). Tu peux taper ce fragment tel quel : en Python, `...` est une instruction valide qui ne fait rien, et la fonction rend la liste vide quand le type est bon.

**`inconnus = set(schema) - MOTS_CLES`.** `set(schema)` est l'ensemble des clés du dictionnaire ; le `-` entre deux ensembles est la différence, ce qui reste après avoir retiré les mots connus. C'est `keys.removeAll(MOTS_CLES)` sur une copie, en Java.

**`raise ValueError(f"... {sorted(inconnus)}")`.** Un schéma qu'on ne sait pas appliquer est une erreur **du programmeur**, pas du modèle : on lève une exception au lieu de rendre une erreur de validation. `sorted` transforme l'ensemble en liste triée. Ce n'est pas cosmétique : l'ordre d'itération d'un ensemble de chaînes change d'une exécution à l'autre (Python mélange les hachages des chaînes à chaque lancement), et un message qui change d'ordre rend la sortie non reproductible.

**`attendu = schema.get("type")`.** `get` rend `None` si la clé est absente, comme `map.get` rend `null` en Java. Un schéma sans `type`, comme `{"exclusiveMinimum": 0}`, est permis : il n'impose aucun type.

**La condition de type, morceau par morceau.**

- `attendu and (...)` : si le schéma n'impose pas de type, Python n'évalue même pas la parenthèse (court-circuit, comme `&&`).
- `isinstance(instance, bool)` vient **avant** le test sur `TYPES` : un booléen est refusé quel que soit le type attendu, puisqu'aucun type de `TYPES` n'est `boolean`.
- `not isinstance(instance, TYPES[attendu])` : l'instance n'est d'aucune des classes acceptées. `36.0` est un `float`, donc refusé pour `integer` : l'étape 77 l'a voulu ainsi (l'étape 8 du cours est plus souple et l'accepte).

**`return [f"{path} : type attendu {attendu}, reçu {...}"]`.** On rend **tout de suite** une liste d'une seule erreur. Continuer n'aurait pas de sens : comparer la chaîne `"300"` à un maximum de 300 lèverait même `TypeError: '>' not supported between instances of 'str' and 'int'`. `type(instance)` donne la classe exacte (`bool` pour `True`, pas `int`), et `NOMS_JSON.get(..., 'null')` donne son nom JSON, ou `"null"` pour `None`, dont la classe `NoneType` n'est pas dans le dictionnaire.

**`erreurs = []` puis `return erreurs`.** La liste que les étapes 2 et 3 rempliront.

**Une limite à connaître.** `MOTS_CLES` contrôle les **clés** du schéma, pas les **valeurs** de `type`. Un schéma `{"type": "array"}` lève `KeyError: 'array'` sur `TYPES[attendu]`. Le validateur ne gère que quatre types JSON, ceux dont les outils de l'agent ont besoin.

## Les tests qui passent maintenant

```powershell
python -m unittest -v tests.test_02_schemas.TestValidateTypes.test_booleen_n_est_pas_un_entier tests.test_02_schemas.TestValidateTypes.test_mot_cle_inconnu_refuse
```

- `test_booleen_n_est_pas_un_entier` : `validate(True, {"type": "integer"})` rend `["$ : type attendu integer, reçu boolean"]`, et `validate(None, {"type": "number"})` rend `["$ : type attendu number, reçu null"]`.
- `test_mot_cle_inconnu_refuse` : `{"type": "integer", "multipleOf": 5}` lève `ValueError`.

Les deux autres tests de `TestValidateTypes` échouent encore : `test_decimal_refuse_comme_entier_et_nan_refuse` attend le refus de NaN (étape 2), et `test_type_faux_avec_chemin` utilise `objet` et un chemin `$.n_mois` (étape 3).

## Ce qu'il faut retenir

- `validate` rend la liste de **toutes** les erreurs, chacune avec son chemin : une seule relance peut tout corriger.
- Un mot-clé inconnu est une erreur de programmation : on lève `ValueError` plutôt que d'ignorer une contrainte.
- En Python, `True` est un `int` : on exclut les booléens **avant** de tester le type.
- Un type faux arrête la validation du nœud.

> Suivant : [Étape 2 — Nombres et chaînes](<02-Nombres-et-chaines.md>)
