"""Palier 04 — registre d'outils, porte de validation, définitions pour l'API, enveloppe d'erreur."""
import json
import unittest

from agent.modele import appel_outil
from agent.outils import (ArgumentsInvalides, ErreurOutil, RefusPolitique, Registre, enregistrer_outils_metier,
                          executer_appel)
from agent.schemas import NON_STRICT, objet


def registre_metier() -> Registre:
    return enregistrer_outils_metier(Registre())


class TestRegistre(unittest.TestCase):
    def test_cinq_outils_metier(self):
        r = registre_metier()
        self.assertEqual(len(r), 5)
        self.assertEqual(list(r.outils), ["mensualite", "ratio_endettement", "convertir_aed_usd",
                                          "gratuite_fin_de_service", "tva"])
        self.assertIn("tva", r)

    def test_nom_deja_pris_ou_vide(self):
        r = registre_metier()
        with self.assertRaises(ValueError):
            r.outil("tva", "doublon", objet({}))
        with self.assertRaises(ValueError):
            r.outil("", "sans nom", objet({}))

    def test_le_decorateur_rend_la_fonction(self):
        r = Registre()

        @r.outil("double", "Double un nombre.", objet({"x": {"type": "number"}}))
        def double(x):
            return 2 * x
        self.assertEqual(double(4), 8)
        self.assertEqual(r.outils["double"].fonction, double)

    def test_hierarchie_des_exceptions(self):
        self.assertTrue(issubclass(ArgumentsInvalides, ValueError))
        self.assertTrue(issubclass(RefusPolitique, PermissionError))
        resultat, _ = executer_appel(registre_metier().appelables(), appel_outil("tva", {"montant_ht": "x"}, "e"))
        self.assertTrue(resultat["content"].startswith("ArgumentsInvalides: "))


class TestPorte(unittest.TestCase):
    def test_appel_valide(self):
        porte = registre_metier().porte("mensualite")
        self.assertEqual(porte(principal=1_000_000, taux_annuel=0.045, n_mois=300), {"mensualite_aed": 5558.32})

    def test_le_schema_arrete_avant_la_fonction(self):
        r, appels = Registre(), []

        @r.outil("compter", "Compte.", objet({"n": {"type": "integer", "minimum": 1}}))
        def compter(n):
            appels.append(n)
            return n
        with self.assertRaises(ArgumentsInvalides) as ctx:
            r.porte("compter")(n="3")
        self.assertEqual(str(ctx.exception), "$.n : type attendu integer, reçu string")
        with self.assertRaises(ArgumentsInvalides):
            r.porte("compter")(n=1, bonus=True)
        self.assertEqual(appels, [])

    def test_outil_inconnu(self):
        with self.assertRaises(ValueError):
            registre_metier().porte("virement")


class TestDefinitionsApi(unittest.TestCase):
    def test_mode_strict_sans_bornes(self):
        defs = registre_metier().definitions_api()
        self.assertEqual(len(defs), 5)
        self.assertTrue(all(d["strict"] for d in defs))
        self.assertFalse(any(f'"{k}"' in json.dumps(defs) for k in NON_STRICT))
        n_mois = defs[0]["input_schema"]["properties"]["n_mois"]
        self.assertEqual(n_mois, {"type": "integer", "description": "Contraintes : minimum=1, maximum=300."})


class TestOutilsMetier(unittest.TestCase):
    def test_sorties_arrondies_comme_dans_77(self):
        o = registre_metier().appelables()
        self.assertEqual(o["ratio_endettement"](existantes=6_000, nouvelle=5558.32, revenu=40_000),
                         {"ratio": 0.289, "recevable": True})
        self.assertEqual(o["convertir_aed_usd"](montant_aed=5558.32), {"montant_usd": 1513.5})
        self.assertEqual(o["tva"](montant_ht=12_000), {"tva_aed": 600, "ttc_aed": 12_600})
        self.assertEqual(o["gratuite_fin_de_service"](salaire_base_mensuel=10_000, annees=7), {"indemnite_aed": 55_000})


class TestExecuterAppel(unittest.TestCase):
    def test_succes(self):
        resultat, ligne = executer_appel(registre_metier().appelables(), appel_outil("tva", {"montant_ht": 100}, "t1"))
        self.assertEqual(resultat, {"type": "tool_result", "tool_use_id": "t1", "content": '{"tva_aed": 5.0, "ttc_aed": 105.0}'})
        self.assertEqual(ligne, ("tva", {"montant_ht": 100}, {"tva_aed": 5.0, "ttc_aed": 105.0}))

    def test_erreur_renvoyee_avec_is_error(self):
        bloc = appel_outil("mensualite", {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": "300"}, "m1")
        resultat, ligne = executer_appel(registre_metier().appelables(), bloc)
        self.assertTrue(resultat["is_error"])
        self.assertEqual(resultat["content"], "ArgumentsInvalides: $.n_mois : type attendu integer, reçu string")
        self.assertEqual(ligne[2], "ERREUR $.n_mois : type attendu integer, reçu string")

    def test_outil_inconnu(self):
        resultat, ligne = executer_appel({}, appel_outil("pirater", {}, "x"))
        self.assertEqual(resultat["content"], "ErreurOutil: outil inconnu : pirater")
        self.assertEqual(ligne, ("pirater", {}, "ERREUR outil inconnu : pirater"))


if __name__ == "__main__":
    unittest.main()
