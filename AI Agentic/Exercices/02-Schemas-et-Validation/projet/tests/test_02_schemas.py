"""Palier 02 — validateur minimal, schéma strict pour l'API, boucle de réparation."""
import json
import unittest

from agent.modele import FakeLLM, Reponse, texte
from agent.schemas import (NON_STRICT, SCHEMA_DEMANDE_CREDIT, essais_moyens, lire_et_valider, objet, p_succes,
                           reparer, schema_pour_api_strict, validate)

N_MOIS = {"type": "integer", "minimum": 1, "maximum": 300}
BASE = {"montant_aed": 150_000, "duree_mois": 36, "revenu_mensuel_aed": 25_000, "emirates_id": "784-1990-1234567-1"}


class TestValidateTypes(unittest.TestCase):
    def test_type_faux_avec_chemin(self):
        schema = objet({"n_mois": N_MOIS})
        self.assertEqual(validate({"n_mois": "300"}, schema), ["$.n_mois : type attendu integer, reçu string"])

    def test_booleen_n_est_pas_un_entier(self):
        self.assertEqual(validate(True, {"type": "integer"}), ["$ : type attendu integer, reçu boolean"])
        self.assertEqual(validate(None, {"type": "number"}), ["$ : type attendu number, reçu null"])

    def test_decimal_refuse_comme_entier_et_nan_refuse(self):
        self.assertEqual(validate(36.0, {"type": "integer"}), ["$ : type attendu integer, reçu number"])
        self.assertEqual(validate(float("nan"), {"type": "number", "minimum": 0}),
                         ["$ : nombre non fini (nan), interdit en JSON"])

    def test_mot_cle_inconnu_refuse(self):
        with self.assertRaises(ValueError):
            validate(5, {"type": "integer", "multipleOf": 5})


class TestValidateContraintes(unittest.TestCase):
    def test_bornes_numeriques(self):
        self.assertEqual(validate(0, {"exclusiveMinimum": 0}), ["$ : 0 doit être > 0"])
        self.assertEqual(validate(301, N_MOIS), ["$ : 301 > maximum 300"])
        self.assertEqual(validate(0, N_MOIS), ["$ : 0 < minimum 1"])
        self.assertEqual(validate(300, N_MOIS), [])

    def test_chaines(self):
        s = {"type": "string", "minLength": 1, "maxLength": 3, "pattern": "^[A-Z]+$"}
        self.assertEqual(validate("", s), ["$ : longueur 0 < minLength 1", "$ : '' ne respecte pas le motif ^[A-Z]+$"])
        self.assertEqual(validate("ABCD", s), ["$ : longueur 4 > maxLength 3"])

    def test_objet_champs_absents_et_non_prevus(self):
        mauvaise = dict(BASE, duree_mois=6, commentaire="urgent")
        del mauvaise["emirates_id"]
        self.assertEqual(validate(mauvaise, SCHEMA_DEMANDE_CREDIT), [
            "$ : champ obligatoire absent « emirates_id »",
            "$.duree_mois : 6 < minimum 12",
            "$ : champ non prévu « commentaire »"])
        self.assertEqual(validate(BASE, SCHEMA_DEMANDE_CREDIT), [])


class TestSchemaStrict(unittest.TestCase):
    def test_objet(self):
        self.assertEqual(objet({"x": {"type": "number"}}), {"type": "object", "properties": {"x": {"type": "number"}},
                                                            "required": ["x"], "additionalProperties": False})
        self.assertEqual(objet(SCHEMA_DEMANDE_CREDIT["properties"]), SCHEMA_DEMANDE_CREDIT)

    def test_bornes_retirees_et_recopiees(self):
        api = schema_pour_api_strict(objet({"n_mois": N_MOIS}))
        self.assertEqual(api["properties"]["n_mois"],
                         {"type": "integer", "description": "Contraintes : minimum=1, maximum=300."})
        self.assertFalse(any(f'"{k}"' in json.dumps(api) for k in NON_STRICT))

    def test_la_validation_locale_reste_necessaire(self):
        six_mois = dict(BASE, duree_mois=6)
        self.assertEqual(validate(six_mois, schema_pour_api_strict(SCHEMA_DEMANDE_CREDIT)), [])
        self.assertEqual(validate(six_mois, SCHEMA_DEMANDE_CREDIT), ["$.duree_mois : 6 < minimum 12"])


class TestReparation(unittest.TestCase):
    def test_json_dans_un_bloc_de_code(self):
        fence = "`" * 3
        self.assertEqual(lire_et_valider(fence + "json\n{}\n" + fence, {}),
                         (None, ["$ : JSON illisible (Expecting value, position 0)"]))

    def test_une_relance_suffit(self):
        essai1 = json.dumps(dict(BASE, duree_mois="36"))
        llm = FakeLLM([Reponse("end_turn", [texte(essai1)]), Reponse("end_turn", [texte(json.dumps(BASE))])])
        r = reparer(llm, SCHEMA_DEMANDE_CREDIT, "Prêt de 150 000 AED sur 36 mois")
        self.assertEqual((r["statut"], r["essais"], llm.appels, r["donnees"]), ("valide", 2, 2, BASE))
        self.assertEqual(r["erreurs"], [["$.duree_mois : type attendu integer, reçu string"], []])
        dernier = llm.requetes[1]["messages"][-1]["content"]      # le modèle voit les chemins à corriger
        self.assertIn("$.duree_mois : type attendu integer", dernier)

    def test_echec_apres_max_essais(self):
        faux = json.dumps(dict(BASE, montant_aed=0))
        llm = FakeLLM([Reponse("end_turn", [texte(faux)])] * 3)
        r = reparer(llm, SCHEMA_DEMANDE_CREDIT, "...", max_essais=3)
        self.assertEqual((r["statut"], r["essais"], llm.appels, r["donnees"]), ("echec", 3, 3, None))

    def test_refus_traite_avant_le_contenu(self):
        r = reparer(FakeLLM([Reponse("refusal", [])]), SCHEMA_DEMANDE_CREDIT, "...")
        self.assertEqual((r["statut"], r["essais"], r["erreurs"]), ("refusal", 1, []))
        with self.assertRaises(ValueError):
            reparer(FakeLLM([]), SCHEMA_DEMANDE_CREDIT, "...", max_essais=0)

    def test_probabilites(self):
        self.assertAlmostEqual(p_succes(0.9, 2), 0.999, places=12)
        self.assertAlmostEqual(essais_moyens(0.9, 2), 1.11, places=12)
        self.assertAlmostEqual(essais_moyens(0.9, 2), p_succes(0.9, 2) / 0.9, places=12)
        for p, r in ((0.0, 1), (1.2, 1), (0.5, -1)):
            with self.assertRaises(ValueError):
                p_succes(p, r)


if __name__ == "__main__":
    unittest.main()
