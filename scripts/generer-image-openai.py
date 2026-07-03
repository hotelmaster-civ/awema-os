#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère une image depuis un prompt via l'API OpenAI Images (gpt-image-1) et l'enregistre.

Voie « 100 % automatique » de la chaîne de production visuelle (voir
outils/revue-visuels/INTEGRATION-GENERATION-IMAGE.md). Nécessite une clé API OpenAI
(≠ abonnement ChatGPT) : export OPENAI_API_KEY="sk-...".

Aucune dépendance externe : utilise l'API HTTP via urllib.

USAGE
-----
1) Une image depuis un prompt :
   python3 scripts/generer-image-openai.py "<prompt>" chemin/sortie.png [--size 1024x1536]

2) En lot depuis le campagne.json (génère les visuels manquants) :
   python3 scripts/generer-image-openai.py --batch \
       modules/marketing/clients/mon-client/_donnees/campagne.json \
       modules/marketing/clients/mon-client/_visuels-recus \
       [--n 10] [--champ prompt_gpt]

Tailles supportées par gpt-image-1 : 1024x1024, 1024x1536 (portrait), 1536x1024 (paysage).
Le format des réseaux (4:5, 9:16, 1:1) est approximé par la taille la plus proche.
"""
import base64
import json
import os
import sys
import urllib.request

API_URL = "https://api.openai.com/v1/images/generations"
MODEL = "gpt-image-1"

# Ratio cible (depuis la fiche) -> taille gpt-image-1 la plus proche
RATIO_TO_SIZE = {
    "9:16": "1024x1536", "4:5": "1024x1536", "3:4": "1024x1536",
    "1:1": "1024x1024",
    "16:9": "1536x1024", "1.91:1": "1536x1024",
}


def generer(prompt, sortie, size="1024x1536"):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("❌ OPENAI_API_KEY non définie. export OPENAI_API_KEY=\"sk-...\"")
    body = json.dumps({"model": MODEL, "prompt": prompt, "size": size, "n": 1}).encode()
    req = urllib.request.Request(
        API_URL, data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    b64 = data["data"][0]["b64_json"]
    os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
    with open(sortie, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"✅ {sortie}")
    return sortie


def lot(campagne, dossier, n=None, champ="prompt_gpt"):
    with open(campagne, encoding="utf-8") as f:
        items = json.load(f)["contenus"]
    os.makedirs(dossier, exist_ok=True)
    faits = 0
    for c in items:
        nom = f"{c['id']:03d}.png"
        out = os.path.join(dossier, nom)
        if os.path.exists(out):
            continue
        size = RATIO_TO_SIZE.get(c.get("ratio", "4:5"), "1024x1536")
        print(f"#{c['id']:03d} {c.get('plateforme','')} ({size})…")
        generer(c[champ], out, size)
        faits += 1
        if n and faits >= n:
            break
    print(f"Terminé : {faits} image(s) générée(s) dans {dossier}")


def main():
    a = sys.argv[1:]
    if a and a[0] == "--batch":
        camp, dossier = a[1], a[2]
        n = int(a[a.index("--n") + 1]) if "--n" in a else None
        champ = a[a.index("--champ") + 1] if "--champ" in a else "prompt_gpt"
        lot(camp, dossier, n, champ)
        return
    if len(a) < 2:
        sys.exit(__doc__)
    prompt, sortie = a[0], a[1]
    size = a[a.index("--size") + 1] if "--size" in a else "1024x1536"
    generer(prompt, sortie, size)


if __name__ == "__main__":
    main()
