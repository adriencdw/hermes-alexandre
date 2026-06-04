#!/bin/bash

DATA=/opt/data

# Crée tous les dossiers nécessaires avec les bonnes permissions
for dir in logs sessions memories skills cron hooks; do
  mkdir -p "$DATA/$dir"
  chmod 777 "$DATA/$dir"
done

# Initialise la config si le volume est vierge
if [ ! -f "$DATA/config.yaml" ]; then
  echo "[entrypoint] Premier démarrage — copie de la config"
  cp /opt/hermes-default/config.yaml "$DATA/config.yaml"
  chmod 666 "$DATA/config.yaml"
fi

# Copie les skills si dispo dans l'image et pas encore dans le volume
if [ -d "/opt/hermes-default/skills" ] && [ ! -d "$DATA/skills/csv-export" ]; then
  cp -r /opt/hermes-default/skills/. "$DATA/skills/"
  chmod -R 777 "$DATA/skills"
fi

# Crée le .env depuis les variables d'environnement Railway
cat > "$DATA/.env" <<EOF
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
APIFY_TOKEN=${APIFY_TOKEN:-}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
TELEGRAM_ALLOWED_USERS=${TELEGRAM_ALLOWED_USERS:-}
EOF
chmod 600 "$DATA/.env"

echo "[entrypoint] Utilisateur: $(id)"
echo "[entrypoint] Permissions /opt/data/logs: $(ls -la $DATA/ | grep logs)"
echo "[entrypoint] Démarrage de la gateway Hermes..."
exec hermes gateway run
