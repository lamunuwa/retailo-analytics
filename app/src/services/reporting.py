from datetime import datetime
from typing import cast

from app.src.repos.reporting import ReportingRepositoryProtocol
from app.src.schemas.reporting import (
    AnalyticsSummary,
    Insight,
    InsightType,
    TopZone,
    TrafficMetric,
)

SUGGESTIONS = {
    "HIGH_TRAFFIC_LOW_SALES": "Revisar disponibilidad, precio, promociones o acomodo de productos",
    "LOW_TRAFFIC_HIGH_SALES": "Mantener la oferta y probar senalizacion para atraer mas trafico",
    "LOW_TRAFFIC_LOW_SALES": "Reevaluar surtido, visibilidad y uso del espacio de esta zona",
    "HIGH_TRAFFIC_HIGH_SALES": "Mantener la estrategia y asegurar inventario suficiente",
}


class StoreAnalyticsService:
    """Genera analitica de una tienda"""

    def __init__(self, repo: ReportingRepositoryProtocol) -> None:
        """Inicializa el servicio con un repositorio"""
        self.repo = repo

    def has_store(self, store_id: int) -> bool:
        """Indica si una tienda existe"""
        return self.repo.get_store_by_id(store_id) is not None

    def traffic(
        self,
        store_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[TrafficMetric]:
        """Calcula el trafico y las ventas por zona"""
        zones = self.repo.get_all_zones_by_store(store_id)
        results = self.repo.get_all_results_by_store(store_id, start_date, end_date)
        sales = self.repo.get_all_sales_by_store(store_id, start_date, end_date)
        visits = {zone.id: 0 for zone in zones}
        dwell = {zone.id: 0.0 for zone in zones}
        units = {zone.id: 0 for zone in zones}
        revenue = {zone.id: 0.0 for zone in zones}

        for result in results:
            for metric in result.zone_metrics:
                if metric.zone_id in visits:
                    visits[metric.zone_id] += metric.visits
                    dwell[metric.zone_id] += metric.dwell_seconds
        for record in sales:
            if record.zone_id in units:
                units[record.zone_id] += record.units_sold
                revenue[record.zone_id] += record.revenue

        total_visits = sum(visits.values())
        total_units = sum(units.values())
        return [
            TrafficMetric(
                zone_id=zone.id,
                zone_name=zone.name,
                zone_type=zone.zone_type,
                visits=visits[zone.id],
                dwell_seconds=round(dwell[zone.id], 2),
                traffic_share=(
                    round(visits[zone.id] * 100 / total_visits, 2) if total_visits else 0.0
                ),
                units_sold=units[zone.id],
                revenue=round(revenue[zone.id], 2),
                sales_share=(
                    round(units[zone.id] * 100 / total_units, 2) if total_units else 0.0
                ),
            )
            for zone in zones
        ]

    def summary(
        self,
        store_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> AnalyticsSummary:
        """Genera el resumen analitico de una tienda"""
        results = self.repo.get_all_results_by_store(store_id, start_date, end_date)
        traffic = self.traffic(store_id, start_date, end_date)
        top = max(traffic, key=lambda metric: metric.visits, default=None)
        return AnalyticsSummary(
            store_id=store_id,
            total_sessions=len(results),
            processed_frames=sum(result.processed_frames for result in results),
            detected_people=sum(result.detected_people for result in results),
            total_visits=sum(metric.visits for metric in traffic),
            total_dwell_seconds=round(sum(metric.dwell_seconds for metric in traffic), 2),
            total_units_sold=sum(metric.units_sold for metric in traffic),
            total_revenue=round(sum(metric.revenue for metric in traffic), 2),
            top_zone=(
                TopZone(zone_id=top.zone_id, zone_name=top.zone_name, visits=top.visits)
                if top is not None and top.visits > 0
                else None
            ),
        )

    def insights(
        self,
        store_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Insight]:
        """Genera hallazgos por zona"""
        traffic = self.traffic(store_id, start_date, end_date)
        if not traffic:
            return []
        threshold = 100 / len(traffic)
        output: list[Insight] = []
        for metric in traffic:
            traffic_level = "HIGH" if metric.traffic_share >= threshold else "LOW"
            sales_level = "HIGH" if metric.sales_share >= threshold else "LOW"
            insight_type = f"{traffic_level}_TRAFFIC_{sales_level}_SALES"
            output.append(
                Insight(
                    type=cast(InsightType, insight_type),
                    zone_id=metric.zone_id,
                    zone_name=metric.zone_name,
                    message=(
                        f"La zona {metric.zone_name} concentra {metric.traffic_share:.2f}% "
                        f"de las visitas y {metric.sales_share:.2f}% de las unidades vendidas"
                    ),
                    suggestion=SUGGESTIONS[insight_type],
                    traffic_share=metric.traffic_share,
                    sales_share=metric.sales_share,
                )
            )
        return output
