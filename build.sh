#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
#  build.sh — Render Build Command
# ─────────────────────────────────────────────────────────────────────
set -o errexit
set -o nounset
set -o pipefail

echo "──────────────────────────────────────────────"
echo "  TIM · Render Build"
echo "──────────────────────────────────────────────"

# ── 1. Python deps ────────────────────────────────────────────────
echo "→ Instalando dependencias Python…"
python -m pip install --upgrade pip
pip install -r requirements.txt

# ── 2. Browser de Playwright + libs de sistema ────────────────────
# --with-deps instala TANTO el binario de Chromium COMO las libs
# que necesita, sin requerir apt-get del sistema (Render bloquea apt).
echo "→ Instalando Chromium + librerías de sistema…"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$PWD/.playwright}"
python -m playwright install --with-deps chromium

echo "──────────────────────────────────────────────"
echo "  ✓ Build completo"
echo "──────────────────────────────────────────────"