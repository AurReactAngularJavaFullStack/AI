# Étape 4 — Le schéma strict pour l'API

> Palier 02, étape 4 sur 8 · Précédent : [Étape 3 — Objets et récursion](<03-Objets-et-recursion.md>) · Suivant : [Étape 5 — Lire puis valider](<05-Lire-et-valider.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire `NON_STRICT` et `schema_pour_api_strict`. Les trois tests de `TestSchemaStrict` passent à la fin.

## Comment raisonner

Quand on déclare un outil à l'API avec `strict: True`, l'API contraint la génération du modèle pour que les arguments respectent **exactement** le schéma : bons types, champs obligatoires présents, aucun champ en plus. C'est une garantie précieuse, mais elle a une limite précise (étape 8 du cours) : le mode strict ne prend pas en charge les bornes numériques ni les longueurs de chaîne, et un schéma qui en contient est refusé avec une erreur 400.

Deux mauvaises réponses viennent à l'esprit : retirer les bornes de nos schémas (on perdrait la validation locale), ou renoncer au mode strict (on perdrait la garantie de forme). La bonne réponse garde les deux : on fabrique, **pour l'API seulement**, une copie du schéma sans les bornes, où elles sont recopiées dans la description, que le modèle lit comme une consigne ; et l'on garde le schéma complet pour `validate`, qui reste seule à vérifier ces bornes. C'est ce que font les assistants des SDK officiels.

Deux contraintes de conception en découlent : la fonction ne doit **jamais modifier** le schéma reçu (il sert encore à la validation locale), et elle doit descendre dans les `properties`, puisque les bornes sont presque toujours dans les sous-schémas des champs.

## Le brouillon qui détruit la validation locale

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`schema_pour_api_strict(schema)`** — Dans ce brouillon, la fonction se conduit comme un correcteur qui rature l'original au lieu de travailler sur une photocopie : elle reçoit un schéma, en retire avec `pop` chacun des cinq mots-clés de `NON_STRICT` présents au premier niveau seulement, puis renvoie ce même dictionnaire, modifié en place. Elle ne touche donc à aucune borne de `SCHEMA_DEMANDE_CREDIT`, rangées dans les sous-schémas des champs, si bien que l'API refuserait encore le schéma ; et, rendue récursive sur le même modèle, elle effacerait les bornes de la constante partagée, au point qu'une demande de 6 mois deviendrait valide en silence.

```python
# [extrait] brouillon
def schema_pour_api_strict(schema: dict) -> dict:
    for k in NON_STRICT:
        schema.pop(k, None)          # modifie le schéma reçu, et seulement au premier niveau
    return schema
```

Ce brouillon a deux défauts, et le second est grave.

- Il ne regarde que le premier niveau. Dans `SCHEMA_DEMANDE_CREDIT`, les bornes sont dans les sous-schémas de `montant_aed`, `duree_mois` et `revenu_mensuel_aed` : il n'en retire aucune, et l'API refuserait le schéma.
- Il modifie le dictionnaire **reçu**. Rendu récursif de la même façon, il retirerait les bornes de `SCHEMA_DEMANDE_CREDIT` lui-même, la constante partagée par tout le module : après un seul appel, `validate(demande_de_6_mois, SCHEMA_DEMANDE_CREDIT)` rendrait la liste vide, en silence. En Java, ce serait un service qui modifie la `Map` qu'on lui passe au lieu d'en renvoyer une copie : le bug apparaît loin de sa cause.

## La version correcte

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`schema_pour_api_strict(schema)`** — La version correcte travaille comme un traducteur qui recopie le règlement sur une feuille neuve et note en marge ce que le guichet de l'API ne sait pas lire : elle reçoit un schéma, construit un nouveau dictionnaire avec toutes ses clés sauf les cinq de `NON_STRICT` et `properties`, reconstruit ensuite `properties` en s'appelant elle-même sur chaque sous-schéma, puis, si ce niveau portait des bornes, écrit « Contraintes : k=v, k=v. » à la suite de la description existante. Elle renvoie cette copie et laisse l'original intact : la durée du schéma de crédit devient un entier décrit par « Contraintes : minimum=12, maximum=300. », tandis que `SCHEMA_DEMANDE_CREDIT` garde ses bornes pour `validate`.

```python
# [extrait] agent/schemas.py
NON_STRICT = ("minimum", "maximum", "exclusiveMinimum", "minLength", "maxLength")


def schema_pour_api_strict(schema: dict) -> dict:
    """Le mode strict de l'API refuse les bornes : on les retire et on les recopie dans la description.

    La validation locale (`validate`) reste la seule à vérifier ces bornes.
    Exemple : {"type": "integer", "minimum": 1, "maximum": 300} devient
    {"type": "integer", "description": "Contraintes : minimum=1, maximum=300."}.
    """
    copie = {k: v for k, v in schema.items() if k not in NON_STRICT and k != "properties"}
    if "properties" in schema:
        copie["properties"] = {nom: schema_pour_api_strict(sous) for nom, sous in schema["properties"].items()}
    retirees = [f"{k}={v}" for k, v in schema.items() if k in NON_STRICT]
    if retirees:
        copie["description"] = (schema.get("description", "") + " Contraintes : " + ", ".join(retirees) + ".").strip()
    return copie
```

**`NON_STRICT`.** Un tuple des cinq mots-clés refusés par le mode strict. `pattern` n'y est pas : l'API l'accepte pour des motifs simples comme celui de l'Emirates ID, qui reste donc dans le schéma envoyé.

**`copie = {k: v for k, v in schema.items() if ...}`.** Une compréhension de dictionnaire : un **nouveau** dictionnaire, construit avec les paires du schéma qui passent le filtre. C'est le cœur de la correction du brouillon : on ne touche jamais au schéma reçu. On écarte les bornes, et aussi `properties`, qu'on va reconstruire juste après. En Java : `schema.entrySet().stream().filter(...).collect(toMap(...))`.

**`copie["properties"] = {nom: schema_pour_api_strict(sous) ...}`.** S'il y a des champs, chacun de leurs sous-schémas passe à son tour dans la fonction : c'est la même récursion que `validate`, sur le schéma cette fois. Les bornes de `duree_mois` sont donc traitées quand la fonction est appelée sur le sous-schéma de `duree_mois`.

**`retirees = [f"{k}={v}" ...]`.** La liste des bornes de **ce** niveau, écrites `minimum=12`, dans l'ordre du schéma.

**La description.** S'il y avait des bornes, on écrit « Contraintes : minimum=12, maximum=300. » à la suite de la description existante (ou d'une chaîne vide). `", ".join(retirees)` met une virgule et une espace entre les bornes. Le `.strip()` final retire l'espace de tête quand il n'y avait pas de description : sans lui, on obtiendrait « ␣Contraintes : … ». Avec une description existante, « Montant HT. » devient « Montant HT. Contraintes : minLength=1. ».

**Un détail à connaître : la copie est superficielle.** Les valeurs qui ne sont pas reconstruites, comme la liste `required`, sont **partagées** entre le schéma et sa copie. C'est sans risque tant que personne ne modifie ces listes ; pour un schéma qu'on voudrait ensuite retoucher, `copy.deepcopy` serait plus sûr.

**L'ordre des clés change.** `properties` est recopiée en dernier : le schéma rendu affiche `type`, `required`, `additionalProperties`, puis `properties`. Deux dictionnaires sont égaux quel que soit l'ordre de leurs clés, et l'API ne s'en soucie pas.

**Vérifier à la main.** `objet({"n_mois": {"type": "integer", "minimum": 1, "maximum": 300}})`. Au niveau racine, aucune borne : la copie garde `type`, `required` et `additionalProperties`. On descend dans `n_mois` : `type` est gardé, `minimum` et `maximum` sont retirés, `retirees` vaut `["minimum=1", "maximum=300"]`, et la description devient `"Contraintes : minimum=1, maximum=300."`.

```text
# [extrait] console
>>> from agent.schemas import SCHEMA_DEMANDE_CREDIT, schema_pour_api_strict, validate
>>> api = schema_pour_api_strict(SCHEMA_DEMANDE_CREDIT)
>>> api["properties"]["duree_mois"]
{'type': 'integer', 'description': 'Contraintes : minimum=12, maximum=300.'}
>>> SCHEMA_DEMANDE_CREDIT["properties"]["duree_mois"]
{'type': 'integer', 'minimum': 12, 'maximum': 300}
```

La dernière ligne montre que l'original est intact.

## Les tests qui passent maintenant

```powershell
python -m unittest -v tests.test_02_schemas.TestSchemaStrict
```

Les trois tests sont verts.

- `test_objet`, déjà vert à l'étape 3.
- `test_bornes_retirees_et_recopiees` : la propriété `n_mois` devient exactement `{"type": "integer", "description": "Contraintes : minimum=1, maximum=300."}`, et le JSON du schéma rendu ne contient plus aucun des cinq mots-clés.
- `test_la_validation_locale_reste_necessaire` : une demande de 6 mois passe le schéma strict (liste vide) mais pas le schéma local (`$.duree_mois : 6 < minimum 12`). Ce test marche aussi parce que `description` est dans `MOTS_CLES` : `validate` accepte le schéma strict sans lever `ValueError`.

## Ce qu'il faut retenir

- Le mode strict garantit la forme, pas les bornes : la validation locale reste obligatoire.
- Une fonction qui transforme un schéma rend une copie ; elle ne modifie jamais ce qu'on lui passe.
- Les bornes retirées ne sont pas perdues : elles passent dans la description, que le modèle lit.

> Suivant : [Étape 5 — Lire puis valider](<05-Lire-et-valider.md>)
