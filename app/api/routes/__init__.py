"""Modular FastAPI route collection."""

from app.api.routes import (
    admin,
    complaints,
    health,
    simulation,
    tickets,
    webhooks,
)

__all__ = [
    "admin",
    "complaints",
    "health",
    "simulation",
    "tickets",
    "webhooks",
]
