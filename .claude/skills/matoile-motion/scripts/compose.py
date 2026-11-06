"""Composite the final picture: source frames (cut + multicam zooms + punch-ins) under the overlay PNGs.
usage: python -I compose.py <workdir> full <out.mp4>        (needs <workdir>/ovl/*.png and <workdir>/voice_mix.wav)
       python -I compose.py <workdir> test 2.5,10,33.4     (renders stills -> <workdir>/test/sheet.jpg)"""
import json, math, subprocess, sys
from PIL import Image

work, mode = sys.argv[1], sys.argv[2]
plan = json.load(open(f"{work}/plan.json", encoding="utf-8"))
SRC, W, H = plan["src"], plan["src_w"], plan["src_h"]
OW, OH = 1920, 1080
fps, frames, (cx, cy), bumps = plan["fps"], plan["frames"], plan["focus"], plan["bumps"]


def bump(t):
    """quick zoom punch on key words: up in 0.12 s, settle over 0.5 s (+4.5 %)"""
    v = 0.0
    for b in bumps:
        d = t - b
        if 0 <= d < 0.12:
            v = max(v, math.sin(d / 0.12 * math.pi / 2))
        elif 0.12 <= d < 0.62:
            x = (d - 0.12) / 0.5
            v = max(v, 1 - (3 * x * x - 2 * x * x * x))
    return 0.045 * v


def transform(img, s):
    # sub-pixel affine zoom about the face (FOCUS) -> smooth slow push-ins, no jitter
    ax, ay = W / (OW * s), H / (OH * s)
    bx, by = W * cx * (1 - 1 / s), H * cy * (1 - 1 / s)
    return img.transform((OW, OH), Image.AFFINE, (ax, 0, bx, 0, ay, by), resample=Image.BICUBIC)


def decoder():
    # light grade + sharpening at source resolution; bt709 in, rgb out
    vf = "scale=in_color_matrix=bt709:in_range=tv,eq=contrast=1.04:saturation=1.10:gamma=0.98,unsharp=5:5:0.45,format=rgb24"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    i = 0
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            p.kill(); return
        yield i, Image.frombuffer("RGB", (W, H), buf, "raw", "RGB", 0, 1)
        i += 1


def frame_at(k, src_img, ovl_path):
    img = transform(src_img, frames[k][1] * (1 + bump(k / fps))).convert("RGBA")
    img.alpha_composite(Image.open(ovl_path).convert("RGBA"))  # fully opaque frames come back as RGB: convert
    return img.convert("RGB")


if mode == "test":
    names = sys.argv[3].split(",")
    need = {}
    for nm in names:  # several stills may share one source frame (freeze at the end)
        need.setdefault(frames[min(len(frames) - 1, round(float(nm) * fps))][0], []).append(nm)
    for i, im in decoder():
        for nm in need.pop(i, []):
            frame_at(min(len(frames) - 1, round(float(nm) * fps)), im, f"{work}/test/t{nm}.png").save(
                f"{work}/test/c{nm}.jpg", quality=88)
        if not need:
            break
    ims = [Image.open(f"{work}/test/c{nm}.jpg").resize((960, 540)) for nm in names]
    rows = (len(ims) + 1) // 2
    sheet = Image.new("RGB", (1920, 540 * rows))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    sheet.save(f"{work}/test/sheet.jpg", quality=85)
    print("sheet:", f"{work}/test/sheet.jpg  (order: {', '.join(names)})")
    sys.exit()

out = sys.argv[3]
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                        "-r", str(fps), "-i", "-", "-i", f"{work}/voice_mix.wav",
                        "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
                        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                       stdin=subprocess.PIPE)
dec = decoder()
cur_i, cur = next(dec)
for k, (src_i, _, _) in enumerate(frames):
    while cur_i < src_i:
        cur_i, cur = next(dec)
    enc.stdin.write(frame_at(k, cur, f"{work}/ovl/{k:05d}.png").tobytes())
    if k % 200 == 0:
        print("frame", k, "/", len(frames), flush=True)
enc.stdin.close()
enc.wait()
print("done", out)
