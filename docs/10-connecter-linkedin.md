# 10 — Connecter LinkedIn

> Guide visuel équivalent : **`connect-linkedin.html`** (boutons + liens directs).
> LinkedIn est la plateforme la plus encadrée — ce guide va jusqu'au jeton OAuth.

## Ce qu'on récupère
Statistiques d'une **Page entreprise** (pas un profil perso) : abonnés, impressions, engagement —
fusionnées dans la fiche de l'entité, **à la charte bleue LinkedIn** (`#0A66C2`), à côté de
Facebook, TikTok et YouTube.

## Pré-requis
- Une **Page entreprise** LinkedIn dont tu es **administrateur**.
- Un compte sur le **portail développeur** LinkedIn.

## Étapes
1. **Page entreprise** — crée-la si besoin : <https://www.linkedin.com/company/setup/new/> ; note son URL
   (`linkedin.com/company/<slug>`).
2. **Créer l'app** — <https://www.linkedin.com/developers/apps/new> → *Create app* ; associe la Page entreprise.
3. **Vérifier la Page** — onglet *Settings* → *Verify* (à ouvrir en tant qu'admin de la Page).
4. **Produits** — onglet *Products* : ajoute *Sign In with LinkedIn using OpenID Connect* et
   *Community Management API* (analytics de Page). ⚠️ Ce dernier peut nécessiter une **validation LinkedIn**.
5. **Auth** — onglet *Auth* : copie **Client ID** + **Client Secret** ; ajoute la redirection OAuth
   `https://<owner>.github.io/<repo>/oauth.html`.
6. **OAuth** — scopes `r_organization_social`, `rw_organization_admin`. L'opérateur `/awema` construit
   l'URL d'autorisation, tu cliques « Autoriser », il échange le code contre un **access token**.

## Sécurité
- `LINKEDIN_CLIENT_ID` (public) et `LINKEDIN_CLIENT_SECRET` (**Secret GitHub**, jamais en clair, jamais commité).
- Les tokens OAuth vont dans la Variable `LINKEDIN_TOKENS` (gérée par l'onboarding) / `.awema/` en local.

## En attendant l'accès live
Tant que la *Community Management API* n'est pas validée, on enregistre l'**URL de Page** + un nombre
d'**abonnés saisi à la main** dans `client.json` (`reseaux.linkedin`), puis on bascule sur les données
live dès l'accès accordé — sans rien changer côté dashboard (il lit déjà `par_reseau.linkedin`).

## Opérateur
```
/awema connecte linkedin pour <client>
```
L'opérateur ne demande que l'inconnu (Client ID/Secret, URL de Page) et lance la procédure.
