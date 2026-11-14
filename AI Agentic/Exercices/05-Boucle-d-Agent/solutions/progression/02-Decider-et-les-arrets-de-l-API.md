# Étape 2 — Décider, et les arrêts de l'API

> Progression du palier 05 · Précédent : [Étape 1 — Le contrat et la boucle bornée](<01-Le-contrat-et-la-boucle-bornee.md>) · Suivant : [Étape 3 — La réponse finale](<03-La-reponse-finale.md>) · Retour à l'énoncé : [README du palier 05](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Chaque tour de boucle commence par le temps « décider » : on envoie l'état au modèle et on lit ce qu'il répond. La réponse a deux attributs, `stop_reason` (pourquoi il s'est arrêté de générer) et `content` (la liste des blocs produits). La question à se poser est : **dans quel ordre lire ces deux attributs ?**

La réponse vient des cinq valeurs possibles de `stop_reason`, listées dans `agent/modele.py` (`STOP_REASONS`) :

- `"end_turn"` : le modèle a fini son tour ; son texte est la réponse ;
- `"tool_use"` : il attend le résultat des outils demandés ;
- `"max_tokens"` : sa réponse a été coupée par la limite de tokens ;
- `"refusal"` : il refuse de poursuivre ;
- `"pause_turn"` : l'API a mis en pause un tour long ; il faut le relancer tel quel.

Deux de ces valeurs disent que le **contenu n'est pas fiable** : une réponse coupée peut contenir une phrase ou un bloc `tool_use` à moitié écrit, et un refus ne contient rien d'exploitable. On les traite donc **avant** de lire le contenu. Une troisième, `pause_turn`, dit qu'il n'y a rien à faire ce tour-ci, sinon relancer. Les deux dernières, `end_turn` et `tool_use`, demandent de lire le contenu : ce sera l'objet des étapes 3 et 4.

Et avant même de tester `stop_reason`, on range la réponse dans l'historique. Ainsi, quel que soit l'arrêt, `messages` contient tout ce que le modèle a dit.

## Un brouillon qui lit le contenu trop tôt

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — Dans ce brouillon, la fonction est un réceptionniste qui prend tout courrier sans pièce jointe pour une lettre achevée, sans regarder s'il a été déchiré en route : elle reçoit les mêmes paramètres que la version juste, appelle le modèle à chaque étape bornée, extrait les blocs `tool_use` et, s'il n'y en a aucun, renvoie le statut `fini` avec le texte de la réponse, sans jamais consulter `stop_reason`. Une réponse `max_tokens` au texte « coupé » devient ainsi une réponse finale, un refus au contenu vide aussi, et, comme la réponse du modèle n'est jamais rangée dans l'historique, le modèle ne verrait pas sa propre demande au tour suivant.

```python
# [extrait] brouillon
def executer_agent(llm, system, question, outils, schemas, max_etapes=8):
    messages = [{"role": "user", "content": question}]
    trace = []
    for etape in range(1, max_etapes + 1):
        reponse = llm.create(system=system, messages=messages, tools=schemas)
        appels = [b for b in reponse.content if b.type == "tool_use"]
        if not appels:                            # pas d'outil demandé : on croit tenir la réponse
            final = "".join(b.text for b in reponse.content if b.type == "text")
            return {"statut": "fini", "reponse": final, "trace": trace, "etapes": etape}
    return {"statut": "max_etapes", "trace": trace, "etapes": max_etapes}
```

Ce brouillon prend toute réponse sans outil pour une réponse finale. Avec `Reponse("max_tokens", [texte("coupé")])`, il rend `fini` et la réponse `"coupé"` : un client lirait une mensualité tronquée, par exemple « 5 5 » au lieu de « 5 558,32 AED ». Avec `Reponse("refusal", [])`, il rend `fini` avec une réponse vide. Le test `test_refus_et_troncature` refuse les deux : il attend `refus`, puis `tronque` **sans** clé `reponse`. Le brouillon oublie aussi de ranger la réponse du modèle dans `messages`, si bien que le modèle ne verrait jamais sa propre demande au tour suivant.

## L'appel au modèle et les trois arrêts de l'API

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la fonction de l'étape 1, dont le corps de boucle commence maintenant par le temps « décider », tenu par un greffier qui consigne chaque réponse avant même de la lire : à chaque étape, elle appelle une seule fois `llm.create` avec des arguments nommés, ajoute aussitôt la réponse telle quelle, le même objet liste, à l'historique sous le rôle `assistant`, puis examine `stop_reason`. Un `"refusal"` lui fait renvoyer le statut `refus`, un `"max_tokens"` le statut `tronque`, chacun avec la trace, le numéro de l'étape et l'historique mais sans clé `reponse`, et un `"pause_turn"` la fait passer au tour suivant sans rien exécuter ; une réponse tronquée « Mensualité estimée à 5 5 » reste ainsi visible dans l'historique sans jamais être servie au client.

```python
# [extrait] agent/boucle.py
def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    ...
    for etape in range(1, max_etapes + 1):
        reponse = llm.create(system=system, messages=messages, tools=schemas)
        messages.append({"role": "assistant", "content": reponse.content})   # tel quel, sans retouche
        if reponse.stop_reason == "refusal":
            return {"statut": "refus", "trace": trace, "etapes": etape, "messages": messages}
        if reponse.stop_reason == "max_tokens":
            return {"statut": "tronque", "trace": trace, "etapes": etape, "messages": messages}
        if reponse.stop_reason == "pause_turn":
            continue
        ...
```

**`reponse = llm.create(system=system, messages=messages, tools=schemas)`.** C'est le temps « décider », le seul appel au modèle de tout le tour. Les trois arguments sont **nommés** : la méthode `create` du port est déclarée `create(self, *, system, messages, tools)`, et l'étoile rend les arguments nommés obligatoires, comme dans le SDK officiel. Un appel positionnel, `llm.create(system, messages, schemas)`, lèverait `TypeError`. On passe `schemas` tels quels : la boucle ne les lit pas, elle les transmet. Le test `test_contenu_recopie_tel_quel_et_outils_transmis` vérifie que le faux modèle a bien reçu `[{"name": "x"}]`. En Java, c'est l'appel `llmPort.create(system, messages, tools)` sur une interface injectée ; le faux modèle joue le rôle d'un bouchon Mockito `when(...).thenReturn(r1, r2, r3)`.

**`messages.append({"role": "assistant", "content": reponse.content})`.** On range la réponse dans l'historique **avant** tout test, et on la range **telle quelle** : c'est le même objet liste que `reponse.content`, sans copie, sans filtrage, sans reformatage. Deux raisons à cela.

- Avec le vrai modèle, la réponse peut contenir des blocs de réflexion signés qui doivent revenir intacts au tour suivant, sinon l'API refuse la requête.
- Le modèle doit retrouver au tour suivant exactement les blocs `tool_use` qu'il a émis, avec leurs identifiants, pour rattacher chaque `tool_result` à sa demande.

Le test `test_contenu_recopie_tel_quel_et_outils_transmis` le vérifie avec `assertIs`, l'égalité d'identité, qui correspond au `==` de Java sur des références : `r["messages"][1]["content"] is llm.script[0].content`.

**Les deux arrêts « contenu non fiable ».** `"refusal"` rend `refus`, `"max_tokens"` rend `tronque`. Les deux dictionnaires ont les quatre clés du contrat, et `etapes` vaut le numéro du tour en cours, puisque le modèle vient d'être appelé `etape` fois. Ni l'un ni l'autre n'a de clé `reponse` : un texte refusé ou coupé ne doit jamais être présenté comme une réponse. À qui sert alors ce statut ? À l'appelant, qui décide : relancer avec une limite de tokens plus haute, reformuler, ou remonter le dossier à un humain.

**`pause_turn` et `continue`.** `continue` passe directement au tour suivant, comme en Java. La réponse en pause est déjà dans `messages` ; le prochain appel renvoie donc l'historique avec cette réponse, et le modèle reprend où il en était. On ne lit pas le contenu, on n'exécute rien, et on ne touche pas à `precedente`. Ce tour compte quand même dans `etapes` et dans la borne : un modèle qui ne ferait que des pauses serait arrêté par `max_etapes`.

**Le piège classique.** Tester `stop_reason` avec `is` au lieu de `==`, par exemple `reponse.stop_reason is "refusal"`. En Python, `is` compare les identités, comme `==` entre deux `String` en Java. Cela marche parfois par hasard, grâce à l'internement des chaînes courtes, et casse dès que la chaîne vient du réseau. On compare des valeurs avec `==`, comme on utilise `equals` en Java.

## Le test qui passe maintenant

```text
python -m unittest -v tests.test_05_boucle.TestArrets.test_refus_et_troncature
```

Ce test passe : `refusal` donne `refus`, `max_tokens` donne `tronque` en une étape, sans clé `reponse`. Dans la console, la réponse tronquée reste visible dans l'historique, ce qui permet de l'auditer sans jamais la servir :

```text
# [extrait] console
>>> from agent.boucle import executer_agent
>>> from agent.modele import FakeLLM, Reponse, texte
>>> r = executer_agent(FakeLLM([Reponse("max_tokens", [texte("Mensualité estimée à 5 5")])]), "s", "q", {}, [])
>>> r
{'statut': 'tronque', 'trace': [], 'etapes': 1, 'messages': [{'role': 'user', 'content': 'q'}, {'role': 'assistant', 'content': [Bloc(type='text', text='Mensualité estimée à 5 5', id='', name='', input={})]}]}
```

Les autres tests échouent encore. Une réponse `end_turn` ou `tool_use` traverse les trois `if` sans être traitée, la boucle rappelle le modèle, et le faux modèle finit par lever `RuntimeError("script épuisé …")`. C'est le comportement voulu du faux modèle : un scénario mal traité se voit tout de suite. L'étape suivante traite la réponse finale.
