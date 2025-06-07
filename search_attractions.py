from mcp.server.fastmcp import FastMCP
from main import tavily_search

mcp = FastMCP("SearchAttractions")

@mcp.tool()
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

if __name__ == "__main__":
    mcp.run(transport="stdio")