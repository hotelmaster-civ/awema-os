# Outil — Dashboard AWEMA (Command Center)

Tableau de bord SaaS premium pour **piloter l'agence et les campagnes** : KPI, calendrier
éditorial, répartition par pilier/plateforme, production, scoring A→E, tunnel WhatsApp,
machine éditoriale. **Un seul fichier HTML, zéro dépendance, zéro installation.**

## Ouvrir (1 double-clic)
1. `python3 build-data.py` → génère `data.js` (campagne La Grande Vision par défaut).
2. Ouvrir `index.html` dans un navigateur.

> Autre campagne : `python3 build-data.py <chemin/campagne.json>`.

## Design (langage visuel)
- **Esthétique** : minimaliste premium, **bento grid**, **glassmorphism**, ombres douces,
  angles arrondis, contraste élevé.
- **Thème** : **dark mode natif profond** + accents électriques (bleu `#4BA3FF`,
  violet `#7C5CFF`, mint `#34E5C4`, gold `#D4AF37`) ; **thème clair** en 1 clic.
- **Typo** : Plus Jakarta Sans (titres) + Inter (texte) — repli système hors-ligne.
- **UX** : mobile-first, **Command+K** (palette de recherche globale), micro-interactions,
  **skeletons** de chargement, compteurs animés, graphiques SVG épurés (donut, aire,
  barres, anneau de progression) **sans librairie**.

## Multi-clients
Pilote **tous les clients de l'agence** via le registre `outils/_data/agence.js`
(généré par `outils/_data/build.py`). Sélecteur de client dans la barre du haut ; toutes
les vues sont **client-aware**. La vue **Clients** gère les clients ; la vue **Présence
digitale** affiche leurs réseaux. Ajouter/brancher un client : [`../_data/README.md`](../_data/README.md).

## Données — réelles uniquement (aucune fiction)
- **Plan éditorial** : calculé sur les contenus réels du client (`campagne.json`).
- **Présence digitale** (audience, likes, commentaires, posts, top fans/posts…) : affichée
  seulement si `reseaux.json` est rempli par `scripts/connect-reseaux.py` (Meta Graph API /
  import). Sinon : états **« à connecter »**.
- **Lien visualiseur** : ouvre les contenus du client sélectionné dans `revue-visuels`.

## Reconstruire après une nouvelle génération
```bash
cd ../../modules/marketing/clients/mon-client/_generateur && python3 generer.py
cd ../../../../../../outils/dashboard && python3 build-data.py
```
