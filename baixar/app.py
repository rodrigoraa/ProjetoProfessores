import os
import re
import uuid
import threading
import time
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    jsonify,
    after_this_request,
)
import yt_dlp

app = Flask(__name__)

# Configurações
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def cleanup_file(filepath, delay=600):
    """Remove o arquivo após 10 minutos para economizar espaço no servidor."""

    def remove():
        time.sleep(delay)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Arquivo removido: {filepath}")

    threading.Thread(target=remove).start()


def get_video_info(url):
    """Extrai metadados sem baixar o vídeo."""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "Video"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration_string"),
                "id": info.get("id"),
            }
        except Exception:
            return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/info", methods=["POST"])
def info():
    """Rota para o professor ver o que vai baixar antes de processar."""
    url = request.json.get("url")
    data = get_video_info(url)
    if data:
        return jsonify(data)
    return jsonify({"error": "URL inválida ou vídeo indisponível"}), 400


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    format_type = request.form.get("format", "mp4")  # mp4 ou mp3

    # Gerar nome único para evitar conflito entre professores
    unique_id = str(uuid.uuid4())[:8]

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s_{unique_id}.%(ext)s",
        "noplaylist": True,
        "ffmpeg_location": "/usr/bin/ffmpeg",
    }

    if format_type == "mp3":
        ydl_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        )

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            # Se for mp3, o yt-dlp muda a extensão no final, precisamos ajustar o path
            if format_type == "mp3":
                file_path = os.path.splitext(file_path)[0] + ".mp3"

        cleanup_file(file_path)  # Agenda a limpeza
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Erro no processamento: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True)
