import json
import time
from typing import List, Dict, Any
from .config import MEMORY_FILE

class MemoryStore:
    """Local RAG & Memory system for Sonny"""
    def __init__(self, file_path=MEMORY_FILE):
        self.file_path = file_path
        self.data: Dict[str, Any] = {"facts": [], "preferences": {}, "conversation_history": []}
        self.load()

    def load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.save()
        else:
            self.save()

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Memory Save Error] {e}")

    def add_fact(self, fact: str, category: str = "general") -> str:
        entry = {
            "fact": fact,
            "category": category,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["facts"].append(entry)
        self.save()
        return f"Learned and saved fact: '{fact}'"

    def search_facts(self, query: str) -> List[Dict[str, Any]]:
        query_terms = query.lower().split()
        results = []
        for item in self.data["facts"]:
            fact_lower = item["fact"].lower()
            if any(term in fact_lower for term in query_terms):
                results.append(item)
        return results

    def get_all_facts(self) -> List[str]:
        return [item["fact"] for item in self.data.get("facts", [])]

    def add_history(self, role: str, content: str):
        self.data["conversation_history"].append({
            "role": role,
            "content": content,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        # Keep last 50 turns
        if len(self.data["conversation_history"]) > 50:
            self.data["conversation_history"] = self.data["conversation_history"][-50:]
        self.save()

    def clear(self):
        self.data = {"facts": [], "preferences": {}, "conversation_history": []}
        self.save()
