#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------
# tickets.sh — Extrae commits y notifica Teams
# ----------------------------------------

print_usage() {
  cat <<EOF
Usage: $0 <old-hash> <new-hash> <environment> <codeversion_suffix>
Example: $0 v1.2.3 \
             $(git rev-parse HEAD) \
             STG 2025-06-25
EOF
}

validate_args() {
  if [ $# -ne 4 ]; then
    echo "ERROR: Parámetros incorrectos."
    print_usage
    exit 1
  fi
}

validate_env() {
  command -v git >/dev/null || { echo "ERROR: git no instalado."; exit 1; }
  command -v jq  >/dev/null || { echo "ERROR: jq no instalado.";  exit 1; }
  if [ -z "${TEAMS_WEBHOOK_URL:-}" ]; then
    echo "ERROR: debes exportar TEAMS_WEBHOOK_URL con tu webhook de Teams.";
    exit 1
  fi
}

get_commits() {
  git log "${OLD_HASH}..${NEW_HASH}" --no-merges --pretty=format:"%s"
}

extract_and_number() {
  local commits="$1"
  local count=1
  > "$OUTPUT_FILE_TICKETS"
  while IFS= read -r line; do
    # Limpiar mensaje
    local msg
    msg=$(printf "%s" "$line" \
      | sed -E 's/\(#([0-9]+)\)//g; s/\[([^\]]+)\]//g; s/[[:space:]]*$//')

    NUMBERED_LIST+="$count. $msg\n"

    # Extraer tickets (COMP-xxx, P00xxx, Pxxxxxx-xxx)
    grep -Pio '((COMP-|P0)[0-9]{3,}-?[0-9]{3,})' <<<"$msg" \
      | tr '[:lower:]' '[:upper:]' \
      | sed 's/ /-/g' \
      >> "$OUTPUT_FILE_TICKETS"

    ((count++))
  done <<< "$commits"

  sort -u -o "$OUTPUT_FILE_TICKETS" "$OUTPUT_FILE_TICKETS"
}

send_to_teams() {
  local payload
  payload=$(jq -Rs --arg text "**Despliegue en:** ${ENVIRONMENT}\n**Codeversion:** ${CODEVERSION}\n\n${NUMBERED_LIST}" \
    '{ text: $text }')

  local code
  code=$(curl -s -w "%{http_code}" -o /dev/null \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$TEAMS_WEBHOOK_URL")

  if [ "$code" -ne 200 ]; then
    echo "ERROR: fallo al enviar a Teams (HTTP $code)."
    exit 1
  fi

  echo "Mensaje enviado a Teams."
}

# ----------------
# Main
# ----------------

validate_args "$@"
validate_env

OLD_HASH=$1
NEW_HASH=$2
ENVIRONMENT=$3
CODEVERSION="LOEWE_$4"
OUTPUT_FILE_TICKETS="tickets_${OLD_HASH}_to_${NEW_HASH}.txt"
NUMBERED_LIST=""

COMMITS=$(get_commits)
if [ -z "$COMMITS" ]; then
  echo "No hay commits entre $OLD_HASH y $NEW_HASH."
  exit 0
fi

extract_and_number "$COMMITS"
send_to_teams

echo "✔ Tickets extraídos en: $OUTPUT_FILE_TICKETS"