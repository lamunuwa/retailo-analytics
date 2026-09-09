from vision.src.modules.session import VideoSession, run_detection
from vision.src.modules.zones import get_configured_zones
from vision.src.runtime import get_runtime_config


def main() -> VideoSession:
    """Inicia la detección y cuenta por zona."""

    zones = get_configured_zones()
    runtime_config = get_runtime_config()

    session = run_detection(
        device=runtime_config.device,
        zones=zones,
        video_source=runtime_config.video_source,
        model_path=runtime_config.model_path,
        tracker_path=runtime_config.tracker_path,
    )

    print(f"Detecciones YOLO: {session.detected_people}")
    print(f"Personas rastreadas: {session.tracked_people}")
    print(f"Detecciones sin track: {session.untracked_detections}")

    for zone_name, count in session.visits_by_zone.items():
        print(f"{zone_name}: {count}")

    return session


if __name__ == "__main__":
    main()
