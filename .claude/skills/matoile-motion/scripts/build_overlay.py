"""Assemble <workdir>/render/overlay.html from the core template + the per-video cards, inline the icons,
fill the profile placeholders and cut the round avatar from the source video.
usage: python build_overlay.py <workdir> <cards_dir>      (cards_dir holds cards.html + cards.js)"""
import json, pathlib, re, shutil, subprocess, sys

SK = pathlib.Path(__file__).resolve().parent.parent
work, cards = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
rd = work / "render"
plan = json.load(open(work / "plan.json"))
prof = plan["profile"]

html = (SK / "template/overlay.src.html").read_text()
html = html.replace("{{CARDS_HTML}}", (cards / "cards.html").read_text())
for k, v in {"NAME": prof["name"], "PLACE": prof["place"], "CTA_CHIP": prof.get("cta_chip", "Au plaisir de discuter !"),
             "CAP_BOTTOM": str(prof.get("cap_bottom", 190))}.items():
    html = html.replace("{{%s}}" % k, v)


def icon(m):  # {{map-pin}} -> inline SVG (skill icons first, then Lucide)
    name = m.group(1)
    f = SK / "template/icons" / f"{name}.svg"
    if not f.exists():
        f = rd / "node_modules/lucide-static/icons" / f"{name}.svg"
    if not f.exists():
        sys.exit(f"icon not found: {name} (see https://lucide.dev/icons)")
    s = re.sub(r"<!--.*?-->", "", f.read_text(), flags=re.S)
    # strip size/class from the <svg> tag only (rect/circle children need their own width/height!)
    s = re.sub(r"<svg[^>]*>", lambda t: re.sub(r'\s(width|height|class)="[^"]*"', "", t.group(0)), s, count=1)
    return s.strip()


html = re.sub(r"\{\{([a-z0-9-]+)\}\}", icon, html)
left = re.findall(r"\{\{[^}]+\}\}", html)
if left:
    sys.exit(f"unfilled placeholders: {left}")
(rd / "overlay.html").write_text(html)
shutil.copy(cards / "cards.js", rd / "cards.js")
shutil.copy(SK / "assets/logo_matoile.png", rd / "logo_matoile.png")
shutil.copy(SK / "scripts/render.js", rd / "render.js")

# round avatar for the CTA + end card: a smiling frame, square crop around the face
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(prof["avatar_t"]), "-i", plan["src"], "-frames:v", "1", "-vf",
                f"crop={prof['avatar_crop']},scale=400:400:flags=lanczos,eq=saturation=1.08:contrast=1.04",
                "-q:v", "2", str(rd / "avatar.jpg")], check=True)
print("overlay ready:", rd / "overlay.html")
