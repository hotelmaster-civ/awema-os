# 09 — Auto-hébergement & personnalisation

> AWEMA n'est pas un SaaS centralisé : **chaque agence héberge sa propre instance** en
> *forkant* ce projet, puis la personnalise entièrement (nom, logo, charte, liens, clients).
> Tes données et tes accès restent chez toi.

## Le principe en une phrase

Tu modifies **un seul fichier** — [`config/agence.json`](../config/agence.json) — et toute
l'application (page d'accueil, dashboard, guides, couleurs, liens GitHub) s'adapte
automatiquement. La génération passe par `outils/_data/build.py` qui produit
`outils/_data/config.js` (`window.AWEMA_CONFIG`), lu par chaque page via
`outils/_data/apply.js`.

```
config/agence.json   ──►  build.py  ──►  outils/_data/config.js  ──►  apply.js  ──►  toutes les pages
   (tu édites ça)              (génère)        (window.AWEMA_CONFIG)     (applique)     (s'adaptent)
```

## 1. Forker le projet

1. Ouvre le dépôt sur GitHub et clique **Fork** (en haut à droite).
2. Choisis ton compte et, si tu veux, un nom de dépôt à ta marque (ex. `mon-agence`).
3. Clone ton fork en local :
   ```bash
   git clone https://github.com/<ton-pseudo>/<ton-repo>.git
   cd <ton-repo>
   ```

## 2. Personnaliser

Trois façons, au choix :

### a) Le formulaire visuel (le plus simple)
Ouvre **`setup.html`** (depuis ta page d'accueil → « Personnaliser mon agence »). Remplis
le nom, le logo, la charte et ton dépôt GitHub : un aperçu live te montre le rendu, puis
tu **télécharges `agence.json`** que tu places dans `config/`.

### b) L'opérateur `/awema` (en langage naturel)
Dans Claude Code :
```
/awema setup nom="Baoulé Digital" github.owner=monpseudo github.repo=mon-agence charte.ciel=#1DA1F2
```
L'opérateur écrit `config/agence.json` **et** régénère `config.js` tout seul.
Sans argument, `python3 scripts/awema.py setup` affiche la config courante.

### c) À la main
Édite [`config/agence.json`](../config/agence.json) puis lance :
```bash
python3 outils/_data/build.py
```

### Champs disponibles
| Clé | Rôle |
|---|---|
| `nom` | Nom court (logo texte, titres, footer) |
| `nom_complet` | Raison sociale complète |
| `tagline` | Sous-titre (« Centre de pilotage ») |
| `slogan` | Phrase d'accroche |
| `initiales` | 1–3 lettres du logo (auto depuis `nom` si vide) |
| `contact` | Email de contact |
| `github.owner` / `github.repo` | Ton fork — réécrit les liens « Code source » et GitHub Pages |
| `charte.{nuit,ciel,gold,violet,mint,pink}` | Couleurs (variables CSS `--nuit`, `--ciel`, …) |

## 3. Mettre en ligne (GitHub Pages)

1. Commit + push ta config :
   ```bash
   git add config/agence.json outils/_data/config.js
   git commit -m "Personnalisation de mon agence"
   git push
   ```
2. Sur ton fork : **Settings → Pages** → Source = branche `main`, dossier **`/ (root)`**.
   Le fichier `.nojekyll` (déjà présent) permet de servir les dossiers `_data` / `_design`.
3. Ton instance est en ligne sur `https://<ton-pseudo>.github.io/<ton-repo>/`.

## 4. Brancher tes accès (réseaux)

Dans **Settings → Secrets and variables → Actions** de ton fork, ajoute selon les réseaux
que tu connectes :

| Accès | Type | Pour |
|---|---|---|
| `META_TOKEN` | Secret | Facebook / Instagram (toutes tes Pages) |
| `YOUTUBE_API_KEY` | Secret | YouTube (stats publiques de chaîne) |
| `TIKTOK_TOKENS` | Variable | Refresh tokens TikTok par client |
| `TIKTOK_PAT` | Secret | Écriture auto de la Variable `TIKTOK_TOKENS` |

Les workflows `.github/workflows/sync-reseaux.yml` et `sync-tiktok.yml` rafraîchissent les
données et committent les résultats. Guides détaillés : [05](05-connecter-reseaux.md),
[06](06-obtenir-token-meta.md), [07](07-connecter-tiktok.md).

> 🔒 **Sécurité.** Aucun token ne vit dans le dépôt. Les secrets restent dans GitHub
> Secrets/Variables ; en local, l'opérateur les garde dans `.awema/` (gitignoré). Voir
> [08 — Agent AWEMA](08-agent-awema.md).

## 5. Onboarder tes clients

- **Formulaire** : `nouveau-client.html` (génère la fiche + checklist de connexion).
- **Opérateur** : `/awema nouveau client …` ou
  `python3 scripts/awema.py client new auto nom="…" fb_page_id="…" yt_handle="@…"`.
- Connecte ensuite leurs réseaux via les guides `connect-tiktok.html` / `connect-youtube.html`.

## Récupérer les mises à jour du projet d'origine (optionnel)

Pour profiter des nouvelles fonctionnalités sans perdre ta personnalisation :
```bash
git remote add upstream https://github.com/awema-test/awema-os.git
git fetch upstream
git merge upstream/main      # ton config/agence.json reste le tien
```
Ta config et tes clients sont à toi ; seul le code commun est mis à jour.
