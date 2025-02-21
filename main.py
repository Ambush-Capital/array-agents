from agents.fetch_market_data import MarketData
from agents.data_analyst import DataAnalystAgent
from agents.portfolio_manager import PortfolioManagerAgent
import json
import os

def print_result(result):
    """Pretty print the result dictionary."""
    if isinstance(result, dict):
        if "error" in result:
            print("❌ Error:", result["error"])
        elif "result" in result:
            if isinstance(result["result"], dict) and "instructions" in result["result"]:
                # Print the human-readable summary
                print("📊 Summary:")
                print(result["result"]["summary"])
                
                print("\n🤖 Machine-Readable Instructions:")
                print(json.dumps(result["result"]["instructions"], indent=2))
            else:
                print("✅ Success:\n", result["result"])
    else:
        print("⚠️ Unexpected result format:", result)

def main():
    # Step 1: Initialize and fetch market data
    print("\n📊 Fetching market data...")
    market_data = MarketData()
    api_url = "http://localhost:3001/current_markets"
    success = market_data.fetch_market_data(api_url)
    
    if not success:
        print("❌ Failed to fetch market data. Exiting...")
        return
    
    # Step 2: Pass market data to analyst
    print("\n🔍 Running market analysis...")
    data_analyst = DataAnalystAgent(market_data)
    analysis_result = data_analyst.analyze_market()
    print_result(analysis_result)
    
    # Step 3: Pass market data and analysis result to portfolio manager
    portfolio_result = None
    if "error" not in analysis_result:
        print("\n💼 Generating portfolio recommendations...")
        portfolio_manager = PortfolioManagerAgent(market_data)
        portfolio_result = portfolio_manager.analyze_market()
        print_result(portfolio_result)
    else:
        print("\n⛔ Skipping portfolio analysis due to market analysis error.")

if __name__ == "__main__":
    main()