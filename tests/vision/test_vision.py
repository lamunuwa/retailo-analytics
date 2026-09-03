from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest
from pytest import CaptureFixture

from vision.src import main as vision_main
from vision.src.modules import session
from vision.src.modules.counting import ZoneCounter
from vision.src.modules.detection import (
    DetectionFrame,
    PersonDetection,
    PersonDetector,
)
from vision.src.modules.visualization import (
    WINDOW_NAME,
    DetectionVisualizer,
)
from vision.src.modules.zones import (
    RoiZone,
    build_zones,
    get_configured_zones,
    validate_zone_points,
)


@pytest.fixture
def temp_zone() -> RoiZone:
    """Crea una zona temporal cuadrada para las pruebas."""

    return RoiZone(
        name="entrada",
        points=((0, 0), (100, 0), (100, 100), (0, 100)),
    )

# Funcionamiento correcto -----------------------------

def test_get_device_cpu_when_cuda_is_unavailable() -> None:
    with patch.object(
        vision_main.torch.cuda,
        "is_available",
        return_value=False,
    ):
        device = vision_main.get_device()

    assert device == "cpu"


def test_get_device_cuda_when_available() -> None:
    with patch.object(
        vision_main.torch.cuda,
        "is_available",
        return_value=True,
    ):
        device = vision_main.get_device()

    assert device == "cuda"


def test_main_ok_uses_configured_zones_and_reports_counts(
    temp_zone: RoiZone,
    capsys: CaptureFixture[str],
) -> None:
    zones = (temp_zone,)

    session_result = session.VideoSession(
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        processed_frames=1,
        detected_people=1,
        detections_by_zone={"entrada": 1},
    )

    with (
        patch.object(vision_main, "get_device", return_value="cpu"),
        patch.object(
            vision_main,
            "get_configured_zones",
            return_value=zones,
        ),
        patch.object(
            vision_main,
            "run_detection",
            return_value=session_result,
        ) as run_detection,
    ):
        result = vision_main.main()

    run_detection.assert_called_once_with(
        device="cpu",
        zones=zones,
    )

    output = capsys.readouterr().out

    assert result == session_result
    assert "Personas detectadas: 1" in output
    assert "entrada: 1" in output

# -----------------------------------------------------

# PersonDetection -------------------------------------

def test_floor_position_ok() -> None:
    person = PersonDetection(
        x1=10.0,
        y1=10.0,
        x2=30.0,
        y2=40.0,
    )

    assert person.floor_position == (20.0, 40.0)

# -----------------------------------------------------


# PersonDetector --------------------------------------


def test_person_detector_ok_converts_yolo_results_to_detection_frames() -> None:
    image = np.zeros((20, 20, 3), dtype=np.uint8)

    result = MagicMock()
    result.orig_img = image
    result.boxes.xyxy.cpu().tolist.return_value = [
        [1.0, 2.0, 3.0, 4.0],
    ]

    model = MagicMock()
    model.predict.return_value = [result]

    with patch(
        "vision.src.modules.detection.YOLO",
        return_value=model,
    ) as yolo:
        detector = PersonDetector(
            model_path="model.pt",
            device="cpu",
            confidence=0.7,
        )

        frames = list(detector.detect_in_video("video.mp4"))

    yolo.assert_called_once_with("model.pt")

    model.predict.assert_called_once_with(
        source="video.mp4",
        stream=True,
        classes=[0],
        conf=0.7,
        device="cpu",
        verbose=False,
    )

    assert frames[0].people == (
        PersonDetection(1.0, 2.0, 3.0, 4.0),
    )
    assert frames[0].image is not image


def test_person_detector_skips_missing_images_and_supports_empty_boxes() -> None:
    missing_image_result = MagicMock()
    missing_image_result.orig_img = None

    empty_boxes_result = MagicMock()
    empty_boxes_result.orig_img = np.zeros(
        (10, 10, 3),
        dtype=np.uint8,
    )
    empty_boxes_result.boxes = None

    model = MagicMock()
    model.predict.return_value = [
        missing_image_result,
        empty_boxes_result,
    ]

    with patch(
        "vision.src.modules.detection.YOLO",
        return_value=model,
    ):
        detector = PersonDetector(
            model_path="model.pt",
            device="cpu",
        )

        frames = list(detector.detect_in_video("video.mp4"))

    assert len(frames) == 1
    assert frames[0].people == ()

# -----------------------------------------------------

# ZoneCounter -----------------------------------------

def test_zone_counter_ok_assigns_people_and_accumulates_counts(
    temp_zone: RoiZone,
) -> None:
    counter = ZoneCounter((temp_zone,))

    person_inside = PersonDetection(
        10.0,
        10.0,
        20.0,
        20.0,
    )
    person_outside = PersonDetection(
        150.0,
        10.0,
        160.0,
        20.0,
    )

    assignments = counter.register(
        (person_inside, person_outside),
    )
    counter.register((person_inside,))

    assert assignments == {
        person_inside: temp_zone,
        person_outside: None,
    }
    assert counter.counts == {"entrada": 2}


def test_zone_counter_counts_returns_a_copy(
    temp_zone: RoiZone,
) -> None:
    counter = ZoneCounter((temp_zone,))

    counts = counter.counts
    counts["entrada"] = 999

    assert counter.counts == {"entrada": 0}

# -----------------------------------------------------

# Zonas ROI -------------------------------------------

def test_validate_zone_points_requires_three_points() -> None:
    try:
        validate_zone_points(
            "invalida",
            ((0, 0), (1, 1)),
        )
    except ValueError as error:
        assert "invalida" in str(error)
    else:
        raise AssertionError(
            "La zona debe requerir al menos tres puntos"
        )


def test_build_zones_ok() -> None:
    zones = build_zones(
        {
            "entrada": (
                (0, 0),
                (10, 0),
                (10, 10),
            )
        }
    )

    zone = zones[0]

    assert zone.name == "entrada"
    assert zone.contains((5.0, 5.0))
    assert not zone.contains((20.0, 20.0))


def test_get_configured_zones_ok() -> None:
    zones = get_configured_zones()

    assert zones[0].name == "entrada"


def test_build_zones_requires_at_least_one_zone() -> None:
    try:
        build_zones({})
    except ValueError as error:
        assert str(error) == "Se requiere al menos una zona ROI"
    else:
        raise AssertionError(
            "Se debe requerir al menos una zona"
        )

# -----------------------------------------------------

# DetectionVisualizer ---------------------------------

def test_detection_visualizer_ok_shows_frame_and_closes_windows(
    temp_zone: RoiZone,
) -> None:
    person = PersonDetection(
        10.0,
        10.0,
        20.0,
        20.0,
    )

    frame = DetectionFrame(
        image=np.zeros((120, 120, 3), dtype=np.uint8),
        people=(person,),
    )

    with (
        patch(
            "vision.src.modules.visualization.cv2.namedWindow"
        ) as named_window,
        patch(
            "vision.src.modules.visualization.cv2.imshow"
        ) as imshow,
        patch(
            "vision.src.modules.visualization.cv2.waitKey",
            return_value=ord("q"),
        ),
        patch(
            "vision.src.modules.visualization.cv2.destroyAllWindows"
        ) as destroy_windows,
    ):
        visualizer = DetectionVisualizer((temp_zone,))

        should_exit = visualizer.show(
            frame,
            {person: temp_zone},
            {"entrada": 1},
        )

        visualizer.close()

    named_window.assert_called_once_with(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL,
    )
    imshow.assert_called_once_with(
        WINDOW_NAME,
        frame.image,
    )
    destroy_windows.assert_called_once()

    assert should_exit

# -----------------------------------------------------

# Sesion de deteccion ---------------------------------

def test_run_detection_ok_collects_metrics(
    temp_zone: RoiZone,
) -> None:
    person = PersonDetection(
        1.0,
        1.0,
        2.0,
        2.0,
    )

    frame = DetectionFrame(
        image=np.zeros((10, 10, 3), dtype=np.uint8),
        people=(person,),
    )

    detector = MagicMock()
    detector.detect_in_video.return_value = [frame]

    counter = MagicMock()
    counter.register.return_value = {person: temp_zone}
    counter.counts = {"entrada": 1}

    with (
        patch.object(
            session,
            "PersonDetector",
            return_value=detector,
        ),
        patch.object(
            session,
            "ZoneCounter",
            return_value=counter,
        ),
    ):
        result = session.run_detection(
            device="cpu",
            zones=(temp_zone,),
            video_path="video.mp4",
            model_path="model.pt",
        )

    detector.detect_in_video.assert_called_once_with("video.mp4")
    counter.register.assert_called_once_with(frame.people)
    assert result.processed_frames == 1
    assert result.detected_people == 1
    assert result.detections_by_zone == {"entrada": 1}

# -----------------------------------------------------
