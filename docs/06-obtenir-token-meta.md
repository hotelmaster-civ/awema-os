# 06 — Obtenir un token Meta + les IDs (Facebook Page & Instagram Business)

> Guide pas-à-pas pour récupérer les 3 valeurs attendues par le connecteur :
> **`META_TOKEN`**, **`FB_PAGE_ID`**, **`IG_USER_ID`**.
> Réutilisable pour **chaque client** de l'agence.

---

## 0. Pré-requis (à vérifier AVANT)

1. **Vous êtes admin de la Page Facebook du client.**
   Si ce n'est pas votre Page : le client doit vous ajouter dans
   **Meta Business Suite → Paramètres → Accès → Personnes/Partenaires** (rôle *Admin* ou
   *Analyste*). Sans cela, aucun token ne pourra lire la Page.
2. **Le compte Instagram du client est un compte *Professionnel* (Business/Créateur)** et il
   est **relié à la Page Facebook**.
   Vérif : appli Instagram → *Paramètres → Compte professionnel*, et la Page liée.
   ⚠️ Un compte Instagram *personnel* n'expose **aucune** statistique via l'API.
3. Un compte développeur Meta (gratuit) : https://developers.facebook.com (se connecter avec
   le Facebook qui administre la Page).

---

## 1. Créer une app Meta

1. https://developers.facebook.com → **My Apps** → **Create App**.
2. **Use case** : choisir **« Other »** → **Type : Business**.
3. Donner un nom (ex : `AWEMA Reporting`), associer un **Business Portfolio** si demandé.
4. L'app est créée → noter l'**App ID** et l'**App Secret**
   (*App settings → Basic*). Gardez l'App Secret **confidentiel**.

---

## 2. Obtenir un token (le plus simple : Graph API Explorer)

1. Ouvrir **https://developers.facebook.com/tools/explorer**
2. En haut à droite : sélectionner votre **app**.
3. Menu **« Utilisateur ou Page »** → **« Obtenir un token d'accès utilisateur »**.
4. **Autorisations → « Ajouter une autorisation »** — ajouter une par une :
   - `pages_show_list`
   - `pages_read_engagement`
   - `read_insights`
   - `instagram_basic`
   - `instagram_manage_insights`
   - *(optionnel)* `business_management`
5. Cliquer **Generate Access Token** → fenêtre Facebook → **autoriser** et **cocher la Page**
   du client → le token apparaît dans **« Token d'accès »**.

> ❗ Erreur *« An active access token must be used »* (code 2500) = le champ token est
> **vide**, il faut générer le token (étape 5). C'est normal au départ.

> ❗ Aucune Page proposée à l'étape 5 ? Vous n'êtes **pas admin d'une Page Facebook** pour ce
> client → créez la Page ou faites-vous ajouter admin (pré-requis 0).

> 💡 Le token de l'Explorateur est **court (~1–2 h)** : suffisant pour un **premier test**.
> Pour le rendre durable → étape 5 (token longue durée).

### Méthode rapide pour les IDs (sans parser `me/accounts`)
Après avoir généré le token utilisateur : recliquer **« Utilisateur ou Page »** et
**sélectionner la Page** → le token devient un **Page token** (= votre `META_TOKEN`). Puis,
dans la barre de requête en haut :
```
me?fields=id,name,fan_count,followers_count   → id = FB_PAGE_ID (+ abonnés)
me?fields=instagram_business_account          → instagram_business_account.id = IG_USER_ID
```

---

## 3. Récupérer FB_PAGE_ID et le Page token

Dans le Graph API Explorer (ou n'importe quel navigateur en remplaçant le token), appeler :

```
GET  me/accounts
```
Réponse (extrait) :
```json
{ "data": [
  { "name": "La Grande Vision",
    "id": "1234567890",                ← FB_PAGE_ID
    "access_token": "EAAB...PAGE..." } ← Page token (à utiliser comme META_TOKEN)
]}
```
- **`id`** = **`FB_PAGE_ID`**.
- **`access_token`** = le **Page token** → ce sera votre **`META_TOKEN`**.

---

## 4. Récupérer IG_USER_ID (compte Instagram Business)

Toujours dans l'Explorer, avec le **Page token** :

```
GET  {FB_PAGE_ID}?fields=instagram_business_account
```
Réponse :
```json
{ "instagram_business_account": { "id": "17841400000000000" },  ← IG_USER_ID
  "id": "1234567890" }
```
- **`instagram_business_account.id`** = **`IG_USER_ID`**.
- Si ce champ est **absent** → l'Instagram n'est pas en compte *Professionnel* relié à la
  Page (revoir le pré-requis 2).

---

## 5. Rendre le token durable (recommandé — évite de recommencer toutes les heures)

Le token de l'Explorer est court. Pour un **Page token non-expirant** :

1. **Échanger** le token utilisateur court contre un **token utilisateur longue durée**
   (~60 jours) :
   ```
   GET https://graph.facebook.com/v21.0/oauth/access_token
       ?grant_type=fb_exchange_token
       &client_id={APP_ID}
       &client_secret={APP_SECRET}
       &fb_exchange_token={TOKEN_COURT}
   ```
   → renvoie un `access_token` longue durée.
2. **Rappeler** `me/accounts` **avec ce token longue durée** → le `access_token` de la Page
   renvoyé est alors **un Page token qui n'expire pas** (jusqu'à changement de mot de passe
   ou révocation). C'est **lui** que vous mettez en `META_TOKEN`.

> Vérifier la validité / l'expiration d'un token :
> **https://developers.facebook.com/tools/debug/accesstoken/** (collez le token → *Debug*).

---

## 6. Tester rapidement (facultatif mais conseillé)

Dans un terminal connecté à Internet :
```bash
# abonnés Page
curl "https://graph.facebook.com/v21.0/{FB_PAGE_ID}?fields=name,fan_count,followers_count&access_token={META_TOKEN}"
# abonnés Instagram
curl "https://graph.facebook.com/v21.0/{IG_USER_ID}?fields=username,followers_count,media_count&access_token={META_TOKEN}"
```
Si ça renvoie des chiffres → tout est prêt.

---

## 7. Où mettre les valeurs (pour l'automatisation)

GitHub → **Settings → Secrets and variables → Actions** :
| Type | Nom | Valeur |
|---|---|---|
| **Secret** | `META_TOKEN` | le Page token (étape 5) |
| **Variable** | `FB_PAGE_ID` | étape 3 |
| **Variable** | `IG_USER_ID` | étape 4 |
| **Variable** | `CLIENT_DIR` | `modules/marketing/clients/mon-client` |

Puis : onglet **Actions → « Sync présence digitale » → Run workflow**.
(Détails : [`docs/05-connecter-reseaux.md`](05-connecter-reseaux.md).)

> En local plutôt qu'en Action :
> ```bash
> export META_TOKEN="EAAB..."; export FB_PAGE_ID="..."; export IG_USER_ID="..."
> python3 scripts/connect-reseaux.py --meta modules/marketing/clients/mon-client
> python3 outils/_data/build.py
> ```

---

## 8. Pièges fréquents

| Symptôme | Cause / solution |
|---|---|
| `me/accounts` ne renvoie pas la Page | Vous n'êtes pas admin de la Page, ou permission `pages_show_list` non accordée |
| `instagram_business_account` absent | IG pas en compte Pro **ou** pas relié à la Page |
| Token expire vite | Vous utilisez le token court de l'Explorer → faire l'étape 5 |
| `(#10) Application does not have permission` | Permission manquante ou **App Review** requis pour un usage hors de vos propres Pages |
| Données vides après quelques semaines | Page token révoqué (mot de passe changé) → régénérer |

### Note « App Review »
Pour vos **propres** Pages / celles où vous êtes admin et ajouté au Business, l'**accès
standard** suffit (pas de revue). Pour exploiter à grande échelle des Pages de tiers, Meta
peut exiger une **App Review** des permissions. Pour démarrer avec La Grande Vision (Page
gérée par vous), l'accès standard est suffisant.

---

## Récap — ce qu'on cherche
| Variable | Provenance |
|---|---|
| `META_TOKEN` | Page token (étapes 3 + 5) |
| `FB_PAGE_ID` | `me/accounts` → `id` (étape 3) |
| `IG_USER_ID` | `{FB_PAGE_ID}?fields=instagram_business_account` → `.id` (étape 4) |
