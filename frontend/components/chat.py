import streamlit as st
from utils import api_client

def render_chat():
    for idx, msg in enumerate(st.session_state.messages):
        role = msg["role"]
        with st.chat_message(role):
            if role == "assistant" and "confidence" in msg:
                st.markdown("### 📄 Answer")
                if msg["confidence"] == "High":
                    st.success(msg["content"])
                else:
                    st.error(msg["content"])
                    
                st.markdown("---")
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("**Confidence**")
                    st.markdown(f"## {msg['score']:.0f}%")
                with cols[1]:
                    st.markdown("**Article**")
                    source = msg["chunks"][0]["metadata"].get("source", "N/A") if msg.get("chunks") else "N/A"
                    st.info(f"`{source}`")
                
                if "citations" in msg and msg["citations"]:
                    with st.expander("📚 Citations"):
                        for cit in msg["citations"]:
                            st.markdown(f"- `{cit}`")
                
                if "chunks" in msg and msg["chunks"]:
                    with st.expander("🔍 View Grounding References"):
                        for c_idx, chunk in enumerate(msg["chunks"]):
                            st.markdown(f"**Ref #{c_idx+1}** (Match Similarity: {chunk['similarity']:.2f})")
                            st.markdown(f"- *Source:* `{chunk['metadata'].get('source')}`")
                            st.markdown(f"- *Heading:* `{chunk['metadata'].get('headers')}`")
                            st.code(chunk["text"], language="markdown")
                            
                if msg["score"] < 70 and not st.session_state.show_escalation:
                    st.markdown("<div style='background:#7F1D1D; color:#F87171; padding:0.5rem; border-radius:5px; margin-bottom:1rem;'>Low confidence. Escalation recommended.</div>", unsafe_allow_html=True)
                    if st.button("🎫 Create Ticket", key=f"escalate_btn_{idx}"):
                        st.session_state.show_escalation = True
                        st.rerun()
            else:
                st.markdown(f"**User Request:**\n\n{msg['content']}")

def render_escalation_form():
    if st.session_state.show_escalation:
        st.markdown("### 🎫 File Support Ticket")
        st.markdown("Our automated assistant was unable to resolve this issue confidently. Fill out this form to escalate this chat to the L1 Support team.")
        
        with st.form("escalation_form"):
            user_name = st.text_input("Full Name", placeholder="John Doe")
            user_email = st.text_input("Email Address", placeholder="john.doe@company.com")
            issue_desc = st.text_area("Additional Context (Optional)", placeholder="Please elaborate on your problem...")
            
            import re
            submitted = st.form_submit_button("Submit Escalation Ticket")
            if submitted:
                if not user_name or not user_email:
                    st.error("Name and Email are required to submit an escalation.")
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
                    st.error("Please enter a valid email address.")
                elif not st.session_state.api_key:
                    st.error("Unable to generate summary. Gemini API Key is missing.")
                else:
                    with st.spinner("Submitting ticket..."):
                        original_question = ""
                        context_chunks = []
                        for m in reversed(st.session_state.messages):
                            if m["role"] == "user" and not original_question:
                                original_question = m["content"]
                            if m["role"] == "assistant" and "chunks" in m and not context_chunks:
                                context_chunks = m["chunks"]
                        
                        res = api_client.escalate_ticket(
                            name=user_name,
                            email=user_email,
                            description=issue_desc,
                            user_question=original_question,
                            retrieved_context=context_chunks,
                            api_key=st.session_state.api_key
                        )
                        if res.status_code == 200:
                            ticket = res.json()
                            st.success(f"🎉 Support ticket **{ticket['ticket_id']}** created! Details logged to CSV files.")
                            st.session_state.show_escalation = False
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"📝 **System Notification:** Filed support ticket [{ticket['ticket_id']}]. Title: *{ticket['ticket_title']}*. Priority: `{ticket['priority']}`. Team: `{ticket['recommended_team']}`."
                            })
                            
                            api_client.save_history(st.session_state.messages)
                            st.rerun()
                        else:
                            st.error(f"Failed to submit ticket: {res.text}")

def handle_chat_input():
    if prompt := st.chat_input("Ask an IT question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)
        
        api_client.save_history(st.session_state.messages)
        
        with st.chat_message("assistant"):
            if not st.session_state.api_key:
                ans = "I'm sorry, I cannot answer questions. The Gemini API key has not been configured in the Sidebar/Env settings."
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                api_client.save_history(st.session_state.messages)
            else:
                with st.spinner("Analyzing knowledge base..."):
                    res = api_client.query_kb(prompt, st.session_state.api_key)
                    if res.status_code == 200:
                        data = res.json()
                        answer = data["answer"]
                        llm_confidence = data["confidence"]
                        best_similarity = data["best_similarity"]
                        citations = data["citations"]
                        results = data["chunks"]
                        
                        if not results or best_similarity < 0.70:
                            st.markdown("### 📄 Answer")
                            st.error(answer)
                            st.markdown("---")
                            cols = st.columns(2)
                            with cols[0]:
                                st.markdown("**Confidence**")
                                st.markdown(f"## {best_similarity * 100:.0f}%")
                            with cols[1]:
                                st.markdown("**Article**")
                                source = results[0]["metadata"].get("source", "N/A") if results else "N/A"
                                st.info(f"`{source}`")
                                
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "confidence": "Low",
                                "score": best_similarity * 100,
                                "chunks": results
                            })
                            api_client.save_history(st.session_state.messages)
                            st.rerun()
                        else:
                            if llm_confidence >= 70:
                                st.markdown("### 📄 Answer")
                                st.success(answer)
                                st.markdown("---")
                                cols = st.columns(2)
                                with cols[0]:
                                    st.markdown("**Confidence**")
                                    st.markdown(f"## {llm_confidence:.0f}%")
                                with cols[1]:
                                    st.markdown("**Article**")
                                    source = results[0]["metadata"].get("source", "N/A") if results else "N/A"
                                    st.info(f"`{source}`")
                                    
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": answer,
                                    "confidence": "High",
                                    "score": llm_confidence,
                                    "chunks": results,
                                    "citations": citations
                                })
                                api_client.save_history(st.session_state.messages)
                            else:
                                fallback_msg = f"I found some relevant document sections, but I cannot confidently resolve your request (Confidence: {llm_confidence:.0f}%): *{answer}*\n\nWould you like to file a support ticket?"
                                st.markdown("### 📄 Answer")
                                st.error(fallback_msg)
                                st.markdown("---")
                                cols = st.columns(2)
                                with cols[0]:
                                    st.markdown("**Confidence**")
                                    st.markdown(f"## {llm_confidence:.0f}%")
                                with cols[1]:
                                    st.markdown("**Article**")
                                    source = results[0]["metadata"].get("source", "N/A") if results else "N/A"
                                    st.info(f"`{source}`")
                                    
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": fallback_msg,
                                    "confidence": "Low",
                                    "score": llm_confidence,
                                    "chunks": results,
                                    "citations": citations
                                })
                                api_client.save_history(st.session_state.messages)
                                st.rerun()
                    else:
                        st.error(f"Error querying API: {res.text}")
