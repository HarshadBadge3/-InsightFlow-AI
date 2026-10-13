"""
InsightFlow AI — Test Suite: EDA & Visualizations (Phase 4)
Tests numeric distributions, box plots, category bar charts, correlation heatmaps,
scatter relationships, trend timeseries, and statistical observations.
"""
import unittest
import pandas as pd
from utils.visualizations import (
    plot_numeric_distribution,
    plot_numeric_boxplot,
    plot_category_frequencies,
    plot_missing_values,
    plot_correlation_heatmap,
    plot_scatter_relationship,
    plot_trend_timeseries,
    compute_basic_statistical_observations
)


class TestVisualizations(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "age": [20, 25, 30, 35, 40, 45, 50],
            "income": [30000.0, 35000.0, 50000.0, 55000.0, 70000.0, 80000.0, 95000.0],
            "dept": ["HR", "IT", "Sales", "IT", "Sales", "HR", "IT"],
            "date": pd.date_range("2024-01-01", periods=7, freq="D").strftime("%Y-%m-%d")
        })

    def test_plot_numeric_distribution(self):
        fig = plot_numeric_distribution(self.df, "age")
        self.assertIsNotNone(fig)
        self.assertEqual(fig.layout.title.text, "Distribution of age")

    def test_plot_numeric_boxplot(self):
        fig = plot_numeric_boxplot(self.df, "income", "dept")
        self.assertIsNotNone(fig)
        self.assertIn("income", fig.layout.title.text)

    def test_plot_category_frequencies(self):
        fig = plot_category_frequencies(self.df, "dept", top_n=5)
        self.assertIsNotNone(fig)
        self.assertIn("Top 5 Categories", fig.layout.title.text)

    def test_plot_correlation_heatmap(self):
        fig = plot_correlation_heatmap(self.df, ["age", "income"])
        self.assertIsNotNone(fig)
        self.assertEqual(fig.layout.title.text, "Numeric Feature Correlation Matrix")

    def test_plot_scatter_relationship(self):
        fig = plot_scatter_relationship(self.df, "age", "income", color_col="dept")
        self.assertIsNotNone(fig)
        self.assertIn("age vs. income", fig.layout.title.text)

    def test_plot_trend_timeseries(self):
        fig = plot_trend_timeseries(self.df, "date", "income")
        self.assertIsNotNone(fig)
        self.assertIn("Trend of income", fig.layout.title.text)

    def test_compute_basic_statistical_observations(self):
        obs = compute_basic_statistical_observations(self.df)
        self.assertTrue(len(obs) >= 3)
        self.assertTrue(any("rows across" in o for o in obs))


if __name__ == "__main__":
    unittest.main()
