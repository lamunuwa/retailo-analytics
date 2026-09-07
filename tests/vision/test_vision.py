from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from pytest import CaptureFixture

from vision.src import main as vision_main
from vision.src import runtime
from vision.src.modules import session
from vision.src.modules.counting import ZoneCounter
from vision.src.modules.detection import (
    DetectionFrame,
    PersonDetection,
    PersonDetector,
)
from vision.src.modules.zones import RoiZone, build_zones, get_configured_zones


def create_zone() -> RoiZone:
    """Crea una zona cuadrada para las pruebas."""

    zone = RoiZone(
        name="entrada",
        points=((0, 0), (100, 0), (100, 100), (0, 100)),
    )

    return zone


# Runtime -----------------------------------------------------


def test_get_device_uses_cpu_when_cuda_is_unavailable() -> None:
    with patch.object(runtime.torch.cuda, "is_available", return_value=False):
        device = runtime.get_device()

    assert device == "cpu"


def test_get_device_uses_cuda_when_available() -> None:
    with (
        patch.object(runtime.torch.cuda, "is_available", return_value=True),
        patch.object(runtime.torch.cuda, "get_device_name", return_value="GPU"),
    ):
        device = runtime.get_device()

    assert device == "cuda"


def test_runtime_uses_environment_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CAMERA_SOURCE", "0")
    monkeypatch.setenv("MODEL_PATH", "model.pt")
    monkeypatch.setenv("TRACKER_PATH", "tracker.yaml")

    assert runtime.get_video_source() == 0
    assert runtime.get_model_path() == "model.pt"
    assert runtime.get_tracker_path() == "tracker.yaml"


def test_runtime_uses_defaults_when_environment_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CAMERA_SOURCE", raising=False)
    monkeypatch.delenv("MODEL_PATH", raising=False)
    monkeypatch.delenv("TRACKER_PATH", raising=False)

    assert runtime.get_video_source() == runtime.DEFAULT_VIDEO_SOURCE
    assert runtime.get_model_path() == runtime.DEFAULT_MODEL_PATH
    assert runtime.get_tracker_path() == "vision/config/bytetrack.yaml"


def test_runtime_config_groups_execution_values() -> None:
    with (
        patch.object(runtime, "get_device", return_value="cpu"),
        patch.object(runtime, "get_video_source", return_value="video.mp4"),
        patch.object(runtime, "get_model_path", return_value="model.pt"),
        patch.object(runtime, "get_tracker_path", return_value="tracker.yaml"),
    ):
        runtime_config = runtime.get_runtime_config()

    assert runtime_config == runtime.VisionRuntimeConfig(
        device="cpu",
        video_source="video.mp4",
        model_path="model.pt",
        tracker_path="tracker.yaml",
    )


# Main --------------------------------------------------------


def test_main_runs_detection_and_prints_metrics(
    capsys: CaptureFixture[str],
) -> None:
    session_result = session.VideoSession(
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        processed_frames=1,
        detected_people=2,
        tracked_people=1,
        untracked_detections=0,
        visits_by_zone={"entrada": 1},
    )
    runtime_config = runtime.VisionRuntimeConfig(
        device="cpu",
        video_source="video.mp4",
        model_path="model.pt",
        tracker_path="tracker.yaml",
    )

    with (
        patch.object(vision_main, "get_configured_zones", return_value=(create_zone(),)),
        patch.object(vision_main, "get_runtime_config", return_value=runtime_config),
        patch.object(vision_main, "run_detection", return_value=session_result),
    ):
        result = vision_main.main()

    output = capsys.readouterr().out

    assert result == session_result
    assert "Personas rastreadas: 1" in output
    assert "entrada: 1" in output


# Detection ---------------------------------------------------


def test_person_detection_uses_the_bottom_center_of_the_box() -> None:
    person = PersonDetection(10.0, 10.0, 30.0, 40.0)

    assert person.floor_position == (20.0, 40.0)


def test_person_detector_creates_tracked_people() -> None:
    result = MagicMock()
    result.orig_img = np.zeros((20, 20, 3), dtype=np.uint8)
    result.boxes.xyxy.cpu().tolist.return_value = [[1.0, 2.0, 3.0, 4.0]]
    result.boxes.id.int().cpu().tolist.return_value = [7]

    model = MagicMock()
    model.track.return_value = [result]

    with patch("vision.src.modules.detection.YOLO", return_value=model):
        detector = PersonDetector(
            model_path="model.pt",
            device="cpu",
            tracker_path="tracker.yaml",
        )
        frames = list(detector.detect_in_video("video.mp4"))

    assert frames[0].people == (PersonDetection(1.0, 2.0, 3.0, 4.0, 7),)
    assert frames[0].image is None


def test_person_detector_skips_invalid_results_and_accepts_missing_ids() -> None:
    missing_image = MagicMock()
    missing_image.orig_img = None

    without_id = MagicMock()
    without_id.orig_img = np.zeros((20, 20, 3), dtype=np.uint8)
    without_id.boxes.xyxy.cpu().tolist.return_value = [[1.0, 2.0, 3.0, 4.0]]
    without_id.boxes.id = None

    model = MagicMock()
    model.track.return_value = [missing_image, without_id]

    with patch("vision.src.modules.detection.YOLO", return_value=model):
        detector = PersonDetector(model_path="model.pt", device="cpu")
        frames = list(detector.detect_in_video("video.mp4"))

    assert len(frames) == 1
    assert frames[0].people[0].track_id is None


# ROI and counting -------------------------------------------


def test_zones_can_be_built_and_detect_points() -> None:
    zones = build_zones(
        {"entrada": ((0, 0), (100, 0), (100, 100), (0, 100))}
    )

    assert zones[0].contains((50.0, 50.0))
    assert not zones[0].contains((150.0, 50.0))
    assert get_configured_zones()[0].name == "entrada"


def test_zones_require_a_valid_polygon() -> None:
    with pytest.raises(ValueError):
        build_zones({})

    with pytest.raises(ValueError):
        build_zones({"invalida": ((0, 0), (1, 1))})


def test_zone_counter_counts_a_track_once_per_zone() -> None:
    counter = ZoneCounter((create_zone(),))
    person = PersonDetection(10.0, 10.0, 20.0, 20.0, track_id=5)

    counter.register((person,))
    counter.register((person,))

    assert counter.counts == {"entrada": 1}


def test_zone_counter_ignores_people_without_track_or_outside_zone() -> None:
    counter = ZoneCounter((create_zone(),))
    without_track = PersonDetection(10.0, 10.0, 20.0, 20.0)
    outside_zone = PersonDetection(150.0, 10.0, 160.0, 20.0, track_id=8)

    counter.register((without_track, outside_zone))

    assert counter.counts == {"entrada": 0}


# Session ------------------------------------------------------


def test_session_collects_tracking_metrics() -> None:
    tracked_person = PersonDetection(1.0, 1.0, 2.0, 2.0, track_id=7)
    untracked_person = PersonDetection(3.0, 3.0, 4.0, 4.0)
    frame = DetectionFrame(image=None, people=(tracked_person, untracked_person))

    detector = MagicMock()
    detector.detect_in_video.return_value = [frame, frame]

    counter = MagicMock()
    counter.counts = {"entrada": 1}

    with (
        patch.object(session, "PersonDetector", return_value=detector),
        patch.object(session, "ZoneCounter", return_value=counter),
    ):
        result = session.run_detection(
            device="cpu",
            zones=(create_zone(),),
            video_source="video.mp4",
            model_path="model.pt",
        )

    assert result.processed_frames == 2
    assert result.detected_people == 4
    assert result.tracked_people == 1
    assert result.untracked_detections == 2
    assert result.visits_by_zone == {"entrada": 1}
