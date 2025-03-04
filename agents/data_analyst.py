from openai import OpenAI
import pandas as pd
import os
from config import OPENAI_API_KEY
from .fetch_market_data import MarketData
from dataclasses import dataclass
from typing import Dict, Union, List, Optional
import json

# Define the StaticContext class with risk parameters and operational rules.
class StaticContext:
    def __init__(self):
        self.risk_parameters = {
            "max_exposure_risk_low": 0.2,  # Max exposure per protocol as a fraction of total assets in low risk
            "max_exposure_risk_medium": 0.4,  # Max exposure per protocol as a fraction of total assets in medium risk
            "max_exposure_risk_high": 0.6,  # Max exposure per protocol as a fraction of total assets in high risk
            "current_risk": "high"  # Current risk level
        }
        self.operational_rules = {
            "min_yield": 4.0,         # Minimum acceptable yield percentage
            "max_positions": 5.0,     # Maximum number of positions > $1000
            "min_position_size": 1.0  # Rule to not close a position
        }

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

        static_context = StaticContext()
        static_context_text = (
            "Static Context:\n"
            "Risk Parameters:\n"
            f"  - Low Risk Max Exposure: {static_context.risk_parameters['max_exposure_risk_low']}\n"
            f"  - Medium Risk Max Exposure: {static_context.risk_parameters['max_exposure_risk_medium']}\n"
            f"  - High Risk Max Exposure: {static_context.risk_parameters['max_exposure_risk_high']}\n\n"
            f"  - Current Risk Level: {static_context.risk_parameters['current_risk']}\n"
            "Operational Rules:\n"
            f"  - Minimum Yield: {static_context.operational_rules['min_yield']}\n"
            f"  - Maximum Positions: {static_context.operational_rules['max_positions']}\n"
            f"  - Minimum Position Size: {static_context.operational_rules['min_position_size']}\n"
        )

        # Step 1: Internal Calculation Prompt (do not output chain-of-thought)
        prompt = f"""
You are a financial data analyst specializing in maximizing yield earned on Solana lending protocols, based on a certain risk tolerance and current market data provided below. 'supply_rate' is where you will see the yield percentage. In your analysis, consider the following static context:
{static_context_text}

Portfolio size: $10,000
Risk tolerance: {static_context.risk_parameters['current_risk']}
Market data: {data}

Perform a detailed analysis and calculations to provide a final, synthesized recommendation that includes:
1. Specific allocation amounts for different protocols, keeping in mind that the recommendation for certain protocols may be $0.
2. A risk assessment for each recommendation.
3. Any relevant market conditions that may affect the decision.

IMPORTANT: Double-check your math carefully. Document your internal chain-of-thought and calculations, but do not include these details in your output. Once you have verified the numbers, store the results for the next step.
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
            return {"error": f"Error during final recommendation: {str(e)}"}