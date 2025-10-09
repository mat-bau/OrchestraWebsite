from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv
import json
#from scheduler_repetition import RepetitionScheduler
from scheduler import OptimizedRepetitionScheduler
import traceback

# Charger les variables d'environnement
load_dotenv()

# Déterminer les chemins absolus
BACKEND_DIR = Path(__file__).parent.absolute()
ROOT_DIR = Path(os.getcwd()).absolute()
DATA_DIR = ROOT_DIR / "data-planifier"

# Créer l'app Flask avec les bons chemins
app = Flask(__name__, 
           static_folder=str(ROOT_DIR / 'frontend'), 
           static_url_path='')

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5050')
# Configuration Flask
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
if DEBUG_MODE:
    CORS(app, resources={r"/*": {"origins": "*"}})
else:
    CORS(app, resources={r"/*": {"origins": BASE_URL}}) 



PORT = int(os.getenv('PORT', 5050))

# Créer les dossiers nécessaires
UPLOAD_FOLDER = DATA_DIR / "uploads"
EXPORTS_FOLDER = DATA_DIR / "exports"
GENERATED_FILE_PATH = None

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORTS_FOLDER, exist_ok=True)

# Route pour servir le frontend
@app.route('/')
def serve_frontend():
    """Sert le fichier index.html du frontend"""
    try:
        index_path = ROOT_DIR / 'frontend' / 'index.html'
        if index_path.exists():
            return send_file(str(index_path))
        else:
            return f"Frontend introuvable. Chemin recherché: {index_path}", 404
    except Exception as e:
        return f"Erreur lors du chargement du frontend: {str(e)}", 500

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Sert les images depuis le dossier images/"""
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    return send_from_directory(images_dir, filename)

# Si vous avez besoin de servir aussi depuis un sous-dossier public spécifique
@app.route('/public/<path:filename>')
def serve_public_image(filename):
    """Sert les images depuis le dossier images/public/"""
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'public')
    return send_from_directory(images_dir, filename)

@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        dispo_file = request.files['disponibilites']
        repart_file = request.files['repartition']
        maybe_penalty = int(request.form['maybe_penalty'])
        max_load = int(request.form['max_load'])
        load_penalty = int(request.form['load_penalty'])
        group_bonus = int(request.form['group_bonus'])
        seuil_absence = int(request.form.get("seuil_absence", 0))
        mode_absence = request.form.get("mode_absence", "strict")
        timeout_limit = int(request.form.get("timeout_limit", 120))
        # NOUVEAU : récupération des créneaux spéciaux
        creneaux_speciaux_json = request.form.get("creneaux_speciaux", "[]")
        creneaux_speciaux = json.loads(creneaux_speciaux_json) if creneaux_speciaux_json else []
        seuil_absence_special = int(request.form.get("seuil_absence_creneau_special", 5))
       

        dispo_path = UPLOAD_FOLDER / dispo_file.filename
        repart_path = UPLOAD_FOLDER / repart_file.filename
        
        dispo_file.save(str(dispo_path))
        repart_file.save(str(repart_path))

        print("🧾 Params :", maybe_penalty, max_load, load_penalty, group_bonus, 
              mode_absence, seuil_absence, f"timeout={timeout_limit}s")

        
        
        planner = OptimizedRepetitionScheduler(
            str(repart_path), str(dispo_path),
            maybe_penalty, max_load, load_penalty, group_bonus,
            mode_absence, seuil_absence,
            creneaux_speciaux=creneaux_speciaux,
            seuil_absence_creneau_special=seuil_absence_special,
            generation_time_limit=timeout_limit
        )
        planner.generer_planning()
        
        global GENERATED_FILE_PATH
        
        GENERATED_FILE_PATH = planner.export_planning(str(EXPORTS_FOLDER), base_filename="planning")
        
        json_data = planner.get_json_data()
        return jsonify(json_data)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/download')
def download():
    try:
        if GENERATED_FILE_PATH and os.path.exists(GENERATED_FILE_PATH):
            return send_file(GENERATED_FILE_PATH, as_attachment=True)
        else:
            return jsonify({"error": "Fichier introuvable"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    """Point de contrôle santé pour debug"""
    return jsonify({
        'status': 'OK',
        'root_dir': str(ROOT_DIR),
        'backend_dir': str(BACKEND_DIR),
        'data_dir': str(DATA_DIR),
        'upload_folder': str(UPLOAD_FOLDER),
        'exports_folder': str(EXPORTS_FOLDER),
        'debug': DEBUG_MODE,
        'frontend_exists': (ROOT_DIR / 'frontend' / 'index.html').exists(),
        'images_folder_exists': (ROOT_DIR / 'images').exists()
    })

if __name__ == '__main__':
    host = '127.0.0.1' if not DEBUG_MODE else '0.0.0.0'
    app.run(debug=DEBUG_MODE, port=PORT, host=host)