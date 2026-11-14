# Étape 5 — La fiabilité d'une chaîne

> Palier 01, étape 5 sur 7 · Précédent : [Étape 4 — La softmax](<04-Softmax.md>) · Suivant : [Étape 6 — Le prompt](<06-Prompt-et-donnees-non-fiables.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire `fiabilite_serie` et `bornes_fiabilite`. Les trois tests de `TestFiabilite` passent à la fin.

## Comment raisonner

La softmax a montré que le modèle tire chaque token au hasard, avec des probabilités. Un agent enchaîne plusieurs tirages de ce genre (choisir l'outil, écrire ses arguments, recopier le résultat) et plusieurs exécutions d'outils. La question d'ingénieur est : **si chaque étape réussit 98 fois sur 100, combien de fois la chaîne entière réussit-elle ?** La réponse fixe toute l'architecture des paliers suivants : calculer avec des outils plutôt que de tête, regrouper deux appels d'outils dans une même réponse, éviter un tour de conversation inutile.

Deux fonctions, parce qu'il y a deux situations :

1. si les étapes échouent **indépendamment** les unes des autres, la probabilité de succès est le produit des pᵢ ;
2. si l'on ne sait rien de leurs liens, on ne peut donner qu'un **encadrement**, toujours vrai.

On commence par la plus simple, le produit, et par son piège : l'élément neutre.

## Le piège de l'accumulateur

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fiabilite_serie(probas)`** — Dans ce brouillon, la fonction est un caissier qui commencerait sa journée avec une caisse vide et prétendrait ensuite la multiplier : elle reçoit la liste des probabilités de réussite des étapes, initialise son accumulateur à 0,0, le multiplie successivement par chaque probabilité, puis renvoie le résultat. Comme zéro fois n'importe quel nombre reste zéro, elle renvoie 0 pour toute entrée, six étapes à 0,98 comprises ; c'est le piège du mauvais élément neutre, que la version suivante corrige en partant de 1 avec `math.prod`.

```python
# [extrait] brouillon
def fiabilite_serie(probas: list[float]) -> float:
    resultat = 0.0                   # mauvais neutre : 0 × quoi que ce soit = 0
    for p in probas:
        resultat *= p
    return resultat
```

On écrit la boucle comme une somme, avec un accumulateur à zéro, et la fonction rend 0 pour toute entrée. Le neutre de la multiplication est 1, pas 0. En Java, c'est l'erreur de `stream.reduce(0.0, (a, b) -> a * b)` au lieu de `reduce(1.0, ...)`. La bibliothèque standard de Python a la bonne fonction : `math.prod`, qui part de 1.

Mais `math.prod([])` vaut 1 : une chaîne de zéro étape « réussirait toujours ». Ce n'est pas une réponse, c'est une liste vide passée par erreur. On la refuse explicitement.

## Le produit

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fiabilite_serie(probas)`** — C'est la même fonction que dans le brouillon, devenue l'inspectrice qui vérifie chaque maillon avant de dire si la chaîne tiendra : elle reçoit la liste des probabilités de réussite, lève `ValueError` si la liste est vide, puis une seconde `ValueError` si l'une des valeurs sort de l'intervalle [0, 1], ce qui écarte aussi un NaN puisque toute comparaison avec lui est fausse. Elle renvoie enfin le produit de toutes les probabilités, calculé par `math.prod` à partir de 1 : six étapes à 0,98, celles du scénario de crédit de l'étape 77, donnent environ 0,8858, et une septième fait tomber la chaîne à 0,8681.

```python
# [extrait] agent/modele.py
def fiabilite_serie(probas: list[float]) -> float:
    """P(succès) = ∏ pᵢ : une chaîne d'étapes indépendantes réussit si TOUTES réussissent (étape 1).

    Exemple : six étapes à 0.98 (trois appels au modèle, trois outils) donnent 0.98⁶ ≈ 0.8858 ;
    une septième étape ferait tomber la chaîne à 0.98⁷ ≈ 0.8681.
    """
    if not probas:
        raise ValueError("il faut au moins une étape")
    if not all(0.0 <= p <= 1.0 for p in probas):
        raise ValueError("chaque probabilité doit être dans [0, 1]")
    return math.prod(probas)
```

**`if not probas:`** refuse la liste vide, pour la raison donnée plus haut.

**`if not all(0.0 <= p <= 1.0 for p in probas):`** se lit de droite à gauche.

- `0.0 <= p <= 1.0` est une **comparaison chaînée**, que Python autorise et Java non : elle vaut `0.0 <= p and p <= 1.0`.
- `(... for p in probas)` est une expression génératrice : elle produit les booléens un par un, sans construire de liste.
- `all(...)` rend vrai si tous les booléens le sont, et s'arrête au premier faux. C'est `probas.stream().allMatch(p -> 0 <= p && p <= 1)`.

Un bonus gratuit : une probabilité égale à `float("nan")` est refusée, parce que toute comparaison avec NaN vaut faux.

**`return math.prod(probas)`.** Le produit, qui part de 1.

**Vérifier à la main.** Le scénario de crédit de l'étape 77 a six étapes (trois appels au modèle, trois exécutions d'outils), chacune fiable à 0,98, valeur illustrative :

$$
0{,}98^2 = 0{,}9604, \qquad 0{,}98^3 = 0{,}941192, \qquad 0{,}98^6 = 0{,}941192^2 = 0{,}885842
$$

Une septième étape donne 0,885842 × 0,98 = 0,868126. Sur 10 000 demandes, c'est environ 177 dossiers de plus avec au moins une erreur.

```powershell
python -m unittest -v tests.test_01_modele.TestFiabilite.test_six_etapes
```

## L'encadrement sans indépendance

En pratique, les erreurs d'un agent sont corrélées : une question mal comprise fausse plusieurs étapes à la fois. Le produit n'est alors plus exact, mais deux bornes restent vraies :

$$
\max\Big(0,\; 1 - \sum_{i=1}^{n} (1 - p_i)\Big) \;\le\; P(\text{succès}) \;\le\; \min_i\, p_i
$$

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`bornes_fiabilite(probas)`** — Cette fonction est l'experte prudente qu'on consulte quand on soupçonne les étapes de tomber en panne ensemble, comme les wagons d'un train qui déraillent l'un derrière l'autre : elle reçoit la liste des probabilités de réussite, applique les deux mêmes gardes que `fiabilite_serie`, liste vide et valeur hors de [0, 1], puis renvoie un tuple de deux nombres. Le premier est 1 moins la somme des probabilités d'échec 1 − pᵢ, ramené à 0 s'il devient négatif ; le second est la plus petite des pᵢ, celle de l'étape la plus fragile. Six étapes à 0,98 donnent ainsi le couple (0,88 ; 0,98), affiché `0.8799999999999999` en flottants, et les étapes à 0,5 et 0,4 donnent (0 ; 0,4).

```python
# [extrait] agent/modele.py
def bornes_fiabilite(probas: list[float]) -> tuple[float, float]:
    """Encadrement valable SANS hypothèse d'indépendance : max(0, 1 − Σ(1 − pᵢ)) <= P <= min pᵢ.

    Exemple : six étapes à 0.98 donnent (1 − 6 × 0.02, 0.98) = (0.88, 0.98).
    """
    if not probas:
        raise ValueError("il faut au moins une étape")
    if not all(0.0 <= p <= 1.0 for p in probas):
        raise ValueError("chaque probabilité doit être dans [0, 1]")
    return max(0.0, 1.0 - sum(1.0 - p for p in probas)), min(probas)
```

**Les gardes** sont les mêmes que plus haut. On pourrait les factoriser dans une fonction privée `_verifier(probas)` ; la solution les répète parce que deux fois trois lignes restent lisibles, et que chaque fonction se comprend seule.

**La borne basse, `max(0.0, 1.0 - sum(1.0 - p for p in probas))`.** `1.0 - p` est la probabilité que l'étape échoue ; leur somme majore la probabilité qu'au moins une échoue (la probabilité d'une réunion est au plus la somme des probabilités) ; un moins cette somme minore donc le succès. Quand la somme dépasse 1, la borne devient négative, ce qui ne dit rien : `max(0.0, ...)` la ramène à 0.

**La borne haute, `min(probas)`.** La chaîne ne peut pas réussir plus souvent que son étape la plus fragile, puisque « tout réussit » implique « cette étape réussit ».

**`return a, b`.** Deux valeurs séparées par une virgule forment un tuple, sans parenthèses nécessaires. L'appelant le déballe : `bas, haut = bornes_fiabilite(...)`. En Java, il faudrait un petit `record Bornes(double bas, double haut)`.

**Vérifier à la main.** Six étapes à 0,98 : la somme des échecs vaut 6 × 0,02 = 0,12, donc les bornes sont 0,88 et 0,98, et le produit 0,8858 tombe bien entre les deux. Deux étapes à 0,5 et 0,4 : la somme des échecs vaut 0,5 + 0,6 = 1,1, la borne basse 1 − 1,1 = −0,1 est ramenée à 0, la borne haute vaut 0,4.

**Le piège classique : l'égalité exacte entre flottants.**

```text
# [extrait] console
>>> from agent.modele import bornes_fiabilite
>>> bornes_fiabilite([0.98] * 6)
(0.8799999999999999, 0.98)
>>> bornes_fiabilite([0.5, 0.4])
(0.0, 0.4)
```

En binaire, 1 − 0,98 ne vaut pas exactement 0,02, et six arrondis s'accumulent. C'est pour cela que le test compare la borne basse avec `assertAlmostEqual(bas, 0.88, places=12)` et non avec `assertEqual`. La même chose arrive en Java avec des `double` ; c'est l'une des raisons pour lesquelles les montants, dans les paliers suivants, sont arrondis avant d'être affichés.

## Les tests qui passent maintenant

```powershell
python -m unittest -v tests.test_01_modele.TestFiabilite
```

Les trois tests sont verts : `test_six_etapes` (0,8858 et 0,8681), `test_bornes_sans_independance` (0,88 et 0,98, puis 0 et 0,4) et `test_entrees_invalides` (`[]`, `[1.2]` et `[-0.1, 0.5]` refusées par `fiabilite_serie`, `[]` refusée par `bornes_fiabilite`).

## Ce qu'il faut retenir

- Une chaîne d'étapes indépendantes réussit avec le produit des fiabilités : chaque étape de plus la fait baisser.
- Sans indépendance, il reste un encadrement : au moins un moins la somme des probabilités d'échec (jamais sous zéro), au plus la fiabilité de l'étape la plus fragile.
- Le neutre d'un produit est 1 ; une liste vide se refuse ; deux flottants se comparent avec une tolérance.

> Suivant : [Étape 6 — Le prompt](<06-Prompt-et-donnees-non-fiables.md>)
