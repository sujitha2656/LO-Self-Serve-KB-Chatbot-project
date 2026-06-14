import streamlit as st
from utils import api_client

def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/nolan/128/bot.png", width=70)
        st.markdown("## SD01 Chatbot Panel")
        
        st.markdown("### API Credentials")
        api_key_input = st.text_input(
            "Gemini API Key",
            value=st.session_state.api_key,
            type="password",
            help="Input your Google Gemini API Key if it's not set in the .env file."
        )
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            st.rerun()

        if not st.session_state.api_key:
            st.warning("⚠️ Gemini API Key is missing. Configure it to enable chatbot replies.")

        st.markdown("---")
        st.markdown("### Document Ingestion")
        
        stats = api_client.get_stats()
        indexed_chunks = stats.get("indexed_chunks", 0)
        source_sops = stats.get("source_sops", 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Indexed Chunks", indexed_chunks)
        with col2:
            st.metric("Source SOPs", source_sops)

        if st.button("🔄 Ingest & Re-index", use_container_width=True):
            if source_sops == 0:
                st.error("No Markdown SOP files found.")
            else:
                with st.spinner("Parsing & Indexing SOPs..."):
                    res = api_client.ingest_documents()
                    if res.status_code == 200:
                        st.success("Successfully indexed chunks!")
                        st.rerun()
                    else:
                        st.error("Failed to ingest documents.")

        if st.button("🗑️ Clear Vector Database", use_container_width=True, type="secondary"):
            api_client.clear_db()
            st.success("Vector DB wiped clean!")
            st.rerun()

        st.markdown("---")
        st.markdown("### Escalation Dashboard")
        tickets = api_client.get_tickets()
        
        if not tickets:
            st.info("No tickets escalated yet.")
        else:
            st.success(f"🎫 {len(tickets)} Escalated Tickets")
            for t in tickets[-3:]:
                with st.expander(f"🔴 {t.get('Ticket ID', t.get('ticket_id'))} - {t.get('Ticket Title', t.get('ticket_title'))}"):
                    st.markdown(f"**Requester:** {t.get('Name', t.get('name'))} ({t.get('Email', t.get('email'))})")
                    st.markdown(f"**Priority:** `{t.get('Priority', t.get('priority'))}` | **Team:** `{t.get('Recommended Team', t.get('recommended_team'))}`")
                    st.markdown(f"**Problem Summary:** *{t.get('Problem Summary', t.get('problem_summary'))}*")
                    st.markdown(f"**Additional Details:** {t.get('Description', t.get('description'))}")
                    st.caption(f"Created: {t.get('Created At', t.get('created_at'))}")
