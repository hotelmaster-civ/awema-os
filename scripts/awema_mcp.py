#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serveur MCP AWEMA — pilote AWEMA en langage naturel depuis tout client MCP (Claude Desktop/Code…).

ADN : Python **stdlib uniquement**. Protocole MCP = JSON-RPC 2.0 en lignes (newline-delimited) sur
stdio. Méthodes gérées : initialize, tools/list, tools/call (+ notifications ignorées).

Chaque outil enveloppe une opération AWEMA existante (l'opérateur `awema.py`, le runner d'agents,
le build) — aucune logique métier nouvelle. **stdout = canal protocole** (n'y écris QUE du JSON-RPC).

Brancher dans un client MCP :
  { "mcpServers": { "awema": { "command": "python3", "args": ["<repo>/scripts/awema_mcp.py"] } } }

Lister les outils (debug humain) :  python3 scripts/awema_mcp.py --tools
"""
import json
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
PROTO = "2024-11-05"


def _run(cmd):
    """Exécute un script du dépôt (cwd=RACINE) et renvoie sa sortie texte (stdout+stderr)."""
    try:
        p = subprocess.run([sys.executable] + cmd, cwd=RACINE, capture_output=True, text=True, timeout=180)
        return ((p.stdout or "") + (p.stderr or "")).strip() or "(ok)"
    except Exception as e:
        return "Erreur d'exécution : %s" % e


# --- Catalogue d'outils : schéma (pour tools/list) + exécuteur (pour tools/call) ---
def _t_status(a):
    return _run(["scripts/awema.py", "client", "list"]) + "\n\nIA : " + _run(["scripts/awema_ai.py", "--check"])


def _t_build(a):
    return _run(["outils/_data/build.py"])


def _t_client_new(a):
    args = ["scripts/awema.py", "client", "new", "auto", "nom=" + str(a.get("nom", ""))]
    for k in ("secteur", "lieu", "facebook", "instagram", "tiktok", "youtube", "linkedin", "whatsapp"):
        if a.get(k):
            args.append("%s=%s" % (k, a[k]))
    return _run(args)


def _t_run_agent(a):
    cible = a.get("client") or "--all"
    return _run(["scripts/run-agent.py", str(a.get("agent", "")), cible])


def _t_needs(a):
    return _run(["scripts/awema.py", "needs", str(a.get("plateforme", ""))])


def _t_providers(a):
    return _run(["scripts/awema_ai.py", "--providers"])


TOOLS = [
    {"name": "awema_status", "run": _t_status,
     "description": "État d'AWEMA : liste des clients gérés + IA active (ou non).",
     "schema": {"type": "object", "properties": {}}},
    {"name": "awema_build", "run": _t_build,
     "description": "Régénère le registre (outils/_data/*.js) après toute modification de données/config.",
     "schema": {"type": "object", "properties": {}}},
    {"name": "awema_client_new", "run": _t_client_new,
     "description": "Crée (ou met à jour) la fiche d'un client. Le slug est dérivé du nom.",
     "schema": {"type": "object", "properties": {
         "nom": {"type": "string", "description": "Nom de l'entité (requis)"},
         "secteur": {"type": "string"}, "lieu": {"type": "string"},
         "facebook": {"type": "string"}, "instagram": {"type": "string"}, "tiktok": {"type": "string"},
         "youtube": {"type": "string"}, "linkedin": {"type": "string"}, "whatsapp": {"type": "string"}},
         "required": ["nom"]}},
    {"name": "awema_run_agent", "run": _t_run_agent,
     "description": "Fait travailler un agent IA et écrit sa proposition. agent ∈ {analyste, stratege, "
                    "creatif, actions-du-jour}. Sans 'client', s'applique à tous (--all). "
                    "actions-du-jour marche sans clé IA ; les autres nécessitent une clé.",
     "schema": {"type": "object", "properties": {
         "agent": {"type": "string", "description": "analyste | stratege | creatif | actions-du-jour"},
         "client": {"type": "string", "description": "slug du client (sinon tous)"}},
         "required": ["agent"]}},
    {"name": "awema_connect_needs", "run": _t_needs,
     "description": "Identifiants requis et présents pour une plateforme (meta, tiktok, youtube, linkedin, ia, whatsapp).",
     "schema": {"type": "object", "properties": {
         "plateforme": {"type": "string"}}, "required": ["plateforme"]}},
    {"name": "awema_ia_providers", "run": _t_providers,
     "description": "Liste les fournisseurs d'IA branchables (avec les options GRATUITES mises en avant).",
     "schema": {"type": "object", "properties": {}}},
]
_BY_NAME = {t["name"]: t for t in TOOLS}


def handle(req):
    """Traite un message JSON-RPC. Fonction PURE pour le protocole (initialize/tools/list/erreurs) ;
    tools/call délègue à l'exécuteur de l'outil. Renvoie le dict réponse, ou None (notifications)."""
    m, i = req.get("method"), req.get("id")
    if m == "initialize":
        return {"jsonrpc": "2.0", "id": i, "result": {
            "protocolVersion": PROTO, "capabilities": {"tools": {}},
            "serverInfo": {"name": "awema", "version": "1.0"}}}
    if m == "tools/list":
        return {"jsonrpc": "2.0", "id": i, "result": {"tools": [
            {"name": t["name"], "description": t["description"], "inputSchema": t["schema"]} for t in TOOLS]}}
    if m == "tools/call":
        p = req.get("params", {}) or {}
        t = _BY_NAME.get(p.get("name"))
        if not t:
            return {"jsonrpc": "2.0", "id": i, "error": {"code": -32602, "message": "outil inconnu : %s" % p.get("name")}}
        out = t["run"](p.get("arguments", {}) or {})
        return {"jsonrpc": "2.0", "id": i, "result": {"content": [{"type": "text", "text": str(out)[:12000]}]}}
    if m and m.startswith("notifications/"):
        return None                                   # pas de réponse aux notifications
    return {"jsonrpc": "2.0", "id": i, "error": {"code": -32601, "message": "méthode inconnue : %s" % m}}


def main():
    if "--tools" in sys.argv:                          # aide humaine (pas le mode serveur)
        for t in TOOLS:
            print("• %-22s %s" % (t["name"], t["description"]))
        return
    for line in sys.stdin:                             # boucle serveur : 1 message JSON par ligne
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        resp = handle(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
