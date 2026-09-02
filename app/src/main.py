from fastapi import FastAPI
from app.src.routers import stores

app = FastAPI(title="RetaiLO Analytics")

app.include_router(stores.router)