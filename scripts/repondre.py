#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AWEMA · Réponses aux commentaires (file d'attente Git, même modèle que ADR-010).

Le dashboard écrit une demande dans modules/*/clients/*/_donnees/_reponses/<id>.json
(statut « a_envoyer ») puis déclenche reply.yml. Ce script envoie la réponse via la
Graph API Meta (POST /<commentaire_id>/comments avec le token de la Page), de façon
IDEMPOTENTE (un fichier « envoye » ou « echec » n'est jamais retraité), et réécrit
le fichier avec le résultat.

Format d'un fichier de file :
  {"id": "r-…", "client": "slug", "reseau": "facebook",
   "commentaire_id": "<id Graph du commentaire>", "message": "texte de la réponse",
   "comptes": {"facebook": "<page_id>"}, "statut": "a_envoyer", "tentatives": 0}

Mode :  python3 scripts/repondre.py            → envoie réellement
        python3 scripts/repondre.py --dry-run  → liste sans envoyer

ADN : stdlib uniquement ; aucun secret dans le dépôt ; les tokens ne sont jamais loggés.
"""
import glob
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone

# réutilise les briques éprouvées du moteur de publication (UA, erreurs lisibles)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publisher import GRAPH, http, msg_erreur, token  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, ".."))
MAX_TENTATIVES = 3


def envoyer_facebook(item):
    """Répond à un commentaire de Page : token de Page via /me/accounts, puis
    POST /<commentaire_id>/comments. → {"ok":bool, "detail"|"error":...}"""
    tok = token("META_TOKEN")
    if not tok:
        return {"ok": False, "error": "META_TOKEN manquant"}
    cid = item.get("commentaire_id")
    if not cid:
        return {"ok": False, "error": "commentaire_id manquant"}
    page_id = (item.get("comptes") or {}).get("facebook")
    st, acc = http(GRAPH + "/me/accounts?" + urllib.parse.urlencode({"access_token": tok}))
    page = None
    for p in (acc or {}).get("data") or []:
        if not page_id or str(p.get("id")) == str(page_id):
            page = p
            break
    if not page:
        return {"ok": False, "error": "Page introuvable (admin requis / scope pages_show_list)"}
    st, r = http(GRAPH + "/%s/comments" % cid, data=urllib.parse.urlencode(
        {"message": item.get("message") or "", "access_token": page.get("access_token")}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    if st in (200, 201) and r.get("id"):
        return {"ok": True, "detail": r.get("id")}
    return {"ok": False, "error": msg_erreur(r)}


ENVOYEURS = {"facebook": envoyer_facebook}


def traiter(item, envoyer=None):
    """Transition de statut d'une demande. Idempotent : ne touche qu'aux « a_envoyer »."""
    if (item.get("statut") or "") != "a_envoyer":
        return item
    fn = (envoyer or ENVOYEURS.get((item.get("reseau") or "facebook").lower()))
    if not fn:
        item["statut"] = "echec"
        item["erreur"] = "réseau non supporté : %s" % item.get("reseau")
        return item
    try:
        res = fn(item)
    except Exception as e:  # une exception ne doit jamais bloquer le reste de la file
        res = {"ok": False, "error": "exception : %s" % str(e)[:160]}
    if res.get("ok"):
        item["statut"] = "envoye"
        item["reponse_id"] = res.get("detail")
        item["envoye_le"] = datetime.now(timezone.utc).isoformat()
        item.pop("erreur", None)
    else:
        item["tentatives"] = (item.get("tentatives") or 0) + 1
        item["erreur"] = res.get("error")
        if item["tentatives"] >= MAX_TENTATIVES:
            item["statut"] = "echec"
    return item


def main(dry_run=False):
    fichiers = sorted(glob.glob(os.path.join(
        RACINE, "modules", "*", "clients", "*", "_donnees", "_reponses", "*.json")))
    en_attente = envoyes = echecs = 0
    for f in fichiers:
        try:
            with open(f, encoding="utf-8") as fh:
                item = json.load(fh)
        except Exception:
            print("⚠️  illisible, ignoré : %s" % os.path.relpath(f, RACINE))
            continue
        if (item.get("statut") or "") != "a_envoyer":
            continue
        en_attente += 1
        if dry_run:
            print("→ [dry-run] %s : « %s » sur %s" % (
                item.get("client"), (item.get("message") or "")[:60], item.get("reseau")))
            continue
        item = traiter(item)
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(item, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        if item.get("statut") == "envoye":
            envoyes += 1
            print("✅ %s : réponse envoyée (%s)" % (item.get("client"), item.get("reponse_id")))
        else:
            echecs += 1
            print("❌ %s : %s (tentative %s/%s)" % (
                item.get("client"), item.get("erreur"), item.get("tentatives"), MAX_TENTATIVES))
    print("Réponses : %d en attente · %d envoyée(s) · %d échec(s)/report(s)"
          % (en_attente, envoyes, echecs))


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
