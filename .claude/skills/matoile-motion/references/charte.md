# Charte MaToile — motion design (validée par l'utilisateur)

Sources : logo MaToile (`assets/logo_matoile.png` : toile d'araignée turquoise + point or sur fond bleu-vert
foncé, bandeau diagonal aux couleurs du drapeau mauricien en haut à droite) et capture de l'appli (fond foncé
avec motif de toile, avatars ronds cerclés d'or, liens en pointillés or). Ne pas réinventer : tout est déjà
codé dans `template/overlay.src.html` (CSS + composants) et `examples/sebastien/cards.*`.

## Couleurs (variables CSS du template)
| Rôle | Hex | Usage |
|---|---|---|
| `--bg` fond | `#0E1A1D` | cartes (à 93 %), contour des sous-titres, fond écran de fin |
| `--bg2` | `#163236` | centre du dégradé radial de l'écran de fin |
| `--node` | `#1B2E34` | intérieur des ronds d'icônes / nœuds |
| `--teal` turquoise | `#4FC9C2` | icônes, étiquettes (labels), bouton « Ajouté », bordure fine des cartes (22 %) |
| `--gold` or | `#E2B65C` | barre d'accent des cartes, contours des chips et des ronds, mots-clés des sous-titres, boutons |
| drapeau | `#EA2839` `#1A206D` `#FFD500` `#00A551` | rouge/bleu/jaune/vert : mini-drapeau, rayures, volet de fin, point REC |
| `--muted` | `#B7C6C7` | sous-titres de cartes |

Pas de jaune vif « générique » ni d'autres couleurs : or + turquoise sur bleu-vert foncé, drapeau en accent.

## Typo
Inter (fontsource, fichiers locaux) partout. Sous-titres : Inter 800, 70 px, casse normale (pas de majuscules —
« MaToile » doit garder sa casse), contour 13 px `--bg` + ombre. Titres de carte Inter 800 45 px,
labels Inter 700 21 px capitales espacées turquoise, chips Inter 700 33 px.

## Mise en page (1920×1080)
- Tout le graphisme va dans **une colonne latérale** (largeur ≤ 690 px, `top` entre 150 et ~700 px), du côté
  opposé au visage : à droite (`left:1160px`, défaut) si la personne est à gauche/centre-gauche, à gauche
  (`PROFILE["panel_side"] = "left"`, `left:70px`) si elle est au centre/à droite. Ne jamais couvrir le visage.
  Les cartes et les souffles audio arrivent du côté de la colonne.
- **Sous-titres centrés en bas** : 250 px du bas en layout `matoile_profile` (au-dessus de la photo de profil de
  l'appli), 190 px en layout `full` (112 px a été jugé trop bas).
- **Zones masquées par la fiche MaToile** (layout `matoile_profile`, coordonnées vidéo 1920×1080) : bords x<62 et
  x>1858 rognés ; flèche retour cercle (212,152) r≈107 ; bouton « … » (1687,152) r≈107 ; photo de profil (403,1060)
  r≈240. La colonne de cartes démarre donc à y≈290 (top 160 + ×0,85) et finit avant y≈820.
- Une seule « idée » à l'écran à la fois : la carte précédente sort quand la suivante entre.

## Composants (classes du template)
- `.card` (+ `.bar` or à gauche, `.ib` rond icône, `.lab`, `.ttl`, `.sub`) — entrée `slide()` : glisse de 90 px
  depuis la droite en 0,42 s (easeOutCubic), sortie 0,28 s. La barre or se déroule de haut en bas.
- `.chip` (pastille foncée, contour or, icône or) — `pop()` : ressort easeOutBack 0,36 s, déclenché **sur le mot**.
- `.tag` (petit bandeau foncé, capitales, mot clé en or) — intro d'une liste de chips (« On peut **filmer** »).
- `.row` + `.ck` (coche qui se dessine) — check-list dans une carte.
- `.tape` / `.tape.y` — gros mots qui « tombent » (`slam()`), 124 px, alternance foncé / or, rotation ±2-3°.
  Pour un nom propre important (nom de chaîne, marque). Masquer les sous-titres pendant (`HIDE_CAPS`).
- `.flag` mini-drapeau mauricien (4 bandes horizontales) à côté de « île Maurice ».
- `.stripes` 4 bandes du drapeau inclinées (soulignement de marque).
- Carte **MaToile** (`#mt` dans l'exemple) : logo arrondi 118 px qui tourne/rebondit + « J'ai rejoint / MaToile »
  + rayures. À mettre dès que la personne parle de MaToile comme plateforme.
- **REC** (`E.rec`, dans le template) : coins de viseur blancs, point rouge qui clignote, timecode. Quand la personne
  parle du tournage en cours (« comme maintenant », « là je filme »…).
- **CTA** (`E.cta`, dans le template) : fiche avec l'avatar rond cerclé d'or, nom, lieu, bouton or
  « Ajouter à ma toile » (icône toile) ; un curseur arrive et clique sur le mot « toile » → bouton turquoise
  « Ajouté à ma toile » + onde or ; puis chip `cta_chip`. Sur « n'hésitez pas à m'ajouter… ».
- **Fin** (toujours) : les 4 rayures du drapeau balaient l'écran en diagonale (sens du bandeau du logo) et révèlent
  le fond foncé avec la toile (anneaux courbes qui se dessinent), le logo MaToile au centre d'un réseau
  (liens pointillés or vers des nœuds vides cerclés d'or), « RETROUVEZ-MOI SUR / MaToile », rayures, avatar + nom +
  lieu, pastille or « Ajoutez-moi à votre toile ». 3 s de plan figé ajoutées, fondu au noir 0,45 s.

Nœuds du réseau : laisser vides (ne jamais utiliser les photos d'autres membres).

## Montage
- Coupe des blancs ≥ 0,4 s (garder ~0,15 s) avec `pauses.py` → rythme serré.
- Chaque coupe change de valeur de plan (large 1,00→1,05 / serré ~1,20 centré sur le visage) = effet multicam ;
  léger zoom continu dans chaque plan ; dernier plan serré 1,22→1,30 pour l'au revoir.
- « Punch » +4,5 % sur 4-5 mots forts (prénom, chiffres, titre, clic).
- Étalonnage léger (contraste 1,04, saturation 1,10) + netteté douce, upscale 1080p.

## Son
- Voix : passe-haut 75 Hz, compresseur 3:1, loudnorm deux passes **-12 LUFS**, limiteur sur-échantillonné à
  -1,5 dBFS → crête ≈ -1,8 dBTP (fort, sans saturation : validé).
- Bruitages synthétiques discrets posés automatiquement par `audio.py` selon les noms d'événements :
  `t_in` souffle, `t_c1..`/`t_chip` pop, `t_w1..` impact, `t_click` clic, `rec.t_in` bip, fin : souffle long + pops.
- Pas de musique (aucune musique libre de droits disponible) — le proposer à l'utilisateur.

## Exports
- Master 1920×1080 H.264 CRF 17 (~1 Mo/s).
- **720p CRF 24** (~7 Mo pour 50 s, identique à l'œil) = version recommandée ; **720p CRF 26** (~5,4 Mo) légère.
