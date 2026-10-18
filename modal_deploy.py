"""Serverless Modal Deployment Specification for the Tri-Pillar Complaint Classifier Sandbox."""

import os
import subprocess
import modal

app = modal.App("social-housing-complaint-classifier-sandbox")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "fastapi>=0.115.0",
        "uvicorn>=0.30.0",
        "fastmcp>=0.4.0",
        "mcp[cli]>=1.2.0",
        "httpx>=0.27.0",
        "requests>=2.32.0",
        "pydantic>=2.9.0",
        "pillow>=10.4.0",
        "streamlit>=1.40.0",
        "pandas>=2.2.0",
        "python-dotenv>=1.0.1",
    )
    .add_local_python_source("app")
)

SECRETS = [modal.Secret.from_name("complaint-sandbox-secrets", required=False)]


# 1. Public FastAPI REST API & Mounted FastMCP SSE Service
@app.function(image=image, secrets=SECRETS, scaledown_window=120)
@modal.concurrent(max_inputs=50)
@modal.asgi_app()
def api():
    from app.api.main import app as fastapi_app

    return fastapi_app


# 2. Public Streamlit Visual Control Deck (max_containers=1 for sticky WebSocket session routing)
@app.function(image=image, secrets=SECRETS, max_containers=1, scaledown_window=300)
@modal.concurrent(max_inputs=50)
@modal.web_server(8501)
def dashboard():
    api_root_url = api.get_web_url().rstrip("/")
    env = os.environ.copy()
    env["SANDBOX_API_BASE"] = f"{api_root_url}/api/v1"
    env["SANDBOX_MCP_URL"] = f"{api_root_url}/mcp/sse"

    subprocess.Popen(
        [
            "streamlit",
            "run",
            "app/ui/dashboard_app.py",
            "--server.port",
            "8501",
            "--server.address",
            "0.0.0.0",
            "--server.headless",
            "true",
            "--server.enableCORS",
            "false",
        ],
        env=env,
    )


# 3. Scheduled Automation Cron (Weekly Inactive Session Pruning & Open-Data Sweep)
@app.function(image=image, secrets=SECRETS, schedule=modal.Cron("0 6 * * 1"))
async def scheduled_pulse():
    from app.storage.session_store import session_store

    pruned = session_store.prune_expired_sessions()
    return {"pruned_sessions": pruned}
