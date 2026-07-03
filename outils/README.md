# Outils d'agence (transverses)

Outils réutilisables par tous les départements et toutes les missions. Chaque outil est
autonome, documenté, et pensé pour un **onboarding immédiat**.

| Outil | Rôle | Techno |
|---|---|---|
| [`revue-visuels/`](revue-visuels/) | Étudier, naviguer, annoter les visuels d'une campagne et générer des prompts de modification | HTML statique (zéro install) |
| [`dashboard/`](dashboard/) | **Command Center** : pilotage KPI, calendrier, piliers/plateformes, production, scoring A→E, tunnel WhatsApp. Dark mode néon, bento grid, Command+K | HTML statique (zéro install) |

## Ajouter un outil

1. Créer `outils/<nom-outil>/` avec un `README.md`.
2. Privilégier le **sans-dépendance** (un fichier HTML, ou un script Python standard).
3. Le rendre **générique** (réutilisable d'un client à l'autre via un fichier de données).
4. Le référencer dans ce tableau.
