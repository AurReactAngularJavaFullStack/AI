# Étape 4 — Nommer le cycle

> Palier 08 · Étape 4 sur 7 · Précédent : [Étape 3 — Le tri topologique de Kahn](<03-Tri-topologique-de-Kahn.md>) · Suivant : [Étape 5 — Les vagues parallèles](<05-Vagues-paralleles.md>) · Retour à l'énoncé : [README du palier 08](<../../README.md>)

## Comment raisonner

Quand Kahn s'arrête trop tôt, on sait **qu'il y a** un cycle ; il faut maintenant dire **lequel**. Un message « cycle détecté » tout court ne permet à personne de corriger le plan, surtout pas au modèle qui l'a proposé.

Le raisonnement vient de la démonstration de l'étape 44. Prenons une tâche restante, c'est-à-dire non sortie. Son compteur n'est jamais tombé à 0 : au moins un de ses prérequis n'est pas sorti non plus, donc il est lui aussi parmi les restantes. On peut donc toujours **remonter** d'une tâche restante vers un de ses prérequis restants, sans jamais être bloqué. Comme il n'y a qu'un nombre fini de tâches, cette remontée finit forcément par repasser par une tâche déjà vue : la portion entre les deux passages est un cycle.

Trois détails à décider pour que le message soit unique et lisible :

1. par quelle tâche commencer la remontée : la plus petite des restantes ;
2. quel prérequis suivre quand il y en a plusieurs : le plus petit parmi les restants ;
3. comment présenter le cycle : dans le sens des arcs (de prérequis vers tâche), en commençant par son plus petit nom et en le répétant à la fin, `a → b → c → a`.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`_nommer_cycle(restants, par_nom)`** — Cette fonction privée est l'enquêteur qui, devant un chantier bloqué, remonte de dépendance en dépendance jusqu'à retomber sur ses propres pas : elle reçoit l'ensemble des tâches que Kahn n'a pas pu sortir et l'index des tâches par nom, part de la plus petite des restantes, note sa position dans `vus`, puis passe chaque fois au plus petit de ses prérequis encore restants, jusqu'à repasser par une tâche déjà vue. Elle découpe alors le chemin à partir de cette première visite, ce qui écarte une éventuelle queue, le retourne dans le sens des arcs, le fait tourner pour commencer par le plus petit nom et répète ce nom à la fin ; elle renvoie cette liste, d'où le message « a → b → c → a » de l'exemple du test, ou « x → x » pour une tâche qui s'attend elle-même.

```python
# [extrait] agent/planification.py
def _nommer_cycle(restants: set[str], par_nom: dict) -> list[str]:
    """Remonte les prérequis parmi les tâches bloquées jusqu'à repasser par une tâche déjà vue."""
    vus: dict[str, int] = {}
    chemin: list[str] = []
    v = min(restants)
    while v not in vus:
        vus[v] = len(chemin)
        chemin.append(v)
        v = min(p for p in par_nom[v].prerequis if p in restants)   # existe : v est bloquée
    boucle = chemin[vus[v]:][::-1]                                  # remise dans le sens des arcs
    i = boucle.index(min(boucle))
    boucle = boucle[i:] + boucle[:i]                                # commence par le plus petit nom
    return boucle + [boucle[0]]
```

Groupe par groupe :

- **`vus: dict[str, int]`** retient, pour chaque tâche visitée, sa **position** dans le chemin, pas seulement le fait qu'elle a été vue. C'est cette position qui permettra de découper le cycle : la remontée peut commencer par une tâche qui n'est pas sur le cycle (une tâche bloquée derrière lui), et il faudra l'écarter.
- **`v = min(restants)`** : le point de départ, déterministe.
- **La boucle `while v not in vus`** note la position de v, l'ajoute au chemin, puis passe au plus petit de ses prérequis restants. `min(...)` sur un générateur vide lèverait `ValueError` ; le commentaire rappelle pourquoi cela n'arrive pas : une tâche restante a toujours un prérequis restant.
- **`chemin[vus[v]:]`** garde la portion du chemin à partir de la première visite de la tâche revue : c'est exactement le cycle, sans la queue éventuelle. **`[::-1]`** la retourne : on a remonté les arcs (de tâche vers prérequis), on veut les lire dans leur sens (de prérequis vers tâche).
- **La rotation** : `boucle.index(min(boucle))` trouve la position du plus petit nom, et `boucle[i:] + boucle[:i]` fait tourner la liste pour qu'il soit en tête. Un cycle n'a ni début ni fin ; choisir le plus petit nom rend le message unique.
- **`boucle + [boucle[0]]`** répète le premier nom à la fin, pour que le message se lise comme un tour complet.

**Analogie Java :** un `LinkedHashMap<String, Integer>` pour `vus`, `Collections.reverse` puis `Collections.rotate(boucle, -i)` pour la mise en forme.

**Exemple fait à la main, celui du test.** Les tâches sont a (attend c), b (attend a), c (attend b), d (attend c) et e. Kahn ne sort que e ; restent a, b, c, d.

| Pas | v | Position notée | Chemin | Prérequis restants de v | v suivant |
| --- | --- | --- | --- | --- | --- |
| 1 | a | 0 | a | c | c |
| 2 | c | 1 | a, c | b | b |
| 3 | b | 2 | a, c, b | a | a, déjà vu en position 0 |

La boucle est `chemin[0:]` = a, c, b, retournée en b, c, a ; le plus petit nom est a, en position 2 ; après rotation, a, b, c ; on ajoute a. Message : `cycle détecté : a → b → c → a`. Vérifions le sens : a → b signifie « b attend a », ce qui est vrai ; b → c, « c attend b », vrai ; c → a, « a attend c », vrai. La tâche d, bloquée derrière le cycle, n'apparaît pas.

**Le cas d'une tâche qui s'attend elle-même.** `Tache("x", 1, ("x",))` : x est restante, son seul prérequis restant est x, déjà vu en position 0. La boucle vaut x, et le message `cycle détecté : x → x`.

**Le cas d'une queue.** Si la remontée commençait par une tâche hors du cycle (par exemple une tâche « 0-avant » qui attendrait c), le chemin serait 0-avant, c, b, a, puis de nouveau c, vu en position 1 : `chemin[1:]` écarte la queue et ne garde que c, b, a. C'est pour ce cas que `vus` mémorise une position.

**Sur le plan circulaire de la démo,** `verifier_identite` attend `relancer_client`, qui attend `rediger_reponse`. Kahn sort `lire_memoire`, `calculer_mensualite`, `calculer_ratio`, `convertir_usd` et `rechercher_regles`, puis s'arrête : restent `evaluer_risque`, `rediger_reponse`, `relancer_client` et `verifier_identite`. La remontée part de `evaluer_risque`, la plus petite, et suit `verifier_identite` (son seul prérequis encore restant), puis `relancer_client`, puis `rediger_reponse`, qui ramène à `evaluer_risque`, vu en position 0. Le chemin retourné vaut `rediger_reponse`, `relancer_client`, `verifier_identite`, `evaluer_risque` ; la rotation met `evaluer_risque` en tête, d'où `evaluer_risque → rediger_reponse → relancer_client → verifier_identite → evaluer_risque`, la ligne 6 de la démo.

- **Piège classique :** rendre tout l'ensemble des tâches restantes comme « le cycle ». Il peut contenir des tâches qui ne sont pas sur le cycle mais seulement bloquées derrière lui, comme d : le message enverrait le modèle corriger la mauvaise dépendance.
- **Piège classique bis :** oublier `[::-1]`. Le message deviendrait `a → c → b → a`, qui se lit « c attend a », faux : les flèches iraient à contresens des dépendances.

**Test qui passe maintenant :**

```powershell
python -m unittest -v tests.test_08_planification.TestTriTopologique.test_cycle_nomme
```

Il vérifie les deux messages exacts, `cycle détecté : a → b → c → a` et `cycle détecté : x → x`. Toute la classe `TestTriTopologique` est maintenant verte.
