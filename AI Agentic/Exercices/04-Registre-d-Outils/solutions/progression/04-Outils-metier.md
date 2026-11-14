# Étape 4 — Les cinq outils métier

> Palier 04, étape 4 sur 7 · Précédent : [Étape 3 — La porte et les appelables](<03-Porte-et-appelables.md>) · Suivant : [Étape 5 — Les définitions pour l'API](<05-Definitions-API.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Le registre sait ranger et garder des outils ; il n'en contient encore aucun. Chaque outil métier est une fonction du palier 03 vue par le modèle. Pour chacun, trois questions, dans cet ordre :

1. **Quel contrat le modèle voit-il ?** Un nom court et stable, une description qui dit l'unité, des noms d'arguments sans ambiguïté.
2. **Quelles bornes le schéma impose-t-il ?** Les domaines du palier 03 (principal > 0, taux ≥ 0…), plus des bornes de bon sens qui attrapent les erreurs typiques du modèle (un taux écrit en pourcentage).
3. **Que rend l'outil ?** Un dictionnaire JSON aux clés explicites, unité comprise (`mensualite_aed`), arrondi au centime : c'est ici, et seulement ici, qu'on arrondit.

Dernière question : où écrire ces cinq outils ? Pas au niveau du module, où ils s'enregistreraient dans un registre global au moment de l'import. Dans une fonction qui reçoit le registre, `enregistrer_outils_metier(registre)` : chaque agent, chaque test, choisit son registre et y ajoute les outils quand il le décide.

## Bloc 1 — La fonction d'enregistrement et l'outil de mensualité

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`enregistrer_outils_metier(registre)`** — Cette fonction est la cérémonie d'embauche au cours de laquelle chaque calculateur du palier 03 reçoit son badge et sa fiche de poste : elle reçoit le registre choisi par l'appelant et, dans ce premier extrait, y inscrit par le décorateur `@registre.outil(...)` l'outil « mensualite », décrit comme la mensualité d'un prêt amortissable en AED, avec un schéma construit par `objet` qui exige un principal strictement positif, un taux annuel entre 0 et 0,3 et un nombre de mois entier entre 1 et 300. Comme le décorateur s'exécute à chaque appel, l'appeler deux fois sur le même registre lèverait `ValueError` ; la suite de la fonction ajoutera les quatre autres outils.

**`outil_mensualite(principal, taux_annuel, n_mois)`** — Cette fonction locale vit dans `enregistrer_outils_metier` et n'est connue que de la table du registre, comme un employé qu'on n'appelle que par le standard : elle reçoit les trois arguments déjà validés par la porte, appelle `mensualite` du palier 03, arrondit le résultat au centime et le renvoie dans un dictionnaire à la clé explicite `mensualite_aed`. Pour 1 000 000 AED à 4,5 % sur 300 mois, le modèle lira donc 5558,32, sans jamais pouvoir croire qu'il s'agit de dollars.

```python
# [extrait] agent/outils.py
def enregistrer_outils_metier(registre: Registre) -> Registre:
    ...
    @registre.outil("mensualite", "Mensualité d'un prêt amortissable, en AED.", objet({
        "principal": {"type": "number", "exclusiveMinimum": 0},
        "taux_annuel": {"type": "number", "minimum": 0, "maximum": 0.3},
        "n_mois": {"type": "integer", "minimum": 1, "maximum": 300}}))
    def outil_mensualite(principal: float, taux_annuel: float, n_mois: int) -> dict:
        return {"mensualite_aed": round(mensualite(principal, taux_annuel, n_mois), 2)}
```

**Un décorateur à l'intérieur d'une fonction.** `@registre.outil(...)` s'exécute à chaque appel de `enregistrer_outils_metier`, sur le registre reçu en paramètre. La fonction `outil_mensualite` est locale : personne ne l'appellera par son nom, seule la table du registre la garde. Appeler deux fois `enregistrer_outils_metier` sur le même registre lèverait `ValueError` (« outil déjà enregistré : mensualite ») : c'est voulu.

**Le contrat.** Le nom public est « mensualite », sans accent ni espace, celui que le modèle écrira. La description dit ce que fait l'outil et dans quelle unité il répond. Le schéma est construit par `objet` du palier 02 : les trois champs sont obligatoires et aucun autre n'est accepté.

**Les bornes, une par une.**

- `principal` : `"exclusiveMinimum": 0`, c'est-à-dire strictement positif, comme la garde de `mensualite`.
- `taux_annuel` : entre 0 et 0,3. Le domaine accepte n'importe quel taux positif ; l'outil, lui, refuse au-delà de 30 % par an. Cette borne (illustrative) n'est pas une règle bancaire : elle attrape l'erreur la plus probable du modèle, écrire 4.5 pour 4,5 %. Le message `$.taux_annuel : 4.5 > maximum 0.3` lui dit exactement quoi corriger.
- `n_mois` : un **entier** entre 1 et 300, soit 25 ans au plus, la durée de l'hypothèque de l'étape 77. Le type `integer` refuse 300.0 aussi bien que « 300 ».

**Pourquoi garder les gardes du palier 03 ?** Le schéma et la garde du domaine se recouvrent, et c'est voulu. Le schéma donne au modèle un message précis, avec le chemin du champ. La garde protège tous les autres appelants de `mensualite`, qui ne passent pas par la porte. Deux protections, deux publics.

**La sortie.** `round(..., 2)` arrondit au centime, une seule fois, au bout du calcul : 5558.324779… devient 5558.32. La clé `mensualite_aed` porte l'unité : quand le modèle relira `{"mensualite_aed": 5558.32}`, il ne pourra pas croire à des dollars.

**Le piège de `round`.** Python arrondit « au pair » les cas exactement à mi-chemin (`round(2.5)` vaut 2, `round(3.5)` vaut 4), et la représentation binaire des décimaux brouille les cas qui ont l'air à mi-chemin : `round(2.675, 2)` vaut 2.67, parce que 2,675 est stocké comme 2,67499999…. Pour des écritures comptables, on utiliserait `decimal.Decimal` avec `ROUND_HALF_UP`, l'équivalent de `BigDecimal.setScale(2, RoundingMode.HALF_UP)` en Java. L'agent suit ici les arrondis de l'étape 77, que les tests reprennent.

## Bloc 2 — Le ratio et la conversion

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`enregistrer_outils_metier(registre)`** — C'est la même fonction que dans l'extrait précédent, dont on lit ici la suite de la cérémonie : sur le même registre, elle inscrit deux nouveaux outils, « ratio_endettement », qui reçoit les mensualités existantes, la nouvelle mensualité et le revenu avec des bornes positives, et « convertir_aed_usd », qui reçoit un montant en AED positif ou nul. Les descriptions disent au modèle la règle de la CBUAE et la parité fixe de 3,6725 AED pour 1 USD, mais aucun schéma ne lui laisse choisir le plafond.

**`outil_ratio(existantes, nouvelle, revenu)`** — Cette fonction locale vit dans `enregistrer_outils_metier` et joue l'interprète entre les noms courts du contrat de l'étape 77 et les paramètres plus longs du domaine : elle reçoit les trois montants validés, appelle `ratio_endettement` avec le plafond par défaut de 50 %, déballe le couple rendu et renvoie un dictionnaire où le ratio est arrondi à quatre décimales et le verdict passe tel quel. Pour 6 000, 5 558,32 et 40 000, le modèle lit un ratio de 0,289 et un dossier recevable, sans avoir eu la possibilité de relever lui-même le plafond.

**`outil_conversion(montant_aed)`** — Cette autre fonction locale de `enregistrer_outils_metier` est le changeur de l'agent : elle reçoit un montant en AED déjà validé, le divise directement par la constante `AED_PAR_USD`, comme dans l'étape 77, arrondit au centime et renvoie un dictionnaire de clé `montant_usd`. La mensualité de 5 558,32 AED devient ainsi 1 513,5 USD ; passer par `aed_vers_usd` donnerait le même nombre, le schéma ayant déjà écarté les montants négatifs que cette fonction refuserait.

```python
# [extrait] agent/outils.py
def enregistrer_outils_metier(registre: Registre) -> Registre:
    ...
    @registre.outil("ratio_endettement",
                    "Endettement total CBUAE : (mensualités existantes + nouvelle) / revenu, plafond 50 %.",
                    objet({"existantes": {"type": "number", "minimum": 0},
                           "nouvelle": {"type": "number", "exclusiveMinimum": 0},
                           "revenu": {"type": "number", "exclusiveMinimum": 0}}))
    def outil_ratio(existantes: float, nouvelle: float, revenu: float) -> dict:
        ratio, recevable = ratio_endettement(existantes, nouvelle, revenu)
        return {"ratio": round(ratio, 4), "recevable": recevable}

    @registre.outil("convertir_aed_usd",
                    "Convertit un montant en AED vers l'USD, à la parité fixe de 3,6725 AED pour 1 USD.",
                    objet({"montant_aed": {"type": "number", "minimum": 0}}))
    def outil_conversion(montant_aed: float) -> dict:
        return {"montant_usd": round(montant_aed / AED_PAR_USD, 2)}
```

**Des noms d'arguments pour le modèle.** L'outil de ratio prend `existantes`, `nouvelle` et `revenu`, plus courts que les paramètres du domaine (`mensualites_existantes`, `nouvelle_mensualite`, `revenu_mensuel`) : c'est le contrat de l'étape 77, que le faux modèle des paliers suivants respectera. La fonction de l'outil fait la traduction, en passant les valeurs dans l'ordre.

**Ce que l'outil ne laisse pas choisir.** Le plafond n'est pas un argument : l'outil appelle `ratio_endettement` avec le plafond par défaut de 50 %. Si le modèle pouvait passer `plafond`, il pourrait aussi le relever pour rendre un dossier recevable. Le cas du retraité passe par un autre chemin (le conseiller, ou un outil dédié), jamais par un paramètre que le modèle remplit.

**La borne de `nouvelle`.** `"exclusiveMinimum": 0` : une nouvelle mensualité nulle n'a pas de sens pour une demande de prêt, même si le domaine l'accepte. Les `existantes`, elles, peuvent valoir 0 (`"minimum": 0`) : un premier crédit.

**Le déballage du couple.** `ratio, recevable = ratio_endettement(...)` déballe le tuple rendu par le domaine, et la sortie l'expose sous deux clés nommées. Le ratio est arrondi à 4 décimales : 0,288958 devient 0,2890, que Python affiche `0.289`. Le booléen passe tel quel et deviendra `true` en JSON.

**La conversion.** `montant_aed / AED_PAR_USD`, arrondi au centime : 5 558,32 / 3,6725 = 1 513,4976, soit `1513.5`. L'outil utilise la constante directement, comme dans 77 ; appeler `aed_vers_usd(montant_aed)` donnerait le même nombre, et le schéma (`"minimum": 0`) a déjà écarté les montants négatifs que cette fonction refuserait.

## Bloc 3 — La fin de service, la TVA, et le registre rendu

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`enregistrer_outils_metier(registre)`** — C'est toujours la même fonction, dont cet extrait montre la fin de la cérémonie : elle inscrit les deux derniers outils, « gratuite_fin_de_service », dont le schéma exige un salaire de base strictement positif et une ancienneté réelle entre 0 et 60 ans, puis « tva », qui reçoit un montant hors taxe positif ou nul. Elle renvoie enfin le registre reçu, complété de ses cinq outils dans l'ordre, ce qui permet d'écrire en une ligne `registre = enregistrer_outils_metier(Registre())`, comme les tests et la démo.

**`outil_gratuite(salaire_base_mensuel, annees)`** — Cette fonction locale de `enregistrer_outils_metier` est le gestionnaire de paie que le modèle peut consulter : elle reçoit le salaire de base et l'ancienneté validés par la porte, appelle `gratuite_fin_de_service` du palier 03, arrondit l'indemnité au centime et la renvoie sous la clé `indemnite_aed`. Pour 10 000 AED et 7 ans, le modèle lit 55 000 ; une ancienneté de plus de 60 ans aura été refusée en amont comme une erreur de lecture, plutôt que masquée par le plafond de 24 mois.

**`outil_tva(montant_ht)`** — Cette dernière fonction locale de `enregistrer_outils_metier` est le caissier qui rend au modèle les deux chiffres dont il a besoin : elle reçoit un montant hors taxe validé, calcule la TVA exacte avec `tva`, et renvoie un dictionnaire où la TVA est arrondie au centime et où le TTC, montant hors taxe plus TVA exacte, n'est arrondi qu'une fois à la fin. Le taux n'est pas un argument, si bien que le modèle ne peut pas décider qu'une facture est au taux zéro ; pour 12 000 AED, il lit 600 de TVA et 12 600 TTC.

```python
# [extrait] agent/outils.py
def enregistrer_outils_metier(registre: Registre) -> Registre:
    ...
    @registre.outil("gratuite_fin_de_service",
                    "Indemnité de fin de service (décret-loi fédéral 33/2021, secteur privé), en AED.",
                    objet({"salaire_base_mensuel": {"type": "number", "exclusiveMinimum": 0},
                           "annees": {"type": "number", "minimum": 0, "maximum": 60}}))
    def outil_gratuite(salaire_base_mensuel: float, annees: float) -> dict:
        return {"indemnite_aed": round(gratuite_fin_de_service(salaire_base_mensuel, annees), 2)}

    @registre.outil("tva", "TVA de 5 % et montant TTC, en AED.", objet({"montant_ht": {"type": "number", "minimum": 0}}))
    def outil_tva(montant_ht: float) -> dict:
        return {"tva_aed": round(tva(montant_ht), 2), "ttc_aed": round(montant_ht + tva(montant_ht), 2)}

    return registre
```

**La fin de service.** `annees` est un `number`, pas un `integer` : l'ancienneté se compte au prorata (3,5 ans). La borne de 60 ans est une borne de vraisemblance (illustrative) : une carrière plus longue trahit une erreur de lecture, que la porte renvoie au modèle au lieu de laisser le plafond de 24 mois la masquer.

**La TVA et le TTC.** L'outil rend les deux, parce que c'est ce dont le modèle a besoin pour répondre ; le domaine, lui, ne rendait que la TVA. Le TTC se calcule à partir de la TVA **exacte**, `montant_ht + tva(montant_ht)`, puis s'arrondit une fois : on n'additionne pas deux nombres déjà arrondis. Le taux n'est pas un argument : le modèle ne peut pas décider qu'une facture est au taux zéro.

**`return registre`.** La fonction rend le registre qu'elle a reçu, complété. Cela permet d'écrire `registre = enregistrer_outils_metier(Registre())` en une ligne, comme dans les tests et la démo. C'est le style *fluent* d'un builder Java, sans copie : c'est le même objet.

**Vérification à la main.** `tva(12_000)` donne 600, et 12 000 + 600 = 12 600 : `{"tva_aed": 600.0, "ttc_aed": 12600.0}`, égal à `{"tva_aed": 600, "ttc_aed": 12_600}` puisque `600.0 == 600` en Python. `gratuite_fin_de_service(10_000, 7)` donne 55 000 : `{"indemnite_aed": 55000.0}`.

**Les tests qui passent maintenant.** La plupart des tests du palier reposent sur `registre_metier()`, c'est-à-dire `enregistrer_outils_metier(Registre())` :

```text
python -m unittest -v tests.test_04_outils.TestPorte tests.test_04_outils.TestOutilsMetier tests.test_04_outils.TestRegistre.test_cinq_outils_metier tests.test_04_outils.TestRegistre.test_nom_deja_pris_ou_vide
```

`test_cinq_outils_metier` vérifie les 5 noms dans l'ordre ; `test_nom_deja_pris_ou_vide` refuse un second « tva » et un nom vide ; `TestPorte` appelle la mensualité par sa porte (5 558,32) et vérifie qu'un outil inconnu est refusé ; `test_sorties_arrondies_comme_dans_77` vérifie les quatre autres sorties.

**Ce qu'il faut retenir.** Un outil, c'est une fonction du domaine vue par le modèle : un nom et des arguments courts, des bornes qui attrapent ses erreurs typiques, une sortie aux clés explicites et arrondie une seule fois. Ce que le modèle ne doit pas choisir (un plafond, un taux de TVA) n'est pas un argument.
