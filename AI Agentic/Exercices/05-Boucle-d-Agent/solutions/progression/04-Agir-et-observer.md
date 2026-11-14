# Étape 4 — Agir et observer

> Progression du palier 05 · Précédent : [Étape 3 — La réponse finale](<03-La-reponse-finale.md>) · Suivant : [Étape 5 — L'arrêt boucle et la signature](<05-L-arret-boucle-et-la-signature.md>) · Retour à l'énoncé : [README du palier 05](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Si la réponse n'est ni un arrêt de l'API ni une réponse finale, elle contient au moins un bloc `tool_use`. C'est le temps « agir » : exécuter chaque outil demandé. Puis vient le temps « observer » : renvoyer chaque résultat au modèle, rattaché à sa demande. Trois questions avant d'écrire.

1. **Qui exécute l'outil ?** Pas la boucle. Le palier 04 a écrit `executer_appel(outils, bloc)`, qui cherche l'outil, l'appelle à travers sa porte (validation du schéma) et transforme le succès comme l'échec en `tool_result`. La boucle se contente de l'appeler : elle ne connaît ni les schémas, ni les exceptions des outils.
2. **Que faire d'une erreur ?** La renvoyer au modèle, jamais l'avaler. `executer_appel` s'en charge déjà : il ne lève jamais, et marque l'échec avec `is_error`. La boucle n'a donc pas besoin de `try`.
3. **Combien de messages pour les résultats ?** Un seul, pour tous les résultats de l'étape. L'API attend, après un message `assistant` qui contient n blocs `tool_use`, **un** message `user` qui contient les n `tool_result` correspondants. C'est aussi ce qui apprend au modèle qu'il peut demander plusieurs outils à la fois.

## Ce que rend `executer_appel` (palier 04)

Avant de l'appeler, on relit son contrat. Le voici, tel qu'il est dans le module du palier 04, que l'on ne modifie pas :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_appel(outils, bloc)`** — C'est la fonction du palier 04, l'agent de liaison qui revient toujours avec un compte rendu : elle reçoit le dictionnaire nom → porte et un bloc `tool_use`, lève à l'intérieur de son `try` une `ErreurOutil` « outil inconnu » si le nom manque, appelle sinon la porte avec les arguments du bloc dépliés en arguments nommés, et renvoie un couple formé d'un `tool_result` à l'identifiant du bloc, dont le contenu est la sortie en JSON, et de la ligne de trace (nom, arguments, sortie). Toute exception devient un `tool_result` au contenu « NomDeLException: message », marqué `is_error`, avec une trace « ERREUR message » ; la boucle n'a donc besoin d'aucun `try` pour l'appeler, et la mensualité de C-1 lui revient sous la forme `'{"mensualite_aed": 5558.32}'`.

```python
# [extrait] agent/outils.py
def executer_appel(outils: dict, bloc) -> tuple[dict, tuple]:
    ...
    try:
        if bloc.name not in outils:
            raise ErreurOutil(f"outil inconnu : {bloc.name}")
        sortie = outils[bloc.name](**bloc.input)
        return ({"type": "tool_result", "tool_use_id": bloc.id, "content": json.dumps(sortie, ensure_ascii=False)},
                (bloc.name, bloc.input, sortie))
    except Exception as e:                    # l'erreur repart vers le modèle, elle n'est pas avalée
        return ({"type": "tool_result", "tool_use_id": bloc.id, "content": f"{type(e).__name__}: {e}",
                 "is_error": True}, (bloc.name, bloc.input, f"ERREUR {e}"))
```

Il rend toujours un couple : le bloc `tool_result` à envoyer au modèle, et la ligne de trace `(nom, arguments, sortie)`. En cas de succès, le contenu est la sortie en JSON, par exemple `'{"mensualite_aed": 5558.32}'`. En cas d'échec, le contenu est `"NomDeLException: message"`, `is_error` vaut `True`, et la sortie de la trace est la chaîne `"ERREUR message"`. `**bloc.input` déplie le dictionnaire des arguments en arguments nommés : `outils["mensualite"](principal=1000000, taux_annuel=0.045, n_mois=300)`. Dans l'étape 77, ce `try` était écrit dans la boucle elle-même ; le découper en fonction permet de le tester seul, et de traiter l'outil inconnu proprement, avec `ErreurOutil` au lieu d'un `KeyError` brut.

## Un brouillon qui envoie un message par résultat

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`agir(outils, appels, messages, trace)`** — Ce brouillon est un facteur zélé qui poste chaque réponse dans une enveloppe séparée alors que le destinataire les attend toutes dans le même pli : il reçoit les portes, la liste des blocs `tool_use` de l'étape, l'historique et la trace, et, pour chaque appel, demande le résultat à `executer_appel`, ajoute la ligne de trace et ajoute aussitôt un message `user` qui ne contient que ce seul résultat. Il ne renvoie rien et modifie les listes reçues ; sur le scénario du crédit, les deux résultats du ratio et de la conversion partent dans deux messages `user` consécutifs, historique que la vraie API refuse, et l'historique final compte 7 messages au lieu de 6.

```python
# [extrait] brouillon
def agir(outils, appels, messages, trace):
    for b in appels:
        resultat, ligne = executer_appel(outils, b)
        trace.append(ligne)
        messages.append({"role": "user", "content": [resultat]})   # un message par résultat : FAUX
```

Sur le scénario du crédit, la deuxième réponse du modèle demande `ratio_endettement` et `convertir_aed_usd`. Ce brouillon ajoute deux messages `user` de suite, et le troisième appel au modèle reçoit un historique `user, assistant, user, assistant, user, user`. Deux défauts en découlent.

- La vraie API refuse cet historique : les deux `tool_result` répondent au même message `assistant`, ils doivent partir ensemble.
- Le test `test_tous_les_resultats_dans_un_seul_message` échoue : il attend que le dernier message reçu au troisième appel contienne `a2` **et** `a3`, et que l'historique final compte 6 messages, pas 7.

Avec ce brouillon, sept des onze tests passent ; avec la version juste, huit. L'étape 13 du cours pose la question en exercice : « une variante ajoute un message `user` par `tool_result` : quel cas la révèle ? » C'est ce test.

## Exécuter les appels et renvoyer tous les résultats ensemble

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la boucle des étapes précédentes, qui reçoit ici la fin de son corps, les temps « agir » et « observer », tenus par un facteur qui réunit toutes les réponses du jour dans un seul pli : pour chaque bloc `tool_use` de la réponse, dans l'ordre où le modèle les a émis, elle obtient de `executer_appel` un `tool_result` et une ligne de trace, range le premier dans une liste neuve `resultats` et la seconde dans `trace`. Après la boucle sur les appels, et pas dedans, elle ajoute un seul message `user` qui contient tous les résultats, puis repart pour l'étape suivante ; sur le scénario du crédit, le troisième appel reçoit ainsi 5 messages, dont le dernier contient `a2` puis `a3`, et l'historique final en compte 6.

```python
# [extrait] agent/boucle.py
def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    ...
    for etape in range(1, max_etapes + 1):
        ...
        resultats = []
        for b in appels:
            resultat, ligne = executer_appel(outils, b)
            resultats.append(resultat)
            trace.append(ligne)
        messages.append({"role": "user", "content": resultats})   # tous les résultats dans UN message
    ...
```

Ces six lignes ferment le corps de la boucle. À l'étape 5, quatre lignes viendront s'intercaler juste avant elles, pour l'arrêt `boucle` ; pour l'instant, elles suivent directement le `return` de la réponse finale.

**`resultats = []`.** Une liste neuve à chaque tour : elle recevra les `tool_result` de ce tour seulement.

**`for b in appels:`.** On parcourt les appels dans l'ordre où le modèle les a émis. Les résultats sont donc dans le même ordre que les demandes, ce que le test vérifie avec `["a2", "a3"]`. Le modèle n'en dépend pas, puisque chaque résultat porte son `tool_use_id`, mais un ordre stable rend la trace lisible et les tests déterministes.

**`resultat, ligne = executer_appel(outils, b)`.** Le temps « agir ». L'affectation multiple déballe le couple rendu, comme on lirait les deux champs d'un `record Pair(Map resultat, Ligne ligne)` en Java. Pas de `try` ici : `executer_appel` ne lève jamais, c'est son contrat.

**`resultats.append(resultat)` et `trace.append(ligne)`.** Le `tool_result` part vers le modèle, et la ligne de trace reste côté programme, pour l'audit. La trace n'est jamais envoyée au modèle : elle contient les objets Python (le dictionnaire `{"ratio": 0.289, "recevable": True}`), tandis que le modèle reçoit leur JSON (`'{"ratio": 0.289, "recevable": true}'`, avec `true` en minuscules).

**`messages.append({"role": "user", "content": resultats})`.** Le temps « observer » : un seul message `user` pour tous les résultats du tour, **après** la boucle sur les appels, pas dedans. Le rôle est `user` parce que, du point de vue de l'API, tout ce qui n'est pas le modèle parle au nom de l'utilisateur. Puis la boucle `for etape` repart : au tour suivant, le modèle reçoit l'historique complet, avec ses demandes et leurs résultats.

**Le piège classique.** Indenter le `messages.append(...)` d'un cran de trop, ce qui le place dans la boucle `for b in appels`. On retombe exactement sur le brouillon : un message par résultat. En Python, l'indentation est la syntaxe des blocs, comme les accolades en Java ; un cran de trop change le programme.

## La trace du scénario, tour par tour

Voici ce que le faux modèle reçoit à chaque appel, dans le scénario du crédit de l'étape 77 :

```text
appel 1 : 1 message   [user q]
          réponse : tool_use mensualite(a1)          → exécuté : {"mensualite_aed": 5558.32}
appel 2 : 3 messages  [user q, assistant [a1], user [résultat a1]]
          réponse : tool_use ratio(a2), conversion(a3) → exécutés : {"ratio": 0.289, "recevable": True}, {"montant_usd": 1513.5}
appel 3 : 5 messages  [… , assistant [a2, a3], user [résultat a2, résultat a3]]
          réponse : end_turn « Dossier recevable. »  → fini, 3 étapes, 6 messages au total
```

Les nombres se refont à la main : (6 000 + 5 558,32) / 40 000 = 0,288958, arrondi à 0,289 ; 5 558,32 / 3,6725 = 1 513,4976, arrondi à 1 513,50 USD.

## Les tests qui passent maintenant

```text
python -m unittest -v tests.test_05_boucle.TestScenarioCredit tests.test_05_boucle.TestErreurs.test_erreur_d_outil_renvoyee_au_modele tests.test_05_boucle.TestArrets.test_max_etapes_borne_les_appels
```

- Les trois tests de `TestScenarioCredit` : les trois sorties, le message unique `["a2", "a3"]` et les 6 messages de l'historique.
- `test_erreur_d_outil_renvoyee_au_modele` : le montant −5 est refusé par la porte, le modèle reçoit `ArgumentsInvalides: $.montant_ht : -5 < minimum 0` avec `is_error`, la trace porte `ERREUR $.montant_ht : -5 < minimum 0`, et le modèle conclut au tour 2.
- `test_max_etapes_borne_les_appels` : trois demandes différentes avec `max_etapes=2` donnent deux outils exécutés, deux appels au modèle et le statut `max_etapes`. La borne écrite à l'étape 1 fait enfin son travail.

Huit tests sur onze passent. Les trois derniers concernent la répétition d'une même action, et la signature qui permet de la voir.
