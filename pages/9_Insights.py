"""
InsightFlow AI — Intelligent Insights & Anomaly Detection (Page 9)
Phase 6: Automatic discovery of dataset patterns, numerical distributions,
IQR anomaly detection, categorical concentrations, correlations, and trends.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import apply_theme
from utils.data_loader import compute_dataset_summary
from utils.insights import generate_dataset_insights, detect_column_anomalies_iqr
from utils.visualizations import (
    plot_numeric_distribution,
    plot_numeric_boxplot,
    plot_scatter_relationship,
    plot_category_frequencies,
    plot_trend_timeseries,
    plot_missing_values,
    THEME_COLORS
)
from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import render_metric_card
from components.ai_button import render_ai_floating_button

st.set_page_config(
    page_title="Intelligent Insights | InsightFlow AI",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

render_header(
    title="Intelligent Insights & Anomaly Detection",
    subtitle="Automatically discover meaningful patterns, distribution characteristics, correlations, and potential anomalies.",
    badge="Module • Insights"
)

df = st.session_state.get("dataset")
is_loaded = st.session_state.get("dataset_loaded", False)
filename = st.session_state.get("dataset_name", "dataset")

if not is_loaded or df is None:
    st.markdown(
        """
        <div class="placeholder-container">
            <div class="placeholder-icon">💡</div>
            <div class="placeholder-title">No Dataset Available</div>
            <div class="placeholder-desc">
                Upload a CSV or Excel file from the Dashboard to generate automated intelligent insights, 
                detect numerical outliers using the IQR method, and analyze feature relationships.
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
    # Check if cached insights match active dataset state
    cached_insights = st.session_state.get("cached_insights_data")
    cached_dataset_name = st.session_state.get("cached_insights_name")
    cached_cleaning_len = st.session_state.get("cached_insights_cleaning_len")
    current_cleaning_len = len(st.session_state.get("cleaning_log", []))

    if (
        cached_insights is not None
        and cached_dataset_name == filename
        and cached_cleaning_len == current_cleaning_len
    ):
        insights_data = cached_insights
    else:
        with st.spinner("Analyzing dataset patterns and detecting anomalies..."):
            insights_data = generate_dataset_insights(df, filename)
            st.session_state["cached_insights_data"] = insights_data
            st.session_state["cached_insights_name"] = filename
            st.session_state["cached_insights_cleaning_len"] = current_cleaning_len

    total_insights = insights_data["total_insights_count"]
    high_priority = insights_data["high_priority_count"]
    total_anomalies = insights_data["total_anomalies_detected"]
    numeric_cols = insights_data["numeric_cols"]
    cat_cols = insights_data["categorical_cols"]
    date_cols = insights_data["date_cols"]

    # 1. Top Overview Metric Cards
    st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Insights Overview</h3>", unsafe_allow_html=True)
    i1, i2, i3, i4, i5 = st.columns(5)
    with i1:
        render_metric_card("Total Insights", f"{total_insights:,}", "Discovered", is_pending=False)
    with i2:
        render_metric_card("High Priority", f"{high_priority:,}", "Attention", is_pending=(high_priority > 0))
    with i3:
        render_metric_card("Potential Anomalies", f"{total_anomalies:,}", "IQR Method", is_pending=(total_anomalies > 0))
    with i4:
        render_metric_card("Numeric Features", f"{len(numeric_cols)}", "Analyzed", is_pending=False)
    with i5:
        render_metric_card("Categorical Features", f"{len(cat_cols)}", "Analyzed", is_pending=False)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Insights Categorization Tabs
    tab_summary, tab_anom, tab_num, tab_cat, tab_corr, tab_trends, tab_quality = st.tabs([
        "🌟 Prioritized Findings",
        "⚠️ Anomaly Detection",
        "📊 Numerical Insights",
        "🏷️ Categorical Insights",
        "🔗 Correlation Insights",
        "📈 Trend Insights",
        "🛡️ Data Quality"
    ])

    # Helper function to render styled insight card
    def render_insight_card(item: dict):
        priority = item.get("priority", "Informational")
        if priority == "High":
            border_color = "#E07A5F"
            badge_bg = "#F2C6B4"
            badge_text_color = "#7D3B23"
            icon = "🚨"
        elif priority == "Medium":
            border_color = "#648F86"
            badge_bg = "#E2F3EC"
            badge_text_color = "#2F6B55"
            icon = "💡"
        else:
            border_color = "#D8CFE8"
            badge_bg = "#E8E1F5"
            badge_text_color = "#554477"
            icon = "ℹ️"

        st.markdown(
            f"""
            <div class="insight-card" style="border-left: 5px solid {border_color}; margin-bottom: 12px; padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #30343B;">
                        {icon} {item.get('title', 'Insight')}
                    </div>
                    <span class="phase-pill" style="background-color: {badge_bg}; color: {badge_text_color}; font-size: 0.72rem; padding: 3px 10px;">
                        {priority} Priority
                    </span>
                </div>
                <div style="color: #4A505A; font-size: 0.92rem; line-height: 1.5; margin-bottom: 8px;">
                    {item.get('description', '')}
                </div>
                <div style="background-color: #F8F5FC; border-radius: 6px; padding: 6px 12px; font-size: 0.82rem; color: #554477;">
                    <strong>Evidence:</strong> {item.get('evidence', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- TAB 1: PRIORITIZED FINDINGS ----------------
    with tab_summary:
        st.markdown("#### High & Medium Priority Discoveries")
        prioritized_items = insights_data["insights_by_priority"]["High"] + insights_data["insights_by_priority"]["Medium"]

        if not prioritized_items:
            st.info("No high or medium priority anomalies or extreme patterns discovered in this dataset.")
        else:
            for item in prioritized_items:
                render_insight_card(item)

    # ---------------- TAB 2: ANOMALY DETECTION (IQR) ----------------
    with tab_anom:
        st.markdown("#### Interquartile Range (IQR) Anomaly Detection")
        st.markdown(
            "Identifies values lying outside $[Q_1 - 1.5 \\times \\text{IQR}, Q_3 + 1.5 \\times \\text{IQR}]$. "
            "*Note: Potential outliers are flagged as statistically unusual observations, not necessarily data errors.*"
        )

        if not numeric_cols:
            st.info("No numeric columns available in the dataset for anomaly detection.")
        else:
            anom_col = st.selectbox("Select numeric feature to inspect for anomalies:", options=numeric_cols, key="anom_select_col")
            col_anom = insights_data["anomaly_details"][anom_col]

            # Anomaly summary metrics
            am1, am2, am3, am4 = st.columns(4)
            with am1:
                st.metric("Total Records", f"{col_anom['total_records']:,}")
            with am2:
                st.metric("Potential Anomalies", f"{col_anom['anomaly_count']:,}")
            with am3:
                st.metric("Anomaly Rate", f"{col_anom['anomaly_rate']}%")
            with am4:
                bounds_str = f"[{col_anom['lower_bound']:,.1f}, {col_anom['upper_bound']:,.1f}]" if col_anom['lower_bound'] is not None else "N/A"
                st.metric("IQR Normal Range", bounds_str)

            # Box Plot Visualization
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            fig_box = plot_numeric_boxplot(df, y_col=anom_col)
            st.plotly_chart(fig_box, use_container_width=True)

            # Anomaly table
            anom_df = col_anom["table"]
            if anom_df.empty:
                st.success(f"🎉 No potential outliers detected in '{anom_col}'. All values are within normal IQR boundaries.")
            else:
                st.markdown(f"##### Detected Anomalies Table for {anom_col}")
                filter_dir = st.radio("Filter direction:", options=["All", "High", "Low"], horizontal=True, key="anom_filter_dir")
                if filter_dir != "All":
                    display_anom = anom_df[anom_df["Anomaly Direction"] == filter_dir]
                else:
                    display_anom = anom_df

                st.dataframe(display_anom.head(100), use_container_width=True, hide_index=True)
                if len(display_anom) > 100:
                    st.caption(f"Displaying first 100 out of {len(display_anom):,} detected anomaly rows.")

    # ---------------- TAB 3: NUMERICAL INSIGHTS ----------------
    with tab_num:
        st.markdown("#### Distribution & Skewness Insights")
        num_items = [i for i in insights_data["all_insights"] if i.get("category") == "Numerical"]
        if not num_items:
            st.info("All numerical columns exhibit relatively balanced distributions without strong skewness or extreme variance.")
        else:
            for item in num_items:
                render_insight_card(item)

    # ---------------- TAB 4: CATEGORICAL INSIGHTS ----------------
    with tab_cat:
        st.markdown("#### Categorical Imbalance & Group Performance")
        cat_items = [i for i in insights_data["all_insights"] if i.get("category") in ["Categorical", "Group Performance"]]
        if not cat_items:
            st.info("No notable category concentrations or group performance skews discovered.")
        else:
            for item in cat_items:
                render_insight_card(item)

    # ---------------- TAB 5: CORRELATION INSIGHTS ----------------
    with tab_corr:
        st.markdown("#### Meaningful Linear Feature Correlations")
        st.caption("Thresholds: |r| >= 0.7 classified as Strong, 0.4 <= |r| < 0.7 classified as Moderate. *Correlation does not imply causation.*")
        corr_items = [i for i in insights_data["all_insights"] if i.get("category") == "Correlations"]
        if not corr_items:
            st.info("No strong or moderate linear correlations detected between numeric features.")
        else:
            for item in corr_items:
                render_insight_card(item)

    # ---------------- TAB 6: TREND INSIGHTS ----------------
    with tab_trends:
        st.markdown("#### Chronological Trajectory Insights")
        trend_items = [i for i in insights_data["all_insights"] if i.get("category") == "Trends"]
        if not date_cols:
            st.info("No valid date/time column detected in this dataset to generate chronological trends.")
        elif not trend_items:
            st.info("No significant overall increase or decrease (> 15%) detected across chronological intervals.")
        else:
            for item in trend_items:
                render_insight_card(item)

    # ---------------- TAB 7: DATA QUALITY ----------------
    with tab_quality:
        st.markdown("#### Data Completeness & Quality Insights")
        qual_items = [i for i in insights_data["all_insights"] if i.get("category") == "Data Quality"]
        for item in qual_items:
            render_insight_card(item)
