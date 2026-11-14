"""Démo du palier 08 — planifier un dossier de crédit : ordre, vagues, calendrier, chemin critique."""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.planification import (Tache, calendrier, chemin_critique, dossier_credit,  # noqa: E402
                                 duree_par_vagues, tri_topologique, vagues)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    print("Palier 08 — dossier de crédit du client C-6 à l'agence A-3 (durées illustratives, en secondes)")
    plan = dossier_credit()
    print(f"1. Ordre de Kahn (départage alphabétique) : {' → '.join(tri_topologique(plan))}")
    print("2. Vagues parallèles :")
    for i, v in enumerate(vagues(plan), start=1):
        print(f"   vague {i} : {', '.join(v)}")
    dates = calendrier(plan)
    print("3. Calendrier au plus tôt, exécutants illimités :")
    for nom in ("evaluer_risque", "rediger_reponse"):
        print(f"   {nom:<16} de {dates[nom][0]:.1f} s à {dates[nom][1]:.1f} s")
    duree, chemin = chemin_critique(plan)
    print(f"4. Chemin critique : {' → '.join(chemin)} = {duree:.1f} s")
    print(f"   séquentiel {sum(t.duree for t in plan):.1f} s ; vagues synchronisées {duree_par_vagues(plan):.1f} s ; "
          f"gain du parallélisme {1 - duree / sum(t.duree for t in plan):.1%}")
    plus_rapide = [Tache(t.nom, 0.8 if t.nom == "rechercher_regles" else t.duree, t.prerequis) for t in plan]
    d2, c2 = chemin_critique(plus_rapide)
    print(f"5. Recherche accélérée à 0.8 s : {d2:.1f} s, le chemin critique devient {' → '.join(c2)}")
    circulaire = [Tache(t.nom, t.duree, ("relancer_client",)) if t.nom == "verifier_identite" else t for t in plan]
    circulaire.append(Tache("relancer_client", 0.5, ("rediger_reponse",)))   # relancer AVANT d'avoir vérifié
    try:
        tri_topologique(circulaire)
    except ValueError as e:
        print(f"6. Plan circulaire refusé : {e}")
    print("OK — palier 08 terminé.")


if __name__ == "__main__":
    main()
