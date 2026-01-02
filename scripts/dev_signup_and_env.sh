#!/usr/bin/env bash
# Usage:
#   source scripts/dev_signup_and_env.sh
# Optional overrides (set before sourcing):
#   BASE=http://localhost:8000 USERNAME=myuser EMAIL=me@example.com PASSWORD=Pass123! \
#   ENABLE_DLP=true GCP_PROJECT_ID=dr-zaius-007 DLP_LOCATION=us \
#   source scripts/dev_signup_and_env.sh
#
# Sets in current shell:
#   BASE, ENABLE_DLP, GCP_PROJECT_ID, DLP_LOCATION, TOKEN

set -euo pipefail

# Defaults (override via environment before sourcing)
BASE="${BASE:-http://localhost:8000}"
USERNAME="${USERNAME:-devuser}"
EMAIL="${EMAIL:-dev@example.com}"
PASSWORD="${PASSWORD:-Devpass123!}"
ROLE="${ROLE:-caregiver}"
CORPUS_URI="${CORPUS_URI:-local://corpus}"

# DLP/env defaults
export ENABLE_DLP="${ENABLE_DLP:-true}"
export GCP_PROJECT_ID="${GCP_PROJECT_ID:-dr-zaius-007}"
export DLP_LOCATION="${DLP_LOCATION:-us}"

echo "[dev] BASE=$BASE"
echo "[dev] ENABLE_DLP=$ENABLE_DLP GCP_PROJECT_ID=$GCP_PROJECT_ID DLP_LOCATION=$DLP_LOCATION"

tmpresp="$(mktemp)"
cleanup() { rm -f "$tmpresp" >/dev/null 2>&1 || true; }
trap cleanup EXIT

# Try signup first
signup_payload=$(cat <<JSON
{"username":"$USERNAME","email":"$EMAIL","password":"$PASSWORD","role":"$ROLE","corpus_uri":"$CORPUS_URI"}
JSON
)

echo "[dev] Attempting signup for user '$USERNAME' ..."
http_code="$(curl -sS -o "$tmpresp" -w "%{http_code}" \
  -H "Content-Type: application/json" \
  -d "$signup_payload" \
  "$BASE/auth/signup" || true)"

if [[ "$http_code" =~ ^2 ]]; then
  echo "[dev] Signup succeeded."
else
  echo "[dev] Signup returned HTTP $http_code; attempting login ..."
  login_payload=$(cat <<JSON
{"username":"$USERNAME","password":"$PASSWORD"}
JSON
)
  http_code="$(curl -sS -o "$tmpresp" -w "%{http_code}" \
    -H "Content-Type: application/json" \
    -d "$login_payload" \
    "$BASE/auth/login" || true)"
  if ! [[ "$http_code" =~ ^2 ]]; then
    echo "[dev] Login failed (HTTP $http_code). Response:"
    cat "$tmpresp"
    return 1 2>/dev/null || exit 1
  fi
  echo "[dev] Login succeeded."
fi

# Extract token without jq (use python)
if ! command -v python3 >/dev/null 2>&1; then
  echo "[dev] python3 is required to parse the token." >&2
  return 1 2>/dev/null || exit 1
fi

TOKEN="$(python3 - "$tmpresp" <<'PY'
import json, sys
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
token = data.get('access_token') or ''
if not token:
    print("ERROR: access_token not found in response JSON", file=sys.stderr)
    sys.exit(1)
print(token)
PY
)"

export BASE
export TOKEN
echo "[dev] TOKEN exported to current shell."
echo "[dev] Next steps:"
echo "  curl -H \"Authorization: Bearer \$TOKEN\" \"\$BASE/redaction/status\""


