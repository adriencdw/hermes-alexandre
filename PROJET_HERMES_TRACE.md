# Trace Projet — Hermes Agent + Apify Immoweb

> Document de référence pour la reproductibilité. Mis à jour au fil des sessions.
> Auteur : Adrien (via Claude Code). Client : Alexandre.

---

## Objectif

Faire tourner **Hermes Agent** (NousResearch, open-source MIT) sur **Modal** (serverless),
connecté à **Telegram**, avec le **MCP Apify** branché sur le scraper Immoweb Belgium,
et une **sauvegarde automatique des données en CSV** sur un Modal Volume persistant.

Flux cible :
```
Alexandre (Telegram) → Hermes Agent (Modal) → MCP Apify → Immoweb scraper → CSV sur Modal Volume
```

---

## Stack technique

| Composant | Version / Détail |
|---|---|
| Hermes Agent | v0.14.0 (NousResearch, MIT) |
| Modal CLI | v1.4.0 |
| Python (Hermes interne) | 3.11.15 |
| LLM | claude-opus-4-6 (Anthropic) |
| MCP Apify | `@apify/actors-mcp-server` via npx (stdio) |
| Actor Immoweb | `crawlerbros/immoweb-scraper` (ID: `UUjIYNdzU5Mo8szQN`) |
| Stockage CSV | Modal Volume `hermes-data`, monté sur `/data` |
| Gateway messagerie | Telegram (long polling) |

---

## Fichiers clés

```
~/.hermes/
├── config.yaml          ← backend modal, mcp_servers Apify
├── .env                 ← tous les secrets (ANTHROPIC_API_KEY, APIFY_TOKEN, TELEGRAM_*)
├── skills/csv-export/
│   ├── SKILL.md         ← description du skill pour Hermes
│   ├── append_csv.py    ← append items → /data/apify_export.csv
│   └── run_and_export.py ← run actor Immoweb + export CSV en un appel
└── SOUL.md              ← identité de l'agent

/home/adrien/Time2Code/Alexandre/
├── hermes-modal-setup.md   ← instruction de setup initiale (source de vérité)
├── PROJET_HERMES_TRACE.md  ← CE FICHIER
└── client_besoins.md       ← besoins client Alexandre
```

---

## Secrets configurés (ne jamais committer)

Tous dans `~/.hermes/.env` :

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Clé API Anthropic pour claude-opus-4-6 |
| `APIFY_TOKEN` | Clé Apify pour le scraper Immoweb |
| `TELEGRAM_BOT_TOKEN` | Token du bot Telegram (créé via @BotFather) |
| `TELEGRAM_ALLOWED_USERS` | `8466667861` (ID Telegram d'Alexandre) |

---

## Configuration config.yaml (changements par rapport au défaut)

```yaml
# Backend terminal → Modal (serverless, hiberne entre sessions)
terminal:
  backend: modal

# MCP Apify déclaré en stdio via npx
mcp_servers:
  apify:
    command: "npx"
    args: ["-y", "@apify/actors-mcp-server"]
    env:
      APIFY_TOKEN: "${APIFY_TOKEN}"
```

---

## Infrastructure Modal

| Ressource | Nom | Créé le |
|---|---|---|
| Volume persistant | `hermes-data` | 2026-06-04 |
| Compte Modal | `adriencdw` | pré-existant |

Le CSV est écrit dans `/data/apify_export.csv` sur le volume `hermes-data`.
Ce chemin survit à l'hibernation de l'environnement Modal.

---

## Actor Apify — Immoweb Belgium

- **Nom** : Immoweb Belgian Real Estate Scraper
- **Actor ID** : `UUjIYNdzU5Mo8szQN`
- **Auteur** : crawlerbros
- **URL** : https://apify.com/crawlerbros/immoweb-scraper
- **Pricing** : pay-per-result, **$1.00 / 1 000 résultats**
- **Modèle de paiement** : crédits Apify à la demande (pas d'abonnement mensuel obligatoire)

### Prérequis paiement Apify

Oui, il faut des crédits sur le compte Apify avant de lancer le scraper en production :
1. Se connecter sur [console.apify.com](https://console.apify.com)
2. Billing → Add credits (carte bancaire ou PayPal)
3. Le premier scrape de test peut être gratuit (free tier Apify : $5 de crédits offerts à l'inscription)

---

## Étapes réalisées (session du 2026-06-04)

- [x] Vérification des prérequis (Python, Node, Modal, Hermes déjà installés)
- [x] `ANTHROPIC_API_KEY` ajouté dans `~/.hermes/.env`
- [x] `TELEGRAM_BOT_TOKEN` ajouté dans `~/.hermes/.env`
- [x] `TELEGRAM_ALLOWED_USERS=8466667861` ajouté dans `~/.hermes/.env`
- [x] `APIFY_TOKEN` ajouté dans `~/.hermes/.env`
- [x] `terminal.backend` passé à `modal` dans `config.yaml`
- [x] Modal Volume `hermes-data` créé
- [x] MCP Apify déclaré dans `config.yaml` (bloc `mcp_servers`)
- [x] Skill CSV créé dans `~/.hermes/skills/csv-export/`

## Étapes restantes

- [ ] Vérifier les crédits Apify sur console.apify.com (ou ajouter un moyen de paiement)
- [ ] `hermes doctor` → vérifier qu'il passe sans erreur bloquante
- [ ] `hermes gateway start` → démarrer la gateway Telegram
- [ ] Dans une session Hermes : `/reload-mcp` → vérifier que les outils `mcp_apify_*` apparaissent
- [ ] Lancer un scrape Immoweb de test (quelques résultats) et vérifier le CSV sur le volume
- [ ] Vérifier la persistance après hibernation : `modal volume ls hermes-data`

---

## Commandes utiles

```bash
# Diagnostic Hermes
hermes doctor

# Démarrer la gateway Telegram (en arrière-plan)
hermes gateway start

# Vérifier le CSV sur le volume Modal
modal volume ls hermes-data
modal volume get hermes-data /apify_export.csv ./local_check.csv

# Recharger le MCP dans une session Hermes active
/reload-mcp

# Mettre à jour Hermes
hermes update

# Lancer manuellement un export CSV depuis un dataset Apify
python3 ~/.hermes/skills/csv-export/run_and_export.py '{"startUrls": [{"url": "https://www.immoweb.be/fr/recherche/maison/a-vendre"}]}'
```

---

## Notes de reproductibilité

Pour reproduire ce setup from scratch sur une nouvelle machine :

1. Installer Hermes : `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
2. Installer Modal : `pip install modal && modal token new`
3. Créer le volume : `modal volume create hermes-data`
4. Copier `~/.hermes/config.yaml` (ou appliquer les changements listés ci-dessus)
5. Renseigner les 4 variables dans `~/.hermes/.env` (voir tableau Secrets)
6. Copier `~/.hermes/skills/csv-export/` sur la nouvelle machine
7. `hermes gateway start` → tester depuis Telegram

Les secrets ne sont **jamais** dans ce fichier ni dans git.
