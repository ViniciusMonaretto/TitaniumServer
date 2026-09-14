#!/usr/bin/env bash
# Ajusta o nível de log do Mosquitto em server/config/mosquitto/config/mosquitto.conf
# (menos verboso que "all").
#
# Uso (a partir da raiz do repositório ou de qualquer diretório):
#   ./scripts/set_mosquitto_log_level.sh
#   MOSQUITTO_LOG_LEVEL=error ./scripts/set_mosquitto_log_level.sh
#
# Níveis válidos (Mosquitto 2): debug, error, warning, notice, information,
#   subscribe, unsubscribe, websockets, all, none
#
# Depois, reinicia o broker, por exemplo:
#   docker compose -f server/docker-compose.yml restart mosquitto

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONF="/opt/titanium-server/config/mosquitto/config/mosquitto.conf"
LEVEL="${MOSQUITTO_LOG_LEVEL:-warning}"

valid_levels='debug error warning notice information subscribe unsubscribe websockets all none'
if ! echo " $valid_levels " | grep -q " ${LEVEL} "; then
  echo "Erro: MOSQUITTO_LOG_LEVEL inválido: ${LEVEL}" >&2
  echo "Use um de: ${valid_levels}" >&2
  exit 1
fi

if [[ ! -f "$CONF" ]]; then
  echo "Erro: ficheiro de configuração não encontrado: ${CONF}" >&2
  exit 1
fi

ts="$(date +%Y%m%d%H%M%S)"
cp -a "$CONF" "${CONF}.bak.${ts}"
echo "Backup: ${CONF}.bak.${ts}"

tmp="$(mktemp)"
grep -v '^log_type[[:space:]]' "$CONF" > "$tmp"
mv "$tmp" "$CONF"

if grep -q '^log_dest[[:space:]]' "$CONF"; then
  sed -i "/^log_dest[[:space:]]/a log_type ${LEVEL}" "$CONF"
else
  printf '\n# Logging (definido por scripts/set_mosquitto_log_level.sh)\nlog_dest stdout\nlog_type %s\nlog_timestamp true\n' "${LEVEL}" >> "$CONF"
  echo "Aviso: não havia log_dest; foram acrescentadas linhas no fim de ${CONF}." >&2
fi

echo "Atualizado ${CONF}: log_type ${LEVEL}"
echo "Reinicia o container Mosquitto para aplicar."
