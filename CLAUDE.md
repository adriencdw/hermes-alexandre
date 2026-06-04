# CLAUDE.md — Instructions & Raisonnements du Projet Hermes/Apify

> Ce fichier est destiné à Claude Code pour les sessions futures.
> Il explique les décisions d'architecture, ce qui a été essayé, ce qui a été abandonné, et pourquoi.

---

## Contexte du projet

**Client :** Alexandre
**Objectif :** Un agent IA (Hermes) accessible via Telegram, capable de scraper
les annonces immobilières sur Immoweb Belgium (via Apify) et de sauvegarder les
résultats dans un CSV persistant. Zéro maintenance manuelle, zéro serveur perso.

**Fichier de trace complet :** `PROJET_HERMES_TRACE.md`

---

## Stack retenue

| Composant | Choix | Raison |
|---|---|---|
| Agent IA | Hermes (NousResearch, MIT) | Open-source, gateway Telegram native, skills system, mémoire persistante |
| LLM | claude-opus-4-6 (Anthropic) | Clé disponible, modèle solide pour le raisonnement |
| Hosting gateway | Railway | Docker officiel Hermes, volume persistant simple, ~$2.5/mois |
| Scraping | Apify MCP (actors-mcp-server) | Pay-per-result ($1/1000), pas d'infra à maintenir |
| Actor Immoweb | crawlerbros/immoweb-scraper (UUjIYNdzU5Mo8szQN) | Seul actor actif pour Immoweb Belgium |
| Stockage CSV | Volume Railway `/opt/data/` | Persistant, survit aux redémarrages |
| Messagerie | Telegram (long polling) | Simple, pas de webhook public requis |

---

## Ce qui a été abandonné et pourquoi

### Modal — abandonné

Le document initial (`hermes-modal-setup.md`) préconisait Modal comme backend serverless.

**Problème découvert en session :** Modal dans Hermes = uniquement le backend terminal
(exécution de commandes shell). La gateway Telegram doit quand même tourner quelque
part en permanence. Modal n'est pas prévu pour des processus longs et persistants
comme une gateway.

**Conclusion :** Modal ajoute de la complexité sans résoudre le besoin central
(hosting de la gateway). Railway fait les deux : héberge la gateway ET persiste les données.

### Fly.io — non retenu

Mentionné dans la doc officielle Hermes pour le mode webhook Telegram.
Plus complexe à configurer (CLI flyctl, fly.toml, certificats TLS).
Railway est plus simple pour ce cas d'usage et le coût est identique.

---

## Architecture déployée

```
Alexandre (Telegram) ──→ Hermes Gateway (Railway container)
                              │
                              ├─→ claude-opus-4-6 (Anthropic API) — LLM
                              │
                              ├─→ MCP Apify (npx @apify/actors-mcp-server)
                              │      └─→ Actor Immoweb (UUjIYNdzU5Mo8szQN)
                              │             └─→ résultats scraping
                              │
                              └─→ CSV append → /opt/data/apify_export.csv
                                               (Railway persistent volume)
```

---

## Structure du repo

```
.
├── CLAUDE.md                  ← ce fichier
├── PROJET_HERMES_TRACE.md     ← trace chronologique des sessions
├── Dockerfile                 ← étend nousresearch/hermes-agent:latest
├── entrypoint.sh              ← init /opt/data + crée .env depuis Railway env vars
├── railway.toml               ← config Railway (volume /opt/data)
├── config.yaml                ← config Hermes sans secrets
├── .env.example               ← template des variables requises
├── .gitignore                 ← exclut .env, logs, sessions
└── skills/
    └── csv-export/
        ├── SKILL.md
        ├── append_csv.py      ← append items → /opt/data/apify_export.csv
        └── run_and_export.py  ← run actor Immoweb + export CSV
```

---

## Secrets (jamais dans git)

Tous configurés comme variables d'environnement Railway :

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Clé API Anthropic |
| `APIFY_TOKEN` | Clé API Apify |
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram (@BotFather) |
| `TELEGRAM_ALLOWED_USERS` | ID Telegram d'Alexandre : `8466667861` |

---

## Déploiement Railway — étapes

1. Créer un projet Railway → "Deploy from GitHub repo"
2. Sélectionner ce repo
3. Ajouter un volume monté sur `/opt/data`
4. Ajouter les 4 variables d'environnement (voir tableau ci-dessus)
5. Railway build le Dockerfile et démarre `hermes gateway run`

---

## Coûts mensuels estimés

| Service | Coût |
|---|---|
| Railway (gateway + volume) | ~$2.50/mois |
| Anthropic (claude-opus-4-6) | ~$0.015/message |
| Apify Immoweb scraper | $1.00 / 1 000 résultats |

---

## Commandes utiles en session future

```bash
# Vérifier les logs Railway
railway logs

# Télécharger le CSV depuis le volume Railway
railway volume download /opt/data/apify_export.csv

# Mettre à jour Hermes (rebuild Railway)
git commit --allow-empty -m "chore: rebuild" && git push

# Vérifier l'état local (si test local nécessaire)
hermes doctor
hermes gateway status
```

---

## Reproduire le setup from scratch

1. `git clone git@github.com:adriencdw/hermes-alexandre.git`
2. Créer un projet Railway, connecter le repo GitHub
3. Ajouter volume `/opt/data` + les 4 variables d'env
4. Railway déploie automatiquement au push sur `main`
