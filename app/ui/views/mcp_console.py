"""Dedicated Option 2 View: Interactive Browser MCP Agent Console."""

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
from app.ui.components.help_and_presets import PRESET_MCP_PROMPTS


async def _discover_mcp_primitives_live(mcp_url: str) -> Dict[str, Any]:
    """Connects over SSE to /mcp/sse and queries tools/list, resources/list, and resources/templates/list."""
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    async with sse_client(mcp_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_res = await session.list_tools()
            resources_res = await session.list_resources()
            templates_res = await session.list_resource_templates()
            return {
                "transport": f"LIVE_SSE ({mcp_url})",
                "tools": [
                    {"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
                    for t in tools_res.tools
                ],
                "resources": [
                    {"uri": str(r.uri), "name": r.name, "description": r.description}
                    for r in resources_res.resources
                ],
                "templates": [
                    {
                        "uriTemplate": str(rt.uriTemplate),
                        "name": rt.name,
                        "description": rt.description,
                    }
                    for rt in templates_res.resourceTemplates
                ],
            }


def discover_mcp_primitives() -> Dict[str, Any]:
    """Discovers MCP tools, resources, and templates over SSE or via in-process FastMCP metadata."""
    mcp_url = os.environ.get("SANDBOX_MCP_URL", "http://127.0.0.1:8000/mcp/sse")
    try:
        return asyncio.run(_discover_mcp_primitives_live(mcp_url))
    except Exception:
        return {
            "transport": "IN_PROCESS_FASTMCP_DIRECT (Start uvicorn on :8000 for live SSE socket)",
            "tools": [
                {
                    "name": "get_latest_triage",
                    "description": "Retrieve the latest multimodal Jev triage and M3NHF SOR decision for a property.",
                },
                {
                    "name": "submit_complaint_triage",
                    "description": "Run a resident or commercial repair complaint through the 4-stage Jev + M3NHF SOR pipeline.",
                },
                {
                    "name": "simulate_complaint_event",
                    "description": "Inject one of the 9 curated preset scenarios into the active session.",
                },
                {
                    "name": "approve_or_override_work_order",
                    "description": "Human-in-the-loop actuator: approve top SOR code or override with surveyor notes.",
                },
            ],
            "resources": [
                {
                    "uri": "sor://properties/prop_oak_01/latest-triage",
                    "name": "prop_oak_01_latest_triage",
                    "description": "Static MCP resource returning the latest triage record for Flat 4, Oak Court.",
                }
            ],
            "templates": [
                {
                    "uriTemplate": "sor://properties/{property_id}/latest-triage",
                    "name": "property_latest_triage_template",
                    "description": "Dynamic URI template returning the latest triage record for any property_id.",
                }
            ],
        }


async def _try_live_sse_mcp_call(mcp_url: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Attempts a live SSE JSON-RPC handshake via mcp.client.sse.sse_client when uvicorn is running."""
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    async with sse_client(mcp_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_list = await session.list_tools()
            result = await session.call_tool(tool_name, arguments=arguments)
            parsed_items = []
            for c in result.content:
                if hasattr(c, "text"):
                    try:
                        parsed_items.append(json.loads(c.text))
                    except Exception:
                        parsed_items.append(c.text)
                elif hasattr(c, "model_dump"):
                    parsed_items.append(c.model_dump())
                else:
                    parsed_items.append(str(c))
            return {
                "transport": f"LIVE_SSE ({mcp_url})",
                "discovered_tools": [t.name for t in tools_list.tools],
                "jsonrpc_method": "tools/call",
                "tool_called": tool_name,
                "arguments": arguments,
                "result": parsed_items[0] if len(parsed_items) == 1 else parsed_items,
            }


def execute_embedded_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Executes an MCP tool via live SSE (/mcp/sse) if reachable, or falls back to direct in-process FastMCP tool execution."""
    mcp_url = os.environ.get("SANDBOX_MCP_URL", "http://127.0.0.1:8000/mcp/sse")
    try:
        return asyncio.run(_try_live_sse_mcp_call(mcp_url, tool_name, arguments))
    except Exception:
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
            "jsonrpc_method": "tools/call",
            "tool_called": tool_name,
            "arguments": arguments,
            "result": out,
        }


def render_mcp_console_view(
    session_id: str,
    page_dashboard: Any = None,
    page_guide_claude: Any = None,
    page_guide_inspector: Any = None,
) -> None:
    """Renders Option 2: Interactive Browser MCP Agent Console modeled after the reference architecture."""
    mcp_url = os.environ.get("SANDBOX_MCP_URL", "http://127.0.0.1:8000/mcp/sse")

    top_col1, top_col2 = st.columns([0.70, 0.30])
    with top_col1:
        st.title("🤖 Interactive MCP Agent Console (Option 2)")
        st.markdown(
            "This page acts as a **live Model Context Protocol (MCP) Client** right in your browser. "
            "See the exact **natural-language prompt** a housing officer or AI agent uses, inspect the resulting "
            "**JSON-RPC 2.0 MCP call**, and watch it mutate your sandbox session in real time."
        )
    with top_col2:
        st.write("")
        if page_dashboard is not None:
            st.page_link(
                page_dashboard,
                label="Open Live Sandbox Dashboard →",
                icon="🎛️",
                use_container_width=True,
            )
        if page_guide_claude is not None:
            st.page_link(
                page_guide_claude,
                label="Option 1: Claude & Cursor Guide",
                icon="🖥️",
                use_container_width=True,
            )

    st.info(
        f"**Active Session Isolation:** `{session_id}` | **MCP SSE Endpoint:** `{mcp_url}`  \n"
        "Any preset or approval you trigger here updates the exact same property store visible on the **Live Sandbox Dashboard**."
    )

    col_left, col_right = st.columns([1, 1.35], gap="large")

    with col_left:
        st.subheader("1. Inspect Discovered MCP Primitives")
        st.caption(
            "Perform an MCP initialization handshake (`initialize` → `tools/list`, `resources/list`, `resources/templates/list`)."
        )
        if st.button(
            "🔄 Connect & Discover Server Capabilities",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Performing MCP handshake..."):
                st.session_state["mcp_discovered_schema"] = discover_mcp_primitives()
                st.toast("MCP Server capabilities discovered!", icon="🤖")

        schema = st.session_state.get("mcp_discovered_schema") or discover_mcp_primitives()
        st.caption(f"Transport: `{schema['transport']}`")

        t_tools, t_res, t_tmpl = st.tabs(
            [
                f"🛠️ Tools ({len(schema['tools'])})",
                f"📄 Static Resources ({len(schema['resources'])})",
                f"🔗 Dynamic Templates ({len(schema['templates'])})",
            ]
        )
        with t_tools:
            for t in schema["tools"]:
                with st.expander(f"**`{t['name']}`**", expanded=True):
                    st.write(t.get("description", ""))
        with t_res:
            for r in schema["resources"]:
                with st.expander(f"**`{r['uri']}`**", expanded=True):
                    st.caption(f"Name: `{r['name']}`")
                    st.write(r.get("description", ""))
        with t_tmpl:
            for rt in schema["templates"]:
                with st.expander(f"**`{rt['uriTemplate']}`**", expanded=True):
                    st.caption(f"Name: `{rt['name']}`")
                    st.write(rt.get("description", ""))

    with col_right:
        st.subheader("2. Execute Guided Agent Prompts & Preset Scenarios via MCP")
        st.caption(
            "Select an operation below to see **how a user prompts the AI agent**, **which MCP primitive the agent selects**, and **the live JSON-RPC response**."
        )

        guided_mode = st.selectbox(
            "Select Guided Agent Workflow",
            options=[
                "PRESET_SCENARIO",
                "READ_PROPERTY_RESOURCE",
                "CUSTOM_COMPLAINT_TOOL",
                "SURVEYOR_APPROVAL_TOOL",
            ],
            format_func=lambda k: {
                "PRESET_SCENARIO": "🎯 1. Trigger Any of the 9 Preset Scenarios via MCP (simulate_complaint_event)",
                "READ_PROPERTY_RESOURCE": "📄 2. Read Property Triage State via MCP Resource (sor://properties/{id}/latest-triage)",
                "CUSTOM_COMPLAINT_TOOL": "📝 3. Submit Custom Multimodal Complaint via MCP Tool (submit_complaint_triage)",
                "SURVEYOR_APPROVAL_TOOL": "✅ 4. Surveyor Sign-Off / SOR Override via MCP Tool (approve_or_override_work_order)",
            }[k],
            key="mcp_guided_workflow_select",
        )

        if guided_mode == "PRESET_SCENARIO":
            preset_map = {p.preset_id: p for p in SCENARIO_PRESETS}
            chosen_id = st.selectbox(
                "Choose Preset Scenario to Trigger via MCP",
                options=list(preset_map.keys()),
                format_func=lambda pid: f"{preset_map[pid].title} ({preset_map[pid].expected_destination.value})",
                key="mcp_guided_preset_select",
            )
            chosen_preset = preset_map[chosen_id]
            prompt_example = PRESET_MCP_PROMPTS.get(chosen_id, "")

            with st.container(border=True):
                st.markdown("##### 💬 How a User or Housing Officer Prompts the AI Agent:")
                st.code(
                    f'"{prompt_example} (session_id=\'{session_id}\')"',
                    language="text",
                )
                st.caption(
                    f"**Why this scenario matters:** {chosen_preset.what_it_tests} — Expected Route: `{chosen_preset.expected_destination.value}`"
                )
                st.markdown(
                    f"**Translated MCP Protocol Call:** `tools/call` → `simulate_complaint_event(preset_id=\"{chosen_id}\", session_id=\"{session_id}\")`"
                )

            if st.button("🚀 Execute MCP `simulate_complaint_event` Now", type="primary", use_container_width=True):
                res = execute_embedded_mcp_tool(
                    "simulate_complaint_event",
                    {"preset_id": chosen_id, "session_id": session_id},
                )
                st.session_state["last_mcp_console_output"] = res
                st.toast(f"MCP Executed: {chosen_preset.title}", icon="✅")

        elif guided_mode == "READ_PROPERTY_RESOURCE":
            prop_id = st.selectbox(
                "Select Property ID to Inspect",
                options=["prop_oak_01", "prop_elm_02", "prop_cedar_03"],
                format_func=lambda pid: {
                    "prop_oak_01": "prop_oak_01 — Flat 4, Oak Court (Social Housing)",
                    "prop_elm_02": "prop_elm_02 — 12 Elm Terrace (Social Housing)",
                    "prop_cedar_03": "prop_cedar_03 — Unit 3B, Cedar Business Park (Commercial)",
                }[pid],
                key="mcp_guided_prop_select",
            )
            uri = f"sor://properties/{prop_id}/latest-triage"
            with st.container(border=True):
                st.markdown("##### 💬 How a User Prompts the AI Agent:")
                st.code(
                    f'"Check the latest triage resource for property {prop_id} ({uri}) in session {session_id}. What is the current routing decision and why?"',
                    language="text",
                )
                st.markdown(
                    f"**Translated MCP Protocol Call:** `resources/read` → `{uri}` (or `tools/call` → `get_latest_triage`)"
                )

            if st.button(f"📖 Read MCP Resource `{uri}`", type="primary", use_container_width=True):
                raw_json = get_latest_triage_json(property_id=prop_id, session_id=session_id)
                st.session_state["last_mcp_console_output"] = {
                    "jsonrpc_method": "resources/read",
                    "resource_uri": uri,
                    "mime_type": "application/json",
                    "result": json.loads(raw_json),
                }
                st.toast(f"Read MCP Resource for {prop_id}", icon="📄")

        elif guided_mode == "CUSTOM_COMPLAINT_TOOL":
            c_prop = st.selectbox(
                "Property ID",
                options=["prop_oak_01", "prop_elm_02", "prop_cedar_03"],
                key="mcp_custom_prop",
            )
            c_text = st.text_input(
                "Complaint Text",
                value="Your plumber finished JOB-77210 yesterday, but the new trap under the sink is still leaking onto the floor!",
                key="mcp_custom_text",
            )
            c_img = st.selectbox(
                "Synthetic Photo Attachment",
                options=[
                    "sink_leak",
                    "broken_hinge",
                    "black_mould",
                    "ceiling_light_leak",
                    "cistern_valve",
                    "inappropriate_placeholder",
                ],
                key="mcp_custom_img",
            )
            with st.container(border=True):
                st.markdown("##### 💬 How a User Prompts the AI Agent:")
                st.code(
                    f'"Submit this tenant complaint for {c_prop} with photo {c_img}: \'{c_text}\'. Tell me the M3NHF SOR code and whether Stage 4 auto-dispatched or escalated it."',
                    language="text",
                )
                st.markdown("**Translated MCP Protocol Call:** `tools/call` → `submit_complaint_triage`")

            if st.button("🚀 Execute MCP `submit_complaint_triage` Now", type="primary", use_container_width=True):
                res = execute_embedded_mcp_tool(
                    "submit_complaint_triage",
                    {
                        "property_id": c_prop,
                        "complaint_text": c_text,
                        "synthetic_image_preset": c_img,
                        "session_id": session_id,
                    },
                )
                st.session_state["last_mcp_console_output"] = res
                st.toast("MCP submitted custom complaint!", icon="🚀")

        elif guided_mode == "SURVEYOR_APPROVAL_TOOL":
            a_tkt = st.text_input("Ticket ID to Approve/Override", value="TKT-BASE-02", key="mcp_app_tkt")
            a_sor = st.text_input("Approved 6-Digit M3NHF SOR Code", value="192005", key="mcp_app_sor")
            a_notes = st.text_input(
                "Surveyor Audit Notes",
                value="Confirmed 192005 push-fit waste trap replacement via MCP Agent.",
                key="mcp_app_notes",
            )
            with st.container(border=True):
                st.markdown("##### 💬 How a Surveyor Prompts the AI Agent:")
                st.code(
                    f'"Approve ticket {a_tkt} in session {session_id} using M3NHF SOR code {a_sor} with note: \'{a_notes}\'."',
                    language="text",
                )
                st.markdown("**Translated MCP Protocol Call:** `tools/call` → `approve_or_override_work_order`")

            if st.button("✅ Execute MCP `approve_or_override_work_order` Now", type="primary", use_container_width=True):
                res = execute_embedded_mcp_tool(
                    "approve_or_override_work_order",
                    {
                        "ticket_id": a_tkt,
                        "override_sor": a_sor,
                        "surveyor_notes": a_notes,
                        "session_id": session_id,
                    },
                )
                st.session_state["last_mcp_console_output"] = res
                st.toast(f"Ticket {a_tkt} approved via MCP!", icon="✅")

        if st.session_state.get("last_mcp_console_output"):
            out_payload = st.session_state["last_mcp_console_output"]
            st.markdown("##### 📡 Live MCP Response Summary & Raw Payload")
            res_obj = out_payload.get("result", {})
            if isinstance(res_obj, dict) and "decision" in res_obj:
                dec = res_obj["decision"]
                r_dec = dec.get("destination", "UNKNOWN")
                sor_c = dec.get("assigned_sor") or "Short-Circuited"
                st.success(
                    f"**Ticket `{res_obj.get('ticket_id')}`** | **Stage 4 Route:** `{r_dec}` | **M3NHF SOR:** `{sor_c}`  \n"
                    f"**Gate Summary:** {dec.get('action_summary', '')}"
                )
            with st.expander("Inspect Full JSON-RPC / MCP Payload", expanded=True):
                st.json(out_payload)
