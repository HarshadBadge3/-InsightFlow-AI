"""
InsightFlow AI — Dataset Explorer (Page 2)
Phase 2: Complete Dataset Understanding & Inspection.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from utils.theme import apply_theme
from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import render_metric_card
from components.ai_button import render_ai_floating_button

st.set_page_config(
    page_title="Dataset Explorer | InsightFlow AI",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

render_header(
    title="Dataset Explorer",
    subtitle="Inspect schema definitions, column summaries, and statistical properties of your loaded data.",
    badge="Module • Dataset Explorer"
)

# Check if dataset is loaded
df = st.session_state.get("dataset")
is_loaded = st.session_state.get("dataset_loaded", False)
info = st.session_state.get("dataset_info")

if not is_loaded or df is None or info is None:
    # Professional Empty State
    st.markdown(
        """
        <div class="placeholder-container">
            <div class="placeholder-icon">📁</div>
            <div class="placeholder-title">No Dataset Loaded Yet</div>
            <div class="placeholder-desc">
                Upload a CSV or Excel (.xlsx, .xls) file from the Dashboard to begin exploring your data schema, 
                previewing rows, and inspecting column characteristics.
            </div>
            <span class="phase-pill" style="background-color: #F2C6B4; color: #7D3B23;">
                Awaiting Dataset Upload
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_c1, col_c2, col_c3 = st.columns([2, 1.5, 2])
    with col_c2:
        if st.button("⬅️ Go to Dashboard to Upload", type="primary", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")

else:
    # 1. Dataset Header & Quick Summary
    filename = st.session_state.get("dataset_name", "dataset")
    file_ext = Path(filename).suffix.upper().replace(".", "") or "FILE"

    # Always ensure info is up-to-date with working dataset
    from utils.data_loader import compute_dataset_summary
    info = compute_dataset_summary(df, filename)
    st.session_state["dataset_info"] = info

    is_cleaned = len(st.session_state.get("cleaning_log", [])) > 0
    status_text = "Cleaned" if is_cleaned else "Original"
    badge_color = "#2F6B55" if is_cleaned else "#554477"
    badge_bg = "#E2F3EC" if is_cleaned else "#E8E1F5"

    st.markdown(
        f"""
        <div class="insight-card" style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="margin: 0 0 4px 0; color: #30343B; font-size: 1.3rem;">📄 {filename}</h3>
                    <p style="margin: 0; color: #68707D; font-size: 0.92rem;">
                        Format: <strong>{file_ext}</strong> • Records: <strong>{info['rows']:,}</strong> • Features: <strong>{info['cols']}</strong> • Dataset Status: <strong>{status_text}</strong>
                    </p>
                </div>
                <div>
                    <span class="phase-pill" style="background-color: {badge_bg}; color: {badge_color};">
                        Status: {status_text}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Key Dataset Metric Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        render_metric_card("Total Rows", f"{info['rows']:,}", "Records", is_pending=False)
    with kpi2:
        render_metric_card("Total Columns", f"{info['cols']}", "Features", is_pending=False)
    with kpi3:
        render_metric_card("Numeric Features", f"{info['numeric_cols_count']}", "Numeric", is_pending=False)
    with kpi4:
        render_metric_card("Categorical / Text", f"{info['categorical_cols_count']}", "Categorical", is_pending=False)
    with kpi5:
        render_metric_card("Missing Values", f"{info['total_missing']:,}", "Detected", is_pending=(info['total_missing'] > 0))

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 3. Data Preview Section
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h3 style="margin: 0; color: #30343B; font-size: 1.18rem;">Data Preview</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    prev_col1, prev_col2 = st.columns([1.5, 4.5])
    with prev_col1:
        row_limit = st.selectbox(
            "Rows to preview:",
            options=[5, 10, 20, 50],
            index=1,
            help="Select the number of initial records to display."
        )

    st.dataframe(
        df.head(row_limit),
        use_container_width=True,
        hide_index=False
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. Column Information Summary Table
    st.markdown("<h3 style='margin: 0 0 10px 0; color: #30343B; font-size: 1.18rem;'>Column Metadata & Structure</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #68707D; font-size: 0.9rem; margin-bottom: 12px;'>"
        "Detailed breakdown of data types, completeness, missing values, and unique counts per column."
        "</p>",
        unsafe_allow_html=True
    )

    col_summary_table = info["column_summary_df"]
    st.dataframe(
        col_summary_table,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 5. Data Types Breakdown & Quality Overview
    st.markdown("<h3 style='margin: 0 0 10px 0; color: #30343B; font-size: 1.18rem;'>Data Types & Hygiene Overview</h3>", unsafe_allow_html=True)
    
    type_col, hygiene_col = st.columns([1, 1])

    with type_col:
        st.markdown(
            f"""
            <div class="insight-card">
                <h4 style="margin: 0 0 12px 0; color: #30343B; font-size: 1.05rem;">🏷️ Feature Classification</h4>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.9rem;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EADBCC; padding-bottom: 6px;">
                        <span><strong>Numeric Columns:</strong></span>
                        <span class="metric-badge">{info['numeric_cols_count']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EADBCC; padding-bottom: 6px;">
                        <span><strong>Categorical / Text Columns:</strong></span>
                        <span class="metric-badge">{info['categorical_cols_count']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-bottom: 2px;">
                        <span><strong>Date / Time Columns:</strong></span>
                        <span class="metric-badge">{info['datetime_cols_count']}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with hygiene_col:
        dup_text = "No duplicates found" if info['total_duplicates'] == 0 else f"{info['total_duplicates']:,} duplicate rows detected"
        miss_text = "No missing values" if info['total_missing'] == 0 else f"{info['total_missing']:,} total null entries"
        
        st.markdown(
            f"""
            <div class="insight-card">
                <h4 style="margin: 0 0 12px 0; color: #30343B; font-size: 1.05rem;">🔍 Initial Observations (Report Only)</h4>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.9rem;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EADBCC; padding-bottom: 6px;">
                        <span><strong>Duplicate Rows:</strong></span>
                        <span style="font-weight: 600; color: {'#2F6B55' if info['total_duplicates'] == 0 else '#7D3B23'};">{dup_text}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #EADBCC; padding-bottom: 6px;">
                        <span><strong>Missing Values:</strong></span>
                        <span style="font-weight: 600; color: {'#2F6B55' if info['total_missing'] == 0 else '#7D3B23'};">{miss_text}</span>
                    </div>
                    <div style="padding-top: 4px; font-size: 0.78rem; color: #68707D;">
                        ℹ️ <em>Note: Reporting only. Data cleaning, duplicate resolution, and imputations will take place in <strong>Phase 3</strong>.</em>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 6. Basic Descriptive Statistics (Numeric Columns)
    st.markdown("<h3 style='margin: 0 0 10px 0; color: #30343B; font-size: 1.18rem;'>Descriptive Statistics (Numeric Features)</h3>", unsafe_allow_html=True)
    if info["numeric_cols_count"] > 0:
        desc_df = df.describe()
        st.dataframe(
            desc_df,
            use_container_width=True
        )
    else:
        st.info("No numeric columns found in this dataset for descriptive statistics calculation.")

    # 7. Missing Value Details Table (If any exist)
    if info["total_missing"] > 0:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 0 0 10px 0; color: #30343B; font-size: 1.18rem;'>Missing Values by Column</h3>", unsafe_allow_html=True)
        
        missing_series = df.isna().sum()
        missing_only = missing_series[missing_series > 0].reset_index()
        missing_only.columns = ["Column", "Missing Count"]
        missing_only["% of Total"] = ((missing_only["Missing Count"] / len(df)) * 100).round(2).astype(str) + "%"

        st.dataframe(
            missing_only,
            use_container_width=True,
            hide_index=True
        )
