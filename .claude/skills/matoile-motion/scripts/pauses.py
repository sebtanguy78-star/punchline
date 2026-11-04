"""Suggest the pauses to cut (REMOVE list for config.py).
Rule that gave the validated rhythm: silences >= 0.4 s at -35 dB; keep ~0.08 s of tail after the voice and
~0.06 s before the next word; ignore the leading silence and the trailing one (it carries the goodbye / end card).
usage: python pauses.py <video>"""
import re, subprocess, sys


def silences(noise, d):
    p = subprocess.run(["ffmpeg", "-i", sys.argv[1], "-vn", "-ac", "1", "-ar", "16000", "-af",
                        f"silencedetect=noise={noise}dB:d={d}", "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", p.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", p.stderr)]
    return list(zip(st, en))


dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", sys.argv[1]],
                           capture_output=True, text=True).stdout)
s35, s40 = silences(-35, 0.4), silences(-40, 0.22)
out = []
for a, b in s35:
    if a < 0.2 or b > dur - 0.3:
        continue
    start = a + 0.08
    for c, d in s40:          # if the -40 dB silence starts later, the voice tail is longer: respect it
        if c < b and d > a:
            start = max(start, c + 0.03)
    end = b - 0.06
    if end - start >= 0.15:
        out.append((round(start, 2), round(end, 2)))
print("REMOVE = [" + ", ".join(f"({a:.2f}, {b:.2f})" for a, b in out) + "]")
print(f"# {len(out)} cuts, {sum(b - a for a, b in out):.2f} s removed")
