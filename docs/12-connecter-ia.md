# 12 — Connecter une IA (n'importe laquelle)

> AWEMA est **agnostique** : tu branches **l'IA de ton choix** pour faire tourner les agents
> (Analyste, Stratège, Créatif…). Tout fournisseur **compatible OpenAI** ou **Anthropic** marche.
> **Sans clé, les agents sont simplement désactivés** (le reste de l'outil fonctionne).
> Guide visuel équivalent : **`connect-ia.html`**.

## ⭐ Options avec un palier GRATUIT / des crédits d'essai
| Fournisseur | Offre | Clé | Inscription |
|---|---|---|---|
| **Groq** | Palier gratuit généreux, très rapide | `GROQ_API_KEY` | console.groq.com/keys |
| **Google Gemini** | Palier gratuit généreux | `GEMINI_API_KEY` | aistudio.google.com/apikey |
| **OpenRouter** | Modèles « :free » sans frais | `OPENROUTER_API_KEY` | openrouter.ai/keys |
| **Cerebras** | Palier gratuit, ultra-rapide | `CEREBRAS_API_KEY` | cloud.cerebras.ai |
| **Mistral** | Palier d'essai gratuit | `MISTRAL_API_KEY` | console.mistral.ai |
| **GitHub Models** | Gratuit (dev) | `GITHUB_MODELS_TOKEN` | github.com/marketplace/models |
| **Ollama (local)** | 100% local & gratuit, hors-ligne | *(aucune)* | ollama.com |
| Anthropic (Claude) | Crédits d'essai · raisonnement élevé | `ANTHROPIC_API_KEY` | console.anthropic.com |
| OpenAI | Payant | `OPENAI_API_KEY` | platform.openai.com |

> Liste à jour + modèles par défaut : `config/ia-providers.json` · `python3 scripts/awema_ai.py --providers`.

## Comment ça marche
1. **Crée une clé** chez le fournisseur de ton choix (les ★ ci-dessus sont gratuits).
2. **Donne la clé à AWEMA**, au choix :
   - **Local** : `python3 scripts/awema.py set ia GROQ_API_KEY=…` (rangée dans `.awema/`, gitignorée).
   - **Automatisation** : ajoute-la en **Secret GitHub** (Settings → Secrets → Actions). Le workflow
     `agents.yml` (quotidien) la lira.
   - **Variable d'env** : `export GROQ_API_KEY=…`.
3. **(Optionnel) choisis le fournisseur** s'il y en a plusieurs : `AWEMA_AI_PROVIDER=groq`
   (ou `awema set ia AWEMA_AI_PROVIDER=groq`). Sinon, AWEMA **auto-détecte** le premier dont la clé existe.
4. **(Optionnel) choisis le modèle** : `AWEMA_AI_MODEL=…` (sinon le modèle par défaut du fournisseur).
5. **Vérifie** : `python3 scripts/awema_ai.py --check` → « ✅ IA active : … ».
6. **Lance les agents** : `python3 scripts/run-agent.py analyste --all` (puis stratege, creatif), ou
   le workflow « Agents IA ». `actions-du-jour` fonctionne **même sans IA** (alertes déterministes).

## Changer d'IA / faire tourner les clés
- Changer de fournisseur : règle `AWEMA_AI_PROVIDER` (ou retire l'ancienne clé).
- Rotation : `awema rotate ia <CLE>=<nouvelle>` (garde l'historique) + mets à jour le Secret GitHub.

## Pourquoi agnostique ?
- **Zéro verrou** : tu n'es pas lié à un fournisseur ni à ses prix.
- **Gratuit possible** : démarre la bêta sans dépense (Groq/Gemini/OpenRouter/Ollama).
- **ADN respecté** : stdlib uniquement, aucune clé dans le dépôt, skip gracieux.

> Ajouter un fournisseur non listé : ajoute une entrée dans `config/ia-providers.json`
> (`type`: `openai` ou `anthropic`, `base_url`, `model`, `cle`). Rien d'autre à coder.
