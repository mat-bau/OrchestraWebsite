from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
import time
import traceback
from pathlib import Path
from dotenv import load_dotenv
from scheduler import OptimizedRepetitionScheduler

load_dotenv()
BACKEND_DIR = Path(__file__).parent.absolute()
ROOT_DIR    = Path(os.getcwd()).absolute()
DATA_DIR    = ROOT_DIR / "data-planifier"

app = Flask(__name__,
            static_folder=str(ROOT_DIR / 'frontend'),
            static_url_path='')

BASE_URL    = os.getenv('BASE_URL', 'http://localhost:5050')
DEBUG_MODE  = os.getenv('DEBUG', 'False').lower() == 'true'
PORT        = int(os.getenv('PORT', 5050))

if DEBUG_MODE:
    CORS(app, resources={r"/*": {"origins": "*"}})
else:
    CORS(app, resources={r"/*": {"origins": BASE_URL}})

UPLOAD_FOLDER  = DATA_DIR / "uploads"
EXPORTS_FOLDER = DATA_DIR / "exports"

os.makedirs(UPLOAD_FOLDER,  exist_ok=True)
os.makedirs(EXPORTS_FOLDER, exist_ok=True)

# Track the latest generated file path per run_id
_run_exports: dict = {}


# ── Static routes ──────────────────────────────────────────

@app.route('/')
def serve_frontend():
    index_path = ROOT_DIR / 'frontend' / 'index.html'
    if index_path.exists():
        return send_file(str(index_path))
    return f"Frontend introuvable. Chemin: {index_path}", 404

@app.route('/images/<path:filename>')
def serve_image(filename):
    images_dir = ROOT_DIR / 'images'
    return send_from_directory(str(images_dir), filename)

@app.route('/public/<path:filename>')
def serve_public_image(filename):
    images_dir = ROOT_DIR / 'images' / 'public'
    return send_from_directory(str(images_dir), filename)

@app.route('/team-profiles.json')
def serve_team_profiles():
    path = ROOT_DIR / 'team-profiles.json'
    if path.exists():
        return send_file(str(path))
    return jsonify({"error": "team-profiles.json introuvable"}), 404

@app.route('/data/<path:filename>')
def serve_data_file(filename):
    """Serve files from frontend/data/ (site-config.json, gallery-structure.json, etc.)"""
    data_dir = ROOT_DIR / 'frontend' / 'data'
    return send_from_directory(str(data_dir), filename)


# ── Helpers ────────────────────────────────────────────────

def _parse_params(form):
    return dict(
        maybe_penalty   = int(form.get('maybe_penalty', 10)),
        max_load        = int(form.get('max_load', 3)),
        load_penalty    = int(form.get('load_penalty', 50)),
        group_bonus     = int(form.get('group_bonus', 20)),
        seuil_absence   = int(form.get('seuil_absence', 0)),
        mode_absence    = form.get('mode_absence', 'flexible'),
        timeout_limit   = int(form.get('timeout_limit', 120)),
        creneaux_speciaux         = json.loads(form.get('creneaux_speciaux', '[]') or '[]'),
        seuil_absence_creneau_special = int(form.get('seuil_absence_creneau_special', 5)),
        forced_assignments        = json.loads(form.get('forced_assignments', '{}') or '{}'),
    )

def _run_planner(repart_path, dispo_path, params):
    planner = OptimizedRepetitionScheduler(
        str(repart_path), str(dispo_path),
        params['maybe_penalty'], params['max_load'],
        params['load_penalty'], params['group_bonus'],
        params['mode_absence'], params['seuil_absence'],
        creneaux_speciaux=params['creneaux_speciaux'],
        seuil_absence_creneau_special=params['seuil_absence_creneau_special'],
        generation_time_limit=params['timeout_limit'],
        forced_assignments=params['forced_assignments'],
    )
    planner.generer_planning()
    return planner


# ── API routes ─────────────────────────────────────────────

@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        dispo_file  = request.files['disponibilites']
        repart_file = request.files['repartition']
        params      = _parse_params(request.form)

        # Save with a unique run_id so /api/replan can reuse them
        run_id = str(uuid.uuid4())
        dispo_path  = UPLOAD_FOLDER / f"{run_id}_dispo.xlsx"
        repart_path = UPLOAD_FOLDER / f"{run_id}_repart.xlsx"
        dispo_file.save(str(dispo_path))
        repart_file.save(str(repart_path))

        planner = _run_planner(repart_path, dispo_path, params)

        export_path = planner.export_planning(str(EXPORTS_FOLDER), base_filename=f"planning_{run_id}")
        _run_exports[run_id] = export_path

        data = planner.get_json_data()
        data['run_id'] = run_id
        return jsonify(data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/replan', methods=['POST'])
def replan():
    """Re-run the solver with forced assignments using previously uploaded files."""
    try:
        run_id = request.form.get('run_id')
        if not run_id:
            return jsonify({"error": "run_id manquant"}), 400

        dispo_path  = UPLOAD_FOLDER / f"{run_id}_dispo.xlsx"
        repart_path = UPLOAD_FOLDER / f"{run_id}_repart.xlsx"

        if not dispo_path.exists() or not repart_path.exists():
            return jsonify({"error": "Fichiers introuvables pour ce run_id. Veuillez re-uploader."}), 404

        params = _parse_params(request.form)
        planner = _run_planner(repart_path, dispo_path, params)

        export_path = planner.export_planning(str(EXPORTS_FOLDER), base_filename=f"planning_{run_id}")
        _run_exports[run_id] = export_path

        data = planner.get_json_data()
        data['run_id'] = run_id
        return jsonify(data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/download')
def download():
    run_id = request.args.get('run_id')
    path = _run_exports.get(run_id) if run_id else None
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    return jsonify({"error": "Fichier introuvable"}), 404


@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'OK',
        'root_dir': str(ROOT_DIR),
        'debug': DEBUG_MODE,
        'frontend_exists': (ROOT_DIR / 'frontend' / 'index.html').exists(),
    })


if __name__ == '__main__':
    host = '127.0.0.1' if not DEBUG_MODE else '0.0.0.0'
    app.run(debug=DEBUG_MODE, port=PORT, host=host)
