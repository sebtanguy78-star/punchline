#!/usr/bin/env bash
# Light exports from the 1080p master (validated: 720p CRF 24 ~7 MB / 50 s looks like the master; CRF 26 ~5.4 MB)
# usage: bash export.sh <master.mp4> <out_basename>
set -euo pipefail
M="$1"; B="$2"
enc() { ffmpeg -v error -y -i "$M" -vf "scale=1280:720:flags=lanczos" -c:v libx264 -preset veryslow -crf "$1" \
  -profile:v high -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a aac -b:a 128k -movflags +faststart "$2"; }
enc 24 "${B}_720p.mp4" & enc 26 "${B}_720p_leger.mp4" & wait
for f in "${B}_720p.mp4" "${B}_720p_leger.mp4"; do echo "$f  $(( $(stat -c %s "$f") / 1024 )) KB"; done
