# 04 — Charte Graphique

La charte est **obligatoire** : tous les visuels, slides, templates, prompts Canva et
prompts IA doivent la respecter strictement.

---

## Charte AWEMA (produit) — thème « Ruche » 🐝

L'identité du produit AWEMA est celle de la ruche : **jaune or et noir**, sobre et premium.
L'abeille (Awa, la mascotte) travaille ; la ruche est organisée ; le miel est le résultat.
Lorsqu'une mission client a sa propre charte, **la charte client prime** sur les visuels
destinés au client — le thème Ruche s'applique à l'interface AWEMA elle-même.

### Couleurs (Ruche)

| Rôle | Nom | HEX | Usage |
|---|---|---|---|
| Fond dominant | **Noir ruche** | `#222222` | Fonds, autorité, sobriété (profondeurs : `#1B1B1B`, `#191919`, `#161616`) |
| Primaire | **Or** | `#D4AF37` | CTA, logo, détails premium |
| Appui | **Miel** | `#FFC94D` | Liens, accents dynamiques, éléments actifs |
| Accent | **Ambre** | `#EDA914` | Dégradés avec le miel, survols, badges |
| Neutre clair | Crème | `#F7F4EA` | Thème clair, respirations |
| Texte | Ivoire | `#F1EDE2` | Texte principal sur fonds noirs (secondaire : `#B3AA92`) |

**Règles d'usage couleur**
- Noir ruche = dominante (60 %). Or/miel/ambre = la famille d'accents (30 %).
- Les couleurs de statut restent fonctionnelles : succès `#34E5C4`, erreur `#FF7D9C`.
- Les couleurs de **marque des plateformes** (Facebook, TikTok…) ne changent jamais : elles portent l'identité de chaque réseau.
- Contraste AA minimum pour l'accessibilité (texte sur fond).
- Typographies : inchangées — **Montserrat** (titres) + **Poppins** (corps).

> Source machine : `config/agence.json` → `charte` (injectée sur toutes les pages par `outils/_data/apply.js`).

---

## Charte Client — La Grande Vision (cabinet d'optique)

### Couleurs

| Rôle | Nom | HEX | RGB | Usage |
|---|---|---|---|---|
| Primaire | **Bleu Nuit** | `#0A1F44` | `10, 31, 68` | Fonds, titres, autorité médicale, confiance |
| Secondaire | **Bleu Ciel** | `#4BA3FF` | `75, 163, 255` | Accents, liens, éléments dynamiques, jeunesse |
| Accent | **Gold** | `#D4AF37` | `212, 175, 55` | Premium, CTA, détails de luxe, distinction |
| Neutre clair | Blanc cassé | `#F7F9FC` | `247, 249, 252` | Fonds clairs, respiration |
| Neutre foncé | Gris ardoise | `#2B2F38` | `43, 47, 56` | Textes secondaires |

**Règles d'usage couleur**
- Bleu Nuit = couleur dominante (60 %). Sérieux médical, confiance, autorité.
- Bleu Ciel = couleur d'appui (30 %). Modernité, accessibilité, énergie.
- Gold = touche premium (10 % maximum). Réservé aux CTA et signes de qualité.
- Contraste AA minimum pour l'accessibilité (texte sur fond).

### Typographies

| Usage | Police | Graisses |
|---|---|---|
| Titres / Display | **Montserrat** | Bold / ExtraBold |
| Corps de texte | **Poppins** | Regular / Medium / SemiBold |

- Hiérarchie : Montserrat Bold pour les titres, Poppins pour le texte courant.
- Pas plus de 2 familles. Interligne aéré (premium).

### Style & univers

- **Premium** · **Moderne** · **Médical** · **Confiance** · **Familial** · **Professionnel**
- Photographie lumineuse, nette, humaine (familles, professionnels de santé, sourires).
- Espaces blancs généreux, composition épurée, pictogrammes en ligne fine.
- Éviter : couleurs criardes, surcharge, ton agressif, stock photo cliché.

### Signature de marque

- Slogan directeur : **« Voir la vie en grand. »**
- Positionnement : l'expert de la santé visuelle de proximité à Yopougon.

---

## Bloc « charte » à insérer dans les prompts IA

> À copier-coller dans tout prompt Canva / Midjourney / GPT Image :

```
Palette: deep navy blue #0A1F44 (dominant), sky blue #4BA3FF (accent), gold #D4AF37 (premium details).
Typography style: Montserrat (headlines) + Poppins (body), clean modern medical.
Mood: premium, modern, medical, trustworthy, family-friendly, professional.
Lighting: bright, soft, natural. Composition: clean, airy, generous white space.
Context: optical / eyewear clinic in Abidjan, Côte d'Ivoire (West Africa).
```

## Codes couleurs prêts pour les outils

```
Bleu Nuit  #0A1F44
Bleu Ciel  #4BA3FF
Gold       #D4AF37
Blanc cassé #F7F9FC
Gris ardoise #2B2F38
```
