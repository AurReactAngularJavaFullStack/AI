"""Palier 08 — la planification : ordonner les tâches d'un dossier, les paralléliser, trouver le chemin critique.

Origine : NOUVEAU module, d'après les étapes 42 (graphes d'orchestration, chemin critique) et 44
(tri topologique de Kahn) du parcours. Un plan est un graphe orienté sans cycle (DAG) : chaque tâche
a une durée et des prérequis ; un arc u → v signifie « u doit finir avant que v commence ».

- `tri_topologique` : Kahn, avec départage ALPHABÉTIQUE parmi les tâches prêtes (ordre unique,
  reproductible) ; un cycle lève `ValueError` en le nommant.
- `vagues` : les tâches qui peuvent partir ensemble (même profondeur dans le graphe).
- `calendrier` et `chemin_critique` : dates au plus tôt, avec des exécutants en nombre illimité ;
  fin(v) = durée(v) + max(fin(u) pour u prérequis de v). La durée du plan est le plus long chemin.
"""
import heapq
from dataclasses import dataclass


@dataclass(frozen=True)
class Tache:
    """Une tâche du plan : un nom unique, une durée >= 0 (secondes simulées), des prérequis.

    Exemple : `Tache("calculer_ratio", 0.6, ("calculer_mensualite",))`.
    """
    nom: str
    duree: float
    prerequis: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.nom:
            raise ValueError("une tâche a un nom non vide")
        if self.duree < 0:
            raise ValueError(f"durée négative pour {self.nom}")
        object.__setattr__(self, "prerequis", tuple(dict.fromkeys(self.prerequis)))   # tuple, sans doublon


def _graphe(taches: list[Tache]) -> tuple[dict, dict, dict]:
    """Successeurs, prérequis et degrés entrants ; refuse les doublons et les prérequis inconnus."""
    par_nom: dict[str, Tache] = {}
    for t in taches:
        if t.nom in par_nom:
            raise ValueError(f"tâche en double : {t.nom}")
        par_nom[t.nom] = t
    succ = {n: [] for n in par_nom}
    for t in taches:
        for p in t.prerequis:
            if p not in par_nom:
                raise ValueError(f"prérequis inconnu : {p} (tâche {t.nom})")
            succ[p].append(t.nom)
    entrant = {t.nom: len(t.prerequis) for t in taches}   # prérequis distincts : Tache les a dédoublonnés
    return par_nom, succ, entrant


def _nommer_cycle(restants: set[str], par_nom: dict) -> list[str]:
    """Remonte les prérequis parmi les tâches bloquées jusqu'à repasser par une tâche déjà vue."""
    vus: dict[str, int] = {}
    chemin: list[str] = []
    v = min(restants)
    while v not in vus:
        vus[v] = len(chemin)
        chemin.append(v)
        v = min(p for p in par_nom[v].prerequis if p in restants)   # existe : v est bloquée
    boucle = chemin[vus[v]:][::-1]                                  # remise dans le sens des arcs
    i = boucle.index(min(boucle))
    boucle = boucle[i:] + boucle[:i]                                # commence par le plus petit nom
    return boucle + [boucle[0]]


def tri_topologique(taches: list[Tache]) -> list[str]:
    """Ordre d'exécution où chaque prérequis passe avant la tâche qui l'attend (Kahn).

    Parmi les tâches prêtes (degré entrant nul), on prend toujours la plus petite par ordre
    alphabétique (tas binaire) : l'ordre rendu est unique. S'il reste des tâches, elles sont sur un
    cycle ou derrière un cycle : `ValueError("cycle détecté : a → b → a")`.
    Exemple (dossier de crédit) : ["lire_memoire", "calculer_mensualite", "calculer_ratio",
    "convertir_usd", "rechercher_regles", "verifier_identite", "evaluer_risque", "rediger_reponse"].
    """
    par_nom, succ, entrant = _graphe(taches)
    pretes = [n for n, d in entrant.items() if d == 0]
    heapq.heapify(pretes)
    ordre = []
    while pretes:
        n = heapq.heappop(pretes)
        ordre.append(n)
        for v in succ[n]:
            entrant[v] -= 1
            if entrant[v] == 0:               # son dernier prérequis vient de finir
                heapq.heappush(pretes, v)
    if len(ordre) != len(par_nom):
        cycle = _nommer_cycle(set(par_nom) - set(ordre), par_nom)
        raise ValueError("cycle détecté : " + " → ".join(cycle))
    return ordre


def vagues(taches: list[Tache]) -> list[list[str]]:
    """Les vagues de Kahn : la vague k+1 contient les tâches dont le dernier prérequis est dans la vague k.

    Chaque vague est triée par nom. Exemple (dossier de crédit) : [["lire_memoire", "rechercher_regles",
    "verifier_identite"], ["calculer_mensualite"], ["calculer_ratio", "convertir_usd"], ["evaluer_risque"],
    ["rediger_reponse"]].
    """
    ordre = tri_topologique(taches)               # valide le graphe (doublons, inconnus, cycles)
    par_nom = {t.nom: t for t in taches}
    niveau: dict[str, int] = {}
    for n in ordre:
        niveau[n] = 1 + max((niveau[p] for p in par_nom[n].prerequis), default=-1)
    resultat: list[list[str]] = [[] for _ in range(max(niveau.values(), default=-1) + 1)]
    for n in sorted(niveau):
        resultat[niveau[n]].append(n)
    return resultat


def calendrier(taches: list[Tache]) -> dict[str, tuple[float, float]]:
    """Dates au plus tôt {nom: (début, fin)} : une tâche démarre dès que TOUS ses prérequis sont finis.

    Exemple (dossier de crédit) : "evaluer_risque" démarre à max(1.5, 1.9, 2.0) = 2.0 et finit à 3.2.
    """
    par_nom = {t.nom: t for t in taches}
    dates: dict[str, tuple[float, float]] = {}
    for n in tri_topologique(taches):
        debut = max((dates[p][1] for p in par_nom[n].prerequis), default=0.0)
        dates[n] = (debut, debut + par_nom[n].duree)
    return dates


def chemin_critique(taches: list[Tache]) -> tuple[float, list[str]]:
    """(durée minimale du plan, chemin critique) : la plus longue chaîne de durées, de la source à la fin.

    On part de la tâche qui finit le plus tard et l'on remonte, à chaque pas, le prérequis qui finit le
    plus tard (égalité : le plus petit nom). Retarder une tâche du chemin retarde tout le plan.
    Exemple (dossier de crédit) : (5.7, ["rechercher_regles", "evaluer_risque", "rediger_reponse"]),
    soit 2.0 + 1.2 + 2.5 secondes, contre 9.5 s en séquentiel.
    """
    if not taches:
        return 0.0, []
    dates = calendrier(taches)
    par_nom = {t.nom: t for t in taches}
    n = min(dates, key=lambda m: (-dates[m][1], m))
    chemin = [n]
    while par_nom[n].prerequis:
        n = min(par_nom[n].prerequis, key=lambda p: (-dates[p][1], p))
        chemin.append(n)
    return dates[chemin[0]][1], chemin[::-1]


def duree_par_vagues(taches: list[Tache]) -> float:
    """Calendrier SYNCHRONISÉ : chaque vague attend la plus lente de la précédente. Borne >= chemin critique.

    Exemple (dossier de crédit) : 2.0 + 0.8 + 0.6 + 1.2 + 2.5 = 7.1 s.
    """
    par_nom = {t.nom: t for t in taches}
    return sum(max(par_nom[n].duree for n in v) for v in vagues(taches))


def dossier_credit() -> list[Tache]:
    """Plan illustratif d'un dossier de crédit à Dubaï : 8 tâches, durées en secondes simulées."""
    return [
        Tache("verifier_identite", 1.5),                     # format de l'Emirates ID, liste de sanctions
        Tache("lire_memoire", 0.5),                          # salaire et crédits en cours (palier 06)
        Tache("rechercher_regles", 2.0),                     # RAG hybride sur les règles CBUAE (palier 07)
        Tache("calculer_mensualite", 0.8, ("lire_memoire",)),
        Tache("calculer_ratio", 0.6, ("calculer_mensualite",)),
        Tache("convertir_usd", 0.4, ("calculer_mensualite",)),
        Tache("evaluer_risque", 1.2, ("verifier_identite", "calculer_ratio", "rechercher_regles")),
        Tache("rediger_reponse", 2.5, ("evaluer_risque", "convertir_usd")),
    ]
