#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AWEMA · Réinitialisation du projet EN PLACE — vide le dépôt de toute donnée client.

Idéal après un fork, ou pour tout recommencer sur une base neuve. Opération
DESTRUCTRICE : elle supprime des fichiers du dépôt courant, puis régénère le
registre. Elle est donc protégée par une double garde :
  • AWEMA_RESET_CONFIRM doit valoir exactement « REINITIALISER » ;
  • déclenchée uniquement par le workflow reset-projet.yml (dispatch manuel).

Elle ne touche JAMAIS aux secrets/tokens (ils vivent dans GitHub Secrets, pas
dans le dépôt) ni à l'historique git (les anciennes données restent dans les
commits passés — c'est un nouveau départ, pas une réécriture d'historique).

Portées (AWEMA_RESET_PORTEE) :
  • client  (défaut) : supprime tous les clients réels et leurs données
                       (campagnes, réseaux, planning, mémoire, agents, retours),
                       ré-installe le client de DÉMO, vide les alias, régénère le
                       registre. GARDE l'identité de l'agence (config, charte, licence).
  • complet          : en plus, remet l'identité de l'agence à neutre (config,
                       licence non-active, README) — repart totalement à zéro.

Usage (local, sur une COPIE de test) :
  AWEMA_RESET_CONFIRM=REINITIALISER AWEMA_RESET_PORTEE=client python3 scripts/reinitialiser.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
CONFIRM_ATTENDU = "REINITIALISER"


def _charger_neutraliser():
    """Réutilise la neutralisation éprouvée de preparer-copie-beta.py (nom à tiret →
    chargement par chemin). Évite toute dérive entre « copie template » et « reset complet »."""
    chemin = os.path.join(ICI, "preparer-copie-beta.py")
    spec = importlib.util.spec_from_file_location("prep_beta", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _reseed_demo(clients_dir):
    """(Ré)installe le client de DÉMO depuis scripts/_demo (ou un repli minimal)."""
    demo = os.path.join(clients_dir, "demo-client", "_donnees")
    src = os.path.join(ICI, "_demo")
    if os.path.isdir(src):
        shutil.copytree(src, demo)
    else:
        os.makedirs(demo, exist_ok=True)
        json.dump({"id": "demo-client", "nom": "Client Démo", "statut": "demo",
                   "module": "marketing", "initiales": "CD"},
                  open(os.path.join(demo, "client.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)


def reset_donnees_client():
    """Supprime tous les clients réels + données mono-client générées ; ré-installe la démo ;
    vide les alias de slugs. Retourne la liste des slugs supprimés."""
    clients_dir = os.path.join(RACINE, "modules", "marketing", "clients")
    supprimes = []
    if os.path.isdir(clients_dir):
        for d in sorted(os.listdir(clients_dir)):
            p = os.path.join(clients_dir, d)
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)
                supprimes.append(d)
    os.makedirs(clients_dir, exist_ok=True)
    _reseed_demo(clients_dir)

    # Fichiers de données mono-client générés (fuite potentielle de vraies données)
    for f in ("outils/dashboard/data.js", "outils/revue-visuels/data.js"):
        fp = os.path.join(RACINE, f)
        if os.path.exists(fp):
            os.remove(fp)

    # Alias de slugs (rattachements à TES comptes) → vidés
    al = os.path.join(RACINE, "config", "aliases.json")
    if os.path.exists(al):
        try:
            a = json.load(open(al, encoding="utf-8"))
            for k in [k for k in a if k != "_doc" and isinstance(a[k], dict)]:
                a[k] = {}
            json.dump(a, open(al, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        except Exception:
            pass
    return supprimes


def main():
    confirm = (os.environ.get("AWEMA_RESET_CONFIRM") or "").strip()
    portee = (os.environ.get("AWEMA_RESET_PORTEE") or "client").strip().lower()
    if confirm != CONFIRM_ATTENDU:
        sys.exit("❌ Réinitialisation refusée : confirmation manquante ou invalide "
                 "(AWEMA_RESET_CONFIRM doit valoir « %s »)." % CONFIRM_ATTENDU)
    if portee not in ("client", "complet"):
        sys.exit("❌ Portée inconnue : « %s » (attendu : client | complet)." % portee)

    if portee == "complet":
        # Remise à neutre TOTALE : réutilise neutraliser() (clients + config + licence + README
        # + registres). Opère sur le dépôt courant.
        prep = _charger_neutraliser()
        prep.neutraliser(RACINE)
        print("✅ Réinitialisation COMPLÈTE effectuée (identité de l'agence remise à neutre).")
    else:
        supprimes = reset_donnees_client()
        print("→ Régénération du registre (build.py)…")
        subprocess.call([sys.executable, os.path.join(RACINE, "outils", "_data", "build.py")],
                        cwd=RACINE)
        print("✅ Données client réinitialisées : %d client(s) supprimé(s) %s· démo ré-installée."
              % (len(supprimes), ("(" + ", ".join(supprimes) + ") ") if supprimes else ""))
    print("ℹ️  Les secrets/tokens GitHub n'ont pas été touchés. L'historique git conserve "
          "les anciennes données (nouveau départ, pas de réécriture).")


if __name__ == "__main__":
    main()
