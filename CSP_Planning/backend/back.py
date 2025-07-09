from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from scheduler_repetition import RepetitionScheduler
import traceback


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8000"}})

UPLOAD_FOLDER = "uploads"
RESULT_FILE = "planning_repetitions.xlsx"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        print("📥 Requête reçue !")
        dispo_file = request.files['disponibilites']
        repart_file = request.files['repartition']
        maybe_penalty = int(request.form['maybe_penalty'])
        max_load = int(request.form['max_load'])
        load_penalty = int(request.form['load_penalty'])
        group_bonus = int(request.form['group_bonus'])
        seuil_absence = int(request.form.get("seuil_absence", 0))
        mode_absence = request.form.get("mode_absence", "fixed")


        dispo_path = os.path.join(UPLOAD_FOLDER, dispo_file.filename)
        repart_path = os.path.join(UPLOAD_FOLDER, repart_file.filename)

        dispo_file.save(dispo_path)
        repart_file.save(repart_path) 
        print("🧾 Params :", maybe_penalty, max_load, load_penalty, group_bonus, mode_absence, seuil_absence)
        print("📂 Fichiers reçus :", dispo_file.filename, repart_file.filename)  # <-- LOG 3


        print("🔧 Instanciation du planner…")
        planner = RepetitionScheduler(
            repart_path, dispo_path,
            maybe_penalty, max_load, load_penalty, group_bonus,
            mode_absence, seuil_absence
        )
        print("✅ Planner instancié.")

        # 2) Génération
        print("⚙️  Lancement de generer_planning()…")
        planner.generer_planning()
        print("✅ generer_planning() terminé.")

        # 3) Export Excel
        print(f"💾 Export vers {RESULT_FILE} …")
        planner.export_planning(RESULT_FILE)
        print("✅ export_planning() terminé.")

        # 4) Sérialisation JSON
        print("🗜  Sérialisation JSON…")
        json_data = planner.get_json_data()
        print("✅ JSON prêt, on renvoie au front.")
        print("✅ Planning généré avec succès.")
        return jsonify(json_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/download', methods=['GET'])
def download():
    try:
        return send_file(RESULT_FILE, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5050)
