"""Invariant : la consolidation somme correctement les réseaux et calcule l'engagement."""
import json
import os
import tempfile
import unittest

from tests.util import charger

cr = charger("scripts/connect-reseaux.py", "cr")


class TestConsolidation(unittest.TestCase):
    def test_sommes_multi_reseaux(self):
        data = cr._vide()
        data["par_reseau"]["facebook"].update({"abonnes": 100, "posts": 10, "likes": 30, "commentaires": 5})
        data["par_reseau"]["tiktok"].update({"abonnes": 400, "posts": 20, "likes": 200})
        cr._consolider(data)
        g = data["global"]
        self.assertEqual(g["audience"], 500)
        self.assertEqual(g["posts"], 30)
        self.assertEqual(g["likes"], 230)
        self.assertEqual(g["commentaires"], 5)

    def test_engagement_par_abonne(self):
        data = cr._vide()
        # 10 posts, 100 abonnés, (likes+comm+partages) = 50 → (50/10)/100*100 = 5.0 %
        data["par_reseau"]["facebook"].update(
            {"abonnes": 100, "posts": 10, "likes": 40, "commentaires": 8, "partages": 2})
        cr._consolider(data)
        self.assertEqual(data["global"]["engagement_taux"], 5.0)

    def test_cadence_multi_prend_le_plus_recent(self):
        # FB ancien, TikTok récent → le « dernier post » doit refléter TikTok
        base = {"cadence": {"dernier_post": "2020-01-01T00:00:00+00:00", "jours_depuis": 2000},
                "tiktok": {"dernier_post": "2026-06-20T00:00:00+00:00"}, "top_posts": []}
        cr._cadence_multi(base)
        self.assertEqual(base["cadence"]["dernier_reseau"], "TikTok")
        self.assertTrue(base["cadence"]["dernier_post"].startswith("2026-06-20"))
        self.assertTrue(base["cadence"]["multi_reseaux"])
        self.assertLess(base["cadence"]["jours_depuis"], 2000)

    def test_connecte_si_un_reseau_a_des_abonnes(self):
        data = cr._vide()
        self.assertFalse(data.get("connecte") or False)
        data["par_reseau"]["youtube"]["abonnes"] = 12
        cr._consolider(data)
        self.assertTrue(data["connecte"])



class TestCadenceMultiReseaux(unittest.TestCase):
    def test_posts_30j_compte_tous_les_reseaux(self):
        # Régression (audit) : un client actif sur TikTok affichait posts_30j=0 (Facebook seul).
        from datetime import datetime, timedelta, timezone
        recent = lambda j: (datetime.now(timezone.utc) - timedelta(days=j)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        base = {"cadence": {"posts_30j": 0, "posts_par_semaine": 0.0},
                "top_posts": [{"date": recent(2), "plateforme": "TikTok"},
                               {"date": recent(5), "plateforme": "TikTok"},
                               {"date": recent(9), "plateforme": "YouTube"},
                               {"date": recent(45), "plateforme": "TikTok"}]}  # hors fenêtre
        cr._cadence_multi(base)
        self.assertEqual(base["cadence"]["posts_30j"], 3)
        self.assertGreater(base["cadence"]["posts_par_semaine"], 0)
        self.assertEqual(base["cadence"]["dernier_reseau"], "TikTok")

    def test_ne_degrade_jamais_une_cadence_facebook_superieure(self):
        # Une cadence PURE Facebook (25 posts complets) est amorcée dans le détail par réseau ;
        # le global = somme des réseaux (12 FB + 1 TikTok) — jamais moins que la valeur Facebook.
        from datetime import datetime, timedelta, timezone
        recent = lambda j: (datetime.now(timezone.utc) - timedelta(days=j)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        base = {"cadence": {"posts_30j": 12, "posts_par_semaine": 2.8, "dernier_post": recent(1)},
                "top_posts": [{"date": recent(3), "plateforme": "TikTok"}]}
        cr._cadence_multi(base)
        self.assertEqual(base["cadence_reseaux"]["facebook"]["posts_30j"], 12)
        self.assertEqual(base["cadence"]["posts_30j"], 13)
        self.assertEqual(base["cadence"]["dernier_reseau"], "Facebook")

    def test_pas_de_double_comptage_ni_etiquette_facebook_fantome(self):
        # Régression (revue) : un client 100 % TikTok avec UNE cadence globale héritée (multi)
        # voyait son unique post compté DEUX fois (étiquettes « Facebook » + « TikTok ») et
        # son dernier_reseau falsifié en « Facebook ».
        from datetime import datetime, timedelta, timezone
        recent = lambda j: (datetime.now(timezone.utc) - timedelta(days=j)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        d = recent(3)
        base = {"cadence": {"dernier_post": d, "dernier_reseau": "Facebook",  # étiquette empoisonnée
                            "posts_30j": 2, "posts_par_semaine": 0.5, "multi_reseaux": True},
                "cadence_reseaux": {"tiktok": {"dernier_post": d, "jours_depuis": 3,
                                               "posts_30j": 1, "posts_par_semaine": 0.2}},
                "top_posts": [{"date": d, "plateforme": "TikTok"}]}
        cr._cadence_multi(base)
        self.assertEqual(base["cadence"]["posts_30j"], 1)          # 1 post réel = 1
        self.assertEqual(base["cadence"]["dernier_reseau"], "TikTok")

    def test_fenetre_glissante_pas_de_compteur_fige(self):
        # Régression (revue) : le cliquet figeait posts_30j pour toujours. Quand le dernier
        # post connu sort des 30 j, le réseau ET le global doivent retomber à zéro.
        from datetime import datetime, timedelta, timezone
        vieux = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        base = {"cadence": {"dernier_post": vieux, "posts_30j": 4, "posts_par_semaine": 0.9,
                            "dernier_reseau": "TikTok", "multi_reseaux": True},
                "cadence_reseaux": {"tiktok": {"dernier_post": vieux, "jours_depuis": 10,
                                               "posts_30j": 4, "posts_par_semaine": 0.9}}}
        cr._cadence_multi(base)
        self.assertEqual(base["cadence_reseaux"]["tiktok"]["posts_30j"], 0)
        self.assertEqual(base["cadence_reseaux"]["tiktok"]["jours_depuis"], 45)
        self.assertEqual(base["cadence"]["posts_30j"], 0)
        self.assertEqual(base["cadence"]["posts_par_semaine"], 0.0)  # jamais « undefined »

    def test_bloc_reseau_corrige_le_dernier_post_approx(self):
        # Régression (revue) : l'approx top_posts (8 plus ENGAGEANTS) peut rater le post le
        # plus RÉCENT — la vraie date du bloc réseau doit corriger l'entrée approx.
        from datetime import datetime, timedelta, timezone
        recent = lambda j: (datetime.now(timezone.utc) - timedelta(days=j)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        base = {"tiktok": {"dernier_post": recent(1)},
                "top_posts": [{"date": recent(10), "plateforme": "TikTok"}]}
        cr._cadence_multi(base)
        tk = base["cadence_reseaux"]["tiktok"]
        self.assertEqual(tk["jours_depuis"], 1)                     # la vraie date prime
        self.assertTrue(tk["approx"])




class TestVisuelsFusion(unittest.TestCase):
    """La fusion des visuels (avatar/couverture) est clé par clé : l'avatar TikTok
    ne doit jamais effacer la couverture Facebook du même client, et inversement."""

    def test_avatar_tiktok_preserve_couverture_facebook(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = os.path.join(tmp, "_donnees")
            os.makedirs(dossier)
            base = cr._vide()
            base["visuels"] = {"photo": "https://fb/photo.jpg", "couverture": "https://fb/cover.jpg"}
            with open(os.path.join(dossier, "reseaux.json"), "w", encoding="utf-8") as f:
                json.dump(base, f)
            sync_tiktok = cr._vide()
            sync_tiktok["par_reseau"]["tiktok"]["abonnes"] = 10
            sync_tiktok["visuels"] = {"photo": "https://tt/avatar.jpg"}
            cr._ecrire(tmp, sync_tiktok)
            with open(os.path.join(dossier, "reseaux.json"), encoding="utf-8") as f:
                out = json.load(f)
            self.assertEqual(out["visuels"]["photo"], "https://tt/avatar.jpg")
            self.assertEqual(out["visuels"]["couverture"], "https://fb/cover.jpg")

    def test_page_info_expose_photo_et_couverture(self):
        # _tiktok_data expose l'avatar quand l'API le fournit — et rien sinon (zéro fiction).
        d = cr._tiktok_data({"follower_count": 5, "avatar_url": "https://tt/a.jpg"}, [])
        self.assertEqual(d["visuels"], {"photo": "https://tt/a.jpg"})
        d2 = cr._tiktok_data({"follower_count": 5}, [])
        self.assertNotIn("visuels", d2)


class TestCadenceParReseau(unittest.TestCase):
    """Le détail cadence_reseaux : une entrée par réseau, fournie par le connecteur
    (liste complète) ou approximée depuis top_posts (marquée approx=True)."""

    def test_calc_cadence_depuis_dates(self):
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        dates = [(now - timedelta(days=d)).isoformat(timespec="seconds") for d in (1, 5, 40)]
        c = cr._calc_cadence(dates)
        self.assertEqual(c["posts_30j"], 2)          # le post à J-40 est hors fenêtre
        self.assertEqual(c["jours_depuis"], 1)
        self.assertIsNone(cr._calc_cadence([]))
        self.assertIsNone(cr._calc_cadence([None, "pas-une-date"]))

    def test_tiktok_remplit_son_detail(self):
        import time
        v = {"create_time": int(time.time()) - 3600, "like_count": 3,
             "comment_count": 1, "share_count": 0, "view_count": 9}
        d = cr._tiktok_data({"follower_count": 5}, [v])
        self.assertIn("tiktok", d["cadence_reseaux"])
        self.assertEqual(d["cadence_reseaux"]["tiktok"]["posts_30j"], 1)
        self.assertIn("tiktok", d["creneau_reseaux"])
        self.assertIn("recommandation", d["creneau_reseaux"]["tiktok"])

    def test_sync_tiktok_preserve_cadence_facebook(self):
        import json as _json
        import os as _os
        import tempfile as _tmp
        with _tmp.TemporaryDirectory() as tmp:
            dossier = _os.path.join(tmp, "_donnees")
            _os.makedirs(dossier)
            base = cr._vide()
            base["cadence_reseaux"] = {"facebook": {"dernier_post": "2026-07-01T10:00:00+0000",
                                                    "jours_depuis": 1, "posts_30j": 13,
                                                    "posts_par_semaine": 3.0}}
            with open(_os.path.join(dossier, "reseaux.json"), "w", encoding="utf-8") as f:
                _json.dump(base, f)
            sync = cr._vide()
            sync["par_reseau"]["tiktok"]["abonnes"] = 10
            sync["cadence_reseaux"] = {"tiktok": {"dernier_post": "2026-07-02T09:00:00+00:00",
                                                  "jours_depuis": 0, "posts_30j": 4,
                                                  "posts_par_semaine": 0.9}}
            cr._ecrire(tmp, sync)
            with open(_os.path.join(dossier, "reseaux.json"), encoding="utf-8") as f:
                out = _json.load(f)
            self.assertEqual(out["cadence_reseaux"]["facebook"]["posts_30j"], 13)
            self.assertEqual(out["cadence_reseaux"]["tiktok"]["posts_30j"], 4)
            # global : somme des réseaux (13 + 4), jamais moins que le meilleur estimateur
            self.assertGreaterEqual(out["cadence"]["posts_30j"], 17)

    def test_sync_facebook_sans_posts_retire_sa_cadence_perimee(self):
        # Régression (revue) : un sync Meta qui ne remonte plus aucun post doit retirer
        # l'entrée facebook de cadence_reseaux (sinon elle ressuscite le global périmé).
        import json as _json
        import os as _os
        import tempfile as _tmp
        with _tmp.TemporaryDirectory() as tmp:
            dossier = _os.path.join(tmp, "_donnees")
            _os.makedirs(dossier)
            base = cr._vide()
            base["cadence_reseaux"] = {"facebook": {"dernier_post": "2026-05-01T10:00:00+0000",
                                                    "jours_depuis": 60, "posts_30j": 13,
                                                    "posts_par_semaine": 3.0}}
            with open(_os.path.join(dossier, "reseaux.json"), "w", encoding="utf-8") as f:
                _json.dump(base, f)
            sync = cr._vide()                       # sync Meta : page vivante mais 0 post
            sync["par_reseau"]["facebook"]["abonnes"] = 50
            cr._ecrire(tmp, sync)
            with open(_os.path.join(dossier, "reseaux.json"), encoding="utf-8") as f:
                out = _json.load(f)
            self.assertNotIn("facebook", out.get("cadence_reseaux") or {})

    def test_approx_depuis_top_posts_sans_ecraser_le_connecteur(self):
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        base = cr._vide()
        base["cadence_reseaux"] = {"facebook": {"dernier_post": now.isoformat(),
                                                "jours_depuis": 0, "posts_30j": 13,
                                                "posts_par_semaine": 3.0}}
        base["top_posts"] = [
            {"plateforme": "Facebook", "date": now.isoformat()},
            {"plateforme": "TikTok", "date": (now - timedelta(days=2)).isoformat()},
            {"plateforme": "TikTok", "date": (now - timedelta(days=9)).isoformat()},
        ]
        cr._cadence_multi(base)
        fb = base["cadence_reseaux"]["facebook"]
        self.assertEqual(fb["posts_30j"], 13)            # le connecteur fait foi
        self.assertNotIn("approx", fb)
        tk = base["cadence_reseaux"]["tiktok"]
        self.assertTrue(tk["approx"])                    # approximé (borne basse)
        self.assertEqual(tk["posts_30j"], 2)

if __name__ == "__main__":
    unittest.main()
