from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from vision.src.modules.counting import ZoneCounter
from vision.src.modules.detection import PersonDetector
from vision.src.modules.zones import RoiZone


@dataclass(frozen=True)
class VideoSession:
    """Representa las metricas generadas durante una sesion de video"""

    started_at: datetime
    finished_at: datetime
    processed_frames: int
    detected_people: int
    tracked_people: int
    untracked_detections: int
    visits_by_zone: dict[str, int]


def run_detection(
    device: str,
    zones: Sequence[RoiZone],
    video_source: str | int = "vision/data/demo/supermarket.mp4",
    model_path: str = "yolov8n.pt",
    confidence: float = 0.25,
    tracker_path: str = "vision/config/bytetrack.yaml",
    image_size: int = 640,
    video_stride: int = 1,
) -> VideoSession:
    """Procesa un video y obtiene las metricas de deteccion por zona"""

    detector = PersonDetector(
        model_path=model_path,
        device=device,
        confidence=confidence,
        tracker_path=tracker_path,
        image_size=image_size,
        video_stride=video_stride,
    )
    counter = ZoneCounter(zones)

    started_at = datetime.now(UTC)
    processed_frames = 0
    detected_people = 0
    tracked_people_ids: set[int] = set()
    untracked_detections = 0

    for frame in detector.detect_in_video(video_source):
        processed_frames += 1
        detected_people += len(frame.people)

        for person in frame.people:
            if person.track_id is None:
                untracked_detections += 1
                continue

            tracked_people_ids.add(person.track_id)

        counter.register(frame.people)

    session = VideoSession(
        started_at=started_at,
        finished_at=datetime.now(UTC),
        processed_frames=processed_frames,
        detected_people=detected_people,
        tracked_people=len(tracked_people_ids),
        untracked_detections=untracked_detections,
        visits_by_zone=counter.counts,
    )

    return session
