import json
import os
import random
from flask import Flask, send_from_directory, jsonify, request
from pathlib import Path

from db import init_db, insert_anxiety_entry, get_statistics

BASE_DIR = Path(__file__).parent.parent

app = Flask(__name__, 
            static_folder=str(BASE_DIR / "html"),
            static_url_path="/")

def _get_random_exercise():
    content_dir = BASE_DIR / "content"
    
    try:
        files = [f for f in os.listdir(content_dir) if os.path.isfile(os.path.join(content_dir, f))]
        
        if not files:
            return None
        
        random_file = random.choice(files)
        file_path = os.path.join(content_dir, random_file)
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
            
    except Exception as e:
        print(f"Error getting random exercise: {e}")
        return None


def _render_page(file):
    """Render an HTML page from the html directory."""
    try:
        html_path = BASE_DIR / "html" / f"{file}.html"
        return send_from_directory(str(BASE_DIR / "html"), f"{file}.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route("/")
@app.route("/button")
def button():
    return _render_page("button")


@app.route("/dashboard")
def dashboard():
    return _render_page("dashboard")


@app.route("/form")
def form():
    return _render_page("form")


@app.route("/exercise")
def exercise():
    return _render_page("exercise")


@app.route("/random_exercise")
def random_exercise():
    exercise_html = _get_random_exercise()
    if exercise_html:
        return jsonify({"exercise": exercise_html})
    else:
        return jsonify({"error": "No exercises available"}), 404


@app.route("/api/stats")
def api_stats():
    stats = get_statistics()
    return jsonify(stats)


@app.route("/button", methods=["POST"])
def button_post():
    return jsonify({"message": "Button clicked"})


@app.route("/form", methods=["POST"])
def form_post():
    try:
        data = request.get_json(force=True)
        
        if not data:
            return jsonify({"error": "Solicitud inválida"}), 400
        
        anxiety_type = data.get("type", "")
        description = data.get("description", "")
        insert_anxiety_entry(anxiety_type, description)
        return jsonify({"message": "Form submitted", "data": data})

    except Exception as e:
        return jsonify({"error": "Solicitud inválida"}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Página no encontrada"}), 404


if __name__ == "__main__":
    init_db()
    print("Database initialized")
    
    port = int(os.environ.get("PORT", 8000))
    print(f"Server starting on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
