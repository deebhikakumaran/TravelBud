import os
import json
import asyncio
from dotenv import load_dotenv
from langgraph.types import Command
from typing_extensions import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from typing import List, Optional, Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from uagents_adapter import LangchainRegisterTool, cleanup_uagent
from uagents_adapter.langchain import AgentManager
from ai_engine import UAgentResponse, UAgentResponseType

# Load environment variables
load_dotenv()

class FlightDetail(BaseModel):
    departure_airport: Annotated[Optional[str], Field(None, description="Departure airport code or name")]
    arrival_airport: Annotated[Optional[str], Field(None, description="Arrival airport code or name")]
    departure_time: Annotated[Optional[str], Field(None, description="Scheduled departure time")]
    arrival_time: Annotated[Optional[str], Field(None, description="Scheduled arrival time")]

class TrainDetail(BaseModel):
    train_number: Annotated[Optional[str], Field(None, description="Train number")]
    departure_station: Annotated[Optional[str], Field(None, description="Departure station code or name")]
    arrival_station: Annotated[Optional[str], Field(None, description="Arrival station code or name")]
    departure_time: Annotated[Optional[str], Field(None, description="Scheduled departure time")]
    arrival_time: Annotated[Optional[str], Field(None, description="Scheduled arrival time")]
    train_fare: Annotated[Optional[float], Field(None, description="Train fare")]

class HotelDetail(BaseModel):
    name: Annotated[str, Field(..., description="Hotel name")]
    address: Annotated[Optional[str], Field(None, description="Hotel address")]
    check_in_time: Annotated[Optional[str], Field(None, description="Hotel check-in time")]
    check_out_time: Annotated[Optional[str], Field(None, description="Hotel check-out time")]

class Attraction(BaseModel):
    image: Annotated[Optional[str],add_messages] = Field(None, description="Valid public URL for each attraction. If there are multiple attractions, then there should be multiple images")
    name: Annotated[str, Field(..., description="Attraction name")]
    description: Annotated[Optional[str], Field(None, description="Brief description of the attraction")]

class Restaurant(BaseModel):
    name: Annotated[str, Field(..., description="Restaurant name")]
    cuisine: Annotated[Optional[str], Field(None, description="Type of cuisine")]
    address: Annotated[Optional[str], Field(None, description="Restaurant address")]

class DayItinerary(BaseModel):
    day: str = Field(..., description="Day label, e.g., 'Day 1'")
    flight_details: List[FlightDetail] = Field(default_factory=list, description="List of flight details for the day")
    train_details: List[TrainDetail] = Field(default_factory=list, description="List of train details for the day")
    hotels: List[HotelDetail] = Field(default_factory=list, description="List of hotels for the day")
    hotel_check_in_time: Optional[str] = Field(None, description="Hotel check-in time for the day")
    local_attractions: List[Attraction] = Field(default_factory=list, description="List of local attractions for the day")
    cab_fare: Optional[float] = Field(None, description="Estimated cab fare for the day")
    nearby_restaurants: List[Restaurant] = Field(default_factory=list, description="List of nearby restaurants for the day")

class LocalTip(BaseModel):
    tip: Annotated[str, add_messages] = Field(...,description="Tip or advice about the destination, so that the user can plan well")
    category: Annotated[Optional[str],add_messages] = Field(None,description="Category of the tip (e.g., weather, local customs or important occasions to enjoy in the destination during the trip if any)")

class Itinerary(BaseModel):
    days: List[DayItinerary] = Field(default_factory=list, description="List of day-by-day itinerary details from Day 1, e.g., 'Day 1', 'Day 2'")
    tips: List[LocalTip] = Field(default_factory=list, description="List of local tips for the trip")

class AgentState(MessagesState):
    # Final structured response from the agent
    final_response: Itinerary

# Set your API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_TOKEN = os.getenv("AGENTVERSE_API_KEY")

# Initialize the model
model = ChatOpenAI(model="gpt-4o", temperature=0)

# Store the graph globally so it can be accessed by the wrapper function
_global_graph = None
# Add an event to signal when the graph is ready
graph_ready = asyncio.Event()

sys_msg = SystemMessage(content=
        """
        You are a supervisor agent for a multi-agent travel planner system. Your role is to coordinate and guide other agents 
        (like Flight Search, Hotel Search, Food, Attractions, and Local Tips), making strategic decisions based on the user's 
        preferences and the current state of the plan.

        You will:
        - ASSIGN TASKS to the agents based on the user's input and the agents' expertise.
        - Ensure that all necessary information is gathered before generating the final itinerary.

        Assign work to one agent at a time — DO NOT call agents in parallel.

        ***DO NOT DO ANY WORK YOURSELF***

        You must:
        1. Understand the user's travel intent and preferences.
        2. Break down the planning into manageable sub-tasks (e.g., flight search, hotel options, food, attractions).
        3. Decide the order in which these sub-tasks should be executed.
        4. Dynamically decide which agent/tool should be invoked at each step.
        5. Maintain memory of what has already been completed (flights booked, hotel found, etc.).
        6. Update and refine the plan with each new piece of information.
        7. Ensure all agent calls help move toward a complete, realistic travel plan.
        8. Always consider future dates and the current date when planning. Use today_date tool for that. The current year is 2025.
        9. Ensure the plan is budget-aware and enjoyable for the user.
        10. If currency is not provided, assume the currency of the departure location.
        11. After getting all the values for expenditure, plot a simple pie-chart to show the expense distribution.
            Currency should be converted into ISO 4217 format, e.g., EUR for Euro, USD for US Dollar, INR for Indian Rupee.

        11. If the date is "today", "tomorrow", or "next Monday", convert it to ISO format (YYYY-MM-DD) for all date-related tasks. 
            Get today’s date using the `today_date` tool.

        12. After getting the list of flights and hotels from the respective agents, book the cheapest flight and hotel that fits the budget. 
            If no flights or hotels are available, inform the user that no options are available within the budget.

        13. Do NOT ask the user for tourist attraction preferences. Instead, search for the top tourist attractions in the destination 
            using the `search_attractions` tool and get the results.

        14. Get the valid public images URL for the attractions.

        ***CAREFULLY REASON THE GIVEN BUDGET USING THE GIVEN CURRENCY AND SEE WHETHER THE TRIP CAN BE DONE COMFORTABLY WITH THIS BUDGET***
        ***YOU NEED TO REASON WELL ABOUT THE INPUTS PROVIDED BY THE USER. IF THE USER SAYS "WE ARE GOING FOR A HONEYMOON TRIP/COUPLES", 
        YOU SHOULD ASSUME THAT THERE ARE 2 ADULTS AND NO CHILDREN. SIMILARLY REASON WELL AND HANDLE EDGE CASES.***

        Rules:
        - Always think step-by-step before invoking a tool.
        - Be efficient; only call tools when absolutely necessary.
        - Infants travel on the lap of an adult traveler, and thus the number of infants must not exceed the number of adults.

        Your goal is to build a coherent, budget-aware, enjoyable trip for the user.

        Respond with a subsequent question to the user to gather more information or provide the output.

        You will receive all collected data in a JSON-like structure:
        * flights
        * hotels
        * attractions
        * food_options
        * local_tips
        * budget_breakdown

        INSTRUCTIONS:
        1. Produce a **day-by-day** Markdown itinerary.
        2. For each day, list:
            * Flight / check-in (Day 1 only)
            * Attractions with inline images (![ ](<url>)). Images should be small with 200–300 px only. 
                Use search_web tool to get image of the attraction.
            * Try to add all attractions images that are publicly available.
            * Meal suggestions with valid links
            * Estimated cab fares
        3. plot a simple pie-chart to show the expense distribution
        4. Conclude with a **summary table** of total expenses by category (flights, hotels, food, transport, misc).
        5. Use headings (### Day 1), bullet lists, and Markdown tables.

        Respond **only** with the formatted Markdown.

""")

async def setup_multi_server_graph_agent():
    global _global_graph
    
    print("Setting up multi-server graph agent...")
    try:
        # Create the client without async with
        client = MultiServerMCPClient(
            {
                "today_date": {
                    "command": "python",
                    "args": ["./today_date.py"],
                    "transport": "stdio",
                },
                "search_flights": {
                    "command": "python",
                    "args": ["./search_flights.py"],
                    "transport": "stdio",
                },
                "regenerate_token": {
                    "command": "python",
                    "args": ["./regenerate_token.py"],
                    "transport": "stdio",
                },
                "search_hotels": {
                    "command": "python",
                    "args": ["./search_hotels.py"],
                    "transport": "stdio",
                },
                "search_food": {
                    "command": "python",
                    "args": ["./search_food.py"],
                    "transport": "stdio",
                },
                "search_attractions": {
                    "command": "python",
                    "args": ["./search_attractions.py"],
                    "transport": "stdio",
                },
                "local_tips": {
                    "command": "python",
                    "args": ["./local_tips.py"],
                    "transport": "stdio",
                },
                # "search_image": {
                #     "command": "python",
                #     "args": ["./search_image.py"],
                #     "transport": "stdio",
                # },
                # "show_expenditure": {
                #     "command": "python",
                #     "args": ["./show_expenditure.py"],
                #     "transport": "stdio",
                # },
            }
        )
        
        # Get tools directly
        tools = await client.get_tools()
        print(f"Successfully loaded {len(tools)} tools")
        
        # Define call_model function
        def call_model(state: AgentState):
            response = model.bind_tools(tools).invoke([sys_msg]+state["messages"])
            return {"messages": [response]}
    
        # Define the function that responds to the user
        def respond(state: AgentState):
            # We call the model with structured output in order to return the same format to the user every time
            # state['messages'][-2] is the last ToolMessage in the convo, which we convert to a HumanMessage for the model to use
            # We could also pass the entire chat history, but this saves tokens since all we care to structure is the output of the tool
            response = model.with_structured_output(Itinerary).invoke(
                [HumanMessage(content=state["messages"][-2].content)]
            )
            # We return the final answer
            # return {"final_response": response}
            return UAgentResponse(
                message=json.dumps(response),
                type=UAgentResponseType.FINAL
            )
        
        
        # Define the function that determines whether to continue or not
        def should_continue(state: AgentState):
            a=0
            messages = state["messages"]
            last_message = messages[-1]
            # If there is no function call, then we respond to the user
            if not last_message.tool_calls:
                if a==0:
                    return "end"
                a=0
                return "respond"
            # Otherwise if there is, we continue
            else:
                a+=1
                return "continue"

        # Build the graph
        builder = StateGraph(AgentState)
        builder.add_node("agent", call_model)
        builder.add_node("respond", respond)
        builder.add_node("tools", ToolNode(tools))
        builder.add_edge(START, "agent")
        builder.add_conditional_edges(
            "agent",
            should_continue,
            {
                "continue": "tools",
                "respond": "respond",
                "end": END,
            },
        )
        builder.add_edge("tools", "agent")
        builder.add_edge("respond", END)

        _global_graph = builder.compile()
        print("Graph successfully compiled")
        
        # Signal that the graph is ready
        graph_ready.set()
        # Keep the connection alive
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error setting up graph: {e}")
        # Set the event even in case of error to avoid deadlock
        graph_ready.set()

def main():
    print("Initializing agent...")
    # Initialize agent manager
    manager = AgentManager()
    
    # Create graph wrapper with proper error handling
    async def graph_func(x):
        # Wait for the graph to be ready before trying to use it
        await graph_ready.wait()
        
        if _global_graph is None:
            error_msg = "Error: Graph not initialized properly. Please try again later."
            print(f"Response: {error_msg}")
            return error_msg
        
        try:
            # Process the message
            TIMEOUT = 120
            # Wrap the main operation in asyncio.wait_for
            response = await asyncio.wait_for(
                _global_graph.ainvoke({"messages": x}),
                timeout=TIMEOUT
            )
            
            # Extract and print the response
            result = response["messages"][-1].content
            print(f"\n✅ Response: {result}\n")
            return result
        except asyncio.TimeoutError:
            error_msg = f"⏰ Request timed out after {TIMEOUT} seconds."
            print(f"\n❌ {error_msg}\n")
            return error_msg
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            print(f"\n❌ {error_msg}\n")
            return error_msg
    
    agent_wrapper = manager.create_agent_wrapper(graph_func)
    
    # Start the graph in background

    manager.start_agent(setup_multi_server_graph_agent)
    
    # Register with uAgents
    print("Registering multi-server graph agent...")
    tool = LangchainRegisterTool()
    try:
        agent_info = tool.invoke(
            {
                "agent_obj": agent_wrapper,
                "name": "ParadoxSupervisor",
                "port": 8010,
                "description": "Acts as the intelligent entry point for all user travel queries in the system.",
                "api_token": API_TOKEN,
                "mailbox": True
            }
        )
        print(f"✅ Registered multi-server graph agent: {agent_info}")
    except Exception as e:
        print(f"⚠️ Error registering agent: {e}")
        print("Continuing with local agent only...")
    try:
        manager.run_forever()
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
        cleanup_uagent("ParadoxSupervisor")
        print("✅ Graph stopped.")

if __name__ == "__main__":
    main()