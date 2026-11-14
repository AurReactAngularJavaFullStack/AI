# Étape 4 — La fin de service

> Palier 03, étape 4 sur 7 · Précédent : [Étape 3 — Le taux d'endettement](<03-Ratio-d-endettement.md>) · Suivant : [Étape 5 — La TVA et le change](<05-TVA-et-change.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Lis la règle comme un juriste, puis traduis-la phrase par phrase. Le décret-loi fédéral 33/2021 dit, pour le secteur privé :

1. il faut au moins un an de service, sinon rien n'est dû ;
2. le salaire journalier est le salaire de **base** divisé par 30 ;
3. on compte 21 jours par an pour les 5 premières années, 30 jours par an au-delà, au prorata des années incomplètes ;
4. le total ne dépasse pas 24 mois de salaire de base.

Quatre phrases, quatre morceaux de code, dans cet ordre-là. Ajoute devant une garde pour les entrées absurdes. Pour la phrase 3, deux écritures sont possibles : des `if`, ou une formule unique avec `min` et `max`. On écrit d'abord les `if`, plus naturels, et l'on voit ce qui manque.

## Bloc 1 — Les deux tranches avec des `if`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`gratuite_fin_de_service(salaire_base_mensuel, annees)`** — Dans ce brouillon, la fonction est un gestionnaire de paie qui n'a lu que le milieu du décret : elle reçoit le salaire de base mensuel et l'ancienneté, calcule le salaire journalier en divisant par 30, puis renvoie 21 jours par année tant que l'ancienneté ne dépasse pas 5 ans, et sinon 105 jours pour la première tranche plus 30 jours par année au-delà. Elle trouve bien 55 000 AED pour 10 000 AED et 7 ans, mais elle verse 6 300 AED pour 0,9 an alors que rien n'est dû avant un an, accorde 385 000 AED pour 40 ans au lieu du plafond de 240 000 AED, et accepte sans broncher un salaire nul ou des années négatives.

```python
# [extrait] brouillon
def gratuite_fin_de_service(salaire_base_mensuel: float, annees: float) -> float:
    jour = salaire_base_mensuel / 30
    if annees <= 5:
        return annees * 21 * jour
    return 5 * 21 * jour + (annees - 5) * 30 * jour
```

Ce brouillon traduit bien la phrase 3, et donne 55 000 AED pour 10 000 AED et 7 ans. Mais il oublie deux phrases sur quatre.

- Phrase 1 : pour 0,9 an, il rend 0,9 × 21 × 333,33 = 6 300 AED, alors que rien n'est dû avant un an.
- Phrase 4 : pour 40 ans, il rend 105 × 333,33 + 35 × 30 × 333,33 = 385 000 AED, alors que le plafond est de 24 × 10 000 = 240 000 AED.

Il accepte aussi un salaire nul ou des années négatives sans broncher. C'est le défaut typique d'une traduction partielle : le cas « normal » marche, les bords sont faux. D'où la méthode : une ligne de code par phrase de la règle, et un test par bord.

## Bloc 2 — La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`gratuite_fin_de_service(salaire_base_mensuel, annees)`** — C'est la même fonction, réécrite par un gestionnaire de paie qui traduit le décret phrase par phrase, dans l'ordre : elle reçoit le salaire de base et l'ancienneté réelle, lève `ValueError` si le salaire n'est pas strictement positif ou si les années sont négatives, rend `0.0` avant un an de service, puis calcule le salaire journalier, base divisée par 30. Elle additionne ensuite `min(annees, 5)` années à 21 jours et `max(annees - 5, 0)` années à 30 jours, et renvoie le plus petit de ce total et de 24 mois de salaire de base. Pour 10 000 AED, elle donne 55 000 AED à 7 ans, 35 000 AED à 5 ans, 0 à 0,9 an et 240 000 AED à 40 ans, tout en gardant le prorata d'une année commencée.

```python
# [extrait] agent/metier.py
def gratuite_fin_de_service(salaire_base_mensuel: float, annees: float) -> float:
    """Indemnité de fin de service (décret-loi fédéral 33/2021, secteur privé, hors ressortissants
    émiriens et hors DIFC) : au moins 1 an de service ; salaire journalier = base / 30 ; 21 jours par an
    les 5 premières années, 30 jours au-delà, au prorata ; plafond : 24 mois de salaire de base.

    Exemple : `gratuite_fin_de_service(10_000, 7)` = 5 × 21 × 333.33 + 2 × 30 × 333.33
    = 35 000 + 20 000 = 55 000 AED ; moins d'un an de service donne 0.
    """
    if salaire_base_mensuel <= 0 or annees < 0:
        raise ValueError("salaire > 0 et annees >= 0")
    if annees < 1:
        return 0.0
    jour = salaire_base_mensuel / 30
    brut = min(annees, 5) * 21 * jour + max(annees - 5, 0) * 30 * jour
    return min(brut, 24 * salaire_base_mensuel)
```

**La docstring** dit le champ d'application : secteur privé, hors ressortissants émiriens (qui relèvent du régime de retraite des nationaux) et hors DIFC (qui a son propre régime d'épargne, DEWS). Une fonction métier qui ne dit pas où elle s'applique sera un jour appelée là où elle ne s'applique pas.

**La garde.** Salaire strictement positif, ancienneté positive ou nulle. Zéro année est une entrée valide (un salarié qui part le premier mois) : elle n'est pas une erreur, elle donne 0.

**Phrase 1.** `if annees < 1: return 0.0`. On rend `0.0` et non `0`, pour que la fonction rende toujours un `float`, comme l'annonce sa signature. Ce retour anticipé (une « clause de garde ») évite d'imbriquer le reste du calcul dans un `else`.

**Phrase 2.** `jour = salaire_base_mensuel / 30` : 30 jours, quel que soit le mois. Le paramètre s'appelle `salaire_base_mensuel` et non `salaire` : c'est la base seule, sans les indemnités de logement ni de transport, qui sert au calcul.

**Phrase 3.** `min(annees, 5) * 21 * jour + max(annees - 5, 0) * 30 * jour`, la formule du README écrite telle quelle.

- `min(annees, 5)` vaut le nombre d'années de la première tranche : 3,5 pour 3,5 ans, 5 dès qu'on dépasse 5 ans.
- `max(annees - 5, 0)` vaut le nombre d'années de la seconde tranche : 0 tant qu'on n'a pas dépassé 5 ans (le `max` empêche une durée négative), 2 pour 7 ans.

Une seule expression couvre tous les cas, sans `if`. C'est l'idiome du « pivot » : pour découper une quantité en tranches, `min(x, seuil)` donne la part sous le seuil, `max(x - seuil, 0)` la part au-dessus. On le retrouve dans les barèmes d'impôt (l'impôt sur les sociétés de 9 % au-delà de 375 000 AED s'écrit `0.09 * max(benefice - 375_000, 0)`).

**Phrase 4.** `min(brut, 24 * salaire_base_mensuel)` : le plafond est un `min`, encore une fois. Pour 40 ans, `brut` vaut 385 000 et `24 * 10_000` vaut 240 000 : la fonction rend 240 000. Ici, `min` rend l'entier `240000` lui-même, parce qu'il est plus petit que le flottant : le test `assertEqual(..., 240_000)` passe, et un entier se compare très bien à un flottant en Python.

**Vérification à la main.** S = 10 000, a = 7 : jour = 333,33 ; min(7, 5) × 21 = 105 jours, soit 35 000 AED ; max(2, 0) × 30 = 60 jours, soit 20 000 AED ; total 55 000 AED, sous 240 000. Pour a = 5 : 105 jours, 35 000 AED. Pour a = 0,9 : 0.

**Le piège des jours entiers.** Compter seulement les années complètes, avec `int(annees)`, ferait perdre au salarié la part de l'année commencée : pour 3,5 ans, il toucherait 3 × 21 × 333,33 = 21 000 AED au lieu de 24 500 AED. La règle dit « au prorata » : `annees` est un réel, et on le garde réel.

**Les tests qui passent maintenant.**

```text
python -m unittest -v tests.test_03_metier.TestFinDeService
```

`test_sept_ans` (55 000), `test_moins_d_un_an_et_plafond` (0, 35 000 et 240 000) et `test_entrees_invalides` (salaire nul, années négatives).

**Ce qu'il faut retenir.** Une ligne de code par phrase de la règle. Les tranches et les plafonds s'écrivent avec `min` et `max`, sans `if`. Un bord oublié (moins d'un an, plafond) donne un code qui marche sur l'exemple et qui est faux en production.
