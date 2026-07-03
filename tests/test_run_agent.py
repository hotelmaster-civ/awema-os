"""Invariant : _entrees() ne rassemble QUE les fichiers présents (skip gracieux des manquants)."""
import json
import os
import tempfile
import unittest

from tests.util import charger

ra = charger("scripts/run-agent.py", "ra_test")


class TestEntrees(unittest.TestCase):
    def test_ne_prend_que_les_fichiers_presents(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "reseaux.json"), "w", encoding="utf-8") as f:
                json.dump({"global": {"abonnes": 10}}, f)
            ctx, dispo = ra._entrees({"entrees": ["reseaux", "memoire", "campagne"]}, d)
            self.assertIn("reseaux", ctx)
            self.assertNotIn("memoire", ctx)
            self.assertEqual(dispo, ["reseaux.json"])

    def test_rien_disponible(self):
        with tempfile.TemporaryDirectory() as d:
            ctx, dispo = ra._entrees({"entrees": ["reseaux"]}, d)
            self.assertEqual(ctx, {})
            self.assertEqual(dispo, [])

    def test_entrees_vides(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ra._entrees({"entrees": []}, d), ({}, []))


class TestEntreesComposites(unittest.TestCase):
    """La Rétrospective lit l'historique des agents et la file de publication (statuts réels)."""

    def test_agents_et_planning_rassembles(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "_agents"))
            os.makedirs(os.path.join(d, "_planning"))
            with open(os.path.join(d, "_agents", "creatif.json"), "w", encoding="utf-8") as f:
                json.dump({"agent": "creatif", "items": [{"hook": "h"}]}, f)
            with open(os.path.join(d, "_agents", "retrospective.json"), "w", encoding="utf-8") as f:
                json.dump({"agent": "retrospective", "items": []}, f)  # ne doit PAS se relire
            with open(os.path.join(d, "_planning", "p1.json"), "w", encoding="utf-8") as f:
                json.dump({"id": "p1", "statut": "publie"}, f)
            with open(os.path.join(d, "_planning", "index.json"), "w", encoding="utf-8") as f:
                json.dump({}, f)  # index ignoré
            ctx, dispo = ra._entrees({"entrees": ["agents", "planning"]}, d)
            self.assertIn("creatif", ctx["agents"])
            self.assertNotIn("retrospective", ctx["agents"])   # pas d'auto-lecture
            self.assertEqual([p["id"] for p in ctx["planning"]], ["p1"])
            self.assertEqual(sorted(dispo), ["_agents/*", "_planning/*"])

    def test_composites_absents_skippes(self):
        with tempfile.TemporaryDirectory() as d:
            ctx, dispo = ra._entrees({"entrees": ["agents", "planning"]}, d)
            self.assertEqual((ctx, dispo), ({}, []))


class TestContexteJson(unittest.TestCase):
    def test_toujours_json_valide_et_petites_entrees_entieres(self):
        ctx = {"memoire": {"ton": "chaleureux"}, "reseaux": {"abonnes": 100}}
        out = json.loads(ra._contexte_json(ctx, budget=24000))  # ne doit jamais lever
        self.assertEqual(out["memoire"]["ton"], "chaleureux")
        self.assertEqual(out["reseaux"]["abonnes"], 100)

    def test_entree_trop_grosse_est_bornee_sans_casser_le_json(self):
        # Régression (audit) : l'ancien [:12000] coupait en plein JSON → mémoire/campagne éjectées.
        ctx = {"memoire": {"ton": "chaleureux"}, "campagne": {"gros": "x" * 50000}}
        out = json.loads(ra._contexte_json(ctx, budget=2000))  # JSON toujours valide malgré l'énorme entrée
        self.assertEqual(out["memoire"]["ton"], "chaleureux")   # la petite entrée prioritaire est préservée
        self.assertTrue(out["campagne"].get("_tronque"))        # la grosse est bornée, pas coupée


if __name__ == "__main__":
    unittest.main()
