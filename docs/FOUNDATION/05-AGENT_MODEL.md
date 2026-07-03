---
titre: 05 — AGENT MODEL
statut: stable
maj: 2026-06-27
---

# 05 — Modèle d'agent

> Un agent est un **travailleur IA spécialisé** qui **propose** ; il ne décide pas. **Aucun agent ne
> doit devenir généraliste.** Architecture (ADR-001) : un agent = un **job Python** (stdlib + **un**
> appel LLM) → un **artefact JSON additif** → rendu par le cockpit.

## Anatomie d'un agent (sept attributs obligatoires)
| Attribut | Définition | Où il vit |
|---|---|---|
| **Mission** | Le « pourquoi » de l'agent, en une phrase. | `role` dans `agents.json`. |
| **Responsabilités** | Ce qu'il fait / ne fait pas (cadre, garde-fous). | `systeme` + `instruction`. |
| **Entrées** | Les fichiers du client qu'il lit. | `entrees` (ex. `reseaux`, `memoire`, `campagne`). |
| **Sorties** | L'artefact JSON produit + son schéma. | `_donnees/_agents/<agent>.json` ; `schema_hint`, `liste`, `item_requis`, `champs_sortie`. |
| **Mémoire** | Le contexte durable qu'il exploite. | `memoire.json` (Mémoire Marketing) ; ses sorties passées. |
| **Critères de réussite** | Ce qui rend sa sortie « bonne ». | défini par module (ex. ≥3 insights + ≥2 reco **sourcés**). |
| **Definition of Done** | Conditions de validité avant écriture. | enveloppe valide + schéma respecté + **preuve réelle**. |

## Enveloppe commune (toute sortie d'agent)
```json
{ "agent": "...", "genere_le": "ISO", "modele": "...",
  "provenance": { "client": "...", "fichiers": ["..."], "genere_par": "run-agent.py" },
  "items": [ ... ] }
```
+ champs structurés déclarés via `champs_sortie` (ex. `cadence_recommandee`). La sortie est **validée**
(`valider_enveloppe`) avant écriture ; invalide → **non écrite** (loggée).

## Règles
1. **Spécialisation stricte.** Un agent = une mission. Pas d'agent « fait-tout ».
2. **Proposition, pas décision.** Sorties étiquetées « proposition IA », horodatées, **sourcées**.
3. **Preuve obligatoire.** Toute affirmation chiffrée cite une métrique réelle des entrées ; sinon, on
   ne l'affirme pas. **Zéro fiction.**
4. **Additif.** L'agent écrit **uniquement** son artefact ; il ne mute jamais la donnée réelle.
5. **Skip gracieux.** Sans clé IA, l'agent ne s'exécute pas (aucune écriture, pas d'erreur).
6. **Humain décideur.** Une action engageante (écrire `campagne.json`) exige une validation explicite.

## Agents du module Marketing (état)
- **Livrés** : **Analyste** (pourquoi/quoi faire), **Stratège** (plan), **Créatif** (publications prêtes),
  + **Proactivité** (`actions-du-jour`, agrégateur **déterministe sans clé IA**).
- **Cible, non implémentés** : **Veille** (marché), **Modérateur** (commentaires/DM), **Chef de projet**
  (coordination). Détail dans `docs/PRD-AWEMA.md`.

## Proactivité (cas particulier)
`actions-du-jour` n'est **pas** un agent LLM : c'est une **fonction déterministe** qui agrège des
alertes dérivées des données réelles + les meilleures propositions des agents. Elle fonctionne **sans
clé IA** et garantit une valeur immédiate (« 3 choses à faire aujourd'hui »).
