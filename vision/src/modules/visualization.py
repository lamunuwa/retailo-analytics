from collections.abc import Sequence

import cv2
import numpy as np

from vision.src.modules.detection import DetectionFrame, PersonDetection
from vision.src.modules.zones import RoiZone


class DetectionVisualizer:
    """Muestra zonas, conteos y personas detectadas mediante OpenCV"""

    def __init__(self, zones: Sequence[RoiZone]) -> None:
        self.zones = tuple(zones)

        cv2.namedWindow("Deteccion de personas por zona", cv2.WINDOW_NORMAL)

    def show(
        self,
        frame: DetectionFrame,
        assignments: dict[PersonDetection, RoiZone | None],
        zone_counts: dict[str, int],
    ) -> bool:
        """Muestra un frame y devuelve si se solicito salir"""

        image = frame.image

        if image is None:
            raise ValueError("El frame no contiene una imagen para visualizar")

        self.draw_heatmap(image, zone_counts)
        self.draw_people(image, assignments)

        cv2.imshow("Deteccion de personas por zona", image)

        should_exit = cv2.waitKey(1) & 0xFF == ord("q")
        return should_exit

    def close(self) -> None:
        """Cierra las ventanas creadas por OpenCV"""

        cv2.destroyAllWindows()

    # Funciones de apoyo ---------------------------------------

    def draw_heatmap(
        self,
        image: np.ndarray,
        zone_counts: dict[str, int],
    ) -> None:
        """Dibuja las zonas con intensidad basada en sus conteos"""

        highest_count = max(zone_counts.values(), default=0)
        overlay = image.copy()

        for zone in self.zones:
            zone_count = zone_counts[zone.name]
            intensity = zone_count / highest_count if highest_count else 0.0

            color = (
                0,
                int(80 + 175 * intensity),
                255,
            )

            cv2.fillPoly(overlay, [zone.contour], color)

            cv2.polylines(
                image,
                [zone.contour],
                isClosed=True,
                color=color,
                thickness=2,
            )

            cv2.putText(
                image,
                f"{zone.name}: {zone_count}",
                tuple(zone.contour[0]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        cv2.addWeighted(
            overlay,
            0.25,
            image,
            0.75,
            0,
            image,
        )

    @staticmethod
    def draw_people(
        image: np.ndarray,
        assignments: dict[PersonDetection, RoiZone | None],
    ) -> None:
        """Dibuja personas y la zona asignada a cada una"""

        for person, zone in assignments.items():
            color = (0, 255, 0) if zone is not None else (0, 0, 255)
            zone_label = zone.name if zone is not None else "sin zona"
            track_label = (
                f"ID {person.track_id}"
                if person.track_id is not None
                else "sin track"
            )
            label = f"{track_label} - {zone_label}"

            cv2.rectangle(
                image,
                (int(person.x1), int(person.y1)),
                (int(person.x2), int(person.y2)),
                color,
                2,
            )

            cv2.putText(
                image,
                label,
                (int(person.x1), max(int(person.y1) - 8, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

    # ----------------------------------------------------------
