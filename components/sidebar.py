"""
Sidebar component for InsightFlow AI with active dataset status and quick navigation.
"""
import streamlit as st


def render_sidebar():
    """
    Renders brand identity, phase scope, dataset status, and navigation info in the sidebar.
    Reflects whether a dataset is currently loaded in st.session_state.
    """
    is_loaded = st.session_state.get("dataset_loaded", False)
    dataset_name = st.session_state.get("dataset_name", "None")

    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #D8CFE8; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: #648F86; color: white; border-radius: 8px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: bold;">
                        IF
                    </div>
                    <div>
                        <div style="font-weight: 700; font-size: 1.15rem; color: #30343B; line-height: 1.2;">InsightFlow AI</div>
                        <div style="font-size: 0.76rem; color: #68707D; font-weight: 500;">AI Data Analyst Workspace</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Dynamic dataset status display
        if is_loaded:
            status_dot = "#648F86"
            status_text = "Loaded"
            info_text = f"📄 <strong>{dataset_name}</strong>"
        else:
            status_dot = "#F2C6B4"
            status_text = "Not Loaded"
            info_text = "Upload via Dashboard"

        st.markdown(
            f"""
            <div style="background: #FFF8ED; border: 1px solid #EADBCC; border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #68707D; margin-bottom: 4px;">Dataset Status</div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="height: 9px; width: 9px; background-color: {status_dot}; border-radius: 50%; display: inline-block;"></span>
                    <span style="font-size: 0.88rem; font-weight: 600; color: #30343B;">{status_text}</span>
                </div>
                <div style="font-size: 0.76rem; color: #68707D; margin-top: 5px; word-break: break-all;">{info_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # If loaded, show simple "Remove Dataset" button in sidebar
        if is_loaded:
            if st.button("🗑️ Remove Dataset", key="sidebar_remove_dataset", use_container_width=True):
                st.session_state["dataset"] = None
                st.session_state["original_dataset"] = None
                st.session_state["dataset_name"] = None
                st.session_state["dataset_loaded"] = False
                st.session_state["dataset_info"] = None
                st.session_state["cleaning_log"] = []
                st.rerun()

        # Navigation shortcuts
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            if st.button("💬 AI Analyst", key="sidebar_launch_ai", use_container_width=True):
                st.switch_page("pages/7_AI_Assistant.py")
        with col_sb2:
            if st.button("📑 Reports", key="sidebar_launch_reports", use_container_width=True):
                st.switch_page("pages/6_Reports.py")

        st.markdown(
            """
            <div style="background: #E2F3EC; border: 1px solid #CDE7DC; border-radius: 8px; padding: 12px; margin: 12px 0 16px 0;">
                <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #2F6B55; margin-bottom: 2px;">Phase 8 Complete</div>
                <div style="font-size: 0.75rem; color: #2F6B55;">Production Ready Workspace</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.caption("InsightFlow AI • v1.0.0 (Production Ready)")
