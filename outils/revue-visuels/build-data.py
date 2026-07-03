#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Transforme un campagne.json en data.js pour l'outil de revue.

Permet d'ouvrir index.html en double-clic (file://) sans serveur : data.js
définit window.CAMPAGNE, que l'application charge automatiquement.

Usage :
  python3 build-data.py <chemin/vers/campagne.json>
  # défaut : la campagne La Grande Vision
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))


def _defaut():
    import glob
    hits = sorted(glob.glob(os.path.join(ICI, "..", "..", "modules", "*", "clients", "*",
                                          "_donnees", "campagne.json")))
    if not hits:
        sys.exit("Usage: python3 build-data.py <chemin/campagne.json> (aucune campagne trouvée)")
    return hits[0]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else _defaut()
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    out = os.path.join(ICI, "data.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("// Généré par build-data.py — ne pas éditer à la main.\n")
        f.write("window.CAMPAGNE = ")
        json.dump(data, f, ensure_ascii=False)
        f.write(";\n")
    print(f"✅ data.js écrit ({data.get('total', '?')} contenus) depuis :\n   {src}")


if __name__ == "__main__":
    main()
