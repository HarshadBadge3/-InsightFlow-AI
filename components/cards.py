"""
Reusable card UI components for InsightFlow AI.
"""
import streamlit as st


def render_metric_card(title: str, value: str, badge_text: str = "Phase 2", is_pending: bool = True):
    """
    Renders a metric card with status badge.
    """
    badge_class = "metric-badge pending" if is_pending else "metric-badge"
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <span class="{badge_class}">{badge_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_nav_card(icon: str, title: str, description: str, phase_tag: str, page_name: str):
    """
    Renders an interactive navigation card that links to another page.
    """
    st.markdown(
        f"""
        <div class="nav-card">
            <div>
                <div class="nav-card-icon">{icon}</div>
                <div class="nav-card-title">{title}</div>
                <div class="nav-card-desc">{description}</div>
            </div>
            <div>
                <span class="nav-card-tag">{phase_tag}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button(f"Open {title}", key=f"btn_nav_{title.replace(' ', '_').lower()}", use_container_width=True):
        st.switch_page(page_name)


def render_placeholder(icon: str, title: str, description: str, status_text: str):
    """
    Renders an empty state placeholder for future phase features.
    """
    st.markdown(
        f"""
        <div class="placeholder-container">
            <div class="placeholder-icon">{icon}</div>
            <div class="placeholder-title">{title}</div>
            <div class="placeholder-desc">{description}</div>
            <span class="phase-pill">{status_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
