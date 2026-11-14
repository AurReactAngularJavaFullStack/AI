"""Démo du palier 04 — le registre des outils EAU, la porte de validation, l'enveloppe d'erreur."""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.modele import appel_outil  # noqa: E402
from agent.outils import ArgumentsInvalides, Registre, enregistrer_outils_metier, executer_appel  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    print("Palier 04 — les outils de la banque B-1, derrière leur porte")
    registre = enregistrer_outils_metier(Registre())
    print(f"1. {len(registre)} outils : {', '.join(registre.outils)}")
    defs = registre.definitions_api()
    print(f"   définitions API strictes : {all(d['strict'] for d in defs)} ; "
          f"n_mois envoyé : {defs[0]['input_schema']['properties']['n_mois']}")

    outils = registre.appelables()
    print(f"2. mensualite(1 000 000 AED, 4,5 %, 300 mois) → {outils['mensualite'](principal=1_000_000, taux_annuel=0.045, n_mois=300)}")
    print(f"   ratio_endettement(6 000, 5 558,32, 40 000) → "
          f"{outils['ratio_endettement'](existantes=6_000, nouvelle=5558.32, revenu=40_000)}")
    print(f"   convertir_aed_usd(5 558,32) → {outils['convertir_aed_usd'](montant_aed=5558.32)}")
    try:
        outils["mensualite"](principal=1_000_000, taux_annuel=0.045, n_mois="300")
    except ArgumentsInvalides as e:
        print(f"3. n_mois=\"300\" arrêté par le schéma, la fonction n'est pas exécutée : {e}")

    for bloc in (appel_outil("tva", {"montant_ht": 12_000}, "t1"),
                 appel_outil("tva", {"montant_ht": -5}, "t2"),
                 appel_outil("virement", {"montant_aed": 180_000}, "t3")):
        resultat, ligne = executer_appel(outils, bloc)
        print(f"4. {bloc.name}({bloc.input}) → is_error = {resultat.get('is_error', False)} ; {resultat['content']}")
    print("OK — palier 04 terminé.")


if __name__ == "__main__":
    main()
