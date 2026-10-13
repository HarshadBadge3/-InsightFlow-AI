"""
InsightFlow AI — Test Suite: Conversational AI Analyst Agent (Phase 5)
Tests natural-language queries, statistics calculations, aggregations, top/bottom records,
fuzzy column matching, pronoun/context resolution, chart requests, clarification handling,
and refusal of unsupported prediction questions.
"""
import unittest
import pandas as pd
from utils.ai_agent import ConversationalDataAnalystAgent


class TestAIAgent(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "employee_id": [101, 102, 103, 104, 105],
            "department": ["Engineering", "Marketing", "Engineering", "Sales", "Marketing"],
            "salary": [95000.0, 72000.0, 110000.0, 68000.0, 85000.0],
            "years_exp": [4, 2, 7, 1, 5]
        })
        self.agent = ConversationalDataAnalystAgent(self.df, "employees.csv")

    def test_summary_query(self):
        res = self.agent.process_query("Give me a summary of this dataset.")
        self.assertIn("5 rows", res["text"])
        self.assertIn("4 columns", res["text"])

    def test_average_statistic_query(self):
        res = self.agent.process_query("What is the average salary?")
        self.assertIn("salary", res["text"].lower())
        self.assertIn("mean", res["text"].lower())
        self.assertIn("86,000", res["text"])

    def test_aggregation_grouping_query(self):
        res = self.agent.process_query("What is the average salary by department?")
        self.assertIn("department", res["text"])
        self.assertIsNotNone(res["table"])

    def test_fuzzy_column_matching(self):
        # User says 'salary' in lower case
        res = self.agent.process_query("What is the mean of salary?")
        self.assertIn("86,000", res["text"])

    def test_top_records_query(self):
        res = self.agent.process_query("Which department has the highest salary?")
        self.assertIn("Engineering", res["text"])

    def test_pronoun_and_followup_resolution(self):
        # Turn 1
        res1 = self.agent.process_query("What is the average salary by department?")
        ctx = res1["context"]
        self.assertEqual(ctx.get("group_col"), "department")

        # Turn 2: Follow up with relative pronoun
        res2 = self.agent.process_query("Which one is the highest?", last_context=ctx)
        self.assertIn("department", res2["text"])
        self.assertIsNotNone(res2["table"])

    def test_unsupported_future_prediction_refusal(self):
        res = self.agent.process_query("Predict my salary next year")
        self.assertIn("predict", res["text"].lower())

    def test_chart_generation_intent(self):
        res = self.agent.process_query("Show me a chart of salary distribution")
        self.assertIsNotNone(res["fig"])

    def test_visualization_intent_give_me_visualization(self):
        res = self.agent.process_query("give me visualization")
        self.assertEqual(res["intent"], "clarification")
        self.assertIn("Which metric or relationship would you like to visualize", res["text"])
        self.assertIn("salary", res["text"])

    def test_visualization_intent_british_spelling(self):
        res = self.agent.process_query("give me visualisation")
        self.assertEqual(res["intent"], "clarification")
        self.assertIn("Which metric or relationship would you like to visualize", res["text"])

    def test_visualization_intent_typo_visualisatio(self):
        res = self.agent.process_query("Give me visualisatio")
        self.assertEqual(res["intent"], "clarification")
        self.assertIn("Which metric or relationship would you like to visualize", res["text"])
        self.assertNotIn("I couldn't identify the exact metric", res["text"])

    def test_visualization_intent_chart_graph_variations(self):
        for phrase in ["show me a chart", "show me a graph", "plot the data", "make a visualization"]:
            res = self.agent.process_query(phrase)
            self.assertEqual(res["intent"], "clarification")
            self.assertIn("visualize", res["text"].lower())

    def test_visualization_typos_visulization_grap_plott(self):
        for phrase in ["visulization", "show grap", "plott the data"]:
            res = self.agent.process_query(phrase)
            self.assertEqual(res["intent"], "clarification")
            self.assertIn("visualize", res["text"].lower())

    def test_visualization_with_column_histogram(self):
        res = self.agent.process_query("histogram of salary")
        self.assertIsNotNone(res["fig"])
        self.assertIn("salary", res["text"].lower())

    def test_visualization_with_column_boxplot(self):
        res = self.agent.process_query("box plot of salary")
        self.assertIsNotNone(res["fig"])
        self.assertIn("box plot", res["text"].lower())

    def test_visualization_two_numeric_scatter(self):
        res = self.agent.process_query("plot salary vs years_exp")
        self.assertIsNotNone(res["fig"])
        self.assertIn("salary", res["text"].lower())
        self.assertIn("years_exp", res["text"].lower())

    def test_visualization_followup_with_context(self):
        # Turn 1: Ask for average salary
        res1 = self.agent.process_query("What is the average salary?")
        ctx = res1["context"]
        self.assertEqual(ctx.get("metric_col"), "salary")

        # Turn 2: Follow up with "visualize this" or "show as chart"
        res2 = self.agent.process_query("visualize this", last_context=ctx)
        self.assertIsNotNone(res2["fig"])
        self.assertIn("salary", res2["text"].lower())

        res3 = self.agent.process_query("show as chart", last_context=ctx)
        self.assertIsNotNone(res3["fig"])


if __name__ == "__main__":
    unittest.main()

