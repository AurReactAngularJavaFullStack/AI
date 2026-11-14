"""Palier 09 — politique, masquage, journal chaîné, risque et veto, approbation, porte protégée, virement."""
import hashlib
import itertools
import unittest

from agent.boucle import executer_agent
from agent.garde_fous import (GENESE, Approbateur, JournalAudit, autoriser, decider, enregistrer_virement, gravite,
                              masquer, proteger, score_risque, veto)
from agent.modele import FakeLLM, Horloge, Reponse, appel_outil, texte
from agent.outils import ErreurOutil, RefusPolitique, Registre, enregistrer_outils_metier

IBAN = "AE07 0331 2345 6789 0123 456"
CLIENT = {"role": "client_banque", "portees": {"lecture", "virement:initier"}}


def monde(incertitude=0.1):
    """Un registre complet, protégé, avec son horloge, son journal, son approbateur et ses virements."""
    horloge = Horloge(90 * 86_400.0)
    journal = JournalAudit(horloge)
    approbateur, virements = Approbateur(horloge, journal), []
    registre = enregistrer_outils_metier(Registre())
    enregistrer_virement(registre, approbateur, journal, virements, incertitude=incertitude)
    session = dict(CLIENT)
    return {"horloge": horloge, "journal": journal, "approbateur": approbateur, "virements": virements,
            "session": session, "outils": proteger(registre, session, journal)}


class TestPolitique(unittest.TestCase):
    def test_trois_refus_et_un_accord(self):
        self.assertEqual(autoriser("assistant_public", "initier_virement", {"lecture"}),
                         (False, "outil initier_virement non autorisé pour le rôle assistant_public"))
        self.assertEqual(autoriser("", "tva", {"lecture"}), (False, "rôle inconnu : (aucun)"))
        self.assertEqual(autoriser("client_banque", "initier_virement", {"lecture"}),
                         (False, "portée manquante : virement:initier"))
        self.assertEqual(autoriser("client_banque", "initier_virement", CLIENT["portees"]), (True, "autorisé"))

    def test_politique_personnalisee(self):
        politique = {"rh": {"gratuite_fin_de_service": {"paie:lire"}}}
        self.assertTrue(autoriser("rh", "gratuite_fin_de_service", {"paie:lire"}, politique)[0])
        self.assertFalse(autoriser("client_banque", "tva", {"lecture"}, politique)[0])


class TestMasquage(unittest.TestCase):
    def test_identite_et_telephone(self):
        self.assertEqual(masquer("Emirates ID 784-1990-1234567-1, tél. +971 50 123 4567"),
                         "Emirates ID [EMIRATES_ID ••••5671], tél. [TEL ••••4567]")

    def test_iban_email_et_long_numero(self):
        self.assertEqual(masquer(f"IBAN {IBAN}"), "IBAN [IBAN ••••3456]")
        self.assertEqual(masquer("écrire à c-1@banque-b1.ae"), "écrire à [EMAIL]")
        self.assertEqual(masquer("AE08 0331 2345 6789 0123 456"), "AE[NUMERO ••••3456]")   # clé fausse : pas un IBAN
        self.assertEqual(masquer("montant 180000 AED"), "montant 180000 AED")              # 6 chiffres : gardé


class TestJournal(unittest.TestCase):
    def test_masque_avant_d_ecrire_et_chaine(self):
        h = Horloge(5.0)
        j = JournalAudit(h)
        self.assertEqual(j.journaliser(f"virement vers {IBAN}"), "virement vers [IBAN ••••3456]")
        h.avancer(10)
        j.journaliser("deuxième")
        self.assertEqual(j.textes(), ["virement vers [IBAN ••••3456]", "deuxième"])
        attendu = hashlib.sha256((GENESE + JournalAudit.corps(5.0, j.textes()[0])).encode("utf-8")).hexdigest()
        self.assertEqual(j.entrees[0]["hash"], attendu)
        self.assertEqual((j.entrees[1]["precedent"], j.entrees[1]["t"]), (attendu, 15.0))
        self.assertIsNone(j.verifier())

    def test_modification_detectee(self):
        j = JournalAudit()
        for e in ("a", "b", "c"):
            j.journaliser(e)
        j.entrees[1]["texte"] = "b modifié"
        self.assertEqual(j.verifier(), 1)


class TestRisque(unittest.TestCase):
    def test_gravite_et_score(self):
        self.assertEqual(gravite("irreversible", 180_000), 1.0)
        self.assertAlmostEqual(gravite("ecriture_reversible", 40_000), 0.8, places=12)
        self.assertAlmostEqual(score_risque(0.7, 1.0, 0.1), 0.70, places=12)
        with self.assertRaises(ValueError):
            gravite("inconnu")

    def test_borne_sur_la_grille(self):
        valeurs = [score_risque(s, g, u) for s, g, u in itertools.product([x / 4 for x in range(5)], repeat=3)]
        self.assertEqual(len(valeurs), 125)
        self.assertEqual(min(valeurs), 0.0)
        self.assertAlmostEqual(max(valeurs), 1.0, places=12)
        with self.assertRaises(ValueError):
            score_risque(1.2, 0, 0)
        with self.assertRaises(ValueError):
            score_risque(0.5, 0.5, 0.5, (0.5, 0.5, 0.5))

    def test_veto_et_decision(self):
        self.assertTrue(veto("irreversible", 10))
        self.assertTrue(veto("lecture", 30_000))
        self.assertFalse(veto("ecriture_reversible", 2_500))
        r_faible, r_injection = score_risque(0.1, 1.0, 0.1), score_risque(0.7, 1.0, 1.0)
        self.assertAlmostEqual(r_faible, 0.46, places=12)
        self.assertEqual((decider(r_faible, False), decider(r_faible, True), decider(r_injection, True)),
                         ("autoriser", "revue", "bloquer"))
        with self.assertRaises(ValueError):
            decider(0.5, False, tau_revue=0.8, tau_blocage=0.7)


class TestApprobateur(unittest.TestCase):
    def test_pas_de_reponse_vaut_refus(self):
        h, j = Horloge(), JournalAudit()
        a = Approbateur(h, j)
        self.assertEqual(a.demander("virement"), (False, "pas de réponse en 120 s : refus par défaut"))
        self.assertEqual(h.t, 120.0)
        self.assertEqual(j.textes(), ["approbation : virement -> refus par délai"])

    def test_reponse_dans_le_delai_ou_trop_tardive(self):
        h = Horloge()
        a = Approbateur(h, JournalAudit(h))
        a.reponses = [("approuvé", 45.0), ("approuvé", 130.0)]
        self.assertEqual(a.demander("v1"), (True, "approuvé"))
        self.assertFalse(a.demander("v2")[0])
        self.assertEqual(h.t, 165.0)


class TestPorteProtegeeEtVirement(unittest.TestCase):
    def test_politique_avant_le_schema(self):
        m = monde()
        m["session"].update(role="assistant_public", portees={"lecture"})
        with self.assertRaises(RefusPolitique):
            m["outils"]["mensualite"](principal="pas un nombre", taux_annuel=0.045, n_mois=300)
        self.assertEqual(m["journal"].textes(), ["politique assistant_public -> mensualite : outil mensualite "
                                                 "non autorisé pour le rôle assistant_public"])

    def test_virement_de_180000_refuse_sans_humain(self):
        m = monde()
        with self.assertRaises(ErreurOutil) as ctx:
            m["outils"]["initier_virement"](iban=IBAN, montant_aed=180_000, motif="Acompte off-plan, lot 214")
        self.assertEqual(str(ctx.exception), "refusé par l'humain : pas de réponse en 120 s : refus par défaut")
        self.assertEqual(m["virements"], [])
        self.assertIn("risque virement [IBAN ••••3456] de 180000 AED : R = 0.70, veto, décision revue",
                      m["journal"].textes())

    def test_virement_approuve_puis_injection_bloquee(self):
        m = monde()
        m["approbateur"].reponses = [("approuvé", 45.0)]
        self.assertEqual(m["outils"]["initier_virement"](iban=IBAN, montant_aed=2_500, motif="loyer"),
                         {"statut": "exécuté", "montant_aed": 2_500})
        self.assertEqual(len(m["virements"]), 1)
        b = monde(incertitude=1.0)                       # signal d'injection : R = 0.88
        with self.assertRaises(ErreurOutil) as ctx:
            b["outils"]["initier_virement"](iban=IBAN, montant_aed=2_500, motif="loyer")
        self.assertEqual(str(ctx.exception), "bloqué par le garde-fou : R = 0.88 >= 0.75")
        self.assertEqual(b["horloge"].t, 90 * 86_400.0)  # l'humain n'a même pas été sollicité

    def test_dans_la_boucle_l_erreur_repart_vers_le_modele(self):
        m = monde()
        llm = FakeLLM([Reponse("tool_use", [appel_outil("initier_virement",
                                                        {"iban": "AE08 0331 2345 6789 0123 456", "montant_aed": 10,
                                                         "motif": "test"}, "v")]),
                       Reponse("end_turn", [texte("IBAN refusé.")])])
        r = executer_agent(llm, "s", "q", m["outils"], [])
        self.assertEqual(r["trace"][0][2], "ERREUR IBAN AE invalide (contrôle mod 97)")
        self.assertEqual((r["statut"], m["virements"]), ("fini", []))


if __name__ == "__main__":
    unittest.main()
