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
