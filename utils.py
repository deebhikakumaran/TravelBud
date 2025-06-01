import os 
import json
import requests

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")
ASI_API_KEY = os.getenv("ASI_API_KEY")
ASI_ENDPOINT = "https://api.asi1.ai/v1/chat/completions"
AGENTVERSE_SEARCH_URL = "https://agentverse.ai/v1/search/agents"
AGENTVERSE_HEADERS = {"Authorization": f"Bearer {AGENTVERSE_API_KEY}"}
ASI_HEADERS = {
        "Authorization": f"Bearer {ASI_API_KEY}",
        "Content-Type": "application/json"
    }


def create_asi_client():
    """Create ASI-1 Mini client with structured output handling"""
    class ASIClient:
        async def query(self, prompt: str, response_format: str = "json"):
            payload = json.dumps({
                "model": "asi1-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "response_format": {"type": response_format},
                "max_tokens": 1000
            })

            response = requests.post(ASI_ENDPOINT, headers=ASI_HEADERS, data=payload)
            response.raise_for_status()
            return response.json()
    
    return ASIClient()