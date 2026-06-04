FROM nousresearch/hermes-agent:latest

# Config Hermes sans secrets (les secrets viennent des env vars Railway)
COPY config.yaml /opt/hermes-default/config.yaml

# Entrypoint : initialise /opt/data si vierge, puis démarre la gateway
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
