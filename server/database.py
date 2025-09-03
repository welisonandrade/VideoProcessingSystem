import sqlite3
import uuid
from datetime import datetime

DATABASE_FILE = 'videos.db'

def get_db_connection():
    """Cria uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados criando a tabela, se não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            original_name TEXT NOT NULL,
            original_ext TEXT NOT NULL,
            mime_type TEXT,
            size_bytes INTEGER,
            duration_sec REAL,
            fps REAL,
            width INTEGER,
            height INTEGER,
            filter TEXT,
            created_at TEXT NOT NULL,
            path_original TEXT NOT NULL,
            path_processed TEXT,
            path_thumb TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso.")

def add_video_record(video_data):
    """Adiciona um novo registro de vídeo ao banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO videos (
            id, original_name, original_ext, mime_type, size_bytes, duration_sec,
            fps, width, height, filter, created_at, path_original, path_processed, path_thumb
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        video_data['id'],
        video_data['original_name'],
        video_data['original_ext'],
        video_data.get('mime_type'),
        video_data.get('size_bytes'),
        video_data.get('duration_sec'),
        video_data.get('fps'),
        video_data.get('width'),
        video_data.get('height'),
        video_data.get('filter'),
        video_data['created_at'],
        video_data['path_original'],
        video_data.get('path_processed'),
        video_data.get('path_thumb')
    ))
    conn.commit()
    conn.close()

def get_all_videos():
    """Retorna todos os registros de vídeos do banco."""
    conn = get_db_connection()
    videos = conn.execute('SELECT * FROM videos ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(video) for video in videos]

if __name__ == '__main__':
    # Este bloco permite que você inicialize o DB manualmente se precisar
    init_db()