---
titre: FOUNDATION — Corpus de référence d'AWEMA OS
statut: stable
maj: 2026-06-27
---

# 🏛️ FOUNDATION — le socle de référence d'AWEMA OS

> Ces documents sont la **constitution** du projet : courts, précis, **stables**. Ils priment sur
> toute autre doc en cas de conflit. On ne les modifie pas à la légère — une évolution structurelle
> passe par un **ADR** (cf. `08-ARCHITECTURE_DECISIONS.md`) avant mise à jour.

| # | Document | Rôle |
|---|---|---|
| 00 | [00-CONSTITUTION.md](00-CONSTITUTION.md) | Loi suprême : priorités, principes fondateurs, règle absolue. |
| 01 | [01-VISION-2030.md](01-VISION-2030.md) | Où va AWEMA : OS d'agence assistée par IA, durable, open source. |
| 02 | [02-KERNEL.md](02-KERNEL.md) | Les 11 concepts universels. Le Kernel ignore le métier. |
| 03 | [03-DESIGN_PRINCIPLES.md](03-DESIGN_PRINCIPLES.md) | ADN technique + règles de conception. |
| 04 | [04-PLUGIN_MODEL.md](04-PLUGIN_MODEL.md) | Comment un module/plugin s'attache au Kernel. |
| 05 | [05-AGENT_MODEL.md](05-AGENT_MODEL.md) | Contrat d'agent (mission → DoD). Aucun agent généraliste. |
| 06 | [06-DATA_MODEL.md](06-DATA_MODEL.md) | Les données = la vérité. Traçabilité obligatoire. |
| 07 | [07-GOVERNANCE.md](07-GOVERNANCE.md) | Gouvernance open source, contribution, officialisation d'un module. |
| 08 | [08-ARCHITECTURE_DECISIONS.md](08-ARCHITECTURE_DECISIONS.md) | Journal des ADR (décisions structurantes). |

**Hiérarchie documentaire** : `FOUNDATION/` (stable, le « pourquoi ») → `PRD-AWEMA.md` (produit) →
`ROADMAP.md` (le « quoi/quand », source unique) → `PLAN-EXECUTION-BETA.md` (le « comment »).
Le reste de `docs/` = guides opérationnels.
