from collections.abc import Sequence

from vision.src.modules.detection import PersonDetection
from vision.src.modules.zones import RoiZone


class ZoneCounter:
    """Zonas ROI y acumula conteos por zona"""

    def __init__(self, zones: Sequence[RoiZone]) -> None:
        if not zones:
            raise ValueError("Se requiere al menos una zona ROI")

        self.zones = tuple(zones)
        self.counts_by_zone = {zone.name: 0 for zone in self.zones}

    @property
    def counts(self) -> dict[str, int]:
        """Genera una copia de los conteos acumulados por zona"""

        return self.counts_by_zone.copy()

    # funciones de apoyo ---------------------------------------

    def find_person_zone(
        self,
        person: PersonDetection,
    ) -> RoiZone | None:
        """Obtiene la primera zona que contiene a la persona detectada"""

        for zone in self.zones:
            if zone.contains(person.floor_position):
                return zone

        return None

    def register(
        self,
        people: Sequence[PersonDetection],
    ) -> dict[PersonDetection, RoiZone | None]:
        """Registra las detecciones por frame y devuelve sus zonas"""

        assignments: dict[PersonDetection, RoiZone | None] = {}

        for person in people:
            assigned_zone = self.find_person_zone(person)

            assignments[person] = assigned_zone

            if assigned_zone is not None:
                self.counts_by_zone[assigned_zone.name] += 1

        return assignments

    # ----------------------------------------------------------
