# Outil — Revue des Visuels de Campagne

Application légère (un seul fichier HTML, **zéro installation**) pour **étudier**,
**naviguer**, **annoter** et **demander des modifications** sur chaque visuel d'une
campagne — les modifications **réinjectent automatiquement dans les prompts**.

Outil **transverse** (réutilisable pour tout client de l'agence).

> 🎨 Habillé avec le **design system AWEMA** (`outils/_design/`) : dark mode néon +
> glassmorphism, **thème clair en 1 clic**, **Command+K** (palette de recherche), skeletons
> de chargement, micro-interactions. Cohérent avec le Dashboard et les futurs outils.

## Ouvrir (1 double-clic)

1. `python3 build-data.py` → génère `data.js` (campagne La Grande Vision par défaut).
2. Ouvrir `index.html` dans un navigateur. C'est tout.

> Pour une autre campagne : `python3 build-data.py <chemin/campagne.json>`,
> ou glisser-déposer le `campagne.json` directement dans l'app.

## Ce que l'outil permet

| Besoin | Fonction |
|---|---|
| **Visualiser & étudier** chaque visuel | Aperçu central à la charte (titre, pilier, CTA, visuel recommandé) + aperçus Canva cliquables |
| **Copier la description du post** | Bloc **légende + hashtags prêt à coller**, adapté à la plateforme de destination (+ bouton « Copier les # ») |
| **Copier le prompt visuel** | Prompt **pro à la charte, optimisé pour la plateforme** (format natif, texte minimaliste, illustration en avant) — au choix Canva / Midjourney / GPT |
| **Générer sur ChatGPT en 1 clic** | Bouton **🤖** : copie le prompt + ouvre `chatgpt.com` (session existante). Puis **colle l'image générée (Ctrl/Cmd+V)** ou **glisse-la** sur l'aperçu → elle se charge dans l'outil |
| **Piloter via Claude Desktop** | Bouton **📋** : copie une instruction prête pour Claude Desktop + MCP navigateur (envoi auto à ChatGPT). Voir [`INTEGRATION-GENERATION-IMAGE.md`](INTEGRATION-GENERATION-IMAGE.md) |
| **Passer au suivant simplement** | Boutons ← → et **flèches clavier** ; liste filtrable (pilier, plateforme, statut, recherche) |
| **Annoter** | Notes d'étude + URL/chemin d'image, sauvegarde automatique (localStorage) |
| **Demander des modifications → prompts** | Champ « modifications » + bouton **Générer prompt mis à jour** (Canva / Midjourney / GPT) prêt à copier |
| **Suivre l'avancement** | Statut par visuel : À produire / En revue / Validé / À retoucher |
| **Exporter** | `retours-campagne.json` + `retours-campagne.md` (brief de retouche) |

## La boucle d'amélioration (modifications → prompts → visuels)

```
Étudier le visuel → Annoter / demander une modif → "Générer prompt mis à jour"
   → Copier le prompt → Régénérer dans Canva/Midjourney/GPT → Re-revue
```

Les retours exportés (`retours-campagne.md`) servent à :
- alimenter les prompts (copier-coller dans Canva/MJ/GPT) ;
- enrichir le générateur (`_generateur/sujets.py` / gabarits de `generer.py`) pour les
  contenus « À retoucher » ou les meilleurs « Validé ».

## Source des données

`campagne.json` est produit par le générateur du client
(`modules/marketing/clients/<client>/_generateur/generer.py` →
`_donnees/campagne.json`). Il contient, par contenu : titre, date, plateforme, persona,
pilier, hook, CTA, format, KPI, les 3 prompts et les aperçus Canva connus.

## Reconstruire après une nouvelle génération

```bash
# 1) régénérer la campagne (côté client)
cd ../../modules/marketing/clients/mon-client/_generateur && python3 generer.py
# 2) reconstruire les données de l'outil
cd ../../../../../../outils/revue-visuels && python3 build-data.py
```

## Notes

- 100 % statique, fonctionne hors-ligne (`file://`). Les annotations restent dans le
  navigateur (localStorage) ; **exporter** pour partager ou versionner.
- Les polices Montserrat/Poppins se chargent via CDN si en ligne ; sinon repli système
  (l'outil reste parfaitement utilisable).
