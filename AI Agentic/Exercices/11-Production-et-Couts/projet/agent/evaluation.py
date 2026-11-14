"""Palier 10 — l'évaluation : mesurer l'agent comme avant un déploiement, et savoir dire non.

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
    """
    if n == 0:
        return None
    if n < 0 or not 0 <= succes <= n:
        raise ValueError("il faut 0 <= succes <= n")
    p = succes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - demi, centre + demi)


def tool_call_f1(attendus: list, reels: list) -> float | None:
    """F1 = 2 |A ∩ R| / (|A| + |R|) sur des multi-ensembles d'appels (nom, arguments) ; None si tout est vide.

    L'intersection de deux `Counter` garde la plus petite multiplicité : un appel répété ne compte
    qu'autant de fois qu'il était attendu. Exemple : 2 appels attendus, un seul fait (correct) :
    2 × 1 / (2 + 1) = 2/3 ≈ 0.6667.
    """
    a = Counter((n, json.dumps(x, sort_keys=True)) for n, x in attendus)
    r = Counter((n, json.dumps(x, sort_keys=True)) for n, x in reels)
    total = sum(a.values()) + sum(r.values())
    return None if total == 0 else 2 * sum((a & r).values()) / total


def goal_accuracy(resultats: list[bool]) -> float | None:
    """Part des tâches dont l'objectif est atteint ; None si aucune tâche. Exemple : 14 sur 18 ≈ 0.7778."""
    return sum(resultats) / len(resultats) if resultats else None


def nombres(t: str) -> list[float]:
    """Nombres cités, lus à la française ; un pourcentage est divisé par 100 ; [REG-2] n'en est pas un.

    Exemple : « 5 558,32 AED ; 28,9 % [REG-1] » (espace fine) donne [5558.32, 0.289].
    """
    t = re.sub(r"\[[A-Z]+-\d+\]", "", t).replace(ESPACE_FINE, "")
    return [float(v.replace(",", ".")) / (100 if pct else 1) for v, pct in re.findall(r"(\d+(?:[.,]\d+)?)\s*(%?)", t)]


def fidelite_approchee(reponse: str, sources: list[str]) -> float | None:
    """Part des NOMBRES de la réponse que l'on retrouve (à `math.isclose` près) dans les sources ; None sans nombre.

    Exemple : « Mensualité 5 419,37 AED ; endettement estimé à 35 % » avec des sources qui contiennent
    5419.37 mais pas 0.35 : 1 / 2 = 0.5.
    """
    cites = nombres(reponse)
    if not cites:
        return None
    connus = [x for s in sources for x in nombres(s)]
    return sum(1 for c in cites if any(math.isclose(c, k, rel_tol=1e-9, abs_tol=1e-9) for k in connus)) / len(cites)


def moyenne_definie(valeurs: list) -> float | None:
    """Moyenne des valeurs définies (les None sont ignorés) ; None si aucune. Exemple : [1, None, 0.5] → 0.75."""
    definies = [v for v in valeurs if v is not None]
    return sum(definies) / len(definies) if definies else None


def noter(res: dict, sources: list[str], attendus: list, but: bool) -> dict:
    """Les trois mesures d'un cas : {"f1", "but", "fidelite"} ; la fidélité n'est définie que si fini.

    `res` est le résultat de `executer_agent` ; sa trace donne les appels réels (nom, arguments).
    """
    return {"f1": tool_call_f1(attendus, [(nom, args) for nom, args, _ in res["trace"]]), "but": but,
            "fidelite": fidelite_approchee(res["reponse"], sources) if res["statut"] == "fini" else None}


def rapport(notes: list[dict]) -> dict:
    """Agrège les notes : {"n", "succes", "taux", "wilson", "tool_f1", "fidelite"}.

    Exemple : 14 cas parfaits et 4 cas à (F1 2/3, fidélité 0.5, but faux) donnent succes 14,
    tool_f1 = (14 + 4 × 2/3) / 18 ≈ 0.926 et fidelite = (14 + 4 × 0.5) / 18 ≈ 0.889.
    """
    succes = sum(n["but"] for n in notes)
    return {"n": len(notes), "succes": succes, "taux": goal_accuracy([n["but"] for n in notes]),
            "wilson": wilson(succes, len(notes)), "tool_f1": moyenne_definie([n["f1"] for n in notes]),
            "fidelite": moyenne_definie([n["fidelite"] for n in notes])}


SEUILS = {"borne_basse": 0.80, "tool_f1": 0.95, "fidelite": 0.95}


def barriere_ci(rap: dict, seuils: dict = SEUILS) -> tuple[int, list[str]]:
    """(code de sortie, motifs) : 0 autorise le déploiement, 1 le bloque. N'appelle jamais `sys.exit`.

    Un motif lisible par seuil violé : borne basse de Wilson, Tool Call F1, fidélité (une moyenne
    indéfinie ne bloque pas). Aucun cas évalué : code 1.
    Exemple : 3 cas parfaits sur 3 : borne basse 0.438 < 0.8, donc (1, ["borne basse de Wilson 0.438 < 0.8"]).
    """
    if rap["n"] == 0:
        return 1, ["aucun cas évalué"]
    motifs = []
    if rap["wilson"][0] < seuils["borne_basse"]:
        motifs.append(f"borne basse de Wilson {rap['wilson'][0]:.3f} < {seuils['borne_basse']}")
    if rap["tool_f1"] is not None and rap["tool_f1"] < seuils["tool_f1"]:
        motifs.append(f"Tool Call F1 {rap['tool_f1']:.3f} < {seuils['tool_f1']}")
    if rap["fidelite"] is not None and rap["fidelite"] < seuils["fidelite"]:
        motifs.append(f"fidélité approchée {rap['fidelite']:.3f} < {seuils['fidelite']}")
    return (1 if motifs else 0), motifs
