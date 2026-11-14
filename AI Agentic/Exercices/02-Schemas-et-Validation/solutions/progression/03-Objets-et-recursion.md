# Étape 3 — Objets et récursion

> Palier 02, étape 3 sur 8 · Précédent : [Étape 2 — Nombres et chaînes](<02-Nombres-et-chaines.md>) · Suivant : [Étape 4 — Le schéma strict pour l'API](<04-Schema-strict-pour-l-API.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** terminer `validate` avec la branche des objets (champs obligatoires, validation récursive avec le chemin, champs non prévus), puis écrire `objet` et lire le schéma de la demande de crédit. Les sept tests de `TestValidateTypes` et `TestValidateContraintes` passent, ainsi que `test_objet`.

## Comment raisonner

Un objet JSON est un dictionnaire dont **chaque valeur** a son propre sous-schéma, rangé sous `properties`. Valider un objet, c'est donc valider chaque champ contre son sous-schéma, c'est-à-dire appeler `validate` sur lui-même : la fonction devient **récursive**. C'est ce qui lui permettra plus tard de valider un objet dans un objet sans une ligne de plus.

Trois questions se posent au niveau de l'objet lui-même, et chacune donne une ligne :

1. les champs **obligatoires** (`required`) sont-ils tous présents ?
2. chaque champ présent et décrit est-il valide ? (récursion, avec un chemin prolongé)
3. un champ présent mais **non décrit** est-il permis ? (`additionalProperties`)

Le chemin est la pièce qui fait la valeur du validateur pour un agent. Sans lui, le modèle lirait « 6 < minimum 12 » sans savoir de quel champ il s'agit. Avec lui, il lit `$.duree_mois : 6 < minimum 12` et sait exactement quoi corriger. La règle de construction est simple : quand on descend dans le champ `cle`, le chemin devient `path + "." + cle`.

## La branche des objets

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`validate(instance, schema, path)`** — C'est la fonction des étapes 1 et 2, qui reçoit maintenant son dernier guichet, celui des objets, tenu par un inspecteur qui fait l'appel des présents puis délègue chaque pièce du dossier à un collègue, lui-même : pour un dictionnaire, elle ajoute d'abord un message « champ obligatoire absent » par nom de `required` manquant, dans l'ordre de `required`, puis parcourt les champs de l'instance dans leur ordre d'écriture. Un champ décrit dans `properties` est validé par un appel récursif avec le chemin prolongé, `$` devenant `$.duree_mois` ; un champ non décrit est signalé « champ non prévu » seulement si `additionalProperties` vaut exactement `False`. Elle renvoie la liste accumulée : la demande de crédit sans `emirates_id`, avec une durée de 6 et un champ `commentaire`, donne trois erreurs dans cet ordre.

```python
# [extrait] agent/schemas.py
def validate(instance, schema: dict, path: str = "$") -> list[str]:
    ...
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        ...
    elif isinstance(instance, str):
        ...
    elif isinstance(instance, dict):
        proprietes = schema.get("properties", {})
        erreurs += [f"{path} : champ obligatoire absent « {c} »" for c in schema.get("required", []) if c not in instance]
        for cle, valeur in instance.items():
            if cle in proprietes:
                erreurs += validate(valeur, proprietes[cle], f"{path}.{cle}")
            elif schema.get("additionalProperties", True) is False:
                erreurs.append(f"{path} : champ non prévu « {cle} »")
    return erreurs
```

**`proprietes = schema.get("properties", {})`.** Le deuxième argument de `get` est la valeur rendue si la clé manque : un schéma d'objet sans `properties` ne décrit aucun champ. C'est `map.getOrDefault("properties", Map.of())` en Java.

**La ligne des champs obligatoires.** C'est une compréhension de liste avec un filtre : pour chaque nom `c` de `required` (une liste vide si le mot-clé manque), **si** `c` n'est pas une clé de l'instance, on produit un message. `c not in instance` teste la présence d'une clé dans un dictionnaire, comme `!map.containsKey(c)`. `erreurs += [...]` ajoute tous ces messages d'un coup à la liste, comme `addAll`. Les messages sortent dans l'ordre de `required`.

**`for cle, valeur in instance.items():`** On parcourt les paires (clé, valeur) de l'instance, comme `for (Map.Entry e : map.entrySet())`. Depuis Python 3.7, un dictionnaire garde l'ordre d'insertion, et `json.loads` insère les clés dans l'ordre du texte : les erreurs sortent donc dans l'ordre où le modèle a écrit les champs, de façon reproductible. En Java, il faudrait une `LinkedHashMap` pour la même garantie.

**`erreurs += validate(valeur, proprietes[cle], f"{path}.{cle}")`.** L'appel récursif. Il reçoit la valeur du champ, son sous-schéma, et le chemin prolongé : `$` devient `$.duree_mois`. Tout ce que les étapes 1 et 2 ont écrit (type, NaN, bornes, longueurs, motif) s'applique au champ sans être réécrit. Si la valeur est elle-même un objet, la récursion descend encore et le chemin devient `$.client.revenu`.

**`elif schema.get("additionalProperties", True) is False:`** Le champ n'est pas décrit. Par défaut, JSON Schema accepte les champs supplémentaires : d'où la valeur par défaut `True`. On ne refuse que si le schéma dit explicitement `False`. On écrit `is False` et non `not ...` : dans JSON Schema, `additionalProperties` peut aussi être un sous-schéma (un dictionnaire), qu'il ne faut pas confondre avec un refus ; `is False` ne reconnaît que le booléen `False` lui-même.

**`return erreurs`.** La liste accumulée par les trois branches. Une instance qui n'est ni un nombre, ni une chaîne, ni un objet (une liste, `None` sans `type` imposé) traverse toutes les branches sans erreur : le validateur ne gère pas les tableaux (c'est le défi 3 de l'énoncé).

**Le piège classique : oublier de prolonger le chemin.** Si l'on écrit `validate(valeur, proprietes[cle])`, chaque appel récursif repart avec le chemin par défaut `$`, et toutes les erreurs disent `$ : 6 < minimum 12`. Les tests comparent les chemins exacts et échouent ; le modèle, lui, ne saurait plus quel champ corriger.

**Vérifier à la main.** La demande correcte, avec la durée mise à 6, un champ `commentaire` ajouté et `emirates_id` retiré, contre `SCHEMA_DEMANDE_CREDIT`. Les champs obligatoires d'abord : `emirates_id` manque. Puis l'instance dans son ordre : `montant_aed` (150 000 > 0, rien), `duree_mois` (récursion : 6 < 12, `$.duree_mois : 6 < minimum 12`), `revenu_mensuel_aed` (rien), `commentaire` (non décrit, `additionalProperties` vaut `False`). Trois erreurs, dans cet ordre, comme l'attend le test.

## La fabrique objet

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`objet(proprietes)`** — Cette fabrique est le notaire qui transforme une liste de clauses en contrat fermé, sans oubli possible : elle reçoit le dictionnaire des propriétés, chaque nom de champ associé à son sous-schéma, et renvoie un nouveau dictionnaire de quatre clés, `type` à `"object"`, `properties` qui reprend ce dictionnaire, `required` qui liste tous les noms de champs dans leur ordre d'insertion, et `additionalProperties` à `False`. Elle écrit une fois pour toutes la forme stricte qu'exigent les outils et le mode strict de l'API ; les paliers 04, 07 et 09 l'utiliseront pour chaque outil, et `objet(SCHEMA_DEMANDE_CREDIT["properties"])` redonne exactement le schéma de la demande de crédit.

```python
# [extrait] agent/schemas.py
def objet(proprietes: dict) -> dict:
    """Schéma d'objet strict : tous les champs obligatoires, aucun champ non prévu.

    Exemple : `objet({"x": {"type": "number"}})` vaut {"type": "object", "properties": {"x": {"type":
    "number"}}, "required": ["x"], "additionalProperties": False}.
    """
    return {"type": "object", "properties": proprietes, "required": list(proprietes), "additionalProperties": False}
```

**Pourquoi une fabrique.** Les schémas d'arguments d'outils sont presque tous de la même forme : un objet, tous ses champs obligatoires, aucun champ en plus. C'est aussi ce qu'exige le mode strict de l'API. Écrire ces quatre clés à la main pour chaque outil, c'est risquer d'oublier `additionalProperties` une fois sur dix. `objet` les écrit une fois pour toutes ; les paliers 04, 07 et 09 l'utiliseront pour chaque outil.

**`list(proprietes)`.** Itérer sur un dictionnaire donne ses clés, dans l'ordre d'insertion : `list(...)` en fait la liste des noms de champs. C'est `new ArrayList<>(map.keySet())` sur une `LinkedHashMap`.

## Le schéma de la demande de crédit

```python
# [extrait] agent/schemas.py
MOTIF_EMIRATES_ID = "^784-[0-9]{4}-[0-9]{7}-[0-9]$"
SCHEMA_DEMANDE_CREDIT = {                      # écrit en toutes lettres : c'est ce que rendrait objet({...})
    "type": "object",
    "properties": {
        "montant_aed": {"type": "number", "exclusiveMinimum": 0},
        "duree_mois": {"type": "integer", "minimum": 12, "maximum": 300},
        "revenu_mensuel_aed": {"type": "number", "exclusiveMinimum": 0},
        "emirates_id": {"type": "string", "pattern": MOTIF_EMIRATES_ID},
    },
    "required": ["montant_aed", "duree_mois", "revenu_mensuel_aed", "emirates_id"],
    "additionalProperties": False,
}
```

Ces lignes sont fournies dans le squelette. On les lit comme un contrat :

- `montant_aed` et `revenu_mensuel_aed` : des nombres strictement positifs, en AED ;
- `duree_mois` : un entier de 12 à 300 mois inclus (bornes illustratives) ;
- `emirates_id` : une chaîne au format `784-AAAA-NNNNNNN-C`. Le motif `^784-[0-9]{4}-[0-9]{7}-[0-9]$` se lit : début, `784`, tiret, quatre chiffres (l'année de naissance), tiret, sept chiffres, tiret, un chiffre de contrôle, fin. Il vérifie le **format**, pas l'existence du numéro ni son chiffre de contrôle ;
- `required` et `additionalProperties` : la forme stricte, celle que rend `objet`.

Le schéma est écrit en toutes lettres plutôt qu'avec `objet(...)` pour que tu voies un JSON Schema complet ; le test `test_objet` vérifie que `objet(SCHEMA_DEMANDE_CREDIT["properties"])` lui est égal. En Java, ce contrat s'écrirait comme un `record DemandeCredit` avec `@Positive`, `@Min(12) @Max(300)` et `@Pattern(regexp = "^784-…$")`.

## Les tests qui passent maintenant

```powershell
python -m unittest -v tests.test_02_schemas.TestValidateTypes tests.test_02_schemas.TestValidateContraintes tests.test_02_schemas.TestSchemaStrict.test_objet
```

Huit tests verts : les quatre de `TestValidateTypes` (dont `test_type_faux_avec_chemin`, qui attend `$.n_mois : type attendu integer, reçu string`), les trois de `TestValidateContraintes` (dont `test_objet_champs_absents_et_non_prevus`) et `test_objet`. La fonction `validate` est complète.

## Ce qu'il faut retenir

- Un objet se valide champ par champ, par récursion : tout ce qui a été écrit pour un nombre ou une chaîne s'applique à chaque champ.
- Le chemin se prolonge à chaque descente (`$` puis `$.duree_mois`) : c'est lui qui dit au modèle quoi corriger.
- `objet` écrit une fois pour toutes la forme stricte : tous les champs obligatoires, aucun champ en plus.

> Suivant : [Étape 4 — Le schéma strict pour l'API](<04-Schema-strict-pour-l-API.md>)
