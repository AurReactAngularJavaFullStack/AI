# Étape 2 — La Tool Call F1

> [Énoncé du palier 10](<../../README.md>) · Précédent : [Étape 1 — L'intervalle de Wilson](<01-Intervalle-de-Wilson.md>) · Suivant : [Étape 3 — Goal Accuracy et moyenne définie](<03-Goal-Accuracy-et-moyenne-definie.md>)

## Comment raisonner

La Tool Call F1 juge le **chemin** de l'agent : les outils qu'il a appelés, comparés à ceux qu'un expert attendait. Trois décisions de modélisation viennent avant la première ligne de code.

1. **Qu'est-ce qu'un appel ?** Le nom de l'outil **et** ses arguments. Appeler `mensualite` avec le mauvais principal n'est pas le bon appel.
2. **Comment comparer deux appels ?** Il faut une clé hachable et canonique. Un dictionnaire Python n'est pas hachable, et deux dictionnaires égaux peuvent s'écrire dans un ordre différent. La clé sera donc le nom et le JSON des arguments à clés triées.
3. **Ensemble ou multi-ensemble ?** Multi-ensemble : un appel répété inutilement doit coûter, et un appel attendu deux fois doit être fait deux fois.

Ensuite seulement, la formule : on compte TP, et l'on divise 2 × TP par la somme des deux tailles (démonstration dans l'énoncé).

## Un brouillon avec des ensembles

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tool_call_f1(attendus, reels)`** — Ce brouillon est un contrôleur qui ne lit que l'en-tête des bons de travail, sans regarder ce qui a été fait ni combien de fois. Il reçoit les deux listes de couples `(nom, arguments)`, en garde seulement les noms dans deux ensembles, compte les noms communs et rend 2 × commun / (taille de l'un + taille de l'autre). Les arguments sont jetés, les doublons fondus dans l'ensemble, de sorte qu'un appel fait deux fois au lieu d'une donne 1 au lieu de 2/3, et deux listes vides lèvent une division par zéro au lieu de rendre `None`.

```python
# [extrait] brouillon
def tool_call_f1(attendus, reels):
    a = {nom for nom, _ in attendus}
    r = {nom for nom, _ in reels}
    return 2 * len(a & r) / (len(a) + len(r))
```

Trois erreurs. Les arguments sont ignorés : un appel à `mensualite` avec un principal faux est compté juste. Les répétitions disparaissent dans l'ensemble : A1 attendu une fois et fait deux fois donne 1 au lieu de 2/3, et une boucle qui rappelle le même outil n'est jamais pénalisée. Enfin, deux listes vides provoquent une division par zéro au lieu de `None`.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tool_call_f1(attendus, reels)`** — La bonne version travaille comme un magasinier qui pointe deux bordereaux ligne par ligne, quantités comprises. Elle reçoit les mêmes deux listes, transforme chaque appel en clé formée du nom et du JSON de ses arguments à clés triées, compte ces clés dans deux `Counter`, additionne leurs tailles avec les répétitions, et obtient TP en sommant l'intersection `a & r`, qui garde pour chaque clé le minimum des deux comptes. Elle rend `None` si le total est nul, sinon 2 × TP / total : 1 quand A1 et A2 sont faits, 2/3 pour un oubli ou une répétition, 1 pour des arguments donnés dans un autre ordre, et 0,0 quand rien n'a été fait alors qu'A1 était attendu.

```python
# [extrait] agent/evaluation.py
def tool_call_f1(attendus: list, reels: list) -> float | None:
    ...
    a = Counter((n, json.dumps(x, sort_keys=True)) for n, x in attendus)
    r = Counter((n, json.dumps(x, sort_keys=True)) for n, x in reels)
    total = sum(a.values()) + sum(r.values())
    return None if total == 0 else 2 * sum((a & r).values()) / total
```

**Ligne par ligne.**

- `json.dumps(x, sort_keys=True)` transforme les arguments en une chaîne canonique : `{"n_mois": 300, "taux_annuel": 0.045, "principal": 975000}` et `{"principal": 975000, "taux_annuel": 0.045, "n_mois": 300}` donnent la même chaîne. Le couple `(nom, chaîne)` est hachable : c'est la clé c de l'énoncé.
- `Counter(...)` compte chaque clé : c'est un multi-ensemble, un dictionnaire clé → nombre d'occurrences. `a` correspond à n_att(c), `r` à n_réel(c).
- `sum(a.values()) + sum(r.values())` est |C_att| + |C_réel|, répétitions comprises.
- `a & r` est l'intersection de deux `Counter` : pour chaque clé, le **minimum** des deux comptes, exactement le terme min(n_att(c), n_réel(c)) de la formule de TP. `sum((a & r).values())` est donc TP.
- Si les deux listes sont vides, `None` : la F1 est indéfinie. Sinon 2 × TP / total.

**Analogie Java.** Un `Counter` est un `Map<Appel, Integer>` alimenté par `merge(cle, 1, Integer::sum)`, ou un `Multiset` de Guava, dont `Multisets.intersection` fait le `&`. La clé serait un `record Appel(String nom, String argumentsJson)`, avec `equals` et `hashCode` générés, et le JSON canonique viendrait d'un `ObjectMapper` configuré avec `ORDER_MAP_ENTRIES_BY_KEYS`.

**Les nombres de l'énoncé.** A1 et A2 attendus, A1 seul fait : a = {A1 : 1, A2 : 1}, r = {A1 : 1}, a & r = {A1 : 1}, TP = 1, total = 3, F1 = 2/3. A1 attendu, A1 fait deux fois : a & r = {A1 : min(1, 2) = 1}, total = 3, F1 = 2/3 encore. Rien attendu, rien fait : `None`. A1 attendu, rien fait : TP = 0, total = 1, F1 = 0,0.

**Le piège classique.** Oublier `sort_keys=True`. Le test `test_repetition_et_ordre_des_arguments` appelle `mensualite` avec les mêmes arguments dans un autre ordre et attend 1 : sans tri, les deux chaînes JSON diffèrent et la F1 tombe à 0. Une limite reste, que l'étape 59 traite par une normalisation champ par champ : 975000 et 975000.0 donnent deux JSON différents (`975000` et `975000.0`), donc deux clés différentes.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_10_evaluation.TestToolCallF1
```

`test_parfait_et_oubli` : 1 pour les deux appels faits, 2/3 pour un oubli. `test_repetition_et_ordre_des_arguments` : 2/3 pour une répétition, 1 pour des arguments dans un autre ordre. `test_indefini` : `None` pour deux listes vides, 0,0 quand rien n'a été fait alors qu'un appel était attendu.
