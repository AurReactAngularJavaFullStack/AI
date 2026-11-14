# Étape 7 — Assemblage et démo

> Palier 03, étape 7 sur 7 · Précédent : [Étape 6 — L'IBAN et l'Emirates ID](<06-IBAN-et-Emirates-ID.md>) · Suivant : [Palier 04 — Registre d'outils](<../../../04-Registre-d-Outils/README.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Toutes les pièces sont écrites. Il reste à relire le module de haut en bas comme le lira un collègue, à lancer toute la suite de tests (pas seulement ceux du palier : un module ne doit rien casser autour de lui), puis la démo, et à comparer sa sortie ligne à ligne avec celle du README.

## Bloc 1 — Le plan du module

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fr(x, decimales)`** — C'est le calligraphe de l'étape 1, placé en tête du module parce que toute la démo passe par lui : il reçoit un montant et un nombre de décimales, 2 par défaut, le formate à l'anglaise, change les virgules de milliers en espaces fines puis le point en virgule, et renvoie la chaîne obtenue sans jamais lever. C'est grâce à lui que la démo affiche « 5 558,32 AED », « 55 000,00 AED » ou « 28,90 % » plutôt que la notation anglaise brute.

**`mensualite(principal, taux_annuel, n_mois)`** — C'est le conseiller de crédit de l'étape 2, inchangé : il reçoit le capital, le taux annuel en fraction et le nombre de mois, lève `ValueError` sur un capital ou une durée qui ne sont pas strictement positifs ou sur un taux négatif, rend P/n quand le taux est nul et la formule de l'annuité sinon, sans arrondi. Au point 1 de la démo, il calcule l'hypothèque de C-1, 1 000 000 AED à 4,5 % sur 300 mois, dont la mensualité affichée vaut 5 558,32 AED.

**`ratio_endettement(mensualites_existantes, nouvelle_mensualite, revenu_mensuel, plafond)`** — C'est l'analyste des risques de l'étape 3, qui pose toutes les mensualités sur la balance : il reçoit les crédits en cours, la nouvelle mensualité, le revenu et le plafond, 0,50 par défaut, vérifie ses trois gardes, puis renvoie le couple (ratio total, ratio inférieur ou égal au plafond). La démo l'appelle sur la mensualité arrondie au centime : 28,90 % et un dossier recevable pour C-1, puis 31,40 % au-dessus des 30 % du retraité C-2, donc refusé.

**`gratuite_fin_de_service(salaire_base_mensuel, annees)`** — C'est le gestionnaire de paie de l'étape 4 : il reçoit le salaire de base et l'ancienneté, refuse un salaire nul ou des années négatives, rend 0 avant un an, puis compte 21 jours par an sur les cinq premières années et 30 jours au-delà, au prorata, avant d'appliquer le plafond de 24 mois de salaire. Au point 3 de la démo, le salarié C-3 à 10 000 AED reçoit 55 000,00 AED après 7 ans, et 240 000,00 AED, le plafond, après 40 ans.

**`tva(montant_ht, taux)`** — C'est le caissier de l'étape 5 : il reçoit un montant hors taxe et un taux, `TAUX_TVA` par défaut, refuse un montant négatif ou un taux hors de [0, 1], et renvoie la TVA seule, sans arrondi, le TTC se calculant à côté. Au point 4 de la démo, la situation de travaux de 120 000 AED hors taxe de l'agence A-3 porte une TVA de 6 000,00 AED, soit un TTC de 126 000,00 AED.

**`aed_vers_usd(montant_aed)`** — C'est le changeur de l'étape 5 dans le sens des dirhams vers les dollars : il reçoit un montant en AED, lève `ValueError` s'il est négatif et renvoie ce montant divisé par la parité fixe de 3,6725, en pleine précision. La démo l'applique à la mensualité arrondie de 5 558,32 AED, ce qui donne 1 513,4976 USD, affichés 1 513,50 USD sur la première ligne du point 1.

**`usd_vers_aed(montant_usd)`** — C'est le même changeur pris dans l'autre sens : il reçoit un montant en USD, refuse un montant négatif et renvoie ce montant multiplié par 3,6725, sans arrondi, de sorte qu'un aller-retour avec `aed_vers_usd` redonne la somme de départ à 10⁻⁶ près. La sortie de la démo ne l'affiche pas, mais le test de conversion le vérifie, et c'est avec la même parité que le palier 11 convertira en dirhams le coût des appels au modèle.

**`iban_ae_valide(iban)`** — C'est le guichetier de l'étape 6, qui contrôle la forme avant la clé : il reçoit un IBAN, retire les espaces et passe en majuscules, rend `False` si la chaîne n'a pas 23 caractères, « AE » en tête et des chiffres ensuite, puis teste le reste modulo 97 de l'entier obtenu après réarrangement et conversion des lettres. Au point 5 de la démo, l'IBAN de clé 07 est jugé valide et celui de clé 08 refusé.

**`emirates_id_format_valide(eid)`** — C'est l'agent d'accueil de l'étape 6, qui ne regarde que le format : il reçoit un numéro, retire tirets et espaces, et renvoie vrai si et seulement s'il reste 15 chiffres commençant par 784, sans contrôle du dernier chiffre et sans jamais lever. Au point 6 de la démo, « 784-1990-1234567-1 » est accepté et « 785-1990-1234567-1 » refusé pour son préfixe.

```python
# [extrait] agent/metier.py
ESPACE_FINE = chr(0x202F)                      # espace fine insécable : séparateur de milliers français
AED_PAR_USD = 3.6725                           # parité fixe du dirham
TAUX_TVA = 0.05
PLAFOND_CBUAE = 0.50
PLAFOND_RETRAITE = 0.30


def fr(x: float, decimales: int = 2) -> str:
    ...


def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    ...


def ratio_endettement(mensualites_existantes: float, nouvelle_mensualite: float, revenu_mensuel: float,
                      plafond: float = PLAFOND_CBUAE) -> tuple[float, bool]:
    ...


def gratuite_fin_de_service(salaire_base_mensuel: float, annees: float) -> float:
    ...


def tva(montant_ht: float, taux: float = TAUX_TVA) -> float:
    ...


def aed_vers_usd(montant_aed: float) -> float:
    ...


def usd_vers_aed(montant_usd: float) -> float:
    ...


def iban_ae_valide(iban: str) -> bool:
    ...


def emirates_id_format_valide(eid: str) -> bool:
    ...
```

Les `...` remplacent les corps écrits aux étapes 1 à 6. Le module se lit dans l'ordre où l'on en a besoin : les constantes, l'affichage, le crédit (mensualité puis ratio, qui prend la mensualité en argument), la fin de service, la TVA et le change, puis les deux contrôles d'identifiants.

**Ce que le module n'importe pas.** Aucun `import` : ni `math` (l'opérateur `**` suffit), ni `re` (les deux contrôles d'identifiants s'en passent), ni rien des paliers 01 et 02. C'est voulu : le domaine ne dépend de rien, et tout le reste de l'agent peut dépendre de lui. En architecture hexagonale, c'est le centre de l'hexagone ; en Spring, ce seraient des classes du package `domain` sans aucune annotation de framework.

**Les écarts avec l'étape 77.** Les fonctions sont celles du code canonique, avec trois ajouts : des gardes qui lèvent `ValueError` dans `ratio_endettement`, `gratuite_fin_de_service` et `tva` (77 ne vérifiait que le revenu) ; les constantes `TAUX_TVA`, `PLAFOND_CBUAE` et `PLAFOND_RETRAITE`, au lieu de valeurs écrites dans les signatures ; et les deux fonctions de change, que 77 écrivait directement dans l'outil de conversion.

## Bloc 2 — Toute la suite de tests

Depuis `projet/` :

```text
python -m unittest -v
```

La fin de la sortie doit être :

```text
----------------------------------------------------------------------
Ran 46 tests in 0.013s

OK
```

46 tests : 32 pour les paliers 01 et 02, que ton module ne doit pas casser, et les 14 du palier 03. La durée varie d'une machine à l'autre. Si un test du palier 03 échoue encore, relance-le seul avec la commande de l'étape qui le concerne : le message d'`assertAlmostEqual` donne la valeur obtenue et la valeur attendue, et l'écart dit presque toujours quel bord est faux.

## Bloc 3 — La démo

```text
python demo.py
```

```text
Palier 03 — dossiers des clients C-1 à C-4 (montants en AED, parité 3,6725 AED pour 1 USD)
1. C-1, hypothèque de 1 000 000 AED à 4,5 % sur 300 mois : mensualité 5 558,32 AED = 1 513,50 USD
   endettement (6 000 + 5 558,32) / 40 000 = 28,90 % → recevable : True
2. C-2, retraité, 7 000 AED de crédits en cours : 31,40 % > 30 % → recevable : False
3. C-3, salaire de base 10 000 AED, 7 ans : fin de service 55 000,00 AED
   même salaire, 40 ans : plafonnée à 24 mois, 240 000,00 AED
4. Agence A-3, situation de travaux 120 000 AED HT : TVA 6 000,00 AED, TTC 126 000,00 AED
5. IBAN AE07 0331 2345 6789 0123 456 : clé mod 97 valide = True
5. IBAN AE08 0331 2345 6789 0123 456 : clé mod 97 valide = False
6. Emirates ID 784-1990-1234567-1 : format valide = True
6. Emirates ID 785-1990-1234567-1 : format valide = False
OK — palier 03 terminé.
```

Chaque point de la sortie vient d'une fonction que tu as écrite.

- Point 1, première ligne : `mensualite(1_000_000, 0.045, 300)` affichée par `fr`, puis `aed_vers_usd` appliquée à la mensualité **arrondie** au centime, 5 558,32 AED, ce qui donne 1 513,4976 USD, affiché 1 513,50.
- Point 1, seconde ligne : `ratio_endettement(6_000, 5558.32, 40_000)`, multiplié par 100 pour l'affichage : 28,90 %.
- Point 2 : le même calcul avec `plafond=PLAFOND_RETRAITE` et 7 000 AED de crédits : 31,40 % et `False`.
- Point 3 : `gratuite_fin_de_service` pour 7 ans (55 000) et pour 40 ans (plafond de 240 000).
- Point 4 : `tva(120_000)` donne 6 000, et le TTC 126 000.
- Points 5 et 6 : les deux contrôles d'identifiants, chacun sur une valeur valide et une valeur fausse.

La démo arrondit avant d'appeler `ratio_endettement` (`round(m, 2)`), parce que c'est le montant au centime que le client paiera et que le conseiller verra ; c'est la seule décision d'arrondi, et elle est prise par l'appelant, pas par le domaine.

## Ce que tu as appris

- Le modèle ne calcule pas : chaque nombre de l'agent viendra d'une fonction pure, testée au centime.
- Une constante par règle réglementaire, écrite une fois.
- Une garde au début de chaque calcul, qui lève `ValueError` avec un message qui dit la règle ; un contrôle d'identifiant, lui, rend `False`.
- Devant chaque division, chercher le dénominateur nul (le taux nul de la mensualité) et le traiter par sa limite.
- Une règle juridique se traduit phrase par phrase ; les tranches et les plafonds s'écrivent avec `min` et `max`.
- Aucun arrondi dans le domaine : on arrondit une seule fois, à l'affichage ou dans l'outil.
- Le mod 97 se calcule avec `int(c, 36)` et un grand entier en Python, ou chiffre par chiffre (Horner) sur papier et dans un langage aux entiers bornés.

## La suite : le palier 04

Ces fonctions ne sont pas encore des outils : le modèle ne peut pas les appeler. Au [palier 04 — Registre d'outils](<../../../04-Registre-d-Outils/README.md>), tu les enveloppes chacune dans un outil qui a un nom public, une description pour le modèle et un schéma JSON, tu construis la porte qui valide les arguments avant d'appeler la fonction, et tu écris `executer_appel`, qui transforme un bloc `tool_use` du modèle en un `tool_result`, succès ou erreur. La mensualité que tu viens d'écrire deviendra `{"mensualite_aed": 5558.32}`.
