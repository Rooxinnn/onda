from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/download")
def download():
    data = request.get_json(silent=True) or {}
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    try:
        result = subprocess.run(
            [sys.executable, "download.py", url],
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            return jsonify({
                "error": "Falha no download",
                "details": result.stderr or result.stdout
            }), 500

        return jsonify({"message": result.stdout})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "O download excedeu o tempo limite."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
