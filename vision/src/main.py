from datetime import UTC, datetime

from vision.src.api_client import APIClientError, CameraZone, RetailoAnalyticsClient
from vision.src.modules.session import VideoSession, run_detection
from vision.src.modules.zones import RoiZone, get_configured_zones
from vision.src.runtime import get_runtime_config


def _build_runtime_zones(api_zones: tuple[CameraZone, ...]) -> tuple[RoiZone, ...]:
    """Convierte las zonas de la API al formato del detector."""
    if not api_zones:
        return get_configured_zones()
    return tuple(RoiZone(name=zone.name, points=zone.points) for zone in api_zones)


def _build_zone_metrics(
    video_session: VideoSession,
    api_zones: tuple[CameraZone, ...],
) -> list[dict[str, int | float]]:
    """Convierte los conteos en metricas publicables."""
    zone_ids = {zone.name: zone.id for zone in api_zones}
    total_visits = sum(
        visits for name, visits in video_session.visits_by_zone.items() if name in zone_ids
    )
    return [
        {
            "zone_id": zone_ids[name],
            "visits": visits,
            "dwell_seconds": 0.0,
            "traffic_share": round(visits * 100 / total_visits, 2) if total_visits else 0.0,
        }
        for name, visits in video_session.visits_by_zone.items()
        if name in zone_ids
    ]


def main() -> VideoSession:
    """Inicia la deteccion crea una sesion y publica resultados."""

    runtime_config = get_runtime_config()
    api_client = RetailoAnalyticsClient(api_url=runtime_config.api_url)
    api_zones = api_client.get_zones(runtime_config.camera_id)
    zones = _build_runtime_zones(api_zones)
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

    elapsed_seconds = max(0.0, (session.finished_at - session.started_at).total_seconds())
    try:
        api_client.create_video_result(
            session_id=session_id,
            processed_frames=session.processed_frames,
            elapsed_seconds=elapsed_seconds,
            detected_people=session.detected_people,
            started_at=session.started_at,
            finished_at=session.finished_at,
            zone_metrics=_build_zone_metrics(session, api_zones),
        )
        print("\nResultados publicados y sesión completada en API")
    except APIClientError as error:
        try:
            api_client.update_session(
                session_id=session_id,
                status="failed",
                finished_at=datetime.now(UTC),
            )
        except APIClientError as update_error:
            print(f"Error al marcar la sesión como failed: {update_error}")
        raise error

    return session


if __name__ == "__main__":
    main()
