from datetime import datetime
import json
from typing import Dict, Any, Optional

import openai
from openai import OpenAI

from agents.base_agent import BaseAgent
from config.risk_parameters import risk_parameters, operational_rules

class RiskManager(BaseAgent):
    """
    Agent responsible for evaluating risks associated with DeFi lending markets
    and proposing risk-mitigation strategies.
    """
    
    def __init__(
        self,
        agent_id: str = "risk_manager",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the RiskManager agent."""
        role = "DeFi Lending Market Risk Manager"
        goal = "Evaluate risks associated with Solana lending pools DeFi lending markets, current exposure and market analysis to propose rebalancing actions or hedging strategies"
        backstory = """You're an expert risk manager with a thorough approach to assessing the risk levels of 
                     various DeFi lending markets and asset pools. You have a deep understanding of the risks 
                     associated with each market and can provide insights that help the Portfolio Manager make 
                     informed decisions based on the stated risk tolerance and predefined risk parameters. You have
                     created risk scoring that accounts for protocol-specific vulnerabilities. Your analysis should begin
                     by reviewing the current wallet data through the provided tool."""
        
        super().__init__(
            agent_id=agent_id,
            role=role,
            goal=goal,
            backstory=backstory,
            config=config
        )
        

    def execute_task(self, market_data: Any, wallet_data: Any, risk_tolerance_input: str, yield_strategy_results: Any) -> Dict[str, Any]:
        """
        Execute risk assessment tasks.
        
        Args:
            market_data: Market data
            wallet_data: Wallet data
            risk_tolerance_input: User's risk tolerance level
            
        Returns:
            Dictionary with task results or error information
        """
        print("Checking your risk levels, hang tight...")
        analysis_results = self._analyze_wallet(market_data, wallet_data, risk_tolerance_input, yield_strategy_results)
        return analysis_results
        
    def _analyze_wallet(self, market_data: Any, wallet_data: Any, risk_tolerance_input: str, yield_strategy_results: Any) -> Dict[str, Any]:
        """Analyze wallet data and return results in markdown format."""
        try:
            # Convert wallet and market data to JSON string
            wallet_data_json = json.dumps(wallet_data, default=str)
            market_data_json = json.dumps(market_data, default=str)

            # Perform wallet analysis
            
            # Create a detailed prompt for the analysis task
            analysis_prompt = f"""
Tasks:
1. Analyze the wallet data and provide the following table of current positions:
- Protocol
- Market Name
- Amount (USDC)
- Allocation %
- Obligation Type
2. Review the current wallet positions and recommended yield strategy for compliance with the risk tolerance of the user and associated risk parameters
3. Review the current wallet positions and recommended yield strategy for compliance with the operational rules

Format your response as a detailed markdown report with appropriate sections, tables, and bullet points.
Include clear recommendations based on your analysis.

Wallet Data: {wallet_data_json}
Market Data: {market_data_json}
Risk Tolerance: {risk_tolerance_input}
Risk Parameters: {risk_parameters}
Operational Rules: {operational_rules}
Recommended Yield Strategy: {yield_strategy_results}
"""
            
            # Call the LLM with the persona-enriched prompt
            analysis_results = self.call_llm(analysis_prompt)
        except Exception as e:
            self.logger.exception(f"Error analyzing wallet: {str(e)}")
            return {
                "error": f"Error analyzing wallet: {str(e)}",
                "status": "failed"
            }
        
        return analysis_results