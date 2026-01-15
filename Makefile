.PHONY: run build up down logs

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f
