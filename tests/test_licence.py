"""Invariant : registre de délivrance des licences (preuve) + validation de format."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import awema  # noqa: E402


class TestLicence(unittest.TestCase):
    def test_ledger_incremente_et_hash(self):
        led = {"licences": []}
        e1 = awema.licence_ajouter(led, "Agence A", "a@x.com", "AWEMA-1111-2222-3333", "2026-06-26T10:00:00+00:00")
        e2 = awema.licence_ajouter(led, "Agence B", "", "AWEMA-4444-5555-6666", "2026-06-26T11:00:00+00:00")
        self.assertEqual((e1["n"], e2["n"]), (1, 2))
        self.assertEqual(e1["statut"], "delivree")
        self.assertEqual(e1["agence"], "Agence A")
        self.assertEqual(len(e1["cle_hash"]), 64)           # sha256
        self.assertEqual(len(led["licences"]), 2)

    def test_acces_demande(self):
        reg = {"demandes": []}
        e = awema.acces_ajouter(reg, "Agence A", "a@x.com", "Resto", "meta", "client commun",
                                "2026-06-26T10:00:00+00:00")
        self.assertEqual(e["id"], 1)
        self.assertEqual(e["statut"], "en_attente")
        self.assertEqual(e["reseau"], "meta")
        self.assertEqual(e["client"], "Resto")
        self.assertEqual(len(reg["demandes"]), 1)

    def test_attente_ajoute_et_dedoublonne(self):
        reg = {"inscrits": []}
        e1 = awema.attente_ajouter(reg, "Awa K.", "awa@x.com", "Community manager",
                                   "2026-06-27T10:00:00+00:00")
        awema.attente_ajouter(reg, "Awa (doublon)", "AWA@x.com", "Agence",
                              "2026-06-27T11:00:00+00:00")  # même contact, casse ≠ → ignoré
        e3 = awema.attente_ajouter(reg, "Ben T.", "ben@x.com", "Marque",
                                   "2026-06-27T12:00:00+00:00")
        self.assertEqual(e1["n"], 1)
        self.assertEqual(e1["profil"], "Community manager")
        self.assertEqual(e3["n"], 2)
        self.assertEqual(len(reg["inscrits"]), 2)           # le doublon n'a pas été ajouté

    def test_format_cle(self):
        self.assertTrue(awema._licence_valide("AWEMA-1A2B-3C4D-5E6F"))
        self.assertFalse(awema._licence_valide("pas-bon"))
        self.assertFalse(awema._licence_valide(""))


if __name__ == "__main__":
    unittest.main()
