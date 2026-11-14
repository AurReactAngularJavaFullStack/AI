"""Démo du palier 07 — la recherche hybride sur les règles EAU, et le même plongement pour la mémoire."""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.memoire import Souvenir, rappeler  # noqa: E402
from agent.metier import fr  # noqa: E402
from agent.outils import Registre  # noqa: E402
from agent.recherche import (citations, classement, enregistrer_recherche, plonger, plonger_texte,  # noqa: E402
                             rechercher_hybride, tokeniser)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REQUETE = "plafond d'endettement d'un retraité et durée maximale d'un prêt personnel"


def main() -> None:
    print("Palier 07 — client C-5, retraité : « quel plafond d'endettement, quelle durée de prêt ? »")
    q = tokeniser(REQUETE)
    print(f"1. Requête tokenisée ({len(q)} mots) : {q}")
    print(f"   plongement : {plonger(q)}")
    r = rechercher_hybride(REQUETE)
    print("2. BM25    : " + "   ".join(f"{d} = {r['bm25'][d]:.4f}" for d in classement(r["bm25"])))
    print("   cosinus : " + "   ".join(f"{d} = {r['cos'][d]:.4f}" for d in classement(r["cos"])))
    print("3. RRF (k_RRF = 60), top-3 : " + "   ".join(f"{d} = {v:.6f}" for d, v in r["fusion"]))
    sortie = enregistrer_recherche(Registre()).porte("rechercher_reglementation")(question=REQUETE)
    print(f"4. L'outil rend {sortie['ids']} ; document piégé, tel que le modèle le reçoit :")
    print(f"   {sortie['documents'][2].splitlines()[1][:80]}…")
    reponse = "Pour un retraité, 30 % du revenu au plus [REG-1] ; un prêt personnel dure au plus 48 mois [REG-2]."
    print(f"5. Citations de la réponse {citations(reponse)} ⊂ documents rendus : "
          f"{set(citations(reponse)) <= set(sortie['ids'])}")

    q_a = (f"Je voudrais une hypothèque de {fr(1_000_000, 0)} AED sur 25 ans à 4,5 %. Avec mon salaire et mon "
           f"crédit en cours, mon dossier est-il recevable ? Donnez aussi la mensualité en USD.")
    memoire = [Souvenir(f"Salaire mensuel déclaré au dossier de crédit : {fr(40_000, 0)} AED", 85.0, 9),
               Souvenir(f"Crédit auto en cours : mensualité de {fr(6_000, 0)} AED", 60.0, 8),
               Souvenir("Cherchait un prêt personnel sur 48 mois", 0.0, 4),
               Souvenir("A demandé le taux de change du dirham en USD", 88.0, 2)]
    gardes = rappeler(q_a, memoire, plonger_texte, 90.0)
    print(f"6. Mémoire de C-1 avec plonger_texte : {plonger_texte(q_a)} → scores {[round(s, 4) for s, _ in gardes]}")
    try:
        rechercher_hybride("bonjour madame")
    except ValueError as e:
        print(f"7. Question sans aucun concept connu : ValueError ({e})")
    print("OK — palier 07 terminé.")


if __name__ == "__main__":
    main()
