---
titre: AWEMA — Donner l'accès à une agence (page de contrôle)
tags: [awema, admin, acces, controle, licence]
maj: 2026-06-26
---

# 🗝️ Donner l'accès à une agence — page de contrôle

> **Ta page Obsidian de référence** : tout le nécessaire quand tu veux donner l'accès à quelqu'un.
> Ouvre-la, suis la checklist, garde la main.

---

## ❓ « Y a-t-il un élément qu'ils ne pourront pas contourner ? » — la réponse honnête

**Dans le code : NON.** Le projet est open-source et auto-hébergé. Quiconque a le code peut retirer
n'importe quelle vérification logicielle (licence, bannière, « kill switch »). Toute serrure écrite
*dans le dépôt* est, par nature, **contournable** par une personne technique.

**Hors du code : OUI — l'accès aux API officielles.** C'est la **plateforme** (Meta, TikTok, LinkedIn)
qui l'applique, pas ton code. Après toute leur config, le **dernier élément manquant** pour que l'outil
soit *réellement* fonctionnel sur les Pages de **leurs** clients, c'est un **jeton de production valide**
— et celui-ci ne peut venir que d'une **App vérifiée** (Business Verification + App Review). Si cette App
est **la tienne** (statut *Tech Provider*), alors :

- ils **ne peuvent pas fabriquer** un jeton valide sans passer par toi ;
- tu **délivres et révoques** l'accès par agence, quand tu veux ;
- c'est **incontournable** car enforce côté Meta/TikTok, pas dans le dépôt.

> 🔑 **Ton vrai levier = être le fournisseur d'accès API (Tech Provider).** La « licence » ci-dessous
> est l'**outil opérationnel** (le code qu'on s'échange, le suivi, la base légale) ; l'**API access**
> est le **cadenas réel**.

### Les deux modèles — A par défaut, B sur demande validée
| Modèle | Quand | Ton contrôle |
|---|---|---|
| **A — Agence autonome (DÉFAUT)** : chaque agence crée SES propres Apps | Mode normal | Aucun besoin (licence + conditions) |
| **B — AWEMA Tech Provider** : l'agence passe par TES Apps, **pour clients communs**, **sur validation** | Opt-in, clients communs | **Fort, révocable, validé par toi** |

**Règle :** par défaut, **chaque agence fournit ses propres API**. Le passage par **tes** API n'a lieu que
pour des **clients communs/hébergés par AWEMA**, **après ton accord explicite** (accepte/refuse par agence).
Quand B s'applique, tu es le « robinet » → verrou réel et révocable.

### Demandes d'accès API managé — tu acceptes/refuses (par agence)
1. L'agence **demande** via `demande-acces.html` (email) — ou tu l'enregistres toi-même.
2. Tu **journalises** la demande (preuve) :
   `python3 scripts/awema.py acces demande "Baoulé Digital" contact=… client="…" reseau=meta motif="…"`
3. Tu **décides**, par agence : `awema acces accepter <id>` (note=…) **ou** `awema acces refuser <id>`.
   `awema acces lister` = état de toutes les demandes (preuve, `.awema/acces-api-registre.json`).
4. **Si accepté seulement** : tu ouvres l'accès côté plateforme (ajoute la Page à ton App Meta / testeur
   TikTok…) puis fournis le token. **Tant que tu n'as pas accepté + ouvert l'accès, rien ne transite par tes API.**

> C'est ça, ton contrôle : **rien ne passe par tes API sans ton accord**, et le registre le prouve.

---

## ✅ Checklist : donner l'accès à UNE agence
> (Par défaut, l'agence est autonome — étapes 1-4 + 6-7. L'étape 5, modèle B, **seulement** si elle a
> demandé un accès managé pour un client commun **et que tu l'as accepté**.)

1. **Réceptionne la candidature** (formulaire `rejoindre.html` → email). Vérifie le profil.
2. **Réserve une place** dans `config/beta-seats.json` (statut → `invite`, nom/handle/contact).
3. **Envoie l'email de bienvenue** (modèle : [[email-bienvenue]]) : lien du dépôt **copie d'accueil**
   (Template repository), `onboarding.html`, conditions ([[11-programme-beta]]), guide API ([[14-acces-api-agence]]).
4. **Délivre une licence** (enregistrée comme preuve) :
   `python3 scripts/awema.py licence delivrer "<Nom Agence>" contact=<email>` → clé à transmettre +
   inscription au **registre** (`awema licence registre` pour la liste). Détails ci-dessous.
5. **Donne l'accès API (le cadenas)** — modèle B :
   - Ajoute leur(s) Page(s) client(s) à **ton** App Meta (System User token *scopé* à ces Pages), ou
   - Ajoute-les comme **testeurs/utilisateurs** de tes Apps TikTok/LinkedIn le temps de la bêta.
   - Tu peux **révoquer** à tout moment côté plateforme → l'outil cesse de récupérer les données.
6. **Marque la place** `active` dans `config/beta-seats.json` + note la date.
7. **Suivi** : un retour utile/mois (issues GitHub). Sinon → avertissement (30 j) → recyclage.

### Révoquer un accès
- **API (effet immédiat, incontournable)** : retire la Page de ton App Meta / retire le testeur TikTok/LinkedIn,
  ou révoque le token. → plus aucune donnée ne remonte, quoi qu'ils fassent côté code.
- **Licence** : `python3 scripts/awema.py licence revoquer` (sur communication) + statut place → `recyclee`.
- **Place** : libère-la dans `config/beta-seats.json` (proposer à la liste d'attente).

---

## 📬 Tout sous la main (liens rapides)
- Formulaire de candidature : `rejoindre.html`
- Email de bienvenue (modèle) : [[email-bienvenue]]
- Conditions & prérequis : [[11-programme-beta]]
- Guide accès API (dev entreprise) : [[14-acces-api-agence]]
- Connecter une IA (gratuite) : `connect-ia.html` · [[12-connecter-ia]]
- Sécurité & isolation : [[13-securite-donnees]]
- Suivi des 20 places : `config/beta-seats.json`
- Générer la copie d'accueil : `python3 scripts/preparer-copie-beta.py ../awema-beta`
- Licence : `python3 scripts/awema.py licence …` (delivrer / set / verifier / revoquer)

---

## 🧩 Délivrer une licence — et la PROUVER (ta base juridique)

> Tu n'as pas besoin d'un verrou technique incontournable : tu as besoin de **prouver à qui tu as
> délivré une licence, et à qui non**. C'est exactement ce que fait le **registre de délivrance**.

**1. Délivrer** (génère une clé unique + l'enregistre comme preuve, horodatée) :
```
python3 scripts/awema.py licence delivrer "Baoulé Digital" contact=awa@baoule.ci
```
→ te donne la clé (ex. `AWEMA-7124-3CE6-48BC`) à transmettre à l'agence, et l'inscrit dans le
**registre privé** `.awema/licences-registre.json` (gitignoré — **à sauvegarder**, c'est ta preuve).

**2. L'agence active** son instance avec la clé que tu lui envoies :
```
python3 scripts/awema.py licence set AWEMA-7124-3CE6-48BC
```
(Sans clé valide, son dashboard affiche **« Instance non activée — contacte AWEMA ».»**)

**3. Prouver / vérifier à tout moment** :
```
python3 scripts/awema.py licence registre              # qui a reçu une licence, quand, statut
python3 scripts/awema.py licence verifier-cle <cle>    # « Délivrée à X le … » ou « pas dans ton registre »
```
→ Le registre est **ta preuve** : pour chaque licence, `agence · contact · date · clé · hash · statut`.
Tu peux démontrer **qui** est légitime (présent au registre) et **qui ne l'est pas** (absent).

**4. Révoquer** (sur manquement) :
```
python3 scripts/awema.py licence revoquer-cle <cle>    # marque « revoquee » dans le registre (preuve)
```
… **et** révoque l'accès API (modèle B) — c'est le seul effet *techniquement* incontournable.

### Limites & vérité
- La vérification *dans* l'instance (`set`/bannière) est **éditable** (code open-source) → c'est un
  **frein + une base légale**, pas une serrure. Tes **conditions** (docs/11) l'exigent ; ton **registre**
  le prouve.
- Le **verrou réel** reste l'**accès API** (tu es le robinet, modèle B).
- Le registre vit en local (`.awema/`, privé) : **sauvegarde-le** (clé USB chiffrée / dépôt privé / coffre).

> En résumé : **API = verrou incontournable ; registre de licences = ta preuve juridique ; conditions =
> ton cadre.** Les trois ensemble = tu gardes la main, et tu peux le prouver.
