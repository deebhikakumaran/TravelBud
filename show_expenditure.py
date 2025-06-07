from mcp.server.fastmcp import FastMCP
import matplotlib.pyplot as plt
import io
import base64

mcp = FastMCP("ShowExpenditure")

@mcp.tool()
def show_expenditure(expenditures: dict) -> str:
    """
    Get all the expenses and generate a pie chart for expenditure distribution and return it as a base64 image string.

    Args:
        expenditures (dict): A dictionary of category-wise expenditures.
            Example: {"Food": 1000, "Travel": 3000, "Stay": 2000}

    Returns:
        str: Base64 string of the pie chart image.
    """
    try:
        categories = list(expenditures.keys())
        amounts = list(expenditures.values())

        # Create pie chart
        fig, ax = plt.subplots()
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures pie is circular

        # Save image to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)

        # Encode buffer to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        return f"Error generating pie chart: {e}"

if __name__ == "__main__":
    mcp.run(transport="stdio")