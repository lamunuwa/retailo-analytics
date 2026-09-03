import torch

from vision.src.modules.session import VideoSession, run_detection
from vision.src.modules.zones import get_configured_zones


def get_device() -> str:
    """Selecciona CUDA si existe, de lo contrario, usa CPU"""

    if torch.cuda.is_available():
        print(f"Dispositivo seleccionado: cuda ({torch.cuda.get_device_name(0)})")
        return "cuda"

    print("Dispositivo seleccionado: cpu")
    return "cpu"


def main() -> VideoSession:
    """Inicia la detección y cuenta por zona."""

    zones = get_configured_zones()
    session = run_detection(
        device=get_device(),
        zones=zones,
    )

    print(f"Personas detectadas: {session.detected_people}")
    for zone_name, count in session.detections_by_zone.items():
        print(f"{zone_name}: {count}")
    return session


if __name__ == "__main__":
    main()
