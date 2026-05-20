# Backend

## Fichiers

- **back.py** — Serveur Flask. Sert le frontend statique et expose les routes API du planificateur.
- **scheduler.py** — Algorithme de planification (min-conflicts). **Ne pas modifier l'algorithme** sans comprendre OR-Tools.
- **scan_images.py** — Scanne `images/public/` et génère `frontend/data/gallery-structure.json`.
- **generate_team_gallery.py** — Lit `team-profiles.json` et fusionne les photos d'équipe dans la structure de galerie.

## Lancer le serveur

Depuis la racine du projet :
```
python3 start.py
```
Le serveur démarre sur `http://localhost:5050`.

## Routes API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/api/upload` | POST | Upload des fichiers Excel + premier calcul |
| `/api/replan` | POST | Recalcul avec assignments forcés |
| `/api/download` | GET | Télécharge le fichier Excel généré (`?run_id=...`) |
| `/api/health` | GET | Vérification que le serveur tourne |
| `/data/<file>` | GET | Sert les fichiers JSON de `frontend/data/` |

## Variables d'environnement (.env)

```
PORT=5050
DEBUG=False
BASE_URL=http://localhost:5050
```
