from mcp.server.fastmcp import FastMCP
from main import tavily_search

mcp = FastMCP("SearchImage")

@mcp.tool()
def search_image(attractions: str, destinations: str) -> str:
    """
    Search valid image URLs from web for the attractions every time when asked.
    Get images from gettyimages.com ONLY.

    Args:
        attractions (str): The name of attractions.
        destinations (str): The name of the destination city or region.

    Returns:
        str: Valid imageUrl for the attractions.

    Note: DO NOT get wikimedia.org image URLs
    """
    try:
        query = f"Get the valid image URLs of {attractions} in {destinations}"
        return tavily_search.invoke({"query": query})
    except Exception as e:
        return f"Unable to fetch image URLs for attractions. Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")