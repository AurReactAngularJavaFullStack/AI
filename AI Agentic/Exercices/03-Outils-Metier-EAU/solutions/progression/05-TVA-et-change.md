# Étape 5 — La TVA et le change

> Palier 03, étape 5 sur 7 · Précédent : [Étape 4 — La fin de service](<04-Fin-de-service.md>) · Suivant : [Étape 6 — L'IBAN et l'Emirates ID](<06-IBAN-et-Emirates-ID.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Trois fonctions d'une ligne de calcul chacune : une multiplication pour la TVA, une division et une multiplication pour le change. Le travail n'est pas dans le calcul, il est dans trois décisions :

1. que rend `tva` : la TVA seule, ou le TTC ? La spécification dit la TVA seule ; le TTC se calcule à côté (`montant_ht + tva(montant_ht)`), et l'outil du palier 04 rendra les deux ;
2. quelles entrées refuser : un montant négatif, et un taux hors de [0, 1] ;
3. faut-il arrondir ? Non, et l'on va voir pourquoi sur un aller-retour de change.

## Bloc 1 — La TVA

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tva(montant_ht, taux)`** — Cette fonction est le caissier qui sépare, sur chaque ticket, la part due à l'État : elle reçoit un montant hors taxe et un taux, `TAUX_TVA` soit 0,05 par défaut, lève `ValueError` si le montant est négatif ou si le taux sort de [0, 1], ce qui écarte un 5 % écrit par erreur sous la forme 5, puis renvoie le produit du montant par le taux, sans arrondi. Elle rend la TVA seule, pas le TTC : 600 AED pour 12 000 AED hors taxe, 0 avec un taux nul, et `4.995000000000001` pour 99,90 AED, d'où la comparaison approchée du test et l'arrondi au fils laissé à l'outil du palier 04.

```python
# [extrait] agent/metier.py
def tva(montant_ht: float, taux: float = TAUX_TVA) -> float:
    """TVA standard des EAU : 5 % (loyer résidentiel exonéré ; première livraison d'un bien
    résidentiel au taux zéro). Exemple : `tva(12_000)` = 600 AED, soit 12 600 AED TTC.
    """
    if montant_ht < 0 or not 0 <= taux <= 1:
        raise ValueError("montant >= 0 et taux dans [0, 1]")
    return montant_ht * taux
```

**La signature.** `taux: float = TAUX_TVA` : 5 % par défaut, mais le taux reste un paramètre. Le taux zéro existe aux Émirats (première livraison d'un bien résidentiel, certaines exportations), et un appelant doit pouvoir le passer explicitement : `tva(12_000, taux=0.0)` vaut 0. L'exonération du loyer résidentiel, elle, n'est pas un taux : elle sort du champ de la TVA, et c'est à l'appelant de ne pas appeler la fonction.

**La garde.** Une seule ligne, deux conditions. `not 0 <= taux <= 1` est la comparaison chaînée vue à l'étape 3, cette fois avec `<=` des deux côtés : un taux de 0 est permis, un taux de 1 aussi (borne théorique), un taux de 5 (5 % écrit en pourcentage) est refusé. Un montant HT nul est permis et donne 0 ; un montant négatif (un avoir) n'est pas une facture, et la fonction le refuse plutôt que de rendre une TVA négative.

**Le calcul.** `montant_ht * taux` : 12 000 × 0,05 = 600 AED. En flottants, 0,05 n'est pas exactement représentable en binaire : pour 12 000 AED le produit tombe juste (`600.0`), mais pour 99,90 AED il vaut `4.995000000000001` au lieu de 4,995. Le test compare donc avec `assertAlmostEqual(..., places=9)`, et l'arrondi au fils se fera dans l'outil, avec `round(..., 2)`.

## Bloc 2 — Le change, dans les deux sens

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`aed_vers_usd(montant_aed)`** — Cette fonction est le changeur du souk qui compte combien de paquets de 3,6725 dirhams tiennent dans la somme qu'on lui tend : elle reçoit un montant en AED, lève `ValueError` (« montant >= 0 ») s'il est négatif, accepte zéro, et renvoie ce montant divisé par `AED_PAR_USD`, en pleine précision. La mensualité de 5 558,32 AED devient ainsi environ 1 513,4976 USD ; arrondir ici au centime ferait apparaître un fils de nulle part au retour, ce que la suite du texte montre.

**`usd_vers_aed(montant_usd)`** — Celle-ci est le même changeur pris de l'autre côté du comptoir : elle reçoit un montant en USD, lève la même `ValueError` s'il est négatif, et renvoie ce montant multiplié par 3,6725, sans arrondi, si bien que 0,0384 USD, l'ordre de grandeur du coût d'un appel au modèle que le palier 11 convertira, donne 0,141024 AED à la représentation binaire près. Combinée à `aed_vers_usd`, elle redonne 180 000 AED après un aller-retour, à 10⁻⁶ près.

```python
# [extrait] agent/metier.py
def aed_vers_usd(montant_aed: float) -> float:
    """Conversion à la parité fixe : USD = AED / 3,6725. Exemple : 5 558.32 AED ≈ 1 513.4976 USD."""
    if montant_aed < 0:
        raise ValueError("montant >= 0")
    return montant_aed / AED_PAR_USD


def usd_vers_aed(montant_usd: float) -> float:
    """Conversion à la parité fixe : AED = USD × 3,6725. Exemple : 0.0384 USD = 0.141024 AED."""
    if montant_usd < 0:
        raise ValueError("montant >= 0")
    return montant_usd * AED_PAR_USD
```

**Deux fonctions plutôt qu'une.** On aurait pu écrire `convertir(montant, sens)`. Deux fonctions aux noms explicites évitent le paramètre booléen ou la chaîne « sens » que l'on finit toujours par inverser. En Java, c'est le même conseil : deux méthodes nommées plutôt qu'un `boolean versUsd`.

**Le sens de l'opération.** `AED_PAR_USD` vaut 3,6725 AED pour 1 USD. Pour passer des AED aux USD, on cherche combien de « paquets » de 3,6725 AED tiennent dans le montant : on divise. Pour passer des USD aux AED, on multiplie. Une vérification d'ordre de grandeur suffit à repérer l'inversion : un montant en USD est toujours plus petit que le même montant en AED.

**La garde.** Un montant négatif n'a pas de sens pour une conversion de prix ; on le refuse, comme partout dans le module. Il n'y a pas de garde sur un montant nul : 0 AED vaut 0 USD.

**Pourquoi aucun arrondi ?** Regarde un aller-retour avec un arrondi intermédiaire au centime :

```text
>>> round(5558.32 / 3.6725, 2)
1513.5
>>> round(1513.5 * 3.6725, 2)
5558.33
```

Un fils est apparu de nulle part : sur des milliers d'opérations, les comptes ne retombent plus juste. Sans arrondi, `usd_vers_aed(aed_vers_usd(180_000))` redonne 180 000 AED à 10⁻⁶ près, ce que vérifie le test. Règle générale du module : on calcule en pleine précision, et l'on arrondit **une seule fois**, au moment de présenter ou de renvoyer le résultat au modèle.

**Le piège du nombre de décimales.** `usd_vers_aed(0.0384)` donne 0.14102399999999998 et non 0.141024 : c'est la représentation binaire de 0,0384 qui ressort. Le test compare donc à `places=9`. Ce montant minuscule n'est pas un hasard : c'est l'ordre de grandeur du coût d'un appel au modèle en USD, que le palier 11 convertira en AED avec la même constante.

**Vérification à la main.** 3,6725 × 1 500 = 5 508,75 ; 5 558,32 − 5 508,75 = 49,57 ; 49,57 / 3,6725 = 13,4976 ; donc 5 558,32 AED = 1 513,4976 USD. Et 0,0384 × 3,6725 = 0,141024 AED.

**Les tests qui passent maintenant.**

```text
python -m unittest -v tests.test_03_metier.TestTvaEtChange
```

`test_tva` (600, taux nul, montant négatif) et `test_conversion` (la parité, les deux sens, l'aller-retour, le montant négatif).

**Ce qu'il faut retenir.** Le domaine ne rend que des valeurs exactes, sans arrondi ; une conversion se nomme par son sens ; un taux reste un paramètre, avec la valeur réglementaire par défaut.
