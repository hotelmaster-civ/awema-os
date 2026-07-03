---
titre: 04 — PLUGIN MODEL
statut: stable
maj: 2026-06-27
---

# 04 — Modèle de plugins

> **Les plugins sont préférés aux modifications du Kernel.** Un plugin **ajoute** une capacité sans
> changer le cœur. Trois familles existent aujourd'hui ; toutes suivent le même esprit : **déclaratif,
> additif, sourcé, à skip gracieux**.

## Familles de plugins (existantes)
| Famille | Déclaré dans | Apporte | Sortie |
|---|---|---|---|
| **Connecteur** | `scripts/awema-connectors.json` | une API externe (réseau social, IA…) | écrit/alimente `reseaux.json` (ou store) |
| **Agent** | `scripts/agents.json` | un travailleur IA spécialisé | écrit `_donnees/_agents/<agent>.json` (additif) |
| **Fournisseur IA** | `config/ia-providers.json` | un LLM branchable (agnostique) | consommé par `awema_ai.py` |

## Contrat commun d'un plugin
1. **Déclaratif** : on l'ajoute via une **entrée de manifeste** (JSON), pas en réécrivant le Kernel.
2. **Additif** : il **n'altère jamais** la donnée réelle existante (`reseaux.json` reste intouché par
   les agents ; un nouveau connecteur fusionne sans écraser les autres réseaux).
3. **Sourcé & horodaté** : sa sortie porte `source`/`genere_le`/`provenance` (cf. [06-DATA_MODEL](06-DATA_MODEL.md)).
4. **Skip gracieux** : sans clé/token/API, il s'auto-désactive sans casser le reste.
5. **Capacités déclarées** : un connecteur déclare ses `keys`, ses `commands`, son `sync_workflow`,
   son `doc`. *(Objectif d'évolution : déclarer aussi ses capacités/métriques pour absorber la mort
   d'une API — cf. ROADMAP « adaptateur de source ».)*

## Ajouter un plugin (procédure)
- **Connecteur** : ajouter une entrée dans `awema-connectors.json` (label, `keys`, `commands`, `doc`) +
  la voie correspondante dans `connect-reseaux.py` (ou un script dédié) → remplit `reseaux.json` →
  `build.py`.
- **Agent** : ajouter une entrée dans `agents.json` (`role`, `entrees`, `modele`, `systeme`,
  `instruction`, `schema_hint`, `liste`, `item_requis`, `champs_sortie`). `run-agent.py` le découvre
  automatiquement. Voir [05-AGENT_MODEL](05-AGENT_MODEL.md).
- **Fournisseur IA** : ajouter une entrée dans `ia-providers.json` (`type` openai|anthropic, `base_url`,
  `model`, `cle`, `gratuit`). Aucune autre modification.

## Quand modifier le Kernel plutôt qu'ajouter un plugin
**Rarement.** Seulement si un **concept universel** manque (cf. [02-KERNEL](02-KERNEL.md)) ou si un
contrat doit changer pour tous. Dans ce cas : **ADR obligatoire**, migration additive et réversible.

## Un module est-il un plugin ?
Conceptuellement, un **module** (ex. Marketing) est le plus gros des plugins : un domaine métier qui
**connaît le Kernel** et apporte ses workflows, sa knowledge, ses agents et ses connecteurs. Le Kernel
ne le nomme jamais. Un module vit dans `modules/<module>/` (répertoire renommé depuis `departements/`,
ADR-006).
