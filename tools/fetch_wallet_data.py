import requests
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field

class WalletData():
    """Knowledge source that fetches data from Wallet Data API."""
    # wallet_id: str = Field(
    #         default="8y9wxTgm4G8gJ1RZr4fQ5eGXtb5vMNXVpd2nGKVTJSYL",
    #         description="The unique identifier for the wallet."
    #     )
    def fetch_wallet_data(self) -> Dict[Any, str]:
        """Fetch and format wallet data."""
        base_url = "http://localhost:3001"
        wallet_id = "8y9wxTgm4G8gJ1RZr4fQ5eGXtb5vMNXVpd2nGKVTJSYL"
        full_url = f"{base_url}/wallet/{wallet_id}"  # Use structured input

        try:
            print("Fetching wallet data...")
            response = requests.get(full_url)
            response.raise_for_status()
            return response.text  # Return JSON response as a string
        except requests.RequestException as e:
            return f"Error fetching wallet data: {str(e)}"  # Return error message


if __name__ == "__main__":
    instance = WalletData()
    print(instance.fetch_wallet_data())