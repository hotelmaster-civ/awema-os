# AWEMA UI — Design System partagé

Langage visuel commun à **tous les outils** de l'agence (présents et à venir).
Esthétique : **minimaliste premium · dark mode néon · glassmorphism · bento grid**.

## Fichiers
| Fichier | Rôle |
|---|---|
| `awema-ui.css` | Tokens (couleurs, thèmes clair/sombre, rayons, ombres, typo) + composants (boutons, cartes/glass, chips, champs, skeleton, toast, palette, bento) |
| `awema-ui.js` | Comportements : `ic()` (icônes SVG), `injectIcons()`, `toast()`, `initTheme()`, `countUp()`, `copy()`, `commandPalette()` |

## Brancher le design system dans un nouvel outil

```html
<!doctype html>
<html lang="fr" data-theme="dark">
<head>
  <meta charset="utf-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../_design/awema-ui.css">
</head>
<body>
  <button class="iconbtn" id="theme" data-ic="moon" data-theme-btn></button>
  <article class="card col4">…</article>

  <script src="../_design/awema-ui.js"></script>
  <script>
    AWEMA.injectIcons();              // remplit les [data-ic]
    AWEMA.initTheme(document.getElementById('theme'));
    AWEMA.toast('Prêt');
  </script>
</body>
</html>
```

## Tokens clés (variables CSS)
- Couleurs : `--bg --surface --elev --border --tx --muted` ; accents `--blue #4BA3FF`,
  `--violet #7C5CFF`, `--mint #34E5C4`, `--gold #D4AF37`, `--pink`, `--amber`.
- Dégradés : `--grad` (CTA), `--grad-mint`. Rayons : `--r`, `--r-sm`. Ombre : `--shadow`.
- Typo : `--font-disp` (Plus Jakarta Sans, titres) · `--font` (Inter, texte).
- Thème : `--data-theme="dark"` (défaut) / `"light"`. La préférence est mémorisée
  (localStorage) par `AWEMA.initTheme`.

## Composants prêts à l'emploi (classes)
`.card` `.glass` · `.btn` `.btn-cta` `.iconbtn` `.ghost` `.mini` `.mini.gold` ·
`.chip.up/.down` `.tag` `.badge` · `.field` `label.lbl` · `.sk` (skeleton) `.fade` ·
`.toast` · `.cmd-ov/.cmd` (palette) · `.bento` + `.col3…col12` (grille responsive).

## Règle pour les outils « à venir »
Tout nouvel outil de `outils/` **doit** lier `awema-ui.css` + `awema-ui.js` et utiliser ces
tokens/composants — pas de couleurs ni de polices en dur. Cela garantit une **cohérence
visuelle totale** et un onboarding immédiat.

## Implémentations de référence
- `outils/dashboard/` — Command Center (bento, KPI, charts SVG, Command+K).
- `outils/revue-visuels/` — Revue des visuels (mêmes tokens, thème, palette, skeleton).
