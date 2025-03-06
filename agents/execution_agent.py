from typing import Dict, Any, Optional, List
import json
import logging
from pathlib import Path
from decimal import Decimal

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
        
        knowledge_sources = ["WalletDataKnowledgeSource"]
        
        super().__init__(
            agent_id=agent_id,
            role=role,
            goal=goal,
            backstory=backstory,
            knowledge_sources=knowledge_sources,
            config=config
        )
    
    def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tasks related to transaction planning and optimization.
        
        Args:
            task_input: Dictionary containing task parameters
                - "task_type": Type of execution task
                - "wallet_data_path": Path to wallet data
                - "portfolio_recommendation_path": Path to portfolio recommendation
                - "output_format": Output format (json, markdown)
                - "output_path": Path to save the output
                
        Returns:
            Dictionary with task results or error information
        """
        task_type = task_input.get("task_type", "create_execution_plan")
        
        if task_type == "create_execution_plan":
            return self._create_execution_plan(task_input)
        elif task_type == "optimize_transactions":
            return self._optimize_transactions(task_input)
        else:
            return {
                "error": f"Unknown task type: {task_type}",
                "status": "failed"
            }
    
    def _create_execution_plan(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create an execution plan based on portfolio recommendation and current wallet data."""
        wallet_data_path = task_input.get("wallet_data_path")
        portfolio_recommendation_path = task_input.get("portfolio_recommendation_path")
        output_format = task_input.get("output_format", "json")
        
        if not wallet_data_path:
            return {
                "error": "Wallet data path is required",
                "status": "failed"
            }
        
        if not portfolio_recommendation_path:
            return {
                "error": "Portfolio recommendation path is required",
                "status": "failed"
            }
        
        try:
            # Access wallet data through knowledge source
            wallet_data_result = self.access_knowledge(
                "WalletDataKnowledgeSource", 
                {"path": wallet_data_path}
            )
            
            if "error" in wallet_data_result:
                return wallet_data_result
            
            # Load portfolio recommendation
            try:
                with open(portfolio_recommendation_path, 'r') as f:
                    portfolio_recommendation = json.load(f)
            except Exception as e:
                return {
                    "error": f"Error loading portfolio recommendation: {str(e)}",
                    "status": "failed"
                }
            
            # Generate execution plan
            execution_plan = self._generate_execution_plan(
                wallet_data_result["data"],
                portfolio_recommendation
            )
            
            # Apply optimization strategies
            execution_plan = self._apply_optimization_strategies(execution_plan)
            
            # Format the output
            if output_format == "markdown":
                formatted_output = self._format_as_markdown(execution_plan)
            else:
                formatted_output = execution_plan
            
            # Save the output if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(formatted_output, output_path)
            
            return {
                "status": "success",
                "data": formatted_output,
                "message": "Execution plan created successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error creating execution plan: {str(e)}")
            return {
                "error": f"Error creating execution plan: {str(e)}",
                "status": "failed"
            }
    
    def _optimize_transactions(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize transaction strategy for a given execution plan."""
        execution_plan_path = task_input.get("execution_plan_path")
        
        if not execution_plan_path:
            return {
                "error": "Execution plan path is required",
                "status": "failed"
            }
        
        try:
            # Load execution plan
            try:
                with open(execution_plan_path, 'r') as f:
                    execution_plan = json.load(f)
            except Exception as e:
                return {
                    "error": f"Error loading execution plan: {str(e)}",
                    "status": "failed"
                }
            
            # Apply optimization strategies
            optimized_plan = self._apply_optimization_strategies(execution_plan)
            
            # Save the optimized plan if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(optimized_plan, f, indent=2)
            
            return {
                "status": "success",
                "data": optimized_plan,
                "message": "Execution plan optimized successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error optimizing transactions: {str(e)}")
            return {
                "error": f"Error optimizing transactions: {str(e)}",
                "status": "failed"
            }
    
    def _generate_execution_plan(
        self, 
        wallet_data: Dict[str, Any], 
        portfolio_recommendation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an execution plan by comparing current wallet positions with recommendations.
        
        Args:
            wallet_data: Current wallet data
            portfolio_recommendation: Portfolio recommendation
            
        Returns:
            Execution plan with transaction instructions
        """
        # Extract current positions
        current_positions = {}
        for position in wallet_data.get("wallet_positions", []):
            key = f"{position['symbol']}:{position['protocol_name']}:{position['market_name']}"
            current_positions[key] = {
                "symbol": position["symbol"],
                "protocol_name": position["protocol_name"],
                "market_name": position["market_name"],
                "amount": self._to_decimal(position["amount"]),
                "obligation_type": position["obligation_type"]
            }
        
        # Extract recommended positions
        recommended_positions = {}
        for position in portfolio_recommendation.get("ideal_positions", []):
            key = f"{position['symbol']}:{position['protocol_name']}:{position['market_name']}"
            recommended_positions[key] = {
                "symbol": position["symbol"],
                "protocol_name": position["protocol_name"],
                "market_name": position["market_name"],
                "amount": self._to_decimal(position["amount"]),
                "obligation_type": position["obligation_type"]
            }
        
        # Calculate positions to add, modify, or remove
        trades = []
        
        # Positions to add or increase
        for key, recommended in recommended_positions.items():
            current = current_positions.get(key)
            
            if current is None:
                # New position
                trades.append({
                    "action": "add",
                    "symbol": recommended["symbol"],
                    "protocol_name": recommended["protocol_name"],
                    "market_name": recommended["market_name"],
                    "amount": str(recommended["amount"]),
                    "obligation_type": recommended["obligation_type"]
                })
            else:
                # Existing position that needs adjustment
                diff = recommended["amount"] - current["amount"]
                
                if abs(diff) > Decimal('0.01'):  # Apply a small threshold to avoid dust transactions
                    if diff > 0:
                        # Increase position
                        trades.append({
                            "action": "increase",
                            "symbol": recommended["symbol"],
                            "protocol_name": recommended["protocol_name"],
                            "market_name": recommended["market_name"],
                            "amount": str(diff),
                            "obligation_type": recommended["obligation_type"]
                        })
                    else:
                        # Decrease position
                        trades.append({
                            "action": "decrease",
                            "symbol": recommended["symbol"],
                            "protocol_name": recommended["protocol_name"],
                            "market_name": recommended["market_name"],
                            "amount": str(abs(diff)),
                            "obligation_type": recommended["obligation_type"]
                        })
        
        # Positions to remove (in current but not in recommended)
        for key, current in current_positions.items():
            if key not in recommended_positions:
                trades.append({
                    "action": "remove",
                    "symbol": current["symbol"],
                    "protocol_name": current["protocol_name"],
                    "market_name": current["market_name"],
                    "amount": str(current["amount"]),
                    "obligation_type": current["obligation_type"]
                })
        
        # Extract unallocated balance
        unallocated_balance = self._get_unallocated_balance(wallet_data)
        
        # Create execution plan
        execution_plan = {
            "trade_execution": trades,
            "unallocated_balance": unallocated_balance,
            "transaction_order": self._determine_transaction_order(trades),
            "execution_strategy": "batch"  # or "sequential"
        }
        
        return execution_plan
    
    def _apply_optimization_strategies(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply optimization strategies to the execution plan.
        
        Args:
            execution_plan: Original execution plan
            
        Returns:
            Optimized execution plan
        """
        optimized_plan = execution_plan.copy()
        trades = optimized_plan.get("trade_execution", [])
        
        # Calculate optimal batch size
        optimized_plan["batch_size"] = min(len(trades), 5)  # Limit to 5 transactions per batch for safety
        
        # Add MEV protection strategy
        optimized_plan["mev_protection"] = {
            "enabled": True,
            "strategy": "time_randomization",
            "parameters": {
                "delay_range_ms": [500, 2000],
                "slippage_tolerance": "0.5%"
            }
        }
        
        # Optimize gas settings
        optimized_plan["gas_settings"] = {
            "prioritize": "speed",  # or "cost"
            "max_fee_per_gas": "auto",  # or specific value
            "gas_priority_fee": "auto"  # or specific value
        }
        
        # Add protocol-specific optimization settings
        for trade in trades:
            protocol = trade["protocol_name"].lower()
            
            if protocol == "marginfi":
                trade["protocol_settings"] = {
                    "use_router": True,
                    "max_slippage": "0.3%"
                }
            elif protocol == "drift":
                trade["protocol_settings"] = {
                    "use_perp_markets": False,
                    "max_slippage": "0.4%"
                }
            elif protocol in ["kamino", "solend", "save"]:
                trade["protocol_settings"] = {
                    "max_slippage": "0.3%"
                }
        
        return optimized_plan
    
    def _determine_transaction_order(self, trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Determine the optimal order for executing transactions.
        
        Args:
            trades: List of trade instructions
            
        Returns:
            List of prioritized trade instructions
        """
        # Sort trades by priority:
        # 1. First withdraw/decrease positions to ensure liquidity for new positions
        # 2. Then add/increase positions
        
        withdrawals = []
        deposits = []
        
        for trade in trades:
            if trade["action"] in ["remove", "decrease"]:
                withdrawals.append(trade)
            else:
                deposits.append(trade)
        
        # Sort withdrawals by amount (largest first)
        withdrawals.sort(key=lambda x: self._to_decimal(x["amount"]), reverse=True)
        
        # Sort deposits by amount (largest first)
        deposits.sort(key=lambda x: self._to_decimal(x["amount"]), reverse=True)
        
        # Combine the lists
        return withdrawals + deposits
    
    def _get_unallocated_balance(self, wallet_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract unallocated balances from wallet data.
        
        Args:
            wallet_data: Wallet data
            
        Returns:
            Dictionary of unallocated balances by symbol
        """
        unallocated = {}
        
        for balance in wallet_data.get("wallet_balances", []):
            symbol = balance["symbol"]
            amount = balance["amount"]
            
            if symbol not in unallocated:
                unallocated[symbol] = amount
            else:
                current = self._to_decimal(unallocated[symbol])
                additional = self._to_decimal(amount)
                unallocated[symbol] = str(current + additional)
        
        return unallocated
    
    def _to_decimal(self, value: str) -> Decimal:
        """Convert string to Decimal safely."""
        try:
            return Decimal(value)
        except:
            return Decimal('0')
    
    def _format_as_markdown(self, execution_plan: Dict[str, Any]) -> str:
        """Format execution plan as markdown."""
        md = "# DeFi Portfolio Execution Plan\n\n"
        
        # Trade execution section
        md += "## Trade Execution Instructions\n\n"
        
        trades = execution_plan.get("trade_execution", [])
        if not trades:
            md += "*No trades required*\n\n"
        else:
            for i, trade in enumerate(trades, 1):
                action_map = {
                    "add": "Deposit",
                    "remove": "Withdraw",
                    "increase": "Increase position by",
                    "decrease": "Decrease position by"
                }
                
                action = action_map.get(trade["action"], trade["action"].capitalize())
                
                md += f"### Trade {i}: {action} {trade['symbol']}\n\n"
                md += f"- **Protocol**: {trade['protocol_name']}\n"
                md += f"- **Market**: {trade['market_name']}\n"
                md += f"- **Amount**: {trade['amount']} {trade['symbol']}\n"
                md += f"- **Type**: {trade['obligation_type']}\n"
                
                if "protocol_settings" in trade:
                    md += "- **Protocol Settings**:\n"
                    for key, value in trade["protocol_settings"].items():
                        formatted_key = key.replace("_", " ").capitalize()
                        md += f"  - {formatted_key}: {value}\n"
                
                md += "\n"
        
        # Unallocated balance section
        md += "## Unallocated Balances\n\n"
        
        unallocated = execution_plan.get("unallocated_balance", {})
        for symbol, amount in unallocated.items():
            md += f"- **{symbol}**: {amount}\n"
        
        md += "\n"
        
        # Execution strategy section
        md += "## Execution Strategy\n\n"
        
        md += f"- **Method**: {execution_plan.get('execution_strategy', 'batch').capitalize()}\n"
        md += f"- **Batch Size**: {execution_plan.get('batch_size', 5)}\n"
        
        # MEV protection section
        if "mev_protection" in execution_plan:
            mev = execution_plan["mev_protection"]
            md += f"- **MEV Protection**: {'Enabled' if mev.get('enabled') else 'Disabled'}\n"
            
            if mev.get("enabled"):
                md += f"  - **Strategy**: {mev.get('strategy', '').replace('_', ' ').capitalize()}\n"
                
                if "parameters" in mev:
                    params = mev["parameters"]
                    if "delay_range_ms" in params:
                        min_delay, max_delay = params["delay_range_ms"]
                        md += f"  - **Transaction Delay**: {min_delay}-{max_delay} ms\n"
                    
                    if "slippage_tolerance" in params:
                        md += f"  - **Slippage Tolerance**: {params['slippage_tolerance']}\n"
        
        # Gas settings section
        if "gas_settings" in execution_plan:
            gas = execution_plan["gas_settings"]
            md += f"- **Gas Strategy**: Prioritize {gas.get('prioritize', 'speed')}\n"
            md += f"  - **Max Fee**: {gas.get('max_fee_per_gas', 'auto')}\n"
            md += f"  - **Priority Fee**: {gas.get('gas_priority_fee', 'auto')}\n"
        
        return md