#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prépare une COPIE D'ACCUEIL propre du dépôt pour les beta testeurs (Programme 20 CM).

Produit un dossier autonome, identique au projet MAIS :
  • sans les données réelles des clients de l'agence (RGPD + confidentialité) ;
  • avec UN client de démo neutre (le dashboard n'est pas vide) ;
  • avec une config d'agence neutre à personnaliser ;
  • registres régénérés (agence.js / config.js).

N'altère JAMAIS le dépôt courant : tout est écrit dans le dossier cible.

Usage :
  python3 scripts/preparer-copie-beta.py ../awema-beta
Puis : pousser ce dossier dans un NOUVEAU dépôt GitHub et le marquer « Template repository »
(Settings → Template repository) pour que chaque CM fasse « Use this template ».
"""
import json
import os
import re
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

IGNORE = shutil.ignore_patterns(
    ".git", ".awema", "__pycache__", "*.pyc", "tiktok_tokens.out", "scratchpad",
    "node_modules", ".DS_Store")

CONFIG_TEMPLATE = {
    "_doc": "Configuration de TON agence. Personnalise via setup.html ou `awema setup`, "
            "puis : python3 outils/_data/build.py.",
    "nom": "Mon Agence", "nom_complet": "Mon Agence — présence en ligne",
    "tagline": "Centre de pilotage",
    "slogan": "La présence en ligne de mes clients, pilotée.",
    "initiales": "MA", "langue": "fr", "contact": "ton-email@exemple.com",
    "github": {"owner": "ton-pseudo", "repo": "mon-agence"},
    "charte": {"nuit": "#0A1F44", "ciel": "#4BA3FF", "gold": "#D4AF37",
               "violet": "#7C5CFF", "mint": "#34E5C4", "pink": "#FF7D9C"},
}

DEMO_CLIENT = {
    "id": "demo-client", "nom": "Client Démo", "secteur": "Exemple",
    "lieu": "—", "module": "marketing", "statut": "actif", "initiales": "CD",
    "reseaux": {"facebook": "", "instagram": "", "tiktok": "", "linkedin": "",
                "whatsapp": "", "youtube": ""},
    "chemins": {"campagne": "_donnees/campagne.json", "reseaux": "_donnees/reseaux.json",
                "revue": "../../../../outils/revue-visuels/index.html?client=demo-client"},
}


def neutraliser(cible):
    """Transforme une COPIE du projet (dossier `cible`) en template public VIERGE.

    Aucune donnée réelle ne subsiste : un seul client de DÉMO, config/licence/alias
    neutres, docs internes retirés, README sans liste de clients, registres régénérés.
    Réutilisable : `preparer-copie-beta.py` (nouveau dépôt) ET `publier-template.py`
    (régénère la branche `main`). N'altère JAMAIS le dépôt courant.
    """
    # 1) Purge des clients réels → un seul client de DÉMO riche (effet « wow » immédiat,
    #    clairement étiqueté exemple, isolé des vraies données — cf. M6)
    clients_dir = os.path.join(cible, "modules", "marketing", "clients")
    if os.path.isdir(clients_dir):
        for d in os.listdir(clients_dir):
            shutil.rmtree(os.path.join(clients_dir, d), ignore_errors=True)
    demo = os.path.join(clients_dir, "demo-client", "_donnees")
    demo_src = os.path.join(cible, "scripts", "_demo")
    if os.path.isdir(demo_src):
        shutil.copytree(demo_src, demo)            # client.json + memoire + reseaux + _agents/*
    else:                                          # repli minimal si _demo absent
        os.makedirs(demo, exist_ok=True)
        json.dump(DEMO_CLIENT, open(os.path.join(demo, "client.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)

    # 2) Config d'agence neutre
    json.dump(CONFIG_TEMPLATE, open(os.path.join(cible, "config", "agence.json"), "w",
              encoding="utf-8"), ensure_ascii=False, indent=2)

    # 2-0) Retire les fichiers de données mono-client générés (fuite potentielle de vraies données)
    for f in ("outils/dashboard/data.js", "outils/revue-visuels/data.js"):
        fp = os.path.join(cible, f)
        if os.path.exists(fp):
            os.remove(fp)

    # 2-0bis) Retire les documents INTERNES (journal de dev, auto-descriptions citant des
    #         données/clients réels — ne doivent pas partir dans les forks d'agences)
    for f in ("docs/AWEMA-OS.md", "docs/AUTO-DESCRIPTION.md", "PROJECT_SELF_DESCRIPTION.md",
              "docs/JOURNAL-SESSIONS.md"):
        fp = os.path.join(cible, f)
        if os.path.exists(fp):
            os.remove(fp)

    # 2-0bis+) 00-INDEX.md : c'est un index d'ADMIN (licence, places bêta, état interne) et il
    #          référence des notes qu'on vient de supprimer. On le remplace par un index PUBLIC
    #          minimal pour les agences (pointe vers la doc utile, sans bloc admin ni liens cassés).
    idx = os.path.join(cible, "docs", "00-INDEX.md")
    if os.path.exists(idx):
        open(idx, "w", encoding="utf-8").write(
            "---\ntitre: 🏠 AWEMA — Index de la documentation\ntags: [awema, index]\n---\n\n"
            "# 🏠 AWEMA — Index de la documentation\n\n"
            "> Bienvenue dans **ton** instance AWEMA. Point d'entrée de la doc.\n\n"
            "## 🚀 Démarrer\n"
            "- [[TUTORIEL-AGENCE]] — installation pas à pas (fork → AWEMA qui tourne, sans commande)\n"
            "- [[17-mise-en-route-complete]] — configurer clés/réseaux à 100 %\n"
            "- [[RECETTE-MANUELLE]] — vérifier que tout marche, de bout en bout\n\n"
            "## 🏛️ Références stables\n"
            "- [[FOUNDATION/README]] — Constitution, Kernel/Module, principes, agents, ADR\n"
            "- [[PRD-AWEMA]] — référence produit · [[ROADMAP]] — feuille de route\n"
            "- [[04-charte-graphique]] — charte · [[03-conventions]] — conventions\n\n"
            "## 🔌 Connecter & sécurité\n"
            "- [[05-connecter-reseaux]] · [[07-connecter-tiktok]] · [[10-connecter-linkedin]]\n"
            "- [[13-securite-donnees]] — données & confidentialité · [[18-sauvegarde-continuite]]\n")

    # 2-0quater) Modèle d'issues GitHub : retire les liens spécifiques à l'amont (email perso,
    #            programme bêta) → version neutre pointant vers la doc locale du fork.
    ic = os.path.join(cible, ".github", "ISSUE_TEMPLATE", "config.yml")
    if os.path.exists(ic):
        open(ic, "w", encoding="utf-8").write(
            "blank_issues_enabled: true\n"
            "contact_links:\n"
            "  - name: 📖 Guide d'installation (pas à pas)\n"
            "    url: https://github.com/\n"
            "    about: Ouvre docs/TUTORIEL-AGENCE.md dans ton dépôt pour configurer ton instance.\n")

    # 2-0ter) Vide les alias de slugs (rattachements spécifiques à TES comptes)
    al = os.path.join(cible, "config", "aliases.json")
    if os.path.exists(al):
        try:
            a = json.load(open(al, encoding="utf-8"))
            for k in [k for k in a if k != "_doc" and isinstance(a[k], dict)]:
                a[k] = {}
            json.dump(a, open(al, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        except Exception:
            pass

    # 2a) Licence remise à NON-ACTIVE : le pilote doit l'activer auprès d'AWEMA
    lic_path = os.path.join(cible, "config", "licence.json")
    if os.path.exists(lic_path):
        try:
            lic = json.load(open(lic_path, encoding="utf-8"))
            lic.update({"agence": "", "cle": "", "statut": "non-active"})
            json.dump(lic, open(lic_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        except Exception:
            pass

    # 2b) Neutralise le README du département (retire la liste des clients réels)
    rdm = os.path.join(cible, "modules", "marketing", "README.md")
    if os.path.exists(rdm):
        lignes, garde = open(rdm, encoding="utf-8").read().splitlines(), []
        for ln in lignes:
            low = ln.lower()
            if ln.startswith("| [") or (ln.startswith("## ") and "client" in low):
                break  # coupe avant la table/section des clients réels
            garde.append(ln)
        garde += ["", "## Clients", "",
                  "_Aucun client pour l'instant — ajoute le tien via `nouveau-client.html`._", ""]
        open(rdm, "w", encoding="utf-8").write("\n".join(garde))

    # 3) Suivi des places remis à zéro (aucune donnée perso ne fuit dans la copie)
    seats = os.path.join(cible, "config", "beta-seats.json")
    if os.path.exists(seats):
        try:
            s = json.load(open(seats, encoding="utf-8"))
            for p in s.get("places", []):
                p.update({"statut": "libre", "membre": "", "handle": "", "contact": "",
                          "fork": "", "rejoint_le": "", "dernier_retour": "", "notes": ""})
            s["liste_attente"] = []
            json.dump(s, open(seats, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        except Exception:
            pass

    # 3b) Généralise le .gitignore : ignore les visuels reçus de TOUS les clients
    #     (et plus seulement un client codé en dur → évite de versionner des visuels réels)
    gi = os.path.join(cible, ".gitignore")
    if os.path.exists(gi):
        lignes = open(gi, encoding="utf-8").read().splitlines()
        out, vus = [], set()
        for ln in lignes:
            # Généralise TOUT chemin client codé en dur (quel que soit le slug)
            g = re.sub(r"(modules/[^/\s]+/clients/)[^/\s*]+/", r"\1*/", ln)
            if g.strip().startswith("modules/marketing/clients/"):
                if g in vus:
                    continue
                vus.add(g)
            out.append(g)
        open(gi, "w", encoding="utf-8").write("\n".join(out) + "\n")

    # 4) Régénère les registres dans la copie
    print("→ Régénération des registres (build.py)…")
    subprocess.call([sys.executable, os.path.join(cible, "outils", "_data", "build.py")], cwd=cible)
    print("⚠️  À personnaliser (prose, non scrubable automatiquement) : docs/01-agence.md et "
          "docs/04-charte-graphique.md décrivent encore TON agence/exemple — remplace-les par les tiens.")


UP_OWNER = "codescooper"
UP_REPO = "AwemA---Agence-Web-Marketing-Africaine"


def repointer_upstream(cible, owner, repo):
    """Repointe l'identité du dépôt CANONIQUE (« upstream ») dans la copie : de
    codescooper/AwemA---… vers owner/repo. Indispensable quand la copie devient un
    NOUVEAU dépôt public de référence (ex. awema-test/awema-os) : sans ça, le bouton
    « Créer ma copie », la détection de fork et les liens docs pointeraient encore vers
    le dépôt d'origine, et les participants forkeraient le mauvais dépôt.

    Ne touche PAS la mention de copyright de l'auteur (AGPL : on conserve l'attribution).
    """
    remps = [
        ("%s.github.io/%s" % (UP_OWNER, UP_REPO), "%s.github.io/%s" % (owner, repo)),  # Pages
        ("%s/%s" % (UP_OWNER, UP_REPO), "%s/%s" % (owner, repo)),                       # chemin repo
        ("'%s'" % UP_REPO, "'%s'" % repo),      # littéraux JS (UP_REPO / dR / fallbacks)
        ("'%s'" % UP_OWNER, "'%s'" % owner),    # littéraux JS (UP_OWNER / dO / fallbacks)
    ]
    exts = (".js", ".html", ".md", ".yml", ".yaml")
    touches = 0
    for racine, _, fichiers in os.walk(cible):
        if ".git" in racine:
            continue
        for f in fichiers:
            if not f.endswith(exts):
                continue
            fp = os.path.join(racine, f)
            try:
                s = open(fp, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            s2 = s
            for old, new in remps:
                s2 = s2.replace(old, new)
            if s2 != s:
                open(fp, "w", encoding="utf-8").write(s2)
                touches += 1
    print("→ Upstream repointé vers %s/%s (%d fichier(s) modifié(s))." % (owner, repo, touches))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    upstream = None
    for a in sys.argv[1:]:
        if a.startswith("--upstream="):
            upstream = a.split("=", 1)[1]
    if not args:
        sys.exit("Usage : python3 scripts/preparer-copie-beta.py <dossier-cible> "
                 "[--upstream=owner/repo]")
    cible = os.path.abspath(args[0])
    if os.path.exists(cible) and os.listdir(cible):
        sys.exit(f"❌ {cible} existe déjà et n'est pas vide. Choisis un dossier neuf.")
    if upstream and upstream.count("/") != 1:
        sys.exit("❌ --upstream doit être de la forme owner/repo (ex. awema-test/awema-os).")
    print(f"→ Copie du projet vers {cible} (sans .git, .awema, données réelles)…")
    shutil.copytree(RACINE, cible, ignore=IGNORE)
    neutraliser(cible)
    if upstream:
        owner, repo = upstream.split("/")
        repointer_upstream(cible, owner, repo)
        # registre régénéré par neutraliser() ; rien d'autre à refaire (build ne dépend pas de l'upstream)

    print("\n✅ Copie propre prête :", cible)
    dest = upstream or "<owner>/<repo>"
    url = "https://github.com/%s.git" % dest if upstream else "<url-du-depot>"
    print("\nProchaines étapes (crée d'abord le dépôt VIDE sur GitHub) :")
    print("  1. cd", cible, "&& git init -b main && git add -A && git commit -m \"AWEMA OS — template public\"")
    print("  2. git remote add origin %s && git push -u origin main" % url)
    print("  3. Settings → coche « Template repository » → chacun fait « Use this template ».")
    print("  4. Settings → Pages → branche main, dossier / (root).")
    if upstream:
        print("  5. Partage le lien : https://github.com/%s" % dest)


if __name__ == "__main__":
    main()
