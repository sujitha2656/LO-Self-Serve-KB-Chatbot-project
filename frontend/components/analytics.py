import streamlit as st
import pandas as pd
from utils import api_client

def render_analytics():
    st.markdown("## 📊 SD01 Chatbot Analytics Dashboard")
    st.markdown("Monitor the performance of the AI assistant and track escalated support tickets.")
    
    col_gen1, col_gen2 = st.columns([3, 1])
    with col_gen2:
        if st.button("🎲 Generate 5 Random Tickets", use_container_width=True):
            with st.spinner("Generating mock tickets..."):
                res = api_client.generate_random_tickets()
                if res.get("status") == "success":
                    st.success("Successfully generated mock tickets!")
                    st.rerun()
                else:
                    st.error("Failed to generate mock tickets.")
    
    # Fetch data
    tickets = api_client.get_tickets()
    history = api_client.get_history()
    
    # Calculate metrics
    total_tickets = len(tickets)
    
    total_queries = 0
    bot_answers = 0
    total_confidence = 0
    high_confidence_answers = 0
    
    for msg in history:
        if msg.get("role") == "user":
            total_queries += 1
        elif msg.get("role") == "assistant" and "score" in msg:
            bot_answers += 1
            score = msg.get("score", 0)
            total_confidence += score
            if score >= 70:
                high_confidence_answers += 1
                
    avg_confidence = (total_confidence / bot_answers) if bot_answers > 0 else 0
    resolution_rate = (high_confidence_answers / bot_answers * 100) if bot_answers > 0 else 0
    
    # Render Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total User Queries", total_queries, help="Number of questions asked in the current session.")
    with col2:
        st.metric("Avg Bot Confidence", f"{avg_confidence:.1f}%", help="Average confidence score across all bot answers.")
    with col3:
        st.metric("Auto-Resolution Rate", f"{resolution_rate:.1f}%", help="Percentage of queries answered with High Confidence (≥70%).")
    with col4:
        st.metric("Total Tickets Created", total_tickets, help="Total number of tickets escalated to IT Helpdesk globally.")
        
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 🎫 Ticket Priority Distribution")
        if tickets:
            df_tickets = pd.DataFrame(tickets)
            if 'Priority' in df_tickets.columns:
                priority_counts = df_tickets['Priority'].value_counts().reset_index()
                priority_counts.columns = ['Priority', 'Count']
                st.bar_chart(priority_counts.set_index('Priority'))
            elif 'priority' in df_tickets.columns:
                priority_counts = df_tickets['priority'].value_counts().reset_index()
                priority_counts.columns = ['Priority', 'Count']
                st.bar_chart(priority_counts.set_index('Priority'))
            else:
                st.info("No priority data available.")
        else:
            st.info("No tickets created yet.")
            
    with col_b:
        st.markdown("### 🤖 Bot Answer Breakdown")
        if bot_answers > 0:
            df_answers = pd.DataFrame({
                "Confidence Level": ["High (≥70%)", "Low (<70%)"],
                "Count": [high_confidence_answers, bot_answers - high_confidence_answers]
            })
            st.bar_chart(df_answers.set_index("Confidence Level"))
        else:
            st.info("No bot answers recorded in the current session.")
    
    st.markdown("---")
    st.markdown("### 📝 Recent Tickets")
    if tickets:
        st.dataframe(pd.DataFrame(tickets).tail(10))
    else:
        st.info("No tickets to display.")
