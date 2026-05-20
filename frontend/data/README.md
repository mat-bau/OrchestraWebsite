# frontend/data/

Fichiers JSON utilisés par le site. **C'est ici que vous éditez le contenu chaque année.**

## site-config.json — À ÉDITER CHAQUE ANNÉE

### Événements (`events`)
```json
{
  "title": "Nom de l'événement",
  "day": "7",
  "month": "Avril",
  "location": "Lieu",
  "facebook_url": "https://www.facebook.com/...",
  "description": "Description courte"
}
```

### Vidéos (`videos`)
```json
{
  "youtube_id": "ID depuis l'URL YouTube (ex: kQVHkU5yPTE)",
  "title": "Titre affiché",
  "year": "2025-2026",
  "category": "concert | trailer | autre"
}
```

### Section About (`about`)
- `intro_text` — texte d'introduction de la page About
- `concert_section.text_2` — phrase sur la date du concert
- `concert_section.trailer_youtube_id` — ID YouTube du trailer à afficher

## gallery-structure.json — GÉNÉRÉ AUTOMATIQUEMENT

Généré par `python3 start.py`. Ne pas éditer à la main.
Contient la structure des dossiers `images/public/` + photos d'équipe.
