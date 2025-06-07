import os
import time
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from uagents_adapter import LangchainRegisterTool, cleanup_uagent
from main import hotel_agent
from utils import extract_langgraph_content, ASI_ENDPOINT, ASI_HEADERS
import requests

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

        print(f"Structured input for Hotel Wrapper: {structured_input}")

        # Execute agent workflow
        result = hotel_agent.invoke({"messages": [{"role": "user", "content": structured_input}]})

        print(f"Result from Hotel Wrapper: {result}")

        # Extract content from LangGraph result
        content = extract_langgraph_content(result)

        print(f"Extracted content from Hotel wrapper: {content}")

        return content

    except Exception as e:
        return f"Error: {str(e)}"

# Add this synchronous version
def _get_structured_input(query: str) -> str:
    """Use ASI-1 Mini to convert natural language to structured query"""
    
    prompt = f"""
    Convert this hotel query to structured parameters for ParadoxHotelAgent:
    Query: {query}
    
    Expected format for ParadoxHotelAgent:
    "destinations, budget"
    """
    
    payload = {
        "model": "asi1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(ASI_ENDPOINT, headers=ASI_HEADERS, json=payload)
        response.raise_for_status()
        print("ASI response:", response.json()['choices'][0]['message']['content'])
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error processing query: {query}"
 
# Register the LangGraph agent via uAgent
tool = LangchainRegisterTool()
agent_info = tool.invoke(
    {
        "agent_obj": langgraph_agent_func,
        "name": "ParadoxHotelAgent",
        "port": 8002,
        "description": "Assists users in finding and booking hotels, offering recommendations based on location, budget, and amenities.",
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
    cleanup_uagent("ParadoxHotelAgent")
    print("✅ Agent stopped.")