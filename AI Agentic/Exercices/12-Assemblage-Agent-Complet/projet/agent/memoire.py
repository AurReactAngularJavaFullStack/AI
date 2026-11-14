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
