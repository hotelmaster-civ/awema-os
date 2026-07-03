/* AWEMA · Graphiques partagés (vanilla, zéro dépendance).
   Consommé par le dashboard (et le rapport client) via <script src>, et par
   tests/tests.html pour le harnais CI. Expose window.AwemaCharts + des globaux
   de compatibilité (MOIS_FR, dfr, courbeAudience, wireCourbe, spark) s'ils
   ne sont pas déjà définis par la page hôte.
   Règles dataviz : axe X proportionnel au TEMPS réel (jamais l'index — les
   synchros sont irrégulières) ; chiffres en encre, pas en couleur de série ;
   crosshair + infobulle par défaut sur les courbes. */
(function () {
  'use strict';
  var MOIS_FR = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];
  function nf(v) { return v == null ? '—' : (+v).toLocaleString('fr-FR'); }
  function dfr(iso) { var d = new Date(iso); return d.getDate() + ' ' + MOIS_FR[d.getMonth()]; }

  function courbeAudience(ev) {
    // ev = [{date,valeur}] — x proportionnel au TEMPS réel (les synchros sont irrégulières).
    var pts = (ev || []).filter(function (p) { return p && p.date && typeof p.valeur === 'number'; })
      .map(function (p) { return { t: +new Date(p.date), date: p.date, v: p.valeur }; })
      .sort(function (a, b) { return a.t - b.t; });
    if (pts.length < 2) return {
      html: '<div style="margin-top:14px;color:var(--muted);font-size:12.5px">' +
        'Pas encore assez d’historique (' + pts.length + ' point). La synchro hebdomadaire l’alimente — chaque ' +
        'passage ajoute un point, la courbe se dessine toute seule.</div>', pts: []
    };
    var W = 760, H = 230, L = 52, R = 16, T = 16, B = 30;
    var t0 = pts[0].t, t1 = pts[pts.length - 1].t || t0 + 1;
    var mn = Math.min.apply(null, pts.map(function (p) { return p.v; }));
    var mx = Math.max.apply(null, pts.map(function (p) { return p.v; }));
    var pad = Math.max((mx - mn) * .08, 1); mn = Math.max(0, mn - pad); mx += pad;
    var X = function (t) { return L + (t - t0) / ((t1 - t0) || 1) * (W - L - R); };
    var Y = function (v) { return T + (1 - (v - mn) / (mx - mn)) * (H - T - B); };
    pts.forEach(function (p) { p.x = X(p.t); p.y = Y(p.v); });
    var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + p.x.toFixed(1) + ' ' + p.y.toFixed(1); }).join(' ');
    var area = d + ' L' + pts[pts.length - 1].x.toFixed(1) + ' ' + (H - B) + ' L' + pts[0].x.toFixed(1) + ' ' + (H - B) + ' Z';
    // grille récessive : 3 niveaux + libellés discrets
    var grid = '';
    [0, .5, 1].forEach(function (f) {
      var v = mn + (mx - mn) * f, y = Y(v);
      grid += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y + '" y2="' + y + '" stroke="rgba(247,244,234,.07)"/>' +
        '<text x="' + (L - 8) + '" y="' + (y + 4) + '" text-anchor="end" font-size="10.5" fill="var(--muted2)">' + nf(Math.round(v)) + '</text>';
    });
    var xh = [pts[0], pts[Math.floor((pts.length - 1) / 2)], pts[pts.length - 1]];
    var vus = []; xh.forEach(function (p) { if (vus.indexOf(p) < 0) vus.push(p); });
    var xl = vus.map(function (p) {
      return '<text x="' + p.x + '" y="' + (H - 9) + '" text-anchor="middle" font-size="10.5" fill="var(--muted2)">' + dfr(p.date) + '</text>';
    }).join('');
    var last = pts[pts.length - 1];
    var html = '<div style="position:relative;margin-top:12px">' +
      '<svg id="evChart" viewBox="0 0 ' + W + ' ' + H + '" style="width:100%;height:auto;display:block" role="img" ' +
      'aria-label="Évolution des abonnés : de ' + nf(pts[0].v) + ' le ' + dfr(pts[0].date) + ' à ' + nf(last.v) + ' le ' + dfr(last.date) + '">' +
      '<defs><linearGradient id="evGrad" x1="0" x2="0" y1="0" y2="1">' +
      '<stop offset="0" stop-color="#FFC94D" stop-opacity=".22"/><stop offset="1" stop-color="#FFC94D" stop-opacity="0"/></linearGradient></defs>' +
      grid + xl +
      '<path d="' + area + '" fill="url(#evGrad)"/>' +
      '<path d="' + d + '" fill="none" stroke="#FFC94D" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>' +
      '<circle cx="' + last.x + '" cy="' + last.y + '" r="3.6" fill="#FFC94D" stroke="var(--bg,#191919)" stroke-width="2"/>' +
      '<text x="' + Math.min(last.x, W - R - 4) + '" y="' + Math.max(last.y - 10, 12) + '" text-anchor="end" font-size="11.5" font-weight="700" fill="var(--tx)">' + nf(last.v) + '</text>' +
      '<line id="evX" x1="0" x2="0" y1="' + T + '" y2="' + (H - B) + '" stroke="rgba(255,201,77,.4)" stroke-dasharray="3 3" style="display:none"/>' +
      '<circle id="evDot" r="4.5" fill="#FFC94D" stroke="var(--bg,#191919)" stroke-width="2" style="display:none"/>' +
      '<rect x="' + L + '" y="' + T + '" width="' + (W - L - R) + '" height="' + (H - T - B) + '" fill="transparent" id="evHit"/>' +
      '</svg>' +
      '<div id="evTip" style="display:none;position:absolute;pointer-events:none;background:#161616;border:1px solid rgba(255,201,77,.35);border-radius:9px;padding:6px 10px;font-size:12px;white-space:nowrap;box-shadow:0 10px 24px -8px rgba(0,0,0,.6);z-index:5"></div>' +
      '</div>';
    return { html: html, pts: pts, W: W, H: H };
  }

  function wireCourbe(c) {
    var g = function (id) { return document.getElementById(id); };
    var svg = g('evChart'), tip = g('evTip'), dot = g('evDot'), xln = g('evX'), hit = g('evHit');
    if (!svg || !c.pts.length) return;
    function move(e) {
      var r = svg.getBoundingClientRect(), sx = (e.clientX - r.left) * (c.W / r.width);
      var best = c.pts[0];
      c.pts.forEach(function (p) { if (Math.abs(p.x - sx) < Math.abs(best.x - sx)) best = p; });
      dot.setAttribute('cx', best.x); dot.setAttribute('cy', best.y); dot.style.display = '';
      xln.setAttribute('x1', best.x); xln.setAttribute('x2', best.x); xln.style.display = '';
      var i = c.pts.indexOf(best), prev = i > 0 ? c.pts[i - 1] : null, delta = prev ? best.v - prev.v : null;
      tip.innerHTML = '<b>' + nf(best.v) + '</b> abonnés · ' + dfr(best.date) +
        (delta != null ? ' <span style="color:' + (delta >= 0 ? '#34E5C4' : '#FF7D9C') + '">' + (delta >= 0 ? '+' : '') + nf(delta) + '</span>' : '');
      tip.style.display = 'block';
      var px = best.x / c.W * r.width, py = best.y / c.H * r.height;
      tip.style.left = Math.min(px + 12, r.width - tip.offsetWidth - 4) + 'px';
      tip.style.top = Math.max(py - 40, 0) + 'px';
    }
    hit.addEventListener('mousemove', move);
    hit.addEventListener('mouseleave', function () { tip.style.display = 'none'; dot.style.display = 'none'; xln.style.display = 'none'; });
  }

  function spark(vals, color) {
    var w = 120, h = 34, mx = Math.max.apply(null, vals), mn = Math.min.apply(null, vals), rng = (mx - mn) || 1;
    var pts = vals.map(function (v, i) { return [i / (vals.length - 1) * w, h - 3 - ((v - mn) / rng) * (h - 8)]; });
    var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join(' ');
    var area = d + ' L' + w + ' ' + h + ' L0 ' + h + ' Z';
    var id = 'g' + Math.random().toString(36).slice(2, 7);
    return '<svg width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '"><defs><linearGradient id="' + id + '" x1="0" x2="0" y1="0" y2="1">' +
      '<stop offset="0" stop-color="' + color + '" stop-opacity=".45"/><stop offset="1" stop-color="' + color + '" stop-opacity="0"/></linearGradient></defs>' +
      '<path d="' + area + '" fill="url(#' + id + ')"/><path d="' + d + '" fill="none" stroke="' + color + '" stroke-width="2" stroke-linecap="round"/></svg>';
  }

  var api = { MOIS_FR: MOIS_FR, nf: nf, dfr: dfr, courbeAudience: courbeAudience, wireCourbe: wireCourbe, spark: spark };
  if (typeof window !== 'undefined') {
    window.AwemaCharts = api;
    ['MOIS_FR', 'dfr', 'courbeAudience', 'wireCourbe', 'spark'].forEach(function (k) {
      if (!(k in window)) window[k] = api[k];
    });
  }
})();
