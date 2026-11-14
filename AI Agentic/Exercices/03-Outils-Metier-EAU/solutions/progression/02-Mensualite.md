# Étape 2 — La mensualité

> Palier 03, étape 2 sur 7 · Précédent : [Étape 1 — Les constantes et l'affichage français](<01-Constantes-et-affichage-fr.md>) · Suivant : [Étape 3 — Le taux d'endettement](<03-Ratio-d-endettement.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Pars de la formule du README, M = P r / (1 − (1 + r)⁻ⁿ), et de ses trois valeurs testées : 5 558,32 AED pour 1 000 000 AED à 4,5 % sur 300 mois, 5 000 AED pour 120 000 AED à taux nul sur 24 mois, et trois appels qui doivent lever `ValueError`. Cela donne l'ordre d'écriture :

1. la garde, qui refuse ce qui n'a pas de sens, parce qu'elle protège tout le reste ;
2. le taux mensuel r, parce que la formule est mensuelle et le taux donné est annuel ;
3. le calcul, avec un cas particulier dès qu'on voit une division : peut-elle valoir 0 ?

Le troisième point est celui qu'on oublie. On commence donc par la version naïve, pour voir où elle casse.

## Bloc 1 — La formule seule

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`mensualite(principal, taux_annuel, n_mois)`** — Dans ce brouillon, la fonction est un conseiller qui applique sa formule sans jamais lever les yeux de sa calculatrice : elle reçoit le capital, le taux annuel en fraction et le nombre de mois, divise le taux par 12 pour obtenir le taux mensuel r, puis renvoie P r / (1 − (1 + r)⁻ⁿ). Pour 1 000 000 AED à 4,5 % sur 300 mois, elle rend déjà 5 558,3248 AED, mais un taux nul la fait tomber sur `ZeroDivisionError`, puisque numérateur et dénominateur valent alors 0, et elle laisse passer sans protester un principal négatif ou une durée nulle.

```python
# [extrait] brouillon
def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    r = taux_annuel / 12
    return principal * r / (1 - (1 + r) ** -n_mois)
```

**Ligne 2.** `taux_annuel / 12` : en Python 3, `/` est toujours une division réelle, même entre deux entiers. 0,045 / 12 = 0,00375.

**Ligne 3.** `(1 + r) ** -n_mois` : `**` est la puissance, l'équivalent de `Math.pow`. L'exposant peut être négatif, et `-n_mois` est bien lu comme l'opposé de `n_mois`. Attention au piège voisin : `-x ** 2` vaut −(x²), parce que `**` lie plus fort que le moins placé à sa gauche ; d'où les parenthèses autour de `1 + r`.

Avec les nombres de l'hypothèque de C-1, cette version rend déjà 5 558,3248 AED. Mais le taux nul la fait tomber :

```text
>>> mensualite(120_000, 0.0, 24)
Traceback (most recent call last):
  ...
ZeroDivisionError: float division by zero
```

Avec r = 0, (1 + 0)⁻²⁴ vaut 1, le dénominateur 1 − 1 vaut 0, et le numérateur aussi. La formule est une forme 0/0, alors que la réponse a un sens évident : sans intérêt, on rembourse 120 000 / 24 = 5 000 AED par mois. Elle laisse aussi passer un principal négatif ou une durée nulle, qui produiraient un nombre absurde ou une autre division par zéro.

## Bloc 2 — La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`mensualite(principal, taux_annuel, n_mois)`** — C'est la même fonction que dans le brouillon, devenue le conseiller prudent qui vérifie le dossier avant de sortir sa calculatrice : elle reçoit le capital, le taux annuel et la durée, lève `ValueError` (« principal > 0, n_mois > 0, taux >= 0 ») si le capital ou la durée ne sont pas strictement positifs ou si le taux est négatif, calcule le taux mensuel, puis renvoie P/n quand ce taux vaut exactement 0 et la formule de l'annuité sinon. Le résultat n'est pas arrondi, 5558,324779619954 pour l'hypothèque de C-1, car l'arrondi au centime se fait une seule fois, dans l'outil du palier 04 ou par `fr` ; un prêt de 120 000 AED sans intérêt sur 24 mois donne exactement 5 000 AED.

```python
# [extrait] agent/metier.py
def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    """M = P r / (1 − (1 + r)^−n), avec r = taux annuel / 12 ; M = P / n si le taux est nul.

    Exemple : `mensualite(1_000_000, 0.045, 300)` : r = 0.00375, M = 3 750 / 0.67467 ≈ 5 558.32 AED ;
    `mensualite(120_000, 0.0, 24)` = 5 000 AED.
    """
    if principal <= 0 or n_mois <= 0 or taux_annuel < 0:
        raise ValueError("principal > 0, n_mois > 0, taux >= 0")
    r = taux_annuel / 12
    return principal / n_mois if r == 0 else principal * r / (1 - (1 + r) ** -n_mois)
```

**La garde (le `if` et son `raise`).** Trois conditions, réunies par `or`, et une seule exception dont le message rappelle le domaine valide. `ValueError` est l'équivalent Python d'`IllegalArgumentException` : l'argument a le bon type mais une valeur interdite. Le taux nul est permis (`< 0`, pas `<= 0`) : un prêt sans intérêt existe, par exemple une avance sur salaire. Le principal et la durée doivent être strictement positifs.

Pourquoi garder ici, alors que le palier 04 validera les arguments de l'outil contre un schéma ? Parce que cette fonction est aussi appelée directement, sans passer par l'outil : par la démo, par l'assemblage du palier 12, par un futur script de simulation. La garde du domaine est la dernière ligne de défense, et elle ne coûte rien.

**Le taux mensuel.** Inchangé.

**Le calcul (la ligne `return`).** `a if condition else b` est l'opérateur ternaire de Python, le `condition ? a : b` de Java, écrit dans l'autre ordre : la valeur normale, puis la condition, puis l'autre valeur. Si r vaut exactement 0, on rend P/n, la limite de la formule quand r tend vers 0 ; sinon la formule.

Comparer un flottant à 0 avec `==` est sûr ici : `0.0 / 12` vaut exactement `0.0`. Le cas visé est le taux nul écrit tel quel, pas un taux minuscule, pour lequel la formule reste calculable.

**Le résultat n'est pas arrondi.** `mensualite(1_000_000, 0.045, 300)` rend 5558.324779619954, et c'est voulu : l'arrondi au centime se fait une seule fois, au bout de la chaîne, dans l'outil du palier 04 (`round(..., 2)`) ou à l'affichage par `fr`. Arrondir ici ferait calculer le ratio d'endettement sur un nombre déjà arrondi, et les erreurs s'accumuleraient.

**Le piège.** Diviser le taux annuel par 100 « parce que c'est un pourcentage » : le module travaille en fractions, et `taux_annuel` vaut déjà 0,045. Avec 0,00045 / 12, la mensualité tomberait à 3 352,18 AED, à peine plus que 1 000 000 / 300 = 3 333 AED, et aucun test d'ordre de grandeur ne crierait si l'on ne vérifie pas la valeur exacte.

**Vérification à la main.** r = 0,00375 ; (1,00375)³⁰⁰ = 3,073743 ; 1 − 1 / 3,073743 = 0,674664 ; 1 000 000 × 0,00375 = 3 750 ; 3 750 / 0,674664 = 5 558,32 AED.

**Les tests qui passent maintenant.** Depuis `projet/` :

```text
python -m unittest -v tests.test_03_metier.TestCredit.test_mensualite_hypotheque tests.test_03_metier.TestCredit.test_mensualite_taux_nul tests.test_03_metier.TestCredit.test_mensualite_entrees_invalides
```

Le premier compare à 5 558,32 avec deux décimales (`assertAlmostEqual(..., places=2)`), le deuxième exige exactement 5 000.0, le troisième essaie un principal nul, une durée nulle et un taux négatif.

**Ce qu'il faut retenir.** Garde d'abord, puis la formule ; devant chaque division, demander « ce dénominateur peut-il valoir 0 ? » et traiter le cas par sa limite. Aucun arrondi dans le domaine.
