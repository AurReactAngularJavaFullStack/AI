"""Démo du palier 02 — valider une demande de crédit, préparer le schéma strict, réparer un JSON."""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.modele import FakeLLM, Reponse, texte  # noqa: E402
from agent.schemas import (SCHEMA_DEMANDE_CREDIT, essais_moyens, p_succes, reparer,  # noqa: E402
                           schema_pour_api_strict, validate)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BON = {"montant_aed": 150_000, "duree_mois": 36, "revenu_mensuel_aed": 25_000, "emirates_id": "784-1990-1234567-1"}


def main() -> None:
    print("Palier 02 — demande de prêt personnel du client C-2 (150 000 AED sur 36 mois)")
    mauvaise = {"montant_aed": 0, "duree_mois": "36", "revenu_mensuel_aed": True, "commentaire": "urgent"}
    print("1. Demande mal formée, erreurs avec leur chemin JSON :")
    for e in validate(mauvaise, SCHEMA_DEMANDE_CREDIT):
        print(f"   {e}")
    print(f"   demande correcte : {validate(BON, SCHEMA_DEMANDE_CREDIT)}")

    api = schema_pour_api_strict(SCHEMA_DEMANDE_CREDIT)
    print(f"2. Schéma strict pour l'API, duree_mois : {api['properties']['duree_mois']}")
    print(f"   6 mois passe le schéma strict : {validate(dict(BON, duree_mois=6), api) == []} ; "
          f"le schéma local le refuse : {validate(dict(BON, duree_mois=6), SCHEMA_DEMANDE_CREDIT)}")

    llm = FakeLLM([Reponse("end_turn", [texte(json.dumps(dict(BON, duree_mois="36")))]),
                   Reponse("end_turn", [texte(json.dumps(BON))])])
    r = reparer(llm, SCHEMA_DEMANDE_CREDIT, "Prêt personnel de 150 000 AED sur 36 mois")
    print(f"3. Réparation : essai 1 → {r['erreurs'][0]}")
    print(f"   statut {r['statut']} en {r['essais']} essais, {llm.appels} appels au modèle")

    faux = json.dumps(dict(BON, montant_aed=0))
    r = reparer(FakeLLM([Reponse("end_turn", [texte(faux)])] * 3), SCHEMA_DEMANDE_CREDIT, "...", max_essais=3)
    print(f"4. Trois essais ratés : statut {r['statut']} → le dossier part en revue humaine")
    r = reparer(FakeLLM([Reponse("refusal", [])]), SCHEMA_DEMANDE_CREDIT, "...")
    print(f"   un refus s'arrête au premier essai : statut {r['statut']}, essais {r['essais']}")
    print(f"5. p = 0.9 par essai, 2 relances : succès {p_succes(0.9, 2):.3f}, "
          f"{essais_moyens(0.9, 2):.2f} appels en moyenne")
    print("OK — palier 02 terminé.")


if __name__ == "__main__":
    main()
