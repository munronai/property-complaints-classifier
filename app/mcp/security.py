"""MCP Cloud Networking & Transport Security Safeguards (Gotcha A: HTTP 421 & Gotcha B: HTTP 405 -> 404)."""

from fastapi import FastAPI, HTTPException

try:
    from mcp.server.transport_security import TransportSecuritySettings

    MCP_TRANSPORT_SECURITY = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "127.0.0.1",
            "127.0.0.1:*",
            "localhost",
            "localhost:*",
            "testserver",
            "testserver:*",
            "*.modal.run",
            "*.modal.run:*",
            "yourdomain.com",
            "yourdomain.com:*",
        ],
        allowed_origins=[
            "http://127.0.0.1:*",
            "http://localhost:*",
            "http://testserver",
            "https://*.modal.run",
            "https://yourdomain.com",
        ],
    )
except ImportError:  # pragma: no cover
    MCP_TRANSPORT_SECURITY = None


def register_mcp_sse_post_fallback(app: FastAPI) -> None:
    """Gotcha B Safeguard: Explicit dummy POST handler for /mcp/sse returning HTTP 404 instead of 405."""

    @app.post("/mcp/sse", include_in_schema=False)
    async def handle_mcp_sse_post() -> None:
        raise HTTPException(
            status_code=404,
            detail="The /mcp/sse endpoint requires HTTP GET. Pass '--transport sse-only' to mcp-remote.",
        )
