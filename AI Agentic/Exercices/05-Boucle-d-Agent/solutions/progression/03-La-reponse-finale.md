# Étape 3 — La réponse finale

> Progression du palier 05 · Précédent : [Étape 2 — Décider, et les arrêts de l'API](<02-Decider-et-les-arrets-de-l-API.md>) · Suivant : [Étape 4 — Agir et observer](<04-Agir-et-observer.md>) · Retour à l'énoncé : [README du palier 05](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Après les trois arrêts de l'API, il reste deux cas : le modèle a fini (`end_turn`), ou il demande des outils (`tool_use`). Avant d'écrire le moindre appel d'outil, on traite le cas le plus simple, la réponse finale. Une boucle qui sait s'arrêter proprement est déjà testable de bout en bout avec une seule réponse scriptée.

Deux questions guident l'écriture.

1. **À quoi reconnaît-on une réponse finale ?** `stop_reason == "end_turn"` est le signal officiel. Mais un modèle peut aussi s'arrêter sur `"tool_use"` sans avoir produit de bloc `tool_use`. Dans les deux cas, il n'y a rien à exécuter, et continuer ne ferait que rappeler le modèle pour rien. On rend donc `fini` dès qu'il n'y a **aucun** appel d'outil, quel que soit le `stop_reason` restant.
2. **Que rend-on comme réponse ?** Le contenu est une liste de blocs. Un modèle peut écrire sa réponse en plusieurs blocs de texte, et mêler du texte et des appels d'outils dans la même réponse. On garde **tous** les blocs de texte, dans l'ordre, et rien d'autre.

Pour savoir s'il y a des appels d'outils, il faut d'abord les extraire. Cette liste resservira aux étapes 4 et 5 : on la calcule une seule fois, dans une variable.

## Un brouillon qui ne garde que le premier bloc

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`reponse_finale(reponse)`** — Ce brouillon est un secrétaire qui ne recopie que la première page d'une lettre et jette les suivantes : il reçoit une réponse du modèle et renvoie le texte de son premier bloc, et rien d'autre. Sur une réponse faite des blocs « Bonjour » et « ! », il rend « Bonjour » et perd la fin de la phrase ; si le premier bloc est un `tool_use`, il rend une chaîne vide, valeur par défaut de `Bloc.text` ; sur un contenu vide, il lève `IndexError`, alors que le test `test_reponse_finale_directe` attend la concaténation de tous les blocs de texte.

```python
# [extrait] brouillon
def reponse_finale(reponse) -> str:
    return reponse.content[0].text            # le premier bloc, et lui seul
```

Sur `Reponse("end_turn", [texte("Bonjour"), texte(" !")])`, ce brouillon rend `"Bonjour"` et perd la fin de la phrase. Sur une réponse dont le premier bloc est un `tool_use`, il rend une chaîne vide, car `Bloc.text` vaut `""` par défaut. Sur un contenu vide, il lève `IndexError`. Le test `test_reponse_finale_directe` attend `"Bonjour !"` : il faut concaténer tous les blocs de texte.

## Extraire les appels, puis reconnaître la fin

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la fonction des étapes 1 et 2, à laquelle on ajoute, juste après le traitement de `pause_turn`, le moment où le chef d'orchestre reconnaît la dernière note : elle extrait d'abord, dans l'ordre, la liste des blocs `tool_use` de la réponse, puis, si `stop_reason` vaut `"end_turn"` ou si cette liste est vide, met bout à bout sans séparateur les textes de tous les blocs `"text"` et renvoie le statut `fini` avec cette réponse, la trace, le numéro de l'étape et l'historique. C'est le seul retour qui porte la clé `reponse` ; une réponse faite de « Bonjour » et « ! » donne ainsi « Bonjour ! » en une étape, et les blocs `tool_use` glissés dans un `end_turn` ne sont jamais exécutés.

```python
# [extrait] agent/boucle.py
def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    ...
    for etape in range(1, max_etapes + 1):
        ...
        appels = [b for b in reponse.content if b.type == "tool_use"]
        if reponse.stop_reason == "end_turn" or not appels:
            final = "".join(b.text for b in reponse.content if b.type == "text")
            return {"statut": "fini", "reponse": final, "trace": trace, "etapes": etape, "messages": messages}
        ...
```

Ces quatre lignes viennent juste après le `continue` de `pause_turn`, toujours dans le corps de la boucle.

**`appels = [b for b in reponse.content if b.type == "tool_use"]`.** Une compréhension de liste : « la liste des `b` de `reponse.content` dont le type vaut `"tool_use"` ». C'est l'équivalent Java de `reponse.content().stream().filter(b -> b.type().equals("tool_use")).toList()`. L'ordre des blocs est conservé ; il compte, car les résultats repartiront dans le même ordre.

**`if reponse.stop_reason == "end_turn" or not appels:`.** Les deux conditions de la fin.

- `reponse.stop_reason == "end_turn"` : le modèle a fini. Même si, par extraordinaire, il a glissé un bloc `tool_use` dans une réponse `end_turn`, on ne l'exécute pas : le signal d'arrêt du modèle l'emporte, et une action ne se déclenche jamais sur un signal ambigu.
- `not appels` : en Python, une liste vide est « fausse », donc `not appels` vaut `True` quand il n'y a aucun appel. C'est le `appels.isEmpty()` de Java.

**`final = "".join(b.text for b in reponse.content if b.type == "text")`.** On met bout à bout les textes des blocs de type `"text"`, sans séparateur. L'argument de `join` est une expression génératrice, une compréhension sans crochets, qui produit les textes un par un sans construire de liste intermédiaire. L'équivalent Java est `Collectors.joining("")` sur un flux filtré. Pourquoi aucun séparateur ? Parce que le modèle découpe parfois une même phrase en plusieurs blocs : `"Bonjour"` et `" !"` doivent donner `"Bonjour !"`, et non `"Bonjour  !"`.

**Le `return`.** C'est le seul dictionnaire qui porte la clé `reponse`. Les quatre autres clés ont la même forme que dans les autres retours : `etapes` vaut le numéro du tour, donc le nombre d'appels faits au modèle.

**Le piège classique.** Écrire `if reponse.stop_reason == "end_turn" and not appels`. Avec `and`, une réponse `"tool_use"` sans bloc `tool_use` ne serait jamais finale : la boucle rappellerait le modèle jusqu'à épuiser son script ou sa borne. L'autre piège est d'ajouter un séparateur dans `join`, que le test refuse.

## Les tests qui passent maintenant

```text
python -m unittest -v tests.test_05_boucle.TestArrets.test_reponse_finale_directe tests.test_05_boucle.TestArrets.test_pause_turn_relance_sans_executer tests.test_05_boucle.TestScenarioCredit.test_contenu_recopie_tel_quel_et_outils_transmis
```

- `test_reponse_finale_directe` : `fini`, réponse `"Bonjour !"`, une étape, trace vide.
- `test_pause_turn_relance_sans_executer` : le premier tour est en pause, et `continue` passe au second, qui rend `fini`. Le résultat compte 2 étapes et la trace reste vide. Ce test ne pouvait pas passer à l'étape 2, faute de statut `fini`.
- `test_contenu_recopie_tel_quel_et_outils_transmis` passe aussi, même sans outils exécutés. Son scénario se termine par un `end_turn` au troisième appel, et il ne vérifie que le premier message `assistant` et les schémas transmis.

```text
# [extrait] console
>>> from agent.boucle import executer_agent
>>> from agent.modele import FakeLLM, Reponse, texte
>>> r = executer_agent(FakeLLM([Reponse("end_turn", [texte("Bonjour"), texte(" !")])]), "s", "q", {}, [])
>>> r["statut"], r["reponse"], r["etapes"]
('fini', 'Bonjour !', 1)
```

Avec le `test_refus_et_troncature` de l'étape 2, quatre tests sur onze passent. Les autres demandent d'exécuter des outils : c'est l'étape 4.
