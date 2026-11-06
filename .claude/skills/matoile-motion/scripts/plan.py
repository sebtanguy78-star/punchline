"""Build the edit plan from a per-video config: cuts, zooms, cleaned words, caption chunks, overlay events.
Every time in the config is in SOURCE seconds; this script maps it to OUTPUT seconds (after the cuts).

usage: python plan.py <config.py> <transcript.json> <workdir>
writes <workdir>/plan.json and <workdir>/plan.js (window.PLAN=...)"""
import json, runpy, subprocess, sys
from fractions import Fraction

cfg = runpy.run_path(sys.argv[1])
tr = json.load(open(sys.argv[2], encoding="utf-8"))
work = sys.argv[3]

SRC = cfg["SRC"]
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                                "stream=width,height,r_frame_rate,nb_read_packets", "-of", "json", SRC],
                               capture_output=True, check=True, text=True).stdout)["streams"][0]
FPS = round(float(Fraction(pr["r_frame_rate"])))
SRC_FRAMES = int(pr["nb_read_packets"])
SRC_W, SRC_H = pr["width"], pr["height"]
HOLD = cfg.get("HOLD", 3.0)            # freeze-frame seconds added for the end card
REMOVE = cfg["REMOVE"]                 # pauses to cut, from pauses.py
FOCUS = cfg.get("FOCUS", (0.445, 0.40))

# --- segments on the frame grid (picture and sound are cut on the same grid -> lip sync is exact)
segs, cur = [], 0
for a, b in REMOVE:
    segs.append((cur, round(a * FPS)))
    cur = round(b * FPS)
segs.append((cur, SRC_FRAMES))

ZOOMS = cfg.get("ZOOMS")
if not ZOOMS:  # default multicam pattern: wide / tight alternation, last shot tighter for the goodbye
    ZOOMS = [((1.00, 1.05) if i % 2 == 0 else (1.20, 1.23)) for i in range(len(segs))]
    ZOOMS[0] = (1.00, 1.07)
    ZOOMS[-1] = (1.22, 1.30)
assert len(ZOOMS) == len(segs), f"ZOOMS needs {len(segs)} entries (one per kept segment), got {len(ZOOMS)}"

frames, seg_out = [], []  # per output frame: [src_frame, scale, seg_index]
for i, ((f0, f1), (z0, z1)) in enumerate(zip(segs, ZOOMS)):
    seg_out.append((len(frames), f0, f1))
    n = f1 - f0
    for k in range(n):
        frames.append([f0 + k, z0 + (z1 - z0) * k / max(1, n - 1), i])
last_src, last_scale = frames[-1][0], frames[-1][1]
for k in range(round(HOLD * FPS)):  # freeze, still zooming slowly so it never looks stuck
    frames.append([last_src, last_scale + 0.0025 * (k + 1), len(segs) - 1])
OUT_DUR = len(frames) / FPS


def m(t):
    """source seconds -> output seconds"""
    f = t * FPS
    for o0, f0, f1 in seg_out:
        if f < f0:
            return o0 / FPS  # inside a removed pause: snap to the cut
        if f <= f1:
            return (o0 + f - f0) / FPS
    return seg_out[-1][0] / FPS + (f - seg_out[-1][1]) / FPS


# --- words: glue Whisper tokens (c + 'est, mi + -août, Ciao + !), apply fixes, French apostrophes
raw = [dict(w=w["w"].strip(), s=w["s"], e=w["e"]) for s in tr["segments"] for w in s["words"]]
words = []
for w in raw:
    t = w["w"]
    if words and (t.startswith("'") or t.startswith("-")):
        words[-1]["w"] += t; words[-1]["e"] = w["e"]; continue
    if words and t in ("!", "?", ":", ";"):
        words[-1]["w"] += " " + t; words[-1]["e"] = w["e"]; continue
    words.append(dict(w))
FIX = cfg.get("FIX", {})
for w in words:
    w["w"] = FIX.get(w["w"], w["w"]).replace("'", "’")
# Whisper sometimes stretches a word over a pause: TIGHT = {word: (start, end)} (closest occurrence)
for word, (s, e) in cfg.get("TIGHT", {}).items():
    cand = [w for w in words if w["w"] == word]
    if cand:
        w = min(cand, key=lambda w: abs(w["s"] - s)); w["s"], w["e"] = s, e
# MERGE = [("ma", "toile.", "MaToile.", (tmin, tmax))] -> two tokens become one (brand names)
for a, b, merged, (t0, t1) in cfg.get("MERGE", []):
    for i, w in enumerate(words[:-1]):
        if w["w"] == a and words[i + 1]["w"] == b and t0 < w["s"] < t1:
            w["w"] = merged; w["e"] = words[i + 1]["e"]; del words[i + 1]; break

KEY = {k.lower() for k in cfg.get("KEY", set())}
for w in words:
    w["key"] = w["w"].lower().strip(",.!?;:  ") in KEY
    w["os"], w["oe"] = round(m(w["s"]), 3), round(m(w["e"]), 3)

# --- caption chunks: hand-written "a|b|c" so lines break on meaning (must match the words exactly)
CHUNKS = cfg["CHUNKS"].split("|")
chunks, i = [], 0
for c in CHUNKS:
    toks = c.split(" ")
    got = [words[i + k]["w"] if i + k < len(words) else "<END>" for k in range(len(toks))]
    if got != toks:
        ctx = " ".join(w["w"] for w in words[max(0, i - 3):i + len(toks) + 3])
        sys.exit(f"CHUNKS mismatch at word {i}: expected {toks}, transcript has {got}\n  context: ... {ctx} ...")
    chunks.append(list(range(i, i + len(toks)))); i += len(toks)
if i != len(words):
    sys.exit(f"CHUNKS cover {i} words but transcript has {len(words)}; missing: {' '.join(w['w'] for w in words[i:])}")
cap = []
for ci, c in enumerate(chunks):
    s = words[c[0]]["os"] - 0.03
    e = words[c[-1]]["oe"] + 0.30
    if ci + 1 < len(chunks):
        e = min(e, words[chunks[ci + 1][0]]["os"] - 0.03)
    cap.append(dict(s=round(s, 3), e=round(e, 3), w=c))

# --- overlay events: every float is a source time -> mapped
events = {k: {kk: (round(m(v), 3) if isinstance(v, float) else v) for kk, v in ev.items()}
          for k, ev in cfg["EVENTS"].items()}
END_AT = cfg["END_AT"]
events["end"] = dict(t_in=round(m(END_AT), 3), t_out=round(OUT_DUR, 3))
events["hide_caps"] = [[round(m(a), 3), round(m(b), 3)] for a, b in cfg.get("HIDE_CAPS", [])] + [[round(m(END_AT), 3), 999]]
bumps = [round(m(t), 3) for t in cfg.get("BUMPS", [])]

plan = dict(src=SRC, src_w=SRC_W, src_h=SRC_H, fps=FPS, out_frames=len(frames), out_dur=OUT_DUR, focus=FOCUS,
            frames=frames, segs=[dict(o0=o0, f0=f0, f1=f1) for o0, f0, f1 in seg_out], words=words, caps=cap,
            events=events, bumps=bumps, profile=cfg["PROFILE"])
json.dump(plan, open(f"{work}/plan.json", "w", encoding="utf-8"), ensure_ascii=False)
open(f"{work}/plan.js", "w", encoding="utf-8").write("window.PLAN=" + json.dumps(plan, ensure_ascii=False) + ";")
print(f"source {SRC_W}x{SRC_H} {FPS}fps {SRC_FRAMES} frames -> output {len(frames)} frames, {OUT_DUR:.2f}s")
for c in cap:
    flag = "  <-- short" if c["e"] - c["s"] < 0.45 else ""
    print("%6.2f-%6.2f  %s%s" % (c["s"], c["e"], " ".join(words[i]["w"] for i in c["w"]), flag))
print(json.dumps({k: v for k, v in events.items() if k != "hide_caps"}))
