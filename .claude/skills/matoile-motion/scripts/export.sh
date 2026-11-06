#!/usr/bin/env bash
# Deliverables from the 1080p master.
#  - <base>_720p_HQ.mp4   : 720p, best quality that fits in ~14.5 MB (two-pass)  <- what the user asks for now
#  - <base>_720p.mp4      : 720p CRF 24 (~7-11 MB, depends on grain: night footage is heavier)
#  - <base>_720p_leger.mp4: 720p CRF 26 (lightest)
# usage: bash export.sh <master.mp4> <out_basename> [target_MB=14.5]
set -euo pipefail
M="$1"; B="$2"; MB="${3:-14.5}"
COLOR="-profile:v high -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv"
SCALE="scale=1280:720:flags=lanczos"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$M")
VK=$(python3 -c "print(int($MB*1e6*8/$DUR/1000) - 165)")   # video kbit/s = budget - audio 160k - container margin
crf() { ffmpeg -v error -y -i "$M" -vf "$SCALE" -c:v libx264 -preset veryslow -crf "$1" $COLOR \
  -c:a aac -b:a 128k -movflags +faststart "$2"; }
hq() {
  local L; L=$(mktemp -u "${B}_plXXXX")
  ffmpeg -v error -y -i "$M" -vf "$SCALE" -c:v libx264 -preset veryslow $COLOR -b:v ${VK}k -maxrate 4500k -bufsize 9000k \
    -pass 1 -passlogfile "$L" -an -f mp4 /dev/null
  ffmpeg -v error -y -i "$M" -vf "$SCALE" -c:v libx264 -preset veryslow $COLOR -b:v ${VK}k -maxrate 4500k -bufsize 9000k \
    -pass 2 -passlogfile "$L" -af volume=-0.3dB -c:a aac -b:a 160k -movflags +faststart "${B}_720p_HQ.mp4"
  rm -f "$L"*
}
hq & crf 24 "${B}_720p.mp4" & crf 26 "${B}_720p_leger.mp4" & wait
for f in "${B}_720p_HQ.mp4" "${B}_720p.mp4" "${B}_720p_leger.mp4"; do echo "$f  $(( $(wc -c < "$f") / 1024 )) KB"; done   # wc: works on macOS and Linux
