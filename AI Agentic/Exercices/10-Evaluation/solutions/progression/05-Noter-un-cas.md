# Étape 5 — Noter un cas

> [Énoncé du palier 10](<../../README.md>) · Précédent : [Étape 4 — La fidélité approchée](<04-Fidelite-approchee.md>) · Suivant : [Étape 6 — Le rapport et la barrière CI](<06-Rapport-et-barriere-CI.md>)

## Comment raisonner

Les trois mesures existent. Il faut maintenant les appliquer à **une exécution réelle** de l'agent, c'est-à-dire au dictionnaire que rend `executer_agent` (palier 05) : `{"statut", "trace", "etapes", "messages"}`, plus `"reponse"` quand le statut vaut `"fini"`. Avant d'écrire, on relit la forme de ce résultat :

- `res["trace"]` est une liste de triplets `(nom, arguments, sortie)`, un par outil **exécuté ou tenté** ; un outil qui a échoué y figure avec une sortie « ERREUR … » ;
- `res["reponse"]` n'existe que si la boucle a fini normalement ; un résultat `"tronque"`, `"boucle"` ou `"max_etapes"` n'a pas de réponse finale.

La fonction `noter` est un adaptateur : elle extrait de ce dictionnaire ce que chaque métrique attend. Le critère de réussite, lui, reste chez l'appelant, parce que seul l'appelant connaît l'objectif métier du cas (le bon verdict de crédit, un virement non exécuté, deux règles citées).

## Un brouillon qui plante sur un cas raté

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`noter(res, sources, attendus, but)`** — Ce brouillon est un correcteur qui exige qu'on lui rende une copie terminée et qui claque la porte devant la copie inachevée. Il reçoit le résultat d'exécution, les sources, les appels attendus et le critère `but`, extrait de la trace les couples `(nom, arguments)` réellement appelés et rend un dictionnaire avec la Tool Call F1, le but et la fidélité de `res["reponse"]`. Le malheur est qu'il lit cette réponse sans regarder le statut : sur une exécution tronquée, qui n'a pas de clé `"reponse"`, il lève `KeyError` et arrête toute l'évaluation sur le premier cas raté.

```python
# [extrait] brouillon
def noter(res, sources, attendus, but):
    reels = [(nom, args) for nom, args, _ in res["trace"]]
    return {"f1": tool_call_f1(attendus, reels), "but": but,
            "fidelite": fidelite_approchee(res["reponse"], sources)}     # KeyError si la boucle n'a pas fini
```

Sur un résultat tronqué, `res["reponse"]` lève `KeyError`, et toute l'évaluation s'arrête sur le premier cas raté, précisément celui qu'on voulait compter comme un échec. En Java, ce serait un `NullPointerException` sur `res.get("reponse").length()`.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`noter(res, sources, attendus, but)`** — La version juste est le même correcteur, devenu patient : il note aussi la copie inachevée, en laissant vide la case qu'il ne peut pas remplir. Elle reçoit les mêmes quatre arguments, déballe chaque triplet `(nom, arguments, sortie)` de la trace pour n'en garder que le nom et les arguments, appels échoués compris, et calcule leur Tool Call F1 face aux appels attendus. Elle recopie le but fourni par l'appelant et ne lit `res["reponse"]` que si le statut vaut `"fini"`, sinon la fidélité vaut `None`. Elle rend le dictionnaire `{"f1", "but", "fidelite"}` : 2/3, vrai et 1,0 pour l'exécution finie qui n'a appelé que A1, 0,0, faux et `None` pour l'exécution tronquée sans trace.

```python
# [extrait] agent/evaluation.py
def noter(res: dict, sources: list[str], attendus: list, but: bool) -> dict:
    ...
    return {"f1": tool_call_f1(attendus, [(nom, args) for nom, args, _ in res["trace"]]), "but": but,
            "fidelite": fidelite_approchee(res["reponse"], sources) if res["statut"] == "fini" else None}
```

**Ligne par ligne.**

- `[(nom, args) for nom, args, _ in res["trace"]]` déballe chaque triplet de la trace et ne garde que le nom et les arguments : ce sont les appels réels. Le tiret bas `_` est la convention Python pour « valeur ignorée », ici la sortie de l'outil.
- `"but": but` recopie le critère calculé par l'appelant.
- L'expression conditionnelle n'évalue `res["reponse"]` **que** si le statut vaut `"fini"`. Python évalue la condition d'abord, puis une seule des deux branches : c'est ce qui évite la `KeyError` du brouillon. Sinon, la fidélité vaut `None` : il n'y a pas de réponse à juger.

**Un appel qui a échoué compte-t-il ?** Oui. Il figure dans la trace, donc dans les appels réels. Un modèle qui demande un virement refusé par le garde-fou du palier 09 a quand même **tenté** l'appel : si l'expert ne l'attendait pas, c'est un faux positif, et la F1 le pénalise. La F1 juge les décisions du modèle, pas le succès des outils.

**Analogie Java.** Un mapper qui transforme un `ResultatAgent` en `NoteCas` : `new NoteCas(f1(attendus, reels), but, res.statut() == FINI ? fidelite(res.reponse(), sources) : null)`.

**Les nombres de l'énoncé.** Une exécution finie qui n'a appelé que A1, avec A1 et A2 attendus : F1 = 2 × 1 / (2 + 1) = 2/3. Sa réponse « Mensualité 5419,37 AED. » cite 5419,37, présent dans la source `{"m": 5419.37}` : fidélité 1. L'exécution tronquée, sans trace, avec A1 attendu : F1 = 2 × 0 / (1 + 0) = 0,0, et fidélité `None`.

## Le test qui passe maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_10_evaluation.TestRapportEtBarriere.test_noter
```

Le test vérifie les deux dictionnaires de l'exemple : `{"f1": 2/3, "but": True, "fidelite": 1.0}` pour l'exécution finie, `{"f1": 0.0, "but": False, "fidelite": None}` pour l'exécution tronquée, construite sans clé `"reponse"`.
