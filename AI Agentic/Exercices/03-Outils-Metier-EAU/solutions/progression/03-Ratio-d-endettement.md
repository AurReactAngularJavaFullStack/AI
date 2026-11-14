# Étape 3 — Le taux d'endettement

> Palier 03, étape 3 sur 7 · Précédent : [Étape 2 — La mensualité](<02-Mensualite.md>) · Suivant : [Étape 4 — La fin de service](<04-Fin-de-service.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

La question métier est : « ce client peut-il supporter ce nouveau prêt ? ». La réponse a deux parties, un nombre (le taux) et un verdict (recevable ou non), et le verdict dépend d'un plafond qui n'est pas le même pour tout le monde (50 %, ou 30 % pour un retraité). D'où la signature : trois montants, un plafond **en paramètre** avec 50 % par défaut, et un couple en retour.

Avant d'écrire le calcul, demande-toi ce que la règle mesure vraiment. La CBUAE ne plafonne pas la nouvelle mensualité : elle plafonne **l'endettement total**. C'est l'erreur qu'on fait le plus souvent, et c'est elle qu'on écrit en premier.

## Bloc 1 — Le ratio qui oublie les dettes existantes

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ratio_endettement(mensualites_existantes, nouvelle_mensualite, revenu_mensuel, plafond)`** — Dans ce brouillon, la fonction est un analyste distrait qui ne pèse que le nouveau sac posé sur la balance et oublie ceux que le client porte déjà : elle reçoit les quatre paramètres, mais divise seulement la nouvelle mensualité par le revenu, et renvoie ce ratio avec le booléen qui dit s'il ne dépasse pas le plafond, 0,50 par défaut. Pour C-1, elle rend 0,139 au lieu de 0,288958, et un client qui rembourse déjà 15 000 AED par mois obtiendrait encore un verdict favorable, alors que son endettement réel atteint 51,4 % ; le paramètre `mensualites_existantes` est reçu, mais jamais utilisé.

```python
# [extrait] brouillon
def ratio_endettement(mensualites_existantes: float, nouvelle_mensualite: float, revenu_mensuel: float,
                      plafond: float = PLAFOND_CBUAE) -> tuple[float, bool]:
    ratio = nouvelle_mensualite / revenu_mensuel
    return ratio, ratio <= plafond
```

Pour C-1 (5 558,32 AED de mensualité, 40 000 AED de revenu), ce brouillon rend 0,139, soit 13,9 %. Le test attend 0,288958 : il manque les 6 000 AED de crédit auto. Le danger n'est pas seulement un mauvais nombre : un client qui rembourse déjà 15 000 AED par mois obtiendrait encore 13,9 % et un verdict favorable, alors que son endettement réel est de (15 000 + 5 558,32) / 40 000 = 51,4 %. Le paramètre `mensualites_existantes` est là, mais rien ne l'utilise : un linter le signalerait, pas le compilateur.

## Bloc 2 — La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ratio_endettement(mensualites_existantes, nouvelle_mensualite, revenu_mensuel, plafond)`** — C'est la même fonction, confiée cette fois à l'analyste scrupuleux qui pose toutes les charges du client sur la balance avant de rendre son verdict : elle reçoit les mensualités en cours, la nouvelle mensualité, le revenu et le plafond, `PLAFOND_CBUAE` par défaut, et lève `ValueError` sur un revenu nul ou négatif, sur une mensualité négative, puis sur un plafond hors de ]0, 1]. Elle additionne ensuite les deux mensualités avant de diviser par le revenu et renvoie le couple (ratio, ratio inférieur ou égal au plafond). C-1 obtient 0,288958 et un dossier recevable, le retraité C-2 au plafond de 0,30 est refusé à 0,313958, et un ratio de 0,5 tout juste reste recevable.

```python
# [extrait] agent/metier.py
def ratio_endettement(mensualites_existantes: float, nouvelle_mensualite: float, revenu_mensuel: float,
                      plafond: float = PLAFOND_CBUAE) -> tuple[float, bool]:
    """Ratio CBUAE : TOUTES les mensualités (existantes + nouvelle) / revenu ; rend (ratio, ratio <= plafond).

    Exemple : `ratio_endettement(6_000, 5558.32, 40_000)` = (11 558.32 / 40 000, True) = (0.288958, True) ;
    avec `plafond=0.30` (retraité), 7 000 + 5 558.32 sur 40 000 donne (0.313958, False).
    """
    if revenu_mensuel <= 0:
        raise ValueError("revenu > 0")
    if mensualites_existantes < 0 or nouvelle_mensualite < 0:
        raise ValueError("les mensualités sont >= 0")
    if not 0 < plafond <= 1:
        raise ValueError("le plafond est dans ]0, 1]")
    ratio = (mensualites_existantes + nouvelle_mensualite) / revenu_mensuel
    return ratio, ratio <= plafond
```

**La signature.** `plafond: float = PLAFOND_CBUAE` : la valeur par défaut est la constante de l'étape 1, évaluée **une fois**, quand Python exécute la ligne `def`. Pour un retraité, l'appelant passe `plafond=PLAFOND_RETRAITE`. Le type de retour `tuple[float, bool]` annonce un couple ; en Java, on écrirait un `record Verdict(double ratio, boolean recevable)`. En Python, un tuple suffit, parce que l'appelant le déballe aussitôt : `ratio, recevable = ratio_endettement(...)`.

**Première garde.** `revenu_mensuel <= 0` : le revenu est un dénominateur. Un revenu nul donnerait `ZeroDivisionError`, un revenu négatif un ratio négatif, donc « recevable ». Les deux sont refusés avec un message qui dit la règle.

**Deuxième garde.** Une mensualité négative ferait baisser le ratio : un modèle qui écrirait « −6 000 » par erreur de signe rendrait un client surendetté recevable. On refuse.

**Troisième garde.** `not 0 < plafond <= 1` utilise une comparaison chaînée : `0 < plafond <= 1` se lit comme en mathématiques et vaut `0 < plafond and plafond <= 1`. Java n'a pas cette écriture. Elle rejette un plafond écrit en pourcentage (`50` au lieu de `0.50`) et un plafond de 1,5, qui n'a pas de sens.

**Le calcul.** `(mensualites_existantes + nouvelle_mensualite) / revenu_mensuel` : on additionne **avant** de diviser. Les parenthèses sont indispensables, sinon Python diviserait seulement la nouvelle mensualité.

**Le verdict.** `ratio <= plafond` : inférieur **ou égal**. Un client à 50 % pile est recevable, comme le dit la règle (« plafonné à 50 % »). Le test le vérifie avec (10 000 + 10 000) / 40 000 = 0,5, qui tombe juste en flottants, puisque 0,5 est une puissance de 2.

**Vérification à la main.** C-1 : (6 000 + 5 558,32) / 40 000 = 11 558,32 / 40 000 = 0,288958 ≤ 0,50, recevable. C-2, retraité : (7 000 + 5 558,32) / 40 000 = 12 558,32 / 40 000 = 0,313958 > 0,30, non recevable.

**Le piège des flottants.** 11 558,32 / 40 000 ne tombe pas juste en binaire : Python rend 0.288958 à quelques 10⁻¹⁷ près. C'est pourquoi le test compare avec `assertAlmostEqual(..., places=6)` et non avec `assertEqual`. Les seules comparaisons exactes du module portent sur des valeurs exactes en binaire, comme 0,5.

**Les tests qui passent maintenant.**

```text
python -m unittest -v tests.test_03_metier.TestCredit
```

Les six tests de `TestCredit` passent : les trois de la mensualité (étape 2) et `test_ratio_toutes_les_mensualites`, `test_ratio_plafond_retraite`, `test_ratio_entrees_invalides`.

**Ce qu'il faut retenir.** Le ratio CBUAE porte sur **toutes** les mensualités ; le plafond est un paramètre, pas une constante figée dans le calcul ; un ratio égal au plafond est recevable.
