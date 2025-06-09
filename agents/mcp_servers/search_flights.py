from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("SearchFood")

token = "CXNoAMYmAWl1NyJ1cHSLPznPKbaW"

@mcp.tool()
def search_flights(
    origin_location_code: str,
    destination_location_code: str,
    departure_date: str,
    return_date: str,
    adults: str,
    travel_class: str = "ECONOMY",
    children: str = "0",
    infants: str = "0",
    currency: str = "INR",
    airline_code: str = None
) -> str:
    """
    Get flight availability details and offers.

    Args:
        origin_location_code (str): The IATA code of the origin location.
        destination_location_code (str): The IATA code of the destination location.
        departure_date (str): Departure date in ISO format ('YYYY-MM-DD').
        return_date (str): Return date in ISO format ('YYYY-MM-DD').
        adults (str): Number of adults.
        children (str): Number of children.
        infants (str): Number of infants.
        travel_class (str): Travel class (e.g., 'ECONOMY', 'PREMIUM ECONOMY', 'BUSINESS', 'FIRST CLASS'). Default is 'ECONOMY'.
        currency (str): Currency code in ISO 4217 format (default is 'EUR').
        airline_code (str, optional): The two-letter IATA airline code (e.g., 'WY' for Oman Air, 'EK' for Emirates). If not provided, results will not be filtered by airline.
    
    Returns:
    - A list of available flights operating on the given date from the specified origin to destination and return.
    - For each flight, include details such as:
        * Flight number
        * Departure and arrival airports
        * Departure and arrival times
        * Travel class
        * Operating airline
        * Price

    ** Do not include Aircraft Details.**
    """
    try:
        global token

        base_url = (
            f"https://test.api.amadeus.com/v2/shopping/flight-offers?"
            f"originLocationCode={origin_location_code}&"
            f"destinationLocationCode={destination_location_code}&"
            f"departureDate={departure_date}&"
            f"returnDate={return_date}&"
            f"adults={adults}&"
            f"children={children}&"
            f"infants={infants}&"
            f"travelClass={travel_class}&"
            f"nonStop=false&currencyCode={currency}&max=10"
        )

        # Append airline code filter if provided
        if airline_code:
            base_url += f"&includedAirlineCodes={airline_code}"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(base_url, headers=headers)

        return response.text
    except Exception as e:
        return f"Unable to fetch flights."

if __name__ == "__main__":
    mcp.run(transport="stdio")