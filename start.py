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
            print("⚠️  Fichier team-profiles.json non trouvé - structure d'équipe non générée")
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
        
        print(f"✅ Structure d'équipe générée : {years_count} années, {instruments_count} instruments")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la génération de l'équipe : {e}")
        import traceback
        traceback.print_exc()
        return False

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
        structure = scan_images_directory(str(root_dir / 'images' / 'public'))
        
        # Sauvegarder dans frontend/
        output_file = root_dir / 'frontend' / 'gallery-structure.json'
        import json
        
        # Charger la structure existante si elle existe (pour garder l'équipe)
        existing_structure = {}
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_structure = json.load(f)
            except:
                pass
        if 'folders' in existing_structure:
            team_folder = next((f for f in existing_structure['folders'] if f['name'] == 'Nos équipes'), None)
            if team_folder:
                # Garder le dossier équipe en premier
                structure['folders'].insert(0, team_folder)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        def count_images(node):
            total = len(node.get('images', []))
            for folder in node.get('folders', []):
                total += count_images(folder)
            return total
        
        total_images = count_images(structure)
        print(f"Galerie scannée : {total_images} images trouvées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du scan de la galerie : {e}")
        print("⚠️  La galerie pourrait ne pas s'afficher correctement")
        return False

def main():
    root_dir = Path(__file__).parent.absolute()
    os.chdir(root_dir)
    load_dotenv()
    
    required_files = ['backend/back.py', 'frontend/index.html']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Fichiers manquants : {', '.join(missing_files)}")
        print(f"📁 Répertoire courant : {os.getcwd()}")
        sys.exit(1)
    
    print("🔄 Initialisation du site OrchestraKot...")
    print("-" * 50)
    
    # 1. Générer la structure de l'équipe
    print("\n📋 Génération de la structure d'équipe...")
    team_success = generate_team_structure()
    
    # 2. Scanner la galerie
    print("\n📸 Scan de la galerie d'images...")
    gallery_success = scan_gallery_images()
    
    print("\n" + "-" * 50)
    if team_success and gallery_success:
        print("✅ Initialisation terminée avec succès!")
    else:
        print("⚠️  Initialisation terminée avec des avertissements")
    
    backend_path = os.path.join(root_dir, 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    try:
        from backend.back import app, PORT, DEBUG_MODE
        
        print("\n🚀 Démarrage du serveur...")
        if DEBUG_MODE:
            print("🔧 Mode développement activé")
        else:
            print("🏭 Mode production activé")
        
        print(f"🌐 Serveur accessible sur : http://localhost:{PORT}")
        print("\n💡 Conseil : Pour mettre à jour la galerie ou l'équipe, relancez simplement ce script")
        print("⏹️  Appuyez sur Ctrl+C pour arrêter le serveur\n")
        
        # Démarrer l'application depuis la racine
        app.run(debug=DEBUG_MODE, port=PORT, host='0.0.0.0')
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("⚠️  Vérifiez que back.py existe dans le dossier backend/")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt du serveur...")
        sys.exit(0)

if __name__ == '__main__':
    main()