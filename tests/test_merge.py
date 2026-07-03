"""Invariant : la fusion multi-réseaux préserve les réseaux non touchés (zéro régression)."""
import json
import os
import tempfile
import unittest

from tests.util import charger

cr = charger("scripts/connect-reseaux.py", "cr")


class TestFusion(unittest.TestCase):
    def _client(self, base):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "_donnees"))
        with open(os.path.join(d, "_donnees", "reseaux.json"), "w", encoding="utf-8") as f:
            json.dump(base, f)
        return d

    @staticmethod
    def _read(d):
        with open(os.path.join(d, "_donnees", "reseaux.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_tiktok_preserve_facebook(self):
        # Base : Facebook déjà connecté
        base = cr._vide()
        base["par_reseau"]["facebook"].update({"abonnes": 100, "posts": 10})
        base["connecte"] = True
        d = self._client(base)

        # Nouveau sync : TikTok uniquement
        data = cr._vide()
        data["source"] = "tiktok-display-api"
        data["par_reseau"]["tiktok"].update({"abonnes": 500, "posts": 20})

        cr._ecrire(d, data)
        out = self._read(d)

        # Facebook préservé, TikTok ajouté, total consolidé
        self.assertEqual(out["par_reseau"]["facebook"]["abonnes"], 100)
        self.assertEqual(out["par_reseau"]["tiktok"]["abonnes"], 500)
        self.assertEqual(out["global"]["audience"], 600)

    def test_objet_plateforme_preserve(self):
        base = cr._vide()
        base["par_reseau"]["facebook"]["abonnes"] = 50
        base["youtube"] = {"abonnes": 9, "titre": "X"}  # objet d'un sync précédent
        d = self._client(base)

        data = cr._vide()
        data["par_reseau"]["tiktok"]["abonnes"] = 7
        cr._ecrire(d, data)
        out = self._read(d)

        # L'objet youtube d'avant n'est pas effacé par un sync tiktok
        self.assertEqual(out.get("youtube", {}).get("abonnes"), 9)
        self.assertEqual(out["par_reseau"]["facebook"]["abonnes"], 50)


if __name__ == "__main__":
    unittest.main()
