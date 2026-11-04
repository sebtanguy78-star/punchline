"""Word-level French transcription with faster-whisper.
usage: python -I transcribe.py <video> <out.json> [model=medium]"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

# decode with ffmpeg ourselves and hand Whisper a float array: avoids PyAV version issues ("metadata_errors")
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
model = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else "medium", device="cpu", compute_type="int8")
segs, info = model.transcribe(audio, word_timestamps=True, beam_size=5, vad_filter=False, language="fr")
out = {"language": info.language, "segments": []}
for s in segs:
    out["segments"].append({"start": s.start, "end": s.end, "text": s.text,
                            "words": [{"w": w.word, "s": w.start, "e": w.end, "p": w.probability} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
# words Whisper was unsure about (often names / places): check them by ear or ask the user
for s in out["segments"]:
    for w in s["words"]:
        if w["p"] < 0.6:
            print(f"  ? {w['w'].strip():<15} {w['s']:.2f}s  p={w['p']:.2f}")
