#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
#  build.sh — Render Build Command
# ─────────────────────────────────────────────────────────────────────
#  Se ejecuta UNA vez durante el deploy, antes de arrancar la app.
#  Aquí instalamos:
#    1. Dependencias Python  (requirements.txt)
#    2. Browser de Playwright (Chromium)  ← OMPI lo necesita
#    3. Librerías de sistema que Chromium requiere (apt)
# ─────────────────────────────────────────────────────────────────────

set -o errexit   # Aborta si falla cualquier comando
set -o nounset   # Aborta si se usa variable sin definir
set -o pipefail  # Captura fallos en pipes

echo "──────────────────────────────────────────────"
echo "  TIM · Render Build"
echo "──────────────────────────────────────────────"

# ── 1. Python deps ────────────────────────────────────────────────
echo "→ Instalando dependencias Python…"
python -m pip install --upgrade pip
pip install -r requirements.txt

# ── 2. Browser de Playwright ──────────────────────────────────────
# El env var PLAYWRIGHT_BROWSERS_PATH ya lo fija ORCH_ONE.py
# apuntando a ./.playwright dentro del proyecto, así persiste.
echo "→ Instalando Chromium para Playwright…"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$PWD/.playwright}"
python -m playwright install chromium

# ── 3. Librerías de sistema para Chromium ─────────────────────────
# Render permite apt-get durante el build (corremos como root).
# Lista alineada con las dependencias oficiales de Playwright.
echo "→ Instalando librerías de sistema para Chromium…"
apt-get update -qq
apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    fonts-liberation \
    libappindicator3-1 \
    libgtk-3-0 \
    || echo "⚠  apt-get falló, intentando playwright install-deps como respaldo…"

# Respaldo oficial (también funciona como root)
python -m playwright install-deps chromium || true

echo "──────────────────────────────────────────────"
echo "  ✓ Build completo"
echo "──────────────────────────────────────────────"
