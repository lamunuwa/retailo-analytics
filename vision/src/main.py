from datetime import UTC, datetime

from vision.src.api_client import APIClientError, RetailoAnalyticsClient
from vision.src.api_contract import ZoneMetricContract, video_result_payload
from vision.src.modules.session import VideoSession, run_detection
from vision.src.modules.zones import RoiZone, build_zones_from_api
from vision.src.runtime import get_runtime_config


def build_zone_metrics(
    session: VideoSession,
    zones: tuple[RoiZone, ...],
) -> list[ZoneMetricContract]:
    """Convierte metricas locales al contrato de API"""

    total_visits = sum(session.visits_by_zone.values())
    metrics: list[ZoneMetricContract] = []
    for zone in zones:
        if zone.zone_id is None:
            raise ValueError(f"La zona '{zone.name}' no tiene ID de API")
        visits = session.visits_by_zone.get(zone.name, 0)
        metrics.append(
            {
                "zone_id": zone.zone_id,
                "visits": visits,
                "dwell_seconds": round(session.dwell_seconds_by_zone.get(zone.name, 0.0), 2),
                "traffic_share": round(visits * 100 / total_visits, 2)
                if total_visits
                else 0.0,
            }
        )
    return metrics


def main() -> VideoSession:
    """Ejecuta Vision y reporta sus resultados"""

    runtime_config = get_runtime_config()

    api_client = RetailoAnalyticsClient(
        api_url=runtime_config.api_url,
        api_token=runtime_config.api_token,
    )
    zones = build_zones_from_api(api_client.get_zones(runtime_config.camera_id))
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
        dwell = session.dwell_seconds_by_zone.get(zone_name, 0.0)
        print(f"{zone_name}: {count} visitas, {dwell:.2f}s de permanencia")

    try:
        api_client.publish_video_result(
            session_id=session_id,
            payload=video_result_payload(
                processed_frames=session.processed_frames,
                elapsed_seconds=(session.finished_at - session.started_at).total_seconds(),
                detected_people=session.detected_people,
                started_at=session.started_at,
                finished_at=session.finished_at,
                zone_metrics=build_zone_metrics(session, zones),
            ),
        )
        print("\nResultados publicados; sesión marcada como completed en API")
    except (APIClientError, ValueError) as e:
        print(f"Error al publicar resultados en API: {e}")
        try:
            api_client.update_session(
                session_id=session_id,
                status="failed",
                finished_at=datetime.now(UTC),
            )
        except APIClientError as update_error:
            print(f"Error al marcar sesión como failed en API: {update_error}")
        raise

    return session


if __name__ == "__main__":
    main()
