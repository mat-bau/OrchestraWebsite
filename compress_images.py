#!/usr/bin/env python3
"""
Script de compression intelligente d'images pour Git
Génère des thumbnails + versions optimisées
Usage: python compress_images.py
"""

from PIL import Image
import os
from pathlib import Path

# Configuration
INPUT_FOLDER = "images"
OUTPUT_FOLDER = "images_compressed"

# Paramètres de compression
MAX_DISPLAY_WIDTH = 1920      # Largeur max pour affichage web
MAX_DISPLAY_HEIGHT = 1080     # Hauteur max pour affichage web
DISPLAY_QUALITY = 85          # Qualité pour images d'affichage (bon compromis)

THUMB_SIZE = (400, 400)       # Taille des thumbnails
THUMB_QUALITY = 80            # Qualité des thumbnails

TARGET_SIZE_MB = 0.5          # Taille cible en Mo par image

def get_file_size_mb(filepath):
    """Retourne la taille du fichier en Mo"""
    return os.path.getsize(filepath) / (1024 * 1024)

def compress_image(img_path, output_path, max_size=(1920, 1080), quality=85):
    """Compresse une image avec redimensionnement intelligent"""
    try:
        img = Image.open(img_path)
        
        # Convertir RGBA en RGB si nécessaire (pour JPEG)
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Redimensionner si l'image est trop grande
        original_size = img.size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Essayer différentes qualités pour atteindre la taille cible
        temp_path = output_path + '.tmp'
        current_quality = quality
        
        while current_quality > 40:
            img.save(temp_path, 'JPEG', optimize=True, quality=current_quality)
            size_mb = get_file_size_mb(temp_path)
            
            if size_mb <= TARGET_SIZE_MB:
                os.rename(temp_path, output_path)
                return {
                    'success': True,
                    'original_size': original_size,
                    'new_size': img.size,
                    'file_size_mb': size_mb,
                    'quality': current_quality
                }
            
            current_quality -= 5
        
        # Si on n'a pas atteint la cible, garder la dernière version
        if os.path.exists(temp_path):
            os.rename(temp_path, output_path)
        
        return {
            'success': True,
            'original_size': original_size,
            'new_size': img.size,
            'file_size_mb': get_file_size_mb(output_path),
            'quality': current_quality,
            'warning': 'Taille cible non atteinte'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def create_thumbnail(img_path, thumb_path, size=THUMB_SIZE, quality=THUMB_QUALITY):
    """Crée un thumbnail"""
    try:
        img = Image.open(img_path)
        
        # Convertir en RGB si nécessaire
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Créer le thumbnail (crop au centre)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Sauvegarder
        img.save(thumb_path, 'JPEG', optimize=True, quality=quality)
        
        return {
            'success': True,
            'file_size_mb': get_file_size_mb(thumb_path)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    print("=" * 70)
    print("🖼️  COMPRESSION INTELLIGENTE D'IMAGES POUR GIT")
    print("=" * 70)
    print(f"📁 Source      : {INPUT_FOLDER}")
    print(f"📁 Destination : {OUTPUT_FOLDER}")
    print(f"🎯 Taille max  : {MAX_DISPLAY_WIDTH}x{MAX_DISPLAY_HEIGHT}px")
    print(f"🎯 Qualité     : {DISPLAY_QUALITY}")
    print(f"📏 Thumbnails  : {THUMB_SIZE[0]}x{THUMB_SIZE[1]}px")
    print(f"💾 Cible       : < {TARGET_SIZE_MB} Mo par image")
    print("=" * 70)
    
    input_path = Path(INPUT_FOLDER)
    output_path = Path(OUTPUT_FOLDER)
    
    if not input_path.exists():
        print(f"❌ Le dossier {INPUT_FOLDER} n'existe pas!")
        return
    
    # Créer la structure de dossiers
    output_path.mkdir(exist_ok=True)
    thumbs_path = output_path / "thumbnails"
    thumbs_path.mkdir(exist_ok=True)
    
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'original_size_mb': 0,
        'compressed_size_mb': 0,
        'thumbs_size_mb': 0
    }
    
    # Parcourir tous les fichiers
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    for root, dirs, files in os.walk(input_path):
        for filename in files:
            if Path(filename).suffix.lower() not in image_extensions:
                continue
            
            stats['total'] += 1
            
            # Chemins
            img_path = Path(root) / filename
            relative_path = img_path.relative_to(input_path)
            
            # Créer la structure de dossiers dans output
            output_dir = output_path / relative_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Nom de fichier de sortie (forcer .jpg)
            output_filename = relative_path.stem + '.jpg'
            output_file = output_dir / output_filename
            
            # Thumbnail
            thumb_filename = relative_path.stem + '_thumb.jpg'
            thumb_dir = thumbs_path / relative_path.parent
            thumb_dir.mkdir(parents=True, exist_ok=True)
            thumb_file = thumb_dir / thumb_filename
            
            # Taille originale
            original_size_mb = get_file_size_mb(img_path)
            stats['original_size_mb'] += original_size_mb
            
            print(f"\n📸 {relative_path} ({original_size_mb:.2f} Mo)")
            
            # Compresser l'image principale
            result = compress_image(img_path, output_file)
            
            if result['success']:
                stats['success'] += 1
                stats['compressed_size_mb'] += result['file_size_mb']
                
                reduction = (1 - result['file_size_mb'] / original_size_mb) * 100
                print(f"   ✅ Compressé: {result['file_size_mb']:.2f} Mo "
                      f"(-{reduction:.1f}%) "
                      f"[Q:{result['quality']}]")
                
                if result.get('warning'):
                    print(f"   ⚠️  {result['warning']}")
                
                # Créer le thumbnail
                thumb_result = create_thumbnail(output_file, thumb_file)
                if thumb_result['success']:
                    stats['thumbs_size_mb'] += thumb_result['file_size_mb']
                    print(f"   🖼️  Thumbnail: {thumb_result['file_size_mb']:.2f} Mo")
                
            else:
                stats['failed'] += 1
                print(f"   ❌ Erreur: {result['error']}")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ Images traitées    : {stats['success']}/{stats['total']}")
    print(f"❌ Échecs             : {stats['failed']}")
    print(f"📦 Taille originale   : {stats['original_size_mb']:.2f} Mo")
    print(f"📦 Taille compressée  : {stats['compressed_size_mb']:.2f} Mo")
    print(f"🖼️  Taille thumbnails  : {stats['thumbs_size_mb']:.2f} Mo")
    print(f"📦 Taille totale      : {stats['compressed_size_mb'] + stats['thumbs_size_mb']:.2f} Mo")
    
    if stats['original_size_mb'] > 0:
        total_reduction = (1 - (stats['compressed_size_mb'] + stats['thumbs_size_mb']) / stats['original_size_mb']) * 100
        print(f"💾 Réduction totale   : {total_reduction:.1f}%")
    
    print("=" * 70)
    print("\n💡 PROCHAINES ÉTAPES:")
    print(f"   1. Vérifiez la qualité des images dans {OUTPUT_FOLDER}/")
    print(f"   2. Remplacez votre dossier 'images' par '{OUTPUT_FOLDER}'")
    print(f"   3. Les thumbnails sont dans '{OUTPUT_FOLDER}/thumbnails/'")
    print("\n🎯 POUR LA GALERIE:")
    print(f"   - Utilisez les images de {OUTPUT_FOLDER}/ pour l'affichage")
    print(f"   - Utilisez les thumbnails pour la vue grille")
    print("=" * 70)

if __name__ == "__main__":
    main()