from mcp.server.fastmcp import FastMCP
import datetime

mcp = FastMCP("SearchFood")

@mcp.tool()
def today_date() -> datetime.date:
    """Return today's date."""
    return datetime.date.today()

if __name__ == "__main__":
    mcp.run(transport="stdio")