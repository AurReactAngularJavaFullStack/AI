# Étape 1 — L'intervalle de Wilson

> [Énoncé du palier 10](<../../README.md>) · Suivant : [Étape 2 — La Tool Call F1](<02-Tool-Call-F1.md>)

## Comment raisonner

Tout le palier repose sur une question : « ce taux de réussite est-il assez bon pour déployer ? ». Un taux seul ne répond pas. 18 réussites sur 18 et 3 sur 3 donnent tous deux 100 %, mais le second ne prouve presque rien. Il faut l'**incertitude** du taux, c'est-à-dire un intervalle, et décider sur sa borne basse : « même dans le cas défavorable, le vrai taux dépasse-t-il 80 % ? ».

On commence donc par `wilson`, la brique dont dépendent `rapport` et `barriere_ci`. La méthode est mécanique : on recopie la formule de l'énoncé **terme à terme**, en nommant chaque morceau (la proportion, le dénominateur commun, le centre, la demi-largeur), puis on traite les bords : n = 0, et les entrées impossibles.

## Un brouillon qui ment

La formule « de lycée », l'intervalle de Wald, vient en premier à l'esprit :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`wilson(succes, n, z)`** — Ce brouillon parle comme un bonimenteur de foire qui, après trois lancers réussis, jure que son tireur ne rate jamais. Il reçoit le nombre de succès, le nombre de cas et le quantile z, 1,96 par défaut, calcule la proportion p = succès / n, puis une demi-largeur z × √(p(1 − p) / n), et rend le couple (p − demi, p + demi). Il ne vérifie rien : 0 sur 0 lève une division par zéro, et 18 sur 18 donne p = 1, une demi-largeur nulle et l'intervalle [1 ; 1], une certitude absolue tirée de 18 essais, ce qui ouvrirait la barrière à n'importe quelle version parfaite sur trois dossiers.

```python
# [extrait] brouillon
def wilson(succes, n, z=1.96):
    p = succes / n
    demi = z * math.sqrt(p * (1 - p) / n)
    return (p - demi, p + demi)
```

Pour 18 sur 18, p = 1, donc p(1 − p) = 0 et la demi-largeur est nulle : l'intervalle vaut [1 ; 1], une certitude absolue tirée de 18 essais. C'est faux, et dangereux : la barrière laisserait passer n'importe quelle version parfaite sur trois cas. Pour 0 sur 0, la division par zéro fait planter le programme. L'intervalle de Wilson corrige le premier défaut en ajoutant z²/2n au centre et z²/4n² sous la racine, ce qui garde une largeur positive même quand p vaut 0 ou 1.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`wilson(succes, n, z)`** — La version juste ressemble à un géomètre qui plante ses jalons avec une marge d'erreur honnête, plus large quand il a peu de mesures. Elle reçoit les mêmes trois arguments, rend `None` d'emblée si n vaut 0, lève `ValueError("il faut 0 <= succes <= n")` pour un n négatif ou des succès hors de [0, n], puis calcule la proportion p, le dénominateur commun d = 1 + z²/n, le centre (p + z²/2n) / d et la demi-largeur z × √(p(1 − p)/n + z²/4n²) / d. Elle rend le couple (centre − demi, centre + demi) : [0,548 ; 0,910] pour 14 sur 18, une borne basse de 18 / 21,8416 = 0,824 pour 18 sur 18 et de 0,438 pour 3 sur 3, chiffres que la barrière comparera ensuite à 0,8.

```python
# [extrait] agent/evaluation.py
def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    ...
    if n == 0:
        return None
    if n < 0 or not 0 <= succes <= n:
        raise ValueError("il faut 0 <= succes <= n")
    p = succes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - demi, centre + demi)
```

**Ligne par ligne.**

- `if n == 0: return None` vient **en premier**. Sans cas, il n'y a pas de proportion : la convention du parcours rend `None`, ni 0 ni 1. Si la validation passait avant, `wilson(0, 0)` la franchirait (0 ≤ 0 ≤ 0 est vrai) et planterait sur `succes / n`.
- La validation refuse un nombre de succès négatif ou supérieur au nombre de cas, avec un message qui dit la règle.
- `p = succes / n` est la proportion observée. En Python 3, `/` est toujours une division réelle : 14 / 18 vaut 0,7778, pas 0 comme une division entière Java `14 / 18`.
- `d = 1 + z * z / n` est le dénominateur commun du centre et de la demi-largeur. `z * z` plutôt que `z ** 2` : même résultat, et c'est l'écriture de l'étape 77.
- `centre` et `demi` traduisent les deux termes de la formule. `math.sqrt` est `Math.sqrt` en Java.
- Le couple `(centre - demi, centre + demi)` est un tuple : en Java, on rendrait un `record Intervalle(double bas, double haut)`, et `None` correspondrait à un `Optional.empty()`.

Pour 14 sur 18, le calcul de l'énoncé donne d = 1,2134, un centre de 0,7289 et une demi-largeur de 0,1811, soit [0,548 ; 0,910]. Pour 18 sur 18, p = 1 annule p(1 − p), et la borne basse se simplifie en n / (n + z²) = 18 / 21,8416 = 0,824.

**Le piège classique.** Lire `z * z / 4 * n * n` au lieu de `z * z / (4 * n * n)`. Sans parenthèses, Python évalue de gauche à droite, ce qui donne (z²/4) × n × n, un nombre énorme, et l'intervalle déborde de [0, 1]. Les parenthèses de l'étape 77 ne sont pas décoratives.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_10_evaluation.TestWilson
```

`test_tout_reussi` compare la borne basse de 18 sur 18 à 18 / (18 + 1,96²) à 12 décimales, et à 0,824 à 3 décimales, vérifie la borne haute à 1, et la borne basse de 3 sur 3 à 0,438. `test_quatorze_sur_dix_huit` vérifie [0,548 ; 0,910]. `test_indefini_et_invalide` vérifie que `wilson(0, 0)` vaut `None` et que `wilson(5, 4)` lève `ValueError`.
