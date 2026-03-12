import os
import uuid
import threading
import time
from flask import Blueprint, render_template, request, send_file, jsonify
from flask_login import login_required, current_user
import yt_dlp

dl_bp = Blueprint("dl", __name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Dicionário global para guardar o progresso de cada download
progress_data = {}


def cleanup_file(filepath, delay=600):
    """Remove o arquivo após o tempo definido (padrão 10 min)."""

    def remove():
        time.sleep(delay)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Arquivo removido para poupar espaço: {filepath}")

    threading.Thread(target=remove).start()


# --- NOVA LÓGICA DE PROGRESSO ---


def get_progress_hook(task_id):
    """Hook que o yt-dlp chama para atualizar o progresso"""

    def hook(d):
        if d["status"] == "downloading":
            # Captura a percentagem atual
            percent = d.get("_percent_str", "0%").strip()
            progress_data[task_id] = {"status": "A transferir...", "percent": percent}
        elif d["status"] == "finished":
            progress_data[task_id] = {
                "status": "A converter formato...",
                "percent": "100%",
            }

    return hook


def process_download(task_id, url, format_type):
    """Função que corre em segundo plano para não bloquear o servidor"""
    progress_data[task_id] = {
        "status": "A iniciar...",
        "percent": "0%",
        "file": None,
        "error": None,
    }

    try:
        file_path_template = os.path.join(
            DOWNLOAD_FOLDER, f"{task_id}_%(title)s.%(ext)s"
        )
        ydl_opts = {
            "outtmpl": file_path_template,
            "progress_hooks": [get_progress_hook(task_id)],  # Liga o hook de progresso
            "quiet": True,
            "no_warnings": True,
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
        else:
            ydl_opts.update(
                {
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                }
            )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if format_type == "mp3" and not file_path.endswith(".mp3"):
                file_path = os.path.splitext(file_path)[0] + ".mp3"

        progress_data[task_id]["status"] = "Concluído"
        progress_data[task_id]["file"] = file_path
        cleanup_file(file_path)

    except Exception as e:
        progress_data[task_id] = {"status": "Erro", "error": str(e)}


@dl_bp.route("/start-download", methods=["POST"])
@login_required
def start_download():
    """Inicia a tarefa em segundo plano e devolve um ID"""
    data = request.json
    url = data.get("url")
    format_type = data.get("format", "mp4")

    if not url:
        return jsonify({"error": "URL inválida"}), 400

    task_id = str(uuid.uuid4())[:8]
    # Inicia a thread para não bloquear a resposta
    threading.Thread(target=process_download, args=(task_id, url, format_type)).start()

    return jsonify({"task_id": task_id})


@dl_bp.route("/progress/<task_id>")
@login_required
def get_progress(task_id):
    """Devolve o estado atual do download"""
    return jsonify(
        progress_data.get(task_id, {"status": "A aguardar...", "percent": "0%"})
    )


@dl_bp.route("/get-file/<task_id>")
@login_required
def get_file(task_id):
    """Entrega o ficheiro ao utilizador quando concluído"""
    data = progress_data.get(task_id)
    if not data or not data.get("file"):
        return "Arquivo não encontrado", 404
    return send_file(data["file"], as_attachment=True)

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
