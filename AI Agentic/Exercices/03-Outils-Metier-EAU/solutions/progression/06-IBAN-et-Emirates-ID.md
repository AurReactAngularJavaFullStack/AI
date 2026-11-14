# Étape 6 — L'IBAN et l'Emirates ID

> Palier 03, étape 6 sur 7 · Précédent : [Étape 5 — La TVA et le change](<05-TVA-et-change.md>) · Suivant : [Étape 7 — Assemblage et démo](<07-Assemblage-et-demo.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Ces deux fonctions ne calculent pas un montant : elles répondent oui ou non. Une chaîne mal formée est donc une réponse normale (`False`), pas une erreur du programme : pas de `ValueError` ici, contrairement au reste du module. C'est le même choix que `validate` au palier 02, qui rend une liste d'écarts au lieu de lever.

Pour l'IBAN, écris l'algorithme du README en quatre lignes de commentaires avant tout code, puis remplis chaque ligne :

1. normaliser : retirer les espaces, passer en majuscules ;
2. contrôler la forme : 23 caractères, « AE », 21 chiffres ; sinon `False` tout de suite ;
3. réarranger : les 4 premiers caractères passent à la fin ;
4. convertir les lettres en nombres, lire le tout comme un entier, tester le reste modulo 97.

Le point délicat est l'étape 4 : comment transformer « A » en 10 et « E » en 14 sans écrire un dictionnaire de 26 lettres ? Python le fait déjà.

```text
>>> int("7", 36), int("A", 36), int("E", 36), int("Z", 36)
(7, 10, 14, 35)
```

`int(texte, base)` lit un texte écrit dans une base de 2 à 36. En base 36, les « chiffres » sont 0 à 9 puis A à Z, et la valeur de A est 10, celle de E est 14, celle de Z est 35 : exactement la table de conversion de la norme ISO 13616. En Java, `Character.getNumericValue('A')` rend aussi 10.

## Bloc 1 — Oublier de convertir les lettres

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`iban_ae_valide(iban)`** — Dans ce brouillon, la fonction est un guichetier qui saute le contrôle visuel et tente directement le calcul de la clé : elle reçoit l'IBAN, retire les espaces et passe en majuscules, déplace les quatre premiers caractères à la fin, puis demande à `int` de lire le tout comme un nombre décimal et renvoie le test du reste modulo 97 égal à 1. Comme les lettres « AE » restent dans la chaîne, `int` lève `ValueError` sur « 0331234567890123456AE07 » au lieu de répondre, et, faute de garde de forme, un IBAN « FR07… » ou de 22 caractères irait jusqu'au calcul.

```python
# [extrait] brouillon
def iban_ae_valide(iban: str) -> bool:
    s = iban.replace(" ", "").upper()
    return int(s[4:] + s[:4]) % 97 == 1
```

Ce brouillon réarrange bien l'IBAN, mais il passe directement « 0331234567890123456AE07 » à `int` :

```text
>>> iban_ae_valide("AE07 0331 2345 6789 0123 456")
Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 10: '0331234567890123456AE07'
```

Il plante au lieu de répondre, et il n'a aucune garde de forme : « FR07… » ou un IBAN de 22 caractères iraient jusqu'au calcul. Les deux défauts se corrigent ensemble.

## Bloc 2 — L'IBAN, version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`iban_ae_valide(iban)`** — C'est la même fonction, devenue le guichetier qui regarde d'abord la forme du document avant de vérifier son sceau : elle reçoit l'IBAN, le normalise, et renvoie `False` sans calcul si la chaîne n'a pas 23 caractères, ne commence pas par « AE » ou ne contient pas que des chiffres après ces deux lettres. Sinon, elle place les quatre premiers caractères à la fin, remplace chaque caractère par sa valeur en base 36, A devenant 10 et E 14, colle ces morceaux en un entier de 25 chiffres et renvoie le test de son reste modulo 97 égal à 1. L'IBAN « AE07 0331 2345 6789 0123 456 » est accepté, la clé 08 donne un reste de 2 et un refus ; seul un chiffre exotique comme « ² », qui passe `isdigit`, peut encore la faire lever, ce que règle le défi 3.

```python
# [extrait] agent/metier.py
def iban_ae_valide(iban: str) -> bool:
    """IBAN émirien : 23 caractères, « AE », puis 21 chiffres ; contrôle ISO 13616 mod 97 = 1.

    On place les 4 premiers caractères à la fin, on remplace A par 10 et E par 14, et le grand nombre
    obtenu doit valoir 1 modulo 97.
    Exemple : `iban_ae_valide("AE07 0331 2345 6789 0123 456")` est vrai ; avec la clé 08, il est faux.
    """
    s = iban.replace(" ", "").upper()
    if len(s) != 23 or not s.startswith("AE") or not s[2:].isdigit():
        return False
    reorganise = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in reorganise)) % 97 == 1
```

**Normaliser.** `iban.replace(" ", "")` retire les espaces de l'affichage par groupes de 4, et `.upper()` accepte un IBAN saisi en minuscules : « ae070331234567890123456 » est le même compte. Les chaînes Python sont immuables : chaque méthode rend une nouvelle chaîne, comme en Java, d'où l'enchaînement.

**La garde de forme.** Trois conditions reliées par `or`, évaluées de gauche à droite et en court-circuit, comme `||` en Java : dès qu'une condition est vraie, on rend `False` sans regarder les suivantes. `len(s) != 23` élimine les longueurs fausses ; `s.startswith("AE")` exige le code pays ; `s[2:].isdigit()` exige que tout ce qui suit « AE » (la clé et le BBAN) soit fait de chiffres. `s[2:]` est une tranche : la chaîne à partir de l'indice 2, l'équivalent de `s.substring(2)`.

**Réarranger.** `s[4:] + s[:4]` : tout sauf les 4 premiers caractères, puis les 4 premiers. « AE070331234567890123456 » devient « 0331234567890123456AE07 ».

**Convertir et tester**, de l'intérieur vers l'extérieur.

1. `int(c, 36)` pour chaque caractère `c` : 0 à 9 restent eux-mêmes, A devient 10, E devient 14.
2. `str(...)` réécrit chaque valeur en texte : 10 devient « 10 », sur deux caractères.
3. `"".join(... for c in reorganise)` colle tous ces morceaux : « 0331234567890123456101407 ». La parenthèse contient une expression génératrice, l'équivalent d'un `stream().map(...).collect(Collectors.joining())`.
4. `int(...)` lit ces 25 chiffres comme un seul entier. Python n'a pas de limite de taille pour ses entiers ; en Java, il faudrait un `BigInteger`, car un `long` s'arrête à 19 chiffres.
5. `% 97 == 1` : le test de la norme.

**Le calcul chiffre par chiffre.** C'est ce que tu fais sur papier, et ce qu'on coderait dans un langage aux entiers bornés : on ne garde que le reste à chaque chiffre (méthode de Horner, justifiée dans le README).

```text
>>> reste = 0
>>> for chiffre in "0331234567890123456101407":
...     reste = (10 * reste + int(chiffre)) % 97
...
>>> reste
1
```

Le tableau du README déroule ces 25 lignes. Avec la clé « 08 », le dernier chiffre devient 8, et la dernière ligne donne 10 × 77 + 8 = 778, dont le reste vaut 2 : l'IBAN est refusé.

**Le piège de `isdigit`.** `str.isdigit()` ne se limite pas aux chiffres 0 à 9 :

```text
>>> "²".isdigit(), "٣".isdigit()
(True, True)
>>> iban_ae_valide("AE07²331234567890123456")
Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 36: '²'
```

L'exposant « ² » passe la garde, puis `int("²", 36)` le refuse. Les chiffres arabes-indiens, courants aux Émirats, passent la garde et sont même convertis par `int`. La fonction reste celle du parcours, recopiée de l'étape 77 ; le défi 3 du README la rend étanche en ajoutant `s.isascii()` à la garde. Retiens le réflexe : en Python comme en Java (`Character.isDigit('٣')` vaut aussi `true`), « est un chiffre » veut dire « est un chiffre dans une écriture quelconque », pas « est l'un des caractères 0 à 9 ».

## Bloc 3 — L'Emirates ID

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`emirates_id_format_valide(eid)`** — Cette fonction est l'agent d'accueil qui jette un œil à la carte d'identité sans appeler le registre national : elle reçoit une chaîne, en retire les tirets puis les espaces, et renvoie directement la valeur de trois conditions reliées par `and`, exactement 15 caractères, tous des chiffres, et le préfixe 784. Elle ne lève jamais d'exception et ne vérifie pas le chiffre de contrôle final, comme son nom l'annonce : « 784-1990-1234567-1 » et sa forme compacte passent, « 785-1990-1234567-1 » échoue par le préfixe et « 784-1990-123456-1 » par sa longueur de 14 chiffres, et un saut de ligne final suffit à la faire répondre `False`.

```python
# [extrait] agent/metier.py
def emirates_id_format_valide(eid: str) -> bool:
    """Format seulement : 15 chiffres commençant par 784 (affiché 784-AAAA-NNNNNNN-C), sans contrôle de clé.

    Exemple : "784-1990-1234567-1" est valide ; "785-1990-1234567-1" et "784-1990-123456-1" ne le sont pas.
    """
    chiffres = eid.replace("-", "").replace(" ", "")
    return len(chiffres) == 15 and chiffres.isdigit() and chiffres.startswith("784")
```

**Normaliser.** On retire les tirets et les espaces : la fonction accepte la forme affichée « 784-1990-1234567-1 » comme la forme compacte « 784199012345671 ».

**Le test.** Trois conditions reliées par `and`, en court-circuit : 15 caractères, tous des chiffres, et le préfixe 784, l'indicatif numérique ISO 3166 des Émirats. La fonction rend directement la valeur booléenne de l'expression, sans `if ... return True else return False`.

**Pourquoi pas une regex ?** Le palier 02 a le motif `MOTIF_EMIRATES_ID`, qui exige les tirets aux bonnes places. Cette fonction est plus tolérante sur la présentation, et plus stricte sur un point : en Python, le `$` d'une regex accepte un saut de ligne final, si bien que « 784-1990-1234567-1 » suivi d'un retour à la ligne passe le motif ; ici, le retour à la ligne n'est pas un chiffre, et la fonction rend `False` (étape 8 du cours).

**Ce que la fonction ne fait pas.** Elle ne vérifie pas le dernier chiffre, la clé : son nom le dit (`format_valide`), et la docstring aussi. Un nom honnête évite qu'un collègue croie le numéro authentifié.

**Vérification à la main.** « 784-1990-1234567-1 » donne 3 + 4 + 7 + 1 = 15 chiffres commençant par 784 : vrai. « 785-… » : faux par le préfixe. « 784-1990-123456-1 » : 14 chiffres, faux par la longueur.

**Les tests qui passent maintenant.**

```text
python -m unittest -v tests.test_03_metier.TestIdentifiants
```

`test_iban` (clé 07 valide, minuscules acceptées, clé 08 refusée, 22 caractères refusés, préfixe FR refusé) et `test_emirates_id` (deux formes valides, mauvais préfixe, 14 chiffres).

**Ce qu'il faut retenir.** Un contrôle d'identifiant rend un booléen et ne lève pas ; la forme d'abord, le calcul ensuite ; `int(c, 36)` convertit les lettres de l'IBAN ; les entiers Python n'ont pas de limite, mais le calcul de Horner reste la méthode de la feuille blanche.
