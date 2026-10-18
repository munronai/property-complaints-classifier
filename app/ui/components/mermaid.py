"""Mermaid diagram renderer component for Streamlit with safe JS string injection and tab-visibility ResizeObserver."""

import json
import textwrap
import uuid
import streamlit.components.v1 as components


def st_mermaid(mermaid_code: str, height: int = 440) -> None:
    """Renders a dark-themed Mermaid diagram safely inside an iframe, handling special characters and hidden Streamlit tabs."""
    cleaned_code = textwrap.dedent(mermaid_code).strip()
    js_code_literal = json.dumps(cleaned_code)
    uid = f"mermaid_{uuid.uuid4().hex[:8]}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            .mermaid-wrapper {{
                display: flex;
                justify-content: center;
                align-items: center;
                background: #0e1117;
                padding: 18px;
                border-radius: 10px;
                border: 1px solid #262730;
                min-height: {max(height - 40, 200)}px;
                box-sizing: border-box;
                overflow-x: auto;
            }}
            .mermaid-wrapper svg {{
                max-width: 100%;
                height: auto !important;
            }}
        </style>
    </head>
    <body>
        <div id="{uid}" class="mermaid-wrapper">
            <span style="color: #9ca3af; font-size: 13px;">Rendering Mermaid diagram...</span>
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

            mermaid.initialize({{
                startOnLoad: false,
                theme: 'dark',
                securityLevel: 'loose',
                flowchart: {{ htmlLabels: false, curve: 'basis' }}
            }});

            const container = document.getElementById('{uid}');
            const definition = {js_code_literal};
            let renderedOnce = false;

            async function renderDiagram() {{
                if (!container) return;
                if (container.clientWidth === 0) return;
                try {{
                    const renderId = '{uid}_svg_' + Math.floor(Math.random() * 100000);
                    const {{ svg }} = await mermaid.render(renderId, definition);
                    container.innerHTML = svg;
                    renderedOnce = true;
                }} catch (err) {{
                    container.innerHTML = '<pre style="color:#f87171; font-size:12px; white-space:pre-wrap;">Mermaid render error: ' + String(err) + '</pre>';
                }}
            }}

            renderDiagram();

            const ro = new ResizeObserver(() => {{
                if (!renderedOnce && container.clientWidth > 0) {{
                    renderDiagram();
                }}
            }});
            ro.observe(document.body);
        </script>
    </body>
    </html>
    """
    components.html(html, height=height, scrolling=True)
