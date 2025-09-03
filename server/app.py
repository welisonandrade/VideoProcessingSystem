import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import database as db
import video_processor as vp

# --- Configurações ---
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'media')
INCOMING_FOLDER = os.path.join(MEDIA_ROOT, 'incoming')
VIDEOS_FOLDER = os.path.join(MEDIA_ROOT, 'videos')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

app = Flask(__name__)
app.config['INCOMING_FOLDER'] = INCOMING_FOLDER
app.config['VIDEOS_FOLDER'] = VIDEOS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Limite de 100 MB

# Garante que as pastas existem
os.makedirs(INCOMING_FOLDER, exist_ok=True)
os.makedirs(VIDEOS_FOLDER, exist_ok=True)

# Inicializa o banco de dados na primeira execução
with app.app_context():
    db.init_db()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Página principal que exibe os vídeos processados."""
    videos = db.get_all_videos()
    return render_template('index.html', videos=videos)


@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    filter_name = request.form.get('filter', 'none')

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Arquivo inválido ou extensão não permitida"}), 400

    # 1. Salva o arquivo temporariamente
    original_filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['INCOMING_FOLDER'], original_filename)
    file.save(temp_path)

    # 2. Prepara a estrutura de pastas final
    now = datetime.now()
    video_uuid = str(uuid.uuid4())
    year, month, day = str(now.year), f"{now.month:02d}", f"{now.day:02d}"

    video_dir = os.path.join(app.config['VIDEOS_FOLDER'], year, month, day, video_uuid)
    original_dir = os.path.join(video_dir, 'original')
    processed_dir = os.path.join(video_dir, 'processed', filter_name)
    thumbs_dir = os.path.join(video_dir, 'thumbs')

    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(thumbs_dir, exist_ok=True)

    # 3. Move o arquivo original para o destino final
    original_ext = original_filename.rsplit('.', 1)[1].lower()
    final_original_path = os.path.join(original_dir, f"video.{original_ext}")
    os.rename(temp_path, final_original_path)

    # 4. Gera thumbnail e extrai metadados
    thumb_path = os.path.join(thumbs_dir, 'frame_0001.jpg')
    success, meta = vp.generate_thumbnail(final_original_path, thumb_path)
    if not success:
        # Lógica para lidar com falha na geração do thumbnail
        return jsonify({"error": "Falha ao processar o vídeo"}), 500

    width, height, fps, frame_count = meta
    duration_sec = frame_count / fps if fps > 0 else 0

    # 5. Aplica o filtro
    final_processed_path = os.path.join(processed_dir, f"video.{original_ext}")
    vp.apply_filter_to_video(final_original_path, final_processed_path, filter_name)

    # 6. Salva metadados no banco de dados
    video_data = {
        'id': video_uuid,
        'original_name': original_filename,
        'original_ext': original_ext,
        'mime_type': file.mimetype,
        'size_bytes': os.path.getsize(final_original_path),
        'duration_sec': duration_sec,
        'fps': fps,
        'width': width,
        'height': height,
        'filter': filter_name,
        'created_at': now.isoformat(),
        'path_original': os.path.relpath(final_original_path, MEDIA_ROOT).replace('\\', '/'),
        'path_processed': os.path.relpath(final_processed_path, MEDIA_ROOT).replace('\\', '/'),
        'path_thumb': os.path.relpath(thumb_path, MEDIA_ROOT).replace('\\', '/')
    }
    db.add_video_record(video_data)

    # 7. (Opcional) Salva meta.json
    with open(os.path.join(video_dir, 'meta.json'), 'w') as f:
        json.dump(video_data, f, indent=4)

    return jsonify({"message": "Vídeo enviado e processado com sucesso!", "video_id": video_uuid}), 201


@app.route('/videos', methods=['GET'])
def get_videos():
    """Endpoint da API para listar todos os vídeos."""
    videos = db.get_all_videos()
    return jsonify(videos)


@app.route('/media/<path:filename>')
def media_files(filename):
    """Serve os arquivos de mídia (vídeos, thumbnails)."""
    return send_from_directory(MEDIA_ROOT, filename)


if __name__ == '__main__':
    # Use host='0.0.0.0' para ser acessível na sua rede local
    app.run(host='0.0.0.0', port=5000, debug=True)