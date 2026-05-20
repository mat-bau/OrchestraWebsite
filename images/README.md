# images/

## Dossiers

| Dossier | Contenu |
|---------|---------|
| `about/` | Photos de la page About (instruments, gîte, etc.) |
| `contact/` | Photo de la page Contact |
| `homebackground/` | Photos du slider de la page d'accueil |
| `public/` | **Galerie publique** — scannée automatiquement par `start.py` |
| `support_graphique/` | Logos OrchestraKot (ne pas modifier) |
| `team/` | Photos des membres, organisées par année |

## Ajouter une photo d'équipe

1. Créer un dossier `team/team{annee}/` si besoin (ex: `team/team2026/`)
2. Nommer la photo `{prenom}{nom}{annee}.jpg` (ex: `mariedupont2026.jpg`)
3. Ajouter le chemin dans `team-profiles.json` → `images` du membre
4. Relancer `python3 start.py`

## Ajouter des photos à la galerie publique

1. Placer les photos dans le sous-dossier approprié de `images/public/`
2. Relancer `python3 start.py` — la galerie est mise à jour automatiquement

## Taille recommandée

- Photos galerie : max 2000px côté le plus long, JPG qualité 80%
- Photos équipe : 400×400px minimum, format carré si possible
