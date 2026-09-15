from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse

from app.src.routers import cameras, stores
from app.src.routers.analytics import router as analytics_router
from app.src.routers.health import router as health_router
from app.src.routers.sessions import router as sessions_router

tags_metadata = [
    {
        "name": "Stores",
        "description": "Registro, consulta, actualización y desactivación de tiendas.",
    },
    {
        "name": "Cameras",
        "description": "Administración de cámaras vinculadas a cada tienda.",
    },
    {
        "name": "Sessions",
        "description": "Rastreo del ciclo de vida de sesiones de procesamiento de video.",
    },
    {
        "name": "Analytics",
        "description": "Ingesta y consulta de eventos de detección de personas.",
    },
    {
        "name": "Health",
        "description": "Estado del servicio y conectividad con la base de datos.",
    },
]

app = FastAPI(
    title="Retailo Analytics API",
    description="API de ingesta y procesamiento para analítica de tiendas.",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.include_router(health_router)
app.include_router(stores.router)
app.include_router(cameras.router)
app.include_router(sessions_router)
app.include_router(analytics_router)


def custom_openapi() -> dict[str, Any]:
    """Conserva el orden de operaciones de Stores en la documentación."""
    if app.openapi_schema is not None:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
    )
    paths = schema["paths"]
    for path, order in {
        "/stores/": ("post", "get"),
        "/stores/{store_id}": ("get", "patch", "delete"),
    }.items():
        operations = paths[path]
        paths[path] = {method: operations[method] for method in order if method in operations}

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # type: ignore[method-assign]


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redirige a la documentación interactiva de la API."""
    return RedirectResponse(url="/docs")
