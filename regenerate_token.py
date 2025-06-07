from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("RegenerateToken")

token = "CXNoAMYmAWl1NyJ1cHSLPznPKbaW"

@mcp.tool()
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

if __name__ == "__main__":
    mcp.run(transport="stdio")