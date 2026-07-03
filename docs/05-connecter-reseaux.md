# 05 — Connecter les réseaux sociaux (présence digitale)

> Objectif : afficher dans le dashboard, **par client**, les vraies données (audience, posts,
> likes, commentaires, meilleurs fans, top posts, évolution). **Zéro donnée inventée** : le
> dashboard reste en « à connecter » tant qu'une source réelle n'est pas branchée.

## Comment ça marche (architecture)

```
Réseaux du client ──(autorisation/token)──▶ connecteur ──▶ reseaux.json ──▶ build.py ──▶ dashboard
   FB / IG / ...          UNE FOIS         connect-reseaux.py   (par client)   agence.js   (affiche)
```

Le dashboard ne fait que **lire** `reseaux.json`. Tout l'enjeu est de **remplir** ce fichier.

---

## Point clé sur l'autonomie

Aucune plateforme (Facebook, Instagram…) ne donne ses chiffres sans **autorisation du
propriétaire du compte** (un *token* / OAuth). Il n'existe pas de raccourci magique : il faut
**une fois** accorder un accès. Ensuite, ça peut tourner **tout seul**.

État des intégrations branchées sur ce projet :
- **`two_minutes_reports` (MCP)** : connecté mais **n'expose pas d'outil** appelable → inutilisable en l'état.
- **PostHog (MCP)** : OK pour l'**analytics produit/web** (funnel, RDV, événements site) — **pas** les likes/fans sociaux.
- **Google Drive (MCP)** : OK pour **lire un CSV** d'export que vous déposez.
- **GitHub (MCP/Actions)** : OK — **support de l'autonomie** (voir Voie A).
- **Meta Graph API** : nécessite **votre token** + Internet.

---

## Voie A — Autonome : GitHub Action + token Meta (recommandé)

Le runner GitHub a accès à Internet (le sandbox de génération, non). Un workflow planifié
récupère les données et met à jour le dépôt — **sans intervention**.

### Pas à pas (UN seul token → TOUTES les Pages)
1. **Créer une app Meta + un token utilisateur** (https://developers.facebook.com) avec :
   `pages_show_list`, `pages_read_engagement`, `read_insights`, `instagram_basic`,
   `instagram_manage_insights`.
   ➡️ **Démarche détaillée : [`06-obtenir-token-meta.md`](06-obtenir-token-meta.md).**
   *(Pas besoin d'IDs par Page : le script les découvre via `me/accounts`.)*
2. GitHub → **Settings → Secrets and variables → Actions** → **Secret** `META_TOKEN`.
3. Onglet **Actions → « Sync présence digitale (réseaux) » → Run workflow**
   (ou planifié chaque lundi 06:00 UTC).
4. Le workflow exécute `connect-reseaux.py --meta-all` → **crée/maj un client par Page**
   → `build.py` → **commit** des `reseaux.json` + `agence.js`.
5. Rouvrir le dashboard → **toutes les Pages apparaissent comme clients**, vue **Présence
   digitale** = chiffres réels.

> Fichier : `.github/workflows/sync-reseaux.yml`.
> 🔐 Le token ne vit **que** dans le Secret GitHub (jamais dans le dépôt). Régénérable à tout
> moment sans rien casser. Les tokens longue durée expirent (~60 j) → rafraîchir.

### En local (équivalent)
```bash
export META_TOKEN="EAAB..."
python3 scripts/connect-reseaux.py --meta-all     # toutes les Pages
python3 outils/_data/build.py
```

---

### Portée / impressions (permission `read_insights`)

Par défaut, `portee` reste `null` (audience, posts, likes, commentaires et top posts
fonctionnent sans). Pour remonter la **portée Page (28 j)** et le **taux d'engagement** :

1. Régénérer le `META_TOKEN` en cochant **`read_insights`** dans l'Explorateur de l'API Graph
   (pas d'App Review pour **tes propres** pages dont tu es admin).
2. Mettre à jour le Secret `META_TOKEN` → **Run workflow**.

Le script essaie plusieurs métriques (les noms valides changent selon la version de l'API) :
- **Portée réelle (reach)** : `page_impressions_unique` / `page_impressions` → `…facebook.portee`.
  ⚠️ **Ces métriques sont dépréciées en API v21** (`(#100) must be a valid insights metric`) :
  la portée reste donc `null` tant que Meta ne les réexpose pas (ou via une version d'API plus ancienne).
- **Vues de la Page (28 j)** : `page_views_total` → `…facebook.vues` (disponible en v21) → `global.vues`.

Le **taux d'engagement** n'est calculé **que** si la vraie portée est disponible (jamais à partir
des simples vues, pour ne pas afficher un chiffre trompeur).

> ⚠️ Le **« meilleur fan » nominatif n'est plus exposé** par l'API Graph (liste des fans fermée
> par Meta). On dispose des **top posts**, des **vues de Page**, des **likes/commentaires** —
> pas d'un classement individuel des fans, ni (en v21) de la portée/reach.

### Cockpit community management (Facebook, automatique)

À chaque sync `--meta-all`, en plus des abonnés/posts/likes, le connecteur dérive **pour chaque
Page** (données réelles, jamais inventées), **à partir des posts** (pas des insights) :
- **Réactions détaillées** par type (👍 ❤️ 🤗 😂 😮 😢 😡).
- **Commentaires à répondre** : commentaires sans réponse de la Page (inbox CM) + liens directs.
- **Abonnés les plus actifs** : top commentateurs (le vrai « meilleur fan », dérivé des commentaires).
- **Cadence** : dernier post, jours depuis, posts/semaine (sur 30 j), posts (30 j).
- **Meilleur créneau** : jour/heure où l'engagement est le plus fort.
- **Types de contenu** : engagement moyen par format (photo / vidéo / lien / statut).
- **Taux d'engagement par abonné** : engagement moyen par post ÷ abonnés.
- **Vues de la Page (28 j)** : `page_views_total` (seule métrique insights encore valide en v21).
- **Évolution de l'audience** : un point horodaté est ajouté à chaque sync → vraie courbe dans le temps.

> ⚠️ **Limites API v21** : Meta a déprécié la quasi-totalité des métriques *insights*
> (`page_impressions*`, `post_impressions*`, `page_fan_adds/removes` → `(#100) invalid metric`).
> La **portée/reach** (Page et post) et la **croissance détaillée** ne sont donc **plus exposées**
> → non affichées (zéro donnée inventée). Tout le reste est dérivé des posts et reste disponible.

Tout s'affiche dans le dashboard, vue **Présence digitale**.

## Voie B — Simple : export CSV (Meta Business Suite / TwoMinuteReports)

Sans app Meta : exporter les chiffres depuis l'outil du client, puis :
```bash
python3 scripts/connect-reseaux.py --manuel modules/marketing/clients/<client> export.csv
python3 outils/_data/build.py
```
CSV attendu (souple) : `reseau,abonnes,posts,likes,commentaires,portee`
```
reseau,abonnes,posts,likes,commentaires,portee
facebook,5230,42,1875,240,41000
instagram,3110,38,2950,180,28000
```
> Variante « Drive » : déposez le CSV sur Google Drive ; je peux le **lire via le MCP Drive**
> et générer `reseaux.json` pour vous.

---

## Voie C — Manuel : éditer le fichier

Éditer directement `modules/marketing/clients/<client>/_donnees/reseaux.json`
(mêmes champs), passer `"connecte": true`, puis `python3 outils/_data/build.py`.

---

## Et le funnel / les conversions (PostHog)

Likes & fans = réseaux (voies ci-dessus). Le **tunnel** (messages WhatsApp, RDV, ventes) se
mesure mieux avec **PostHog** : il faut **émettre des événements** depuis le site / le tunnel
(`message_recu`, `rdv_pris`, `vente`). Une fois ces événements présents, je peux construire le
funnel réel via le MCP PostHog. Tant qu'ils n'existent pas, le tunnel reste en « — ».

---

## Ce dont j'ai besoin de vous pour démarrer
- **Voie A** : confirmer que vous avez créé le `META_TOKEN` + les IDs, et les avoir mis en
  Secret/Variables GitHub. Je peux alors déclencher et valider.
- **Voie B** : un **CSV** (ou son lien Drive).
- **PostHog** : me dire quels **événements** existent déjà (ou en faire émettre).

> Tableau récap des champs attendus : voir `outils/_data/README.md` et le contrat
> `reseaux.json` de chaque client.
