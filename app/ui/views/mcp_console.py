"""Sandbox Tab 4: Embedded Option 2 MCP Agent Console (Browser-Based MCP Inspector & Client)."""

import asyncio
import json
import os
from typing import Any, Dict
import streamlit as st

from app.domain.presets import SCENARIO_PRESETS
from app.mcp.resources import get_latest_triage_json
from app.mcp.tools import (
    exec_approve_or_override_work_order,
    exec_get_latest_triage,
    exec_simulate_complaint_event,
    exec_submit_complaint_triage,
)


async def _try_live_sse_mcp_call(mcp_url: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Attempts a live SSE JSON-RPC handshake via mcp.client.sse.sse_client when uvicorn is running."""
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    async with sse_client(mcp_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_list = await session.list_tools()
            result = await session.call_tool(tool_name, arguments=arguments)
            return {
                "transport": f"LIVE_SSE ({mcp_url})",
                "discovered_tools": [t.name for t in tools_list.tools],
                "tool_called": tool_name,
                "arguments": arguments,
                "result": [c.model_dump() if hasattr(c, "model_dump") else str(c) for c in result.content],
            }


def execute_embedded_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Executes an MCP tool via live SSE (/mcp/sse) if reachable, or falls back to direct in-process FastMCP tool execution."""
    mcp_url = os.environ.get("SANDBOX_MCP_URL", "http://127.0.0.1:8000/mcp/sse")
    try:
        return asyncio.run(_try_live_sse_mcp_call(mcp_url, tool_name, arguments))
    except Exception:
        # Fallback to direct FastMCP tool invocation when running Streamlit standalone
        if tool_name == "get_latest_triage":
            out = exec_get_latest_triage(**arguments)
        elif tool_name == "submit_complaint_triage":
            out = exec_submit_complaint_triage(**arguments)
        elif tool_name == "simulate_complaint_event":
            out = exec_simulate_complaint_event(**arguments)
        elif tool_name == "approve_or_override_work_order":
            out = exec_approve_or_override_work_order(**arguments)
        else:
            out = {"error": f"Unknown tool: {tool_name}"}

        return {
            "transport": "IN_PROCESS_FASTMCP_DIRECT (Start uvicorn on :8000 for live SSE socket)",
            "discovered_tools": [
                "get_latest_triage",
                "submit_complaint_triage",
                "simulate_complaint_event",
                "approve_or_override_work_order",
            ],
            "discovered_resources": [
                "sor://properties/prop_oak_01/latest-triage",
                "sor://properties/{property_id}/latest-triage",
            ],
            "tool_called": tool_name,
            "arguments": arguments,
            "result": out,
        }


def render_mcp_console_view(session_id: str) -> None:
    """Renders Pillar 3's Embedded Option 2 MCP Console and Option 1 Claude/Cursor connection guide."""
    st.markdown("### 🤖 Embedded MCP Agent Console (Pillar 2 Protocol Inspector)")
    st.caption(
        "Test Model Context Protocol (MCP) tool calls and resource lookups directly inside your browser "
        "**without needing Claude Desktop or Cursor installed** (Option 2), or copy the SSE bridge configuration "
        "for external AI agents (Option 1)."
    )

    col_opt2, col_opt1 = st.columns([0.62, 0.38], gap="large")

    with col_opt2:
        st.markdown("#### ⚡ Option 2: Interactive Browser MCP Tool & Resource Runner")
        action_type = st.radio(
            "Select MCP Operation Type",
            options=["CALL_TOOL", "READ_RESOURCE"],
            format_func=lambda k: (
                "🛠️ Call MCP Tool (tools/call)"
                if k == "CALL_TOOL"
                else "📄 Read MCP Resource (resources/read)"
            ),
            horizontal=True,
            key="mcp_console_op_radio",
        )

        if action_type == "CALL_TOOL":
            selected_tool = st.selectbox(
                "Select FastMCP Tool",
                options=[
                    "get_latest_triage",
                    "submit_complaint_triage",
                    "simulate_complaint_event",
                    "approve_or_override_work_order",
                ],
                key="mcp_console_tool_select",
            )

            tool_args: Dict[str, Any] = {"session_id": session_id}

            if selected_tool == "get_latest_triage":
                prop_id = st.selectbox(
                    "property_id",
                    options=["prop_oak_01", "prop_elm_02", "prop_cedar_03"],
                    key="mcp_arg_prop",
                )
                tool_args["property_id"] = prop_id

            elif selected_tool == "submit_complaint_triage":
                tool_args["property_id"] = st.selectbox(
                    "property_id",
                    options=["prop_oak_01", "prop_elm_02", "prop_cedar_03"],
                    key="mcp_submit_prop",
                )
                tool_args["complaint_text"] = st.text_input(
                    "complaint_text",
                    value="Kitchen cupboard door hinge snapped off, door hanging loose (see photo).",
                    key="mcp_submit_text",
                )
                tool_args["synthetic_image_preset"] = st.selectbox(
                    "synthetic_image_preset",
                    options=["broken_hinge", "sink_leak", "black_mould", "ceiling_light_leak", "cistern_valve", "inappropriate_placeholder"],
                    key="mcp_submit_preset",
                )

            elif selected_tool == "simulate_complaint_event":
                preset_ids = [p.preset_id for p in SCENARIO_PRESETS]
                tool_args["preset_id"] = st.selectbox(
                    "preset_id",
                    options=preset_ids,
                    key="mcp_sim_preset_id",
                )

            elif selected_tool == "approve_or_override_work_order":
                tool_args["ticket_id"] = st.text_input(
                    "ticket_id",
                    value="TKT-BASE-02",
                    key="mcp_approve_tkt_id",
                )
                tool_args["override_sor"] = st.text_input(
                    "override_sor (6-digit M3NHF code)",
                    value="112005",
                    key="mcp_approve_sor",
                )
                tool_args["surveyor_notes"] = st.text_input(
                    "surveyor_notes",
                    value="Confirmed 112005 via MCP Agent Actuator Tool",
                    key="mcp_approve_notes",
                )

            if st.button("Execute MCP Tool Call →", type="primary", use_container_width=True):
                st.session_state["last_mcp_console_output"] = execute_embedded_mcp_tool(
                    selected_tool, tool_args
                )

        else:
            resource_uri = st.selectbox(
                "Select Static or Dynamic MCP Resource URI",
                options=[
                    "sor://properties/prop_oak_01/latest-triage",
                    "sor://properties/prop_elm_02/latest-triage",
                    "sor://properties/prop_cedar_03/latest-triage",
                ],
                key="mcp_resource_uri_select",
            )
            if st.button("Read MCP Resource →", type="primary", use_container_width=True):
                prop_id = resource_uri.split("/")[3]
                raw_json = get_latest_triage_json(property_id=prop_id, session_id=session_id)
                st.session_state["last_mcp_console_output"] = {
                    "resource_uri": resource_uri,
                    "mime_type": "application/json",
                    "contents": json.loads(raw_json),
                }

        if st.session_state.get("last_mcp_console_output"):
            st.markdown("##### 📡 JSON-RPC / MCP Response Payload")
            st.json(st.session_state["last_mcp_console_output"])

    with col_opt1:
        st.markdown("#### 🔌 Option 1: External Agent Config (Claude Desktop / Cursor)")
        with st.container(border=True):
            st.markdown(
                "FastMCP is mounted directly inside FastAPI at `/mcp/sse` with **DNS Rebinding Protection (`HTTP 421` fix)** "
                "and an explicit **`POST /mcp/sse -> HTTP 404` negotiation handler** so `mcp-remote` cleanly falls back to `GET` SSE."
            )
            st.code(
                """{
  "mcpServers": {
    "housing-sor-triage": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://127.0.0.1:8000/mcp/sse",
        "--transport",
        "sse-only"
      ]
    }
  }
}""",
                language="json",
            )
            st.caption(
                "**Exposed Tools:**  \n"
                "- `get_latest_triage(property_id, session_id)`  \n"
                "- `submit_complaint_triage(complaint_text, ...)`  \n"
                "- `simulate_complaint_event(preset_id, session_id)`  \n"
                "- `approve_or_override_work_order(ticket_id, ...)`"
            )
