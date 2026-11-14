# Étape 6 — Le rapport et la barrière CI

> [Énoncé du palier 10](<../../README.md>) · Précédent : [Étape 5 — Noter un cas](<05-Noter-un-cas.md>) · Suivant : [Étape 7 — Assembler, tester, lancer la démo](<07-Assembler-tester-lancer.md>)

## Comment raisonner

On a une note par cas. Il reste deux choses : **agréger** les notes d'un jeu de cas en quelques nombres lisibles, et **décider** à partir de ces nombres. On les sépare en deux fonctions, comme on a séparé `autoriser` de son exception au palier 09 : `rapport` calcule, `barriere_ci` juge. Un rapport sert aussi à autre chose qu'à la barrière (un tableau de bord, une comparaison de versions), et la barrière doit pouvoir se tester sur un rapport fabriqué à la main.

Pour la barrière, la question de conception est : **qui quitte le programme ?** Pas la fonction. Elle rend un code et des motifs ; c'est le script d'intégration continue qui appelle `sys.exit(code)`. Une fonction qui quitte le programme ne se teste pas : elle tuerait le lanceur de tests avec elle.

## Le rapport

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rapport(notes)`** — Cette fonction joue le greffier du conseil de classe qui, à partir d'une pile de fiches individuelles, dresse le procès-verbal en quelques lignes. Elle reçoit la liste des notes rendues par `noter`, compte une fois pour toutes les buts atteints, puis rend un dictionnaire aux six clés : `"n"`, le nombre de notes ; `"succes"` ; `"taux"`, la Goal Accuracy des buts ; `"wilson"`, l'intervalle calculé sur ces succès et n ; `"tool_f1"` et `"fidelite"`, les moyennes définies des deux mesures. Elle ne lève rien pour une liste vide, où taux et intervalle valent `None` ; pour 14 notes parfaites et 4 fautives, elle rend une F1 moyenne de 0,926 et une fidélité moyenne de 0,889.

```python
# [extrait] agent/evaluation.py
def rapport(notes: list[dict]) -> dict:
    ...
    succes = sum(n["but"] for n in notes)
    return {"n": len(notes), "succes": succes, "taux": goal_accuracy([n["but"] for n in notes]),
            "wilson": wilson(succes, len(notes)), "tool_f1": moyenne_definie([n["f1"] for n in notes]),
            "fidelite": moyenne_definie([n["fidelite"] for n in notes])}
```

**Ligne par ligne.**

- `succes = sum(n["but"] for n in notes)` compte les buts atteints, les booléens valant 0 ou 1. On le calcule une fois, parce qu'il sert deux fois.
- `"taux"` est la Goal Accuracy de l'étape 3, `None` si la liste est vide.
- `"wilson"` est l'intervalle de l'étape 1 sur (succes, n), `None` si n = 0.
- `"tool_f1"` et `"fidelite"` sont les moyennes **définies** de l'étape 3 : les cas sans F1 ou sans fidélité ne comptent pas.

Pour 14 notes parfaites et 4 fautives (F1 2/3, fidélité 0,5, but faux), la Tool Call F1 moyenne vaut (14 + 4 × 2/3) / 18 = 16,667 / 18 = 0,926 et la fidélité (14 + 4 × 0,5) / 18 = 16 / 18 = 0,889 : les nombres de la candidate de l'étape 77.

**Analogie Java.** Un `record Rapport(int n, int succes, Double taux, Intervalle wilson, Double toolF1, Double fidelite)`, où les `Double` en objet peuvent valoir `null`, construit par une méthode statique de fabrique.

## Les seuils et la barrière

D'abord un brouillon qui ressemble à un script de CI :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`barriere_ci(rap, seuils)`** — Ce brouillon est un gardien de barrière qui, au lieu de lever ou baisser la barre, fait sauter tout le poste de péage. Il reçoit le rapport et les seuils, compare la borne basse de Wilson et la F1 moyenne à leurs seuils, et appelle `sys.exit(1)` si l'une des deux est trop basse, `sys.exit(0)` sinon, sans jamais rendre de valeur ni dire pourquoi. Il ignore la fidélité, plante sur un rapport vide parce qu'il indexe `rap["wilson"]` qui vaut `None`, plante encore sur une F1 moyenne `None`, et tue avec lui le lanceur de tests qui voudrait le vérifier.

```python
# [extrait] brouillon
def barriere_ci(rap, seuils):
    if rap["wilson"][0] < seuils["borne_basse"] or rap["tool_f1"] < seuils["tool_f1"]:
        sys.exit(1)                               # tue aussi le lanceur de tests
    sys.exit(0)
```

Trois défauts. `sys.exit` rend la fonction intestable, et un développeur ne sait pas **pourquoi** sa version est bloquée. Un rapport vide plante sur `rap["wilson"][0]`, puisque `wilson` vaut `None`. Et une F1 moyenne `None` plante sur la comparaison `None < 0.95` (`TypeError` en Python 3). La version retenue :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`barriere_ci(rap, seuils)`** — La version retenue est un contrôleur qui remplit un procès-verbal et le remet au chef de gare, seul habilité à arrêter le train. Elle reçoit le rapport et les seuils, `SEUILS` par défaut, rend `(1, ["aucun cas évalué"])` si le rapport ne compte aucun cas, puis ajoute un motif à trois décimales pour chaque seuil violé, dans l'ordre fixe borne basse, Tool Call F1, fidélité, en sautant toute moyenne qui vaut `None`. Elle rend le couple formé du code, 1 s'il existe au moins un motif et 0 sinon, et de la liste des motifs, sans appeler `sys.exit` : la candidate à 14 sur 18 reçoit trois motifs, dont « borne basse de Wilson 0.548 < 0.8 », et la production à 18 sur 18 obtient `(0, [])`.

```python
# [extrait] agent/evaluation.py
SEUILS = {"borne_basse": 0.80, "tool_f1": 0.95, "fidelite": 0.95}


def barriere_ci(rap: dict, seuils: dict = SEUILS) -> tuple[int, list[str]]:
    ...
    if rap["n"] == 0:
        return 1, ["aucun cas évalué"]
    motifs = []
    if rap["wilson"][0] < seuils["borne_basse"]:
        motifs.append(f"borne basse de Wilson {rap['wilson'][0]:.3f} < {seuils['borne_basse']}")
    if rap["tool_f1"] is not None and rap["tool_f1"] < seuils["tool_f1"]:
        motifs.append(f"Tool Call F1 {rap['tool_f1']:.3f} < {seuils['tool_f1']}")
    if rap["fidelite"] is not None and rap["fidelite"] < seuils["fidelite"]:
        motifs.append(f"fidélité approchée {rap['fidelite']:.3f} < {seuils['fidelite']}")
    return (1 if motifs else 0), motifs
```

**Ligne par ligne.**

- `SEUILS` regroupe les trois seuils, illustratifs : une borne basse de Wilson d'au moins 0,80 (il faut donc au moins 16 cas parfaits, démonstration de l'énoncé), une F1 et une fidélité moyennes d'au moins 0,95. C'est la valeur par défaut du paramètre `seuils` : un dictionnaire par défaut est partagé entre les appels, ce qui ne pose aucun problème tant que la fonction ne le modifie pas.
- `rap["n"] == 0` d'abord : un jeu vide ne prouve rien, il bloque, et l'on n'indexe jamais `rap["wilson"]`, qui vaut `None`.
- Chaque seuil violé ajoute **un motif lisible**, dans un ordre fixe. `{rap['wilson'][0]:.3f}` écrit la valeur à trois décimales (« 0.548 »), et `{seuils['borne_basse']}` écrit le seuil tel quel : le flottant `0.80` s'affiche « 0.8 ». Les guillemets simples à l'intérieur de la f-string évitent de fermer la chaîne délimitée par des guillemets doubles (une contrainte de Python avant la version 3.12).
- `rap["tool_f1"] is not None and …` : l'opérateur `and` court-circuite, la comparaison n'est faite que si la moyenne existe. Une moyenne indéfinie ne bloque pas : il n'y avait rien à mesurer. La borne basse, elle, existe toujours ici, puisque n > 0.
- `(1 if motifs else 0), motifs` : le code se déduit des motifs, ce qui garantit qu'un code 1 a toujours au moins une raison écrite, et qu'un code 0 n'en a aucune.

**Analogie Java.** C'est la « quality gate » d'un pipeline Maven ou Gradle : une méthode `Verdict evaluer(Rapport r)` rend le verdict et ses raisons, et seul le `main` du script appelle `System.exit(verdict.code())`. On teste la méthode, jamais le `main`.

**Le piège classique.** Comparer la **moyenne** du taux de réussite au seuil, au lieu de la borne basse. 14 sur 18 donne un taux de 0,778, sous 0,80 de toute façon ; mais 3 sur 3 donne 1,0 et passerait, alors que sa borne basse, 0,438, dit qu'on ne sait presque rien.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_10_evaluation.TestRapportEtBarriere
```

`test_candidate_bloquee_avec_trois_motifs` vérifie n = 18, succes = 14, les deux moyennes, le code 1 et les trois motifs exacts. `test_production_passe_trois_cas_ne_suffisent_pas` vérifie `(0, [])` pour 18 cas parfaits, le motif de la borne basse 0,438 pour 3 cas parfaits et `(1, ["aucun cas évalué"])` pour un jeu vide. `test_moyenne_indefinie_ne_bloque_pas` vérifie qu'une F1 et une fidélité indéfinies sur 18 cas réussis rendent `(0, [])`. Avec `test_noter` de l'étape 5, toute la classe est verte, et les 14 tests du palier aussi.
