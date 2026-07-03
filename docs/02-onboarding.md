# 02 — Onboarding (démarrer en 10 minutes)

Bienvenue. Cet guide te rend opérationnel rapidement, que tu sois humain ou agent IA.

## Étape 1 — Comprendre où tu es (2 min)

Lis dans l'ordre :
1. [`README.md`](../README.md) (racine) — la porte d'entrée.
2. [`AGENTS.md`](../AGENTS.md) — les règles d'or.
3. [`docs/01-agence.md`](01-agence.md) — l'organisation.

## Étape 2 — Rejoindre une mission (3 min)

1. Identifie ton **département** : `modules/<dept>/README.md`.
2. Identifie ton **client** : `modules/<dept>/clients/<client>/README.md`.
3. Lis le **brief** : `clients/<client>/00-brief/`.

## Étape 3 — Connaître les règles non négociables (2 min)

- **Charte graphique** : `docs/04-charte-graphique.md`.
- **Conventions & qualité** : `docs/03-conventions.md`.

## Étape 4 — Produire (3 min pour comprendre le flux)

- Range tes livrables dans les **sous-dossiers numérotés** du client (`00..10`).
- Pour le volume (contenus, scripts), utilise/édite le **générateur** dans `_generateur/`
  puis lance-le.
- Mets à jour le `README.md` du dossier concerné.

## Carte des sous-dossiers d'une mission marketing

| Dossier | Contenu | Format |
|---|---|---|
| `00-brief/` | Brief client, objectifs, contraintes | Markdown |
| `01-strategie/` | Audit, marché, concurrence, personas, positionnement, piliers | Markdown |
| `02-calendrier-editorial/` | Calendrier 90 jours / 180 contenus | CSV + README |
| `03-contenus/` | Les 180 contenus rédigés (textes, hashtags, prompts, KPI) | Markdown |
| `04-scripts-video/` | 60+ scripts Reels/TikTok/Shorts | Markdown |
| `05-prompts-visuels/` | Prompts Canva / Midjourney / GPT Image | Markdown |
| `06-tunnel-whatsapp/` | Tunnel WhatsApp complet (7 étapes) | Markdown |
| `07-crm-relance/` | Séquences de relance J0→J90 (SMS/WhatsApp/Email) | Markdown |
| `08-scoring/` | Système de scoring automatique + formules | CSV + README |
| `09-automatisation/` | Workflows Make / n8n / Zapier | Markdown |
| `10-presentation/` | Présentation direction (30+ slides) | Markdown |
| `_generateur/` | Scripts de génération du volume | Python |
| `_exports-pdf/` | Exports PDF professionnels | PDF |

## FAQ

**Où créer un nouveau fichier ?** Dans le sous-dossier numéroté qui correspond à sa nature.
Jamais à la racine.

**Comment régénérer 180 contenus ?** `cd .../_generateur && python3 generer.py`.

**Comment exporter en PDF ?** Voir `scripts/README.md` et `_exports-pdf/`.

**Un outil (Canva, Drive…) n'est pas connecté ?** Produis le fichier dans le dépôt
(source de vérité), la publication en ligne viendra ensuite.
