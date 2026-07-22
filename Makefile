# AEGIS LENS - Development Makefile
# Production-grade development automation

.PHONY: help install test lint format clean build docker-build docker-up docker-down db-setup db-migrate

# Default target
help:
	@echo "AEGIS LENS - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install           Install all dependencies"
	@echo "  make install-dev       Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run all tests"
	@echo "  make test-db           Run database tests"
	@echo "  make test-chronos     Run CHRONOS tests"
	@echo "  make test-cov          Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint              Run linters"
	@echo "  make format            Format code"
	@echo "  make format-check      Check code formatting"
	@echo ""
	@echo "Database:"
	@echo "  make db-setup          Setup all databases"
	@echo "  make db-migrate         Run database migrations"
	@echo "  make db-reset          Reset databases"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      Build Docker images"
	@echo "  make docker-up         Start Docker services"
	@echo "  make docker-down       Stop Docker services"
	@echo "  make docker-logs       View Docker logs"
	@echo ""
	@echo "Build:"
	@echo "  make build             Build all packages"
	@echo "  make build-chronos     Build CHRONOS WASM"
	@echo ""
	@echo "Clean:"
	@echo "  make clean             Clean build artifacts"
	@echo "  make clean-all         Clean everything including dependencies"

# Installation
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing CHRONOS JS dependencies..."
	cd packages/chronos/js && npm install
	@echo "Installation complete!"

install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-mock black flake8 mypy isort
	cd packages/chronos/js && npm install
	@echo "Development installation complete!"

# Testing
test:
	@echo "Running all tests..."
	cd packages/database && python -m pytest tests/ -v
	cd packages/chronos && cargo test
	cd packages/chronos/js && npm test

test-db:
	@echo "Running database tests..."
	cd packages/database && python -m pytest tests/ -v

test-chronos:
	@echo "Running CHRONOS tests..."
	cd packages/chronos && cargo test
	cd packages/chronos/js && npm test

test-cov:
	@echo "Running tests with coverage..."
	cd packages/database && python -m pytest tests/ --cov=. --cov-report=html
	cd packages/chronos/js && npm test -- --coverage

# Code Quality
lint:
	@echo "Running linters..."
	@echo "Python..."
	flake8 packages/database --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 packages/database --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "Rust..."
	cd packages/chronos && cargo clippy
	@echo "JavaScript..."
	cd packages/chronos/js && npm run lint

format:
	@echo "Formatting code..."
	@echo "Python..."
	black packages/database
	isort packages/database
	@echo "Rust..."
	cd packages/chronos && cargo fmt
	@echo "JavaScript..."
	cd packages/chronos/js && npm run format

format-check:
	@echo "Checking code formatting..."
	@echo "Python..."
	black --check packages/database
	isort --check-only packages/database
	@echo "Rust..."
	cd packages/chronos && cargo fmt -- --check
	@echo "JavaScript..."
	cd packages/chronos/js && npm run format:check

# Database
db-setup:
	@echo "Setting up databases..."
	@echo "PostgreSQL..."
	cd packages/database && python setup_postgres.py
	@echo "TimescaleDB..."
	cd packages/database && python setup_timescale.py
	@echo "Neo4j..."
	cd packages/database && python setup_neo4j.py
	@echo "Database setup complete!"

db-migrate:
	@echo "Running database migrations..."
	cd packages/database && alembic upgrade head
	cd packages/database/alembic_timescale && alembic upgrade head
	@echo "Migrations complete!"

db-reset:
	@echo "Resetting databases..."
	docker-compose down -v
	docker-compose up -d postgres timescaledb neo4j redis
	@echo "Waiting for databases to be ready..."
	sleep 10
	@echo "Running setup scripts..."
	cd packages/database && python setup_postgres.py
	cd packages/database && python setup_timescale.py
	cd packages/database && python setup_neo4j.py
	@echo "Database reset complete!"

# Docker
docker-build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "Docker build complete!"

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Docker services started!"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down
	@echo "Docker services stopped!"

docker-logs:
	@echo "Viewing Docker logs..."
	docker-compose logs -f

# Build
build:
	@echo "Building all packages..."
	@echo "CHRONOS WASM..."
	cd packages/chronos && wasm-pack build --target web --out-dir pkg --release
	@echo "Build complete!"

build-chronos:
	@echo "Building CHRONOS WASM..."
	cd packages/chronos && wasm-pack build --target web --out-dir pkg --release
	@echo "CHRONOS build complete!"

# Clean
clean:
	@echo "Cleaning build artifacts..."
	cd packages/chronos && cargo clean
	cd packages/chronos && rm -rf pkg/
	cd packages/database && find . -type d -name __pycache__ -exec rm -rf {} +
	cd packages/database && find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"

clean-all:
	@echo "Cleaning everything..."
	cd packages/chronos && cargo clean
	cd packages/chronos && rm -rf pkg/
	cd packages/chronos/js && rm -rf node_modules/
	cd packages/database && find . -type d -name __pycache__ -exec rm -rf {} +
	cd packages/database && find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf coverage
	@echo "Deep clean complete!"
