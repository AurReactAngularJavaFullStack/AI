"""Palier 11 — la production : ce que coûte une tâche, combien en passent, comment survivre aux erreurs.

Origine : NOUVEAU module, d'après les étapes 66 (seau à jetons), 70 (p95) et 72 (coût des tokens,
cache de préfixe) du parcours. Tous les prix sont ILLUSTRATIFS (3 USD et 15 USD par million de tokens
d'entrée et de sortie, comme à l'étape 72) : on les vérifie sur la grille du fournisseur avant tout
chiffrage. Les montants sont convertis en AED à la parité fixe de 3,6725.

Rien n'attend en temps réel : le seau à jetons et les relances avancent une `Horloge` simulée, et la
gigue des relances est tirée d'un `random.Random(graine)` local, jamais de l'état global.
"""
import math
import random

from agent.metier import AED_PAR_USD
from agent.modele import Horloge

PRIX_ENTREE_USD_MTOK = 3.00        # illustratif : USD par million de tokens d'entrée
PRIX_SORTIE_USD_MTOK = 15.00       # illustratif : USD par million de tokens de sortie
FACTEUR_LECTURE_CACHE = 0.10       # un token relu dans le cache coûte 0,1 fois le prix d'entrée
FACTEUR_ECRITURE_CACHE = 1.25      # un token écrit dans le cache coûte 1,25 fois le prix d'entrée


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


class SeauAJetons:
    """Seau à jetons (étape 66) : capacité C, recharge r jetons par seconde (horloge simulée).

    Une demande de coût c passe si le seau contient au moins c jetons ; sinon elle est refusée et le
    seau ne change pas. Sur toute fenêtre de durée T, il ne passe jamais plus de C + r·T jetons.
    Exemple : C = 10 000, r = 50/s, demandes de 3 000 à t = 0 : 7 000, 4 000, 1 000 restants, la 4e
    est refusée ; à t = 40 s, le seau a regagné 2 000 jetons (3 000 au total) et la demande passe.
    """

    def __init__(self, capacite: float, recharge_par_s: float, horloge: Horloge) -> None:
        if capacite <= 0 or recharge_par_s < 0:
            raise ValueError("capacité > 0 et recharge >= 0")
        self.capacite = capacite
        self.recharge = recharge_par_s
        self.horloge = horloge
        self.jetons = float(capacite)
        self.dernier = horloge.t

    def consommer(self, cout: float) -> bool:
        """Recharge pour le temps écoulé (sans dépasser C), puis accepte la demande si cout <= jetons."""
        if cout < 0:
            raise ValueError("coût >= 0")
        self.jetons = min(self.capacite, self.jetons + self.recharge * (self.horloge.t - self.dernier))
        self.dernier = self.horloge.t
        if cout <= self.jetons:
            self.jetons -= cout
            return True
        return False


def attente_backoff(tentative: int, base_s: float = 1.0, plafond_s: float = 30.0, gigue: float = 0.0,
                    rng: random.Random | None = None) -> float:
    """Attente avant la relance n° `tentative` (>= 1) : a = min(P, b · 2^(n−1)) × (1 − g · u), u ∈ [0, 1).

    La gigue ne fait que RACCOURCIR l'attente, d'au plus la fraction g : elle désynchronise des
    clients qui ont échoué ensemble, et le plafond P tient toujours. Sans `rng` (ou g = 0), pas de gigue.
    Exemple : b = 1 s, P = 30 s : 1, 2, 4, 8, 16, 30, 30… ; avec g = 0.5 et u = 0.4, la 3e attente
    vaut 4 × (1 − 0.2) = 3.2 s.
    """
    if tentative < 1:
        raise ValueError("tentative >= 1")
    if base_s <= 0 or plafond_s < base_s:
        raise ValueError("il faut 0 < base_s <= plafond_s")
    if not 0 <= gigue <= 1:
        raise ValueError("la gigue est dans [0, 1]")
    attente = min(plafond_s, base_s * 2 ** (tentative - 1))
    if rng is not None and gigue > 0:
        attente *= 1 - gigue * rng.random()
    return attente


class ErreurTransitoire(Exception):
    """Erreur qui vaut d'être relancée : surcharge, limite de débit (429), coupure réseau."""


def executer_avec_relances(fonction, max_tentatives: int = 4, base_s: float = 1.0, plafond_s: float = 30.0,
                           gigue: float = 0.1, graine: int = 0, horloge: Horloge | None = None) -> dict:
    """Appelle `fonction()` ; après une `ErreurTransitoire`, attend (horloge simulée) puis relance.

    Rend {"statut": "succes" | "echec", "resultat", "tentatives", "attentes", "erreurs"}. Toute autre
    exception (argument invalide, refus de politique…) remonte aussitôt : la relancer ne la corrigerait
    pas. Il n'y a pas d'attente après la dernière tentative ratée.
    Exemple : une fonction qui échoue deux fois puis réussit, sans gigue : tentatives 3, attentes [1, 2],
    horloge avancée de 3 s.
    """
    if max_tentatives < 1:
        raise ValueError("max_tentatives >= 1")
    rng = random.Random(graine)
    attentes: list[float] = []
    erreurs: list[str] = []
    for tentative in range(1, max_tentatives + 1):
        try:
            resultat = fonction()
            return {"statut": "succes", "resultat": resultat, "tentatives": tentative,
                    "attentes": attentes, "erreurs": erreurs}
        except ErreurTransitoire as e:
            erreurs.append(str(e))
            if tentative < max_tentatives:
                a = attente_backoff(tentative, base_s, plafond_s, gigue, rng)
                attentes.append(a)
                if horloge is not None:
                    horloge.avancer(a)
    return {"statut": "echec", "resultat": None, "tentatives": max_tentatives, "attentes": attentes, "erreurs": erreurs}


def percentile(valeurs: list[float], p: float) -> float:
    """Percentile au rang le plus proche : la valeur de rang ⌈p × n / 100⌉ dans la liste triée.

    Toujours une valeur observée, jamais une interpolation. Exemple : pour 20 latences, le p95 est la
    19e plus petite (⌈95 × 20 / 100⌉ = 19) ; la médiane (p = 50) est la 10e. On multiplie AVANT de
    diviser : `7 / 100 * 100` vaut 7.000000000000001 en flottant, et son plafond 8 au lieu de 7.
    """
    if not valeurs:
        raise ValueError("liste vide : le percentile n'est pas défini")
    if not 0 < p <= 100:
        raise ValueError("p est dans ]0, 100]")
    triees = sorted(valeurs)
    rang = math.ceil(p * len(triees) / 100)   # p × n est exact pour des entiers : pas de 7,000…01
    return triees[rang - 1]


def p95(valeurs: list[float]) -> float:
    """Le 95e percentile au rang le plus proche : une requête sur vingt est plus lente que lui.

    Exemple : les latences 1.0, 1.1, …, 2.9 s (20 valeurs, pas de 0.1) ont un p95 de 2.8 s.
    """
    return percentile(valeurs, 95)


def budget_restant(budget_aed: float, depenses_aed: list[float]) -> float:
    """Budget moins la somme des dépenses ; négatif en cas de dépassement.

    Exemple : budget journalier de 50 AED, dépenses [12.5, 20.25, 7.0] : 50 − 39.75 = 10.25 AED.
    """
    if budget_aed < 0 or any(d < 0 for d in depenses_aed):
        raise ValueError("budget et dépenses sont >= 0")
    return budget_aed - sum(depenses_aed)


def taches_possibles(reste_aed: float, cout_tache_aed: float) -> int:
    """Nombre de tâches encore finançables : ⌊reste / coût⌋, 0 si le reste est négatif ou nul.

    Exemple : 10.25 AED à 0.141024 AED la tâche : ⌊72.68…⌋ = 72 tâches.
    """
    if cout_tache_aed <= 0:
        raise ValueError("coût d'une tâche > 0")
    return max(0, math.floor(reste_aed / cout_tache_aed))
