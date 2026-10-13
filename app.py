"""
InsightFlow AI — Your Personal AI Data Analyst
Entry point application script (Phase 1).
"""
import streamlit as st

st.set_page_config(
    page_title="InsightFlow AI — AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Automatically switch to 1_Dashboard.py
st.switch_page("pages/1_Dashboard.py")
