"""Dedicated MCP Integration Guides for Option 1 (Claude Desktop & Cursor) and Option 3 (Official MCP Inspector)."""

import os
from typing import Any
import streamlit as st

from app.domain.presets import SCENARIO_PRESETS
from app.ui.components.help_and_presets import PRESET_MCP_PROMPTS


def render_claude_cursor_guide(
    session_id: str,
    page_dashboard: Any = None,
    page_mcp: Any = None,
) -> None:
    """Renders Option 1: Connecting Claude Desktop or Cursor IDE + Prompt Playbook for all Presets."""
    mcp_url = os.environ.get("SANDBOX_MCP_URL", "http://127.0.0.1:8000/mcp/sse")

    top_col1, top_col2 = st.columns([0.72, 0.28])
    with top_col1:
        st.title("🖥️ Guide: Connecting Claude Desktop or Cursor IDE (Option 1)")
        st.markdown(
            "Because the **Complaint Classifier Sandbox** exposes a standard **Model Context Protocol (MCP)** "
            "server over Server-Sent Events (`/mcp/sse`), you can connect your own local AI assistant directly "
            "to this live housing & commercial repairs engine."
        )
    with top_col2:
        st.write("")
        if page_mcp is not None:
            st.page_link(
                page_mcp,
                label="Open Browser MCP Console (Option 2) →",
                icon="🤖",
                use_container_width=True,
            )
        if page_dashboard is not None:
            st.page_link(
                page_dashboard,
                label="Open Live Sandbox Dashboard →",
                icon="🎛️",
                use_container_width=True,
            )

    st.divider()

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("1. Claude Desktop Configuration")
        st.markdown(
            "Open your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` "
            "on macOS or `%APPDATA%\\Claude\\claude_desktop_config.json` on Windows) and add the `mcp-remote` bridge:"
        )
        st.code(
            f"""{{
  "mcpServers": {{
    "housing-sor-triage": {{
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "{mcp_url}",
        "--transport",
        "sse-only"
      ]
    }}
  }}
}}""",
            language="json",
        )
        st.caption(
            "Note: `--transport sse-only` tells `mcp-remote` to connect directly via SSE, and our server's "
            "`POST /mcp/sse -> HTTP 404` handler plus DNS Rebinding protection ensures zero HTTP 421/405 errors."
        )

    with col2:
        st.subheader("2. Cursor IDE Configuration")
        st.markdown(
            "In Cursor, navigate to **Settings → Cursor Settings → Features → MCP** and add a new **SSE** server, "
            "or add this to `.cursor/mcp.json`:"
        )
        st.code(
            f"""{{
  "mcpServers": {{
    "housing-sor-triage": {{
      "url": "{mcp_url}"
    }}
  }}
}}""",
            language="json",
        )
        st.info(
            f"**Your Active Sandbox Session ID:** `{session_id}`  \n"
            "Include this session ID in your prompt (or leave as `default`) if you want your external AI agent's "
            "actions to appear live on your current browser dashboard!"
        )

    st.divider()
    st.subheader(
        "3. Step-by-Step Agent Prompt Playbook (Copy & Paste into Claude or Cursor)"
    )
    st.markdown(
        "How does a human or autonomous housing officer actually prompt an AI agent so that it uses our **MCP Resources** "
        "and **MCP Tools**? Try this 3-step closed-loop sequence:"
    )

    p1, p2, p3 = st.columns(3)
    with p1:
        with st.container(border=True):
            st.markdown("##### Step 1: Read Clean Baseline State")
            st.caption(
                "Triggers `get_latest_triage` tool or `sor://properties/{id}/latest-triage` resource:"
            )
            st.code(
                f'Use the housing-sor-triage MCP server (session_id="{session_id}") to check the latest triage state for property "prop_oak_01". Confirm that the baseline ticket TKT-BASE-03 is a clean, auto-dispatched plumbing repair (114010).',
                language="text",
            )
    with p2:
        with st.container(border=True):
            st.markdown("##### Step 2: Inject a Critical or Ambiguous Preset")
            st.caption(
                "Triggers `simulate_complaint_event` or `submit_complaint_triage`:"
            )
            st.code(
                f'Use simulate_complaint_event with preset_id="preset_ambiguous_margin" (or "preset_awaabs_law_damp") and session_id="{session_id}". Explain why Stage 4 blocked auto-dispatch and what ticket_id was created.',
                language="text",
            )
    with p3:
        with st.container(border=True):
            st.markdown("##### Step 3: Approve / Override Work Order")
            st.caption(
                "Triggers `approve_or_override_work_order` human-in-the-loop actuator:"
            )
            st.code(
                f'Use approve_or_override_work_order on the paused ticket from Step 2 in session_id="{session_id}" to override the M3NHF SOR code to "192005" with surveyor_notes="Confirmed push-fit waste trap leak via photo".',
                language="text",
            )

    st.divider()
    st.subheader("4. Exact Agent Prompts for All 9 Curated Preset Scenarios")
    st.markdown(
        "Want to test a specific preset scenario through an AI agent? Copy any prompt below—it instructs the agent "
        "which MCP tool to call and what domain question to answer:"
    )

    for p in SCENARIO_PRESETS:
        with st.expander(
            f"📋 **{p.title}** (`{p.preset_id}`) — Expected Route: `{p.expected_destination.value}`"
        ):
            st.markdown(f"**Why this scenario matters:** {p.what_it_tests}")
            st.markdown("**Copy-Paste Agent Prompt:**")
            prompt_txt = PRESET_MCP_PROMPTS.get(p.preset_id, "")
            st.code(f'{prompt_txt} (Use session_id="{session_id}")', language="text")


def render_mcp_inspector_guide(
    session_id: str,
    page_mcp: Any = None,
) -> None:
    """Renders Option 3: Inspecting the Server via Official MCP Inspector CLI."""
    mcp_url = os.environ.get("SANDBOX_MCP_URL", "http://127.0.0.1:8000/mcp/sse")

    top_col1, top_col2 = st.columns([0.72, 0.28])
    with top_col1:
        st.title(
            "🔍 Guide: Inspecting the Server via Official MCP Inspector (Option 3)"
        )
        st.markdown(
            "Developers and protocol engineers can inspect the raw JSON-RPC 2.0 schemas, resources, and tool "
            "definitions exposed by this sandbox using the official open-source **Anthropic MCP Inspector**."
        )
    with top_col2:
        st.write("")
        if page_mcp is not None:
            st.page_link(
                page_mcp,
                label="Open Browser MCP Console (Option 2) →",
                icon="🤖",
                use_container_width=True,
            )

    st.divider()

    st.subheader("1. Launch the Official Inspector CLI")
    st.markdown(
        "Ensure the FastAPI server is running on port `8000`, then run this command in your terminal:"
    )
    st.code(
        f"npx @modelcontextprotocol/inspector@latest {mcp_url}",
        language="bash",
    )

    st.subheader("2. Connect in the Inspector Web UI")
    st.markdown(f"""
        1. Open the local URL printed in your terminal (typically `http://localhost:5173` or `http://localhost:6274`).
        2. Set **Transport Type** to **`SSE`**.
        3. Set **URL** to **`{mcp_url}`** and click **Connect**.
        4. Navigate to the **Resources** tab to inspect `sor://properties/prop_oak_01/latest-triage` and dynamic template `sor://properties/{{property_id}}/latest-triage`.
        5. Navigate to the **Tools** tab to test `get_latest_triage`, `submit_complaint_triage`, `simulate_complaint_event`, and `approve_or_override_work_order` with your active `session_id` (`{session_id}`).
        """)
