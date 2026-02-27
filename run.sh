#!/usr/bin/env bash
# =============================================================================
# AnyDocument AI — Run Script
# Activates the virtual environment and launches the Streamlit application.
# =============================================================================

set -euo pipefail

VENV_DIR="AIvenv"

if [ ! -d "$VENV_DIR" ]; then
    echo "[ERROR] Virtual environment '$VENV_DIR' not found."
    echo "        Please run './setup.sh' first."
    exit 1
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "[INFO]  Starting AnyDocument AI…"
echo "[INFO]  Open http://localhost:8501 in your browser."
echo ""

streamlit run app.py
