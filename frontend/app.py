import streamlit as st
import os
from dotenv import load_dotenv
from components.sidebar import render_sidebar
from components.chat import render_chat, render_escalation_form, handle_chat_input
from components.analytics import render_analytics

# Load environment variables
load_dotenv()

# Page setup
st.set_page_config(
    page_title="SD01 Helpdesk AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom premium CSS styling for UI
st.markdown("""
<style>
    .reportview-container {
        background: #0F172A;
    }
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .confidence-badge {
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        margin-left: 0.5rem;
    }
    .confidence-high {
        background-color: #065F46;
        color: #34D399;
        border: 1px solid #059669;
    }
    .confidence-low {
        background-color: #7F1D1D;
        color: #F87171;
        border: 1px solid #B91C1C;
    }
</style>
""", unsafe_allow_html=True)

# Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_escalation" not in st.session_state:
    st.session_state.show_escalation = False
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

# Render components
render_sidebar()

# Main Content Panel
st.markdown("<h1 class='main-header'>SD01 Helpdesk AI Assistant</h1>", unsafe_allow_html=True)
with st.expander("ℹ️ Welcome to SD01 Helpdesk! Click here for instructions.", expanded=False):
    st.markdown("""
    **How to use this AI Assistant:**
    1. **Configure API Key**: Expand the sidebar and enter your Google Gemini API Key. This enables the LLM logic.
    2. **Ingest Knowledge**: If you have added new `.md` SOPs in the `backend/data/kb` folder, click the **🔄 Ingest & Re-index** button in the sidebar to vectorize the documents.
    3. **Ask Questions**: Type your IT issue in the chat box below (e.g., "How do I reset my VPN password?").
    
    **Features:**
    - 🔍 **RAG Grounding**: The bot searches indexed SOPs to provide accurate answers.
    - 📊 **Confidence Scoring**: Each answer displays a confidence score. If the score is high (≥70%), the answer is provided directly.
    - 🎫 **Smart Escalation**: If the bot is not confident (<70%), it will recommend escalating the issue and automatically extract ticket metadata (Title, Summary, Priority, Team) for you!
    """)

tab_chat, tab_analytics = st.tabs(["💬 Chat", "📊 Analytics"])

with tab_chat:
    render_chat()
    render_escalation_form()
    handle_chat_input()

with tab_analytics:
    render_analytics()
