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
    def fetch_wallet_data(self, wallet_id=None) -> Dict[Any, str]:
        """
        Fetch and format wallet data.
        
        Args:
            wallet_id (str, optional): The wallet ID to fetch data for.
                                      If not provided, a default wallet ID will be used.
        
        Returns:
            Dict: Wallet data as a dictionary
        """
        base_url = "http://localhost:3001"
        # Use provided wallet_id or fall back to default
        wallet_id = wallet_id or "8y9wxTgm4G8gJ1RZr4fQ5eGXtb5vMNXVpd2nGKVTJSYL"
        full_url = f"{base_url}/wallet/{wallet_id}"  # Use structured input

        try:
            print(f"Fetching wallet data for wallet ID: {wallet_id}...")
            response = requests.get(full_url)
            response.raise_for_status()
            return response.json()  # Return parsed JSON response as a dictionary
        except requests.RequestException as e:
            return {"error": f"Error fetching wallet data: {str(e)}"}  # Return error message as dictionary


if __name__ == "__main__":
    instance = WalletData()
    print(instance.fetch_wallet_data())