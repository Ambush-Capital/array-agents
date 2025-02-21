from openai import OpenAI
import pandas as pd
import os
from config import OPENAI_API_KEY
from .fetch_market_data import MarketData
from dataclasses import dataclass
from typing import Dict, Union, List, Optional
import json

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class DataAnalystAgent:
    def __init__(self, market_data=None):
        if market_data is None:
            market_data = MarketData()
        self.market_data = market_data

    def analyze_market(self):
        # Get market data from MarketData object
        try:
            data = self.market_data.get_market_data()
            if data is None:
                return {"error": "No market data available"}
            
            market_data = pd.DataFrame(data)
            if market_data.empty:
                return {"error": "Market data is empty"}
        except Exception as e:
            return {"error": f"Error processing market data: {str(e)}"}

        # Prepare the prompt for the LLM
        prompt = f"""You are a financial data analyst, specializing in yield optimization. Analyze the following market data, with a particular focus on supply rate, and provide specific allocation recommendations for a $10,000 portfolio with high risk:
Context: 

Market Data Summary:
{data}

Please provide:
1. Specific allocation amounts for different protocols
2. Expected yield/returns
3. Risk assessment for each recommendation
4. Any relevant market conditions affecting the decision
"""
        # Call the OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in DeFi investments."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return {"error": f"Error calling OpenAI API: {str(e)}"}