"""Palier 09 — les garde-fous : ce que le code refuse même quand le modèle est convaincu du contraire.

Origine : étape 77, section 7 (politique, masquage, risque, veto, approbation, outil de virement) et
étape 66 (journal d'audit chaîné par SHA-256). Les globales de 77 (HORLOGE, JOURNAL, SESSION,
APPROBATEUR, VIREMENTS) deviennent des objets passés en paramètre.

- `autoriser` : refus par défaut ; seule une règle rôle → outil → portées autorise.
- `masquer` puis `JournalAudit.journaliser` : le journal ne voit jamais une donnée personnelle en clair,
  et chaque entrée porte le SHA-256 de (hash précédent + entrée) : modifier une ligne casse la chaîne.
- `score_risque`, `veto`, `decider` : R = w_s·s + w_g·g + w_u·u, deux seuils, veto non compensatoire.
- `Approbateur` : l'humain répond dans le délai, sinon c'est un refus.
- `proteger` compose avec le registre du palier 04 : politique, PUIS schéma, PUIS outil.
"""
import hashlib
import json
import re

from agent.metier import emirates_id_format_valide, iban_ae_valide
from agent.modele import Horloge
from agent.outils import ErreurOutil, RefusPolitique, Registre
from agent.schemas import objet

LECTURE = {"lecture"}
POLITIQUE = {                                  # rôle → outil → portées requises ; tout le reste est refusé
    "client_banque": dict.fromkeys(["rechercher_reglementation", "mensualite", "ratio_endettement",
                                    "convertir_aed_usd", "gratuite_fin_de_service", "tva"], LECTURE)
                     | {"initier_virement": {"lecture", "virement:initier"}},
    "assistant_public": dict.fromkeys(["rechercher_reglementation", "tva"], LECTURE),
}


def autoriser(role: str, outil: str, portees: set, politique: dict | None = None) -> tuple[bool, str]:
    """Refus par défaut, en trois tests : rôle inconnu, outil absent des règles du rôle, portée manquante.

    Exemple : `autoriser("assistant_public", "initier_virement", {"lecture"})` vaut
    (False, "outil initier_virement non autorisé pour le rôle assistant_public").
    """
    regles = (POLITIQUE if politique is None else politique).get(role)
    if regles is None:
        return False, f"rôle inconnu : {role or '(aucun)'}"
    requises = regles.get(outil)
    if requises is None:
        return False, f"outil {outil} non autorisé pour le rôle {role}"
    manquantes = sorted(requises - set(portees))
    if manquantes:
        return False, "portée manquante : " + ", ".join(manquantes)
    return True, "autorisé"


def masquer(texte_brut: str) -> str:
    """E-mail → [EMAIL] ; IBAN AE valide → [IBAN ••••3456] ; Emirates ID → [EMIRATES_ID ••••5671] ;
    +971 ou 05… → [TEL ••••4567] ; toute autre suite d'au moins 9 chiffres → [NUMERO ••••…].

    Exemple : "Emirates ID 784-1990-1234567-1, tél. +971 50 123 4567" devient
    "Emirates ID [EMIRATES_ID ••••5671], tél. [TEL ••••4567]".
    """
    def fin(m: re.Match) -> str:
        return "••••" + "".join(c for c in m.group(0) if c.isdigit())[-4:]

    t = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[EMAIL]", texte_brut)
    t = re.sub(r"\bAE\d{2}(?: ?\d){19}\b",
               lambda m: f"[IBAN {fin(m)}]" if iban_ae_valide(m.group(0)) else m.group(0), t)
    t = re.sub(r"\b784[- ]?\d{4}[- ]?\d{7}[- ]?\d\b",
               lambda m: f"[EMIRATES_ID {fin(m)}]" if emirates_id_format_valide(m.group(0)) else m.group(0), t)
    t = re.sub(r"(?:\+|\b00)971[ -]?\d(?:[ -]?\d){7,8}\b|\b05\d(?:[ -]?\d){7}\b", lambda m: f"[TEL {fin(m)}]", t)
    return re.sub(r"\d(?:[ -]?\d){8,}", lambda m: f"[NUMERO {fin(m)}]", t)


GENESE = "0" * 64


class JournalAudit:
    """Journal d'audit masqué et chaîné : hash_i = SHA-256(hash_{i−1} + corps_i), avec hash_0 = GENESE.

    `corps_i` est le JSON trié de {"t": instant simulé, "texte": texte masqué}. Exemple : après deux
    `journaliser`, `verifier()` vaut None ; si l'on modifie le texte de l'entrée 0, il vaut 0.
    """

    def __init__(self, horloge: Horloge | None = None) -> None:
        self.horloge = horloge if horloge is not None else Horloge()
        self.entrees: list[dict] = []

    @staticmethod
    def corps(t: float, texte: str) -> str:
        """Le texte haché d'une entrée. Exemple : `corps(0.0, "a")` vaut '{"t": 0.0, "texte": "a"}'."""
        return json.dumps({"t": t, "texte": texte}, sort_keys=True, ensure_ascii=False)

    def journaliser(self, evenement: str) -> str:
        """Masque PUIS écrit (le journal ne voit jamais le clair) ; rend le texte masqué écrit."""
        texte = masquer(evenement)
        precedent = self.entrees[-1]["hash"] if self.entrees else GENESE
        h = hashlib.sha256((precedent + self.corps(self.horloge.t, texte)).encode("utf-8")).hexdigest()
        self.entrees.append({"t": self.horloge.t, "texte": texte, "precedent": precedent, "hash": h})
        return texte

    def textes(self) -> list[str]:
        """Les textes masqués, dans l'ordre d'écriture."""
        return [e["texte"] for e in self.entrees]

    def verifier(self) -> int | None:
        """Indice de la première entrée incohérente, None si toute la chaîne est intacte."""
        precedent = GENESE
        for i, e in enumerate(self.entrees):
            attendu = hashlib.sha256((precedent + self.corps(e["t"], e["texte"])).encode("utf-8")).hexdigest()
            if e["precedent"] != precedent or e["hash"] != attendu:
                return i
            precedent = e["hash"]
        return None


POIDS = (0.4, 0.4, 0.2)             # (w_s, w_g, w_u) : sensibilité, gravité de l'action, incertitude
TAU_REVUE, TAU_BLOCAGE = 0.5, 0.75  # seuils illustratifs, à calibrer sur l'historique
MONTANT_VETO_AED = 25_000           # illustratif : au-delà, revue humaine obligatoire
SENSIBILITE = {"publique": 0.0, "interne": 0.3, "personnelle": 0.7, "sensible": 1.0}
GRAVITE = {"lecture": 0.0, "ecriture_reversible": 0.5, "irreversible": 1.0}
INCERTITUDE_MODELE = 0.1            # illustratif : par exemple 1 − fidélité mesurée (étape 67)


def gravite(type_action: str, montant_aed: float = 0.0, montant_ref_aed: float = 50_000) -> float:
    """g = max(gravité du type, min(1, montant / montant de référence)).

    Exemple : `gravite("irreversible", 180_000)` = max(1, min(1, 3.6)) = 1 ;
    `gravite("ecriture_reversible", 40_000)` = max(0.5, 0.8) = 0.8.
    """
    if type_action not in GRAVITE:
        raise ValueError(f"type d'action inconnu : {type_action}")
    if montant_aed < 0 or montant_ref_aed <= 0:
        raise ValueError("montant >= 0 et montant de référence > 0")
    return max(GRAVITE[type_action], min(1.0, montant_aed / montant_ref_aed))


def score_risque(s: float, g: float, u: float, poids: tuple[float, float, float] = POIDS) -> float:
    """R = w_s·s + w_g·g + w_u·u : une combinaison convexe, donc R ∈ [0, 1].

    Exemple (virement de 77) : `score_risque(0.7, 1.0, 0.1)` = 0.28 + 0.40 + 0.02 = 0.70.
    """
    if not all(0 <= x <= 1 for x in (s, g, u)):
        raise ValueError("chaque entrée doit être dans [0, 1]")
    if any(w < 0 for w in poids) or abs(sum(poids) - 1) > 1e-9:
        raise ValueError("les poids doivent être >= 0 et de somme 1")
    w_s, w_g, w_u = poids
    return w_s * s + w_g * g + w_u * u


def veto(type_action: str, montant_aed: float) -> bool:
    """Règle dure, hors du score : irréversible OU montant >= 25 000 AED ⇒ jamais sans humain.

    Exemple : `veto("lecture", 30_000)` est vrai ; `veto("ecriture_reversible", 2_500)` est faux.
    """
    return type_action == "irreversible" or montant_aed >= MONTANT_VETO_AED


def decider(r: float, veto_actif: bool, tau_revue: float = TAU_REVUE, tau_blocage: float = TAU_BLOCAGE) -> str:
    """Décision : « bloquer » si R >= τ_blocage ; sinon « revue » si R >= τ_revue ou veto ; sinon « autoriser ».

    Exemple : `decider(0.70, True)` = "revue" ; `decider(0.46, False)` = "autoriser" ;
    `decider(0.88, True)` = "bloquer".
    """
    if not 0 <= tau_revue < tau_blocage <= 1:
        raise ValueError("il faut 0 <= tau_revue < tau_blocage <= 1")
    if r >= tau_blocage:
        return "bloquer"
    if r >= tau_revue or veto_actif:
        return "revue"
    return "autoriser"


class Approbateur:
    """Approbation humaine sur horloge simulée : pas de réponse dans le délai = refus.

    `reponses` contient les réponses simulées de l'humain, (décision, délai en secondes) ou None.
    Exemple : sans réponse, `demander("virement")` avance l'horloge de 120 s et rend
    (False, "pas de réponse en 120 s : refus par défaut").
    """

    def __init__(self, horloge: Horloge, journal: JournalAudit, delai_s: float = 120.0) -> None:
        if delai_s <= 0:
            raise ValueError("délai > 0")
        self.horloge, self.journal, self.delai_s = horloge, journal, delai_s
        self.reponses: list = []

    def demander(self, demande: str) -> tuple[bool, str]:
        """Rend (approuvé ?, décision ou motif), et journalise la demande et sa décision."""
        reponse = self.reponses.pop(0) if self.reponses else None
        if reponse is None or reponse[1] > self.delai_s:
            self.horloge.avancer(self.delai_s)
            self.journal.journaliser(f"approbation : {demande} -> refus par délai")
            return False, f"pas de réponse en {self.delai_s:.0f} s : refus par défaut"
        decision, delai = reponse
        self.horloge.avancer(delai)
        self.journal.journaliser(f"approbation : {demande} -> {decision}")
        return decision == "approuvé", decision


def proteger(registre: Registre, session: dict, journal: JournalAudit, politique: dict | None = None) -> dict:
    """Le dictionnaire nom → appelable pour la boucle : politique (journalisée), PUIS schéma, PUIS outil.

    `session` ({"role", "portees"}) vient de l'authentification, jamais du modèle ; il est relu à
    chaque appel. Un refus lève `RefusPolitique` avant toute validation.
    """
    def enveloppe(nom: str):
        porte = registre.porte(nom)

        def appeler(**arguments):
            ok, motif = autoriser(session["role"], nom, session["portees"], politique)
            journal.journaliser(f"politique {session['role']} -> {nom} : {motif}")
            if not ok:
                raise RefusPolitique(motif)
            return porte(**arguments)
        return appeler
    return {nom: enveloppe(nom) for nom in registre.outils}


SCHEMA_VIREMENT = objet({
    "iban": {"type": "string", "pattern": "^AE[0-9]{2}( ?[0-9]){19}$"},
    "montant_aed": {"type": "number", "exclusiveMinimum": 0},
    "motif": {"type": "string", "minLength": 1, "maxLength": 140}})


def enregistrer_virement(registre: Registre, approbateur: Approbateur, journal: JournalAudit, virements: list,
                         incertitude: float = INCERTITUDE_MODELE) -> Registre:
    """Enregistre "initier_virement" : IBAN mod 97, risque, décision journalisée, approbation DANS l'outil.

    La seule ligne qui modifie le monde (`virements.append`) est la dernière : « bloquer » et un refus
    humain lèvent `ErreurOutil` avant elle. Exemple : 180 000 AED, s = 0.7, u = 0.1 → R = 0.70, veto,
    « revue » ; sans réponse humaine, `ErreurOutil("refusé par l'humain : pas de réponse en 120 s : …")`.
    """
    @registre.outil("initier_virement", "Virement sortant en AED vers un IBAN émirien. Action IRRÉVERSIBLE.",
                    SCHEMA_VIREMENT)
    def outil_virement(iban: str, montant_aed: float, motif: str) -> dict:
        if not iban_ae_valide(iban):
            raise ValueError("IBAN AE invalide (contrôle mod 97)")
        r = score_risque(SENSIBILITE["personnelle"], gravite("irreversible", montant_aed), incertitude)
        decision = decider(r, veto("irreversible", montant_aed))
        journal.journaliser(f"risque virement {iban} de {montant_aed} AED : R = {r:.2f}, veto, décision {decision}")
        if decision == "bloquer":
            raise ErreurOutil(f"bloqué par le garde-fou : R = {r:.2f} >= {TAU_BLOCAGE}")
        if decision == "revue":                # l'approbation est DANS l'outil, à chaque appel
            ok, motif_humain = approbateur.demander(f"virement de {montant_aed} AED vers {iban}")
            if not ok:
                raise ErreurOutil(f"refusé par l'humain : {motif_humain}")
        virements.append({"iban": iban, "montant_aed": montant_aed, "motif": motif})
        return {"statut": "exécuté", "montant_aed": montant_aed}

    return registre
