from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO


@dataclass(frozen=True)
class PersonDetection:
    """Representa una persona detectada"""

    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def floor_position(self) -> tuple[float, float]:
        """Obtiene el punto central de la box"""

        center_x = (self.x1 + self.x2) / 2
        floor_y = self.y2

        return center_x, floor_y


@dataclass(frozen=True)
class DetectionFrame:
    """Imagen y personas detectadas en un frame"""

    image: np.ndarray
    people: tuple[PersonDetection, ...]


class PersonDetector:
    """Procesa un YOLO y detecta personas en un video"""

    def __init__(
        self,
        model_path: str,
        device: str,
        confidence: float = 0.5,
    ) -> None:
        self.model = YOLO(model_path)
        self.device = device
        self.confidence = confidence

    def detect_in_video(self, video_path: str) -> Iterator[DetectionFrame]:
        """Procesa un video y produce cada frame con sus personas detectadas"""

        results = self.model.predict(
            source=video_path,
            stream=True,
            classes=[0],
            conf=self.confidence,
            device=self.device,
            verbose=False,
        )

        for result in results:
            original_image = getattr(result, "orig_img", None)

            if original_image is None:
                continue

            boxes = getattr(result, "boxes", None)
            coordinates = [] if boxes is None else boxes.xyxy.cpu().tolist()

            people = tuple(PersonDetection(*box) for box in coordinates)

            detection_frame = DetectionFrame(
                image=np.asarray(original_image).copy(),
                people=people,
            )

            yield detection_frame
