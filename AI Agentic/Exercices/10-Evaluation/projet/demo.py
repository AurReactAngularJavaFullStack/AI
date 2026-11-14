"""Démo du palier 10 — évaluer deux versions de l'agent sur des dossiers de crédit, puis la barrière CI."""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.boucle import executer_agent  # noqa: E402
from agent.evaluation import SEUILS, barriere_ci, noter, rapport, wilson  # noqa: E402
from agent.metier import fr, mensualite, ratio_endettement  # noqa: E402
from agent.modele import FakeLLM, Reponse, appel_outil, texte  # noqa: E402
from agent.outils import Registre, enregistrer_outils_metier  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cas(i: int, candidat: bool) -> dict:
    """Dossier C-i : la candidate saute le ratio une fois sur quatre et invente « 35 % »."""
    principal, revenu, existantes = 1_000_000 - 25_000 * i, 40_000 - 1_500 * i, 6_000 + 500 * i
    m = round(mensualite(principal, 0.045, 300), 2)
    ratio = round(ratio_endettement(existantes, m, revenu)[0], 4)
    verdict = "recevable" if ratio <= 0.50 else "non recevable"
    a1, a2 = {"principal": principal, "taux_annuel": 0.045, "n_mois": 300}, {"existantes": existantes, "nouvelle": m,
                                                                            "revenu": revenu}
    script = [Reponse("tool_use", [appel_outil("mensualite", a1, "v1")])]
    if candidat and i % 4 == 1:
        script.append(Reponse("end_turn", [texte(f"Mensualité {fr(m)} AED ; endettement estimé à 35 % : dossier recevable.")]))
    else:
        script += [Reponse("tool_use", [appel_outil("ratio_endettement", a2, "v2")]),
                   Reponse("end_turn", [texte(f"Mensualité {fr(m)} AED ; endettement {fr(ratio * 100)} % : dossier {verdict}.")])]
    registre = enregistrer_outils_metier(Registre())
    res = executer_agent(FakeLLM(script), "s", f"Dossier C-{i}", registre.appelables(), registre.definitions_api())
    sources = [str(s) for _, _, s in res["trace"]]
    but = res["statut"] == "fini" and res["reponse"].endswith(f"dossier {verdict}.") and len(res["trace"]) == 2
    return noter(res, sources, [("mensualite", a1), ("ratio_endettement", a2)], but)


def main() -> None:
    print("Palier 10 — 18 dossiers de crédit C-1 à C-18, version production contre version candidate")
    for version in ("production", "candidate"):
        rap = rapport([cas(i, version == "candidate") for i in range(1, 19)])
        code, motifs = barriere_ci(rap, SEUILS)
        print(f"  {version:<10} : {rap['succes']}/{rap['n']}   Wilson [{rap['wilson'][0]:.3f} ; {rap['wilson'][1]:.3f}]   "
              f"Tool F1 {rap['tool_f1']:.3f}   fidélité {rap['fidelite']:.3f}   → code {code}")
        for m in motifs:
            print(f"    - {m}")
    print("Pourquoi 18 cas et pas 3 : la borne basse de n sur n vaut n / (n + 1,96²)")
    for n in (3, 15, 16, 18):
        print(f"  {n:>2} sur {n:<2} → borne basse {wilson(n, n)[0]:.3f}")
    print(f"  aucun cas : wilson(0, 0) = {wilson(0, 0)} ; barrière : {barriere_ci(rapport([]))}")
    print("OK — palier 10 terminé.")


if __name__ == "__main__":
    main()
