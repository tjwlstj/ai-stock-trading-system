.PHONY: help install start stop test clean build docker-build docker-up docker-down

# Default target
help:
	@echo "AI Stock Trading System - Available Commands:"
	@echo ""
	@echo "  make install     - Install all dependencies"
	@echo "  make start       - Start backend and frontend servers"
	@echo "  make stop        - Stop all running servers"
	@echo "  make test        - Run all tests"
	@echo "  make clean       - Clean build artifacts and cache"
	@echo "  make build       - Build frontend for production"
	@echo ""
	@echo "  Docker Commands:"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up   - Start services with Docker Compose"
	@echo "  make docker-down - Stop Docker services"
	@echo ""
	@echo "  Environment:"
	@echo "  make env-check   - Verify environment setup"

# Environment setup
env-check:
	@echo "🔍 Checking environment..."
	@./scripts/verify_env.sh

install: env-check
	@echo "📦 Installing dependencies..."
	@cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
	@cd frontend && pnpm install

# Development servers
start:
	@echo "🚀 Starting development servers..."
	@./scripts/run_backend.sh &
	@./scripts/run_frontend.sh &
	@echo "✅ Servers started. Backend: http://localhost:8000, Frontend: http://localhost:5173"

stop:
	@echo "🛑 Stopping servers..."
	@pkill -f "uvicorn" || true
	@pkill -f "vite" || true
	@echo "✅ Servers stopped"

# Testing
test:
	@echo "🧪 Running tests..."
	@./scripts/run_tests.sh

# Build
build:
	@echo "🏗️ Building frontend..."
	@cd frontend && pnpm run build

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf backend/.venv
	@rm -rf frontend/node_modules
	@rm -rf frontend/dist
	@rm -rf backend/__pycache__
	@rm -rf backend/app/__pycache__
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Docker commands
docker-build:
	@echo "🐳 Building Docker images..."
	@docker-compose build

docker-up:
	@echo "🐳 Starting Docker services..."
	@docker-compose up -d
	@echo "✅ Services started. Backend: http://localhost:8000, Frontend: http://localhost:3000"

docker-down:
	@echo "🐳 Stopping Docker services..."
	@docker-compose down

# Development helpers
backend:
	@./scripts/run_backend.sh

frontend:
	@./scripts/run_frontend.sh

logs:
	@echo "📋 Showing recent logs..."
	@tail -f logs/app.log 2>/dev/null || echo "No log file found. Start the backend first."

# Quick setup for new developers
setup: env-check install
	@echo "🎉 Setup complete! Run 'make start' to begin development."
