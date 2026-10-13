"""
InsightFlow AI — Exploratory Data Analysis (Page 4)
Phase 4: Statistical distributions, categorical frequencies, correlation heatmaps,
scatter relationships, trend analysis, and deterministic factual observations.
Does not mutate the underlying working dataset.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from utils.theme import apply_theme
from utils.data_loader import compute_dataset_summary
from utils.visualizations import (
    plot_numeric_distribution,
    plot_numeric_boxplot,
    plot_category_frequencies,
    plot_missing_values,
    plot_correlation_heatmap,
    plot_scatter_relationship,
    plot_trend_timeseries,
    compute_basic_statistical_observations
)
from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import render_metric_card
from components.ai_button import render_ai_floating_button

st.set_page_config(
    page_title="Exploratory Data Analysis | InsightFlow AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

render_header(
    title="Exploratory Data Analysis (EDA)",
    subtitle="Analyze statistical distributions, evaluate correlations, and inspect multivariate relationships.",
    badge="Module • EDA"
)

# Session state verification
df = st.session_state.get("dataset")
is_loaded = st.session_state.get("dataset_loaded", False)

if not is_loaded or df is None:
    st.markdown(
        """
        <div class="placeholder-container">
            <div class="placeholder-icon">🔍</div>
            <div class="placeholder-title">No Dataset Loaded Yet</div>
            <div class="placeholder-desc">
                Upload a dataset from the Dashboard to begin exploratory data analysis, 
                inspect distribution histograms, correlation heatmaps, and categorical frequencies.
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
    # Safely compute current working dataset summary
    filename = st.session_state.get("dataset_name", "dataset")
    info = compute_dataset_summary(df, filename)
    st.session_state["dataset_info"] = info

    numeric_cols = info["numeric_cols"]
    cat_cols = info["categorical_cols"]
    date_cols = info["datetime_cols"]

    # 1. Top EDA KPI Overview Cards
    st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>EDA Dataset Overview</h3>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_metric_card("Rows", f"{info['rows']:,}", "Records", is_pending=False)
    with k2:
        render_metric_card("Columns", f"{info['cols']}", "Features", is_pending=False)
    with k3:
        render_metric_card("Numeric Columns", f"{len(numeric_cols)}", "Numeric", is_pending=False)
    with k4:
        render_metric_card("Categorical Columns", f"{len(cat_cols)}", "Categorical", is_pending=False)
    with k5:
        render_metric_card("Missing Values", f"{info['total_missing']:,}", "Entries", is_pending=(info['total_missing'] > 0))

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. EDA Analysis Workspace Tabs
    tab_num, tab_cat, tab_corr, tab_scatter, tab_trend, tab_missing, tab_stats = st.tabs([
        "📊 Numeric Distributions",
        "🏷️ Categorical Frequencies",
        "🔥 Correlation Matrix",
        "🎯 Feature Relationships",
        "📈 Trend Analysis",
        "❓ Missing Data Analysis",
        "📋 Statistical Summary"
    ])

    # ---------------- TAB 1: NUMERIC DISTRIBUTIONS ----------------
    with tab_num:
        st.markdown("#### Numeric Distribution & Spread")
        if not numeric_cols:
            st.info("No numeric columns found in the current dataset.")
        else:
            c_sel1, c_sel2 = st.columns([2, 1])
            with c_sel1:
                selected_num = st.selectbox("Select numeric feature:", options=numeric_cols, key="eda_select_num")
            with c_sel2:
                hist_bins = st.slider("Histogram bins:", min_value=10, max_value=80, value=30, step=5, key="eda_num_bins")

            # Numeric Summary Cards for Selected Feature
            col_data = df[selected_num].dropna()
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            with m1:
                st.metric("Count", f"{len(col_data):,}")
            with m2:
                st.metric("Mean", f"{col_data.mean():,.2f}")
            with m3:
                st.metric("Median", f"{col_data.median():,.2f}")
            with m4:
                st.metric("Std Dev", f"{col_data.std():,.2f}")
            with m5:
                st.metric("Min", f"{col_data.min():,.2f}")
            with m6:
                st.metric("Max", f"{col_data.max():,.2f}")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            plot_col1, plot_col2 = st.columns([1.2, 1])
            with plot_col1:
                fig_hist = plot_numeric_distribution(df, selected_num, bins=hist_bins)
                st.plotly_chart(fig_hist, use_container_width=True)
            with plot_col2:
                fig_box = plot_numeric_boxplot(df, y_col=selected_num)
                st.plotly_chart(fig_box, use_container_width=True)

    # ---------------- TAB 2: CATEGORICAL FREQUENCIES ----------------
    with tab_cat:
        st.markdown("#### Categorical Frequency Analysis")
        if not cat_cols:
            st.info("No categorical/text columns found in the current dataset.")
        else:
            cat_col1, cat_col2 = st.columns([2, 1])
            with cat_col1:
                selected_cat = st.selectbox("Select categorical feature:", options=cat_cols, key="eda_select_cat")
            with cat_col2:
                top_k = st.selectbox("Display Top N Categories:", options=[5, 10, 15, 20], index=1, key="eda_top_k")

            cat_series = df[selected_cat].dropna()
            total_unique = cat_series.nunique()
            mode_val = cat_series.mode().iloc[0] if not cat_series.empty else "N/A"
            mode_count = (cat_series == mode_val).sum() if not cat_series.empty else 0

            cm1, cm2, cm3 = st.columns(3)
            with cm1:
                st.metric("Distinct Categories", f"{total_unique:,}")
            with cm2:
                st.metric("Most Frequent Value", f"{mode_val}")
            with cm3:
                st.metric("Top Value Count", f"{mode_count:,}")

            fig_bar = plot_category_frequencies(df, selected_cat, top_n=top_k)
            st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------- TAB 3: CORRELATION HEATMAP ----------------
    with tab_corr:
        st.markdown("#### Correlation Matrix")
        if len(numeric_cols) < 2:
            st.warning("⚠️ Correlation analysis requires at least two numeric columns in the dataset.")
        else:
            selected_corr_cols = st.multiselect(
                "Filter numeric columns included in correlation matrix:",
                options=numeric_cols,
                default=numeric_cols,
                key="eda_corr_multiselect"
            )

            if len(selected_corr_cols) < 2:
                st.info("Please select at least two numeric features to display correlation values.")
            else:
                fig_corr = plot_correlation_heatmap(df, selected_corr_cols)
                if fig_corr:
                    st.plotly_chart(fig_corr, use_container_width=True)

    # ---------------- TAB 4: SCATTER RELATIONSHIPS ----------------
    with tab_scatter:
        st.markdown("#### Bivariate Feature Relationships")
        if len(numeric_cols) < 2:
            st.warning("⚠️ Relationship scatter plots require at least two numeric features.")
        else:
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                x_axis_num = st.selectbox("X-Axis (Numeric):", options=numeric_cols, index=0, key="eda_sc_x")
            with sc2:
                default_y_idx = 1 if len(numeric_cols) > 1 else 0
                y_axis_num = st.selectbox("Y-Axis (Numeric):", options=numeric_cols, index=default_y_idx, key="eda_sc_y")
            with sc3:
                color_options = ["None"] + cat_cols
                chosen_color = st.selectbox("Grouping / Color (Optional):", options=color_options, key="eda_sc_color")

            fig_scatter = plot_scatter_relationship(
                df,
                x_col=x_axis_num,
                y_col=y_axis_num,
                color_col=None if chosen_color == "None" else chosen_color
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    # ---------------- TAB 5: TREND ANALYSIS ----------------
    with tab_trend:
        st.markdown("#### Temporal Trend Analysis")
        # Identify possible date columns
        potential_dates = list(date_cols)
        for col in df.columns:
            if col not in potential_dates:
                # Check column name or values
                if any(k in col.lower() for k in ["date", "time", "year", "month", "day", "timestamp"]):
                    potential_dates.append(col)

        if not potential_dates or not numeric_cols:
            st.info("ℹ️ No suitable date/time column available for trend analysis. (You can convert string date columns in the Data Cleaning page).")
        else:
            tr1, tr2 = st.columns(2)
            with tr1:
                chosen_date = st.selectbox("Select Date/Time column:", options=potential_dates, key="eda_trend_date")
            with tr2:
                chosen_val = st.selectbox("Select Numeric Metric:", options=numeric_cols, key="eda_trend_val")

            fig_trend = plot_trend_timeseries(df, chosen_date, chosen_val)
            st.plotly_chart(fig_trend, use_container_width=True)

    # ---------------- TAB 6: MISSING DATA ANALYSIS ----------------
    with tab_missing:
        st.markdown("#### Missing Value Patterns")
        if info["total_missing"] == 0:
            st.success("🎉 No missing values detected in the current working dataset.")
        else:
            fig_miss = plot_missing_values(df)
            if fig_miss:
                st.plotly_chart(fig_miss, use_container_width=True)

            # Detailed table of missing values
            null_series = df.isna().sum()
            missing_table = null_series[null_series > 0].reset_index()
            missing_table.columns = ["Column", "Missing Count"]
            missing_table["% of Total"] = ((missing_table["Missing Count"] / len(df)) * 100).round(2).astype(str) + "%"
            st.dataframe(missing_table, use_container_width=True, hide_index=True)

    # ---------------- TAB 7: STATISTICAL SUMMARY ----------------
    with tab_stats:
        st.markdown("#### Comprehensive Descriptive Statistics")
        if numeric_cols:
            st.markdown("##### Numeric Features Summary")
            desc_table = df[numeric_cols].describe().T
            desc_table["median"] = df[numeric_cols].median()
            st.dataframe(desc_table, use_container_width=True)
        else:
            st.info("No numeric columns found in the dataset.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3. Deterministic Statistical Observations (Grounded in Dataset)
    st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Key Statistical Observations</h3>", unsafe_allow_html=True)

    observations = compute_basic_statistical_observations(df)

    st.markdown(
        """
        <div class="insight-card">
            <h4 style="margin: 0 0 10px 0; color: #30343B; font-size: 1.05rem;">📌 Grounded Dataset Observations</h4>
            <div style="font-size: 0.9rem; color: #30343B; line-height: 1.6;">
        """,
        unsafe_allow_html=True
    )

    for obs in observations:
        st.markdown(f"• {obs}")

    st.markdown(
        """
            </div>
            <div style="margin-top: 12px; font-size: 0.78rem; color: #68707D;">
                <em>Observations are computed mathematically directly from working data. Conversational queries will be connected in Phase 5.</em>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
