# PRD / North Star — AWEMA

> **Document de référence produit.** Toute décision d'architecture se mesure à une seule question :
> *« Est-ce que cela rapproche AWEMA du meilleur système d'exploitation pour agences digitales
> assisté par IA ? »* Si non → on ne le développe pas.
>
> Ce PRD **fusionne** la vision « OS d'agence assistée par IA » avec l'existant. Il ne remplace pas
> l'ADN ; il l'étend. Roadmap opérationnelle : [[ROADMAP]]. Plan d'exécution : [[PLAN-EXECUTION-BETA]].

## 1. Positionnement
**AWEMA = le système d'exploitation d'une agence digitale assistée par IA.**
Le community management n'est que le **premier module**. Le dashboard n'est pas un tableau de
statistiques : c'est un **centre de commandement** qui réunit progressivement réseaux, CM, IA,
contenus, calendrier, clients, campagnes, veille, analytics, collaboration, automatisation.

**Différenciateur principal — il change :**
- ❌ avant : « agréger plusieurs réseaux »
- ✅ désormais : **« faire travailler une équipe d'agents IA spécialisés »**.
- L'IA ne **répond** pas. Elle **travaille** : elle observe, analyse, propose, prépare.

**Promesse pilote (les 20)** : en ouvrant le cockpit, l'agence comprend *immédiatement* « **je gagne
plusieurs heures par semaine** ». Le « wow » vient du **cockpit + IA + recommandations + simplicité** —
**pas** de la quantité de graphiques.

## 2. ADN — invariants non négociables
Auto-hébergement · zéro SaaS obligatoire · **Git = source de vérité** · GitHub Pages · HTML/CSS/JS
vanilla · **Python stdlib uniquement** · données réelles · **zéro fiction** · aucun secret dans le
dépôt · fork simple · personnalisation par config · **opérateur IA en langage naturel**.

## 3. Décision d'architecture fondatrice — « Agents = jobs, JSON = vérité, cockpit = renderer »
C'est le point qui réconcilie « équipe d'agents IA » avec l'ADN. **ADR-001 :**

- Un **agent** = un **script Python** (stdlib + **un** appel HTTPS LLM) déclenché par **GitHub Actions**
  (planifié / `workflow_dispatch`) **ou** localement via l'opérateur `/awema`. L'agent **est** le
  back-end : éphémère, sans serveur permanent.
- **Entrées** : la **mémoire** du client (`memoire.json`), la **présence réelle** (`reseaux.json`),
  le plan (`campagne.json`), et plus tard le **marché** (`marche.json`).
- **LLM** : **agnostique** — n'importe quel fournisseur **compatible OpenAI** (Groq, Gemini, OpenRouter,
  Cerebras, Mistral, GitHub Models, Ollama local…) **ou Anthropic** (Claude). Registre + options
  **gratuites** : `config/ia-providers.json` (cf. [[12-connecter-ia]]). Clé en **GitHub Secret** / `.awema`
  local. Runner = Internet. **Skip gracieux si aucune clé** (comme les autres connecteurs). Zéro verrou fournisseur.
- **Sorties** : des **artefacts JSON déterministes**, versionnés, écrits dans `_agents/` par client
  (`_agents/analyste.json`, `_agents/creatif.json`, …). Auditable, diff-able, réversible.
- **Cockpit (statique)** : lit ces artefacts et les **rend proactivement** (feed « Actions du jour »,
  recommandations, bouton « Générer ? »). Le dashboard montre le **travail des agents**, pas des chiffres bruts.
- **Humain dans la boucle** : les sorties d'agents sont des **propositions** horodatées et **sourcées**
  (provenance). L'humain valide / rejette → réécrit le JSON. *Zéro fiction* : un agent **annote** la
  donnée réelle ; ses propositions sont étiquetées « proposition IA », jamais présentées comme des faits.

> Conséquence : ajouter de l'IA **n'introduit qu'un seul secret** (`ANTHROPIC_API_KEY`) et **aucun
> serveur**. Les agents sont **additifs** (nouveaux fichiers `_agents/*.json`) → **zéro régression**
> sur les données existantes.

## 4. L'équipe d'agents (cible) — priorité bêta marquée ⭐
| Agent | Rôle | Entrées → Sortie | Bêta |
|---|---|---|---|
| **Analyste** ⭐ | Explique les résultats : *pourquoi ? que faire ? que reproduire ?* | reseaux+mémoire → `analyste.json` (insights, recommandations) | **OUI** |
| **Stratège** ⭐ | Planning éditorial, fréquence, meilleures heures, objectifs | perf+mémoire → `stratege.json` | **OUI** |
| **Créatif** ⭐ | Idées, hooks, scripts, publications, prompts image/vidéo, variantes | mémoire+perf → `creatif.json` (+ action « Générer ») | **OUI** |
| **Veille** | Concurrents, hashtags, tendances, créateurs, secteurs → alertes/opportunités | comptes publics → `marche.json` | post-bêta |
| **Modérateur** | Trie commentaires/DM/réactions (urgent/prospect/client/plainte/spam), prépare réponses | ingestion → `moderateur.json` | post-bêta |
| **Chef de projet** | Suit validations, tâches, publications, campagnes ; coordonne les agents | `_agents/*` → `projet.json` | post-bêta |

## 5. Proactivité — d'« on consulte » à « AWEMA propose »
Un agrégateur des sorties d'agents → `_agents/actions-du-jour.json`, rendu en **tête du Command Center** :
> « Le taux d'engagement baisse depuis 12 jours. » · « Vos vidéos courtes performent +38 %. »
> « Je recommande 3 publications demain. **Souhaitez-vous les générer ?** »

Chaque alerte est **réelle** (dérivée des données), **sourcée**, **actionnable** (1 clic → agent/validation).

## 6. Mémoire Marketing (par client) — le carburant des agents
Nouveau fichier `_donnees/memoire.json` par client, construit **progressivement** (seed à l'onboarding,
enrichi par les agents) : identité, charte, ton, personas, produits, FAQ, campagnes, historique,
publications, images/vidéos (références), performances synthétisées. **Tous les agents la lisent.**
Extension naturelle du modèle (`client.json` / `reseaux.json` / `campagne.json`).

## 7. Module Intelligence Marketing (indépendant, post-bêta)
`reseaux.json` = *ma présence*. Ajout de `_donnees/marche.json` = *mon marché* : concurrents (pages
publiques via les **mêmes connecteurs**), hashtags, formats, horaires, couleurs, audience, **parts de
voix**. Alimenté par l'agent **Veille**. Onglet « Marché » au dashboard. Conçu comme **module
découplé** (activable/désactivable) — il ne doit pas alourdir le cœur bêta.

## 8. Points d'extension long terme (à **prévoir**, **ne pas** implémenter)
Le JSON reste la source de vérité. On documente — sans coder — les coutures pour plus tard :
- **Séries temporelles** : `_data/timeseries/<client>/<metric>.ndjson` (append-only ; `evolution_audience`
  en est l'amorce) → migrable vers SQLite/DuckDB/Parquet **sans casser** le JSON.
- **Cache analytique** : couche de lecture optionnelle, jamais source de vérité.
- **Adaptateur de source** : chaque connecteur déclare ses **capacités** → absorber la mort d'APIs
  (cf. Meta v21) sans réécrire l'UI.

## 9. Analyse de l'existant (doublons / inutile / incohérences)
**Doublons / divergences**
- La roadmap vivait dans `AWEMA-OS.md`. → **[[ROADMAP]] devient la source unique** ; `AWEMA-OS.md`
  n'en garde qu'un pointeur + le journal.
- Bêta « 20 CM » (docs/11) vs « 20 agences pilotes » (nouvelle vision) → unifié en **« 20 pilotes
  (agences / CM) »**.
- `nouveau-client.html` (onboarding *client*) vs `onboarding.html` (onboarding *pilote*) : rôles
  distincts → on clarifie, on garde les deux.

**À déprioriser / repousser (hors cœur « OS IA »)**
- Vues dashboard à moitié faites (Calendrier, Scoring A→E, Tunnel WhatsApp, Automatisation) →
  **marquées « bientôt »** pour la bêta (qualité > quantité ; ne pas montrer d'inachevé).
- Export PDF (`html2pdf.py`, `export-pdf.sh`, `csv2html.py`) : utilitaires d'agence, **pas** un wow
  bêta → repoussés.
- `generer-image-openai.py` (OpenAI) **incohérent** avec « Claude par défaut » → **aligné sur Claude**
  (ou repoussé) lors du module Créatif.

**Incohérences corrigées par cette vision**
- « présence + marché » promis, marché absent → **module Intelligence Marketing** + agent Veille.
- Engagement *par abonné* (mort du reach v21) → **étiquetage « dégradation gracieuse »** explicite.
- LinkedIn live bloqué (email pro) → hors chemin critique bêta ; « prêt, activable ».

## 10. Critères de succès de la bêta
1. Un pilote atteint le **premier « wow » en < 30 min** (onboarding → données réelles → 1ʳᵉ reco IA).
2. À l'ouverture du cockpit : **« 3 choses à faire aujourd'hui »** réelles et actionnables.
3. Sur un client : l'**Analyste** explique *pourquoi* + *quoi faire* en langage clair.
4. En 1 clic : le **Créatif** propose 3 publications (hooks + scripts + prompts) calées sur ce qui marche.
5. Sentiment dominant attendu : *« ça me fait gagner des heures et ça me dit quoi faire »*.

Qualité > quantité. **Peu de fonctionnalités, extrêmement bien finies.**
