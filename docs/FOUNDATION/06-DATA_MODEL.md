---
titre: 06 — DATA MODEL
statut: stable
maj: 2026-06-27
---

# 06 — Modèle de données

> **Les données sont la vérité.** Git versionne des fichiers JSON ; il n'y a **pas de base de données**.
> Toute donnée affichée est **traçable** (source, horodatage, provenance). **Données réelles
> prioritaires ; zéro fiction** (ce qui n'existe pas reste `null`/`[]`).

## Hiérarchie de la donnée
| Niveau | Fichier | Concept Kernel | Rôle |
|---|---|---|---|
| Instance | `config/agence.json` | Context | Branding/charte/fork (point unique de personnalisation). |
| Instance | `config/licence.json`, `aliases.json`, `ia-providers.json`, `beta-seats.json` | Security/Context | Activation, alias, fournisseurs IA, places bêta. |
| Client | `client.json` | Mission | Profil, handles réseaux, chemins. **Requis** pour être listé. |
| Client | `reseaux.json` | Context | Présence digitale **réelle** consolidée (multi-réseaux). |
| Client | `memoire.json` | Memory | Mémoire Marketing (identité, ton, personas, produits, FAQ…). |
| Client | `campagne.json` | Workflow | Plan éditorial (`total`, `contenus[]`). |
| Client | `_agents/<agent>.json` | Agent | Sorties IA **additives** (propositions sourcées). |
| Privé | `.awema/*` (gitignoré) | Security | Credentials + registres de preuve (licences, accès, attente). |

## Source de vérité → rendu
Les fichiers ci-dessus sont **la** vérité. `outils/_data/build.py` les **agrège** (sans rien inventer)
en fichiers générés **lecture seule** : `agence.js` (`window.AWEMA_REGISTRY`), `config.js`,
`ia-providers.js`. Le front lit ces registres. **Ne jamais éditer un `.js` généré à la main.**

## Traçabilité (obligatoire)
- Une **mesure** vient d'un connecteur : `reseaux.json` porte `source`, `maj`, et `null` si non connecté.
- Une **proposition** vient d'un agent : l'artefact porte `genere_le`, `modele`, `provenance`
  (client, fichiers lus) et chaque item chiffré porte une **preuve** (métrique réelle).
- Aucune valeur affichée ne doit être **non attribuable** à l'une de ces deux origines.

## Règles
1. **Additif.** Une nouvelle source écrit un **nouveau** fichier ou fusionne sans écraser ; l'absence
   d'un fichier = comportement actuel inchangé.
2. **Données privées hors git.** Contacts/preuves dans `.awema/` ; `beta-seats.json` ne contient que
   pseudo/handle + contact minimal (RGPD).
3. **`null` honnête.** Une métrique indisponible reste `null` et s'affiche « source indisponible »
   (jamais un faux zéro).

## Points d'extension prévus (à NE PAS implémenter sans besoin réel)
- **Séries temporelles** : `_data/timeseries/<client>/<metric>.ndjson` append-only (`evolution_audience`
  en est l'amorce) → migrable vers SQLite/DuckDB/Parquet **sans casser le JSON**.
- **Cache analytique** : couche de lecture optionnelle, **jamais** source de vérité.
- **Module Marché** : `marche.json` par client (présence des concurrents) — post-bêta.
