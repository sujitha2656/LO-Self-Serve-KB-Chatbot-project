import os
import re
from pathlib import Path
from typing import List, Dict, Any

# Project base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "kb"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index.bin"
FAISS_METADATA_PATH = DATA_DIR / "faiss_metadata.pkl"
OUTPUTS_DIR = BASE_DIR / "outputs"

# CSV and JSON files
TICKETS_CSV = DATA_DIR / "tickets.csv"
ESCALATED_TICKETS_CSV = OUTPUTS_DIR / "escalated_tickets.csv"
CHAT_HISTORY_JSON = OUTPUTS_DIR / "chat_history.json"

# Ensure directories exist
KB_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# AI Models & Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-latest")
SIMILARITY_THRESHOLD = 0.70

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class MarkdownParser:
    """
    Parses and chunks Markdown KB documents by headers (H1, H2, H3),
    retaining source titles and hierarchies in metadata.
    """
    @staticmethod
    def chunk_file(file_path: Path, max_chunk_size: int = 1500) -> List[Dict[str, Any]]:
        """Reads a markdown file, splits it into sections by headers, and returns sections."""
        if not file_path.exists():
            return []
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.split("\n")
        chunks = []
        current_headers = {1: "", 2: "", 3: ""}
        current_chunk_lines = []
        
        def flush_chunk(headers: Dict[int, str], lines_list: List[str]):
            if not lines_list:
                return
            text = "\n".join(lines_list).strip()
            if not text:
                return
                
            active_headers = []
            for level in sorted(headers.keys()):
                if headers[level]:
                    active_headers.append(f"H{level}: {headers[level]}")
            
            headers_path = " > ".join(active_headers)
            
            if len(text) > max_chunk_size:
                sub_chunks = MarkdownParser._split_text_by_length(text, max_chunk_size)
                for i, sub_text in enumerate(sub_chunks):
                    chunks.append({
                        "text": sub_text,
                        "metadata": {
                            "source": file_path.name,
                            "headers": headers_path,
                            "chunk_index": i
                        }
                    })
            else:
                chunks.append({
                    "text": text,
                    "metadata": {
                        "source": file_path.name,
                        "headers": headers_path,
                        "chunk_index": 0
                    }
                })
        
        header_pattern = re.compile(r"^(#{1,3})\s+(.*)$")
        
        for line in lines:
            match = header_pattern.match(line)
            if match:
                flush_chunk(current_headers, current_chunk_lines)
                current_chunk_lines = []
                
                level = len(match.group(1))
                title = match.group(2).strip()
                
                current_headers[level] = title
                for l in range(level + 1, 4):
                    current_headers[l] = ""
                    
            current_chunk_lines.append(line)
            
        flush_chunk(current_headers, current_chunk_lines)
        return chunks

    @staticmethod
    def _split_text_by_length(text: str, max_size: int) -> List[str]:
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            if len(para) > max_size:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > max_size:
                        for i in range(0, len(sentence), max_size):
                            chunks.append(sentence[i:i+max_size])
                    else:
                        if current_length + len(sentence) > max_size:
                            chunks.append("\n\n".join(current_chunk))
                            current_chunk = [sentence]
                            current_length = len(sentence)
                        else:
                            current_chunk.append(sentence)
                            current_length += len(sentence) + 2
            else:
                if current_length + len(para) > max_size:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [para]
                    current_length = len(para)
                else:
                    current_chunk.append(para)
                    current_length += len(para) + 2
                    
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
        return chunks
