# Étape 6 — L'enveloppe d'erreur

> Palier 04, étape 6 sur 7 · Précédent : [Étape 5 — Les définitions pour l'API](<05-Definitions-API.md>) · Suivant : [Étape 7 — Assemblage et démo](<07-Assemblage-et-demo.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Écris d'abord le contrat de `executer_appel`, en deux phrases, avant tout code. Elle reçoit un bloc `tool_use` et le dictionnaire des portes ; elle rend **toujours** un `tool_result` pour ce bloc et une ligne de trace, quoi qu'il arrive. Pourquoi « toujours » ?

- L'API exige qu'à chaque bloc `tool_use` du modèle réponde un bloc `tool_result` de même identifiant dans le message suivant. Si l'exécution d'un outil lève et que la boucle s'arrête, ou saute ce résultat, la conversation devient invalide.
- Une erreur est une information pour le modèle. Renvoyée avec `is_error`, elle lui permet de se corriger à l'étape suivante (le README chiffre le gain : 0,9 devient 0,999 avec deux relances, valeurs illustratives). Levée, elle arrête l'agent.

Le code suit : un `try` autour de tout, un seul `except` qui transforme n'importe quelle exception en résultat d'erreur.

## Bloc 1 — Sans filet

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_appel(outils, bloc)`** — Dans ce brouillon, la fonction est un coursier qui livre les commandes sans filet : elle reçoit le dictionnaire des portes et un bloc `tool_use`, appelle directement la porte du nom demandé avec les arguments du bloc dépliés, et renvoie un couple formé d'un `tool_result` à l'identifiant du bloc, dont le contenu est la sortie en JSON, et d'une ligne de trace. Le cas heureux marche, mais un outil inconnu comme « pirater » lève `KeyError` et arrête la boucle, une `ArgumentsInvalides` sort au lieu d'être lue par le modèle, et `json.dumps` sans option transforme chaque « é » en séquence d'échappement illisible dans la trace.

```python
# [extrait] brouillon
def executer_appel(outils: dict, bloc) -> tuple[dict, tuple]:
    sortie = outils[bloc.name](**bloc.input)
    return ({"type": "tool_result", "tool_use_id": bloc.id, "content": json.dumps(sortie)},
            (bloc.name, bloc.input, sortie))
```

Le cas heureux marche. Tout le reste fait sortir une exception. Un outil inconnu, `executer_appel({}, appel_outil("pirater", {}, "x"))`, lève `KeyError: 'pirater'` : la boucle s'arrête, et le modèle ne saura jamais que l'outil n'existe pas. Un argument mal formé fait sortir l'`ArgumentsInvalides` de la porte, alors que son message est précisément ce dont le modèle a besoin. Et `json.dumps(sortie)` sans option écrit chaque accent sous forme d'échappement : « é » devient `\u00e9`, lisible par une machine mais pas par un humain qui relit la trace.

## Bloc 2 — La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_appel(outils, bloc)`** — C'est la même fonction, devenue l'agent de liaison qui revient toujours avec un compte rendu, bon ou mauvais : elle reçoit le dictionnaire des appelables et un bloc `tool_use`, et place tout son travail dans un `try`, où elle lève volontairement une `ErreurOutil` « outil inconnu » si le nom manque, appelle sinon la porte avec les arguments dépliés et renvoie un `tool_result` dont le contenu est la sortie sérialisée avec `ensure_ascii=False`, accompagné de la trace (nom, arguments, sortie). Toute exception ordinaire est rattrapée par un seul `except Exception` qui renvoie un `tool_result` au contenu « NomDeLaClasse: message », marqué `is_error`, et une trace terminée par « ERREUR » ; un appel « tva » sur 100 AED rend ainsi 5,0 de TVA et 105,0 TTC, et un `n_mois` écrit « 300 » rend une erreur que le modèle lira pour se corriger.

```python
# [extrait] agent/outils.py
def executer_appel(outils: dict, bloc) -> tuple[dict, tuple]:
    """Exécute un bloc `tool_use` ; rend (tool_result, ligne de trace). Aucune exception ne sort.

    Succès : `content` est la sortie en JSON, la trace vaut (nom, arguments, sortie).
    Échec : `content` vaut « NomDeLException: message », `is_error` vaut True, et la trace porte
    « ERREUR message ». Un outil inconnu donne « ErreurOutil: outil inconnu : x ».
    Exemple : un appel à "tva" avec {"montant_ht": 100} donne le contenu '{"tva_aed": 5.0, "ttc_aed": 105.0}'.
    """
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

**La signature.** `outils` est le dictionnaire nom → porte de `appelables()` ; on l'annote `dict` parce que la boucle pourra lui passer d'autres appelables (au palier 09, les enveloppes de `proteger`). `bloc` n'est pas annoté : tout objet qui a `id`, `name` et `input` convient, un `Bloc` du palier 01 comme un bloc de l'API réelle. C'est du *duck typing* : en Java, on déclarerait une interface `ToolUse` avec trois accesseurs.

**L'outil inconnu, dans le `try`.** `if bloc.name not in outils: raise ErreurOutil(...)`. On lève volontairement, à l'intérieur du `try`, pour que ce cas passe par le même `except` que les autres et produise la même forme d'erreur : `ErreurOutil: outil inconnu : pirater`. Un seul chemin d'erreur, une seule forme.

**L'appel.** `outils[bloc.name](**bloc.input)` : on récupère la porte et on lui déplie le dictionnaire d'arguments du modèle en arguments nommés. Si les arguments sont mal formés, la porte lève `ArgumentsInvalides` ; si la fonction métier refuse, elle lève `ValueError` ; au palier 09, la politique lèvera `RefusPolitique`. Toutes ces exceptions arrivent au même `except`.

**Le succès.** Deux valeurs. Le `tool_result` : `type` vaut `"tool_result"`, `tool_use_id` reprend `bloc.id` (c'est lui qui relie la réponse à la demande, quand le modèle a demandé plusieurs outils dans la même réponse), et `content` est la sortie sérialisée par `json.dumps(sortie, ensure_ascii=False)`, qui garde les accents tels quels. Pas de clé `is_error` : son absence vaut succès. La ligne de trace `(bloc.name, bloc.input, sortie)` garde la sortie en objet Python, pas en texte : l'évaluation du palier 10 comparera ces lignes aux appels attendus.

**L'échec.** `except Exception as e` attrape toute erreur ordinaire, mais pas `KeyboardInterrupt` ni `SystemExit`, qui héritent de `BaseException` : un Ctrl+C doit toujours arrêter le programme. C'est le `catch (Exception e)` de Java, et non `catch (Throwable t)`. Le contenu vaut `f"{type(e).__name__}: {e}"` : le nom de la classe (`ArgumentsInvalides`, `ErreurOutil`, `ValueError`), deux-points, puis le message. La clé `is_error` vaut `True`. La trace porte `f"ERREUR {e}"` à la place de la sortie.

**« Pas avalée ».** Le commentaire de la ligne `except` dit l'essentiel : attraper toutes les exceptions est d'habitude une faute (`except: pass` les fait disparaître) ; ici, chaque exception est **transmise**, sous une autre forme, au modèle et à la trace. Rien ne se perd. C'est aussi la distinction de MCP (étape 46) : une erreur d'outil part dans le **résultat**, avec `isError`, pour que le modèle la lise ; une erreur de protocole (requête illisible) part dans le champ `error` de la réponse.

**Le piège de la sortie non sérialisable.** `json.dumps` est dans le `try`. Si un outil rendait un ensemble Python, `{1, 2}`, la sérialisation lèverait `TypeError: Object of type set is not JSON serializable`, et le modèle recevrait une erreur alors que l'outil a bien tourné. Pour un calcul, ce n'est qu'une gêne ; pour un outil à effet de bord, ce serait grave : l'effet a eu lieu, le modèle croit le contraire, et il risque de recommencer. Règle : un outil rend un dictionnaire de types JSON (nombres, chaînes, booléens, listes, dictionnaires).

**Vérification à la main.** Le bloc « tva » avec `{"montant_ht": 100}` : 100 × 0,05 = 5,0 de TVA, 105,0 TTC, donc le contenu `'{"tva_aed": 5.0, "ttc_aed": 105.0}'` et la trace `("tva", {"montant_ht": 100}, {"tva_aed": 5.0, "ttc_aed": 105.0})`. Le bloc « mensualite » avec `"n_mois": "300"` : la porte lève, le contenu vaut `ArgumentsInvalides: $.n_mois : type attendu integer, reçu string`, `is_error` vaut vrai, et la trace se termine par `ERREUR $.n_mois : type attendu integer, reçu string`.

**Les tests qui passent maintenant.** Tous ceux du palier :

```text
python -m unittest -v tests.test_04_outils.TestExecuterAppel tests.test_04_outils.TestRegistre.test_hierarchie_des_exceptions
```

`test_succes`, `test_erreur_renvoyee_avec_is_error` et `test_outil_inconnu` vérifient les trois cas ci-dessus au caractère près ; `test_hierarchie_des_exceptions` vérifie les deux parentés de l'étape 1 et que le contenu d'une erreur de schéma commence par `ArgumentsInvalides: `.

**Ce qu'il faut retenir.** `executer_appel` ne lève jamais : tout échec devient un `tool_result` marqué `is_error`, dont le contenu commence par le nom de la classe d'exception. La ligne de trace garde la sortie en objet, ou « ERREUR … ». Un outil rend un dictionnaire sérialisable en JSON.
