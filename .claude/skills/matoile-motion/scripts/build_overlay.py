"""Assemble <workdir>/render/overlay.html from the core template + the per-video cards, inline the icons,
fill the profile placeholders and cut the round avatar from the source video.
usage: python build_overlay.py <workdir> <cards_dir>      (cards_dir holds cards.html + cards.js)"""
import json, pathlib, re, shutil, subprocess, sys

SK = pathlib.Path(__file__).resolve().parent.parent
work, cards = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
rd = work / "render"
plan = json.load(open(work / "plan.json", encoding="utf-8"))
prof = plan["profile"]
# Layout presets. "matoile_profile" = the video plays as the header of a MaToile profile page (validated on the
# user's phone screenshot): the app crops ~62 px on each side and draws a back button (top-left), a "..." button
# (top-right) and the round profile photo (bottom-left) over the video -> keep every animation out of those zones.
LAYOUTS = {
    "full": dict(panel_top=0, panel_scale=1, left_x=70, right_x=1160, rec_x=56, rec_top=56, rec_bottom=56, cap_bottom=190),
    "matoile_profile": dict(panel_top=160, panel_scale=0.85, left_x=130, right_x=1160, rec_x=120, rec_top=290,
                            rec_bottom=180, cap_bottom=250),
}
L = dict(LAYOUTS[prof.get("layout", "matoile_profile")])
L.update({k: v for k, v in prof.items() if k in L})          # explicit PROFILE values win
# REC labels: "full" = REC top-left / timecode top-right. Profile layout = both stacked on the side opposite the
# cards (the top corners are behind the app buttons, and the cards' first tag sits where "REC" used to be).
if prof.get("layout", "matoile_profile") == "full":
    rec_lbl, rec_tc = "", ""
else:
    side = "right" if prof.get("panel_side") == "left" else "left"
    other = "left" if side == "right" else "right"
    rec_lbl = f"{other}:auto;{side}:40px;top:30px"
    rec_tc = f"{other}:auto;{side}:40px;top:82px"

html = (SK / "template/overlay.src.html").read_text(encoding="utf-8")
html = html.replace("{{CARDS_HTML}}", (cards / "cards.html").read_text(encoding="utf-8"))
for k, v in {"NAME": prof["name"], "PLACE": prof["place"], "CTA_CHIP": prof.get("cta_chip", "Au plaisir de discuter !"),
             "CAP_BOTTOM": str(L["cap_bottom"]), "PANEL_TOP": str(L["panel_top"]), "PANEL_SCALE": str(L["panel_scale"]),
             "REC_LBL": rec_lbl, "REC_TC": rec_tc, "REC_X": str(L["rec_x"]), "REC_TOP": str(L["rec_top"]), "REC_BOTTOM": str(L["rec_bottom"]),
             # card column: right (x=1160) when the person is framed left/centre-left, left (x=70) when the face
             # sits centre/right -- the cards must never cover the face, even on the tight (zoomed) shots
             "PANEL_LEFT": str(prof.get("panel_left", L["left_x"] if prof.get("panel_side") == "left" else L["right_x"]))}.items():
    html = html.replace("{{%s}}" % k, v)


def icon(m):  # {{map-pin}} -> inline SVG (skill icons first, then Lucide)
    name = m.group(1)
    f = SK / "template/icons" / f"{name}.svg"
    if not f.exists():
        f = rd / "node_modules/lucide-static/icons" / f"{name}.svg"
    if not f.exists():
        sys.exit(f"icon not found: {name} (see https://lucide.dev/icons)")
    s = re.sub(r"<!--.*?-->", "", f.read_text(encoding="utf-8"), flags=re.S)
    # strip size/class from the <svg> tag only (rect/circle children need their own width/height!)
    s = re.sub(r"<svg[^>]*>", lambda t: re.sub(r'\s(width|height|class)="[^"]*"', "", t.group(0)), s, count=1)
    return s.strip()


html = re.sub(r"\{\{([a-z0-9-]+)\}\}", icon, html)
left = re.findall(r"\{\{[^}]+\}\}", html)
if left:
    sys.exit(f"unfilled placeholders: {left}")
(rd / "overlay.html").write_text(html, encoding="utf-8")
shutil.copy(cards / "cards.js", rd / "cards.js")
shutil.copy(SK / "assets/logo_matoile.png", rd / "logo_matoile.png")
shutil.copy(SK / "scripts/render.js", rd / "render.js")

# round avatar for the CTA + end card: a smiling frame, square crop around the face
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(prof["avatar_t"]), "-i", plan["src"], "-frames:v", "1", "-vf",
                f"crop={prof['avatar_crop']},scale=400:400:flags=lanczos,eq=saturation=1.08:contrast=1.04",
                "-q:v", "2", str(rd / "avatar.jpg")], check=True)
print("overlay ready:", rd / "overlay.html")
