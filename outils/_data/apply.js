// Personnalisation auto-hébergée AWEMA.
// À charger APRÈS config.js : <script src="…/config.js"></script><script src="…/apply.js"></script>
// Applique config/agence.json à n'importe quelle page : charte (couleurs), nom/initiales/tagline
// (éléments [data-ag]), titre de l'onglet, et réécriture des liens GitHub vers le fork de l'agence.
(function () {
  var c = window.AWEMA_CONFIG;
  if (!c) return;
  // 1) Charte graphique → variables CSS (--nuit, --ciel, …)
  var ch = c.charte || {}, root = document.documentElement;
  Object.keys(ch).forEach(function (k) { root.style.setProperty('--' + k, ch[k]); });
  // 2) Textes de marque : tout élément <… data-ag="nom|nom_complet|tagline|slogan|initiales|contact">
  document.querySelectorAll('[data-ag]').forEach(function (el) {
    var v = c[el.dataset.ag];
    if (v) el.textContent = v;
  });
  // 3) Titre de l'onglet (préserve un éventuel suffixe après « · » / « — »)
  if (c.nom) {
    var t = document.title, sep = t.indexOf('·') >= 0 ? '·' : (t.indexOf('—') >= 0 ? '—' : null);
    document.title = sep ? c.nom + ' ' + sep + ' ' + t.split(sep).slice(1).join(sep).trim() : c.nom;
  }
  // 4) Liens GitHub → repo du fork (owner/repo de config), pour Pages + « Code source »
  var g = c.github || {};
  // « ton-pseudo » = placeholder du template public (pas encore configuré) : ne rien réécrire,
  // sinon les liens GitHub pointent vers un dépôt inexistant et awema-fork.js ne les retrouve plus.
  if (g.owner && g.repo && g.owner !== 'ton-pseudo') {
    var dO = 'awema-test', dR = 'awema-os';
    document.querySelectorAll('a[href]').forEach(function (a) {
      a.href = a.href
        .replace(dO + '.github.io/' + dR, g.owner + '.github.io/' + g.repo)
        .replace('github.com/' + dO + '/' + dR, 'github.com/' + g.owner + '/' + g.repo);
    });
  }
})();
