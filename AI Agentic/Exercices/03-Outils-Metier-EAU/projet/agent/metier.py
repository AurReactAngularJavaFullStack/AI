"""Palier 03 — les calculs métier des Émirats, que le modèle ne doit jamais faire de tête.

SQUELETTE : les constantes sont fournies ; chaque fonction lève NotImplementedError tant que tu ne l'as
pas écrite. Ordre conseillé : fr, mensualite, ratio_endettement, gratuite_fin_de_service, tva,
aed_vers_usd, usd_vers_aed, iban_ae_valide, emirates_id_format_valide (voir README.md, « Travail à faire »).

Règles réelles utilisées (à confirmer avec le texte en vigueur) : TVA 5 % ; 1 USD = 3,6725 AED ;
plafond d'endettement CBUAE 50 % du revenu (30 % pour un retraité) ; fin de service (décret-loi
fédéral 33/2021) : 21 jours par an les 5 premières années, 30 jours au-delà, plafond 24 mois ;
Emirates ID : 15 chiffres commençant par 784 ; IBAN AE : 23 caractères, contrôle mod 97 = 1.
"""

ESPACE_FINE = chr(0x202F)                      # espace fine insécable : séparateur de milliers français
AED_PAR_USD = 3.6725                           # parité fixe du dirham
TAUX_TVA = 0.05
PLAFOND_CBUAE = 0.50
PLAFOND_RETRAITE = 0.30


def fr(x: float, decimales: int = 2) -> str:
    """Affichage français d'un montant : espace fine pour les milliers, virgule décimale.

    Exemple : `fr(5558.32)` vaut « 5 558,32 » et `fr(1_000_000, 0)` vaut « 1 000 000 »
    (le séparateur est l'espace fine insécable U+202F).
    """
    # TODO 1 : formater à l'anglaise avec une f-string (séparateur de milliers « , », `decimales` décimales).
    # TODO 2 : remplacer les deux séparateurs — attention à l'ordre des deux remplacements.
    raise NotImplementedError("Palier 03 : à coder — voir README.md")


def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    """M = P r / (1 − (1 + r)^−n), avec r = taux annuel / 12 ; M = P / n si le taux est nul.

    Exemple : `mensualite(1_000_000, 0.045, 300)` : r = 0.00375, M = 3 750 / 0.67467 ≈ 5 558.32 AED ;
    `mensualite(120_000, 0.0, 24)` = 5 000 AED.
    """
    # TODO 1 : refuser (ValueError) un principal <= 0, une durée <= 0 ou un taux < 0.
    # TODO 2 : calculer le taux mensuel r.
    # TODO 3 : taux nul → division simple ; sinon la formule (le dénominateur vaudrait 0 pour r = 0).
    raise NotImplementedError("Palier 03 : à coder — voir README.md")


def ratio_endettement(mensualites_existantes: float, nouvelle_mensualite: float, revenu_mensuel: float,
                      plafond: float = PLAFOND_CBUAE) -> tuple[float, bool]:
    """Ratio CBUAE : TOUTES les mensualités (existantes + nouvelle) / revenu ; rend (ratio, ratio <= plafond).

    Exemple : `ratio_endettement(6_000, 5558.32, 40_000)` = (11 558.32 / 40 000, True) = (0.288958, True) ;
    avec `plafond=0.30` (retraité), 7 000 + 5 558.32 sur 40 000 donne (0.313958, False).
    """
    # TODO 1 : trois gardes → ValueError : revenu <= 0 ; une mensualité < 0 ; plafond hors de ]0, 1].
    # TODO 2 : additionner TOUTES les mensualités avant de diviser par le revenu.
    # TODO 3 : rendre le couple (ratio, verdict) ; un ratio égal au plafond est recevable.
    raise NotImplementedError("Palier 03 : à coder — voir README.md")


def gratuite_fin_de_service(salaire_base_mensuel: float, annees: float) -> float:
    """Indemnité de fin de service (décret-loi fédéral 33/2021, secteur privé, hors ressortissants
    émiriens et hors DIFC) : au moins 1 an de service ; salaire journalier = base / 30 ; 21 jours par an
    les 5 premières années, 30 jours au-delà, au prorata ; plafond : 24 mois de salaire de base.

    Exemple : `gratuite_fin_de_service(10_000, 7)` = 5 × 21 × 333.33 + 2 × 30 × 333.33
    = 35 000 + 20 000 = 55 000 AED ; moins d'un an de service donne 0.
    """
    # TODO 1 : ValueError si le salaire est <= 0 ou si les années sont < 0.
    # TODO 2 : moins d'un an de service → 0.0.
    # TODO 3 : salaire journalier, puis les deux tranches (5 premières années, puis le reste) avec min et max.
    # TODO 4 : plafonner à 24 mois de salaire de base.
    raise NotImplementedError("Palier 03 : à coder — voir README.md")


def tva(montant_ht: float, taux: float = TAUX_TVA) -> float:
    """TVA standard des EAU : 5 % (loyer résidentiel exonéré ; première livraison d'un bien
    résidentiel au taux zéro). Exemple : `tva(12_000)` = 600 AED, soit 12 600 AED TTC.
    """
    # TODO 1 : ValueError si le montant est < 0 ou si le taux sort de [0, 1].
    # TODO 2 : rendre la TVA seule (pas le TTC).
    raise NotImplementedError("Palier 03 : à coder — voir README.md")


def aed_vers_usd(montant_aed: float) -> float:
    """Conversion à la parité fixe : USD = AED / 3,6725. Exemple : 5 558.32 AED ≈ 1 513.4976 USD."""
    # TODO : ValueError pour un montant < 0, puis diviser par la constante de parité (sans arrondir).
    raise NotImplementedError("Palier 03 : à coder — voir README.md")


def usd_vers_aed(montant_usd: float) -> float:
    """Conversion à la parité fixe : AED = USD × 3,6725. Exemple : 0.0384 USD = 0.141024 AED."""
    # TODO : ValueError pour un montant < 0, puis multiplier par la constante de parité (sans arrondir).
    raise NotImplementedError("Palier 03 : à coder — voir README.md")


def iban_ae_valide(iban: str) -> bool:
    """IBAN émirien : 23 caractères, « AE », puis 21 chiffres ; contrôle ISO 13616 mod 97 = 1.

    On place les 4 premiers caractères à la fin, on remplace A par 10 et E par 14, et le grand nombre
    obtenu doit valoir 1 modulo 97.
    Exemple : `iban_ae_valide("AE07 0331 2345 6789 0123 456")` est vrai ; avec la clé 08, il est faux.
    """
    # TODO 1 : normaliser (retirer les espaces, passer en majuscules).
    # TODO 2 : contrôler la forme (longueur, préfixe, chiffres) ; une forme fausse rend False, sans exception.
    # TODO 3 : déplacer les 4 premiers caractères à la fin.
    # TODO 4 : convertir chaque caractère en nombre (indice : la base 36), concaténer, tester le reste modulo 97.
    raise NotImplementedError("Palier 03 : à coder — voir README.md")


def emirates_id_format_valide(eid: str) -> bool:
    """Format seulement : 15 chiffres commençant par 784 (affiché 784-AAAA-NNNNNNN-C), sans contrôle de clé.

    Exemple : "784-1990-1234567-1" est valide ; "785-1990-1234567-1" et "784-1990-123456-1" ne le sont pas.
    """
    # TODO 1 : retirer les tirets et les espaces.
    # TODO 2 : trois conditions à réunir : longueur, uniquement des chiffres, préfixe.
    raise NotImplementedError("Palier 03 : à coder — voir README.md")
