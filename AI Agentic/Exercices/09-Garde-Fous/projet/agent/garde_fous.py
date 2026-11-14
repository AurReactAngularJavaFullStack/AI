"""Palier 09 — les garde-fous : ce que le code refuse même quand le modèle est convaincu du contraire.

SQUELETTE À COMPLÉTER. Les signatures, les docstrings et les constantes sont celles de la solution :
ne les change pas, les tests en dépendent. Remplace chaque `raise NotImplementedError(...)` par le code
demandé, dans l'ordre du README : politique, masquage, journal, risque, veto et décision, approbation,
porte protégée, outil de virement.

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

    Rend (True, "autorisé") ou (False, motif), avec exactement l'un de ces trois motifs :
    "rôle inconnu : <rôle>" (« (aucun) » si le rôle est vide), "outil <outil> non autorisé pour le
    rôle <rôle>", "portée manquante : <portées triées, séparées par ', '>".
    `politique` vaut None pour utiliser POLITIQUE ; `portees` peut être n'importe quel itérable.

    Exemple : `autoriser("assistant_public", "initier_virement", {"lecture"})` vaut
    (False, "outil initier_virement non autorisé pour le rôle assistant_public").
    """
    # TODO 1 : choisir la table (POLITIQUE si `politique` vaut None, attention : un dict vide n'est pas None).
    # TODO 2 : rôle absent de la table → refus ; outil absent des règles du rôle → refus.
    # TODO 3 : portées requises moins portées présentes (différence d'ensembles), triées → refus si non vide.
    raise NotImplementedError("Palier 09 : à coder — voir README.md")


def masquer(texte_brut: str) -> str:
    """E-mail → [EMAIL] ; IBAN AE valide → [IBAN ••••3456] ; Emirates ID → [EMIRATES_ID ••••5671] ;
    +971 ou 05… → [TEL ••••4567] ; toute autre suite d'au moins 9 chiffres → [NUMERO ••••…].

    Les quatre chiffres affichés sont les quatre DERNIERS chiffres du passage reconnu (séparateurs
    retirés). Un IBAN dont la clé mod 97 est fausse n'est pas étiqueté IBAN : il tombe dans le filet
    [NUMERO …]. Une suite de moins de 9 chiffres (un montant) reste en clair.

    Exemple : "Emirates ID 784-1990-1234567-1, tél. +971 50 123 4567" devient
    "Emirates ID [EMIRATES_ID ••••5671], tél. [TEL ••••4567]".
    """
    # TODO 4 : une petite fonction locale qui rend "••••" + les 4 derniers chiffres d'une correspondance.
    # TODO 5 : cinq re.sub, DANS CET ORDRE : e-mail, IBAN (iban_ae_valide), Emirates ID
    #          (emirates_id_format_valide), téléphone, puis le filet des longs numéros.
    #          Pourquoi cet ordre ? Le filet attraperait tout le reste avant les règles qui savent nommer.
    raise NotImplementedError("Palier 09 : à coder — voir README.md")


GENESE = "0" * 64


class JournalAudit:
    """Journal d'audit masqué et chaîné : hash_i = SHA-256(hash_{i−1} + corps_i), avec hash_0 = GENESE.

    `corps_i` est le JSON trié de {"t": instant simulé, "texte": texte masqué}. Exemple : après deux
    `journaliser`, `verifier()` vaut None ; si l'on modifie le texte de l'entrée 0, il vaut 0.

    Attributs publics (les tests les lisent) : `horloge` (une `Horloge`, neuve si None est passé) et
    `entrees`, liste de dictionnaires {"t", "texte", "precedent", "hash"}, dans l'ordre d'écriture.
    """

    def __init__(self, horloge: Horloge | None = None) -> None:
        # TODO 6 : ranger l'horloge (en créer une si None) et une liste d'entrées vide.
        raise NotImplementedError("Palier 09 : à coder — voir README.md")

    @staticmethod
    def corps(t: float, texte: str) -> str:
        """Le texte haché d'une entrée. Exemple : `corps(0.0, "a")` vaut '{"t": 0.0, "texte": "a"}'."""
        # TODO 7 : json.dumps avec clés triées, sans échapper les accents.
        raise NotImplementedError("Palier 09 : à coder — voir README.md")

    def journaliser(self, evenement: str) -> str:
        """Masque PUIS écrit (le journal ne voit jamais le clair) ; rend le texte masqué écrit."""
        # TODO 8 : masquer ; prendre le hash de la dernière entrée (GENESE si le journal est vide) ;
        #          hacher precedent + corps(t, texte) en SHA-256 hexadécimal ; ajouter l'entrée.
        raise NotImplementedError("Palier 09 : à coder — voir README.md")

    def textes(self) -> list[str]:
        """Les textes masqués, dans l'ordre d'écriture."""
        # TODO 9 : une compréhension de liste.
        raise NotImplementedError("Palier 09 : à coder — voir README.md")

    def verifier(self) -> int | None:
        """Indice de la première entrée incohérente, None si toute la chaîne est intacte."""
        # TODO 10 : repartir de GENESE, RECALCULER chaque hash depuis t et texte, comparer « precedent »
        #           et « hash » ; ne jamais faire confiance aux valeurs stockées.
        raise NotImplementedError("Palier 09 : à coder — voir README.md")


POIDS = (0.4, 0.4, 0.2)             # (w_s, w_g, w_u) : sensibilité, gravité de l'action, incertitude
TAU_REVUE, TAU_BLOCAGE = 0.5, 0.75  # seuils illustratifs, à calibrer sur l'historique
MONTANT_VETO_AED = 25_000           # illustratif : au-delà, revue humaine obligatoire
SENSIBILITE = {"publique": 0.0, "interne": 0.3, "personnelle": 0.7, "sensible": 1.0}
GRAVITE = {"lecture": 0.0, "ecriture_reversible": 0.5, "irreversible": 1.0}
INCERTITUDE_MODELE = 0.1            # illustratif : par exemple 1 − fidélité mesurée (étape 67)


def gravite(type_action: str, montant_aed: float = 0.0, montant_ref_aed: float = 50_000) -> float:
    """g = max(gravité du type, min(1, montant / montant de référence)).

    Erreurs : type absent de GRAVITE → ValueError ; montant < 0 ou montant de référence <= 0 → ValueError.
    Exemple : `gravite("irreversible", 180_000)` = max(1, min(1, 3.6)) = 1 ;
    `gravite("ecriture_reversible", 40_000)` = max(0.5, 0.8) = 0.8.
    """
    # TODO 11 : valider, puis une seule ligne de calcul.
    raise NotImplementedError("Palier 09 : à coder — voir README.md")


def score_risque(s: float, g: float, u: float, poids: tuple[float, float, float] = POIDS) -> float:
    """R = w_s·s + w_g·g + w_u·u : une combinaison convexe, donc R ∈ [0, 1].

    Erreurs : une entrée hors de [0, 1] → ValueError ; un poids négatif ou une somme des poids
    différente de 1 (à 1e-9 près) → ValueError.
    Exemple (virement de 77) : `score_risque(0.7, 1.0, 0.1)` = 0.28 + 0.40 + 0.02 = 0.70.
    """
    # TODO 12 : les deux validations (ce sont elles qui garantissent R ∈ [0, 1]), puis la somme pondérée.
    raise NotImplementedError("Palier 09 : à coder — voir README.md")


def veto(type_action: str, montant_aed: float) -> bool:
    """Règle dure, hors du score : irréversible OU montant >= 25 000 AED ⇒ jamais sans humain.

    Exemple : `veto("lecture", 30_000)` est vrai ; `veto("ecriture_reversible", 2_500)` est faux.
    """
    # TODO 13 : une expression booléenne, avec MONTANT_VETO_AED.
    raise NotImplementedError("Palier 09 : à coder — voir README.md")


def decider(r: float, veto_actif: bool, tau_revue: float = TAU_REVUE, tau_blocage: float = TAU_BLOCAGE) -> str:
    """Décision : « bloquer » si R >= τ_blocage ; sinon « revue » si R >= τ_revue ou veto ; sinon « autoriser ».

    Erreur : seuils qui ne vérifient pas 0 <= tau_revue < tau_blocage <= 1 → ValueError.
    Exemple : `decider(0.70, True)` = "revue" ; `decider(0.46, False)` = "autoriser" ;
    `decider(0.88, True)` = "bloquer".
    """
    # TODO 14 : valider les seuils, puis tester les zones de la PLUS grave à la moins grave.
    raise NotImplementedError("Palier 09 : à coder — voir README.md")


class Approbateur:
    """Approbation humaine sur horloge simulée : pas de réponse dans le délai = refus.

    `reponses` contient les réponses simulées de l'humain, (décision, délai en secondes) ou None.
    Exemple : sans réponse, `demander("virement")` avance l'horloge de 120 s et rend
    (False, "pas de réponse en 120 s : refus par défaut").

    Attributs publics : `horloge`, `journal`, `delai_s`, et `reponses` (liste vide au départ, que les
    tests remplissent). Un délai <= 0 lève ValueError.
    """

    def __init__(self, horloge: Horloge, journal: JournalAudit, delai_s: float = 120.0) -> None:
        # TODO 15 : refuser un délai <= 0, ranger les trois paramètres, créer `reponses` vide.
        raise NotImplementedError("Palier 09 : à coder — voir README.md")

    def demander(self, demande: str) -> tuple[bool, str]:
        """Rend (approuvé ?, décision ou motif), et journalise la demande et sa décision.

        Pas de réponse (liste vide ou None) ou délai > delai_s : l'horloge avance de delai_s, le journal
        reçoit "approbation : <demande> -> refus par délai", et la méthode rend
        (False, "pas de réponse en 120 s : refus par défaut"). Sinon l'horloge avance du délai de
        l'humain, le journal reçoit "approbation : <demande> -> <décision>", et la méthode rend
        (décision == "approuvé", décision).
        """
        # TODO 16 : retirer la PREMIÈRE réponse de la file (ou None) ; le silence vaut refus, jamais accord.
        raise NotImplementedError("Palier 09 : à coder — voir README.md")


def proteger(registre: Registre, session: dict, journal: JournalAudit, politique: dict | None = None) -> dict:
    """Le dictionnaire nom → appelable pour la boucle : politique (journalisée), PUIS schéma, PUIS outil.

    `session` ({"role", "portees"}) vient de l'authentification, jamais du modèle ; il est relu à
    chaque appel. Un refus lève `RefusPolitique` avant toute validation.
    Chaque appel journalise "politique <rôle> -> <nom> : <motif rendu par autoriser>".
    """
    # TODO 17 : une fonction FABRIQUE enveloppe(nom) qui prend registre.porte(nom) et rend appeler(**arguments) ;
    #           appeler lit session À CHAQUE APPEL, autorise, journalise, lève RefusPolitique ou délègue à la porte.
    # TODO 18 : rendre {nom: enveloppe(nom) for nom in registre.outils}. Piège : une lambda écrite directement
    #           dans la compréhension capturerait la variable de boucle, pas sa valeur.
    raise NotImplementedError("Palier 09 : à coder — voir README.md")


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

    Description de l'outil : "Virement sortant en AED vers un IBAN émirien. Action IRRÉVERSIBLE." ;
    schéma : SCHEMA_VIREMENT ; sortie : {"statut": "exécuté", "montant_aed": montant}.
    Messages exacts : ValueError("IBAN AE invalide (contrôle mod 97)") ;
    journal "risque virement <iban> de <montant> AED : R = <r à 2 décimales>, veto, décision <décision>" ;
    ErreurOutil("bloqué par le garde-fou : R = <r à 2 décimales> >= <TAU_BLOCAGE>") ;
    demande à l'humain "virement de <montant> AED vers <iban>" ; ErreurOutil("refusé par l'humain : <motif>").
    """
    # TODO 19 : décorer une fonction interne outil_virement(iban, montant_aed, motif) avec registre.outil(...).
    # TODO 20 : dans l'ordre : contrôle mod 97, R (sensibilité « personnelle », gravité de l'irréversible,
    #           incertitude), décision avec veto, journal, bloquer ?, revue → approbateur, et SEULEMENT
    #           À LA FIN virements.append(...). Rendre le registre.
    raise NotImplementedError("Palier 09 : à coder — voir README.md")
