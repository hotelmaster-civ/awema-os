"""Invariant : l'agrégateur « actions du jour » dérive des alertes réelles (sans IA)."""
import unittest

from tests.util import charger

ra = charger("scripts/run-agent.py", "ra")


class TestActionsDuJour(unittest.TestCase):
    def test_alertes_deterministes(self):
        reseaux = {
            "cadence": {"jours_depuis": 12},
            "a_repondre": {"total": 3},
            "types_contenu": {"video": {"engagement_moyen": 40}, "photo": {"engagement_moyen": 10}},
        }
        items = ra.aggreger_actions(reseaux, {})
        titres = " | ".join(i["titre"] for i in items)
        self.assertIn("Cadence en retard", titres)
        self.assertIn("à répondre", titres)
        self.assertIn("video", titres)            # format gagnant = celui au plus fort engagement
        # priorités triées (1 d'abord)
        self.assertLessEqual(items[0]["priorite"], items[-1]["priorite"])

    def test_enrichi_par_agents(self):
        agents = {
            "analyste": {"items": [{"type": "reco", "titre": "Republie tes shorts", "action": "Programme 3 shorts"}]},
            "creatif": {"items": [{"hook": "Arrête de scroller", "reseau": "TikTok", "format": "Short"}]},
        }
        items = ra.aggreger_actions({}, agents)
        srcs = {i["source"] for i in items}
        self.assertIn("analyste", srcs)
        self.assertIn("creatif", srcs)

    def test_vide_si_rien(self):
        self.assertEqual(ra.aggreger_actions({}, {}), [])

    def test_cap_a_6(self):
        reseaux = {"cadence": {"jours_depuis": 30}, "a_repondre": {"total": 9},
                   "types_contenu": {"v": {"engagement_moyen": 5}},
                   "evolution_audience": [{"valeur": 100}, {"valeur": 90}]}
        agents = {"analyste": {"items": [{"type": "reco", "titre": "x"}]},
                  "stratege": {"items": [{"angle": "a", "reseau": "TikTok", "format": "Short"}]},
                  "creatif": {"items": [{"hook": "h", "reseau": "TikTok", "format": "Short"}]}}
        self.assertLessEqual(len(ra.aggreger_actions(reseaux, agents)), 6)


if __name__ == "__main__":
    unittest.main()
