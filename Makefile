.PHONY: install format lint test clean run migrate

include .env
export

install:
	poetry install --no-root

format:
	poetry run black . --exclude "(migrations/|alembic/|\.poetry/)"
	poetry run isort . --skip migrations --skip alembic --skip .poetry

lint: lint-black lint-isort lint-flake8 lint-mypy

lint-black:
	poetry run black --check . --exclude "(migrations/|alembic/)"

lint-isort:
	poetry run isort --check-only . --skip migrations --skip alembic

lint-flake8:
	poetry run flake8 . --exclude migrations,alembic

lint-mypy:
	poetry run mypy . --exclude migrations --exclude alembic

test:
	poetry run pytest tests -s -vvv --cov=src

run:
	poetry run uvicorn src.main:app --reload --host $(HOST) --port $(PORT) --workers $(WORKER_COUNT)

migrate:
	poetry run alembic upgrade head

migrations:
	poetry run alembic revision --autogenerate -m "$(message)"

# Docker commands
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down -v

docker-logs:
	docker compose logs -f

docker-prune:
	docker system prune -af

docker-prod-build:
	docker compose -f compose.prod.yaml build

docker-prod-up:
	docker compose -f compose.prod.yaml up -d

docker-prod-down:
	docker compose -f compose.prod.yaml down -v

docker-prod-clean:
	docker compose -f compose.prod.yaml down -v
	docker container prune -f
	docker network prune -f
# Scale API service with specified number of replicas
docker-prod-scale:
	docker compose -f compose.prod.yaml up -d --scale api=$(scale)

# Show running containers with their ports
docker-prod-status:
	@echo "API Containers and Ports:"
	@docker ps --format "table {{.Names}}\t{{.Ports}}" | grep api


# Full rebuild and restart with scaling
docker-prod-rebuild: docker-prod-clean docker-prod-build
	docker compose -f compose.prod.yaml up -d --scale api=3

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +