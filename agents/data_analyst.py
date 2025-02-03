import openai
import pandas as pd
from config import OPENAI_API_KEY

# Set up your OpenAI API key
openai.api_key = OPENAI_API_KEY

class DataAnalystAgent:
    def __init__(self, market_data_file="/Users/carly/rayray/trading-strategies-ai/data/market_data/market_data.csv"):
        self.market_data_file = market_data_file

    def analyze_market(self):
        # 1. Load market data from CSV
        try:
            market_data = pd.read_csv(self.market_data_file)
        except FileNotFoundError:
            return "Error: Market data file not found."  # Handle file errors

        # 2. Extract relevant data (example - adjust based on your CSV structure)
        # solana_price = market_data['SOL_price'].iloc[-1]  # Get latest SOL price
        # liquidity_pools = market_data[['pool_name', 'APY']]  # Get pool data

        # 3. Prepare the prompt for the LLM
        prompt = f"""Use the current {market_data}  to make a specific recommendation on how to allocate $10000 with moderate risk"""
        #to identify opportunities for yield.

       # * Liquidity of trading pairs
       # * APYs offered by different DeFi protocols
       # * Potential risks (impermanent loss, smart contract vulnerabilities)
       # * Overall market sentiment (positive, negative, neutral)

        #Provide a concise summary of your findings and highlight the most promising opportunities for yield generation. Use specific numbers for the protocols
   # """
        # 4. Call the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a financial analyst specializing in DeFi investments."},
                        {"role": "user", "content": prompt}],
                max_tokens=300
            )
            analysis_result = response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error in AI response: {str(e)}"

        return analysis_result  # 4. Return the analysis result