# Mehak's Kitchen — common developer tasks.
# Usage: make <target>   (run from the repo root)

.PHONY: help install migrate seed run test lint build up down clean

help:
	@echo "Targets:"
	@echo "  install   Install backend + frontend dependencies"
	@echo "  migrate   Apply database migrations (alembic upgrade head)"
	@echo "  seed      Create the initial admin + sample catalogue"
	@echo "  run       Run the backend API (uvicorn, reload)"
	@echo "  test      Run the backend test suite"
	@echo "  lint      Lint the frontend"
	@echo "  build     Build the frontend for production"
	@echo "  up/down   Start/stop the full stack with docker compose"
	@echo "  clean     Wipe transactional/test data (never in production)"

install:
	pip install -r backend/requirements.txt
	cd frontend && npm ci

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python seed.py

run:
	cd backend && uvicorn main:app --reload

test:
	python -m pytest tests/ -q

lint:
	cd frontend && npm run lint

build:
	cd frontend && npm run build

up:
	docker compose up --build

down:
	docker compose down

clean:
	cd backend && python clean_data.py
