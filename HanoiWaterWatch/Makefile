.PHONY: help dev test build seed gen
help:
	@echo "dev: Docker Compose; test: backend and frontend; build: frontend production bundle"
dev:
	docker compose up --build
build:
	cd frontend && npm ci && npm run build
test:
	cd backend && python -m pytest -q
	cd frontend && npm test -- --run
seed:
	cd backend && python -m app.cli seed
gen:
	python tools/gen_registry.py

