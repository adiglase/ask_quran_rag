SQLITE_PATH ?= en-sahih-international-simple.db

.PHONY: lint type test check migrate ingest

lint:
	uv run ruff check .

type:
	uv run mypy .

test:
	uv run pytest

check: lint type test

migrate:
	uv run alembic upgrade head

ingest:
	uv run python -m app.ingest $(SQLITE_PATH)
