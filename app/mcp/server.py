"""FastMCP Server assembly and direct FastAPI process mounting."""

import inspect
from typing import Any
from fastapi import FastAPI

from app.mcp.resources import register_mcp_resources
from app.mcp.security import (
    MCP_TRANSPORT_SECURITY,
    register_mcp_sse_post_fallback,
)
from app.mcp.tools import register_mcp_tools


def build_mcp_server() -> Any:
    """Creates and configures the FastMCP / MCPServer instance with resources and tools."""
    try:
        from mcp.server.mcpserver import MCPServer as FastMCPClass
    except ImportError:
        try:
            from mcp.server.fastmcp import FastMCP as FastMCPClass  # type: ignore[no-redef]
        except ImportError:
            from fastmcp import FastMCP as FastMCPClass  # type: ignore[no-redef]

    init_sig = inspect.signature(FastMCPClass.__init__)
    kwargs: dict[str, Any] = {}
    if "transport_security" in init_sig.parameters and MCP_TRANSPORT_SECURITY is not None:
        kwargs["transport_security"] = MCP_TRANSPORT_SECURITY

    mcp = FastMCPClass("Social-Housing-SOR-Triage-Sandbox", **kwargs)
    register_mcp_resources(mcp)
    register_mcp_tools(mcp)
    return mcp


mcp_server = build_mcp_server()


def mount_mcp_into_fastapi(app: FastAPI) -> None:
    """Mounts FastMCP SSE app directly at /mcp with Gotcha A (421) and Gotcha B (405 -> 404) safeguards."""
    # Register explicit POST /mcp/sse -> 404 handler BEFORE mounting /mcp
    register_mcp_sse_post_fallback(app)

    if hasattr(mcp_server, "sse_app"):
        sse_sig = inspect.signature(mcp_server.sse_app)
        if "transport_security" in sse_sig.parameters and MCP_TRANSPORT_SECURITY is not None:
            sse_asgi = mcp_server.sse_app(transport_security=MCP_TRANSPORT_SECURITY)
        else:
            sse_asgi = mcp_server.sse_app()
    else:
        sse_asgi = mcp_server.http_app(
            path="/sse",
            transport="sse",
            allowed_hosts=MCP_TRANSPORT_SECURITY.allowed_hosts if MCP_TRANSPORT_SECURITY else None,
            allowed_origins=MCP_TRANSPORT_SECURITY.allowed_origins if MCP_TRANSPORT_SECURITY else None,
        )

    app.mount("/mcp", sse_asgi)
