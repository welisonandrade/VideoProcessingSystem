import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

import database
import video_processor

app = Flask(__name__)

# Configurações de diretório
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media')
app.config['MEDIA_ROOT'] = MEDIA_ROOT

# Inicializa o banco de dados
database.init_db()


# Rota para a GUI web do servidor
@app.route('/')
def index():
    videos = database.get_all_videos()
    return render_template('index.html', videos=videos)


# Rota para servir os arquivos de mídia (vídeos, thumbnails)
@app.route('/media/<path:filepath>')
def serve_media(filepath):
    # ANTES (CÓDIGO ATUAL):
    # return send_from_directory(app.config['MEDIA_ROOT'], filepath)

    # DEPOIS (NOVO CÓDIGO):
    # Primeiro, obtemos o objeto de resposta da função send_from_directory
    response = send_from_directory(app.config['MEDIA_ROOT'], filepath)

    # Agora, modificamos o cabeçalho para instruir o navegador a exibir inline
    response.headers['Content-Disposition'] = 'inline'

    # Retornamos a resposta modificada
    return response


# Rota para o histórico de vídeos (API para o cliente)
@app.route('/history')
def get_history():
    videos = database.get_all_videos()
    return jsonify(videos)


# Rota de upload de vídeo
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "Nenhum arquivo de vídeo enviado"}), 400

    video_file = request.files['video']
    filter_name = request.form.get('filter', 'grayscale')

    if video_file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    # 1. Gera IDs e prepara a estrutura de pastas
    video_uuid = str(uuid.uuid4())
    now = datetime.now()
    original_name, original_ext = os.path.splitext(secure_filename(video_file.filename))

    # Estrutura: /media/videos/yyyy/mm/dd/{uuid}/
    video_dir = os.path.join('videos', now.strftime('%Y/%m/%d'), video_uuid)
    full_video_dir = os.path.join(MEDIA_ROOT, video_dir)
    os.makedirs(full_video_dir, exist_ok=True)

    # 2. Salva o vídeo original
    path_original = os.path.join(video_dir, f'original{original_ext}')
    video_file.save(os.path.join(MEDIA_ROOT, path_original))

    # 3. Processa o vídeo
    #path_processed = os.path.join(video_dir, f'processed_{filter_name}{original_ext}')
    #path_processed = os.path.join(video_dir, f'processed_{filter_name}{original_ext}')
    path_processed = os.path.join(video_dir, f'processed_{filter_name}.avi')
    try:
        video_processor.process_video(
            os.path.join(MEDIA_ROOT, path_original),
            os.path.join(MEDIA_ROOT, path_processed),
            filter_name
        )
    except Exception as e:
        return jsonify({"error": f"Erro no processamento: {e}"}), 500

    # 4. Gera thumbnail
    path_thumbnail = os.path.join(video_dir, 'thumbnail.jpg')
    video_processor.generate_thumbnail(
        os.path.join(MEDIA_ROOT, path_original),
        os.path.join(MEDIA_ROOT, path_thumbnail)
    )

    # 5. Extrai metadados e salva no banco
    metadata = video_processor.extract_metadata(os.path.join(MEDIA_ROOT, path_original))

    video_data = {
        'id': video_uuid,
        'original_name': original_name,
        'original_ext': original_ext,
        'mime_type': video_file.mimetype,
        'size_bytes': os.path.getsize(os.path.join(MEDIA_ROOT, path_original)),
        'duration_sec': metadata['duration_sec'],
        'fps': metadata['fps'],
        'width': metadata['width'],
        'height': metadata['height'],
        'filter': filter_name,
        'created_at': now.isoformat(),
        'path_original': path_original.replace('\\', '/'),
        'path_processed': path_processed.replace('\\', '/'),
        'path_thumbnail': path_thumbnail.replace('\\', '/')
    }
    database.add_video_record(video_data)

    return jsonify({"message": "Vídeo enviado e processado com sucesso!", "video": video_data}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)