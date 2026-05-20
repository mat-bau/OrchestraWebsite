# frontend/src/scss/

Sources SCSS. Compilées en `frontend/style.css` par `npm run build`.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `main.scss` | Point d'entrée — importe tous les partials |
| `_variables.scss` | Couleurs, polices, breakpoints |
| `_legacy.scss` | CSS original (ne pas modifier) |
| `_about.scss` | Styles page About |
| `_gallery.scss` | Styles galerie photos |
| `_videos.scss` | Styles page Vidéos (timeline) |
| `_planner.scss` | Styles planificateur |
| `_contact.scss` | Styles page Contact |
| `_responsive.scss` | Overrides mobile (< 768px) |

## Modifier le CSS

1. Éditer le fichier partial correspondant à la page
2. `npm run build` pour recompiler
3. Rafraîchir le navigateur

## Ajouter des styles pour une nouvelle page

1. Créer `_mapage.scss`
2. Ajouter `@import 'mapage';` dans `main.scss` avant `responsive`
