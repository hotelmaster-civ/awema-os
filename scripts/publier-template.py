#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publie / régénère la branche TEMPLATE PUBLIC (`main`) à partir de l'opérationnel.

Principe (cf. docs/13-securite-donnees.md) :
  • le template public PUISE les FONCTIONNALITÉS (code, docs, outils, pages, workflows) ;
  • il ne PUISE JAMAIS les contenus clients NI la liste des clients ;
  • il reste VIERGE de toute donnée, sauf le client de DÉMO (`demo-client`).

Le tri propre-vs-data est fait par `preparer-copie-beta.neutraliser()` (source unique
de vérité de la neutralisation). Ce script applique cette neutralisation à une COPIE de
l'arbre opérationnel courant, puis met à jour la branche `main` :

  python3 scripts/publier-template.py            # DRY-RUN : montre ce que `main` deviendrait
  python3 scripts/publier-template.py --push     # publie réellement (commit + push origin main)

N'altère JAMAIS la branche opérationnelle ni ses données (tout passe par un worktree jetable).
"""
import os
import shutil
import subprocess
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
BRANCHE_PUBLIQUE = "main"

sys.path.insert(0, ICI)
import importlib
_pcb = importlib.import_module("preparer-copie-beta")  # tiret dans le nom → import dynamique


def git(*args, cwd=RACINE, check=True, capture=False):
    r = subprocess.run(["git", *args], cwd=cwd, check=check,
                       text=True, capture_output=capture)
    return (r.stdout or "").strip() if capture else r


def main():
    push = "--push" in sys.argv[1:]

    branche_op = git("rev-parse", "--abbrev-ref", "HEAD", capture=True)
    if branche_op == BRANCHE_PUBLIQUE:
        sys.exit(f"❌ Tu es sur « {BRANCHE_PUBLIQUE} ». Lance ce script depuis la branche "
                 "opérationnelle (privée).")

    print(f"→ Branche opérationnelle : {branche_op}")
    print(f"→ Branche publique cible : {BRANCHE_PUBLIQUE}")
    git("fetch", "origin", BRANCHE_PUBLIQUE, check=False)

    # 1) Copie l'arbre opérationnel courant (sans .git/.awema/etc.) puis NEUTRALISE
    propre = tempfile.mkdtemp(prefix="awema-template-")
    cible = os.path.join(propre, "tree")
    print(f"→ Copie de l'arbre opérationnel → {cible}")
    shutil.copytree(RACINE, cible, ignore=_pcb.IGNORE)
    print("→ Neutralisation (purge data, démo seule, licence/alias vides, registres régénérés)…")
    _pcb.neutraliser(cible)

    # 2) Worktree jetable sur la branche publique (basée sur origin/main)
    wt = os.path.join(propre, "wt-main")
    existe_local = git("rev-parse", "--verify", "--quiet", BRANCHE_PUBLIQUE,
                      check=False, capture=True)
    base = f"origin/{BRANCHE_PUBLIQUE}"
    if existe_local:
        git("worktree", "add", "--force", wt, BRANCHE_PUBLIQUE)
        git("reset", "--hard", base, cwd=wt, check=False)
    else:
        git("worktree", "add", "--force", "-b", BRANCHE_PUBLIQUE, wt, base)

    try:
        # 3) Remplace le contenu du worktree par l'arbre propre (préserve son .git)
        for nom in os.listdir(wt):
            if nom == ".git":
                continue
            p = os.path.join(wt, nom)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        for nom in os.listdir(cible):
            s, d = os.path.join(cible, nom), os.path.join(wt, nom)
            shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)

        git("add", "-A", cwd=wt)
        stat = git("diff", "--cached", "--stat", cwd=wt, capture=True)

        # 3bis) GARDE-FOU : aucun client réel ne doit apparaître dans l'index
        suivis = git("diff", "--cached", "--name-only", cwd=wt, capture=True).splitlines()
        fuite = [f for f in suivis
                 if f.startswith("modules/marketing/clients/")
                 and not f.startswith("modules/marketing/clients/demo-client/")]
        if fuite:
            sys.exit("🚨 FUITE DÉTECTÉE — des données client non-démo seraient publiées :\n  "
                     + "\n  ".join(fuite[:20]) + "\nPublication ANNULÉE.")

        if not stat:
            print("\n✅ `main` est déjà à jour — aucun changement à publier.")
            return

        print("\n=== CE QUE `main` DEVIENDRAIT ===\n" + stat)
        print("\n🔒 Garde-fou OK : seul `demo-client` est présent côté clients.")

        if not push:
            print("\nℹ️  DRY-RUN — rien n'a été poussé. Relance avec --push pour publier.")
            return

        git("commit", "-m",
            "chore(template): synchronise les fonctionnalités (données neutralisées)",
            cwd=wt)
        git("push", "origin", BRANCHE_PUBLIQUE, cwd=wt)
        print("\n🚀 Publié : origin/" + BRANCHE_PUBLIQUE + " mis à jour (features à jour, data vierge).")
    finally:
        git("worktree", "remove", "--force", wt, check=False)
        shutil.rmtree(propre, ignore_errors=True)


if __name__ == "__main__":
    main()
