#!/usr/bin/env python3
"""
Script de lancement depuis la racine du projet
Usage: python3 start.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def generate_team_structure():
    """Génère la structure de l'équipe depuis team-profiles.json"""
    try:
        backend_path = Path(__file__).parent / 'backend'
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from generate_team_gallery import generate_team_structure, merge_with_existing_gallery
        import json
        
        root_dir = Path(__file__).parent.absolute()
        profiles_file = root_dir / 'team-profiles.json'
        
        # Vérifier si le fichier existe
        if not profiles_file.exists():
            #print("Fichier team-profiles.json non trouvé - structure d'équipe non générée")
            return False
        
        # Générer la structure
        team_structure = generate_team_structure()
        
        # Fusionner avec la galerie existante
        gallery = merge_with_existing_gallery(team_structure)
        
        # Sauvegarder
        output_file = root_dir / 'frontend' / 'gallery-structure.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(gallery, f, indent=2, ensure_ascii=False)
        
        # Compter les membres
        years_count = len(team_structure['folders'][0]['folders'])
        instruments_count = len(team_structure['folders'][1]['folders'])
        
        #print(f"Structure d'équipe générée : {years_count} années, {instruments_count} instruments")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la génération de l'équipe : {e}")
        import traceback
        traceback.print_exc()
        return False

def scan_gallery_images():
    """Scanne le dossier images et génère la structure JSON pour la galerie"""
    try:
        backend_path = Path(__file__).parent / 'backend'
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from scan_images import scan_images_directory
        
        root_dir = Path(__file__).parent.absolute()
        structure = scan_images_directory(str(root_dir / 'images' / 'public'))
        
        output_file = root_dir / 'frontend' / 'gallery-structure.json'
        import json
        
        existing_structure = {}
        team_photos = {}
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_structure = json.load(f)
                    team_photos = existing_structure.get('team_photos', {})
            except:
                pass
        
        if 'folders' in existing_structure:
            team_folder = next((f for f in existing_structure['folders'] if f['name'] == 'Nos équipes'), None)
            if team_folder:
                structure['folders'].insert(0, team_folder)
        if team_photos:
            structure['team_photos'] = team_photos
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        def count_images(node):
            total = len(node.get('images', []))
            for folder in node.get('folders', []):
                total += count_images(folder)
            return total
        
        total_images = count_images(structure)+1
        #print(f"Galerie scannée : {total_images} images trouvées")
        return True
        
    except Exception as e:
        #print(f"Erreur lors du scan de la galerie : {e}")
        #print("La galerie pourrait ne pas s'afficher correctement")
        return False

def main():
    root_dir = Path(__file__).parent.absolute()
    os.chdir(root_dir)
    load_dotenv()
    
    required_files = ['backend/back.py', 'frontend/index.html']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        #print(f"Fichiers manquants : {', '.join(missing_files)}")
        #print(f"Répertoire courant : {os.getcwd()}")
        sys.exit(1)
    
    #print("Initialisation du site OrchestraKot...")
    #print("-" * 50)
    
    # 1. Générer la structure de l'équipe
    #print("\nGénération de la structure d'équipe...")
    team_success = generate_team_structure()
    
    # 2. Scanner la galerie
    #print("\nScan de la galerie d'images...")
    gallery_success = scan_gallery_images()
    
    #print("\n" + "-" * 50)
    #if team_success and gallery_success:
        #print("Initialisation terminée avec succès!")
    #else:
        #print("Initialisation terminée avec des avertissements")
    
    backend_path = os.path.join(root_dir, 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    try:
        from backend.back import app, PORT, DEBUG_MODE
        
        #print("\nDémarrage du serveur...")
        #if DEBUG_MODE:
            #print("Mode développement activé")
        #else:
            #print("Mode production activé")
        
        #print(f"Serveur accessible sur : http://localhost:{PORT}")
        #print("\nConseil : Pour mettre à jour la galerie ou l'équipe, relancez simplement ce script")
        #print("Appuyez sur Ctrl+C pour arrêter le serveur\n")
        
        # Démarrer l'application depuis la racine
        app.run(debug=DEBUG_MODE, port=PORT, host='0.0.0.0')
        
    except ImportError as e:
        #print(f"Erreur d'import : {e}")
        #print("Vérifiez que back.py existe dans le dossier backend/")
        sys.exit(1)
    except KeyboardInterrupt:
        #print("\n\n⏹️  Arrêt du serveur...")
        sys.exit(0)

if __name__ == '__main__':
    main()