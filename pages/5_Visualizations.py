"""
InsightFlow AI — Interactive Visualizations Builder (Page 5)
Phase 4: Multi-type chart generator (Bar, Line, Scatter, Histogram, Box, Pie)
with aggregations, color groupings, and customizable visual parameters.
Does not mutate the underlying working dataset.
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
from utils.visualizations import apply_chart_layout, THEME_COLORS
from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import render_metric_card
from components.ai_button import render_ai_floating_button

st.set_page_config(
    page_title="Visualizations | InsightFlow AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

render_header(
    title="Data Visualization Studio",
    subtitle="Build customized interactive charts from your dataset with aggregation controls and grouping dimensions.",
    badge="Module • Visualizations"
)

# Session state verification
df = st.session_state.get("dataset")
is_loaded = st.session_state.get("dataset_loaded", False)

if not is_loaded or df is None:
    st.markdown(
        """
        <div class="placeholder-container">
            <div class="placeholder-icon">📈</div>
            <div class="placeholder-title">No Dataset Loaded Yet</div>
            <div class="placeholder-desc">
                Upload a dataset from the Dashboard to launch the Visualization Studio, 
                configure custom chart types, apply aggregations, and export interactive plots.
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
    filename = st.session_state.get("dataset_name", "dataset")
    info = compute_dataset_summary(df, filename)
    st.session_state["dataset_info"] = info

    numeric_cols = info["numeric_cols"]
    cat_cols = info["categorical_cols"]
    all_cols = list(df.columns)

    # Visualization Builder Sidebar / Control Panel
    st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Chart Builder Controls</h3>", unsafe_allow_html=True)

    ctrl_col1, ctrl_col2 = st.columns([1, 2.5])

    with ctrl_col1:
        st.markdown(
            """
            <div class="insight-card" style="padding: 16px;">
                <h4 style="margin: 0 0 10px 0; color: #30343B; font-size: 1.02rem;">⚙️ Configuration</h4>
            """,
            unsafe_allow_html=True
        )

        chart_type = st.selectbox(
            "Select Chart Type:",
            options=["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Box Plot", "Pie Chart"],
            key="studio_chart_type"
        )

        fig = None

        # 1. BAR CHART CONFIGURATION
        if chart_type == "Bar Chart":
            x_col = st.selectbox("X-Axis (Category or Feature):", options=all_cols, key="bar_x")
            y_col = st.selectbox("Y-Axis (Numeric Metric):", options=["None (Count)"] + numeric_cols, key="bar_y")
            color_choice = st.selectbox("Color / Grouping (Optional):", options=["None"] + cat_cols, key="bar_color")
            color_col = None if color_choice == "None" else color_choice

            if y_col != "None (Count)":
                agg_func = st.selectbox("Aggregation Function:", options=["Sum", "Mean", "Median", "Min", "Max"], key="bar_agg")
            else:
                agg_func = "Count"

            st.markdown("</div>", unsafe_allow_html=True)

        # 2. LINE CHART CONFIGURATION
        elif chart_type == "Line Chart":
            x_col = st.selectbox("X-Axis (Date or Feature):", options=all_cols, key="line_x")
            y_col = st.selectbox("Y-Axis (Numeric Metric):", options=numeric_cols, key="line_y")
            color_choice = st.selectbox("Color / Series Grouping (Optional):", options=["None"] + cat_cols, key="line_color")
            color_col = None if color_choice == "None" else color_choice
            st.markdown("</div>", unsafe_allow_html=True)

        # 3. SCATTER PLOT CONFIGURATION
        elif chart_type == "Scatter Plot":
            if len(numeric_cols) < 2:
                st.warning("Scatter plot requires at least two numeric columns.")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                x_col = st.selectbox("X-Axis (Numeric):", options=numeric_cols, index=0, key="scatter_x")
                y_col = st.selectbox("Y-Axis (Numeric):", options=numeric_cols, index=min(1, len(numeric_cols)-1), key="scatter_y")
                color_choice = st.selectbox("Color / Category Grouping (Optional):", options=["None"] + cat_cols, key="scatter_color")
                color_col = None if color_choice == "None" else color_choice
                st.markdown("</div>", unsafe_allow_html=True)

        # 4. HISTOGRAM CONFIGURATION
        elif chart_type == "Histogram":
            if not numeric_cols:
                st.warning("Histogram requires at least one numeric column.")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                num_col = st.selectbox("Select Numeric Column:", options=numeric_cols, key="hist_num")
                bins = st.slider("Number of Bins:", min_value=5, max_value=100, value=30, step=5, key="hist_bins")
                color_choice = st.selectbox("Color Grouping (Optional):", options=["None"] + cat_cols, key="hist_color")
                color_col = None if color_choice == "None" else color_choice
                st.markdown("</div>", unsafe_allow_html=True)

        # 5. BOX PLOT CONFIGURATION
        elif chart_type == "Box Plot":
            if not numeric_cols:
                st.warning("Box plot requires a numeric column.")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                y_col = st.selectbox("Y-Axis (Numeric Metric):", options=numeric_cols, key="box_y")
                x_choice = st.selectbox("X-Axis (Categorical Grouping):", options=["None"] + cat_cols, key="box_x")
                x_col = None if x_choice == "None" else x_choice
                st.markdown("</div>", unsafe_allow_html=True)

        # 6. PIE CHART CONFIGURATION
        elif chart_type == "Pie Chart":
            if not cat_cols:
                st.warning("Pie chart requires at least one categorical column.")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                cat_col = st.selectbox("Select Categorical Slice Feature:", options=cat_cols, key="pie_cat")
                val_choice = st.selectbox("Values / Metric:", options=["Count"] + numeric_cols, key="pie_val")
                val_col = None if val_choice == "Count" else val_choice
                top_slices = st.slider("Max Slices to Display:", min_value=3, max_value=15, value=7, key="pie_slices")
                st.markdown("</div>", unsafe_allow_html=True)

    with ctrl_col2:
        st.markdown(
            """
            <div class="insight-card" style="padding: 16px;">
                <h4 style="margin: 0 0 10px 0; color: #30343B; font-size: 1.02rem;">📊 Interactive Chart Canvas</h4>
            """,
            unsafe_allow_html=True
        )

        try:
            # Render Bar Chart
            if chart_type == "Bar Chart":
                if y_col == "None (Count)":
                    plot_data = df.dropna(subset=[x_col])
                    if color_col:
                        fig = px.histogram(
                            plot_data,
                            x=x_col,
                            color=color_col,
                            barmode="group",
                            color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4"]
                        )
                    else:
                        counts = plot_data[x_col].value_counts().head(20).reset_index()
                        counts.columns = [x_col, "Count"]
                        fig = px.bar(
                            counts,
                            x=x_col,
                            y="Count",
                            text="Count",
                            color_discrete_sequence=[THEME_COLORS["primary"]]
                        )
                        fig.update_traces(textposition="outside")
                    fig = apply_chart_layout(fig, f"Count by {x_col}", x_col, "Count")
                else:
                    # Aggregation
                    group_cols = [x_col] + ([color_col] if color_col else [])
                    plot_data = df.dropna(subset=group_cols + [y_col])
                    
                    agg_map = {"Sum": "sum", "Mean": "mean", "Median": "median", "Min": "min", "Max": "max"}
                    agg_df = plot_data.groupby(group_cols, as_index=False)[y_col].agg(agg_map[agg_func])
                    
                    fig = px.bar(
                        agg_df,
                        x=x_col,
                        y=y_col,
                        color=color_col,
                        barmode="group",
                        color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4"]
                    )
                    fig = apply_chart_layout(fig, f"{agg_func} of {y_col} by {x_col}", x_col, f"{agg_func} of {y_col}")

            # Render Line Chart
            elif chart_type == "Line Chart":
                if not numeric_cols:
                    st.info("Line chart requires at least one numeric column on the Y-axis.")
                else:
                    plot_data = df.dropna(subset=[x_col, y_col] + ([color_col] if color_col else [])).copy()
                    # If x is date-like, sort by it
                    try:
                        plot_data["_sort_x"] = pd.to_datetime(plot_data[x_col], errors="coerce")
                        if plot_data["_sort_x"].notna().sum() > len(plot_data) * 0.5:
                            plot_data.sort_values(by="_sort_x", inplace=True)
                    except Exception:
                        pass
                    
                    fig = px.line(
                        plot_data,
                        x=x_col,
                        y=y_col,
                        color=color_col,
                        markers=True,
                        color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4"]
                    )
                    fig = apply_chart_layout(fig, f"{y_col} along {x_col}", x_col, y_col)

            # Render Scatter Plot
            elif chart_type == "Scatter Plot":
                if len(numeric_cols) >= 2:
                    sub_cols = [x_col, y_col] + ([color_col] if color_col else [])
                    plot_data = df.dropna(subset=sub_cols)
                    fig = px.scatter(
                        plot_data,
                        x=x_col,
                        y=y_col,
                        color=color_col,
                        color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4"]
                    )
                    fig = apply_chart_layout(fig, f"{x_col} vs. {y_col}", x_col, y_col)

            # Render Histogram
            elif chart_type == "Histogram":
                if numeric_cols:
                    sub_cols = [num_col] + ([color_col] if color_col else [])
                    plot_data = df.dropna(subset=sub_cols)
                    fig = px.histogram(
                        plot_data,
                        x=num_col,
                        nbins=bins,
                        color=color_col,
                        marginal="box" if not color_col else None,
                        color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4"]
                    )
                    fig = apply_chart_layout(fig, f"Distribution of {num_col}", num_col, "Frequency")

            # Render Box Plot
            elif chart_type == "Box Plot":
                if numeric_cols:
                    sub_cols = [y_col] + ([x_col] if x_col else [])
                    plot_data = df.dropna(subset=sub_cols)
                    fig = px.box(
                        plot_data,
                        x=x_col,
                        y=y_col,
                        color=x_col if x_col else None,
                        color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4"]
                    )
                    fig = apply_chart_layout(fig, f"Box Plot of {y_col}" + (f" by {x_col}" if x_col else ""), x_col or "", y_col)

            # Render Pie Chart
            elif chart_type == "Pie Chart":
                if cat_cols:
                    sub_cols = [cat_col] + ([val_col] if val_col else [])
                    plot_data = df.dropna(subset=sub_cols)
                    
                    unique_cat_count = plot_data[cat_col].nunique()
                    if unique_cat_count > 10:
                        st.caption(f"💡 Notice: '{cat_col}' contains {unique_cat_count} categories. Displaying top {top_slices} slices for optimal readability.")

                    if val_col:
                        pie_agg = plot_data.groupby(cat_col, as_index=False)[val_col].sum()
                        pie_agg.sort_values(by=val_col, ascending=False, inplace=True)
                        pie_top = pie_agg.head(top_slices)
                        fig = px.pie(
                            pie_top,
                            names=cat_col,
                            values=val_col,
                            color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4", "#8FB3AB", "#DE9E85"]
                        )
                    else:
                        counts = plot_data[cat_col].value_counts().head(top_slices).reset_index()
                        counts.columns = [cat_col, "Count"]
                        fig = px.pie(
                            counts,
                            names=cat_col,
                            values="Count",
                            color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4", "#8FB3AB", "#DE9E85"]
                        )
                    fig.update_layout(
                        title={"text": f"Composition by {cat_col}", "font": {"size": 16, "color": THEME_COLORS["text"]}},
                        paper_bgcolor="rgba(0,0,0,0)",
                        font={"family": "Plus Jakarta Sans, sans-serif", "color": THEME_COLORS["text"]}
                    )

            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Configure chart parameters on the left to render your visualization.")

        except Exception as e:
            st.error(f"Unable to render chart with current selections: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)
