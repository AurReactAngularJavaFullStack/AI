# Étape 5 — L'arrêt boucle et la signature

> Progression du palier 05 · Précédent : [Étape 4 — Agir et observer](<04-Agir-et-observer.md>) · Suivant : [Étape 6 — Les preuves, vérifiées sur le code](<06-Les-preuves-verifiees-sur-le-code.md>) · Retour à l'énoncé : [README du palier 05](<../../README.md>)

## Comment raisonner depuis la feuille blanche

La borne `max_etapes` arrête tout modèle, mais tard : huit appels facturés, et 64 messages relus. Le cas le plus fréquent de modèle qui tourne en rond est plus simple : il redemande **exactement** la même chose qu'au tour d'avant, parce qu'il n'a pas compris le résultat, ou parce qu'un outil lui renvoie toujours la même erreur. On veut l'arrêter dès la deuxième demande identique, **sans** l'exécuter une seconde fois. Une action qui écrit, comme un virement, ne doit jamais partir deux fois par erreur.

Pour comparer deux tours, il faut une représentation comparable de « ce que le modèle demande ». On procède en trois questions.

1. **Qu'est-ce qui définit une action ?** Le nom de l'outil et ses arguments. Pas l'identifiant du bloc : le modèle en génère un nouveau à chaque demande, si bien que deux demandes identiques ont deux identifiants différents.
2. **Comment comparer des arguments ?** Ce sont des dictionnaires, parfois imbriqués. On les écrit en JSON avec les clés triées : deux dictionnaires égaux donnent alors le même texte, quel que soit l'ordre dans lequel le modèle a écrit les clés.
3. **Et quand une réponse demande plusieurs outils ?** La signature est la **liste** des couples (nom, arguments), dans l'ordre des blocs. Deux tours sont identiques si leurs listes sont égales, élément par élément.

On écrit d'abord la fonction pure, testable seule, puis on l'utilise dans la boucle.

## Pourquoi trier les clés

```text
# [extrait] console
>>> import json
>>> json.dumps({"b": 2, "a": 1})
'{"b": 2, "a": 1}'
>>> json.dumps({"b": 2, "a": 1}, sort_keys=True)
'{"a": 1, "b": 2}'
```

Un dictionnaire Python garde l'ordre d'insertion, et `json.dumps` le suit. Le modèle, lui, n'écrit pas toujours les clés dans le même ordre d'un tour à l'autre. Sans `sort_keys=True`, `{"b": 2, "a": 1}` et `{"a": 1, "b": 2}` donneraient deux textes différents, et la répétition passerait inaperçue. En Java, c'est l'option `SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS` de Jackson.

## Un brouillon sans tri

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`signature_appels(appels)`** — Dans ce brouillon, la fonction est un contrôleur qui recopie chaque ordre de mission mot pour mot, dans l'ordre où son auteur l'a griffonné : elle reçoit la liste des blocs `tool_use` d'une étape et renvoie la liste des couples (nom de l'outil, arguments écrits en JSON), dans l'ordre des blocs, mais sans trier les clés. Deux demandes identiques dont le modèle a simplement inversé les arguments, `{"b": 2, "a": 1}` puis `{"a": 1, "b": 2}`, donnent alors deux textes différents, et la répétition passe inaperçue ; le brouillon ne réussit que lorsque le faux modèle rejoue deux fois le même objet.

```python
# [extrait] brouillon
import json


def signature_appels(appels: list) -> list[tuple[str, str]]:
    return [(b.name, json.dumps(b.input)) for b in appels]       # sans sort_keys : FAUX
```

Ce brouillon passe `test_meme_action_deux_fois`, car le faux modèle rejoue alors deux fois le même objet. Il échoue en revanche sur `test_signature_independante_de_l_ordre_des_arguments`, qui compare `{"b": 2, "a": 1}` à `{"a": 1, "b": 2}`.

## La signature d'une étape

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`signature_appels(appels)`** — C'est la même fonction, devenue le contrôleur qui note chaque ordre de mission dans un format canonique, toujours le même, pour reconnaître d'un coup d'œil celui qu'on lui a déjà présenté : elle reçoit la liste des blocs `tool_use` d'une étape et renvoie, par une compréhension, la liste des couples (nom, arguments sérialisés par `json.dumps` avec `sort_keys=True`), dans l'ordre des blocs. L'identifiant du bloc n'y entre pas, et la liste garde l'ordre et les répétitions ; un appel « tva » sur un montant hors taxe de 100 a ainsi la signature `[("tva", '{"montant_ht": 100}')]`, et les deux ordres des clés de l'outil « ratio » donnent `[("ratio", '{"a": 1, "b": 2}')]`.

```python
# [extrait] agent/boucle.py
def signature_appels(appels: list) -> list[tuple[str, str]]:
    """La signature d'une étape : la liste des couples (nom, arguments en JSON trié).

    Trier les clés rend la signature indépendante de l'ordre des arguments.
    Exemple : un appel "tva" avec {"montant_ht": 100} a la signature [("tva", '{"montant_ht": 100}')].
    """
    return [(b.name, json.dumps(b.input, sort_keys=True)) for b in appels]
```

**L'annotation `list[tuple[str, str]]`.** Une liste de couples de chaînes : l'équivalent Java serait `List<Map.Entry<String, String>>`, ou une liste de `record Signature(String nom, String arguments)`. Les annotations de la forme `list[...]` datent de Python 3.9 ; le cours n'utilise jamais `typing.List`.

**La compréhension.** Pour chaque bloc `b`, un couple `(b.name, json.dumps(b.input, sort_keys=True))`, dans l'ordre des blocs. Le couple est un `tuple` : immuable et comparable élément par élément. Deux listes de tuples sont égales si elles ont la même longueur et des éléments égaux un à un, exactement comme `List.equals` en Java.

**Pourquoi une liste et pas un ensemble.** Avec un ensemble, la demande « TVA de 100, puis TVA de 100 » dans une même réponse se confondrait avec « TVA de 100 » seule, et l'ordre des demandes serait perdu. La liste garde les deux informations.

**Pourquoi du JSON et pas le dictionnaire lui-même.** On pourrait comparer les dictionnaires directement, puisque `{"a": 1} == {"a": 1}` en Python. Mais le texte JSON trié est une forme canonique : il se journalise, se compare et se hache, ce qui servira si l'on veut garder un ensemble de signatures déjà vues (défi 1 de l'énoncé). C'est aussi la clé qu'utilise `tool_call_f1` au palier 10.

**Exemple.** `signature_appels([appel_outil("ratio", {"b": 2, "a": 1}, "x")])` vaut `[("ratio", '{"a": 1, "b": 2}')]`. Le même appel avec les clés dans l'autre ordre et l'identifiant `"y"` donne la même signature.

## Un brouillon qui mémorise trop tôt

Dans la boucle, il faut comparer la signature du tour à celle du tour précédent, puis la mémoriser. L'ordre de ces deux opérations est décisif.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`detecter_boucle(appels, precedente)`** — Ce brouillon est un vigile qui inscrit le visiteur sur sa liste avant de vérifier s'il y figurait déjà, et le trouve donc toujours : il reçoit les blocs `tool_use` de l'étape et la signature de l'étape précédente, calcule la signature courante avec `signature_appels`, l'affecte à `precedente` avant de les comparer, puis renvoie le couple (`"boucle"`, signature) si elles sont égales, (`None`, signature) sinon. Comme la comparaison porte sur la signature et elle-même, elle est toujours vraie : le scénario du crédit s'arrêterait avec le statut `boucle` dès l'étape 1, sans qu'aucun outil soit exécuté.

```python
# [extrait] brouillon
def detecter_boucle(appels, precedente):
    signature = signature_appels(appels)
    precedente = signature                        # mémorisée AVANT la comparaison : FAUX
    if signature == precedente:                   # toujours vrai
        return "boucle", precedente
    return None, precedente
```

Avec ce brouillon, la comparaison compare la signature à elle-même : elle est toujours vraie. Le scénario du crédit s'arrêterait avec le statut `boucle` dès l'étape 1, sans aucun outil exécuté. C'est l'exercice « trouver le bug » de l'étape 1 du cours, et le défi 3 de l'énoncé.

## L'arrêt boucle dans la boucle

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la boucle des étapes précédentes, dans laquelle on glisse, entre la réponse finale et l'exécution des outils, le vigile qui compare avant d'inscrire : elle calcule la signature des appels de l'étape avec `signature_appels`, renvoie le statut `boucle` avec la trace, le numéro de l'étape et l'historique si cette signature est égale à `precedente`, avant d'avoir exécuté quoi que ce soit, et sinon mémorise la signature dans `precedente` puis exécute les appels. Au premier tour d'outils, `precedente` vaut `None` et rien ne s'arrête ; deux demandes identiques de TVA sur 100 donnent `boucle` à l'étape 2 avec une seule ligne de trace, tandis qu'une oscillation entre deux demandes différentes reste l'affaire de la borne `max_etapes`.

```python
# [extrait] agent/boucle.py
def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    ...
    for etape in range(1, max_etapes + 1):
        ...
        signature = signature_appels(appels)
        if signature == precedente:           # même action, mêmes arguments, deux fois de suite
            return {"statut": "boucle", "trace": trace, "etapes": etape, "messages": messages}
        precedente = signature
        resultats = []
        ...
```

Ces quatre lignes s'insèrent entre le `return` de la réponse finale et `resultats = []`.

**`signature = signature_appels(appels)`.** La liste `appels` a été calculée à l'étape 3 ; on la réutilise.

**`if signature == precedente:`.** Au premier tour d'outils, `precedente` vaut `None`, et aucune liste n'est égale à `None` : pas d'arrêt. Aux tours suivants, on compare à la signature du dernier tour d'outils. Égalité : le modèle redemande exactement la même chose. On rend `boucle` **avant** d'exécuter, ce qui fait que la trace ne contient que la première exécution.

**`precedente = signature`.** On mémorise **après** la comparaison, jamais avant. Un tour `pause_turn` ne passe pas par ces lignes : il ne modifie donc pas `precedente`. Une demande répétée de part et d'autre d'une pause est quand même reconnue.

**Ce que cet arrêt ne voit pas.** Il ne compare que deux tours consécutifs. Une oscillation A, B, A, B lui échappe, puisque chaque tour diffère du précédent : c'est `max_etapes` qui la rattrape. Ne compter que sur l'arrêt `boucle` est un des pièges listés à l'étape 1 du cours.

**Le piège classique.** Comparer les blocs eux-mêmes, `appels == appels_precedents`. Deux blocs `Bloc` sont des `dataclass`, donc égaux si **tous** leurs champs sont égaux, identifiant compris. Or le vrai modèle donne un identifiant neuf à chaque demande : la répétition ne serait jamais détectée.

## Les tests qui passent maintenant

```text
python -m unittest -v tests.test_05_boucle
```

Les onze tests du palier passent. Les trois derniers sont :

- `test_meme_action_deux_fois` : `tva(100)` deux fois, d'où `boucle` à l'étape 2, avec une seule ligne de trace ;
- `test_signature_independante_de_l_ordre_des_arguments` : les deux ordres de clés donnent `[("ratio", '{"a": 1, "b": 2}')]` ;
- `test_cinq_statuts` : cinq scripts, avec `max_etapes=2`, donnent dans l'ordre `fini`, `refus`, `tronque`, `boucle` et `max_etapes`. Le dernier script, `[tva(1), tva(2)]`, exécute deux tours différents et épuise la borne.

Le code est complet. L'étape suivante vérifie, sur ce code, les garanties annoncées dans le rappel de cours.
