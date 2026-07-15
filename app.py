import os
import subprocess
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# WICHTIG: Erlaubt deiner GitHub Page (andere Domain) den Zugriff auf diese API
CORS(app, resources={r"/*": {"origins": "*"}})

VALID_STYLES = ['google', 'llvm', 'chromium', 'mozilla', 'webkit']

@app.route('/format', methods=['POST'])
def format_code():
    data = request.json or {}
    code = data.get('code', '')
    language = data.get('language', 'cpp').lower().strip()
    style = data.get('style', 'google').lower().strip()

    if not code.strip():
        return jsonify({"error": "Kein Code zur Formatierung übermittelt"}), 400

    if style not in VALID_STYLES:
        style = 'google'

    # Dateiendung bestimmen, damit clang-format den korrekten Parser (C++ oder Java) wählt
    suffix = ".cpp" if language == "cpp" else ".java"
    
    unique_id = uuid.uuid4().hex
    temp_filename = f"/tmp/input_{unique_id}{suffix}"

    try:
        # Code temporär wegschreiben
        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(code)

        # Befehl zusammenbauen: clang-format -style=[Style] [Datei]
        cmd = [
            "clang-format",
            f"-style={style}",
            temp_filename
        ]

        # Prozess asynchron ausführen
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

        if process.returncode != 0:
            raise Exception(process.stderr)

        formatted_code = process.stdout

        return jsonify({
            "success": True,
            "formatted_code": formatted_code
        })

    except Exception as e:
        return jsonify({"error": f"Formatierungsfehler: {str(e)}"}), 500

    finally:
        # Temporäre Datei löschen
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == '__main__':
    app.run(port=8080)
