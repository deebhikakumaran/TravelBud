from uagents import Agent, Context, Protocol
from uagents_adapter import LangchainRegisterTool
from main import local_tips_agent as langgraph_local_tips_agent
import time
import requests
from uagents_adapter import cleanup_uagent
from datetime import datetime
from uuid import uuid4
from uagents_core.contrib.protocols.chat import (
    ChatMessage, 
    ChatAcknowledgement, 
    TextContent,
    chat_protocol_spec
)
import asyncio
from utils import AGENTVERSE_API_KEY, create_asi_client, ASI_ENDPOINT, ASI_HEADERS

# Initialize ASI client
asi = create_asi_client()

# Initialize uAgent with proper config
local_tips_agent = Agent(
    name="ParadoxLocalTipsAgent",
    seed="paradox_local_tips_agent_seed",
    port=8005,
    endpoint=["http://localhost:8005/submit"]
)

# Create chat protocol instance
chat_proto = Protocol(spec=chat_protocol_spec)
    
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    try:
        # Send immediate acknowledgement
        ack = ChatAcknowledgement(
            timestamp=datetime.now(),
            acknowledged_msg_id=msg.msg_id
        )
        await ctx.send(sender, ack)

        # Extract text content
        text_content = next(c for c in msg.content if isinstance(c, TextContent))

        # Process with async ASI LLM
        structured_input = await _get_structured_input_async(text_content.text)

        # Execute LangGraph agent in thread pool
        result = await asyncio.wait_for(
            asyncio.to_thread(
                langgraph_local_tips_agent.invoke,
                {"messages": [{"role": "user", "content": structured_input}]}
            ),
            timeout=30.0
        )

        # Extract content from result
        content = extract_langgraph_content(result)

        # Send response with extracted content
        response = ChatMessage(
            content=[TextContent(text=content)], 
            msg_id=str(uuid4()),
            timestamp=datetime.now()
        )
        await ctx.send(sender, response)

    except Exception as e:
        error_msg = ChatMessage(
            content=[TextContent(text=f"Local tips search error: {str(e)}")],
            msg_id=str(uuid4()),
            timestamp=datetime.now()
        )
        await ctx.send(sender, error_msg)

# Add async version for chat protocol
async def _get_structured_input_async(query: str) -> str:
    """Use ASI-1 Mini to convert natural language to structured query"""

    prompt = f"""
    Convert this local tips query to structured parameters for ParadoxLocalTipsAgent:
    Query: {query}
    
    Expected format for ParadoxLocalTipsAgent:
    "destinations, departure_date, return_date"
    """
    
    response = await asi.query(prompt, response_format="json")
    return response['choices'][0]['message']['content']

@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")

# Enhanced agent wrapper with ASI integration
def local_tips_agent_wrapper(query) -> str:  
    try:
        # Extract natural language query
        if isinstance(query, dict):
            user_input = query.get("query") or str(query)
        else:
            user_input = str(query)

        # Process with ASI-1 Mini for structured input
        structured_input = _get_structured_input(user_input)

        print(f"Structured input for LocalTips Wrapper: {structured_input}")

        # Execute agent workflow
        result = langgraph_local_tips_agent.invoke({"messages": [{"role": "user", "content": structured_input}]})
        
        print(f"Result from LocalTips Wrapper: {result}")

        # Extract content from LangGraph result
        content = extract_langgraph_content(result)

        print(f"Extracted content from LocalTips wrapper: {content}")

        return content

    except Exception as e:
        return f"Error: {str(e)}"
    
def extract_langgraph_content(result):
    """Extract content from LangGraph LocalTips agent result"""
    try:
        # If result has messages key 
        if isinstance(result, dict) and 'messages' in result:
            messages = result['messages']
            if messages and hasattr(messages[-1], 'content'):
                return messages[-1].content
            elif messages:
                return str(messages[-1])
        
        # If result is a single message object
        elif hasattr(result, 'content'):
            return result.content
        
        # If result is a list of messages
        elif isinstance(result, list) and result:
            last_msg = result[-1]
            if hasattr(last_msg, 'content'):
                return last_msg.content
            else:
                return str(last_msg)
        
        # Fallback
        else:
            return str(result)
            
    except Exception as e:
        return f"Error extracting content: {str(e)}"
    
def _get_structured_input(query: str) -> str:
    """Use ASI-1 Mini to convert natural language to structured query"""
    
    prompt = f"""
    Convert this local tips query to structured parameters for ParadoxLocalTipsAgent:
    Query: {query}
    
    Expected format for ParadoxLocalTipsAgent:
    "destinations, departure_date, return_date"
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

# Include the chat protocol
local_tips_agent.include(chat_proto, publish_manifest=True)

# Register with Agentverse
tool = LangchainRegisterTool()
agent_info = tool.invoke({
    "agent_obj": local_tips_agent_wrapper,
    "name": "ParadoxLocalTipsAgent",
    "port": 8005,  # Must match agent's port
    "description": "Local tips search agent",
    "api_token": AGENTVERSE_API_KEY,
    "mailbox": True
})

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cleanup_uagent("ParadoxLocalTipsAgent")
    print("Agent stopped.")
