from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path
from decimal import Decimal

from agents.base_agent import BaseAgent
from config.risk_parameters import risk_parameters, operational_rules

class PortfolioManager(BaseAgent):
    """
    Agent responsible for portfolio optimization and management.
    """
    
    def __init__(
        self,
        agent_id: str = "portfolio_manager",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the PortfolioManager agent."""
        role = "DeFi Lending Portfolio Manager"
        goal = "Continuously adjust asset allocation among various lending markets to maximize yield based on real-time yield and risk data."
        backstory = """You're a seasoned portfolio manager with a deep understanding of the complex inputs required to 
                   optimize a DeFi lending portfolio. You can understand and synthesize inputs from your team and various
                   sources to make informed decisions on asset allocation and risk management. You have a deep perspective
                   around rebalancing thresholds based on risk and volatility, position sizing and diversification rules.
                   You have created a portfolio optimization model that can be used to generate trade recommendations."""
        
        super().__init__(
            agent_id=agent_id,
            role=role,
            goal=goal,
            backstory=backstory,
            config=config
        )
    
    def execute_task(self, market_data: Any, wallet_data: Any, yield_strategy_results: Any, yield_analysis_results: Any, risk_analysis_results: Any, risk_tolerance_input: str) -> Dict[str, Any]:
        """
        Execute portfolio management tasks.
        
        Args:
            market_data: Market data
            wallet_data: Wallet data
            yield_strategy_results: Yield strategy results
            risk_tolerance_input: User's risk tolerance level
            
        Returns:
            Dictionary with task results or error information
        """
        print("Developing your final recommendation")
        optimized_portfolio = self._optimize_portfolio(market_data, wallet_data, yield_strategy_results, yield_analysis_results, risk_analysis_results, risk_tolerance_input)
        final_recc_to_execute = self._generate_final_recc(optimized_portfolio)
        return (optimized_portfolio, final_recc_to_execute)
        
    def _optimize_portfolio(self, market_data: Any, wallet_data: Any, yield_analysis_results: Any, yield_strategy_results: Any, risk_analysis_results: Any, risk_tolerance_input: str) -> Dict[str, Any]:
        """
        Optimize portfolio allocation based on yield and risk analysis.
        
        This combines yield strategy and risk-adjusted strategy to create
        a final optimization recommendation.
        """
        
        # Convert wallet and market data to JSON string
        market_data_json = json.dumps(market_data, default=str)
        wallet_data_json = json.dumps(wallet_data, default=str)
        
        # Create a detailed prompt for the optimization task
        optimization_prompt = f"""
Task: Analyze all of the data provided and make a final recommendation to optimize the portfolio allocation based on yield and risk analysis. 
Do not make any information up that you do not have available to you.

Here are the data sources to consider that have been provided by your Yield Analyst and Risk Manager:
1. Market Data: {market_data_json}
2. Wallet Data: {wallet_data_json}
3. Yield Analysis Results: {yield_analysis_results}
4. Yield Strategy Results: {yield_strategy_results}
5. Risk Analysis Results: {risk_analysis_results}
6. Risk Tolerance: {risk_tolerance_input}
7. Risk Parameters: {risk_parameters}
8. Operational Rules: {operational_rules}

Format your response as a detailed markdown report with appropriate sections, tables, and bullet points.
Include clear recommendations based on your analysis.
"""
        
        # Call the LLM with the persona-enriched prompt
        optimized_portfolio = self.call_llm(optimization_prompt)
        return optimized_portfolio
 
    def _generate_final_recc(self, optimized_portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a final reccomdation, without any analysis provided to pass to the execution agent
        """
        
        # Create a detailed prompt for the final reccomendation task
        final_recc_prompt = f"""
You have just reviewed the optimized portfolio allocation based on yield and risk analysis. You have provided a 
final recommendation in your {optimized_portfolio}. Strip out all analysis from that response and provide only the final reccomendation.

The final recommendation consists of a JSON object with the following components:
1. Protocol Name
2. Market Name
3. Amount (USDC)
4. Obligation Type

Check your final reccomendation to ensure it is consistent with the provided optimized portfolio allocation.
Do not provide any extraneous details or explanations
"""
        
        # Call the LLM with the persona-enriched prompt
        final_recc_to_execute = self.call_llm(final_recc_prompt)
        return final_recc_to_execute