#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/../frontend"

echo "🎨 Starting AI Stock Trading System Frontend"
echo "==========================================="

cd "$FRONTEND_DIR"

# Enable corepack for pnpm
echo "📦 Enabling corepack..."
corepack enable || {
  echo "⚠️  corepack not available, trying to install pnpm globally..."
  npm install -g pnpm || {
    echo "❌ Failed to install pnpm. Please install it manually:"
    echo "   npm install -g pnpm"
    exit 1
  }
}

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
  echo "⚠️  .env.local not found, copying from .env.example..."
  if [ -f ".env.example" ]; then
    cp ".env.example" ".env.local"
    echo "✅ Created .env.local from template"
  fi
fi

echo "📦 Installing dependencies..."
pnpm install

echo "🌐 Starting development server..."
echo "Frontend will be available at: http://localhost:5173"
echo "Make sure the backend is running on the configured port"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
pnpm run dev --host
