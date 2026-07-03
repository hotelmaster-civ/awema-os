"""Invariant : build.py n'embarque les contenus d'une campagne dans le registre que si son
campagne.json reste sous SEUIL_CAMPAGNE ; au-delà → {"total", "differe": true} (chargé à la
demande par les pages). Sans réseau, sur une arborescence temporaire."""
import json
import os
import tempfile
import unittest

from tests.util import charger


def _client(base, slug, campagne=None):
    d = os.path.join(base, "modules", "marketing", "clients", slug, "_donnees")
    os.makedirs(d)
    with open(os.path.join(d, "client.json"), "w", encoding="utf-8") as f:
        json.dump({"id": slug, "nom": slug.title()}, f)
    if campagne is not None:
        with open(os.path.join(d, "campagne.json"), "w", encoding="utf-8") as f:
            json.dump(campagne, f, ensure_ascii=False)


class TestSeuilCampagne(unittest.TestCase):
    def _registre(self, tmp):
        b = charger("outils/_data/build.py", "build_test")
        b.RACINE = tmp
        b.ICI = os.path.join(tmp, "out")
        os.makedirs(b.ICI, exist_ok=True)
        b.main()
        t = open(os.path.join(b.ICI, "agence.js"), encoding="utf-8").read()
        return {c["id"]: c for c in json.loads(t.split("=", 1)[1].rstrip().rstrip(";"))["clients"]}

    def test_petite_campagne_embarquee_grosse_differee(self):
        with tempfile.TemporaryDirectory() as tmp:
            _client(tmp, "petit", {"total": 2, "contenus": [{"titre": "a"}, {"titre": "b"}]})
            _client(tmp, "gros", {"total": 3, "contenus": [{"titre": "x" * 30000}] * 3})  # > 64 Ko
            _client(tmp, "sans", None)
            reg = self._registre(tmp)
            # petite : contenus embarqués tels quels
            self.assertEqual(len(reg["petit"]["campagne"]["contenus"]), 2)
            self.assertNotIn("differe", reg["petit"]["campagne"])
            # grosse : résumé seulement (total conservé, pas de contenus, marqueur differe)
            self.assertTrue(reg["gros"]["campagne"]["differe"])
            self.assertEqual(reg["gros"]["campagne"]["total"], 3)
            self.assertNotIn("contenus", reg["gros"]["campagne"])
            # sans campagne : null, comme avant
            self.assertIsNone(reg["sans"]["campagne"])



class TestRevueDansRegistre(unittest.TestCase):
    """L'axe PRODUCTION unifié : les statuts de la revue des visuels (retours-visuels.json,
    écrits par le visualiseur) remontent dans le registre en map compacte {id: statut} —
    les « À produire » (défaut) n'encombrent pas le registre."""

    def test_revue_exposee_et_compacte(self):
        with tempfile.TemporaryDirectory() as tmp:
            _client(tmp, "avec-revue", {"total": 1, "contenus": [{"titre": "a"}]})
            d = os.path.join(tmp, "modules", "marketing", "clients", "avec-revue", "_donnees")
            with open(os.path.join(d, "retours-visuels.json"), "w", encoding="utf-8") as f:
                json.dump({"client": "Avec-Revue", "retours": [
                    {"id": 1, "statut": "Validé"},
                    {"id": 2, "statut": "À retoucher"},
                    {"id": 3, "statut": "À produire"},     # défaut → absent de la map
                    {"id": 4},                              # sans statut → ignoré
                ]}, f, ensure_ascii=False)
            _client(tmp, "sans-revue", {"total": 1, "contenus": [{"titre": "b"}]})
            b = charger("outils/_data/build.py", "build_test_revue")
            b.RACINE = tmp
            b.ICI = os.path.join(tmp, "out")
            os.makedirs(b.ICI, exist_ok=True)
            b.main()
            t = open(os.path.join(b.ICI, "agence.js"), encoding="utf-8").read()
            reg = {c["id"]: c for c in json.loads(t.split("=", 1)[1].rstrip().rstrip(";"))["clients"]}
            self.assertEqual(reg["avec-revue"]["revue"], {"1": "Validé", "2": "À retoucher"})
            self.assertIsNone(reg["sans-revue"]["revue"])


if __name__ == "__main__":
    unittest.main()
