# Méthode Universelle de Production Éditoriale

> Process standard et **réutilisable pour tout client** du Département Marketing.
> Correspond à l'**Onglet 1** du Google Sheet de production.
> Objectif : transformer une stratégie en **machine à contenu mesurable et automatisable**.

La méthode est une **boucle** en 10 phases. Les 9 premières construisent le système ; la
10ᵉ (Boucle IA) le rend autonome et auto-améliorant.

```
AUDIT → PERSONAS → PILIERS → CALENDRIER → PRODUCTION → VALIDATION
   → PUBLICATION → MESURE → OPTIMISATION → BOUCLE IA ↺
```

---

## 1. AUDIT

**But :** comprendre le point de départ.
- Diagnostic de l'existant (présence sociale, site, avis, e-réputation).
- Analyse du marché local et de la concurrence.
- Forces / faiblesses / opportunités / menaces (SWOT).
- Inventaire des actifs (photos, logo, témoignages, offres).

**Livrable :** note d'audit + SWOT. **Où :** `01-strategie/`.

## 2. PERSONAS

**But :** savoir à qui l'on parle.
- 3 à 5 personas : situation, douleurs, objections, déclencheurs, canaux, ton.
- Mapping persona ↔ objectif business.

**Livrable :** fiches personas. **Où :** `01-strategie/`.

## 3. PILIERS

**But :** structurer le discours de marque.
- 4 à 6 piliers éditoriaux (thématiques récurrentes).
- Chaque pilier sert un objectif (notoriété, expertise, preuve, conversion…).
- Règle de répartition (% par pilier) pour l'équilibre du feed.

**Livrable :** piliers éditoriaux. **Où :** `01-strategie/`.

## 4. CALENDRIER

**But :** planifier la diffusion.
- Cadence (ex : 2 posts/jour), plateformes, horaires optimaux.
- Affectation : date, heure, plateforme, objectif, persona, pilier, sujet, format.
- Colonnes standard : Date, Heure, Plateforme, Objectif, Persona, Pilier, Sujet, Titre,
  Hook, CTA, Format, Prompt Visuel, Prompt Vidéo, Statut.

**Livrable :** calendrier éditorial (CSV). **Où :** `02-calendrier-editorial/`.

## 5. PRODUCTION

**But :** produire les contenus à l'échelle.
- Rédaction multi-plateformes (FB / IG / LinkedIn / TikTok).
- Hashtags, CTA, prompts visuels (Canva / Midjourney / GPT Image), scripts vidéo.
- **Industrialisation** : générateur déterministe pour le volume.

**Livrable :** contenus + scripts + prompts. **Où :** `03-contenus/`, `04-scripts-video/`,
`05-prompts-visuels/`.

## 6. VALIDATION

**But :** garantir la qualité avant diffusion.
- Checklist : conformité charte, exactitude médicale, ton, orthographe, CTA, mentions.
- Statut : `À produire → En revue → Validé → Programmé → Publié`.

**Livrable :** contenus au statut `Validé`. **Où :** colonne `Statut` du calendrier.

## 7. PUBLICATION

**But :** diffuser au bon moment, au bon endroit.
- Programmation (Meta Business Suite, TikTok, planificateurs).
- Tunnel d'entrée (lien WhatsApp, formulaire RDV).

**Livrable :** contenus publiés + tunnel actif. **Où :** `06-tunnel-whatsapp/`.

## 8. MESURE

**But :** mesurer ce qui compte.
- KPI par objectif : portée, engagement, partages, commentaires, messages reçus, RDV.
- Collecte (insights natifs + PostHog) → tableau de scoring.

**Livrable :** données de performance. **Où :** `08-scoring/`.

## 9. OPTIMISATION

**But :** améliorer en continu.
- Scoring automatique A→E par contenu.
- Décision : **À reproduire / À optimiser / À abandonner**.
- Ajustement piliers, formats, horaires.

**Livrable :** recommandations d'optimisation. **Où :** `08-scoring/`.

## 10. BOUCLE IA (automatisation)

**But :** rendre le système autonome et auto-améliorant.

Chaque mois, automatiquement :
1. Analyse des résultats.
2. Détection des meilleurs contenus.
3. Génération des nouveaux sujets.
4. Génération du calendrier.
5. Génération des scripts.
6. Génération des visuels.
7. Génération des publications.

**Livrable :** workflows Make / n8n / Zapier. **Où :** `09-automatisation/`.

---

## Tableau de synthèse (Onglet 1)

| Phase | Objectif | Entrée | Sortie | Dossier |
|---|---|---|---|---|
| 1. Audit | Diagnostiquer | Marché, existant | SWOT, audit | `01-strategie/` |
| 2. Personas | Cibler | Audit | Fiches personas | `01-strategie/` |
| 3. Piliers | Structurer | Personas | Piliers éditoriaux | `01-strategie/` |
| 4. Calendrier | Planifier | Piliers | Calendrier 180 | `02-calendrier-editorial/` |
| 5. Production | Produire | Calendrier | Contenus, scripts, prompts | `03/04/05` |
| 6. Validation | Contrôler | Contenus | Contenus validés | `Statut` |
| 7. Publication | Diffuser | Validés | Posts + tunnel | `06-tunnel-whatsapp/` |
| 8. Mesure | Mesurer | Posts | KPI | `08-scoring/` |
| 9. Optimisation | Améliorer | KPI | Reco A→E | `08-scoring/` |
| 10. Boucle IA | Automatiser | Reco | Workflows | `09-automatisation/` |
