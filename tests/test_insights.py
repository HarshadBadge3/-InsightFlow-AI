"""
InsightFlow AI — Test Suite: Intelligent Insights & Anomaly Detection (Phase 6)
Tests numerical skewness, coefficient of variation, categorical dominance,
Pearson correlation classification, time trends, and IQR anomaly detection.
"""
import unittest
import pandas as pd
from utils.insights import generate_dataset_insights, detect_column_anomalies_iqr


class TestInsights(unittest.TestCase):

    def test_iqr_anomaly_detection(self):
        # Normal values + 1 extreme outlier
        df = pd.DataFrame({"salary": [50000, 52000, 48000, 51000, 49000, 53000, 500000]})
        res = detect_column_anomalies_iqr(df, "salary")
        self.assertGreater(res["anomaly_count"], 0)
        self.assertIn("High", res["table"]["Anomaly Direction"].values)

    def test_skewness_detection(self):
        # Right-skewed distribution
        df = pd.DataFrame({
            "val": [10, 11, 12, 10, 11, 100, 150],
            "city": ["NY", "NY", "LA", "NY", "CHI", "NY", "LA"]
        })
        insights = generate_dataset_insights(df, "skew_test.csv")
        all_titles = [i["title"] for i in insights["all_insights"]]
        self.assertTrue(any("Skewed" in t for t in all_titles))

    def test_categorical_dominance(self):
        # 80% NY
        df = pd.DataFrame({"city": ["NY", "NY", "NY", "NY", "London"]})
        insights = generate_dataset_insights(df, "city_test.csv")
        all_titles = [i["title"] for i in insights["all_insights"]]
        self.assertTrue(any("Dominant Category" in t for t in all_titles))

    def test_correlation_insights(self):
        df = pd.DataFrame({
            "hours": [1, 2, 3, 4, 5, 6, 7],
            "score": [10, 20, 30, 40, 50, 60, 70]  # Perfect r = 1.0
        })
        insights = generate_dataset_insights(df, "corr_test.csv")
        all_titles = [i["title"] for i in insights["all_insights"]]
        self.assertTrue(any("Correlation:" in t for t in all_titles))

    def test_constant_column_graceful_handling(self):
        df = pd.DataFrame({"constant": [5, 5, 5, 5, 5]})
        res = detect_column_anomalies_iqr(df, "constant")
        self.assertEqual(res["anomaly_count"], 0)
        self.assertEqual(res["iqr"], 0.0)


if __name__ == "__main__":
    unittest.main()
