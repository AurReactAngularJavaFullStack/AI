# Étape 1 — Les constantes et l'affichage français

> Palier 03, étape 1 sur 7 · Précédent : [Énoncé du palier 03](<../../README.md>) · Suivant : [Étape 2 — La mensualité](<02-Mensualite.md>) · Retour à l'énoncé : [README](<../../README.md>)

## Comment raisonner

Devant le fichier vide, commence par ce qui ne bouge pas : les chiffres réglementaires. Ils servent à plusieurs fonctions (le plafond de 50 % au ratio, le taux de 5 % à la TVA, la parité au change), et d'autres modules les importeront plus tard (`AED_PAR_USD` au palier 11, `ESPACE_FINE` au palier 10). Les écrire une seule fois, en haut du module, sous un nom en majuscules, c'est garantir qu'un changement de règle tient en une ligne.

Écris ensuite `fr`, la fonction d'affichage. C'est la plus courte du module, elle n'a aucune garde, et pourtant elle contient un piège d'ordre : un bon échauffement. Elle sert à la démo de ce palier et à l'assemblage du palier 12.

## Bloc 1 — Les constantes réglementaires

```python
# [extrait] agent/metier.py
ESPACE_FINE = chr(0x202F)                      # espace fine insécable : séparateur de milliers français
AED_PAR_USD = 3.6725                           # parité fixe du dirham
TAUX_TVA = 0.05
PLAFOND_CBUAE = 0.50
PLAFOND_RETRAITE = 0.30
```

**Ligne 1.** `chr(0x202F)` rend le caractère Unicode de code 202F en hexadécimal, l'espace fine insécable, que la typographie française place entre les milliers. On l'écrit avec `chr` plutôt qu'en collant le caractère entre guillemets : dans un éditeur, une espace fine ressemble à une espace ordinaire, et un relecteur ne verrait pas la différence. `chr(0x202F)` se lit, se recherche et ne se transforme pas en silence au copier-coller.

**Ligne 2.** `AED_PAR_USD = 3.6725` : le dirham est arrimé au dollar à cette parité fixe. C'est un chiffre réel, que l'on peut écrire en dur. Le nom dit le sens de la conversion : il faut 3,6725 AED pour 1 USD, donc on multiplie pour aller vers l'AED et l'on divise pour aller vers l'USD.

**Lignes 3 à 5.** La TVA de 5 %, le plafond d'endettement total de la CBUAE (50 % du revenu) et celui d'un retraité (30 %). Ce sont des fractions, pas des pourcentages : `0.05`, pas `5`. Tout le module calcule en fractions et ne passe en pourcentage qu'à l'affichage.

**Analogie Java.** Ce sont des `public static final double` d'une classe utilitaire. Python n'a pas de `final` : la convention des MAJUSCULES dit « ne pas réaffecter », et c'est l'équipe qui la respecte. Un autre module les lit par `from agent.metier import AED_PAR_USD`, l'équivalent d'un `import static`.

**Le piège.** Recopier `3.6725` dans chaque fonction qui convertit, ou `0.50` dans chaque test d'endettement. Le jour où un plafond change (ou si l'on veut le plafond des retraités), il faut retrouver toutes les copies, et l'on en oublie une.

Aucun test ne porte encore sur ces lignes seules ; `TestTvaEtChange.test_conversion` vérifiera plus tard que `AED_PAR_USD` vaut 3.6725.

## Bloc 2 — `fr`, version naïve

Le format anglais des nombres sait déjà grouper les milliers. Dans une console Python :

```text
>>> f"{5558.32:,.2f}"
'5,558.32'
>>> f"{1_000_000:,.0f}"
'1,000,000'
```

Dans la spécification de format `,.2f`, la virgule demande un séparateur de milliers (toujours une virgule en Python), `.2` demande deux décimales et `f` la notation à virgule fixe. Il reste à échanger les séparateurs : la virgule doit devenir une espace fine et le point une virgule. Le premier réflexe donne ceci :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fr(x, decimales)`** — Dans ce brouillon, la fonction ressemble à un copiste pressé qui change les signes dans le mauvais ordre et efface au passage ce qu'il vient d'écrire : elle reçoit un montant et un nombre de décimales, 2 par défaut, le formate à l'anglaise avec une virgule pour les milliers et un point pour les décimales, remplace d'abord le point par une virgule, puis toutes les virgules par l'espace fine. Elle renvoie donc une chaîne où la partie décimale s'est noyée dans un séparateur : `fr(5558.32)` part de « 5,558.32 » et finit en « 5 558 32 », ce qui montre pourquoi l'ordre des deux remplacements est toute la difficulté de la fonction.

```python
# [extrait] brouillon
def fr(x: float, decimales: int = 2) -> str:
    return f"{x:,.{decimales}f}".replace(".", ",").replace(",", ESPACE_FINE)
```

`fr(5558.32)` part de « 5,558.32 ». Le premier `replace` change le point en virgule : « 5,558,32 ». Le second change **toutes** les virgules en espaces fines, y compris celle qu'on vient de créer : « 5 558 32 ». La partie décimale a disparu dans un séparateur.

## Bloc 3 — `fr`, version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fr(x, decimales)`** — C'est la même fonction que dans le brouillon, tenue cette fois par un copiste qui libère d'abord le signe « , » avant de le réutiliser : elle reçoit le montant et le nombre de décimales, 2 par défaut parce que l'AED se divise en 100 fils, formate le nombre à l'anglaise avec une f-string dont la précision est elle-même un champ, change ensuite les virgules de milliers en espaces fines `ESPACE_FINE`, et seulement après le point décimal en virgule. Elle renvoie la chaîne obtenue, sans jamais lever d'exception : « 5 558,32 » pour 5558,32, « 1 000 000 » pour un million sans décimale, « 28,9 » pour un pourcentage à une décimale, et « 55 000,00 » dans la démo, toujours avec le même nombre de décimales.

```python
# [extrait] agent/metier.py
def fr(x: float, decimales: int = 2) -> str:
    """Affichage français d'un montant : espace fine pour les milliers, virgule décimale.

    Exemple : `fr(5558.32)` vaut « 5 558,32 » et `fr(1_000_000, 0)` vaut « 1 000 000 »
    (le séparateur est l'espace fine insécable U+202F).
    """
    return f"{x:,.{decimales}f}".replace(",", ESPACE_FINE).replace(".", ",")
```

**La signature.** `decimales: int = 2` : deux décimales par défaut, parce que l'AED se divise en 100 fils. On passera `0` pour un montant rond (« 1 000 000 ») et `1` pour un pourcentage (« 28,9 »).

**La docstring.** Elle donne la spécification et un exemple chiffré : c'est ce que tu liras dans six mois, et ce que lira l'équipe. Elle mentionne U+202F, parce que l'espace du rendu n'est pas une espace ordinaire.

**La ligne de calcul**, de gauche à droite.

1. `f"{x:,.{decimales}f}"` : une f-string dont la spécification de format contient elle-même un champ, `{decimales}`. Python remplace d'abord `{decimales}` par sa valeur, puis applique le format obtenu, par exemple `,.2f`. C'est l'équivalent de `String.format("%,." + decimales + "f", x)`, sans la concaténation.
2. `.replace(",", ESPACE_FINE)` : les virgules de milliers deviennent des espaces fines **pendant qu'il n'y a encore aucune virgule décimale**. « 5,558.32 » devient « 5 558.32 ».
3. `.replace(".", ",")` : le seul point restant est le point décimal ; il devient une virgule. « 5 558.32 » devient « 5 558,32 ».

L'ordre est la seule difficulté de la fonction : on libère d'abord le symbole « , », puis on le réutilise.

**Pourquoi pas le module `locale` ?** `locale.setlocale(locale.LC_ALL, "fr_FR")` dépend des locales installées sur la machine : elle échoue sur un serveur Linux minimal et change l'état global du processus. Le remplacement manuel donne la même sortie partout, et la démo doit être déterministe. En Java, `NumberFormat.getInstance(Locale.FRANCE)` embarque ses données dans le JDK, ce qui rend le problème moins visible ; en Python, on fait le travail soi-même.

**Le piège, encore.** `round(x, 2)` puis `str(...)` ne suffit pas : `str(5558.3)` donne « 5558.3 », sans séparateur ni second zéro. Le format `.2f` garantit toujours deux décimales : `fr(55000)` donne « 55 000,00 », comme dans la démo.

**Le test qui passe maintenant.** Depuis `projet/` :

```text
python -m unittest -v tests.test_03_metier.TestFormatage.test_montants_a_la_francaise
```

Le test vérifie « 5 558,32 », « 1 000 000 », « 28,9 », et que `ESPACE_FINE` est bien le caractère U+202F.

**Ce qu'il faut retenir.** Une constante par règle, en majuscules, en haut du module. Pour `fr` : formater à l'anglaise, puis échanger les séparateurs en libérant la virgule avant de la réutiliser.
