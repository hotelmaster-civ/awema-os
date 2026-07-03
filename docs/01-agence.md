# 01 — L'Agence (AWEMA)

## Vision

**AWEMA — Agence Web Marketing Africaine** est une agence panafricaine qui conçoit, déploie
et automatise des systèmes de croissance digitale pour les entreprises africaines (TPE,
PME, professions de santé, commerces, marques).

Notre différence : nous ne livrons pas « quelques publications », nous installons des
**systèmes marketing complets, automatisés et industrialisables**, pilotables par des
équipes humaines **et** des agents IA.

## Modèle d'organisation « holistique »

L'agence est organisée en **départements** autonomes mais interopérables. Chaque
département partage les mêmes conventions, la même structure de dossiers et la même
exigence de documentation, afin qu'un agent (humain ou IA) puisse passer de l'un à l'autre
sans friction.

```
AWEMA
├── Marketing & Contenu      ← stratégie éditoriale, social media, copywriting, growth   ✅ actif
├── Web & Développement      ← sites, apps, intégrations, MCP/automatisation             ⏳ à venir
├── Design & Création        ← identité, motion, UX/UI, Canva/Midjourney                 ⏳ à venir
├── Growth & Publicité (Ads) ← Meta/Google Ads, tunnels d'acquisition                    ⏳ à venir
├── Data & Analytics         ← mesure, scoring, dashboards (PostHog), reporting          ⏳ à venir
├── Relation Client & CRM    ← WhatsApp Business, séquences, fidélisation                ⏳ à venir
└── Direction & Opérations   ← coordination, qualité, finance, RH                        ⏳ à venir
```

> La présente livraison concerne le **Département Marketing & Contenu** et sa **première
> mission** : le cabinet d'optique **La Grande Vision** (Yopougon, Côte d'Ivoire).

## Comment un département est structuré

Chaque département suit **exactement** ce gabarit :

```
modules/<nom-departement>/
├── README.md            ← rôle, mission, méthode, livrables types du département
├── methodologie/        ← méthodes réutilisables (process, frameworks)
├── templates/           ← gabarits vierges prêts à dupliquer
└── clients/
    └── <nom-client>/    ← une mission = un dossier, rangé en sous-dossiers numérotés
```

## Principes transverses

1. **Réutilisabilité d'abord.** Chaque actif est pensé pour servir au client suivant.
2. **Documentation native.** Un dossier sans `README.md` est un dossier interdit.
3. **Industrialisation.** Le volume répétitif est généré par script, pas à la main.
4. **Charte respectée.** Voir `04-charte-graphique.md`.
5. **Orientation résultats.** Chaque livrable porte un KPI et un système de mesure.

## Ajouter un nouveau département (procédure)

1. Créer `modules/<nom>/` avec les 3 sous-dossiers + `README.md`.
2. Copier les conventions depuis `docs/03-conventions.md`.
3. Référencer le département dans la table ci-dessus.
4. Documenter sa méthode dans `methodologie/`.

## Ajouter un nouveau client (procédure)

1. Créer `modules/<dept>/clients/<client>/`.
2. Y déposer le brief dans `00-brief/`.
3. Dériver la charte client dans `docs/04-charte-graphique.md`.
4. Suivre la méthode du département.
