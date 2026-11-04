#!/usr/bin/env bash
# Stills at chosen OUTPUT times (overlay + zoomed video) -> <workdir>/test/sheet.jpg, to check before the full render
# usage: bash preview.sh <workdir> 2.5,10.4,33.0,46.5
set -euo pipefail
W="$(cd "$1" && pwd)"; SK="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$W/test" && mkdir -p "$W/test"
(cd "$W/render" && node render.js "$W/test" "t=$2")
"$W/venv/bin/python" -I "$SK/compose.py" "$W" test "$2"
