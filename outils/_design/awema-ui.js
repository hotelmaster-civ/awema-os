/* ============================================================================
   AWEMA UI — comportements partagés (icônes, thème, toast, count-up, palette).
   Usage : <script src="../_design/awema-ui.js"></script> puis window.AWEMA.*
   Sans dépendance. Compatible file:// (hors-ligne).
   ========================================================================== */
window.AWEMA = (function () {
  const ICONS = {
    grid:'<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    cal:'<rect x="3" y="4" width="18" height="17" rx="3"/><path d="M3 9h18M8 2v4M16 2v4"/>',
    layers:'<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    chart:'<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    chat:'<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/>',
    bolt:'<path d="M13 2L3 14h7l-1 8 10-12h-7l1-8z"/>',
    users:'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 21a6.5 6.5 0 0 1 13 0M17 11a3 3 0 1 0-1-5.8M21.5 21a5.5 5.5 0 0 0-4-5.3"/>',
    cog:'<circle cx="12" cy="12" r="3.2"/><path d="M19 12a7 7 0 0 0-.1-1.3l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2.3-1.3L13.8 2h-3.6l-.4 2.5a7 7 0 0 0-2.3 1.3l-2.3-1-2 3.4 2 1.5A7 7 0 0 0 5 12a7 7 0 0 0 .1 1.3l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2.3 1.3l.4 2.5h3.6l.4-2.5a7 7 0 0 0 2.3-1.3l2.3 1 2-3.4-2-1.5A7 7 0 0 0 19 12z"/>',
    menu:'<path d="M3 6h18M3 12h18M3 18h18"/>',
    search:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/>',
    moon:'<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M19 5l-1.5 1.5M6.5 17.5L5 19"/>',
    plus:'<path d="M12 5v14M5 12h14"/>',
    rdv:'<path d="M20 6L9 17l-5-5"/>',
    eye:'<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/>',
    bubble:'<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/>',
    target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4"/>',
    image:'<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="2"/><path d="M21 15l-5-5L5 21"/>',
    download:'<path d="M12 3v12M7 11l5 4 5-4M5 21h14"/>',
    sparkle:'<path d="M12 3l1.8 4.6L18 9l-4.2 1.4L12 15l-1.8-4.6L6 9l4.2-1.4z"/>',
    arrow:'<path d="M5 12h14M13 6l6 6-6 6"/>',
    check:'<path d="M20 6L9 17l-5-5"/>',
    wand:'<path d="M15 4V2M15 10V8M11 6H9M21 6h-2M18 9l-1.5-1.5M18 3l-1.5 1.5M4 20l9-9M12 7l1 1"/>'
  };
  function ic(name, attrs) {
    const p = ICONS[name] || '';
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" ${attrs || ''}>${p}</svg>`;
  }
  /* Remplit tous les [data-ic] de la page par l'icône correspondante */
  function injectIcons(root) {
    (root || document).querySelectorAll('[data-ic]').forEach(el => {
      if (el.dataset.icDone) return;
      el.insertAdjacentHTML('afterbegin', ic(el.dataset.ic));
      el.dataset.icDone = '1';
    });
  }
  /* Toast partagé (crée le conteneur si absent) */
  function toast(msg) {
    let t = document.getElementById('awema-toast');
    if (!t) { t = document.createElement('div'); t.id = 'awema-toast'; t.className = 'toast'; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(t._t); t._t = setTimeout(() => t.classList.remove('show'), 1700);
  }
  /* Thème : lit/écrit la préférence, branche un bouton optionnel */
  const THEME_KEY = 'awema-theme';
  function applyTheme(mode) {
    document.documentElement.setAttribute('data-theme', mode);
    try { localStorage.setItem(THEME_KEY, mode); } catch (e) {}
    document.querySelectorAll('[data-theme-btn]').forEach(b => { b.innerHTML = ic(mode === 'dark' ? 'sun' : 'moon'); });
  }
  function initTheme(btn) {
    let saved = 'dark';
    try { saved = localStorage.getItem(THEME_KEY) || 'dark'; } catch (e) {}
    applyTheme(saved);
    if (btn) btn.addEventListener('click', () => applyTheme(
      document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'));
  }
  /* Compteur animé */
  function countUp(el, to, suffix) {
    let s = null; const dur = 900;
    const step = t => { if (!s) s = t; const p = Math.min((t - s) / dur, 1);
      el.textContent = Math.round(to * (1 - Math.pow(1 - p, 3))).toLocaleString('fr-FR') + (suffix || '');
      if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }
  function copy(text) {
    const ok = () => toast('Copié ✓');
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(ok, () => fb());
    else fb();
    function fb() { const a = document.createElement('textarea'); a.value = text; document.body.appendChild(a);
      a.select(); document.execCommand('copy'); a.remove(); ok(); }
  }
  /* Palette de commande réutilisable.
     config = { input, overlay, results, sources:()=>[{t,s,run,icon}] } */
  function commandPalette(cfg) {
    let list = [], sel = 0;
    const open = () => { cfg.overlay.classList.add('on'); cfg.input.value = ''; cfg.input.focus(); render(''); };
    const close = () => cfg.overlay.classList.remove('on');
    const isOpen = () => cfg.overlay.classList.contains('on');
    function render(q) {
      q = (q || '').toLowerCase();
      list = cfg.sources().filter(r => (r.t + ' ' + (r.s || '')).toLowerCase().includes(q)).slice(0, 10);
      sel = 0;
      cfg.results.innerHTML = list.length ? list.map((r, i) =>
        `<div class="r ${i === 0 ? 'sel' : ''}" data-i="${i}">${ic(r.icon || 'arrow')}
         <div><div>${r.t}</div>${r.s ? `<small>${r.s}</small>` : ''}</div><span class="k">↵</span></div>`).join('')
        : `<div style="padding:22px;text-align:center;color:var(--muted);font-size:13px">Aucun résultat</div>`;
      cfg.results.querySelectorAll('.r').forEach(el => {
        el.onclick = () => go(+el.dataset.i);
        el.onmouseenter = () => { sel = +el.dataset.i; hi(); };
      });
    }
    const hi = () => cfg.results.querySelectorAll('.r').forEach((e, i) => e.classList.toggle('sel', i === sel));
    function go(i) { const r = list[i]; if (r) { close(); r.run && r.run(); } }
    cfg.input.addEventListener('input', e => render(e.target.value));
    cfg.overlay.addEventListener('click', e => { if (e.target === cfg.overlay) close(); });
    document.addEventListener('keydown', e => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); isOpen() ? close() : open(); }
      if (e.key === 'Escape') close();
      if (isOpen()) {
        if (e.key === 'ArrowDown') { e.preventDefault(); sel = Math.min(sel + 1, list.length - 1); hi(); }
        if (e.key === 'ArrowUp') { e.preventDefault(); sel = Math.max(sel - 1, 0); hi(); }
        if (e.key === 'Enter') go(sel);
      }
    });
    return { open, close };
  }
  return { ic, injectIcons, toast, initTheme, applyTheme, countUp, copy, commandPalette };
})();
