"""Invariant : la file de réponses aux commentaires est idempotente (jamais de double
envoi), suit la Graph API (token de Page → POST /<commentaire>/comments) et passe en
« echec » après MAX_TENTATIVES. Aucun appel réseau."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import repondre  # noqa: E402


def demande(**kw):
    base = {"id": "r-1", "client": "mon-client", "reseau": "facebook",
            "commentaire_id": "123_456", "message": "Merci pour votre retour !",
            "comptes": {"facebook": "9001"}, "statut": "a_envoyer", "tentatives": 0}
    base.update(kw)
    return base


class TestEnvoyerFacebook(unittest.TestCase):
    def setUp(self):
        self._http = repondre.http
        os.environ["META_TOKEN"] = "tok-test"
        self.appels = []

    def tearDown(self):
        repondre.http = self._http
        os.environ.pop("META_TOKEN", None)

    def faux_http(self, reponses):
        file_att = list(reponses)

        def h(url, data=None, headers=None, method=None):
            self.appels.append({"url": url, "data": data})
            return file_att.pop(0)
        return h

    def test_flux_token_de_page_puis_post_commentaire(self):
        repondre.http = self.faux_http([
            (200, {"data": [{"id": "9001", "access_token": "page-tok"}]}),
            (200, {"id": "123_456_789"}),
        ])
        r = repondre.envoyer_facebook(demande())
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["detail"], "123_456_789")
        self.assertIn("/me/accounts", self.appels[0]["url"])
        self.assertIn("/123_456/comments", self.appels[1]["url"])
        corps = self.appels[1]["data"].decode()
        self.assertIn("access_token=page-tok", corps)   # token de la PAGE, pas de l'utilisateur
        self.assertIn("message=", corps)

    def test_page_introuvable(self):
        repondre.http = self.faux_http([(200, {"data": [{"id": "AUTRE", "access_token": "x"}]})])
        r = repondre.envoyer_facebook(demande())
        self.assertFalse(r["ok"])
        self.assertIn("Page introuvable", r["error"])

    def test_token_absent(self):
        os.environ.pop("META_TOKEN", None)
        r = repondre.envoyer_facebook(demande())
        self.assertFalse(r["ok"])
        self.assertIn("META_TOKEN", r["error"])


class TestTraiter(unittest.TestCase):
    def test_succes_marque_envoye(self):
        it = repondre.traiter(demande(), envoyer=lambda i: {"ok": True, "detail": "rep-9"})
        self.assertEqual(it["statut"], "envoye")
        self.assertEqual(it["reponse_id"], "rep-9")
        self.assertIn("envoye_le", it)

    def test_echec_incremente_puis_echec_final(self):
        it = demande()
        for n in range(1, repondre.MAX_TENTATIVES + 1):
            it = repondre.traiter(it, envoyer=lambda i: {"ok": False, "error": "boom"})
            self.assertEqual(it["tentatives"], n)
        self.assertEqual(it["statut"], "echec")

    def test_idempotent_jamais_de_double_envoi(self):
        compteur = []
        it = repondre.traiter(demande(statut="envoye"),
                              envoyer=lambda i: compteur.append(1) or {"ok": True})
        self.assertEqual(it["statut"], "envoye")
        self.assertEqual(compteur, [])   # l'envoyeur n'a jamais été appelé

    def test_exception_ne_crashe_pas_la_file(self):
        def explose(i):
            raise RuntimeError("réseau KO")
        it = repondre.traiter(demande(), envoyer=explose)
        self.assertEqual(it["statut"], "a_envoyer")   # re-tentera au prochain run
        self.assertEqual(it["tentatives"], 1)
        self.assertIn("réseau KO", it["erreur"])

    def test_reseau_non_supporte(self):
        it = repondre.traiter(demande(reseau="pigeon-voyageur"))
        self.assertEqual(it["statut"], "echec")


if __name__ == "__main__":
    unittest.main()
