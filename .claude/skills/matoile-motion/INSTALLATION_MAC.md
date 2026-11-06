# Installer le skill « matoile-motion » sur ton Mac

Ce skill permet à Claude Code, sur ton Mac, de monter tes vidéos face caméra exactement comme la vidéo validée
(charte MaToile, sous-titres animés, cartes, fin avec le logo, son à -12 LUFS, export 720p < 15 Mo).

## 1. Installer les outils (une seule fois)
Ouvre le Terminal et colle :

```bash
# Homebrew (si tu ne l'as pas déjà) : https://brew.sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# les outils utilisés par le skill
brew install ffmpeg node python
```

## 2. Installer le skill
Si tu as téléchargé `matoile-motion.skill` (dans Téléchargements) :

```bash
mkdir -p ~/.claude/skills
unzip -o ~/Downloads/matoile-motion.skill -d ~/.claude/skills/
```

Tu dois obtenir le fichier `~/.claude/skills/matoile-motion/SKILL.md`.

## 3. L'utiliser
Lance Claude Code dans le Terminal (`claude`), puis par exemple :

> Monte cette vidéo avec le skill matoile-motion : (glisse la vidéo dans le Terminal)

Claude prépare un dossier de travail dans `~/Movies/MaToile/<nom-de-la-video>/` et y dépose la vidéo finale
(`…_720p_HQ.mp4`).

## Bon à savoir
- **Premier montage plus long** : le skill télécharge une fois le modèle de transcription (environ 1,5 Go) et le
  navigateur qui dessine les animations (environ 200 Mo). Les fois suivantes, c'est direct.
- **Durée** : compte environ 10 minutes pour une vidéo d'une minute (transcription + rendu + export).
- **Vidéo d'iPhone** : si elle est en HDR, Claude la convertit d'abord pour garder de bonnes couleurs.
