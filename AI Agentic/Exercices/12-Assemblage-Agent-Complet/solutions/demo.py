"""Démo du palier 12 — l'agent complet de l'étape 77 : trois scénarios, puis l'évaluation avant déploiement."""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.assemblage import (evaluation_complete, scenario_credit, scenario_reglementation,  # noqa: E402
                              scenario_virement)
from agent.evaluation import barriere_ci, rapport  # noqa: E402
from agent.modele import fiabilite_serie  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    print("Palier 12 — l'assistant de la banque B-1 (Dubaï), assemblé")
    a = scenario_credit()
    res = a["res"]
    print("(a) hypothèque : mémoire rappelée " + " | ".join(f"{s.texte} ({score:.4f})" for score, s in res["rappel"]))
    for nom, args, sortie in res["trace"]:
        print(f"    outil {nom}({json.dumps(args)}) -> {sortie}")
    print(f"    [{res['statut']}, {res['etapes']} étapes] {res['reponse']}")
    print(f"    fiabilité de la chaîne, 6 étapes à 0.98 : {fiabilite_serie([0.98] * 6):.4f}")
    b = scenario_reglementation()
    rendus = b["res"]["trace"][0][2]
    print(f"(b) réglementation : documents rendus {rendus['ids']} ; [{b['res']['statut']}] {b['res']['reponse'][:60]}…")
    c = scenario_virement()
    agent = c["agent"]
    print(f"(c) virement piégé : {c['res']['trace'][0][2]}")
    print(f"    horloge +{agent.horloge.t - 90 * 86_400:.0f} s ; virements exécutés : {len(agent.virements)} ; "
          f"journal de {len(agent.journal.textes())} entrées, chaîne intacte : {agent.journal.verifier() is None}")
    print(f"    {agent.journal.textes()[2]}")
    ev = evaluation_complete()
    print("Évaluation : 18 cas de référence (3 scénarios + 15 variantes du dossier de crédit)")
    for version in ("production", "candidate"):
        rap = ev[version]
        print(f"  {version:<10} : {rap['succes']}/{rap['n']}   Wilson [{rap['wilson'][0]:.3f} ; {rap['wilson'][1]:.3f}]   "
              f"Tool F1 {rap['tool_f1']:.3f}   fidélité {rap['fidelite']:.3f}   → barrière CI : code {rap['code']}")
        for m in rap["motifs"]:
            print(f"    - {m}")
    trois = rapport(ev["communes"])
    print(f"  les 3 scénarios seuls : 3/3, Wilson basse {trois['wilson'][0]:.3f} → code {barriere_ci(trois)[0]}")
    print("OK — palier 12 terminé.")


if __name__ == "__main__":
    main()
