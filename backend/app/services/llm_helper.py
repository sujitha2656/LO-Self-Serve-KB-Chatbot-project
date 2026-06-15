import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL_NAME

class LLMHelper:
    """
    Integrates Gemini Generative AI SDK, running grounded questions, chat history summaries,
    and automatic structured service ticket generation.
    """
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        genai.configure(api_key=key)
        self.model_name = GEMINI_MODEL_NAME

    def generate_answer(self, user_question: str, retrieved_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Submits retrieved context and question to Gemini and returns structured response:
        {
         "answer": "",
         "confidence": 0,
         "citations": []
        }
        """
        if not retrieved_context:
            return {
                "answer": "I could not find this in the knowledge base.",
                "confidence": 0,
                "citations": []
            }

        context_blocks = []
        for idx, doc in enumerate(retrieved_context):
            meta = doc.get("metadata", {})
            source_file = meta.get("source", "Unknown Document")
            headers = meta.get("headers", "General")
            text = doc.get("text", "")
            context_blocks.append(
                f"Document [{idx}]:\n"
                f"- Article Name: {source_file}\n"
                f"- Section Heading: {headers}\n"
                f"- Content: {text}\n"
                f"---"
            )
        
        context_text = "\n".join(context_blocks)
        
        prompt = f"""
        You are an IT Service Desk Knowledge Assistant.

        Answer ONLY from the supplied context.

        Rules:
        1. Cite article name.
        2. Cite section heading.
        3. If answer not found say:
           "I could not find this in the knowledge base."

        4. Generate confidence score:
           0-100

        Context:
        {context_text}

        Question:
        {user_question}
        """
        
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "answer": {"type": "STRING"},
                "confidence": {"type": "INTEGER"},
                "citations": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                }
            },
            "required": ["answer", "confidence", "citations"]
        }
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": response_schema,
                    "temperature": 0.0
                },
                system_instruction="You are an IT Service Desk Knowledge Assistant. You answer questions using only the provided context and citations."
            )
            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            print("LLM Error:", repr(e))
            return {
                "answer": "I could not find this in the knowledge base.",
                "confidence": 0,
                "citations": [],
                "error": str(e)
            }

    def generate_ticket_fields(self, user_question: str, retrieved_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates structured service ticket information using Gemini when confidence is low:
        {
          "ticket_title": "",
          "problem_summary": "",
          "priority": "Low|Medium|High",
          "recommended_team": ""
        }
        """
        context_blocks = []
        for idx, doc in enumerate(retrieved_context):
            meta = doc.get("metadata", {})
            source_file = meta.get("source", "Unknown Document")
            headers = meta.get("headers", "General")
            text = doc.get("text", "")
            context_blocks.append(
                f"Document [{idx}]:\n"
                f"- Article Name: {source_file}\n"
                f"- Section Heading: {headers}\n"
                f"- Content: {text}\n"
                f"---"
            )
            
        context_text = "\n".join(context_blocks) if context_blocks else "No relevant articles retrieved."
        
        prompt = f"""
        Role: IT Service Desk Ticketing Assistant

        Given the User's Question and the Retrieved Context from the knowledge base, generate a structured support ticket.

        Rules for fields:
        1. ticket_title: A short, descriptive title summarizing the main request.
        2. problem_summary: A detailed summary explaining what the user was trying to do, what context was found, and what failed.
        3. priority: Decide priority based on:
           - "High": Critical path blocks (e.g. login lockouts, password reset failures, vpn gateway down).
           - "Medium": Service disruption but workaround exists (e.g. Outlook sync issues, printer offline).
           - "Low": Informational requests or minor troubleshooting (e.g. general questions).
        4. recommended_team: Suggest a resolving support team based on:
           - VPN / Network issues: "Network Operations Team"
           - Account / Password / Security issues: "IAM Security Operations"
           - Outlook / Office apps: "Collaboration Support Team"
           - Printer / Local hardware: "Local IT Hardware Support"
           - General / Other: "Service Desk General Tier"

        Question:
        {user_question}

        Retrieved Context:
        {context_text}
        """
        
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "ticket_title": {"type": "STRING"},
                "problem_summary": {"type": "STRING"},
                "priority": {
                    "type": "STRING",
                    "enum": ["Low", "Medium", "High"]
                },
                "recommended_team": {"type": "STRING"}
            },
            "required": ["ticket_title", "problem_summary", "priority", "recommended_team"]
        }
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": response_schema,
                    "temperature": 0.0
                },
                system_instruction="You are an IT Service Desk Ticketing Assistant. You output structured JSON support ticket details."
            )
            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            # Fallback values
            return {
                "ticket_title": f"Escalation request: {user_question[:30]}...",
                "problem_summary": f"User question: {user_question}. Fallback due to error: {str(e)}",
                "priority": "Medium",
                "recommended_team": "Service Desk General Tier"
            }

    def generate_summary_for_ticket(self, conversation_history: List[Dict[str, str]]) -> str:
        """Generates a brief summary of the client chat transcript."""
        if not conversation_history:
            return "No conversation history provided."
            
        formatted_history = []
        for msg in conversation_history:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            formatted_history.append(f"{role}: {content}")
            
        history_text = "\n".join(formatted_history)
        
        prompt = f"""
        Review the support transcript:
        ---
        {history_text}
        ---
        
        Write a concise, 1-sentence summary of the core issue that needs human engineer resolution.
        """
        
        try:
            model = genai.GenerativeModel(model_name=self.model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Summary unavailable. Error: {str(e)}"
