# 14 — Accès API (dev entreprise) pour faire tourner AWEMA officiellement

> Pour gérer **officiellement** les réseaux de **tes clients** (pas juste tes comptes perso), il faut
> des accès API « niveau entreprise » : une **App développeur** par plateforme, souvent une
> **vérification d'entreprise** et une **revue d'application** (App Review). Ce guide te mène de bout en bout.

## Deux modèles — le **A est le défaut**
- **A — Agence autonome (PAR DÉFAUT)** : tu crées **tes propres Apps** sur chaque plateforme. Indépendance
  totale, aucune dépendance à AWEMA. C'est le mode normal : suis ce guide.
- **B — Via AWEMA (Tech Provider) — sur demande & validation** : tu passes par les Apps **déjà vérifiées
  d'AWEMA** *uniquement* pour des **clients communs / hébergés par AWEMA**. **Chaque demande est validée
  au cas par cas par AWEMA** avant tout passage par ses API (accepte/refuse par agence).
  → Demande : **`demande-acces.html`** · suivi/validation : [[ACCES-AGENCE]].

> Tu n'es **jamais obligé** de passer par AWEMA. Le modèle B est un service **opt-in**, réservé aux
> clients communs, et **soumis à approbation**. Le reste de ce guide = modèle A (ton autonomie).

---

## 1) Meta — Facebook & Instagram (le plus structurant)
Pour lire les Pages de tes clients, tu dois être **admin** de leurs Pages (ou via le **Business Manager**
du client qui te délègue un accès partenaire).

1. **Meta Business Manager** : crée/utilise ton Business (business.facebook.com). Fais la
   **Vérification d'entreprise** (documents légaux) — requise pour les permissions avancées.
2. **App Meta** : developers.facebook.com → *Créer une App* (type *Business*).
3. **Produits** : ajoute *Facebook Login* + *Pages API* (+ *Instagram* si comptes IG Pro liés).
4. **Permissions** (demandées en **App Review** pour la production) :
   `pages_show_list`, `pages_read_engagement`, `pages_read_user_content`, `read_insights`
   (+ `instagram_basic`, `instagram_manage_insights` pour IG).
5. **Accès aux Pages clientes** : le client t'ajoute comme **admin** de sa Page, **ou** partage l'accès
   via *Business Manager → Partenaires*. Tu génères alors un **token de Page** (idéalement via un
   **System User** du Business, token longue durée).
6. **Donne le token à AWEMA** : Secret GitHub `META_TOKEN` (jamais dans le dépôt). Un seul token
   découvre toutes tes Pages (`--meta-all`). Guides : [[05-connecter-reseaux]], [[06-obtenir-token-meta]].

> ⚠️ Sans App Review, ton App reste en *mode dev* (seuls les comptes testeurs). Pour gérer de **vrais
> clients**, l'App Review + la vérification d'entreprise sont nécessaires (modèle A) — ou passe en modèle B.

## 2) TikTok — Display API (par compte)
1. developers.tiktok.com → crée une **App** ; ajoute le produit **Login Kit** + scopes
   `user.info.basic/profile/stats`, `video.list`.
2. Configure l'URL de redirection (oauth.html) ; en **Sandbox**, ajoute les comptes de test.
3. Pour la **production**, l'App passe une revue TikTok. Chaque compte client **autorise** (OAuth) ;
   l'assistant échange le code contre un refresh token (rotatif).
4. Secrets : `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` ; tokens dans la Variable `TIKTOK_TOKENS`.
   Guides : [[07-connecter-tiktok]] · assistant `scripts/tiktok-onboard.py`.

## 3) YouTube — Data API v3 (clé, sans OAuth)
1. console.cloud.google.com → projet → active **YouTube Data API v3** → crée une **clé API**.
2. Secret GitHub `YOUTUBE_API_KEY`. Donne le `@handle`/URL de chaque chaîne cliente.
   (Stats **publiques** : abonnés, vues, vidéos — pas d'OAuth.) Guide : `connect-youtube.html`.

## 4) LinkedIn — Pages entreprise (Community Management API)
1. developer.linkedin.com → **Create app**, associe une **Page entreprise** (admin), **Verify** la Page.
2. Produits : *Sign In with LinkedIn (OIDC)* + **Community Management API** (*Development Tier* = immédiat
   pour tes propres Pages ; sinon revue LinkedIn). ⚠️ **Email pro** requis pour la vérification.
3. Génère l'**access token** (assistant `scripts/linkedin-onboard.py`) → Secret `LINKEDIN_TOKEN`.
   Guides : `connect-linkedin.html`, [[10-connecter-linkedin]].

## 5) IA (agents) — optionnelle et au choix
Branche **n'importe quelle IA** ; plusieurs sont **gratuites** (Groq, Gemini, OpenRouter, Ollama…).
Sans clé, les agents sont désactivés (le reste marche). Guide : `connect-ia.html` · [[12-connecter-ia]].

---

## Récapitulatif des secrets (Settings → Secrets and variables → Actions)
| Réseau | Secret(s) |
|---|---|
| Facebook / Instagram | `META_TOKEN` |
| TikTok | `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, Variable `TIKTOK_TOKENS`, `TIKTOK_PAT` |
| YouTube | `YOUTUBE_API_KEY` |
| LinkedIn | `LINKEDIN_TOKEN` (+ `LINKEDIN_CLIENT_ID/SECRET` pour ré-auth) |
| IA (optionnel) | la clé du fournisseur choisi (ex. `GROQ_API_KEY`) |

> 🔒 Aucun secret dans le dépôt — uniquement GitHub Secrets / `.awema` local. Rotation : `awema rotate …`.
> Sécurité & isolation : [[13-securite-donnees]]. Activation officielle : [[ACCES-AGENCE]].
