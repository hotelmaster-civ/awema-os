---
titre: 02 — KERNEL (concepts universels)
statut: stable
maj: 2026-06-27
---

# 02 — Kernel

> Le Kernel = les **concepts universels** d'un OS d'agence. **Il ne contient aucune logique métier.**
> Les **modules** (ex. Marketing) connaissent le Kernel ; **le Kernel ne connaît jamais les modules**.
> Concrètement, le Kernel se manifeste comme des **conventions + contrats + outils transverses**, pas
> comme un framework lourd. *(Un « module » vit physiquement dans `modules/<module>/` — répertoire
> renommé depuis `departements/` par l'ADR-006.)*

## Les 11 concepts autorisés
| Concept | Définition (universelle) | Manifestation actuelle dans le dépôt |
|---|---|---|
| **Mission** | Une unité de travail pour une entité cliente. | `modules/<module>/clients/<client>/` (+ `client.json` : champ `module`). |
| **Workflow** | Une suite d'étapes reproductible. | Méthodologies de module + séquences GitHub Actions. |
| **Knowledge** | Savoir réutilisable, indépendant d'un client. | `methodologie/`, `templates/`, `docs/`. |
| **Memory** | Ce que le système retient dans le temps. | `memoire.json` (par client) ; historique `.awema/credentials.json`. |
| **Context** | L'état courant exploitable par humains/agents. | Registre `outils/_data/agence.js` (`window.AWEMA_REGISTRY`). |
| **Agent** | Un travailleur IA spécialisé qui **propose**. | `scripts/agents.json` + `scripts/run-agent.py` → `_agents/*.json`. |
| **Event** | Un déclencheur. | `cron`, `workflow_dispatch`, `push` (workflows) ; commande `/awema`. |
| **Automation** | Une exécution sans intervention. | `.github/workflows/*` ; `connect-reseaux.py` ; `build.py`. |
| **Plugin** | Un point d'extension additif. | Manifestes `awema-connectors.json` (connecteurs) & `agents.json` (agents). |
| **Security** | Secrets, isolation, traçabilité d'accès. | Store `.awema/` (gitignoré) ; GitHub Secrets ; licence + accès API. |
| **API** | Une frontière d'échange avec l'extérieur. | Connecteurs réseaux (`connect-reseaux.py`) ; client LLM (`awema_ai.py`). |

## Règles du Kernel
1. **Aucune logique métier dans le Kernel.** « Calendrier éditorial », « cadence de publication »,
   « scoring A→E » sont **du Marketing**, pas du Kernel.
2. **Dépendance à sens unique.** Module → Kernel autorisé. Kernel → Module **interdit** (le Kernel ne
   nomme jamais un module).
3. **Stabilité.** Le Kernel évolue lentement et par **ADR**. Étendre se fait par **plugin**
   (cf. [04-PLUGIN_MODEL](04-PLUGIN_MODEL.md)), pas en modifiant le Kernel.
4. **Neutralité des données.** Le Kernel transporte/affiche la donnée ; il n'en interprète pas le sens
   métier (c'est le rôle des agents d'un module).

## Frontière Kernel / Module (exemples)
- **Kernel** : « un client a une Mémoire », « un agent écrit un artefact JSON sourcé », « le cockpit
  rend des propositions », « un connecteur déclare ses clés ».
- **Marketing** : « un Reel performe mieux qu'un carrousel », « publier 4×/semaine », « répondre aux
  commentaires en attente », « meilleur créneau le vendredi ».
