"""Invariant : l'enveloppe commune des sorties d'agents est correctement validée."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import awema_ai  # noqa: E402


class TestEnveloppeAgent(unittest.TestCase):
    def test_enveloppe_valide(self):
        env = awema_ai.enveloppe(
            "analyste",
            [{"type": "insight", "titre": "T", "explication": "E"}],
            "claude-sonnet-4-6", {"client": "demo"})
        ok, err = awema_ai.valider_enveloppe(env, ["type", "titre", "explication"])
        self.assertTrue(ok, err)

    def test_cle_manquante_detectee(self):
        ok, err = awema_ai.valider_enveloppe({"agent": "x"}, None)
        self.assertFalse(ok)
        self.assertTrue(any("items" in e for e in err))

    def test_item_requis_manquant(self):
        env = awema_ai.enveloppe("analyste", [{"titre": "sans type"}], "m", {})
        ok, err = awema_ai.valider_enveloppe(env, ["type", "titre"])
        self.assertFalse(ok)
        self.assertTrue(any("type" in e for e in err))

    def test_skip_gracieux_sans_cle(self):
        # Sans clé, chat() renvoie None (pas d'exception) → CI/offline restent verts.
        if not awema_ai.disponible():
            self.assertIsNone(awema_ai.chat("ping", schema_hint='{"items":[]}'))
        else:
            self.skipTest("clé IA présente dans cet environnement")

    def test_enveloppe_champs_extra_struct(self):
        # Stratège : items (plan) + champs structurés en plus (cadence, heures, objectifs)
        env = awema_ai.enveloppe(
            "stratege",
            [{"jour": "Lundi", "format": "Short", "angle": "x", "reseau": "TikTok"}],
            "claude-opus-4-8", {"client": "demo"})
        env["cadence_recommandee"] = "4/sem"
        env["meilleures_heures"] = ["Mardi 19h"]
        ok, err = awema_ai.valider_enveloppe(env, ["jour", "format", "angle", "reseau"])
        self.assertTrue(ok, err)
        self.assertEqual(env["cadence_recommandee"], "4/sem")

    def test_creatif_item_requis(self):
        env = awema_ai.enveloppe(
            "creatif",
            [{"hook": "Arrête de scroller", "format": "Short", "reseau": "TikTok",
              "script": "...", "prompt_image": "..."}],
            "claude-sonnet-4-6", {"client": "demo"})
        ok, err = awema_ai.valider_enveloppe(env, ["hook", "format", "reseau"])
        self.assertTrue(ok, err)
        # hook manquant → invalide
        env2 = awema_ai.enveloppe("creatif", [{"format": "Post", "reseau": "Facebook"}], "m", {})
        ok2, _ = awema_ai.valider_enveloppe(env2, ["hook", "format", "reseau"])
        self.assertFalse(ok2)

    def test_extraction_json_robuste(self):
        self.assertEqual(awema_ai._extraire_json('Voici: {"a":1} merci'), {"a": 1})
        self.assertEqual(awema_ai._extraire_json('```json\n{"b":2}\n```'), {"b": 2})


if __name__ == "__main__":
    unittest.main()
