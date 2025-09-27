#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔍 AI Stock Trading System - Environment Verification"
echo "=================================================="

echo "==> Checking .env in project root"
if [ ! -f "$ROOT_DIR/.env" ]; then
  echo "❌ .env not found. Copying from .env.example"
  if [ -f "$ROOT_DIR/.env.example" ]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    echo "✅ Created .env from template"
    echo "⚠️  Please fill in the placeholders in .env"
  else
    echo "❌ .env.example not found either!"
    exit 1
  fi
fi

REQ_KEYS=(OPENAI_API_KEY)
MISSING=0
for k in "${REQ_KEYS[@]}"; do
  if ! grep -qE "^${k}=" "$ROOT_DIR/.env" || grep -qE "^${k}=.*your_.*_here" "$ROOT_DIR/.env"; then
    echo "❌ Missing or placeholder value for: $k in .env"
    MISSING=1
  else
    echo "✅ Found: $k"
  fi
done

echo "==> Checking frontend .env"
if [ ! -f "$ROOT_DIR/frontend/.env.local" ]; then
  echo "❌ frontend/.env.local not found. Copying from frontend/.env.example"
  if [ -f "$ROOT_DIR/frontend/.env.example" ]; then
    cp "$ROOT_DIR/frontend/.env.example" "$ROOT_DIR/frontend/.env.local"
    echo "✅ Created frontend/.env.local from template"
  else
    echo "⚠️  frontend/.env.example not found"
  fi
fi

echo "==> Checking backend requirements"
if [ ! -f "$ROOT_DIR/backend/requirements.txt" ]; then
  echo "❌ backend/requirements.txt missing"
  MISSING=1
else
  echo "✅ Found backend/requirements.txt"
fi

echo "==> Checking Python version"
if command -v python3 >/dev/null 2>&1; then
  PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
  echo "✅ Python version: $PYTHON_VERSION"
else
  echo "❌ Python3 not found"
  MISSING=1
fi

echo "==> Checking Node.js version"
if command -v node >/dev/null 2>&1; then
  NODE_VERSION=$(node --version)
  echo "✅ Node.js version: $NODE_VERSION"
else
  echo "❌ Node.js not found"
  MISSING=1
fi

echo "==> Checking pnpm"
if command -v pnpm >/dev/null 2>&1; then
  PNPM_VERSION=$(pnpm --version)
  echo "✅ pnpm version: $PNPM_VERSION"
else
  echo "⚠️  pnpm not found, will try to enable corepack"
fi

if [ "$MISSING" -eq 1 ]; then
  echo ""
  echo "⛔ Environment check failed."
  echo "Please fix the issues above before proceeding."
  exit 1
fi

echo ""
echo "✅ Environment verification completed successfully!"
echo "You can now run the backend and frontend servers."
