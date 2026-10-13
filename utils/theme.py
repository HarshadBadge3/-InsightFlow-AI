"""
Theme and styling configuration for InsightFlow AI.
Color Palette:
- Main Background: #F3F0FA
- Card Background: #FFF8ED
- Secondary Background: #E2F3EC
- Lavender: #E8E1F5
- Primary Accent: #648F86
- Soft Peach: #F2C6B4
- Text: #30343B
"""

COLORS = {
    "main_bg": "#F3F0FA",
    "card_bg": "#FFF8ED",
    "secondary_bg": "#E2F3EC",
    "lavender": "#E8E1F5",
    "primary_accent": "#648F86",
    "soft_peach": "#F2C6B4",
    "text": "#30343B",
    "text_muted": "#68707D",
    "border": "#E2DBEC",
    "shadow": "rgba(48, 52, 59, 0.06)",
    "white": "#FFFFFF"
}

CUSTOM_CSS = """
<style>
/* Font and root background styling */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #30343B;
}

.stApp {
    background-color: #F3F0FA;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #E8E1F5;
    border-right: 1px solid #D8CFE8;
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #30343B;
}

/* Top header / toolbar transparency */
header[data-testid="stHeader"] {
    background: transparent;
}

/* Base Card Styling */
.insight-card {
    background-color: #FFF8ED;
    border: 1px solid #EADBCC;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 14px rgba(48, 52, 59, 0.05);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.insight-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(48, 52, 59, 0.08);
}

/* Metric / Highlight Card */
.metric-box {
    background-color: #FFF8ED;
    border-radius: 12px;
    border: 1px solid #EADBCC;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(48, 52, 59, 0.04);
}

.metric-title {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #68707D;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #30343B;
    margin-bottom: 4px;
}

.metric-badge {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    background-color: #E2F3EC;
    color: #2F6B55;
}

.metric-badge.pending {
    background-color: #F2C6B4;
    color: #7D3B23;
}

/* Navigation & Action Cards */
.nav-card {
    background-color: #FFF8ED;
    border: 1px solid #EADBCC;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(48, 52, 59, 0.04);
    transition: all 0.2s ease;
}

.nav-card:hover {
    border-color: #648F86;
    box-shadow: 0 6px 18px rgba(100, 143, 134, 0.15);
}

.nav-card-icon {
    font-size: 1.8rem;
    margin-bottom: 12px;
}

.nav-card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #30343B;
    margin-bottom: 8px;
}

.nav-card-desc {
    font-size: 0.88rem;
    color: #68707D;
    line-height: 1.45;
    margin-bottom: 16px;
}

.nav-card-tag {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 4px;
    background-color: #E8E1F5;
    color: #554477;
    margin-top: auto;
}

/* Floating AI Button at bottom right */
.floating-ai-btn {
    position: fixed;
    bottom: 24px;
    right: 28px;
    z-index: 9999;
    background: #648F86;
    color: #FFFFFF !important;
    padding: 11px 18px;
    border-radius: 30px;
    box-shadow: 0 4px 18px rgba(100, 143, 134, 0.4);
    display: flex;
    align-items: center;
    gap: 9px;
    font-weight: 600;
    font-size: 0.92rem;
    text-decoration: none !important;
    border: 1.5px solid rgba(255, 255, 255, 0.35);
    transition: all 0.2s ease;
}

.floating-ai-btn:hover {
    background: #527A72;
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 24px rgba(100, 143, 134, 0.5);
    color: #FFFFFF !important;
}

/* Primary Button Styling */
div.stButton > button:first-child {
    background-color: #648F86;
    color: #FFFFFF;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    padding: 8px 18px;
    box-shadow: 0 2px 6px rgba(100, 143, 134, 0.25);
    transition: all 0.15s ease;
}

div.stButton > button:first-child:hover {
    background-color: #527A72;
    border: none;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(100, 143, 134, 0.35);
}

div.stButton > button:first-child:active {
    background-color: #43665F;
}

/* Secondary Button Styling */
div.stButton > button[kind="secondary"] {
    background-color: #FFF8ED;
    color: #30343B;
    border: 1px solid #EADBCC;
}

/* Empty State / Placeholder Container */
.placeholder-container {
    background-color: #FFF8ED;
    border: 1.5px dashed #D6CBBA;
    border-radius: 14px;
    padding: 44px 32px;
    text-align: center;
    margin: 20px 0;
}

.placeholder-icon {
    font-size: 2.8rem;
    margin-bottom: 12px;
}

.placeholder-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #30343B;
    margin-bottom: 8px;
}

.placeholder-desc {
    font-size: 0.95rem;
    color: #68707D;
    max-width: 540px;
    margin: 0 auto 18px auto;
    line-height: 1.5;
}

.phase-pill {
    display: inline-block;
    padding: 6px 14px;
    background-color: #E2F3EC;
    color: #2F6B55;
    font-weight: 700;
    font-size: 0.8rem;
    border-radius: 20px;
    letter-spacing: 0.03em;
}

/* Chat suggested questions */
.suggested-card {
    background-color: #FFF8ED;
    border: 1px solid #EADBCC;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    cursor: default;
    box-shadow: 0 2px 8px rgba(48, 52, 59, 0.03);
    transition: all 0.15s ease;
}

.suggested-card:hover {
    border-color: #648F86;
    background-color: #FFFFFF;
}

.suggested-card-text {
    font-size: 0.9rem;
    font-weight: 500;
    color: #30343B;
}

/* Breadcrumb / Page Tag */
.page-tag {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #648F86;
    background-color: #E2F3EC;
    padding: 3px 10px;
    border-radius: 12px;
    margin-bottom: 8px;
}

/* Responsive tweaks */
@media (max-width: 768px) {
    .floating-ai-btn {
        bottom: 16px;
        right: 16px;
        padding: 9px 14px;
        font-size: 0.82rem;
    }
    .placeholder-container {
        padding: 28px 16px;
    }
}
</style>
"""


def apply_theme():
    """Injects custom CSS theme into the active Streamlit app page."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
