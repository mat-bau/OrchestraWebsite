# data-planifier/

Dossier de travail du planificateur de répétitions.

## Sous-dossiers

- `uploads/` — fichiers Excel uploadés (conservés par session avec un UUID)
- `exports/` — fichiers Excel générés (planning final téléchargeable)

## Format du fichier Répartition (repartition.xlsx)

Colonnes obligatoires :
- **Morceau** — nom du morceau
- Une colonne par musicien (nom exact) avec les valeurs : `Oui`, `Non`, `Peut-être`

Colonne optionnelle :
- **Répétitions** — nombre de fois que le morceau doit être répété (entier, défaut = 1)

## Format du fichier Disponibilités (disponibilites.xlsx)

- Ligne 1 : en-têtes (Nom, puis les créneaux ex: "Lundi 05 14:00-16:00")
- Lignes suivantes : un musicien par ligne, valeurs `Oui` / `Non` / `Peut-être`

## Nettoyage

Les fichiers uploads et exports s'accumulent avec le temps.
Ils peuvent être supprimés manuellement si l'espace disque est limité.
Seuls les fichiers de la session en cours sont nécessaires.
