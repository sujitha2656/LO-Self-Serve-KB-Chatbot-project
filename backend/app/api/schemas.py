from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    prompt: str
    api_key: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    best_similarity: float
    citations: List[str]
    chunks: List[Dict[str, Any]]

class EscalateRequest(BaseModel):
    name: str
    email: str
    description: Optional[str] = ""
    user_question: str
    retrieved_context: List[Dict[str, Any]]
    api_key: Optional[str] = None

class HistoryRequest(BaseModel):
    messages: List[Dict[str, Any]]
