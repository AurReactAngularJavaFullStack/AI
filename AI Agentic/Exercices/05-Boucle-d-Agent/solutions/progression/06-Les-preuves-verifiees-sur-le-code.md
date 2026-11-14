# Étape 6 — Les preuves, vérifiées sur le code

> Progression du palier 05 · Précédent : [Étape 5 — L'arrêt boucle et la signature](<05-L-arret-boucle-et-la-signature.md>) · Suivant : [Étape 7 — Assemblage, tests et démo](<07-Assemblage-tests-et-demo.md>) · Retour à l'énoncé : [README du palier 05](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Onze tests verts montrent que la boucle traite onze scénarios. Ils ne montrent pas qu'elle termine pour **tout** modèle, ni combien elle coûte. Pour cela, on relie chaque garantie du rappel de cours à une ligne précise du code, puis on la mesure avec le faux modèle. C'est ce qu'on attend d'un développeur d'agents en entretien : savoir dire pourquoi la boucle s'arrête, et pas seulement montrer qu'elle s'est arrêtée sur un exemple.

## Garantie 1 — la boucle fait au plus E max appels au modèle

$$
N_{LLM} \le E_{max}
$$

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la boucle complète de l'étape 5, dont cet extrait ne garde que l'ossature qui porte la preuve, comme un inspecteur qui ne surligne, dans un règlement, que les deux phrases dont dépend la sécurité : la fonction reçoit le modèle, le prompt, la question, les outils, les schémas et la borne, 8 par défaut, et parcourt les étapes de 1 à `max_etapes` en appelant `llm.create` exactement une fois par tour. Si aucun `return` du corps ne l'a fait sortir, elle renvoie le statut `max_etapes` avec la trace, la borne comme nombre d'étapes et l'historique ; face à un faux modèle adversaire qui demande cent TVA différentes, elle s'arrête ainsi après 8 appels et 8 lignes de trace.

```python
# [extrait] agent/boucle.py
def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    ...
    for etape in range(1, max_etapes + 1):
        reponse = llm.create(system=system, messages=messages, tools=schemas)
        ...
    return {"statut": "max_etapes", "trace": trace, "etapes": max_etapes, "messages": messages}
```

**La preuve, en lisant ces lignes.** L'appel `llm.create` est la seule ligne du module qui appelle le modèle. Elle est dans le corps d'une boucle `for` sur `range(1, max_etapes + 1)`, qui a exactement E max éléments, et elle est exécutée une fois par tour. Les autres instructions du tour sont des `return` (qui sortent), un `continue` (qui passe au tour suivant) ou des appels d'outils (qui n'appellent pas le modèle). Aucun chemin ne fait donc plus d'un appel par tour, ni plus de E max tours. La borne ne dépend pas du modèle : elle vaut pour un modèle adversaire.

**La mesure.** Un faux modèle qui demanderait cent fois la TVA, avec un montant différent à chaque fois pour échapper à l'arrêt `boucle`, est arrêté au huitième appel :

```text
# [extrait] console
>>> from agent.boucle import executer_agent
>>> from agent.modele import FakeLLM, Reponse, appel_outil, fiabilite_serie
>>> from agent.outils import Registre, enregistrer_outils_metier
>>> outils = enregistrer_outils_metier(Registre()).appelables()
>>> adversaire = FakeLLM([Reponse("tool_use", [appel_outil("tva", {"montant_ht": v}, f"t{v}")]) for v in range(1, 101)])
>>> r = executer_agent(adversaire, "s", "q", outils, [])
>>> r["statut"], r["etapes"], adversaire.appels, len(r["trace"])
('max_etapes', 8, 8, 8)
```

`adversaire.appels` est le compteur du faux modèle : 8 appels sur les 100 réponses prévues. Le test `test_max_etapes_borne_les_appels` vérifie la même chose avec `max_etapes=2`.

## Garantie 2 — une tâche de k étapes d'outils coûte k + 1 appels

$$
N_{LLM} = k + 1
$$

Chaque étape d'outils commence par un appel au modèle, celui qui produit les blocs `tool_use`. La réponse finale en demande un de plus, celui qui lit les derniers résultats et rédige. Sans `pause_turn`, on a donc k + 1 appels. Dans le scénario du crédit, la deuxième étape demande **deux** outils, mais c'est une seule étape : k = 2, et `r["etapes"] == 3`, ce que vérifie `test_trois_etapes_et_sorties`. Si le modèle avait demandé la conversion à part, k vaudrait 3 et la tâche coûterait 4 appels. C'est le bénéfice concret du message unique de l'étape 4 : il permet au modèle de grouper ses demandes.

## Garantie 3 — E appels relisent E² messages

$$
\lvert M_e \rvert = 2e - 1
$$

$$
\sum_{e=1}^{E} (2e - 1) = E^{2}
$$

**La preuve.** Au premier appel, l'historique ne contient que la question : 1 message. Chaque tour d'outils ajoute exactement deux messages, la réponse du modèle (`messages.append({"role": "assistant", …})`) et le message unique de résultats (`messages.append({"role": "user", …})`). Au e-ième appel, l'historique contient donc 1 + 2(e − 1) = 2e − 1 messages. La somme des E premiers nombres impairs vaut E² : c'est vrai pour E = 1 (1 = 1²), et passer de E − 1 à E ajoute 2E − 1 = E² − (E − 1)².

**La mesure.** Le faux modèle garde une copie de l'historique reçu à chaque appel, dans `requetes`. On reprend l'adversaire de la garantie 1 :

```text
# [extrait] console
>>> [len(q["messages"]) for q in adversaire.requetes]
[1, 3, 5, 7, 9, 11, 13, 15]
>>> sum(len(q["messages"]) for q in adversaire.requetes)
64
```

Huit appels relisent 64 = 8² messages ; le scénario du crédit en relit 1 + 3 + 5 = 9 = 3². Si l'on avait envoyé un message par résultat (brouillon de l'étape 4), chaque tour à deux outils en ajouterait trois, et le total croîtrait plus vite encore. C'est pourquoi `max_etapes` doit rester bas : le coût en tokens d'entrée suit ce carré, pas le nombre d'appels.

## Garantie 4 — chaque étape de plus coûte de la fiabilité

$$
P(\text{succès}) = \prod_{i=1}^{n} p_i
$$

La boucle ne calcule pas cette formule : elle la subit. Le scénario du crédit enchaîne n = 6 étapes, trois appels au modèle et trois exécutions d'outils. Le palier 01 a écrit la fonction qui fait ce produit :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fiabilite_serie(probas)`** — C'est la fonction du palier 01, l'ingénieur qui inspecte une chaîne dont chaque maillon peut céder : elle reçoit la liste des probabilités de réussite des étapes, lève `ValueError` si la liste est vide ou si l'une des valeurs sort de [0, 1], et renvoie leur produit, calculé par `math.prod` à partir de 1. Appliquée aux six étapes du scénario du crédit, trois appels au modèle et trois exécutions d'outils fiables à 0,98, elle donne 0,8858, et une septième étape ferait tomber la chaîne à 0,8681 : c'est le chiffre qui justifie de grouper les demandes d'outils dans une même réponse.

```python
# [extrait] agent/modele.py
def fiabilite_serie(probas: list[float]) -> float:
    ...
    if not probas:
        raise ValueError("il faut au moins une étape")
    if not all(0.0 <= p <= 1.0 for p in probas):
        raise ValueError("chaque probabilité doit être dans [0, 1]")
    return math.prod(probas)
```

`math.prod` multiplie les éléments de la liste, comme une réduction `stream().reduce(1.0, (a, b) -> a * b)` en Java. Avec pᵢ = 0,98 pour chaque étape :

```text
# [extrait] console
>>> round(fiabilite_serie([0.98] * 6), 4), round(fiabilite_serie([0.98] * 7), 4)
(0.8858, 0.8681)
```

Six étapes donnent 0,98⁶ ≈ 0,8858 ; une septième, par exemple un quatrième appel au modèle pour la conversion, ferait tomber la chaîne à 0,98⁷ ≈ 0,8681. Chaque facteur est au plus égal à 1, donc ajouter une étape ne peut que faire baisser le produit. D'où trois choix de conception, tous visibles dans la boucle : les calculs passent par des outils déterministes (fiabilité proche de 1), les demandes groupées partent ensemble, et les arrêts coupent court au lieu d'ajouter des tours inutiles.

## Ce qu'il faut retenir

| Garantie | Ligne du code qui la porte | Test ou mesure |
|---|---|---|
| au plus E max appels | `for etape in range(1, max_etapes + 1)` et un seul `llm.create` par tour | `test_max_etapes_borne_les_appels`, adversaire arrêté à 8 |
| k + 1 appels pour k étapes d'outils | un appel par tour, tous les résultats d'un tour dans un message | `test_trois_etapes_et_sorties` : 3 étapes |
| E² messages relus | deux `messages.append` par tour d'outils | `requetes` : 1, 3, 5, …, 15 ; somme 64 |
| fiabilité en produit | moins d'étapes grâce aux demandes groupées | `fiabilite_serie` : 0,8858 contre 0,8681 |

L'étape suivante assemble le module complet, lance tous les tests et la démo.
