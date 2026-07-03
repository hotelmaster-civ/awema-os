# 17 — Mise en route complète (faire tourner AWEMA à 100 %)

> **Principe (modèle A, par défaut)** : chaque agence fournit **ses propres** ressources (Apps, clés,
> tokens) et reste **100 % autonome**. Tout secret vit dans **GitHub → Secrets** (ou `.awema/` local) —
> **jamais dans le dépôt**. Le modèle B (via AWEMA, sur validation) est une exception pour clients communs.

## C'est quoi « 100 % » ?
Tu n'as **pas** besoin de *toutes* les plateformes — seulement de **celles où sont tes clients**.
« 100 % » = **Socle** + **IA** + **les réseaux de tes clients connectés** + **automatisation active**.

| Niveau | Tu connectes | Tu obtiens |
|---|---|---|
| **Socle** (obligatoire) | GitHub (fork + Pages + jeton navigateur) | L'app tourne, saisie **1-clic**, cockpit, démo. |
| **Cerveau** (recommandé, **gratuit**) | 1 clé IA (Groq/Gemini/Ollama) | Analyste / Stratège / Créatif **travaillent**. |
| **Yeux** | ≥ 1 réseau (Meta/TikTok/YouTube/LinkedIn) | **Données réelles** à analyser. |
| **100 %** | Tous les réseaux de tes clients + automatisation | Analyses **fraîches sans geste**, en continu. |

## Tableau des ressources (quoi · où · pour quoi)
| Ressource | Donne | Où la ranger | Guide | Requis si… |
|---|---|---|---|---|
| **Dépôt GitHub + Pages** | hébergement de l'instance | — | [[09-auto-hebergement]] | **toujours** |
| **Jeton fin (PAT) navigateur** | bouton **« Enregistrer »** (écrit dans le dépôt) | navigateur (localStorage, ADR-007) | [[14-acces-api-agence]] | **toujours** |
| **Clé IA** (`GROQ_API_KEY`…) + `AWEMA_AI_PROVIDER` | agents qui proposent | **Secret** (+ Variable) GitHub | [[12-connecter-ia]] | tu veux l'IA (gratuit) |
| `META_TOKEN` | Facebook / Instagram | **Secret** | [[06-obtenir-token-meta]], [[05-connecter-reseaux]] | clients sur FB/IG |
| `TIKTOK_CLIENT_KEY` / `_SECRET` + Variable `TIKTOK_TOKENS` + `TIKTOK_PAT` | TikTok | **Secrets** + **Variable** | [[07-connecter-tiktok]] | clients sur TikTok |
| `YOUTUBE_API_KEY` | YouTube (stats publiques) | **Secret** | `connect-youtube.html` | clients sur YouTube |
| `LINKEDIN_TOKEN` (+ `CLIENT_ID/SECRET`) | LinkedIn (Page entreprise) | **Secret** | [[10-connecter-linkedin]] | clients sur LinkedIn |
| `WHATSAPP_TOKEN` + `WHATSAPP_PHONE_ID` + `WHATSAPP_WABA_ID` | WhatsApp (messagerie) | **Secrets** | `connect-whatsapp.html` | tu fais du tunnel WhatsApp |

> **Où mettre un Secret** : dépôt GitHub → **Settings → Secrets and variables → Actions → New repository
> secret**. (Pour un usage purement local : l'opérateur les range dans `.awema/`, gitignoré.)

## Runbook ordonné (de zéro à 100 %)
1. **Forke** le template (`awema-os`) sur ton GitHub, active **Settings → Pages** (branche `main`, `/root`).
2. **Personnalise** : `setup.html` → bouton **Enregistrer** (la 1ʳᵉ fois, connecte ton GitHub via un **jeton fin** : *Contents R/W + Actions R/W*, limité à ton dépôt).
3. **Branche une IA gratuite** : `connect-ia.html` → crée une clé **Groq** (2 min) → Secret `GROQ_API_KEY`. Vérifie : `python3 scripts/awema_ai.py --check`.
4. **Pour CHAQUE réseau de tes clients** : suis le guide `connect-<réseau>.html` → crée l'App, récupère le token → **Secret** GitHub. (App Review/vérif d'entreprise nécessaires pour gérer de **vrais** clients — cf. [[14-acces-api-agence]].)
5. **Ajoute tes clients** : `nouveau-client.html` (bouton Enregistrer) + leur **Mémoire** : `memoire.html`.
6. **Première synchro** : onglet **Actions** du dépôt → lance `Sync présence digitale` et `Sync TikTok` (bouton *Run workflow*). → `reseaux.json` se remplit → les **agents** ré-analysent automatiquement.
7. **C'est autonome** : `sync-reseaux`/`sync-tiktok` (hebdo) → `agents.yml` (quotidien **+ après chaque sync**) → `build.yml` (à chaque écriture). Le cockpit (Pages) sert les résultats à jour.

## Vérifier que tout tourne
- `python3 scripts/awema.py serve` → ouvre le cockpit ; **« Présence par réseau »** montre l'état **réel** de connexion par client.
- Manque-t-il quelque chose pour une plateforme ? `python3 scripts/awema.py needs <meta|tiktok|youtube|linkedin|ia>` (ou via le MCP : *« qu'est-ce qu'il me manque pour TikTok ? »*).
- IA active ? `python3 scripts/awema_ai.py --check`.

## Modèle A vs B (rappel)
- **A — Autonome (défaut)** : tes propres Apps. Indépendance totale. Suis ce guide.
- **B — Via AWEMA (Tech Provider, sur validation)** : seulement pour clients communs/hébergés par AWEMA →
  `demande-acces.html` puis [[ACCES-AGENCE]]. AWEMA valide au cas par cas.

> 🔒 Sécurité & isolation (chaque agence = son fork, ses secrets) : [[13-securite-donnees]].
