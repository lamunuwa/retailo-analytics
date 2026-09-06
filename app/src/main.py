from fastapi import FastAPI

from app.src.routers.analytics import router as analytics_router

app = FastAPI(
    title="Retailo Analytics API",
    description="API de ingesta y procesamiento para analítica de tiendas.",
    version="1.0.0",
)

app.include_router(analytics_router)


@app.get("/", tags=["Healthcheck"])
def root() -> dict[str, str]:
    """Endpoint de verificación de estado del servidor."""
    return {"status": "online"}
from app.src.routers import stores

app = FastAPI(title="RetaiLO Analytics")

app.include_router(stores.router)
