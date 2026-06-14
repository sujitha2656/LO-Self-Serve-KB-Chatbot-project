import os
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

def get_stats():
    try:
        return requests.get(f"{API_URL}/stats").json()
    except Exception:
        return {"indexed_chunks": 0, "source_sops": 0}

def ingest_documents():
    return requests.post(f"{API_URL}/ingest")

def clear_db():
    return requests.post(f"{API_URL}/clear_db")

def get_tickets():
    try:
        return requests.get(f"{API_URL}/tickets").json()
    except Exception:
        return []

def query_kb(prompt: str, api_key: str):
    return requests.post(f"{API_URL}/query", json={"prompt": prompt, "api_key": api_key})

def escalate_ticket(name: str, email: str, description: str, user_question: str, retrieved_context: list, api_key: str):
    return requests.post(f"{API_URL}/escalate", json={
        "name": name,
        "email": email,
        "description": description,
        "user_question": user_question,
        "retrieved_context": retrieved_context,
        "api_key": api_key
    })

def save_history(messages: list):
    try:
        requests.post(f"{API_URL}/history", json={"messages": messages})
    except Exception:
        pass

def get_history():
    try:
        data = requests.get(f"{API_URL}/history").json()
        return data if isinstance(data, list) else []
    except Exception:
        return []

def generate_random_tickets():
    try:
        return requests.post(f"{API_URL}/random_tickets").json()
    except Exception:
        return {}
