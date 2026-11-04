#!/usr/bin/env bash
# Render every overlay frame (4 Chromium workers in parallel) into <workdir>/ovl/
# usage: bash render_all.sh <workdir>
set -euo pipefail
W="$(cd "$1" && pwd)"
N=$(python3 -c "import json;print(json.load(open('$W/plan.json'))['out_frames'])")
Q=$(( (N + 3) / 4 ))
rm -rf "$W/ovl" && mkdir -p "$W/ovl"
cd "$W/render"
for i in 0 1 2 3; do
  E=$(( (i + 1) * Q < N ? (i + 1) * Q : N ))
  node render.js "$W/ovl" $((i * Q)) $E &
done
wait
echo "overlay frames: $(ls "$W/ovl" | wc -l) / $N"
