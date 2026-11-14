"""Palier 03 — calculs métier des Émirats : crédit, fin de service, TVA, change, identifiants."""
import unittest

from agent.metier import (AED_PAR_USD, ESPACE_FINE, aed_vers_usd, emirates_id_format_valide, fr,
                          gratuite_fin_de_service, iban_ae_valide, mensualite, ratio_endettement, tva, usd_vers_aed)


class TestFormatage(unittest.TestCase):
    def test_montants_a_la_francaise(self):
        self.assertEqual(fr(5558.32), f"5{ESPACE_FINE}558,32")
        self.assertEqual(fr(1_000_000, 0), f"1{ESPACE_FINE}000{ESPACE_FINE}000")
        self.assertEqual(fr(28.9, 1), "28,9")
        self.assertEqual(ESPACE_FINE, " ")


class TestCredit(unittest.TestCase):
    def test_mensualite_hypotheque(self):
        self.assertAlmostEqual(mensualite(1_000_000, 0.045, 300), 5558.32, places=2)

    def test_mensualite_taux_nul(self):
        self.assertEqual(mensualite(120_000, 0.0, 24), 5000.0)

    def test_mensualite_entrees_invalides(self):
        for args in ((0, 0.045, 300), (1_000, 0.045, 0), (1_000, -0.01, 12)):
            with self.assertRaises(ValueError):
                mensualite(*args)

    def test_ratio_toutes_les_mensualites(self):
        ratio, recevable = ratio_endettement(6_000, 5558.32, 40_000)
        self.assertAlmostEqual(ratio, 0.288958, places=6)
        self.assertTrue(recevable)

    def test_ratio_plafond_retraite(self):
        ratio, recevable = ratio_endettement(7_000, 5558.32, 40_000, plafond=0.30)
        self.assertAlmostEqual(ratio, 0.313958, places=6)
        self.assertFalse(recevable)
        self.assertTrue(ratio_endettement(10_000, 10_000, 40_000)[1])   # 0.50 exactement : recevable

    def test_ratio_entrees_invalides(self):
        for args in ((6_000, 5_000, 0), (-1, 5_000, 40_000), (0, 5_000, 40_000, 1.5)):
            with self.assertRaises(ValueError):
                ratio_endettement(*args)


class TestFinDeService(unittest.TestCase):
    def test_sept_ans(self):
        self.assertAlmostEqual(gratuite_fin_de_service(10_000, 7), 55_000.0, places=6)

    def test_moins_d_un_an_et_plafond(self):
        self.assertEqual(gratuite_fin_de_service(10_000, 0.9), 0.0)
        self.assertAlmostEqual(gratuite_fin_de_service(10_000, 5), 35_000.0, places=6)
        self.assertEqual(gratuite_fin_de_service(10_000, 40), 240_000)        # 24 mois de salaire

    def test_entrees_invalides(self):
        with self.assertRaises(ValueError):
            gratuite_fin_de_service(0, 3)
        with self.assertRaises(ValueError):
            gratuite_fin_de_service(10_000, -1)


class TestTvaEtChange(unittest.TestCase):
    def test_tva(self):
        self.assertAlmostEqual(tva(12_000), 600.0, places=9)
        self.assertEqual(tva(12_000, taux=0.0), 0.0)
        with self.assertRaises(ValueError):
            tva(-1)

    def test_conversion(self):
        self.assertEqual(AED_PAR_USD, 3.6725)
        self.assertAlmostEqual(aed_vers_usd(5558.32), 1513.4976, places=4)
        self.assertAlmostEqual(usd_vers_aed(0.0384), 0.141024, places=9)
        self.assertAlmostEqual(usd_vers_aed(aed_vers_usd(180_000)), 180_000, places=6)
        with self.assertRaises(ValueError):
            aed_vers_usd(-5)


class TestIdentifiants(unittest.TestCase):
    def test_iban(self):
        self.assertTrue(iban_ae_valide("AE07 0331 2345 6789 0123 456"))
        self.assertTrue(iban_ae_valide("ae070331234567890123456"))
        self.assertFalse(iban_ae_valide("AE08 0331 2345 6789 0123 456"))     # mauvaise clé
        self.assertFalse(iban_ae_valide("AE07 0331 2345 6789 0123 45"))      # 22 caractères
        self.assertFalse(iban_ae_valide("FR07 0331 2345 6789 0123 456"))

    def test_emirates_id(self):
        self.assertTrue(emirates_id_format_valide("784-1990-1234567-1"))
        self.assertTrue(emirates_id_format_valide("784199012345671"))
        self.assertFalse(emirates_id_format_valide("785-1990-1234567-1"))
        self.assertFalse(emirates_id_format_valide("784-1990-123456-1"))


if __name__ == "__main__":
    unittest.main()
