"""Modular Streamlit views for Landing Page, Product Insights, and Sandbox Control Deck."""

from app.ui.views.landing_page import render_landing_page
from app.ui.views.live_intake import render_live_intake_view
from app.ui.views.mcp_console import render_mcp_console_view
from app.ui.views.product_insights import render_product_insights_view
from app.ui.views.surveyor_desk import render_surveyor_desk_view
from app.ui.views.time_machine import render_time_machine_view

__all__ = [
    "render_landing_page",
    "render_live_intake_view",
    "render_mcp_console_view",
    "render_product_insights_view",
    "render_surveyor_desk_view",
    "render_time_machine_view",
]
