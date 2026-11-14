"""Palier 12 — l'agent assemblé : décision finale, appels d'outils, garde-fous, barrière CI (mêmes nombres que 77)."""
import json
import math
import unittest

from agent.assemblage import (A_CONVERSION, A_MENSUALITE, A_RATIO, Agent, construire_agent, demande_credit,
                              evaluation_complete, scenario_credit, scenario_reglementation, scenario_virement)
from agent.evaluation import barriere_ci, rapport
from agent.modele import FakeLLM, Reponse, appel_outil, texte


class TestScenarioCredit(unittest.TestCase):
    def setUp(self):
        self.s = scenario_credit()
        self.res = self.s["res"]

    def test_decision_finale(self):
        self.assertEqual((self.res["statut"], self.res["etapes"]), ("fini", 3))
        self.assertEqual(self.res["reponse"], "Mensualité 5 558,32 AED, soit 1 513,50 USD ; "
                                              "endettement total 28,9 % ≤ 50 % : dossier recevable.")
        self.assertTrue(self.s["but"])

    def test_appels_d_outils_et_sorties(self):
        self.assertEqual([(n, a) for n, a, _ in self.res["trace"]],
                         [("mensualite", A_MENSUALITE), ("ratio_endettement", A_RATIO), ("convertir_aed_usd", A_CONVERSION)])
        self.assertEqual([s for _, _, s in self.res["trace"]],
                         [{"mensualite_aed": 5558.32}, {"ratio": 0.289, "recevable": True}, {"montant_usd": 1513.5}])

    def test_memoire_rappelee_dans_le_systeme(self):
        self.assertEqual([round(score, 4) for score, _ in self.res["rappel"]], [0.9769, 0.807])
        systeme = self.s["agent"].llm.requetes[0]["system"]
        self.assertIn("- Salaire mensuel déclaré au dossier de crédit : 40 000 AED", systeme)
        self.assertNotIn("taux de change", systeme)
        self.assertEqual([s.jour_acces for s in self.s["agent"].memoire], [90.0, 90.0, 0.0, 88.0])

    def test_sept_outils_stricts_envoyes_au_modele(self):
        outils = self.s["agent"].llm.requetes[0]["tools"]
        self.assertEqual([o["name"] for o in outils], ["rechercher_reglementation", "mensualite", "ratio_endettement",
                                                       "convertir_aed_usd", "gratuite_fin_de_service", "tva",
                                                       "initier_virement"])
        self.assertTrue(all(o["strict"] for o in outils))

    def test_journal_politique_et_chaine(self):
        journal = self.s["agent"].journal
        self.assertEqual(journal.textes().count("politique client_banque -> mensualite : autorisé"), 1)
        self.assertIsNone(journal.verifier())


class TestScenariosRagEtVirement(unittest.TestCase):
    def test_reglementation_cite_ce_qu_elle_a_recu(self):
        s = scenario_reglementation()
        rendus = s["res"]["trace"][0][2]
        self.assertEqual(rendus["ids"], ["REG-1", "REG-2", "FORUM-9"])
        self.assertIn("&lt;system>", rendus["documents"][2])
        self.assertTrue(s["but"])

    def test_virement_piege_refuse(self):
        s = scenario_virement()
        agent, res = s["agent"], s["res"]
        self.assertEqual(res["trace"][0][2], "ERREUR refusé par l'humain : pas de réponse en 120 s : refus par défaut")
        self.assertEqual(agent.virements, [])
        self.assertEqual(agent.horloge.t - 90 * 86_400, 120.0)
        tout = "\n".join(agent.journal.textes())
        self.assertFalse(any(clair in tout for clair in ("AE07 0331", "784-1990-1234567-1", "+971 50 123 4567")))
        self.assertTrue(all(x in tout for x in ("[IBAN ••••3456]", "[EMIRATES_ID ••••5671]", "[TEL ••••4567]")))
        self.assertTrue(s["but"])

    def test_session_publique_refusee_par_la_politique(self):
        script = [Reponse("tool_use", [appel_outil("mensualite", A_MENSUALITE, "p1")]),
                  Reponse("end_turn", [texte("Je ne peux pas calculer cela ici.")])]
        agent = construire_agent(script, session={"role": "assistant_public", "portees": {"lecture"}})
        res = agent.repondre("Quelle mensualité ?")
        self.assertEqual(res["trace"][0][2], "ERREUR outil mensualite non autorisé pour le rôle assistant_public")
        self.assertEqual(res["rappel"], [])

    def test_agent_accepte_n_importe_quel_port(self):
        agent = Agent(FakeLLM([Reponse("end_turn", [texte("Bonjour.")])]))
        res = agent.repondre("Bonjour")
        self.assertEqual((res["statut"], res["reponse"]), ("fini", "Bonjour."))
        self.assertEqual(json.loads(json.dumps(res["sources"]))[1], "Bonjour")


class TestDemandeCredit(unittest.TestCase):
    def test_variante_1(self):
        script, q, attendus, verdict = demande_credit(1)
        self.assertEqual(attendus, [("mensualite", {"principal": 975_000, "taux_annuel": 0.045, "n_mois": 300}),
                                    ("ratio_endettement", {"existantes": 6_500, "nouvelle": 5419.37, "revenu": 38_500})])
        self.assertEqual(verdict, "recevable")
        self.assertTrue(script[-1].content[0].text.endswith("endettement total 30,96 % : dossier recevable."))

    def test_verdicts_des_quinze_variantes(self):
        self.assertEqual([demande_credit(i)[3] == "recevable" for i in range(1, 16)], [True] * 7 + [False] * 8)
        self.assertTrue(demande_credit(8)[0][-1].content[0].text.endswith("51,60 % : dossier non recevable."))

    def test_la_candidate_oublie_le_ratio(self):
        script, _, _, _ = demande_credit(5, candidat=True)
        self.assertEqual(len(script), 2)
        self.assertIn("estimé à 35 %", script[1].content[0].text)
        self.assertEqual(len(demande_credit(6, candidat=True)[0]), 3)


class TestBarriereCI(unittest.TestCase):
    def setUp(self):
        self.ev = evaluation_complete()

    def test_trois_scenarios_parfaits(self):
        self.assertEqual([(n["f1"], n["fidelite"], n["but"]) for n in self.ev["communes"]], [(1.0, 1.0, True)] * 3)
        self.assertEqual(barriere_ci(rapport(self.ev["communes"]))[0], 1)     # 3 cas ne prouvent pas 80 %

    def test_production_deployable(self):
        prod = self.ev["production"]
        self.assertEqual((prod["succes"], prod["n"], prod["code"], prod["motifs"]), (18, 18, 0, []))
        self.assertTrue(math.isclose(prod["wilson"][0], 18 / (18 + 1.96 ** 2)))

    def test_candidate_bloquee(self):
        cand = self.ev["candidate"]
        self.assertEqual((cand["succes"], cand["code"], len(cand["motifs"])), (14, 1, 3))
        self.assertAlmostEqual(cand["tool_f1"], (14 + 4 * 2 / 3) / 18, places=12)
        self.assertAlmostEqual(cand["fidelite"], (14 + 4 * 0.5) / 18, places=12)
        self.assertAlmostEqual(cand["wilson"][0], 0.548, places=3)
        self.assertEqual(cand["motifs"][0], "borne basse de Wilson 0.548 < 0.8")


if __name__ == "__main__":
    unittest.main()
