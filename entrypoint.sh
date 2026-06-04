#!/bin/bash
set -e

DATA=/opt/data

# Initialise la config si le volume est vierge
if [ ! -f "$DATA/config.yaml" ]; then
  echo "[entrypoint] Premier démarrage — initialisation de /opt/data"
  cp /opt/hermes-default/config.yaml "$DATA/config.yaml"
  mkdir -p "$DATA/skills" "$DATA/memories" "$DATA/sessions" "$DATA/logs" "$DATA/cron"
fi

# Crée le .env depuis les variables d'environnement Railway
cat > "$DATA/.env" <<EOF
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
APIFY_TOKEN=${APIFY_TOKEN}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_ALLOWED_USERS=${TELEGRAM_ALLOWED_USERS}
EOF

# Copie les skills du repo si absents
if [ ! -d "$DATA/skills/csv-export" ] && [ -d "/opt/hermes-default/skills" ]; then
  cp -r /opt/hermes-default/skills "$DATA/"
fi

exec hermes gateway run
