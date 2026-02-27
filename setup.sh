#!/usr/bin/env bash
# =============================================================================
# AnyDocument AI — Setup Script
# Installs system dependencies, Python packages, Ollama, and starter models.
# =============================================================================

set -euo pipefail

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()    { echo -e "${GREEN}[INFO]${NC}  $*"; }
warning() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ── 1. System packages ────────────────────────────────────────────────────────
info "Updating package list and installing system dependencies…"
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-venv curl

# ── 2. Virtual environment ────────────────────────────────────────────────────
VENV_DIR="AIvenv"
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment in './$VENV_DIR'…"
    python3 -m venv "$VENV_DIR"
else
    info "Virtual environment '$VENV_DIR' already exists — skipping creation."
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# ── 3. Python dependencies ────────────────────────────────────────────────────
info "Installing Python dependencies from requirements.txt…"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

deactivate

# ── 4. Ollama ─────────────────────────────────────────────────────────────────
if command -v ollama &>/dev/null; then
    info "Ollama is already installed — skipping installation."
else
    if [ "$(uname)" = "Linux" ]; then
        info "Installing Ollama…"
        curl -fsSL https://ollama.com/install.sh | sh
    else
        warning "Automatic Ollama installation is only supported on Linux."
        warning "Please install Ollama manually from https://ollama.com/download"
    fi
fi

# ── 5. Starter models ─────────────────────────────────────────────────────────
info "Pulling starter models (this may take a while on first run)…"
ollama pull qwen:0.5b  || warning "Could not pull qwen:0.5b — skipping."
ollama pull phi3:mini  || warning "Could not pull phi3:mini — skipping."

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
info "Setup complete! Run the application with:  ./run.sh"
