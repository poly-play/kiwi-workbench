#!/bin/bash

# ==========================================
# Kiwi Workbench - One-Click Setup Script
# ==========================================

# Ensure we are in the project root
cd "$(dirname "$0")/.." || exit

echo "🥝 Initializing Kiwi Workbench Environment..."

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please download it from: https://www.python.org/downloads/macos/"
    exit 1
fi
echo "✅ Python 3 found."

# 2. Check/Install uv
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (The ultra-fast package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to path for current session if needed
    source "$HOME/.cargo/env" 2>/dev/null || true
else
    echo "✅ uv already installed."
fi

# 3. Setup Environment Variables
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file to add your API Keys!"
else
    echo "✅ .env exists."
fi

# 4. Sync Dependencies
echo "🚀 Syncing dependencies (this might take a moment)..."
uv sync --project engine

echo ""
echo "🎉 Kiwi Workbench is READY!"
echo "Try running: uv run --project engine engine/scripts/system/generic_reporter.py --help"
