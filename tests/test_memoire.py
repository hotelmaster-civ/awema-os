"""Invariant : l'application de paires à la Mémoire Marketing (fonction pure)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import awema  # noqa: E402


class TestMemoire(unittest.TestCase):
    def test_scalaires_et_nested(self):
        m = awema.appliquer_memoire(awema.memoire_vide(), [
            'ton=chaleureux', 'mission=aider les PME', 'cible=PME ivoiriennes', 'secteur=Tech'])
        self.assertEqual(m["ton"], "chaleureux")
        self.assertEqual(m["identite"]["mission"], "aider les PME")
        self.assertEqual(m["identite"]["cible"], "PME ivoiriennes")
        self.assertEqual(m["identite"]["secteur"], "Tech")

    def test_listes_append(self):
        m = awema.appliquer_memoire(awema.memoire_vide(), [
            'faq+=Livrez-vous ?::Oui, sous 48h.',
            'persona+=Awa::veut gagner du temps::prix',
            'produit+=Pack Social::3 posts/sem::25000',
            'mot_cle+=proximité'])
        self.assertEqual(m["faq"][0], {"q": "Livrez-vous ?", "r": "Oui, sous 48h."})
        self.assertEqual(m["personas"][0]["nom"], "Awa")
        self.assertEqual(m["personas"][0]["objection"], "prix")
        self.assertEqual(m["produits"][0]["nom"], "Pack Social")
        self.assertEqual(m["charte"]["mots_cles"], ["proximité"])

    def test_cle_inconnue_leve(self):
        with self.assertRaises(ValueError):
            awema.appliquer_memoire(awema.memoire_vide(), ['inconnu=x'])

    def test_idempotence_partielle(self):
        # remplir deux fois n'écrase pas les listes existantes (append), met à jour les scalaires
        m = awema.appliquer_memoire(awema.memoire_vide(), ['ton=a', 'faq+=q::r'])
        m = awema.appliquer_memoire(m, ['ton=b', 'faq+=q2::r2'])
        self.assertEqual(m["ton"], "b")
        self.assertEqual(len(m["faq"]), 2)


if __name__ == "__main__":
    unittest.main()
