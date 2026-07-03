# Générer un visuel depuis un prompt → le charger dans l'outil

L'outil de revue produit, pour chaque visuel, un **prompt à la charte optimisé par
plateforme**. Voici comment passer du prompt à une image, puis **recharger l'image dans
l'interface**. Trois méthodes, de la plus simple à la plus automatisée.

---

## Méthode 1 — Passerelle ChatGPT en 1 clic (recommandée, sans réglage)

> La plus fiable et conforme : 1 clic à l'aller, 1 collage au retour.

1. Sur un visuel, clique **🤖 Générer sur ChatGPT**.
   → le prompt est **copié** dans le presse-papier **et** `chatgpt.com` s'ouvre (où tu es
   déjà connecté).
2. Dans ChatGPT : **colle** (Ctrl/Cmd+V) et envoie. ChatGPT génère l'image.
3. **Copie l'image** générée (clic droit → Copier l'image) — ou télécharge-la.
4. Reviens dans l'outil et **colle l'image (Ctrl/Cmd+V)** n'importe où, **ou glisse** le
   fichier sur l'aperçu central.
   → l'image se charge dans l'interface et est **sauvegardée** avec le visuel (et incluse
   à l'export des retours).

✅ Aucune installation. ✅ Utilise ta session ChatGPT. ✅ Rien à automatiser de fragile.

> Pourquoi pas un envoi 100 % automatique vers chatgpt.com ? Une page statique ne peut pas
> piloter ta session ChatGPT (sécurité navigateur), et scripter chatgpt.com est fragile et
> sensible aux CGU. Les méthodes 2 et 3 couvrent l'automatisation réelle.

---

## Méthode 2 — Claude Desktop + MCP navigateur (automatisation assistée)

> « Vrai » envoi automatique : Claude Desktop pilote **ton** navigateur (ta session ChatGPT).

### Pré-requis (une fois)
- **Claude Desktop** installé.
- Un **MCP de navigateur** configuré, par ex. :
  - *Playwright MCP* (`@playwright/mcp`) — pilote Chrome/Chromium, peut utiliser ton profil ;
  - ou *Chrome DevTools / navigateur* équivalent.
- Dans `claude_desktop_config.json` :
  ```json
  {
    "mcpServers": {
      "playwright": { "command": "npx", "args": ["-y", "@playwright/mcp@latest"] }
    }
  }
  ```

### Utilisation
1. Sur un visuel, clique **📋 Claude Desktop** → l'**instruction complète est copiée**
   (prompt image + nom de fichier de sortie).
2. Colle-la dans **Claude Desktop** et envoie. Claude, via le MCP navigateur :
   ouvre `chatgpt.com`, colle le prompt, attend l'image, la **télécharge** sous
   `NNN-<plateforme>.png`.
3. Dans l'outil, charge l'image obtenue : **glisse-la** sur l'aperçu (ou Ctrl/Cmd+V),
   ou renseigne son chemin dans le champ *Image du visuel*.

⚠️ Dépend de la stabilité de l'interface ChatGPT et de l'anti-bot ; à utiliser de façon
raisonnable et conforme aux CGU d'OpenAI.

---

## Méthode 3 — API OpenAI Images (100 % automatique, sans navigateur)

> Le plus robuste pour de la production en lot. Nécessite une **clé API OpenAI** (≠ abonnement
> ChatGPT) — usage facturé à l'image.

1. Définir la clé : `export OPENAI_API_KEY="sk-..."`.
2. Générer une image depuis un prompt :
   ```bash
   python3 scripts/generer-image-openai.py "<le prompt copié>" \
     modules/marketing/clients/mon-client/_visuels-recus/001.png
   ```
   ou en lot depuis `campagne.json` (voir l'en-tête du script).
3. Dans l'outil, **glisse** l'image générée sur l'aperçu, ou indique son chemin dans
   *Image du visuel*.

Le script `scripts/generer-image-openai.py` est fourni et documenté.

---

## Récapitulatif

| Méthode | Auto ? | Installation | Coût | Fiabilité |
|---|---|---|---|---|
| 1. Passerelle ChatGPT | semi (1 clic + 1 collage) | aucune | abonnement ChatGPT | ★★★★★ |
| 2. Claude Desktop + MCP | assistée | Claude Desktop + MCP | abonnement ChatGPT | ★★★☆☆ |
| 3. API OpenAI Images | totale | clé API | à l'image | ★★★★☆ |

Dans **tous les cas**, le retour de l'image dans l'interface se fait par **collage
(Ctrl/Cmd+V)**, **glisser-déposer** sur l'aperçu, ou **chemin/URL** dans le champ *Image du
visuel* — et l'image part dans l'export des retours.
