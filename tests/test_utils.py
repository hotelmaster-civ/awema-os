"""Invariants des helpers purs d'awema.py : slug, initiales, validation de licence."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import awema  # noqa: E402


class TestSlugify(unittest.TestCase):
    def test_accents_supprimes(self):
        self.assertEqual(awema._slugify("Éclat Beauté"), "eclat-beaute")

    def test_espaces_et_ponctuation_collapses(self):
        self.assertEqual(awema._slugify("Code  Scooper !"), "code-scooper")

    def test_vide_donne_fallback(self):
        self.assertEqual(awema._slugify(""), "client")

    def test_idempotent_sur_un_slug(self):
        self.assertEqual(awema._slugify("mon-client"), "mon-client")


class TestInitiales(unittest.TestCase):
    def test_deux_mots(self):
        self.assertEqual(awema._initiales("Code Scooper"), "CS")

    def test_un_seul_mot(self):
        self.assertEqual(awema._initiales("Awema"), "AW")

    def test_vide_donne_AW(self):
        self.assertEqual(awema._initiales(""), "AW")


class TestLicenceFormat(unittest.TestCase):
    def test_format_valide(self):
        self.assertTrue(awema._licence_valide("AWEMA-1A2B-3C4D-5E6F"))

    def test_minuscules_refusees(self):
        self.assertFalse(awema._licence_valide("awema-1a2b-3c4d-5e6f"))

    def test_trop_court_refuse(self):
        self.assertFalse(awema._licence_valide("AWEMA-1A2B-3C4D"))

    def test_vide_refuse(self):
        self.assertFalse(awema._licence_valide(""))


if __name__ == "__main__":
    unittest.main()
