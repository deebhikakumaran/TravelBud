from mcp.server.fastmcp import FastMCP
from main import tavily_search

mcp = FastMCP("SearchHotels")

@mcp.tool()
def search_hotels(destinations: str, departure_date: str,return_date: str, budget: int) -> str:
    """
    Search for hotels in the specified destinations within the given total budget.
    The budget given is entire trip budget, divide the total amount by number of nights to arrive at per day hotel cost.
    Also leave some amount for other activities such as restaurants, visiting tourist places, misc, etc.,

    Args:
        destinations (str): City name or region to search hotels in.
        departure_date (str): Departure date in ISO format ('YYYY-MM-DD').
        return_date (str): Return date in ISO format ('YYYY-MM-DD').
        budget (int): Total budget (in the user's currency) for the entire hotel stay.

    Returns:
        str: Raw JSON or text response from TavilySearchResults containing hotel options under the given budget leaving some amount for other activities.
    """
    query = f"Search hotels in {destinations} for days between {departure_date} and {return_date} within a total budget of {budget}"
    return tavily_search.invoke({"query": query})

if __name__ == "__main__":
    mcp.run(transport="stdio")