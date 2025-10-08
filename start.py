#!/usr/bin/env python3
"""
Script de lancement depuis la racine du projet
Usage: python3 start.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def scan_gallery_images():
    """Scanne le dossier images et génère la structure JSON pour la galerie"""
    try:
        # Importer et exécuter le scanner
        backend_path = Path(__file__).parent / 'backend'
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from scan_images import scan_images_directory
        
        # Scanner le dossier images
        root_dir = Path(__file__).parent.absolute()
        structure = scan_images_directory(str(root_dir / 'images'))
        
        # Sauvegarder dans frontend/
        output_file = root_dir / 'frontend' / 'gallery-structure.json'
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        # Compter les images
        def count_images(node):
            total = len(node.get('images', []))
            for folder in node.get('folders', []):
                total += count_images(folder)
            return total
        
        total_images = count_images(structure)
        print(f"Galerie scannée : {total_images} images trouvées")
        return True
        
    except Exception as e:
        print(f"Erreur lors du scan de la galerie : {e}")
        print("La galerie pourrait ne pas s'afficher correctement")
        return False

def main():
    root_dir = Path(__file__).parent.absolute()
    os.chdir(root_dir)
    load_dotenv()
    
    required_files = ['backend/back.py', 'frontend/index.html']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Fichiers manquants : {', '.join(missing_files)}")
        print(f"Répertoire courant : {os.getcwd()}")
        sys.exit(1)
    
    scan_gallery_images()
    backend_path = os.path.join(root_dir, 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    try:
        from backend.back import app, PORT, DEBUG_MODE
        
        if DEBUG_MODE:
            print("Mode développement activé")
        else:
            print("Mode production activé")
        
        print("Conseil : Pour mettre à jour la galerie, relancez simplement ce script")
        
        # Démarrer l'application depuis la racine
        app.run(debug=DEBUG_MODE, port=PORT, host='0.0.0.0')
        
    except ImportError as e:
        print(f"Erreur d'import : {e}")
        print("Vérifiez que back.py existe dans le dossier backend/")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
        sys.exit(0)

if __name__ == '__main__':
    main()