# 13 — Sécurité, confidentialité & isolation des données

> Réponse à : « mes données clients sont embarquées dans le projet ; je ne veux pas que ceux qui me
> rejoignent ou testent aient accès à mes données ni à celles des autres. Comment sécuriser chaque compte ? »

## 1. Le modèle d'isolation (le point clé)
AWEMA est **auto-hébergé** : **chaque agence/pilote possède son PROPRE fork**, avec ses **propres**
données, dans **son** dépôt. Conséquence directe :

- **Les pilotes ne reçoivent jamais ton dépôt.** Ils partent de la **copie d'accueil** (`scripts/preparer-copie-beta.py`),
  qui est **vidée de toute donnée réelle** (vérifié : 0 fuite) et ne contient qu'**un client de DÉMO** étiqueté.
- **Un pilote ne voit pas les données d'un autre** : chaque pilote a son fork séparé. Il n'y a **aucun
  espace partagé** où les données se croisent.
- **Tes 27 clients restent dans TON instance.** Personne d'autre n'y a accès *via le produit*.

```
TON dépôt (tes 27 clients)  ──fork──►  ❌ jamais partagé tel quel
Copie d'accueil (0 donnée, 1 démo) ──►  Pilote A (son fork, ses données)
                                   └─►  Pilote B (son fork, ses données)   ← A et B ne se voient pas
```

## 2. Le vrai risque à connaître : dépôt **public** = données **publiques**
GitHub Pages gratuit exige un dépôt **public**. Si **ton** dépôt est public, alors le registre
`outils/_data/agence.js` (audience, posts, commentaires…) est **lisible par tous** sur le web.
**Ce ne sont pas des secrets** (pas de token), mais ce sont des **données business privées**.

**Recommandations (par ordre de simplicité) :**
1. ✅ **Garde ton instance de production en dépôt PRIVÉ.** Pour des Pages privées, GitHub demande un
   plan **Pro/Team** — sinon : héberge le tableau de bord **en local** (`file://`) ou sur un hébergeur
   avec **contrôle d'accès** (Netlify/Cloudflare Pages + mot de passe). Le code marche à l'identique.
   > ⚠️ **Coût caché à connaître avant de passer en privé** : sur un dépôt **public**, les minutes
   > GitHub Actions sont **illimitées et gratuites** ; sur un dépôt **privé**, le plan Free en donne
   > **2 000/mois** — or la seule publication programmée (cron toutes les 15 min) en consomme ~1 500 à
   > 3 000/mois, plus les syncs et agents. En privé, il faut donc soit un plan payant, soit **espacer le
   > cron de `publish.yml`** (ex. toutes les heures : `0 * * * *`), soit accepter l'arrêt des workflows
   > en fin de mois. Choix documenté ici pour trancher en connaissance de cause.
2. ✅ **Sépare partage de code et données.** Si tu veux que des gens contribuent au *code*, fais-le sur
   un dépôt public **sans tes données** (ou via la copie d'accueil) ; garde le dépôt **avec données** privé.
3. ✅ **Ne partage que la copie d'accueil** aux pilotes (elle est déjà propre). Ne leur donne jamais
   accès en écriture/lecture à ton dépôt de production.

> Vérifie à tout moment qu'une copie est propre : génère-la et cherche tes clients — il ne doit rien
> rester. `scripts/preparer-copie-beta.py` retire les clients réels, neutralise la config, et ne laisse
> qu'un client de démo.

## 3. Sécuriser chaque compte connecté (tokens & clés)
Les **identifiants** (tokens, clés API) sont la partie réellement sensible. Invariants AWEMA :

- 🔒 **Aucun secret dans le dépôt.** Jamais. Ni en clair, ni « caché ».
- Les secrets vivent **uniquement** dans :
  - **GitHub → Secrets** (pour l'automatisation : `META_TOKEN`, `YOUTUBE_API_KEY`, `TIKTOK_CLIENT_SECRET`,
    `LINKEDIN_TOKEN`, `ANTHROPIC_API_KEY`…). Les Secrets ne sont **jamais** exposés, même en dépôt public.
  - Le **store local `.awema/`** (gitignoré, `chmod 600`) géré par l'opérateur — avec **historique** des rotations.
- **Un compte = un token, rotatif.** Renouvelle régulièrement et au moindre doute :
  `awema rotate <plateforme> <CLE>=<nouvelle>` (garde l'ancienne en historique), puis mets à jour le Secret GitHub.
- **Scopes minimaux.** Ne demande que les permissions nécessaires (lecture d'insights, pas plus).
- **TikTok / LinkedIn (OAuth)** : refresh/redirections gérés par les assistants ; les tokens rotatifs
  sont resauvegardés via un PAT fin (permissions minimales).

### En cas de fuite d'un identifiant
1. **Révoque** la clé/token côté plateforme (Meta, TikTok, Google, LinkedIn, Anthropic…).
2. Génère-en une nouvelle, `awema rotate …`, mets à jour le Secret GitHub.
3. Si un secret a transité ailleurs (chat, capture…), **considère-le compromis** et régénère-le.

## 4. Données clients & vie privée (RGPD / lois locales)
- Ne traite que des comptes que tu es **autorisé** à gérer (admin de la Page).
- Le projet ne stocke **aucune donnée fictive** ; il stocke des **métriques agrégées** + des extraits de
  commentaires publics (pour le community management). Évite d'y mettre des données personnelles sensibles.
- Pour un partage public, préfère les **métriques agrégées** ; garde les exemples nominatifs en privé.

## 5. Checklist sécurité (à cocher avant d'ouvrir la bêta)
- [ ] Mon instance de production est **privée** (ou locale / accès contrôlé).
- [ ] Les pilotes reçoivent **uniquement** la copie d'accueil (propre, vérifiée).
- [ ] Aucun secret n'est dans le dépôt (`git log -p` ne révèle aucun token).
- [ ] `.gitignore` couvre `.awema/`, `tiktok_tokens.out`, et tout fichier de clés.
- [ ] Tokens à **scopes minimaux**, **rotation** documentée.
- [ ] Pilotes informés des **conditions** (docs/11) : ne pas committer de secrets, ne traiter que leurs comptes.
