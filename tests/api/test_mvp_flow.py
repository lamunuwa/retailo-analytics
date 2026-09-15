from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.src.core.db import Base
from app.src.repos.cameras import CameraRepository
from app.src.repos.recommendations import RecommendationRepository
from app.src.repos.reporting import ReportingRepository
from app.src.repos.results import VideoResultRepository
from app.src.repos.sales import SalesRepository
from app.src.repos.sessions import SessionRepository
from app.src.repos.stores import StoreRepository
from app.src.repos.zones import ZoneRepository
from app.src.routers.cameras import create_camera
from app.src.routers.recommendations import (
    generate_recommendations,
    get_all_recommendations,
    update_recommendation_status,
)
from app.src.routers.reporting import (
    get_analytics_insights,
    get_analytics_summary,
    get_analytics_traffic,
)
from app.src.routers.results import create_video_result, get_video_result
from app.src.routers.sales import create_sales_record, get_all_sales_records
from app.src.routers.sessions import create_session, get_session
from app.src.routers.stores import create_store
from app.src.routers.zones import create_zone, delete_zone, get_all_zones, update_zone
from app.src.schemas.cameras import CameraCreate
from app.src.schemas.recommendations import RecommendationStatusUpdate
from app.src.schemas.results import VideoResultCreate
from app.src.schemas.sales import SalesRecordCreate
from app.src.schemas.sessions import SessionCreate
from app.src.schemas.stores import StoreCreate
from app.src.schemas.zones import ZoneCreate, ZoneUpdate
from app.src.services.reporting import StoreAnalyticsService


@pytest.fixture
def db() -> Iterator[Session]:
    """Crea una base de datos temporal"""
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


def create_store_camera_zone(
    db: Session,
    zone_name: str = "Refrigeradores",
) -> tuple[int, int, int]:
    """Crea las entidades base de una prueba"""
    store = create_store(StoreCreate(name="Abarrotes Centro"), StoreRepository(db))
    camera = create_camera(
        store.id,
        CameraCreate.model_validate(
            {"name": "Cámara principal", "source_type": "demo_video"}
        ),
        CameraRepository(db),
    )
    zone = create_zone(
        camera.id,
        ZoneCreate.model_validate(
            {
                "name": zone_name,
                "zone_type": "fridges",
                "points": [
                {"x": 0, "y": 0},
                {"x": 100, "y": 0},
                {"x": 100, "y": 100},
                {"x": 0, "y": 100},
                ],
            }
        ),
        ZoneRepository(db),
    )
    return store.id, camera.id, zone.id


def test_complete_mvp_flow(db: Session) -> None:
    """Valida el flujo completo del MVP"""
    store_id, camera_id, zone_id = create_store_camera_zone(db)
    now = datetime.now(UTC)
    video_session = create_session(
        camera_id,
        SessionCreate(started_at=now),
        SessionRepository(db),
    )
    result_payload = VideoResultCreate.model_validate(
        {
            "processed_frames": 300,
            "elapsed_seconds": 30,
            "detected_people": 12,
            "started_at": now,
            "finished_at": now + timedelta(seconds=30),
            "zone_metrics": [{
                "zone_id": zone_id,
                "visits": 7,
                "dwell_seconds": 42.5,
                "traffic_share": 100,
            }],
        }
    )
    result = create_video_result(video_session.id, result_payload, VideoResultRepository(db))
    assert result.zone_metrics[0].visits == 7
    assert get_session(video_session.id, SessionRepository(db)).status == "completed"
    assert get_video_result(video_session.id, VideoResultRepository(db)).id == result.id
    with pytest.raises(HTTPException, match="El resultado de video ya existe"):
        create_video_result(video_session.id, result_payload, VideoResultRepository(db))

    sale = create_sales_record(
        store_id,
        SalesRecordCreate(
            zone_id=zone_id,
            category="Bebidas",
            units_sold=3,
            revenue=75.5,
            recorded_at=now,
        ),
        SalesRepository(db),
    )
    assert sale.revenue == 75.5
    assert len(get_all_sales_records(store_id, SalesRepository(db), None, None)) == 1

    service = StoreAnalyticsService(ReportingRepository(db))
    summary = get_analytics_summary(store_id, service, None, None)
    assert summary.total_sessions == 1
    assert summary.total_visits == 7
    assert summary.total_dwell_seconds == 42.5
    traffic = get_analytics_traffic(store_id, service, None, None)
    assert traffic[0].traffic_share == 100
    insights = get_analytics_insights(store_id, service, None, None)
    assert insights[0].type == "HIGH_TRAFFIC_HIGH_SALES"

    generated = generate_recommendations(store_id, db, None, None)
    assert generated[0].status == "pending"
    assert generate_recommendations(store_id, db, None, None)[0].id == generated[0].id
    assert len(get_all_recommendations(store_id, db, "pending")) == 1
    updated = update_recommendation_status(
        generated[0].id,
        RecommendationStatusUpdate(status="accepted"),
        db,
    )
    assert updated.status == "accepted"


def test_zone_validation_update_and_delete(db: Session) -> None:
    """Valida la actualizacion y desactivacion de zonas"""
    _, camera_id, zone_id = create_store_camera_zone(db)
    with pytest.raises(ValidationError, match="area"):
        ZoneCreate.model_validate(
            {
                "name": "Sin área",
                "zone_type": "other",
                "points": [
                    {"x": 0, "y": 0},
                    {"x": 1, "y": 1},
                    {"x": 2, "y": 2},
                    {"x": 3, "y": 3},
                ],
            }
        )
    repo = ZoneRepository(db)
    updated = update_zone(zone_id, ZoneUpdate(name="Fríos"), repo)
    assert updated.name == "Fríos"
    assert delete_zone(zone_id, repo).is_active is False
    assert get_all_zones(camera_id, repo) == []


def test_parent_and_cross_camera_integrity(db: Session) -> None:
    """Valida la integridad entre entidades relacionadas"""
    with pytest.raises(HTTPException, match="Tienda no encontrada"):
        create_camera(
            999,
            CameraCreate.model_validate(
                {"name": "Huérfana", "source_type": "demo_video"}
            ),
            CameraRepository(db),
        )

    store_id, camera_id, _ = create_store_camera_zone(db)
    _, _, foreign_zone_id = create_store_camera_zone(db, "Caja")
    started_at = datetime.now(UTC)
    video_session = create_session(
        camera_id,
        SessionCreate(started_at=started_at),
        SessionRepository(db),
    )
    payload = VideoResultCreate.model_validate(
        {
            "processed_frames": 1,
            "elapsed_seconds": 1,
            "detected_people": 1,
            "started_at": started_at,
            "finished_at": started_at + timedelta(seconds=1),
            "zone_metrics": [{
                "zone_id": foreign_zone_id,
                "visits": 1,
                "dwell_seconds": 1,
                "traffic_share": 100,
            }],
        }
    )
    with pytest.raises(HTTPException, match="Cada zone_id"):
        create_video_result(video_session.id, payload, VideoResultRepository(db))
    service = StoreAnalyticsService(ReportingRepository(db))
    assert get_analytics_summary(store_id, service, None, None).total_sessions == 0


def test_repository_empty_and_missing_paths(db: Session) -> None:
    """Valida consultas sin resultados"""
    assert RecommendationRepository(db).get_by_id(999) is None
    assert SalesRepository(db).get_all_by_store(999) == []
    assert VideoResultRepository(db).get_by_session_id(999) is None
    with pytest.raises(HTTPException, match="Sesion no encontrada"):
        get_video_result(999, VideoResultRepository(db))
