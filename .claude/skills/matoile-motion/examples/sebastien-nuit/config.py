# Vidéo 2 — Sébastien, présentation de nuit (720x406, 24 fps, 52 s). Temps = secondes SOURCE.
SRC = "/path/to/VID_20261104_111019_085_bsl.mp4"

HOLD = 3.0
# pauses.py + (17.14,17.14) = changement de plan sans couper (avant « comme maintenant »)
#           + (46.22, 46.45) = petite pause avant « alors n'hésitez pas » (0,37 s, sous le seuil auto)
REMOVE = [(7.85, 8.09), (10.94, 11.12), (13.09, 13.46), (17.14, 17.14), (23.43, 23.64), (29.65, 29.96),
          (33.29, 33.51), (38.40, 38.73), (41.33, 41.86), (46.22, 46.45)]
# source basse résolution (720 px) : plans serrés un peu moins forts (~1.15) pour rester net
ZOOMS = [(1.00, 1.06), (1.16, 1.19), (1.00, 1.04), (1.15, 1.18), (1.00, 1.06), (1.15, 1.19),
         (1.00, 1.04), (1.15, 1.19), (1.00, 1.04), (1.15, 1.19), (1.02, 1.16)]
FOCUS = (0.545, 0.33)            # visage au centre-droit, haut du cadre
BUMPS = [2.62, 11.62, 12.46, 38.00, 48.58]

FIX = {"B": "Baie", "facecam,": "face cam,", "soirs.": "soir."}
TIGHT = {"avec": (11.14, 11.62), "si": (18.08, 18.14), "C'est": (29.97, 30.06), "qui": (36.73, 36.80)}
TIGHT = {k.replace("'", "’"): v for k, v in TIGHT.items()}
TIGHT["des"] = (20.03, 20.18)
MERGE = [("ma", "toile", "MaToile", (30, 32)), ("ma", "toile.", "MaToile.", (50, 51.5)),
         ("ajoutez", "moi", "ajoutez-moi", (47, 49))]
KEY = {"sébastien", "grand", "baie", "maurice", "2026", "studio", "podcast", "mobile", "caméras", "micros", "3",
       "échanges", "débats", "face cam", "projets", "formations", "coaching", "histoire", "décors", "adresses",
       "contacts", "matoile", "personnes", "youtube", "familiale", "trio", "coco", "dodo", "jeudis", "sortir",
       "découvrir", "toile", "ciao"}
CHUNKS = ("Salut à tous,|bienvenue sur ma fiche,|moi c’est Sébastien,|je suis arrivé|à Grand Baie|dans le nord|"
          "de l’île Maurice,|mi-août 2026.|J’ai ensuite lancé|un studio|de podcast mobile|avec 3 caméras|"
          "et 3 micros,|ce qui permet de pouvoir|filmer des échanges|lors de débats|ou même en face cam,|"
          "comme maintenant|si vous avez des projets,|des formations,|du coaching|ou même simplement|"
          "une histoire à raconter.|L’île Maurice nous offre|de très très|beaux décors,|il suffit pour ça d’avoir|"
          "des bonnes adresses|et surtout|des bons contacts.|C’est pour ça que|j’ai rejoint MaToile|pour rencontrer|"
          "de nouvelles personnes.|Récemment j’ai lancé|une chaîne YouTube|familiale qui s’appelle|"
          "le Trio Coco Dodo,|voilà on essaye|de sortir une vidéo|tous les jeudis soir.|En dehors de la vidéo|"
          "je suis toujours partant|pour sortir, découvrir|de nouvelles choses,|alors n’hésitez pas,|"
          "ajoutez-moi à votre toile|et on se dit à bientôt|sur MaToile.|Ciao !")

EVENTS = dict(
    name=dict(t_in=1.30, t_name=2.62, t_out=8.30),
    loc=dict(t_in=3.86, t_sub=5.20, t_chip=6.44, t_out=8.45),
    studio=dict(t_in=9.10, t_c1=11.62, t_c2=12.46, t_out=13.75),
    formats=dict(t_in=14.15, t_c1=14.98, t_c2=15.84, t_c3=16.76, t_out=17.40),
    rec=dict(t_in=17.18, t_out=23.30),                       # « comme maintenant… »
    projets=dict(t_in=17.95, t_c1=18.88, t_c2=20.18, t_c3=20.92, t_c4=22.40, t_out=23.75),
    decors=dict(t_in=24.90, t_c1=27.70, t_c2=28.76, t_out=30.20),
    matoile=dict(t_in=30.55, t_c1=31.90, t_out=33.40),       # « j'ai rejoint MaToile pour rencontrer… »
    yt=dict(t_in=33.60, t_out=36.85),
    trio=dict(t_in=37.10, t_w1=37.40, t_w2=37.68, t_w3=38.00, t_chip=40.20, t_out=41.40),
    partant=dict(t_in=43.10, t_c1=44.14, t_c2=45.14, t_out=46.55),
    cta=dict(t_in=46.62, t_cursor=47.30, t_click=48.58, t_chip=49.92, t_out=51.20),
)
HIDE_CAPS = [(37.02, 38.45)]
END_AT = 51.75

PROFILE = dict(
    name="Sébastien",
    place="Grand Baie · Île Maurice",
    cta_chip="À bientôt sur MaToile !",
    avatar_t=52.0, avatar_crop="200:200:290:20",
    cap_bottom=190,
    panel_side="left",           # visage au centre-droit -> cartes à gauche
)
