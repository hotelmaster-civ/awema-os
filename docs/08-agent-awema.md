# 08 — Opérateur AWEMA (commande `/awema`)

> Un agent piloté en **langage naturel** pour connecter/maintenir les plateformes. Tu lui dis quoi
> faire ; il sait quelles plateformes existent, **ne demande que les valeurs qu'il ne connaît pas**,
> lance la procédure, **fait tourner (rotation) les mots de passe/tokens** et garde le **dernier en
> mémoire + fichier local** pour les prochaines fois.

## Utilisation

Dans Claude Code :
```
/awema connecte tiktok
/awema fais tourner le token meta
/awema statut des connexions
/awema (ré)autorise les comptes tiktok et lance la synchro
```
L'agent : identifie la plateforme → regarde ce qui manque → **te demande uniquement l'inconnu** →
enregistre → lance la connexion (ou te guide pour l'étape navigateur/GitHub) → confirme (valeurs masquées).

## Le moteur : `scripts/awema.py`

CLI utilisable aussi à la main :
```bash
python3 scripts/awema.py list                 # plateformes + état
python3 scripts/awema.py needs tiktok          # identifiants requis / manquants
python3 scripts/awema.py set tiktok TIKTOK_CLIENT_KEY=… TIKTOK_CLIENT_SECRET=…
python3 scripts/awema.py rotate meta META_TOKEN=…   # « incrémente » : nouveau courant, ancien en historique
python3 scripts/awema.py get tiktok            # valeurs masquées + taille d'historique
python3 scripts/awema.py history meta          # historique des identifiants (masqué)
python3 scripts/awema.py connect meta          # lance la connexion avec les identifiants stockés
python3 scripts/awema.py env tiktok            # lignes set/export prêtes à coller
```

## Mémoire des identifiants (le « dernier mot de passe en liste »)

- Fichier **local** : `.awema/credentials.json` — **gitignoré**, permissions `600`, jamais poussé.
- Par plateforme : un **`current`** (le dernier) + une **`history`** (les précédents, jusqu'à 10).
- Chaque `set`/`rotate` archive l'ancienne valeur avant d'écrire la nouvelle.

## Les plateformes : `scripts/awema-connectors.json`

Chaque plateforme déclare ses **identifiants** (`keys`), ses **commandes** (`connect`/`onboard`,
`sync_workflow`), sa procédure de **rotation** et sa **doc**. Déjà fournis : **Meta**, **TikTok**.

### Ajouter une plateforme (n'importe quel type : clé API, mot de passe, OAuth)
Ajoute une entrée sous `platforms` :
```json
"ma-plateforme": {
  "label": "Ma Plateforme",
  "keys": [{"name": "MAPLATEFORME_TOKEN", "secret": true, "github": "secret", "prompt": "Token API…"}],
  "commands": {"connect": "python3 scripts/mon-connecteur.py", "sync_workflow": "sync-xxx.yml"},
  "rotate": "Comment régénérer le token…",
  "doc": "docs/xx.md"
}
```
L'opérateur `/awema` la prend en charge automatiquement (statut, demande des manques, connexion, rotation).

## Sécurité

- Les secrets ne vivent **que** dans `.awema/` (local) et dans les **Secrets/Variables GitHub**.
- L'agent ne ré-affiche jamais un secret en clair (masquage), ne committe jamais `.awema/`.
- Pour brancher une plateforme à l'automatisation GitHub : reporte la valeur dans le Secret/Variable
  indiqué par le champ `github` de la clé, puis lance le `sync_workflow`.
