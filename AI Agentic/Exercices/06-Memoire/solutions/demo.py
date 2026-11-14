"""Démo du palier 06 — la mémoire du client C-1 : cosinus, récence, importance, score, relecture."""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.memoire import Souvenir, cosinus, min_max, rappeler, recence  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Plongement donné à la main (8 concepts : dette, revenu, crédit, durée, taxe, change, emploi, immobilier).
# Au palier 07, recherche.plonger_texte calculera exactement ces vecteurs à partir des textes.
QUESTION = "Hypothèque de 1 000 000 AED sur 25 ans : avec mon salaire et mon crédit, recevable ? Mensualité en USD ?"
VECTEURS = {
    QUESTION: [1, 1, 2, 1, 0, 1, 0, 0],
    "Salaire mensuel déclaré au dossier de crédit : 40 000 AED": [0, 1, 1, 0, 0, 0, 0, 0],
    "Crédit auto en cours : mensualité de 6 000 AED": [1, 0, 1, 0, 0, 0, 0, 0],
    "Cherchait un prêt personnel sur 48 mois": [0, 0, 1, 1, 0, 0, 0, 0],
    "A demandé le taux de change du dirham en USD": [0, 0, 0, 0, 0, 3, 0, 0],
}


def main() -> None:
    print("Palier 06 — la mémoire du client C-1, au jour 90 de la relation")
    memoire = [Souvenir(t, j, imp) for t, j, imp in zip(list(VECTEURS)[1:], (85.0, 60.0, 0.0, 88.0), (9, 8, 4, 2))]
    sims = [cosinus(VECTEURS[QUESTION], VECTEURS[s.texte]) for s in memoire]
    recs = [recence(90.0 - s.jour_acces, 30.0) for s in memoire]
    print("1. Composantes brutes, puis ramenées dans [0, 1] par min-max :")
    print("   cosinus  " + "  ".join(f"{x:.4f}" for x in sims) + "   →  " + "  ".join(f"{x:.4f}" for x in min_max(sims)))
    print("   récence  " + "  ".join(f"{x:.4f}" for x in recs) + "   →  " + "  ".join(f"{x:.4f}" for x in min_max(recs)))
    imps = [float(s.importance) for s in memoire]
    print("   importance " + "  ".join(f"{x:.0f}" for x in imps) + "   →  " + "  ".join(f"{x:.4f}" for x in min_max(imps)))
    print("2. Score de pertinence S = 0.5 sim + 0.3 rec + 0.2 imp, tous les souvenirs :")
    for score, s in rappeler(QUESTION, [Souvenir(m.texte, m.jour_acces, m.importance) for m in memoire],
                             VECTEURS.__getitem__, 90.0, k=4):
        print(f"   {score:.4f}  {s.texte}")
    gardes = rappeler(QUESTION, memoire, VECTEURS.__getitem__, 90.0, k=2)
    print(f"3. Les 2 souvenirs mis dans le prompt : {[round(sc, 4) for sc, _ in gardes]}")
    print(f"   relus, leurs jours d'accès deviennent : {[s.jour_acces for s in memoire]}")
    print(f"4. Demi-vie 30 jours : un souvenir de 90 jours pèse {recence(90, 30):.3f} de sa valeur neuve")
    print("OK — palier 06 terminé.")


if __name__ == "__main__":
    main()
