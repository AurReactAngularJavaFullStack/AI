"""Démo du palier 11 — le coût d'une tâche, le débit, les relances et la latence, en production."""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE if (RACINE / "agent").is_dir() else RACINE.parent))

from agent.modele import Horloge  # noqa: E402
from agent.production import (ErreurTransitoire, SeauAJetons, budget_restant, cout_tache,  # noqa: E402
                              executer_avec_relances, p95, percentile, taches_possibles)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    print("Palier 11 — l'agent de la banque B-1 en production (prix illustratifs : 3 et 15 USD par million)")
    sans = cout_tache(14_000, 1_000)
    avec = cout_tache(2_000, 1_000, cache_lus=8_000, cache_ecrits=4_000)
    print(f"1. Une tâche, 14 000 tokens d'entrée sans cache : {sans['usd']:.4f} USD = {sans['aed']:.6f} AED")
    print(f"   avec 4 000 écrits et 8 000 relus dans le cache : {avec['usd']:.4f} USD = {avec['aed']:.6f} AED")
    reste = budget_restant(50.0, [12.5, 20.25, 7.0])
    print(f"2. Budget journalier 50 AED, déjà dépensé 39,75 AED : reste {reste:.2f} AED, "
          f"soit {taches_possibles(reste, avec['aed'])} tâches")

    horloge = Horloge()
    seau = SeauAJetons(10_000, 50, horloge)
    decisions = [seau.consommer(3_000) for _ in range(4)]
    horloge.avancer(40)
    decisions += [seau.consommer(3_000), seau.consommer(3_000)]
    print(f"3. Seau de 10 000 tokens, recharge 50/s, appels de 3 000 : {decisions} (deux derniers à t = 40 s)")

    etat = {"appels": 0}

    def appel_api():
        etat["appels"] += 1
        if etat["appels"] <= 3:
            raise ErreurTransitoire("surcharge (529)")
        return "réponse"
    horloge = Horloge()
    r = executer_avec_relances(appel_api, max_tentatives=5, gigue=0.2, graine=11, horloge=horloge)
    print(f"4. Trois surcharges puis succès : {r['statut']} en {r['tentatives']} tentatives ; attentes "
          + ", ".join(f"{a:.3f}" for a in r["attentes"]) + f" s ; horloge +{horloge.t:.3f} s")
    etat["appels"] = -10
    r = executer_avec_relances(appel_api, max_tentatives=3, gigue=0.0, horloge=Horloge())
    print(f"   panne longue : {r['statut']} après {r['tentatives']} tentatives, attentes {r['attentes']}")

    latences = [0.8, 0.9, 1.0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0, 2.2, 2.6, 3.4, 6.0]
    print(f"5. 20 latences (s) : médiane {percentile(latences, 50):.1f}, p95 {p95(latences):.1f}, max {max(latences):.1f}")
    print("OK — palier 11 terminé.")


if __name__ == "__main__":
    main()
