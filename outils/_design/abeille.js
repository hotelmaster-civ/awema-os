/* Awa l'abeille 🐝 — mascotte d'aide contextuelle d'AWEMA.
   Additif & autonome : injecte son CSS, fonctionne en file:// et sur toute page.
   Usage : <script src="<chemin>/_design/abeille.js" data-aide="<cle-page>"></script>
   Si data-aide absent, la clé est déduite du nom de fichier (ex. memoire.html → "memoire"). */
(function () {
  var sc = document.currentScript;
  var KEY = (sc && sc.dataset && sc.dataset.aide) ||
    ((location.pathname.split('/').pop() || 'index').replace(/\.html?$/, '') || 'index');

  // ——— Ce qu'Awa explique, page par page (court, chaleureux, jamais perdu) ———
  var AIDE = {
    tutoriel: { t: "Le guide complet, pas à pas 🧭", s: [
      "Suis les 14 étapes <b>dans l'ordre</b> : de la copie du projet jusqu'à AWEMA qui tourne.",
      "Tu ne tapes <b>aucune commande</b> : tu cliques, tu colles, tu attends.",
      "À chaque étape, repère le <b>✅ « ce que tu vois »</b> : c'est ta preuve que c'est réussi.",
      "Bloqué ? Note l'étape + le message exact, et demande de l'aide." ] },
    index: { t: "Bienvenue chez AWEMA 👋", s: [
      "Ici tu découvres l'outil : ce qu'il fait et pour qui.",
      "Clique <b>« Explorer le dashboard »</b> pour voir le cockpit en action.",
      "Pas encore prêt ? Laisse ton contact via <b>« Liste d'attente »</b>." ] },
    onboarding: { t: "Ton parcours en 4 étapes", s: [
      "Suis les étapes dans l'ordre : Personnalise → Ajoute un client → Connecte ses réseaux → Pilote.",
      "Coche <b>« Marquer comme fait »</b> à chaque étape (ta progression est gardée).",
      "Commence par <b>« Voir la démo »</b> pour comprendre où tu vas." ] },
    setup: { t: "Mets l'outil à TA marque", s: [
      "Renseigne le nom de ton agence, ton contact et tes couleurs.",
      "Clique <b>« Enregistrer »</b> : AWEMA écrit la config et régénère l'app <b>en arrière-plan</b>.",
      "La 1ʳᵉ fois seulement, connecte ton GitHub. Tout s'adapte (nom, logo, charte)." ] },
    configuration: { t: "Mise en route — configurer à 100 %", s: [
      "<b>Étape 1, ton socle :</b> GitHub = l'hébergement gratuit. Clique « Connecter mon GitHub », puis « Activer l'hébergement (Pages) ».",
      "AWEMA <b>coche tout seul</b> ce qui est déjà fait (il vérifie ton état sur GitHub) — bouton « ↻ Revérifier » si besoin.",
      "Tu ne connectes que les réseaux de <b>tes</b> clients (pas tous).",
      "<b>Dernière étape :</b> clique simplement « Lancer la 1ʳᵉ récupération » — ensuite tout est automatique.",
      "Gérer de vrais clients exige une App vérifiée côté plateforme (exigence des réseaux, incompressible)." ] },
    "nouveau-client": { t: "Crée la fiche d'un client", s: [
      "Donne au moins son <b>nom</b> (le reste est optionnel).",
      "Clique <b>« Enregistrer »</b> : la fiche est créée dans ton dépôt, visible au cockpit <b>en arrière-plan</b>.",
      "Ensuite : connecte ses réseaux et remplis sa <b>Mémoire Marketing</b>." ] },
    memoire: { t: "L'ADN de la marque, pour l'IA", s: [
      "Cette page nourrit les agents IA avec l'identité de la marque.",
      "1) Choisis le client · 2) Remplis identité, ton, personas, produits, FAQ.",
      "3) Clique <b>« Enregistrer »</b> : AWEMA écrit dans ton dépôt et met à jour l'IA <b>en arrière-plan</b>.",
      "La 1ʳᵉ fois seulement, tu connectes ton GitHub. Plus c'est rempli, plus l'IA est juste 🎯" ] },
    "liste-attente": { t: "Reste informé·e", s: [
      "Les places pilotes sont complètes : laisse ton contact pour le lancement (sur abonnement).",
      "Remplis nom + email, clique <b>« M'ajouter »</b> : ça ouvre un mail pré-rempli — <b>envoie-le</b>." ] },
    merci: { t: "C'est noté 🎉", s: [
      "Pense à <b>envoyer l'email</b> qui vient de s'ouvrir, sinon ton contact n'est pas enregistré.",
      "En attendant, explore le cockpit en démo." ] },
    rejoindre: { t: "Candidate au programme", s: [
      "Remplis le formulaire : on revient vers toi avec ton accès et le guide.",
      "Clique <b>« Envoyer »</b> : un mail pré-rempli s'ouvre — n'oublie pas de l'envoyer." ] },
    "demande-acces": { t: "Accès API « managé » (optionnel)", s: [
      "Par défaut, chaque agence utilise <b>ses propres</b> accès API — tu n'as pas besoin de cette page.",
      "Elle sert <b>uniquement</b> si tu veux passer par les API d'AWEMA pour un client commun (sur validation)." ] },
    "connect-facebook": { t: "Connecter Facebook / Instagram", s: [
      "Tu dois être <b>admin</b> de la Page.",
      "Suis les étapes pour obtenir un <b>token</b>, copie-le (boutons « copier »).",
      "Place-le en <b>Secret GitHub</b> <code>META_TOKEN</code>, puis lance la synchro indiquée." ] },
    "connect-tiktok": { t: "Connecter TikTok", s: [
      "<b>Il te faut une « clé d'accès GitHub »</b> (un PAT) : clique « en créer un ↗ », cherche <b>Variables</b> → mets « Read and write », puis <b>copie le code tout de suite</b>.",
      "Colle tes 3 valeurs (2 clés TikTok + la clé GitHub), une seule fois.",
      "Ensuite : <b>clic → Authorize → retour → Finaliser</b>. AWEMA fait l'échange tout seul.",
      "La partie « ligne de commande » est <b>réservée aux experts</b> : ignore-la." ] },
    "connect-youtube": { t: "Connecter YouTube", s: [
      "Crée une <b>clé API</b> Google (YouTube Data API v3) — pas d'OAuth, c'est public.",
      "Mets-la en Secret <code>YOUTUBE_API_KEY</code> et renseigne le <code>@handle</code> de la chaîne." ] },
    "connect-linkedin": { t: "Connecter LinkedIn", s: [
      "Il te faut une <b>Page entreprise</b> (admin) et une app LinkedIn vérifiée.",
      "⚠️ La vérification demande un <b>email pro</b> (pas gmail).",
      "Suis les étapes pour obtenir le token <code>LINKEDIN_TOKEN</code>." ] },
    "connect-whatsapp": { t: "Connecter WhatsApp Business", s: [
      "C'est un canal de <b>messagerie</b> (pas d'abonnés).",
      "Récupère token + Phone ID + WABA ID, mets-les en Secrets. (Connecteur en préparation.)" ] },
    "connect-ia": { t: "Brancher une IA (gratuite possible)", s: [
      "Choisis un fournisseur — plusieurs sont <b>gratuits</b> (Groq, Gemini, Ollama…).",
      "Crée une clé (bouton « Obtenir une clé »), puis : <code>awema set ia &lt;CLE&gt;=…</code>.",
      "Vérifie : <code>python3 scripts/awema_ai.py --check</code> → « ✅ IA active ».",
      "Sans IA, le feed « 3 choses à faire » marche quand même 👍" ] },
    oauth: { t: "Page de retour (OAuth)", s: [
      "Cette page récupère un <b>code</b> après autorisation.",
      "Copie-le (bouton) et suis l'instruction affichée pour l'échanger contre un jeton." ] },
    "revue-visuels": { t: "Revue des visuels", s: [
      "À gauche : la liste (filtre par pilier/plateforme/statut). Au centre : l'aperçu.",
      "À droite : copie la <b>description</b> et le <b>prompt</b>, note tes retours, change le statut.",
      "Flèches ← → pour passer au visuel suivant." ] },
    terms: { t: "Conditions d'utilisation", s: ["Les règles d'usage du service. Lis-les puis reviens en arrière."] },
    privacy: { t: "Confidentialité", s: ["Comment les données sont traitées. Lis puis reviens en arrière."] },
    _defaut: { t: "Awa est là pour t'aider", s: [
      "Tu es sur AWEMA. Reviens à l'accueil avec le bouton « ← » en haut.",
      "Besoin du cockpit ? Ouvre <code>outils/dashboard/index.html</code>." ] }
  };
  var dash = {
    t: "Ton cockpit de pilotage", s: [
      "Choisis un <b>client</b> dans le menu en haut.",
      "<b>Vue d'ensemble</b> = tes « 3 choses à faire aujourd'hui ». <b>Présence digitale</b> = ses vraies stats.",
      "Les vues marquées <b>« bientôt »</b> arrivent après la bêta.",
      "Raccourci : <b>Cmd/Ctrl + K</b> pour chercher. 🐝" ] };
  AIDE["index-dashboard"] = dash; AIDE.dashboard = dash;
  var d = AIDE[KEY] || AIDE._defaut;

  // ——— Mascotte SVG (abeille stylisée) ———
  var BEE = '<svg viewBox="0 0 48 48" width="30" height="30" aria-hidden="true">' +
    '<ellipse cx="24" cy="29" rx="12" ry="13" fill="#F4C430"/>' +
    '<path d="M16 24h16M15 30h18M17 36h14" stroke="#1a1206" stroke-width="3.4" stroke-linecap="round"/>' +
    '<ellipse cx="15" cy="17" rx="7" ry="5" fill="#F3E5BE" opacity=".92" transform="rotate(-25 15 17)"/>' +
    '<ellipse cx="33" cy="17" rx="7" ry="5" fill="#F3E5BE" opacity=".92" transform="rotate(25 33 17)"/>' +
    '<circle cx="20" cy="22" r="1.7" fill="#1a1206"/><circle cx="28" cy="22" r="1.7" fill="#1a1206"/>' +
    '<path d="M21 8c0-3 6-3 6 0" stroke="#1a1206" stroke-width="2" fill="none" stroke-linecap="round"/>' +
    '<circle cx="21" cy="7" r="1.6" fill="#1a1206"/><circle cx="27" cy="7" r="1.6" fill="#1a1206"/></svg>';

  // ——— CSS (charte AWEMA avec valeurs de repli) ———
  var css = document.createElement('style');
  css.textContent = [
    '.awa-btn{position:fixed;right:20px;bottom:20px;z-index:9998;width:58px;height:58px;border-radius:50%;',
    'border:none;cursor:pointer;display:grid;place-items:center;background:linear-gradient(135deg,#F4C430,#D4AF37);',
    'box-shadow:0 12px 26px -8px rgba(212,175,55,.7);transition:transform .18s}',
    '.awa-btn:hover{transform:translateY(-3px) scale(1.05)}',
    '.awa-btn .dot{position:absolute;top:-3px;right:-3px;width:16px;height:16px;border-radius:50%;',
    'background:#FF7D9C;color:#fff;font:700 11px/16px Poppins,sans-serif;text-align:center;animation:awaPulse 2s ease-in-out infinite}',
    '@keyframes awaPulse{0%,100%{box-shadow:0 0 0 0 rgba(255,125,156,.6)}70%{box-shadow:0 0 0 7px rgba(255,125,156,0)}}',
    '.awa-tip{position:fixed;right:84px;bottom:30px;z-index:9998;background:#292929;color:#F1EDE2;border:1px solid rgba(255,255,255,.14);',
    'border-radius:10px;padding:6px 11px;font:600 12px Poppins,sans-serif;white-space:nowrap;box-shadow:0 10px 24px -10px rgba(0,0,0,.6);opacity:0;transform:translateX(8px);transition:.25s;pointer-events:none}',
    '.awa-tip.on{opacity:1;transform:translateX(0)}',
    '.awa-pop{position:fixed;right:20px;bottom:88px;z-index:9999;width:min(340px,calc(100vw - 40px));',
    'background:#292929;border:1px solid rgba(255,214,102,.22);border-radius:18px;',
    'padding:18px;color:#F1EDE2;box-shadow:0 24px 60px -18px rgba(0,0,0,.6);',
    'font-family:Poppins,system-ui,sans-serif;backdrop-filter:blur(10px);transform:translateY(10px);opacity:0;',
    'pointer-events:none;transition:.2s}',
    '.awa-pop.on{transform:none;opacity:1;pointer-events:auto}',
    '.awa-pop h4{font-family:Montserrat,Poppins,sans-serif;font-size:15.5px;margin:0 0 4px;display:flex;gap:8px;align-items:center}',
    '.awa-pop .sub{font-size:11.5px;color:#B3AA92;margin-bottom:10px}',
    '.awa-pop ol{margin:0;padding-left:18px;display:grid;gap:7px}',
    '.awa-pop li{font-size:13px;line-height:1.5;color:#F1EDE2}',
    '.awa-pop code{background:rgba(0,0,0,.3);border-radius:5px;padding:1px 5px;font-size:11.5px}',
    '.awa-pop .ok{margin-top:13px;width:100%;border:none;border-radius:11px;padding:10px;cursor:pointer;',
    'font:700 13px Poppins,sans-serif;background:linear-gradient(135deg,#FFC94D,#EDA914);color:#222222}',
    '.awa-pop a{color:#FFC94D}'
  ].join('');
  document.head.appendChild(css);

  // ——— Construction ———
  function build() {
    var btn = document.createElement('button');
    btn.className = 'awa-btn'; btn.setAttribute('aria-label', "Besoin d'aide ? Clique sur Awa l'abeille");
    btn.title = "Besoin d'aide ? Clique sur Awa 🐝";
    btn.innerHTML = BEE + '<span class="dot">?</span>';
    var tip = document.createElement('div'); tip.className = 'awa-tip'; tip.textContent = "Besoin d'aide ?";
    btn.addEventListener('mouseenter', function(){ tip.classList.add('on'); });
    btn.addEventListener('mouseleave', function(){ tip.classList.remove('on'); });
    document.body.appendChild(tip);
    var pop = document.createElement('div');
    pop.className = 'awa-pop';
    pop.innerHTML = '<h4>' + BEE.replace('width="30" height="30"', 'width="22" height="22"') +
      ' ' + d.t + '</h4><div class="sub">Awa, l\'abeille d\'AWEMA — je te guide.</div>' +
      '<ol>' + d.s.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ol>' +
      '<button class="ok">Compris ✓</button>';
    document.body.appendChild(btn); document.body.appendChild(pop);
    function toggle(v) { pop.classList.toggle('on', v); btn.querySelector('.dot').style.display = v ? 'none' : ''; }
    btn.onclick = function () { toggle(!pop.classList.contains('on')); };
    pop.querySelector('.ok').onclick = function () { toggle(false); };
    // Première visite de CETTE page → ouvre une fois automatiquement
    try {
      var k = 'awema-awa-' + KEY;
      if (!localStorage.getItem(k)) { setTimeout(function () { toggle(true); }, 700); localStorage.setItem(k, '1'); }
    } catch (e) { }
  }
  if (document.body) build(); else document.addEventListener('DOMContentLoaded', build);
})();
