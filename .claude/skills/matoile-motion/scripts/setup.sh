#!/usr/bin/env bash
# Prepare a work folder: Python venv (Whisper, Pillow, numpy) + fonts/icons for the overlay + Playwright/Chromium.
# Works on macOS (Homebrew) and Linux. First run downloads ~200 MB (Chromium); the first transcription downloads
# the Whisper "medium" model (~1.5 GB, cached in ~/.cache/huggingface).
# usage: bash setup.sh <workdir>
set -euo pipefail
W="$1"; mkdir -p "$W/render" "$W/test" "$W/ovl"
if [ "$(uname)" = "Darwin" ]; then HINT="brew install"; else HINT="sudo apt-get install -y"; fi
miss=""
command -v ffmpeg  >/dev/null || miss="$miss ffmpeg"
command -v ffprobe >/dev/null || miss="$miss ffmpeg"
command -v node    >/dev/null || miss="$miss node"
command -v npm     >/dev/null || miss="$miss node"
command -v python3 >/dev/null || miss="$miss python"
if [ -n "$miss" ]; then
  echo "Il manque :$miss  ->  installe-les avec :  $HINT$(echo "$miss" | tr ' ' '\n' | sort -u | tr '\n' ' ')"
  [ "$(uname)" = "Darwin" ] && echo "(Homebrew : https://brew.sh)"
  exit 1
fi
[ -x "$W/venv/bin/python" ] || python3 -m venv "$W/venv"
"$W/venv/bin/python" -m pip install -q --upgrade pip
"$W/venv/bin/python" -m pip install -q faster-whisper pillow numpy
cd "$W/render"
[ -f package.json ] || npm init -y >/dev/null
npm i --silent @fontsource/inter lucide-static
# Playwright: reuse one that is already importable (cloud images ship it), otherwise install it + Chromium locally
if ! node -e "require('playwright')" 2>/dev/null; then
  npm i --silent playwright && npx playwright install chromium
fi
echo "setup OK -> $W"
