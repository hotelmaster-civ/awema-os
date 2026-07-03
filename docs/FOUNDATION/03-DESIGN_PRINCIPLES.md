---
titre: 03 — DESIGN PRINCIPLES
statut: stable
maj: 2026-06-27
---

# 03 — Principes de conception

> Comment on construit. Ces principes traduisent la Constitution en règles d'ingénierie.

## ADN technique (invariants non négociables)
1. **Auto-hébergement, zéro SaaS.** Chaque agence forke et héberge **son** instance.
2. **Git = source de vérité.** L'état vit dans des fichiers JSON versionnés, pas dans une base.
3. **GitHub Pages** sert le front statique (`.nojekyll`, depuis la racine).
4. **Front : HTML/CSS/JS vanilla.** Aucune dépendance, fonctionne aussi en `file://`.
5. **Back : Python stdlib uniquement** pour le cœur. Toute exception (ex. Playwright) reste **hors
   cœur** et optionnelle.
6. **Aucun secret dans le dépôt.** Secrets en GitHub Secrets/Variables ou `.awema/` (gitignoré, `600`).
7. **Données réelles, zéro fiction.** On n'invente jamais une métrique.
8. **Personnalisation par config.** Un seul `config/agence.json` repersonnalise toute l'instance.
9. **Opérateur IA en langage naturel** (`/awema`) qui ne demande que l'inconnu.

## Règles de conception
- **Additif d'abord.** Étendre en **ajoutant** des fichiers (nouveau connecteur, nouvel agent, nouvel
  artefact JSON), jamais en mutant la donnée réelle existante. → **zéro régression**.
- **Plugin > Kernel.** Avant de toucher au Kernel, se demander si un plugin suffit. En général, oui.
- **Skip gracieux.** Toute brique (IA, connecteur) s'auto-désactive proprement sans sa clé/token ;
  CI et usage hors-ligne restent verts.
- **Dégradation gracieuse.** Une métrique indisponible affiche « source indisponible », jamais un `null`
  muet ni une erreur.
- **Déterminisme.** À entrée égale, sortie égale (générateurs, agrégateurs). Facilite tests et diff.
- **Traçabilité.** Tout artefact porte `source`, `genere_le`, `modele`, `provenance`.
- **Humain dans la boucle.** Une action engageante (écrire un plan, publier) exige une validation
  humaine explicite.
- **Simplicité d'abord.** Moins de code, plus de clarté. Pas d'abstraction spéculative.

## Definition of Done (toute contribution)
1. Rangée au bon endroit · 2. Documentée (README/doc à jour) · 3. Conforme à la charte ·
4. Cohérente avec la vision · 5. Directement exploitable (zéro placeholder/TODO) · 6. Tests
d'invariants verts · 7. Skip gracieux si dépendance externe · 8. Commit atomique sur branche de travail.

## Anti-patterns (à refuser)
Logique métier dans le Kernel · fonctionnalité « parce qu'intéressante » · secret dans le dépôt ·
donnée fictive · dépendance front · rename destructif sans ADR · abstraction prématurée.
