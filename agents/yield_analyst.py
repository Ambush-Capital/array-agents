from typing import Dict, Any, Optional, List
import logging
import json
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from agents.base_agent import BaseAgent
from models.market_model import MarketData, LendingReserve
# from tools.fetch_market_data import MarketDataKnowledgeSource

class YieldAnalyst(BaseAgent):
    """
    Agent responsible for analyzing yield opportunities in DeFi lending markets.
    """
    
    def __init__(
        self,
        agent_id: str = "yield_analyst",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the YieldAnalyst agent."""
        role = "DeFi Lending Yield Analyst"
        goal = "Analyze the Market Data to identify optimal lending opportunities by comparing risk-adjusted returns. Create detailed recommendations based on analysis."
        backstory = """You're a meticulous analyst with a keen eye for detail. You're known for
                    your ability to turn complex data into clear and concise reports and recommendations, 
                    making it easy for others to understand and act on the information you provide. Never proceed 
                    with analysis without consulting the market data through the provided tool."""
                    
        # knowledge_sources = ["MarketDataKnowledgeSource"]
        
        super().__init__(
            agent_id=agent_id,
            role=role,
            goal=goal,
            backstory=backstory,
            # knowledge_sources=knowledge_sources,
            config=config
        )
    
    def execute_task(self, market_data: Any) -> Dict[str, Any]:
        """
        Execute yield analysis tasks.
        
        Args:
            task_input: Dictionary containing task parameters
                - "task_type": Type of analysis task
                - "market_data_path": Path to market data file
                - "wallet_data_path": Optional path to wallet data file
                - "output_format": Format of the output (markdown, json)
                - "output_path": Path to save the output
                
        Returns:
            Dictionary with task results or error information
        """
        # task_type = task_input.get("task_type", "yield_analysis")

        # if task_type == "yield_analysis":
        print("Vibing on some numbers, back in a flash with your results")
        analysis_results = self._analyze_yields(market_data)
        yield_strategy_results = self._create_strategy(analysis_results, market_data)
        return (analysis_results, yield_strategy_results)
        # return (analysis_results)
        # elif task_type == "yield_strategy":
        #     return self._generate_yield_strategy(task_input)
        # else:
        #     return {
        #         "error": f"Unknown task type: {task_type}",
        #         "status": "failed"
        #     }
    
    
    def _analyze_yields(self, market_data: Any) -> Dict[str, Any]:
        """Analyze yields from market data and return results in markdown format."""
        try:
            # Convert market data to JSON string
            market_data_json = json.dumps(market_data, default=str)
            # Perform yield analysis
            
            # Create a detailed prompt for the analysis task
            analysis_prompt = f"""
Task: Perform a comprehensive yield analysis on the provided DeFi lending market data.

Expected output:
1. A table, organized by Current Supply Rate (%), from highest to lowest. The columns in the table include:
- Protocol
- Market Name
- Total Supply
- Total Borrows
- Utilization % (calculated from Total Borrows / Total Supply)
- Current Supply Rate (%)
- 7d Avg Supply Rate (%) - where available
- 30d Avg Supply Rate (%) - where available

2. Your top 3 recommended yield opportunities across all protocols and assets
3. Comparative analysis of different protocols (SAVE/Solend, Marginfi, Kamino, Drift)
4. Anomalies or unusual patterns in the current market (utilize the 7d and 30d averages)

Format your response as a detailed markdown report with appropriate sections, tables, and bullet points. Do not make any information up that you do not know.
Include clear recommendations based on your analysis.

Do not make up any information that you do not have

Market Data: {market_data_json}
"""
            
            # Call the LLM with the persona-enriched prompt
            analysis_results = self.call_llm(analysis_prompt)
        except Exception as e:
            self.logger.exception(f"Error analyzing yields: {str(e)}")
            return {
                "error": f"Error analyzing yields: {str(e)}",
                "status": "failed"
            }
        
        return analysis_results

    def _create_strategy(self, analysis_results: Any, market_data: Any) -> Dict[str, Any]:
        """Generate yield strategy using market data and analysis results in markdown."""
        try:
            # Convert market data and analysis results to JSON strings
            market_data_json = json.dumps(market_data, default=str)
            # Use analysis_results directly as it's already a string
            # Perform yield strategy generation
            # Create detailed prompt for the strategy generation task
            yield_strategy_prompt = f"""
Task: Generate a recommended allocation strategy to maximize yield based on the given analysis results and market data.

Expected output: A table with the recommended positions and their expected returns. The columns should include:
- Protocol
- Market Name
- Allocation percentage
- Expected yield
- Rationale

Do not make any information up that you do not know.

Analysis Results: {analysis_results}
Market Data: {market_data_json}
"""
            # Call the LLM with the persona-enriched prompt
            yield_strategy = self.call_llm(yield_strategy_prompt)
        except Exception as e:
            self.logger.exception(f"Error generating yield strategy: {str(e)}")
            return {
                "error": f"Error generating yield strategy: {str(e)}",
                "status": "failed"
            }
        
        return yield_strategy

#     def _calculate_expected_yield(
#         self, 
#         positions: List[Dict[str, Any]], 
#         yield_data: List[Dict[str, Any]]
#     ) -> float:
#         """Calculate the expected yield for a set of positions."""
#         if not positions:
#             return 0.0
            
#         total_amount = sum(float(pos["amount"]) for pos in positions)
#         if total_amount == 0:
#             return 0.0
            
#         weighted_yield = 0.0
        
#         for position in positions:
#             # Find the yield data for this position
#             for yield_info in yield_data:
#                 if (yield_info["protocol"] == position["protocol_name"] and 
#                     yield_info["market"] == position["market_name"]):
                    
#                     amount = float(position["amount"])
#                     weight = amount / total_amount
#                     weighted_yield += weight * yield_info["supply_rate"]
#                     break
        
#         return round(weighted_yield, 2)
    
#     def _calculate_yield_increase(
#         self, 
#         wallet_data: Dict[str, Any], 
#         ideal_positions: List[Dict[str, Any]], 
#         yield_data: List[Dict[str, Any]]
#     ) -> float:
#         """Calculate the potential yield increase from current to ideal positions."""
#         # Calculate current yield
#         current_positions = wallet_data.get("wallet_positions", [])
#         current_yield = 0.0
        
#         if current_positions:
#             total_current_amount = sum(float(pos["amount"]) for pos in current_positions)
            
#             if total_current_amount > 0:
#                 for position in current_positions:
#                     # Find the yield data for this position
#                     for yield_info in yield_data:
#                         if (yield_info["protocol"] == position["protocol_name"] and 
#                             yield_info["market"] == position["market_name"]):
                            
#                             amount = float(position["amount"])
#                             weight = amount / total_current_amount
#                             current_yield += weight * yield_info["supply_rate"]
#                             break
        
#         # Calculate ideal yield
#         ideal_yield = self._calculate_expected_yield(ideal_positions, yield_data)
        
#         # Calculate increase
#         yield_increase = ideal_yield - current_yield
        
#         return round(yield_increase, 2)
    
#     def _format_yield_analysis_as_markdown(self, analysis: Dict[str, Any]) -> str:
#         """Format yield analysis results as markdown."""
#         md = "# DeFi Lending Yield Analysis\n\n"
        
#         # Best Yields Section
#         md += "## Top Yield Opportunities\n\n"
#         md += "| Token | Protocol | Market | Supply Rate | Utilization | Trend |\n"
#         md += "| ----- | -------- | ------ | ----------- | ----------- | ----- |\n"
        
#         for yield_info in analysis["best_yields"]:
#             trend = yield_info.get("trend", "N/A")
#             trend_icon = "→" if trend == "stable" else "↑" if trend == "up" else "↓" if trend == "down" else ""
#             md += f"| {yield_info['token']} | {yield_info['protocol']} | {yield_info['market']} | "
#             md += f"{yield_info['supply_rate']}% | {yield_info['utilization']}% | {trend} {trend_icon} |\n"
        
#         md += "\n"
        
#         # Protocol Comparison Section
#         md += "## Protocol Comparison\n\n"
#         md += "| Protocol | Avg Yield | Max Yield | Min Yield | Avg Utilization | Markets |\n"
#         md += "| -------- | --------- | --------- | --------- | --------------- | ------- |\n"
        
#         for protocol, data in analysis["protocol_comparison"].items():
#             md += f"| {protocol} | {data['avg_yield']}% | {data['max_yield']}% | "
#             md += f"{data['min_yield']}% | {data['avg_utilization']}% | {data['market_count']} |\n"
        
#         md += "\n"
        
#         # Market Insights Section
#         md += "## Market Insights\n\n"
        
#         for insight in analysis["market_insights"]:
#             md += f"- {insight}\n"
        
#         return md
    
#     def _format_strategy_as_markdown(self, strategy: Dict[str, Any]) -> str:
#         """Format yield strategy as markdown."""
#         md = "# DeFi Lending Yield Strategy\n\n"
        
#         md += f"**Total Portfolio Value:** ${strategy.get('total_portfolio_value', '0.00')}\n"
#         md += f"**Expected Average Yield:** {strategy.get('expected_avg_yield', '0.00')}%\n"
#         md += f"**Potential Yield Increase:** {strategy.get('yield_increase', '0.00')}%\n\n"
        
#         md += "## Recommended Positions\n\n"
#         md += "| Token | Protocol | Market | Amount | % of Portfolio |\n"
#         md += "| ----- | -------- | ------ | ------ | -------------- |\n"
        
#         ideal_positions = strategy.get("ideal_positions", [])
#         total_amount = sum(float(pos["amount"]) for pos in ideal_positions) if ideal_positions else 0
        
#         for position in ideal_positions:
#             amount = float(position["amount"])
#             total_portfolio_value = float(strategy.get("total_portfolio_value", "0"))
#             percentage = (amount / total_portfolio_value) * 100 if total_portfolio_value > 0 else 0
            
#             md += f"| {position['symbol']} | {position['protocol_name']} | {position['market_name']} | "
#             md += f"${amount:.2f} | {percentage:.2f}% |\n"
        
#         md += "\n"
        
#         md += "## Action Required\n\n"
#         md += f"**Rebalancing Required:** {'Yes' if strategy.get('rebalancing_required', False) else 'No'}\n\n"
        
#         return md

# if __name__ == '__main__':
#     # Standalone execution of YieldAnalyst for testing purposes
#     # Import YieldAnalyst from the current module if not already imported
#     from agents.yield_analyst import YieldAnalyst

#     # Instantiate the analyst
#     analyst = YieldAnalyst()

#     # Create a dummy strategy dictionary to test the _format_strategy_as_markdown method
#     dummy_strategy = {
#         'name': 'Test Strategy',
#         'details': 'This is a test strategy used for standalone execution.',
#         'total_portfolio_value': '1000.00',
#         'expected_avg_yield': '5.25',
#         'yield_increase': '1.75',
#         'ideal_positions': [
#             {
#                 'symbol': 'USDC',
#                 'protocol_name': 'Solend',
#                 'market_name': 'Main Pool',
#                 'amount': '500.00'
#             }
#         ],
#         'rebalancing_required': True
#     }

#     # Call the method to format the strategy, and print the result
#     formatted_strategy = analyst._format_strategy_as_markdown(dummy_strategy)
#     print('Formatted Strategy:')
#     print(formatted_strategy)