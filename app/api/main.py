"""Pillar 1 & Pillar 2 Application Factory: Modular FastAPI REST API + Mounted FastMCP SSE Server."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    admin,
    complaints,
    health,
    simulation,
    tickets,
    webhooks,
)
from app.config import settings
from app.mcp.server import mount_mcp_into_fastapi


def create_app() -> FastAPI:
    """Builds the unified FastAPI + FastMCP ASGI application."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Tri-Pillar Sandbox API & FastMCP Server for Social Housing & Property Complaint "
            "Classification using TypeSafe Jev and M3NHF Schedule of Rates (SOR) codes."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Pillar 1 Modular REST Routers under /api/v1
    api_prefix = "/api/v1"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(complaints.router, prefix=api_prefix)
    app.include_router(webhooks.router, prefix=api_prefix)
    app.include_router(simulation.router, prefix=api_prefix)
    app.include_router(tickets.router, prefix=api_prefix)
    app.include_router(admin.router, prefix=api_prefix)

    # Mount Pillar 2 FastMCP Server at /mcp (with POST /mcp/sse -> 404 safeguard registered first)
    mount_mcp_into_fastapi(app)

    return app


app = create_app()
