from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO


@dataclass(frozen=True)
class PersonDetection:
    """Representa una persona detectada en un frame"""

    x1: float
    y1: float
    x2: float
    y2: float
    track_id: int | None = None

    @property
    def floor_position(self) -> tuple[float, float]:
        """Obtiene el punto inferior central de la persona"""

        center_x = (self.x1 + self.x2) / 2
        floor_y = self.y2

        return center_x, floor_y


@dataclass(frozen=True)
class DetectionFrame:
    """Representa una imagen y las personas detectadas en un frame"""

    image: np.ndarray | None
    people: tuple[PersonDetection, ...]


class PersonDetector:
    """Crea un detector de personas mediante YOLO"""

    def __init__(
        self,
        model_path: str,
        device: str,
        tracker_path: str = "vision/config/bytetrack.yaml",
        confidence: float = 0.25,
        image_size: int = 640,
        video_stride: int = 1,
        include_image: bool = False,
    ) -> None:
        self.model = YOLO(model_path)
        self.device = device
        self.tracker_path = tracker_path
        self.confidence = confidence
        self.image_size = image_size
        self.video_stride = video_stride
        self.include_image = include_image

    def detect_in_video(
        self,
        video_path: str,
    ) -> Iterator[DetectionFrame]:
        """Procesa un video y devuelve cada frame con sus personas detectadas"""

        results = self.model.track(
            source=video_path,
            stream=True,
            persist=True,
            tracker=self.tracker_path,
            classes=[0],
            conf=self.confidence,
            device=self.device,
            imgsz=self.image_size,
            vid_stride=self.video_stride,
            stream_buffer=False,
            verbose=False,
        )

        for result in results:
            original_image = getattr(result, "orig_img", None)

            if original_image is None:
                continue

            boxes = getattr(result, "boxes", None)
            coordinates = [] if boxes is None else boxes.xyxy.cpu().tolist()
            track_ids_tensor = None if boxes is None else getattr(boxes, "id", None)
            track_ids = (
                []
                if track_ids_tensor is None
                else track_ids_tensor.int().cpu().tolist()
            )

            people: list[PersonDetection] = []

            for index, box in enumerate(coordinates):
                track_id = (
                    int(track_ids[index])
                    if index < len(track_ids)
                    else None
                )

                person = PersonDetection(
                    x1=box[0],
                    y1=box[1],
                    x2=box[2],
                    y2=box[3],
                    track_id=track_id,
                )
                people.append(person)

            image = (
                np.asarray(original_image).copy()
                if self.include_image
                else None
            )

            detection_frame = DetectionFrame(
                image=image,
                people=tuple(people),
            )

            yield detection_frame
