"""
Conversational AI Data Analyst Agent module.
Coordinates natural-language understanding, conversation context memory,
intent detection, analytical tool selection, and grounded response synthesis.
Calculations are executed purely via Pandas without external hallucinations.
"""
import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import requests

from utils.analysis_tools import (
    get_dataset_summary,
    calculate_numeric_statistic,
    group_and_aggregate,
    get_top_bottom_records,
    get_missing_value_summary,
    get_category_frequency,
    calculate_correlation,
    analyze_time_trend
)
from utils.visualizations import (
    plot_numeric_distribution,
    plot_numeric_boxplot,
    plot_category_frequencies,
    plot_missing_values,
    plot_correlation_heatmap,
    plot_scatter_relationship,
    plot_trend_timeseries
)


def get_api_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieves API key and endpoint configuration from environment variables.
    Checks AI_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY.
    """
    for key_name in ["AI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]:
        key = os.environ.get(key_name)
        if key and key.strip():
            return key.strip(), "gemini"

    for key_name in ["OPENAI_API_KEY"]:
        key = os.environ.get(key_name)
        if key and key.strip():
            return key.strip(), "openai"

    return None, None


def call_llm_json(prompt: str, api_key: str, provider: str) -> Optional[Dict[str, Any]]:
    """
    Calls configured LLM provider to extract structured analysis parameters as JSON.
    Gracefully returns None on timeout, connection error, or invalid formatting.
    """
    try:
        if provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"}
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_text)

        elif provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": "You output strictly valid JSON."}, {"role": "user", "content": prompt}],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"]
                return json.loads(raw_text)

    except Exception:
        pass
    return None


class ConversationalDataAnalystAgent:
    """
    Autonomous Data Analyst Agent that coordinates natural language understanding,
    context resolution, tool execution, and dataset-grounded responses.
    """

    def __init__(self, df: pd.DataFrame, filename: str = "dataset"):
        self.df = df
        self.filename = filename
        self.summary = get_dataset_summary(df, filename)
        self.numeric_cols = self.summary["numeric_columns"]
        self.cat_cols = self.summary["categorical_columns"]
        self.date_cols = self.summary["datetime_columns"]
        self.all_cols = self.summary["column_names"]

    def find_best_matching_column(self, term: str, candidates: Optional[List[str]] = None) -> Optional[str]:
        """
        Fuzzy matches a user-specified term to actual column names in the dataset.
        """
        if not term:
            return None
        t_clean = term.lower().strip().replace("_", " ").replace("-", " ")
        cols_to_check = candidates if candidates is not None else self.all_cols

        # Exact match
        for col in cols_to_check:
            if col.lower() == term.lower() or col.lower().strip() == t_clean:
                return col

        # Substring match
        for col in cols_to_check:
            c_clean = col.lower().replace("_", " ").replace("-", " ")
            if t_clean in c_clean or c_clean in t_clean:
                return col

        return None

    def generate_visualization_suggestions(self) -> List[str]:
        """
        Dynamically constructs contextual visualization suggestion prompts based on available dataset columns.
        """
        suggestions = []
        if self.numeric_cols:
            suggestions.append(f"Show a histogram of {self.numeric_cols[0]}")
        if self.cat_cols:
            suggestions.append(f"Show {self.cat_cols[0]} distribution")
        if self.numeric_cols and self.cat_cols:
            suggestions.append(f"Compare {self.numeric_cols[0]} by {self.cat_cols[0]}")
        if len(self.numeric_cols) >= 2:
            suggestions.append(f"Show a scatter plot of {self.numeric_cols[0]} and {self.numeric_cols[1]}")
        return suggestions

    def resolve_pronouns_and_context(self, question: str, last_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolves pronouns ('one', 'it', 'them') and relative follow-up modifications
        ('make it top 10', 'show as chart', 'and what about the lowest') using the last query context.
        """
        resolved = {
            "metric_col": None,
            "group_col": None,
            "aggregation": "mean",
            "limit": 5,
            "chart_requested": False
        }

        q_lower = question.lower()

        # Check if user is referencing previous context
        has_reference = any(ref in q_lower for ref in ["one", "it", "that", "same", "highest", "lowest", "top", "make it", "chart", "plot", "show", "visualize", "this"])

        if last_context and has_reference:
            resolved["metric_col"] = last_context.get("metric_col")
            resolved["group_col"] = last_context.get("group_col")
            resolved["aggregation"] = last_context.get("aggregation", "mean")
            resolved["limit"] = last_context.get("limit", 5)

        # Check for limit updates e.g., "make it top 10" or "top 3"
        limit_match = re.search(r'(?:top|bottom|limit|make it)\s*(\d+)', q_lower)
        if limit_match:
            resolved["limit"] = int(limit_match.group(1))

        # Check chart request (supports common spelling mistakes and variations)
        vis_pattern = re.compile(
            r'\b(?:visu\w*|visl\w*|chart\w*|graf\w*|graph\w*|grap\b|plot\w*|hist\w*|scatter\w*|box\s*plot\w*|bar\s*chart\w*|line\s*chart\w*|pie\s*chart\w*)\b',
            re.IGNORECASE
        )
        if vis_pattern.search(q_lower):
            resolved["chart_requested"] = True

        return resolved

    def parse_intent(self, question: str, last_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Determines the analytical intent and parameters.
        First attempts deterministic semantic pattern matching grounded in the active dataset schema.
        Optionally augments via LLM API if credentials are provided.
        """
        q_lower = question.lower().strip()
        context_res = self.resolve_pronouns_and_context(question, last_context)

        # 1. Dataset Overview / Structure Intent
        if any(k in q_lower for k in ["summary", "overview", "what is this data", "describe dataset", "how many rows", "how many columns", "dataset shape"]):
            return {"intent": "dataset_summary"}

        # 2. Missing Value Analysis Intent
        if any(k in q_lower for k in ["missing", "null", "nan", "empty values"]):
            return {"intent": "missing_values"}

        # 3. Correlation / Relationship Intent
        if any(k in q_lower for k in ["correlation", "correlated", "relationship between", "relation between"]):
            # Identify the two columns
            matched_cols = []
            for col in self.numeric_cols:
                if col.lower() in q_lower or col.lower().replace("_", " ") in q_lower:
                    matched_cols.append(col)
            if len(matched_cols) >= 2:
                return {
                    "intent": "correlation",
                    "col_a": matched_cols[0],
                    "col_b": matched_cols[1],
                    "chart": any(w in q_lower for w in ["chart", "plot", "scatter", "visualize"])
                }
            elif len(self.numeric_cols) >= 2:
                # Ambiguous or generic correlation question
                return {
                    "intent": "clarification",
                    "message": f"Which two numeric columns would you like to analyze for correlation? Available numeric columns: {', '.join(self.numeric_cols)}."
                }

        # 4. Temporal Trend Intent
        if any(k in q_lower for k in ["trend", "over time", "by month", "by year", "by date", "chronological"]):
            matched_metric = None
            for col in self.numeric_cols:
                if col.lower() in q_lower or col.lower().replace("_", " ") in q_lower:
                    matched_metric = col
                    break
            if not matched_metric and context_res["metric_col"]:
                matched_metric = context_res["metric_col"]

            if not self.date_cols:
                return {
                    "intent": "unsupported",
                    "message": "I couldn't perform trend analysis because no date/time columns are detected in this dataset."
                }
            if matched_metric:
                return {
                    "intent": "trend",
                    "date_col": self.date_cols[0],
                    "metric_col": matched_metric
                }

        # 5. Dedicated Visualization Intent (Evaluated before generic metric extraction)
        # Check if the query expresses visualization intent via keywords, natural phrases, or common misspellings
        vis_pattern = re.compile(
            r'\b(?:visu\w*|visl\w*|chart\w*|graf\w*|graph\w*|grap\b|plot\w*|hist\w*|scatter\w*|box\s*plot\w*|bar\s*chart\w*|line\s*chart\w*|pie\s*chart\w*)\b',
            re.IGNORECASE
        )
        is_visualization_query = bool(vis_pattern.search(q_lower))

        if is_visualization_query:
            # Check for explicitly mentioned columns
            v_metric = None
            for col in self.numeric_cols:
                if col.lower() in q_lower or col.lower().replace("_", " ") in q_lower:
                    v_metric = col
                    break

            v_group = None
            for col in self.cat_cols:
                if col.lower() in q_lower or col.lower().replace("_", " ") in q_lower:
                    v_group = col
                    break

            # If user referenced previous context (e.g., "visualize it", "show me a chart of that")
            if not v_metric and context_res["metric_col"]:
                v_metric = context_res["metric_col"]
            if not v_group and context_res["group_col"]:
                v_group = context_res["group_col"]

            # Scenario A: Metric and categorical group both present -> Grouped bar or box plot
            if v_metric and v_group:
                return {
                    "intent": "group_aggregation",
                    "metric_col": v_metric,
                    "group_col": v_group,
                    "aggregation": "mean",
                    "ascending": False,
                    "limit": 5,
                    "chart": True
                }

            # Scenario B: Two numeric columns mentioned -> Scatter plot
            matched_nums = [c for c in self.numeric_cols if c.lower() in q_lower or c.lower().replace("_", " ") in q_lower]
            if len(matched_nums) >= 2:
                return {
                    "intent": "correlation",
                    "col_a": matched_nums[0],
                    "col_b": matched_nums[1],
                    "chart": True
                }

            # Scenario C: Only a numeric column is identified
            if v_metric:
                if "box" in q_lower:
                    return {
                        "intent": "custom_visualization",
                        "chart_type": "box",
                        "column": v_metric
                    }
                else:
                    return {
                        "intent": "numeric_statistic",
                        "column": v_metric,
                        "statistic": "mean",
                        "chart": True
                    }

            # Scenario D: Only a categorical column is identified -> Frequency chart
            if v_group:
                return {
                    "intent": "category_frequency",
                    "column": v_group,
                    "limit": 10,
                    "chart": True
                }

            # Scenario E: General / Ambiguous Visualization Request without columns
            # Provide helpful, dataset-aware conversational clarification
            suggestions = self.generate_visualization_suggestions()
            if suggestions:
                sug_text = "\n".join([f"• {s}" for s in suggestions])
                clarification_msg = (
                    f"Sure! Which metric or relationship would you like to visualize in `{self.filename}`? You can ask for something like:\n{sug_text}"
                )
            else:
                clarification_msg = (
                    "Sure! Which metric or relationship would you like to visualize? I can create a bar chart, line chart, scatter plot, histogram, box plot, or pie chart."
                )

            return {
                "intent": "clarification",
                "message": clarification_msg
            }

        # 6. Group Aggregation Intent (e.g. "Which department has the highest salary?", "revenue by department")
        has_group_keyword = any(k in q_lower for k in ["by", "across", "per", "in each", "which", "highest category", "top category", "department", "category"])
        has_stat_keyword = any(k in q_lower for k in ["average", "mean", "highest", "lowest", "max", "maximum", "min", "minimum", "sum", "total", "median"])

        # Check for metric and group column in question or context
        detected_metric = None
        for col in self.numeric_cols:
            if col.lower() in q_lower or col.lower().replace("_", " ") in q_lower:
                detected_metric = col
                break
        if not detected_metric and ("one" in q_lower or "it" in q_lower or context_res["metric_col"]):
            detected_metric = context_res["metric_col"]

        detected_group = None
        for col in self.cat_cols:
            if col.lower() in q_lower or col.lower().replace("_", " ") in q_lower:
                detected_group = col
                break
        if not detected_group and context_res["group_col"]:
            detected_group = context_res["group_col"]

        # If metric is still missing but question is ambiguous: "Show me the highest value"
        if ("highest value" in q_lower or "lowest value" in q_lower or "what is the maximum" in q_lower) and not detected_metric:
            if len(self.numeric_cols) > 1:
                return {
                    "intent": "clarification",
                    "message": f"Which metric do you mean: {', '.join(self.numeric_cols[:4])}?"
                }
            elif len(self.numeric_cols) == 1:
                detected_metric = self.numeric_cols[0]

        # Determine aggregation
        agg = "mean"
        if any(w in q_lower for w in ["sum", "total"]):
            agg = "sum"
        elif any(w in q_lower for w in ["median"]):
            agg = "median"
        elif any(w in q_lower for w in ["min", "lowest", "minimum", "least"]):
            agg = "min"
        elif any(w in q_lower for w in ["max", "highest", "maximum", "peak", "top"]):
            agg = "max"

        ascending = any(w in q_lower for w in ["lowest", "bottom", "least", "min", "minimum"])

        # Limit
        limit = context_res["limit"]
        if "highest one" in q_lower or "which category has the highest" in q_lower or "which department has the highest" in q_lower:
            limit = 1

        # If user explicitly asks for distribution/histogram of a single column, prefer numeric distribution
        if detected_metric and ("distribution" in q_lower or "histogram" in q_lower) and not has_group_keyword:
            detected_group = None

        if detected_metric and detected_group:
            return {
                "intent": "group_aggregation",
                "metric_col": detected_metric,
                "group_col": detected_group,
                "aggregation": agg,
                "ascending": ascending,
                "limit": limit,
                "chart": context_res["chart_requested"]
            }

        # 7. Single Numeric Statistic Intent (e.g. "What is the average salary?", "What is the minimum age?")
        if detected_metric and (has_stat_keyword or "distribution" in q_lower or "spread" in q_lower):
            stat_name = "mean"
            if any(w in q_lower for w in ["median"]):
                stat_name = "median"
            elif any(w in q_lower for w in ["min", "lowest", "minimum", "least"]):
                stat_name = "min"
            elif any(w in q_lower for w in ["max", "highest", "maximum", "peak"]):
                stat_name = "max"
            elif any(w in q_lower for w in ["sum", "total"]):
                stat_name = "sum"
            elif any(w in q_lower for w in ["std", "standard deviation"]):
                stat_name = "std"
            elif any(w in q_lower for w in ["count", "rows"]):
                stat_name = "count"

            return {
                "intent": "numeric_statistic",
                "column": detected_metric,
                "statistic": stat_name,
                "chart": any(w in q_lower for w in ["distribution", "histogram", "chart", "plot", "spread", "box"])
            }

        # 8. Frequency Analysis Intent (e.g. "What are the most common departments?", "most frequent category")
        if detected_group:
            return {
                "intent": "category_frequency",
                "column": detected_group,
                "limit": limit,
                "chart": context_res["chart_requested"]
            }

        # 9. Ungrounded / Unavailable Information Guard
        pred_keywords = ["next month", "tomorrow", "forecast", "will buy", "will quit", "prediction", "predict", "churn next year"]
        if any(w in q_lower for w in pred_keywords):
            return {
                "intent": "unsupported",
                "message": f"I can't reliably predict future events or outcomes from the available dataset '{self.filename}' because it contains historical records without forward-looking predictive features."
            }

        # 10. General Conversational Fallback / Clarification
        # Handle partially understood or open-ended inquiries conversationally
        matched_any_col = None
        for col in self.all_cols:
            if col.lower() in q_lower or col.lower().replace("_", " ") in q_lower:
                matched_any_col = col
                break

        if matched_any_col:
            if matched_any_col in self.cat_cols:
                return {
                    "intent": "clarification",
                    "message": f"Sure. I can show the distribution of '{matched_any_col}' or compare numeric features across it. Which would you prefer?"
                }
            else:
                return {
                    "intent": "clarification",
                    "message": f"Sure. I can calculate the mean, min/max, distribution, or outliers for '{matched_any_col}'. What would you like to explore?"
                }

        if any(w in q_lower for w in ["tell me", "help me", "explore", "what can you do", "analyze", "hello", "hi"]):
            return {
                "intent": "clarification",
                "message": f"I can help with a dataset summary, statistics, trends, correlations, or visualizations for '{self.filename}'. What would you like to explore?"
            }

        return {
            "intent": "clarification",
            "message": f"I can help you explore '{self.filename}'. You can ask for a dataset summary, average statistics, correlations, group comparisons, or charts for: {', '.join(self.all_cols[:5])}."
        }

    def process_query(self, user_question: str, last_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes the full agent lifecycle:
        Question -> Intent & Parameters -> Tool Execution -> Grounded Response -> Context Update
        """
        intent_info = self.parse_intent(user_question, last_context)
        intent = intent_info.get("intent")

        response = {
            "intent": intent,
            "text": "",
            "table": None,
            "fig": None,
            "context": last_context or {}
        }

        # 1. Clarification
        if intent == "clarification":
            response["text"] = intent_info.get("message", "Could you please clarify your question?")
            return response

        # 2. Unsupported / Grounding Guard
        if intent == "unsupported":
            response["text"] = intent_info.get("message", "This question cannot be answered from the current dataset.")
            return response

        # 3. Dataset Summary
        if intent == "dataset_summary":
            sum_data = self.summary
            response["text"] = (
                f"**Dataset Overview for `{self.filename}`:**\n\n"
                f"• **Dimensions:** {sum_data['rows']:,} rows × {sum_data['columns']} columns\n"
                f"• **Numeric Columns ({len(sum_data['numeric_columns'])}):** {', '.join(sum_data['numeric_columns'][:6])}\n"
                f"• **Categorical Columns ({len(sum_data['categorical_columns'])}):** {', '.join(sum_data['categorical_columns'][:6])}\n"
                f"• **Total Missing Values:** {sum_data['total_missing']:,} cells"
            )
            return response

        # 4. Missing Values Analysis
        if intent == "missing_values":
            miss_data = get_missing_value_summary(self.df)
            if miss_data["total_missing"] == 0:
                response["text"] = f"No missing values were detected in `{self.filename}`."
            else:
                response["text"] = (
                    f"**Missing Value Summary:**\n\n"
                    f"• Total missing entries: **{miss_data['total_missing']:,}** ({miss_data['missing_percentage']}% of all cells)\n"
                    f"• Columns with missing entries: **{miss_data['columns_with_missing']}**"
                )
                if miss_data["breakdown"]:
                    response["table"] = pd.DataFrame(miss_data["breakdown"])
                    response["fig"] = plot_missing_values(self.df)
            return response

        # 5. Numeric Statistic
        if intent == "numeric_statistic":
            col = intent_info["column"]
            stat = intent_info["statistic"]
            result = calculate_numeric_statistic(self.df, col, stat)
            if "error" in result:
                response["text"] = result["error"]
                return response

            val = result["value"]
            val_str = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
            response["text"] = f"The **{result['statistic']}** of **{col}** is **{val_str}** (calculated across {result['count']:,} records)."
            
            # Save context for follow-ups
            response["context"] = {
                "metric_col": col,
                "statistic": stat
            }

            if intent_info.get("chart", False):
                response["fig"] = plot_numeric_distribution(self.df, col)
            return response

        # 6. Group Aggregation
        if intent == "group_aggregation":
            m_col = intent_info["metric_col"]
            g_col = intent_info["group_col"]
            agg = intent_info["aggregation"]
            limit = intent_info.get("limit", 5)
            asc = intent_info.get("ascending", False)

            result = group_and_aggregate(self.df, m_col, g_col, aggregation=agg, ascending=asc, limit=limit)
            if "error" in result:
                response["text"] = result["error"]
                return response

            table = result["table"]
            top_rec = result["top_record"]
            
            # Response formatting
            if limit == 1 and top_rec:
                val = top_rec['value']
                val_str = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
                direction_word = "lowest" if asc else "highest"
                response["text"] = (
                    f"The {g_col} with the **{direction_word} {agg} {m_col}** is **{top_rec['group']}** with **{val_str}**."
                )
            else:
                direction_word = "Bottom" if asc else "Top"
                response["text"] = (
                    f"Here are the **{direction_word} {len(table)}** {g_col} groups by {agg} {m_col}:"
                )
                response["table"] = table

            # Render Bar Chart if requested or if multiple groups
            if intent_info.get("chart", False) or len(table) > 1:
                response["fig"] = plot_category_frequencies(self.df, g_col, top_n=limit)

            # Update conversation memory
            response["context"] = {
                "metric_col": m_col,
                "group_col": g_col,
                "aggregation": agg,
                "ascending": asc,
                "limit": limit
            }
            return response

        # 7. Category Frequency
        if intent == "category_frequency":
            col = intent_info["column"]
            limit = intent_info.get("limit", 5)
            result = get_category_frequency(self.df, col, n=limit)
            if "error" in result:
                response["text"] = result["error"]
                return response

            top_val = result["most_frequent"]
            top_cnt = result["most_frequent_count"]
            response["text"] = (
                f"**{col}** has **{result['unique_categories']:,}** distinct categories. "
                f"The most frequent is **'{top_val}'** with **{top_cnt:,}** occurrences."
            )
            response["table"] = result["table"]
            response["fig"] = plot_category_frequencies(self.df, col, top_n=limit)
            response["context"] = {"group_col": col}
            return response

        # 8. Correlation
        if intent == "correlation":
            c_a = intent_info["col_a"]
            c_b = intent_info["col_b"]
            result = calculate_correlation(self.df, c_a, c_b)
            if "error" in result:
                response["text"] = result["error"]
                return response

            r_val = result["correlation"]
            strength = result["relationship_strength"]
            response["text"] = (
                f"The Pearson correlation between **{c_a}** and **{c_b}** is **{r_val:.3f}** ({strength} correlation)."
            )
            response["fig"] = plot_scatter_relationship(self.df, c_a, c_b)
            response["context"] = {"metric_col": c_b, "secondary_metric": c_a}
            return response

        # 9. Trend Analysis
        if intent == "trend":
            d_col = intent_info["date_col"]
            m_col = intent_info["metric_col"]
            result = analyze_time_trend(self.df, d_col, m_col)
            if "error" in result:
                response["text"] = result["error"]
                return response

            response["text"] = (
                f"Analyzed **{m_col}** over **{d_col}** from **{result['start_date']}** (value: {result['start_value']:,.2f}) "
                f"to **{result['end_date']}** (value: {result['end_value']:,.2f})."
            )
            response["fig"] = plot_trend_timeseries(self.df, d_col, m_col)
            response["context"] = {"metric_col": m_col, "date_col": d_col}
            return response

        # 10. Custom Visualization (e.g. standalone Box Plot)
        if intent == "custom_visualization":
            col = intent_info["column"]
            c_type = intent_info.get("chart_type", "box")
            if c_type == "box":
                response["text"] = f"Here is the box plot showing the distribution and quartiles for **{col}**:"
                response["fig"] = plot_numeric_boxplot(self.df, y_col=col)
                response["context"] = {"metric_col": col}
                return response

        return response
