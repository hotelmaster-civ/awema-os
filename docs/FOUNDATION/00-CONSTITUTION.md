---
titre: 00 — CONSTITUTION d'AWEMA OS
statut: stable
maj: 2026-06-27
---

# 00 — Constitution

> La loi suprême du projet. Tout le reste s'y conforme.

## Raison d'être
AWEMA OS est le **système d'exploitation open source d'une agence digitale assistée par IA**.
Aujourd'hui, un seul module est officiel : **Marketing**. L'architecture doit **rendre possibles**
les autres domaines (Finance, RH, Commercial, Support, Production, Direction) **sans qu'on les
développe maintenant**.

## Ordre de priorité (jamais l'inverse)
1. **Qualité** · 2. **Simplicité** · 3. **Architecture** · 4. **Documentation** · 5. **Tests** ·
6. **Performance** · 7. **Fonctionnalités**.

Une fonctionnalité n'est jamais une raison suffisante. Une **fonctionnalité** ne passe avant aucune
des six valeurs au-dessus.

## Principes fondateurs
1. **Le Marketing est le seul module officiel.**
2. **Le Kernel ne connaît aucun métier.** Les modules connaissent le Kernel ; le Kernel ne connaît
   jamais les modules.
3. **Les plugins sont préférés aux modifications du Kernel.**
4. **Toute fonctionnalité est documentée.**
5. **Toute décision structurante produit un ADR.**
6. **Toute évolution importante met à jour la documentation.**
7. **Toute donnée affichée est traçable** (source, horodatage, provenance).
8. **Les données réelles sont prioritaires. Zéro fiction.**
9. **Les agents produisent des propositions ; les humains décident.**

## Règle absolue
> **Ne jamais ajouter une fonctionnalité parce qu'elle est intéressante.** Elle doit répondre à un
> **besoin réel** du module Marketing. Si elle peut attendre : on ne l'implémente pas.

## En cas de doute, privilégier toujours
moins de code · plus de clarté · plus de documentation · plus de modularité · plus de tests.

## Test de recevabilité (avant toute modification)
- Est-elle **utile aujourd'hui** ?
- Est-elle **cohérente avec la vision** ([01-VISION-2030](01-VISION-2030.md)) ?
- **Ajoute-t-elle de la complexité** ? (si oui, justifier)
- **Peut-elle attendre** ? (si oui, reporter)

## Inviolable
On ne casse jamais une architecture existante pour aller plus vite. Toute migration risquée est
**additive**, **réversible**, et **tracée par un ADR**.
