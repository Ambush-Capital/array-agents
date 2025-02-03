from agents.data_analyst import DataAnalystAgent

if __name__ == "__main__":
    # Create an instance of DataAnalystAgent
    agent = DataAnalystAgent(market_data_file="/Users/carly/rayray/trading-strategies-ai/data/market_data/market_data.csv")
    
    # Call the analyze_market method
    analysis = agent.analyze_market()
    
    # Print the analysis result
    print(analysis)