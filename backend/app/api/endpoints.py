from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.api.schemas import QueryRequest, QueryResponse, EscalateRequest, HistoryRequest
from app.core.config import KB_DIR, MarkdownParser, SIMILARITY_THRESHOLD
from app.services.embeddings import EmbeddingEngine
from app.services.rag_engine import RAGEngine
from app.services.llm_helper import LLMHelper
from app.services.ticket_handler import TicketHandler

router = APIRouter()

embedder = EmbeddingEngine()
rag_engine = RAGEngine()
ticket_handler = TicketHandler()

# Global LLM helper placeholder; set by main.py
llm_helper = None

@router.post("/query", response_model=QueryResponse)
def query_kb(req: QueryRequest):
    try:
        query_vector = embedder.embed_query(req.prompt)
        results = rag_engine.query_similarity(query_vector, n_results=10)
        
        best_similarity = results[0]["similarity"] if results else 0.0
        
        if not results or best_similarity < SIMILARITY_THRESHOLD:
            return QueryResponse(
                answer="I could not find this in the knowledge base.",
                confidence=0.0,
                best_similarity=best_similarity,
                citations=[],
                chunks=results
            )
        
        current_llm_helper = llm_helper
        if req.api_key:
            try:
                current_llm_helper = LLMHelper(api_key=req.api_key)
            except Exception:
                pass

        if not current_llm_helper:
            raise HTTPException(status_code=500, detail="LLM not configured.")
            
        llm_response = current_llm_helper.generate_answer(req.prompt, results)
        
        answer = llm_response.get("answer", "")
        llm_confidence = llm_response.get("confidence", 0)
        citations = llm_response.get("citations", [])
        
        return QueryResponse(
            answer=answer,
            confidence=llm_confidence,
            best_similarity=best_similarity,
            citations=citations,
            chunks=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.post("/escalate")
def escalate_ticket(req: EscalateRequest):
    try:
        current_llm_helper = llm_helper
        if req.api_key:
            try:
                current_llm_helper = LLMHelper(api_key=req.api_key)
            except Exception:
                pass

        if not current_llm_helper:
            raise HTTPException(status_code=500, detail="LLM not configured.")
            
        ticket = ticket_handler.create_ticket(
            name=req.name,
            email=req.email,
            description=req.description,
            user_question=req.user_question,
            retrieved_context=req.retrieved_context,
            llm_helper=current_llm_helper
        )
        return ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ticket escalation failed: {str(e)}")

@router.post("/history")
def save_history(req: HistoryRequest):
    ticket_handler.save_chat_history(req.messages)
    return {"status": "success"}

@router.get("/history")
def get_history():
    return ticket_handler.get_chat_history()

@router.post("/ingest")
def ingest_documents():
    try:
        rag_engine.reset_collection()
        
        total_chunks = 0
        sops = 0
        files = list(KB_DIR.glob("*.md")) if KB_DIR.exists() else []
        
        for f in files:
            chunks = MarkdownParser.chunk_file(f)
            if chunks:
                sops += 1
                texts = [c["text"] for c in chunks]
                metadatas = [c["metadata"] for c in chunks]
                
                embeddings = embedder.embed_documents(texts)
                ids = [f"{f.stem}_chunk_{i}" for i in range(len(chunks))]
                
                rag_engine.add_documents(ids, embeddings, texts, metadatas)
                total_chunks += len(chunks)
                
        return {"status": "success", "chunks_indexed": total_chunks, "source_sops": sops}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@router.post("/clear_db")
def clear_db():
    rag_engine.reset_collection()
    return {"status": "success"}

@router.get("/stats")
def get_stats():
    files = list(KB_DIR.glob("*.md")) if KB_DIR.exists() else []
    return {
        "indexed_chunks": rag_engine.get_document_count(),
        "source_sops": len(files)
    }

@router.get("/tickets")
def get_tickets():
    return ticket_handler.get_all_tickets()

@router.post("/random_tickets")
def generate_random_tickets():
    try:
        tickets = ticket_handler.generate_random_tickets(n=5)
        return {"status": "success", "generated": tickets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Random ticket generation failed: {str(e)}")
