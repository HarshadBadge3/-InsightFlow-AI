"""
InsightFlow AI — Data Cleaning Engine (Page 3)
Phase 3: Interactive, user-controlled data cleaning with previews, history log, reset, and export.
Never modifies data silently or automatically.
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
from utils.cleaner import (
    handle_missing_values,
    remove_duplicates,
    preview_clean_column_names,
    apply_clean_column_names,
    trim_text_whitespace,
    convert_column_type,
    remove_empty_columns
)
from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import render_metric_card
from components.ai_button import render_ai_floating_button

st.set_page_config(
    page_title="Data Cleaning | InsightFlow AI",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

render_header(
    title="Data Cleaning Engine",
    subtitle="Inspect data quality issues, apply user-controlled cleaning transformations, and track modifications.",
    badge="Module • Data Cleaning"
)

# Session state verification
df = st.session_state.get("dataset")
original_df = st.session_state.get("original_dataset")
is_loaded = st.session_state.get("dataset_loaded", False)

if "cleaning_log" not in st.session_state:
    st.session_state["cleaning_log"] = []

if not is_loaded or df is None:
    # Professional Empty State
    st.markdown(
        """
        <div class="placeholder-container">
            <div class="placeholder-icon">🧹</div>
            <div class="placeholder-title">No Dataset Loaded Yet</div>
            <div class="placeholder-desc">
                Upload a CSV or Excel dataset from the Dashboard to begin inspecting quality issues, 
                handling missing entries, removing duplicate rows, and standardizing schemas.
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
    # Ensure original_dataset is kept safe
    if original_df is None:
        st.session_state["original_dataset"] = df.copy()
        original_df = st.session_state["original_dataset"]

    # Compute current metrics
    filename = st.session_state.get("dataset_name", "dataset")
    info = compute_dataset_summary(df, filename)
    st.session_state["dataset_info"] = info

    total_rows = info["rows"]
    total_cols = info["cols"]
    total_missing = info["total_missing"]
    total_duplicates = info["total_duplicates"]
    
    # Columns with missing values
    cols_with_missing = [c for c in df.columns if df[c].isna().sum() > 0]
    
    # Empty columns count
    empty_cols_detected = [c for c in df.columns if df[c].isna().all()]

    # 1. Top Data Quality Overview Cards
    st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Data Quality Overview</h3>", unsafe_allow_html=True)
    q1, q2, q3, q4, q5 = st.columns(5)
    with q1:
        render_metric_card("Total Rows", f"{total_rows:,}", "Working Records", is_pending=False)
    with q2:
        render_metric_card("Total Columns", f"{total_cols}", "Features", is_pending=False)
    with q3:
        render_metric_card("Missing Values", f"{total_missing:,}", "Entries", is_pending=(total_missing > 0))
    with q4:
        render_metric_card("Duplicate Rows", f"{total_duplicates:,}", "Identified", is_pending=(total_duplicates > 0))
    with q5:
        render_metric_card("Cols with Missing", f"{len(cols_with_missing)}", "Columns", is_pending=(len(cols_with_missing) > 0))

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Interactive Cleaning Operations (Organized into structured tabs)
    st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Cleaning Operations</h3>", unsafe_allow_html=True)

    tab_missing, tab_dup, tab_cols, tab_text, tab_types, tab_empty = st.tabs([
        "🧩 Missing Values",
        "👥 Duplicate Rows",
        "🏷️ Column Names",
        "✂️ Text Whitespace",
        "🔄 Data Types",
        "🗑️ Empty Columns"
    ])

    # ---------------- TAB 1: MISSING VALUES ----------------
    with tab_missing:
        st.markdown("#### Handle Missing Values")
        st.markdown(
            "Select a column containing missing values, review the proposed strategy and estimated impact, "
            "then apply the operation explicitly."
        )

        if not cols_with_missing:
            st.success("🎉 No missing values detected in any column of the working dataset!")
        else:
            col_target = st.selectbox(
                "Select column to clean:",
                options=cols_with_missing,
                key="select_missing_col"
            )

            is_numeric = pd.api.types.is_numeric_dtype(df[col_target])
            miss_count = int(df[col_target].isna().sum())
            total_records = len(df)
            miss_pct = (miss_count / total_records * 100) if total_records > 0 else 0

            # Strategy Selection
            if is_numeric:
                strategies = ["Mean", "Median", "Custom Value", "Drop Rows"]
            else:
                strategies = ["Mode", "Custom Value", "Drop Rows"]

            col_opt1, col_opt2 = st.columns([1.5, 2])
            with col_opt1:
                selected_strategy = st.radio("Choose resolution strategy:", options=strategies, key="radio_missing_strat")

            custom_val = None
            with col_opt2:
                if selected_strategy == "Custom Value":
                    custom_val = st.text_input(
                        "Enter custom fill value:",
                        placeholder="e.g. Unknown or 0",
                        key="input_missing_custom"
                    )

            # Impact Preview Box
            st.markdown(
                f"""
                <div class="insight-card" style="background-color: #FFF8ED; border-left: 4px solid #648F86; padding: 14px 18px; margin: 12px 0;">
                    <strong>Proposed Transformation Preview:</strong><br>
                    • Target Column: <code>{col_target}</code> ({'Numeric' if is_numeric else 'Categorical/Text'})<br>
                    • Current Missing Values: <strong>{miss_count:,}</strong> ({miss_pct:.1f}% of column)<br>
                    • Selected Strategy: <strong>{selected_strategy}</strong><br>
                    • Estimated Affected Rows: <strong>{miss_count:,}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Apply Missing Value Strategy", type="primary", key="btn_apply_missing"):
                new_df, affected_count, err = handle_missing_values(df, col_target, selected_strategy, custom_val)
                if err:
                    st.error(f"❌ {err}")
                else:
                    detail = f"using {selected_strategy}" + (f" ('{custom_val}')" if custom_val else "")
                    log_entry = f"Filled missing values in '{col_target}' {detail} ({affected_count:,} values affected)"
                    if selected_strategy == "Drop Rows":
                        log_entry = f"Dropped rows with missing values in '{col_target}' ({affected_count:,} rows removed)"

                    st.session_state["dataset"] = new_df
                    st.session_state["cleaning_log"].append(log_entry)
                    st.success(f"✅ {log_entry}")
                    st.rerun()

    # ---------------- TAB 2: DUPLICATES ----------------
    with tab_dup:
        st.markdown("#### Remove Duplicate Rows")
        st.markdown("Detect exact duplicate records across all columns and optionally remove redundant rows.")

        if total_duplicates == 0:
            st.success("🎉 No duplicate rows found in the working dataset.")
        else:
            st.warning(f"⚠️ **{total_duplicates:,} duplicate rows** detected in the current working dataset.")
            expected_rows = total_rows - total_duplicates

            # Before / After Preview Box
            st.markdown(
                f"""
                <div class="insight-card" style="background-color: #FFF8ED; border-left: 4px solid #648F86; padding: 14px 18px; margin: 12px 0;">
                    <strong>Duplicate Removal Preview:</strong><br>
                    • Current Row Count: <strong>{total_rows:,}</strong><br>
                    • Duplicates Identified: <strong>{total_duplicates:,}</strong><br>
                    • Expected Row Count After Removal: <strong>{expected_rows:,}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Remove Duplicate Rows", type="primary", key="btn_apply_duplicates"):
                new_df, removed_count = remove_duplicates(df)
                log_entry = f"Removed {removed_count:,} duplicate rows (Row count changed: {total_rows:,} → {len(new_df):,})"
                st.session_state["dataset"] = new_df
                st.session_state["cleaning_log"].append(log_entry)
                st.success(f"✅ {log_entry}")
                st.rerun()

    # ---------------- TAB 3: COLUMN NAMES ----------------
    with tab_cols:
        st.markdown("#### Standardize Column Names")
        st.markdown(
            "Normalize column headers to clean snake_case: trims whitespace, converts to lowercase, "
            "replaces spaces with underscores, and safely removes special characters."
        )

        name_preview = preview_clean_column_names(list(df.columns))
        changed_names = [p for p in name_preview if p["Original"] != p["Cleaned"]]

        if not changed_names:
            st.success("🎉 All column names already follow standard naming conventions!")
        else:
            st.markdown(f"Found **{len(changed_names)}** column header(s) eligible for standardization:")
            st.dataframe(pd.DataFrame(name_preview), use_container_width=True, hide_index=True)

            if st.button("Standardize Column Names", type="primary", key="btn_apply_col_names"):
                new_df, renamed_count = apply_clean_column_names(df)
                log_entry = f"Standardized {renamed_count} column header(s) to snake_case format"
                st.session_state["dataset"] = new_df
                st.session_state["cleaning_log"].append(log_entry)
                st.success(f"✅ {log_entry}")
                st.rerun()

    # ---------------- TAB 4: TEXT WHITESPACE ----------------
    with tab_text:
        st.markdown("#### Trim Text Whitespace")
        st.markdown("Remove accidental leading and trailing whitespace from string/text columns (e.g. `' Sales '` → `'Sales'`).")

        text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
        if not text_cols:
            st.info("No text/categorical columns found in the current dataset.")
        else:
            trim_scope = st.radio(
                "Scope of whitespace trimming:",
                options=["All Text Columns", "Specific Column"],
                horizontal=True,
                key="radio_trim_scope"
            )

            target_trim_cols = text_cols
            if trim_scope == "Specific Column":
                chosen_col = st.selectbox("Select text column to trim:", options=text_cols, key="select_trim_col")
                target_trim_cols = [chosen_col]

            st.markdown(
                f"""
                <div class="insight-card" style="background-color: #FFF8ED; border-left: 4px solid #648F86; padding: 14px 18px; margin: 12px 0;">
                    <strong>Whitespace Trimming Scope:</strong><br>
                    • Columns Included: <code>{', '.join(target_trim_cols)}</code><br>
                    • Operation: Strips leading/trailing spaces without altering internal words or numeric values.
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Trim Whitespace", type="primary", key="btn_apply_trim"):
                new_df, cells_trimmed = trim_text_whitespace(df, target_trim_cols)
                log_entry = f"Trimmed whitespace across {len(target_trim_cols)} text column(s) ({cells_trimmed:,} cell values affected)"
                st.session_state["dataset"] = new_df
                st.session_state["cleaning_log"].append(log_entry)
                st.success(f"✅ {log_entry}")
                st.rerun()

    # ---------------- TAB 5: DATA TYPES ----------------
    with tab_types:
        st.markdown("#### Safe Data Type Conversion")
        st.markdown(
            "Convert columns into Numeric, Text, or Date representations safely. "
            "Values that cannot be converted are coerced into nulls and explicitly reported."
        )

        type_col_select = st.selectbox("Select column to convert:", options=list(df.columns), key="select_cast_col")
        current_type = str(df[type_col_select].dtype)

        c_opt1, c_opt2 = st.columns([1.5, 2])
        with c_opt1:
            st.markdown(f"Current Type: <code>{current_type}</code>", unsafe_allow_html=True)
            target_type = st.selectbox("Convert to target type:", options=["Numeric", "Date", "Text"], key="select_target_type")

        with c_opt2:
            st.markdown(
                f"""
                <div class="insight-card" style="background-color: #FFF8ED; border-left: 4px solid #648F86; padding: 12px 16px; margin: 0;">
                    <strong>Conversion Safeguard:</strong><br>
                    Non-parseable values will be coerced into null values rather than throwing fatal runtime exceptions. 
                    Any newly created nulls will be reported.
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button(f"Convert '{type_col_select}' to {target_type}", type="primary", key="btn_apply_cast"):
            new_df, coerced_count, err = convert_column_type(df, type_col_select, target_type)
            if err:
                st.error(f"❌ {err}")
            else:
                log_entry = f"Converted column '{type_col_select}' to {target_type}"
                if coerced_count > 0:
                    log_entry += f" ({coerced_count:,} unparseable values converted to null)"
                    st.warning(f"⚠️ {coerced_count:,} values could not be parsed as {target_type} and became null.")
                st.session_state["dataset"] = new_df
                st.session_state["cleaning_log"].append(log_entry)
                st.success(f"✅ {log_entry}")
                st.rerun()

    # ---------------- TAB 6: EMPTY COLUMNS ----------------
    with tab_empty:
        st.markdown("#### Remove Completely Empty Columns")
        st.markdown("Detect and remove columns that contain 100% missing values across all records.")

        if not empty_cols_detected:
            st.success("🎉 No completely empty columns found in the dataset.")
        else:
            st.warning(f"⚠️ **{len(empty_cols_detected)} completely empty column(s)** detected: `{'`, `'.join(empty_cols_detected)}`")

            st.markdown(
                f"""
                <div class="insight-card" style="background-color: #FFF8ED; border-left: 4px solid #648F86; padding: 14px 18px; margin: 12px 0;">
                    <strong>Columns Eligible for Removal:</strong><br>
                    • Columns: <code>{', '.join(empty_cols_detected)}</code><br>
                    • Current Column Count: <strong>{total_cols}</strong><br>
                    • Expected Column Count After Removal: <strong>{total_cols - len(empty_cols_detected)}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Remove Completely Empty Columns", type="primary", key="btn_apply_empty_cols"):
                new_df, removed_cols = remove_empty_columns(df)
                log_entry = f"Removed {len(removed_cols)} empty column(s): {', '.join(removed_cols)}"
                st.session_state["dataset"] = new_df
                st.session_state["cleaning_log"].append(log_entry)
                st.success(f"✅ {log_entry}")
                st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3. Cleaning History Log & Reset Controls
    st.markdown("<h3 style='font-size: 1.15rem; color: #30343B; margin-bottom: 12px;'>Audit Log & Dataset Controls</h3>", unsafe_allow_html=True)

    log_col, action_col = st.columns([1.6, 1])

    with log_col:
        st.markdown(
            """
            <div class="insight-card">
                <h4 style="margin: 0 0 10px 0; color: #30343B; font-size: 1.05rem;">📜 Cleaning Audit History</h4>
            """,
            unsafe_allow_html=True
        )

        cleaning_log = st.session_state.get("cleaning_log", [])
        if not cleaning_log:
            st.markdown("<p style='color: #68707D; font-size: 0.9rem; margin: 0;'>No cleaning transformations applied yet. Dataset is in original state.</p>", unsafe_allow_html=True)
        else:
            for idx, entry in enumerate(cleaning_log, start=1):
                st.markdown(
                    f"""
                    <div style="padding: 6px 0; border-bottom: 1px solid #EADBCC; font-size: 0.88rem; color: #30343B;">
                        <strong>{idx}.</strong> {entry}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("</div>", unsafe_allow_html=True)

    with action_col:
        st.markdown(
            """
            <div class="insight-card">
                <h4 style="margin: 0 0 10px 0; color: #30343B; font-size: 1.05rem;">⚙️ Management & Export</h4>
            """,
            unsafe_allow_html=True
        )

        # Reset Option with Confirmation
        st.markdown("<p style='font-size: 0.86rem; color: #68707D;'>Revert all cleaning changes back to the original uploaded file:</p>", unsafe_allow_html=True)
        reset_confirm = st.checkbox("Confirm reset to original data", key="chk_confirm_reset")
        if st.button("↺ Reset to Original Dataset", key="btn_reset_dataset", disabled=not reset_confirm):
            st.session_state["dataset"] = original_df.copy()
            st.session_state["cleaning_log"] = []
            st.session_state["dataset_info"] = compute_dataset_summary(original_df, filename)
            st.success("Dataset successfully restored to original uploaded state.")
            st.rerun()

        st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #EADBCC;'>", unsafe_allow_html=True)

        # Download Cleaned Dataset as CSV
        csv_data = df.to_csv(index=False).encode("utf-8")
        clean_filename = f"cleaned_{filename.rsplit('.', 1)[0]}.csv"

        st.download_button(
            label="📥 Download Cleaned CSV",
            data=csv_data,
            file_name=clean_filename,
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)
