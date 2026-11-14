"""Palier 08 — tâches, tri topologique de Kahn, vagues, calendrier au plus tôt, chemin critique."""
import unittest

from agent.planification import (Tache, calendrier, chemin_critique, dossier_credit, duree_par_vagues,
                                 tri_topologique, vagues)

ORDRE_DOSSIER = ["lire_memoire", "calculer_mensualite", "calculer_ratio", "convertir_usd", "rechercher_regles",
                 "verifier_identite", "evaluer_risque", "rediger_reponse"]


class TestTache(unittest.TestCase):
    def test_creation(self):
        t = Tache("calculer_ratio", 0.6, ["calculer_mensualite"])
        self.assertEqual(t.prerequis, ("calculer_mensualite",))
        self.assertEqual(tri_topologique([t, Tache("calculer_mensualite", 0)]), ["calculer_mensualite", "calculer_ratio"])

    def test_entrees_invalides(self):
        self.assertEqual(chemin_critique([Tache("a", 0)]), (0, ["a"]))     # une durée nulle est permise
        with self.assertRaises(ValueError):
            Tache("a", -1.0)
        with self.assertRaises(ValueError):
            Tache("", 1.0)


class TestTriTopologique(unittest.TestCase):
    def test_dossier_de_credit(self):
        ordre = tri_topologique(dossier_credit())
        self.assertEqual(ordre, ORDRE_DOSSIER)
        position = {n: i for i, n in enumerate(ordre)}
        for t in dossier_credit():
            for p in t.prerequis:
                self.assertLess(position[p], position[t.nom])

    def test_departage_alphabetique(self):
        taches = [Tache("c", 1), Tache("b", 1), Tache("a", 1, ("c",))]
        self.assertEqual(tri_topologique(taches), ["b", "c", "a"])

    def test_cycle_nomme(self):
        taches = [Tache("a", 1, ("c",)), Tache("b", 1, ("a",)), Tache("c", 1, ("b",)), Tache("d", 1, ("c",)),
                  Tache("e", 1)]
        with self.assertRaises(ValueError) as ctx:
            tri_topologique(taches)
        self.assertEqual(str(ctx.exception), "cycle détecté : a → b → c → a")
        with self.assertRaises(ValueError) as ctx:
            tri_topologique([Tache("x", 1, ("x",))])
        self.assertEqual(str(ctx.exception), "cycle détecté : x → x")

    def test_prerequis_inconnu_et_doublon(self):
        with self.assertRaises(ValueError):
            tri_topologique([Tache("a", 1, ("fantome",))])
        with self.assertRaises(ValueError):
            tri_topologique([Tache("a", 1), Tache("a", 2)])
        taches = [Tache("a", 1), Tache("z", 5), Tache("v", 1, ("a", "a", "z"))]   # prérequis cité deux fois
        self.assertEqual(taches[2].prerequis, ("a", "z"))
        self.assertEqual(tri_topologique(taches), ["a", "z", "v"])


class TestVagues(unittest.TestCase):
    def test_dossier_de_credit(self):
        self.assertEqual(vagues(dossier_credit()), [
            ["lire_memoire", "rechercher_regles", "verifier_identite"], ["calculer_mensualite"],
            ["calculer_ratio", "convertir_usd"], ["evaluer_risque"], ["rediger_reponse"]])

    def test_cas_limites(self):
        self.assertEqual(vagues([]), [])
        self.assertEqual(vagues([Tache("b", 1), Tache("a", 1)]), [["a", "b"]])
        with self.assertRaises(ValueError):
            vagues([Tache("a", 1, ("b",)), Tache("b", 1, ("a",))])


class TestCheminCritique(unittest.TestCase):
    def test_calendrier_au_plus_tot(self):
        dates = calendrier(dossier_credit())
        self.assertEqual(dates["lire_memoire"], (0.0, 0.5))
        debut, fin = dates["evaluer_risque"]
        self.assertAlmostEqual(debut, 2.0, places=9)        # max(1.5, 1.9, 2.0)
        self.assertAlmostEqual(fin, 3.2, places=9)

    def test_chemin_et_duree(self):
        duree, chemin = chemin_critique(dossier_credit())
        self.assertAlmostEqual(duree, 5.7, places=9)
        self.assertEqual(chemin, ["rechercher_regles", "evaluer_risque", "rediger_reponse"])

    def test_sequentiel_vagues_critique(self):
        taches = dossier_credit()
        sequentiel = sum(t.duree for t in taches)
        self.assertAlmostEqual(sequentiel, 9.5, places=9)
        self.assertAlmostEqual(duree_par_vagues(taches), 7.1, places=9)
        self.assertGreaterEqual(duree_par_vagues(taches), chemin_critique(taches)[0])

    def test_plan_vide_et_tache_seule(self):
        self.assertEqual(chemin_critique([]), (0.0, []))
        self.assertEqual(chemin_critique([Tache("seule", 4.0)]), (4.0, ["seule"]))


if __name__ == "__main__":
    unittest.main()
