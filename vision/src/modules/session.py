from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from vision.src.modules.counting import ZoneCounter
from vision.src.modules.detection import PersonDetector
from vision.src.modules.visualization import DetectionVisualizer
from vision.src.modules.zones import RoiZone


@dataclass(frozen=True)
class VideoSession:
    """Son las metricas generadas durante una sesion (rep del video)"""

    started_at: datetime
    finished_at: datetime
    processed_frames: int
    detected_people: int
    detections_by_zone: dict[str, int]


def run_detection(
    device: str,
    zones: Sequence[RoiZone],
    video_path: str = "vision/data/demo/supermarket.mp4", # gitignorado
    model_path: str = "yolov8n.pt", # gitignorado
) -> VideoSession:
    """Corre la deteccion de personas"""

    detector = PersonDetector(
        model_path=model_path,
        device=device,
    )
    counter = ZoneCounter(zones)
    visualizer = DetectionVisualizer(zones)

    started_at = datetime.now(UTC)
    processed_frames = 0
    detected_people = 0

    try:
        for frame in detector.detect_in_video(video_path):
            processed_frames += 1
            detected_people += len(frame.people)

            assignments = counter.register(frame.people)
            should_exit = visualizer.show(
                frame,
                assignments,
                counter.counts,
            )

            if should_exit:
                break

    finally:
        visualizer.close()

    session = VideoSession(
        started_at=started_at,
        finished_at=datetime.now(UTC),
        processed_frames=processed_frames,
        detected_people=detected_people,
        detections_by_zone=counter.counts,
    )

    return session
