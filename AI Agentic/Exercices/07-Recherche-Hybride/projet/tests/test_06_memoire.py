"""Palier 06 — cosinus, min-max, récence, score de pertinence, rappel des souvenirs."""
import math
import unittest

from agent.memoire import Souvenir, cosinus, min_max, rappeler, recence, score_pertinence

# Les vecteurs du scénario (a) de 77, calculés à la main (concepts : dette, revenu, crédit, durée,
# taxe, change, emploi, immobilier). Le palier 07 les retrouvera avec `recherche.plonger_texte`.
VECTEURS = {
    "question": [1, 1, 2, 1, 0, 1, 0, 0],
    "salaire": [0, 1, 1, 0, 0, 0, 0, 0],
    "credit auto": [1, 0, 1, 0, 0, 0, 0, 0],
    "pret personnel": [0, 0, 1, 1, 0, 0, 0, 0],
    "change": [0, 0, 0, 0, 0, 3, 0, 0],
}


def souvenirs():
    return [Souvenir("salaire", 85.0, 9), Souvenir("credit auto", 60.0, 8),
            Souvenir("pret personnel", 0.0, 4), Souvenir("change", 88.0, 2)]


class TestCosinus(unittest.TestCase):
    def test_exemple_chiffre(self):
        self.assertAlmostEqual(cosinus(VECTEURS["question"], VECTEURS["salaire"]), 0.75, places=12)
        self.assertAlmostEqual(cosinus(VECTEURS["question"], VECTEURS["change"]), 1 / math.sqrt(8), places=12)

    def test_cas_limites(self):
        self.assertEqual(cosinus([1, 0], [0, 1]), 0.0)
        self.assertAlmostEqual(cosinus([1, 2], [2, 4]), 1.0, places=12)
        self.assertAlmostEqual(cosinus([1, 2], [-1, -2]), -1.0, places=12)

    def test_vecteur_nul_et_dimensions(self):
        with self.assertRaises(ValueError):
            cosinus([0, 0], [1, 1])
        with self.assertRaises(ValueError):
            cosinus([1, 2], [1, 2, 3])


class TestMinMax(unittest.TestCase):
    def test_importances(self):
        for obtenu, attendu in zip(min_max([9, 8, 4, 2]), [1.0, 0.857143, 0.285714, 0.0]):
            self.assertAlmostEqual(obtenu, attendu, places=6)

    def test_valeurs_egales_et_liste_vide(self):
        self.assertEqual(min_max([3, 3]), [0.0, 0.0])
        with self.assertRaises(ValueError):
            min_max([])


class TestRecence(unittest.TestCase):
    def test_demi_vie(self):
        self.assertEqual(recence(0, 30), 1.0)
        self.assertAlmostEqual(recence(30, 30), 0.5, places=12)
        self.assertAlmostEqual(recence(90, 30), 0.125, places=12)
        self.assertAlmostEqual(recence(5, 30), 0.8909, places=4)

    def test_entrees_invalides(self):
        with self.assertRaises(ValueError):
            recence(-1, 30)
        with self.assertRaises(ValueError):
            recence(5, 0)


class TestScorePertinence(unittest.TestCase):
    def test_exemple(self):
        self.assertAlmostEqual(score_pertinence(1.0, 0.9229, 1.0, (0.5, 0.3, 0.2)), 0.97687, places=5)

    def test_refus(self):
        with self.assertRaises(ValueError):
            score_pertinence(0.5, 0.5, 0.5, (0.6, 0.6, -0.2))
        with self.assertRaises(ValueError):
            score_pertinence(0.5, 0.5, 0.5, (0.5, 0.3, 0.3))
        with self.assertRaises(ValueError):
            score_pertinence(1.2, 0.5, 0.5, (0.5, 0.3, 0.2))


class TestRappeler(unittest.TestCase):
    def test_scenario_de_77(self):
        mem = souvenirs()
        gardes = rappeler("question", mem, VECTEURS.__getitem__, 90.0)
        self.assertEqual([s.texte for _, s in gardes], ["salaire", "credit auto"])
        self.assertAlmostEqual(gardes[0][0], 0.9769, places=4)
        self.assertAlmostEqual(gardes[1][0], 0.8070, places=4)

    def test_tous_les_scores(self):
        gardes = rappeler("question", souvenirs(), VECTEURS.__getitem__, 90.0, k=4)
        for (score, _), attendu in zip(gardes, [0.9769, 0.8070, 0.5571, 0.3]):
            self.assertAlmostEqual(score, attendu, places=4)

    def test_relire_remet_l_horloge_a_zero(self):
        mem = souvenirs()
        rappeler("question", mem, VECTEURS.__getitem__, 90.0)
        self.assertEqual([s.jour_acces for s in mem], [90.0, 90.0, 0.0, 88.0])

    def test_cas_limites_et_erreurs(self):
        self.assertEqual(rappeler("question", [], VECTEURS.__getitem__, 90.0), [])
        with self.assertRaises(ValueError):
            rappeler("question", souvenirs(), VECTEURS.__getitem__, 90.0, k=0)
        with self.assertRaises(ValueError):                     # souvenir « du futur » : âge négatif
            rappeler("question", souvenirs(), VECTEURS.__getitem__, 50.0)
        with self.assertRaises(ValueError):
            Souvenir("x", 0.0, 11)


if __name__ == "__main__":
    unittest.main()
