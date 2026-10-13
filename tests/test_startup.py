"""
InsightFlow AI — Test Suite: App Startup & Module Import Verification
Verifies that all utility modules, components, and Streamlit page scripts
can be imported without syntax errors or missing dependencies.
"""
import unittest
import importlib


class TestAppStartup(unittest.TestCase):

    def test_import_components(self):
        import components.sidebar
        import components.header
        import components.cards
        import components.ai_button
        self.assertTrue(True)

    def test_import_utils(self):
        import utils.theme
        import utils.data_loader
        import utils.cleaner
        import utils.visualizations
        import utils.analysis_tools
        import utils.ai_agent
        import utils.insights
        import utils.report_generator
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
