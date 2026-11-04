#!/usr/bin/env bash
# Prepare a work folder: Python venv (Whisper, Pillow, numpy) + fonts/icons for the overlay + Playwright.
# usage: bash setup.sh <workdir>
set -euo pipefail
W="$1"; mkdir -p "$W/render" "$W/test" "$W/ovl"
command -v ffmpeg >/dev/null || { echo "ffmpeg manquant (apt-get install -y ffmpeg)"; exit 1; }
[ -x "$W/venv/bin/python" ] || python3 -m venv "$W/venv"
"$W/venv/bin/pip" install -q faster-whisper pillow numpy
cd "$W/render"
[ -f package.json ] || npm init -y >/dev/null
npm i --silent @fontsource/inter lucide-static
if ! node -e "require('playwright')" 2>/dev/null; then
  npm i --silent playwright && npx playwright install chromium
fi
echo "setup OK -> $W"
