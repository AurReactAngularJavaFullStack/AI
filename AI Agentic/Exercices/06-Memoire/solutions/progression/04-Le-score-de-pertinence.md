# Étape 4 — Le score de pertinence

> Progression du palier 06 · Précédent : [Étape 3 — La récence](<03-La-recence.md>) · Suivant : [Étape 5 — Le souvenir](<05-Le-souvenir.md>) · Retour à l'énoncé : [README du palier 06](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Le calcul du score tient en une ligne : une somme pondérée de trois nombres.

$$
S = w_{sim}\,sim + w_{rec}\,rec + w_{imp}\,imp
$$

Une ligne suffit pour le calcul ; le travail est ailleurs. Il faut décider ce que la fonction **refuse**, parce que tout l'intérêt du score est d'être un nombre entre 0 et 1, comparable d'une question à l'autre. La démonstration de l'étape 17 dit exactement à quelles conditions il le reste. Les trois composantes doivent être dans [0, 1], et les poids doivent être positifs et de somme 1 :

$$
0 = \sum_c w_c \times 0 \;\le\; \sum_c w_c\,x_c \;\le\; \sum_c w_c \times 1 = 1
$$

Chaque hypothèse de la preuve devient une garde du code. On écrit donc d'abord les gardes, une par hypothèse, puis la ligne de calcul.

## Un brouillon sans gardes

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`score_pertinence(sim, rec, imp, poids)`** — Dans ce brouillon, la fonction est un jury qui applique ses coefficients sans jamais vérifier ni les coefficients ni les copies : elle reçoit les trois composantes et le triplet des poids, déballe ce triplet en trois poids, et renvoie la somme des trois produits. Le calcul est juste sur des entrées justes, mais des poids (0,6 ; 0,6 ; −0,2) font valoir −0,2 au souvenir (0, 0, 1), des poids de somme 1,1 portent un souvenir parfait à 1,1, et une importance brute de 9 pèse 1,8 et écrase tout le reste, sans le moindre avertissement.

```python
# [extrait] brouillon
def score_pertinence(sim, rec, imp, poids):
    w_sim, w_rec, w_imp = poids
    return w_sim * sim + w_rec * rec + w_imp * imp
```

Ce brouillon calcule juste quand on lui donne des entrées justes, et faux sans prévenir dans les autres cas.

- Avec les poids (0,6 ; 0,6 ; −0,2), de somme 1 mais avec un poids négatif, le souvenir (0, 0, 1) vaut −0,2. Un souvenir important serait **puni** pour son importance.
- Avec (0,5 ; 0,3 ; 0,3), de somme 1,1, un souvenir parfait vaut 1,1. Un seuil de 0,6 n'a plus le même sens qu'avec des poids de somme 1.
- Avec une importance brute de 9 au lieu de son min-max, l'importance pèse 0,2 × 9 = 1,8 et écrase tout le reste.

Le test `test_refus` vérifie les trois refus.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`score_pertinence(sim, rec, imp, poids)`** — C'est la même fonction, devenue le jury scrupuleux qui contrôle son barème et chaque copie avant de noter : elle reçoit les trois composantes et les poids, lève `ValueError` (« les poids doivent être >= 0 et de somme 1 ») si un poids est négatif ou si leur somme s'écarte de 1 de plus de 10⁻⁹, puis une autre `ValueError` qui conseille de normaliser d'abord si une composante sort de [0, 1]. Elle renvoie ensuite la somme des produits poids × composante, appariés par `zip` ; le souvenir « salaire », de composantes 1, 0,9229 et 1 avec les poids (0,5 ; 0,3 ; 0,2), obtient 0,97687, tandis que des poids légitimes comme (0,7 ; 0,29 ; 0,01), dont la somme flottante vaut 0,9999999999999999, restent acceptés grâce à la tolérance.

```python
# [extrait] agent/memoire.py
def score_pertinence(sim: float, rec: float, imp: float, poids: tuple[float, float, float]) -> float:
    """S = w_sim · sim + w_rec · rec + w_imp · imp ; refuse ce qui casse la borne [0, 1].

    Poids négatifs, somme différente de 1 ou composante hors de [0, 1] : `ValueError`.
    Exemple : `score_pertinence(1.0, 0.9229, 1.0, (0.5, 0.3, 0.2))` = 0.5 + 0.27687 + 0.2 ≈ 0.9769.
    """
    if min(poids) < 0 or abs(sum(poids) - 1.0) > 1e-9:
        raise ValueError("les poids doivent être >= 0 et de somme 1")
    if not all(0.0 <= x <= 1.0 for x in (sim, rec, imp)):
        raise ValueError("chaque composante doit être dans [0, 1] : normaliser d'abord")
    return sum(w * x for w, x in zip(poids, (sim, rec, imp)))
```

**La signature.** `poids: tuple[float, float, float]` annonce exactement trois réels, dans l'ordre similarité, récence, importance. Un tuple plutôt qu'une liste, parce qu'un réglage ne change pas pendant un calcul ; en Java, ce serait un `record Poids(double sim, double rec, double imp)`.

**Première garde, les poids.** `min(poids) < 0` détecte un poids négatif : si le plus petit est positif, tous le sont. `abs(sum(poids) - 1.0) > 1e-9` détecte une somme différente de 1, avec une tolérance. Pourquoi une tolérance ? Parce qu'en flottant, des poids de somme mathématique 1 ne donnent pas toujours exactement 1.0 :

```text
# [extrait] console
>>> sum((0.7, 0.29, 0.01))
0.9999999999999999
```

Une comparaison stricte, `sum(poids) != 1.0`, refuserait ce réglage légitime. 10⁻⁹ est très au-dessus de l'erreur d'arrondi d'une somme de trois flottants, de l'ordre de 10⁻¹⁶, et très en dessous de toute erreur de saisie réelle, comme 1,1. C'est le même principe que `Math.abs(a - b) < 1e-9` en Java, ou que `math.isclose`.

**Deuxième garde, les composantes.** `all(0.0 <= x <= 1.0 for x in (sim, rec, imp))` est vrai si les trois composantes sont dans [0, 1]. Python permet l'encadrement chaîné `0.0 <= x <= 1.0`, qui s'écrirait `0.0 <= x && x <= 1.0` en Java. Le message dit quoi faire : « normaliser d'abord ». La fonction ne normalise pas elle-même, car le min-max a besoin de **tous** les candidats, alors qu'elle n'en voit qu'un.

**Le calcul.** `zip(poids, (sim, rec, imp))` associe chaque poids à sa composante, et `sum(w * x for …)` fait la somme des produits. Écrire la somme avec `zip` plutôt que trois termes nommés évite d'associer un poids à la mauvaise composante, et la formule reste juste si l'on ajoute un quatrième signal.

**Le piège classique.** Vérifier les poids mais pas les composantes. Un appelant qui oublie le min-max passe alors une importance de 9, et le score sort de [0, 1] sans erreur. C'est le défaut que l'étape 17 démontre, avec un souvenir hors sujet qui bat un souvenir pertinent.

## Vérification à la main et à la console

Pour le souvenir « salaire » du scénario du crédit, les composantes normalisées valent 1, 0,9229 et 1. Son score vaut donc 0,5 × 1 + 0,3 × 0,9229 + 0,2 × 1 = 0,5 + 0,27687 + 0,2 = 0,97687.

```text
# [extrait] console
>>> from agent.memoire import score_pertinence
>>> score_pertinence(1.0, 0.9229, 1.0, (0.5, 0.3, 0.2))
0.97687
>>> score_pertinence(0.0, 0.0, 1.0, (0.6, 0.6, -0.2))
Traceback (most recent call last):
  ...
ValueError: les poids doivent être >= 0 et de somme 1
```

## Le test qui passe maintenant

```text
python -m unittest -v tests.test_06_memoire.TestScorePertinence
```

Les deux tests passent : l'exemple 0,97687, comparé à cinq décimales, et les trois refus (poids négatif, somme 1,1, similarité 1,2). Neuf tests sur treize sont verts. Il ne reste que `TestRappeler`, qui a besoin de l'objet souvenir.
