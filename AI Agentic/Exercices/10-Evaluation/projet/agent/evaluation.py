"""Palier 10 — l'évaluation : mesurer l'agent comme avant un déploiement, et savoir dire non.

SQUELETTE À COMPLÉTER. Les signatures, les docstrings et les constantes sont celles de la solution :
ne les change pas, les tests en dépendent. Remplace chaque `raise NotImplementedError(...)` par le code
demandé, dans l'ordre du README : wilson, tool_call_f1, goal_accuracy, moyenne_definie, nombres,
fidelite_approchee, noter, rapport, barriere_ci.

Origine : étape 77, sections 4 et 9 (`wilson`, `tool_call_f1`, `goal_accuracy`, `nombres`,
`fidelite_approchee`, `moyenne_definie`, `noter`, `rapport`, `barriere_ci`), étapes 59, 60 et 65.

Convention du parcours : une métrique sans dénominateur rend None (indéfinie) — ni 0 ni 1 — et
n'entre pas dans les moyennes.
"""
import json
import math
import re
from collections import Counter

from agent.metier import ESPACE_FINE


def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalle de Wilson à 95 % pour une proportion ; None si n = 0.

    centre = (p + z²/2n) / (1 + z²/n) ; demi-largeur = z √(p(1−p)/n + z²/4n²) / (1 + z²/n).
    Exemple : 18 sur 18 donne une borne basse n / (n + z²) = 18 / 21.8416 ≈ 0.824 ; 14 sur 18 donne
    ≈ [0.548 ; 0.910] ; 3 sur 3 donne une borne basse ≈ 0.438.
    Erreur : n < 0, ou succes hors de [0, n] → ValueError (« il faut 0 <= succes <= n »).
    """
    # TODO 1 : n == 0 → None (testé AVANT la validation) ; puis valider succes et n.
    # TODO 2 : p, le dénominateur d = 1 + z²/n, le centre, la demi-largeur ; rendre (centre − demi, centre + demi).
    raise NotImplementedError("Palier 10 : à coder — voir README.md")


def tool_call_f1(attendus: list, reels: list) -> float | None:
    """F1 = 2 |A ∩ R| / (|A| + |R|) sur des multi-ensembles d'appels (nom, arguments) ; None si tout est vide.

    L'intersection de deux `Counter` garde la plus petite multiplicité : un appel répété ne compte
    qu'autant de fois qu'il était attendu. Exemple : 2 appels attendus, un seul fait (correct) :
    2 × 1 / (2 + 1) = 2/3 ≈ 0.6667.
    Deux appels qui ne diffèrent que par l'ordre de leurs arguments sont le même appel.
    """
    # TODO 3 : une clé canonique par appel : (nom, json.dumps(arguments, sort_keys=True)) — un dict n'est pas hachable.
    # TODO 4 : deux Counter, leur intersection &, puis 2 × TP / (|A| + |R|), ou None si |A| + |R| = 0.
    raise NotImplementedError("Palier 10 : à coder — voir README.md")


def goal_accuracy(resultats: list[bool]) -> float | None:
    """Part des tâches dont l'objectif est atteint ; None si aucune tâche. Exemple : 14 sur 18 ≈ 0.7778."""
    # TODO 5 : une ligne ; en Python, True vaut 1 dans une somme.
    raise NotImplementedError("Palier 10 : à coder — voir README.md")


def nombres(t: str) -> list[float]:
    """Nombres cités, lus à la française ; un pourcentage est divisé par 100 ; [REG-2] n'en est pas un.

    Exemple : « 5 558,32 AED ; 28,9 % [REG-1] » (espace fine) donne [5558.32, 0.289].
    Seule l'espace fine ESPACE_FINE (U+202F) est un séparateur de milliers ; la virgule ou le point
    est le séparateur décimal ; un « % » qui suit le nombre (espaces permis) le divise par 100.
    """
    # TODO 6 : retirer les citations [ABC-12] et les espaces fines.
    # TODO 7 : re.findall avec deux groupes (le nombre, le « % » facultatif) ; virgule → point ; float.
    raise NotImplementedError("Palier 10 : à coder — voir README.md")


def fidelite_approchee(reponse: str, sources: list[str]) -> float | None:
    """Part des NOMBRES de la réponse que l'on retrouve (à `math.isclose` près) dans les sources ; None sans nombre.

    Exemple : « Mensualité 5 419,37 AED ; endettement estimé à 35 % » avec des sources qui contiennent
    5419.37 mais pas 0.35 : 1 / 2 = 0.5.
    Tolérance : math.isclose(c, k, rel_tol=1e-9, abs_tol=1e-9).
    """
    # TODO 8 : nombres cités ; aucun → None (indéfinie, PAS 0 ni 1).
    # TODO 9 : nombres connus de toutes les sources ; compter les cités retrouvés ; diviser par le nombre de cités.
    raise NotImplementedError("Palier 10 : à coder — voir README.md")


def moyenne_definie(valeurs: list) -> float | None:
    """Moyenne des valeurs définies (les None sont ignorés) ; None si aucune. Exemple : [1, None, 0.5] → 0.75."""
    # TODO 10 : filtrer les None (attention : 0.0 est une valeur définie, ne pas filtrer par « if v »).
    raise NotImplementedError("Palier 10 : à coder — voir README.md")


def noter(res: dict, sources: list[str], attendus: list, but: bool) -> dict:
    """Les trois mesures d'un cas : {"f1", "but", "fidelite"} ; la fidélité n'est définie que si fini.

    `res` est le résultat de `executer_agent` ; sa trace donne les appels réels (nom, arguments).
    Un résultat qui n'est pas « fini » n'a pas de clé "reponse" : ne pas la lire dans ce cas.
    """
    # TODO 11 : appels réels = (nom, arguments) de chaque ligne (nom, arguments, sortie) de la trace.
    raise NotImplementedError("Palier 10 : à coder — voir README.md")


def rapport(notes: list[dict]) -> dict:
    """Agrège les notes : {"n", "succes", "taux", "wilson", "tool_f1", "fidelite"}.

    Exemple : 14 cas parfaits et 4 cas à (F1 2/3, fidélité 0.5, but faux) donnent succes 14,
    tool_f1 = (14 + 4 × 2/3) / 18 ≈ 0.926 et fidelite = (14 + 4 × 0.5) / 18 ≈ 0.889.
    """
    # TODO 12 : succes = nombre de buts atteints ; taux par goal_accuracy ; wilson ; deux moyennes définies.
    raise NotImplementedError("Palier 10 : à coder — voir README.md")


SEUILS = {"borne_basse": 0.80, "tool_f1": 0.95, "fidelite": 0.95}


def barriere_ci(rap: dict, seuils: dict = SEUILS) -> tuple[int, list[str]]:
    """(code de sortie, motifs) : 0 autorise le déploiement, 1 le bloque. N'appelle jamais `sys.exit`.

    Un motif lisible par seuil violé : borne basse de Wilson, Tool Call F1, fidélité (une moyenne
    indéfinie ne bloque pas). Aucun cas évalué : code 1.
    Exemple : 3 cas parfaits sur 3 : borne basse 0.438 < 0.8, donc (1, ["borne basse de Wilson 0.438 < 0.8"]).
    Motifs exacts, valeurs à 3 décimales : "borne basse de Wilson 0.548 < 0.8",
    "Tool Call F1 0.926 < 0.95", "fidélité approchée 0.889 < 0.95" ; (1, ["aucun cas évalué"]) si n = 0.
    """
    # TODO 13 : n == 0 d'abord (rap["wilson"] vaut alors None : ne pas l'indexer).
    # TODO 14 : trois tests, dans cet ordre ; une moyenne None ne crée pas de motif ; code 1 s'il y a un motif.
    raise NotImplementedError("Palier 10 : à coder — voir README.md")
