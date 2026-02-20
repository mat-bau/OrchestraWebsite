#!/bin/bash

MAX_SIZE=5000 # 1 Mo
CURRENT_BATCH_SIZE=0
FILES_COUNT=0

# Couleurs pour le terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}== Verification des fichiers en cours... ==${NC}"

# On récupère TOUT : modifiés, nouveaux, et même ceux déjà en 'staged' (index)
# On filtre pour ne garder que les chemins de fichiers valides
files=$(git status --porcelain | sed 's/^...//')

if [ -z "$files" ]; then
    echo "❌ Aucun fichier modifié ou nouveau détecté. Git est déjà à jour !"
    exit 0
fi

for file in $files; do
    if [ ! -f "$file" ]; then continue; fi

    FILE_SIZE=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
    
    echo "Ajout de : $file ($((FILE_SIZE/1024)) KB)"
    git add "$file"
    CURRENT_BATCH_SIZE=$((CURRENT_BATCH_SIZE + FILE_SIZE))
    FILES_COUNT=$((FILES_COUNT + 1))

    if [ $CURRENT_BATCH_SIZE -ge $MAX_SIZE ]; then
        echo -e "${GREEN}🚀 Batch de 1Mo atteint. Push de $FILES_COUNT fichiers...${NC}"
        git commit -m "Auto-batch push: $(date +%H:%M:%S)"
        git push origin $(git rev-parse --abbrev-ref HEAD)
        CURRENT_BATCH_SIZE=0
        FILES_COUNT=0
    fi
done

# Push final pour le reste
if [ $FILES_COUNT -gt 0 ]; then
    echo -e "${GREEN}🚀 Envoi du dernier batch ($FILES_COUNT fichiers)...${NC}"
    git commit -m "Final batch push"
    git push origin $(git rev-parse --abbrev-ref HEAD)
fi

echo -e "${BLUE}✅ Terminé avec succès !${NC}"