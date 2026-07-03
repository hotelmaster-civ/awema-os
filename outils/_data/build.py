#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit le registre multi-clients de l'agence pour les outils web.

Scanne modules/<dept>/clients/<client>/_donnees/ et agrège, par client :
  - client.json   (profil + réseaux + chemins)   [requis pour être listé]
  - campagne.json (les contenus du plan)          [optionnel]
  - reseaux.json  (présence digitale, réelle)     [optionnel]

Sortie : outils/_data/agence.js  →  window.AWEMA_REGISTRY = { genere, clients:[...] }
Aucune donnée fictive : ce qui n'existe pas reste null/[].

Poids du registre : les `contenus` d'une campagne ne sont EMBARQUÉS que si campagne.json reste
raisonnable (≤ SEUIL_CAMPAGNE). Au-delà, le registre porte {"total", "differe": true} et les pages
consommatrices (dashboard, revue-visuels) chargent le campagne.json source à la demande — il est
déjà servi par GitHub Pages. Sans ça, UN client à grosse campagne (ex. 670 Ko) faisait exploser le
registre téléchargé par toutes les pages.

Usage : python3 build.py
"""
import glob
import json
import os

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, "..", ".."))
SEUIL_CAMPAGNE = 64_000  # octets : au-delà, les contenus ne sont plus embarqués dans le registre


def lire(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def main():
    clients = []
    motif = os.path.join(RACINE, "modules", "*", "clients", "*", "_donnees", "client.json")
    for cj in sorted(glob.glob(motif)):
        donnees = os.path.dirname(cj)                 # .../_donnees
        client = lire(cj) or {}
        camp_path = os.path.join(donnees, "campagne.json")
        campagne = lire(camp_path)
        camp_lourde = campagne is not None and os.path.getsize(camp_path) > SEUIL_CAMPAGNE
        reseaux = lire(os.path.join(donnees, "reseaux.json"))
        memoire = lire(os.path.join(donnees, "memoire.json"))   # Mémoire Marketing (M1)
        client_dir = os.path.dirname(donnees)         # .../<client>
        rel = os.path.relpath(client_dir, RACINE).replace(os.sep, "/")
        # Sorties des agents IA (additives) : _donnees/_agents/<agent>.json
        agents = {}
        for aj in sorted(glob.glob(os.path.join(donnees, "_agents", "*.json"))):
            a = lire(aj)
            if a:
                agents[os.path.splitext(os.path.basename(aj))[0]] = a
        # Statuts de revue des visuels (axe PRODUCTION) — écrits par le visualiseur
        # dans _donnees/retours-visuels.json via l'API GitHub. Map compacte {id: statut}.
        retours = lire(os.path.join(donnees, "retours-visuels.json"))
        revue = None
        if retours and isinstance(retours.get("retours"), list):
            revue = {str(r["id"]): r["statut"] for r in retours["retours"]
                     if r.get("id") is not None and r.get("statut")
                     and r["statut"] != "À produire"} or None
        # File d'attente de publication (ADR-010) : _donnees/_planning/<id>.json
        planning = []
        for pj in sorted(glob.glob(os.path.join(donnees, "_planning", "*.json"))):
            if os.path.basename(pj) == "index.json":
                continue
            p = lire(pj)
            if p:
                planning.append(p)
        clients.append({
            **client,
            "_dir": rel,
            "profils": client.get("reseaux", {}),          # handles (depuis client.json)
            "campagne": (
                {"total": (campagne or {}).get("total", 0), "differe": True} if camp_lourde
                else {"total": (campagne or {}).get("total", 0),
                      "contenus": (campagne or {}).get("contenus", [])}
            ) if campagne else None,
            "reseaux": reseaux,                             # métriques (depuis reseaux.json) ou null
            "memoire": memoire,                             # Mémoire Marketing (depuis memoire.json) ou null
            "agents": agents or None,                       # sorties IA (depuis _agents/) ou null
            "planning": planning or None,                   # file de publication (depuis _planning/) ou null
            "revue": revue,                                 # statuts de revue des visuels {id: statut} ou null
        })

    lic = lire(os.path.join(RACINE, "config", "licence.json")) or {}
    # Registre DÉTERMINISTE : pas d'horodatage de build (évite le bruit git ; la fraîcheur réelle
    # vient des champs `maj` de chaque reseaux.json). Le registre ne change que si une donnée change.
    registre = {"licence": {"statut": lic.get("statut", "non-active"), "agence": lic.get("agence", "")},
                "clients": clients}
    out = os.path.join(ICI, "agence.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("// Généré par outils/_data/build.py — ne pas éditer.\n")
        f.write("window.AWEMA_REGISTRY = ")
        json.dump(registre, f, ensure_ascii=False)
        f.write(";\n")

    # Config de l'agence (personnalisation auto-hébergée) → config.js pour tous les outils
    cfg = lire(os.path.join(RACINE, "config", "agence.json")) or {}
    cfg.pop("_doc", None)
    with open(os.path.join(ICI, "config.js"), "w", encoding="utf-8") as f:
        f.write("// Généré par build.py depuis config/agence.json — édite le JSON, pas ce fichier.\n")
        f.write("window.AWEMA_CONFIG = ")
        json.dump(cfg, f, ensure_ascii=False)
        f.write(";\n")

    # Registre des fournisseurs d'IA → ia-providers.js (pour le guide connect-ia.html)
    ia = lire(os.path.join(RACINE, "config", "ia-providers.json")) or {}
    ia.pop("_doc", None)
    with open(os.path.join(ICI, "ia-providers.js"), "w", encoding="utf-8") as f:
        f.write("// Généré par build.py depuis config/ia-providers.json — édite le JSON, pas ce fichier.\n")
        f.write("window.AWEMA_IA_PROVIDERS = ")
        json.dump(ia, f, ensure_ascii=False)
        f.write(";\n")
    noms = ", ".join(c.get("nom", c.get("id", "?")) for c in clients) or "(aucun)"
    print(f"✅ agence.js — {len(clients)} client(s) : {noms}")
    for c in clients:
        n = (c.get("campagne") or {}).get("total", 0)
        rc = "réseaux connectés" if (c.get("reseaux") or {}).get("connecte") else "réseaux à connecter"
        print(f"   • {c.get('nom')} — {n} contenus — {rc}")


if __name__ == "__main__":
    main()
