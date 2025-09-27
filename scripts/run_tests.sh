#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."

echo "🧪 Running AI Stock Trading System Tests"
echo "======================================="

cd "$ROOT_DIR"

# Test environment setup
echo "==> Setting up test environment"
export OPENAI_API_KEY="test_key_for_testing"
export DATABASE_PATH="data/test.db"
export FLASK_ENV="testing"

echo "==> Python backend tests"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-cov

# Run tests
echo "🧪 Running pytest..."
python -m pytest ../test_*.py -v --tb=short || {
  echo "❌ Python tests failed"
  exit 1
}

echo "✅ Python tests passed"

echo "==> Frontend build test"
cd ../frontend

# Enable corepack
corepack enable || npm install -g pnpm

echo "📦 Installing frontend dependencies..."
pnpm install

echo "🏗️  Testing frontend build..."
pnpm run build || {
  echo "❌ Frontend build failed"
  exit 1
}

echo "✅ Frontend build successful"

echo "==> Linting frontend code"
pnpm run lint || {
  echo "⚠️  Frontend linting issues found"
  # Don't fail on lint issues, just warn
}

echo ""
echo "🎉 All tests completed successfully!"
echo "✅ Backend tests: PASSED"
echo "✅ Frontend build: PASSED"
echo "✅ System is ready for deployment"
