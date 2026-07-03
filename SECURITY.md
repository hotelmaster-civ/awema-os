# Politique de sécurité — AWEMA OS

## Modèle de sécurité (à connaître avant de forker)

AWEMA est **auto-hébergé** : ton instance vit dans **ton** dépôt GitHub (fork) et est servie
par **GitHub Pages**. Il n'y a **aucun serveur AWEMA** ni base de données tierce.

- **Les secrets ne sont jamais dans le dépôt.** Clés IA et tokens réseaux vivent dans
  **GitHub → Settings → Secrets and variables → Actions**. Le dépôt (public ou privé) ne
  contient aucune clé. Les workflows n'affichent jamais un secret dans leurs logs.
- **Le jeton d'accès (PAT) reste dans ton navigateur.** Quand tu « Connectes GitHub » depuis
  le dashboard, ton PAT fin est stocké dans le `localStorage` de **ce** navigateur uniquement,
  envoyé exclusivement à `api.github.com`, jamais loggé. Sur un **ordinateur partagé**, utilise
  **Réglages → 🔒 Se déconnecter** avant de partir.
- **Données réelles, zéro fiction.** Les métriques affichées proviennent des API officielles
  des plateformes. Rien n'est inventé.
- **OAuth côté serveur.** L'échange du `code` OAuth (TikTok/Meta/LinkedIn) se fait dans une
  GitHub Action ; le `client_secret` reste un Secret GitHub, jamais exposé au navigateur.

## Bonnes pratiques pour ton instance

1. Utilise un **PAT fin** (fine-grained) limité à **ton** dépôt, avec le minimum de droits
   (Contents + Actions + Variables/Secrets selon les workflows utilisés). Renouvelle-le régulièrement.
2. Garde ton dépôt **privé** si tu y stockes des données clients réelles (le fork est privé par
   défaut si tu le choisis). Le template public (`main`) ne contient qu'un client de **démo**.
3. Ne **committe jamais** de token : le `.gitignore` exclut déjà `*_tokens.out`, `.awema/`, les
   visuels reçus des clients et les `data.js` mono-client. Ne force pas leur ajout.
4. Ne merge **jamais** une branche contenant des données clients réelles dans une branche
   destinée à être publique. Publie le template via `python3 scripts/publier-template.py --push`
   (il neutralise et refuse de pousser de vraies données).
5. Pour repartir de zéro : **Réglages → Zone dangereuse → Réinitialiser** (double confirmation).

## Signaler une vulnérabilité

Merci de **ne pas** ouvrir d'issue publique pour une faille de sécurité.

Contacte le mainteneur en privé (adresse dans `config/agence.json` de l'instance d'origine, ou
via la fiche de contact du dépôt amont). Décris : le composant touché, un scénario de
reproduction, et l'impact estimé. Une réponse est visée sous quelques jours.

Périmètre particulièrement sensible (merci d'y prêter attention) :
- toute **XSS** dans les pages du dashboard/visualiseur/rapport/oauth (le PAT est en localStorage) ;
- toute fuite d'un **Secret** dans les logs d'un workflow ;
- tout contournement des **gardes** de réinitialisation ou de publication du template.

## Ce qui est déjà en place

- Échappement systématique des contenus externes (API sociales, sorties d'IA, commentaires) —
  module partagé `outils/_design/awema-format.js` (`esc`/`escAttr`/`safeUrl`), testé.
- Filtrage des schémas d'URL (`safeUrl` : seuls `http(s)`/`mailto` — pas de `javascript:`).
- Double garde sur la réinitialisation (`REINITIALISER` côté script **et** workflow).
- Garde anti-fuite dans la publication du template (refuse toute vraie donnée client).
- Harnais de tests : **117 tests Python + 40 tests JS** (job CI **Tests**).
