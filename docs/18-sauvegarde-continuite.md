# 18 — Sauvegarde & continuité d'activité

> Réponse à : « tout AWEMA (site, automatisation, données, clés) vit sur GitHub — que se passe-t-il si
> GitHub tombe en panne, si mon compte est suspendu ou compromis ? »

## 1. Comprendre ce qui est en jeu

GitHub porte **cinq rôles à la fois** dans AWEMA : l'hébergement du site (Pages), le moteur
d'automatisation (Actions), les données clients (le dépôt), les clés (Secrets/Variables) et ta
connexion (le PAT). Tout n'a pas le même niveau de risque :

| Quoi | Récupérable ? | Comment |
|---|---|---|
| **Le dépôt** (code + données clients + historique) | ✅ Totalement | Chaque `git clone` est une sauvegarde complète |
| **Clés IA / Meta / LinkedIn / YouTube** (Secrets) | ✅ Re-créables | Tu les regénères chez le fournisseur en quelques minutes |
| **Refresh tokens TikTok** (Variable `TIKTOK_TOKENS`) | ⚠️ **NON exportables** | Ils n'existent **que** dans la Variable GitHub ; perdus → ré-autoriser chaque compte TikTok (le bouton « Se connecter avec TikTok », ~2 min par compte) |
| **Ton PAT** | ✅ Re-créable | 1 minute dans les réglages GitHub |

**La seule perte irréversible** est donc la liste des tokens TikTok — et sa réparation est une
ré-autorisation, pas une perte de données.

## 2. La routine de sauvegarde (5 minutes par mois)

1. **Clone miroir du dépôt** sur ton ordinateur (ou un disque externe) :
   ```
   git clone --mirror https://github.com/TON-COMPTE/TON-DEPOT.git sauvegarde-awema.git
   ```
   Les mois suivants : `cd sauvegarde-awema.git && git remote update`. Pas de terminal ? Le bouton
   **Code → Download ZIP** de GitHub fait une sauvegarde correcte (sans l'historique).
2. **Range tes clés dans le coffre local** au moment où tu les crées : le CLI `awema` a un store
   local chiffré par les droits du fichier (`.awema/`, jamais dans le dépôt) —
   `python3 scripts/awema.py set meta META_TOKEN=…`. Ainsi une clé notée dans `.awema/` sur TON
   poste survit à la perte du compte GitHub.
3. **Note quelque part hors GitHub** (gestionnaire de mots de passe) : la liste de tes fournisseurs
   de clés (Groq, Meta, LinkedIn…) et le compte e-mail associé à chacun. C'est ce qui rend la
   re-création rapide.

## 3. Scénarios de panne

### GitHub est en panne (quelques heures)
Rien à faire. Les posts « dus » pendant la panne seront publiés **au premier cron qui repasse**
(le moteur sélectionne tout ce qui est dû, pas seulement l'instant présent). Le dashboard revient
avec Pages. C'est le scénario bénin.

### Mon compte GitHub est suspendu ou inaccessible
1. Crée un nouveau compte (ou récupère l'ancien via le support GitHub).
2. Pousse ta sauvegarde miroir : `cd sauvegarde-awema.git && git push --mirror https://github.com/NOUVEAU/DEPOT.git`.
3. Réactive Pages + les workflows (bandeau « enable » de l'onglet Actions — voir tutoriel, étape 1 bis).
4. Recolle tes clés (Secrets) depuis ton coffre local / les fournisseurs.
5. Ré-autorise les comptes TikTok (seule étape sans raccourci).
   → **Temps de reprise réaliste : une demi-journée**, zéro donnée client perdue si la sauvegarde
   mensuelle est faite.

### Mon PAT ou une clé a fuité (machine partagée, etc.)
1. **Révoque** immédiatement : GitHub → Settings → Developer settings → le token « awema » → Delete.
2. Côté navigateur : dashboard → Réglages → **« Se déconnecter »** sur le poste concerné.
3. Recrée un PAT (expiration 90 jours recommandée) et reconnecte-toi.
4. Si un token social a fuité (META_TOKEN…) : révoque-le chez le fournisseur puis regénère.

## 4. Ce qu'on ne fait PAS (et pourquoi)

- **Pas d'export automatique des Secrets vers un artefact** : un fichier de tokens qui traîne dans
  les artefacts de CI est une fuite en puissance ; la re-création manuelle est plus sûre.
- **Pas de miroir automatique vers un second hébergeur** pour l'instant : c'est de la complexité
  permanente pour un scénario rare — la sauvegarde mensuelle §2 couvre le besoin. Si le projet
  grossit, un `git push --mirror` planifié vers GitLab/Codeberg est l'évolution naturelle.

## 5. Checklist

- [ ] J'ai un clone miroir du dépôt datant de moins d'un mois.
- [ ] Mes clés sont dans le coffre local `.awema/` (ou re-créables : je sais chez qui et avec quel compte).
- [ ] Je sais que les tokens TikTok se réparent par ré-autorisation (pas de panique).
- [ ] Mon PAT a une date d'expiration.
- [ ] Sur machine partagée : je me déconnecte du dashboard en partant.
