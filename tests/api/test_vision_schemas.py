from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from app.src.schemas.vision import VideoResult


def test_video_result_valido() -> None:
    datos: dict[str, Any] = {
        "processed_frames": 1000,
        "elapsed_seconds": 10,
        "detected_people": 10,
        "started_at": "2026-08-30T12:00:00",
        "finished_at": "2026-08-30T12:01:38",
        "zone_metrics": [
            {
                "zone_id": 1,
                "visits": 10,
                "dwell_seconds": 10,
                "traffic_share": 42.5,
            }
        ],
    }

    resultado = VideoResult(**datos)

    assert resultado.processed_frames == 1000
    assert resultado.detected_people == 10
    assert isinstance(resultado.started_at, datetime)
    assert len(resultado.zone_metrics) == 1
    assert resultado.zone_metrics[0].zone_id == 1


def test_video_result_rechaza_datos_faltantes() -> None:
    datos: dict[str, Any] = {
        "processed_frames": 1000,
        "started_at": "2026-08-30T12:00:00",
    }

    with pytest.raises(ValidationError):
        VideoResult(**datos)


def test_video_result_rechaza_tipos_incorrectos() -> None:
    datos: dict[str, Any] = {
        "processed_frames": "mil",  # Invalido, debe ser int
        "elapsed_seconds": 10,
        "detected_people": 10,
        "started_at": "2026-08-30T12:00:00",
        "finished_at": "2026-08-30T12:01:38",
        "zone_metrics": [],
    }

    with pytest.raises(ValidationError):
        VideoResult(**datos)
