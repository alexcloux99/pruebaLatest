cd tools
cp .env.example .env
Edita .env y pega tu webhook en TEAMS_WEBHOOK_URL
export $(grep -v '^#' .env | xargs)
chmod +x tickets.sh
./tickets.sh <old-hash> <new-hash> <ENTORNO> <CODEVERSION_SUFFIX>