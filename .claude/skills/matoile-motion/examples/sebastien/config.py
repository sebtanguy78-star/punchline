# Config of the validated video (Sébastien, 50 s face cam, 1080x608 24 fps). Copy this file for a new video and
# rewrite every section; all times are SOURCE seconds (as in the Whisper transcript), plan.py maps them.

SRC = "/path/to/VID_20261104_034943_823_bsl.mp4"   # overridden by the command line in the test run

# --- edit -------------------------------------------------------------------------------------------
HOLD = 3.0                       # seconds of freeze added at the end for the end card
REMOVE = [(6.37, 6.61), (11.31, 11.56), (17.78, 18.08), (23.36, 23.81), (26.30, 26.63),   # from pauses.py
          (33.02, 33.35), (37.76, 38.19), (42.95, 43.38), (46.14, 46.66), (48.25, 48.71)]
# one (start, end) zoom per kept segment = len(REMOVE) + 1. None -> automatic wide/tight alternation.
ZOOMS = [(1.00, 1.07), (1.20, 1.23), (1.00, 1.05), (1.18, 1.21), (1.26, 1.28), (1.00, 1.05),
         (1.20, 1.23), (1.00, 1.05), (1.18, 1.21), (1.03, 1.06), (1.22, 1.30)]
FOCUS = (0.445, 0.40)            # face centre in the source frame (0-1), zooms are centred on it
BUMPS = [2.26, 9.82, 10.68, 34.62, 45.80]   # +4.5 % zoom punch on strong words (name, numbers, title, click)

# --- words ------------------------------------------------------------------------------------------
FIX = {"B": "Baie", "fast": "face"}         # Whisper mis-hearings ("Grand B" -> Grand Baie, "fast cam" -> face cam)
TIGHT = {"avec": (18.10, 18.36), "J’ai": (26.63, 27.04), "et": (46.70, 47.10), "Ciao !": (48.74, 49.20)}
MERGE = [("ma", "toile.", "MaToile.", (25, 27))]   # the brand: "j'ai rejoint ma toile" -> MaToile
KEY = {"matoile", "sébastien", "grand", "baie", "maurice", "2026", "studio", "podcasts", "mobiles", "caméras", "micros",
       "débats", "face", "cam", "décor", "décors", "adresses", "contacts", "toile", "youtube", "familiale",
       "trio", "coco", "dodo", "jeudis", "resto", "personnes", "ciao", "échanges", "fille", "femme", "3"}
CHUNKS = ("Salut à tous,|bienvenue sur ma fiche,|moi c’est Sébastien,|je suis arrivé|à Grand Baie|dans le nord|"
          "de l’île Maurice,|mi-août 2026.|J’ai ensuite monté|un petit studio|de podcasts mobiles|avec 3 caméras|"
          "et 3 micros,|ce qui permet|de pouvoir filmer|des échanges|lors de débats|ou même|du face cam|"
          "comme maintenant|avec un beau décor.|L’île Maurice a|de très bons décors,|il suffit d’avoir|"
          "les bonnes adresses,|les bons contacts,|c’est pour ça|que j’ai rejoint MaToile.|J’ai aussi ensuite|"
          "lancé une petite|chaîne YouTube|familiale|avec ma femme|et ma fille|de 3 ans,|qui s’appelle|"
          "Trio Coco Dodo,|donc voilà|on essaye de faire|une petite vidéo|tous les jeudis.|Sinon à part ça|je suis|"
          "toujours partant|pour aller faire|un bon resto,|rencontrer de|nouvelles personnes.|N’hésitez pas|"
          "à m’ajouter|à votre toile|et au plaisir|de discuter.|Ciao !")

# --- overlay ----------------------------------------------------------------------------------------
# keys must match the ids used in cards.js; t_in / t_out = card in/out, t_c1.. / t_chip = chip pops,
# t_w1.. = big word slams, t_click = CTA click. (audio.py puts the SFX on these names automatically)
EVENTS = dict(
    name=dict(t_in=0.95, t_name=2.26, t_out=6.85),
    loc=dict(t_in=3.40, t_sub=4.36, t_chip=5.40, t_out=6.95),
    studio=dict(t_in=7.70, t_c1=9.82, t_c2=10.68, t_out=11.85),
    formats=dict(t_in=12.40, t_c1=13.30, t_c2=14.20, t_c3=15.84, t_out=16.45),
    rec=dict(t_in=16.34, t_out=19.12),                       # viewfinder on "comme maintenant"
    decors=dict(t_in=19.95, t_c1=21.62, t_c2=22.58, t_out=24.10),
    matoile=dict(t_in=25.55, t_out=28.35),                   # brand card on "j'ai rejoint MaToile"
    yt=dict(t_in=28.70, t_c1=31.32, t_c2=32.02, t_out=33.50),
    trio=dict(t_in=33.72, t_w1=33.78, t_w2=34.28, t_w3=34.62, t_chip=36.60, t_out=38.35),
    partant=dict(t_in=39.60, t_c1=41.06, t_c2=41.62, t_out=43.55),
    cta=dict(t_in=44.05, t_cursor=44.70, t_click=45.80, t_chip=47.10, t_out=48.45),   # "ajoutez-moi à votre toile"
)
HIDE_CAPS = [(33.70, 35.05)]     # no captions while the big Trio/Coco/Dodo title is on screen
END_AT = 49.30                   # end card (flag wipe + logo) starts right after the last word

PROFILE = dict(
    name="Sébastien",
    place="Grand Baie · Île Maurice",
    cta_chip="Au plaisir de discuter !",
    avatar_t=49.5, avatar_crop="330:330:337:62",   # smiling frame; crop=w:h:x:y in source pixels
    cap_bottom=190,              # caption baseline height (px from bottom of 1080). 112 was judged too low.
)
