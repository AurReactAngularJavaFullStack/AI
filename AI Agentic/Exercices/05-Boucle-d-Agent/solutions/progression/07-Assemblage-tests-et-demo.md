# Étape 7 — Assemblage, tests et démo

> Progression du palier 05 · Précédent : [Étape 6 — Les preuves, vérifiées sur le code](<06-Les-preuves-verifiees-sur-le-code.md>) · Suivant : [Palier 06 — Mémoire](<../../../06-Memoire/README.md>) · Retour à l'énoncé : [README du palier 05](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Le module est écrit morceau par morceau ; il reste à le relire d'un trait, comme le lira la personne qui fera la revue de code. Une seule question pour cette relecture : **l'ordre des tests dans un tour est-il le bon ?** On doit y trouver, dans cet ordre : l'appel au modèle, l'historique, les deux arrêts « contenu non fiable », la pause, la réponse finale, la répétition, puis l'action. Chaque arrêt est placé avant tout ce qui pourrait avoir un effet. On peut le réécrire de mémoire à partir de cette phrase.

## Le module complet

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`signature_appels(appels)`** — C'est la fonction de l'étape 5, le contrôleur qui note chaque ordre de mission dans un format canonique : elle reçoit la liste des blocs `tool_use` d'une étape et renvoie la liste des couples (nom de l'outil, arguments sérialisés en JSON à clés triées), dans l'ordre des blocs, sans l'identifiant de l'appel. Deux demandes identiques dont seul l'ordre des arguments diffère ont donc la même signature, et c'est cette liste que `executer_agent` compare d'une étape à l'autre ; dans la démo, la même action demandée deux fois est ainsi arrêtée à l'étape 2 avec un seul outil exécuté.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est le chef d'orchestre assemblé, qui joue chaque tour dans l'ordre fixé par les étapes 1 à 5 : il reçoit le modèle, le prompt système, la question, les portes des outils, les schémas et la borne, 8 par défaut, lève `ValueError` si la borne est inférieure à 1, puis, à chaque étape, appelle une fois le modèle, range sa réponse telle quelle, rend `refus` ou `tronque` avant de lire le contenu, relance sur `pause_turn`, rend `fini` avec la réponse quand il n'y a plus d'outil à appeler, rend `boucle` si la signature répète la précédente, et sinon exécute tous les appels avec `executer_appel` et renvoie tous les résultats dans un seul message `user`. Les cinq retours portent `statut`, `trace`, `etapes` et `messages`, plus `reponse` pour `fini` ; dans la démo, le dossier de C-1 finit en 3 étapes, avec une mensualité de 5 558,32 AED, 1 513,50 USD et un endettement de 28,9 %.

```python
# [extrait] agent/boucle.py
"""Palier 05 — la boucle d'agent : percevoir → décider → agir → observer, avec des arrêts garantis.

Origine : étape 77, section 1 (`executer_agent`, code canonique des étapes 1 et 13).

La boucle ne sait pas quel modèle elle utilise : elle appelle `llm.create(system=…, messages=…,
tools=…)` et lit `stop_reason` et `content`. Cinq statuts d'arrêt :
- "refus" (`stop_reason == "refusal"`) et "tronque" (`"max_tokens"`), traités avant de lire le contenu ;
- "fini" : réponse terminée (`"end_turn"`) ou sans aucun bloc `tool_use` ;
- "boucle" : la même liste d'appels, mêmes arguments, deux étapes de suite ;
- "max_etapes" : la borne, qui arrête n'importe quel modèle, même adversaire.
`"pause_turn"` relance simplement l'étape suivante, sans rien exécuter.
"""
import json

from agent.outils import executer_appel

STATUTS = ("fini", "refus", "tronque", "boucle", "max_etapes")


def signature_appels(appels: list) -> list[tuple[str, str]]:
    """La signature d'une étape : la liste des couples (nom, arguments en JSON trié).

    Trier les clés rend la signature indépendante de l'ordre des arguments.
    Exemple : un appel "tva" avec {"montant_ht": 100} a la signature [("tva", '{"montant_ht": 100}')].
    """
    return [(b.name, json.dumps(b.input, sort_keys=True)) for b in appels]


def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    """Fait tourner la boucle ReAct ; rend {"statut", "trace", "etapes", "messages"} (+ "reponse" si fini).

    - `outils` : dictionnaire nom → appelable (par exemple `Registre.appelables()`) ;
    - `schemas` : définitions au format de l'API (`Registre.definitions_api()`) ;
    - `trace` : une ligne (nom, arguments, sortie) par outil exécuté, « ERREUR … » si l'outil a échoué ;
    - le contenu de chaque réponse est recopié tel quel dans l'historique, et TOUS les résultats d'une
      étape repartent dans UN seul message `user`.
    Le nombre d'appels au modèle ne dépasse jamais `max_etapes`.
    Exemple (scénario de 77) : mensualité, puis ratio + conversion dans la même réponse, puis texte
    final : statut "fini", 3 étapes, 3 lignes de trace.
    """
    if max_etapes < 1:
        raise ValueError("max_etapes doit valoir au moins 1")
    messages = [{"role": "user", "content": question}]
    trace = []
    precedente = None
    for etape in range(1, max_etapes + 1):
        reponse = llm.create(system=system, messages=messages, tools=schemas)
        messages.append({"role": "assistant", "content": reponse.content})   # tel quel, sans retouche
        if reponse.stop_reason == "refusal":
            return {"statut": "refus", "trace": trace, "etapes": etape, "messages": messages}
        if reponse.stop_reason == "max_tokens":
            return {"statut": "tronque", "trace": trace, "etapes": etape, "messages": messages}
        if reponse.stop_reason == "pause_turn":
            continue
        appels = [b for b in reponse.content if b.type == "tool_use"]
        if reponse.stop_reason == "end_turn" or not appels:
            final = "".join(b.text for b in reponse.content if b.type == "text")
            return {"statut": "fini", "reponse": final, "trace": trace, "etapes": etape, "messages": messages}
        signature = signature_appels(appels)
        if signature == precedente:           # même action, mêmes arguments, deux fois de suite
            return {"statut": "boucle", "trace": trace, "etapes": etape, "messages": messages}
        precedente = signature
        resultats = []
        for b in appels:
            resultat, ligne = executer_appel(outils, b)
            resultats.append(resultat)
            trace.append(ligne)
        messages.append({"role": "user", "content": resultats})   # tous les résultats dans UN message
    return {"statut": "max_etapes", "trace": trace, "etapes": max_etapes, "messages": messages}
```

**La docstring du module** résume le contrat en une page : le port LLM, les cinq statuts, le cas `pause_turn`. C'est le premier texte que lira un collègue ; il doit suffire pour utiliser la fonction sans lire son corps.

**Les imports et `STATUTS`** (étape 1) : la seule dépendance est `executer_appel`, du palier 04. Le module n'importe ni `modele`, ni `schemas`, ni `metier` : il ne connaît ni le faux modèle, ni les outils, qu'il reçoit en paramètres. C'est ce qui permettra au palier 09 d'envelopper les outils dans des garde-fous, et au palier 12 de brancher le vrai modèle, sans toucher à une ligne de la boucle.

**`signature_appels`** (étape 5) : une ligne, une compréhension, et `sort_keys=True` pour que l'ordre des clés ne compte pas.

**`executer_agent`**, de haut en bas.

- La garde et l'état initial (étape 1) : `ValueError` pour une borne absurde, puis l'historique d'un seul message, la trace vide et `precedente = None`.
- Le temps « décider » (étape 2) : un seul `llm.create` par tour, avec des arguments nommés, et la réponse rangée telle quelle.
- Les arrêts de l'API (étape 2) : `refusal` et `max_tokens` avant toute lecture du contenu, puis `pause_turn` qui relance.
- La réponse finale (étape 3) : aucun appel d'outil, ou `end_turn`, rend `fini`. C'est le seul retour qui porte `reponse`.
- L'arrêt `boucle` (étape 5) : la signature est comparée **avant** d'exécuter, puis mémorisée.
- Les temps « agir » et « observer » (étape 4) : `executer_appel` pour chaque bloc, puis un seul message `user` pour tous les résultats.
- La borne (étape 1) : après la boucle, le statut `max_etapes`.

Les cinq `return` ont la même forme : `statut`, `trace`, `etapes` et `messages`, plus `reponse` pour `fini`. Un appelant peut donc toujours lire ces quatre clés sans tester le statut d'abord.

## Tous les tests

Depuis `projet/`, une fois ton fichier `agent/boucle.py` complet :

```text
python -m unittest -v
```

La fin de la sortie doit être :

```text
Ran 69 tests in 0.0XXs

OK
```

Les 69 tests regroupent les 58 tests des paliers 01 à 04, qui passaient déjà, et les 11 tests du palier 05. Le temps exact varie d'une machine à l'autre. Si un test des paliers précédents échoue, c'est qu'un module antérieur a été modifié : ils sont recopiés de la solution et ne doivent pas changer.

## La démo

```text
python demo.py
```

Sortie attendue :

```text
Palier 05 — client C-1 : hypothèque de 1 000 000 AED, revenu 40 000 AED, crédit auto 6 000 AED
  outil mensualite({"principal": 1000000, "taux_annuel": 0.045, "n_mois": 300}) -> {'mensualite_aed': 5558.32}
  outil ratio_endettement({"existantes": 6000, "nouvelle": 5558.32, "revenu": 40000}) -> {'ratio': 0.289, 'recevable': True}
  outil convertir_aed_usd({"montant_aed": 5558.32}) -> {'montant_usd': 1513.5}
  [fini, 3 étapes] Mensualité 5 558,32 AED, soit 1 513,50 USD ; endettement total 28,9 % ≤ 50 % : dossier recevable.
  résultats renvoyés ensemble à l'étape 3 : ['a2', 'a3']
Les arrêts qui protègent la facture :
  même action deux fois : boucle à l'étape 2, 1 outil exécuté
  trois appels différents, max_etapes = 2 : max_etapes, 2 appels au modèle
  refus du modèle : refus à l'étape 1
  erreur d'outil renvoyée au modèle : ERREUR $.montant_ht : -5 < minimum 0
OK — palier 05 terminé.
```

Ligne par ligne :

- **Les trois lignes `outil …`** sont la trace du scénario du crédit : `mensualite`, puis `ratio_endettement` et `convertir_aed_usd`, avec leurs arguments en JSON et leurs sorties. Les nombres sont ceux de l'étape 77 : 5 558,32 AED, un ratio de 0,289 et 1 513,50 USD.
- **`[fini, 3 étapes]`** : la tâche compte k = 2 étapes d'outils, donc k + 1 = 3 appels au modèle. La réponse finale est écrite par le faux modèle, à partir des sorties des outils.
- **`résultats renvoyés ensemble à l'étape 3 : ['a2', 'a3']`** : le dernier message reçu par le modèle au troisième appel contient les deux `tool_result`, dans un seul message.
- **`même action deux fois`** : arrêt `boucle` à l'étape 2, un seul outil exécuté.
- **`max_etapes = 2`** : trois demandes différentes, deux appels au modèle seulement.
- **`refus du modèle`** : arrêt `refus` à l'étape 1, rien d'exécuté.
- **`erreur d'outil renvoyée au modèle`** : la ligne de trace de l'appel refusé par la porte, que le modèle a reçue avec `is_error`.

La dernière ligne, `OK — palier 05 terminé.`, confirme que la démo est allée au bout.

## Ce que tu as appris

- Une boucle d'agent se borne **avant** d'être utile : `for etape in range(1, max_etapes + 1)` garantit au plus E max appels au modèle, quel que soit le modèle.
- Les `stop_reason` de l'API se traitent dans un ordre précis : refus et troncature avant de lire le contenu, pause sans rien exécuter, réponse finale dès qu'il n'y a plus d'outil à appeler.
- Le contenu du modèle se recopie tel quel, et tous les résultats d'un tour partent dans un seul message `user`.
- Une erreur d'outil n'arrête pas la boucle : elle devient un `tool_result` marqué `is_error`, que le modèle lit et corrige.
- La répétition se détecte par une signature canonique, du JSON à clés triées, comparée avant d'exécuter. L'oscillation, elle, n'est rattrapée que par la borne.
- Le coût suit E² messages relus, et la fiabilité suit le produit des pᵢ : moins de tours, c'est moins cher et plus sûr.

## La suite

L'agent sait maintenant agir, mais il a la mémoire d'un poisson rouge : chaque question repart de zéro, et le client doit redonner son salaire à chaque demande. Le [palier 06 — Mémoire](<../../../06-Memoire/README.md>) lui donne une mémoire longue. Il choisit quels souvenirs placer dans le prompt système, selon leur proximité avec la question, leur fraîcheur et leur importance, avant que `executer_agent` ne prenne le relais.
