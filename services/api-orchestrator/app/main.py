"""FastAPI application entry point for the API Layer domain."""

from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.signals import router as signals_router

app = FastAPI(title="Investment Platform API Orchestrator")
app.include_router(health_router)
app.include_router(signals_router)
