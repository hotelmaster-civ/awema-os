#!/usr/bin/env bash
# Export PDF des livrables AWEMA (Google Doc / Sheet / Slides → PDF professionnels).
#
# Pipeline sans dépendance réseau au runtime :
#   Markdown -> HTML (md2html.py)  -> PDF (html2pdf.py via Chromium/Playwright)
#   CSV      -> HTML (csv2html.py) -> PDF (html2pdf.py, paysage)
#   Slides   -> Marp CLI si dispo, sinon HTML -> PDF
#
# Pré-requis (une seule fois) :
#   pip install playwright   (+ un Chromium ; PLAYWRIGHT_BROWSERS_PATH ou CHROME_BIN)
#
# Usage :  bash scripts/export-pdf.sh [dossier-client]
#          (défaut : $AWEMA_CLIENT_DIR, sinon le premier client trouvé)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLIENT="${1:-${AWEMA_CLIENT_DIR:-}}"
if [ -z "$CLIENT" ]; then
  CLIENT="$(ls -d "$ROOT"/modules/*/clients/*/ 2>/dev/null | head -1)"
  CLIENT="${CLIENT%/}"
fi
[ -n "$CLIENT" ] && [ -d "$CLIENT" ] || { echo "Usage: bash scripts/export-pdf.sh <dossier-client>"; exit 1; }
OUT="$CLIENT/_exports-pdf"
TMP="$(mktemp -d)"
mkdir -p "$OUT"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}"

md_to_pdf() {  # $1 src.md  $2 nom  $3 titre
  python3 "$ROOT/scripts/md2html.py" "$1" "$TMP/$2.html" "$3"
  python3 "$ROOT/scripts/html2pdf.py" "$TMP/$2.html" "$OUT/$2.pdf"
}
csv_to_pdf() {  # $1 src.csv  $2 nom  $3 titre
  python3 "$ROOT/scripts/csv2html.py" "$1" "$TMP/$2.html" "$3"
  python3 "$ROOT/scripts/html2pdf.py" "$TMP/$2.html" "$OUT/$2.pdf"
}

echo "📄 Export PDF — La Grande Vision"
echo "• Google Doc (180 contenus)…"
md_to_pdf "$CLIENT/03-contenus/contenus.md" "01-contenus-180" "La Grande Vision — 180 contenus"
echo "• Google Doc (60 scripts vidéo)…"
md_to_pdf "$CLIENT/04-scripts-video/scripts-video.md" "02-scripts-video" "La Grande Vision — 60 scripts vidéo"
echo "• Google Sheet (calendrier éditorial)…"
csv_to_pdf "$CLIENT/02-calendrier-editorial/calendrier-editorial.csv" "03-calendrier-editorial" "Calendrier Éditorial — 180 contenus"
echo "• Google Sheet (scoring)…"
csv_to_pdf "$CLIENT/08-scoring/scoring.csv" "04-scoring" "Système de Scoring"
echo "• Stratégie / Tunnel / CRM / Automatisation…"
md_to_pdf "$CLIENT/01-strategie/01-audit-marche-concurrence.md" "05-strategie-audit" "Stratégie — Audit & Marché"
md_to_pdf "$CLIENT/01-strategie/02-personas.md" "06-personas" "Personas"
md_to_pdf "$CLIENT/06-tunnel-whatsapp/README.md" "07-tunnel-whatsapp" "Tunnel WhatsApp"
md_to_pdf "$CLIENT/07-crm-relance/README.md" "08-crm-relance" "CRM & Relances J0→J90"
md_to_pdf "$CLIENT/09-automatisation/README.md" "09-automatisation" "Automatisation"
echo "• Google Slides (présentation direction)…"
if command -v npx >/dev/null 2>&1 && npx --no-install @marp-team/marp-cli --version >/dev/null 2>&1; then
  npx --no-install @marp-team/marp-cli "$CLIENT/10-presentation/presentation-direction.md" \
    --pdf --allow-local-files -o "$OUT/10-presentation-direction.pdf"
else
  md_to_pdf "$CLIENT/10-presentation/presentation-direction.md" "10-presentation-direction" "Présentation Direction"
fi

rm -rf "$TMP"
echo "✅ Terminé. PDF dans : $OUT"
ls -1 "$OUT"
