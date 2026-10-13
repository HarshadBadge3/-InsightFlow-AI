"""
Dataset loading and inspection utilities for Phase 2.
Supports CSV, XLSX, and XLS formats with robust error handling and encoding fallbacks.
"""
import io
import pandas as pd
from typing import Tuple, Optional, Dict, Any


def load_dataset(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Reads an uploaded file (CSV, XLSX, XLS) into a Pandas DataFrame.
    Returns:
        (df, None) on success
        (None, error_message) on failure
    """
    if uploaded_file is None:
        return None, "No file uploaded."

    filename = uploaded_file.name.lower()
    
    try:
        if filename.endswith(".csv"):
            # Attempt standard UTF-8 read first, then fallback to latin1/cp1252 if needed
            content = uploaded_file.getvalue()
            if len(content) == 0:
                return None, "The uploaded CSV file is empty."
            
            try:
                df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.BytesIO(content), encoding="latin1")
                except Exception as enc_err:
                    return None, f"Could not decode CSV file: {str(enc_err)}"
            except pd.errors.EmptyDataError:
                return None, "The uploaded CSV file contains no data or columns."
            except Exception as e:
                return None, f"Error parsing CSV file: {str(e)}"

        elif filename.endswith(".xlsx"):
            content = uploaded_file.getvalue()
            if len(content) == 0:
                return None, "The uploaded Excel file is empty."
            try:
                df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
            except Exception as e:
                return None, f"Error parsing Excel (.xlsx) file: {str(e)}"

        elif filename.endswith(".xls"):
            content = uploaded_file.getvalue()
            if len(content) == 0:
                return None, "The uploaded Excel file is empty."
            try:
                df = pd.read_excel(io.BytesIO(content), engine="xlrd")
            except Exception as e:
                return None, f"Error parsing legacy Excel (.xls) file: {str(e)}"

        else:
            return None, f"Unsupported file format '{uploaded_file.name}'. Please upload a .csv, .xlsx, or .xls file."

        # Validate resulting dataframe
        if df.empty:
            return None, "The uploaded file was loaded, but contains zero rows."
        
        return df, None

    except Exception as e:
        return None, f"An unexpected error occurred while reading the file: {str(e)}"


def compute_dataset_summary(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
    """
    Calculates basic descriptive metadata and structural overview of the dataset.
    Does NOT modify the dataset.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    
    # Identify column data types
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    
    # Also check object columns that cleanly parse to datetime (basic check without mutating df)
    cat_cols = []
    detected_dates = list(datetime_cols)
    
    for col in df.columns:
        if col not in numeric_cols and col not in datetime_cols:
            cat_cols.append(col)
            
    total_missing = int(df.isna().sum().sum())
    total_duplicates = int(df.duplicated().sum())

    # Build per-column information summary
    col_summary = []
    for col in df.columns:
        col_summary.append({
            "Column": str(col),
            "Data Type": str(df[col].dtype),
            "Non-Null": int(df[col].notna().sum()),
            "Null": int(df[col].isna().sum()),
            "Unique": int(df[col].nunique(dropna=True))
        })
    col_summary_df = pd.DataFrame(col_summary)

    return {
        "filename": filename,
        "rows": total_rows,
        "cols": total_cols,
        "numeric_cols_count": len(numeric_cols),
        "categorical_cols_count": len(cat_cols),
        "datetime_cols_count": len(detected_dates),
        "numeric_cols": numeric_cols,
        "categorical_cols": cat_cols,
        "datetime_cols": detected_dates,
        "total_missing": total_missing,
        "total_duplicates": total_duplicates,
        "column_summary_df": col_summary_df
    }
