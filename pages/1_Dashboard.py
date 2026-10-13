"""
InsightFlow AI — Dashboard (Page 1)
Phase 2: CSV/Excel Upload + Dataset Understanding
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from utils.theme import apply_theme
from utils.data_loader import load_dataset, compute_dataset_summary
from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import render_metric_card, render_nav_card
from components.ai_button import render_ai_floating_button

st.set_page_config(
    page_title="Dashboard | InsightFlow AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

# Main Header
render_header(
    title="Welcome to InsightFlow AI",
    subtitle="Turn your data into meaningful insights with an intelligent AI-powered data analysis workspace.",
    badge="InsightFlow AI • Production Ready v1.0"
)

# Initialize Session State Variables if not present
if "dataset" not in st.session_state:
    st.session_state["dataset"] = None
if "original_dataset" not in st.session_state:
    st.session_state["original_dataset"] = None
if "dataset_name" not in st.session_state:
    st.session_state["dataset_name"] = None
if "dataset_loaded" not in st.session_state:
    st.session_state["dataset_loaded"] = False
if "dataset_info" not in st.session_state:
    st.session_state["dataset_info"] = None
if "cleaning_log" not in st.session_state:
    st.session_state["cleaning_log"] = []

is_loaded = st.session_state["dataset_loaded"]

# Upload & Dataset Status Section
if not is_loaded:
    st.markdown(
        """
        <div class="insight-card" style="border-left: 5px solid #648F86; margin-bottom: 20px;">
            <h3 style="margin: 0 0 6px 0; color: #30343B; font-size: 1.25rem;">Upload Your Dataset</h3>
            <p style="margin: 0 0 14px 0; color: #68707D; font-size: 0.95rem;">
                Select or drop a CSV or Excel (.xlsx, .xls) file to inspect structure, columns, and initial summary statistics.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader(
        label="Upload a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Supported formats: .csv, .xlsx, .xls",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        with st.spinner("Reading and inspecting dataset..."):
            df, error_msg = load_dataset(uploaded_file)
            if error_msg:
                st.error(f"❌ {error_msg}")
            else:
                summary = compute_dataset_summary(df, uploaded_file.name)
                st.session_state["original_dataset"] = df.copy()
                st.session_state["dataset"] = df.copy()
                st.session_state["dataset_name"] = uploaded_file.name
                st.session_state["dataset_loaded"] = True
                st.session_state["dataset_info"] = summary
                st.session_state["cleaning_log"] = []
                st.success(f"✅ Successfully loaded **{uploaded_file.name}** ({len(df):,} rows × {len(df.columns)} columns)!")
                st.rerun()

else:
    # Re-calculate summary from current working dataset if available
    working_df = st.session_state["dataset"]
    dataset_name = st.session_state["dataset_name"]
    info = compute_dataset_summary(working_df, dataset_name)
    st.session_state["dataset_info"] = info
    rows = info["rows"]
    cols = info["cols"]

    is_cleaned = len(st.session_state.get("cleaning_log", [])) > 0
    status_label = "Cleaned Working Dataset" if is_cleaned else "Original Dataset"

    st.markdown(
        f"""
        <div class="insight-card" style="border-left: 5px solid #648F86; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span style="height: 10px; width: 10px; background-color: #648F86; border-radius: 50%; display: inline-block;"></span>
                        <h3 style="margin: 0; color: #30343B; font-size: 1.25rem;">Active Dataset: {dataset_name}</h3>
                    </div>
                    <p style="margin: 0; color: #68707D; font-size: 0.95rem;">
                        Working Data: <strong>{rows:,}</strong> rows × <strong>{cols}</strong> columns • State: <strong>{status_label}</strong>
                    </p>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span class="phase-pill" style="background-color: #E2F3EC; color: #2F6B55;">
                        Dataset Active ({status_label})
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_btn1, col_btn2, col_btn3 = st.columns([1.5, 2, 2.5])
    with col_btn1:
        if st.button("🗑️ Remove Dataset", key="btn_remove_dataset_main", use_container_width=True):
            st.session_state["dataset"] = None
            st.session_state["original_dataset"] = None
            st.session_state["dataset_name"] = None
            st.session_state["dataset_loaded"] = False
            st.session_state["dataset_info"] = None
            st.session_state["cleaning_log"] = []
            st.rerun()
    with col_btn2:
        if st.button("🧹 Open Data Cleaning", key="btn_go_cleaning", type="primary", use_container_width=True):
            st.switch_page("pages/3_Data_Cleaning.py")
    with col_btn3:
        if st.button("📁 Open Dataset Explorer", key="btn_go_explorer", use_container_width=True):
            st.switch_page("pages/2_Dataset_Explorer.py")

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Overview Metric Cards
st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Workspace Overview</h3>", unsafe_allow_html=True)
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

if is_loaded:
    info = st.session_state["dataset_info"]
    with m_col1:
        render_metric_card("Dataset", st.session_state["dataset_name"], "Active", is_pending=False)
    with m_col2:
        render_metric_card("Total Rows", f"{info['rows']:,}", "Loaded", is_pending=False)
    with m_col3:
        render_metric_card("Total Columns", f"{info['cols']}", "Loaded", is_pending=False)
    with m_col4:
        render_metric_card("Missing Values", f"{info['total_missing']:,}", "Detected", is_pending=(info['total_missing'] > 0))
else:
    with m_col1:
        render_metric_card("Dataset Status", "Not Loaded", "Phase 2", is_pending=True)
    with m_col2:
        render_metric_card("Total Rows", "—", "Phase 2", is_pending=True)
    with m_col3:
        render_metric_card("Total Columns", "—", "Phase 2", is_pending=True)
    with m_col4:
        render_metric_card("Missing Values", "—", "Phase 2", is_pending=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Workspace Navigation Cards
st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Workspace Modules</h3>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    render_nav_card(
        icon="📁",
        title="Dataset Explorer",
        description="Inspect schemas, column types, sample data records, and summary statistics.",
        phase_tag="Active",
        page_name="pages/2_Dataset_Explorer.py"
    )

with c2:
    render_nav_card(
        icon="🧹",
        title="Data Cleaning",
        description="Inspect quality issues, handle missing values, duplicates, column names, and type conversions.",
        phase_tag="Active",
        page_name="pages/3_Data_Cleaning.py"
    )

with c3:
    render_nav_card(
        icon="🔍",
        title="Exploratory Analysis",
        description="Analyze distributions, correlations, and multivariate patterns.",
        phase_tag="Active",
        page_name="pages/4_EDA.py"
    )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    render_nav_card(
        icon="📈",
        title="Visualizations",
        description="Generate interactive, publication-ready visual charts.",
        phase_tag="Active",
        page_name="pages/5_Visualizations.py"
    )

with c5:
    render_nav_card(
        icon="💡",
        title="Intelligent Insights",
        description="Automatically discover key patterns, correlations, and IQR numerical anomalies.",
        phase_tag="Active",
        page_name="pages/9_Insights.py"
    )

with c6:
    render_nav_card(
        icon="📑",
        title="Analytical Reports",
        description="Export executive-level summaries, verified statistics, and insights in PDF and HTML.",
        phase_tag="Active",
        page_name="pages/6_Reports.py"
    )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

c7, c8, _ = st.columns(3)
with c7:
    render_nav_card(
        icon="✨",
        title="AI Assistant",
        description="Query your data in plain English with an autonomous analyst agent.",
        phase_tag="Active",
        page_name="pages/7_AI_Assistant.py"
    )
with c8:
    render_nav_card(
        icon="⚙️",
        title="Settings",
        description="Configure workspace preferences, appearance, and analysis parameters.",
        phase_tag="Active",
        page_name="pages/8_Settings.py"
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Getting Started & Recent Activity Sections
col_guide, col_activity = st.columns([1.2, 1])

with col_guide:
    st.markdown(
        """
        <div class="insight-card">
            <h4 style="margin: 0 0 12px 0; color: #30343B; font-size: 1.05rem;">🚀 Getting Started</h4>
            <div style="font-size: 0.9rem; color: #68707D; line-height: 1.6;">
                <ol style="padding-left: 20px; margin: 0;">
                    <li><strong>Connect Your Data (Phase 2):</strong> Load CSV or Excel files into your isolated session above.</li>
                    <li><strong>Inspect Structure (Phase 2):</strong> Navigate to Dataset Explorer to view columns and distributions.</li>
                    <li><strong>Assess Data Quality (Phase 3):</strong> Review missing records and type mismatches.</li>
                    <li><strong>Analyze & Discover (Phase 4):</strong> Review statistical distributions and correlation matrices.</li>
                    <li><strong>Collaborate with AI (Phase 5):</strong> Ask natural language questions in real-time.</li>
                </ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_activity:
    status_msg = f"Active session with <strong>{st.session_state['dataset_name']}</strong>." if is_loaded else "No active dataset loaded."
    st.markdown(
        f"""
        <div class="insight-card">
            <h4 style="margin: 0 0 12px 0; color: #30343B; font-size: 1.05rem;">🕒 Recent Activity</h4>
            <div style="font-size: 0.9rem; color: #68707D; line-height: 1.6;">
                <p style="margin: 0 0 8px 0;">{status_msg}</p>
                <div style="background: #E8E1F5; border-radius: 8px; padding: 10px 14px; font-size: 0.84rem; color: #554477;">
                    📌 Session tracking and history will be connected in future phases.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
