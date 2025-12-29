# DrZaius Backend

FastAPI backend with clean layers (routers → services → repositories), SQLAlchemy, Alembic, and Pydantic schemas. Error handling is standardized with request IDs and consistent payloads.

## Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Optional: Node/Expo (frontend runs separately)

## Environment
Create `.env` or export variables:

```bash
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/drzaius
export INVITE_SIGNING_SECRET=dev-invite-secret-change-me
export EMAIL_FROM=no-reply@example.com
# Pipeline & DLP (stubs OK if disabled)
export ENABLE_PIPELINE=false
export ENABLE_DLP=false
# GCP (only needed if enabling providers later)
export GCP_PROJECT_ID=""
export GCP_LOCATION=us-central1
```

## Setup and Run
```bash
cd /Users/shardool/MonoZaius/DrZaiusBackend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Health:
```bash
curl -i http://localhost:8000/readyz
curl -i http://localhost:8000/healthz
```

## API Quickstart (curl)

### Auth (signup/login)
```bash
# Signup (role and corpus_uri required)
curl -s -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"userA@example.com","email":"userA@example.com","password":"Passw0rd!","full_name":"User A","role":"caregiver","corpus_uri":"user://userA@example.com/corpus"}'

curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"userA@example.com","password":"Passw0rd!"}'
```

### Groups and Members (pagination)
```bash
# Get token and IDs first (see signup/login)
TOKEN_A="<paste access_token>"
TOKEN_B="<paste access_token>"

# Create group
GROUP_ID=$(curl -s -X POST http://localhost:8000/groups \
  -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" \
  -d '{"name":"QA Group","description":"Test group"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["data"]["id"])')

# Add members
USER_A_ID=$(curl -s -H "Authorization: Bearer $TOKEN_A" http://localhost:8000/auth/me | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
USER_B_ID=$(curl -s -H "Authorization: Bearer $TOKEN_B" http://localhost:8000/auth/me | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')

curl -i -X POST "http://localhost:8000/groups/$GROUP_ID/access" \
  -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" \
  -d "{\"userId\":\"$USER_A_ID\",\"role\":\"admin\"}"

curl -i -X POST "http://localhost:8000/groups/$GROUP_ID/access" \
  -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" \
  -d "{\"userId\":\"$USER_B_ID\",\"role\":\"member\"}"

# List with pagination (check X-Total-Count header)
curl -i "http://localhost:8000/groups/$GROUP_ID/access?limit=1&offset=0" -H "Authorization: Bearer $TOKEN_A"
curl -i "http://localhost:8000/groups/$GROUP_ID/access?limit=1&offset=1" -H "Authorization: Bearer $TOKEN_A"
```

### Payment Codes (create/list/void/redeem)
```bash
# Create
CODE=$(curl -s -X POST "http://localhost:8000/groups/$GROUP_ID/payments/codes" \
  -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" \
  -d '{"ttl_minutes":30}' | python3 -c 'import sys,json; print(json.load(sys.stdin).get("code",""))')
echo "CODE=$CODE"

# List
curl -s "http://localhost:8000/groups/$GROUP_ID/payments/codes" -H "Authorization: Bearer $TOKEN_A"

# Void
curl -i -X POST "http://localhost:8000/groups/$GROUP_ID/payments/codes/$CODE/void" -H "Authorization: Bearer $TOKEN_A"

# Redeem (B)
curl -i -X POST "http://localhost:8000/payments/redeem" \
  -H "Authorization: Bearer $TOKEN_B" -H "Content-Type: application/json" \
  -d "{\"code\":\"$CODE\"}"
```

### Redaction (stub)
```bash
curl -i -X POST "http://localhost:8000/redaction/test" \
  -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" \
  -d '{"text":"SSN 123-45-6789 and john@example.com"}'
```

## Error Handling
- Request ID: every response includes `X-Request-Id`; global exception handler logs with it.
- Validation errors: 400 with `{"message":"invalid_payload","details":[...]}`.
- Domain errors: routers map service `ValueError(Errors.*)` to proper HTTP codes.
- Upload validation (size/MIME) returns 413/415 accordingly.

## Design
- Separation of Concerns: routers (I/O), services (business logic), repositories (data access).
- Dependency Injection: services accept repositories; routers provide via small providers.
- Constants: `backend/core/constants.py` centralizes routes, messages, errors, roles, headers.
- Pydantic response models enforce consistent shapes.

# DrZaius Backend

## Development
Run with:

```bash
uvicorn backend.app:app --reload
```

### Configuration
- Create a `.env` file (see example values below):

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/drzaius
AUTO_CREATE_DB=false
```

### Database
- Install dependencies:
```
pip install -r requirements.txt
```
- To bootstrap tables for local dev without migrations, set `AUTO_CREATE_DB=true` in `.env` and start the app once.
- Recommended: use Alembic for migrations (`alembic init` then generate revisions).