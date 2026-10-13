"""
Intelligent Insights and Anomaly Detection Engine for Phase 6.
Performs deterministic, dataset-grounded profiling across numerical, categorical,
correlation, missing-value, and trend patterns.
Identifies potential outliers using the explainable Interquartile Range (IQR) method.
Never modifies the underlying dataset.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


def analyze_numeric_insights(df: pd.DataFrame, numeric_cols: List[str]) -> List[Dict[str, Any]]:
    """
    Computes statistical characteristics of numeric columns including skewness,
    variation (coefficient of variation), and quartile metrics.
    """
    insights = []
    if len(df) < 2 or not numeric_cols:
        return insights

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 2:
            continue

        mean_val = float(series.mean())
        median_val = float(series.median())
        std_val = float(series.std()) if len(series) > 1 else 0.0
        min_val = float(series.min())
        max_val = float(series.max())
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1

        # 1. Skewness check (Mean vs Median comparison)
        if abs(median_val) > 1e-5:
            rel_diff = (mean_val - median_val) / abs(median_val)
            if rel_diff > 0.15:
                diff_pct = rel_diff * 100
                insights.append({
                    "priority": "Medium",
                    "category": "Numerical",
                    "title": f"Right-Skewed Distribution in {col}",
                    "description": f"'{col}' exhibits a right-skewed distribution because the mean ({mean_val:,.2f}) is noticeably higher than the median ({median_val:,.2f}).",
                    "evidence": f"Mean: {mean_val:,.2f} • Median: {median_val:,.2f} • Difference: +{diff_pct:.1f}%",
                    "column": col
                })
            elif rel_diff < -0.15:
                diff_pct = abs(rel_diff) * 100
                insights.append({
                    "priority": "Medium",
                    "category": "Numerical",
                    "title": f"Left-Skewed Distribution in {col}",
                    "description": f"'{col}' exhibits a left-skewed distribution because the mean ({mean_val:,.2f}) is noticeably lower than the median ({median_val:,.2f}).",
                    "evidence": f"Mean: {mean_val:,.2f} • Median: {median_val:,.2f} • Difference: -{diff_pct:.1f}%",
                    "column": col
                })

        # 2. High Variation check (Coefficient of Variation = std / mean)
        if abs(mean_val) > 1e-5 and std_val > 0:
            cv = std_val / abs(mean_val)
            if cv > 1.0:
                insights.append({
                    "priority": "Medium",
                    "category": "Numerical",
                    "title": f"High Variability in {col}",
                    "description": f"'{col}' shows wide dispersion relative to its average value (coefficient of variation: {cv:.2f}).",
                    "evidence": f"Mean: {mean_val:,.2f} • Std Dev: {std_val:,.2f} • CV: {cv:.2f}",
                    "column": col
                })

    return insights


def detect_column_anomalies_iqr(df: pd.DataFrame, col: str) -> Dict[str, Any]:
    """
    Detects potential numerical outliers using the explainable IQR method:
    IQR = Q3 - Q1
    Lower Bound = Q1 - 1.5 * IQR
    Upper Bound = Q3 + 1.5 * IQR
    """
    series = df[col].dropna()
    total_records = len(series)
    if total_records < 4:
        return {
            "column": col,
            "total_records": total_records,
            "anomaly_count": 0,
            "anomaly_rate": 0.0,
            "lower_bound": None,
            "upper_bound": None,
            "table": pd.DataFrame()
        }

    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Identify anomalies
    low_mask = df[col] < lower_bound
    high_mask = df[col] > upper_bound
    anom_mask = low_mask | high_mask
    anom_count = int(anom_mask.sum())
    anom_rate = round((anom_count / total_records * 100), 2) if total_records > 0 else 0.0

    # Build anomaly detail records
    anom_rows = []
    if anom_count > 0:
        anom_indices = df[anom_mask].index
        for idx in anom_indices:
            val = df.loc[idx, col]
            direction = "High" if val > upper_bound else "Low"
            anom_rows.append({
                "Row Index": int(idx),
                "Column": col,
                "Value": float(val) if isinstance(val, (int, float, np.number)) else val,
                "Anomaly Direction": direction,
                "Lower Bound": round(lower_bound, 2),
                "Upper Bound": round(upper_bound, 2)
            })

    anom_df = pd.DataFrame(anom_rows)

    return {
        "column": col,
        "total_records": total_records,
        "anomaly_count": anom_count,
        "anomaly_rate": anom_rate,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "table": anom_df
    }


def analyze_all_anomalies(df: pd.DataFrame, numeric_cols: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Runs IQR anomaly detection across all numerical columns in the dataset.
    Returns: (list_of_insight_cards, dict_of_column_anomaly_results)
    """
    insights = []
    results = {}

    for col in numeric_cols:
        anom_res = detect_column_anomalies_iqr(df, col)
        results[col] = anom_res
        count = anom_res["anomaly_count"]
        rate = anom_res["anomaly_rate"]

        if count > 0:
            priority = "High" if rate >= 5.0 else "Medium"
            insights.append({
                "priority": priority,
                "category": "Anomalies",
                "title": f"Potential Anomalies Detected in {col}",
                "description": f"Identified {count:,} observations ({rate}% of non-null records) outside standard IQR boundaries in '{col}'.",
                "evidence": f"Bounds: [{anom_res['lower_bound']:,.2f}, {anom_res['upper_bound']:,.2f}] • Count: {count:,} ({rate}%)",
                "column": col,
                "anomaly_count": count,
                "anomaly_rate": rate
            })

    return insights, results


def analyze_categorical_insights(df: pd.DataFrame, cat_cols: List[str]) -> List[Dict[str, Any]]:
    """
    Analyzes category dominance, imbalance, and rare categories across text/categorical columns.
    """
    insights = []
    total_rows = len(df)
    if total_rows < 2 or not cat_cols:
        return insights

    for col in cat_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        counts = series.value_counts()
        unique_count = len(counts)
        top_category = counts.index[0]
        top_freq = counts.iloc[0]
        top_share = (top_freq / len(series)) * 100

        # Dominant Category / Imbalance (> 40% share)
        if top_share >= 40.0 and unique_count > 1:
            priority = "High" if top_share >= 65.0 else "Medium"
            insights.append({
                "priority": priority,
                "category": "Categorical",
                "title": f"Dominant Category in {col}",
                "description": f"'{top_category}' accounts for {top_share:.1f}% of all non-null entries in '{col}', indicating substantial category concentration.",
                "evidence": f"Top category: '{top_category}' • Share: {top_share:.1f}% ({top_freq:,} / {len(series):,} records)",
                "column": col
            })

        # Low-frequency / Rare categories (Categories with < 2% of records when unique > 4)
        if unique_count >= 5:
            rare_threshold = max(1, int(len(series) * 0.02))
            rare_cats = counts[counts <= rare_threshold]
            if len(rare_cats) > 0 and len(rare_cats) < unique_count:
                insights.append({
                    "priority": "Informational",
                    "category": "Categorical",
                    "title": f"Low-Frequency Categories in {col}",
                    "description": f"'{col}' contains {len(rare_cats)} low-frequency category groups representing <= 2% of observations each.",
                    "evidence": f"Distinct categories: {unique_count} • Rare categories count: {len(rare_cats)}",
                    "column": col
                })

    return insights


def analyze_group_performance_insights(df: pd.DataFrame, cat_cols: List[str], numeric_cols: List[str]) -> List[Dict[str, Any]]:
    """
    Evaluates group-level performance and variations (e.g. highest/lowest performing department by salary/revenue).
    """
    insights = []
    if len(df) < 3 or not cat_cols or not numeric_cols:
        return insights

    # Check top combinations
    for c_col in cat_cols[:2]:
        for n_col in numeric_cols[:2]:
            sub = df[[c_col, n_col]].dropna()
            if len(sub) < 3:
                continue

            grouped = sub.groupby(c_col, as_index=False)[n_col].mean()
            if len(grouped) < 2:
                continue

            grouped.sort_values(by=n_col, ascending=False, inplace=True)
            top_group = grouped.iloc[0]
            bottom_group = grouped.iloc[-1]
            overall_avg = sub[n_col].mean()

            top_val = top_group[n_col]
            bot_val = bottom_group[n_col]

            if abs(overall_avg) > 1e-5:
                diff_pct = ((top_val - overall_avg) / abs(overall_avg)) * 100
                if diff_pct >= 20.0:
                    insights.append({
                        "priority": "Medium",
                        "category": "Group Performance",
                        "title": f"Top-Performing {c_col} for {n_col}",
                        "description": f"The '{top_group[c_col]}' group leads in average {n_col} ({top_val:,.2f}), outperforming the overall average ({overall_avg:,.2f}) by {diff_pct:.1f}%.",
                        "evidence": f"Top group: '{top_group[c_col]}' ({top_val:,.2f}) • Overall average: {overall_avg:,.2f} (+{diff_pct:.1f}%)",
                        "group_col": c_col,
                        "metric_col": n_col
                    })

    return insights


def analyze_correlation_insights(df: pd.DataFrame, numeric_cols: List[str]) -> List[Dict[str, Any]]:
    """
    Computes Pearson correlation across numeric feature pairs and documents meaningful relationships.
    Strictly notes correlation does not imply causation.
    Thresholds:
    |r| < 0.3: weak
    0.3 <= |r| <= 0.7: moderate
    |r| > 0.7: strong
    """
    insights = []
    if len(df) < 3 or len(numeric_cols) < 2:
        return insights

    corr_matrix = df[numeric_cols].corr()
    checked_pairs = set()

    for i, col1 in enumerate(numeric_cols):
        for j, col2 in enumerate(numeric_cols):
            if i >= j:
                continue
            pair_key = tuple(sorted([col1, col2]))
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)

            r = corr_matrix.loc[col1, col2]
            if pd.isna(r):
                continue

            abs_r = abs(r)
            if abs_r >= 0.7:
                direction = "positive" if r > 0 else "negative"
                insights.append({
                    "priority": "High",
                    "category": "Correlations",
                    "title": f"Strong {direction.capitalize()} Correlation: {col1} & {col2}",
                    "description": f"'{col1}' and '{col2}' exhibit a strong {direction} linear relationship (r = {r:.2f}). Note: correlation does not imply causation.",
                    "evidence": f"Pearson r = {r:.3f} (|r| >= 0.7 classified as strong)",
                    "col_a": col1,
                    "col_b": col2,
                    "r": r
                })
            elif abs_r >= 0.4:
                direction = "positive" if r > 0 else "negative"
                insights.append({
                    "priority": "Medium",
                    "category": "Correlations",
                    "title": f"Moderate {direction.capitalize()} Correlation: {col1} & {col2}",
                    "description": f"'{col1}' and '{col2}' show a moderate {direction} linear correlation (r = {r:.2f}).",
                    "evidence": f"Pearson r = {r:.3f} (0.3 <= |r| <= 0.7 classified as moderate)",
                    "col_a": col1,
                    "col_b": col2,
                    "r": r
                })

    return insights


def analyze_missing_data_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Analyzes missing value rates and identifies high-risk columns.
    """
    insights = []
    total_records = len(df)
    if total_records == 0:
        return insights

    null_counts = df.isna().sum()
    null_cols = null_counts[null_counts > 0]

    if null_cols.empty:
        insights.append({
            "priority": "Informational",
            "category": "Data Quality",
            "title": "Clean Completeness",
            "description": "Zero missing values detected across all columns in the active working dataset.",
            "evidence": "100% complete records across all features."
        })
    else:
        for col, count in null_cols.items():
            rate = (count / total_records) * 100
            priority = "High" if rate >= 10.0 else "Medium"
            insights.append({
                "priority": priority,
                "category": "Data Quality",
                "title": f"Missing Values in {col}",
                "description": f"Column '{col}' has {count:,} missing values ({rate:.1f}% of records), which may impact downstream statistical calculations.",
                "evidence": f"Missing: {count:,} / {total_records:,} rows ({rate:.1f}%)",
                "column": col
            })

    return insights


def analyze_trend_insights(df: pd.DataFrame, date_cols: List[str], numeric_cols: List[str]) -> List[Dict[str, Any]]:
    """
    Evaluates temporal trends when a valid date/time column is available.
    """
    insights = []
    if len(df) < 3 or not date_cols or not numeric_cols:
        return insights

    date_col = date_cols[0]
    for metric in numeric_cols[:2]:
        sub = df[[date_col, metric]].dropna().copy()
        sub[date_col] = pd.to_datetime(sub[date_col], errors="coerce")
        sub = sub.dropna(subset=[date_col]).sort_values(by=date_col)
        if len(sub) < 3:
            continue

        start_val = sub.iloc[0][metric]
        end_val = sub.iloc[-1][metric]
        start_date = sub.iloc[0][date_col].strftime("%Y-%m-%d")
        end_date = sub.iloc[-1][date_col].strftime("%Y-%m-%d")

        if abs(start_val) > 1e-5:
            pct_change = ((end_val - start_val) / abs(start_val)) * 100
            direction = "increased" if pct_change > 0 else "decreased"
            priority = "Medium" if abs(pct_change) >= 15.0 else "Informational"
            insights.append({
                "priority": priority,
                "category": "Trends",
                "title": f"Chronological Trend in {metric}",
                "description": f"'{metric}' {direction} by {abs(pct_change):.1f}% from {start_date} to {end_date}.",
                "evidence": f"Initial ({start_date}): {start_val:,.2f} • Final ({end_date}): {end_val:,.2f} • Change: {pct_change:+.1f}%",
                "date_col": date_col,
                "metric_col": metric
            })

    return insights


def generate_dataset_insights(df: pd.DataFrame, filename: str = "dataset") -> Dict[str, Any]:
    """
    Orchestrates all analytical modules and prioritizes insights into High, Medium, and Informational tiers.
    """
    total_rows = len(df)
    total_cols = len(df.columns)

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    for col in df.columns:
        if col not in date_cols and col not in numeric_cols:
            if any(k in col.lower() for k in ["date", "time", "year", "month", "day", "timestamp"]):
                date_cols.append(col)

    # 1. Gather all insights
    num_insights = analyze_numeric_insights(df, numeric_cols)
    anom_insights, anomaly_details = analyze_all_anomalies(df, numeric_cols)
    cat_insights = analyze_categorical_insights(df, cat_cols)
    group_insights = analyze_group_performance_insights(df, cat_cols, numeric_cols)
    corr_insights = analyze_correlation_insights(df, numeric_cols)
    miss_insights = analyze_missing_data_insights(df)
    trend_insights = analyze_trend_insights(df, date_cols, numeric_cols)

    all_insights = (
        anom_insights +
        num_insights +
        corr_insights +
        group_insights +
        cat_insights +
        miss_insights +
        trend_insights
    )

    # 2. Prioritize insights
    high_priority = [i for i in all_insights if i.get("priority") == "High"]
    med_priority = [i for i in all_insights if i.get("priority") == "Medium"]
    info_priority = [i for i in all_insights if i.get("priority") == "Informational"]

    # Total anomalies across dataset
    total_anomalies = sum(res["anomaly_count"] for res in anomaly_details.values())

    return {
        "filename": filename,
        "rows": total_rows,
        "columns": total_cols,
        "numeric_cols": numeric_cols,
        "categorical_cols": cat_cols,
        "date_cols": date_cols,
        "total_insights_count": len(all_insights),
        "high_priority_count": len(high_priority),
        "total_anomalies_detected": total_anomalies,
        "insights_by_priority": {
            "High": high_priority,
            "Medium": med_priority,
            "Informational": info_priority
        },
        "all_insights": all_insights,
        "anomaly_details": anomaly_details
    }
