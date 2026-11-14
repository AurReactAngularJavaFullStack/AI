# Étape 6 — La boucle de réparation

> Palier 02, étape 6 sur 8 · Précédent : [Étape 5 — Lire puis valider](<05-Lire-et-valider.md>) · Suivant : [Étape 7 — Les probabilités de la réparation](<07-Probabilites-de-reparation.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire `reparer`, la première boucle du paquet qui parle au modèle, sur le `FakeLLM` du palier 01. Les tests `test_une_relance_suffit`, `test_echec_apres_max_essais` et `test_refus_traite_avant_le_contenu` passent à la fin.

## Comment raisonner

On a tout ce qu'il faut : un port LLM (`llm.create`), un faux modèle pour les tests, et `lire_et_valider` qui dit si un texte est un JSON conforme. La boucle de réparation les relie : demander un JSON, le valider, et, s'il est faux, **renvoyer les erreurs au modèle** pour qu'il corrige, au plus `max_essais` fois, avant de passer la main à un humain.

Avant d'écrire la boucle, on fixe ses **sorties**, parce qu'il y en a quatre et que l'appelant doit pouvoir les distinguer :

| Statut | Quand | Ce que fait l'appelant |
| --- | --- | --- |
| `"valide"` | un essai a produit un JSON conforme | il utilise les données |
| `"echec"` | `max_essais` essais ratés | il envoie le dossier en revue humaine |
| `"refusal"` | le modèle refuse de répondre | il n'insiste pas : un refus ne se répare pas |
| `"max_tokens"` | la réponse a été coupée | il augmente la limite ou découpe la demande |

On rend toujours le même dictionnaire de quatre clés (`statut`, `donnees`, `essais`, `erreurs`), quel que soit le statut : l'appelant n'a jamais à tester la présence d'une clé.

Ensuite, on ordonne le corps de la boucle selon une règle de l'API vue au palier 01 : **le `stop_reason` se lit avant le contenu**. Une réponse coupée ou refusée peut contenir un texte partiel qui ressemble à du JSON ; le valider n'aurait pas de sens.

Enfin, on décide de ce que voit le modèle au tour suivant : sa propre réponse fautive, recopiée telle quelle, puis un message qui liste les erreurs avec leurs chemins. C'est ce qui distingue la réparation d'une simple relance : chaque essai reçoit plus d'information que le précédent.

## Le brouillon qui ne s'arrête pas

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`reparer(llm, schema, demande)`** — Dans ce brouillon, la fonction ressemble à un employé qui renverrait sans fin le même formulaire avec pour seule annotation « Recommence. » : elle reçoit le modèle, le schéma et la demande, ouvre un historique avec cette demande, puis, dans une boucle `while True` sans borne, appelle le modèle sans prompt système, lit le texte du premier bloc sans jamais regarder `stop_reason`, et renvoie un dictionnaire de statut « valide » dès que `lire_et_valider` ne trouve plus d'erreur. Sinon elle ajoute un message « Recommence. » qui ne contient ni les erreurs ni la réponse fautive ; un modèle qui se trompe toujours fait alors tourner la boucle indéfiniment, et un refus au contenu vide la fait planter sur `IndexError`.

```python
# [extrait] brouillon
def reparer(llm, schema: dict, demande: str) -> dict:
    messages = [{"role": "user", "content": demande}]
    while True:                                          # aucune borne
        reponse = llm.create(system="", messages=messages, tools=[])
        donnees, erreurs = lire_et_valider(reponse.content[0].text, schema)   # stop_reason jamais lu
        if not erreurs:
            return {"statut": "valide", "donnees": donnees}
        messages.append({"role": "user", "content": "Recommence."})          # sans les erreurs
```

Ce brouillon accumule les fautes classiques d'une première boucle d'agent.

- **`while True`** : un modèle qui se trompe toujours fait tourner la boucle sans fin, chaque tour coûtant un appel facturé. Avec le faux modèle, le script s'épuise et lève `RuntimeError` ; avec le vrai, la facture monte. Toute boucle qui appelle un modèle doit être bornée.
- **`stop_reason` jamais lu** : un refus (`content` vide) fait planter `reponse.content[0]` avec `IndexError` ; une réponse tronquée est validée comme si elle était complète.
- **`reponse.content[0].text`** : on suppose un seul bloc de texte, alors qu'une réponse peut en contenir plusieurs.
- **« Recommence. » sans les erreurs** : le modèle ne sait pas ce qu'il a mal fait, et sa réponse fautive n'est même pas dans l'historique. Il a autant de chances de se tromper au deuxième essai qu'au premier.
- **pas de prompt système** : le modèle ne connaît pas le schéma qu'il doit respecter.

## La version correcte

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`reparer(llm, schema, demande, max_essais)`** — La version correcte est celle d'un chef de bureau méthodique qui accorde un nombre fixe de chances et souligne chaque fois les cases fautives : elle reçoit le modèle, le schéma, la demande et `max_essais`, 3 par défaut, lève `ValueError` avant tout appel si ce nombre est inférieur à 1, compose un système qui contient le schéma en JSON, puis fait au plus `max_essais` essais numérotés à partir de 1. À chaque essai, elle s'arrête aussitôt sur `"refusal"` ou `"max_tokens"`, concatène sinon le texte de tous les blocs `"text"`, le lit et le valide, note la liste d'erreurs de l'essai, renvoie « valide » si elle est vide, et ajoute sinon la réponse fautive recopiée telle quelle puis un message qui liste les erreurs avec leurs chemins. Après le dernier essai raté, elle renvoie « echec » ; le résultat est toujours un dictionnaire aux quatre clés `statut`, `donnees`, `essais` et `erreurs`.

```python
# [extrait] agent/schemas.py
def reparer(llm, schema: dict, demande: str, max_essais: int = 3) -> dict:
    ...
    if max_essais < 1:
        raise ValueError("max_essais doit valoir au moins 1")
    system = "Réponds uniquement par un objet JSON conforme à ce schéma : " + json.dumps(schema, ensure_ascii=False)
    messages = [{"role": "user", "content": demande}]
    erreurs_par_essai = []
    for essai in range(1, max_essais + 1):
        reponse = llm.create(system=system, messages=messages, tools=[])
        if reponse.stop_reason in ("refusal", "max_tokens"):
            return {"statut": reponse.stop_reason, "donnees": None, "essais": essai, "erreurs": erreurs_par_essai}
        brut = "".join(b.text for b in reponse.content if b.type == "text")
        donnees, erreurs = lire_et_valider(brut, schema)
        erreurs_par_essai.append(erreurs)
        if not erreurs:
            return {"statut": "valide", "donnees": donnees, "essais": essai, "erreurs": erreurs_par_essai}
        messages.append({"role": "assistant", "content": reponse.content})
        messages.append({"role": "user", "content": "Ta réponse ne respecte pas le schéma :\n" + "\n".join(erreurs)
                         + "\nRenvoie uniquement l'objet JSON corrigé."})
    return {"statut": "echec", "donnees": None, "essais": max_essais, "erreurs": erreurs_par_essai}
```

La ligne `...` remplace la docstring.

**La garde, en premier.** `max_essais < 1` lève `ValueError` **avant** tout appel au modèle. Le test `test_refus_traite_avant_le_contenu` le vérifie avec `reparer(FakeLLM([]), ..., max_essais=0)` : si la garde venait après l'appel, le faux modèle au script vide lèverait `RuntimeError` et le test échouerait.

**Le prompt système.** La consigne, puis le schéma sérialisé en JSON. `ensure_ascii=False` garde les caractères accentués tels quels au lieu de les écrire sous forme d'échappement (`\u00e9` pour é) : le modèle lit un texte plus court et plus clair. C'est ici le schéma **complet**, bornes comprises : on ne passe pas par l'outil strict de l'API, la consigne est dans le texte.

**`messages` et `erreurs_par_essai`.** L'historique de la conversation commence par la demande ; la liste des erreurs recevra une liste par essai lu, pour mesurer (étape 11 du cours) à quel essai on réussit et sur quel champ on échoue.

**`for essai in range(1, max_essais + 1):`** `range(1, 4)` donne 1, 2 et 3 : on numérote les essais à partir de 1, comme on les compte à voix haute. La borne de la boucle est la borne du coût : au plus `max_essais` appels au modèle, quoi qu'il réponde. C'est le `@Retryable(maxAttempts = 3)` de Spring Retry, avec une différence de fond : Spring rejoue la même requête, alors qu'ici chaque essai reçoit les erreurs du précédent.

**`if reponse.stop_reason in ("refusal", "max_tokens"): return ...`.** Le `stop_reason` est lu **avant** le contenu. Le statut rendu est la raison d'arrêt elle-même. `erreurs_par_essai` n'est pas complétée : l'essai n'a pas été lu, il n'a donc pas d'erreurs de validation.

**`brut = "".join(b.text for b in reponse.content if b.type == "text")`.** On concatène le texte de **tous** les blocs de type `"text"`, et l'on ignore les autres (un bloc d'appel d'outil, un bloc de réflexion du vrai modèle). C'est la forme des blocs définie au palier 01 qui rend cette ligne possible.

**`donnees, erreurs = lire_et_valider(brut, schema)`** puis **`erreurs_par_essai.append(erreurs)`.** On note les erreurs de l'essai, même quand la liste est vide : le dernier élément vide signale l'essai réussi.

**`if not erreurs: return {"statut": "valide", ...}`.** Succès : on rend les données et le numéro de l'essai.

**Les deux messages ajoutés.** D'abord la réponse fautive, rôle `assistant`, contenu `reponse.content` recopié **tel quel** : c'est une règle de l'API (le modèle a besoin de voir ce qu'il a écrit, blocs de réflexion compris). Ensuite un message `user` qui liste les erreurs une par ligne, avec leurs chemins, et redemande le JSON. L'expression est coupée sur deux lignes à l'intérieur des parenthèses de l'appel, ce que Python permet sans caractère de continuation.

**`return {"statut": "echec", ..., "essais": max_essais, ...}`.** On n'arrive ici qu'après `max_essais` essais ratés. L'appelant passe la main à un humain plutôt que de deviner.

**Le piège classique : renvoyer les erreurs sans la réponse fautive.** Le message « `$.duree_mois` : type attendu integer » n'a de sens qu'à côté du JSON qui contenait `"duree_mois": "36"`. Sans le message `assistant`, le modèle ne verrait plus le texte à corriger et devrait tout réécrire de mémoire, avec autant de chances de se tromper qu'au premier essai.

## Ce que voit le modèle au deuxième essai

On rejoue le scénario du test `test_une_relance_suffit` : un faux modèle `llm` dont le script contient la demande avec `"duree_mois": "36"`, puis la demande correcte, et l'appel `reparer(llm, SCHEMA_DEMANDE_CREDIT, "Prêt de 150 000 AED sur 36 mois")`. On affiche ensuite les messages reçus au deuxième appel :

```text
# [extrait] console
>>> for m in llm.requetes[1]["messages"]: print(m["role"], "→", m["content"])
user → Prêt de 150 000 AED sur 36 mois
assistant → [Bloc(type='text', text='{"montant_aed": 150000, "duree_mois": "36", "revenu_mensuel_aed": 25000, "emirates_id": "784-1990-1234567-1"}', id='', name='', input={})]
user → Ta réponse ne respecte pas le schéma :
$.duree_mois : type attendu integer, reçu string
Renvoie uniquement l'objet JSON corrigé.
```

C'est le champ `requetes` du `FakeLLM`, écrit au palier 01, qui permet de le vérifier : la copie de la liste prise au deuxième appel contient trois messages. Le test `test_une_relance_suffit` lit le dernier et vérifie qu'il contient le chemin `$.duree_mois`.

## Les tests qui passent maintenant

```powershell
python -m unittest -v tests.test_02_schemas.TestReparation.test_une_relance_suffit tests.test_02_schemas.TestReparation.test_echec_apres_max_essais tests.test_02_schemas.TestReparation.test_refus_traite_avant_le_contenu
```

- `test_une_relance_suffit` : une durée `"36"` puis une demande correcte donnent `"valide"`, 2 essais, 2 appels, les bonnes données, et `erreurs` vaut `[["$.duree_mois : type attendu integer, reçu string"], []]`.
- `test_echec_apres_max_essais` : trois réponses avec un montant nul donnent `"echec"`, 3 essais, 3 appels, `donnees` à `None`.
- `test_refus_traite_avant_le_contenu` : un refus donne `"refusal"`, 1 essai, aucune liste d'erreurs ; `max_essais=0` lève `ValueError`.

## Ce qu'il faut retenir

- Toute boucle qui appelle un modèle est bornée : `for essai in range(1, max_essais + 1)`.
- Le `stop_reason` se lit avant le contenu : un refus ne se répare pas.
- Une réparation renvoie au modèle sa réponse fautive **et** la liste des erreurs avec leurs chemins.
- Le résultat a toujours la même forme, quel que soit le statut.

> Suivant : [Étape 7 — Les probabilités de la réparation](<07-Probabilites-de-reparation.md>)
