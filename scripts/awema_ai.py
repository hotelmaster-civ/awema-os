#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Client IA AWEMA — AGNOSTIQUE : branche N'IMPORTE QUELLE IA pour faire tourner les agents.

Supporte tout fournisseur **compatible OpenAI** (Groq, Gemini, OpenRouter, Cerebras, Mistral,
GitHub Models, Ollama local, OpenAI…) et **Anthropic** (Claude). Le registre des fournisseurs —
avec ceux offrant un **palier gratuit / des crédits d'essai** — est dans `config/ia-providers.json`.

ADN respecté : stdlib uniquement, aucun secret dans le dépôt. La clé vient de l'environnement
(`<CLE>` du fournisseur) ou du store local `.awema/`. Sans clé → tout s'auto-désactive proprement
(`disponible()` → False, `chat()` → None) : la CI et l'usage hors-ligne restent verts.

Sélection du fournisseur : `AWEMA_AI_PROVIDER=<id>` (ex. groq, gemini, anthropic…). Sinon, auto-détection
du premier fournisseur dont la clé est présente. Modèle surchargeable via `AWEMA_AI_MODEL`.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANTHROPIC_VERSION = "2023-06-01"


# --------------------------------------------------------------------------- #
# Registre des fournisseurs & résolution clé / fournisseur actif
# --------------------------------------------------------------------------- #
def _registre():
    try:
        with open(os.path.join(RACINE, "config", "ia-providers.json"), encoding="utf-8") as f:
            d = json.load(f)
        return d.get("defaut", "anthropic"), (d.get("providers") or {})
    except Exception:
        return "anthropic", {}


def _store_keys():
    """Toutes les valeurs présentes dans le store local .awema (toutes plateformes confondues)."""
    out = {}
    try:
        store = json.load(open(os.path.join(RACINE, ".awema", "credentials.json"), encoding="utf-8"))
        for p in (store.get("platforms") or {}).values():
            for k, v in (p.get("current") or {}).items():
                if v:
                    out.setdefault(k, str(v).strip())
    except Exception:
        pass
    return out


def _lookup(name):
    """Valeur d'une clé : environnement d'abord, puis store local .awema."""
    return (os.environ.get(name) or _store_keys().get(name) or "").strip() or None


def actif():
    """(id, config) du fournisseur actif, ou (None, None). Choix : AWEMA_AI_PROVIDER (env/store),
    sinon premier fournisseur dont la clé est disponible."""
    _, providers = _registre()
    if not providers:
        return None, None
    choisi = os.environ.get("AWEMA_AI_PROVIDER") or _store_keys().get("AWEMA_AI_PROVIDER")
    if choisi and choisi in providers:
        cfg = providers[choisi]
        if _lookup(cfg.get("cle", "")) or choisi == "ollama":
            return choisi, cfg
        return None, None
    for pid, cfg in providers.items():
        if _lookup(cfg.get("cle", "")):          # auto-détection (clé présente)
            return pid, cfg
    return None, None


def disponible():
    """Vrai si une IA est configurée (donc si les agents peuvent tourner)."""
    return actif()[0] is not None


def _resolve_model(hint, cfg):
    # Priorité : surcharge explicite AWEMA_AI_MODEL > modèle épinglé par l'agent > défaut du fournisseur.
    # (Avant, la surcharge était ignorée pour les 3 agents Claude, contredisant la doc.)
    override = (os.environ.get("AWEMA_AI_MODEL") or "").strip()
    if override:
        return override
    if cfg.get("type") == "anthropic" and hint and str(hint).startswith("claude"):
        return hint
    return cfg.get("model")


def modele_actif(hint=None):
    """Modèle réellement utilisé pour le fournisseur actif (pour journaliser la provenance)."""
    pid, cfg = actif()
    return _resolve_model(hint, cfg) if cfg else (hint or None)


# --------------------------------------------------------------------------- #
# Extraction JSON robuste
# --------------------------------------------------------------------------- #
def _extraire_json(texte):
    texte = (texte or "").strip()
    m = re.search(r"```(?:json)?\s*(.+?)```", texte, re.S)
    if m:
        texte = m.group(1).strip()
    try:
        return json.loads(texte)
    except Exception:
        pass
    for ouvre, ferme in (("{", "}"), ("[", "]")):
        i, j = texte.find(ouvre), texte.rfind(ferme)
        if i != -1 and j > i:
            try:
                return json.loads(texte[i:j + 1])
            except Exception:
                continue
    return None


def _pause(secondes):
    time.sleep(secondes)  # isolé pour être neutralisable en test


def _post(url, headers, payload, tentatives=4):
    # User-Agent explicite : sans lui, le pare-feu Cloudflare de certains fournisseurs (ex. Groq)
    # bloque la requête « Python-urllib » avec un 403 / code 1010. On n'écrase pas un en-tête fourni.
    h = {"User-Agent": "AWEMA/1.0 (+https://github.com/codescooper/awema-os)",
         "Accept": "application/json"}
    h.update(headers or {})
    data = json.dumps(payload).encode("utf-8")
    for essai in range(tentatives):
        req = urllib.request.Request(url, data=data, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            # 429 (quota) et 5xx (panne temporaire) : on retente avec backoff exponentiel,
            # en respectant l'en-tête Retry-After s'il est fourni. Les autres codes échouent net.
            retryable = e.code == 429 or 500 <= e.code < 600
            if retryable and essai < tentatives - 1:
                try:
                    ra = int((e.headers.get("Retry-After") or "0").strip())
                except Exception:
                    ra = 0
                _pause(ra if ra > 0 else min(2 ** essai, 30))
                continue
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")
            except Exception:
                pass
            msg = body
            try:
                j = json.loads(body)
                msg = (j.get("error", {}).get("message") if isinstance(j.get("error"), dict)
                       else j.get("error")) or j.get("message") or body
            except Exception:
                pass
            raise RuntimeError(f"HTTP {e.code} — {msg}") from None
        except urllib.error.URLError as e:
            # Erreur réseau (timeout, DNS…) : on retente aussi.
            if essai < tentatives - 1:
                _pause(min(2 ** essai, 30))
                continue
            raise RuntimeError(f"réseau : {getattr(e, 'reason', e)}") from None


# --------------------------------------------------------------------------- #
# chat() — dispatch par type de fournisseur
# --------------------------------------------------------------------------- #
def chat(user, system=None, schema_hint=None, model=None, max_tokens=None):
    """Appelle l'IA active. Renvoie le texte, ou (si schema_hint) un objet JSON parsé.

    Renvoie None UNIQUEMENT si aucune IA n'est configurée (skip gracieux). Lève RuntimeError sur
    erreur API réelle OU si la réponse n'est pas un JSON exploitable (schema_hint demandé) — ainsi
    un échec de parsing n'est plus confondu par l'appelant avec « pas de clé IA »."""
    pid, cfg = actif()
    if not cfg:
        return None
    key = _lookup(cfg.get("cle", "")) or ("ollama" if pid == "ollama" else None)
    if not key:
        return None
    if max_tokens is None:
        try:
            max_tokens = int(os.environ.get("AWEMA_AI_MAX_TOKENS", "4000"))
        except Exception:
            max_tokens = 4000
    model = _resolve_model(model, cfg)
    base = (cfg.get("base_url") or "").rstrip("/")
    contenu = user
    if schema_hint:
        contenu += ("\n\nRéponds UNIQUEMENT avec un JSON valide conforme à ce schéma "
                    f"(pas de texte autour) :\n{schema_hint}")

    if cfg.get("type") == "anthropic":
        payload = {"model": model, "max_tokens": max_tokens,
                   "messages": [{"role": "user", "content": contenu}]}
        if system:
            payload["system"] = system
        data = _post(base + "/messages", {
            "x-api-key": key, "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json"}, payload)
        blocs = data.get("content") or []
        texte = "".join(b.get("text", "") for b in blocs if b.get("type") == "text")
    else:  # compatible OpenAI (/chat/completions)
        msgs = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": contenu}]
        entetes = {"Authorization": f"Bearer {key}", "content-type": "application/json"}
        payload = {"model": model, "max_tokens": max_tokens, "messages": msgs}
        if schema_hint:
            # Mode JSON natif : la plupart des fournisseurs compatibles OpenAI (Groq, Gemini,
            # Mistral, OpenAI…) garantissent alors un JSON syntaxiquement valide.
            payload["response_format"] = {"type": "json_object"}
        try:
            data = _post(base + "/chat/completions", entetes, payload)
        except RuntimeError as e:
            # Certains fournisseurs ne supportent pas response_format → 400. On retente UNE fois
            # sans, en s'appuyant sur le schema_hint du prompt (comportement historique).
            if schema_hint and "HTTP 400" in str(e):
                payload.pop("response_format", None)
                data = _post(base + "/chat/completions", entetes, payload)
            else:
                raise
        texte = (((data.get("choices") or [{}])[0]).get("message") or {}).get("content", "")

    if not schema_hint:
        return texte
    obj = _extraire_json(texte)
    if obj is None:
        apercu = " ".join((texte or "").split())[:200] or "<réponse vide>"
        raise RuntimeError("réponse IA non conforme (aucun JSON exploitable) — extrait : " + apercu)
    return obj


# --------------------------------------------------------------------------- #
# Enveloppe commune des sorties d'agents + validation
# --------------------------------------------------------------------------- #
def enveloppe(agent, items, modele, provenance):
    return {
        "agent": agent,
        "genere_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modele": modele,
        "provenance": provenance or {},
        "items": list(items or []),
    }


def valider_enveloppe(obj, item_requis=None):
    err = []
    if not isinstance(obj, dict):
        return False, ["la sortie n'est pas un objet"]
    for k in ("agent", "genere_le", "modele", "provenance", "items"):
        if k not in obj:
            err.append(f"clé manquante : {k}")
    if "items" in obj and not isinstance(obj["items"], list):
        err.append("items doit être une liste")
    if "provenance" in obj and not isinstance(obj["provenance"], dict):
        err.append("provenance doit être un objet")
    for n, it in enumerate(obj.get("items", []) if isinstance(obj.get("items"), list) else []):
        if not isinstance(it, dict):
            err.append(f"items[{n}] n'est pas un objet")
            continue
        for k in (item_requis or []):
            if k not in it:
                err.append(f"items[{n}] : clé requise manquante « {k} »")
    return (len(err) == 0), err


if __name__ == "__main__":
    import sys
    if "--providers" in sys.argv:
        _, providers = _registre()
        print("Fournisseurs d'IA branchables (★ = palier gratuit / crédits d'essai) :\n")
        for pid, c in providers.items():
            star = "★" if c.get("gratuit") else " "
            print(f"  {star} {pid:12} {c.get('label',''):22} {c.get('offre','')}")
            print(f"      clé: {c.get('cle','')}  ·  inscription: {c.get('signup','')}")
        print("\nActiver : AWEMA_AI_PROVIDER=<id> + sa clé (env ou `awema set ia <CLE>=…`).")
    elif "--check" in sys.argv:
        pid, cfg = actif()
        if pid:
            print(f"✅ IA active : {cfg.get('label', pid)} ({pid}) · modèle {modele_actif()}")
        else:
            print("ℹ️ Aucune IA configurée — agents désactivés (skip gracieux). "
                  "Voir les options gratuites : python3 scripts/awema_ai.py --providers")
    else:
        print(__doc__)
