import os
import uuid
import threading
import time
from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user
import yt_dlp

dl_bp = Blueprint("dl", __name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def cleanup_file(filepath, delay=600):
    """Remove o arquivo após o tempo definido (padrão 10 min)."""

    def remove():
        time.sleep(delay)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Arquivo removido para poupar espaço: {filepath}")

    threading.Thread(target=remove).start()


@dl_bp.route("/ferramentas")
@login_required
def ferramentas():
    return render_template("downloader.html", nome=current_user.nome)


@dl_bp.route("/download", methods=["POST"])
@login_required
def download_video():
    url = request.form.get("url")
    format_type = request.form.get("format", "mp4")  # Pega a escolha do HTML

    if not url:
        return "URL inválida", 400

    unique_id = str(uuid.uuid4())[:8]

    # Configuração base
    ydl_opts = {
        # 'restrictfilenames': True -> Remove espaços e caracteres especiais do nome do ficheiro
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s_{unique_id}.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
    }

    # Se o professor escolher MP3
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
    else:
        # Se escolher MP4 (Vídeo)
        ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            # Ajuste de extensão para MP3 caso o post-processor tenha mudado
            if format_type == "mp3" and not file_path.endswith(".mp3"):
                file_path = os.path.splitext(file_path)[0] + ".mp3"

        cleanup_file(file_path)  # Agenda a remoção
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Erro no processamento: {str(e)}", 500


@dl_bp.route("/video-info", methods=["POST"])
@login_required
def video_info():
    url = request.json.get("url")
    if not url:
        return {"error": "URL vazia"}, 400

    ydl_opts = {"quiet": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration_string"),
            }
    except Exception as e:
        return {"error": str(e)}, 500


def limpar_pasta_antiga():
    agora = time.time()
    for f in os.listdir(DOWNLOAD_FOLDER):
        caminho = os.path.join(DOWNLOAD_FOLDER, f)
        # Se o arquivo tem mais de 1 hora (3600 segundos)
        if os.stat(caminho).st_mtime < agora - 3600:
            try:
                os.remove(caminho)
            except:
                pass


@dl_bp.route("/ferramentas")
@login_required
def ferramentas():
    limpar_pasta_antiga()  # Limpa o lixo antes de mostrar a página
    return render_template("downloader.html", nome=current_user.nome)
