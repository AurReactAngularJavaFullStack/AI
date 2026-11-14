"""Palier 08 — la planification : ordonner les tâches d'un dossier, les paralléliser, trouver le chemin critique.

SQUELETTE À COMPLÉTER. Chaque fonction lève `NotImplementedError` tant que tu ne l'as pas écrite.
Ordre conseillé (celui de README.md) : Tache.__post_init__ → _graphe → tri_topologique → _nommer_cycle
→ vagues → calendrier → chemin_critique → duree_par_vagues. Les deux fonctions privées (_graphe,
_nommer_cycle) sont une proposition de découpage : tu peux t'organiser autrement, seuls les noms
publics sont testés.

Un plan est un graphe orienté sans cycle (DAG) : chaque tâche a une durée et des prérequis ; un arc
u → v signifie « u doit finir avant que v commence ».
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
        """Refuse un nom vide et une durée négative (ValueError) ; range `prerequis` en tuple sans doublon.

        Exemple : `Tache("calculer_ratio", 0.6, ["calculer_mensualite"]).prerequis` vaut ("calculer_mensualite",) ;
        `Tache("v", 1, ("a", "a", "z")).prerequis` vaut ("a", "z") (l'ordre de première apparition est gardé).
        """
        # TODO 1 : nom vide → ValueError ; durée < 0 → ValueError (une durée nulle est permise).
        # TODO 2 : la classe est gelée (frozen=True) : self.prerequis = … lève une erreur.
        #          Passer par object.__setattr__(self, "prerequis", …) pour ranger un tuple
        #          sans doublon, dans l'ordre (indice : les clés d'un dict sont uniques et ordonnées).
        raise NotImplementedError("Palier 08 : à coder — voir README.md")


def _graphe(taches: list[Tache]) -> tuple[dict, dict, dict]:
    """Successeurs, prérequis et degrés entrants ; refuse les doublons et les prérequis inconnus.

    Rend (par_nom, succ, entrant) : nom → Tache, nom → liste des tâches qui l'attendent,
    nom → nombre de prérequis (distincts, puisque Tache les a dédoublonnés).
    """
    # TODO 1 : construire par_nom ; un nom déjà vu → ValueError("tâche en double : …").
    # TODO 2 : succ[p] reçoit t.nom pour chaque prérequis p de t ; un p inconnu → ValueError.
    # TODO 3 : entrant[nom] = nombre de prérequis de la tâche (autant que d'entrées dans succ).
    raise NotImplementedError("Palier 08 : à coder — voir README.md")


def _nommer_cycle(restants: set[str], par_nom: dict) -> list[str]:
    """Remonte les prérequis parmi les tâches bloquées jusqu'à repasser par une tâche déjà vue.

    Rend le cycle dans le sens des arcs, en commençant et finissant par son plus petit nom :
    ["a", "b", "c", "a"].
    """
    # TODO 1 : partir de min(restants) ; tant que la tâche n'a pas déjà été vue, noter sa position
    #          dans le chemin, puis passer au plus petit de ses prérequis qui est encore dans restants.
    # TODO 2 : la boucle est la fin du chemin à partir de la première visite de la tâche revue ;
    #          la retourner (on a remonté les arcs à l'envers), la faire commencer par son plus petit nom,
    #          puis répéter le premier nom à la fin.
    raise NotImplementedError("Palier 08 : à coder — voir README.md")


def tri_topologique(taches: list[Tache]) -> list[str]:
    """Ordre d'exécution où chaque prérequis passe avant la tâche qui l'attend (Kahn).

    Parmi les tâches prêtes (degré entrant nul), on prend toujours la plus petite par ordre
    alphabétique (tas binaire) : l'ordre rendu est unique. S'il reste des tâches, elles sont sur un
    cycle ou derrière un cycle : `ValueError("cycle détecté : a → b → a")`.
    Exemple (dossier de crédit) : ["lire_memoire", "calculer_mensualite", "calculer_ratio",
    "convertir_usd", "rechercher_regles", "verifier_identite", "evaluer_risque", "rediger_reponse"].
    """
    # TODO 1 : obtenir par_nom, succ, entrant ; mettre les tâches de degré entrant nul dans un tas (heapq).
    # TODO 2 : tant que le tas n'est pas vide : sortir le plus petit nom, l'ajouter à l'ordre,
    #          décrémenter le degré entrant de chacun de ses successeurs ; pousser ceux qui tombent à 0.
    # TODO 3 : si l'ordre ne contient pas toutes les tâches → ValueError("cycle détecté : " + cycle nommé).
    raise NotImplementedError("Palier 08 : à coder — voir README.md")


def vagues(taches: list[Tache]) -> list[list[str]]:
    """Les vagues de Kahn : la vague k+1 contient les tâches dont le dernier prérequis est dans la vague k.

    Chaque vague est triée par nom. Exemple (dossier de crédit) : [["lire_memoire", "rechercher_regles",
    "verifier_identite"], ["calculer_mensualite"], ["calculer_ratio", "convertir_usd"], ["evaluer_risque"],
    ["rediger_reponse"]].
    """
    # TODO 1 : appeler tri_topologique (il valide aussi le graphe).
    # TODO 2 : dans cet ordre, niveau(v) = 1 + max(niveau des prérequis), et 0 pour une tâche sans prérequis.
    # TODO 3 : ranger chaque nom dans la liste de son niveau, chaque liste triée par nom ; plan vide → [].
    raise NotImplementedError("Palier 08 : à coder — voir README.md")


def calendrier(taches: list[Tache]) -> dict[str, tuple[float, float]]:
    """Dates au plus tôt {nom: (début, fin)} : une tâche démarre dès que TOUS ses prérequis sont finis.

    Exemple (dossier de crédit) : "evaluer_risque" démarre à max(1.5, 1.9, 2.0) = 2.0 et finit à 3.2.
    """
    # TODO : parcourir l'ordre topologique ; début = max des fins des prérequis (0.0 s'il n'y en a pas) ;
    #        fin = début + durée.
    raise NotImplementedError("Palier 08 : à coder — voir README.md")


def chemin_critique(taches: list[Tache]) -> tuple[float, list[str]]:
    """(durée minimale du plan, chemin critique) : la plus longue chaîne de durées, de la source à la fin.

    On part de la tâche qui finit le plus tard et l'on remonte, à chaque pas, le prérequis qui finit le
    plus tard (égalité : le plus petit nom). Retarder une tâche du chemin retarde tout le plan.
    Exemple (dossier de crédit) : (5.7, ["rechercher_regles", "evaluer_risque", "rediger_reponse"]),
    soit 2.0 + 1.2 + 2.5 secondes, contre 9.5 s en séquentiel.
    """
    # TODO 1 : plan vide → (0.0, []).
    # TODO 2 : calculer le calendrier ; partir de la tâche de plus grande fin (égalité : plus petit nom).
    # TODO 3 : tant que la tâche courante a des prérequis, passer à celui qui finit le plus tard.
    # TODO 4 : rendre (fin de la dernière tâche, chemin remis dans l'ordre d'exécution).
    raise NotImplementedError("Palier 08 : à coder — voir README.md")


def duree_par_vagues(taches: list[Tache]) -> float:
    """Calendrier SYNCHRONISÉ : chaque vague attend la plus lente de la précédente. Borne >= chemin critique.

    Exemple (dossier de crédit) : 2.0 + 0.8 + 0.6 + 1.2 + 2.5 = 7.1 s.
    """
    # TODO : somme, sur les vagues, de la plus grande durée de la vague.
    raise NotImplementedError("Palier 08 : à coder — voir README.md")


def dossier_credit() -> list[Tache]:
    """Plan illustratif d'un dossier de crédit à Dubaï : 8 tâches, durées en secondes simulées."""
    # Données fournies : rien à coder ici. Elles ne fonctionnent qu'une fois Tache.__post_init__ écrit.
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
