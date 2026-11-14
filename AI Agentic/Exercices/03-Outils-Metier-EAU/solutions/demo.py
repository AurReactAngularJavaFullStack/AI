"""Démo du palier 03 — les calculs EAU que le modèle ne fait jamais de tête."""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.metier import (PLAFOND_RETRAITE, aed_vers_usd, emirates_id_format_valide, fr,  # noqa: E402
                          gratuite_fin_de_service, iban_ae_valide, mensualite, ratio_endettement, tva)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    print("Palier 03 — dossiers des clients C-1 à C-4 (montants en AED, parité 3,6725 AED pour 1 USD)")
    m = mensualite(1_000_000, 0.045, 300)
    print(f"1. C-1, hypothèque de {fr(1_000_000, 0)} AED à 4,5 % sur 300 mois : mensualité {fr(m)} AED"
          f" = {fr(aed_vers_usd(round(m, 2)))} USD")
    ratio, ok = ratio_endettement(6_000, round(m, 2), 40_000)
    print(f"   endettement (6 000 + {fr(m)}) / 40 000 = {fr(ratio * 100, 2)} % → recevable : {ok}")
    ratio_r, ok_r = ratio_endettement(7_000, round(m, 2), 40_000, plafond=PLAFOND_RETRAITE)
    print(f"2. C-2, retraité, 7 000 AED de crédits en cours : {fr(ratio_r * 100, 2)} % > 30 % → recevable : {ok_r}")
    print(f"3. C-3, salaire de base 10 000 AED, 7 ans : fin de service {fr(gratuite_fin_de_service(10_000, 7))} AED")
    print(f"   même salaire, 40 ans : plafonnée à 24 mois, {fr(gratuite_fin_de_service(10_000, 40))} AED")
    ht = 120_000
    print(f"4. Agence A-3, situation de travaux {fr(ht, 0)} AED HT : TVA {fr(tva(ht))} AED, "
          f"TTC {fr(ht + tva(ht))} AED")
    for iban in ("AE07 0331 2345 6789 0123 456", "AE08 0331 2345 6789 0123 456"):
        print(f"5. IBAN {iban} : clé mod 97 valide = {iban_ae_valide(iban)}")
    for eid in ("784-1990-1234567-1", "785-1990-1234567-1"):
        print(f"6. Emirates ID {eid} : format valide = {emirates_id_format_valide(eid)}")
    print("OK — palier 03 terminé.")


if __name__ == "__main__":
    main()
