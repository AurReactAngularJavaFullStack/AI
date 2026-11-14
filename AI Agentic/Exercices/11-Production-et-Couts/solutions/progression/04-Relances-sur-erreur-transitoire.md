# Étape 4 — Les relances sur erreur transitoire

> Palier 11 · Étape 4 sur 7 · Précédent : [Étape 3 — L'attente exponentielle et la gigue](<03-Attente-exponentielle-et-gigue.md>) · Suivant : [Étape 5 — Les percentiles et le p95](<05-Percentiles-et-p95.md>) · Énoncé : [README du palier 11](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Une relance ne se décide pas sur « il y a eu une erreur », mais sur « cette erreur peut disparaître toute seule ». Une surcharge du fournisseur (529), une limite de débit (429) ou une coupure réseau passent en quelques secondes : on réessaie. Une requête mal formée (400), un argument refusé par le schéma ou un refus de politique du palier 09 donneront la même erreur à chaque essai : relancer gaspille des appels facturés et retarde le message d'erreur. Il faut donc une **exception à part** pour ce qui mérite une relance, et n'attraper qu'elle.

Les trois tests de `TestRelances` fixent ensuite le contrat. Une fonction qui échoue deux fois puis réussit donne trois tentatives, des attentes `[1, 2]` et une horloge avancée de 3 s. Une fonction qui échoue toujours, avec quatre tentatives, donne quatre erreurs mais **trois** attentes : on n'attend pas après le dernier échec, puisqu'il n'y a plus rien à attendre. Et une `ValueError` remonte après un seul appel.

L'ordre d'écriture : l'exception, puis la boucle des tentatives, puis le résultat d'échec après la boucle.

## L'exception qui mérite une relance

```python
# [extrait] agent/production.py
class ErreurTransitoire(Exception):
    """Erreur qui vaut d'être relancée : surcharge, limite de débit (429), coupure réseau."""
```

Une classe vide, qui hérite d'`Exception` : son seul rôle est d'être reconnue par un `except`. La docstring suffit comme corps. C'est l'équivalent d'une `class ErreurTransitoire extends RuntimeException {}` en Java, que l'on passerait à `@Retryable(retryFor = ErreurTransitoire.class)` pour dire à Spring Retry quoi relancer. Le code qui appelle le modèle traduira les erreurs du fournisseur (429, 529, délai dépassé) en `ErreurTransitoire`, et laissera toutes les autres telles quelles.

## Une première version, avec quatre erreurs

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_avec_relances(fonction, max_tentatives)`** — Ce brouillon est un livreur têtu qui sonne à la porte jusqu'à quatre fois, même quand on lui a crié par l'interphone que le destinataire n'habite pas là, puis qui repart sans laisser d'avis de passage. Il reçoit la fonction à appeler et le nombre de tentatives, quatre par défaut, appelle la fonction et rend aussitôt son résultat en cas de succès ; à la moindre exception, quelle qu'elle soit, il dort pour de vrai 2ᵏ⁻¹ secondes avec `time.sleep`, y compris après le dernier échec, puis recommence. S'il épuise ses tentatives, il rend `None`, sans dire combien d'essais ont eu lieu ni pourquoi ils ont échoué : une erreur 400 est relancée quatre fois et le test attend 15 secondes réelles.

```python
# [extrait] brouillon
import time


def executer_avec_relances(fonction, max_tentatives=4):
    for tentative in range(1, max_tentatives + 1):
        try:
            return fonction()
        except Exception:                          # relance aussi une requête invalide (400)
            time.sleep(2 ** (tentative - 1))      # vraie attente, même après le dernier échec
    return None                                    # l'appelant ne sait ni pourquoi ni combien de fois
```

**`except Exception` relance tout**, y compris la `ValueError("400 : requête invalide")` du test, appelée alors quatre fois au lieu d'une. **`time.sleep` attend pour de vrai** : un test de quatre tentatives dure 1 + 2 + 4 + 8 = 15 s, et la sortie n'est plus reproductible. **L'attente a lieu aussi après le dernier échec**, 8 s perdues pour rien avant de rendre la main. Et **`return None` efface l'histoire** : l'appelant ne sait pas si `None` est un résultat légitime ou un échec, ni combien de tentatives ont eu lieu, ni pourquoi elles ont échoué. On ne peut ni journaliser, ni alerter, ni facturer correctement.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_avec_relances(fonction, max_tentatives, base_s, plafond_s, gigue, graine, horloge)`** — La version juste est un standardiste méthodique qui tient un registre de ses rappels : il ne recompose le numéro que si la ligne était seulement occupée, note chaque échec et chaque pause, et raccroche net si on lui répond que le numéro n'existe pas. Elle reçoit un appelable sans argument, quatre tentatives par défaut, les paramètres du backoff avec une gigue de 0,1, une graine et une horloge facultative ; elle lève `ValueError` si `max_tentatives` vaut moins de 1, crée une seule fois un générateur `random.Random(graine)`, puis appelle la fonction et rend aussitôt un dictionnaire « succes » avec le résultat, le numéro de la tentative réussie, les attentes et les erreurs. Une `ErreurTransitoire` est notée, suivie, s'il reste une tentative, d'une attente calculée par `attente_backoff`, notée et ajoutée à l'horloge ; toute autre exception remonte sans relance. Si toutes les tentatives échouent, elle rend le dictionnaire « echec », avec `resultat` à `None` : deux surcharges suivies d'un succès, sans gigue, donnent 3 tentatives, les attentes [1, 2] et une horloge avancée de 3 s.

```python
# [extrait] agent/production.py
def executer_avec_relances(fonction, max_tentatives: int = 4, base_s: float = 1.0, plafond_s: float = 30.0,
                           gigue: float = 0.1, graine: int = 0, horloge: Horloge | None = None) -> dict:
    """Appelle `fonction()` ; après une `ErreurTransitoire`, attend (horloge simulée) puis relance.

    Rend {"statut": "succes" | "echec", "resultat", "tentatives", "attentes", "erreurs"}. Toute autre
    exception (argument invalide, refus de politique…) remonte aussitôt : la relancer ne la corrigerait
    pas. Il n'y a pas d'attente après la dernière tentative ratée.
    Exemple : une fonction qui échoue deux fois puis réussit, sans gigue : tentatives 3, attentes [1, 2],
    horloge avancée de 3 s.
    """
    if max_tentatives < 1:
        raise ValueError("max_tentatives >= 1")
    rng = random.Random(graine)
    attentes: list[float] = []
    erreurs: list[str] = []
    for tentative in range(1, max_tentatives + 1):
        try:
            resultat = fonction()
            return {"statut": "succes", "resultat": resultat, "tentatives": tentative,
                    "attentes": attentes, "erreurs": erreurs}
        except ErreurTransitoire as e:
            erreurs.append(str(e))
            if tentative < max_tentatives:
                a = attente_backoff(tentative, base_s, plafond_s, gigue, rng)
                attentes.append(a)
                if horloge is not None:
                    horloge.avancer(a)
    return {"statut": "echec", "resultat": None, "tentatives": max_tentatives, "attentes": attentes, "erreurs": erreurs}
```

**La signature.** `fonction` est un appelable sans argument : pour relancer `llm.create(system=…, messages=…, tools=…)`, l'appelant écrit `lambda: llm.create(...)`, comme on passe un `Supplier<T>` en Java. Les paramètres de l'attente sont ceux de l'étape 3, avec une gigue de 0,1 par défaut, plus `graine` pour le générateur et une `horloge` optionnelle : sans horloge, la fonction calcule et rend les attentes sans faire avancer le temps.

**La garde et l'état.** `max_tentatives < 1` est refusé : zéro tentative n'appellerait jamais la fonction. Le générateur `random.Random(graine)` est créé **une fois**, avant la boucle, puis passé à chaque `attente_backoff` : ses tirages successifs donnent des gigues différentes d'une relance à l'autre, et la même graine redonne exactement la même suite, ce que vérifie `test_echec_apres_max_tentatives_et_determinisme`. Le piège serait de le créer dans la boucle : chaque relance recommencerait la suite au même premier tirage. `attentes` et `erreurs` sont deux listes vides, annotées pour dire ce qu'elles contiendront.

**La boucle.** `range(1, max_tentatives + 1)` numérote les tentatives à partir de 1, comme `attente_backoff` l'attend. Dans le `try`, un succès rend aussitôt le dictionnaire « succes », avec le numéro de la tentative qui a réussi et les listes accumulées jusque-là. Le `return` dans le `try` sort de la boucle et de la fonction : il n'y a pas besoin de drapeau.

**Le `except`.** Il n'attrape **que** `ErreurTransitoire`. Toute autre exception traverse la fonction sans être touchée, et l'appelant la reçoit avec sa pile d'appels d'origine : c'est le `noRetryFor` de Spring Retry, sans rien à configurer. Pour une erreur transitoire, on note son message, puis, **seulement s'il reste une tentative** (`tentative < max_tentatives`), on calcule l'attente, on la note, et l'on avance l'horloge si elle existe. Le temps simulé avance, aucune seconde réelle ne passe.

**Après la boucle**, on n'arrive là que si toutes les tentatives ont échoué : le dictionnaire « echec » porte `resultat` à `None`, le nombre de tentatives, les attentes et les messages d'erreur. L'appelant a toute l'histoire, et peut décider : répondre au client que le service est momentanément indisponible, journaliser les erreurs, ou mettre la tâche en file d'attente.

**Pourquoi un dictionnaire plutôt qu'une exception en cas d'échec ?** Parce qu'un échec après relances est un résultat attendu en production, que l'on compte et que l'on affiche : la démo du palier imprime le statut, le nombre de tentatives et les attentes. En Java, on rendrait un petit objet résultat, plutôt que de laisser `RetryTemplate` relancer la dernière exception.

```text
# [extrait] console
>>> from agent.modele import Horloge
>>> from agent.production import ErreurTransitoire, executer_avec_relances
>>> appels = []
>>> def appel_api():
...     appels.append(1)
...     if len(appels) <= 2:
...         raise ErreurTransitoire("surcharge (529)")
...     return "réponse"
...
>>> h = Horloge()
>>> r = executer_avec_relances(appel_api, gigue=0, horloge=h)
>>> r["statut"], r["tentatives"], r["attentes"], r["erreurs"], h.t
('succes', 3, [1.0, 2.0], ['surcharge (529)', 'surcharge (529)'], 3.0)
```

Les attentes valent 1 puis 2 secondes, l'horloge a avancé de 3 s, et la fonction a été appelée trois fois.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_11_production.TestRelances
```

Les trois tests passent : le succès après deux échecs, l'échec après quatre tentatives avec trois attentes identiques d'une exécution à l'autre, et l'erreur non transitoire qui remonte après un seul appel.
