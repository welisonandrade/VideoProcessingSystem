import os
from pathlib import Path
from flask import Flask, render_template, url_for
import cv2

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
VIDEOS_DIR = STATIC_DIR / "videos"
THUMBS_DIR = STATIC_DIR / "thumbs"

def ensure_dirs():
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)

def is_video(filename: str) -> bool:
    exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    return Path(filename).suffix.lower() in exts

def thumb_name_for(video_name: str) -> str:
    stem = Path(video_name).stem
    return f"{stem}.jpg"

def generate_thumbnail(video_path: Path, thumb_path: Path, width: int = 320):
    """Extrai o primeiro frame do vídeo e salva como JPG redimensionado."""
    cap = cv2.VideoCapture(str(video_path))
    try:
        ok, frame = cap.read()
        if not ok or frame is None:
            return
        h, w = frame.shape[:2]
        new_w = width
        new_h = int(h * (new_w / w))
        frame_resized = cv2.resize(frame, (new_w, new_h))
        cv2.imwrite(str(thumb_path), frame_resized, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    finally:
        cap.release()

def collect_videos_with_thumbs():
    ensure_dirs()
    items = []
    for name in sorted(os.listdir(VIDEOS_DIR)):
        if not is_video(name):
            continue
        video_path = VIDEOS_DIR / name
        thumb_filename = thumb_name_for(name)
        thumb_path = THUMBS_DIR / thumb_filename
        if not thumb_path.exists():
            generate_thumbnail(video_path, thumb_path)
        items.append({
            "video_url": url_for("static", filename=f"videos/{name}"),
            "thumb_url": url_for("static", filename=f"thumbs/{thumb_filename}"),
            "filename": name
        })
    return items

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return gallery()

@app.route("/gallery")
def gallery():
    videos = collect_videos_with_thumbs()
    return render_template("index.html", videos=videos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
