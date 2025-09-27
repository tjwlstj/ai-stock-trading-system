#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../backend"
ROOT_DIR="$SCRIPT_DIR/.."

echo "🚀 Starting AI Stock Trading System Backend"
echo "=========================================="

cd "$BACKEND_DIR"

# Check if .env exists in root
if [ ! -f "$ROOT_DIR/.env" ]; then
  echo "❌ .env file not found in project root"
  echo "Please run ./scripts/verify_env.sh first"
  exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv .venv
fi

echo "📦 Activating virtual environment..."
source .venv/bin/activate

echo "📦 Installing/updating dependencies..."
pip install -U pip
pip install -r requirements.txt

# Set Python path to include backend directory
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"

# Load environment variables from root .env
echo "🔧 Loading environment variables..."
set -a
source "$ROOT_DIR/.env"
set +a

# Create data directory if it doesn't exist
mkdir -p data logs

echo "🌐 Starting FastAPI server with Uvicorn..."
echo "Backend will be available at: http://localhost:${BACKEND_PORT:-8000}"
echo "API Documentation: http://localhost:${BACKEND_PORT:-8000}/docs"
echo "Health check: http://localhost:${BACKEND_PORT:-8000}/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server with Uvicorn
python main.py
