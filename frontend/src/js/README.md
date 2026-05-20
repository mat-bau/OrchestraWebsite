# frontend/src/js/

Modules JavaScript ES — un fichier par page. Chargés avec `<script type="module">`.

## Modules

| Fichier | Page | Rôle |
|---------|------|------|
| `utils.js` | — | Fonctions partagées : `loadJSON`, `escapeHtml`, `youtubeThumbnail`, `getCurrentSchoolYear` |
| `nav.js` | Toutes | Menu mobile (hamburger) |
| `home.js` | index.html | Injecte les événements depuis `site-config.json` dans le carousel |
| `about.js` | about.html | Charge l'équipe depuis `team-profiles.json`, met à jour les textes depuis `site-config.json` |
| `gallery.js` | gallery.html | Navigation galerie, barre de filtres, lightbox (clavier + swipe tactile) |
| `videos.js` | videos.html | Rendu timeline chronologique, modal vidéo lazy |
| `planner.js` | planifier.html | Upload Excel, grille hebdomadaire, drag-and-drop, re-run solver |
| `contact.js` | offer.html | Validation reCAPTCHA + RGPD, soumission Google Forms, overlay succès |

## Dépendances globales

- `window.$` (jQuery 1.11.1) et plugins (FlexSlider, OwlCarousel) — chargés avant les modules via `<script src="js/...">` classiques
- Les modules ES accèdent à jQuery via `window.$`
