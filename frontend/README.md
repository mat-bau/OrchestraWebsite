# Frontend

## Pages

| Fichier | Description |
|---------|-------------|
| `index.html` | Accueil — slider photos + carousel événements |
| `about.html` | À propos — équipe, concert, initiation |
| `gallery.html` | Galerie photos — navigation par dossiers |
| `videos.html` | Vidéos — timeline chronologique |
| `offer.html` | Contact / demande de prestation |
| `planifier.html` | Outil de planification des répétitions |

## Pour changer quelque chose chaque année

- **Événements (accueil)** → éditer `data/site-config.json` → section `events`
- **Vidéos** → éditer `data/site-config.json` → section `videos`
- **Texte About / trailer** → éditer `data/site-config.json` → section `about`
- **Membres de l'équipe** → éditer `team-profiles.json` à la racine, puis relancer `python3 start.py`
- **Photos** → ajouter dans `images/`, puis relancer `python3 start.py`

## Reconstruire le CSS (si vous modifiez un fichier .scss)

```
npm run build
```

## Structure des sources

```
src/
  scss/   ← sources SCSS (modifier ici, pas dans style.css)
  js/     ← modules ES — un fichier par page
data/     ← fichiers JSON (site-config.json, gallery-structure.json)
js/       ← jQuery + plugins tiers (ne pas modifier)
```
