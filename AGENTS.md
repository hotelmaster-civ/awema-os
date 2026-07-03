# AGENTS.md — Onboarding express pour agents (IA & humains)

> Lu en priorité par tout agent IA. Contexte minimal pour être opérationnel en < 5 min.
> **Lis-le entièrement avant d'agir.** La référence stable, c'est [`docs/FOUNDATION/`](docs/FOUNDATION/README.md).

---

## 1. Où es-tu ?

Tu opères dans **AWEMA OS** — le système d'exploitation open source d'une **agence digitale assistée par
IA**. Architecture : un **Kernel** de concepts universels **sans logique métier** + des **modules**
métier. **Un seul module est officiel : Marketing.** Tu interviens dans un module, sur des missions
clients. Ton travail doit être **réutilisable par le prochain agent** : rangé, documenté, conforme.

> ⚠️ « Agent » a deux sens ici : **toi** (l'agent qui opère le dépôt) et les **agents IA du produit**
> (Analyste, Stratège, Créatif, Rétrospective, Proactivité) qui produisent des propositions. Leur contrat :
> [`docs/FOUNDATION/05-AGENT_MODEL.md`](docs/FOUNDATION/05-AGENT_MODEL.md).

## 2. Règles d'or (toujours)

1. **Range avant de produire.** Le bon dossier (module → client → sous-dossier numéroté). Jamais de
   fichier « en vrac » à la racine.
2. **Documente ce que tu produis.** Chaque dossier a un `README.md`. Mets-le à jour.
3. **Additif d'abord. Plugin avant Kernel.** Étends en **ajoutant** (connecteur, agent, artefact JSON) ;
   ne mute jamais la donnée réelle existante. Touche au Kernel seulement si un concept universel manque,
   et **via un ADR**.
4. **Données réelles, zéro fiction.** N'invente aucune métrique. Toute donnée affichée est **traçable**.
5. **Propose, ne décide pas.** Les sorties d'agents sont des **propositions** sourcées ; l'**humain
   décide**. Une action engageante exige une validation explicite.
6. **Aucun secret dans le dépôt.** Secrets en GitHub Secrets/Variables ou `.awema/` (gitignoré).
7. **Respecte la charte** (`docs/04-charte-graphique.md`) et sépare **méthode** (`methodologie/`,
   `templates/`) et **livrable** (`clients/<client>/`).
8. **Industrialise le volume** (générateur déterministe `_generateur/` au-delà de ~20 éléments).
9. **Definition of Done** avant de livrer (`docs/03-conventions.md` +
   `docs/FOUNDATION/03-DESIGN_PRINCIPLES.md`). Pas de brouillon.

## 3. Avant toute décision structurante

Applique le **test de recevabilité** ([Constitution](docs/FOUNDATION/00-CONSTITUTION.md)) : utile
aujourd'hui ? cohérent avec la vision ? ajoute de la complexité ? peut attendre ? Si une fonctionnalité
**peut attendre, ne l'implémente pas.** Toute décision structurante → **ADR**
([`docs/FOUNDATION/08-ARCHITECTURE_DECISIONS.md`](docs/FOUNDATION/08-ARCHITECTURE_DECISIONS.md)).

## 4. Carte mentale du dépôt

```
docs/FOUNDATION/       → socle stable (Kernel, principes, plugins, agents, données, gouvernance, ADR)
docs/                  → produit (PRD, ROADMAP, PLAN) + guides (conventions, charte, connexions, sécurité)
modules/<module>/ → un MODULE : README + methodologie/ + templates/ + clients/<client>/
outils/                → cockpit, revue-visuels, _data/build.py (registre)
scripts/               → awema.py (opérateur), awema_ai.py, run-agent.py, connect-reseaux.py + manifestes
config/ · tests/ · .github/workflows/
```

## 5. Opérateur `/awema` (langage naturel)

Connecte/maintient les plateformes ; **ne demande que l'inconnu**. Ex. : `/awema connecte tiktok`,
`/awema fais tourner le token meta`, `/awema statut des connexions`. Moteur : `scripts/awema.py`
(mémoire des identifiants dans `.awema/credentials.json`, gitignoré). Détail : `docs/08-agent-awema.md`.

## 6. Démarrer une tâche dans le module Marketing (checklist)

- [ ] Lire `modules/marketing/README.md` (rôle & méthode)
- [ ] Lire le **brief client** : `clients/<client>/00-brief/` · la **charte** : `docs/04-charte-graphique.md`
- [ ] Suivre la **Méthode Universelle de Production Éditoriale**
      (`modules/marketing/methodologie/methode-universelle-production-editoriale.md`)
- [ ] Produire dans les sous-dossiers numérotés ; mettre à jour les `README.md`
- [ ] Vérifier la *Definition of Done* avant de livrer

## 7. Régénérer & vérifier

```bash
python3 outils/_data/build.py              # régénère le registre après toute édition de données/config
python3 -m unittest discover -s tests      # harnais anti-régression (doit rester vert)
```

## 8. Outils & intégrations (selon session)

Google Drive/Docs/Sheets/Slides · Canva · Gmail/Calendar · PostHog · GitHub (MCP). Si un outil n'est pas
connecté, produis le livrable **en fichier dans le dépôt** (source de vérité) ; la publication est secondaire.

## 9. Fin de session (obligatoire)

Laisse le projet **cohérent** : doc à jour · `ROADMAP.md` · ADR · `PROJECT_SELF_DESCRIPTION.md` si besoin.
Rapport : fait / reste à faire / risques / dette / décisions / prochaines étapes.

---

_Range, documente, industrialise. Propose — l'humain décide._
