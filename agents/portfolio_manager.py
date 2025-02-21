from openai import OpenAI
import pandas as pd
from config import OPENAI_API_KEY
from agents.data_analyst import DataAnalystAgent
from agents.fetch_market_data import MarketData
import os
import json
from typing import Dict, List, Union

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class PortfolioManagerAgent:
    def __init__(self, market_data: MarketData, wallet_data_file=None):
        if wallet_data_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            wallet_data_file = os.path.join(base_dir, "data", "wallet_data", "current_wallet.csv")
        
        self.market_data = market_data
        self.wallet_data_file = wallet_data_file
        self.data_analyst = DataAnalystAgent(market_data)

    def analyze_market(self) -> Dict[str, Union[str, Dict]]:
        # Use DataAnalystAgent to get the analysis result
        analysis_result = self.data_analyst.analyze_market()
        if "error" in analysis_result:
            return analysis_result

        # Load current wallet data from CSV
        try:
            wallet_data = pd.read_csv(self.wallet_data_file)
            if wallet_data.empty:
                return {"error": "Wallet data file is empty"}
        except FileNotFoundError:
            return {"error": "Wallet data file not found"}
        except pd.errors.EmptyDataError:
            return {"error": "Wallet data file is empty"}
        except Exception as e:
            return {"error": f"Error reading wallet data: {str(e)}"}

        # Prepare the prompt for the LLM
        prompt = f"""Based on the market analysis and current wallet data, provide specific rebalancing instructions in a structured format that can be executed as code.

Market Analysis:
{analysis_result}

Current Wallet Summary:
{wallet_data}

Please provide your response in the following JSON format:
{{
    "rebalancing_instructions": {{
        "trades": [
            {{
                "action": "buy" or "sell",
                "asset": "asset_name",
                "amount": float,  # Amount in USD
                "target_percentage": float,  # Target allocation percentage
                "current_percentage": float,  # Current allocation percentage
                "reason": "string explaining the trade"
            }}
        ],
        "risk_level": "low" or "moderate" or "high",
        "total_portfolio_value": float,  # Total portfolio value in USD
        "expected_annual_yield": float,  # Expected annual yield as percentage
        "execution_priority": "immediate" or "staged",  # Whether to execute all trades at once or in stages
        "market_conditions": "string describing current market conditions"
    }}
}}

Ensure all numbers are realistic and the trades balance to 100% allocation."""

        # Call the OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial advisor specializing in portfolio rebalancing. Always return valid JSON that matches the specified format exactly."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1000,
            )
            
            # Parse the response as JSON
            try:
                rebalancing_instructions = json.loads(response.choices[0].message.content)
                
                # Add a human-readable summary
                summary = self._generate_summary(rebalancing_instructions)
                
                return {
                    "result": {
                        "instructions": rebalancing_instructions,
                        "summary": summary
                    }
                }
            except json.JSONDecodeError as e:
                return {"error": f"Failed to parse AI response as JSON: {str(e)}"}
                
        except Exception as e:
            return {"error": f"Error in AI response: {str(e)}"}

    def _generate_summary(self, instructions: Dict) -> str:
        """Generate a human-readable summary of the rebalancing instructions."""
        rebal = instructions.get('rebalancing_instructions', {})
        trades = rebal.get('trades', [])
        
        summary = []
        summary.append(f"Portfolio Rebalancing Summary:")
        summary.append(f"Risk Level: {rebal.get('risk_level', 'N/A')}")
        summary.append(f"Total Portfolio Value: ${rebal.get('total_portfolio_value', 0):,.2f}")
        summary.append(f"Expected Annual Yield: {rebal.get('expected_annual_yield', 0):.2f}%")
        summary.append(f"Execution Priority: {rebal.get('execution_priority', 'N/A')}")
        summary.append("\nRequired Trades:")
        
        for trade in trades:
            summary.append(
                f"• {trade['action'].upper()} {trade['asset']}: ${trade['amount']:,.2f} "
                f"(Current: {trade['current_percentage']:.1f}% → Target: {trade['target_percentage']:.1f}%)"
            )
        
        summary.append(f"\nMarket Conditions: {rebal.get('market_conditions', 'N/A')}")
        
        return "\n".join(summary)