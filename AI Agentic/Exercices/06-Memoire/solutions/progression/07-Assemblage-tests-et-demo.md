# Étape 7 — Assemblage, tests et démo

> Progression du palier 06 · Précédent : [Étape 6 — Rappeler](<06-Rappeler.md>) · Suivant : [Palier 07 — Recherche hybride](<../../../07-Recherche-Hybride/README.md>) · Retour à l'énoncé : [README du palier 06](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Le module est complet ; on le relit d'un trait, de haut en bas. L'ordre des fonctions est celui des dépendances : chaque fonction n'utilise que celles qui la précèdent. Pour le réécrire de mémoire, il suffit de retenir la phrase du score : « trois signaux, chacun ramené dans [0, 1] sur tous les candidats, mélangés par des poids positifs de somme 1, puis les k meilleurs, relus ».

## Le module complet

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — C'est la fonction de l'étape 1, le navigateur qui compare deux caps : elle reçoit deux vecteurs, lève `ValueError` si leurs dimensions diffèrent ou si l'un d'eux est nul, puis renvoie le produit scalaire divisé par le produit des normes, borné à [−1, 1]. Dans la démo, elle donne 0,75 pour les trois souvenirs de crédit et 0,3536 pour le taux de change, la composante « sens » du score.

**`min_max(valeurs)`** — C'est la fonction de l'étape 2, l'arbitre qui ramène toutes les notes sur une échelle de 0 à 1 : elle reçoit une liste, lève `ValueError` si elle est vide, renvoie des zéros partout si toutes les valeurs sont égales, et sinon la liste ramenée dans [0, 1] dans le même ordre. La démo montre son effet sur les trois composantes : les importances 9, 8, 4 et 2 deviennent 1, 0,8571, 0,2857 et 0.

**`recence(age, demi_vie)`** — C'est la fonction de l'étape 3, l'horlogère qui gradue la fraîcheur en demi-vies : elle reçoit l'âge d'un souvenir et la demi-vie, refuse un âge négatif ou une demi-vie qui n'est pas strictement positive, et renvoie l'exponentielle décroissante, qui vaut 1 à l'âge 0 et 1/2 à la demi-vie. Le bloc 4 de la démo le rappelle : avec une demi-vie de 30 jours, un souvenir de 90 jours pèse 0,125 de sa valeur neuve.

**`score_pertinence(sim, rec, imp, poids)`** — C'est la fonction de l'étape 4, le jury qui additionne trois notes normalisées avec leurs coefficients : elle reçoit les trois composantes et les poids, lève `ValueError` sur un poids négatif, une somme de poids différente de 1 au-delà de 10⁻⁹ ou une composante hors de [0, 1], puis renvoie la somme pondérée. Avec les poids (0,5 ; 0,3 ; 0,2), elle donne au bloc 2 de la démo les scores 0,9769, 0,8070, 0,5571 et 0,3000.

**`Souvenir.__post_init__()`** — C'est la méthode de l'étape 5, l'archiviste qui contrôle la note d'importance au moment où la fiche entre au classeur : appelée par la dataclass juste après son constructeur généré, elle ne reçoit que le souvenir lui-même et lève `ValueError` si l'importance n'est pas comprise entre 1 et 10. Elle ne renvoie rien, et la dataclass n'étant pas gelée, `rappeler` pourra plus tard modifier le jour d'accès des souvenirs relus.

**`rappeler(question, souvenirs, plonger_texte, jour, k, demi_vie, poids)`** — C'est la fonction de l'étape 6, la bibliothécaire qui choisit les fiches à poser sur le bureau du conseiller : elle reçoit la question, les souvenirs, la fonction de plongement injectée, le jour courant et son réglage, calcule les trois composantes alignées et normalisées, les combine en scores, trie par la clé (opposé du score, texte), garde les k meilleurs et les relit en faisant passer leur jour d'accès au jour courant. Au bloc 3 de la démo, elle rend le salaire et le crédit auto, de scores 0,9769 et 0,807, et les jours d'accès deviennent [90, 90, 0, 88].

```python
# [extrait] agent/memoire.py
"""Palier 06 — la mémoire : retrouver les bons souvenirs, par sens, fraîcheur et importance.

Origine : étape 77, sections 4 et 6 (`cosinus`, `min_max`, `recence`, `score_pertinence`, `Souvenir`,
`rappeler`), étapes 14, 16 et 17 du parcours.

Score d'un souvenir (étape 17) : S = w_sim · sim + w_rec · rec + w_imp · imp, chaque composante étant
d'abord ramenée dans [0, 1] par min-max sur l'ensemble des souvenirs.
Le plongement des textes est INJECTÉ (`plonger_texte`, une fonction texte → vecteur) : ce module ne
dépend d'aucun modèle d'embedding ; le palier 07 fournira `recherche.plonger_texte`.
"""
import math
from collections.abc import Callable
from dataclasses import dataclass


def cosinus(a: list[float], b: list[float]) -> float:
    """cos(a, b) = a · b / (‖a‖ ‖b‖), borné à [−1, 1] ; un vecteur nul lève `ValueError` (pas d'epsilon).

    Exemple : `cosinus([1, 1, 2, 1, 0, 1, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0])` = 3 / (√8 × √2) = 3 / 4 = 0.75.
    """
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


def min_max(valeurs: list[float]) -> list[float]:
    """x' = (x − min) / (max − min) ; si toutes les valeurs sont égales, le signal ne départage rien : 0.0.

    Exemple : `min_max([9, 8, 4, 2])` = [1.0, 0.857143, 0.285714, 0.0] ; `min_max([3, 3])` = [0.0, 0.0].
    """
    if not valeurs:
        raise ValueError("liste vide : min-max n'est pas défini")
    lo, hi = min(valeurs), max(valeurs)
    if hi == lo:
        return [0.0 for _ in valeurs]
    return [(v - lo) / (hi - lo) for v in valeurs]


def recence(age: float, demi_vie: float) -> float:
    """rec = e^(−λ · âge) avec λ = ln 2 / demi-vie (étape 16) : 1 à l'âge 0, 1/2 à la demi-vie.

    Exemple : avec une demi-vie de 30 jours, `recence(5, 30)` ≈ 0.8909 et `recence(90, 30)` = 1/8 = 0.125.
    """
    if age < 0 or demi_vie <= 0:
        raise ValueError("il faut age >= 0 et demi_vie > 0")
    lam = math.log(2) / demi_vie
    return math.exp(-lam * age)


def score_pertinence(sim: float, rec: float, imp: float, poids: tuple[float, float, float]) -> float:
    """S = w_sim · sim + w_rec · rec + w_imp · imp ; refuse ce qui casse la borne [0, 1].

    Poids négatifs, somme différente de 1 ou composante hors de [0, 1] : `ValueError`.
    Exemple : `score_pertinence(1.0, 0.9229, 1.0, (0.5, 0.3, 0.2))` = 0.5 + 0.27687 + 0.2 ≈ 0.9769.
    """
    if min(poids) < 0 or abs(sum(poids) - 1.0) > 1e-9:
        raise ValueError("les poids doivent être >= 0 et de somme 1")
    if not all(0.0 <= x <= 1.0 for x in (sim, rec, imp)):
        raise ValueError("chaque composante doit être dans [0, 1] : normaliser d'abord")
    return sum(w * x for w, x in zip(poids, (sim, rec, imp)))


@dataclass
class Souvenir:
    """Un souvenir : son texte, le jour de son dernier accès (horloge simulée), son importance de 1 à 10.

    Exemple : `Souvenir("Salaire mensuel déclaré : 40 000 AED", 85.0, 9)`.
    """
    texte: str
    jour_acces: float
    importance: int

    def __post_init__(self) -> None:
        if not 1 <= self.importance <= 10:
            raise ValueError("importance de 1 (banal) à 10 (crucial)")


def rappeler(question: str, souvenirs: list[Souvenir], plonger_texte: Callable[[str], list[float]], jour: float,
             k: int = 2, demi_vie: float = 30.0,
             poids: tuple[float, float, float] = (0.5, 0.3, 0.2)) -> list[tuple[float, Souvenir]]:
    """Les k souvenirs les plus pertinents, avec leur score, du meilleur au moins bon.

    Étapes : cosinus question/souvenir, récence (âge = jour − jour_acces), importance ; min-max de
    chaque composante ; somme pondérée ; tri décroissant (égalités départagées par le texte) ; les k
    premiers. Les souvenirs rappelés sont RELUS : leur `jour_acces` passe à `jour`.
    Exemple (scénario de 77, jour 90) : sims [0.75, 0.75, 0.75, 0.3536], âges [5, 30, 90, 2],
    importances [9, 8, 4, 2] → scores 0.9769, 0.8070, 0.5571, 0.3 ; on garde les deux premiers.
    """
    if k < 1:
        raise ValueError("k doit valoir au moins 1")
    if not souvenirs:
        return []
    vq = plonger_texte(question)
    sims = min_max([cosinus(vq, plonger_texte(s.texte)) for s in souvenirs])
    recs = min_max([recence(jour - s.jour_acces, demi_vie) for s in souvenirs])
    imps = min_max([float(s.importance) for s in souvenirs])
    notes = [(score_pertinence(sims[j], recs[j], imps[j], poids), s) for j, s in enumerate(souvenirs)]
    gardes = sorted(notes, key=lambda x: (-x[0], x[1].texte))[:k]
    for _, s in gardes:
        s.jour_acces = jour                   # relire remet l'horloge du souvenir à zéro (étape 16)
    return gardes
```

**La docstring du module** donne la formule du score et la règle d'architecture : le plongement est injecté, et le module ne dépend d'aucun modèle d'embedding.

**`cosinus`** (étape 1) : deux gardes, les dimensions et le vecteur nul, puis le quotient borné à [−1, 1].

**`min_max`** (étape 2) : la liste vide refusée, le signal constant ramené à 0 partout, puis la formule, dans l'ordre.

**`recence`** (étape 3) : l'âge négatif et la demi-vie non positive refusés, λ = ln 2 / demi-vie, puis l'exponentielle.

**`score_pertinence`** (étape 4) : une garde par hypothèse de la preuve de l'étape 17 (poids positifs, somme 1, composantes dans [0, 1]), puis la somme pondérée.

**`Souvenir`** (étape 5) : une `dataclass` modifiable, dont l'importance est contrôlée dans `__post_init__`.

**`rappeler`** (étape 6) : les trois listes alignées et normalisées, les scores, le tri par la clé `(-score, texte)`, les k premiers, puis la relecture.

## Tous les tests

Depuis `projet/`, une fois ton fichier `agent/memoire.py` complet :

```text
python -m unittest -v
```

La fin de la sortie doit être :

```text
Ran 82 tests in 0.0XXs

OK
```

Les 82 tests regroupent les 69 tests des paliers 01 à 05, qui passaient déjà, et les 13 tests du palier 06. Le temps exact varie d'une machine à l'autre.

## La démo

```text
python demo.py
```

Sortie attendue :

```text
Palier 06 — la mémoire du client C-1, au jour 90 de la relation
1. Composantes brutes, puis ramenées dans [0, 1] par min-max :
   cosinus  0.7500  0.7500  0.7500  0.3536   →  1.0000  1.0000  1.0000  0.0000
   récence  0.8909  0.5000  0.1250  0.9548   →  0.9229  0.4519  0.0000  1.0000
   importance 9  8  4  2   →  1.0000  0.8571  0.2857  0.0000
2. Score de pertinence S = 0.5 sim + 0.3 rec + 0.2 imp, tous les souvenirs :
   0.9769  Salaire mensuel déclaré au dossier de crédit : 40 000 AED
   0.8070  Crédit auto en cours : mensualité de 6 000 AED
   0.5571  Cherchait un prêt personnel sur 48 mois
   0.3000  A demandé le taux de change du dirham en USD
3. Les 2 souvenirs mis dans le prompt : [0.9769, 0.807]
   relus, leurs jours d'accès deviennent : [90.0, 90.0, 0.0, 88.0]
4. Demi-vie 30 jours : un souvenir de 90 jours pèse 0.125 de sa valeur neuve
OK — palier 06 terminé.
```

Ligne par ligne :

- **Le bloc 1** montre les trois composantes brutes, puis leur min-max, pour les quatre souvenirs du client C-1. Les trois souvenirs de crédit ont le même cosinus, 0,75, et le change 0,3536. Le min-max les ramène à 1 et 0. La récence 0,1250 du prêt personnel, vieux de 90 jours, devient 0. L'importance 9 du salaire devient 1.
- **Le bloc 2** classe les quatre souvenirs avec k = 4, sur une **copie** de la mémoire, pour ne pas relire les souvenirs avant l'étape suivante. On y retrouve les scores 0,9769, 0,8070, 0,5571 et 0,3000, recalculés à la main dans l'énoncé.
- **Le bloc 3** rappelle les deux souvenirs qui iront dans le prompt, salaire et crédit auto, puis montre leur relecture : les jours d'accès passent de [85, 60, 0, 88] à [90, 90, 0, 88].
- **Le bloc 4** rappelle la règle de la demi-vie : 90 jours, c'est trois demi-vies de 30 jours, soit 1/8 = 0,125.

Le texte des deux souvenirs gardés est exactement ce que `construire_prompt` (palier 01) placera dans la balise `<memoire>` du prompt système. Le palier 12 fera ce branchement : il appellera `rappeler` avec `recherche.plonger_texte` et le jour de son horloge, puis passera les textes des souvenirs gardés à `construire_prompt`.

## Ce que tu as appris

- Le cosinus compare des directions ; un vecteur nul est une erreur, pas un cosinus nul, et l'arrondi flottant impose une borne.
- Min-max met des signaux d'échelles différentes à la même étendue, sans changer l'ordre d'aucun ; un signal constant ne compte pour personne.
- La récence se règle par une demi-vie, qui a un sens métier, et non par un taux ; un âge négatif trahit une horloge fausse.
- Le score reste dans [0, 1] si et seulement si ses hypothèses sont vérifiées : chaque hypothèse de la preuve devient une garde du code.
- Une dataclass se valide dans `__post_init__`, et ne se gèle pas quand on doit la modifier.
- `rappeler` dépend d'une fonction injectée, trie avec une clé explicite et déterministe, et relit les souvenirs gardés.

## La suite

La mémoire compare la question à des souvenirs dont les vecteurs sont, pour l'instant, écrits à la main. Le [palier 07 — Recherche hybride](<../../../07-Recherche-Hybride/README.md>) construit le plongement `plonger_texte` qui les calculera à partir des textes. Il réutilise le `cosinus` de ce palier, et y ajoute le classement par mots exacts (BM25) et la fusion de deux classements (RRF), pour retrouver les règles qui fondent une réponse.
