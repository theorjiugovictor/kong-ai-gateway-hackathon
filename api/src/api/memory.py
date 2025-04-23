from typing import Dict, List
import json

class MemoryManager:
    def __init__(self):
        self.memory_store = {}  # In production, use a proper database
        
    async def save_chat_history(
        self,
        user_id: str,
        message: Message,
        response: str,
        emotion: str
    ):
        if user_id not in self.memory_store:
            self.memory_store[user_id] = []
            
        self.memory_store[user_id].append({
            "timestamp": message.timestamp,
            "message": message.content,
            "response": response,
            "emotion": emotion
        })
        
    async def get_chat_history(self, user_id: str) -> List[dict]:
        return self.memory_store.get(user_id, [])