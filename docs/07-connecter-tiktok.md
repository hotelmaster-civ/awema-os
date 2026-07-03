# 07 — Connecter TikTok (présence digitale)

> Objectif : afficher dans le dashboard, **par client**, les vraies données TikTok (abonnés,
> vidéos, vues/likes/commentaires/partages, top vidéos). Données réelles uniquement.

## Ce qu'il faut savoir (≠ Meta)

TikTok n'a **pas** de « un token → tous les comptes ». Chaque compte client doit **autoriser
une fois** (OAuth). Le `refresh_token` obtenu est **rotatif** (un nouveau à chaque
rafraîchissement) → on le stocke dans une **Variable** GitHub que le workflow réécrit tout
seul après chaque run.

```
Compte TikTok ──(OAuth, 1 fois)──▶ refresh_token ──▶ Variable TIKTOK_TOKENS
        │                                                     │
        └────────── workflow sync-tiktok.yml ◀────────────────┘  (rafraîchit + réécrit le token roté)
                          │
                          ▼  reseaux.json (bloc tiktok) ──▶ build.py ──▶ dashboard
```

## Étape 1 — Créer l'app TikTok (une fois)
1. https://developers.tiktok.com → **Manage apps** → **Connect an app**.
2. Ajoute les produits **Login Kit** et **Display API**.
3. Scopes : `user.info.basic`, `user.info.profile`, `user.info.stats`, `video.list`.
4. **Redirect URI** : mets une URL que tu contrôles (ex. `https://localhost/cb` suffit pour
   l'onboarding manuel — tu copieras juste le `code` depuis l'URL de redirection).
5. Note le **Client key** et le **Client secret**.

> ⚠️ Hors compte développeur, TikTok demande souvent une **App review** pour `user.info.stats`
> + `video.list`. En **sandbox**, ça marche pour les comptes ajoutés comme testeurs.

## Étape 2 — Autoriser chaque compte (récupérer un refresh_token)

### 🟢 Méthode automatisée (recommandée) — `scripts/tiktok-onboard.py`
Un assistant qui automatise **tout** sauf le clic « Authorize » (qu'OAuth impose) : il capture le
code (petit serveur local, **zéro copier-coller**), échange le token, propose le slug, **boucle**
sur plusieurs comptes, et **met à jour la Variable `TIKTOK_TOKENS` tout seul**.

Pré-requis (une fois) : dans l'app TikTok → *URL properties / Login Kit*, ajoute la Redirect URI
`http://127.0.0.1:8723/callback` (et `http://localhost:8723/callback`). Si TikTok refuse
localhost, lance avec `--paste` (utilise la redirect github.io existante).

```bash
# Windows : set ... / mac-linux : export ...
set TIKTOK_CLIENT_KEY=...
set TIKTOK_CLIENT_SECRET=...
set GH_PAT=...                 # PAT fin « Variables: Read and write » → MAJ auto de la Variable
python scripts/tiktok-onboard.py          # capture auto
python scripts/tiktok-onboard.py --paste  # repli (coller l'URL)
```
Déroulé : connecte-toi au compte voulu dans le navigateur → Entrée → autorise → l'assistant
enregistre le compte, puis demande « un autre ? ». À la fin, la Variable est à jour → **Run
workflow**. Pour ajouter d'autres comptes plus tard, relance le script (il fusionne avec
l'existant). **Change de compte TikTok dans le navigateur entre chaque autorisation.**

### Méthode manuelle (équivalent, pas à pas)
Pour **chaque** compte TikTok à suivre :

1. Ouvre dans le navigateur (en étant connecté au bon compte TikTok) :
   ```
   https://www.tiktok.com/v2/auth/authorize/?client_key=TON_CLIENT_KEY
     &scope=user.info.basic,user.info.profile,user.info.stats,video.list
     &response_type=code&redirect_uri=TA_REDIRECT_URI&state=x
   ```
   (tout sur une seule ligne, sans espaces)
2. Approuve. TikTok redirige vers `TA_REDIRECT_URI?code=XXXXX&...` → **copie la valeur `code`**
   (valable quelques minutes).
3. Échange ce code contre un refresh_token avec le helper fourni :
   ```bash
   export TIKTOK_CLIENT_KEY="..." TIKTOK_CLIENT_SECRET="..."
   python3 scripts/connect-reseaux.py --tiktok-auth "<code>" "TA_REDIRECT_URI"
   ```
   → il affiche le **`refresh_token`** (valable ~365 j) à coller dans la Variable.

## Étape 3 — Renseigner les secrets + la variable (GitHub)
**Settings → Secrets and variables → Actions** :
- **Secret** `TIKTOK_CLIENT_KEY`
- **Secret** `TIKTOK_CLIENT_SECRET`
- **Secret** `TIKTOK_PAT` — un *fine-grained PAT* sur CE dépôt avec la permission
  **« Variables : Read and write »** (sert à réécrire le token roté après chaque run).
- **Variable** `TIKTOK_TOKENS` — JSON associant **le slug du client** (nom du dossier dans
  `modules/marketing/clients/<slug>`) à son refresh_token :
  ```json
  {"mon-client": "rft.abc123...", "autre-client": "rft.def456..."}
  ```

## Étape 4 — Lancer
**Actions → « Sync TikTok (présence digitale) » → Run workflow** (ou planifié lundi 06:30 UTC).
Le workflow : rafraîchit chaque token → récupère profil + vidéos → fusionne dans `reseaux.json`
(sans toucher aux données Facebook) → **réécrit la Variable** avec les tokens rotés → `build.py`
→ commit. Le dashboard affiche une carte **TikTok** par client connecté.

## En local (équivalent)
```bash
export TIKTOK_CLIENT_KEY="..." TIKTOK_CLIENT_SECRET="..."
export TIKTOK_TOKENS='{"mon-client":"rft.abc123..."}'
export TIKTOK_TOKENS_OUT=tiktok_tokens.out      # tokens rotés (à reporter dans la Variable)
python3 scripts/connect-reseaux.py --tiktok-all
python3 outils/_data/build.py
```

## Données récupérées
- **Profil** : abonnés, nombre de vidéos, likes cumulés.
- **Par vidéo (20 dernières)** : vues, likes, commentaires, partages → top vidéos, engagement.
- Fusionnées avec Facebook : un client peut afficher **FB + TikTok** côte à côte.

> 🔐 Le `refresh_token` ne vit **que** dans la Variable GitHub (réécrite automatiquement) et
> n'est **jamais** committé (`tiktok_tokens.out` est dans `.gitignore`). Client key/secret et
> PAT restent en Secrets.
