# _data — Registre multi-clients de l'agence

Couche de données partagée par les outils web (dashboard, revue-visuels…).
**Aucune donnée fictive** : tout provient des fichiers réels des clients.

## Fichiers
| Fichier | Rôle |
|---|---|
| `build.py` | Agrège tous les clients → `agence.js` |
| `agence.js` | `window.AWEMA_REGISTRY = { clients:[…] }` (généré, consommé par les outils) |

## Source de vérité (par client)
`modules/<dept>/clients/<client>/_donnees/` :
| Fichier | Contenu | Requis |
|---|---|---|
| `client.json` | Profil : id, nom, secteur, lieu, statut, **handles réseaux**, chemins | ✅ (pour être listé) |
| `campagne.json` | Les contenus du plan (généré par le générateur du client) | optionnel |
| `reseaux.json` | **Présence digitale réelle** (audience, likes, commentaires, posts, top fans…) | optionnel |

## Régénérer le registre
```bash
python3 outils/_data/build.py
```

## Ajouter un client à l'agence
1. Créer `modules/<dept>/clients/<nouveau-client>/_donnees/client.json`
   (copier celui de `mon-client`, adapter id/nom/secteur/handles).
2. (Optionnel) ajouter `campagne.json` (via le générateur) et `reseaux.json`.
3. `python3 outils/_data/build.py` → le client apparaît dans le dashboard.

## Brancher les réseaux sociaux (présence digitale)

> Objectif : à partir des **profils du client**, obtenir audience, nb de posts, likes,
> commentaires, meilleurs fans, top posts, évolution d'audience.

Le contrat `reseaux.json` reste **null** tant qu'aucune source n'est branchée
(pas de chiffres inventés). Trois voies pour le remplir :

### Voie 1 — Meta Graph API (Facebook Page + Instagram Business) — recommandée
Données officielles et fiables. Pré-requis : une app Meta + un **token** Page/IG avec les
permissions `pages_read_engagement`, `instagram_basic`, `instagram_manage_insights`.
```bash
export META_TOKEN="EAAB..."; export FB_PAGE_ID="123..."; export IG_USER_ID="178..."
python3 scripts/connect-reseaux.py --meta modules/marketing/clients/mon-client
python3 outils/_data/build.py
```
Récupère : abonnés, nb posts, likes & commentaires agrégés, top posts.
*(TikTok / LinkedIn : via leurs APIs respectives — à ajouter dans le connecteur.)*

### Voie 2 — Outil de reporting tiers (ex. TwoMinuteReports, Meta Business Suite)
Connecter les comptes du client dans l'outil, **exporter un CSV**, puis :
```bash
python3 scripts/connect-reseaux.py --manuel modules/marketing/clients/mon-client export.csv
python3 outils/_data/build.py
```
CSV attendu (souple) : `reseau,abonnes,posts,likes,commentaires,portee`.

### Voie 3 — Saisie manuelle
Éditer directement `reseaux.json` du client (mêmes champs), passer `connecte: true`,
puis régénérer le registre.

> ⚠️ Le réseau du conteneur de génération peut bloquer `graph.facebook.com`
> (`host_not_allowed`). Lancer le connecteur depuis une machine ayant accès Internet,
> ou utiliser la voie 2/3.

## Ce que le dashboard affiche
- **Sélecteur de client** (tous les clients du registre).
- Vues **client-aware** (contenus, calendrier, scoring…) sur les données réelles.
- Vue **Présence digitale** : KPIs réseaux, top fans, top posts, évolution — ou états
  « à connecter » si `reseaux.json` n'est pas encore rempli.
- **Lien vers le visualiseur** (revue-visuels) du client sélectionné.
