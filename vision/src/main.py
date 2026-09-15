from datetime import UTC, datetime

from vision.src.api_client import APIClientError, RetailoAnalyticsClient
from vision.src.modules.session import VideoSession, run_detection
from vision.src.modules.zones import get_configured_zones
from vision.src.runtime import get_runtime_config


def main() -> VideoSession:
    """Inicia la detección, crea sesión en la API y reporta resultados."""

    zones = get_configured_zones()
    runtime_config = get_runtime_config()

    api_client = RetailoAnalyticsClient(api_url=runtime_config.api_url)
    started_at = datetime.now(UTC)

    try:
        session_id = api_client.create_session(
            camera_id=runtime_config.camera_id,
            started_at=started_at,
        )
        print(f"Sesión creada en API: session_id={session_id}")
    except APIClientError as e:
        print(f"Error al crear sesión en API: {e}")
        raise

    try:
        session = run_detection(
            device=runtime_config.device,
            zones=zones,
            video_path=runtime_config.video_path,
            model_path=runtime_config.model_path,
            tracker_path=runtime_config.tracker_path,
        )
    except Exception:
        try:
            api_client.update_session(
                session_id=session_id,
                status="failed",
                finished_at=datetime.now(UTC),
            )
            print("Sesión marcada como failed en API")
        except APIClientError as api_error:
            print(f"Error al actualizar sesión como failed en API: {api_error}")

        raise

    print(f"\nDetecciones YOLO: {session.detected_people}")
    print(f"Personas rastreadas: {session.tracked_people}")
    print(f"Detecciones sin track: {session.untracked_detections}")

    for zone_name, count in session.visits_by_zone.items():
        print(f"{zone_name}: {count}")

    try:
        api_client.update_session(
            session_id=session_id,
            status="completed",
            finished_at=session.finished_at,
        )
        print("\nSesión marcada como completed en API")
    except APIClientError as e:
        print(f"Error al actualizar sesión en API: {e}")

    return session


if __name__ == "__main__":
    main()
