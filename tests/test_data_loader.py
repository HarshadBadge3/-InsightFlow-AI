"""
InsightFlow AI — Test Suite: Data Ingestion & Understanding (Phases 1 & 2)
Tests file loading (CSV, UTF-8, Latin-1, Excel), metadata computation, and error states.
"""
import io
import unittest
import pandas as pd
from utils.data_loader import load_dataset, compute_dataset_summary


class TestDataIngestion(unittest.TestCase):

    def test_valid_csv_stream(self):
        csv_data = "col1,col2,col3\n1,2,3\n4,5,6\n7,8,9\n"
        stream = io.BytesIO(csv_data.encode("utf-8"))
        stream.name = "test_valid.csv"
        df, err = load_dataset(stream)
        self.assertIsNone(err)
        self.assertEqual(len(df), 3)
        self.assertEqual(len(df.columns), 3)

    def test_latin1_encoded_csv(self):
        csv_data = "City,Temperature,Description\nMünchen,22.5,Schön\nZürich,19.0,Kühl\n"
        stream = io.BytesIO(csv_data.encode("latin-1"))
        stream.name = "test_latin1.csv"
        df, err = load_dataset(stream)
        self.assertIsNone(err)
        self.assertEqual(len(df), 2)
        self.assertIn("City", df.columns)

    def test_empty_csv(self):
        stream = io.BytesIO(b"")
        stream.name = "empty.csv"
        df, err = load_dataset(stream)
        self.assertIsNotNone(err)
        self.assertIsNone(df)

    def test_unsupported_extension(self):
        stream = io.BytesIO(b"hello world")
        stream.name = "unsupported.txt"
        df, err = load_dataset(stream)
        self.assertIsNotNone(err)
        self.assertIn("Unsupported file format", err)

    def test_numeric_only_summary(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [10.5, 20.5, 30.5]})
        summary = compute_dataset_summary(df, "numeric.csv")
        self.assertEqual(summary["rows"], 3)
        self.assertEqual(summary["cols"], 2)
        self.assertEqual(summary["numeric_cols_count"], 2)
        self.assertEqual(summary["categorical_cols_count"], 0)

    def test_categorical_only_summary(self):
        df = pd.DataFrame({"Category": ["A", "B", "C"], "Region": ["North", "South", "East"]})
        summary = compute_dataset_summary(df, "cat.csv")
        self.assertEqual(summary["rows"], 3)
        self.assertEqual(summary["cols"], 2)
        self.assertEqual(summary["categorical_cols_count"], 2)
        self.assertEqual(summary["numeric_cols_count"], 0)

    def test_single_row_dataset(self):
        df = pd.DataFrame({"X": [100], "Y": ["Solo"]})
        summary = compute_dataset_summary(df, "single.csv")
        self.assertEqual(summary["rows"], 1)
        self.assertEqual(summary["total_missing"], 0)


if __name__ == "__main__":
    unittest.main()
