"""
InsightFlow AI — Test Suite: Data Cleaning Engine (Phase 3)
Tests missing value strategies, duplicate row removal, column standardization,
whitespace trimming, data type conversion, empty column removal, and preservation.
"""
import unittest
import numpy as np
import pandas as pd
from utils.cleaner import (
    clean_column_name_string,
    preview_clean_column_names,
    apply_clean_column_names,
    handle_missing_values,
    remove_duplicates,
    trim_text_whitespace,
    convert_column_type,
    remove_empty_columns
)


class TestDataCleaner(unittest.TestCase):

    def test_clean_column_name_string(self):
        self.assertEqual(clean_column_name_string("  First Name! "), "first_name")
        self.assertEqual(clean_column_name_string("Annual-Salary ($)"), "annual_salary")
        self.assertEqual(clean_column_name_string("###"), "column")

    def test_apply_clean_column_names(self):
        df = pd.DataFrame({"Customer ID": [1], "Purchase Date": ["2024-01-01"]})
        cleaned_df, count = apply_clean_column_names(df)
        self.assertEqual(count, 2)
        self.assertIn("customer_id", cleaned_df.columns)
        self.assertIn("purchase_date", cleaned_df.columns)

    def test_handle_missing_values_mean(self):
        df = pd.DataFrame({"score": [10.0, np.nan, 30.0]})
        cleaned_df, count, err = handle_missing_values(df, "score", "Mean")
        self.assertIsNone(err)
        self.assertEqual(count, 1)
        self.assertEqual(cleaned_df["score"].iloc[1], 20.0)

    def test_handle_missing_values_mode(self):
        df = pd.DataFrame({"city": ["London", "Paris", "London", np.nan]})
        cleaned_df, count, err = handle_missing_values(df, "city", "Mode")
        self.assertIsNone(err)
        self.assertEqual(count, 1)
        self.assertEqual(cleaned_df["city"].iloc[3], "London")

    def test_handle_missing_values_drop(self):
        df = pd.DataFrame({"A": [1, np.nan, 3]})
        cleaned_df, count, err = handle_missing_values(df, "A", "Drop Rows")
        self.assertIsNone(err)
        self.assertEqual(len(cleaned_df), 2)

    def test_remove_duplicates(self):
        df = pd.DataFrame({"A": [1, 2, 2, 3], "B": ["x", "y", "y", "z"]})
        cleaned_df, removed = remove_duplicates(df)
        self.assertEqual(removed, 1)
        self.assertEqual(len(cleaned_df), 3)

    def test_trim_text_whitespace(self):
        df = pd.DataFrame({"name": ["  Alice ", "Bob\t", " Charlie "]})
        cleaned_df, trimmed = trim_text_whitespace(df)
        self.assertEqual(trimmed, 3)
        self.assertEqual(cleaned_df["name"].tolist(), ["Alice", "Bob", "Charlie"])

    def test_convert_column_type_numeric(self):
        df = pd.DataFrame({"val": ["10", "20", "invalid"]})
        cleaned_df, coerced, err = convert_column_type(df, "val", "Numeric")
        self.assertIsNone(err)
        self.assertEqual(coerced, 1)
        self.assertTrue(pd.isna(cleaned_df["val"].iloc[2]))

    def test_remove_empty_columns(self):
        df = pd.DataFrame({"A": [1, 2], "empty_col": [np.nan, np.nan]})
        cleaned_df, removed_cols = remove_empty_columns(df)
        self.assertIn("empty_col", removed_cols)
        self.assertEqual(len(cleaned_df.columns), 1)

    def test_preservation_of_original_dataframe(self):
        df = pd.DataFrame({"A": [1, np.nan, 3]})
        df_copy = df.copy()
        cleaned_df, _, _ = handle_missing_values(df, "A", "Mean")
        pd.testing.assert_frame_equal(df, df_copy)


if __name__ == "__main__":
    unittest.main()
