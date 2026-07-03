"""Invariant : la réinitialisation vide le dépôt de toute donnée client, ré-installe la démo,
et REFUSE de s'exécuter sans la confirmation exacte. Testée sur une COPIE temporaire — jamais
sur le dépôt courant."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)


def _mini_repo(base):
    """Arborescence minimale : 2 clients réels + scripts nécessaires (reinitialiser, build,
    preparer-copie-beta, _demo, contrats _data)."""
    for slug in ("client-reel-a", "client-reel-b"):
        d = os.path.join(base, "modules", "marketing", "clients", slug, "_donnees")
        os.makedirs(d)
        json.dump({"id": slug, "nom": slug, "module": "marketing"},
                  open(os.path.join(d, "client.json"), "w", encoding="utf-8"))
        json.dump({"total": 1, "contenus": [{"titre": "secret réel"}]},
                  open(os.path.join(d, "campagne.json"), "w", encoding="utf-8"))
    # data.js mono-client (doit disparaître)
    for f in ("outils/dashboard/data.js", "outils/revue-visuels/data.js"):
        os.makedirs(os.path.join(base, os.path.dirname(f)), exist_ok=True)
        open(os.path.join(base, f), "w").write("window.CAMPAGNE={client:'réel'};")
    os.makedirs(os.path.join(base, "config"), exist_ok=True)
    json.dump({"_doc": "x", "tiktok": {"code": "reel"}},
              open(os.path.join(base, "config", "aliases.json"), "w", encoding="utf-8"))
    json.dump({"nom": "Vraie Agence"}, open(os.path.join(base, "config", "agence.json"), "w", encoding="utf-8"))
    # scripts requis
    os.makedirs(os.path.join(base, "scripts"), exist_ok=True)
    for s in ("reinitialiser.py", "preparer-copie-beta.py"):
        shutil.copy(os.path.join(RACINE, "scripts", s), os.path.join(base, "scripts", s))
    shutil.copytree(os.path.join(RACINE, "scripts", "_demo"), os.path.join(base, "scripts", "_demo"),
                    dirs_exist_ok=True)
    # build.py + contrats _data
    shutil.copytree(os.path.join(RACINE, "outils", "_data"), os.path.join(base, "outils", "_data"),
                    dirs_exist_ok=True)


def _run(base, confirm, portee):
    env = dict(os.environ, AWEMA_RESET_CONFIRM=confirm, AWEMA_RESET_PORTEE=portee)
    return subprocess.run([sys.executable, os.path.join(base, "scripts", "reinitialiser.py")],
                          cwd=base, env=env, capture_output=True, text=True)


class TestReinitialiser(unittest.TestCase):
    def test_refuse_sans_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            _mini_repo(tmp)
            r = _run(tmp, "oui", "client")
            self.assertNotEqual(r.returncode, 0)               # sortie en erreur
            self.assertTrue(os.path.isdir(os.path.join(tmp, "modules", "marketing", "clients", "client-reel-a")))

    def test_portee_client_vide_les_clients_reels(self):
        with tempfile.TemporaryDirectory() as tmp:
            _mini_repo(tmp)
            r = _run(tmp, "REINITIALISER", "client")
            self.assertEqual(r.returncode, 0, r.stderr)
            clients = os.path.join(tmp, "modules", "marketing", "clients")
            restants = sorted(os.listdir(clients))
            self.assertEqual(restants, ["demo-client"])         # démo seule
            self.assertFalse(os.path.exists(os.path.join(tmp, "outils", "dashboard", "data.js")))
            # alias vidés
            al = json.load(open(os.path.join(tmp, "config", "aliases.json"), encoding="utf-8"))
            self.assertEqual(al["tiktok"], {})
            # identité de l'agence CONSERVÉE en portée client
            ag = json.load(open(os.path.join(tmp, "config", "agence.json"), encoding="utf-8"))
            self.assertEqual(ag["nom"], "Vraie Agence")
            # registre régénéré sans les clients réels
            reg = open(os.path.join(tmp, "outils", "_data", "agence.js"), encoding="utf-8").read()
            self.assertNotIn("client-reel-a", reg)
            self.assertNotIn("secret réel", reg)

    def test_portee_complet_neutralise_l_agence(self):
        with tempfile.TemporaryDirectory() as tmp:
            _mini_repo(tmp)
            r = _run(tmp, "REINITIALISER", "complet")
            self.assertEqual(r.returncode, 0, r.stderr)
            ag = json.load(open(os.path.join(tmp, "config", "agence.json"), encoding="utf-8"))
            self.assertNotEqual(ag.get("nom"), "Vraie Agence")  # identité remise à neutre
            self.assertEqual(sorted(os.listdir(os.path.join(tmp, "modules", "marketing", "clients"))),
                             ["demo-client"])

    def test_portee_inconnue_refusee(self):
        with tempfile.TemporaryDirectory() as tmp:
            _mini_repo(tmp)
            r = _run(tmp, "REINITIALISER", "supprime-tout-mdr")
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
