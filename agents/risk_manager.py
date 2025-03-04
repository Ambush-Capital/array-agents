from typing import Dict, Any, Optional, List
import json
import logging
import os
from pathlib import Path
from decimal import Decimal

from agents.base_agent import BaseAgent

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
        
        knowledge_sources = ["MarketDataKnowledgeSource", "WalletDataKnowledgeSource"]
        
        super().__init__(
            agent_id=agent_id,
            role=role,
            goal=goal,
            backstory=backstory,
            knowledge_sources=knowledge_sources,
            config=config
        )
        
        self.market_data_path = config.get("market_data_path")
        self.wallet_data_path = config.get("wallet_data_path")
        
    def load_market_data(self, path):
        """Load market data from the given path. Expected to be in JSON format."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def load_wallet_data(self, path):
        """Load wallet data from the given path. Expected to be in JSON format."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute risk assessment tasks.
        
        Args:
            task_input: Dictionary containing task parameters
                - "task_type": Type of risk task
                - "output_format": Format of the output (markdown, json)
                - "output_path": Path to save the output
                
        Returns:
            Dictionary with task results or error information
        """
        task_type = task_input.get("task_type", "risk_assessment")
        
        if task_type == "risk_assessment":
            return self._assess_risks(task_input)
        elif task_type == "risk_adjusted_strategy":
            return self._generate_risk_adjusted_strategy(task_input)
        else:
            return {
                "error": f"Unknown task type: {task_type}",
                "status": "failed"
            }
    
    def _assess_risks(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks based on market data and wallet data."""
        output_format = task_input.get("output_format", "markdown")
        
        try:
            # Load market data
            market_data = self.load_market_data(self.market_data_path)
            
            # Load wallet data
            wallet_data = self.load_wallet_data(self.wallet_data_path)
            
            # Perform risk assessment
            assessment = self._perform_risk_assessment(
                market_data,
                wallet_data
            )
            
            # Format the assessment based on the requested format
            if output_format == "markdown":
                formatted_assessment = self._format_assessment_as_markdown(assessment)
            else:
                formatted_assessment = assessment
            
            # Save the assessment if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(formatted_assessment, output_path)
            
            return {
                "status": "success",
                "data": formatted_assessment,
                "message": "Risk assessment completed successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error assessing risks: {str(e)}")
            return {
                "error": f"Error assessing risks: {str(e)}",
                "status": "failed"
            }
    
    def _generate_risk_adjusted_strategy(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a risk-adjusted strategy based on yield strategy and risk assessment."""
        output_format = task_input.get("output_format", "json")
        
        try:
            # Load market data
            market_data = self.load_market_data(self.market_data_path)
            
            # Load wallet data
            wallet_data = self.load_wallet_data(self.wallet_data_path)
            
            # Load yield strategy
            yield_strategy_path = task_input.get("yield_strategy_path")
            try:
                with open(yield_strategy_path, 'r') as f:
                    yield_strategy = json.load(f)
            except Exception as e:
                return {
                    "error": f"Error loading yield strategy: {str(e)}",
                    "status": "failed"
                }
            
            # Generate risk-adjusted strategy
            adjusted_strategy = self._adjust_strategy_for_risk(
                market_data,
                wallet_data,
                yield_strategy
            )
            
            # Format the strategy based on the requested format
            if output_format == "markdown":
                formatted_strategy = self._format_strategy_as_markdown(adjusted_strategy)
            else:
                formatted_strategy = adjusted_strategy
            
            # Save the strategy if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(formatted_strategy, output_path)
            
            return {
                "status": "success",
                "data": formatted_strategy,
                "message": "Risk-adjusted strategy generated successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error generating risk-adjusted strategy: {str(e)}")
            return {
                "error": f"Error generating risk-adjusted strategy: {str(e)}",
                "status": "failed"
            }
    
    def _perform_risk_assessment(
        self, 
        market_data: Dict[str, Any], 
        wallet_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform risk assessment on market data and wallet data.
        
        In a real implementation, this would involve complex risk modeling.
        For demonstration, we'll implement a simplified version.
        """
        assessment = {
            "overall_risk_level": "medium",
            "protocol_risks": {},
            "concentration_risk": {},
            "utilization_risks": [],
            "recommendations": []
        }
        
        # Get current allocations
        allocations = self._calculate_allocations(wallet_data)
        
        # Assess protocol risks
        protocols = set()
        for token_data in market_data:
            for reserve in token_data.get("lending_reserves", []):
                protocols.add(reserve["protocol_name"])
        
        for protocol in protocols:
            assessment["protocol_risks"][protocol] = self._assess_protocol_risk(protocol, market_data)
        
        # Assess concentration risk
        assessment["concentration_risk"] = self._assess_concentration_risk(allocations)
        
        # Assess utilization risks
        assessment["utilization_risks"] = self._assess_utilization_risk(market_data)
        
        # Generate recommendations
        assessment["recommendations"] = self._generate_risk_recommendations(
            assessment, allocations
        )
        
        return assessment
    
    def _calculate_allocations(self, wallet_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate current allocations by protocol."""
        allocations = {}
        total_value = 0
        
        # Sum up the total value
        for position in wallet_data.get("wallet_positions", []):
            protocol = position["protocol_name"]
            amount = float(position["amount"])
            
            if protocol not in allocations:
                allocations[protocol] = 0
            
            allocations[protocol] += amount
            total_value += amount
            
        for balance in wallet_data.get("wallet_balances", []):
            amount = float(balance["amount"])
            total_value += amount
            
            if "Unallocated" not in allocations:
                allocations["Unallocated"] = 0
            
            allocations["Unallocated"] += amount
            
        # Normalize allocations
        for protocol, amount in allocations.items():
            allocations[protocol] = amount / total_value
            
        return allocations