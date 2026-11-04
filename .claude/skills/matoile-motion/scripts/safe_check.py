"""Draw the MaToile profile-page UI on top of preview stills (side crop, back button, '...' button, profile photo)
to check that no animation hides under them. Zones measured on the user's phone screenshot (header 555 px tall for a
1080 px video -> scale 0.514, 32 screen px cropped each side).
usage: python safe_check.py <workdir> 2.5,10.4,...   (same times as preview.sh) -> <workdir>/test/sheet_safe.jpg"""
import sys
from PIL import Image, ImageDraw

work, names = sys.argv[1], sys.argv[2].split(",")
ims = []
for nm in names:
    im = Image.open(f"{work}/test/c{nm}.jpg").convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    red = (255, 40, 60, 110)
    d.rectangle([0, 0, 62, 1080], fill=red); d.rectangle([1858, 0, 1920, 1080], fill=red)   # cropped by the app
    for cx, cy, r in [(212, 152, 107), (1687, 152, 107), (403, 1060, 240)]:                  # back, menu, photo
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=red, outline=(255, 255, 255, 220), width=4)
    ims.append(Image.alpha_composite(im, ov).convert("RGB").resize((960, 540)))
sheet = Image.new("RGB", (1920, 540 * ((len(ims) + 1) // 2)))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
sheet.save(f"{work}/test/sheet_safe.jpg", quality=85)
print("sheet:", f"{work}/test/sheet_safe.jpg")
