import requests
import json

class MarketData:
    def __init__(self):
        self.data = None
        
    def fetch_market_data(self, api_url):
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            self.data = response.json()
            print(f"Market data successfully fetched")
            return True

        except requests.RequestException as e:
            print(f"Error fetching market data: {str(e)}")
            return False
        except Exception as e:
            print(f"Error saving market data: {str(e)}")
            return False
    
    def get_market_data(self):
        return self.data

if __name__ == "__main__":
    api_url = "http://localhost:3001/current_markets"
    # output_file = "/Users/carly/rayray/brains-py/data/market_data/market_data.json"
    market_data = MarketData()
    market_data.fetch_market_data(api_url)
    print(market_data.get_market_data())