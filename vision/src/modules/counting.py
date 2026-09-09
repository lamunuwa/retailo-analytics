from collections.abc import Callable, Sequence
from time import monotonic

from vision.src.modules.detection import PersonDetection
from vision.src.modules.zones import RoiZone


class ZoneCounter:
    """Registra los tracks activos recientemente en las zonas ROI.

    Los IDs de ByteTrack se olvidan después de ``track_ttl_seconds`` sin ser
    vistos. Esto evita que una cámara que opera continuamente conserve todos
    los IDs que el tracker haya generado desde su inicio.
    """

    def __init__(
        self,
        zones: Sequence[RoiZone],
        track_ttl_seconds: float = 300.0,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if not zones:
            raise ValueError("Se requiere al menos una zona ROI")
        if track_ttl_seconds <= 0:
            raise ValueError("El TTL de los tracks debe ser mayor que cero")

        self.zones = tuple(zones)
        self.track_ttl_seconds = track_ttl_seconds
        self.clock = clock
        self.track_last_seen_by_zone: dict[str, dict[int, float]] = {
            zone.name: {} for zone in self.zones
        }

    @property
    def counts(self) -> dict[str, int]:
        """Obtiene los tracks activos recientemente por zona."""

        self.purge_expired(self.clock())

        counts_by_zone = {
            zone_name: len(last_seen_by_track)
            for zone_name, last_seen_by_track in self.track_last_seen_by_zone.items()
        }

        return counts_by_zone

    # Funciones de apoyo ---------------------------------------

    def purge_expired(self, now: float) -> None:
        """Elimina tracks que llevan más del TTL configurado sin aparecer."""

        expiration_time = now - self.track_ttl_seconds
        for last_seen_by_track in self.track_last_seen_by_zone.values():
            expired_track_ids = [
                track_id
                for track_id, last_seen in last_seen_by_track.items()
                if last_seen < expiration_time
            ]
            for track_id in expired_track_ids:
                del last_seen_by_track[track_id]

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

            if assigned_zone is not None and person.track_id is not None:
                self.track_last_seen_by_zone[assigned_zone.name][person.track_id] = observed_at

        return assignments

    # ----------------------------------------------------------
