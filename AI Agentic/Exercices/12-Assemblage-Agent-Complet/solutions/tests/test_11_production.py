"""Palier 11 — coût d'une tâche, seau à jetons, backoff avec gigue, relances, p95, budget."""
import random
import unittest

from agent.modele import Horloge
from agent.production import (ErreurTransitoire, SeauAJetons, attente_backoff, budget_restant, cout_tache,
                              executer_avec_relances, p95, percentile, taches_possibles)

LATENCES = [round(1.0 + 0.1 * i, 1) for i in range(20)]      # 1.0, 1.1, …, 2.9 s


def echoue_puis_reussit(n_echecs: int):
    etat = {"appels": 0}

    def fonction():
        etat["appels"] += 1
        if etat["appels"] <= n_echecs:
            raise ErreurTransitoire("surcharge (529)")
        return "réponse"
    return fonction, etat


class TestCout(unittest.TestCase):
    def test_exemple_avec_cache(self):
        c = cout_tache(2_000, 1_000, cache_lus=8_000, cache_ecrits=4_000)
        self.assertAlmostEqual(c["usd"], 0.0384, places=12)
        self.assertAlmostEqual(c["aed"], 0.141024, places=12)

    def test_lecture_du_cache_au_dixieme(self):
        plein = cout_tache(10_000, 0)["usd"]
        self.assertAlmostEqual(plein, 0.03, places=12)
        self.assertAlmostEqual(cout_tache(0, 0, cache_lus=10_000)["usd"], plein * 0.1, places=12)
        self.assertAlmostEqual(cout_tache(0, 0, cache_ecrits=10_000)["usd"], plein * 1.25, places=12)

    def test_entrees_invalides(self):
        with self.assertRaises(ValueError):
            cout_tache(-1, 0)
        with self.assertRaises(ValueError):
            cout_tache(10, 10, prix_entree=-3)


class TestSeauAJetons(unittest.TestCase):
    def test_sequence_de_l_etape_66(self):
        h = Horloge()
        seau = SeauAJetons(10_000, 50, h)
        self.assertEqual([seau.consommer(3_000) for _ in range(4)], [True, True, True, False])
        self.assertEqual(seau.jetons, 1_000)
        h.avancer(40)
        self.assertTrue(seau.consommer(3_000))
        self.assertFalse(seau.consommer(3_000))

    def test_recharge_plafonnee(self):
        h = Horloge()
        seau = SeauAJetons(10_000, 50, h)
        seau.consommer(9_000)
        h.avancer(1_000)
        self.assertTrue(seau.consommer(0))
        self.assertEqual(seau.jetons, 10_000)
        self.assertFalse(seau.consommer(10_001))

    def test_entrees_invalides(self):
        with self.assertRaises(ValueError):
            SeauAJetons(0, 50, Horloge())
        with self.assertRaises(ValueError):
            SeauAJetons(10, 1, Horloge()).consommer(-1)


class TestBackoff(unittest.TestCase):
    def test_exponentielle_plafonnee(self):
        self.assertEqual([attente_backoff(n) for n in range(1, 8)], [1, 2, 4, 8, 16, 30, 30])

    def test_gigue_tiree_d_un_generateur_local(self):
        u = random.Random(3).random()
        a = attente_backoff(3, gigue=0.5, rng=random.Random(3))
        self.assertAlmostEqual(a, 4 * (1 - 0.5 * u), places=12)
        self.assertTrue(2.0 < a <= 4.0)

    def test_entrees_invalides(self):
        for kwargs in ({"tentative": 0}, {"tentative": 1, "base_s": 0}, {"tentative": 1, "plafond_s": 0.5},
                       {"tentative": 1, "gigue": 1.5}):
            with self.assertRaises(ValueError):
                attente_backoff(**kwargs)


class TestRelances(unittest.TestCase):
    def test_succes_apres_deux_echecs(self):
        fonction, etat = echoue_puis_reussit(2)
        h = Horloge()
        r = executer_avec_relances(fonction, gigue=0, horloge=h)
        self.assertEqual((r["statut"], r["resultat"], r["tentatives"], r["attentes"]), ("succes", "réponse", 3, [1, 2]))
        self.assertEqual((h.t, etat["appels"]), (3.0, 3))

    def test_echec_apres_max_tentatives_et_determinisme(self):
        r1 = executer_avec_relances(echoue_puis_reussit(9)[0], max_tentatives=4, graine=42)
        r2 = executer_avec_relances(echoue_puis_reussit(9)[0], max_tentatives=4, graine=42)
        self.assertEqual((r1["statut"], r1["tentatives"], len(r1["attentes"]), len(r1["erreurs"])), ("echec", 4, 3, 4))
        self.assertEqual(r1["attentes"], r2["attentes"])

    def test_erreur_non_transitoire_remonte_aussitot(self):
        appels = []

        def mauvaise_requete():
            appels.append(1)
            raise ValueError("400 : requête invalide")
        with self.assertRaises(ValueError):
            executer_avec_relances(mauvaise_requete)
        self.assertEqual(len(appels), 1)


class TestPercentilesEtBudget(unittest.TestCase):
    def test_p95_au_rang_le_plus_proche(self):
        self.assertEqual(p95(LATENCES), 2.8)
        self.assertEqual(percentile(LATENCES, 50), 1.9)
        self.assertEqual(p95(list(reversed(LATENCES))), 2.8)
        self.assertEqual(p95([0.7]), 0.7)
        self.assertEqual(percentile(list(range(1, 101)), 7), 7)    # 7 / 100 * 100 = 7.000…01 donnerait 8
        with self.assertRaises(ValueError):
            p95([])
        with self.assertRaises(ValueError):
            percentile(LATENCES, 0)

    def test_budget(self):
        self.assertAlmostEqual(budget_restant(50, [12.5, 20.25, 7.0]), 10.25, places=12)
        self.assertEqual(budget_restant(10, [12]), -2)
        self.assertEqual(taches_possibles(10.25, 0.141024), 72)
        self.assertEqual(taches_possibles(-2, 0.141024), 0)
        with self.assertRaises(ValueError):
            taches_possibles(10, 0)
        with self.assertRaises(ValueError):
            budget_restant(50, [-1])


if __name__ == "__main__":
    unittest.main()
