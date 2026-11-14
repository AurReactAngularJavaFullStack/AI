# Étape 5 — Les vagues parallèles

> Palier 08 · Étape 5 sur 7 · Précédent : [Étape 4 — Nommer le cycle](<04-Nommer-le-cycle.md>) · Suivant : [Étape 6 — Calendrier et chemin critique](<06-Calendrier-et-chemin-critique.md>) · Retour à l'énoncé : [README du palier 08](<../../README.md>)

## Comment raisonner

L'ordre de Kahn dit dans quel ordre exécuter les tâches **une par une**. Mais un orchestrateur d'agent peut lancer plusieurs outils en même temps : lire la mémoire, chercher les règles et vérifier l'identité n'ont rien à attendre les uns des autres. La question devient : quelles tâches peuvent partir **ensemble** ?

On range chaque tâche à un niveau. Une tâche sans prérequis est au niveau 0. Une tâche avec prérequis doit attendre le **plus tardif** d'entre eux, donc elle est un niveau au-dessus du plus haut de ses prérequis :

$$
\text{niveau}(v) = 1 + \max_{u \to v} \text{niveau}(u)
$$

Pour appliquer cette formule, il faut connaître le niveau de tous les prérequis avant de calculer celui de la tâche : c'est exactement ce que garantit l'ordre topologique. On parcourt donc l'ordre de Kahn une seule fois. Les tâches d'un même niveau forment une vague ; aucune ne dépend d'une autre de la même vague, puisque le niveau croît strictement le long d'un arc.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`vagues(taches)`** — Cette fonction est le régisseur qui fait entrer en scène, vague après vague, tous les figurants dont l'entrée ne dépend plus de personne : elle reçoit les tâches, obtient d'abord l'ordre de `tri_topologique`, ce qui reprend toute la validation et fait sortir un cycle avec son nom, puis parcourt cet ordre en donnant à chaque tâche le niveau 1 + le plus haut niveau de ses prérequis, ou 0 sans prérequis grâce à `default=-1`. Elle crée une liste vide distincte par niveau, y range les noms dans l'ordre alphabétique et renvoie cette liste de vagues, vide pour un plan vide ; sur le dossier de crédit, elle rend cinq vagues, de `lire_memoire`, `rechercher_regles` et `verifier_identite` jusqu'à `rediger_reponse` seule.

```python
# [extrait] agent/planification.py
def vagues(taches: list[Tache]) -> list[list[str]]:
    """Les vagues de Kahn : la vague k+1 contient les tâches dont le dernier prérequis est dans la vague k.

    Chaque vague est triée par nom. Exemple (dossier de crédit) : [["lire_memoire", "rechercher_regles",
    "verifier_identite"], ["calculer_mensualite"], ["calculer_ratio", "convertir_usd"], ["evaluer_risque"],
    ["rediger_reponse"]].
    """
    ordre = tri_topologique(taches)               # valide le graphe (doublons, inconnus, cycles)
    par_nom = {t.nom: t for t in taches}
    niveau: dict[str, int] = {}
    for n in ordre:
        niveau[n] = 1 + max((niveau[p] for p in par_nom[n].prerequis), default=-1)
    resultat: list[list[str]] = [[] for _ in range(max(niveau.values(), default=-1) + 1)]
    for n in sorted(niveau):
        resultat[niveau[n]].append(n)
    return resultat
```

Groupe par groupe :

- **`ordre = tri_topologique(taches)`** en première ligne : on réutilise toute la validation (doublon, prérequis inconnu, cycle). Un plan circulaire n'a pas de vagues, et l'erreur sort avec le cycle nommé. On ne recode rien.
- **`par_nom`** : ici, une simple compréhension suffit, puisque `tri_topologique` a déjà refusé les doublons.
- **`max((…), default=-1)`** : `max` sur une séquence vide lève `ValueError`, sauf avec `default`. Pour une tâche sans prérequis, le maximum vaut −1 et le niveau 1 + (−1) = 0 : une seule formule couvre les deux cas du rappel de cours. En Java : `stream().mapToInt(…).max().orElse(-1)`.
- **`niveau[p]` existe toujours** au moment où on le lit, parce que p a été traité avant n dans l'ordre topologique. Parcourir `taches` dans l'ordre de la liste lèverait `KeyError` dès qu'une tâche est écrite avant son prérequis.
- **`resultat = [[] for _ in range(…)]`** crée une liste vide **distincte** par niveau. Le nombre de vagues est le niveau maximal plus 1 ; pour un plan vide, `max(…, default=-1) + 1` vaut 0, et l'on rend `[]`.
- **`for n in sorted(niveau)`** parcourt les noms dans l'ordre alphabétique, si bien que chaque vague est déjà triée quand on y ajoute ses tâches.

**Exemple fait à la main, sur l'ordre de Kahn du dossier de crédit.**

| Tâche (ordre de Kahn) | Niveaux des prérequis | Niveau |
| --- | --- | --- |
| `lire_memoire` | aucun | 0 |
| `calculer_mensualite` | 0 | 1 |
| `calculer_ratio` | 1 | 2 |
| `convertir_usd` | 1 | 2 |
| `rechercher_regles` | aucun | 0 |
| `verifier_identite` | aucun | 0 |
| `evaluer_risque` | 0, 2, 0 | 3 |
| `rediger_reponse` | 3, 2 | 4 |

D'où cinq vagues : `["lire_memoire", "rechercher_regles", "verifier_identite"]`, `["calculer_mensualite"]`, `["calculer_ratio", "convertir_usd"]`, `["evaluer_risque"]`, `["rediger_reponse"]`. La démo les numérote de 1 à 5 ; le code, de 0 à 4.

- **Piège classique :** écrire `[[]] * (max_niveau + 1)`. On obtient cinq références vers **la même** liste : chaque `append` apparaîtrait dans toutes les vagues. C'est le même piège que `dict.fromkeys(cles, [])` à l'étape 2.
- **Piège classique bis :** calculer le niveau comme « 1 + niveau du premier prérequis ». `evaluer_risque` serait au niveau 1 (par `verifier_identite`) et partirait avant `calculer_ratio`, dont il a besoin. C'est le prérequis le **plus tardif** qui compte.

**Ce que les vagues ne disent pas.** Elles donnent le parallélisme possible, pas le calendrier. Si l'on exécute vraiment vague par vague, `calculer_mensualite` (vague 2) attend la fin de `rechercher_regles` (vague 1, 2,0 s), alors qu'il n'en dépend pas : il n'a besoin que de `lire_memoire`, finie à 0,5 s. L'étape 6 calcule le vrai calendrier, et mesure ce que coûte cette synchronisation.

**Tests qui passent maintenant :**

```powershell
python -m unittest -v tests.test_08_planification.TestVagues
```

Deux tests verts : les cinq vagues du dossier de crédit, et les cas limites (plan vide, deux tâches indépendantes `[["a", "b"]]`, et un cycle qui lève `ValueError`).
