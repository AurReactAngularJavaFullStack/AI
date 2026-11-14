# Étape 1 — Tokeniser et plonger

> Palier 07 · Étape 1 sur 8 · Précédent : [Énoncé du palier](<../../README.md>) · Suivant : [Étape 2 — Indexer le corpus](<02-Indexer-le-corpus.md>) · Retour à l'énoncé : [README du palier 07](<../../README.md>)

## Comment raisonner

Devant une feuille blanche, on ne commence pas par BM25 : BM25 compte des **mots**, et le cosinus compare des **vecteurs**. Il faut donc d'abord décider ce qu'est un mot, puis comment un texte devient un vecteur. Ces deux fonctions sont au bas de la pile : tout le reste du module les appelle, et une erreur ici fausse tous les scores sans faire échouer un seul calcul. On les écrit donc en premier, on les teste en premier, et l'on vérifie à la main sur une phrase courte.

La question à se poser pour `tokeniser` : quand deux textes parlent du même mot, est-ce que leurs listes de mots contiennent la même chaîne ? « Durée » et « durée », « prêt » et « pret », « d'un » et « un » doivent se rejoindre. D'où trois décisions : tout en minuscules, accents retirés, découpe sur tout ce qui n'est pas lettre ou chiffre. Puis une quatrième : retirer les mots vides, qui sont partout et ne départagent rien.

## Les imports et les constantes

```python
# [extrait] agent/recherche.py
import math
import re
import unicodedata

from agent.memoire import cosinus
from agent.modele import encadrer_donnees
from agent.outils import Registre
from agent.schemas import objet
```

- `math` servira au logarithme de l'IDF (étape 3), `re` aux découpes et aux citations, `unicodedata` à la normalisation des accents.
- Les quatre imports suivants sont la règle des paliers : on **compose** avec ce qui existe, on ne le réécrit pas. `cosinus` vient du palier 06, `encadrer_donnees` du palier 01, `Registre` du palier 04, `objet` du palier 02. C'est le premier écart avec l'étape 77, qui avait tout dans un seul fichier.
- **Analogie Java :** ce sont des `import` de classes d'autres packages du même module Maven. Python n'a pas de visibilité `package-private` : l'underscore initial (`_x`) est la seule convention de « privé ».
- **Piège classique :** importer `agent.recherche` depuis `agent.memoire` pour récupérer `plonger_texte` créerait un import circulaire. C'est pourquoi la mémoire reçoit le plongement en paramètre (injection), au lieu de l'importer.

```python
# [extrait] agent/recherche.py
MOTS_VIDES = {"a", "au", "aux", "ce", "d", "de", "des", "du", "en", "est", "et", "l", "la", "le", "les", "ne", "ou",
              "pas", "pour", "quel", "quelle", "s", "se", "sur", "un", "une", "y"}
CONCEPTS = {                                   # plongement jouet : une dimension par concept métier
    "dette": {"endettement", "dette", "mensualite", "mensualites", "remboursement"},
    "revenu": {"salaire", "revenu", "retraite", "retraites"}, "credit": {"pret", "credit", "hypotheque", "emprunt"},
    "duree": {"duree", "mois", "ans", "annee", "annees"}, "taxe": {"tva", "taxe", "exonere"},
    "change": {"change", "dirham", "usd", "indexe"}, "emploi": {"service", "salarie", "contrat", "jours"},
    "immobilier": {"bien", "loyer", "transfert", "residentiel", "dld"},
}
```

- `MOTS_VIDES` est un `set` : le test `m not in MOTS_VIDES` coûte O(1), comme un `HashSet.contains` en Java. Une liste coûterait une comparaison par mot vide.
- Les mots vides sont écrits **sans accent** et en minuscules, parce qu'on les compare après normalisation : « à » devient `a`, qui est dans l'ensemble.
- `CONCEPTS` associe à chaque concept l'ensemble des mots qui le portent. L'ordre des clés compte : la composante 0 du vecteur est « dette », la 5 est « change ». Depuis Python 3.7, un `dict` garde l'ordre d'insertion, comme une `LinkedHashMap` ; on peut donc s'y fier.
- Les mots des concepts sont, eux aussi, déjà normalisés (`mensualite`, `hypotheque`) : sinon « mensualité » tokenisé ne les trouverait jamais.
- **Piège classique :** `"retraite"` et `"retraites"` sont tous deux dans le concept revenu, mais pour BM25 ce sont deux mots différents. Le plongement « comprend » le pluriel, BM25 non ; tu le verras au score du message de forum.

## Une première version, trop naïve

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tokeniser(t)`** — Dans ce brouillon, la fonction est un correcteur pressé qui coupe les phrases aux seuls espaces et ne touche ni aux accents ni à la ponctuation : elle reçoit un texte, le passe en minuscules, le découpe avec `split()` et renvoie la liste des morceaux qui ne sont pas des mots vides. Sur « Durée maximale d'un prêt », elle rend `durée`, `maximale`, `d'un` et `prêt` : l'accent de « durée » empêche toute rencontre avec un `duree` saisi sans accent, « d'un » reste collé et échappe au filtre des mots vides, et une virgule resterait accrochée au mot qui la précède.

```python
# [extrait] brouillon
def tokeniser(t: str) -> list[str]:
    return [m for m in t.lower().split() if m not in MOTS_VIDES]
```

C'est ce qu'on écrit spontanément : minuscules, découpe sur les espaces, filtre. Sur « Durée maximale d'un prêt », `t.lower().split()` donne `['durée', 'maximale', "d'un", 'prêt']`. Trois défauts sautent aux yeux : « durée » garde son accent et ne rencontrera jamais un `duree` saisi sans accent ; « d'un » reste collé et n'est pas reconnu comme mot vide ; et une virgule ou un deux-points resterait accroché au mot qui le précède (« CBUAE, » n'est pas « CBUAE »). Il faut donc normaliser les accents et découper sur les **caractères**, pas sur les espaces.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tokeniser(t)`** — C'est la même fonction, confiée cette fois à un correcteur méticuleux qui ramène chaque mot à sa forme nue avant de l'archiver : elle reçoit un texte, le met en minuscules, le décompose en forme NFKD pour séparer chaque lettre de son accent, jette les caractères combinants, puis relève avec `re.findall` toutes les suites de lettres ASCII et de chiffres, dont elle écarte les mots de `MOTS_VIDES`. Elle renvoie la liste des mots dans l'ordre, répétitions comprises, comme BM25 en a besoin : « Durée maximale d'un prêt » donne `["duree", "maximale", "pret"]`, et la requête de référence les 7 mots de `plafond` à `personnel`.

```python
# [extrait] agent/recherche.py
def tokeniser(t: str) -> list[str]:
    """Minuscules, accents retirés (NFKD), découpe sur [a-z0-9]+, mots vides retirés.

    Exemple : `tokeniser("Durée maximale d'un prêt")` = ["duree", "maximale", "pret"].
    """
    t = "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))
    return [m for m in re.findall(r"[a-z0-9]+", t) if m not in MOTS_VIDES]
```

Ligne par ligne :

- `t.lower()` met tout en minuscules. On le fait **avant** la normalisation : `"É".lower()` vaut `"é"`, qui se décompose ensuite comme les autres.
- `unicodedata.normalize("NFKD", …)` décompose chaque lettre accentuée en deux caractères : la lettre de base, puis l'accent seul, un caractère dit « combinant ». La forme K (compatibilité) ramène aussi quelques variantes typographiques à leur forme simple.
- `if not unicodedata.combining(c)` jette les accents isolés. Le `"".join(…)` recolle le reste : « prêt » devient « pret ».
- `re.findall(r"[a-z0-9]+", t)` rend toutes les suites maximales de lettres ASCII et de chiffres : l'apostrophe, la virgule, le « % » et les espaces deviennent des séparateurs. « d'un » donne `d` et `un`.
- La compréhension de liste filtre les mots vides, en gardant l'ordre et les répétitions : BM25 a besoin des deux.

Ce que fait la normalisation, sur une seule lettre :

```text
# [extrait] console
>>> import unicodedata
>>> [hex(ord(c)) for c in unicodedata.normalize("NFKD", "é")]
['0x65', '0x301']
```

`0x65` est « e », `0x301` est l'accent aigu combinant : c'est lui que `unicodedata.combining` reconnaît.

- **Analogie Java :** `Normalizer.normalize(t.toLowerCase(), Normalizer.Form.NFKD).replaceAll("\\p{M}", "")`, puis un `Matcher` sur `[a-z0-9]+` dont on collecte les `group()` dans une `List<String>` filtrée par un `stream()`.
- **Piège classique :** `[a-z0-9]` ne garde que l'alphabet latin. Un texte en arabe disparaîtrait entièrement, et une question en arabe donnerait une liste vide. Pour un agent bilingue aux Émirats, il faudrait une classe de caractères Unicode (`\w`) et des mots vides arabes ; ce palier reste volontairement en français.
- **Piège classique bis :** écrire `t.lower` sans parenthèses ne lève aucune erreur dans un IDE, mais `unicodedata.normalize` reçoit alors une méthode au lieu d'une chaîne et lève `TypeError`.

**Test qui passe maintenant :**

```powershell
python -m unittest -v tests.test_07_recherche.TestTokenisation.test_accents_et_mots_vides
```

Il vérifie l'exemple de la docstring et les 7 mots de la requête de référence : `plafond`, `endettement`, `retraite`, `duree`, `maximale`, `pret`, `personnel`.

## Le plongement jouet

Un vrai modèle d'embedding rend un vecteur de plusieurs centaines de nombres, impossible à vérifier à la main. Le module le remplace par un vecteur de 8 nombres, un par concept, qui compte les mots du texte relevant de ce concept. On garde ainsi la propriété qui compte pour la recherche : deux textes qui parlent des mêmes choses ont des vecteurs proches, même s'ils n'emploient pas les mêmes mots (« hypothèque » et « prêt » relèvent tous deux du concept crédit).

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`plonger(tokens)`** — Cette fonction est le documentaliste qui trie chaque mot dans l'un des huit tiroirs thématiques de `CONCEPTS` puis compte le contenu de chaque tiroir : elle reçoit une liste de mots tokenisés, parcourt les ensembles de mots des concepts dans leur ordre, compte pour chacun les mots du texte qui lui appartiennent, répétitions comprises, et renvoie ces 8 comptes sous forme de flottants. Un mot qui ne relève d'aucun concept ne compte nulle part ; les 7 mots de la requête de référence donnent ainsi `[1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]`, pour dette, revenu, crédit et durée.

```python
# [extrait] agent/recherche.py
def plonger(tokens: list[str]) -> list[float]:
    """Pour chacun des 8 concepts, le nombre de mots qui en relèvent.

    Exemple : `plonger(["plafond", "endettement", "retraite", "duree", "maximale", "pret", "personnel"])`
    = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0] (dette, revenu, crédit, durée).
    """
    return [float(sum(1 for t in tokens if t in mots)) for mots in CONCEPTS.values()]
```

- La compréhension externe parcourt les **ensembles** de mots, dans l'ordre des concepts : elle produit une composante par concept, donc toujours 8 nombres.
- `sum(1 for t in tokens if t in mots)` compte les mots du texte qui appartiennent à l'ensemble : c'est la somme d'indicatrices du rappel de cours. Un mot répété compte autant de fois qu'il apparaît.
- `float(…)` rend des flottants, comme un vrai embedding et comme l'annotation `list[float]`. En Python `1 == 1.0`, donc le test passerait aussi avec des entiers, mais le type annoncé doit être tenu.
- **Analogie Java :** `CONCEPTS.values().stream().map(mots -> (double) tokens.stream().filter(mots::contains).count()).toList()`.
- **Piège classique :** parcourir `CONCEPTS` (les clés) au lieu de `CONCEPTS.values()` ferait tester `t in "dette"`, c'est-à-dire « t est-il une sous-chaîne de "dette" » : aucune erreur, et des vecteurs faux.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`plonger_texte(t)`** — Cette fonction d'une ligne est la chaîne de montage à deux postes qui fait passer un texte brut chez le correcteur puis chez le documentaliste : elle reçoit un texte, appelle `tokeniser` puis `plonger` sur le résultat, et renvoie le vecteur de 8 flottants obtenu. C'est elle que la mémoire du palier 06 reçoit par injection, ce qui permettra un jour de brancher un vrai modèle d'embedding sans toucher à la mémoire ; « A demandé le taux de change du dirham en USD » donne un vecteur nul partout sauf en position 5, le concept change, qui vaut 3,0.

```python
# [extrait] agent/recherche.py
def plonger_texte(t: str) -> list[float]:
    """`plonger(tokeniser(t))` : la fonction texte → vecteur qu'attend `memoire.rappeler`.

    Exemple : "A demandé le taux de change du dirham en USD" donne [0, 0, 0, 0, 0, 3, 0, 0].
    """
    return plonger(tokeniser(t))
```

- Une seule ligne, mais un rôle d'architecture : c'est la fonction `Callable[[str], list[float]]` que `memoire.rappeler` reçoit en paramètre depuis le palier 06. La mémoire ne dépend ainsi d'aucun modèle d'embedding ; le jour où l'on branche un vrai modèle, on remplace `plonger_texte`, pas la mémoire.
- **Analogie Java :** une implémentation de `Function<String, List<Double>>` passée par injection de dépendance.
- Sur l'exemple : « A demandé le taux de change du dirham en USD » donne `demande`, `taux`, `change`, `dirham`, `usd` ; `change`, `dirham` et `usd` relèvent du concept change (indice 5), `taux` d'aucun. D'où 3,0 en position 5.

**Test qui passe maintenant :**

```powershell
python -m unittest -v tests.test_07_recherche.TestTokenisation.test_plongement
```

Prochaine étape : le corpus, et la façon de le tokeniser une fois pour toutes.
