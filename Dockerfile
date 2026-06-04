FROM nousresearch/hermes-agent:latest

# Config et skills Hermes (les secrets viennent des env vars Railway)
COPY config.yaml /opt/hermes-default/config.yaml
COPY skills/ /opt/hermes-default/skills/

# Entrypoint : initialise /opt/data si vierge, puis démarre la gateway
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
