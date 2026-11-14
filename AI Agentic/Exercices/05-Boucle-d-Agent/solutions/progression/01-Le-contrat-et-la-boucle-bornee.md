# Étape 1 — Le contrat et la boucle bornée

> Progression du palier 05 · Précédent : [Énoncé du palier](<../../README.md>) · Suivant : [Étape 2 — Décider, et les arrêts de l'API](<02-Decider-et-les-arrets-de-l-API.md>) · Retour à l'énoncé : [README du palier 05](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Devant un fichier vide, on n'écrit pas la boucle en premier. On écrit d'abord son **contrat** : ce qu'elle reçoit, ce qu'elle rend, et comment elle s'arrête. En Java, c'est le réflexe de poser l'interface et les tests JUnit avant l'implémentation. Ici, le contrat est déjà dans `tests/test_05_boucle.py` ; il suffit de le lire avec trois questions en tête.

1. **Qu'est-ce qui entre ?** Les tests appellent toujours `executer_agent(llm, "s", "q", outils(), [])`. Ils passent donc un faux modèle, un prompt système, une question, le dictionnaire des outils et la liste des schémas, plus parfois `max_etapes=2`.
2. **Qu'est-ce qui sort ?** Les tests lisent `r["statut"]`, `r["trace"]`, `r["etapes"]`, `r["messages"]` et, seulement quand le statut vaut `fini`, `r["reponse"]`. La sortie est donc un dictionnaire à clés fixes.
3. **Comment ça s'arrête ?** `test_cinq_statuts` énumère les cinq statuts. Un seul arrêt ne dépend pas du modèle : `max_etapes`. C'est lui qu'on écrit en premier, parce que c'est la seule garantie qui tienne face à un modèle qui se trompe, ou qui ne s'arrête jamais.

L'ordre d'écriture de ce palier suit ce raisonnement : le contrat et la borne (cette étape), puis ce que le modèle répond (étapes 2 et 3), puis ce que font les outils (étape 4), puis la détection de la répétition (étape 5).

## La tentation du `while True`

Le premier réflexe, quand on lit « la boucle tourne jusqu'à ce que le modèle ait fini », est d'écrire une boucle infinie et de compter sur le modèle pour en sortir.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas)`** — Dans ce brouillon, la fonction ressemble à un chef d'orchestre qui attend que les musiciens décident seuls de la fin du concert : elle reçoit le modèle, le prompt système, la question, les outils et les schémas, ouvre un historique avec la question, puis, dans un `while True` sans borne, appelle le modèle et ne sort qu'en renvoyant un dictionnaire de statut `fini` quand il répond `end_turn`. Un modèle qui demande des outils sans fin la fait tourner indéfiniment, chaque tour étant facturé ; un refus ou une troncature n'ont pas de sortie propre, et le résultat oublie les clés `trace` et `etapes` que les tests lisent.

```python
# [extrait] brouillon
def executer_agent(llm, system, question, outils, schemas):
    messages = [{"role": "user", "content": question}]
    while True:                                   # on compte sur le modèle pour s'arrêter
        reponse = llm.create(system=system, messages=messages, tools=schemas)
        if reponse.stop_reason == "end_turn":
            return {"statut": "fini", "messages": messages}
        # … exécuter les outils, ajouter les résultats, recommencer …
```

Ce brouillon a l'air juste, et il passerait même un test « réponse finale directe ». Il a pourtant trois défauts graves.

- **Il ne termine pas pour tout modèle.** Un modèle qui demande des outils sans fin, par erreur ou parce qu'un document piégé l'y pousse, le fait tourner indéfiniment. Chaque tour est un appel facturé, et le tour e relit 2e − 1 messages : la facture croît comme un carré (étape 6 de cette progression).
- **Il n'a qu'une sortie.** Un refus, une réponse tronquée ou une répétition finissent soit en boucle infinie, soit en statut `fini` trompeur.
- **Son contrat de sortie est incomplet.** Il manque `trace` et `etapes`, que les tests lisent.

La correction est simple : une boucle `for` sur un nombre d'étapes fixé à l'avance, et un retour explicite quand ce nombre est épuisé. Le `while True` d'un agent est l'équivalent d'un `while (true)` sans `break` garanti dans un service Spring : on ne le met pas en production.

## Les imports et la constante des statuts

```python
# [extrait] agent/boucle.py
import json

from agent.outils import executer_appel

STATUTS = ("fini", "refus", "tronque", "boucle", "max_etapes")
```

- `import json` : la bibliothèque standard de sérialisation JSON. Elle servira à l'étape 5, pour écrire les arguments d'un appel sous une forme comparable. On l'importe dès maintenant, puisque le squelette l'importe déjà.
- `from agent.outils import executer_appel` : la seule dépendance du module, vers le palier 04. La boucle ne touche jamais au registre ni aux schémas : elle confie chaque bloc `tool_use` à `executer_appel`, qui rend un couple (`tool_result`, ligne de trace) et ne lève jamais. C'est la règle des paliers : on compose avec ce qui existe, on ne le réécrit pas.
- `STATUTS` : un tuple, pas une liste, parce que l'ensemble des statuts ne doit pas changer pendant l'exécution. En Java, ce serait un `enum Statut { FINI, REFUS, TRONQUE, BOUCLE, MAX_ETAPES }`. Python a aussi `enum.Enum`, mais le test compare à des chaînes, et les chaînes passent telles quelles dans les journaux et le JSON.

**Le piège classique.** Écrire les statuts avec des accents ou une autre casse, par exemple `"tronqué"` ou `"Fini"`. Le test `test_cinq_statuts` compare la constante au tuple exact `("fini", "refus", "tronque", "boucle", "max_etapes")`.

## Le contrat de la fonction et la borne

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — Ce premier squelette juste est celui d'un chef d'orchestre qui fixe d'avance le nombre de mesures et ne compte que sur lui-même pour baisser le rideau : la fonction reçoit le modèle, le prompt système, la question, les portes des outils, les schémas et la borne `max_etapes`, 8 par défaut, lève `ValueError` (« max_etapes doit valoir au moins 1 ») si la borne est inférieure à 1, puis prépare l'historique avec la question, une trace vide et une signature précédente à `None`. Elle parcourt ensuite les étapes de 1 à `max_etapes`, dont le corps viendra aux étapes suivantes, et, si aucune ne l'a fait sortir, renvoie le statut `max_etapes` avec la trace, le nombre d'étapes égal à la borne et l'historique : quatre clés, la forme de tous les retours à venir.

```python
# [extrait] agent/boucle.py
def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    ...
    if max_etapes < 1:
        raise ValueError("max_etapes doit valoir au moins 1")
    messages = [{"role": "user", "content": question}]
    trace = []
    precedente = None
    for etape in range(1, max_etapes + 1):
        ...
    return {"statut": "max_etapes", "trace": trace, "etapes": max_etapes, "messages": messages}
```

Les lignes `...` marquent ce qui viendra aux étapes suivantes : la docstring, déjà présente dans le squelette, puis le corps de la boucle.

**La signature.** Elle est imposée par le squelette, mot pour mot. `llm` n'a pas d'annotation : la boucle accepte tout objet qui possède une méthode `create(*, system, messages, tools)`. C'est le typage structurel de Python, l'équivalent d'une interface `LlmPort` que l'on n'aurait pas besoin de déclarer. `max_etapes: int = 8` a une valeur par défaut, comme dans l'étape 77.

**La garde.** `if max_etapes < 1: raise ValueError(...)` refuse une borne absurde dès l'entrée, avec un message clair. Sans elle, `range(1, 1)` serait vide, la boucle ne ferait aucun appel, et la fonction rendrait `{"statut": "max_etapes", "etapes": 0}` : un statut qui fait croire que le modèle a épuisé son budget alors qu'il n'a jamais été appelé. C'est la convention de tout le cours : une entrée invalide lève `ValueError`, elle ne produit pas un résultat trompeur. En Java, ce serait un `IllegalArgumentException` levé par un `Objects.checkIndex` ou une précondition de Guava.

**L'état initial.** Trois variables, une par besoin de la boucle.

- `messages = [{"role": "user", "content": question}]` : l'historique, au format de l'API. Il commence par un seul message, la question. C'est tout ce que le modèle « perçoit » au premier tour, en plus du prompt système.
- `trace = []` : le journal des outils exécutés, une ligne par outil. Il sert à l'audit et, au palier 10, à l'évaluation.
- `precedente = None` : la signature de l'étape d'avant, qui servira à l'arrêt `boucle` (étape 5). `None` veut dire « aucune étape encore ». Aucune signature réelle n'est égale à `None`, donc la première étape ne peut pas être prise pour une répétition.

**La boucle bornée.** `for etape in range(1, max_etapes + 1)` fait prendre à `etape` les valeurs 1, 2, …, `max_etapes` : c'est le `for (int etape = 1; etape <= maxEtapes; etape++)` de Java. On numérote à partir de 1 parce que `etapes` est rendu à l'utilisateur et compte des appels au modèle : « fini à l'étape 3 » veut dire « trois appels ».

**Le retour après la boucle.** Si l'on sort de la boucle sans être passé par un `return`, c'est que les `max_etapes` tours ont tous été consommés : on rend le statut `max_etapes`, avec `"etapes": max_etapes`. Les quatre clés `statut`, `trace`, `etapes` et `messages` y sont déjà ; tous les autres retours de la fonction auront la même forme.

**Le piège classique.** Écrire `range(max_etapes)` : `etape` vaudrait 0 au premier tour, et tous les nombres d'étapes rendus seraient décalés de un. Le test `test_reponse_finale_directe` attend `etapes == 1` pour une réponse finale au premier appel.

## Ce que l'on peut déjà vérifier

Remplace provisoirement le corps de la boucle par `pass`, et lance une console Python depuis `projet/` :

```text
# [extrait] console
>>> from agent.boucle import executer_agent
>>> from agent.modele import FakeLLM
>>> from agent.outils import Registre, enregistrer_outils_metier
>>> outils = enregistrer_outils_metier(Registre()).appelables()
>>> executer_agent(FakeLLM([]), "s", "q", outils, [], max_etapes=0)
Traceback (most recent call last):
  ...
ValueError: max_etapes doit valoir au moins 1
```

La garde fonctionne. Lance ensuite les tests du palier :

```text
python -m unittest -v tests.test_05_boucle
```

Aucun test ne passe encore, et c'est normal : le corps de la boucle ne fait rien. Mais ils n'échouent plus par `NotImplementedError` : ils échouent sur leurs assertions, ou parce que la clé `reponse` manque. Le module s'exécute, et le contrat est en place. L'étape suivante remplit le temps « décider ».
