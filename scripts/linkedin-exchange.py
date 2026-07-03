#!/usr/bin/env python3
"""AWEMA · Échange OAuth LinkedIn côté GitHub Actions (flux 100 % Pages-native).

Déclenché par oauth.html (workflow_dispatch) après autorisation LinkedIn. Le client_secret
vit en Secret GitHub, jamais dans le navigateur. Le script :
  1. échange le `code` contre un access_token (même appel que linkedin-onboard.py) ;
  2. enregistre l'access token dans la Variable LINKEDIN_TOKEN (lue par sync-reseaux.yml),
     et, s'il existe, le refresh_token dans LINKEDIN_REFRESH_TOKEN.

Entrées (env) :
  LI_CODE                code OAuth (entrée workflow)             — requis
  LI_REDIRECT            redirect_uri EXACTE (oauth.html)         — requis
  LINKEDIN_CLIENT_ID     Secret app LinkedIn                      — requis
  LINKEDIN_CLIENT_SECRET Secret app LinkedIn                      — requis
  GH_PAT                 PAT (Variables: R/W) — AWEMA_PAT ou TIKTOK_PAT — requis pour écrire
  GITHUB_REPOSITORY      owner/repo (fourni par Actions)

ADN : stdlib uniquement, aucun secret écrit dans le dépôt, token jamais imprimé.
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _oauth_lib import post_form, gh_set_var, fail  # noqa: E402

TOKEN = "https://www.linkedin.com/oauth/v2/accessToken"


def echanger(cid, cs, code, redirect):
    d = post_form(TOKEN, {"grant_type": "authorization_code", "code": code,
                          "redirect_uri": redirect, "client_id": cid, "client_secret": cs})
    if not d.get("access_token"):
        raise RuntimeError("réponse sans access_token : %s" % d)
    return d


def main():
    cid = (os.environ.get("LINKEDIN_CLIENT_ID") or "").strip()
    cs = (os.environ.get("LINKEDIN_CLIENT_SECRET") or "").strip()
    code = (os.environ.get("LI_CODE") or "").strip()
    redirect = (os.environ.get("LI_REDIRECT") or "").strip()
    pat = (os.environ.get("GH_PAT") or "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    if not cid or not cs:
        fail("LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET manquants (Secrets du dépôt).")
    if not code or not redirect:
        fail("code ou redirect_uri manquant (entrées du workflow).")
    if not pat:
        fail("PAT manquant (Secret AWEMA_PAT ou TIKTOK_PAT, « Variables: Read and write »).")

    print("🔑 Échange du code LinkedIn…")
    d = echanger(cid, cs, code, redirect)
    access = d["access_token"]
    exp = d.get("expires_in")
    gh_set_var(repo, pat, "LINKEDIN_TOKEN", access)
    msg = "✅ LINKEDIN_TOKEN enregistré (Variable)"
    if exp:
        msg += " · valable ~%d j" % (int(exp) // 86400)
    if d.get("refresh_token"):
        gh_set_var(repo, pat, "LINKEDIN_REFRESH_TOKEN", d["refresh_token"])
        msg += " · refresh_token conservé"
    print(msg + ".")
    print("➡️  Lance « Sync présence digitale (réseaux) » pour récupérer les stats LinkedIn.")


if __name__ == "__main__":
    main()
