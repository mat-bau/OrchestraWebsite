#!/usr/bin/env python3
"""
Script pour installer les Git hooks automatiques
Usage: python setup_git_hooks.py
"""

import os
from pathlib import Path

# Hook pre-commit pour vérifier la taille
PRE_COMMIT_HOOK = """#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

MAX_SIZE_MB = 1.0  # Taille max par commit

def get_staged_files():
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\\n') if result.stdout.strip() else []

def get_file_size_mb(filepath):
    if not Path(filepath).exists():
        return 0
    return Path(filepath).stat().st_size / (1024 * 1024)

def main():
    staged_files = get_staged_files()
    
    if not staged_files:
        sys.exit(0)
    
    # Calculer la taille totale
    total_size = 0
    large_files = []
    
    for file in staged_files:
        size = get_file_size_mb(file)
        total_size += size
        
        if size > MAX_SIZE_MB:
            large_files.append((file, size))
    
    # Vérifier si des fichiers sont trop gros
    if large_files:
        print("⚠️  ATTENTION: Fichiers trop gros détectés:")
        for file, size in large_files:
            print(f"   📦 {file}: {size:.2f} Mo")
        print(f"\\n💡 Utilisez 'python push_images.py' pour pusher par lots")
    
    # Vérifier si le commit total est trop gros
    if total_size > MAX_SIZE_MB:
        print(f"\\n❌ COMMIT BLOQUÉ:")
        print(f"   Taille totale: {total_size:.2f} Mo (max: {MAX_SIZE_MB} Mo)")
        print(f"\\n💡 Solutions:")
        print(f"   1. Compressez vos images: python compress_images.py")
        print(f"   2. Pushez par lots: python push_images.py")
        print(f"   3. Commitez moins de fichiers à la fois")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
"""

# Hook post-commit pour rappeler push_images.py
POST_COMMIT_HOOK = """#!/bin/bash
# Rappel pour utiliser push_images.py s'il reste des images

UNTRACKED=$(git ls-files --others --exclude-standard images/ 2>/dev/null | grep -E '\\.(jpg|jpeg|png|gif|webp|bmp)$' | wc -l)

if [ "$UNTRACKED" -gt 0 ]; then
    echo ""
    echo "💡 Il reste $UNTRACKED image(s) non commitée(s)"
    echo "   Utilisez: python push_images.py"
    echo ""
fi
"""

def main():
    print("="*70)
    print("🔧 INSTALLATION DES GIT HOOKS")
    print("="*70)
    
    # Vérifier qu'on est dans un repo Git
    if not Path('.git').exists():
        print("❌ Erreur: Pas de repository Git trouvé!")
        return
    
    hooks_dir = Path('.git/hooks')
    hooks_dir.mkdir(exist_ok=True)
    
    # Installer pre-commit hook
    pre_commit_path = hooks_dir / 'pre-commit'
    print(f"\n📝 Installation de pre-commit hook...")
    
    with open(pre_commit_path, 'w') as f:
        f.write(PRE_COMMIT_HOOK)
    
    # Rendre exécutable
    pre_commit_path.chmod(0o755)
    print(f"✅ pre-commit installé: {pre_commit_path}")
    
    # Installer post-commit hook
    post_commit_path = hooks_dir / 'post-commit'
    print(f"\n📝 Installation de post-commit hook...")
    
    with open(post_commit_path, 'w') as f:
        f.write(POST_COMMIT_HOOK)
    
    # Rendre exécutable
    post_commit_path.chmod(0o755)
    print(f"✅ post-commit installé: {post_commit_path}")
    
    print("\n" + "="*70)
    print("✅ INSTALLATION TERMINÉE")
    print("="*70)
    print("\n🎯 Fonctionnalités activées:")
    print("   • Bloque les commits > 1 Mo")
    print("   • Détecte les fichiers trop gros")
    print("   • Rappelle d'utiliser push_images.py")
    print("\n💡 Workflow recommandé:")
    print("   1. Ajoutez vos images: git add images/")
    print("   2. Le hook vérifiera automatiquement la taille")
    print("   3. Si bloqué, utilisez: python push_images.py")
    print("="*70)

if __name__ == "__main__":
    main()