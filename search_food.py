from mcp.server.fastmcp import FastMCP
from main import tavily_search

mcp = FastMCP("SearchFood")

@mcp.tool()
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

if __name__ == "__main__":
    mcp.run(transport="stdio")