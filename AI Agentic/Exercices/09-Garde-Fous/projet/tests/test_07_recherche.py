"""Palier 07 — tokenisation, plongement jouet, BM25, classement, RRF, outil de recherche encadré."""
import math
import unittest

from agent.outils import ArgumentsInvalides, Registre
from agent.recherche import (CORPUS, bm25_score, citations, classement, enregistrer_recherche, idf_bm25, indexer,
                             plonger, plonger_texte, rechercher_hybride, rrf, tokeniser)

REQUETE = "plafond d'endettement d'un retraité et durée maximale d'un prêt personnel"


class TestTokenisation(unittest.TestCase):
    def test_accents_et_mots_vides(self):
        self.assertEqual(tokeniser("Durée maximale d'un prêt"), ["duree", "maximale", "pret"])
        self.assertEqual(tokeniser(REQUETE),
                         ["plafond", "endettement", "retraite", "duree", "maximale", "pret", "personnel"])

    def test_plongement(self):
        self.assertEqual(plonger(tokeniser(REQUETE)), [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(plonger_texte("A demandé le taux de change du dirham en USD"),
                         [0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0])

    def test_index(self):
        index = indexer()
        self.assertEqual(len(index), 7)
        self.assertEqual(sum(len(m) for m in index.values()), 94)
        self.assertAlmostEqual(sum(len(m) for m in index.values()) / len(index), 13.43, places=2)
        self.assertEqual(indexer({"R-1": "Prêt à 5 %"}), {"R-1": ["pret", "5"]})


class TestBM25(unittest.TestCase):
    def test_idf(self):
        self.assertAlmostEqual(idf_bm25(1, 7), math.log(1 + 6.5 / 1.5), places=12)
        self.assertAlmostEqual(idf_bm25(1, 7), 1.6740, places=4)
        with self.assertRaises(ValueError):
            idf_bm25(8, 7)

    def test_scores_du_scenario_b(self):
        s = rechercher_hybride(REQUETE)["bm25"]
        for doc, attendu in (("REG-2", 5.0951), ("REG-1", 3.1771), ("FORUM-9", 1.9524), ("REG-4", 0.6775)):
            self.assertAlmostEqual(s[doc], attendu, places=4)
        self.assertEqual(s["REG-3"], 0.0)

    def test_mot_absent_et_corpus_vide(self):
        corpus = [["pret", "duree"], ["tva"]]
        self.assertEqual(bm25_score(["inconnu"], corpus[0], corpus), 0.0)
        with self.assertRaises(ValueError):
            bm25_score(["pret"], [], [])


class TestFusion(unittest.TestCase):
    def test_classement(self):
        self.assertEqual(classement({"B": 2.0, "A": 2.0, "C": 0.0, "D": 3.0}), ["D", "A", "B"])

    def test_deux_classements_et_rrf(self):
        r = rechercher_hybride(REQUETE)
        self.assertEqual(classement(r["bm25"]), ["REG-2", "REG-1", "FORUM-9", "REG-4"])
        self.assertEqual(classement(r["cos"]), ["REG-1", "FORUM-9", "REG-2", "REG-4"])
        self.assertAlmostEqual(r["cos"]["REG-1"], 0.8018, places=4)
        self.assertEqual([d for d, _ in r["fusion"]], ["REG-1", "REG-2", "FORUM-9"])
        for (_, v), attendu in zip(r["fusion"], (1 / 62 + 1 / 61, 1 / 61 + 1 / 63, 1 / 63 + 1 / 62)):
            self.assertAlmostEqual(v, attendu, places=12)
        self.assertAlmostEqual(r["fusion"][0][1], 0.032522, places=6)

    def test_rrf_ne_depend_que_des_rangs(self):
        r = rechercher_hybride(REQUETE)
        deformes = rrf([classement({d: math.log(1 + v) for d, v in r["bm25"].items()}),
                        classement({d: v ** 3 for d, v in r["cos"].items()})])[:3]
        self.assertEqual(deformes, r["fusion"])

    def test_rrf_document_absent_et_erreurs(self):
        self.assertEqual(rrf([["A"], ["B", "A"]], k_rrf=0), [("A", 1.5), ("B", 1.0)])
        with self.assertRaises(ValueError):
            rrf([["A"]], k_rrf=-1)
        with self.assertRaises(ValueError):
            rechercher_hybride(REQUETE, k=0)
        with self.assertRaises(ValueError):                     # aucun concept connu : vecteur nul
            rechercher_hybride("bonjour madame")


class TestOutilRecherche(unittest.TestCase):
    def setUp(self):
        self.porte = enregistrer_recherche(Registre()).porte("rechercher_reglementation")

    def test_ids_et_documents_encadres(self):
        sortie = self.porte(question=REQUETE)
        self.assertEqual(sortie["ids"], ["REG-1", "REG-2", "FORUM-9"])
        piege = sortie["documents"][2]
        self.assertIn("&lt;system>", piege)
        self.assertNotIn("<system>", piege)
        self.assertEqual(piege.count("</document>"), 1)

    def test_schema_et_corpus_personnalise(self):
        with self.assertRaises(ArgumentsInvalides):
            self.porte(question="ab")
        corpus = {"R-1": "TVA de 5 % sur le loyer commercial", "R-2": CORPUS["REG-5"]}
        porte = enregistrer_recherche(Registre(), corpus).porte("rechercher_reglementation")
        self.assertEqual(porte(question="taux de TVA")["ids"], ["R-1"])

    def test_citations(self):
        self.assertEqual(citations("… 30 % [REG-1] ; 48 mois [REG-2]."), ["REG-1", "REG-2"])
        self.assertEqual(citations("aucune règle"), [])


if __name__ == "__main__":
    unittest.main()
