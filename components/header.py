"""
Header components for InsightFlow AI pages.
"""
import streamlit as st


def render_header(title: str, subtitle: str, badge: str = "InsightFlow AI • Phase 1"):
    """
    Renders a unified, modern header with breadcrumb badge and subtitle.
    """
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <span class="page-tag">{badge}</span>
            <h1 style="margin: 4px 0 8px 0; color: #30343B; font-weight: 700; font-size: 2.1rem;">
                {title}
            </h1>
            <p style="color: #68707D; font-size: 1.05rem; margin: 0; line-height: 1.5;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
