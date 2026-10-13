"""
Deterministic and safe analytical operations for the AI Data Analyst Agent.
Executes calculations directly using Python and Pandas.
Never modifies the underlying dataset in-place.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


def get_dataset_summary(df: pd.DataFrame, filename: str = "dataset") -> Dict[str, Any]:
    """
    Returns a structured summary of the dataset schema, data types, dimensions, and missing values.
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    # Detect additional date-like columns
    for col in df.columns:
        if col not in date_cols and col not in numeric_cols:
            if any(k in col.lower() for k in ["date", "time", "year", "month", "day", "timestamp"]):
                date_cols.append(col)

    null_counts = df.isna().sum()
    missing_dict = {col: int(null_counts[col]) for col in df.columns if null_counts[col] > 0}

    return {
        "filename": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "data_types": {col: str(df[col].dtype) for col in df.columns},
        "numeric_columns": numeric_cols,
        "categorical_columns": cat_cols,
        "datetime_columns": date_cols,
        "total_missing": int(null_counts.sum()),
        "missing_by_column": missing_dict
    }


def calculate_numeric_statistic(df: pd.DataFrame, column: str, statistic: str) -> Dict[str, Any]:
    """
    Calculates standard numeric statistics on a specific column.
    Supported statistics: mean, median, min, max, sum, std, count
    """
    if column not in df.columns:
        return {"error": f"Column '{column}' was not found in the dataset."}

    series = df[column].dropna()
    if not pd.api.types.is_numeric_dtype(series):
        # Attempt safe conversion
        coerced = pd.to_numeric(series, errors="coerce").dropna()
        if coerced.empty:
            return {"error": f"Column '{column}' contains non-numeric data and cannot be used for numeric statistics."}
        series = coerced

    stat_lower = statistic.strip().lower()
    val = None
    stat_name = stat_lower

    if stat_lower in ["mean", "average", "avg"]:
        val = series.mean()
        stat_name = "mean"
    elif stat_lower in ["median", "med"]:
        val = series.median()
        stat_name = "median"
    elif stat_lower in ["min", "minimum", "lowest", "least", "bottom"]:
        val = series.min()
        stat_name = "minimum"
    elif stat_lower in ["max", "maximum", "highest", "peak", "top"]:
        val = series.max()
        stat_name = "maximum"
    elif stat_lower in ["sum", "total"]:
        val = series.sum()
        stat_name = "sum"
    elif stat_lower in ["std", "standard deviation", "stddev"]:
        val = series.std()
        stat_name = "standard deviation"
    elif stat_lower in ["count", "rows", "records"]:
        val = len(series)
        stat_name = "count"
    else:
        return {"error": f"Unsupported statistic '{statistic}'. Supported: mean, median, min, max, sum, std, count."}

    return {
        "column": column,
        "statistic": stat_name,
        "value": float(val) if isinstance(val, (int, float, np.number)) else val,
        "count": len(series)
    }


def group_and_aggregate(
    df: pd.DataFrame,
    metric_col: str,
    group_col: str,
    aggregation: str = "mean",
    ascending: bool = False,
    limit: Optional[int] = 5
) -> Dict[str, Any]:
    """
    Groups by a categorical column and aggregates a numeric metric column.
    Supported aggregations: mean, sum, median, min, max, count
    """
    if group_col not in df.columns:
        return {"error": f"Group column '{group_col}' was not found in the dataset."}
    if metric_col not in df.columns:
        return {"error": f"Metric column '{metric_col}' was not found in the dataset."}

    sub_df = df[[group_col, metric_col]].dropna().copy()
    if not pd.api.types.is_numeric_dtype(sub_df[metric_col]):
        sub_df[metric_col] = pd.to_numeric(sub_df[metric_col], errors="coerce")
        sub_df = sub_df.dropna()
        if sub_df.empty:
            return {"error": f"Metric column '{metric_col}' contains no valid numeric values."}

    agg_lower = aggregation.strip().lower()
    agg_map = {
        "mean": "mean", "average": "mean", "avg": "mean",
        "sum": "sum", "total": "sum",
        "median": "median",
        "min": "min", "minimum": "min", "lowest": "min",
        "max": "max", "maximum": "max", "highest": "max",
        "count": "count"
    }

    if agg_lower not in agg_map:
        return {"error": f"Unsupported aggregation '{aggregation}'. Supported: mean, sum, median, min, max, count."}

    pandas_agg = agg_map[agg_lower]
    grouped = sub_df.groupby(group_col, as_index=False)[metric_col].agg(pandas_agg)
    grouped.sort_values(by=metric_col, ascending=ascending, inplace=True)

    if limit and limit > 0:
        result_df = grouped.head(limit)
    else:
        result_df = grouped

    # Prepare top/best result
    top_record = None
    if not result_df.empty:
        best_row = result_df.iloc[0]
        top_record = {
            "group": str(best_row[group_col]),
            "value": float(best_row[metric_col]) if isinstance(best_row[metric_col], (int, float, np.number)) else best_row[metric_col]
        }

    return {
        "group_column": group_col,
        "metric_column": metric_col,
        "aggregation": pandas_agg,
        "ascending": ascending,
        "limit": limit,
        "top_record": top_record,
        "table": result_df
    }


def get_top_bottom_records(
    df: pd.DataFrame,
    column: str,
    n: int = 5,
    ascending: bool = False
) -> Dict[str, Any]:
    """
    Returns the top or bottom N records sorted by a specific column.
    """
    if column not in df.columns:
        return {"error": f"Column '{column}' was not found in the dataset."}

    sorted_df = df.dropna(subset=[column]).sort_values(by=column, ascending=ascending).head(n)
    return {
        "column": column,
        "n": n,
        "direction": "bottom" if ascending else "top",
        "table": sorted_df
    }


def get_missing_value_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes an exact breakdown of missing data in the dataset.
    """
    total_cells = df.size
    total_missing = int(df.isna().sum().sum())
    missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0

    null_series = df.isna().sum()
    null_cols = null_series[null_series > 0]
    
    breakdown = []
    for col, count in null_cols.items():
        breakdown.append({
            "Column": col,
            "Missing Count": int(count),
            "Percentage": f"{(count / len(df) * 100):.2f}%"
        })

    return {
        "total_missing": total_missing,
        "missing_percentage": round(missing_pct, 2),
        "columns_with_missing": len(null_cols),
        "breakdown": breakdown
    }


def get_category_frequency(df: pd.DataFrame, column: str, n: int = 5) -> Dict[str, Any]:
    """
    Computes frequency and proportions for a categorical column.
    """
    if column not in df.columns:
        return {"error": f"Column '{column}' was not found in the dataset."}

    series = df[column].dropna()
    total_count = len(series)
    unique_count = series.nunique()
    
    vc = series.value_counts().head(n).reset_index()
    vc.columns = [column, "Count"]
    vc["Percentage"] = ((vc["Count"] / total_count) * 100).round(2).astype(str) + "%"

    most_frequent = vc.iloc[0][column] if not vc.empty else None
    most_frequent_count = int(vc.iloc[0]["Count"]) if not vc.empty else 0

    return {
        "column": column,
        "unique_categories": unique_count,
        "most_frequent": most_frequent,
        "most_frequent_count": most_frequent_count,
        "table": vc
    }


def calculate_correlation(df: pd.DataFrame, col_a: str, col_b: str) -> Dict[str, Any]:
    """
    Calculates Pearson correlation between two numeric columns.
    """
    if col_a not in df.columns:
        return {"error": f"Column '{col_a}' was not found in the dataset."}
    if col_b not in df.columns:
        return {"error": f"Column '{col_b}' was not found in the dataset."}

    sub_df = df[[col_a, col_b]].dropna()
    if not pd.api.types.is_numeric_dtype(sub_df[col_a]) or not pd.api.types.is_numeric_dtype(sub_df[col_b]):
        return {"error": f"Both '{col_a}' and '{col_b}' must be numeric to calculate correlation."}

    corr_val = sub_df[col_a].corr(sub_df[col_b])
    
    if pd.isna(corr_val):
        desc = "Undefined (one or both columns have zero variance)"
    elif abs(corr_val) > 0.7:
        desc = "Strong " + ("positive" if corr_val > 0 else "negative")
    elif abs(corr_val) > 0.3:
        desc = "Moderate " + ("positive" if corr_val > 0 else "negative")
    else:
        desc = "Weak or negligible"

    return {
        "column_a": col_a,
        "column_b": col_b,
        "correlation": round(float(corr_val), 3) if pd.notna(corr_val) else 0.0,
        "relationship_strength": desc
    }


def analyze_time_trend(df: pd.DataFrame, date_col: str, metric_col: str) -> Dict[str, Any]:
    """
    Calculates temporal trend metrics (earliest date, latest date, overall change).
    """
    if date_col not in df.columns or metric_col not in df.columns:
        return {"error": "Specified date or metric column was not found."}

    trend_df = df[[date_col, metric_col]].dropna().copy()
    trend_df[date_col] = pd.to_datetime(trend_df[date_col], errors="coerce")
    trend_df = trend_df.dropna(subset=[date_col]).sort_values(by=date_col)

    if trend_df.empty:
        return {"error": "No valid chronological date entries found."}

    start_val = trend_df.iloc[0][metric_col]
    end_val = trend_df.iloc[-1][metric_col]
    earliest = trend_df.iloc[0][date_col].strftime("%Y-%m-%d")
    latest = trend_df.iloc[-1][date_col].strftime("%Y-%m-%d")

    return {
        "date_column": date_col,
        "metric_column": metric_col,
        "start_date": earliest,
        "end_date": latest,
        "start_value": float(start_val) if isinstance(start_val, (int, float, np.number)) else start_val,
        "end_value": float(end_val) if isinstance(end_val, (int, float, np.number)) else end_val,
        "record_count": len(trend_df)
    }
