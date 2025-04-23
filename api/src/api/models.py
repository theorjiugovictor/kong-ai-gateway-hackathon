from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    user_id: str
    content: str
    timestamp: datetime = datetime.now()

class ChatHistory(BaseModel):
    user_id: str
    messages: List[Message]
    emotion_history: List[str]
    
class CustomerIntent(BaseModel):
    intent_name: str
    examples: List[str]

class AgentResponse(BaseModel):
    message: str
    detected_emotion: str
    intent: str
    confidence: float