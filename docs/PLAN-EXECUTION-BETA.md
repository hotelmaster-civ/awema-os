# PLAN D'EXÉCUTION — Route vers la bêta (module par module, zéro régression)

> Vision : [[PRD-AWEMA]] · Roadmap : [[ROADMAP]]. Chaque module est **autonome**, **additif**,
> livrable seul, avec **critères d'acceptation** et **garde-fou anti-régression**. On n'enchaîne pas
> un module tant que le précédent n'est pas vert.

## Règles d'or (anti-régression)
1. **Additif d'abord** : les agents écrivent de **nouveaux** fichiers (`_agents/*.json`, `memoire.json`,
   `marche.json`). Ils **ne modifient jamais** `reseaux.json` → la donnée réelle existante est intouchable.
2. **Skip gracieux** : toute brique IA s'auto-désactive sans `ANTHROPIC_API_KEY` (comme les connecteurs
   sans token) → CI et usage hors-ligne restent verts.
3. **Schéma validé** : chaque sortie d'agent est validée contre un schéma avant écriture (sinon, on
   n'écrit pas et on loggue).
4. **Sourcé & horodaté** : chaque artefact porte `source`, `genere_le`, `modele`, et `provenance`
   (sur quelles données réelles il s'appuie). *Zéro fiction.*
5. **Le cockpit dégrade proprement** : si un `_agents/*.json` manque, l'UI affiche « pas encore généré »,
   jamais une erreur.
6. **Un test par invariant** : merge réseaux, consolidation, parsing connecteurs, schéma d'agent.

---

## Module M0 — Substrat IA & garde-fous  *(socle, requis)*
**But** : pouvoir faire tourner un agent et l'afficher, sans risque.
**Livrables**
- `tests/` (stdlib `unittest`) : `test_merge.py` (fusion multi-réseaux préserve les autres réseaux),
  `test_consolidation.py` (totaux/engagement), `test_schemas.py` (valide les schémas d'agents).
  Lançable `python3 -m unittest discover tests`.
- `scripts/awema_ai.py` : client Claude minimal (stdlib `urllib`), `chat(messages, schema=None,
  model=...)`, lit `ANTHROPIC_API_KEY` (env / `.awema`), **renvoie `None` proprement sans clé**,
  remonte le vrai message d'erreur API. Sortie **structurée** (JSON forcé via instruction + validation).
- `scripts/agents.json` : manifeste d'agents (`{id, role, entrees[], sortie_schema, declencheur, modele}`).
- `scripts/run-agent.py <agent> [client|--all]` : charge entrées → appelle `awema_ai` → valide → écrit
  `modules/.../<client>/_donnees/_agents/<agent>.json`.
- Cockpit : helper JS `loadAgent(client, nom)` + composant « feed d'agents » (vide propre).
**Schéma de sortie (commun)** : `{ "agent","genere_le","modele","provenance":{...},"items":[...] }`.
**Acceptation** : `run-agent.py --all` sans clé → skip propre ; avec clé → écrit un JSON valide ;
`unittest` vert. Le cockpit affiche « pas encore généré » si absent.
**Garde-fou** : tests M0 + agents purement additifs.

---

## Module M1 — Mémoire Marketing  *(carburant)*
**But** : chaque client a une `memoire.json` exploitable par les agents.
**Livrables**
- Schéma `memoire.json` : `{identite, charte, ton, personas[], produits[], faq[], campagnes[],
  historique[], performances_synthese, references_visuelles[]}` (tout optionnel, se remplit progressivement).
- **Seed** : extension de `nouveau-client.html` / `setup.html` (quelques champs : ton, personas, produits,
  FAQ) + `awema client memoire <slug> KEY=…`.
- `build.py` : exposer `memoire` (résumé non sensible) dans le registre pour le cockpit.
- Cockpit : panneau « Mémoire » (lecture + lien d'édition) sur la fiche client.
**Acceptation** : créer un client → renseigner mémoire → visible au cockpit ; agents M2–M4 la consomment.
**Garde-fou** : `memoire.json` est un **nouveau** fichier ; absence = comportement actuel inchangé.

---

## Module M2 — Agent Analyste ⭐  *(premier wow)*
**But** : répondre *pourquoi ? que faire ? que reproduire ?* sur la présence réelle.
**Livrables**
- Agent `analyste` (dans `agents.json`) : entrées `reseaux.json` + `memoire.json` → `_agents/analyste.json`
  `{items:[{type:"insight|reco", titre, explication, preuve:{metrique,valeur,variation}, action?}]}`.
- Cockpit : panneau **« Pourquoi & Que faire »** sur la vue Présence digitale (rend `items`, étiquette
  « proposition IA », montre la **preuve** chiffrée réelle).
**Acceptation** : sur un client à données réelles (ex. *La Grande Vision*), l'Analyste produit ≥ 3 insights
sourcés + ≥ 2 recommandations actionnables, en langage clair.
**Garde-fou** : tests de schéma ; lecture seule des données réelles.

---

## Module M3 — Agent Stratège ⭐
**But** : transformer la perf en **plan**.
**Livrables**
- Agent `stratege` → `_agents/stratege.json` `{cadence_recommandee, meilleures_heures[],
  objectifs[], plan_editorial:[{date, format, angle, reseau}]}` (s'appuie sur `meilleur_creneau`,
  `types_contenu`, `cadence` déjà calculés + mémoire).
- Cockpit : section « Plan recommandé » (Vue d'ensemble / Calendrier) + bouton « Pousser vers le plan ».
**Acceptation** : plan cohérent avec les vraies perfs (heures/format issus des données), éditable.
**Garde-fou** : additif ; n'écrit pas `campagne.json` sans validation humaine explicite.

---

## Module M4 — Agent Créatif ⭐
**But** : produire des publications prêtes, calées sur ce qui marche.
**Livrables**
- Agent `creatif` → `_agents/creatif.json` `{idees:[{hook, script, format, reseau, prompt_image,
  variantes[]}]}` (entrées : mémoire + `types_contenu`/`top_posts`).
- **Réaligner la génération d'image sur Claude** (ou laisser le prompt prêt à coller) — retirer la
  dépendance OpenAI du chemin bêta.
- Visualiseur : action « **Générer 3 publications** » → affiche les propositions → « Valider » écrit
  dans `campagne.json` (humain dans la boucle).
**Acceptation** : 1 clic → 3 publications cohérentes avec la marque (mémoire) et la perf ; validables.
**Garde-fou** : écrit dans `campagne.json` **uniquement** sur validation ; tests de schéma.

---

## Module M5 — Proactivité (Command Center) ⭐
**But** : passer de « on consulte » à « AWEMA propose ».
**Livrables**
- `scripts/run-agent.py actions-du-jour --all` : agrège `analyste/stratege/creatif` (+ alertes dérivées :
  baisse d'engagement, cadence en retard, format gagnant) → `_agents/actions-du-jour.json`.
- Cockpit : **feed proactif en tête** du Command Center (« 3 choses à faire aujourd'hui »), chaque item
  **actionnable** (1 clic → agent / validation / lien).
- Workflow `.github/workflows/agents.yml` (planifié + `dispatch`, skip sans clé) : exécute les agents,
  commite les `_agents/*.json`, régénère le registre.
**Acceptation** : à l'ouverture, l'agence voit ≥ 3 actions réelles, sourcées, cliquables.
**Garde-fou** : nouveau workflow indépendant ; n'impacte pas `sync-reseaux`/`sync-tiktok`.

---

## Module M6 — Onboarding → wow < 30 min
**But** : le pilote ressent le « wow » immédiatement.
**Livrables**
- Jeu de **données démo « wow »** (1 client fictif *étiqueté DÉMO*, isolé de la promesse « zéro fiction »
  réelle : clairement marqué « exemple ») dans la **copie d'accueil**, pour que le cockpit + agents
  s'illustrent dès l'arrivée, avant même de connecter un réseau.
- `onboarding.html` : étape « Voir une démo IA » + bascule « Maintenant, mes vraies données ».
- Mesure du temps-jusqu'au-wow (checklist) ; alignement `preparer-copie-beta.py`.
**Acceptation** : un nouveau pilote atteint une 1ʳᵉ reco IA en < 30 min (démo immédiate, réel ensuite).
**Garde-fou** : la démo est **étiquetée** et **séparée** des données réelles (cohérent avec l'ADN).

---

## Séquencement & dépendances
```
M0 (socle+tests) ─► M1 (mémoire) ─► M2 Analyste ─► M3 Stratège ─► M4 Créatif ─► M5 Proactivité ─► M6 Onboarding-wow
                         └────────────── M2..M4 consomment la mémoire ──────────────┘
```
- **Chemin critique du wow** : M0 → M2 → M5 (Analyste + feed proactif). M1 améliore tout ; M3/M4
  amplifient. Si le temps manque, **livrer M0+M1+M2+M5** donne déjà l'effet « ça me dit quoi faire ».
- Chaque module finit par : tests verts + démo manuelle (Playwright screenshot) + commit isolé.

## Définition de « terminé » (par module)
1. Code + schéma + manifeste à jour. 2. Skip gracieux sans clé. 3. Tests d'invariants verts.
4. Rendu cockpit vérifié (capture). 5. Doc concernée mise à jour. 6. Commit atomique, branche de travail.

## Post-bêta (rappel, hors plan détaillé ici)
Veille / Intelligence Marketing (`marche.json`), Modérateur, Chef de projet, Instagram, LinkedIn live,
collaboration, couche analytique/séries temporelles. Détail à ouvrir après les retours des 20 pilotes.
