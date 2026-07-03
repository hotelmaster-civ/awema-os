/* AWEMA · Formatage & vocabulaire partagés (vanilla, zéro dépendance).
   Une seule implémentation pour tout le produit : dashboard, visualiseur, rapport.
   Évite la dérive (ex. deux verts « publié » différents) et les échappeurs dupliqués.
   Expose window.AwemaFmt + des globaux de compat (nf/esc/escP/escAttr) si libres. */
(function () {
  'use strict';

  // Nombre en français, ou tiret cadratin si absent (jamais « undefined »/« NaN »).
  function nf(v) { return v == null || v === '' ? '—' : (isNaN(+v) ? String(v) : (+v).toLocaleString('fr-FR')); }

  // Échappement HTML pour du CONTENU d'élément (& < >).
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>]/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m]; }); }
  // Échappement pour une VALEUR D'ATTRIBUT (ajoute les guillemets).
  function escAttr(s) { return esc(s).replace(/"/g, '&quot;'); }

  // Vocabulaire de DIFFUSION (file de publication) — source unique de vérité.
  // Les couleurs de statut suivent la charte : succès #34E5C4, erreur #FF7D9C.
  var DIFFUSION = {
    programme:     { label: 'programmé', emoji: '🗓', color: '#D4AF37' },
    publie:        { label: 'publié',    emoji: '✅', color: '#34E5C4' },
    partiel:       { label: 'partiel',   emoji: '◐',  color: '#FFC94D' },
    echec:         { label: 'échec',     emoji: '✗',  color: '#FF7D9C' },
    attente_video: { label: 'attente',   emoji: '⏸',  color: '#B3AA92' }
  };

  // Vocabulaire de PRODUCTION (revue des visuels) — source unique de vérité.
  var PRODUCTION = {
    'À produire':   '#B3AA92',
    'En revue':     '#FFC861',
    'À retoucher':  '#FF7D9C',
    'Validé':       '#34E5C4'
  };

  // Badge de diffusion unifié. Rendu identique partout ; cliquable si l'URL du
  // post publié est connue (perfs → contenu). Retourne '' pour un statut inconnu.
  function diffBadge(statut, url, style) {
    var d = DIFFUSION[statut]; if (!d) return '';
    var txt = d.emoji + ' ' + d.label;
    var base = 'border-color:' + d.color + '55;color:' + d.color + (style || '');
    return url
      ? '<a class="pill" href="' + escAttr(safeUrl(url)) + '" target="_blank" rel="noopener" style="text-decoration:none;' + base + '" title="Ouvrir le post publié">' + txt + ' ↗</a>'
      : '<span class="pill" style="' + base + '">' + txt + '</span>';
  }

  // Couleur d'un statut de production (défaut : muted).
  function prodColor(statut) { return PRODUCTION[statut] || '#B3AA92'; }

  // URL sûre pour un href : n'autorise que http(s)/mailto (les liens viennent des API
  // sociales → un « javascript:… » injecté deviendrait exécutable). Sinon « # ».
  function safeUrl(u) {
    var s = String(u == null ? '' : u).trim();
    return /^(https?:|mailto:)/i.test(s) ? s : '#';
  }

  var api = { nf: nf, esc: esc, escAttr: escAttr, safeUrl: safeUrl, DIFFUSION: DIFFUSION, PRODUCTION: PRODUCTION, diffBadge: diffBadge, prodColor: prodColor };
  if (typeof window !== 'undefined') {
    window.AwemaFmt = api;
    // Globaux de compatibilité : ne pas écraser si la page les a déjà définis.
    if (!('nf' in window)) window.nf = nf;
    if (!('esc' in window)) window.esc = esc;
    if (!('escP' in window)) window.escP = esc;          // escP = nom historique du dashboard
    if (!('escAttr' in window)) window.escAttr = escAttr;
  }
})();
