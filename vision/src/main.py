import logging
import time

import torch
from ultralytics import YOLO

VIDEO_PATH = "vision/data/demo/supermarket.mp4"
MODEL_PATH = "yolov8n.pt"
PROGRESS_EVERY_N_FRAMES = 30

logger = logging.getLogger(__name__)


def get_device() -> str:
    """Selecciona CUDA si está disponible; de lo contrario, usa CPU."""

    if torch.cuda.is_available():
        logger.info("Dispositivo seleccionado: cuda (%s)", torch.cuda.get_device_name(0))
        return "cuda"

    logger.info("Dispositivo seleccionado: cpu")
    return "cpu"


def main() -> None:
    """Ejecuta detección de personas sobre un video sin interfaz gráfica."""

    device = get_device()
    model = YOLO(MODEL_PATH)
    logger.info(
        "Iniciando detección: fuente=%s, modelo=%s, dispositivo=%s",
        VIDEO_PATH,
        MODEL_PATH,
        device,
    )

    started_at = time.perf_counter()
    frames_processed = 0
    total_detections = 0

    try:
        results = model.predict(
            source=VIDEO_PATH,
            stream=True,
            classes=[0],
            conf=0.5,
            device=device,
            verbose=False,
        )

        for result in results:
            frames_processed += 1
            if isinstance(result, torch.Tensor):
                logger.warning("El frame %d no contiene resultados de detección", frames_processed)
                continue

            boxes = result.boxes
            detections_in_frame = len(boxes) if boxes is not None else 0
            total_detections += detections_in_frame

            if frames_processed % PROGRESS_EVERY_N_FRAMES == 0:
                elapsed = time.perf_counter() - started_at
                effective_fps = frames_processed / elapsed if elapsed > 0 else 0.0
                logger.info(
                    "Progreso: frame=%d, detecciones=%d, FPS efectivo=%.2f",
                    frames_processed,
                    detections_in_frame,
                    effective_fps,
                )
    except Exception:
        logger.exception("La detección de Vision falló después de %d frames", frames_processed)
        raise

    elapsed = time.perf_counter() - started_at
    effective_fps = frames_processed / elapsed if elapsed > 0 else 0.0
    logger.info(
        "Detección finalizada: frames=%d, detecciones=%d, duración=%.2f s, FPS efectivo=%.2f",
        frames_processed,
        total_detections,
        elapsed,
        effective_fps,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
