import os
import time
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from uagents_adapter import LangchainRegisterTool, cleanup_uagent
from main import attraction_agent
import requests
from utils import extract_langgraph_content, ASI_ENDPOINT, ASI_HEADERS

load_dotenv()

# Get API token for Agentverse
API_TOKEN = os.environ["AGENTVERSE_API_KEY"]

if not API_TOKEN:
    raise ValueError("Please set AGENTVERSE_API_KEY environment variable")

# Wrap LangGraph agent into a function for UAgent
def langgraph_agent_func(query):
    try:
        # Extract natural language query
        if isinstance(query, dict):
            user_input = query.get("query") or str(query)
        else:
            user_input = str(query)

        # Process with ASI-1 Mini for structured input
        structured_input = _get_structured_input(user_input)

        print(f"Structured input for Attraction Wrapper: {structured_input}")

        # Execute agent workflow
        result = attraction_agent.invoke({"messages": [{"role": "user", "content": structured_input}]})

        print(f"Result from Attraction Wrapper: {result}")

        # Extract content from LangGraph result
        content = extract_langgraph_content(result)

        print(f"Extracted content from Attraction wrapper: {content}")

        return content

    except Exception as e:
        return f"Error: {str(e)}"

def _get_structured_input(query: str) -> str:
    """Use ASI-1 Mini to convert natural language to structured query"""
    
    prompt = f"""
    Convert this attraction query to structured parameters for ParadoxAttractionAgent:
    Query: {query}
    
    Expected format for ParadoxAttractionAgent:
    "destinations"
    """
    
    payload = {
        "model": "asi1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(ASI_ENDPOINT, headers=ASI_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error processing query: {query}"
    
# Register the LangGraph agent via uAgent
tool = LangchainRegisterTool()
agent_info = tool.invoke(
    {
        "agent_obj": langgraph_agent_func,
        "name": "ParadoxAttractionAgent",
        "port": 8004,
        "description": "Recommends popular sights, landmarks, and activities, guiding users to must-visit attractions and experiences.",
        "api_token": API_TOKEN,
        "mailbox": True
    }
)

print(f"✅ Registered LangGraph agent: {agent_info}")

# Keep the agent alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Shutting down LangGraph agent...")
    cleanup_uagent("ParadoxAttractionAgent")
    print("✅ Agent stopped.")