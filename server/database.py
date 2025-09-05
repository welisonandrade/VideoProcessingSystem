import sqlite3
import os

DB_FILE = "videos.db"
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'media')
DB_PATH = os.path.join(MEDIA_ROOT, DB_FILE)

def get_db_connection():
    # Garante que o diretório media exista
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
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
            filter TEXT NOT NULL,
            created_at TEXT NOT NULL,
            path_original TEXT NOT NULL,
            path_processed TEXT NOT NULL,
            path_thumbnail TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_video_record(video_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO videos (
            id, original_name, original_ext, mime_type, size_bytes, duration_sec, 
            fps, width, height, filter, created_at, path_original, 
            path_processed, path_thumbnail
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        video_data['id'], video_data['original_name'], video_data['original_ext'],
        video_data['mime_type'], video_data['size_bytes'], video_data['duration_sec'],
        video_data['fps'], video_data['width'], video_data['height'],
        video_data['filter'], video_data['created_at'], video_data['path_original'],
        video_data['path_processed'], video_data['path_thumbnail']
    ))
    conn.commit()
    conn.close()

def get_all_videos():
    conn = get_db_connection()
    videos = conn.execute("SELECT * FROM videos ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(video) for video in videos]