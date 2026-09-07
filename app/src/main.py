from fastapi import FastAPI

from app.src.routers import stores

from app.src.routers import cameras

app = FastAPI(title="Retailo Analytics API")

app.include_router(stores.router)

app.include_router(cameras.router)