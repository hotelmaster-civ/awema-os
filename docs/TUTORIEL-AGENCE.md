# 🧭 Installer AWEMA pour ton agence — le guide complet (débutant)

> Pensé pour **débuter de zéro**. Tu ne tapes **aucune commande** : tu **cliques, colles, attends**.
> Compte ~30 min la première fois. Les étapes 0→2 se font sur **github.com** ; ensuite, **tout se passe
> dans ton navigateur**, sur le site d'AWEMA (une page interactive `tutoriel.html` reprend la suite avec
> des boutons cliquables).

## L'idée en une image 🐝

AWEMA est un **robot-assistant gratuit** pour ton agence. Il lui faut un **bureau** pour vivre et ranger ses
dossiers : ce bureau, c'est **GitHub** (gratuit). Ce guide = installer ton robot dans son bureau, lui donner
une **cervelle** (une IA gratuite), et le **brancher aux réseaux** de tes clients pour qu'il aille chercher
leurs vrais chiffres tout seul.

---

## Étape 0 — Créer un compte GitHub (gratuit)

GitHub = le « bureau en ligne » gratuit où vit ton AWEMA. Crée un compte : 👉 https://github.com/signup
**C'est bon quand** tu peux te connecter et voir ton tableau de bord GitHub.

## Étape 1 — Copier le projet pour toi (le « fork »)

Un **fork** = **ta copie privée** du projet, comme photocopier un classeur modèle pour le remplir avec **tes**
dossiers. Elle t'appartient ; tes clients et tes chiffres restent chez toi.
👉 **Bouton _Fork_** en haut à droite de la page du projet → _Create fork_.
**C'est bon quand** le projet apparaît sous **ton** nom : `ton-pseudo / AwemA-…`.

## Étape 1 bis — Activer l'automatisation (⚠️ à ne pas sauter)

Sur **toute copie (fork)**, GitHub **désactive l'automatisation par sécurité** — sinon rien ne
tournera tout seul (ni synchro, ni agents IA, ni publication programmée), sans aucun message d'erreur.
C'est **le piège le plus courant** : on croit que « ça tourne » alors que rien n'est allumé.

👉 Ouvre l'onglet **Actions** de ta copie. Si un bandeau jaune s'affiche
(« _Workflows aren't being run on this forked repository_ »), clique le bouton vert
**« I understand my workflows, go ahead and enable them »**.

**C'est bon quand** l'onglet Actions liste tes workflows (Publication, Sync, Agents…) au lieu du bandeau jaune.

> 💡 À refaire une seule fois par copie. Si tu ne publies rien pendant **60 jours**, GitHub rendort
> les tâches planifiées : reviens dans **Actions** et clique **« Enable workflow »** pour les réveiller.

## Étape 2 — Allumer ton site (« GitHub Pages »)

« Pages » transforme ta copie en **vrai site web** — c'est l'écran d'AWEMA que tu utiliseras tous les jours.
1. Dans **ta** copie → onglet **Settings**.
2. Menu de gauche → **Pages**.
3. Sous _Source_ : branche **`main`**, dossier **`/ (root)`** → **Save**.
4. Patiente 1-2 min → GitHub affiche **« Your site is live at … »**.

**Note bien ton adresse** `https://ton-pseudo.github.io/AwemA-…/` — c'est **l'adresse de ton AWEMA**.
Mets-la en favori et **ouvre-la**. À partir d'ici, fais tout depuis **ce site**.

> 💡 La suite est aussi disponible en **page interactive** sur ton site : ouvre **`…/tutoriel.html`** pour
> dérouler les étapes 3→13 avec des boutons cliquables et l'aide d'Awa.

## Étape 3 — Fabriquer la « clé d'accès » (le token)

Pour qu'AWEMA range des choses dans ton bureau GitHub **tout seul**, il lui faut une clé : un **token** (« PAT »).
À créer **une seule fois**. 👉 https://github.com/settings/personal-access-tokens/new
- **Token name** : `awema` · **Expiration** : 90 jours (ou plus).
- **Repository access** → _Only select repositories_ → **ta copie** du projet.
- **Permissions** → _Repository permissions_ → mets sur **Read and write** : **Contents**, **Actions**,
  **Variables**, **Secrets**.
- **Generate token** → **copie** la suite de caractères (tu ne la reverras plus).

> 🔒 Cette clé est **personnelle**. Ne la partage pas. AWEMA la garde **sur ton appareil**, jamais dans le projet.

## Étape 4 — Présenter la clé à AWEMA

Sur ton site → page **Mise en route** (`configuration.html`) → **« 🔗 Connecter mon GitHub »** → colle la clé,
ton pseudo et le nom de ta copie → valide.
**C'est bon quand** tu vois **« ✅ Connecté »**. C'est l'étape clé : ensuite, AWEMA fait le reste tout seul.

## Étape 5 — Donner une « cervelle » (une IA gratuite)

**Groq** est gratuit et parfait pour démarrer : crée un compte, génère une clé (👉 https://console.groq.com/keys),
copie-la. Sur la Mise en route → étape **« Cerveau — une IA »** → choisis **Groq** → colle la clé →
**« ⚡ Enregistrer la clé IA »**.
**C'est bon quand** tu vois « ✅ branché » (ou une fenêtre qui ouvre le bon écran GitHub avec ta clé déjà copiée).
> Sans IA, AWEMA marche quand même (le feed « 3 choses à faire » fonctionne) ; l'IA sert aux analyses poussées.

## Étape 6 — Mettre AWEMA à ta marque

Page **`setup.html`** : nom, logo, couleurs de **ton** agence. Tout l'écran s'adapte.

## Étape 7 — Ajouter tes clients

Page **`nouveau-client.html`** : un formulaire crée la fiche (le nom suffit). Aucun code.

## Étape 8 — Remplir l'« ADN marketing » de chaque client

Page **`memoire.html`** : ton, produits, cible, interdits. Plus c'est rempli, plus les idées de l'IA sont **justes**.

## Étape 9 — Brancher les réseaux de tes clients

Tu ne branches que ceux dont tu as besoin. Chaque page guide pas à pas :
| Réseau | Page | En bref |
|---|---|---|
| Facebook & Instagram | `connect-facebook.html` | 1 « token Meta » → toutes les Pages. Coller → « Découvrir mes Pages ». |
| TikTok | `connect-tiktok.html` | Coller 3 clés, puis **clic → Authorize → retour → Finaliser**. |
| YouTube | `connect-youtube.html` | Le plus simple : coller une clé API → « Synchroniser ». |
| LinkedIn | `connect-linkedin.html` | Comme TikTok : coller les clés → Authorize → Finaliser. |
| WhatsApp | `connect-whatsapp.html` | Coller token + identifiants WhatsApp Business. |

> ⚠️ Pour gérer de **vrais comptes de clients**, Meta/TikTok/LinkedIn exigent souvent une **app vérifiée +
> validation** de leur côté. C'est une exigence des plateformes, pas d'AWEMA — incompressible.

## Étape 10 — Lancer la récupération

Clique le bouton **« Synchroniser »** (ou « Découvrir mes Pages ») du réseau branché. **Patiente 1-2 min**, puis
ouvre le cockpit : les chiffres réels apparaissent.

## Étape 11 — Piloter depuis ton cockpit

Page **`outils/dashboard/index.html`** : audience réelle, commentaires à répondre, meilleurs posts, cadence, et
le feed **« 3 choses à faire aujourd'hui »**.

## Étape 12 — Ensuite, ça tourne tout seul

AWEMA **resynchronise périodiquement** et fait travailler ses agents **chaque jour et après chaque synchro**. Ton
cockpit reste à jour sans intervention. Tu ouvres ton AWEMA quand tu veux : c'est déjà frais.

> ⚠️ **Condition** : que l'automatisation ait bien été activée (Étape 1 bis). Et si tu laisses ta copie
> **inactive plus de 60 jours**, GitHub met les tâches planifiées en veille — un passage dans l'onglet
> **Actions** → **« Enable workflow »** les relance.

## Étape 13 — Si quelque chose ne marche pas (c'est normal)

- **Message rouge ?** Souvent une clé mal collée → recommence l'étape (ça ne casse rien).
- **Pas sûr d'avoir réussi ?** Cherche le **✅ vert** / « enregistré / lancé ».
- **Une synchro a échoué ?** GitHub → onglet **Actions** → clique le run rouge → la ligne en erreur (souvent
  « secret manquant » = un token à reposer).
- **Perdu sur une page ?** Clique **Awa 🐝** en bas à droite : elle explique la page.

---

🎉 **Ton agence tourne sur AWEMA.** Ajoute d'autres clients, branche d'autres réseaux, laisse les agents travailler.
Pour piloter AWEMA **en langage naturel depuis Claude** (avancé) → [`docs/16-piloter-avec-claude-mcp.md`](16-piloter-avec-claude-mcp.md).
