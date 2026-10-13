"""
InsightFlow AI — Analytical Reports (Page 6)
Phase 7: Intelligent Report Generation Engine
Exports comprehensive, verified analysis reports in PDF and HTML formats.
All metrics and insights are grounded strictly in computed dataset results.
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
from components.ai_button import render_ai_floating_button
from utils.report_generator import (
    build_report_data,
    generate_html_report,
    generate_pdf_report,
    sanitize_filename
)

st.set_page_config(
    page_title="Reports | InsightFlow AI",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

render_header(
    title="Intelligent Analytical Reports",
    subtitle="Export executive-level summaries, verified statistics, and intelligent insights in publication-ready PDF and HTML formats.",
    badge="Module • Reports"
)

# 1. Dataset Verification Check
if not st.session_state.get("dataset_loaded", False) or st.session_state.get("dataset") is None:
    st.markdown(
        """
        <div class="placeholder-container">
            <div class="placeholder-icon">📑</div>
            <div class="placeholder-title">No Active Dataset Found</div>
            <div class="placeholder-desc">
                Upload a CSV or Excel dataset from the Dashboard to compile and export professional reports.
            </div>
            <span class="phase-pill">Awaiting Dataset</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("📊 Go to Dashboard to Upload", type="primary", use_container_width=False):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

df: pd.DataFrame = st.session_state["dataset"]
dataset_name: str = st.session_state.get("dataset_name", "dataset.csv")
cleaning_log = st.session_state.get("cleaning_log", [])

# 2. Configuration & Scope Selection
st.markdown(
    """
    <div class="insight-card" style="border-left: 5px solid #648F86; margin-bottom: 20px;">
        <h3 style="margin: 0 0 6px 0; color: #30343B; font-size: 1.15rem;">Report Configuration</h3>
        <p style="margin: 0; color: #68707D; font-size: 0.92rem;">
            Select report scope and format options. All findings are strictly computed from your current active session.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

col_cfg1, col_cfg2 = st.columns([1.5, 2.5])

with col_cfg1:
    report_scope = st.radio(
        "Report Scope",
        options=["Full Analysis", "Summary"],
        index=0,
        help="Full Analysis includes all descriptive statistics, detailed insights, and anomaly tables. Summary highlights key takeaways."
    )

with col_cfg2:
    st.markdown("<div style='font-size: 0.88rem; font-weight: 600; color: #30343B; margin-bottom: 8px;'>Included Sections</div>", unsafe_allow_html=True)
    inc_col1, inc_col2 = st.columns(2)
    with inc_col1:
        st.checkbox("Executive Summary", value=True, disabled=True)
        st.checkbox("Data Quality & Cleaning Log", value=True, disabled=True)
        st.checkbox("Descriptive Statistics", value=True, disabled=True)
    with inc_col2:
        st.checkbox("Intelligent Insights (Phase 6)", value=True, disabled=True)
        st.checkbox("IQR Anomaly Profiling", value=True, disabled=True)
        st.checkbox("Methodology & Takeaways", value=True, disabled=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# 3. Report Compilation & Generation Controls
# Check if existing report matches active dataset and scope
has_matching_report = (
    "compiled_report_data" in st.session_state
    and st.session_state.get("compiled_dataset_name") == dataset_name
    and st.session_state.get("compiled_scope") == report_scope
    and st.session_state.get("compiled_cleaning_len") == len(cleaning_log)
)

col_act1, col_act2 = st.columns([2, 3])
with col_act1:
    generate_btn = st.button("⚙️ Compile & Generate Report", type="primary", use_container_width=True)

if generate_btn:
    with st.spinner("Compiling verified findings across analytical modules..."):
        try:
            report_data = build_report_data(
                df=df,
                filename=dataset_name,
                cleaning_log=cleaning_log,
                scope=report_scope
            )
            html_output = generate_html_report(report_data, df)
            pdf_output = generate_pdf_report(report_data, df)

            st.session_state["compiled_report_data"] = report_data
            st.session_state["compiled_html"] = html_output
            st.session_state["compiled_pdf"] = pdf_output
            st.session_state["compiled_scope"] = report_scope
            st.session_state["compiled_dataset_name"] = dataset_name
            st.session_state["compiled_cleaning_len"] = len(cleaning_log)
            st.success("✅ Report compiled successfully!")
        except Exception as e:
            st.error(f"❌ Failed to generate report: {str(e)}")
            st.stop()

if not has_matching_report and not generate_btn:
    st.info("ℹ️ Click **'Compile & Generate Report'** above to compile the latest verified analysis for this dataset.")
    st.stop()

report_data = st.session_state["compiled_report_data"]
html_output = st.session_state["compiled_html"]
pdf_output = st.session_state["compiled_pdf"]

# 4. Report Overview KPI Cards
st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-top: 10px; margin-bottom: 12px;'>Compiled Report Summary</h3>", unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Target Dataset</div>
            <div class="metric-value" style="font-size: 1.1rem; word-break: break-all;">{dataset_name}</div>
            <span class="metric-badge">{report_data['metadata']['status']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Dimensions</div>
            <div class="metric-value">{report_data['metadata']['total_records']:,} × {report_data['metadata']['total_features']}</div>
            <span class="metric-badge">Rows × Cols</span>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi3:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Verified Insights</div>
            <div class="metric-value">{report_data['all_insights_count']}</div>
            <span class="metric-badge">{report_data['high_priority_count']} High Priority</span>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi4:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">IQR Outliers</div>
            <div class="metric-value">{report_data['total_anomalies']:,}</div>
            <span class="metric-badge">Flagged</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# 5. Export / Download Center
base_slug = sanitize_filename(Path(dataset_name).stem)

st.markdown(
    """
    <div class="insight-card" style="border-left: 5px solid #648F86; margin-bottom: 20px;">
        <h3 style="margin: 0 0 6px 0; color: #30343B; font-size: 1.15rem;">📥 Download Center</h3>
        <p style="margin: 0; color: #68707D; font-size: 0.92rem;">
            Export the complete analytical brief in publication-grade vector PDF format or standalone interactive HTML.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

dl_col1, dl_col2 = st.columns(2)

with dl_col1:
    st.download_button(
        label="📑 Download PDF Report",
        data=pdf_output,
        file_name=f"InsightFlow_Report_{base_slug}.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )

with dl_col2:
    st.download_button(
        label="🌐 Download HTML Report",
        data=html_output,
        file_name=f"InsightFlow_Report_{base_slug}.html",
        mime="text/html",
        use_container_width=True
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# 6. Interactive In-App Report Preview
st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Interactive Report Preview</h3>", unsafe_allow_html=True)

with st.expander("👁️ View Live HTML Preview", expanded=True):
    st.components.v1.html(html_output, height=750, scrolling=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.caption("InsightFlow AI • Phase 7 Report Engine • Fully Grounded in Active Workspace Data")
