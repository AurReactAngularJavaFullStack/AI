"""Palier 03 — les calculs métier des Émirats, que le modèle ne doit jamais faire de tête.

Origine : étape 77, section 4 (fonctions canoniques du parcours) et en-tête (`fr`, `ESPACE_FINE`).
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
    return f"{x:,.{decimales}f}".replace(",", ESPACE_FINE).replace(".", ",")


def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    """M = P r / (1 − (1 + r)^−n), avec r = taux annuel / 12 ; M = P / n si le taux est nul.

    Exemple : `mensualite(1_000_000, 0.045, 300)` : r = 0.00375, M = 3 750 / 0.67467 ≈ 5 558.32 AED ;
    `mensualite(120_000, 0.0, 24)` = 5 000 AED.
    """
    if principal <= 0 or n_mois <= 0 or taux_annuel < 0:
        raise ValueError("principal > 0, n_mois > 0, taux >= 0")
    r = taux_annuel / 12
    return principal / n_mois if r == 0 else principal * r / (1 - (1 + r) ** -n_mois)


def ratio_endettement(mensualites_existantes: float, nouvelle_mensualite: float, revenu_mensuel: float,
                      plafond: float = PLAFOND_CBUAE) -> tuple[float, bool]:
    """Ratio CBUAE : TOUTES les mensualités (existantes + nouvelle) / revenu ; rend (ratio, ratio <= plafond).

    Exemple : `ratio_endettement(6_000, 5558.32, 40_000)` = (11 558.32 / 40 000, True) = (0.288958, True) ;
    avec `plafond=0.30` (retraité), 7 000 + 5 558.32 sur 40 000 donne (0.313958, False).
    """
    if revenu_mensuel <= 0:
        raise ValueError("revenu > 0")
    if mensualites_existantes < 0 or nouvelle_mensualite < 0:
        raise ValueError("les mensualités sont >= 0")
    if not 0 < plafond <= 1:
        raise ValueError("le plafond est dans ]0, 1]")
    ratio = (mensualites_existantes + nouvelle_mensualite) / revenu_mensuel
    return ratio, ratio <= plafond


def gratuite_fin_de_service(salaire_base_mensuel: float, annees: float) -> float:
    """Indemnité de fin de service (décret-loi fédéral 33/2021, secteur privé, hors ressortissants
    émiriens et hors DIFC) : au moins 1 an de service ; salaire journalier = base / 30 ; 21 jours par an
    les 5 premières années, 30 jours au-delà, au prorata ; plafond : 24 mois de salaire de base.

    Exemple : `gratuite_fin_de_service(10_000, 7)` = 5 × 21 × 333.33 + 2 × 30 × 333.33
    = 35 000 + 20 000 = 55 000 AED ; moins d'un an de service donne 0.
    """
    if salaire_base_mensuel <= 0 or annees < 0:
        raise ValueError("salaire > 0 et annees >= 0")
    if annees < 1:
        return 0.0
    jour = salaire_base_mensuel / 30
    brut = min(annees, 5) * 21 * jour + max(annees - 5, 0) * 30 * jour
    return min(brut, 24 * salaire_base_mensuel)


def tva(montant_ht: float, taux: float = TAUX_TVA) -> float:
    """TVA standard des EAU : 5 % (loyer résidentiel exonéré ; première livraison d'un bien
    résidentiel au taux zéro). Exemple : `tva(12_000)` = 600 AED, soit 12 600 AED TTC.
    """
    if montant_ht < 0 or not 0 <= taux <= 1:
        raise ValueError("montant >= 0 et taux dans [0, 1]")
    return montant_ht * taux


def aed_vers_usd(montant_aed: float) -> float:
    """Conversion à la parité fixe : USD = AED / 3,6725. Exemple : 5 558.32 AED ≈ 1 513.4976 USD."""
    if montant_aed < 0:
        raise ValueError("montant >= 0")
    return montant_aed / AED_PAR_USD


def usd_vers_aed(montant_usd: float) -> float:
    """Conversion à la parité fixe : AED = USD × 3,6725. Exemple : 0.0384 USD = 0.141024 AED."""
    if montant_usd < 0:
        raise ValueError("montant >= 0")
    return montant_usd * AED_PAR_USD


def iban_ae_valide(iban: str) -> bool:
    """IBAN émirien : 23 caractères, « AE », puis 21 chiffres ; contrôle ISO 13616 mod 97 = 1.

    On place les 4 premiers caractères à la fin, on remplace A par 10 et E par 14, et le grand nombre
    obtenu doit valoir 1 modulo 97.
    Exemple : `iban_ae_valide("AE07 0331 2345 6789 0123 456")` est vrai ; avec la clé 08, il est faux.
    """
    s = iban.replace(" ", "").upper()
    if len(s) != 23 or not s.startswith("AE") or not s[2:].isdigit():
        return False
    reorganise = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in reorganise)) % 97 == 1


def emirates_id_format_valide(eid: str) -> bool:
    """Format seulement : 15 chiffres commençant par 784 (affiché 784-AAAA-NNNNNNN-C), sans contrôle de clé.

    Exemple : "784-1990-1234567-1" est valide ; "785-1990-1234567-1" et "784-1990-123456-1" ne le sont pas.
    """
    chiffres = eid.replace("-", "").replace(" ", "")
    return len(chiffres) == 15 and chiffres.isdigit() and chiffres.startswith("784")
