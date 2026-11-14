# Étape 1 — Les prix et le coût d'une tâche

> Palier 11 · Étape 1 sur 7 · Suivant : [Étape 2 — Le seau à jetons](<02-Seau-a-jetons.md>) · Énoncé : [README du palier 11](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Avant d'écrire une ligne, regarde ce que le test attend. `TestCout.test_exemple_avec_cache` appelle `cout_tache(2_000, 1_000, cache_lus=8_000, cache_ecrits=4_000)` et compare `c["usd"]` à 0.0384 et `c["aed"]` à 0.141024, à douze décimales près. Trois choses en découlent : la fonction rend un dictionnaire à deux clés, elle ne doit rien arrondir, et l'ordre des paramètres est fixé (entrée, sortie, puis les deux paramètres du cache, nommés).

Ensuite, écris la formule sur une feuille, avec ses unités. Les prix sont en USD **par million** de tokens : on multiplie chaque nombre de tokens par son prix, on additionne, et on divise **une seule fois** par un million à la fin. Les deux termes du cache utilisent le prix d'**entrée**, multiplié par 0,1 pour une lecture et par 1,25 pour une écriture. Refais l'exemple à la main : 6 000 + 15 000 + 2 400 + 15 000 = 38 400, divisé par un million, 0,0384 USD.

Enfin, l'ordre d'écriture dans le fichier : les constantes d'abord, parce que la signature de `cout_tache` les utilise comme valeurs par défaut, et que Python évalue ces valeurs au moment où il lit le `def`. Une constante définie plus bas provoquerait un `NameError` dès l'import du module.

## Les imports et les constantes

```python
# [extrait] agent/production.py
import math
import random

from agent.metier import AED_PAR_USD
from agent.modele import Horloge

PRIX_ENTREE_USD_MTOK = 3.00        # illustratif : USD par million de tokens d'entrée
PRIX_SORTIE_USD_MTOK = 15.00       # illustratif : USD par million de tokens de sortie
FACTEUR_LECTURE_CACHE = 0.10       # un token relu dans le cache coûte 0,1 fois le prix d'entrée
FACTEUR_ECRITURE_CACHE = 1.25      # un token écrit dans le cache coûte 1,25 fois le prix d'entrée
```

**Les deux premiers imports** servent plus loin : `math` pour `math.ceil` (le rang du percentile) et `math.floor` (le nombre de tâches), `random` pour le type `random.Random` du générateur de gigue. On les écrit dès maintenant, en tête de fichier, comme on déclare ses `import` en haut d'une classe Java.

**`from agent.metier import AED_PAR_USD`** réutilise la parité du palier 03, 3,6725 AED pour 1 USD. On ne recopie pas le nombre : il n'existe qu'à un seul endroit du paquet. C'est l'équivalent d'une constante `public static final` dans une classe partagée, que tous les services importent au lieu de la retaper.

**`from agent.modele import Horloge`** importe l'horloge simulée du palier 01. Le seau à jetons et les relances en ont besoin : aucune ligne de ce module ne lira l'heure réelle.

**Les quatre constantes** portent leur unité dans leur nom : `USD_MTOK` dit « USD par million de tokens », ce qui évite la confusion classique entre un prix par token (0,000003 USD) et un prix par million (3 USD). Le commentaire « illustratif » rappelle que ces chiffres ne viennent pas d'une grille réelle. En production, ils viendraient d'un fichier de configuration, comme une propriété `prix.entree` injectée par `@Value` dans un bean Spring ; ici, les paramètres `prix_entree` et `prix_sortie` de la fonction jouent ce rôle.

**Le piège classique** : écrire `0.000003` comme prix par token. Le calcul reste juste, mais il devient illisible, on se trompe facilement d'un facteur 1 000, et le résultat traîne plus de bruit d'arrondi. Garder des prix par million et une seule division à la fin rend chaque terme vérifiable à la main.

## Une première version, trop naïve

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cout_tache(tokens_entree, tokens_sortie, cache_lus, cache_ecrits)`** — Ce brouillon ressemble à un épicier qui pèse ensemble les pommes, les pommes soldées et les pommes de luxe, puis facture le tout au prix des pommes ordinaires. Il reçoit les tokens d'entrée, de sortie, lus et écrits dans le cache, additionne les trois sortes de tokens d'entrée, les facture à 3 USD par million et la sortie à 15, divise par un million et rend `{"usd": …, "aed": …}` en multipliant par 3,6725 écrit en dur. Sur l'exemple, il rend 0,057 USD, le coût sans cache, au lieu de 0,0384 ; et comme il ne vérifie rien, des tokens négatifs donneraient un coût négatif qui ferait remonter le budget tout seul.

```python
# [extrait] brouillon
def cout_tache(tokens_entree, tokens_sortie, cache_lus=0, cache_ecrits=0):
    entree = tokens_entree + cache_lus + cache_ecrits          # tous les tokens d'entrée au même prix
    usd = (entree * 3.00 + tokens_sortie * 15.00) / 1_000_000
    return {"usd": usd, "aed": usd * 3.6725}
```

Ce brouillon est celui qu'on écrit quand on a lu « le coût est linéaire en tokens » sans lire la suite. Sur l'exemple, il additionne 2 000 + 8 000 + 4 000 = 14 000 tokens d'entrée au tarif plein et rend 0,057 USD : exactement le coût **sans** cache. Le test attend 0,0384 et échoue. Le brouillon a trois défauts. Il oublie les facteurs : un token relu ne coûte que 0,1 fois le prix d'entrée, un token écrit en coûte 1,25 fois. Il recopie les prix et la parité en dur, si bien qu'un changement de modèle oblige à modifier le code. Et il accepte des tokens négatifs, qui donneraient un coût négatif, donc un budget qui remonte tout seul.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cout_tache(tokens_entree, tokens_sortie, cache_lus, cache_ecrits, prix_entree, prix_sortie)`** — La version juste est un caissier méticuleux qui passe chaque article sous le bon code de prix avant d'imprimer le ticket dans deux monnaies. Elle reçoit les quatre nombres de tokens, les deux du cache valant 0 par défaut, et les deux prix en USD par million, `PRIX_ENTREE_USD_MTOK` et `PRIX_SORTIE_USD_MTOK` par défaut ; elle lève `ValueError` si le plus petit des quatre nombres de tokens est négatif, puis une autre si un prix l'est. Elle facture l'entrée hors cache au prix plein, les tokens lus à `FACTEUR_LECTURE_CACHE` fois ce prix, les tokens écrits à `FACTEUR_ECRITURE_CACHE` fois, la sortie à son propre prix, divise une seule fois par un million et rend l'USD avec sa conversion par `AED_PAR_USD` : 0,0384 USD et 0,14102399999999998 AED à la console, soit 0,141024 AED aux arrondis près.

```python
# [extrait] agent/production.py
def cout_tache(tokens_entree: int, tokens_sortie: int, cache_lus: int = 0, cache_ecrits: int = 0,
               prix_entree: float = PRIX_ENTREE_USD_MTOK, prix_sortie: float = PRIX_SORTIE_USD_MTOK) -> dict:
    """Coût d'une tâche : {"usd": …, "aed": …}, les prix étant en USD par million de tokens.

    C = (N_in · P_in + N_lu · 0,1 · P_in + N_écrit · 1,25 · P_in + N_out · P_out) / 10⁶, puis × 3,6725.
    `tokens_entree` ne compte que les tokens d'entrée hors cache. La sortie ne se met jamais en cache.
    Exemple : 2 000 en entrée, 4 000 écrits, 8 000 lus, 1 000 en sortie :
    (6 000 + 15 000 + 2 400 + 15 000) / 10⁶ = 0.0384 USD = 0.141024 AED.
    """
    if min(tokens_entree, tokens_sortie, cache_lus, cache_ecrits) < 0:
        raise ValueError("les nombres de tokens sont >= 0")
    if prix_entree < 0 or prix_sortie < 0:
        raise ValueError("les prix sont >= 0")
    usd = (tokens_entree * prix_entree + cache_lus * FACTEUR_LECTURE_CACHE * prix_entree
           + cache_ecrits * FACTEUR_ECRITURE_CACHE * prix_entree + tokens_sortie * prix_sortie) / 1_000_000
    return {"usd": usd, "aed": usd * AED_PAR_USD}
```

**La signature.** Les deux paramètres du cache valent 0 par défaut : l'appel le plus courant, `cout_tache(14_000, 1_000)`, reste court, et un appel sans cache ne change pas de forme. Les prix ont pour valeur par défaut les constantes illustratives, mais on peut les remplacer pour chiffrer un autre modèle. L'annotation `-> dict` annonce le dictionnaire à deux clés.

**La docstring** recopie la formule et l'exemple chiffré du README. C'est la spécification que l'on relit le lendemain, quand on refait le palier de tête.

**Les deux gardes.** `min(tokens_entree, tokens_sortie, cache_lus, cache_ecrits) < 0` teste les quatre nombres de tokens en une seule comparaison : si le plus petit est négatif, au moins un l'est. La seconde garde refuse un prix négatif. Les deux lèvent `ValueError`, la convention du paquet pour une entrée invalide, comme une `IllegalArgumentException` en Java. Zéro est permis partout : une tâche sans sortie, ou un modèle gratuit en test, sont des cas légitimes.

**La formule.** Les quatre termes suivent la formule du README, dans le même ordre : l'entrée hors cache au prix plein, les tokens lus au dixième du prix d'entrée, les tokens écrits à 1,25 fois ce prix, la sortie à son propre prix. La parenthèse ouverte sur la première ligne permet de couper l'expression sur deux lignes sans barre oblique inverse. La division par `1_000_000` vient une seule fois, à la fin ; les tirets bas rendent le million lisible, comme `1_000_000` en Java depuis la version 7.

**Le retour.** On rend les deux devises. L'USD est la monnaie de la facture du fournisseur ; l'AED est celle du budget de la banque. On convertit avec `AED_PAR_USD`, jamais avec un 3.6725 recopié.

**Le piège des flottants.** 0,0384 × 3,6725 ne tombe pas juste en binaire, comme le montre la console :

```text
# [extrait] console
>>> from agent.production import cout_tache
>>> cout_tache(2_000, 1_000, cache_lus=8_000, cache_ecrits=4_000)
{'usd': 0.0384, 'aed': 0.14102399999999998}
>>> cout_tache(14_000, 1_000)
{'usd': 0.057, 'aed': 0.2093325}
```

C'est pour cela que les tests utilisent `assertAlmostEqual(..., places=12)` et jamais `assertEqual` sur un montant calculé. En Java, on écrirait la même chose avec `assertEquals(0.141024, c, 1e-12)`. Pour une écriture comptable, on passerait à `decimal.Decimal`, l'équivalent de `BigDecimal` ; pour une estimation de coût comparée à un budget, le flottant suffit.

## Le test qui passe maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_11_production.TestCout
```

Les trois tests passent : l'exemple avec cache, le cache au dixième et à 1,25 fois (10 000 tokens coûtent 0,03 USD au tarif plein, 0,003 USD relus, 0,0375 USD écrits), et les entrées invalides (`cout_tache(-1, 0)` et un prix d'entrée de −3 lèvent `ValueError`).
