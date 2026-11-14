"""Démo du palier 05 — la boucle d'agent sur le scénario hypothèque, puis ses trois arrêts de sûreté."""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.boucle import executer_agent  # noqa: E402
from agent.metier import fr  # noqa: E402
from agent.modele import FakeLLM, Reponse, appel_outil, construire_prompt, texte  # noqa: E402
from agent.outils import Registre, enregistrer_outils_metier  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    print("Palier 05 — client C-1 : hypothèque de 1 000 000 AED, revenu 40 000 AED, crédit auto 6 000 AED")
    registre = enregistrer_outils_metier(Registre())
    outils, schemas = registre.appelables(), registre.definitions_api()
    a1 = {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300}
    a2, a3 = {"existantes": 6_000, "nouvelle": 5558.32, "revenu": 40_000}, {"montant_aed": 5558.32}
    llm = FakeLLM([
        Reponse("tool_use", [appel_outil("mensualite", a1, "a1")]),
        Reponse("tool_use", [appel_outil("ratio_endettement", a2, "a2"), appel_outil("convertir_aed_usd", a3, "a3")]),
        Reponse("end_turn", [texte(f"Mensualité {fr(5558.32)} AED, soit {fr(1513.5)} USD ; endettement total "
                                   f"{fr(28.9, 1)} % ≤ 50 % : dossier recevable.")])])
    systeme, message = construire_prompt("Mon dossier est-il recevable ?", [], [])
    r = executer_agent(llm, systeme, message, outils, schemas)
    for nom, args, sortie in r["trace"]:
        print(f"  outil {nom}({json.dumps(args)}) -> {sortie}")
    print(f"  [{r['statut']}, {r['etapes']} étapes] {r['reponse']}")
    dernier = llm.requetes[2]["messages"][-1]["content"]
    print(f"  résultats renvoyés ensemble à l'étape 3 : {[b['tool_use_id'] for b in dernier]}")

    print("Les arrêts qui protègent la facture :")
    meme = Reponse("tool_use", [appel_outil("tva", {"montant_ht": 100}, "x")])
    r = executer_agent(FakeLLM([meme] * 2), "s", "q", outils, [])
    print(f"  même action deux fois : {r['statut']} à l'étape {r['etapes']}, {len(r['trace'])} outil exécuté")
    llm = FakeLLM([Reponse("tool_use", [appel_outil("tva", {"montant_ht": v}, "m")]) for v in (1, 2, 3)])
    r = executer_agent(llm, "s", "q", outils, [], max_etapes=2)
    print(f"  trois appels différents, max_etapes = 2 : {r['statut']}, {llm.appels} appels au modèle")
    r = executer_agent(FakeLLM([Reponse("refusal", [])]), "s", "q", outils, [])
    print(f"  refus du modèle : {r['statut']} à l'étape {r['etapes']}")
    r = executer_agent(FakeLLM([Reponse("tool_use", [appel_outil("tva", {"montant_ht": -5}, "e")]),
                                Reponse("end_turn", [texte("Montant refusé.")])]), "s", "q", outils, [])
    print(f"  erreur d'outil renvoyée au modèle : {r['trace'][0][2]}")
    print("OK — palier 05 terminé.")


if __name__ == "__main__":
    main()
