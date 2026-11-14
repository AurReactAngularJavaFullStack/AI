# Étape 2 — Le graphe et les degrés entrants

> Palier 08 · Étape 2 sur 7 · Précédent : [Étape 1 — La tâche et le dossier de crédit](<01-Tache-et-dossier-de-credit.md>) · Suivant : [Étape 3 — Le tri topologique de Kahn](<03-Tri-topologique-de-Kahn.md>) · Retour à l'énoncé : [README du palier 08](<../../README.md>)

## Comment raisonner

Kahn a besoin de deux informations par tâche, et le plan n'en donne directement aucune :

- **les successeurs** : quand une tâche se termine, quelles tâches peuvent en profiter ? Le plan dit l'inverse, « de qui je dépends » ; il faut donc **retourner** les arcs ;
- **le degré entrant** : combien de prérequis restent à attendre ? Au départ, c'est le nombre de prérequis.

Écris d'abord ces deux tables à la main pour le dossier de crédit, avant de coder. Les successeurs : `lire_memoire` → `calculer_mensualite` ; `calculer_mensualite` → `calculer_ratio`, `convertir_usd` ; `calculer_ratio`, `verifier_identite` et `rechercher_regles` → `evaluer_risque` ; `convertir_usd` et `evaluer_risque` → `rediger_reponse` ; `rediger_reponse` → personne. Les degrés entrants : 0, 0, 0, 1, 1, 1, 3, 2.

C'est aussi le bon endroit pour refuser deux fautes de plan qui fausseraient tout le reste en silence : deux tâches de même nom (laquelle des deux attend-on ?) et un prérequis qui ne correspond à aucune tâche (on l'attendrait éternellement). On regroupe tout cela dans une fonction privée, que `tri_topologique` appellera en première ligne.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`_graphe(taches)`** — Cette fonction privée est le géomètre qui relève le plan avant le début du chantier et dessine, pour chaque poste, qui l'attend et combien de postes il attend lui-même : elle reçoit la liste des tâches, les indexe par nom en levant `ValueError` (« tâche en double ») si un nom revient, puis, dans un second passage, retourne chaque arc pour remplir la liste des successeurs de chaque tâche, en levant `ValueError` (« prérequis inconnu ») si un prérequis ne correspond à aucune tâche. Elle compte enfin les prérequis de chaque tâche et renvoie le triplet (index par nom, successeurs, degrés entrants) ; sur le dossier de crédit, `calculer_mensualite` a pour successeurs `calculer_ratio` et `convertir_usd`, et les degrés entrants valent 0, 0, 0, 1, 1, 1, 3 et 2, soit 8 arcs.

```python
# [extrait] agent/planification.py
def _graphe(taches: list[Tache]) -> tuple[dict, dict, dict]:
    """Successeurs, prérequis et degrés entrants ; refuse les doublons et les prérequis inconnus."""
    par_nom: dict[str, Tache] = {}
    for t in taches:
        if t.nom in par_nom:
            raise ValueError(f"tâche en double : {t.nom}")
        par_nom[t.nom] = t
    succ = {n: [] for n in par_nom}
    for t in taches:
        for p in t.prerequis:
            if p not in par_nom:
                raise ValueError(f"prérequis inconnu : {p} (tâche {t.nom})")
            succ[p].append(t.nom)
    entrant = {t.nom: len(t.prerequis) for t in taches}   # prérequis distincts : Tache les a dédoublonnés
    return par_nom, succ, entrant
```

Groupe par groupe :

- **Le nom commence par un underscore.** C'est la convention Python du « privé » : la fonction n'est pas exportée par le module, n'est pas testée directement, et le contrôle d'API ne la compare pas. En Java, ce serait une méthode `private static`.
- **`par_nom`** : un premier passage indexe les tâches par nom, comme une `Map<String, Tache>`. Le test `t.nom in par_nom` **avant** l'insertion détecte le doublon ; sans lui, la seconde tâche écraserait la première sans bruit.
- **`succ = {n: [] for n in par_nom}`** : une liste vide par tâche, y compris celles que personne n'attend. Initialiser toutes les clés d'avance évite un `KeyError` plus loin et un `defaultdict`. Attention à ne pas écrire `dict.fromkeys(par_nom, [])` : ce serait **la même** liste pour toutes les clés.
- **La double boucle** retourne chaque arc : pour chaque prérequis p de t, t devient un successeur de p. Le contrôle `p not in par_nom` vient avant l'ajout ; le message nomme le prérequis fautif **et** la tâche qui le cite, pour que le modèle (ou le développeur) sache quoi corriger.
- **`entrant`** compte les prérequis. Comme `Tache` a retiré les doublons, il y a exactement autant de prérequis que d'entrées de cette tâche dans les listes `succ` : chaque sortie d'un prérequis fera un décrément, et le compteur tombera à 0 au dernier.
- **Le retour** est un tuple de trois dictionnaires, que l'appelant déballe : `par_nom, succ, entrant = _graphe(taches)`.

**Analogie Java :** une méthode de construction d'un graphe en listes d'adjacence, `Map<String, List<String>>`, avec une `Map<String, Integer>` de degrés entrants ; Python évite seulement les déclarations de types génériques à rallonge.

**Ce que l'on obtient sur le dossier de crédit :**

```text
# [extrait] console
>>> from agent.planification import _graphe, dossier_credit
>>> par_nom, succ, entrant = _graphe(dossier_credit())
>>> succ["calculer_mensualite"], succ["rediger_reponse"]
(['calculer_ratio', 'convertir_usd'], [])
>>> entrant
{'verifier_identite': 0, 'lire_memoire': 0, 'rechercher_regles': 0, 'calculer_mensualite': 1, 'calculer_ratio': 1, 'convertir_usd': 1, 'evaluer_risque': 3, 'rediger_reponse': 2}
```

La somme des degrés entrants vaut 0 + 0 + 0 + 1 + 1 + 1 + 3 + 2 = 8 : c'est le nombre d'arcs du plan, et la somme des longueurs des listes `succ` vaut aussi 8. C'est une bonne vérification à faire sur papier : chaque arc est compté une fois à son arrivée et une fois à son départ.

- **Piège classique :** construire `succ` et `entrant` dans la même boucle que `par_nom`. Une tâche peut citer un prérequis défini **plus bas** dans la liste (`dossier_credit` ne le fait pas, mais rien ne l'interdit) : au moment où on la lit, ce prérequis n'est pas encore dans `par_nom`, et il serait déclaré inconnu à tort. D'où les deux passages.
- **Piège classique bis :** compter dans `entrant` les tâches qui **attendent** t au lieu des tâches **qu'attend** t. On obtiendrait le degré sortant : `rediger_reponse` aurait 0 et partirait la première.

**Tests à cette étape :** `_graphe` n'est appelée que par `tri_topologique` ; ses deux erreurs seront vérifiées par `TestTriTopologique.test_prerequis_inconnu_et_doublon` dès l'étape 3. La console ci-dessus suffit pour l'instant.
