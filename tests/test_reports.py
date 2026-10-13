"""
InsightFlow AI — Test Suite: Report Generation Engine (Phase 7)
Tests report data compilation, HTML report generation, multi-page vector PDF generation,
scope filtering, and filename sanitization.
"""
import unittest
import pandas as pd
from utils.report_generator import (
    build_report_data,
    generate_html_report,
    generate_pdf_report,
    sanitize_filename
)


class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "product_id": [f"P{i}" for i in range(20)],
            "price": [10.0, 12.5, 11.0, 15.0, 500.0] * 4,  # Outlier present
            "category": ["Food", "Books", "Food", "Fashion", "Tech"] * 4
        })

    def test_build_report_data_full(self):
        data = build_report_data(self.df, "products.csv", ["Cleaned 1 col"], "Full Analysis")
        self.assertEqual(data["metadata"]["total_records"], 20)
        self.assertEqual(data["metadata"]["scope"], "Full Analysis")
        self.assertGreater(len(data["statistics"]), 0)
        self.assertGreater(data["all_insights_count"], 0)

    def test_build_report_data_summary(self):
        data = build_report_data(self.df, "products.csv", scope="Summary")
        self.assertEqual(data["metadata"]["scope"], "Summary")
        self.assertTrue(len(data["insights"]) <= data["all_insights_count"])

    def test_generate_html_report(self):
        data = build_report_data(self.df, "products.csv")
        html = generate_html_report(data, self.df)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Executive Summary", html)
        self.assertIn("products.csv", html)

    def test_generate_pdf_report(self):
        data = build_report_data(self.df, "products.csv")
        pdf_bytes = generate_pdf_report(data, self.df)
        self.assertTrue(isinstance(pdf_bytes, bytes))
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 2000)

    def test_sanitize_filename(self):
        clean = sanitize_filename("Monthly Sales (Final) [2024].xlsx")
        self.assertEqual(clean, "Monthly_Sales__Final___2024_.xlsx")


if __name__ == "__main__":
    unittest.main()
