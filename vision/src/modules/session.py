from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from time import monotonic

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
    video_source: str | int,
    model_path: str = "yolov8n.pt",
    confidence: float = 0.25,
    tracker_path: str = "vision/config/bytetrack.yaml",
    image_size: int = 640,
    video_stride: int = 1,
    track_ttl_seconds: float = 300.0,
    clock: Callable[[], float] = monotonic,
) -> VideoSession:
    """Procesa un video y obtiene métricas de tracks vistos recientemente.

    ``track_ttl_seconds`` limita la retención en memoria de los IDs generados
    por ByteTrack; por tanto, los conteos representan la ventana activa más
    reciente y no una colección ilimitada desde el arranque del proceso.
    """

    if track_ttl_seconds <= 0:
        raise ValueError("El TTL de los tracks debe ser mayor que cero")

    detector = PersonDetector(
        model_path=model_path,
        device=device,
        confidence=confidence,
        tracker_path=tracker_path,
        image_size=image_size,
        video_stride=video_stride,
    )
    counter = ZoneCounter(
        zones,
        track_ttl_seconds=track_ttl_seconds,
        clock=clock,
    )

    started_at = datetime.now(UTC)
    processed_frames = 0
    detected_people = 0
    tracked_people_last_seen: dict[int, float] = {}
    untracked_detections = 0

    for frame in detector.detect_in_video(video_source):
        observed_at = clock()
        expiration_time = observed_at - track_ttl_seconds
        tracked_people_last_seen = {
            track_id: last_seen
            for track_id, last_seen in tracked_people_last_seen.items()
            if last_seen >= expiration_time
        }
        processed_frames += 1
        detected_people += len(frame.people)

        for person in frame.people:
            if person.track_id is None:
                untracked_detections += 1
                continue

            tracked_people_last_seen[person.track_id] = observed_at

        counter.register(frame.people, now=observed_at)

    session = VideoSession(
        started_at=started_at,
        finished_at=datetime.now(UTC),
        processed_frames=processed_frames,
        detected_people=detected_people,
        tracked_people=len(tracked_people_last_seen),
        untracked_detections=untracked_detections,
        visits_by_zone=counter.counts,
    )

    return session
