import os, shutil, subprocess, tempfile
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
ALLOWED_HOSTS = ("youtube.com", "www.youtube.com", "youtu.be", "music.youtube.com")

def valid_url(value):
    return value.startswith(("https://", "http://")) and any(host in value for host in ALLOWED_HOSTS)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/convert")
def convert():
    data = request.get_json(silent=True) or {}
    url, quality = str(data.get("url", "")).strip(), str(data.get("quality", "192"))
    if not valid_url(url): return jsonify(error="Insira um link válido do YouTube."), 400
    if quality not in {"128", "192", "320"}: quality = "192"
    folder = tempfile.mkdtemp(prefix="onda-")
    try:
        subprocess.run(["yt-dlp", "--no-playlist", "-x", "--audio-format", "vorbis", "--audio-quality", f"{quality}K", "-o", f"{folder}/audio.%(ext)s", url], check=True, capture_output=True, text=True, timeout=180)
        path = f"{folder}/audio.ogg"
        if not os.path.exists(path): return jsonify(error="A conversão não gerou um arquivo OGG."), 500
        response = send_file(path, as_attachment=True, download_name="audio.ogg", mimetype="audio/ogg")
        response.call_on_close(lambda: shutil.rmtree(folder, ignore_errors=True))
        return response
    except subprocess.TimeoutExpired:
        shutil.rmtree(folder, ignore_errors=True); return jsonify(error="A conversão demorou demais."), 504
    except subprocess.CalledProcessError:
        shutil.rmtree(folder, ignore_errors=True); return jsonify(error="Não foi possível converter este vídeo."), 422
    except Exception:
        shutil.rmtree(folder, ignore_errors=True); return jsonify(error="Erro inesperado no servidor."), 500

if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
