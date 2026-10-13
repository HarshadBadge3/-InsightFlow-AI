# InsightFlow AI — Your Personal AI Data Analyst

> **Production Release (v1.0.0):** All development phases (Phases 1 through 8) are complete, fully tested, and regression-validated.

---

## 1. Project Overview

**InsightFlow AI** is a professional, full-featured data analytics workspace built in Python using Streamlit. It enables users to upload CSV and Excel datasets, inspect schemas, apply non-destructive data cleaning, perform exploratory data analysis (EDA), generate interactive visualizations, ask natural-language questions through an autonomous conversational data analyst agent, uncover statistical insights, detect numerical anomalies using the Interquartile Range (IQR) method, and export publication-grade PDF and standalone HTML reports.

All analytical calculations are grounded strictly in the active dataset. The system executes deterministic calculations via Pandas and NumPy, completely eliminating hallucinated statistics.

---

## 2. Project Architecture

```
                  ┌─────────────────────────────────────────┐
                  │           User File Ingestion           │
                  │        (CSV, XLSX, XLS Formats)         │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │          Dataset Understanding          │
                  │   (Schema profiling, types, metadata)   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │          Data Cleaning Engine           │
                  │    (Missing, Duplicates, Types, Trim)   │
                  │       [Preserves Original Dataset]      │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       EDA & Visualization Studio        │
                  │  (Distributions, Boxplots, Heatmaps)    │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │      Conversational AI Analyst          │
                  │    (Intent parsing, Pandas tools,       │
                  │     conversation memory & Plotly)       │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    Intelligent Insights & Anomalies     │
                  │   (Skewness, Pearson corr, IQR bounds)  │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │        Intelligent Report Engine        │
                  │    (Vector PDF & Standalone HTML)       │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │          Deployment & Runtime           │
                  │  (Production ready, headless Streamlit) │
                  └─────────────────────────────────────────┘
```

---

## 3. Key Features

### 📁 Dataset Ingestion & Understanding
- **Multi-Format Support:** Ingestion of `.csv`, `.xlsx`, and `.xls` files with automatic character encoding detection (UTF-8, Latin-1 fallback).
- **Session Isolation:** Dataset persistence across page transitions via Streamlit session state without saving user files to shared disk locations.
- **Structural Profiling:** Automatic identification of dimensions, column data types, missing value percentages, duplicate rows, and unique value cardinality.
- **Original Dataset Preservation:** Clean copy preserved in `st.session_state["original_dataset"]` allowing 1-click full reversion at any time.

### 🧹 User-Controlled Data Cleaning
- **Missing Value Imputation:** Imputation strategies for numerical features (Mean, Median, Custom, Drop) and categorical features (Mode, Custom, Drop) with impact previews.
- **Duplicate Row Deduplication:** Identification and removal of redundant records with before/after count comparisons.
- **Column Standardization:** Automatic conversion of arbitrary column names into standardized `snake_case`.
- **Text Whitespace Sanitization:** Elimination of leading, trailing, and redundant tab/space characters across text columns.
- **Safe Type Casting:** Controlled type coercion for numerical, date, and text columns with explicit null-coercion reporting.
- **Empty Column Pruning:** Detection and removal of columns with 100% missing values.
- **Audit Logging:** Continuous transformation log tracking all operations in `st.session_state["cleaning_log"]`.

### 🔍 Exploratory Data Analysis & Visualization Studio
- **Distribution Analysis:** Histograms with marginal box plots and kernel density representations.
- **Categorical Breakdown:** Frequency bar charts with configurable Top-N selectors (5, 10, 15, 20).
- **Correlation Heatmap:** Interactive Pearson correlation matrix with automated high-correlation callouts.
- **Multivariate Scatter Plots:** Bivariate relationships with optional third-variable categorical color grouping.
- **Time-Series Trends:** Chronological line charts sorted by detected date features.
- **Chart Builder:** Interactive builder supporting Bar, Line, Scatter, Histogram, Box, and Pie charts with aggregation controls (Sum, Mean, Median, Min, Max).

### ✨ Conversational AI Data Analyst Agent
- **Grounded Tool Execution:** Natural-language queries map directly to deterministic Pandas analytical tools; the agent never fabricates numbers.
- **Multi-Turn Memory:** Contextual memory resolves relative modifications (*"make it top 10"*, *"show that as a chart"*) and pronouns (*"which department has the highest one?"*).
- **Fuzzy Column Matching:** Resilient matching handles typos, alternate casings, and partial column names.
- **Refusal Guards:** Refuses speculative or forward-looking predictions not grounded in historical records and requests targeted clarification for ambiguous queries.
- **Dynamic Charts:** Automatically renders Plotly visual charts when requested in conversation.

### 💡 Intelligent Insights & IQR Anomaly Detection
- **Statistical Skewness:** Identifies distribution asymmetry when mean and median diverge by more than 15%.
- **Categorical Dominance:** Flags category concentration where a single category accounts for more than 40% of observations.
- **Correlation Classification:** Computes Pearson correlation coefficients ($|r| \ge 0.7$ Strong, $0.4 \le |r| < 0.7$ Moderate). Strict principle: correlation does not imply causation.
- **IQR Anomaly Detection:** Univariate outlier detection using the explainable formula:
  $$\text{IQR} = Q_3 - Q_1$$
  $$\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}, \quad \text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$$
- **Prioritization:** Automatically assigns High, Medium, or Informational priority to all discoveries.

### 📑 Publication-Grade Analytical Reports
- **Grounded Synthesis:** Compiles verified findings across all modules into an executive data model.
- **Vector PDF Export:** Multi-page PDF report generated via native `matplotlib.backends.backend_pdf.PdfPages` containing executive summaries, KPI cards, descriptive statistics tables, prioritized insights, and anomaly bounds.
- **Standalone HTML Export:** Self-contained, responsive HTML report styled in the curated InsightFlow color palette, viewable in any browser.
- **Scope Options:** Full Analysis and Executive Summary scopes.

---

## 4. UI Design System & Color Palette

InsightFlow AI uses a consistent, light color palette designed for readability:

| Color Role | Hex Code | Purpose |
|---|---|---|
| Main Background | `#F3F0FA` | Page background canvas |
| Card Background | `#FFF8ED` | KPI cards, containers, callout boxes |
| Secondary Accent | `#E2F3EC` | Success badges, active modules |
| Lavender Accent | `#E8E1F5` | Informational pills, tags |
| Primary Accent | `#648F86` | Primary action buttons, chart series |
| Soft Peach | `#F2C6B4` | Warning badges, pending status |
| Base Text | `#30343B` | High-contrast typography |

---

## 5. Technology Stack

- **Language:** Python 3.11+
- **Application Framework:** Streamlit (`>=1.30.0`)
- **Data Manipulation:** Pandas (`>=2.0.0`), NumPy (`>=1.26.0`)
- **Visualization:** Plotly (`>=5.18.0`), Matplotlib (`>=3.8.0`)
- **Excel Spreadsheet Parsers:** `openpyxl` (`>=3.1.2`), `xlrd` (`>=2.0.1`)
- **Configuration & Environment:** `python-dotenv` (`>=1.0.0`), `requests` (`>=2.31.0`)
- **Testing:** Python standard `unittest` framework

---

## 6. Project Structure

```
InsightFlow_AI/
│
├── app.py                      # Main entrypoint redirecting to Dashboard
├── requirements.txt            # Python dependencies
├── README.md                   # Complete project documentation
├── .gitignore                  # Git exclusions (bytecode, environments, secrets)
├── .env.example                # Sample environment configuration template
│
├── .streamlit/
│   └── config.toml             # Custom theme color mappings & server options
│
├── pages/
│   ├── 1_Dashboard.py          # Dashboard with live KPIs, upload zone & module cards
│   ├── 2_Dataset_Explorer.py   # Schema definitions, metadata breakdown, data preview
│   ├── 3_Data_Cleaning.py      # Interactive Cleaning Engine (Missing, Dups, Types, Reset)
│   ├── 4_EDA.py                # Exploratory Data Analysis (Distributions, Heatmaps, Scatter)
│   ├── 5_Visualizations.py     # Interactive Visualization Studio (Bar, Line, Box, Pie)
│   ├── 6_Reports.py            # Analytical Reports (Full/Summary Scope, PDF & HTML Exports)
│   ├── 7_AI_Assistant.py       # Conversational AI Data Analyst Agent (Chat & Context)
│   ├── 8_Settings.py           # Workspace preferences & configuration
│   └── 9_Insights.py           # Intelligent Insights & IQR Anomaly Detection Engine
│
├── components/
│   ├── header.py               # Top branding and page badge header
│   ├── sidebar.py              # Dynamic dataset status indicator & quick shortcuts
│   ├── cards.py                # Reusable KPI, navigation & empty state cards
│   └── ai_button.py            # Floating quick-access AI Analyst launcher
│
├── utils/
│   ├── theme.py                # CSS injection and brand palette styling
│   ├── data_loader.py          # Multi-encoding file parser and schema profiling
│   ├── cleaner.py              # Non-destructive data cleaning transformation logic
│   ├── visualizations.py       # Plotly chart builders & statistical observations
│   ├── analysis_tools.py       # Deterministic analytical functions (Aggregation, Stats)
│   ├── ai_agent.py             # Autonomous agent, intent parsing & conversation memory
│   ├── insights.py             # Automated insight engine & IQR anomaly detection
│   └── report_generator.py     # Analytical report compiler, PDF & HTML generators
│
└── tests/
    ├── test_startup.py         # Module import and startup test suite
    ├── test_data_loader.py     # File ingestion and schema profiling tests
    ├── test_cleaner.py         # Data cleaning transformation test suite
    ├── test_visualizations.py  # EDA and Plotly chart generation tests
    ├── test_ai_agent.py        # Conversational agent and memory test suite
    ├── test_insights.py        # Insights and IQR anomaly detection tests
    ├── test_reports.py         # Report compilation, PDF and HTML export tests
    └── test_end_to_end.py      # End-to-end integration and smoke test suite
```

---

## 7. Installation & Local Execution

### Prerequisites
- Python 3.10 or higher
- Git (optional)

### Setup Steps
1. Navigate to the project directory:
   ```bash
   cd InsightFlow_AI
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Set up environment variables:
   ```bash
   cp .env.example .env
   ```

5. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```
   Open your browser at `http://localhost:8501`.

---

## 8. Automated Testing

InsightFlow AI includes an automated test suite covering all modules:

```bash
python -m unittest discover -s tests -v
```

### Test Coverage Summary:
- **`test_startup.py`:** Verifies clean imports for all components and utility modules.
- **`test_data_loader.py`:** Tests CSV (UTF-8, Latin-1), Excel, unsupported formats, and empty files.
- **`test_cleaner.py`:** Validates missing value imputation, duplicate removal, column standardization, whitespace trimming, data type coercion, and original dataset preservation.
- **`test_visualizations.py`:** Tests histogram, box plot, frequency bar chart, correlation heatmap, scatter plot, and time-series line chart generation.
- **`test_ai_agent.py`:** Verifies natural-language query resolution, summary extraction, mean calculations, group aggregations, fuzzy column matching, pronoun resolution, and refusal of unsupported future predictions.
- **`test_insights.py`:** Tests distribution skewness, categorical dominance, Pearson correlation classification, and IQR anomaly detection.
- **`test_reports.py`:** Tests report data model compilation, standalone HTML rendering, multi-page vector PDF generation, and filename sanitization.
- **`test_end_to_end.py`:** Simulates the complete end-to-end user workflow from raw dirty data ingestion to cleaning, visualization, conversational analysis, insight discovery, and dual report export.

---

## 9. Deployment Guidelines

InsightFlow AI is architected for deployment across standard containerized and cloud platforms:

### Streamlit Community Cloud
1. Push the repository to GitHub.
2. Link the repository in [Streamlit Community Cloud](https://share.streamlit.io).
3. Set Main file path to `app.py`.
4. Deploy with one click.

### Docker Container Deployment
A standard production `Dockerfile` for InsightFlow AI:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 10. System Limitations & Boundaries

To ensure transparency, the following technical boundaries are noted:
- **Grounded Historical Analysis:** All analytical computations operate strictly on historical records present in the uploaded dataset. The application does not perform predictive forecasting, machine learning regression modeling, or speculative extrapolation.
- **Correlation Caution:** Statistical correlation does not imply causality; correlation findings reflect linear relationships only ($r$).
- **Session-Based Storage:** Datasets are isolated within the active Streamlit browser session. Closing or refreshing the browser resets the session. No persistent database or authentication layer is required.
- **Code Execution Safety:** The conversational AI analyst operates exclusively through predefined, deterministic Pandas analysis functions and does not execute arbitrary Python scripts from user text prompts.

---

## 11. Multi-Phase Roadmap Status

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Foundation, UI System & Multi-Page Navigation | Complete |
| **Phase 2** | CSV/Excel Upload & Dataset Understanding | Complete |
| **Phase 3** | Interactive Data Cleaning Engine | Complete |
| **Phase 4** | Exploratory Data Analysis & Visualization Studio | Complete |
| **Phase 5** | Conversational AI Data Analyst Agent | Complete |
| **Phase 6** | Intelligent Insights & IQR Anomaly Detection | Complete |
| **Phase 7** | Intelligent Report Generation (PDF & HTML) | Complete |
| **Phase 8** | Final Testing, Optimization & Deployment Readiness | Complete |
