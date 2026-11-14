"""Palier 05 — boucle d'agent : les cinq arrêts, le scénario de 77, les erreurs renvoyées au modèle."""
import unittest

from agent.boucle import STATUTS, executer_agent, signature_appels
from agent.modele import FakeLLM, Reponse, appel_outil, texte
from agent.outils import Registre, enregistrer_outils_metier


def outils():
    return enregistrer_outils_metier(Registre()).appelables()


def tva(v, id_="t"):
    return Reponse("tool_use", [appel_outil("tva", {"montant_ht": v}, id_)])


class TestArrets(unittest.TestCase):
    def test_reponse_finale_directe(self):
        r = executer_agent(FakeLLM([Reponse("end_turn", [texte("Bonjour"), texte(" !")])]), "s", "q", outils(), [])
        self.assertEqual((r["statut"], r["reponse"], r["etapes"], r["trace"]), ("fini", "Bonjour !", 1, []))

    def test_refus_et_troncature(self):
        self.assertEqual(executer_agent(FakeLLM([Reponse("refusal", [])]), "s", "q", outils(), [])["statut"], "refus")
        r = executer_agent(FakeLLM([Reponse("max_tokens", [texte("coupé")])]), "s", "q", outils(), [])
        self.assertEqual((r["statut"], r["etapes"]), ("tronque", 1))
        self.assertNotIn("reponse", r)

    def test_meme_action_deux_fois(self):
        r = executer_agent(FakeLLM([tva(100)] * 2), "s", "q", outils(), [])
        self.assertEqual((r["statut"], r["etapes"], len(r["trace"])), ("boucle", 2, 1))

    def test_max_etapes_borne_les_appels(self):
        llm = FakeLLM([tva(v) for v in (1, 2, 3)])
        r = executer_agent(llm, "s", "q", outils(), [], max_etapes=2)
        self.assertEqual((r["statut"], r["etapes"], llm.appels, len(r["trace"])), ("max_etapes", 2, 2, 2))
        with self.assertRaises(ValueError):
            executer_agent(FakeLLM([]), "s", "q", outils(), [], max_etapes=0)

    def test_pause_turn_relance_sans_executer(self):
        llm = FakeLLM([Reponse("pause_turn", [texte("…")]), Reponse("end_turn", [texte("ok")])])
        r = executer_agent(llm, "s", "q", outils(), [])
        self.assertEqual((r["statut"], r["etapes"], r["trace"]), ("fini", 2, []))

    def test_cinq_statuts(self):
        self.assertEqual(STATUTS, ("fini", "refus", "tronque", "boucle", "max_etapes"))
        scripts = ([Reponse("end_turn", [texte("ok")])], [Reponse("refusal", [])], [Reponse("max_tokens", [])],
                   [tva(1)] * 2, [tva(1), tva(2)])
        statuts = [executer_agent(FakeLLM(s), "s", "q", outils(), [], max_etapes=2)["statut"] for s in scripts]
        self.assertEqual(tuple(statuts), STATUTS)


class TestScenarioCredit(unittest.TestCase):
    def setUp(self):
        a1 = {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300}
        a2, a3 = {"existantes": 6_000, "nouvelle": 5558.32, "revenu": 40_000}, {"montant_aed": 5558.32}
        self.llm = FakeLLM([
            Reponse("tool_use", [appel_outil("mensualite", a1, "a1")]),
            Reponse("tool_use", [appel_outil("ratio_endettement", a2, "a2"), appel_outil("convertir_aed_usd", a3, "a3")]),
            Reponse("end_turn", [texte("Dossier recevable.")])])
        self.r = executer_agent(self.llm, "s", "q", outils(), [{"name": "x"}])

    def test_trois_etapes_et_sorties(self):
        self.assertEqual((self.r["statut"], self.r["etapes"]), ("fini", 3))
        self.assertEqual([s for _, _, s in self.r["trace"]],
                         [{"mensualite_aed": 5558.32}, {"ratio": 0.289, "recevable": True}, {"montant_usd": 1513.5}])

    def test_tous_les_resultats_dans_un_seul_message(self):
        dernier = self.llm.requetes[2]["messages"][-1]
        self.assertEqual(dernier["role"], "user")
        self.assertEqual([b["tool_use_id"] for b in dernier["content"]], ["a2", "a3"])
        self.assertEqual(len(self.r["messages"]), 6)             # user, (assistant, user) × 2, assistant

    def test_contenu_recopie_tel_quel_et_outils_transmis(self):
        self.assertIs(self.r["messages"][1]["content"], self.llm.script[0].content)
        self.assertEqual(self.llm.requetes[0]["tools"], [{"name": "x"}])


class TestErreurs(unittest.TestCase):
    def test_erreur_d_outil_renvoyee_au_modele(self):
        llm = FakeLLM([Reponse("tool_use", [appel_outil("tva", {"montant_ht": -5}, "e1")]),
                       Reponse("end_turn", [texte("Montant invalide.")])])
        r = executer_agent(llm, "s", "q", outils(), [])
        resultat = llm.requetes[1]["messages"][-1]["content"][0]
        self.assertTrue(resultat["is_error"])
        self.assertEqual(resultat["content"], "ArgumentsInvalides: $.montant_ht : -5 < minimum 0")
        self.assertEqual(r["trace"][0][2], "ERREUR $.montant_ht : -5 < minimum 0")
        self.assertEqual(r["statut"], "fini")

    def test_signature_independante_de_l_ordre_des_arguments(self):
        a = appel_outil("ratio", {"b": 2, "a": 1}, "x")
        b = appel_outil("ratio", {"a": 1, "b": 2}, "y")
        self.assertEqual(signature_appels([a]), signature_appels([b]))
        self.assertEqual(signature_appels([a]), [("ratio", '{"a": 1, "b": 2}')])


if __name__ == "__main__":
    unittest.main()
