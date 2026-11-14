"""Palier 06 — la mémoire : retrouver les bons souvenirs, par sens, fraîcheur et importance.

SQUELETTE À COMPLÉTER. Lis d'abord ../README.md (énoncé), puis code dans cet ordre :
`cosinus`, `min_max`, `recence`, `score_pertinence`, `Souvenir.__post_init__`, `rappeler`.
Lance les tests après chaque fonction :

    python -m unittest -v tests.test_06_memoire

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
    # TODO 1 : des dimensions différentes lèvent ValueError.
    # TODO 2 : calculer les deux normes (racine de la somme des carrés) ; une norme nulle lève ValueError,
    #          sans epsilon : un vecteur nul n'a pas de direction.
    # TODO 3 : produit scalaire / (produit des normes), puis ramener le résultat dans [-1, 1]
    #          (pour [1, 1, 1] et [2, 2, 2], le quotient flottant vaut 1.0000000000000002).
    raise NotImplementedError("Palier 06 : à coder — voir README.md")


def min_max(valeurs: list[float]) -> list[float]:
    """x' = (x − min) / (max − min) ; si toutes les valeurs sont égales, le signal ne départage rien : 0.0.

    Exemple : `min_max([9, 8, 4, 2])` = [1.0, 0.857143, 0.285714, 0.0] ; `min_max([3, 3])` = [0.0, 0.0].
    """
    # TODO 1 : une liste vide lève ValueError.
    # TODO 2 : si le plus grand et le plus petit sont égaux, rendre une liste de 0.0 de même longueur.
    # TODO 3 : sinon, appliquer la formule à chaque valeur, dans l'ordre.
    raise NotImplementedError("Palier 06 : à coder — voir README.md")


def recence(age: float, demi_vie: float) -> float:
    """rec = e^(−λ · âge) avec λ = ln 2 / demi-vie (étape 16) : 1 à l'âge 0, 1/2 à la demi-vie.

    Exemple : avec une demi-vie de 30 jours, `recence(5, 30)` ≈ 0.8909 et `recence(90, 30)` = 1/8 = 0.125.
    """
    # TODO 1 : un âge négatif ou une demi-vie <= 0 lèvent ValueError.
    # TODO 2 : calculer λ à partir de la demi-vie, puis l'exponentielle décroissante.
    raise NotImplementedError("Palier 06 : à coder — voir README.md")


def score_pertinence(sim: float, rec: float, imp: float, poids: tuple[float, float, float]) -> float:
    """S = w_sim · sim + w_rec · rec + w_imp · imp ; refuse ce qui casse la borne [0, 1].

    Poids négatifs, somme différente de 1 ou composante hors de [0, 1] : `ValueError`.
    Exemple : `score_pertinence(1.0, 0.9229, 1.0, (0.5, 0.3, 0.2))` = 0.5 + 0.27687 + 0.2 ≈ 0.9769.
    """
    # TODO 1 : refuser un poids négatif, ou une somme des poids différente de 1, avec une tolérance de 1e-9 :
    #          en flottant, sum((0.7, 0.29, 0.01)) vaut 0.9999999999999999, pas 1.0.
    # TODO 2 : refuser une composante hors de [0, 1] (il fallait normaliser d'abord).
    # TODO 3 : rendre la somme pondérée.
    raise NotImplementedError("Palier 06 : à coder — voir README.md")


@dataclass
class Souvenir:
    """Un souvenir : son texte, le jour de son dernier accès (horloge simulée), son importance de 1 à 10.

    Exemple : `Souvenir("Salaire mensuel déclaré : 40 000 AED", 85.0, 9)`.
    """
    texte: str
    jour_acces: float
    importance: int

    def __post_init__(self) -> None:
        """Appelée par la dataclass juste après l'__init__ généré : refuse une importance hors de 1..10."""
        # TODO : lever ValueError si l'importance n'est pas comprise entre 1 et 10 (bornes incluses).
        raise NotImplementedError("Palier 06 : à coder — voir README.md")


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
    # TODO 1 : k < 1 lève ValueError ; aucune mémoire → liste vide.
    # TODO 2 : plonger la question UNE fois, puis chaque souvenir ; trois listes de composantes brutes
    #          (cosinus, récence avec l'âge jour − jour_acces, importance en float), chacune passée par min_max.
    # TODO 3 : un couple (score, souvenir) par souvenir, avec score_pertinence et les poids.
    # TODO 4 : trier par score décroissant, égalités départagées par le texte (ordre alphabétique),
    #          et garder les k premiers.
    # TODO 5 : « relire » les souvenirs gardés : leur jour_acces passe à `jour`.
    raise NotImplementedError("Palier 06 : à coder — voir README.md")
