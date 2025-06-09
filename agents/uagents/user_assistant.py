from uagents import Agent, Context, Protocol, Model 
import requests
from datetime import datetime
from uuid import uuid4
from uagents_core.contrib.protocols.chat import (
    ChatMessage, 
    ChatAcknowledgement, 
    TextContent,
    chat_protocol_spec
)
from uagents.experimental.quota import QuotaProtocol, RateLimit
from uagents_core.models import ErrorMessage
import asyncio
from utils import ASI_ENDPOINT, ASI_HEADERS, AGENTVERSE_SEARCH_URL, AGENTVERSE_HEADERS

# Define message models
class Request(Model):
    text: str

class Response(Model):
    text: str
    agent: str
    status_code: int

class AgentInfo(Model):
    address: str
    name: str
    description: str
    
# Initialize uAgent with proper config
user_assistant = Agent(
    name="ParadoxUserAssistant",
    seed="paradox_user_assistant_seed",
    port=8000,
    mailbox=True
)  

proto = QuotaProtocol(
    storage_reference=user_assistant.storage,
    name="UserAssistantRateLimit",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=60, max_requests=30),
)

# Create chat protocol instance
chat_proto = Protocol(spec=chat_protocol_spec)

# Shared state for response coordination
response_event = asyncio.Event()
latest_response = None

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle replies from agents and coordinate agents"""
    global latest_response
    try:
        # Send immediate acknowledgement
        ack = ChatAcknowledgement(
            timestamp=datetime.now(),
            acknowledged_msg_id=msg.msg_id
        )
        await ctx.send(sender, ack)

        # Extract text content
        content = extract_content(msg)

        print(f"Received message from {sender}: {content}")

        # Store response
        latest_response = content
        response_event.set()

    except Exception as e:
        error_msg = ChatMessage(
            content=[TextContent(type="text", text=f"User Assistant error: {str(e)}")],
            msg_id=str(uuid4()),
            timestamp=datetime.now()
        )
        await ctx.send(sender, error_msg)

def extract_content(query):
    """Extract text content from ChatMessage"""
    try:
        text_content = None
        for content in query.content:
            if isinstance(content, TextContent):
                text_content = content
                break
            elif isinstance(content, dict) and "text" in content:
                text_content = TextContent(**content)
                break

        if not text_content:
            raise ValueError("Message contains no text content")

        response = text_content.text

        return response.strip()

    except Exception as e:
        return f"Error extracting content: {str(e)}"

@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")

async def _determine_service_type(query: str) -> str:
    """Use ASI-1 Mini for intent classification"""
    prompt = f"""
    Classify this travel query to the appropriate agent:
    Query: {query}

    Options: ParadoxFlightAgent, ParadoxHotelAgent, ParadoxFoodAgent, ParadoxAttractionAgent, ParadoxLocalTipsAgent

    Return only the agent name.
    """

    payload = {
        "model": "asi1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(ASI_ENDPOINT, headers=ASI_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error processing query: {query}"

async def search_agents(agent_name: str) -> list[AgentInfo]:
    """Search Agentverse for available agents"""
    try:

        body = {
            "filters": {
                "state": ["active"],
                "agent_type": ["mailbox"]
            },
            "sort": "relevancy",
            "direction": "asc",
            "search_text": agent_name,
            "offset": 0,
            "limit": 5,
        }

        
        response = requests.post(AGENTVERSE_SEARCH_URL, headers=AGENTVERSE_HEADERS, json=body)

        print(f"Agentverse search response: {response.status_code} - {agent_name}")  # Debug

        return [
            AgentInfo(
                address=agent["address"],
                name=agent["name"],
                description=agent["description"]
            ) for agent in response.json().get("agents", [])
        ]
    except Exception as e:
        return []

async def _forward_to_agent(ctx: Context, agent_address: str, query: str) -> str:
    """Send query to target agent"""
    try:
        await ctx.send(
            agent_address,
            ChatMessage(
                content=[TextContent(type="text", text=query)],
                msg_id=str(uuid4()),
                timestamp=datetime.now()
            )
        )

        return "Sent to agent successfully"

    except Exception as e:
        return f"Error communicating with agent: {str(e)}"

@user_assistant.on_rest_post("/send-query", Request, Response)
async def handle_user_query(ctx: Context, req: Request) -> Response:
    """Handle REST requests with rate limiting"""

    # Check rate limit
    if not proto.add_request(
        agent_address='rest_clients',
        function_name="handle_user_query",
        window_size_minutes=60,
        max_requests=30
    ):
        return Response(text="Rate limit exceeded. Try again in an hour.", status_code=429, agent='ParadoxUserAssistant')
    
    global latest_response

    # Reset event for new query
    response_event.clear()
    latest_response = ''
    
    try:
        user_query = req.text.strip()

        # 1. Determine required service type using ASI:One
        service_type = await _determine_service_type(user_query)

        # 2. Search Agentverse for relevant agents
        agents = await search_agents(service_type)

        if not agents:
            raise ValueError(f"No {service_type} agents available")
        
        # 3. Select first available agent
        target_agent = agents[0]

        # 4. Forward query to target agent
        result = await _forward_to_agent(ctx, target_agent.address, user_query)

        # 5. Wait for agent response with 100s timeout
        try:
            await asyncio.wait_for(response_event.wait(), timeout=100.0)
            return Response(text=latest_response, status_code=200, agent=target_agent.name)
        
        except asyncio.TimeoutError:
            return Response(text="Error: Agent response timeout", status_code=500, agent=target_agent.name)
        
        finally:
            # Reset event for next query
            response_event.clear()
            latest_response = ''

    except Exception as e:
        return Response(text=f"User Assistant error: {str(e)}", status_code=500, agent='ParadoxUserAssistant')

# Include the chat protocol
user_assistant.include(proto, publish_manifest=True)
user_assistant.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    user_assistant.run()