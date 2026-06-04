#!/bin/bash
set -e

DATA=/opt/data

# Initialise la config si le volume est vierge
if [ ! -f "$DATA/config.yaml" ]; then
  echo "[entrypoint] Premier démarrage — initialisation de /opt/data"
  cp /opt/hermes-default/config.yaml "$DATA/config.yaml"
  mkdir -p "$DATA/skills" "$DATA/memories" "$DATA/sessions" "$DATA/logs" "$DATA/cron"
fi

# Copie les skills si dispo dans l'image et pas encore dans le volume
SKILLS_SRC="/opt/hermes-default/skills"
if [ -d "$SKILLS_SRC" ] && [ ! -d "$DATA/skills/csv-export" ]; then
  cp -r "$SKILLS_SRC/." "$DATA/skills/"
fi

# Crée le .env depuis les variables d'environnement Railway
cat > "$DATA/.env" <<EOF
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
APIFY_TOKEN=${APIFY_TOKEN:-}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
TELEGRAM_ALLOWED_USERS=${TELEGRAM_ALLOWED_USERS:-}
EOF

echo "[entrypoint] Fixe les permissions sur /opt/data..."
chmod -R 777 "$DATA" 2>/dev/null || true

echo "[entrypoint] Démarrage de la gateway Hermes..."
exec hermes gateway run
