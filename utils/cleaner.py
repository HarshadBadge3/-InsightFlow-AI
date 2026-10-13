"""
Data cleaning helper functions for Phase 3.
Provides explicit, user-controlled transformations for handling missing values, duplicates,
column names, whitespace trimming, safe data type casting, and empty column removal.
Never alters the dataset in-place or silently.
"""
import re
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional


def clean_column_name_string(col_name: str) -> str:
    """
    Standardizes a single column name:
    - Strips whitespace
    - Converts to lowercase
    - Replaces spaces and dashes with underscores
    - Removes punctuation / special characters (keeping alphanumeric and underscores)
    - Condenses multiple consecutive underscores
    """
    name = str(col_name).strip().lower()
    # Replace whitespace and hyphens with underscores
    name = re.sub(r'[\s\-]+', '_', name)
    # Remove any character that is not alphanumeric or underscore
    name = re.sub(r'[^\w]', '', name)
    # Condense consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Strip leading/trailing underscores
    name = name.strip('_')
    return name if name else "column"


def preview_clean_column_names(columns: List[str]) -> List[Dict[str, str]]:
    """
    Returns a mapping list of original column names to cleaned column names,
    handling any potential duplicate names created by cleaning.
    """
    seen = {}
    mapping = []
    for col in columns:
        cleaned = clean_column_name_string(col)
        # Prevent collisions
        if cleaned in seen:
            seen[cleaned] += 1
            cleaned = f"{cleaned}_{seen[cleaned]}"
        else:
            seen[cleaned] = 1
        mapping.append({"Original": col, "Cleaned": cleaned})
    return mapping


def apply_clean_column_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Applies column name standardization to the dataframe.
    Returns: (new_df, count_of_renamed_columns)
    """
    new_df = df.copy()
    preview = preview_clean_column_names(list(new_df.columns))
    rename_dict = {item["Original"]: item["Cleaned"] for item in preview}
    renamed_count = sum(1 for orig, cleaned in rename_dict.items() if orig != cleaned)
    new_df.rename(columns=rename_dict, inplace=True)
    return new_df, renamed_count


def handle_missing_values(
    df: pd.DataFrame,
    column: str,
    strategy: str,
    custom_value: Optional[str] = None
) -> Tuple[pd.DataFrame, int, Optional[str]]:
    """
    Handles missing values for a specific column based on selected strategy.
    Strategies for numeric: 'Mean', 'Median', 'Drop Rows'
    Strategies for categorical: 'Mode', 'Custom Value', 'Drop Rows'
    Returns: (new_df, affected_rows_count, error_message)
    """
    if column not in df.columns:
        return df, 0, f"Column '{column}' not found in dataset."

    new_df = df.copy()
    missing_mask = new_df[column].isna()
    affected_count = int(missing_mask.sum())

    if affected_count == 0:
        return new_df, 0, f"No missing values found in column '{column}'."

    try:
        if strategy == "Mean":
            if not pd.api.types.is_numeric_dtype(new_df[column]):
                return df, 0, f"Cannot calculate Mean for non-numeric column '{column}'."
            mean_val = new_df[column].mean()
            new_df[column] = new_df[column].fillna(mean_val)

        elif strategy == "Median":
            if not pd.api.types.is_numeric_dtype(new_df[column]):
                return df, 0, f"Cannot calculate Median for non-numeric column '{column}'."
            median_val = new_df[column].median()
            new_df[column] = new_df[column].fillna(median_val)

        elif strategy == "Mode":
            mode_series = new_df[column].mode(dropna=True)
            if mode_series.empty:
                return df, 0, f"Could not determine Mode for column '{column}'."
            mode_val = mode_series.iloc[0]
            new_df[column] = new_df[column].fillna(mode_val)

        elif strategy == "Custom Value":
            if custom_value is None or str(custom_value).strip() == "":
                return df, 0, "Custom fill value cannot be empty."
            # Attempt numeric conversion if column is numeric
            fill_val = custom_value
            if pd.api.types.is_numeric_dtype(new_df[column]):
                try:
                    fill_val = float(custom_value) if "." in str(custom_value) else int(custom_value)
                except ValueError:
                    return df, 0, f"Custom value '{custom_value}' is not a valid number for numeric column '{column}'."
            new_df[column] = new_df[column].fillna(fill_val)

        elif strategy == "Drop Rows":
            new_df = new_df.dropna(subset=[column])
            # Reset index cleanly
            new_df.reset_index(drop=True, inplace=True)

        else:
            return df, 0, f"Unknown missing value strategy '{strategy}'."

        return new_df, affected_count, None

    except Exception as e:
        return df, 0, f"Error processing missing values: {str(e)}"


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Removes duplicated rows from the dataset.
    Returns: (new_df, removed_duplicate_count)
    """
    new_df = df.copy()
    initial_rows = len(new_df)
    new_df = new_df.drop_duplicates()
    new_df.reset_index(drop=True, inplace=True)
    removed_count = initial_rows - len(new_df)
    return new_df, removed_count


def trim_text_whitespace(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, int]:
    """
    Strips leading and trailing whitespace from string/object columns.
    If columns is None, applies to all object/string columns.
    Returns: (new_df, count_of_cells_trimmed)
    """
    new_df = df.copy()
    target_cols = columns if columns else new_df.select_dtypes(include=["object", "string"]).columns.tolist()
    
    cells_trimmed = 0
    for col in target_cols:
        if col in new_df.columns and pd.api.types.is_object_dtype(new_df[col]) or pd.api.types.is_string_dtype(new_df[col]):
            # Calculate how many cells will change
            s = new_df[col].astype(str)
            trimmed = new_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            # Compare non-null changed entries
            mask = new_df[col].notna() & (new_df[col] != trimmed)
            cells_trimmed += int(mask.sum())
            new_df[col] = trimmed

    return new_df, cells_trimmed


def convert_column_type(
    df: pd.DataFrame,
    column: str,
    target_type: str
) -> Tuple[pd.DataFrame, int, Optional[str]]:
    """
    Safely converts a column's data type.
    Target types: 'Numeric', 'Text', 'Date'
    Coerces invalid entries without silently dropping them, and reports newly created nulls.
    Returns: (new_df, newly_created_missing_count, error_message)
    """
    if column not in df.columns:
        return df, 0, f"Column '{column}' does not exist in dataset."

    new_df = df.copy()
    original_nulls = int(new_df[column].isna().sum())

    try:
        if target_type == "Numeric":
            converted = pd.to_numeric(new_df[column], errors="coerce")
            new_nulls = int(converted.isna().sum())
            coerced_count = max(0, new_nulls - original_nulls)
            new_df[column] = converted
            return new_df, coerced_count, None

        elif target_type == "Date":
            converted = pd.to_datetime(new_df[column], errors="coerce")
            new_nulls = int(converted.isna().sum())
            coerced_count = max(0, new_nulls - original_nulls)
            new_df[column] = converted
            return new_df, coerced_count, None

        elif target_type == "Text":
            new_df[column] = new_df[column].astype(str)
            # Restore genuine None/NaN strings if previous value was NaN
            return new_df, 0, None

        else:
            return df, 0, f"Unsupported target type '{target_type}'."

    except Exception as e:
        return df, 0, f"Error converting column '{column}': {str(e)}"


def remove_empty_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Detects and drops columns where 100% of values are null/empty.
    Returns: (new_df, list_of_removed_column_names)
    """
    new_df = df.copy()
    empty_cols = [col for col in new_df.columns if new_df[col].isna().all()]
    if empty_cols:
        new_df.drop(columns=empty_cols, inplace=True)
    return new_df, empty_cols
