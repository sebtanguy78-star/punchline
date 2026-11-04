---
name: matoile-motion
description: Montage vidéo « motion design » aux couleurs de MaToile (réseau de l'île Maurice) pour des vidéos face caméra, podcast ou fiche de présentation — coupe des blancs, zooms façon multicam, sous-titres animés mot à mot, cartes infos animées synchronisées sur la voix, viseur REC, carte MaToile, bouton « Ajouter à ma toile », écran de fin avec rayures du drapeau mauricien et logo MaToile, son fort à -12 LUFS sans saturation, exports 1080p + 720p légers. Utilise ce skill dès que l'utilisateur envoie une vidéo (mp4, mov…) d'une personne qui parle et demande de la monter, d'ajouter du motion design, des sous-titres, des animations, de « faire comme la dernière fois », « même charte », « pour MaToile », une vidéo de profil / de présentation — même s'il ne cite pas MaToile explicitement.
---

# MaToile motion — montage face caméra à la charte MaToile

Ce skill refait **à l'identique** une vidéo que l'utilisateur a validée (« c'est super, la prochaine fois je veux
tout pareil »). Le style, les couleurs, les animations, le son et les exports sont figés dans les scripts et le
template : ton travail sur une nouvelle vidéo est surtout **éditorial** (lire la transcription, choisir les
moments forts, écrire le texte des cartes), pas de redessiner. Réponds à l'utilisateur en français.

Avant d'écrire le contenu, lis `references/charte.md` (couleurs, composants, règles de mise en page) et regarde
l'exemple complet `examples/sebastien/` (config + cartes de la vidéo validée).

## Ce que l'utilisateur attend (résultat validé)
- Rythme : blancs coupés, alternance plan large / plan serré à chaque coupe, petits « punch » de zoom sur les mots forts.
- Sous-titres mot à mot (pop), Inter 800 casse normale, mots-clés en or, **placés plus haut qu'à l'origine**
  (`cap_bottom` 190 px — demande explicite de l'utilisateur).
- Cartes infos à droite, synchronisées sur les mots : nom + lieu, puis une carte par idée (chips sur les noms
  concrets, chiffres, lieux), viseur REC si la personne parle du tournage, carte MaToile quand elle cite MaToile,
  gros titre « qui tombe » pour un nom de marque/chaîne, CTA « Ajouter à ma toile » avec clic, écran de fin MaToile.
- Charte MaToile stricte : bleu-vert foncé, turquoise `#4FC9C2`, or `#E2B65C`, drapeau mauricien en accent.
- Son plus fort sans saturer : -12 LUFS, crête ≤ -1,5 dBTP. Bruitages discrets.
- Livraison : master 1080p + **720p ~7 Mo (recommandé)** + 720p léger ~5 Mo.

## Pipeline
Variables : `SK` = dossier de ce skill, `W` = dossier de travail (scratchpad), `V` = vidéo de l'utilisateur.
Le rendu complet prend ~6 min pour 50 s de vidéo ; donne des nouvelles à l'utilisateur entre les étapes.

1. **Préparer** : `bash $SK/scripts/setup.sh $W` (venv Whisper/Pillow, polices Inter, icônes Lucide, Playwright).
2. **Regarder la vidéo** : `ffprobe` (taille, fps, durée) + planche contact
   (`ffmpeg -i $V -vf "fps=1/2,scale=360:-1,tile=5x5" -frames:v 1 $W/contact.jpg`) et une image pleine résolution.
   Repère le centre du visage → `FOCUS` (x, y entre 0 et 1) et une image où la personne sourit → avatar.
3. **Transcrire** : `$W/venv/bin/python -I $SK/scripts/transcribe.py $V $W/transcript.json` (Whisper medium,
   français). Les mots marqués `?` sont incertains (souvent noms propres / lieux) : corrige-les via `FIX`
   et signale-les à l'utilisateur. Déjà vu : « Grand B » → Grand Baie, « fast cam » → face cam, « ma toile » → MaToile.
4. **Pauses** : `python3 $SK/scripts/pauses.py $V` → colle la ligne `REMOVE = [...]` dans la config.
5. **Écrire la config** : copie `examples/sebastien/config.py` dans `$W/config.py` (mets `SRC = "$V"`) et réécris
   chaque section pour la nouvelle vidéo (voir « Écrire le contenu » plus bas). Copie `examples/sebastien/cards.html`
   et `cards.js` dans `$W/cards/` et adapte-les.
6. **Plan** : `python3 $SK/scripts/plan.py $W/config.py $W/transcript.json $W` — affiche les sous-titres avec leurs
   horaires de sortie (`<-- short` = moins de 0,45 s : fusionne avec le voisin si possible). En cas d'erreur
   « CHUNKS mismatch », le message montre les mots attendus : corrige le découpage.
7. **Calque** : `python3 $SK/scripts/build_overlay.py $W $W/cards` (assemble le HTML, icônes, avatar).
8. **Aperçu** : `bash $SK/scripts/preview.sh $W 3.2,10.5,24.9,32.6,43.6,47.5` (temps de SORTIE, en secondes,
   un par carte importante + fin) puis **regarde `$W/test/sheet.jpg`** : rien sur le visage, textes lisibles,
   icônes complètes, pas de chevauchement. Corrige et recommence tant que ce n'est pas propre.
9. **Rendu complet** (en parallèle) : `bash $SK/scripts/render_all.sh $W` et
   `$W/venv/bin/python -I $SK/scripts/audio.py $W`, puis
   `$W/venv/bin/python -I $SK/scripts/compose.py $W full $W/<Nom>_MaToile_master.mp4`.
10. **Exports** : `bash $SK/scripts/export.sh $W/<Nom>_MaToile_master.mp4 $W/<Nom>_MaToile`.
11. **Vérifier** : `ffprobe` (1920×1080 / 1280×720, durée), loudness
    (`ffmpeg -i f.mp4 -af ebur128=peak=true -f null -` → I ≈ -12 LUFS, Peak ≤ -1,5), et quelques images extraites
    du fichier final. N'annonce que ce que tu as vérifié ; tu ne peux pas écouter : dis-le pour les bruitages.
12. **Livrer** avec SendUserFile : le 720p recommandé (et le léger), le master si demandé. Message court en
    français : ce qui a été fait, mots à vérifier (orthographe des noms), proposition de version 9:16.

## Écrire le contenu (la partie qui demande du jugement)
Lis toute la transcription et découpe-la en idées. Pour chaque idée, une carte ; pour chaque nom concret,
chiffre ou lieu prononcé, une chip qui pop **au moment exact du mot** (prends le `s` du mot dans transcript.json).

- `CHUNKS` : sous-titres de 1 à 4 mots, coupés sur le sens (« à Grand Baie | dans le nord | de l'île Maurice, »),
  jamais un article seul en fin de ligne, ~25 caractères max. Doit reprendre les mots exactement (apostrophes `’`,
  « Ciao ! » avec espace insécable).
- `KEY` : mots en or — noms propres, lieux, chiffres, mots-thèmes (1 à 2 par ligne au plus).
- `EVENTS` (temps source) : `t_in` un peu avant le mot déclencheur, `t_out` juste avant la carte suivante
  (une carte peut chevaucher une coupe : ça masque le saut d'image). Toujours `name` (prénom) + `loc` en intro si
  la personne se présente. `rec` sur « comme maintenant ». `matoile` sur la mention de MaToile. `cta` sur
  « ajoutez-moi / n'hésitez pas » avec `t_click` sur le mot « toile ». `END_AT` juste après le dernier mot.
- `BUMPS` : 4-5 mots forts. `HIDE_CAPS` : pendant un gros titre (`.tape`).
- `PROFILE` : prénom, lieu (« Ville · Île Maurice »), `avatar_t` + `avatar_crop` (`w:h:x:y` carré autour du visage
  en pixels source — vérifie l'image `$W/render/avatar.jpg`), `cap_bottom` 190, et **`panel_side`** :
  `"right"` (défaut, colonne de cartes à x=1160) si le visage est à gauche/centre-gauche, `"left"` (x=70, les cartes
  glissent depuis la gauche) si le visage est au centre ou à droite. Règle : en 1920 px de large, le bord du visage
  sur le plan serré ne doit jamais toucher la colonne (≥ 40 px d'écart). Vidéo 2 (visage à x≈0,55) → `"left"`.
- Source en basse définition (≤ 720 px de large) : plans serrés à ~1,15 au lieu de 1,20 pour garder du piqué.
- Un long passage sans pause (> 6 s) peut recevoir un changement de plan sans coupe : une entrée `(t, t)` dans
  `REMOVE` (placer `t` entre deux mots), avec un zoom différent pour le segment suivant.
- `cards.html` / `cards.js` : copie les blocs de l'exemple et change les textes, icônes (`{{nom-lucide}}`, voir
  lucide.dev ; `{{web}}` = icône toile MaToile) et positions `top`. Chaque bloc de `renderCards` suit le même
  schéma : `slide()` pour la carte, `pop()` pour chaque chip, avec les noms d'événements de la config.
  Les ids HTML doivent être uniques ; garde les chips d'une même carte espacées de ~94 px en `top`.

## Pièges déjà rencontrés
- PyAV récent casse `faster_whisper.decode_audio` (`metadata_errors`) : `transcribe.py` décode avec ffmpeg et passe un
  tableau numpy — ne pas « simplifier ».
- Icônes Lucide : ne retirer `width/height` que sur la balise `<svg>` (sinon les `<rect>` disparaissent : caméra,
  micro, calendrier tronqués). `build_overlay.py` le fait déjà.
- Quand le calque est entièrement opaque (fin), Chromium écrit un PNG RGB : `compose.py` convertit en RGBA.
- Les images figées de fin partagent la même image source : le mode `test` de `compose.py` le gère.
- Emojis couleur dans les chips = rendu flou/incohérent sur fond foncé : utiliser des icônes Lucide (le 👋 du
  label d'intro est la seule exception validée).
- Ne pas publier la vidéo dans le dépôt Git d'un site (fichier lourd, déployé publiquement) : livrer le fichier.

## Fichiers
- `scripts/` : `setup.sh`, `transcribe.py`, `pauses.py`, `plan.py`, `build_overlay.py`, `render.js`,
  `render_all.sh`, `preview.sh`, `audio.py`, `compose.py`, `export.sh`.
- `template/overlay.src.html` : charte + composants génériques (sous-titres, REC, CTA, volet drapeau, écran de fin).
  `template/icons/web.svg` : icône toile.
- `assets/logo_matoile.png` : logo fourni par l'utilisateur.
- `examples/sebastien/` : config + cartes de la vidéo validée (référence de rythme et de contenu).
- `examples/sebastien-nuit/` : 2ᵉ vidéo (de nuit, 720 px, visage au centre-droit) : cartes à gauche
  (`panel_side`), plans serrés réduits, changement de plan sans coupe, carte « Vous avez un projet ? » à 4 chips.
- `references/charte.md` : couleurs, typo, composants, timings, son, exports.
