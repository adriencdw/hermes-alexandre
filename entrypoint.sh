#!/bin/bash

DATA=/opt/data

echo "=== DIAG ==="
echo "user: $(id)"
ls -la "$DATA/" 2>&1 | head -20
echo "=== .env ==="
ls -la "$DATA/.env" 2>&1 || echo ".env absent"
echo "=== rm .env ==="
rm -f "$DATA/.env" 2>&1 && echo "rm OK" || echo "rm ECHOUE"
echo "=== touch .env ==="
touch "$DATA/.env" 2>&1 && chmod 777 "$DATA/.env" && echo "touch OK" || echo "touch ECHOUE"
echo "============="

# Crée tous les dossiers nécessaires
for dir in logs sessions memories skills cron hooks; do
  mkdir -p "$DATA/$dir" && chmod 777 "$DATA/$dir"
done

# Config initiale
if [ ! -f "$DATA/config.yaml" ]; then
  cp /opt/hermes-default/config.yaml "$DATA/config.yaml"
fi

# Skills
if [ -d "/opt/hermes-default/skills" ] && [ ! -d "$DATA/skills/csv-export" ]; then
  cp -r /opt/hermes-default/skills/. "$DATA/skills/"
fi

# .env depuis les variables Railway
cat > "$DATA/.env" <<EOF
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
APIFY_TOKEN=${APIFY_TOKEN:-}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
TELEGRAM_ALLOWED_USERS=${TELEGRAM_ALLOWED_USERS:-}
TELEGRAM_HOME_CHANNEL=${TELEGRAM_HOME_CHANNEL:-8466667861}
TELEGRAM_HOME_CHANNEL_NAME=${TELEGRAM_HOME_CHANNEL_NAME:-Alexandre}
EOF
chmod 777 "$DATA/.env"

echo "[entrypoint] .env final: $(stat -c '%a %U:%G' $DATA/.env 2>/dev/null)"
echo "[entrypoint] Démarrage gateway..."
exec hermes gateway run
