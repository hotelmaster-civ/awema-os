"""Invariant : sélection de fournisseur IA agnostique + résolution du modèle (sans réseau)."""
import io
import os
import sys
import unittest
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import awema_ai  # noqa: E402

AI_VARS = ["AWEMA_AI_PROVIDER", "AWEMA_AI_MODEL", "GROQ_API_KEY", "GEMINI_API_KEY",
           "OPENROUTER_API_KEY", "CEREBRAS_API_KEY", "MISTRAL_API_KEY", "GITHUB_MODELS_TOKEN",
           "TOGETHER_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]


class TestIA(unittest.TestCase):
    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in AI_VARS}
        for k in AI_VARS:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_selection_explicite(self):
        os.environ["AWEMA_AI_PROVIDER"] = "anthropic"
        os.environ["ANTHROPIC_API_KEY"] = "x"
        pid, cfg = awema_ai.actif()
        self.assertEqual(pid, "anthropic")
        self.assertEqual(cfg["type"], "anthropic")

    def test_auto_detection(self):
        os.environ["GROQ_API_KEY"] = "x"     # Groq est en tête du registre → auto-détecté
        self.assertEqual(awema_ai.actif()[0], "groq")
        self.assertTrue(awema_ai.disponible())

    def test_resolution_modele(self):
        # Anthropic : on garde le modèle claude tuné par l'agent
        os.environ["AWEMA_AI_PROVIDER"] = "anthropic"
        os.environ["ANTHROPIC_API_KEY"] = "x"
        self.assertEqual(awema_ai.modele_actif("claude-opus-4-8"), "claude-opus-4-8")
        # Fournisseur non-Claude : le hint claude est ignoré → modèle par défaut du fournisseur
        os.environ["AWEMA_AI_PROVIDER"] = "groq"
        os.environ["GROQ_API_KEY"] = "x"
        self.assertEqual(awema_ai.modele_actif("claude-opus-4-8"), "llama-3.3-70b-versatile")
        # Surcharge globale
        os.environ["AWEMA_AI_MODEL"] = "mon-modele"
        self.assertEqual(awema_ai.modele_actif("claude-opus-4-8"), "mon-modele")

    def test_override_modele_anthropic(self):
        os.environ["AWEMA_AI_PROVIDER"] = "anthropic"
        os.environ["ANTHROPIC_API_KEY"] = "x"
        os.environ["AWEMA_AI_MODEL"] = "claude-sonnet-4-6"
        # hint non-claude (ex. d'un agent mal configuré) → on retombe sur la surcharge globale
        self.assertEqual(awema_ai.modele_actif("gpt-4o"), "claude-sonnet-4-6")

    def test_override_bat_le_modele_epingle(self):
        # Régression (audit) : AWEMA_AI_MODEL doit surcharger MÊME un agent épinglé sur un modèle
        # claude — c'est le levier documenté pour forcer un modèle moins cher (ex. haiku).
        os.environ["AWEMA_AI_PROVIDER"] = "anthropic"
        os.environ["ANTHROPIC_API_KEY"] = "x"
        os.environ["AWEMA_AI_MODEL"] = "claude-haiku-4-5"
        self.assertEqual(awema_ai.modele_actif("claude-opus-4-8"), "claude-haiku-4-5")


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestPostRetry(unittest.TestCase):
    def setUp(self):
        self._pause = awema_ai._pause
        self._urlopen = awema_ai.urllib.request.urlopen
        awema_ai._pause = lambda s: None  # neutralise l'attente en test

    def tearDown(self):
        awema_ai._pause = self._pause
        awema_ai.urllib.request.urlopen = self._urlopen

    def test_retente_sur_429_puis_reussit(self):
        appels = {"n": 0}

        def faux(req, timeout=90):
            appels["n"] += 1
            if appels["n"] == 1:
                raise urllib.error.HTTPError(req.full_url, 429, "rate", {"Retry-After": "0"},
                                             io.BytesIO(b'{"error":"slow down"}'))
            return _Resp(b'{"ok": true}')
        awema_ai.urllib.request.urlopen = faux
        out = awema_ai._post("http://x", {}, {"a": 1})
        self.assertEqual(out, {"ok": True})
        self.assertEqual(appels["n"], 2)  # 1 échec 429 + 1 succès

    def test_400_ne_retente_pas(self):
        appels = {"n": 0}

        def faux(req, timeout=90):
            appels["n"] += 1
            raise urllib.error.HTTPError(req.full_url, 400, "bad", {}, io.BytesIO(b'{"error":"nope"}'))
        awema_ai.urllib.request.urlopen = faux
        with self.assertRaises(RuntimeError):
            awema_ai._post("http://x", {}, {"a": 1})
        self.assertEqual(appels["n"], 1)  # aucun retry sur une erreur cliente


class TestModeJson(unittest.TestCase):
    """Mode JSON natif (response_format) chez les fournisseurs OpenAI-compatibles + repli."""

    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in AI_VARS}
        for k in AI_VARS:
            os.environ.pop(k, None)
        os.environ["AWEMA_AI_PROVIDER"] = "groq"
        os.environ["GROQ_API_KEY"] = "x"
        self._post = awema_ai._post

    def tearDown(self):
        awema_ai._post = self._post
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_schema_demande_le_mode_json(self):
        vus = []

        def faux_post(url, headers, payload, **kw):
            vus.append(payload)
            return {"choices": [{"message": {"content": '{"items": []}'}}]}
        awema_ai._post = faux_post
        out = awema_ai.chat("liste", schema_hint='{"items":[]}')
        self.assertEqual(out, {"items": []})
        self.assertEqual(vus[0].get("response_format"), {"type": "json_object"})

    def test_sans_schema_pas_de_mode_json(self):
        vus = []

        def faux_post(url, headers, payload, **kw):
            vus.append(payload)
            return {"choices": [{"message": {"content": "bonjour"}}]}
        awema_ai._post = faux_post
        self.assertEqual(awema_ai.chat("salut"), "bonjour")
        self.assertNotIn("response_format", vus[0])

    def test_repli_si_fournisseur_refuse_le_mode_json(self):
        vus = []

        def faux_post(url, headers, payload, **kw):
            vus.append(dict(payload))
            if "response_format" in payload:
                raise RuntimeError("HTTP 400 — response_format is not supported")
            return {"choices": [{"message": {"content": '{"items": [1]}'}}]}
        awema_ai._post = faux_post
        out = awema_ai.chat("liste", schema_hint='{"items":[]}')
        self.assertEqual(out, {"items": [1]})
        self.assertEqual(len(vus), 2)                       # 1 essai + 1 repli
        self.assertNotIn("response_format", vus[1])          # repli sans le paramètre

    def test_parsing_rate_leve_une_erreur_explicite(self):
        awema_ai._post = lambda url, headers, payload, **kw: {
            "choices": [{"message": {"content": "désolé, pas de JSON ici"}}]}
        with self.assertRaises(RuntimeError) as cm:
            awema_ai.chat("liste", schema_hint='{"items":[]}')
        self.assertIn("non conforme", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
