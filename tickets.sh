#!/bin/bash
 
# Validate parameters
if [ $# -ne 4 ]; then
  echo "Usage: $0 <old-hash> <new-hash> <environment> <codeversion_suffix>"
  exit 1
fi
 
# Parameters
OLD_HASH=$1
NEW_HASH=$2
ENVIRONMENT=$3
CODEVERSION="LOEWE_$4"
 
# Output file for tickets
OUTPUT_FILE_TICKETS="tickets_${OLD_HASH}_to_${NEW_HASH}.txt"
 
# Teams Webhook URL
TEAMS_WEBHOOK_URL=""
 
# Clear previous ticket file
> "$OUTPUT_FILE_TICKETS"
 
# Retrieve commit messages between the given hashes
COMMIT_MESSAGES=$(git log "$OLD_HASH".."$NEW_HASH" --no-merges --pretty=format:"%s")
 
# Verify if there are commits
if [ -z "$COMMIT_MESSAGES" ]; then
  echo "No commits found between $OLD_HASH and $NEW_HASH."
  exit 1
fi
 
# Process commits and format the output
NUMBERED_LIST=""
COUNT=1
while IFS= read -r line; do
  # Clean the commit message
  CLEANED_LINE=$(echo "$line" | sed -E 's/\(#([0-9]+)\)//g' | sed -E 's/\[([^\]]+)\]//g' | sed 's/[[:space:]]*$//')
 
  # Add a list commit
  NUMBERED_LIST+="$COUNT. $CLEANED_LINE\n"
 
  # Extract tickets
  while [[ $CLEANED_LINE =~ ([Cc][Oo][Mm][Pp][- ]?[0-9]{3,})|([Pp]00[- ]?[0-9]{3,})|([Pp][0-9]{6}[- ]?[0-9]{3,}) ]]; do
    TICKET=$(echo "${BASH_REMATCH[0]// /-}" | tr '[:lower:]' '[:upper:]')
    echo "$TICKET" >> "$OUTPUT_FILE_TICKETS"
    CLEANED_LINE=${CLEANED_LINE#*"${BASH_REMATCH[0]}"}
  done
 
  ((COUNT++))
done <<< "$COMMIT_MESSAGES"
 
# Remove duplicate tickets from the file
sort -u -o "$OUTPUT_FILE_TICKETS" "$OUTPUT_FILE_TICKETS"
 
# Message to Teams
MESSAGE="**Despliegue realizado en entorno: ${ENVIRONMENT}**\n\n**Codeversion:** ${CODEVERSION}\n\n${NUMBERED_LIST}"
 
# Send the formatted message to Teams
curl -H "Content-Type: application/json" -d "{\"text\": \"${MESSAGE}\"}" "$TEAMS_WEBHOOK_URL"
 
# Confirmations
echo "Commit messages sent to Teams."
echo "Tickets extracted and saved to: $OUTPUT_FILE_TICKETS"