# Étape 2 — Nombres et chaînes

> Palier 02, étape 2 sur 8 · Précédent : [Étape 1 — Le contrôle de type](<01-Controle-de-type.md>) · Suivant : [Étape 3 — Objets et récursion](<03-Objets-et-recursion.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** ajouter à `validate` les contraintes des nombres (`minimum`, `maximum`, `exclusiveMinimum`, et le refus de NaN) puis celles des chaînes (`minLength`, `maxLength`, `pattern`). Les tests `test_decimal_refuse_comme_entier_et_nan_refuse`, `test_bornes_numeriques` et `test_chaines` passent à la fin.

## Comment raisonner

Le type est maintenant garanti, ou absent. On sait donc, à cet endroit du code, qu'une instance qui ressemble à un nombre peut être comparée à un nombre. On range les contraintes **par famille de valeur** : chaque mot-clé ne s'applique qu'à un genre d'instance (`minimum` aux nombres, `minLength` aux chaînes), et un mot-clé qui ne s'applique pas est simplement ignoré. Cela donne une suite de branches `if … elif …` sur la nature de l'instance, une par famille.

Dans une branche, on veut **toutes** les erreurs, pas la première : chaque contrainte a son propre `if`, sans `elif` entre elles, et chacune ajoute son message à la liste.

Une exception à cette règle : une valeur qui n'est pas un nombre fini (NaN ou l'infini). Elle n'a pas de sens en JSON, et la comparer à des bornes donnerait des réponses absurdes. On la refuse tout de suite, comme un type faux.

## Le piège de NaN

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`validate(instance, schema, path)`** — Dans ce brouillon réduit à la seule borne basse, la fonction ressemble à un gardien qui mesure la taille des visiteurs sans remarquer que l'un d'eux n'a pas de taille du tout : elle reçoit l'instance, le schéma et le chemin, et, si l'instance est un nombre qui n'est pas un booléen et que le schéma porte un `minimum`, ajoute une erreur quand le nombre est strictement en dessous. Elle renvoie la liste des erreurs, mais comme toute comparaison avec NaN est fausse, un `float("nan")` contre un minimum de 0 passe sans protester et la liste reste vide ; c'est le piège que la version suivante ferme.

```python
# [extrait] brouillon
def validate(instance, schema: dict, path: str = "$") -> list[str]:
    erreurs = []
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            erreurs.append(f"{path} : {instance} < minimum {schema['minimum']}")
    return erreurs
```

Ce brouillon teste bien la borne. Mais toute comparaison avec NaN (« not a number ») vaut faux : `nan < 0` est faux, `nan > 300` aussi. NaN passe donc **toutes** les bornes :

```text
# [extrait] console
>>> import json
>>> json.loads('{"montant_aed": NaN}')
{'montant_aed': nan}
>>> validate(float("nan"), {"type": "number", "minimum": 0})        # avec le brouillon
[]
```

La première ligne montre que le risque est réel : le module `json` de Python accepte par défaut `NaN` et `Infinity`, qui ne sont pourtant pas du JSON valide. Un modèle qui écrit `NaN` produit donc un montant que le validateur naïf laisse passer, et que tout calcul suivant propage. Java a le même comportement avec `Double.NaN` : `Double.NaN < 0` vaut `false`.

## La branche des nombres

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`validate(instance, schema, path)`** — C'est la fonction de l'étape 1, à laquelle on ajoute le guichet des nombres, tenu par un métrologue qui vérifie d'abord que la mesure existe avant de la comparer aux bornes : pour une instance numérique qui n'est pas un booléen, elle renvoie aussitôt une seule erreur « nombre non fini » si la valeur est NaN ou infinie, puis teste, chacun par un `if` indépendant, le `minimum` inclus, le `maximum` inclus et l'`exclusiveMinimum` exclu, en ajoutant un message par borne violée. Elle renvoie la liste ainsi remplie : avec des bornes 1 et 300, la valeur 301 donne « 301 > maximum 300 », 0 donne « 0 < minimum 1 », 300 passe, et, sans type, 0 contre un `exclusiveMinimum` de 0 donne « 0 doit être > 0 ».

```python
# [extrait] agent/schemas.py
def validate(instance, schema: dict, path: str = "$") -> list[str]:
    ...
    erreurs = []
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if not math.isfinite(instance):
            return [f"{path} : nombre non fini ({instance}), interdit en JSON"]
        if "minimum" in schema and instance < schema["minimum"]:
            erreurs.append(f"{path} : {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            erreurs.append(f"{path} : {instance} > maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            erreurs.append(f"{path} : {instance} doit être > {schema['exclusiveMinimum']}")
    ...
    return erreurs
```

**`if isinstance(instance, (int, float)) and not isinstance(instance, bool):`** La condition d'entrée de la branche répète l'exclusion du booléen. C'est nécessaire : quand le schéma n'a pas de `type`, l'étape 1 n'a rien contrôlé, et `True` arriverait ici comme un entier.

**`if not math.isfinite(instance): return [...]`.** `math.isfinite` est faux pour NaN, l'infini et moins l'infini. On rend aussitôt une seule erreur, comme pour un type faux. Le message affiche la valeur (`nan`, `inf`), ce qui aide le modèle à comprendre.

**Les trois bornes, trois `if` indépendants.**

- `instance < schema["minimum"]` : le minimum est **inclus**, on n'a une erreur que strictement en dessous.
- `instance > schema["maximum"]` : le maximum est inclus aussi ; 300 est accepté pour un maximum de 300.
- `instance <= schema["exclusiveMinimum"]` : la borne est **exclue**, 0 est refusé pour `exclusiveMinimum` 0. C'est ainsi qu'on écrit « strictement positif » pour un montant, l'équivalent de `@Positive` en Bean Validation.

**`"minimum" in schema`.** On teste la présence de la clé avant de la lire ; `schema["minimum"]` sur une clé absente lèverait `KeyError`. Les f-strings recopient la borne telle qu'elle est écrite dans le schéma.

**Le piège classique.** Écrire `elif` entre les bornes : un nombre qui viole deux contraintes (par exemple un `minimum` et un `exclusiveMinimum`) n'en signalerait qu'une, et le modèle corrigerait en deux relances au lieu d'une.

**Vérifier à la main.** Avec N = `{"type": "integer", "minimum": 1, "maximum": 300}` : 301 > 300 donne `$ : 301 > maximum 300` ; 0 < 1 donne `$ : 0 < minimum 1` ; 300 ne viole rien, la liste est vide. Sans type, `validate(0, {"exclusiveMinimum": 0})` : 0 ≤ 0, donc `$ : 0 doit être > 0`.

```powershell
python -m unittest -v tests.test_02_schemas.TestValidateContraintes.test_bornes_numeriques tests.test_02_schemas.TestValidateTypes.test_decimal_refuse_comme_entier_et_nan_refuse
```

Le second test vérifie que `36.0` est refusé comme entier (le contrôle de type de l'étape 1) et que NaN donne `$ : nombre non fini (nan), interdit en JSON`.

## La branche des chaînes

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`validate(instance, schema, path)`** — C'est toujours la même fonction, qui ouvre maintenant, juste après celui des nombres, le guichet des chaînes, tenu par un typographe qui compte les lettres et compare l'écriture à un modèle : pour une instance de type `str`, elle ajoute une erreur si la longueur, comptée en caractères, est sous `minLength` ou au-dessus de `maxLength`, puis une autre si `re.search` ne trouve aucune correspondance du motif `pattern`, en affichant la chaîne avec ses apostrophes. Elle renvoie la liste complète : avec les longueurs 1 et 3 et le motif des majuscules, la chaîne vide reçoit deux erreurs, longueur puis motif, et `"ABCD"` une seule, sa longueur 4 dépassant 3.

```python
# [extrait] agent/schemas.py
def validate(instance, schema: dict, path: str = "$") -> list[str]:
    ...
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        ...
    elif isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            erreurs.append(f"{path} : longueur {len(instance)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            erreurs.append(f"{path} : longueur {len(instance)} > maxLength {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            erreurs.append(f"{path} : {instance!r} ne respecte pas le motif {schema['pattern']}")
    ...
    return erreurs
```

**`elif isinstance(instance, str):`** Une instance est un nombre **ou** une chaîne, jamais les deux : `elif` convient ici, entre les familles, alors qu'il ne convenait pas entre les contraintes d'une même famille.

**`len(instance)`** compte des caractères, pas des octets : « é » compte pour 1, un mot arabe compte ses lettres. C'est ce qu'attend JSON Schema, et c'est la différence avec un `getBytes().length` en Java.

**`re.search(schema["pattern"], instance) is None`.** JSON Schema dit qu'un motif doit trouver une correspondance **quelque part** dans la chaîne : c'est `re.search`, et non `re.match` (qui n'essaie qu'au début) ni `re.fullmatch`. Pour exiger la chaîne entière, le motif lui-même commence par `^` et finit par `$`, comme `MOTIF_EMIRATES_ID`. `re.search` rend un objet de correspondance ou `None` ; `is None` est la façon idiomatique de tester `None`, comme `== null` en Java.

**`{instance!r}`.** Le suffixe `!r` affiche la représentation de la valeur, avec ses guillemets : la chaîne vide s'affiche `''`, alors qu'elle serait invisible sans eux.

**Vérifier à la main.** Schéma `{"type": "string", "minLength": 1, "maxLength": 3, "pattern": "^[A-Z]+$"}`. La chaîne vide : longueur 0 < 1, première erreur ; le motif exige au moins une majuscule, seconde erreur. `"ABCD"` : longueur 4 > 3, une erreur ; le motif est respecté.

**Une limite de Python à connaître.** En Python, `$` accepte aussi la position juste avant un saut de ligne final : `re.search(MOTIF_EMIRATES_ID, "784-1990-1234567-1\n")` trouve une correspondance. JSON Schema suit les expressions régulières de JavaScript, où ce n'est pas le cas. Pour être strict, on écrirait `\Z` à la place de `$` ; le cours garde `$`, la forme que l'API accepte en mode strict.

## Les tests qui passent maintenant

```powershell
python -m unittest -v tests.test_02_schemas.TestValidateContraintes.test_chaines
```

À ce stade, cinq tests du palier sont verts : `test_booleen_n_est_pas_un_entier`, `test_mot_cle_inconnu_refuse`, `test_decimal_refuse_comme_entier_et_nan_refuse`, `test_bornes_numeriques` et `test_chaines`. Les objets arrivent à l'étape 3.

## Ce qu'il faut retenir

- Un `if` par contrainte dans une famille (on veut toutes les erreurs), un `elif` entre familles (une valeur n'en a qu'une).
- NaN passe toutes les comparaisons : `math.isfinite` le refuse avant les bornes.
- `minimum` et `maximum` sont inclus, `exclusiveMinimum` est exclu ; un motif se cherche avec `re.search`.

> Suivant : [Étape 3 — Objets et récursion](<03-Objets-et-recursion.md>)
