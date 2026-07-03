#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AWEMA · Planificateur de publication (file d'attente Git + cron). ADR-010.

Parcourt les posts en file d'attente (modules/*/clients/*/_donnees/_planning/*.json), publie ceux
qui sont DUS (statut=programme et publier_le <= maintenant) sur chaque réseau, de façon IDEMPOTENTE
(un réseau déjà publié n'est jamais republié), met à jour le statut et réécrit le fichier.

Tokens d'écriture lus dans l'environnement (Secrets/Variables GitHub) :
  META_TOKEN · LINKEDIN_TOKEN · YOUTUBE_API_KEY (lecture) … (voir TOKENS)
Mode :  python3 scripts/publisher.py            → publie réellement
        python3 scripts/publisher.py --dry-run  → simule (aucun appel réseau), pour tester le moteur

ADN : stdlib uniquement ; aucun secret écrit dans le dépôt ; aucune donnée fictive.
Les appels de publication suivent les specs des plateformes mais doivent être validés en conditions réelles.
"""
import glob
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from urllib.error import HTTPError

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, ".."))
MAX_TENTATIVES = 3
GRAPH = "https://graph.facebook.com/v21.0"


# ————————————————————————— utilitaires —————————————————————————
def maintenant():
    # PUBLISH_NOW (ISO) permet de tester ; sinon l'heure réelle UTC.
    s = os.environ.get("PUBLISH_NOW")
    if s:
        return parse_iso(s)
    return datetime.now(timezone.utc)


def parse_iso(s):
    """Parse ISO-8601. Les offsets de fuseau sont HONORÉS (les pages d'interface écrivent du vrai
    UTC via toISOString(), converti depuis l'heure locale de l'agence : Lagos 09:00 → 08:00Z).
    Une date SANS offset (JSON édité à la main) est interprétée comme UTC — mets un offset
    explicite (ex. 2026-07-02T09:00:00+01:00) si tu écris les fichiers _planning toi-même."""
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        d = datetime.fromisoformat(s)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def http(url, data=None, headers=None, method=None):
    # User-Agent explicite : sans lui, des pare-feux (Cloudflare) bloquent « Python-urllib » (403/1010).
    h = {"Accept": "application/json", "User-Agent": "AWEMA/1.0 (+https://github.com/codescooper/awema-os)"}
    if headers:
        h.update(headers)
    body = None
    if data is not None:
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=h, method=method or ("POST" if data is not None else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"error": "HTTP %s" % e.code}
    except Exception as e:
        return 0, {"error": str(e)}


def token(name):
    return (os.environ.get(name) or "").strip() or None


def telecharger(url):
    """Télécharge un média (octets bruts) depuis son URL publique. None si échec.
    Fonction module-level pour rester monkeypatchable dans les tests (aucun réseau)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "AWEMA/1.0 (+https://github.com/codescooper/awema-os)"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()
    except Exception:
        return None


def msg_erreur(r):
    """Message d'erreur lisible, robuste quel que soit le format de `r`.

    http() renvoie {"error": "<chaîne>"} sur timeout/URLError et l'API renvoie
    {"error": {"message": ...}} : sans ce garde-fou, `.get("message")` sur une
    chaîne lève AttributeError et fait crasher toute la publication.
    """
    e = (r or {}).get("error")
    if isinstance(e, dict):
        return e.get("message") or str(e)[:160]
    if isinstance(e, str):
        return e[:160]
    return str(r)[:160]


# ————————————————————————— connecteurs d'écriture —————————————————————————
# Chaque connecteur : (item, medias[urls]) -> {"ok":bool, "url"|"error":..., "detail":...}
# Codés selon les specs ; à valider en live (scopes d'écriture + IDs de compte + App Review requis).

def c_facebook(item, medias):
    tok = token("META_TOKEN")
    if not tok:
        return {"ok": False, "error": "META_TOKEN manquant"}
    page_id = (item.get("comptes") or {}).get("facebook")
    # Récupère le page access token (et l'id si absent) via /me/accounts.
    st, acc = http(GRAPH + "/me/accounts?" + urllib.parse.urlencode({"access_token": tok}))
    pages = (acc or {}).get("data") or []
    page = None
    for p in pages:
        if not page_id or str(p.get("id")) == str(page_id):
            page = p
            break
    if not page:
        return {"ok": False, "error": "Page introuvable (admin requis / scope pages_show_list)"}
    pid, ptok = page.get("id"), page.get("access_token")
    texte = (item.get("contenu") or {}).get("texte", "")
    if medias:
        st, r = http(GRAPH + "/%s/photos" % pid, data=urllib.parse.urlencode(
            {"url": medias[0], "caption": texte, "access_token": ptok}).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"})
    else:
        lien = (item.get("contenu") or {}).get("lien", "")
        params = {"message": texte, "access_token": ptok}
        if lien:
            params["link"] = lien
        st, r = http(GRAPH + "/%s/feed" % pid, data=urllib.parse.urlencode(params).encode(),
                     headers={"Content-Type": "application/x-www-form-urlencoded"})
    if st in (200, 201) and (r.get("id") or r.get("post_id")):
        pubid = r.get("post_id") or r.get("id")
        return {"ok": True, "url": "https://www.facebook.com/%s" % pubid, "detail": pubid}
    return {"ok": False, "error": msg_erreur(r)}


def linkedin_upload_image(tok, author, url_image):
    """Upload d'une image LinkedIn en 3 temps (spec Assets API) :
    1. POST /v2/assets?action=registerUpload → uploadUrl + URN d'asset ;
    2. PUT des octets bruts sur uploadUrl ;
    3. l'URN est référencé dans le ugcPost par l'appelant.
    Retourne (urn, None) ou (None, "message d'erreur")."""
    entetes = {"Authorization": "Bearer " + tok, "X-Restli-Protocol-Version": "2.0.0"}
    st, r = http("https://api.linkedin.com/v2/assets?action=registerUpload", data={
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author,
            "serviceRelationships": [{"relationshipType": "OWNER",
                                      "identifier": "urn:li:userGeneratedContent"}]}},
        headers=entetes)
    val = (r or {}).get("value") or {}
    asset = val.get("asset")
    mecanismes = val.get("uploadMechanism") or {}
    up = (mecanismes.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest") or {}).get("uploadUrl")
    if st not in (200, 201) or not asset or not up:
        return None, "registerUpload refusé : " + msg_erreur(r)
    octets = telecharger(url_image)
    if not octets:
        return None, "média introuvable/illisible : %s" % url_image[:120]
    st2, r2 = http(up, data=octets, method="PUT",
                   headers={"Authorization": "Bearer " + tok,
                            "Content-Type": "application/octet-stream"})
    if st2 not in (200, 201):
        return None, "upload binaire refusé (HTTP %s) : %s" % (st2, msg_erreur(r2))
    return asset, None


def c_linkedin(item, medias):
    tok = token("LINKEDIN_TOKEN")
    if not tok:
        return {"ok": False, "error": "LINKEDIN_TOKEN manquant"}
    org = (item.get("comptes") or {}).get("linkedin")
    if not org:
        return {"ok": False, "error": "URN d'organisation LinkedIn manquant (comptes.linkedin)"}
    author = org if str(org).startswith("urn:") else ("urn:li:organization:%s" % org)
    texte = (item.get("contenu") or {}).get("texte", "")
    # Images : chaque média passe par registerUpload → PUT → URN. Un échec d'upload fait
    # échouer le réseau ENTIER (retry au prochain run) plutôt que de publier sans visuel.
    assets = []
    for m in medias or []:
        urn, err = linkedin_upload_image(tok, author, m)
        if err:
            return {"ok": False, "error": err}
        assets.append({"status": "READY", "media": urn})
    contenu_partage = {
        "shareCommentary": {"text": texte},
        "shareMediaCategory": "IMAGE" if assets else "NONE"}
    if assets:
        contenu_partage["media"] = assets
    payload = {
        "author": author, "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": contenu_partage},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}}
    st, r = http("https://api.linkedin.com/v2/ugcPosts", data=payload,
                 headers={"Authorization": "Bearer " + tok, "X-Restli-Protocol-Version": "2.0.0"})
    if st in (200, 201) and r.get("id"):
        return {"ok": True, "url": "https://www.linkedin.com/feed/update/%s" % r.get("id"), "detail": r.get("id")}
    return {"ok": False, "error": msg_erreur(r)}


def c_instagram(item, medias):
    tok = token("META_TOKEN")
    if not tok:
        return {"ok": False, "error": "META_TOKEN manquant"}
    ig = (item.get("comptes") or {}).get("instagram")
    if not ig:
        return {"ok": False, "error": "ID utilisateur Instagram (Business) manquant (comptes.instagram)"}
    if not medias:
        return {"ok": False, "error": "Instagram exige une image (URL publique)"}
    texte = (item.get("contenu") or {}).get("texte", "")
    st, r = http(GRAPH + "/%s/media" % ig, data=urllib.parse.urlencode(
        {"image_url": medias[0], "caption": texte, "access_token": tok}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    cid = r.get("id")
    if not cid:
        return {"ok": False, "error": msg_erreur(r)}
    st, r2 = http(GRAPH + "/%s/media_publish" % ig, data=urllib.parse.urlencode(
        {"creation_id": cid, "access_token": tok}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    if r2.get("id"):
        return {"ok": True, "url": "https://www.instagram.com/", "detail": r2.get("id")}
    return {"ok": False, "error": msg_erreur(r2)}


def c_video_a_venir(item, medias):
    # YouTube (upload vidéo) & TikTok (Content Posting API auditée / brouillon) : activés en phase ultérieure.
    return {"ok": False, "error": "Connecteur vidéo à activer (validation plateforme requise)", "differe": True}


CONNECTEURS = {
    "facebook": c_facebook,
    "linkedin": c_linkedin,
    "instagram": c_instagram,
    "youtube": c_video_a_venir,
    "tiktok": c_video_a_venir,
}


# ————————————————————————— moteur (testable) —————————————————————————
def est_du(item, ref):
    if (item.get("statut") or "") not in ("programme", "partiel"):
        return False
    d = parse_iso(item.get("publier_le"))
    return d is not None and d <= ref


def medias_urls(item):
    return [m.get("url") for m in (item.get("media") or []) if m.get("url")]


def publier_item(item, ref, publish=None, dry=False):
    """Publie les réseaux DUS et non encore réussis. Renvoie l'item modifié. `publish` injectable pour les tests."""
    publish = publish or (lambda reseau, it, med: CONNECTEURS.get(reseau, c_video_a_venir)(it, med))
    item.setdefault("resultats", {})
    med = medias_urls(item)
    horo = ref.isoformat()
    for reseau in (item.get("reseaux") or []):
        deja = item["resultats"].get(reseau)
        if deja and deja.get("ok"):
            continue  # idempotent : jamais republier
        if dry:
            res = {"ok": True, "url": "(dry-run)", "detail": "simulation"}
        else:
            try:
                res = publish(reseau, item, med)
            except Exception as e:
                # Un réseau qui plante ne doit jamais faire perdre les réseaux déjà publiés du même item.
                res = {"ok": False, "error": ("exception: %s" % e)[:160]}
        res = dict(res)
        res["at"] = horo
        item["resultats"][reseau] = res
    # statut global
    reseaux = item.get("reseaux") or []
    resolus = [r for r in reseaux if item["resultats"].get(r, {}).get("ok")]
    attente = [r for r in reseaux if not item["resultats"].get(r, {}).get("ok")
               and item["resultats"].get(r, {}).get("differe")]
    echecs = [r for r in reseaux if r not in resolus and r not in attente]
    if len(resolus) == len(reseaux):
        item["statut"] = "publie"
    elif echecs:
        # Au moins un réseau en échec réel (hors différé) → on compte les tentatives.
        # La transition vers « echec » s'applique AUSSI aux posts partiels (au moins un succès) :
        # sans ça, un post partiel était re-tenté toutes les 15 min indéfiniment.
        item["tentatives"] = item.get("tentatives", 0) + 1
        if item["tentatives"] >= MAX_TENTATIVES:
            item["statut"] = "echec"
        else:
            item["statut"] = "partiel" if resolus else "programme"
    else:
        # Il ne reste que des réseaux différés (vidéo à venir) : mis en attente, plus de re-tentative
        # en boucle (évite le churn de commits). Réactivables quand le connecteur vidéo sera livré.
        item["statut"] = "attente_video"
    item["maj_le"] = horo
    return item


def lister_fichiers():
    motif = os.path.join(RACINE, "modules", "*", "clients", "*", "_donnees", "_planning", "*.json")
    return [f for f in sorted(glob.glob(motif)) if os.path.basename(f) != "index.json"]


def main():
    dry = "--dry-run" in sys.argv
    ref = maintenant()
    traites = 0
    for path in lister_fichiers():
        try:
            with open(path, encoding="utf-8") as f:
                item = json.load(f)
        except Exception as e:
            print("⚠️ illisible: %s (%s)" % (path, e))
            continue
        if not est_du(item, ref):
            continue
        avant = item.get("statut")
        try:
            item = publier_item(item, ref, dry=dry)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(item, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # Un item défaillant ne doit jamais empêcher les suivants d'être publiés/enregistrés.
            print("⚠️ échec traitement %s (%s)" % (os.path.relpath(path, RACINE), e))
            continue
        traites += 1
        print("• %s : %s → %s" % (os.path.relpath(path, RACINE), avant, item["statut"]))
    print("✅ %d post(s) traité(s)%s." % (traites, " [DRY-RUN]" if dry else ""))


if __name__ == "__main__":
    main()
