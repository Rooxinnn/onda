import os
import shutil
import subprocess
import tempfile

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ALLOWED_HOSTS = (
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "music.youtube.com",
)


def valid_youtube_url(value):
    return (
        value.startswith(("https://", "http://"))
        and any(host in value for host in ALLOWED_HOSTS)
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/convert")
def convert():
    data = request.get_json(silent=True) or {}

    url = str(data.get("url", "")).strip()
    quality = str(data.get("quality", "192"))

    if not valid_youtube_url(url):
        return jsonify(error="Insira um link válido do YouTube."), 400

    if quality not in {"128", "192", "320"}:
        quality = "192"

    folder = tempfile.mkdtemp(prefix="onda-")
    output = os.path.join(folder, "audio.%(ext)s")

    command = [
        "yt-dlp",
        "--no-playlist",
        "--extractor-args",
        "youtube:player_client=android",
        "--js-runtimes",
        "node",
        "-x",
        "--audio-format",
        "vorbis",
        "--audio-quality",
        f"{quality}K",
        "-o",
        output,
        url,
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )

        ogg_path = os.path.join(folder, "audio.ogg")

        if not os.path.exists(ogg_path):
            shutil.rmtree(folder, ignore_errors=True)
            return jsonify(
                error="A conversão não gerou um arquivo OGG."
            ), 500

        response = send_file(
            ogg_path,
            as_attachment=True,
            download_name="audio.ogg",
            mimetype="audio/ogg",
        )

        response.call_on_close(
            lambda: shutil.rmtree(folder, ignore_errors=True)
        )

        return response

    except subprocess.TimeoutExpired:
        shutil.rmtree(folder, ignore_errors=True)
        return jsonify(
            error="A conversão demorou demais e foi cancelada."
        ), 504

    except subprocess.CalledProcessError as error:
        shutil.rmtree(folder, ignore_errors=True)

        print("Erro do yt-dlp:")
        print(error.stderr)

        return jsonify(
            error="O YouTube não permitiu a conversão deste vídeo."
        ), 422

    except Exception as error:
        shutil.rmtree(folder, ignore_errors=True)

        print("Erro inesperado:")
        print(error)

        return jsonify(
            error="O servidor encontrou um erro inesperado."
        ), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
    )
