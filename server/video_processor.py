import cv2
import os

def generate_thumbnail(video_path, thumb_path, width=320):
    """Gera um thumbnail do primeiro frame do vídeo."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False, None

    ret, frame = cap.read()
    if not ret:
        cap.release()
        return False, None

    # Redimensiona mantendo a proporção
    h, w, _ = frame.shape
    ratio = width / float(w)
    height = int(h * ratio)
    resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    cv2.imwrite(thumb_path, resized_frame)
    cap.release()
    return True, (w, h, cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT))


def apply_filter_to_video(input_path, output_path, filter_name):
    """Aplica um filtro a cada frame de um vídeo e salva o resultado."""
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Não foi possível abrir o vídeo de entrada: {input_path}")

    # Pega as propriedades do vídeo original
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Define o codec e cria o objeto VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # ou 'XVID'
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = None
        if filter_name == 'grayscale':
            # Converte o frame para escala de cinza
            processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Converte de volta para BGR para manter 3 canais de cor
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
        elif filter_name == 'edge_detection':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            processed_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        elif filter_name == 'pixelate':
            h, w, _ = frame.shape
            pixel_size = 16
            # Reduz a imagem
            small = cv2.resize(frame, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_LINEAR)
            # Expande de volta para o tamanho original
            processed_frame = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        else:
            # Se o filtro não for reconhecido, mantém o frame original
            processed_frame = frame

        out.write(processed_frame)

    # Libera os recursos
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return True