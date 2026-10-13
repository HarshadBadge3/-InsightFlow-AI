"""
InsightFlow AI — Conversational AI Data Analyst Agent (Page 7)
Phase 5: Natural language querying with multi-turn conversation memory,
safe tool selection, Pandas calculations, and grounded responses.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from utils.theme import apply_theme
from utils.data_loader import compute_dataset_summary
from utils.ai_agent import ConversationalDataAnalystAgent, get_api_credentials
from components.sidebar import render_sidebar
from components.header import render_header
from components.cards import render_metric_card
from components.ai_button import render_ai_floating_button

st.set_page_config(
    page_title="AI Data Analyst | InsightFlow AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()
render_ai_floating_button()

# Main Header
render_header(
    title="AI Data Analyst",
    subtitle="Ask questions about your data in natural language with autonomous analytical tool execution.",
    badge="Module • AI Assistant"
)

# Initialize Chat and Context History in Session State
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "agent_context" not in st.session_state:
    st.session_state["agent_context"] = {}

df = st.session_state.get("dataset")
is_loaded = st.session_state.get("dataset_loaded", False)
filename = st.session_state.get("dataset_name", "dataset")

if not is_loaded or df is None:
    # Empty State when no dataset is loaded
    st.markdown(
        """
        <div class="placeholder-container">
            <div class="placeholder-icon">💬</div>
            <div class="placeholder-title">No Dataset Loaded for Analysis</div>
            <div class="placeholder-desc">
                Upload a CSV or Excel dataset from the Dashboard to begin chatting with your AI Data Analyst. 
                The agent will dynamically understand your columns, compute statistics, and answer your questions.
            </div>
            <span class="phase-pill" style="background-color: #F2C6B4; color: #7D3B23;">
                Awaiting Dataset Upload
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    col_c1, col_c2, col_c3 = st.columns([2, 1.5, 2])
    with col_c2:
        if st.button("⬅️ Go to Dashboard to Upload", type="primary", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")

else:
    # Initialize Agent with current working dataset
    agent = ConversationalDataAnalystAgent(df, filename)
    info = compute_dataset_summary(df, filename)
    st.session_state["dataset_info"] = info

    # Dataset Status Banner
    st.markdown(
        f"""
        <div class="insight-card" style="margin-bottom: 16px; padding: 14px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="font-weight: 700; color: #30343B; font-size: 1.05rem;">Active Dataset: {filename}</span>
                    <span style="color: #68707D; font-size: 0.88rem; margin-left: 12px;">
                        {info['rows']:,} rows • {info['cols']} columns • {info['numeric_cols_count']} numeric features
                    </span>
                </div>
                <div>
                    <span class="phase-pill" style="background-color: #E2F3EC; color: #2F6B55;">Agent Ready</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_chat, col_suggestions = st.columns([1.7, 1])

    with col_chat:
        st.markdown("<h4 style='color: #30343B; font-size: 1.1rem; margin-bottom: 12px;'>Conversation History</h4>", unsafe_allow_html=True)

        # Clear Conversation Button
        c_head1, c_head2 = st.columns([4, 1.5])
        with c_head2:
            if st.button("Clear History", use_container_width=True):
                st.session_state["chat_history"] = []
                st.session_state["agent_context"] = {}
                st.rerun()

        # Render Conversation Messages
        if not st.session_state["chat_history"]:
            st.markdown(
                """
                <div style="background-color: #FFF8ED; border: 1px dashed #D6CBBA; border-radius: 12px; padding: 32px 20px; text-align: center; margin-bottom: 16px;">
                    <div style="font-size: 2.2rem; margin-bottom: 6px;">💬</div>
                    <div style="font-weight: 700; color: #30343B; font-size: 1.1rem; margin-bottom: 4px;">Start a Conversation</div>
                    <div style="color: #68707D; font-size: 0.9rem; max-width: 440px; margin: 0 auto;">
                        Ask any question below or click one of the suggested inquiries on the right.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for msg in st.session_state["chat_history"]:
                role = msg["role"]
                with st.chat_message(role, avatar="🧑" if role == "user" else "🤖"):
                    st.markdown(msg["content"])
                    if msg.get("table") is not None:
                        st.dataframe(msg["table"], use_container_width=True)
                    if msg.get("fig") is not None:
                        st.plotly_chart(msg["fig"], use_container_width=True)

        # Natural Language Chat Input
        user_input = st.chat_input(placeholder="Ask anything about your dataset (e.g. 'What is the average salary?')...")

        if user_input:
            # 1. Append and render user message
            st.session_state["chat_history"].append({"role": "user", "content": user_input})

            # 2. Process query through Autonomous Agent
            last_ctx = st.session_state.get("agent_context", {})
            agent_response = agent.process_query(user_input, last_ctx)

            # 3. Update conversation context
            st.session_state["agent_context"] = agent_response["context"]

            # 4. Append assistant response
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": agent_response["text"],
                "table": agent_response.get("table"),
                "fig": agent_response.get("fig")
            })
            st.rerun()

    with col_suggestions:
        st.markdown("<h4 style='color: #30343B; font-size: 1.1rem; margin-bottom: 12px;'>Suggested Questions</h4>", unsafe_allow_html=True)
        st.markdown(
            """
            <p style="font-size: 0.88rem; color: #68707D; margin-bottom: 12px;">
                Tailored dynamically to the active columns in your dataset:
            </p>
            """,
            unsafe_allow_html=True
        )

        # Dynamic sample questions based on actual dataset schema
        dynamic_suggestions = ["Give me a summary of this dataset."]
        
        if info["numeric_cols"]:
            first_num = info["numeric_cols"][0]
            dynamic_suggestions.append(f"What is the average {first_num}?")
            dynamic_suggestions.append(f"Show the distribution of {first_num}.")
            if len(info["numeric_cols"]) > 1:
                second_num = info["numeric_cols"][1]
                dynamic_suggestions.append(f"What is the correlation between {first_num} and {second_num}?")

        if info["categorical_cols"] and info["numeric_cols"]:
            first_cat = info["categorical_cols"][0]
            first_num = info["numeric_cols"][0]
            dynamic_suggestions.append(f"Which {first_cat} has the highest {first_num}?")
        elif info["categorical_cols"]:
            first_cat = info["categorical_cols"][0]
            dynamic_suggestions.append(f"What are the most frequent categories in {first_cat}?")

        dynamic_suggestions.append("Which columns have missing values?")

        for idx, q in enumerate(dynamic_suggestions[:5]):
            if st.button(q, key=f"btn_sugg_{idx}", use_container_width=True):
                # Trigger question automatically
                st.session_state["chat_history"].append({"role": "user", "content": q})
                last_ctx = st.session_state.get("agent_context", {})
                agent_response = agent.process_query(q, last_ctx)
                st.session_state["agent_context"] = agent_response["context"]
                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": agent_response["text"],
                    "table": agent_response.get("table"),
                    "fig": agent_response.get("fig")
                })
                st.rerun()

        st.markdown(
            """
            <div style="margin-top: 18px; background-color: #E8E1F5; border-radius: 8px; padding: 14px; font-size: 0.82rem; color: #554477; line-height: 1.5;">
                <strong>Autonomous Analyst Architecture:</strong><br>
                • <strong>Natural Language Understanding:</strong> Analyzes user intent and resolves conversational pronouns.<br>
                • <strong>Deterministic Execution:</strong> Computations run safely via Pandas on local working data.<br>
                • <strong>No Hallucinations:</strong> The agent never invents predictions or non-existent metrics.
            </div>
            """,
            unsafe_allow_html=True
        )
