import os
import faiss
import numpy as np
import pickle
from typing import Dict, List, Any
from app.core.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH

class RAGEngine:
    """
    RAG Search Engine using FAISS for vector search and pickle for metadata storage.
    """
    def __init__(self):
        self.dimension = 384  # all-MiniLM-L6-v2 output dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        self.documents = []
        self.metadatas = []
        self.ids = []
        self._load()

    def _load(self):
        """Loads FAISS index and metadata from disk if they exist."""
        if FAISS_INDEX_PATH.exists() and FAISS_METADATA_PATH.exists():
            try:
                self.index = faiss.read_index(str(FAISS_INDEX_PATH))
                with open(FAISS_METADATA_PATH, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])
                    self.ids = data.get("ids", [])
            except Exception:
                pass

    def _save(self):
        """Saves FAISS index and metadata to disk."""
        faiss.write_index(self.index, str(FAISS_INDEX_PATH))
        with open(FAISS_METADATA_PATH, 'wb') as f:
            pickle.dump({
                "documents": self.documents,
                "metadatas": self.metadatas,
                "ids": self.ids
            }, f)

    def add_documents(self, ids: List[str], embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]):
        """Adds text chunks with vectors and metadata to FAISS."""
        if not ids:
            return
            
        embeddings_np = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_np)
        
        self.index.add(embeddings_np)
        self.ids.extend(ids)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        
        self._save()

    def query_similarity(self, query_vector: List[float], n_results: int = 3) -> List[Dict[str, Any]]:
        """Queries database and extracts matches with similarity scores."""
        if self.index.ntotal == 0:
            return []
            
        q_np = np.array([query_vector]).astype('float32')
        faiss.normalize_L2(q_np)
        
        distances, indices = self.index.search(q_np, n_results)
        
        formatted_results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
                
            formatted_results.append({
                "id": self.ids[idx],
                "text": self.documents[idx],
                "distance": float(dist),  # For IndexFlatIP, distance is dot product (cosine similarity since L2 normalized)
                "similarity": float(dist),
                "metadata": self.metadatas[idx]
            })
            
        return formatted_results

    def get_document_count(self) -> int:
        """Returns number of elements indexed."""
        return self.index.ntotal

    def reset_collection(self):
        """Cleans collection."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.documents = []
        self.metadatas = []
        self.ids = []
        if FAISS_INDEX_PATH.exists():
            FAISS_INDEX_PATH.unlink()
        if FAISS_METADATA_PATH.exists():
            FAISS_METADATA_PATH.unlink()
