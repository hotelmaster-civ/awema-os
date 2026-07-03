#!/usr/bin/env python3
"""AWEMA · Échange OAuth TikTok côté GitHub Actions (flux 100 % Pages-native).

Déclenché par le bouton « Finaliser » de oauth.html (workflow_dispatch). Le navigateur
ne voit JAMAIS le client_secret : il vit ici en Secret GitHub. Le script :
  1. échange le `code` reçu contre un refresh_token (même appel que tiktok-onboard.py) ;
  2. lit le nom du compte (pour proposer un slug si absent) ;
  3. fusionne {slug: refresh_token} dans la Variable TIKTOK_TOKENS (rotative) via le PAT.

Entrées (env) :
  TT_CODE                code OAuth (entrée workflow)            — requis
  TT_REDIRECT            redirect_uri EXACTE utilisée à l'autorisation (oauth.html) — requis
  TT_SLUG               slug client (sinon dérivé du nom du compte) — optionnel
  TIKTOK_CLIENT_KEY      Secret app TikTok                        — requis
  TIKTOK_CLIENT_SECRET   Secret app TikTok                        — requis
  GH_PAT                 Secret TIKTOK_PAT (Variables: R/W)       — requis pour écrire
  GITHUB_REPOSITORY      owner/repo (fourni par Actions)

ADN : stdlib uniquement, aucun secret écrit dans le dépôt, refresh_token jamais imprimé.
"""
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from urllib.error import HTTPError
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _oauth_lib import post_form, gh, fail, UA  # noqa: E402

TOKEN = "https://open.tiktokapis.com/v2/oauth/token/"
USERINFO = "https://open.tiktokapis.com/v2/user/info/?fields=display_name"


def slugify(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()


def echanger(ck, cs, code, redirect):
    d = post_form(TOKEN, {"client_key": ck, "client_secret": cs, "code": code,
                           "grant_type": "authorization_code", "redirect_uri": redirect})
    if d.get("error"):
        raise RuntimeError("%s — %s" % (d.get("error"), d.get("error_description")))
    return d


def nom_compte(access):
    try:
        req = urllib.request.Request(USERINFO, headers={"Authorization": "Bearer " + access, "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return (json.load(r).get("data", {}).get("user", {}) or {}).get("display_name", "")
    except Exception:
        return ""


def gh_get_tokens(repo, pat):
    try:
        _, body = gh("GET", "/repos/%s/actions/variables/TIKTOK_TOKENS" % repo, pat)
        return json.loads(json.loads(body).get("value") or "{}")
    except HTTPError as e:
        if e.code == 404:
            return {}
        raise


def gh_set_tokens(repo, pat, mapping):
    value = json.dumps(mapping, ensure_ascii=False)
    try:
        gh("PATCH", "/repos/%s/actions/variables/TIKTOK_TOKENS" % repo, pat,
           {"name": "TIKTOK_TOKENS", "value": value})
    except HTTPError as e:
        if e.code == 404:
            gh("POST", "/repos/%s/actions/variables" % repo, pat,
               {"name": "TIKTOK_TOKENS", "value": value})
        else:
            raise


def main():
    ck = (os.environ.get("TIKTOK_CLIENT_KEY") or "").strip()
    cs = (os.environ.get("TIKTOK_CLIENT_SECRET") or "").strip()
    code = (os.environ.get("TT_CODE") or "").strip()
    redirect = (os.environ.get("TT_REDIRECT") or "").strip()
    slug = slugify(os.environ.get("TT_SLUG") or "")
    pat = (os.environ.get("GH_PAT") or "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    if not ck or not cs:
        fail("TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET manquants (Secrets du dépôt).")
    if not code or not redirect:
        fail("code ou redirect_uri manquant (entrées du workflow).")
    if not pat:
        fail("TIKTOK_PAT manquant (Secret, PAT avec « Variables: Read and write »).")

    print("🔑 Échange du code TikTok…")
    tok = echanger(ck, cs, code, redirect)
    rt = tok.get("refresh_token")
    access = tok.get("access_token")
    if not rt:
        fail("Aucun refresh_token reçu (code expiré/déjà utilisé, ou redirect_uri différente de l'autorisation).")

    if not slug:
        slug = slugify(nom_compte(access)) or ("compte-" + (tok.get("open_id", "x")[:8]))
    print("👤 Compte → slug : %s" % slug)

    mapping = gh_get_tokens(repo, pat)
    deja = slug in mapping
    mapping[slug] = rt
    gh_set_tokens(repo, pat, mapping)
    print("✅ « %s » %s dans TIKTOK_TOKENS (%d compte(s))."
          % (slug, "mis à jour" if deja else "ajouté", len(mapping)))
    print("➡️  Lance « Sync TikTok » pour récupérer les stats de ce compte.")


if __name__ == "__main__":
    main()
