# Étape 3 — Le tri topologique de Kahn

> Palier 08 · Étape 3 sur 7 · Précédent : [Étape 2 — Le graphe et les degrés entrants](<02-Graphe-et-degres-entrants.md>) · Suivant : [Étape 4 — Nommer le cycle](<04-Nommer-le-cycle.md>) · Retour à l'énoncé : [README du palier 08](<../../README.md>)

## Comment raisonner

L'idée de Kahn tient en une phrase : **une tâche peut partir quand tous ses prérequis sont finis**. On garde donc une réserve de tâches prêtes (degré entrant nul), on en sort une, on la range dans l'ordre, et l'on prévient ses successeurs qu'ils ont un prérequis de moins à attendre ; ceux dont le compteur tombe à 0 rejoignent la réserve. On s'arrête quand la réserve est vide.

Deux questions restent à trancher avant d'écrire :

1. **Quelle tâche sortir quand plusieurs sont prêtes ?** N'importe laquelle donne un ordre valide, mais pas toujours le même. Pour un ordre unique, donc testable et reproductible, on sort toujours la plus petite par ordre alphabétique.
2. **Comment savoir que le plan était faux ?** Si la réserve se vide alors que des tâches n'ont pas été sorties, ces tâches attendent quelque chose qui n'arrivera jamais : un cycle (étape 4).

## Une première version, avec une file

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tri_topologique(taches)`** — Dans ce brouillon, la fonction est un chef de chantier qui fait passer les artisans prêts dans l'ordre où ils se sont inscrits, sans autre règle : elle reçoit les tâches, obtient de `_graphe` les successeurs et les degrés entrants, place les sources dans une file `deque`, puis sort la première, l'ajoute à l'ordre, décrémente le compteur de ses successeurs et met en file ceux qui tombent à 0, jusqu'à épuisement. Elle renvoie un ordre valide mais qui dépend de l'ordre d'écriture de la liste, `["c", "b", "a"]` au lieu de `["b", "c", "a"]` pour l'exemple du test, et, sur un plan circulaire, un ordre incomplet sans rien signaler.

```python
# [extrait] brouillon
from collections import deque

def tri_topologique(taches: list[Tache]) -> list[str]:
    par_nom, succ, entrant = _graphe(taches)
    pretes = deque(n for n, d in entrant.items() if d == 0)
    ordre = []
    while pretes:
        n = pretes.popleft()
        ordre.append(n)
        for v in succ[n]:
            entrant[v] -= 1
            if entrant[v] == 0:
                pretes.append(v)
    return ordre
```

C'est le Kahn de l'étape 44 : une file (premier entré, premier sorti). Sur le dossier de crédit, il rend `verifier_identite`, `lire_memoire`, `rechercher_regles`, `calculer_mensualite`, … : un ordre **valide**, mais qui dépend de l'ordre dans lequel les tâches ont été écrites dans la liste. Mélange la liste, et l'ordre change. Le test `test_dossier_de_credit` attend `lire_memoire` en premier, et `test_departage_alphabetique` attend `["b", "c", "a"]` pour une liste écrite c, b, a : la file rendrait `["c", "b", "a"]`. Et ce brouillon a un second défaut, plus grave : sur un plan circulaire, il rend un ordre **incomplet** sans rien signaler.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tri_topologique(taches)`** — C'est la même fonction, confiée à un chef de chantier qui, parmi les artisans prêts, appelle toujours le premier par ordre alphabétique et sait reconnaître un chantier bloqué : elle reçoit les tâches, laisse `_graphe` refuser doublons et prérequis inconnus, range les sources dans un tas binaire avec `heapq.heapify`, puis sort à chaque tour le plus petit nom, l'ajoute à l'ordre et pousse dans le tas les successeurs dont le compteur tombe à 0. Si toutes les tâches ne sont pas sorties, elle lève `ValueError` avec le cycle nommé par `_nommer_cycle`, sinon elle renvoie l'ordre : sur le dossier de crédit, `lire_memoire`, `calculer_mensualite`, `calculer_ratio`, `convertir_usd`, `rechercher_regles`, `verifier_identite`, `evaluer_risque`, puis `rediger_reponse`.

```python
# [extrait] agent/planification.py
def tri_topologique(taches: list[Tache]) -> list[str]:
    """Ordre d'exécution où chaque prérequis passe avant la tâche qui l'attend (Kahn).

    Parmi les tâches prêtes (degré entrant nul), on prend toujours la plus petite par ordre
    alphabétique (tas binaire) : l'ordre rendu est unique. S'il reste des tâches, elles sont sur un
    cycle ou derrière un cycle : `ValueError("cycle détecté : a → b → a")`.
    Exemple (dossier de crédit) : ["lire_memoire", "calculer_mensualite", "calculer_ratio",
    "convertir_usd", "rechercher_regles", "verifier_identite", "evaluer_risque", "rediger_reponse"].
    """
    par_nom, succ, entrant = _graphe(taches)
    pretes = [n for n, d in entrant.items() if d == 0]
    heapq.heapify(pretes)
    ordre = []
    while pretes:
        n = heapq.heappop(pretes)
        ordre.append(n)
        for v in succ[n]:
            entrant[v] -= 1
            if entrant[v] == 0:               # son dernier prérequis vient de finir
                heapq.heappush(pretes, v)
    if len(ordre) != len(par_nom):
        cycle = _nommer_cycle(set(par_nom) - set(ordre), par_nom)
        raise ValueError("cycle détecté : " + " → ".join(cycle))
    return ordre
```

Groupe par groupe :

- **`_graphe(taches)`** fait les contrôles de doublon et de prérequis inconnu, et prépare les deux tables. Si le plan est mal formé, l'erreur sort ici, avant tout calcul.
- **`pretes = [...]` puis `heapq.heapify(pretes)`** : on part des sources, puis on transforme la liste en **tas binaire**, en place et en O(n). `heapq` n'est pas une classe : ce sont des fonctions qui maintiennent une liste ordinaire en tas. En Java, l'équivalent est une `PriorityQueue<String>`, dont l'ordre naturel est l'ordre alphabétique.
- **`heapq.heappop(pretes)`** retire et rend le plus petit nom en O(log n) : c'est le départage alphabétique.
- **`for v in succ[n]: entrant[v] -= 1`** : la tâche n est finie, chacun de ses successeurs a un prérequis de moins à attendre. C'est la mise à jour d_in(v) ← d_in(v) − 1 du rappel de cours.
- **`if entrant[v] == 0: heapq.heappush(pretes, v)`** : v vient de perdre son dernier prérequis, il rejoint les tâches prêtes. Un compteur ne fait que baisser, donc une tâche n'entre qu'une fois dans le tas.
- **`if len(ordre) != len(par_nom)`** : le critère de l'étape 44, « Kahn sort toutes les tâches si et seulement si le plan est sans cycle ». Les tâches restantes, `set(par_nom) - set(ordre)`, sont sur un cycle ou bloquées derrière ; `_nommer_cycle` (étape 4) en extrait un cycle lisible.
- **`" → ".join(cycle)`** compose le message `cycle détecté : a → b → c → a`. Le message est destiné à un humain, ou au modèle qui a proposé le plan et devra le corriger : il doit nommer les tâches, pas seulement dire « cycle ».

**Kahn pas à pas sur le dossier de crédit.** Les tâches prêtes au départ sont `lire_memoire`, `rechercher_regles` et `verifier_identite`. Le tas rend `lire_memoire` (« l » avant « r » et « v »), dont la sortie libère `calculer_mensualite` ; le tas contient alors `calculer_mensualite`, `rechercher_regles`, `verifier_identite`, et rend `calculer_mensualite`, qui libère `calculer_ratio` et `convertir_usd`. Ces deux-là sortent ensuite, puisque « ca » et « co » précèdent « r » et « v » ; `calculer_ratio` fait passer `evaluer_risque` de 3 à 2, `convertir_usd` fait passer `rediger_reponse` de 2 à 1. Puis `rechercher_regles` (`evaluer_risque` : 2 → 1), `verifier_identite` (`evaluer_risque` : 1 → 0, il entre dans le tas), `evaluer_risque` (`rediger_reponse` : 1 → 0) et enfin `rediger_reponse`. Huit tâches sorties sur huit :

```text
# [extrait] console
>>> from agent.planification import dossier_credit, tri_topologique
>>> tri_topologique(dossier_credit())
['lire_memoire', 'calculer_mensualite', 'calculer_ratio', 'convertir_usd', 'rechercher_regles', 'verifier_identite', 'evaluer_risque', 'rediger_reponse']
```

**Le départage, sur l'exemple du test.** Avec `[Tache("c", 1), Tache("b", 1), Tache("a", 1, ("c",))]`, le tas de départ contient b et c ; b sort, puis c, qui libère a. Résultat `["b", "c", "a"]` : a est le plus petit nom, mais il n'est prêt qu'après c. L'ordre alphabétique départage les tâches **prêtes**, il ne passe jamais avant une dépendance.

- **Piège classique :** trier toutes les tâches par nom au départ, puis « réparer » les dépendances. On mélange alors deux critères, et l'on finit par sortir une tâche avant son prérequis. Kahn n'a besoin de l'ordre alphabétique que pour choisir parmi les tâches **déjà prêtes**.
- **Piège classique bis :** pousser v dans le tas dès que `entrant[v]` diminue, au lieu d'attendre qu'il atteigne 0. `evaluer_risque` partirait alors après son premier prérequis, sans attendre les deux autres.

**Tests qui passent maintenant :**

```powershell
python -m unittest -v tests.test_08_planification.TestTriTopologique tests.test_08_planification.TestTache.test_creation
```

Quatre tests verts : l'ordre du dossier de crédit (et, pour chaque arc, le prérequis placé avant), le départage alphabétique, les doublons et prérequis inconnus (dont le prérequis cité deux fois, qui sort bien après ses deux prérequis), et la création d'une tâche avec une liste de prérequis. `test_cycle_nomme` échoue encore par `NotImplementedError`, levée dans `_nommer_cycle` : c'est l'étape suivante.
