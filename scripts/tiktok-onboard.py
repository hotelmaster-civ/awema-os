#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assistant d'onboarding TikTok (automatisé au maximum).

OAuth impose UNE action humaine par compte : se connecter au bon compte TikTok dans le
navigateur + cliquer « Authorize ». Ce script automatise TOUT le reste :

  • ouvre l'URL d'autorisation dans le navigateur ;
  • CAPTURE le code automatiquement (petit serveur local) — aucun copier-coller ;
  • échange le code → refresh_token ;
  • récupère le nom du compte et propose un slug ;
  • boucle pour ajouter plusieurs comptes ;
  • MET À JOUR la Variable GitHub TIKTOK_TOKENS automatiquement (si GH_PAT fourni),
    sinon affiche le JSON prêt à coller.

PRÉ-REQUIS (une fois) :
  - Dans l'app TikTok → URL properties / Login Kit → ajouter la Redirect URI :
        http://127.0.0.1:8723/callback
    (et http://localhost:8723/callback par sécurité).
    Si TikTok refuse localhost, lance avec --paste (utilise la redirect github.io existante).

USAGE (Windows cmd / PowerShell / bash) :
  set TIKTOK_CLIENT_KEY=...        (export sous mac/linux)
  set TIKTOK_CLIENT_SECRET=...
  set GH_PAT=...                   (PAT fin avec « Variables: Read and write » — optionnel mais
                                     recommandé : met à jour la Variable tout seul)
  python scripts/tiktok-onboard.py            # capture auto (serveur local)
  python scripts/tiktok-onboard.py --paste    # repli : coller l'URL de redirection
"""
import http.server
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
import webbrowser
from urllib.error import HTTPError

AUTH = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN = "https://open.tiktokapis.com/v2/oauth/token/"
USERINFO = "https://open.tiktokapis.com/v2/user/info/?fields=display_name,follower_count"
SCOPES = "user.info.basic,user.info.profile,user.info.stats,video.list"
REDIRECT_GITHUB = ("https://codescooper.github.io/"
                   "AwemA---Agence-Web-Marketing-Africaine/oauth.html")
REPO_DEFAUT = "codescooper/AwemA---Agence-Web-Marketing-Africaine"
PORT = int(os.environ.get("TIKTOK_PORT", "8723"))


def slugify(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or ""


def ask(prompt, default=""):
    v = input(f"{prompt}" + (f" [{default}]" if default else "") + " > ").strip()
    return v or default


def _post_form(url, params):
    body = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def echanger(ck, cs, code, redirect):
    d = _post_form(TOKEN, {"client_key": ck, "client_secret": cs, "code": code,
                           "grant_type": "authorization_code", "redirect_uri": redirect})
    if d.get("error"):
        raise RuntimeError(f"{d.get('error')} — {d.get('error_description')}")
    return d


def nom_compte(access):
    try:
        req = urllib.request.Request(USERINFO, headers={"Authorization": f"Bearer {access}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return (json.load(r).get("data", {}).get("user", {}) or {}).get("display_name", "")
    except Exception:
        return ""


class _Catch(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        capte = ("code" in params) or ("error" in params)
        if capte:
            self.server.captured = params
        ok = "code" in params
        msg = ("✅ Compte autorisé — reviens au terminal." if ok
               else ("❌ " + (params.get("error_description", [""])[0]) if "error" in params else "…"))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write((
            "<html><body style='font-family:system-ui;background:#0A1F44;color:#eaf0fb;"
            "text-align:center;padding-top:90px'><h2 style='font-family:Montserrat'>AWEMA</h2>"
            f"<p style='font-size:18px'>{msg}</p></body></html>").encode())

    def log_message(self, *a):
        pass


def capter_auto(ck, cs):
    redirect = f"http://127.0.0.1:{PORT}/callback"
    url = AUTH + "?" + urllib.parse.urlencode({
        "client_key": ck, "response_type": "code", "scope": SCOPES,
        "redirect_uri": redirect, "state": os.urandom(4).hex()})
    httpd = http.server.HTTPServer(("127.0.0.1", PORT), _Catch)
    httpd.captured = None
    httpd.timeout = 300
    print("→ J'ouvre le navigateur… autorise le compte TikTok connecté.")
    print("   (si rien ne s'ouvre, colle cette URL dans le navigateur)\n   " + url + "\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    tours = 0
    while httpd.captured is None and tours < 120:
        httpd.handle_request()
        tours += 1
    httpd.server_close()
    if httpd.captured is None:
        raise RuntimeError("aucune redirection reçue (timeout).")
    p = httpd.captured
    code = (p.get("code") or [None])[0]
    if not code:
        raise RuntimeError("refusé : " + (p.get("error_description", [""])[0]))
    return echanger(ck, cs, code, redirect)


def capter_paste(ck, cs):
    url = AUTH + "?" + urllib.parse.urlencode({
        "client_key": ck, "response_type": "code", "scope": SCOPES,
        "redirect_uri": REDIRECT_GITHUB, "state": "x"})
    print("→ Ouvre cette URL, autorise, puis colle l'URL de la page de redirection :\n   " + url + "\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    pasted = ask("URL collée")
    q = urllib.parse.urlparse(pasted).query or pasted.split("?", 1)[-1]
    code = urllib.parse.parse_qs(q).get("code", [""])[0]
    if not code:
        raise RuntimeError("aucun code trouvé dans l'URL collée.")
    return echanger(ck, cs, code, REDIRECT_GITHUB)


# --------- GitHub : lire / écrire la Variable TIKTOK_TOKENS ---------
def gh(method, path, pat, data=None):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method,
                                 data=(json.dumps(data).encode() if data is not None else None),
                                 headers={"Authorization": f"Bearer {pat}",
                                          "Accept": "application/vnd.github+json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, (r.read().decode() or "")


def gh_get_tokens(repo, pat):
    try:
        st, body = gh("GET", f"/repos/{repo}/actions/variables/TIKTOK_TOKENS", pat)
        return json.loads(json.loads(body).get("value") or "{}")
    except HTTPError as e:
        if e.code == 404:
            return {}
        raise


def gh_set_tokens(repo, pat, mapping):
    value = json.dumps(mapping, ensure_ascii=False)
    try:
        gh("PATCH", f"/repos/{repo}/actions/variables/TIKTOK_TOKENS", pat,
           {"name": "TIKTOK_TOKENS", "value": value})
    except HTTPError as e:
        if e.code == 404:
            gh("POST", f"/repos/{repo}/actions/variables", pat,
               {"name": "TIKTOK_TOKENS", "value": value})
        else:
            raise


def main():
    paste = "--paste" in sys.argv
    print("=" * 64)
    print("  AWEMA · Assistant de connexion TikTok")
    print("  (OAuth impose une seule action manuelle : se connecter au compte")
    print("   + cliquer « Authorize ». Le reste est automatique.)")
    print("=" * 64)
    ck = (os.environ.get("TIKTOK_CLIENT_KEY") or ask("Client key TikTok")).strip()
    cs = (os.environ.get("TIKTOK_CLIENT_SECRET") or ask("Client secret TikTok")).strip()
    # Diagnostic SANS exposer le secret : longueurs + préfixe de clé (publique).
    print(f"\n🔎 Diagnostic identifiants :")
    print(f"   client_key    : {len(ck)} car.  ‹{ck[:4]}…{ck[-2:]}›" if ck else "   client_key    : VIDE ❌")
    diag = []
    if not cs:
        diag.append("VIDE ❌")
    else:
        if cs == "ton-secret":
            diag.append("c'est le PLACEHOLDER « ton-secret » ❌")
        if cs != cs.strip():
            diag.append("espaces autour ⚠️")
        if len(cs) >= 50:
            diag.append("anormalement long (doublé ?) ⚠️")
    print(f"   client_secret : {len(cs)} car.  " + (" · ".join(diag) if diag else "format OK ✓"))
    print("   (Un secret d'app TikTok fait ~32-40 caractères. S'il vaut 10 = placeholder.)\n")
    repo = os.environ.get("GITHUB_REPOSITORY", REPO_DEFAUT)
    pat = os.environ.get("GH_PAT")

    if not pat:
        print("\nℹ️  Aucun GH_PAT détecté → je ne pourrai pas mettre à jour la Variable tout seul.")
        print("   Pour l'automatiser (recommandé), crée un PAT « fine-grained » :")
        print("   1) https://github.com/settings/personal-access-tokens/new")
        print("   2) Repository access : Only select repositories → ton dépôt")
        print("   3) Permissions → Repository → Variables : Read and write")
        print("   4) Generate, copie le token, puis relance avec :  set GH_PAT=<le token>")
        print("   (Sans PAT, pas de souci : j'affiche le JSON final à coller à la main.)\n")

    mapping = {}
    if pat:
        try:
            mapping = gh_get_tokens(repo, pat)
            print(f"🔗 Variable GitHub lue — comptes déjà présents : {list(mapping) or '—'}")
        except Exception as e:
            print(f"⚠️ Lecture Variable impossible ({e}). On repart de zéro.")
    elif os.environ.get("TIKTOK_TOKENS"):
        try:
            mapping = json.loads(os.environ["TIKTOK_TOKENS"])
        except Exception:
            pass

    print("\nMode :", "collage d'URL (--paste)" if paste else "capture automatique (serveur local)")
    while True:
        print("\n———————————————————————————————————————————————")
        print("1) Dans le navigateur, connecte-toi au compte TikTok à ajouter.")
        go = ask("2) Entrée pour autoriser  (ou 'q' pour terminer)")
        if go.lower() == "q":
            break
        try:
            tok = capter_paste(ck, cs) if paste else capter_auto(ck, cs)
        except Exception as e:
            print("⚠️ Échec :", e, "— on réessaie.")
            continue
        access, rt = tok.get("access_token"), tok.get("refresh_token")
        if not rt:
            print("⚠️ Pas de refresh_token reçu, on réessaie.")
            continue
        nom = nom_compte(access)
        slug = ask(f"Slug client pour « {nom or '?'} »", slugify(nom))
        if not slug:
            print("⚠️ Slug vide, ignoré.")
            continue
        mapping[slug] = rt
        print(f"✅ « {slug} » ajouté ({len(mapping)} compte(s) au total).")

    if not mapping:
        print("\nRien à enregistrer. À bientôt.")
        return
    if pat:
        try:
            gh_set_tokens(repo, pat, mapping)
            print(f"\n✅ Variable GitHub TIKTOK_TOKENS mise à jour automatiquement "
                  f"({len(mapping)} compte(s)). Lance « Run workflow » → Sync TikTok.")
            return
        except Exception as e:
            print(f"\n⚠️ MAJ Variable échouée ({e}). Voici le JSON à coller à la main :")
    print("\n➡️  Colle ceci dans la Variable GitHub TIKTOK_TOKENS :\n")
    print(json.dumps(mapping, ensure_ascii=False))


if __name__ == "__main__":
    main()
