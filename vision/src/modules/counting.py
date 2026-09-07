from collections.abc import Sequence

from vision.src.modules.detection import PersonDetection
from vision.src.modules.zones import RoiZone


class ZoneCounter:
    """Registra zonas ROI y acumula los conteos de personas"""

    def __init__(self, zones: Sequence[RoiZone]) -> None:
        if not zones:
            raise ValueError("Se requiere al menos una zona ROI")

        self.zones = tuple(zones)
        self.track_ids_by_zone: dict[str, set[int]] = {
            zone.name: set()
            for zone in self.zones
        }

    @property
    def counts(self) -> dict[str, int]:
        """Obtiene una copia de los conteos acumulados por zona"""

        counts_by_zone = {
            zone_name: len(track_ids)
            for zone_name, track_ids in self.track_ids_by_zone.items()
        }

        return counts_by_zone

    # Funciones de apoyo ---------------------------------------

    def find_person_zone(self, person: PersonDetection) -> RoiZone | None:
        """Busca la zona que contiene a una persona detectada"""

        for zone in self.zones:
            if zone.contains(person.floor_position):
                return zone

        return None

    def register(
        self,
        people: Sequence[PersonDetection],
    ) -> dict[PersonDetection, RoiZone | None]:
        """Registra las personas de un frame y devuelve sus zonas"""

        assignments: dict[PersonDetection, RoiZone | None] = {}

        for person in people:
            assigned_zone = self.find_person_zone(person)
            assignments[person] = assigned_zone

            if assigned_zone is not None and person.track_id is not None:
                self.track_ids_by_zone[assigned_zone.name].add(person.track_id)

        return assignments

    # ----------------------------------------------------------
