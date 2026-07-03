"""Invariants de parsing/classification de connect-reseaux.py (sans réseau)."""
import unittest

from tests.util import charger

cr = charger("scripts/connect-reseaux.py", "cr_parse")


class TestTypePost(unittest.TestCase):
    def _p(self, mt):
        return {"attachments": {"data": [{"media_type": mt}]}}

    def test_photo(self):
        self.assertEqual(cr._type_post(self._p("photo")), "photo")

    def test_video(self):
        self.assertEqual(cr._type_post(self._p("video")), "vidéo")

    def test_share_est_lien(self):
        self.assertEqual(cr._type_post(self._p("share")), "lien")

    def test_sans_attachement_est_statut(self):
        self.assertEqual(cr._type_post({}), "statut")


class TestParseDt(unittest.TestCase):
    def test_iso_valide(self):
        d = cr._parse_dt("2026-07-02T18:30:00+0000")
        self.assertIsNotNone(d)
        self.assertEqual((d.year, d.month, d.hour), (2026, 7, 18))

    def test_vide_est_none(self):
        self.assertIsNone(cr._parse_dt(""))

    def test_invalide_est_none(self):
        self.assertIsNone(cr._parse_dt("pas-une-date"))


class TestTs(unittest.TestCase):
    def test_epoch_vers_iso_utc(self):
        self.assertTrue(cr._ts(0).startswith("1970-01-01"))

    def test_invalide_est_none(self):
        self.assertIsNone(cr._ts("xyz"))


if __name__ == "__main__":
    unittest.main()
