#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Briques communes aux échanges OAuth côté GitHub Actions (tiktok/linkedin/meta-exchange.py).

Factorise les helpers HTTP + API GitHub auparavant dupliqués dans les 3 scripts. stdlib uniquement.
User-Agent explicite partout (sinon Cloudflare bloque « Python-urllib » avec un 403/1010).

API : post_form(url, params) · get_json(url) · gh(method, path, pat, data=None)
      gh_set_var(repo, pat, name, value) · gh_get_var(repo, pat, name) · fail(msg)
"""
import json
import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError

UA = "AWEMA/1.0 (+https://github.com/codescooper/awema-os)"


def fail(msg):
    print("::error::" + msg)
    sys.exit(1)


def post_form(url, params):
    """POST application/x-www-form-urlencoded → JSON (échange de jeton OAuth)."""
    body = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def get_json(url):
    """GET → JSON ; renvoie {'error': {...}} en cas d'HTTPError (ex. Graph API Meta)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except Exception:
            return {"error": {"message": "HTTP %s" % e.code}}


def gh(method, path, pat, data=None):
    """Appel API GitHub authentifié. Renvoie (status, body_text)."""
    req = urllib.request.Request("https://api.github.com" + path, method=method,
                                 data=(json.dumps(data).encode() if data is not None else None),
                                 headers={"Authorization": "Bearer " + pat,
                                          "Accept": "application/vnd.github+json",
                                          "Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, (r.read().decode() or "")


def gh_set_var(repo, pat, name, value):
    """Crée ou met à jour une Variable Actions (PATCH, sinon POST si absente)."""
    try:
        gh("PATCH", "/repos/%s/actions/variables/%s" % (repo, name), pat, {"name": name, "value": value})
    except HTTPError as e:
        if e.code == 404:
            gh("POST", "/repos/%s/actions/variables" % repo, pat, {"name": name, "value": value})
        else:
            raise


def gh_get_var(repo, pat, name):
    """Valeur d'une Variable Actions, ou None si absente."""
    try:
        _, body = gh("GET", "/repos/%s/actions/variables/%s" % (repo, name), pat)
        return json.loads(body).get("value")
    except HTTPError as e:
        if e.code == 404:
            return None
        raise
