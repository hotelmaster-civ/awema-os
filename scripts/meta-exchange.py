#!/usr/bin/env python3
"""AWEMA · Échange OAuth Meta (Facebook/Instagram) côté GitHub Actions — flux 100 % Pages-native.

Déclenché par oauth.html après « Se connecter avec Facebook ». Le client_secret de l'app vit en
Secret GitHub, jamais dans le navigateur. Le script :
  1. échange le `code` contre un token court ;
  2. l'allonge en token LONGUE DURÉE (~60 j) ;
  3. l'enregistre dans la Variable META_TOKEN (lue par sync-reseaux.yml).

Entrées (env) :
  FB_CODE                code OAuth (entrée workflow)              — requis
  FB_REDIRECT            redirect_uri EXACTE (oauth.html)          — requis
  FACEBOOK_APP_ID        Secret app Meta                           — requis
  FACEBOOK_APP_SECRET    Secret app Meta                           — requis
  GH_PAT                 PAT (Variables: R/W) — AWEMA_PAT/TIKTOK_PAT — requis
  GITHUB_REPOSITORY      owner/repo (fourni par Actions)

ADN : stdlib uniquement, aucun secret écrit dans le dépôt, token jamais imprimé.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _oauth_lib import get_json, gh_set_var, fail  # noqa: E402

GRAPH = "https://graph.facebook.com/v21.0"


def main():
    app_id = (os.environ.get("FACEBOOK_APP_ID") or "").strip()
    app_secret = (os.environ.get("FACEBOOK_APP_SECRET") or "").strip()
    code = (os.environ.get("FB_CODE") or "").strip()
    redirect = (os.environ.get("FB_REDIRECT") or "").strip()
    pat = (os.environ.get("GH_PAT") or "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    if not app_id or not app_secret:
        fail("FACEBOOK_APP_ID / FACEBOOK_APP_SECRET manquants (Secrets du dépôt).")
    if not code or not redirect:
        fail("code ou redirect_uri manquant (entrées du workflow).")
    if not pat:
        fail("PAT manquant (Secret AWEMA_PAT ou TIKTOK_PAT, « Variables: Read and write »).")

    print("🔑 Échange du code Meta…")
    d = get_json(GRAPH + "/oauth/access_token?" + urllib.parse.urlencode({
        "client_id": app_id, "client_secret": app_secret, "redirect_uri": redirect, "code": code}))
    short = d.get("access_token")
    if not short:
        fail("Pas de token : " + json.dumps(d.get("error") or d)[:180])

    print("⏳ Allongement en token longue durée…")
    d2 = get_json(GRAPH + "/oauth/access_token?" + urllib.parse.urlencode({
        "grant_type": "fb_exchange_token", "client_id": app_id,
        "client_secret": app_secret, "fb_exchange_token": short}))
    longtok = d2.get("access_token") or short

    gh_set_var(repo, pat, "META_TOKEN", longtok)
    print("✅ META_TOKEN enregistré (Variable, ~60 j).")
    print("➡️  Lance « Sync présence digitale (réseaux) » pour découvrir toutes tes Pages.")


if __name__ == "__main__":
    main()
