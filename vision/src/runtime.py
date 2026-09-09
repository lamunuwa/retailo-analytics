import os
from dataclasses import dataclass

import torch

DEFAULT_VIDEO_SOURCE = "vision/data/demo/supermarket.mp4"
DEFAULT_MODEL_PATH = "yolov8n.pt"


@dataclass(frozen=True)
class VisionRuntimeConfig:
    """Representa la configuracion local para ejecutar Vision"""

    device: str
    video_source: str | int
    model_path: str
    tracker_path: str


def get_video_source() -> str | int:
    """Obtiene la camara o video configurado para la deteccion"""

    configured_source = os.getenv("CAMERA_SOURCE", "").strip()

    if not configured_source:
        return DEFAULT_VIDEO_SOURCE

    if configured_source.isdigit():
        return int(configured_source)

    return configured_source


def get_model_path() -> str:
    """Obtiene el modelo YOLO configurado para la deteccion"""

    configured_model = os.getenv("MODEL_PATH", "").strip()

    if configured_model:
        return configured_model

    return DEFAULT_MODEL_PATH


def get_tracker_path() -> str:
    """Obtiene el tracker configurado para el seguimiento"""

    configured_tracker = os.getenv("TRACKER_PATH", "").strip()

    if configured_tracker:
        return configured_tracker

    return "vision/config/bytetrack.yaml"


def get_device() -> str:
    """Selecciona CUDA si existe, de lo contrario, usa CPU"""

    if torch.cuda.is_available():
        print(f"Dispositivo seleccionado: cuda ({torch.cuda.get_device_name(0)})")
        return "cuda"

    print("Dispositivo seleccionado: cpu")
    return "cpu"


def get_runtime_config() -> VisionRuntimeConfig:
    """Obtiene la configuracion necesaria para ejecutar Vision"""

    runtime_config = VisionRuntimeConfig(
        device=get_device(),
        video_source=get_video_source(),
        model_path=get_model_path(),
        tracker_path=get_tracker_path(),
    )

    return runtime_config
