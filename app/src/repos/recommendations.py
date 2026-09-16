from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.src.models.recommendations import RecommendationModel
from app.src.schemas.reporting import Insight


class RecommendationRepositoryProtocol(Protocol):
    """Define las operaciones de recomendaciones"""

    def create(self, store_id: int, insights: list[Insight]) -> list[RecommendationModel]:
        """Crea las recomendaciones que aun no existen"""
        ...

    def get_all_by_store(
        self, store_id: int, status: str | None
    ) -> list[RecommendationModel]:
        """Obtiene las recomendaciones de una tienda"""
        ...

    def get_by_id(self, recommendation_id: int) -> RecommendationModel | None:
        """Obtiene una recomendacion por identificador"""
        ...

    def update(
        self, recommendation: RecommendationModel, status: str
    ) -> RecommendationModel:
        """Actualiza el estado de una recomendacion"""
        ...


class RecommendationRepository:
    """Gestiona la persistencia de recomendaciones"""

    def __init__(self, session: Session) -> None:
        """Inicializa el repositorio con una sesion"""
        self.session = session

    def create(self, store_id: int, insights: list[Insight]) -> list[RecommendationModel]:
        """Crea las recomendaciones que aun no existen"""
        existing_stmt = select(RecommendationModel).where(
            RecommendationModel.store_id == store_id,
            RecommendationModel.status == "pending",
        )
        existing = {
            (item.zone_id, item.insight_type): item
            for item in self.session.scalars(existing_stmt).all()
        }
        recommendations: list[RecommendationModel] = []
        for insight in insights:
            key = (insight.zone_id, insight.type)
            recommendation = existing.get(key)
            if recommendation is None:
                recommendation = RecommendationModel(
                    store_id=store_id,
                    zone_id=insight.zone_id,
                    zone_name=insight.zone_name,
                    insight_type=insight.type,
                    message=insight.message,
                    suggestion=insight.suggestion,
                )
                self.session.add(recommendation)
            recommendations.append(recommendation)
        self.session.commit()
        for recommendation in recommendations:
            self.session.refresh(recommendation)
        return recommendations

    def get_all_by_store(
        self, store_id: int, status: str | None
    ) -> list[RecommendationModel]:
        """Obtiene las recomendaciones de una tienda"""
        stmt = select(RecommendationModel).where(RecommendationModel.store_id == store_id)
        if status is not None:
            stmt = stmt.where(RecommendationModel.status == status)
        stmt = stmt.order_by(RecommendationModel.created_at.desc(), RecommendationModel.id.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, recommendation_id: int) -> RecommendationModel | None:
        """Obtiene una recomendacion por identificador"""
        return self.session.get(RecommendationModel, recommendation_id)

    def update(
        self, recommendation: RecommendationModel, status: str
    ) -> RecommendationModel:
        """Actualiza el estado de una recomendacion"""
        recommendation.status = status
        self.session.commit()
        self.session.refresh(recommendation)
        return recommendation
