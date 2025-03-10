from datetime import datetime
import json
from typing import Dict, Any, Optional

import openai
from openai import OpenAI

from agents.base_agent import BaseAgent

class ExecutionAgent(BaseAgent):
    """
    Agent responsible for creating executable trade instructions for various lending protocols.
    Optimizes transaction execution for gas usage, fees, slippage, and timing.
    """
    
    def __init__(
        self,
        agent_id: str = "execution_agent",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the ExecutionAgent."""
        role = "DeFi Lending Transaction Expert"
        goal = "Create executable trade instructions for the various lending protocols"
        backstory = """You're a solana protocol expert with a deep understanding of transaction execution
                    and optimization around gas usage, fees, slippage and timing. You have experience with deposits,
                    withdrawls, borrows, and repayments. You have expertise in the various lending protocols and can provide 
                    trade instructions based on the Portfolio Managers instruction. You also implement MEV protection strategies"""
        
        super().__init__(
            agent_id=agent_id,
            role=role,
            goal=goal,
            backstory=backstory,
            config=config
        )
    
    def execute_task(self, wallet_data: Any, final_recc_to_execute: Any) -> Dict[str, Any]:
        """
        Execute tasks related to transaction planning and optimization.
        
        Args:
            wallet_data: Dictionary containing wallet data
            final_recc_to_execute: Dictionary containing final reccomendation
                
        Returns:
            Dictionary with task results or error information
        """
        print("Creating execution instructions, hang tight...")
        execution_plan = self._create_execution_plan(wallet_data, final_recc_to_execute)
        return execution_plan
    
    def _create_execution_plan(self, wallet_data: Any, final_recc_to_execute: Any) -> Dict[str, Any]:
        try:
            # Convert wallet and market data to JSON string
            wallet_data_json = json.dumps(wallet_data, default=str)
            final_recc_to_execute_json = json.dumps(final_recc_to_execute, default=str)

            # Create a detailed prompt for the analysis task
            analysis_prompt = f"""
You have the current wallet data of a portfolio and the final reccomendation for a new portfolio. Your task is to create executable trade instructions to rebalance the portfolio to the final reccomendation.

Example: If the current wallet has 100 USDC in a certain market and the final reccomendation is 200 USDC, you would create a deposit instruction for 100 USDC to the market.

Provide the trade instructions in JSON format. Do not include any analysis or explanation.
Rules:
1. You should never withdraw and deposit from the same market
2. Ensure all assets in wallet are allocated to a yield opportunity
Check your work to ensure it is consistent with the provided final reccomendation.


Current Wallet Data:
{wallet_data_json}

Final Reccomendation:
{final_recc_to_execute_json}
"""
            
            # Call the LLM with the persona-enriched prompt
            execution_plan = self.call_llm(analysis_prompt)
        except Exception as e:
            self.logger.exception(f"Error creating execution plan: {str(e)}")
            return {
                "error": f"Error creating execution plan: {str(e)}",
                "status": "failed"
            }
        
        return execution_plan