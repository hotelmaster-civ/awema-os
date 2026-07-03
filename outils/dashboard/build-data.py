#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère outils/dashboard/data.js (window.CAMPAGNE) depuis campagne.json.
Usage: python3 build-data.py [chemin/campagne.json]"""
import json, os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
def _defaut():
    import glob
    hits = sorted(glob.glob(os.path.join(ICI, "..", "..", "modules", "*", "clients", "*",
                                          "_donnees", "campagne.json")))
    if not hits:
        sys.exit("Usage: python3 build-data.py <chemin/campagne.json> (aucune campagne trouvée)")
    return hits[0]
src = sys.argv[1] if len(sys.argv) > 1 else _defaut()
with open(src, encoding="utf-8") as f:
    data = json.load(f)
with open(os.path.join(ICI, "data.js"), "w", encoding="utf-8") as f:
    f.write("// Généré par build-data.py — ne pas éditer.\nwindow.CAMPAGNE = ")
    json.dump(data, f, ensure_ascii=False)
    f.write(";\n")
print(f"✅ data.js écrit ({data.get('total','?')} contenus) depuis {src}")
