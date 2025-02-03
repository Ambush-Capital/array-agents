import openai
import pandas as pd
from config import OPENAI_API_KEY
from agents.data_analyst import DataAnalystAgent

# Set up your OpenAI API key
openai.api_key = OPENAI_API_KEY

class PortfolioManagerAgent:
    def __init__(self, market_data_file="/Users/carly/rayray/trading-strategies-ai/data/market_data/market_data.csv", wallet_data_file="/Users/carly/rayray/trading-strategies-ai/data/wallet_data/current_wallet.csv"):
        self.market_data_file = market_data_file
        self.wallet_data_file = wallet_data_file
        self.data_analyst = DataAnalystAgent(market_data_file)

    def analyze_market(self):
        # Use DataAnalystAgent to get the analysis result
        analysis_result = self.data_analyst.analyze_market()
        if "Error" in analysis_result:
            return analysis_result

        # Load current wallet data from CSV
        try:
            wallet_data = pd.read_csv(self.wallet_data_file)
        except FileNotFoundError:
            return "Error: Wallet data file not found."  # Handle file errors

        # Prepare the prompt for the LLM to generate rebalancing instructions
        prompt = f"""Based on the following analysis result and current wallet data, provide instructions for rebalancing the wallet:
        Analysis Result: {analysis_result}
        Current Wallet Data: {wallet_data}
        """

        # Call the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a financial analyst specializing in DeFi investments."},
                          {"role": "user", "content": prompt}],
                max_tokens=300
            )
            rebalancing_instructions = response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error in AI response: {str(e)}"

        return rebalancing_instructions  # Return the rebalancing instructions