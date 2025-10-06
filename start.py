#!/usr/bin/env python3
"""
Script de lancement depuis la racine du projet
Usage: python3 start.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    # S'assurer qu'on est dans la racine du projet
    root_dir = Path(__file__).parent.absolute()
    os.chdir(root_dir)
    
    # Charger les variables d'environnement depuis la racine
    load_dotenv()
    
    # Vérifier que les fichiers requis existent
    required_files = ['backend/back.py', 'frontend/index.html']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Fichiers manquants : {', '.join(missing_files)}")
        print(f"Répertoire courant : {os.getcwd()}")
        sys.exit(1)
    
    print("Démarrage de l'application depuis la racine...")
    print(f"Répertoire de travail : {os.getcwd()}")
    
    backend_path = os.path.join(root_dir, 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, str(backend_path))
    

    try:
        from backend.back import app, PORT, DEBUG_MODE
        print(f"Application disponible sur : http://localhost:{PORT}")
        
        if DEBUG_MODE:
            print("Mode développement activé")
        else:
            print("Mode production activé")
        
        # Démarrer l'application depuis la racine
        app.run(debug=DEBUG_MODE, port=PORT, host='0.0.0.0')
        
    except ImportError as e:
        print(f"Erreur d'import : {e}")
        print("Vérifiez que back.py existe dans le dossier backend/")
        sys.exit(1)

if __name__ == '__main__':
    main()