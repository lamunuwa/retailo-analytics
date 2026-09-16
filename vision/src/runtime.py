import os
from dataclasses import dataclass

import torch

DEFAULT_DEMO_VIDEO_PATH = "vision/data/demo/supermarket.mp4"
DEFAULT_MODEL_PATH = "yolov8n.pt"
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_CAMERA_ID = 1


@dataclass(frozen=True)
class VisionRuntimeConfig:
    """Representa la configuracion local para ejecutar Vision"""

    device: str
    video_path: str
    model_path: str
    tracker_path: str
    camera_id: int
    api_url: str
    api_token: str = ""


def get_demo_video_path() -> str:
    """Obtiene la ruta del video demo"""

    configured_path = os.getenv("DEMO_VIDEO_PATH", "").strip()

    return configured_path or DEFAULT_DEMO_VIDEO_PATH


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


def get_camera_id() -> int:
    """Obtiene el camera_id configurado para asociar con la API"""

    configured_camera_id = os.getenv("CAMERA_ID", "").strip()

    if configured_camera_id and configured_camera_id.isdigit():
        return int(configured_camera_id)

    return DEFAULT_CAMERA_ID


def get_api_url() -> str:
    """Obtiene la URL base de la API"""

    configured_api_url = os.getenv("API_BASE_URL", "").strip()

    if configured_api_url:
        return configured_api_url

    return DEFAULT_API_URL


def get_api_token() -> str:
    """Obtiene el token opcional de la API"""

    return os.getenv("API_TOKEN", "").strip()


def get_device() -> str:
    """Selecciona CUDA si existe, de lo contrario, usa CPU"""

    if torch.cuda.is_available():
        print(f"Dispositivo seleccionado: cuda ({torch.cuda.get_device_name(0)})")
        return "cuda"

    print("Dispositivo seleccionado: cpu")
    return "cpu"


def get_runtime_config() -> VisionRuntimeConfig:
    """Obtiene la configuracion necesaria para ejecutar Vision"""
    return VisionRuntimeConfig(
        device=get_device(),
        video_path=get_demo_video_path(),
        model_path=get_model_path(),
        tracker_path=get_tracker_path(),
        camera_id=get_camera_id(),
        api_url=get_api_url(),
        api_token=get_api_token(),
    )
