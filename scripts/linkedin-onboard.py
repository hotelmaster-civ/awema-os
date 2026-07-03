#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assistant d'autorisation LinkedIn — génère l'ACCESS TOKEN OAuth dont le connecteur a besoin.

Le « Client Secret » de l'app ≠ l'access token. Cet assistant fait, UNE FOIS, la danse OAuth
dans ton navigateur et récupère l'access token (Bearer) qui lit les stats de Page entreprise.

Pré-requis (côté app LinkedIn, voir connect-linkedin.html / docs/10) :
  • app vérifiée avec ta Page entreprise ;
  • produit « Community Management API » demandé (Development Tier = immédiat pour tes Pages) ;
  • Client ID + Client Secret (onglet Auth) ;
  • une URL de redirection autorisée (onglet Auth).

Usage :
  # 1) Capture auto (serveur local) — ajoute http://127.0.0.1:8724/callback aux redirect URLs de l'app
  export LINKEDIN_CLIENT_ID=...    # (ou on te le demande)
  python3 scripts/linkedin-onboard.py

  # 2) Repli sans serveur local — utilise la redirection github.io déjà enregistrée (oauth.html)
  python3 scripts/linkedin-onboard.py --paste

Le secret n'est jamais affiché ni passé en argument : il est lu via variable d'env ou saisie masquée.
À la fin : l'access token est rangé dans le store local (.awema, gitignoré) et te montre comment
le mettre dans le Secret GitHub LINKEDIN_TOKEN.
"""
import getpass
import http.server
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

AUTH = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN = "https://www.linkedin.com/oauth/v2/accessToken"
SCOPES = os.environ.get("LINKEDIN_SCOPES", "r_organization_social rw_organization_admin")
REDIRECT_GITHUB = ("https://codescooper.github.io/"
                   "AwemA---Agence-Web-Marketing-Africaine/oauth.html")
PORT = int(os.environ.get("LINKEDIN_PORT", "8724"))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ask(prompt, default=""):
    v = input(f"{prompt}" + (f" [{default}]" if default else "") + " > ").strip()
    return v or default


def _post_form(url, params):
    body = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        try:
            j = json.loads(body)
            raise RuntimeError(f"{j.get('error')} — {j.get('error_description', body)}") from None
        except RuntimeError:
            raise
        except Exception:
            raise RuntimeError(f"HTTP {e.code} — {body}") from None


def echanger(cid, cs, code, redirect):
    d = _post_form(TOKEN, {"grant_type": "authorization_code", "code": code,
                           "redirect_uri": redirect, "client_id": cid, "client_secret": cs})
    if not d.get("access_token"):
        raise RuntimeError(f"réponse sans access_token : {d}")
    return d


def _authorize_url(cid, redirect):
    return AUTH + "?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": redirect,
        "scope": SCOPES, "state": os.urandom(4).hex()})


class _Catch(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if ("code" in params) or ("error" in params):
            self.server.captured = params
        ok = "code" in params
        msg = ("✅ Page autorisée — reviens au terminal." if ok
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


def capter_auto(cid, cs):
    redirect = f"http://127.0.0.1:{PORT}/callback"
    url = _authorize_url(cid, redirect)
    httpd = http.server.HTTPServer(("127.0.0.1", PORT), _Catch)
    httpd.captured = None
    httpd.timeout = 300
    print(f"\n→ Ajoute d'abord cette URL aux « Authorized redirect URLs » de l'app (onglet Auth) :\n   {redirect}\n")
    input("   Quand c'est fait, appuie sur Entrée pour ouvrir le navigateur… ")
    print("→ J'ouvre le navigateur… autorise la Page.")
    print("   (si rien ne s'ouvre, colle cette URL)\n   " + url + "\n")
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
    return echanger(cid, cs, code, redirect)


def capter_paste(cid, cs):
    redirect = REDIRECT_GITHUB
    url = _authorize_url(cid, redirect)
    print(f"\n→ Vérifie que cette URL est dans les « Authorized redirect URLs » de l'app :\n   {redirect}\n")
    print("→ Ouvre cette URL, autorise, puis colle l'URL de la page de redirection :\n   " + url + "\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    colle = ask("URL de redirection (ou juste le code)")
    if "code=" in colle:
        q = urllib.parse.urlparse(colle).query or colle.split("?", 1)[-1]
        code = urllib.parse.parse_qs(q).get("code", [""])[0]
    else:
        code = colle.strip()
    if not code:
        raise RuntimeError("aucun code fourni.")
    return echanger(cid, cs, code, redirect)


def main():
    paste = "--paste" in sys.argv
    print("=== Assistant d'autorisation LinkedIn (AWEMA) ===")
    cid = os.environ.get("LINKEDIN_CLIENT_ID") or ask("Client ID de l'app LinkedIn")
    if not cid:
        sys.exit("❌ Client ID requis.")
    cs = os.environ.get("LINKEDIN_CLIENT_SECRET")
    if not cs:
        cs = getpass.getpass("Client Secret (saisie masquée) > ").strip()
    if not cs:
        sys.exit("❌ Client Secret requis (il sert UNE fois à fabriquer le token).")
    print(f"\nScopes demandés : {SCOPES}")
    print("Mode :", "collage d'URL (--paste)" if paste else "capture automatique (serveur local)")
    try:
        d = capter_paste(cid, cs) if paste else capter_auto(cid, cs)
    except Exception as e:
        sys.exit(f"\n❌ Échec : {e}\n   → Vérifie : produit Community Management API accordé, app vérifiée avec la Page, "
                 "redirect URL enregistrée, scopes autorisés.")
    access = d["access_token"]
    exp = d.get("expires_in")
    refresh = d.get("refresh_token")
    print("\n✅ Access token obtenu" + (f" (valable ~{int(exp)//86400} j)" if exp else "") + ".")
    if refresh:
        print("   (refresh_token également fourni — conservé dans le store local)")

    # Range dans le store local (.awema, gitignoré) sans exposer la valeur en argument
    try:
        subprocess.run([sys.executable, os.path.join(RACINE, "scripts", "awema.py"),
                        "set", "linkedin", "LINKEDIN_TOKEN", "--stdin"],
                       input=access, text=True, cwd=RACINE, check=True)
        if refresh:
            subprocess.run([sys.executable, os.path.join(RACINE, "scripts", "awema.py"),
                            "set", "linkedin", "LINKEDIN_REFRESH_TOKEN", "--stdin"],
                           input=refresh, text=True, cwd=RACINE, check=True)
        print("✅ Rangé dans le store local (.awema/credentials.json).")
    except Exception as e:
        print(f"ℹ️ Stockage local non effectué ({e}).")

    print("\n— PROCHAINES ÉTAPES —")
    print("1) Mets-le dans le Secret GitHub  LINKEDIN_TOKEN  (Settings → Secrets and variables → Actions) :")
    print("   ┌─────────────────────────────────────────────────────────────")
    print("   │ " + access)
    print("   └─────────────────────────────────────────────────────────────")
    print("2) Lance la synchro :  awema connect linkedin   (ou le workflow « Sync présence digitale »).")


if __name__ == "__main__":
    main()
