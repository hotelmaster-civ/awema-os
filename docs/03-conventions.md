# 03 — Conventions & Qualité

Ces conventions s'appliquent à **tous** les départements et toutes les missions.

## Langue & ton

- Langue de travail et de livraison : **français**.
- Ton : professionnel, clair, premium, orienté résultats.

## Nommage des fichiers & dossiers

- `kebab-case`, **sans accents**, sans espaces : `calendrier-editorial.csv`.
- Préfixe numérique pour l'ordre : `00-brief`, `01-strategie`, …
- Dossiers techniques préfixés `_` : `_generateur/`, `_exports-pdf/`.

## Formats

| Besoin | Format | Pourquoi |
|---|---|---|
| Documentation, stratégie, contenus | **Markdown** (`.md`) | lisible, versionnable, convertible |
| Données tabulaires (calendrier, scoring) | **CSV** (`.csv`) | importable dans Google Sheets / Excel |
| Génération de volume | **Python 3** (`.py`) | régénérable, sans dépendance lourde |
| Livrables finaux | **PDF** | présentable à la direction |

> Les CSV sont conçus pour être **importés tels quels dans Google Sheets**. Les colonnes de
> formules contiennent la formule Google Sheets prête à coller.

## Structure obligatoire d'un dossier

- Chaque dossier contient un `README.md` décrivant : son rôle, son contenu, comment
  l'utiliser/régénérer.

## Génération de volume (industrialisation)

- Dès qu'un livrable dépasse ~20 éléments répétitifs, on écrit un **générateur** dans
  `_generateur/` plutôt que de tout rédiger à la main.
- Le générateur encode : personas, piliers, charte, gabarits de texte, prompts.
- Le générateur doit être **déterministe** (même entrée → même sortie) et **documenté**.

## Definition of Done (DoD)

Un livrable est « fini » seulement si :

1. ✅ Il est **rangé** dans le bon dossier.
2. ✅ Il est **documenté** (README à jour).
3. ✅ Il **respecte la charte graphique** (couleurs, polices, ton).
4. ✅ Il est **cohérent** avec la stratégie (personas, piliers, KPI).
5. ✅ Il est **directement exploitable** (pas de placeholder, pas de « TODO »).
6. ✅ Il porte un **KPI** ou un moyen de mesure quand c'est pertinent.
7. ✅ Le volume est **régénérable** par script si applicable.

## Conventions Git

- Branches de travail dédiées (ex : `claude/...`).
- Commits clairs et descriptifs, en français.
- Pas de Pull Request sans demande explicite.

## Niveau de qualité attendu

Chaque document doit sembler réalisé par une **agence marketing premium**. Pas d'ébauche :
du livrable professionnel, illustré, cohérent, automatisable, prêt à être présenté à la
direction.
