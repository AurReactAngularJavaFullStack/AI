# Étape 5 — Les définitions pour l'API

> Palier 04, étape 5 sur 7 · Précédent : [Étape 4 — Les cinq outils métier](<04-Outils-metier.md>) · Suivant : [Étape 6 — L'enveloppe d'erreur](<06-Executer-appel.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Le modèle ne peut appeler que les outils qu'on lui décrit. À chaque appel, la boucle lui envoie la liste des outils au format de l'API : pour chacun, `name`, `description`, `input_schema` et, en mode strict, `strict: true`. Le mode strict contraint le décodage du modèle : il ne **peut** produire que des arguments qui respectent le schéma envoyé. Mais il n'accepte pas tous les mots-clés JSON Schema : les bornes (`minimum`, `maximum`, `exclusiveMinimum`, `minLength`, `maxLength`) sont refusées.

Le registre est la source unique du contrat : on ne recopie pas les schémas à la main dans une seconde liste. On les dérive. La seule question est : quel schéma envoyer ? Pas le schéma complet, que l'API refuserait ; une version sans bornes, que `schema_pour_api_strict` du palier 02 sait fabriquer.

## Bloc 1 — Envoyer le schéma tel quel

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.definitions_api()`** — Dans ce brouillon, la méthode est un maître d'hôtel qui tend au client la fiche technique de la cuisine au lieu de la carte : elle ne reçoit rien et renvoie, pour chaque outil du registre et dans son ordre, un dictionnaire aux quatre clés `name`, `description`, `input_schema` et `strict`, mais avec le schéma complet de l'outil, bornes comprises. La forme et l'ordre sont justes, pourtant `n_mois` y garde son minimum et son maximum : en mode strict, une vraie API rejetterait toute la requête, et le test qui cherche les cinq mots-clés de bornes dans le JSON trouve `"minimum"` et échoue.

```python
# [extrait] brouillon
class Registre:
    ...
    def definitions_api(self) -> list[dict]:
        return [{"name": o.nom, "description": o.description, "input_schema": o.schema, "strict": True}
                for o in self.outils.values()]
```

La forme est la bonne, et l'ordre aussi. Mais `input_schema` contient encore `"minimum": 1, "maximum": 300` pour `n_mois` : en mode strict, une vraie API rejetterait la requête entière, et l'agent ne démarrerait pas. Hors ligne, le test `test_mode_strict_sans_bornes` le voit : il sérialise toutes les définitions avec `json.dumps` et cherche chacun des cinq mots-clés de `NON_STRICT` entre guillemets ; il trouve `"minimum"`, et échoue.

## Bloc 2 — La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.definitions_api()`** — C'est la même méthode, devenue le maître d'hôtel qui recopie chaque plat sur la carte en retirant les détails que le guichet de l'API ne sait pas lire : elle ne reçoit rien et renvoie, par une compréhension de liste sur `self.outils.values()`, une définition par outil dans l'ordre du registre, avec le nom, la description, `strict` à `True` et un `input_schema` produit par `schema_pour_api_strict`. Ce schéma est une copie sans bornes, les bornes étant recopiées dans la description, si bien que la porte garde intact le schéma complet ; pour « mensualite », la durée part comme un entier décrit par « Contraintes : minimum=1, maximum=300. », et la liste compte cinq définitions, « mensualite » en tête.

```python
# [extrait] agent/outils.py
class Registre:
    ...
    def definitions_api(self) -> list[dict]:
        """Les définitions au format de l'API, en mode strict : bornes retirées, recopiées en description.

        Exemple : pour "mensualite", `input_schema["properties"]["n_mois"]` vaut
        {"type": "integer", "description": "Contraintes : minimum=1, maximum=300."} et `strict` vaut True.
        """
        return [{"name": o.nom, "description": o.description, "input_schema": schema_pour_api_strict(o.schema),
                 "strict": True} for o in self.outils.values()]
```

**Une compréhension de liste.** `[expression for o in self.outils.values()]` construit une liste avec un élément par outil, dans l'ordre du registre : « mensualite » en premier, « tva » en dernier. C'est un `stream().map(...).toList()`. `self.outils.values()` parcourt les objets `Outil`, sans les noms (qu'on lit dans `o.nom`).

**Les quatre clés.** `name` et `description` recopient l'outil ; `strict` vaut toujours `True` ; `input_schema` reçoit `schema_pour_api_strict(o.schema)`. Les noms des clés sont ceux de l'API Claude, en anglais : ce ne sont pas des noms à nous, on les écrit exactement.

**Ce que fait `schema_pour_api_strict`**, sur `n_mois`, dont le schéma complet vaut `{"type": "integer", "minimum": 1, "maximum": 300}` :

1. elle copie les clés qui ne sont pas des bornes : `{"type": "integer"}` ;
2. elle note les bornes retirées, dans l'ordre : `minimum=1`, puis `maximum=300` ;
3. elle les écrit dans la description, qui était vide : « Contraintes : minimum=1, maximum=300. ».

Le résultat vaut `{"type": "integer", "description": "Contraintes : minimum=1, maximum=300."}`. Le modèle lit encore les bornes, en clair, dans la description ; l'API ne les applique pas. Elle descend aussi dans `properties`, si bien que les trois champs de « mensualite » sont traités, et laisse `required` et `additionalProperties`, que le mode strict exige.

**Le piège : modifier le schéma en place.** Une version « économe » retirerait les bornes directement dans `o.schema`, par exemple avec `del schema["minimum"]`. La porte, qui lit le même dictionnaire, perdrait alors ses bornes : `n_mois = 3000` passerait. `schema_pour_api_strict` construit une **copie** et ne touche jamais au schéma reçu. La porte garde le schéma complet, l'API reçoit le schéma allégé : deux usages, une seule source, aucune interférence. En Java, on parlerait de copie défensive.

**Pourquoi les bornes restent indispensables à la porte.** Le mode strict garantit que `n_mois` sera un entier, pas qu'il sera entre 1 et 300. Un modèle qui lit mal « 25 ans » et écrit 2500 mois produira un entier valide pour l'API. Seule la validation locale l'arrête, avec `$.n_mois : 2500 > maximum 300`.

**Vérifier à la console**, depuis `projet/` :

```text
>>> from agent.outils import Registre, enregistrer_outils_metier
>>> defs = enregistrer_outils_metier(Registre()).definitions_api()
>>> len(defs), defs[0]["name"], defs[0]["strict"]
(5, 'mensualite', True)
>>> defs[0]["input_schema"]["properties"]["n_mois"]
{'type': 'integer', 'description': 'Contraintes : minimum=1, maximum=300.'}
```

**Le test qui passe maintenant.**

```text
python -m unittest -v tests.test_04_outils.TestDefinitionsApi
```

Il vérifie les 5 définitions, `strict` partout, l'absence des cinq mots-clés de bornes dans le JSON, et la propriété `n_mois` exacte.

**Ce qu'il faut retenir.** Les définitions pour l'API se **dérivent** du registre, elles ne s'écrivent pas une seconde fois. Le schéma envoyé est une copie sans bornes ; le schéma complet reste à la porte, seule à vérifier les bornes.
