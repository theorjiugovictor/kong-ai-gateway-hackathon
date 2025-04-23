from typing import Dict

class SpecializedAgent:
    def __init__(self, intent: str, system_prompt: str):
        self.intent = intent
        self.system_prompt = system_prompt
        
    async def generate_response(self, message: str, emotion: str, history: List[dict]) -> str:
        # Here you would integrate with Opper AI
        # This is a placeholder for the actual implementation
        pass

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, SpecializedAgent] = {
            "order_status": SpecializedAgent(
                "order_status",
                "You are a helpful assistant specialized in checking order status..."
            ),
            "return_request": SpecializedAgent(
                "return_request",
                "You are a helpful assistant specialized in handling return requests..."
            ),
            # Add other agents here
        }
    
    def get_agent(self, intent: str) -> SpecializedAgent:
        return self.agents.get(intent)