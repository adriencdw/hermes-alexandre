FROM nousresearch/hermes-agent:latest

# Config et skills Hermes (les secrets viennent des env vars Railway)
COPY config.yaml /opt/hermes-default/config.yaml
COPY skills/ /opt/hermes-default/skills/
COPY hermes-init/ /opt/hermes-default/init/

# Entrypoint : initialise /opt/data si vierge, puis démarre la gateway
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER root
ENTRYPOINT ["/entrypoint.sh"]
