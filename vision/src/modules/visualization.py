from collections.abc import Sequence

import cv2
import numpy as np

from vision.src.modules.detection import DetectionFrame, PersonDetection
from vision.src.modules.zones import RoiZone

WINDOW_NAME = "Deteccion de personas por zona"


class DetectionVisualizer:
    """Dibuja zonas, conteos y detecciones sobre la ventana de OpenCV."""

    def __init__(self, zones: Sequence[RoiZone]) -> None:
        self.zones = tuple(zones)

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    def show(
        self,
        frame: DetectionFrame,
        assignments: dict[PersonDetection, RoiZone | None],
        zone_counts: dict[str, int],
    ) -> bool:
        """Muestra el frame y devuelve si se solicito salir con la tecla q."""

        image = frame.image

        self.draw_heatmap(image, zone_counts)
        self.draw_people(image, assignments)

        cv2.imshow(WINDOW_NAME, image)

        should_exit = cv2.waitKey(1) & 0xFF == ord("q")
        return should_exit

    def close(self) -> None:
        """Cierra las ventanas creadas por OpenCV."""

        cv2.destroyAllWindows()

    # funciones de apoyo ---------------------------------------

    def draw_heatmap(
        self,
        image: np.ndarray,
        zone_counts: dict[str, int],
    ) -> None:
        """Dibuja cada zona con intensidad proporcional a su conteo."""

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
        """Dibuja personas y etiqueta la zona asignada a cada una."""

        for person, zone in assignments.items():
            color = (0, 255, 0) if zone is not None else (0, 0, 255)
            label = zone.name if zone is not None else "sin zona"

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
