# Guide de Gestion des Images pour Git

Voici comment utiliser les script pour envoyer plein d'images sur le repo du site

### Push Automatique par Lots

**Installation :**
```bash
# 1. Installer les hooks
python setup_git_hooks.py
# Sur mac
python3 setup_git_hooks.py 

# 2. Push vos images par lots
python push_images.py
# Sur mac
python3 push_images.py
```

**Utilisation :**
```bash
# Compresser vos images (première fois)
python compress_images.py

# Pusher les images automatiquement
python push_images.py
```

Le script va :
1. Détecter toutes les nouvelles images
2. Les grouper en lots de 1 Mo max
3. Les commiter et pusher automatiquement
4. Vous montrer la progression

## 🔧 Workflow Recommandé

### Workflow Complet

```bash
# 1. Compresser les images
python compress_images.py
# → Réduit 4 Mo → 0.3-0.5 Mo par image
# → Crée des thumbnails

# 2. Vérifier ce qui va être pushé
git status

# 3. Pusher par lots (si pas Git LFS)
python push_images.py
# → Commits automatiques de 1 Mo max
# → Push progressif

# 4. Scanner la galerie
python start.py
# → Met à jour gallery-structure.json
```

## 🛡️ Hooks Git Installés

Après `python setup_git_hooks.py` :

### Pre-commit Hook
- Bloque les commits > 1 Mo
- Alerte sur les fichiers trop gros
- Suggère d'utiliser `push_images.py`

### Post-commit Hook
- Rappelle s'il reste des images à pusher
- Compte les fichiers non trackés

## 💡 Bonnes Pratiques

### 1. Toujours Compresser d'Abord
```bash
python compress_images.py
```
- Réduit de ~85% la taille
- Améliore les performances web
- Facilite le push Git

### 2. Organiser par Dossiers
```
images/
├── public/              ← Images publiques
│   ├── Concert 2024/
│   ├── Concert 2023/
│   └── Nos équipes/
└── thumbnails/          ← Généré automatiquement
    └── public/
```

### 3. Ne Pas Commiter les Originaux
Ajoutez dans `.gitignore` :
```
# Images non compressées
images/originals/
images/*_original.*
*.raw
```

### 4. Vérifier Régulièrement la Taille du Repo
```bash
# Voir la taille du repo
du -sh .git

# Voir les plus gros fichiers
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 | \
  tail -20
```

## 🚨 En Cas de Problème

### "Repository too large"
```bash
# 1. Utiliser push_images.py au lieu de git push
python push_images.py

# 2. Ou installer Git LFS
python setup_git_lfs.py
```

### "File too large" (> 100 Mo)
```bash
# 1. Compresser davantage
# Dans compress_images.py, ajustez:
TARGET_SIZE_MB = 0.3  # Au lieu de 0.5

# 2. Puis recompresser
python compress_images.py
```

### Rollback un Push Raté
```bash
# Annuler le dernier commit (local)
git reset --soft HEAD~1

# Ou annuler et supprimer les changements
git reset --hard HEAD~1
```

## Estimation de la Capacité

- Repository GitHub : Max ~1 Go recommandé
- Avec compression : ~200-300 images HD
- Avec thumbnails : ~2000-3000 images totales

## 🔗 Ressources

- [Git LFS Official](https://git-lfs.github.com/)
- [GitHub Large Files](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
- [Optimiser les Images Web](https://web.dev/fast/#optimize-your-images)

## Support

Si vous rencontrez des problèmes :
1. Vérifiez que vous avez bien compressé les images
2. Utilisez `python push_images.py` pour pusher par lots et n'hésiter pas à descendre la capacité des lots (MAX_COMMIT_SIZE_MB = ...)
3. Consultez les logs Git : `git log --oneline`

---

**Auteur :** Rondin from OrchestraKot  
**Date :** Octobre 2025  
**Version :** 1.0