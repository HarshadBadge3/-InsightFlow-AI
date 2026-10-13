"""
Floating AI Assistant button component.
Provides an attractive, modern button in the bottom-right corner to navigate to the AI Assistant page.
"""
import streamlit as st


def render_ai_floating_button():
    """
    Renders a floating AI Assistant access component at the bottom right.
    Uses HTML anchor targeting the AI Assistant page with matching color palette.
    """
    st.markdown(
        """
        <a href="AI_Assistant" target="_self" class="floating-ai-btn" title="Open AI Data Analyst">
            <span>✨</span>
            <span>AI Analyst</span>
        </a>
        """,
        unsafe_allow_html=True
    )
