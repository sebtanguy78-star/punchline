"""Audio: splice the voice on the same frame grid as the picture, clean + make it loud (-12 LUFS) without
saturation (true-peak safe limiter), add subtle synthetic SFX synced to the overlay events.
usage: python -I audio.py <workdir>        -> <workdir>/voice_mix.wav"""
import json, subprocess, sys, re
import numpy as np

SR = 48000
WORK = sys.argv[1]
plan = json.load(open(f"{WORK}/plan.json"))
SRC, fps = plan["src"], plan["fps"]
spf = SR // fps  # samples per frame (2000 at 24 fps)
work = f"{WORK}/audio_tmp"
OUT = f"{WORK}/voice_mix.wav"

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
src = np.frombuffer(raw, np.float32).reshape(-1, 2)

# --- splice
N = plan["out_frames"] * spf
voice = np.zeros((N, 2), np.float32)
fade = int(0.006 * SR)
ramp = np.linspace(0, 1, fade, dtype=np.float32)[:, None]
for s in plan["segs"]:
    a, b = s["f0"] * spf, min(s["f1"] * spf, len(src))
    piece = src[a:b].copy()
    piece[:fade] *= ramp
    piece[-fade:] *= ramp[::-1]
    o = s["o0"] * spf
    voice[o:o + len(piece)] += piece


def ff(inp, out, af):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", inp,
                        "-af", af, "-f", "f32le", "-ar", str(SR), "-ac", "2", out], capture_output=True, text=True)
    if p.returncode:
        sys.exit(p.stderr)
    return p.stderr


# --- voice chain: high-pass, compression, two-pass loudnorm to -12 LUFS (validated: loud, no saturation)
voice.tofile(work + "_v.raw")
pre = "highpass=f=75,acompressor=threshold=-24dB:ratio=3:attack=6:release=150:makeup=3"
st = ff(work + "_v.raw", "/dev/null", pre + ",loudnorm=I=-12:TP=-2:LRA=7:print_format=json")
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", st, re.S).group(0))
ln = (f"loudnorm=I=-12:TP=-2:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
ff(work + "_v.raw", work + "_vn.raw", pre + "," + ln)
voice = np.fromfile(work + "_vn.raw", np.float32).reshape(-1, 2)[:N]
voice = np.pad(voice, ((0, N - len(voice)), (0, 0)))

# --- synthetic SFX (quiet, short)
rng = np.random.default_rng(7)


def db(x):
    return 10 ** (x / 20)


def lp(x, a):  # one-pole low-pass with per-sample coefficient array
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc); y[i] = acc
    return y


def whoosh(d=0.34, g=-31):
    n = int(d * SR); t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t ** 0.7) ** 2
    a = 0.02 + 0.22 * np.sin(np.pi * t) ** 2  # brighter in the middle
    x = rng.standard_normal(n)
    y = lp(lp(x, a), a) - lp(x, a * 0.15)
    y = y / (np.abs(y).max() + 1e-9) * env
    pan = np.linspace(0.35, -0.35, n)  # sweeps right -> left like the cards
    return np.stack([y * (1 - pan), y * (1 + pan)], 1) * db(g)


def pop(g=-27, f0=1400, f1=520, d=0.07):
    n = int(d * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.012)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.018)
    return np.repeat(y[:, None], 2, 1) * db(g)


def thump(g=-21):
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 55 + 90 * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05)
    y += 0.25 * rng.standard_normal(n) * np.exp(-t / 0.008)
    return np.repeat(y[:, None], 2, 1) * db(g)


def click(g=-22):
    n = int(0.03 * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * 2600 * t) * 0.6 + rng.standard_normal(n) * 0.4) * np.exp(-t / 0.004)
    return np.repeat(y[:, None], 2, 1) * db(g)


def beep(g=-30):
    n = int(0.13 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 1000 * t) * np.minimum(1, np.minimum(t / 0.004, (0.13 - t) / 0.01))
    return np.repeat(y[:, None], 2, 1) * db(g)


sfx = np.zeros_like(voice)


def put(t, s):
    o = int(t * SR)
    if 0 <= o < N:
        k = min(len(s), N - o); sfx[o:o + k] += s[:k].astype(np.float32)


E = plan["events"]
for k, ev in E.items():          # generic rules, keyed on the event field names used in cards.js
    if k in ("end", "hide_caps"):
        continue
    for kk, t in ev.items():
        if not isinstance(t, (int, float)):
            continue
        if kk == "t_in":
            put(t, beep()) if k == "rec" else put(t - 0.06, whoosh())   # card slides in / REC starts
        elif re.fullmatch(r"t_c\d+|t_chip", kk):
            put(t, pop())                                               # chip pops
        elif re.fullmatch(r"t_w\d+", kk):
            put(t + 0.05, thump())                                      # big word slams (Trio/Coco/Dodo)
        elif kk == "t_click":
            put(t - 0.02, click())                                      # cursor click on the CTA
put(E["end"]["t_in"] - 0.05, whoosh(0.85, -25))      # flag-stripe wipe
put(E["end"]["t_in"] + 0.45, pop(-24, 900, 300, 0.12))  # logo
put(E["end"]["t_in"] + 1.35, pop(-27))                  # pill

mix = voice + sfx
# fade out over the last 0.6 s
n = int(0.6 * SR); mix[-n:] *= np.linspace(1, 0, n)[:, None] ** 2
mix.astype(np.float32).tofile(work + "_mix.raw")
ff(work + "_mix.raw", work + "_fin.raw", "aresample=192000,alimiter=limit=0.84:attack=1.5:release=60:level=disabled,aresample=48000")
fin = np.fromfile(work + "_fin.raw", np.float32)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", work + "_fin.raw",
                "-c:a", "pcm_s16le", OUT], check=True)
import glob, os
for f in glob.glob(work + "_*.raw"):
    os.remove(f)
print("audio", len(fin) / 2 / SR, "s")
