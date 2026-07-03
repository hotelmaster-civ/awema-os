#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Connecteur « présence digitale » → écrit reseaux.json (données RÉELLES).

Remplit le contrat outils/_data (reseaux.json) à partir des réseaux sociaux. Voies :

  1) META — TOUTES LES PAGES (recommandé pour l'agence)
     Un seul token : découvre toutes les Pages gérées et crée/maj un client par Page.
     export META_TOKEN="EAAB..."
     python3 connect-reseaux.py --meta-all

  2) META — UNE PAGE précise
     export META_TOKEN="EAAB..." FB_PAGE_ID="..." IG_USER_ID="..."
     python3 connect-reseaux.py --meta modules/marketing/clients/mon-client

  3) IMPORT MANUEL (CSV exporté depuis Meta Business Suite / TwoMinuteReports / autre)
     python3 connect-reseaux.py --manuel <client_dir> <export.csv>

  4) TIKTOK — comptes autorisés (Display API v2) — voir docs/07-connecter-tiktok.md
     export TIKTOK_CLIENT_KEY=... TIKTOK_CLIENT_SECRET=... TIKTOK_TOKENS='{"slug":"refresh"}'
     python3 connect-reseaux.py --tiktok-all
     # Onboarding (échange d'un code OAuth contre un refresh_token) :
     python3 connect-reseaux.py --tiktok-auth <code> <redirect_uri>

  5) LINKEDIN — Pages entreprise (Community Management API) — voir docs/10-connecter-linkedin.md
     export LINKEDIN_TOKEN=...        # access token OAuth (r_organization_social / rw_organization_admin)
     python3 connect-reseaux.py --linkedin-all

Les réseaux fusionnent : Facebook (--meta-all) et TikTok (--tiktok-all) coexistent dans le
même reseaux.json sans s'écraser.

Aucune donnée inventée : si une source est absente, les champs restent null.
Le réseau du sandbox peut bloquer graph.facebook.com → lancer depuis une machine
connectée (ou via le GitHub Action .github/workflows/sync-reseaux.yml).

TEST hors-ligne : définir AWEMA_PAGES_FIXTURE=<fichier.json> pour simuler me/accounts.
"""
import csv
import glob
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request


# User-Agent explicite sur TOUTES les requêtes du fichier : sans lui, des pare-feux (Cloudflare)
# bloquent « Python-urllib » avec un 403/1010 (cf. scripts/_oauth_lib.py). L'opener global ajoute
# l'en-tête à chaque urlopen() sauf s'il est déjà fourni par la requête.
_UA_OPENER = urllib.request.build_opener()
_UA_OPENER.addheaders = [("User-Agent", "AWEMA/1.0 (+https://github.com/codescooper/awema-os)"),
                         ("Accept", "application/json")]
urllib.request.install_opener(_UA_OPENER)
from datetime import datetime, timezone

GRAPH = "https://graph.facebook.com/v21.0"
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.environ.get("AWEMA_PAGES_FIXTURE")  # tests hors-ligne


def _pages_ignorees():
    """IDs de Pages à ne JAMAIS synchroniser (anciennes pages, doublons, pages vides).
    Éditer scripts/reseaux-ignore.json : {"pages_ignorees": ["<page_id>", ...]}."""
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reseaux-ignore.json")
    try:
        return {str(x) for x in json.load(open(f, encoding="utf-8")).get("pages_ignorees", [])}
    except Exception:
        return set()


IGNOREES = _pages_ignorees()

# Insights Page (28 j) — les noms de métriques valides varient selon la version de l'API.
# On distingue la VRAIE portée (reach) des simples VUES de page : ce ne sont pas la même chose.
#   • page_impressions_unique / page_impressions = portée/impressions (souvent dépréciées en v21)
#   • page_views_total = nombre de vues de la Page (disponible en v21)
# Pour chaque indicateur, on essaie les candidats dans l'ordre et on garde le 1er qui répond.
# Insights Page (28 j) — en API v21, Meta a déprécié la quasi-totalité des métriques :
# page_impressions*, post_impressions*, page_fan_adds/removes → (#100) « invalid metric ».
# SEULE page_views_total répond encore. On ne sonde donc QUE les vues (les autres indicateurs
# « portée » / « croissance » ne sont plus exposés par l'API — on ne les invente pas).
VUES_CANDIDATS = ["page_views_total"]            # vues de la Page (28 j) — disponible en v21
_METRIQUE = {"vues": None}

REACTIONS = ["like", "love", "care", "haha", "wow", "sad", "angry"]
JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def _vide():
    return {
        "connecte": False, "source": None, "maj": None,
        "global": {k: None for k in ["audience", "posts", "likes", "commentaires",
                                      "partages", "portee", "vues", "engagement_taux"]},
        "par_reseau": {r: {k: None for k in ["abonnes", "posts", "likes", "commentaires",
                                             "partages", "portee", "vues"]}
                       for r in ["facebook", "instagram", "tiktok", "linkedin", "youtube"]},
        "reactions": None,            # {like,love,care,haha,wow,sad,angry} (Facebook, posts récents)
        "cadence": None,              # {dernier_post, jours_depuis, posts_30j, posts_par_semaine}
        "meilleur_creneau": None,     # {jour, heure, par_jour, recommandation}
        "types_contenu": None,        # {photo:{n,eng_moyen}, video:{...}, ...}
        "a_repondre": None,           # {total, exemples:[...]}  ← inbox community management
        "top_commentateurs": [],      # abonnés les plus actifs (vrais « top fans »)
        "top_fans": [], "top_posts": [], "evolution_audience": [],
    }


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # Remonte le vrai message d'erreur Graph (sinon on n'a que "400 Bad Request")
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        msg = body
        try:
            err = json.loads(body).get("error", {})
            msg = (f"{err.get('message')} "
                   f"(code={err.get('code')}, subcode={err.get('error_subcode')})")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} — {msg}") from None


def via_meta(client_dir):
    token = os.environ.get("META_TOKEN")
    page = os.environ.get("FB_PAGE_ID")
    ig = os.environ.get("IG_USER_ID")
    if not token:
        sys.exit("❌ META_TOKEN manquant. export META_TOKEN=...  (et FB_PAGE_ID / IG_USER_ID)")
    data = _vide()
    data["source"] = "meta-graph-api"

    def q(path, params):
        params = {**params, "access_token": token}
        return _get(f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}")

    # --- Facebook Page ---
    if page:
        fb = data["par_reseau"]["facebook"]
        try:
            info = q(page, {"fields": "fan_count,followers_count,picture.type(large){url},cover{source}"})
            fb["abonnes"] = info.get("followers_count") or info.get("fan_count")
            photo = ((info.get("picture") or {}).get("data") or {}).get("url")
            couv = (info.get("cover") or {}).get("source")
            if photo or couv:
                data["visuels"] = {k: v for k, v in
                                   (("photo", photo), ("couverture", couv)) if v}
        except Exception as e:
            print("⚠️ FB page:", e)
        try:
            posts = q(f"{page}/posts", {"fields": "message,likes.summary(true),comments.summary(true),shares",
                                        "limit": 25})["data"]
            fb["posts"] = len(posts)
            likes = sum((p.get("likes", {}).get("summary", {}).get("total_count", 0)) for p in posts)
            comm = sum((p.get("comments", {}).get("summary", {}).get("total_count", 0)) for p in posts)
            fb["likes"], fb["commentaires"] = likes, comm
            for p in posts:
                data["top_posts"].append({
                    "titre": (p.get("message") or "")[:80], "plateforme": "Facebook",
                    "likes": p.get("likes", {}).get("summary", {}).get("total_count", 0),
                    "commentaires": p.get("comments", {}).get("summary", {}).get("total_count", 0),
                    "partages": (p.get("shares") or {}).get("count", 0)})
        except Exception as e:
            print("⚠️ FB posts:", e)

    # --- Instagram Business ---
    if ig:
        ins = data["par_reseau"]["instagram"]
        try:
            info = q(ig, {"fields": "followers_count,media_count"})
            ins["abonnes"] = info.get("followers_count")
            ins["posts"] = info.get("media_count")
        except Exception as e:
            print("⚠️ IG info:", e)
        try:
            media = q(f"{ig}/media", {"fields": "caption,like_count,comments_count", "limit": 25})["data"]
            ins["likes"] = sum(m.get("like_count", 0) for m in media)
            ins["commentaires"] = sum(m.get("comments_count", 0) for m in media)
            for m in media:
                data["top_posts"].append({
                    "titre": (m.get("caption") or "")[:80], "plateforme": "Instagram",
                    "likes": m.get("like_count", 0), "commentaires": m.get("comments_count", 0), "partages": 0})
        except Exception as e:
            print("⚠️ IG media:", e)

    _ecrire(client_dir, data)


def via_manuel(client_dir, csv_path):
    """CSV attendu (souple) : colonnes reseau,abonnes,posts,likes,commentaires,portee."""
    data = _vide(); data["source"] = "manuel"
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r = (row.get("reseau") or "").strip().lower()
            if r in data["par_reseau"]:
                for k in ["abonnes", "posts", "likes", "commentaires", "portee"]:
                    v = row.get(k)
                    data["par_reseau"][r][k] = int(v) if v and v.isdigit() else None
    _ecrire(client_dir, data)


def _consolider(data):
    pr = data["par_reseau"]
    def somme(k):
        vals = [pr[r].get(k) for r in pr if pr[r].get(k) is not None]
        return sum(vals) if vals else None
    g = data["global"]
    g["audience"] = somme("abonnes"); g["posts"] = somme("posts")
    g["likes"] = somme("likes"); g["commentaires"] = somme("commentaires")
    g["partages"] = somme("partages")
    g["portee"] = somme("portee")   # portée Page (reach) — non exposée par l'API v21 → null
    g["vues"] = somme("vues")        # vues de la Page (28 j)
    # Taux d'engagement PAR ABONNÉ = engagement moyen par post / nb d'abonnés (×100).
    # (La portée/reach n'étant plus exposée en v21, on rapporte l'engagement aux abonnés —
    #  indicateur CM standard, toujours disponible.)
    nb, aud = pr["facebook"]["posts"], pr["facebook"]["abonnes"]
    if nb and aud:
        eng = (pr["facebook"].get("likes") or 0) + (pr["facebook"].get("commentaires") or 0) \
            + (pr["facebook"].get("partages") or 0)
        g["engagement_taux"] = round((eng / nb) / aud * 100, 1)
    data["top_posts"] = sorted(
        data["top_posts"],
        key=lambda p: p["likes"] + p["commentaires"] + p.get("partages", 0), reverse=True)[:8]
    data["connecte"] = any(pr[r]["abonnes"] is not None for r in pr)
    data["maj"] = datetime.now(timezone.utc).isoformat(timespec="seconds")


RESEAUX = ["facebook", "instagram", "tiktok", "linkedin", "youtube"]
PLATEFORME = {"facebook": "Facebook", "instagram": "Instagram",
              "tiktok": "TikTok", "linkedin": "LinkedIn", "youtube": "YouTube"}
# Sections dérivées spécifiques à Facebook (issues des posts FB) — préservées si FB n'a pas tourné.
SECTIONS_FB = ["reactions", "cadence", "meilleur_creneau", "types_contenu",
               "a_repondre", "top_commentateurs", "top_fans"]


def _ecrire(client_dir, data):
    """Fusionne les données du réseau qui vient de tourner DANS le reseaux.json existant,
    sans écraser les autres réseaux (Facebook et TikTok coexistent), puis reconsolide."""
    out = os.path.join(client_dir, "_donnees", "reseaux.json")
    base = {}
    try:
        with open(out, encoding="utf-8") as f:
            base = json.load(f)
    except FileNotFoundError:
        pass
    ancienne_ev = base.get("evolution_audience") or []

    # Réseaux réellement remplis par CE sync (les autres sont préservés)
    owned = {net for net, bloc in data["par_reseau"].items()
             if any(v is not None for v in bloc.values())}

    bpr = base.get("par_reseau") or {}
    for net in RESEAUX:
        if net in owned or net not in bpr:
            bpr[net] = data["par_reseau"][net]
        bpr.setdefault(net, {k: None for k in
                             ["abonnes", "posts", "likes", "commentaires", "partages", "portee", "vues"]})
    base["par_reseau"] = bpr

    # top_posts : garde ceux des AUTRES plateformes + ceux de ce sync
    owned_labels = {PLATEFORME[n] for n in owned}
    gardes = [p for p in (base.get("top_posts") or []) if p.get("plateforme") not in owned_labels]
    base["top_posts"] = gardes + (data.get("top_posts") or [])

    if "facebook" in owned:                          # sections dérivées des posts FB
        for k in SECTIONS_FB:
            base[k] = data.get(k)
    if "tiktok" in owned and data.get("tiktok") is not None:
        base["tiktok"] = data["tiktok"]
    if "youtube" in owned and data.get("youtube") is not None:
        base["youtube"] = data["youtube"]
    if "linkedin" in owned and data.get("linkedin") is not None:
        base["linkedin"] = data["linkedin"]
    # Visuels (avatar/couverture) : fusion clé par clé — l'avatar TikTok n'efface
    # jamais la couverture Facebook, et inversement.
    if data.get("visuels"):
        vz = base.get("visuels") or {}
        vz.update({k: v for k, v in data["visuels"].items() if v})
        base["visuels"] = vz
    # Cadence & créneau PAR RÉSEAU : chaque connecteur ne met à jour que SES réseaux
    # (la synchro TikTok ne touche pas la cadence Facebook, et inversement). Pour les réseaux
    # que CE sync possède, son contenu fait foi : une entrée absente signifie « plus aucun post
    # connu » — on retire l'ancienne au lieu de laisser une cadence périmée ressusciter.
    for cle in ("cadence_reseaux", "creneau_reseaux"):
        d = dict(base.get(cle) or {})
        d.update(data.get(cle) or {})
        for net in owned:
            if net not in (data.get(cle) or {}):
                d.pop(net, None)
        if d or cle in base:
            base[cle] = d

    base["source"] = data.get("source") or base.get("source")
    base["client"] = os.path.basename(client_dir.rstrip("/"))
    base.setdefault("global", {k: None for k in ["audience", "posts", "likes", "commentaires",
                                                 "partages", "portee", "vues", "engagement_taux"]})
    for k in ("_doc", "portee_post", "croissance"):  # clés obsolètes
        base.pop(k, None)

    _consolider(base)                                # reconsolide sur les réseaux fusionnés
    _cadence_multi(base)                             # « dernier post » TOUS réseaux (pas seulement FB)

    audience = base["global"].get("audience")
    if audience is not None:
        jour = datetime.now(timezone.utc).date().isoformat()
        ev = [p for p in ancienne_ev if p.get("date") != jour]
        ev.append({"date": jour, "valeur": audience})
        base["evolution_audience"] = ev[-90:]
    else:
        base["evolution_audience"] = ancienne_ev

    with open(out, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=2)
    print(f"✅ {out} — connecté={base['connecte']} source={base['source']} réseaux={sorted(owned)}")
    print("   Pense à régénérer le registre : python3 outils/_data/build.py")


# --------------------------------------------------------------------------- #
# META — découverte de TOUTES les Pages (un client par Page)
# --------------------------------------------------------------------------- #
def slugify(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "page"


def initiales(nom):
    parts = [p for p in re.split(r"\s+", nom or "") if p]
    if not parts:
        return "AW"
    if len(parts) >= 2:
        return (parts[0][:1] + parts[1][:1]).upper()
    return parts[0][:2].upper()


def _pages():
    """Liste les Pages gérées (me/accounts) avec IG lié. Pagination gérée.
    En mode FIXTURE, lit un JSON {"data":[...]} pour tester hors-ligne."""
    if FIXTURE:
        with open(FIXTURE, encoding="utf-8") as f:
            return json.load(f).get("data", [])
    token = os.environ.get("META_TOKEN")
    if not token:
        sys.exit("❌ META_TOKEN manquant. export META_TOKEN=\"EAAB...\"")
    fields = ("name,id,access_token,fan_count,followers_count,"
              "instagram_business_account{id,username,followers_count,media_count}")
    url = f"{GRAPH}/me/accounts?fields={fields}&limit=50&access_token={token}"
    out = []
    while url:
        d = _get(url)
        out += d.get("data", [])
        url = (d.get("paging") or {}).get("next")
    return out


def _trouver_client_par_pageid(page_id):
    motif = os.path.join(RACINE, "modules", "*", "clients", "*", "_donnees", "client.json")
    for cj in glob.glob(motif):
        try:
            d = json.load(open(cj, encoding="utf-8"))
        except Exception:
            continue
        if str(d.get("fb_page_id")) == str(page_id):
            return os.path.dirname(os.path.dirname(cj))
    return None


def _assurer_client_json(client_dir, pg):
    donnees = os.path.join(client_dir, "_donnees")
    os.makedirs(donnees, exist_ok=True)
    cj = os.path.join(donnees, "client.json")
    nom = pg.get("name") or pg.get("id")
    ig = pg.get("instagram_business_account") or {}
    slug = os.path.basename(client_dir)
    if os.path.exists(cj):
        d = json.load(open(cj, encoding="utf-8"))            # préserve les éditions humaines
    else:
        d = {
            "id": slug, "nom": nom, "secteur": "", "lieu": "",
            "module": "marketing", "statut": "actif", "initiales": initiales(nom),
            "reseaux": {
                "facebook": f"https://facebook.com/{pg.get('id')}",
                "instagram": (f"https://instagram.com/{ig.get('username')}" if ig.get("username") else ""),
                "tiktok": "", "linkedin": "", "whatsapp": "",
            },
            "chemins": {
                "campagne": "_donnees/campagne.json", "reseaux": "_donnees/reseaux.json",
                "revue": f"../../../../outils/revue-visuels/index.html?client={slug}",
            },
        }
    d["fb_page_id"] = pg.get("id")
    if ig.get("id"):
        d["ig_user_id"] = ig.get("id")
    json.dump(d, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _champs_posts():
    """Champs riches récupérés en UN appel /posts (réactions par type, commentaires+réponses)."""
    rea = ",".join(f"reactions.type({t.upper()}).limit(0).summary(total_count).as(r_{t})"
                   for t in REACTIONS)
    return ("message,created_time,permalink_url,shares,"
            "attachments{media_type},"
            "comments.summary(true).limit(60){from,message,created_time,"
            "comments.limit(30){from}}," + rea)


def _engagement_page(data, page_id, ptok):
    """Récupère les posts FB enrichis (réactions, commentaires, réponses) puis dérive
    tous les indicateurs community management. Sauté en mode FIXTURE."""
    if FIXTURE or not ptok:
        return
    fb = data["par_reseau"]["facebook"]
    posts = []
    try:
        posts = _get(f"{GRAPH}/{page_id}/posts?fields={_champs_posts()}"
                     f"&limit=30&access_token={ptok}")["data"]
    except Exception as e:
        print(f"  ⚠️ FB posts {page_id}: {e}")

    if posts:
        rea_tot = {t: 0 for t in REACTIONS}
        partages = 0
        for p in posts:
            n_com = (p.get("comments", {}).get("summary", {}) or {}).get("total_count", 0)
            rea = {t: (p.get(f"r_{t}", {}).get("summary", {}) or {}).get("total_count", 0)
                   for t in REACTIONS}
            for t in REACTIONS:
                rea_tot[t] += rea[t]
            n_rea = sum(rea.values())
            sh = (p.get("shares") or {}).get("count", 0)
            partages += sh
            p["_rea"], p["_ncom"], p["_sh"] = n_rea, n_com, sh
            p["_eng"] = n_rea + n_com + sh
            data["top_posts"].append({
                "titre": (p.get("message") or "")[:80], "plateforme": "Facebook",
                "date": p.get("created_time"), "lien": p.get("permalink_url"),
                "likes": n_rea, "commentaires": n_com, "partages": sh,
                "type": _type_post(p), "reactions": rea, "portee": None})
        fb["posts"] = len(posts)
        fb["likes"] = sum(p["_rea"] for p in posts)
        fb["commentaires"] = sum(p["_ncom"] for p in posts)
        fb["partages"] = partages
        data["reactions"] = rea_tot
        _derive_commentaires(data, page_id, posts)
        _cadence(data, posts)
        _creneau(data, posts)
        _types_contenu(data, posts)

    _insights_page(data, page_id, ptok)


def _type_post(p):
    att = ((p.get("attachments") or {}).get("data") or [{}])
    mt = (att[0].get("media_type") or "").lower() if att else ""
    return {"photo": "photo", "video": "vidéo", "share": "lien",
            "album": "album", "link": "lien"}.get(mt, "statut")


def _derive_commentaires(data, page_id, posts):
    """Top commentateurs (abonnés les plus actifs) + commentaires SANS réponse de la Page."""
    compte = {}
    a_repondre = []
    for p in posts:
        for c in (p.get("comments", {}).get("data") or []):
            auteur = (c.get("from") or {})
            nom, aid = auteur.get("name"), auteur.get("id")
            if not nom or str(aid) == str(page_id):
                continue
            compte[nom] = compte.get(nom, 0) + 1
            reponses = (c.get("comments", {}).get("data") or [])
            page_a_repondu = any(str((r.get("from") or {}).get("id")) == str(page_id)
                                 for r in reponses)
            if not page_a_repondu:
                # "id" = ID Graph du commentaire → permet la réponse in-app (scripts/repondre.py)
                a_repondre.append({
                    "id": c.get("id"), "auteur": nom, "message": (c.get("message") or "")[:140],
                    "date": c.get("created_time"), "lien": p.get("permalink_url")})
    top = sorted(compte.items(), key=lambda kv: kv[1], reverse=True)[:8]
    data["top_commentateurs"] = [{"nom": n, "commentaires": k} for n, k in top]
    data["top_fans"] = [{"nom": n, "interactions": k} for n, k in top]  # alias dashboard
    a_repondre.sort(key=lambda x: x.get("date") or "", reverse=True)
    data["a_repondre"] = {"total": len(a_repondre), "exemples": a_repondre[:12]}


def _calc_cadence(dates):
    """Cadence depuis une liste de dates ISO (ordre libre) : dernier post, jours depuis,
    posts sur 30 j, rythme hebdo (4,345 sem./mois). None si aucune date exploitable."""
    dates = sorted([d for d in dates if d], reverse=True)
    if not dates:
        return None
    dernier = _parse_dt(dates[0])
    if not dernier:
        return None
    now = datetime.now(timezone.utc)
    p30 = sum(1 for d in dates if (_parse_dt(d) and (now - _parse_dt(d)).days <= 30))
    return {"dernier_post": dates[0], "jours_depuis": (now - dernier).days,
            "posts_30j": p30, "posts_par_semaine": round(p30 / 4.345, 1)}


def _cadence(data, posts):
    c = _calc_cadence([p.get("created_time") for p in posts])
    if not c:
        return
    data["cadence"] = c
    # Détail par réseau : chaque connecteur remplit SA clé depuis sa liste complète de posts.
    data.setdefault("cadence_reseaux", {})["facebook"] = dict(c)


def _cadence_multi(base):
    """Consolide la cadence sur TOUS les réseaux (Facebook ⊕ Instagram ⊕ TikTok ⊕ YouTube…) :
    - détail : cadence_reseaux, une entrée par réseau (posée par les connecteurs qui ont la
      liste complète des posts ; sinon approximée depuis top_posts, marquée approx=True) ;
    - global : RECALCULÉ à chaque consolidation (jamais de cliquet — un compteur figé devient
      une valeur inventée dès que la fenêtre de 30 j glisse)."""
    maintenant = datetime.now(timezone.utc)
    cad = base.get("cadence") or {}
    cr = dict(base.get("cadence_reseaux") or {})

    # 0) Héritage : une cadence PURE Facebook (pas encore consolidée multi) vient de la liste
    #    complète des 25 posts — c'est la meilleure information Facebook disponible.
    if "facebook" not in cr and cad.get("dernier_post") and not cad.get("multi_reseaux"):
        cr["facebook"] = {k: cad[k] for k in
                          ("dernier_post", "jours_depuis", "posts_30j", "posts_par_semaine")
                          if k in cad}

    # 1) Approximation par réseau depuis top_posts (8 posts max, triés par ENGAGEMENT :
    #    borne basse, marquée approx) — sans jamais écraser une entrée de connecteur.
    label2net = {v: k for k, v in PLATEFORME.items()}
    par_net = {}
    for p in base.get("top_posts") or []:
        net = label2net.get(p.get("plateforme"))
        if net and p.get("date"):
            par_net.setdefault(net, []).append(p["date"])
    for net, dates in par_net.items():
        if net not in cr:
            c = _calc_cadence(dates)
            if c:
                c["approx"] = True
                cr[net] = c

    # 2) Blocs réseau historiques (tiktok/youtube/linkedin) : ils portent la VRAIE date du
    #    dernier post. Elle corrige les entrées approx (les top_posts sont les plus engageants,
    #    pas les plus récents) et crée une ligne minimale quand on n'a rien d'autre.
    for net in ("tiktok", "youtube", "linkedin"):
        dp = (base.get(net) or {}).get("dernier_post")
        pd = _parse_dt(dp)
        if not pd:
            continue
        e = cr.get(net)
        if e is None:
            cr[net] = {"dernier_post": dp, "jours_depuis": None,
                       "posts_30j": None, "posts_par_semaine": None, "approx": True}
        elif e.get("approx"):
            ancien = _parse_dt(e.get("dernier_post"))
            if not ancien or pd > ancien:
                e["dernier_post"] = dp

    # 3) Fenêtres GLISSANTES : jours_depuis recalculé maintenant ; un réseau dont le dernier
    #    post connu est sorti des 30 j n'a — par définition — aucun post sur 30 j.
    for e in cr.values():
        pd = _parse_dt(e.get("dernier_post"))
        if not pd:
            continue
        e["jours_depuis"] = (maintenant - pd).days
        if e["jours_depuis"] > 30 and (e.get("posts_30j") or 0) != 0:
            e["posts_30j"] = 0
            e["posts_par_semaine"] = 0.0

    if cr:
        base["cadence_reseaux"] = cr

    # 4) GLOBAL — reconstruit depuis le détail + top_posts uniquement. L'ancienne cadence
    #    globale n'est PAS candidate : c'est une donnée dérivée (son étiquette réseau peut
    #    être fausse et son compteur figé) ; la version « pure Facebook » a été amorcée en 0).
    candidats = []
    for net, e in cr.items():
        if e and e.get("dernier_post"):
            candidats.append((e["dernier_post"], PLATEFORME.get(net, net)))
    for p in base.get("top_posts") or []:
        if p.get("date"):
            candidats.append((p["date"], p.get("plateforme") or "?"))
    parsed = [(_parse_dt(d), d, lab) for d, lab in candidats]
    parsed = [x for x in parsed if x[0]]
    if not parsed:
        return
    parsed.sort(key=lambda x: x[0], reverse=True)
    dt, raw, lab = parsed[0]
    # posts/30 j global = max(somme des compteurs par réseau — rafraîchis en 3),
    #                         posts datés dédupliqués par (réseau, jour))
    vus, n30 = set(), 0
    for d0, lab0 in candidats:
        pd = _parse_dt(d0)
        if not pd:
            continue
        cle = (lab0, pd.date().isoformat())
        if cle in vus:
            continue
        vus.add(cle)
        if (maintenant - pd).days <= 30:
            n30 += 1
    somme_reseaux = sum((e.get("posts_30j") or 0) for e in cr.values() if e)
    meilleur = max(n30, somme_reseaux)
    base["cadence"] = {
        "dernier_post": raw, "jours_depuis": (maintenant - dt).days,
        "posts_30j": meilleur, "posts_par_semaine": round(meilleur / (30 / 7), 1),
        "dernier_reseau": lab, "multi_reseaux": True}


def _calc_creneau(posts):
    """Engagement moyen par jour de semaine et par heure → meilleur créneau pour publier.
    posts = [{"created_time": ISO, "_eng": int}]. None si aucune date exploitable."""
    par_jour, par_heure = {}, {}
    for p in posts:
        dt = _parse_dt(p.get("created_time"))
        if not dt:
            continue
        eng = p.get("_eng", 0)
        par_jour.setdefault(dt.weekday(), []).append(eng)
        par_heure.setdefault(dt.hour, []).append(eng)
    if not par_jour:
        return None
    moy_jour = {j: sum(v) / len(v) for j, v in par_jour.items()}
    moy_heure = {h: sum(v) / len(v) for h, v in par_heure.items()}
    best_j = max(moy_jour, key=moy_jour.get)
    best_h = max(moy_heure, key=moy_heure.get)
    return {
        "jour": JOURS_FR[best_j], "heure": f"{best_h:02d}h",
        "par_jour": {JOURS_FR[j]: round(m, 1) for j, m in sorted(moy_jour.items())},
        "recommandation": f"{JOURS_FR[best_j]} vers {best_h:02d}h"}


def _creneau(data, posts):
    c = _calc_creneau(posts)
    if not c:
        return
    data["meilleur_creneau"] = c
    data.setdefault("creneau_reseaux", {})["facebook"] = dict(c)


def _types_contenu(data, posts):
    grp = {}
    for p in posts:
        t = _type_post(p)
        grp.setdefault(t, []).append(p.get("_eng", 0))
    data["types_contenu"] = {t: {"n": len(v), "engagement_moyen": round(sum(v) / len(v), 1)}
                             for t, v in grp.items()}


def _parse_dt(s):
    if not s:
        return None
    try:
        return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _insights_page(data, page_id, ptok):
    """Vues de la Page (28 j) via read_insights — seule métrique insights encore valide en v21.
    Reste null si la permission read_insights manque."""
    if FIXTURE or not ptok:
        return
    data["par_reseau"]["facebook"]["vues"] = _insight_28j(page_id, ptok, "vues", VUES_CANDIDATS)


def _insight_28j(page_id, ptok, cle, candidats):
    """Retourne la valeur (28 j) du 1er métrique candidat qui répond, sinon None.
    Mémorise la métrique gagnante par indicateur pour accélérer les pages suivantes."""
    ordre = ([_METRIQUE[cle]] if _METRIQUE[cle] else []) + [
        m for m in candidats if m != _METRIQUE[cle]]
    for metric in ordre:
        try:
            rep = _get(f"{GRAPH}/{page_id}/insights?metric={metric}"
                       f"&period=days_28&access_token={ptok}").get("data", [])
            for m in rep:
                vals = m.get("values") or []
                val = vals[-1].get("value") if vals else None
                if val is not None:
                    _METRIQUE[cle] = metric
                    return val
        except Exception as e:
            print(f"  ⚠️ insights {page_id} [{metric}]: {e}")
    return None


def _engagement_ig(data, ig, ptok):
    if not ig:
        return
    ins = data["par_reseau"]["instagram"]
    ins["abonnes"] = ig.get("followers_count")
    ins["posts"] = ig.get("media_count")
    if FIXTURE or not ptok or not ig.get("id"):
        return
    try:
        media = _get(f"{GRAPH}/{ig['id']}/media?fields=caption,like_count,"
                     f"comments_count,timestamp&limit=25&access_token={ptok}")["data"]
        ins["likes"] = sum(m.get("like_count", 0) for m in media)
        ins["commentaires"] = sum(m.get("comments_count", 0) for m in media)
        for m in media:
            data["top_posts"].append({
                "titre": (m.get("caption") or "")[:80], "plateforme": "Instagram",
                "date": m.get("timestamp"),
                "likes": m.get("like_count", 0), "commentaires": m.get("comments_count", 0),
                "partages": 0})
        c = _calc_cadence([m.get("timestamp") for m in media])
        if c:
            data.setdefault("cadence_reseaux", {})["instagram"] = c
        cn = _calc_creneau([{"created_time": m.get("timestamp"),
                             "_eng": (m.get("like_count") or 0) + (m.get("comments_count") or 0)}
                            for m in media])
        if cn:
            data.setdefault("creneau_reseaux", {})["instagram"] = cn
    except Exception as e:
        print(f"  ⚠️ IG media: {e}")


def _page_info(page_id, ptok):
    """Abonnés + nom + visuels (photo de profil, couverture) via le TOKEN DE PAGE.
    Les URLs CDN Meta expirent au bout de quelques semaines : la synchro hebdo les rafraîchit."""
    if FIXTURE or not ptok:
        return None, None, None
    try:
        d = _get(f"{GRAPH}/{page_id}?fields=name,followers_count,fan_count,"
                 f"picture.type(large){{url}},cover{{source}}&access_token={ptok}")
        ab = d.get("followers_count")
        if ab is None:
            ab = d.get("fan_count")
        visuels = {}
        photo = ((d.get("picture") or {}).get("data") or {}).get("url")
        couv = (d.get("cover") or {}).get("source")
        if photo:
            visuels["photo"] = photo
        if couv:
            visuels["couverture"] = couv
        return ab, d.get("name"), visuels or None
    except Exception as e:
        print(f"  ⚠️ page info {page_id}: {e}")
        return None, None, None


def via_meta_all():
    """Un client par Page gérée. Crée les dossiers manquants, met à jour reseaux.json."""
    try:
        pages = _pages()
    except RuntimeError as e:
        msg = str(e)
        if "code=190" in msg or "access token" in msg.lower():
            sys.exit(
                "❌ Token Meta invalide ou EXPIRÉ.\n"
                "   → Régénère un token **longue durée** (~60 j) : Explorateur API Graph → ⓘ →\n"
                "     « Open in Access Token Tool » → « Extend Access Token », puis mets-le dans\n"
                "     le Secret GitHub META_TOKEN. (Le token de l'Explorateur dure ~1-2 h.)\n"
                f"   Détail Graph : {msg}")
        raise
    n = 0
    for pg in pages:
        page_id = pg.get("id")
        if not page_id:
            continue
        if str(page_id) in IGNOREES:
            print(f"  ⏭️  {pg.get('name') or page_id} ignorée (reseaux-ignore.json)")
            continue
        ptok = pg.get("access_token")
        # Abonnés + nom + visuels (avatar/couverture) fiables via le token de Page
        ab, nom_maj, visuels = _page_info(page_id, ptok)
        if nom_maj:
            pg["name"] = nom_maj
        if ab is None:
            ab = pg.get("followers_count") or pg.get("fan_count")
        client_dir = _trouver_client_par_pageid(page_id) or os.path.join(
            RACINE, "modules", "marketing", "clients", slugify(pg.get("name") or page_id))
        _assurer_client_json(client_dir, pg)
        data = _vide()
        data["source"] = "meta-graph-api"
        if visuels:
            data["visuels"] = visuels
        data["par_reseau"]["facebook"]["abonnes"] = ab
        _engagement_page(data, page_id, ptok)
        _engagement_ig(data, pg.get("instagram_business_account") or {}, ptok)
        _ecrire(client_dir, data)
        n += 1
        print(f"  ✓ {pg.get('name')} ({ab if ab is not None else '—'} abonnés) → "
              f"{os.path.relpath(client_dir, RACINE)}")
    print(f"✅ {n} page(s) synchronisée(s). Régénère le registre : python3 outils/_data/build.py")


# --------------------------------------------------------------------------- #
# TIKTOK — Display API v2 (un compte = une autorisation OAuth, refresh token rotatif)
# --------------------------------------------------------------------------- #
TIKTOK_OAUTH = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_REDIRECT_DEFAUT = ("https://codescooper.github.io/"
                          "AwemA---Agence-Web-Marketing-Africaine/oauth.html")
TIKTOK_API = "https://open.tiktokapis.com/v2"
TIKTOK_USER_FIELDS = ("open_id,display_name,follower_count,following_count,"
                      "likes_count,video_count,avatar_url")
TIKTOK_VIDEO_FIELDS = ("id,title,video_description,view_count,like_count,"
                       "comment_count,share_count,create_time,share_url")


def _tiktok_refresh(client_key, client_secret, refresh_token):
    """Échange un refresh_token contre un access_token + un NOUVEAU refresh_token (rotatif)."""
    body = urllib.parse.urlencode({
        "client_key": client_key, "client_secret": client_secret,
        "grant_type": "refresh_token", "refresh_token": refresh_token}).encode()
    req = urllib.request.Request(TIKTOK_OAUTH, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if d.get("error"):
        raise RuntimeError(f"refresh: {d.get('error')} — {d.get('error_description')}")
    return d  # access_token, refresh_token, expires_in, ...


def _tiktok_get(path, token):
    req = urllib.request.Request(f"{TIKTOK_API}/{path}",
                                 headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _tiktok_post(path, token, payload):
    req = urllib.request.Request(f"{TIKTOK_API}/{path}", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _tiktok_data(user, videos):
    """Façonne un objet reseaux.json (bloc tiktok + top_posts) à partir des réponses API."""
    data = _vide(); data["source"] = "tiktok-display-api"
    if user.get("avatar_url"):
        data["visuels"] = {"photo": user["avatar_url"]}
    tk = data["par_reseau"]["tiktok"]
    tk["abonnes"] = user.get("follower_count")
    tk["posts"] = user.get("video_count")
    tk["likes"] = sum(v.get("like_count", 0) for v in videos) or None
    tk["commentaires"] = sum(v.get("comment_count", 0) for v in videos) or None
    tk["partages"] = sum(v.get("share_count", 0) for v in videos) or None
    tk["vues"] = sum(v.get("view_count", 0) for v in videos) or None
    top = []
    for v in videos:
        titre = (v.get("title") or v.get("video_description") or "")[:80]
        top.append({
            "titre": titre, "plateforme": "TikTok", "date": _ts(v.get("create_time")),
            "lien": v.get("share_url"), "likes": v.get("like_count", 0),
            "commentaires": v.get("comment_count", 0), "partages": v.get("share_count", 0),
            "vues": v.get("view_count", 0), "type": "vidéo"})
    data["top_posts"] = top
    c = _calc_cadence([_ts(v.get("create_time")) for v in videos])
    if c:
        data.setdefault("cadence_reseaux", {})["tiktok"] = c
    cn = _calc_creneau([{"created_time": _ts(v.get("create_time")),
                         "_eng": (v.get("like_count") or 0) + (v.get("comment_count") or 0)
                         + (v.get("share_count") or 0)} for v in videos])
    if cn:
        data.setdefault("creneau_reseaux", {})["tiktok"] = cn
    dpost = max((p["date"] for p in top if p.get("date")), default=None)  # dernier post réel TikTok
    data["tiktok"] = {
        "abonnes": user.get("follower_count"), "video_count": user.get("video_count"),
        "likes_total": user.get("likes_count"),
        "vues_recentes": tk["vues"], "display_name": user.get("display_name"),
        "dernier_post": dpost,
        "top_videos": sorted(top, key=lambda p: p["vues"], reverse=True)[:8],
        "maj": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    return data


def _ts(unix):
    try:
        return datetime.fromtimestamp(int(unix), timezone.utc).isoformat(timespec="seconds")
    except Exception:
        return None


def _client_par_slug(slug):
    d = os.path.join(RACINE, "modules", "marketing", "clients", slug)
    return d if os.path.isdir(os.path.join(d, "_donnees")) else None


def _assurer_client_tiktok(client_dir, slug, user):
    """Crée un client.json minimal pour un client TikTok seul (sinon invisible au dashboard).
    Préserve un client.json existant (ne touche qu'au lien TikTok manquant)."""
    cj = os.path.join(client_dir, "_donnees", "client.json")
    nom = (user or {}).get("display_name") or slug
    if os.path.exists(cj):
        d = json.load(open(cj, encoding="utf-8"))
        d.setdefault("reseaux", {})
        if not d["reseaux"].get("tiktok"):
            d["reseaux"]["tiktok"] = "https://www.tiktok.com/"
    else:
        d = {
            "id": slug, "nom": nom, "secteur": "", "lieu": "",
            "module": "marketing", "statut": "actif", "initiales": initiales(nom),
            "reseaux": {"facebook": "", "instagram": "", "tiktok": "https://www.tiktok.com/",
                        "linkedin": "", "whatsapp": ""},
            "chemins": {"campagne": "_donnees/campagne.json", "reseaux": "_donnees/reseaux.json",
                        "revue": f"../../../../outils/revue-visuels/index.html?client={slug}"},
        }
    json.dump(d, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def via_tiktok_auth(code_ou_url, redirect_uri=None):
    """Onboarding : échange un CODE d'autorisation OAuth contre un refresh_token (à coller
    dans la Variable TIKTOK_TOKENS). Accepte soit le code brut, soit l'URL de redirection
    complète (le code en est extrait + décodé automatiquement). Usage :
      export TIKTOK_CLIENT_KEY=... TIKTOK_CLIENT_SECRET=...
      python3 connect-reseaux.py --tiktok-auth "<code ou URL collée>"  [redirect_uri]"""
    ck = os.environ.get("TIKTOK_CLIENT_KEY"); cs = os.environ.get("TIKTOK_CLIENT_SECRET")
    if not (ck and cs):
        sys.exit("❌ export TIKTOK_CLIENT_KEY=... TIKTOK_CLIENT_SECRET=... d'abord.")
    # Si on a collé l'URL complète (…oauth.html?code=…&scopes=…), on en extrait le code.
    if "code=" in code_ou_url:
        q = urllib.parse.urlparse(code_ou_url).query or code_ou_url.split("?", 1)[-1]
        code = urllib.parse.parse_qs(q).get("code", [""])[0]
        if not redirect_uri:
            base = code_ou_url.split("?", 1)[0]
            if base.startswith("http"):
                redirect_uri = base
    else:
        code = urllib.parse.unquote(code_ou_url)
    if not redirect_uri:
        redirect_uri = os.environ.get("TIKTOK_REDIRECT_URI", TIKTOK_REDIRECT_DEFAUT)
    body = urllib.parse.urlencode({
        "client_key": ck, "client_secret": cs, "code": code,
        "grant_type": "authorization_code", "redirect_uri": redirect_uri}).encode()
    req = urllib.request.Request(TIKTOK_OAUTH, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if d.get("error"):
        sys.exit(f"❌ {d.get('error')} — {d.get('error_description')}")
    print("✅ refresh_token obtenu (valable ~365 j). Ajoute-le à la Variable TIKTOK_TOKENS :")
    print(f'   {{"<slug-du-client>": "{d.get("refresh_token")}"}}')
    print(f"   (open_id={d.get('open_id')}, expires_in={d.get('expires_in')}s)")


def _alias_slug(reseau, slug):
    """Redirige un slug de compte vers la fiche client canonique (config/aliases.json)."""
    try:
        with open(os.path.join(RACINE, "config", "aliases.json"), encoding="utf-8") as f:
            amap = json.load(f)
        return (amap.get(reseau) or {}).get(slug, slug)
    except Exception:
        return slug


def _sauver_tokens_tiktok(mapping):
    """Écrit l'état courant des refresh tokens dans TIKTOK_TOKENS_OUT (rotation TikTok :
    l'ancien token est invalidé côté serveur dès le refresh — il faut donc sauvegarder
    APRÈS CHAQUE compte, pas seulement en fin de boucle)."""
    out = os.environ.get("TIKTOK_TOKENS_OUT")
    if not out:
        return False
    with open(out, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False)
    return True


def via_tiktok_all():
    """Pour chaque compte TikTok autorisé (TIKTOK_TOKENS = {slug: refresh_token}), rafraîchit
    le token, récupère profil + vidéos, et fusionne dans reseaux.json. Écrit les refresh
    tokens ROTÉS dans le fichier TIKTOK_TOKENS_OUT pour que le workflow mette à jour la Variable."""
    ck = os.environ.get("TIKTOK_CLIENT_KEY")
    cs = os.environ.get("TIKTOK_CLIENT_SECRET")
    raw = os.environ.get("TIKTOK_TOKENS")
    if not (ck and cs and raw):
        sys.exit("❌ TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET et TIKTOK_TOKENS (JSON) requis.")
    try:
        comptes = json.loads(raw)              # {slug: refresh_token}
    except Exception:
        sys.exit("❌ TIKTOK_TOKENS doit être un JSON : {\"client-slug\": \"refresh_token\"}")
    nouveaux, n = {}, 0
    for slug, rt in comptes.items():
        try:
            tok = _tiktok_refresh(ck, cs, rt)
        except Exception as e:
            print(f"  ⚠️ {slug} : refresh échoué ({e}) — re-autorisation nécessaire.")
            nouveaux[slug] = rt                # conserve l'ancien (sera à renouveler à la main)
            continue
        access = tok.get("access_token")
        nouveaux[slug] = tok.get("refresh_token") or rt   # ROTATION : on garde le nouveau
        try:
            user = (_tiktok_get(f"user/info/?fields={TIKTOK_USER_FIELDS}", access)
                    .get("data", {}).get("user", {}))
            videos = (_tiktok_post(f"video/list/?fields={TIKTOK_VIDEO_FIELDS}", access,
                                   {"max_count": 20}).get("data", {}).get("videos", []))
        except Exception as e:
            print(f"  ⚠️ {slug} : récupération données échouée ({e}).")
            continue
        _sauver_tokens_tiktok(nouveaux)                  # tokens rotés sécurisés AVANT toute écriture
        try:
            canon = _alias_slug("tiktok", slug)          # rattache à la fiche canonique si alias
            client_dir = _client_par_slug(canon)
            if not client_dir:
                client_dir = os.path.join(RACINE, "modules", "marketing", "clients", canon)
                os.makedirs(os.path.join(client_dir, "_donnees"), exist_ok=True)
            _assurer_client_tiktok(client_dir, canon, user)  # client.json → visible au dashboard
            _ecrire(client_dir, _tiktok_data(user, videos))
        except Exception as e:
            # Un client.json corrompu ne doit JAMAIS interrompre la boucle après rotation :
            # les nouveaux refresh_tokens sont déjà sauvegardés, on passe au compte suivant.
            print(f"  ⚠️ {slug} : écriture des données échouée ({e}) — token roté conservé.")
            continue
        n += 1
        print(f"  ✓ TikTok {slug} ({user.get('follower_count', '—')} abonnés, "
              f"{user.get('video_count', '—')} vidéos)")
    if _sauver_tokens_tiktok(nouveaux):
        print(f"🔑 Refresh tokens rotés écrits dans {os.environ.get('TIKTOK_TOKENS_OUT')} "
              "(à reporter dans la Variable TIKTOK_TOKENS).")
    print(f"✅ {n} compte(s) TikTok synchronisé(s). Régénère le registre : python3 outils/_data/build.py")


# --------------------------------------------------------------------------- #
# YOUTUBE — Data API v3 (stats publiques de chaîne, clé API, SANS OAuth)
# --------------------------------------------------------------------------- #
YT_API = "https://www.googleapis.com/youtube/v3"


def _yt(path, params):
    return _get(f"{YT_API}/{path}?{urllib.parse.urlencode(params)}")


def _youtube_data(key, handle, chid):
    """Stats publiques d'une chaîne (abonnés, vues, vidéos) + top vidéos récentes."""
    params = {"part": "snippet,statistics,contentDetails", "key": key}
    if chid:
        params["id"] = chid
    else:
        params["forHandle"] = (handle or "").lstrip("@")
    items = _yt("channels", params).get("items", [])
    if not items:
        return None
    ch = items[0]
    st = ch.get("statistics", {}) or {}
    def _i(x):
        try:
            return int(x)
        except Exception:
            return None
    data = _vide(); data["source"] = "youtube-data-api"
    yt = data["par_reseau"]["youtube"]
    yt["abonnes"] = _i(st.get("subscriberCount"))
    yt["posts"] = _i(st.get("videoCount"))
    yt["vues"] = _i(st.get("viewCount"))                 # vues totales de la chaîne
    uploads = ((ch.get("contentDetails", {}) or {}).get("relatedPlaylists", {}) or {}).get("uploads")
    vids = []
    if uploads:
        try:
            pit = _yt("playlistItems", {"part": "contentDetails", "playlistId": uploads,
                                        "maxResults": 15, "key": key}).get("items", [])
            ids = [i["contentDetails"]["videoId"] for i in pit
                   if (i.get("contentDetails") or {}).get("videoId")]
            if ids:
                vd = _yt("videos", {"part": "snippet,statistics", "id": ",".join(ids),
                                    "key": key}).get("items", [])
                for v in vd:
                    s = v.get("statistics", {}) or {}; sn = v.get("snippet", {}) or {}
                    vids.append({
                        "titre": (sn.get("title") or "")[:80], "plateforme": "YouTube",
                        "date": sn.get("publishedAt"), "lien": f"https://youtu.be/{v.get('id')}",
                        "likes": _i(s.get("likeCount")) or 0,
                        "commentaires": _i(s.get("commentCount")) or 0,
                        "partages": 0, "vues": _i(s.get("viewCount")) or 0, "type": "vidéo"})
        except Exception as e:
            print(f"  ⚠️ YouTube vidéos: {e}")
    yt["likes"] = sum(v["likes"] for v in vids) or None
    yt["commentaires"] = sum(v["commentaires"] for v in vids) or None
    data["top_posts"] = vids
    c = _calc_cadence([v.get("date") for v in vids])
    if c:
        data.setdefault("cadence_reseaux", {})["youtube"] = c
    cn = _calc_creneau([{"created_time": v.get("date"), "_eng": v["likes"] + v["commentaires"]}
                        for v in vids])
    if cn:
        data.setdefault("creneau_reseaux", {})["youtube"] = cn
    ydpost = max((v["date"] for v in vids if v.get("date")), default=None)  # dernière vidéo réelle
    data["youtube"] = {
        "abonnes": yt["abonnes"], "video_count": yt["posts"], "vues_totales": yt["vues"],
        "titre": (ch.get("snippet", {}) or {}).get("title"), "dernier_post": ydpost,
        "top_videos": sorted(vids, key=lambda x: x["vues"], reverse=True)[:8],
        "maj": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    data["_channel_id"] = ch.get("id")
    return data


def via_youtube_all():
    """Synchronise toutes les chaînes YouTube déclarées : un client.json avec yt_handle
    (ex. « @codescooper ») ou yt_channel_id. Fusionne dans reseaux.json (à côté de FB/TikTok)."""
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        sys.exit("❌ YOUTUBE_API_KEY requis (Secret/clé API Google).")
    motif = os.path.join(RACINE, "modules", "*", "clients", "*", "_donnees", "client.json")
    n = 0
    for cj in glob.glob(motif):
        try:
            c = json.load(open(cj, encoding="utf-8"))
        except Exception:
            continue
        handle, chid = c.get("yt_handle"), c.get("yt_channel_id")
        if not (handle or chid):
            continue
        client_dir = os.path.dirname(os.path.dirname(cj))
        try:
            data = _youtube_data(key, handle, chid)
        except Exception as e:
            print(f"  ⚠️ YouTube {c.get('id')}: {e}")
            continue
        if not data:
            print(f"  ⚠️ YouTube {c.get('id')}: chaîne introuvable ({handle or chid}).")
            continue
        cid = data.pop("_channel_id", None)
        if cid and not chid:                              # mémorise l'ID résolu pour la prochaine fois
            c["yt_channel_id"] = cid
            json.dump(c, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        _ecrire(client_dir, data)
        yt = data["par_reseau"]["youtube"]
        n += 1
        print(f"  ✓ YouTube {c.get('id')} ({yt['abonnes']} abonnés, {yt['posts']} vidéos, "
              f"{yt['vues']} vues)")
    print(f"✅ {n} chaîne(s) YouTube synchronisée(s). Régénère le registre : python3 outils/_data/build.py")


# --------------------------------------------------------------------------- #
# LINKEDIN — Pages entreprise (Community Management API)
# --------------------------------------------------------------------------- #
LI_API = "https://api.linkedin.com/rest"
LI_VERSION = os.environ.get("LINKEDIN_VERSION", "202401")


def _li_token():
    return (os.environ.get("LINKEDIN_TOKEN")
            or os.environ.get("LINKEDIN_ACCESS_TOKEN")
            or os.environ.get("LINKEDIN_TOKENS"))


def _li(path, token, params=None):
    """GET REST LinkedIn avec les en-têtes requis ; remonte le vrai message d'erreur."""
    url = f"{LI_API}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, safe=":(),%")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "LinkedIn-Version": LI_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        msg = body
        try:
            j = json.loads(body)
            msg = j.get("message") or j.get("error_description") or body
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} — {msg}") from None


def _li_vanity(url_or_slug):
    """Extrait le vanity name (slug) d'une URL LinkedIn /company/<slug> (ou renvoie tel quel)."""
    if not url_or_slug:
        return None
    m = re.search(r"/company/([^/?#]+)", url_or_slug)
    slug = (m.group(1) if m else url_or_slug).strip().strip("/")
    return slug or None


def _linkedin_org_id(token, slug):
    """Résout l'ID numérique de l'organisation à partir de son vanity name."""
    res = _li("organizations", token, {"q": "vanityName", "vanityName": slug})
    els = res.get("elements") or []
    if not els:
        return None
    return els[0].get("id")


def _linkedin_data(token, slug, org_id):
    """Stats d'une Page entreprise : abonnés (networkSizes) + impressions/engagement
    (organizationalEntityShareStatistics). Renvoie un dict façon _vide() + objet linkedin."""
    if not org_id:
        org_id = _linkedin_org_id(token, slug)
    if not org_id:
        return None
    urn = f"urn:li:organization:{org_id}"
    data = _vide(); data["source"] = "linkedin-rest-api"
    lk = data["par_reseau"]["linkedin"]

    # Abonnés
    try:
        ns = _li(f"networkSizes/{urllib.parse.quote(urn, safe='')}", token,
                 {"edgeType": "COMPANY_FOLLOWED_BY_MEMBER"})
        lk["abonnes"] = ns.get("firstDegreeSize")
    except Exception as e:
        print(f"  ⚠️ LinkedIn abonnés: {e}")

    # Statistiques de partage (impressions, clics, likes, commentaires, partages, engagement)
    impressions = engagement = None
    try:
        ss = _li("organizationalEntityShareStatistics", token,
                 {"q": "organizationalEntity", "organizationalEntity": urn})
        els = ss.get("elements") or []
        tot = (els[0].get("totalShareStatistics") if els else {}) or {}
        impressions = tot.get("impressionCount")
        lk["likes"] = tot.get("likeCount")
        lk["commentaires"] = tot.get("commentCount")
        lk["partages"] = tot.get("shareCount")
        lk["vues"] = impressions                      # impressions ≈ vues
        engagement = tot.get("engagement")
    except Exception as e:
        print(f"  ⚠️ LinkedIn statistiques: {e}")

    # Titre de la Page (best effort)
    titre = None
    try:
        info = _li(f"organizations/{org_id}", token, {"projection": "(id,localizedName,vanityName)"})
        titre = info.get("localizedName")
    except Exception:
        pass

    if engagement is not None:
        eng_pct = round(engagement * 100, 1)
    elif impressions:
        inter = (lk.get("likes") or 0) + (lk.get("commentaires") or 0) + (lk.get("partages") or 0)
        eng_pct = round(inter / impressions * 100, 1) if impressions else None
    else:
        eng_pct = None

    data["linkedin"] = {
        "abonnes": lk["abonnes"], "impressions": impressions,
        "posts": lk.get("posts"), "engagement_taux": eng_pct,
        "titre": titre or slug, "vanity": slug,
        "maj": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    data["_org_id"] = org_id
    return data


def via_linkedin_all():
    """Synchronise toutes les Pages LinkedIn déclarées : un client.json avec un lien
    reseaux.linkedin (/company/<slug>), un champ linkedin_vanity, ou linkedin_org_id.
    Fusionne dans reseaux.json (à côté de FB/TikTok/YouTube)."""
    token = _li_token()
    if not token:
        sys.exit("❌ LINKEDIN_TOKEN requis (access token OAuth, scopes r_organization_social / rw_organization_admin).")
    motif = os.path.join(RACINE, "modules", "*", "clients", "*", "_donnees", "client.json")
    n = 0
    for cj in glob.glob(motif):
        try:
            c = json.load(open(cj, encoding="utf-8"))
        except Exception:
            continue
        org_id = c.get("linkedin_org_id")
        slug = c.get("linkedin_vanity") or _li_vanity((c.get("reseaux") or {}).get("linkedin"))
        if not (org_id or slug):
            continue
        client_dir = os.path.dirname(os.path.dirname(cj))
        try:
            data = _linkedin_data(token, slug, org_id)
        except Exception as e:
            print(f"  ⚠️ LinkedIn {c.get('id')}: {e}")
            continue
        if not data:
            print(f"  ⚠️ LinkedIn {c.get('id')}: organisation introuvable ({slug or org_id}).")
            continue
        oid = data.pop("_org_id", None)
        if oid and not org_id:                            # mémorise l'ID résolu
            c["linkedin_org_id"] = oid
            if slug and not c.get("linkedin_vanity"):
                c["linkedin_vanity"] = slug
            json.dump(c, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        _ecrire(client_dir, data)
        lk = data["par_reseau"]["linkedin"]
        n += 1
        print(f"  ✓ LinkedIn {c.get('id')} ({lk['abonnes']} abonnés, "
              f"{(data['linkedin'] or {}).get('impressions')} impressions)")
    print(f"✅ {n} Page(s) LinkedIn synchronisée(s). Régénère le registre : python3 outils/_data/build.py")


def main():
    a = sys.argv[1:]
    if a and a[0] == "--meta-all":
        via_meta_all()
    elif a and a[0] == "--tiktok-all":
        via_tiktok_all()
    elif a and a[0] == "--youtube-all":
        via_youtube_all()
    elif a and a[0] == "--linkedin-all":
        via_linkedin_all()
    elif len(a) >= 2 and a[0] == "--tiktok-auth":
        via_tiktok_auth(a[1], a[2] if len(a) >= 3 else None)
    elif len(a) >= 2 and a[0] == "--meta":
        via_meta(a[1])
    elif len(a) >= 3 and a[0] == "--manuel":
        via_manuel(a[1], a[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
