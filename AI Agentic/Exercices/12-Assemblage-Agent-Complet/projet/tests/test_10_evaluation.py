"""Palier 10 — Wilson, Tool Call F1, Goal Accuracy, fidélité approchée, rapport et barrière CI."""
import unittest

from agent.evaluation import (SEUILS, barriere_ci, fidelite_approchee, goal_accuracy, moyenne_definie, nombres,
                              noter, rapport, tool_call_f1, wilson)
from agent.metier import ESPACE_FINE

A1 = ("mensualite", {"principal": 975_000, "taux_annuel": 0.045, "n_mois": 300})
A2 = ("ratio_endettement", {"existantes": 6_500, "nouvelle": 5419.37, "revenu": 38_500})
PARFAIT = {"f1": 1.0, "but": True, "fidelite": 1.0}
FAUTIF = {"f1": 2 / 3, "but": False, "fidelite": 0.5}


class TestWilson(unittest.TestCase):
    def test_tout_reussi(self):
        bas, haut = wilson(18, 18)
        self.assertAlmostEqual(bas, 18 / (18 + 1.96 ** 2), places=12)
        self.assertAlmostEqual(bas, 0.824, places=3)
        self.assertAlmostEqual(haut, 1.0, places=12)
        self.assertAlmostEqual(wilson(3, 3)[0], 0.438, places=3)

    def test_quatorze_sur_dix_huit(self):
        bas, haut = wilson(14, 18)
        self.assertAlmostEqual(bas, 0.548, places=3)
        self.assertAlmostEqual(haut, 0.910, places=3)

    def test_indefini_et_invalide(self):
        self.assertIsNone(wilson(0, 0))
        with self.assertRaises(ValueError):
            wilson(5, 4)


class TestToolCallF1(unittest.TestCase):
    def test_parfait_et_oubli(self):
        self.assertEqual(tool_call_f1([A1, A2], [A1, A2]), 1.0)
        self.assertAlmostEqual(tool_call_f1([A1, A2], [A1]), 2 / 3, places=12)

    def test_repetition_et_ordre_des_arguments(self):
        self.assertAlmostEqual(tool_call_f1([A1], [A1, A1]), 2 / 3, places=12)
        inverse = ("mensualite", {"n_mois": 300, "taux_annuel": 0.045, "principal": 975_000})
        self.assertEqual(tool_call_f1([A1], [inverse]), 1.0)

    def test_indefini(self):
        self.assertIsNone(tool_call_f1([], []))
        self.assertEqual(tool_call_f1([A1], []), 0.0)


class TestGoalEtFidelite(unittest.TestCase):
    def test_goal_accuracy(self):
        self.assertAlmostEqual(goal_accuracy([True] * 14 + [False] * 4), 14 / 18, places=12)
        self.assertIsNone(goal_accuracy([]))

    def test_nombres_a_la_francaise(self):
        self.assertEqual(nombres(f"5{ESPACE_FINE}558,32 AED ; 28,9 % [REG-1]"), [5558.32, 0.289])
        self.assertEqual(nombres("aucun chiffre [REG-2]"), [])

    def test_fidelite(self):
        reponse = f"Mensualité 5{ESPACE_FINE}419,37 AED ; endettement estimé à 35 % : dossier recevable."
        self.assertEqual(fidelite_approchee(reponse, ['{"mensualite_aed": 5419.37}']), 0.5)
        self.assertEqual(fidelite_approchee(reponse, ['{"mensualite_aed": 5419.37}', "plafond 35 %"]), 1.0)
        self.assertIsNone(fidelite_approchee("Dossier recevable.", ["5419.37"]))

    def test_moyenne_definie(self):
        self.assertEqual(moyenne_definie([1.0, None, 0.5]), 0.75)
        self.assertIsNone(moyenne_definie([None, None]))


class TestRapportEtBarriere(unittest.TestCase):
    def test_noter(self):
        res = {"statut": "fini", "reponse": "Mensualité 5419,37 AED.", "trace": [(A1[0], A1[1], {"m": 5419.37})]}
        self.assertEqual(noter(res, ['{"m": 5419.37}'], [A1, A2], True), {"f1": 2 / 3, "but": True, "fidelite": 1.0})
        tronque = {"statut": "tronque", "trace": []}
        self.assertEqual(noter(tronque, [], [A1], False), {"f1": 0.0, "but": False, "fidelite": None})

    def test_candidate_bloquee_avec_trois_motifs(self):
        rap = rapport([PARFAIT] * 14 + [FAUTIF] * 4)
        self.assertEqual((rap["n"], rap["succes"]), (18, 14))
        self.assertAlmostEqual(rap["tool_f1"], (14 + 4 * 2 / 3) / 18, places=12)
        self.assertAlmostEqual(rap["fidelite"], (14 + 4 * 0.5) / 18, places=12)
        code, motifs = barriere_ci(rap)
        self.assertEqual(code, 1)
        self.assertEqual(motifs, ["borne basse de Wilson 0.548 < 0.8", "Tool Call F1 0.926 < 0.95",
                                  "fidélité approchée 0.889 < 0.95"])

    def test_production_passe_trois_cas_ne_suffisent_pas(self):
        self.assertEqual(barriere_ci(rapport([PARFAIT] * 18), SEUILS), (0, []))
        self.assertEqual(barriere_ci(rapport([PARFAIT] * 3)), (1, ["borne basse de Wilson 0.438 < 0.8"]))
        self.assertEqual(barriere_ci(rapport([])), (1, ["aucun cas évalué"]))

    def test_moyenne_indefinie_ne_bloque_pas(self):
        notes = [{"f1": None, "but": True, "fidelite": None}] * 18
        rap = rapport(notes)
        self.assertIsNone(rap["tool_f1"])
        self.assertEqual(barriere_ci(rap), (0, []))


if __name__ == "__main__":
    unittest.main()
