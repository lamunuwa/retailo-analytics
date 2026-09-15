from collections.abc import Callable, Sequence
from time import monotonic

from vision.src.modules.detection import PersonDetection
from vision.src.modules.zones import RoiZone


class ZoneCounter:
    """Registra visitas y permanencia por zona"""

    def __init__(
        self,
        zones: Sequence[RoiZone],
        track_ttl_seconds: float = 300.0,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        """Inicializa el contador de zonas"""
        if not zones:
            raise ValueError("Se requiere al menos una zona ROI")
        if track_ttl_seconds <= 0:
            raise ValueError("El TTL de los tracks debe ser mayor que cero")

        self.zones = tuple(zones)
        self.track_ttl_seconds = track_ttl_seconds
        self.clock = clock
        self.track_last_seen: dict[int, float] = {}
        self.track_zone: dict[int, str | None] = {}
        self.visits_by_zone = {zone.name: 0 for zone in self.zones}
        self.dwell_seconds_by_zone = {zone.name: 0.0 for zone in self.zones}

    @property
    def counts(self) -> dict[str, int]:
        """Obtiene las visitas acumuladas"""

        self.purge_expired(self.clock())
        return dict(self.visits_by_zone)

    @property
    def dwell_seconds(self) -> dict[str, float]:
        """Obtiene la permanencia acumulada"""
        return dict(self.dwell_seconds_by_zone)

    def purge_expired(self, now: float) -> None:
        """Elimina tracks que superaron el TTL"""

        expiration_time = now - self.track_ttl_seconds
        expired_track_ids = [
            track_id
            for track_id, last_seen in self.track_last_seen.items()
            if last_seen < expiration_time
        ]
        for track_id in expired_track_ids:
            del self.track_last_seen[track_id]
            del self.track_zone[track_id]

    def find_person_zone(self, person: PersonDetection) -> RoiZone | None:
        """Busca la zona que contiene a una persona detectada"""

        for zone in self.zones:
            if zone.contains(person.floor_position):
                return zone

        return None

    def register(
        self,
        people: Sequence[PersonDetection],
        now: float | None = None,
    ) -> dict[PersonDetection, RoiZone | None]:
        """Registra las personas de un frame y devuelve sus zonas"""

        observed_at = self.clock() if now is None else now
        self.purge_expired(observed_at)
        assignments: dict[PersonDetection, RoiZone | None] = {}

        for person in people:
            assigned_zone = self.find_person_zone(person)
            assignments[person] = assigned_zone

            if person.track_id is None:
                continue

            previous_seen = self.track_last_seen.get(person.track_id)
            previous_zone = self.track_zone.get(person.track_id)
            assigned_name = assigned_zone.name if assigned_zone is not None else None
            if previous_seen is not None and previous_zone is not None:
                self.dwell_seconds_by_zone[previous_zone] += max(0.0, observed_at - previous_seen)
            if assigned_name is not None and assigned_name != previous_zone:
                self.visits_by_zone[assigned_name] += 1
            self.track_last_seen[person.track_id] = observed_at
            self.track_zone[person.track_id] = assigned_name

        return assignments

    def snapshot(self, now: float) -> tuple[dict[str, int], dict[str, float]]:
        """Obtiene una copia consistente de las metricas"""

        self.purge_expired(now)
        for track_id, zone_name in self.track_zone.items():
            if zone_name is not None:
                self.dwell_seconds_by_zone[zone_name] += max(
                    0.0, now - self.track_last_seen[track_id]
                )
                self.track_last_seen[track_id] = now
        return dict(self.visits_by_zone), dict(self.dwell_seconds_by_zone)
