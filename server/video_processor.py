import cv2


def apply_grayscale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def apply_pixelate(frame, pixels=10):
    h, w, _ = frame.shape
    small = cv2.resize(frame, (pixels, int(h / w * pixels)), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def apply_canny_edges(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(gray, 100, 200)


# ...

def process_video(input_path, output_path, filter_name):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Não foi possível abrir o vídeo de entrada: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 1. Usando o codec MJPG, que é o mais confiável e compatível
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 2. Verificação CRÍTICA para diagnosticar falhas de codec
    if not out.isOpened():
        print("--- ERRO CRÍTICO NO SERVIDOR ---")
        print(
            "O cv2.VideoWriter não pôde ser aberto. Isso geralmente indica um problema com o codec ou permissões de pasta.")
        print(f"  - Codec Tentado: MJPG")
        print(f"  - Caminho de Saída: {output_path}")
        raise IOError("Falha ao inicializar o VideoWriter. O arquivo processado não pode ser criado.")

    filter_function = {
        'grayscale': apply_grayscale,
        'pixelate': apply_pixelate,
        'canny_edges': apply_canny_edges
    }.get(filter_name)

    if not filter_function:
        raise ValueError(f"Filtro desconhecido: {filter_name}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = filter_function(frame)

        # Converte frames de 1 canal (como grayscale) de volta para 3 canais para salvar
        if len(processed_frame.shape) == 2:
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)

        out.write(processed_frame)

    print(f"Vídeo processado e salvo com sucesso em: {output_path}")
    cap.release()
    out.release()
    cv2.destroyAllWindows()



def extract_metadata(video_path):
    cap = cv2.VideoCapture(video_path)
    metadata = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    }
    metadata['duration_sec'] = metadata['frame_count'] / metadata['fps'] if metadata['fps'] > 0 else 0
    cap.release()
    return metadata


def generate_thumbnail(video_path, thumb_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(thumb_path, frame)
    cap.release()