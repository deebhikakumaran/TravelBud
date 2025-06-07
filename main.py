import dateparser
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain_community.tools.tavily_search import TavilySearchResults
import requests
from dotenv import load_dotenv
import datetime
from typing import List, Optional, Annotated
from pydantic import BaseModel, Field
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, AIMessage
load_dotenv()

import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# if "GOOGLE_API_KEY" not in os.environ:
#     os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

llm = ChatOpenAI(model="gpt-4.1", temperature=0)

tavily_search=TavilySearchResults(max_results=5)

from typing import List, Optional, Annotated
from pydantic import BaseModel, Field

token = "CXNoAMYmAWl1NyJ1cHSLPznPKbaW"

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

class Itinerary(BaseModel):
    days: List[DayItinerary] = Field(default_factory=list, description="List of day-by-day itinerary details from Day 1, e.g., 'Day 1', 'Day 2'")


def parse_date(date_str: str) -> str:
    """Parse a natural-language date into DD-MM-YYYY."""
    parsed = dateparser.parse(date_str)
    if parsed is None:
        raise ValueError(f"Could not parse date: {date_str}")
    return parsed.strftime("%d-%m-%Y")


@tool
def today_date() -> datetime.date:
    """Return today's date."""
    return datetime.date.today()


@tool
def search_flights(depart: str, destinations: str, departure_date: str, return_date: str) -> str:
    """
    Search for flights from the departure location to the destinations on the specified travel dates.

    Args:
        depart (str): IATA code or city name of departure airport.
        destinations (str): IATA code or city name of destination airport(s).
        departure_date (str): Desired departure date in natural language (e.g. "June 2, 2025").
        return_date (str): Desired return date in natural language.

    Returns:
        str: Raw JSON or text response from TavilySearchResults containing flight options.
    """
    dep = parse_date(departure_date)
    ret = parse_date(return_date)
    query = (
        f"Search flights from {depart} to {destinations} for a round-trip, "
        f"departing {dep}, returning {ret}"
    )
    return tavily_search.invoke({"query": query})

# @tool
# def search_flights(
#     origin_location_code: str,
#     destination_location_code: str,
#     departure_date: str,
#     return_date: str,
#     adults: str,
#     travel_class: str = "ECONOMY",
#     children: str = "0",
#     infants: str = "0",
#     currency: str = "INR",
#     airline_code: str = None
# ) -> str:
#     """
#     Get flight availability details and offers.

#     Args:
#         origin_location_code (str): The IATA code of the origin location.
#         destination_location_code (str): The IATA code of the destination location.
#         departure_date (str): Departure date in ISO format ('YYYY-MM-DD').
#         return_date (str): Return date in ISO format ('YYYY-MM-DD').
#         adults (str): Number of adults.
#         children (str): Number of children.
#         infants (str): Number of infants.
#         travel_class (str): Travel class (e.g., 'ECONOMY', 'PREMIUM ECONOMY', 'BUSINESS', 'FIRST CLASS'). Default is 'ECONOMY'.
#         currency (str): Currency code in ISO 4217 format (default is 'EUR').
#         airline_code (str, optional): The two-letter IATA airline code (e.g., 'WY' for Oman Air, 'EK' for Emirates). If not provided, results will not be filtered by airline.
    
#     Returns:
#     - A list of available flights operating on the given date from the specified origin to destination and return.
#     - For each flight, include details such as:
#         * Flight number
#         * Departure and arrival airports
#         * Departure and arrival times
#         * Travel class
#         * Operating airline
#         * Price

#     ** Do not include Aircraft Details.**
#     """
#     try:
#         global token

#         base_url = (
#             f"https://test.api.amadeus.com/v2/shopping/flight-offers?"
#             f"originLocationCode={origin_location_code}&"
#             f"destinationLocationCode={destination_location_code}&"
#             f"departureDate={departure_date}&"
#             f"returnDate={return_date}&"
#             f"adults={adults}&"
#             f"children={children}&"
#             f"infants={infants}&"
#             f"travelClass={travel_class}&"
#             f"nonStop=false&currencyCode={currency}&max=10"
#         )

#         # Append airline code filter if provided
#         if airline_code:
#             base_url += f"&includedAirlineCodes={airline_code}"

#         headers = {
#             "Authorization": f"Bearer {token}"
#         }

#         response = requests.get(base_url, headers=headers)

#         return response.text
#     except Exception as e:
#         return f"Unable to fetch flights."

@tool
def regenerate_token() -> dict:
    """
    Return the access token when it is expired from the domain **test.api.amadeus.com**
    
    Return:
        Access token
    """
    global token

    try:
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"

        payload = {
            'client_id': 'Yop9wZHCvDFA4gEgPxnMrsQz6dhdC8qk',
            'client_secret': 'ZlqJ2GQwDnozgdjw',
            'grant_type': 'client_credentials'
        }

        files = []

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        token = response.json()['access_token']
        return response.text

    except Exception as e:
        return "Unable to regenerate token"
    
@tool
def search_hotels(destinations: str, budget: int) -> str:
    """
    Search for hotels in the specified destinations within the given total budget.

    Args:
        destinations (str): City name or region to search hotels in.
        budget (int): Total budget (in the user's currency) for the entire hotel stay.

    Returns:
        str: Raw JSON or text response from TavilySearchResults containing hotel options.
    """
    query = f"Search hotels in {destinations} within a total budget of {budget}"
    return tavily_search.invoke({"query": query})


@tool
def search_food(destinations: str, food_preferences: str) -> str:
    """
    Find restaurants or food options in the specified destinations matching the user's preferences.

    Args:
        destinations (str): City or neighborhood to search for food.
        food_preferences (str): Dietary or cuisine preferences (e.g., "vegetarian", "sushi").

    Returns:
        str: Raw JSON or text response from TavilySearchResults containing restaurant options.
    """
    query = f"Find restaurants in {destinations} serving {food_preferences}"
    return tavily_search.invoke({"query": query})

@tool
def search_attractions(destinations: str) -> str:
    """
    Search for the top tourist attractions in the specified destinations.

    Args:
        destinations (str): City or region to find attractions in.

    Returns:
        str: Raw JSON or text response from TavilySearchResults containing attraction listings.
    """
    query = f"Top tourist attractions in {destinations}"
    return tavily_search.invoke({"query": query})

@tool
def local_tips(destinations: str, departure_date: str, return_date: str) -> str:
    """
    Search for local customs, weather, and travel tips (including festivals/events)
    in the specified destinations and travel window.

    Args:
        destinations (str): City or region to gather local tips for.
        departure_date (str): Start of the trip in natural language.
        return_date (str): End of the trip in natural language.

    Returns:
        str: Raw JSON or text response from TavilySearchResults containing local tips.
    """
    dep = parse_date(departure_date)
    ret = parse_date(return_date)
    query = (
        f"Local customs, weather, and travel tips for {destinations} "
        f"from {dep} to {ret}, plus any local festivals or events."
    )
    return tavily_search.invoke({"query": query})


@tool
def search_web(query) -> str:
    """
    Search for content and images from web

    Args:
        query (str): search query

    Returns:
        str: Raw JSON or text response from TavilySearchResults containing search results.
    """
    query = f"{query}"
    return tavily_search.invoke({"query": query})


#Agents
# flight_agent = create_react_agent(
#     llm,
#     tools=[today_date, search_flights, regenerate_token],
#     prompt="""
#     You are a flight booking expert.\n"
#     - Assist ONLY with flight booking tasks.\n"
#     - Return **only** the flight search results.\n"
#     - Consider class of traveller to be economy if not provided.\n"
#     - Suggest layover flights if no direct flights are available and are available at low cost.\n"
#     """,
#     name="flight_agent",
# )
flight_agent = create_react_agent(
    llm,
    tools=[today_date, search_flights],
    prompt="""
    You are a flight booking expert.\n"
    - Assist ONLY with flight booking tasks.\n"
    - Return **only** the flight search results.\n"
    - Consider class of traveller to be economy if not provided.\n"
    - Suggest layover flights if no direct flights are available and are available at low cost.\n"
    """,
    name="flight_agent",
)

hotel_agent = create_react_agent(
    llm,
    tools=[today_date, search_hotels],
    prompt="""
    You are a hotel booking expert.\n"
    - Assist ONLY with hotel booking tasks.\n"
    - Return **only** the hotel search results.\n"
    """,
    name="hotel_agent",
)

food_agent = create_react_agent(
    llm,
    tools=[today_date, search_food],
    prompt=(
        "You are a restaurant and food recommendation expert.\n"
        "Assist ONLY with restaurant and food recommendation tasks.\n"
        "Return **only** the food search results."
    ),
    name="food_agent",
)

attraction_agent = create_react_agent(
    llm,
    tools=[today_date, search_attractions],
    prompt=(
        "You are a tourist attraction expert.\n"
        "Assist ONLY with attraction search tasks.\n"
        "Return **only** the attractions search results."
    ),
    name="attraction_agent",
)

local_tips_agent = create_react_agent(
    llm,
    tools=[today_date, local_tips],
    prompt=(
        "You are a local tips expert.\n"
        "Assist ONLY with local customs and tips tasks.\n"
        "Return **only** the local tips search results."
    ),
    name="local_tips_agent",
)


#Supervisor

# supervisor = create_supervisor(
#     model=init_chat_model("openai:o3-mini"),
#     agents=[
#         flight_agent,
#         hotel_agent,
#         food_agent,
#         attraction_agent,
#         local_tips_agent,
#     ],
#     tools=[today_date],
#     prompt=(
#         """You are a supervisor agent for a multi-agent travel planner system. Your role is to coordinate and guide other agents
#         (like Flight Search, Hotel Search, Food, Attractions, and Local Tips),
#         making strategic decisions based on the user's preferences and the current state of the plan.

#         You must:
#         1. Understand the user's travel intent and preferences.
#         2. Break down the planning into manageable sub-tasks (e.g., flight search, hotel options, food, attractions).
#         3. Decide the order in which these sub-tasks should be executed.
#         4. Dynamically decide which agent/tool should be invoked at each step.
#         5. Maintain memory of what has already been completed (flights booked, hotel found, etc).
#         6. Update and refine the plan with each new piece of information.
#         7. Ensure all agent calls help move toward a complete, realistic travel plan.
#         8. Always consider future dates and the current date when planning.
#         9. Ensure the plan is budget-aware and enjoyable for the user.
#         10. Use the formatter agent to compile the final itinerary.
#         11. If currency is not provided, assume the currency of the departure location.
#         ***CAREFULLY REASON THE GIVEN BUDGET USING THE GIVEN CURRENCY AND SEE WHETHER THE TRIP CAN BE DONE COMFORTABLY USING THAT BUDGET, IF NOT, TELL THE USER YOU CANNOT VISIT COMFORTABLY WITH THIS BUDGET***

#         Rules:
#         - Always think step-by-step before invoking a tool.
#         - Be efficient: only call tools when absolutely necessary.

#         Your goal is to build a coherent, budget-aware, enjoyable trip for the user.

#         Respond with a subsequent question to the user to gather more information or provide the output of formatter agent 
#         only if all details are available. Do not summarize.

#         "You will receive all collected data in a JSON-like structure:\n"
#         - flights\n"
#         - hotels\n"
#         - attractions\n"
#         - food_options\n"
#         - local_tips\n"
#         - budget_breakdown\n\n"

#         INSTRUCTIONS:\n"
#         1. Produce a **day-by-day** Markdown itinerary.\n"
#         2. For each day, list:\n"
#         - Flight / check-in (Day 1 only)\n"
#         - Attractions with inline images (`![](<url>)`). Images should be small with 200 - 300 px only. Use search_web tool to get them.\n"
#         - Try to add all attractions images that are publicly available.\n"
#         - Meal suggestions with valid links\n"
#         - Estimated cab fares\n"
#         3. Conclude with a **summary table** of total expenses by category (flights, hotels, food, transport, misc).\n"
#         4. Use headings (`### Day 1`), bullet lists, and Markdown tables.\n\n"
#         Respond *only* with the formatted Markdown.
#         """),
#     add_handoff_messages=False,
#     add_handoff_back_messages=False,
#     output_mode="last_message",
#     response_format=Itinerary,
#     state_schema=AgentStateWithStructuredResponse
# )

# app = supervisor.compile()