# 16 — Lancer en local & piloter AWEMA en langage naturel (MCP)

> Deux confort majeurs : **(A)** lancer toute l'app en **une commande**, **(B)** laisser **Claude** (ou
> tout client MCP) piloter AWEMA en **langage naturel**. ADN respecté : **Python stdlib uniquement**.

## A · Lancer en local — une seule commande
```bash
python3 scripts/awema.py serve
```
→ régénère le registre, démarre un serveur local (port 8000, sinon le suivant libre) et **ouvre le
navigateur**. Accueil : `http://127.0.0.1:8000/` · Cockpit : `…/outils/dashboard/index.html`. `Ctrl+C` arrête.

> Aucune installation : pas de `pip`, pas de `npm`. Il suffit de **Python 3** (déjà présent sur macOS/Linux ;
> sur Windows : `py scripts\awema.py serve`).

## B · Piloter avec Claude (serveur MCP)
Le serveur **`scripts/awema_mcp.py`** expose les opérations d'AWEMA comme **outils MCP**. Tout client
compatible (Claude Desktop, Claude Code…) peut alors **agir en langage naturel**.

### Brancher (une fois)
Ajoute le serveur à la config MCP de ton client (remplace `<repo>` par le chemin absolu du projet) :
```json
{
  "mcpServers": {
    "awema": { "command": "python3", "args": ["<repo>/scripts/awema_mcp.py"] }
  }
}
```
- **Claude Desktop** : `Réglages → Developer → Edit Config` (`claude_desktop_config.json`).
- **Claude Code** : `claude mcp add awema -- python3 <repo>/scripts/awema_mcp.py` (ou `.mcp.json` du projet).

Vérifier les outils exposés (debug humain) : `python3 scripts/awema_mcp.py --tools`.

### Ce que tu peux dire à Claude
- « **Quel est l'état d'AWEMA ?** » → `awema_status` (clients + IA active)
- « **Crée le client Restaurant Le Baoulé, secteur restauration, à Abidjan** » → `awema_client_new`
- « **Fais tourner l'analyste sur tous les clients** » → `awema_run_agent`
- « **Génère les actions du jour** » → `awema_run_agent` (marche **sans clé IA**)
- « **Qu'est-ce qu'il me manque pour connecter TikTok ?** » → `awema_connect_needs`
- « **Régénère le registre** » → `awema_build`
- « **Quelles IA gratuites puis-je brancher ?** » → `awema_ia_providers`

### Outils MCP disponibles
| Outil | Rôle |
|---|---|
| `awema_status` | Clients gérés + IA active. |
| `awema_build` | Régénère le registre (`outils/_data/*.js`). |
| `awema_client_new` | Crée/MAJ la fiche d'un client (nom requis). |
| `awema_run_agent` | Fait travailler un agent (analyste/stratege/creatif/actions-du-jour). |
| `awema_connect_needs` | Identifiants requis/présents pour une plateforme. |
| `awema_ia_providers` | Fournisseurs d'IA branchables (gratuits mis en avant). |

> **Sécurité** : le serveur tourne **en local**, opère sur **ton** dépôt, n'expose **aucun secret**
> (les clés restent dans GitHub Secrets / `.awema/`). Il n'ajoute **aucune logique métier** : chaque
> outil enveloppe une commande AWEMA existante.

> **Lien avec `/awema`** : c'est la même philosophie « opérateur en langage naturel », rendue **standard**
> (MCP) donc utilisable par n'importe quelle IA, pas seulement le slash-command de Claude Code.
