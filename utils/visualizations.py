"""
Exploratory Data Analysis and Plotly visualization utility module for Phase 4.
Generates responsive, publication-ready charts using the InsightFlow light color palette.
Does not mutate the underlying dataset.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional

# Primary styling colors matching project guidelines
THEME_COLORS = {
    "primary": "#648F86",
    "secondary": "#2F6B55",
    "accent": "#F2C6B4",
    "lavender": "#E8E1F5",
    "card_bg": "#FFF8ED",
    "text": "#30343B",
    "text_muted": "#68707D",
    "grid": "#EADBCC",
    "colorscale": ["#E2F3EC", "#648F86", "#30343B"]
}


def apply_chart_layout(fig: go.Figure, title: str, x_title: str = "", y_title: str = "") -> go.Figure:
    """
    Applies standard styling to Plotly figures matching the InsightFlow palette.
    """
    fig.update_layout(
        title={
            "text": title,
            "font": {"size": 16, "color": THEME_COLORS["text"], "family": "Plus Jakarta Sans, sans-serif"},
            "x": 0.02,
            "xanchor": "left"
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFF8ED",
        font={"family": "Plus Jakarta Sans, sans-serif", "color": THEME_COLORS["text"], "size": 12},
        margin={"l": 40, "r": 30, "t": 50, "b": 40},
        xaxis={
            "title": x_title,
            "gridcolor": THEME_COLORS["grid"],
            "zerolinecolor": THEME_COLORS["grid"],
            "showline": True,
            "linecolor": "#D8CFE8"
        },
        yaxis={
            "title": y_title,
            "gridcolor": THEME_COLORS["grid"],
            "zerolinecolor": THEME_COLORS["grid"],
            "showline": True,
            "linecolor": "#D8CFE8"
        },
        legend={
            "bgcolor": "rgba(255, 248, 237, 0.8)",
            "bordercolor": THEME_COLORS["grid"],
            "borderwidth": 1
        }
    )
    return fig


def plot_numeric_distribution(df: pd.DataFrame, column: str, bins: int = 30) -> go.Figure:
    """
    Creates an interactive histogram with KDE/frequency distribution.
    """
    data = df[column].dropna()
    fig = px.histogram(
        data,
        x=column,
        nbins=bins,
        marginal="box",
        color_discrete_sequence=[THEME_COLORS["primary"]]
    )
    fig = apply_chart_layout(fig, f"Distribution of {column}", column, "Frequency")
    return fig


def plot_numeric_boxplot(df: pd.DataFrame, y_col: str, x_col: Optional[str] = None) -> go.Figure:
    """
    Creates an interactive box plot, optionally grouped by a categorical variable.
    """
    clean_data = df.dropna(subset=[y_col])
    if x_col and x_col in df.columns:
        clean_data = clean_data.dropna(subset=[x_col])
        fig = px.box(
            clean_data,
            x=x_col,
            y=y_col,
            color=x_col,
            color_discrete_sequence=[THEME_COLORS["primary"], "#7D3B23", "#2F6B55", "#554477", "#F2C6B4"]
        )
        title = f"Box Plot of {y_col} grouped by {x_col}"
        x_label = x_col
    else:
        fig = px.box(
            clean_data,
            y=y_col,
            color_discrete_sequence=[THEME_COLORS["primary"]]
        )
        title = f"Box Plot of {y_col}"
        x_label = ""

    fig = apply_chart_layout(fig, title, x_label, y_col)
    return fig


def plot_category_frequencies(df: pd.DataFrame, column: str, top_n: int = 10) -> go.Figure:
    """
    Creates an interactive horizontal or vertical bar chart for category frequencies.
    """
    counts = df[column].dropna().value_counts().head(top_n).reset_index()
    counts.columns = [column, "Count"]

    fig = px.bar(
        counts,
        x=column,
        y="Count",
        text="Count",
        color_discrete_sequence=[THEME_COLORS["primary"]]
    )
    fig.update_traces(textposition="outside")
    fig = apply_chart_layout(fig, f"Top {top_n} Categories in {column}", column, "Count")
    return fig


def plot_missing_values(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Creates a bar chart visualizing missing values count and percentage per column.
    """
    null_counts = df.isna().sum()
    null_cols = null_counts[null_counts > 0].reset_index()
    if null_cols.empty:
        return None

    null_cols.columns = ["Column", "Missing Count"]
    null_cols["Percentage"] = ((null_cols["Missing Count"] / len(df)) * 100).round(2)
    null_cols.sort_values(by="Missing Count", ascending=False, inplace=True)

    fig = px.bar(
        null_cols,
        x="Column",
        y="Missing Count",
        text=null_cols["Percentage"].apply(lambda p: f"{p}%"),
        color="Missing Count",
        color_continuous_scale=[THEME_COLORS["accent"], "#7D3B23"]
    )
    fig.update_traces(textposition="outside")
    fig = apply_chart_layout(fig, "Missing Values Count & Percentage by Column", "Column", "Missing Count")
    fig.update_layout(coloraxis_showscale=False)
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, numeric_cols: List[str]) -> Optional[go.Figure]:
    """
    Creates an annotated correlation matrix heatmap for numeric columns.
    """
    if len(numeric_cols) < 2:
        return None

    corr_matrix = df[numeric_cols].corr().round(2)

    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Tealgrn",
        zmin=-1,
        zmax=1
    )
    fig = apply_chart_layout(fig, "Numeric Feature Correlation Matrix", "", "")
    return fig


def plot_scatter_relationship(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None
) -> go.Figure:
    """
    Creates an interactive scatter plot between two numeric variables, optionally colored by a third.
    """
    cols_to_drop = [x_col, y_col]
    if color_col and color_col in df.columns:
        cols_to_drop.append(color_col)

    clean_data = df.dropna(subset=cols_to_drop)

    fig = px.scatter(
        clean_data,
        x=x_col,
        y=y_col,
        color=color_col if color_col and color_col in df.columns else None,
        color_discrete_sequence=[THEME_COLORS["primary"], "#2F6B55", "#7D3B23", "#554477", "#F2C6B4"],
        trendline=None
    )
    title = f"{x_col} vs. {y_col}" + (f" by {color_col}" if color_col else "")
    fig = apply_chart_layout(fig, title, x_col, y_col)
    return fig


def plot_trend_timeseries(df: pd.DataFrame, date_col: str, val_col: str) -> go.Figure:
    """
    Creates an interactive time series line chart, sorted by date.
    Does not mutate original dataframe.
    """
    trend_df = df[[date_col, val_col]].dropna().copy()
    trend_df[date_col] = pd.to_datetime(trend_df[date_col], errors="coerce")
    trend_df = trend_df.dropna(subset=[date_col]).sort_values(by=date_col)

    fig = px.line(
        trend_df,
        x=date_col,
        y=val_col,
        color_discrete_sequence=[THEME_COLORS["primary"]],
        markers=True
    )
    fig = apply_chart_layout(fig, f"Trend of {val_col} over {date_col}", date_col, val_col)
    return fig


def compute_basic_statistical_observations(df: pd.DataFrame) -> List[str]:
    """
    Generates deterministic, factual statistical observations from the dataset.
    No LLM, no hallucinated assumptions, no ungrounded predictions.
    """
    observations = []
    total_records = len(df)
    total_features = len(df.columns)
    
    observations.append(f"The dataset contains {total_records:,} rows across {total_features} columns.")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()

    # Numeric observations
    if numeric_cols:
        for col in numeric_cols[:3]:  # Top 3 numeric columns
            mean_val = df[col].mean()
            median_val = df[col].median()
            min_val = df[col].min()
            max_val = df[col].max()
            if pd.notna(mean_val) and pd.notna(median_val):
                observations.append(
                    f"'{col}' has a mean of {mean_val:,.2f}, median of {median_val:,.2f}, with values ranging from {min_val:,.2f} to {max_val:,.2f}."
                )

    # Correlation observation
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        corr_vals = corr_matrix.values.copy()
        np.fill_diagonal(corr_vals, np.nan)
        corr_df = pd.DataFrame(corr_vals, index=corr_matrix.index, columns=corr_matrix.columns)
        abs_corr = corr_df.abs().stack()
        if not abs_corr.empty:
            max_pair = abs_corr.idxmax()
            corr_val = corr_matrix.loc[max_pair[0], max_pair[1]]
            observations.append(
                f"The highest linear correlation among numeric features is between '{max_pair[0]}' and '{max_pair[1]}' (r = {corr_val:.2f})."
            )

    # Categorical observations
    if cat_cols:
        for col in cat_cols[:2]:  # Top 2 categorical columns
            n_unique = df[col].nunique()
            top_val = df[col].mode(dropna=True)
            top_str = f"with '{top_val.iloc[0]}' being the most frequent" if not top_val.empty else ""
            observations.append(f"'{col}' contains {n_unique:,} distinct categories {top_str}.")

    # Missing value observation
    total_missing = int(df.isna().sum().sum())
    if total_missing > 0:
        missing_cols_count = sum(df[c].isna().sum() > 0 for c in df.columns)
        observations.append(f"A total of {total_missing:,} missing values are distributed across {missing_cols_count} column(s).")
    else:
        observations.append("The current working dataset contains zero missing values.")

    return observations
