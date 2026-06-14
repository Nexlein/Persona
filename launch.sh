#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 1. Ensure .env exists ---
if [ ! -f .env ]; then
  echo "No .env file found. Copying env.example → .env"
  cp env.example .env
  echo ""
  echo "  Please fill in your secrets in .env then re-run ./launch.sh"
  echo ""
  exit 1
fi

# ── 2. Guard against unconfigured placeholders ---
if grep -q "CHANGE_ME" .env; then
  echo ""
  echo "  Your .env still contains CHANGE_ME placeholders."
  echo "  Please fill in all values before launching."
  echo ""
  exit 1
fi

# ── 3. Generate credentials.json from .env ---
./update_credentials.py

# ── 4. Start the container ---
docker compose up --build -d

# ── 5. Wait until n8n is fully ready ---
echo "Waiting for n8n to be ready..."
until docker compose exec n8n wget -qO- http://localhost:5678/healthz >/dev/null 2>&1; do
  sleep 2
done
echo "n8n is ready."

# ── 6. Import credentials and workflows ---
docker compose exec n8n n8n import:credentials --input=/backup/credentials.json
docker compose exec n8n n8n import:workflow --separate --input=/backup/

echo ""
echo "  All done! Open http://localhost:5678 to use your n8n instance."
echo ""
