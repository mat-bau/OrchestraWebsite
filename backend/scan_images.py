#!/usr/bin/env python3
"""
Script pour scanner récursivement le dossier images et générer un JSON
Usage: python scan_images.py [base_path]
Peut être appelé depuis n'importe où dans le projet
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import sys

# Extensions d'images supportées
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

def scan_images_directory(base_path: str = None) -> Dict:
    """
    Scanne récursivement le dossier images et retourne la structure
    """
    if base_path is None:
        current_dir = Path(__file__).parent.absolute()
        if current_dir.name == 'backend':
            project_root = current_dir.parent
        else:
            project_root = current_dir
        base_path = project_root / 'images' / 'public'
    else:
        base_path = Path(base_path)
    
    if not base_path.exists():
        return {"error": "Le dossier images n'existe pas"}
    
    def scan_folder(folder_path: Path, relative_to: Path) -> Dict:
        """Fonction récursive pour scanner un dossier"""
        result = {
            "name": folder_path.name,
            "path": str(folder_path.relative_to(relative_to)),
            "folders": [],
            "images": []
        }
        
        try:
            items = sorted(folder_path.iterdir())
            
            for item in items:
                # Ignorer les fichiers cachés
                if item.name.startswith('.'):
                    continue
                    
                if item.is_dir():
                    # Scanner récursivement les sous-dossiers
                    subfolder = scan_folder(item, relative_to)
                    # N'ajouter que si le dossier contient des images ou sous-dossiers
                    if subfolder['images'] or subfolder['folders']:
                        result['folders'].append(subfolder)
                        
                elif item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                    # Ajouter l'image
                    result['images'].append({
                        "name": item.name,
                        "path": str(item.relative_to(relative_to)),
                        "size": item.stat().st_size
                    })
        
        except PermissionError:
            print(f"Permission refusée pour: {folder_path}")
        
        return result
    
    structure = scan_folder(base_path, base_path.parent)
    
    return structure

def main():
    """Fonction principale"""
    
    # Accepter un chemin en argument
    base_path = sys.argv[1] if len(sys.argv) > 1 else None
    structure = scan_images_directory(base_path)
    
    # Déterminer où sauvegarder le fichier
    if base_path:
        output_dir = Path(base_path).parent
    else:
        # Sauvegarder dans frontend/
        current_dir = Path(__file__).parent.absolute()
        if current_dir.name == 'backend':
            output_dir = current_dir.parent / 'frontend'
        else:
            output_dir = current_dir / 'frontend'
    
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'gallery-structure.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    # Compter le total d'images
    def count_images(node):
        total = len(node.get('images', []))
        for folder in node.get('folders', []):
            total += count_images(folder)
        return total

if __name__ == "__main__":
    main()