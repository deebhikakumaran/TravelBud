from mcp.server.fastmcp import FastMCP
from main import tavily_search

mcp = FastMCP("LocalTips")

@mcp.tool()
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
    # dep = parse_date(departure_date)
    # ret = parse_date(return_date)
    query = (
        f"Local customs, weather, and travel tips for {destinations} "
        f"from {departure_date} to {return_date}, plus any local festivals or events."
    )
    return tavily_search.invoke({"query": query})

if __name__ == "__main__":
    mcp.run(transport="stdio")