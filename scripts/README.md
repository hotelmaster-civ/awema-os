# scripts/ — Utilitaires transverses

| Fichier | Rôle |
|---|---|
| `export-pdf.sh` | Exporte tous les livrables (Doc/Sheet/Slides) en **PDF professionnels** |
| `md2html.py` | Convertisseur Markdown → HTML (charte AWEMA), sans dépendance |
| `csv2html.py` | Convertisseur CSV → HTML (tableau paysage, charte) |
| `html2pdf.py` | Rendu HTML → PDF via Chromium (Playwright) |
| `generer-image-openai.py` | Génère une image depuis un prompt via l'API OpenAI Images (voie 100 % auto) — voir `outils/revue-visuels/INTEGRATION-GENERATION-IMAGE.md` |

## Exporter les PDF

```bash
bash scripts/export-pdf.sh
```
Les PDF sont écrits dans
`modules/marketing/clients/mon-client/_exports-pdf/`.

## Pré-requis (une seule fois)

```bash
pip install playwright
# un navigateur Chromium doit être disponible :
#   - soit via PLAYWRIGHT_BROWSERS_PATH (ex : /opt/pw-browsers)
#   - soit en pointant CHROME_BIN vers un binaire chrome/chromium
#   - soit : python -m playwright install chromium
```

`html2pdf.py` détecte automatiquement un Chromium présent dans
`PLAYWRIGHT_BROWSERS_PATH`, ou utilise `CHROME_BIN` si défini.

## Présentation en slides (optionnel)

Pour un rendu *slides* (et non document) de la présentation :
```bash
npx @marp-team/marp-cli .../10-presentation/presentation-direction.md --pdf
```
