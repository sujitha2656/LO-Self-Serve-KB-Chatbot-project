import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.utils import KB_DIR, MarkdownParser
from src.embeddings import EmbeddingEngine
from src.rag_engine import RAGEngine
from src.llm_helper import LLMHelper
from src.ticket_handler import TicketHandler


# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def temp_kb_file():
    """Creates a temporary Markdown file for testing chunking."""
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False, encoding="utf-8") as f:
        f.write("# Main Title\n\nIntro text.\n\n## Section One\nContent for section one.\n\n## Section Two\nContent for section two.")
        file_path = Path(f.name)
    yield file_path
    if file_path.exists():
        file_path.unlink()


@pytest.fixture
def mock_chroma_db():
    """Initializes a transient in-memory RAGEngine instance."""
    # We use a temporary directory for ChromaDB to prevent polluting production index files
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = RAGEngine(persist_dir=temp_dir)
        yield engine


@pytest.fixture
def mock_ticket_handler():
    """Initializes a TicketHandler pointed to temp CSV files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tickets_csv = temp_path / "tickets.csv"
        escalated_csv = temp_path / "escalated_tickets.csv"
        
        # Patch the configuration paths in ticket_handler module
        with patch("src.ticket_handler.TICKETS_CSV", tickets_csv), \
             patch("src.ticket_handler.ESCALATED_TICKETS_CSV", escalated_csv):
            handler = TicketHandler()
            yield handler


# ==========================================
# 1. KNOWLEDGE BASE INDEXING TESTS
# ==========================================

def test_markdown_parser_happy(temp_kb_file):
    """Happy Path: Parsing a valid Markdown file yields structured chunks with metadata."""
    chunks = MarkdownParser.chunk_file(temp_kb_file)
    
    assert len(chunks) == 3
    assert chunks[0]["metadata"]["headers"] == "H1: Main Title"
    assert chunks[1]["metadata"]["headers"] == "H1: Main Title > H2: Section One"
    assert "section one" in chunks[1]["text"]
    assert chunks[2]["metadata"]["headers"] == "H1: Main Title > H2: Section Two"


def test_markdown_parser_nonexistent():
    """Negative Path: Parsing a file that does not exist returns an empty list."""
    non_existent = Path("/path/to/nowhere/docs.md")
    chunks = MarkdownParser.chunk_file(non_existent)
    assert chunks == []


# ==========================================
# 2. VECTOR SEARCH TESTS
# ==========================================

def test_vector_search_happy(mock_chroma_db):
    """Happy Path: Indexing chunks and querying returns matching vectors and similarity scores."""
    embedder = EmbeddingEngine()
    
    # Chunk contents
    texts = [
        "To reset your corporate password, visit the reset web portal.",
        "FortiClient VPN requires Microsoft Authenticator MFA approvals.",
        "Outlook mail sync configurations can be automated via control panel."
    ]
    metadatas = [
        {"source": "password.md", "headers": "Reset"},
        {"source": "vpn.md", "headers": "VPN"},
        {"source": "outlook.md", "headers": "Outlook"}
    ]
    ids = ["c1", "c2", "c3"]
    embeddings = embedder.embed_documents(texts)
    
    mock_chroma_db.add_documents(ids, embeddings, texts, metadatas)
    
    # Query Search
    query = "How to configure corporate VPN client?"
    query_vector = embedder.embed_query(query)
    results = mock_chroma_db.query_similarity(query_vector, n_results=1)
    
    assert len(results) == 1
    assert results[0]["metadata"]["source"] == "vpn.md"
    assert results[0]["similarity"] > 0.0
    assert "FortiClient VPN" in results[0]["text"]


def test_vector_search_empty_query(mock_chroma_db):
    """Negative Path: Searching with empty parameters returns empty list safely."""
    results = mock_chroma_db.query_similarity([], n_results=2)
    assert results == []


# ==========================================
# 3. CITATION GENERATION TESTS
# ==========================================

@patch("google.generativeai.GenerativeModel")
def test_citation_generation_happy(mock_gen_model):
    """Happy Path: LLM generates grounded answers containing citations from the context."""
    # Setup mock response from Gemini GenerativeModel
    mock_response = MagicMock()
    mock_response.text = '{"answer": "To connect to FortiClient Corporate VPN, download it from the company portal. [Source: vpn_setup.md, Section: Installation Steps]", "confidence": 95, "citations": ["vpn_setup.md > Installation Steps"]}'
    
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gen_model.return_value = mock_model_instance
    
    # Invoke
    llm = LLMHelper(api_key="dummy_key")
    retrieved_context = [
        {
            "text": "Download FortiClient and setup connection gateway vpn.company.com",
            "metadata": {"source": "vpn_setup.md", "headers": "Installation Steps"}
        }
    ]
    
    response = llm.generate_answer("How to setup VPN", retrieved_context)
    
    assert response["confidence"] == 95
    assert len(response["citations"]) == 1
    assert "vpn_setup.md > Installation Steps" in response["citations"]
    assert "[Source: vpn_setup.md" in response["answer"]


@patch("google.generativeai.GenerativeModel")
def test_citation_generation_unanswerable(mock_gen_model):
    """Negative Path: If context is unrelated, LLM answers with standard fallback and empty citations."""
    mock_response = MagicMock()
    mock_response.text = '{"answer": "I could not find this in the knowledge base.", "confidence": 0, "citations": []}'
    
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gen_model.return_value = mock_model_instance
    
    llm = LLMHelper(api_key="dummy_key")
    retrieved_context = [
        {
            "text": "Corporate printer paper jams can be cleared in Drawer A.",
            "metadata": {"source": "printer.md", "headers": "Paper Jam"}
        }
    ]
    
    response = llm.generate_answer("How to reset active directory password?", retrieved_context)
    
    assert response["confidence"] == 0
    assert response["citations"] == []
    assert response["answer"] == "I could not find this in the knowledge base."


# ==========================================
# 4. CONFIDENCE SCORING TESTS
# ==========================================

def test_confidence_scoring_empty_context():
    """Negative Path: If retrieved context list is empty, confidence score is forced to 0."""
    llm = LLMHelper(api_key="dummy_key")
    response = llm.generate_answer("How do I setup FortiClient?", [])
    assert response["confidence"] == 0
    assert response["answer"] == "I could not find this in the knowledge base."


# ==========================================
# 5. TICKET ESCALATION TESTS
# ==========================================

@patch("src.llm_helper.LLMHelper.generate_ticket_fields")
def test_ticket_escalation_happy(mock_ticket_fields, mock_ticket_handler):
    """Happy Path: Tickets are generated with automated priorities and logged to CSV files."""
    # Mock LLM ticket analysis
    mock_ticket_fields.return_value = {
        "ticket_title": "FortiClient VPN timeout issue",
        "problem_summary": "VPN connection fails on gateway vpn.company.com",
        "priority": "High",
        "recommended_team": "Network Operations Team"
    }
    
    llm = LLMHelper(api_key="dummy_key")
    
    ticket = mock_ticket_handler.create_ticket(
        name="Jane Doe",
        email="jane.doe@company.com",
        description="Getting status code 98 when connecting.",
        user_question="VPN connection timeout",
        retrieved_context=[],
        llm_helper=llm
    )
    
    assert ticket["ticket_id"] == "TKT-1001"
    assert ticket["ticket_title"] == "FortiClient VPN timeout issue"
    assert ticket["priority"] == "High"
    assert ticket["recommended_team"] == "Network Operations Team"
    
    # Confirm it is written to local tickets database
    all_tickets = mock_ticket_handler.get_all_tickets()
    assert len(all_tickets) == 1
    assert all_tickets[0]["Ticket ID"] == "TKT-1001"
    assert all_tickets[0]["Priority"] == "High"


def test_ticket_escalation_invalid_inputs(mock_ticket_handler):
    """Negative Path: Creating ticket with missing fields fails gracefully."""
    llm = LLMHelper(api_key="dummy_key")
    
    # Try calling without LLM (missing key or library errors)
    # The handler falls back to default values rather than crashing
    ticket = mock_ticket_handler.create_ticket(
        name="Jane Doe",
        email="jane.doe@company.com",
        description="",
        user_question="Random issue",
        retrieved_context=[],
        llm_helper=None  # Triggers fallback
    )
    
    assert ticket["ticket_id"] == "TKT-1001"
    assert "Fallback" in ticket["problem_summary"]
    assert ticket["priority"] == "Medium"
