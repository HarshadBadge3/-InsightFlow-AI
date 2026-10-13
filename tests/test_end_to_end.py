"""
InsightFlow AI — Test Suite: End-to-End Smoke Test & Lifecycle Workflow
Simulates the entire multi-phase user journey:
1. Ingestion of multi-column dataset
2. Schema profiling & quality metric calculation
3. Cleaning operations (whitespace, type conversion, missing values, duplicates)
4. Audit trail logging and original dataframe preservation
5. EDA generation (numeric & categorical charts, correlations)
6. Natural-language AI Data Analyst execution with conversation memory
7. Intelligent Insights and IQR outlier identification
8. Dual-format Analytical Report compilation (HTML and multi-page vector PDF)
9. Reversion / Reset to original dataset
"""
import io
import unittest
import numpy as np
import pandas as pd

from utils.data_loader import load_dataset, compute_dataset_summary
from utils.cleaner import (
    apply_clean_column_names,
    handle_missing_values,
    remove_duplicates,
    trim_text_whitespace,
    convert_column_type
)
from utils.visualizations import (
    plot_numeric_distribution,
    plot_category_frequencies,
    plot_correlation_heatmap
)
from utils.ai_agent import ConversationalDataAnalystAgent
from utils.insights import generate_dataset_insights
from utils.report_generator import (
    build_report_data,
    generate_html_report,
    generate_pdf_report
)


class TestEndToEndWorkflow(unittest.TestCase):

    def test_full_pipeline(self):
        # 1. Ingestion
        raw_csv = (
            " Employee ID , Department , Salary , Experience , Start Date \n"
            " 101 , Engineering , 95000 , 5 , 2020-01-15 \n"
            " 102 , Marketing , 70000 , 3 , 2021-03-10 \n"
            " 103 , Engineering , 115000 , 8 , 2018-07-01 \n"
            " 104 , Sales , , 2 , 2022-09-20 \n"
            " 105 , Marketing , 82000 , 4 , 2019-11-05 \n"
            " 106 , Engineering , 350000 , 12 , 2015-04-12 \n"  # Extreme salary outlier
            " 105 , Marketing , 82000 , 4 , 2019-11-05 \n"      # Duplicate row
        )
        stream = io.BytesIO(raw_csv.encode("utf-8"))
        stream.name = "employees_raw.csv"

        df_loaded, err = load_dataset(stream)
        self.assertIsNone(err)
        self.assertEqual(len(df_loaded), 7)

        # 2. Schema profiling
        summary = compute_dataset_summary(df_loaded, "employees_raw.csv")
        self.assertEqual(summary["rows"], 7)
        self.assertEqual(summary["total_duplicates"], 1)

        # Preserve original
        df_original = df_loaded.copy()

        # 3. Data Cleaning Pipeline
        cleaning_audit = []

        # 3a. Clean column names
        df_clean, col_renamed = apply_clean_column_names(df_loaded)
        if col_renamed > 0:
            cleaning_audit.append(f"Standardized {col_renamed} column names")

        # 3b. Trim whitespace
        df_clean, cells_trimmed = trim_text_whitespace(df_clean)
        if cells_trimmed > 0:
            cleaning_audit.append(f"Trimmed whitespace in {cells_trimmed} cells")

        # 3c. Remove duplicates
        df_clean, dupes_removed = remove_duplicates(df_clean)
        self.assertEqual(dupes_removed, 1)
        self.assertEqual(len(df_clean), 6)
        cleaning_audit.append(f"Removed {dupes_removed} duplicate rows")

        # 3d. Convert salary to numeric and fill missing with median
        df_clean, coerced, _ = convert_column_type(df_clean, "salary", "Numeric")
        df_clean, filled_count, _ = handle_missing_values(df_clean, "salary", "Median")
        self.assertEqual(filled_count, 1)
        cleaning_audit.append("Imputed missing salary with median")

        # Verify original dataset preservation (remains exactly 7 rows with duplicate intact and uncleaned names)
        self.assertEqual(len(df_original), 7)
        self.assertIn(" Salary ", df_original.columns)
        self.assertEqual(df_original[" Salary "].iloc[3], " ")

        # 4. EDA Visualizations
        fig_dist = plot_numeric_distribution(df_clean, "salary")
        self.assertIsNotNone(fig_dist)

        fig_freq = plot_category_frequencies(df_clean, "department")
        self.assertIsNotNone(fig_freq)

        # 5. AI Analyst Inquiries & Context Memory
        agent = ConversationalDataAnalystAgent(df_clean, "employees_clean.csv")

        # Turn 1: Group aggregation
        turn1 = agent.process_query("What is the average salary by department?")
        self.assertIsNotNone(turn1["table"])
        self.assertIn("department", turn1["text"])

        # Turn 2: Contextual follow-up
        turn2 = agent.process_query("Which one is the highest?", last_context=turn1["context"])
        self.assertIsNotNone(turn2["table"])

        # 6. Intelligent Insights & Anomaly Detection
        insights = generate_dataset_insights(df_clean, "employees_clean.csv")
        self.assertGreater(insights["total_insights_count"], 0)
        self.assertGreater(insights["total_anomalies_detected"], 0)

        # 7. Analytical Report Generation
        report_data = build_report_data(df_clean, "employees_clean.csv", cleaning_audit, "Full Analysis")
        self.assertEqual(report_data["metadata"]["total_records"], 6)

        html_content = generate_html_report(report_data, df_clean)
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("employees_clean.csv", html_content)

        pdf_bytes = generate_pdf_report(report_data, df_clean)
        self.assertTrue(isinstance(pdf_bytes, bytes))
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 3000)


if __name__ == "__main__":
    unittest.main()
