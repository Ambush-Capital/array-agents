import requests
from datetime import datetime
from typing import Dict, Any
from pydantic import Field
import os

class MarketData():
    """Knowledge source that fetches data from Market Data API."""

    def fetch_market_data(self) -> Dict[Any, str]:
        """Fetch and format market data."""
        base_url = "http://localhost:3001"
        self.api_endpoint = "/current_markets"
        full_url = f"{base_url}{self.api_endpoint}"  # Use structured input

        try:
            print("Fetching market data...")
            response = requests.get(full_url)
            response.raise_for_status()
            return response.text  # Return JSON response as a string
        except requests.RequestException as e:
            return f"Error fetching market data: {str(e)}"  # Return error message

if __name__ == "__main__":
    instance = MarketData()
    print(instance.fetch_market_data())