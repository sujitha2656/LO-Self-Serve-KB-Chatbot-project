from sentence_transformers import SentenceTransformer
from typing import List
from app.core.config import EMBEDDING_MODEL_NAME

class EmbeddingEngine:
    """
    SentenceTransformer wrapper to generate local vector embeddings for KB chunks and queries.
    """
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Encodes a list of documents in batches."""
        if not texts:
            return []
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
        
    def embed_query(self, text: str) -> List[float]:
        """Encodes a single query string."""
        return self.model.encode(text).tolist()
