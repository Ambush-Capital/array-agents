from typing import Dict, Any, Optional, List
import requests
import json
import logging
from pathlib import Path
from datetime import datetime
import os

from agents.base_agent import BaseAgent
from models.market_model import MarketDataManager
from tools.fetch_market_data import MarketDataKnowledgeSource
from tools.fetch_wallet_data import WalletDataKnowledgeSource

class DataAggregator(BaseAgent):
    """
    Agent responsible for collecting data required for portfolio optimization,
    including market data and wallet data.
    """
    
    def __init__(
        self,
        agent_id: str = "data_aggregator",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the DataAggregator agent."""
        role = "DeFi Lending Data Aggregator"
        goal = "Collect data required to make a detailed portfolio recommendation to optimize yield including: current lending market data, historical data, reporting, risk metrics, and wallet data"
        backstory = """You're a meticulous analyst with a keen eye for detail. You're known for
                   your ability to turn complex data into clear and concise reports, making
                   it easy for others to understand and act on the information you provide."""
        
        tools = ["fetch_market_data", "fetch_wallet_data"]
        
        super().__init__(
            agent_id=agent_id,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            config=config
        )
        
        self.market_data_manager = MarketDataManager()
    
    def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tasks for aggregating various types of data.
        
        Args:
            task_input: Dictionary containing task parameters
                Required keys depend on the task:
                - For market data: "api_url"
                - For wallet data: "wallet_address"
                
        Returns:
            Dictionary with task results or error information
        """
        task_type = task_input.get("task_type")
        
        if task_type == "fetch_market_data":
            return self._fetch_market_data(task_input)
        elif task_type == "fetch_wallet_data":
            return self._fetch_wallet_data(task_input)
        elif task_type == "aggregate_all_data":
            return self._aggregate_all_data(task_input)
        else:
            return {
                "error": f"Unknown task type: {task_type}",
                "status": "failed"
            }
    
    def _fetch_market_data(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch market data using MarketDataKnowledgeSource and save it."""
        market_tool = MarketDataKnowledgeSource()
        market_data = market_tool.fetch_market_data()

        market_data_path = self.config.get('market_data_path', os.path.join('data', 'market_data.json'))
        os.makedirs(os.path.dirname(market_data_path), exist_ok=True)

        with open(market_data_path, 'w') as f:
            f.write(market_data)

        return {
            'market_data_path': market_data_path,
            'timestamp': datetime.now().isoformat()
        }

    def _fetch_wallet_data(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch wallet data using WalletDataKnowledgeSource and save it."""
        wallet_tool = WalletDataKnowledgeSource()
        wallet_data = wallet_tool.fetch_wallet_data()

        wallet_data_path = self.config.get('wallet_data_path', os.path.join('data', 'wallet_data.json'))
        os.makedirs(os.path.dirname(wallet_data_path), exist_ok=True)

        with open(wallet_data_path, 'w') as f:
            f.write(wallet_data)

        return {
            'wallet_data_path': wallet_data_path,
            'timestamp': datetime.now().isoformat()
        }
    
    def _aggregate_all_data(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch and aggregate all required data for portfolio optimization.
        This combines market data, wallet data, and any other relevant information.
        """
        api_url = task_input.get("api_url")
        wallet_address = task_input.get("wallet_address")
        output_dir = task_input.get("output_dir", "data")
        
        if not api_url:
            return {
                "error": "API URL is required for aggregating data",
                "status": "failed"
            }
        
        if not wallet_address:
            return {
                "error": "Wallet address is required for aggregating data",
                "status": "failed"
            }
        
        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            market_data_path = f"{output_dir}/market_data.json"
            wallet_data_path = f"{output_dir}/wallet_data.json"
            
            # Fetch market data
            market_result = self._fetch_market_data({
                "api_url": api_url,
                "output_path": market_data_path
            })
            
            if "error" in market_result:
                return market_result
            
            # Fetch wallet data
            wallet_result = self._fetch_wallet_data({
                "wallet_address": wallet_address,
                "output_path": wallet_data_path
            })
            
            if "error" in wallet_result:
                return wallet_result
            
            # Combine the data into a consolidated report
            aggregated_data = {
                "market_data": market_result["data"],
                "wallet_data": wallet_result["data"],
                "timestamp": task_input.get("timestamp", "")
            }
            
            # Save the aggregated data
            aggregated_path = f"{output_dir}/aggregated_data.json"
            with open(aggregated_path, 'w') as f:
                json.dump(aggregated_data, f, indent=2)
            
            return {
                "status": "success",
                "data": {
                    "market_data_path": market_data_path,
                    "wallet_data_path": wallet_data_path,
                    "aggregated_data_path": aggregated_path
                },
                "message": "All data successfully aggregated"
            }
            
        except Exception as e:
            self.logger.exception(f"Error aggregating data: {str(e)}")
            return {
                "error": f"Error aggregating data: {str(e)}",
                "status": "failed"
            }