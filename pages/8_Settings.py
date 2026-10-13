"""
InsightFlow AI — Settings (Page 8)
Configuration and workspace settings placeholder.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from utils.theme import apply_theme
from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import render_placeholder
from components.ai_button import render_ai_floating_button

st.set_page_config(
    page_title="Settings | InsightFlow AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

render_header(
    title="Workspace Settings",
    subtitle="Manage workspace preferences, runtime environment, and export configurations.",
    badge="Module • Settings"
)

render_placeholder(
    icon="⚙️",
    title="Workspace Preferences",
    description="Customizable configurations including themes, model selections, export preferences, and session retention parameters will be configured here.",
    status_text="Configuration Ready"
)
