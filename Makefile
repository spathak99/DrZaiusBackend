PY?=python3
APP=backend.app:app
HOST?=0.0.0.0
PORT?=8000

.PHONY: run run-prod migrate makemigration lint

run:
	uvicorn $(APP) --reload --host $(HOST) --port $(PORT)

run-prod:
	uvicorn $(APP) --host $(HOST) --port $(PORT)

migrate:
	alembic upgrade head

makemigration:
	@echo "Usage: make makemigration MSG='describe change'"
	alembic revision -m "$(MSG)"

lint:
	@echo "Running basic lint (ruff if available, otherwise skip)"
	@command -v ruff >/dev/null 2>&1 && ruff check || echo "ruff not installed"


