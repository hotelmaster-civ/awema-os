---
titre: 07 — GOVERNANCE
statut: stable
maj: 2026-06-27
---

# 07 — Gouvernance

> Comment le projet évolue **sans perdre sa cohérence**, en tant que plateforme open source durable.

## Autorité
- Le **Chief Software Architect** garantit la cohérence technique, fonctionnelle, documentaire et
  philosophique. Il fait respecter la [Constitution](00-CONSTITUTION.md).
- **Les agents proposent ; les humains décident.** Aucune décision structurante n'est automatique.

## Hiérarchie des sources (en cas de conflit)
1. `FOUNDATION/` (stable) → 2. `PRD-AWEMA.md` → 3. `ROADMAP.md` (source unique du quoi/quand) →
4. `PLAN-EXECUTION-BETA.md` → 5. guides `docs/*` → 6. le code.
Si le **code contredit** la doc : on **analyse pourquoi** avant d'agir ; on ne modifie jamais aveuglément.

## Processus de contribution
1. **Besoin réel** rattaché au module **Marketing** (sinon refus — cf. règle absolue).
2. **Test de recevabilité** (Constitution) : utile aujourd'hui ? cohérent ? complexité ? peut attendre ?
3. **Plugin d'abord** ; modification du Kernel seulement si un concept universel manque (→ ADR).
4. **Branche de travail** dédiée ; commits français ; **pas de PR sans demande explicite**.
5. **Definition of Done** respectée ; tests d'invariants verts.
6. **Documentation à jour** (la doc fait partie du livrable, pas une option).

## Officialiser un nouveau module (Finance, RH, …)
Un domaine reste **hors périmètre** tant que le Marketing n'est pas exemplaire. Pour devenir officiel,
il faut au minimum : (a) un **ADR** justifiant le besoin ; (b) sa documentation de module ; (c) qu'il
**n'introduise aucune logique métier dans le Kernel** ; (d) qu'il réutilise les concepts du Kernel.
**Par défaut : on documente la possibilité, on ne code pas la logique.**

## Contrôle d'accès & base juridique (rappel)
- **Licence** : outil **opérationnel** de suivi + **base légale** (le registre `.awema/` est la preuve
  « à qui/quand »). **Pas** une serrure (code open-source, vérification éditable).
- **Verrou réel = accès API** (modèle B « AWEMA Tech Provider ») : l'éditeur peut **révoquer** ; la
  plateforme l'applique. Par **défaut (modèle A)**, chaque agence est autonome (ses propres API).
- Détail : `docs/14-acces-api-agence.md`, `docs/ACCES-AGENCE.md`.

## Sécurité (invariants)
Aucun secret dans le dépôt · secrets en GitHub Secrets/Variables ou `.awema/` (gitignoré, `600`) ·
rotation + historique · scopes minimaux · isolation par fork (un pilote ne voit jamais les données d'un
autre). Détail : `docs/13-securite-donnees.md`.

## Fin de session (obligatoire)
Mettre à jour : documentation · `ROADMAP.md` · ADR · `PROJECT_SELF_DESCRIPTION.md` si nécessaire.
Laisser le projet dans un **état cohérent** ; produire un **rapport de session** (fait / reste à faire /
risques / dette / décisions / prochaines étapes).
