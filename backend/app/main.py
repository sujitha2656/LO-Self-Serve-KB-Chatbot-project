from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from app.api import endpoints
from app.services.llm_helper import LLMHelper
from app.core.config import GEMINI_API_KEY

app = FastAPI(title="SD01 Knowledge Base Chatbot API")

if GEMINI_API_KEY:
    try:
        endpoints.llm_helper = LLMHelper(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Warning: LLMHelper initialization failed: {e}")

app.include_router(endpoints.router)
