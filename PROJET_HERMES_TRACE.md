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
| LLM | ~~claude-opus-4-6~~ → **claude-haiku-4-5-20251001** (Anthropic) |
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

## Mises à jour (session du 2026-06-04 — suite)

- [x] LLM changé de claude-opus-4-6 → **claude-haiku-4-5-20251001** (moins cher)
- [x] Skill Immoweb créé (`skills/immoweb/`) avec :
  - URL builder pour Immoweb.be (type, transaction, filtres, communes)
  - Recherches sauvegardées dans `/opt/data/saved_searches.json`
  - Instructions complètes pour Hermes dans `SKILL.md`
- [x] Actor Apify Immoweb : `crawlerbros/immoweb-scraper` (ID: `UUjIYNdzU5Mo8szQN`)
  - Input : `searchUrls`, `maxItems`, `proxyConfiguration` (RESIDENTIAL BE obligatoire)
  - Output : `price`, `bedrooms`, `livingArea`, `locality`, `postcode`, `energyClass`, etc.

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

## Étapes restantes / TODOs

- [ ] **Ajouter l'ID Telegram du client** dans `TELEGRAM_ALLOWED_USERS` sur Railway
      → Format : `8466667861,ID_DU_CLIENT` (Adrien + client)
      → Railway dashboard → service → Variables → TELEGRAM_ALLOWED_USERS
      → L'ID Telegram d'Adrien (8466667861) est déjà présent
- [ ] Vérifier que le volume Railway `/opt/data` est bien attaché (fait manuellement le 2026-06-04)
- [ ] Tester une recherche Immoweb de bout en bout depuis Telegram
- [ ] Vérifier que les recherches sauvegardées persistent après redémarrage du container

## Accès Telegram — utilisateurs autorisés

| Utilisateur | ID Telegram | Statut |
|---|---|---|
| Adrien (admin) | `8466667861` | ✓ configuré |
| Alexandre (client) | à fournir | ⏳ en attente |

Pour ajouter le client : Railway dashboard → service hermes-alexandre
→ Variables → `TELEGRAM_ALLOWED_USERS` → `8466667861,ID_ALEXANDRE`

## Mémoire persistante Hermes

Fichiers copiés au premier démarrage du container (dans `/opt/data/`) :

| Fichier | Rôle |
|---|---|
| `SOUL.md` | Identité de l'agent, instructions générales |
| `memories/immoweb-skill.md` | Instruction permanente : utiliser le skill Immoweb pour toute recherche |

Ces fichiers sont dans `hermes-init/` dans le repo Git.
**Ne pas écraser** si déjà présents sur le volume (l'entrypoint vérifie avant de copier).

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

Pour reproduire ce setup from scratch :

1. Créer un projet Railway → connecter le repo GitHub `adriencdw/hermes-alexandre`
2. Ajouter un volume Railway monté sur `/opt/data`
3. Ajouter les 4 variables d'env (voir tableau Secrets ci-dessus)
4. Railway build le Dockerfile et démarre automatiquement

Les secrets ne sont **jamais** dans ce fichier ni dans git.

---

## Problèmes rencontrés — Leçons pour le futur

> Section rédigée après la session de déploiement du 2026-06-04.
> But : ne pas répéter ces erreurs sur un prochain projet similaire.

---

### 1. Mauvaise compréhension de Modal dans le document de setup

**Ce qui s'est passé :** Le document `hermes-modal-setup.md` décrivait Modal comme un backend
"serverless complet" pour Hermes. On a passé du temps à configurer Modal avant de réaliser
que Modal ne gère que le terminal backend (exécution de commandes shell), pas la gateway
Telegram. La gateway doit tourner quelque part en permanence.

**Pourquoi :** Le document d'instructions mélangeait deux concepts : l'exécution des outils
(Modal) et l'hébergement de l'agent (gateway). Ce n'est pas la même chose.

**Comment éviter :** Avant de commencer tout setup d'agent avec gateway, poser la question :
*"Où tourne le processus qui écoute les messages en permanence ?"* Si la réponse n'est pas
claire dans le doc, chercher sur la doc officielle avant de coder. Ici : Railway/Fly.io pour
la gateway, pas Modal.

---

### 2. python-telegram-bot absent de l'image locale

**Ce qui s'est passé :** `hermes gateway start` échouait localement car
`python-telegram-bot` n'était pas installé dans le venv Hermes.

**Pourquoi :** C'est une dépendance optionnelle de Hermes (gateway Telegram) non installée
par défaut.

**Comment éviter :** Toujours lancer `hermes doctor` en premier — il liste les dépendances
manquantes. Fix : `uv pip install python-telegram-bot` dans le venv Hermes.

---

### 3. Incident Railway (504 sur toute l'API) pendant le déploiement

**Ce qui s'est passé :** Au milieu du déploiement, toutes les requêtes Railway (upload,
redeploy, GraphQL) retournaient 504. On a passé ~30 minutes à déboguer ce qui semblait être
un problème de code, alors que c'était un incident côté Railway.

**Pourquoi :** Railway avait un incident infrastructure ce jour-là.

**Comment éviter :** Si plusieurs opérations Railway différentes échouent toutes avec 504,
vérifier https://status.railway.com avant de chercher une cause dans le code. Attendre
la résolution de l'incident plutôt que de multiplier les tentatives de déploiement.

---

### 4. Cache Docker Railway — changements Dockerfile non pris en compte

**Ce qui s'est passé :** Après avoir ajouté `COPY skills/` dans le Dockerfile, Railway
continuait à builder une image à 4 étapes (l'ancienne), ignorant le changement. Plusieurs
redéploiements successifs n'ont rien changé.

**Pourquoi :** Railway met en cache les layers Docker. Quand la couche FROM n'a pas changé,
il peut réutiliser les layers suivants même si le Dockerfile a changé en local — surtout
quand on fait `railway up` depuis le poste local (upload tarball) plutôt que depuis GitHub.

**Comment éviter :**
- Connecter Railway directement au repo GitHub (auto-deploy sur push) plutôt que d'utiliser
  `railway up` depuis le local. Le déploiement GitHub force un build propre.
- Si `railway up` est utilisé, vérifier les build logs en comptant les étapes : si le nombre
  d'étapes ne correspond pas au Dockerfile, c'est du cache.

---

### 5. Crash loop entrypoint à cause de `set -e` + `cp` sur dossier absent

**Ce qui s'est passé :** Le premier entrypoint avait `set -e` et essayait de copier
`/opt/hermes-default/skills/` qui n'existait pas dans l'image (le `COPY skills/` du Dockerfile
n'avait pas été pris en compte, voir problème 4). Le `cp` échouait → `set -e` → exit → Railway
redémarrait → boucle infinie.

**Pourquoi :** `set -e` fait échouer tout le script au premier erreur, même sur des opérations
optionnelles.

**Comment éviter :** Dans les entrypoints Docker :
- Ne mettre `set -e` que si chaque commande est critique.
- Toujours protéger les opérations optionnelles avec `|| true` ou des guards `if [ -d ... ]`.
- Tester l'entrypoint localement avec `docker run` avant de déployer.

---

### 6. Permission denied sur `/opt/data/.env` — user `hermes` dans l'image de base

**Ce qui s'est passé :** Le plus long à déboguer. Hermes échouait à lire `/opt/data/.env`
avec `PermissionError`. On a essayé `chmod`, `USER root`, réécriture du fichier — rien
ne semblait marcher pendant plusieurs itérations.

**Pourquoi :** L'image Docker `nousresearch/hermes-agent` crée `/opt/data` avec comme
propriétaire l'utilisateur `hermes` (non-root) et le mode `700` (drwx------). Sans
`USER root` dans notre Dockerfile, l'entrypoint tournait en tant que `hermes` et ne pouvait
pas écrire un `.env` propre. Une fois `USER root` ajouté, l'entrypoint tournait bien en
root (confirmé par les logs), mais on voyait encore l'erreur — parce que les logs affichés
venaient encore de l'ancien container en cours de remplacement.

**Ce qui a finalement résolu :** Ajouter `USER root` dans le Dockerfile + rendre l'entrypoint
complètement idempotent (rm -f + touch + chmod 777 explicites sur chaque dossier).

**Comment éviter :**
- Toujours vérifier le USER par défaut d'une image de base : `docker inspect <image> | grep User`.
- Pour les images dont on hérite, ajouter `USER root` explicitement si l'entrypoint doit
  créer des fichiers.
- Ajouter des `echo "user: $(id)"` et `ls -la` dans l'entrypoint dès le début pour diagnostiquer
  rapidement, pas après 5 itérations.
- Ne pas confondre "les logs montrent encore l'erreur" avec "le fix n'a pas marché" — Railway
  affiche quelques secondes de l'ancien container pendant la transition.

---

### 7. Pas de volume Railway attaché malgré `railway.toml`

**Ce qui s'est passé :** Le `railway.toml` déclarait `[[volumes]]` avec `mountPath = "/opt/data"`,
mais Railway n'a pas créé le volume automatiquement via `railway up`. La requête GraphQL
confirmait 0 volumes attachés au projet.

**Pourquoi :** `railway up` uploade du code mais ne provisionne pas l'infrastructure déclarée
dans `railway.toml` (volumes, etc.). L'infrastructure se configure via le dashboard ou via
`railway volume` CLI.

**Comment éviter :** Après chaque `railway up` initial, vérifier que les volumes sont bien
créés via le dashboard Railway ou `railway volume list`. Le volume persistant est essentiel
pour que les sessions, mémoires et CSV survivent aux redémarrages.
