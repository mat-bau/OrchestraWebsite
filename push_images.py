#!/usr/bin/env python3
"""
Script pour pusher les images par lots de max 1 Mo
Usage: python push_images.py
"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

# Configuration
MAX_COMMIT_SIZE_MB = 0.70  # Taille max par commit
IMAGES_FOLDER = "images"   # Dossier à traiter
BRANCH = "main"            # Branche Git

def get_file_size_mb(filepath: Path) -> float:
    """Retourne la taille du fichier en Mo"""
    return filepath.stat().st_size / (1024 * 1024)

def run_git_command(command: List[str]) -> Tuple[bool, str]:
    """Execute une commande Git et retourne le résultat"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def get_untracked_images() -> List[Path]:
    """Récupère la liste des fichiers images non trackés"""
    # Extensions d'images
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    # Obtenir les fichiers non trackés
    success, output = run_git_command(['git', 'ls-files', '--others', '--exclude-standard'])
    
    if not success:
        print(f"❌ Erreur Git: {output}")
        return []
    
    untracked_files = output.strip().split('\n') if output.strip() else []
    
    # Filtrer uniquement les images dans le dossier images/
    image_files = []
    for file in untracked_files:
        file_path = Path(file)
        if (file_path.exists() and 
            file_path.suffix.lower() in image_extensions and
            str(file_path).startswith(IMAGES_FOLDER)):
            image_files.append(file_path)
    
    return image_files

def get_modified_images() -> List[Path]:
    """Récupère la liste des images modifiées"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    success, output = run_git_command(['git', 'diff', '--name-only'])
    
    if not success:
        return []
    
    modified_files = output.strip().split('\n') if output.strip() else []
    
    image_files = []
    for file in modified_files:
        file_path = Path(file)
        if (file_path.exists() and 
            file_path.suffix.lower() in image_extensions and
            str(file_path).startswith(IMAGES_FOLDER)):
            image_files.append(file_path)
    
    return image_files

def create_batches(files: List[Path], max_size_mb: float) -> List[List[Path]]:
    """Crée des lots de fichiers ne dépassant pas max_size_mb"""
    batches = []
    current_batch = []
    current_size = 0.0
    
    # Trier les fichiers par taille (plus petits en premier)
    sorted_files = sorted(files, key=lambda f: get_file_size_mb(f))
    
    for file in sorted_files:
        file_size = get_file_size_mb(file)
        
        # Si le fichier est trop gros seul
        if file_size > max_size_mb:
            # Le mettre dans son propre batch avec un warning
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_size = 0.0
            
            batches.append([file])
            print(f"⚠️  {file} ({file_size:.2f} Mo) dépasse la limite et sera dans son propre commit")
            continue
        
        # Si ajouter ce fichier dépasse la limite
        if current_size + file_size > max_size_mb:
            batches.append(current_batch)
            current_batch = [file]
            current_size = file_size
        else:
            current_batch.append(file)
            current_size += file_size
    
    # Ajouter le dernier batch
    if current_batch:
        batches.append(current_batch)
    
    return batches

def commit_and_push_batch(batch: List[Path], batch_num: int, total_batches: int) -> bool:
    """Commit et push un lot de fichiers"""
    batch_size = sum(get_file_size_mb(f) for f in batch)
    
    print(f"\n{'='*70}")
    print(f"📦 Batch {batch_num}/{total_batches} - {len(batch)} fichiers - {batch_size:.2f} Mo")
    print(f"{'='*70}")
    
    # Afficher les fichiers
    for file in batch:
        print(f"   📸 {file} ({get_file_size_mb(file):.2f} Mo)")
    
    # Ajouter les fichiers
    for file in batch:
        success, output = run_git_command(['git', 'add', str(file)])
        if not success:
            print(f"❌ Erreur lors de l'ajout de {file}: {output}")
            return False
    
    # Créer le commit
    commit_message = f"Add images batch {batch_num}/{total_batches} ({batch_size:.2f} Mo)"
    success, output = run_git_command(['git', 'commit', '-m', commit_message])
    
    if not success:
        print(f"❌ Erreur lors du commit: {output}")
        return False
    
    print(f"✅ Commit créé: {commit_message}")
    
    # Push
    print(f"⬆️  Push en cours vers {BRANCH}...")
    success, output = run_git_command(['git', 'push', 'origin', BRANCH])
    
    if not success:
        print(f"❌ Erreur lors du push: {output}")
        print(f"💡 Vous pouvez réessayer manuellement: git push origin {BRANCH}")
        return False
    
    print(f"✅ Push réussi!")
    return True

def main():
    print("="*70)
    print("🚀 PUSH AUTOMATIQUE D'IMAGES PAR LOTS")
    print("="*70)
    print(f"📁 Dossier       : {IMAGES_FOLDER}")
    print(f"📊 Taille max    : {MAX_COMMIT_SIZE_MB} Mo par commit")
    print(f"🌿 Branche       : {BRANCH}")
    print("="*70)
    
    # Vérifier qu'on est dans un repo Git
    if not Path('.git').exists():
        print("❌ Erreur: Pas de repository Git trouvé!")
        print("   Assurez-vous d'être à la racine du projet")
        return
    
    # Récupérer les images non trackées et modifiées
    print("\n🔍 Recherche des images à pusher...")
    untracked = get_untracked_images()
    modified = get_modified_images()
    
    all_images = list(set(untracked + modified))  # Supprimer les doublons
    
    if not all_images:
        print("✅ Aucune image à pusher!")
        return
    
    total_size = sum(get_file_size_mb(f) for f in all_images)
    print(f"\n📊 Statistiques:")
    print(f"   🆕 Nouvelles images  : {len(untracked)}")
    print(f"   ✏️  Images modifiées  : {len(modified)}")
    print(f"   📦 Total             : {len(all_images)} images ({total_size:.2f} Mo)")
    
    # Créer les batches
    print(f"\n📦 Création des batches de {MAX_COMMIT_SIZE_MB} Mo...")
    batches = create_batches(all_images, MAX_COMMIT_SIZE_MB)
    
    print(f"\n✅ {len(batches)} batch(es) créé(s)")
    
    # Demander confirmation
    print("\n" + "="*70)
    response = input(f"Voulez-vous pusher ces {len(batches)} batch(es) ? (o/N) : ")
    
    if response.lower() not in ['o', 'oui', 'y', 'yes']:
        print("❌ Annulé par l'utilisateur")
        return
    
    # Pusher chaque batch
    success_count = 0
    for i, batch in enumerate(batches, 1):
        if commit_and_push_batch(batch, i, len(batches)):
            success_count += 1
        else:
            print(f"\n⚠️  Arrêt après l'échec du batch {i}")
            break
    
    # Résumé final
    print("\n" + "="*70)
    print("📊 RÉSUMÉ FINAL")
    print("="*70)
    print(f"✅ Batches pushés avec succès : {success_count}/{len(batches)}")
    
    if success_count == len(batches):
        print("🎉 Toutes les images ont été pushées!")
    else:
        print(f"⚠️  {len(batches) - success_count} batch(es) n'ont pas pu être pushé(s)")
    
    print("="*70)

if __name__ == "__main__":
    main()