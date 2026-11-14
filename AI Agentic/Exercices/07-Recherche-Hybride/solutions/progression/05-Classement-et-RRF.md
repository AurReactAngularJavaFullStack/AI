# Étape 5 — Classement et RRF

> Palier 07 · Étape 5 sur 8 · Précédent : [Étape 4 — Le score BM25](<04-Score-BM25.md>) · Suivant : [Étape 6 — La recherche hybride](<06-Recherche-hybride.md>) · Retour à l'énoncé : [README du palier 07](<../../README.md>)

## Comment raisonner

À l'étape 6, on aura deux dictionnaires de scores : BM25 (de 0 à 5,1 ici, sans maximum en général) et cosinus (de 0 à 1). On ne peut pas les additionner : BM25 écraserait le cosinus. Deux solutions existent dans le cours. Le score hybride de l'étape 23 ramène chaque signal dans [0, 1] par min-max, puis fait une moyenne pondérée par un α qu'il faut régler. La Reciprocal Rank Fusion de l'étape 24 oublie les scores et ne garde que les **rangs** : rien à normaliser, rien à régler. Le module choisit RRF, comme l'étape 77.

Il faut donc deux fonctions, dans cet ordre : `classement`, qui transforme des scores en une liste ordonnée, puis `rrf`, qui fusionne plusieurs listes. Avant d'écrire `classement`, on fixe ses trois règles, parce que le résultat de la fusion en dépend :

1. score décroissant ;
2. à score égal, l'identifiant le plus petit d'abord, pour que le résultat ne dépende pas de l'ordre du dictionnaire ;
3. un score nul ne donne pas de rang : un document qui n'a aucun mot ou aucun concept en commun avec la question n'a pas à recevoir des points de fusion.

## Des scores aux rangs

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`classement(scores)`** — Cette fonction est le maître de cérémonie qui appelle les lauréats sur l'estrade dans l'ordre de leur note et laisse assis ceux qui n'ont rien obtenu : elle reçoit un dictionnaire identifiant → score, trie ses couples avec la clé (opposé du score, identifiant), qui met les grands scores en tête et départage les égalités par ordre alphabétique, puis renvoie la liste des seuls identifiants de score strictement positif. Le dictionnaire où D vaut 3,0, A et B valent 2,0 et C vaut 0,0 donne `["D", "A", "B"]` ; ce sont ces listes de rangs que `rrf` fusionnera.

```python
# [extrait] agent/recherche.py
def classement(scores: dict[str, float]) -> list[str]:
    """Rangs d'un retriever : score décroissant, nom en cas d'égalité ; un score nul ne classe pas.

    Exemple : `classement({"B": 2.0, "A": 2.0, "C": 0.0})` = ["A", "B"].
    """
    return [d for d, s in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0])) if s > 0]
```

- `scores.items()` donne les couples (identifiant, score).
- `sorted(…, key=lambda kv: (-kv[1], kv[0]))` trie selon un **tuple** : Python compare d'abord le premier élément, puis le second en cas d'égalité. `-kv[1]` met les grands scores en premier, `kv[0]` départage par nom croissant.
- **Analogie Java :** `Comparator.comparing((Map.Entry<String, Double> e) -> -e.getValue()).thenComparing(Map.Entry::getKey)`.
- `if s > 0` filtre **après** le tri, dans la compréhension ; le filtre aurait pu venir avant, le résultat serait le même.
- **Piège classique :** écrire `sorted(scores.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)`. `reverse=True` renverse **tout** le tuple, donc les noms aussi : à score égal, B passerait avant A. Négativer le seul score garde le départage croissant.

Sur l'exemple du test, `classement({"B": 2.0, "A": 2.0, "C": 0.0, "D": 3.0})` : D (3,0), puis A et B à 2,0 départagés par le nom, et C écarté. Résultat : `["D", "A", "B"]`.

**Test qui passe maintenant :**

```powershell
python -m unittest -v tests.test_07_recherche.TestFusion.test_classement
```

## La fusion, première tentative

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rrf(classements, k_rrf)`** — Dans ce brouillon, la fonction est un président de jury qui numérote les places à partir de zéro et laisse le hasard départager les ex aequo : elle reçoit une liste de classements et la constante `k_rrf`, 60 par défaut, cumule pour chaque document 1 / (k_rrf + rang) avec un rang tiré de `enumerate` qui commence à 0, puis renvoie les couples (identifiant, score) triés par score seul. REG-1 obtient alors 0,033060 au lieu de 0,032522, `k_rrf=0` provoquerait une division par zéro sur le premier document, et deux documents de même score restent dans l'ordre d'insertion du dictionnaire.

```python
# [extrait] brouillon
def rrf(classements: list[list[str]], k_rrf: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for c in classements:
        for rang, doc in enumerate(c):                 # FAUX : le premier a le rang 0
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k_rrf + rang)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)   # FAUX : égalités non départagées
```

Deux erreurs, faciles à faire et difficiles à voir.

- `enumerate(c)` numérote à partir de 0, alors que la formule de RRF numérote à partir de 1. Avec k_RRF = 60, REG-1 obtiendrait 1/61 + 1/60 = 0,033060 au lieu de 0,032522 : tous les scores sont faux, sans que l'ordre change forcément, donc un test qui ne regarde que l'ordre ne le verrait pas. Avec `k_rrf=0`, le premier document provoquerait une division par zéro.
- Le tri sur le seul score laisse les égalités dans l'ordre d'insertion du dictionnaire. Or les égalités sont fréquentes en RRF : deux documents classés 1ᵉʳ et 2ᵉ en sens inverse par les deux signaux ont exactement le même score. Le résultat dépendrait alors de l'ordre des classements.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rrf(classements, k_rrf)`** — C'est la même fonction, présidée cette fois avec rigueur : elle reçoit les classements et `k_rrf`, lève `ValueError` (« k_rrf >= 0 ») si la constante est négative, numérote chaque classement à partir de 1 avec `enumerate(c, start=1)`, cumule pour chaque document 1 / (k_rrf + rang) dans un dictionnaire où un nouveau venu part de 0, et renvoie les couples (identifiant, score) triés par la même clé que `classement`. Un document absent d'un classement n'y reçoit rien ; sur la requête du client C-5, REG-1 obtient 0,032522, REG-2 0,032266, FORUM-9 0,032002 et REG-4 0,031250, et `rrf([["A"], ["B", "A"]], k_rrf=0)` rend A à 1,5 et B à 1,0.

```python
# [extrait] agent/recherche.py
def rrf(classements: list[list[str]], k_rrf: int = 60) -> list[tuple[str, float]]:
    """RRF(d) = Σ_C 1 / (k_RRF + rang_C(d)) ; un document absent d'un classement y contribue 0.

    Sortie triée par score décroissant, égalités départagées par le nom.
    Exemple : REG-1, 2e par les mots et 1er par le sens : 1/62 + 1/61 ≈ 0.032522.
    """
    if k_rrf < 0:
        raise ValueError("k_rrf >= 0")
    scores: dict[str, float] = {}
    for c in classements:
        for rang, doc in enumerate(c, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k_rrf + rang)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
```

- `if k_rrf < 0` : un `k_rrf` négatif pourrait annuler le dénominateur (k_RRF = −1 et rang 1). Zéro reste permis, puisque le rang vaut au moins 1.
- `scores: dict[str, float] = {}` : une annotation de variable, utile à la lecture et aux outils, sans effet à l'exécution.
- `enumerate(c, start=1)` numérote à partir de 1 : c'est la correction du brouillon.
- `scores.get(doc, 0.0) + …` cumule ; un document vu pour la première fois part de 0. C'est ce qui réalise « un document absent d'un classement y contribue 0 » : il n'y a simplement pas de terme pour ce classement. En Java : `scores.merge(doc, 1.0 / (k + rang), Double::sum)`.
- Le tri final reprend exactement la clé de `classement`.

**Exemple fait à la main.** Les deux classements de la requête du client C-5 sont `["REG-2", "REG-1", "FORUM-9", "REG-4"]` (BM25) et `["REG-1", "FORUM-9", "REG-2", "REG-4"]` (cosinus) :

| Document | Rang BM25 | Rang cosinus | Calcul | RRF |
| --- | --- | --- | --- | --- |
| REG-1 | 2 | 1 | 1/62 + 1/61 | 0,032522 |
| REG-2 | 1 | 3 | 1/61 + 1/63 | 0,032266 |
| FORUM-9 | 3 | 2 | 1/63 + 1/62 | 0,032002 |
| REG-4 | 4 | 4 | 1/64 + 1/64 | 0,031250 |

REG-1 gagne sans être premier par les mots, parce qu'il est bien placé par les deux signaux. Aucun document ne peut dépasser 2/61 = 0,032787, la valeur d'un document premier partout.

Vérification dans la console, sur l'exemple du test où un document est absent d'un classement :

```text
# [extrait] console
>>> from agent.recherche import rrf
>>> rrf([["A"], ["B", "A"]], k_rrf=0)
[('A', 1.5), ('B', 1.0)]
```

A reçoit 1/1 du premier classement et 1/2 du second ; B ne reçoit que 1/1 du second.

- **Piège classique :** passer à `rrf` les dictionnaires de scores au lieu des classements. `enumerate` sur un dictionnaire parcourt ses clés dans l'ordre d'insertion, pas dans l'ordre des scores : aucune erreur, et une fusion fausse. C'est pourquoi `rrf` prend des **listes** produites par `classement`.

**Tests à cette étape :** `test_classement` est vert. Les trois tests de fusion (`test_deux_classements_et_rrf`, `test_rrf_ne_depend_que_des_rangs`, `test_rrf_document_absent_et_erreurs`) appellent aussi `rechercher_hybride` : ils passeront à l'étape suivante. La vérification console ci-dessus suffit pour l'instant.
