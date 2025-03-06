from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path
from decimal import Decimal

from agents.base_agent import BaseAgent

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
                   
        knowledge_sources = ["MarketDataKnowledgeSource", "WalletDataKnowledgeSource"]
        
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
        Execute portfolio management tasks.
        
        Args:
            task_input: Dictionary containing task parameters including:
                - "task_type": Type of portfolio task
                - "market_data_path": Path to market data file
                - "wallet_data_path": Path to wallet data file
                - "yield_strategy_path": Path to yield strategy file
                - "risk_adjusted_strategy_path": Path to risk-adjusted strategy file
                - "research_path": Optional path to research file
                - "output_format": Format of the output (markdown, json)
                - "output_path": Path to save the output
                
        Returns:
            Dictionary with task results or error information
        """
        task_type = task_input.get("task_type", "portfolio_optimization")
        
        if task_type == "portfolio_optimization":
            return self._optimize_portfolio(task_input)
        elif task_type == "portfolio_review":
            return self._review_portfolio(task_input)
        else:
            return {
                "error": f"Unknown task type: {task_type}",
                "status": "failed"
            }
    
    def _optimize_portfolio(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize portfolio allocation based on yield and risk analysis.
        
        This combines yield strategy and risk-adjusted strategy to create
        a final optimization recommendation.
        """
        market_data_path = task_input.get("market_data_path")
        wallet_data_path = task_input.get("wallet_data_path")
        yield_strategy_path = task_input.get("yield_strategy_path")
        risk_adjusted_strategy_path = task_input.get("risk_adjusted_strategy_path")
        research_path = task_input.get("research_path")
        output_format = task_input.get("output_format", "json")
        
        required_paths = [
            ("market_data_path", market_data_path),
            ("wallet_data_path", wallet_data_path),
            ("yield_strategy_path", yield_strategy_path),
            ("risk_adjusted_strategy_path", risk_adjusted_strategy_path)
        ]
        
        for name, path in required_paths:
            if not path:
                return {
                    "error": f"{name} is required for portfolio optimization",
                    "status": "failed"
                }
        
        try:
            # Access market data through knowledge source
            market_data_result = self.access_knowledge(
                "MarketDataKnowledgeSource", 
                {"path": market_data_path}
            )
            
            if "error" in market_data_result:
                return market_data_result
            
            # Access wallet data through knowledge source
            wallet_data_result = self.access_knowledge(
                "WalletDataKnowledgeSource", 
                {"path": wallet_data_path}
            )
            
            if "error" in wallet_data_result:
                return wallet_data_result
            
            # Load yield strategy
            try:
                with open(yield_strategy_path, 'r') as f:
                    yield_strategy = json.load(f)
            except Exception as e:
                return {
                    "error": f"Error loading yield strategy: {str(e)}",
                    "status": "failed"
                }
            
            # Load risk-adjusted strategy
            try:
                with open(risk_adjusted_strategy_path, 'r') as f:
                    risk_adjusted_strategy = json.load(f)
            except Exception as e:
                return {
                    "error": f"Error loading risk-adjusted strategy: {str(e)}",
                    "status": "failed"
                }
            
            # Load research if available
            research_data = None
            if research_path:
                try:
                    with open(research_path, 'r') as f:
                        research_data = f.read()
                except Exception as e:
                    self.logger.warning(f"Could not load research data: {str(e)}")
            
            # Generate optimized portfolio
            optimization = self._generate_optimized_portfolio(
                yield_strategy,
                risk_adjusted_strategy,
                market_data_result["data"],
                wallet_data_result["data"],
                research_data
            )
            
            # Format the optimization based on the requested format
            if output_format == "markdown":
                formatted_optimization = self._format_optimization_as_markdown(optimization)
            else:
                formatted_optimization = optimization
            
            # Save the optimization if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(formatted_optimization, output_path)
            
            return {
                "status": "success",
                "data": formatted_optimization,
                "message": "Portfolio optimization completed successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error optimizing portfolio: {str(e)}")
            return {
                "error": f"Error optimizing portfolio: {str(e)}",
                "status": "failed"
            }
    
    def _review_portfolio(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review current portfolio allocation and performance.
        
        This provides an assessment of the current state without
        generating new recommendations.
        """
        market_data_path = task_input.get("market_data_path")
        wallet_data_path = task_input.get("wallet_data_path")
        output_format = task_input.get("output_format", "markdown")
        
        if not market_data_path:
            return {
                "error": "Market data path is required for portfolio review",
                "status": "failed"
            }
        
        if not wallet_data_path:
            return {
                "error": "Wallet data path is required for portfolio review",
                "status": "failed"
            }
        
        try:
            # Access market data through knowledge source
            market_data_result = self.access_knowledge(
                "MarketDataKnowledgeSource", 
                {"path": market_data_path}
            )
            
            if "error" in market_data_result:
                return market_data_result
            
            # Access wallet data through knowledge source
            wallet_data_result = self.access_knowledge(
                "WalletDataKnowledgeSource", 
                {"path": wallet_data_path}
            )
            
            if "error" in wallet_data_result:
                return wallet_data_result
            
            # Generate portfolio review
            review = self._review_current_portfolio(
                market_data_result["data"],
                wallet_data_result["data"]
            )
            
            # Format the review based on the requested format
            if output_format == "markdown":
                formatted_review = self._format_review_as_markdown(review)
            else:
                formatted_review = review
            
            # Save the review if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(formatted_review, output_path)
            
            return {
                "status": "success",
                "data": formatted_review,
                "message": "Portfolio review completed successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error reviewing portfolio: {str(e)}")
            return {
                "error": f"Error reviewing portfolio: {str(e)}",
                "status": "failed"
            }
    
    def _generate_optimized_portfolio(
        self,
        yield_strategy: Dict[str, Any],
        risk_adjusted_strategy: Dict[str, Any],
        market_data: Dict[str, Any],
        wallet_data: Dict[str, Any],
        research_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an optimized portfolio allocation.
        
        This combines the yield-optimized and risk-adjusted strategies,
        taking into account current market data, wallet positions, and research.
        """
        # Extract current wallet positions
        current_positions = wallet_data.get("wallet_positions", [])
        wallet_balances = wallet_data.get("wallet_balances", [])
        
        # Calculate total portfolio value
        portfolio_value = sum(float(pos["amount"]) for pos in current_positions)
        portfolio_value += sum(float(bal["amount"]) for bal in wallet_balances)
        
        # Extract strategies
        yield_positions = yield_strategy.get("ideal_positions", [])
        risk_positions = risk_adjusted_strategy.get("ideal_positions", [])
        
        # Determine optimization approach based on risk score
        risk_score = risk_adjusted_strategy.get("risk_score", 5)
        
        # Lower risk score = prioritize yield, higher = prioritize risk adjustment
        if risk_score < 3:
            # Low risk, prioritize yield
            yield_weight = 0.8
            risk_weight = 0.2
            approach = "yield_priority"
            approach_description = (
                "The portfolio has a low risk score, so the optimization prioritizes "
                "yield while maintaining the current balanced risk profile."
            )
        elif risk_score < 6:
            # Medium risk, balance yield and risk
            yield_weight = 0.5
            risk_weight = 0.5
            approach = "balanced"
            approach_description = (
                "The portfolio has a moderate risk score, so the optimization balances "
                "yield optimization with risk management."
            )
        else:
            # High risk, prioritize risk reduction
            yield_weight = 0.2
            risk_weight = 0.8
            approach = "risk_priority"
            approach_description = (
                "The portfolio has a high risk score, so the optimization prioritizes "
                "risk reduction while still seeking reasonable yield."
            )
        
        # Create optimized positions by combining yield and risk strategies
        optimized_positions = self._combine_strategies(
            yield_positions, 
            risk_positions, 
            yield_weight, 
            risk_weight
        )
        
        # Calculate trades required to move from current to optimized positions
        required_trades = self._calculate_required_trades(
            current_positions, 
            optimized_positions
        )
        
        # Calculate expected yield of optimized portfolio
        expected_yield = self._calculate_expected_yield(optimized_positions, market_data)
        
        # Calculate yield change
        current_yield = self._calculate_current_yield(current_positions, market_data)
        yield_change = expected_yield - current_yield
        
        # Prepare the optimization result
        optimization = {
            "total_portfolio_value": str(portfolio_value),
            "optimization_approach": approach,
            "approach_description": approach_description,
            "risk_score": risk_score,
            "risk_level": risk_adjusted_strategy.get("risk_level", "medium"),
            "current_yield": current_yield,
            "expected_yield": expected_yield,
            "yield_change": yield_change,
            "optimized_positions": optimized_positions,
            "required_trades": required_trades,
            "trade_urgency": self._determine_trade_urgency(yield_change, required_trades),
            "execution_timeline": self._recommend_execution_timeline(required_trades, yield_change),
            "market_notes": self._extract_market_notes(research_data)
        }
        
        return optimization
    
    def _combine_strategies(
        self,
        yield_positions: List[Dict[str, Any]],
        risk_positions: List[Dict[str, Any]],
        yield_weight: float,
        risk_weight: float
    ) -> List[Dict[str, Any]]:
        """
        Combine yield and risk strategies with appropriate weighting.
        
        This creates a blended allocation that balances yield optimization
        and risk management.
        """
        # Create a map of positions by protocol and market
        position_map = {}
        
        # Add yield positions to the map
        for position in yield_positions:
            key = f"{position['protocol_name']}|{position['market_name']}"
            position_map[key] = {
                "symbol": position["symbol"],
                "protocol_name": position["protocol_name"],
                "market_name": position["market_name"],
                "yield_amount": float(position["amount"]),
                "risk_amount": 0.0,
                "obligation_type": position["obligation_type"]
            }
        
        # Add or update with risk positions
        for position in risk_positions:
            key = f"{position['protocol_name']}|{position['market_name']}"
            if key in position_map:
                position_map[key]["risk_amount"] = float(position["amount"])
            else:
                position_map[key] = {
                    "symbol": position["symbol"],
                    "protocol_name": position["protocol_name"],
                    "market_name": position["market_name"],
                    "yield_amount": 0.0,
                    "risk_amount": float(position["amount"]),
                    "obligation_type": position["obligation_type"]
                }
        
        # Calculate weighted amounts
        optimized_positions = []
        for key, position in position_map.items():
            weighted_amount = (
                position["yield_amount"] * yield_weight + 
                position["risk_amount"] * risk_weight
            )
            
            # Only include positions with non-zero allocation
            if weighted_amount > 0:
                optimized_positions.append({
                    "symbol": position["symbol"],
                    "protocol_name": position["protocol_name"],
                    "market_name": position["market_name"],
                    "amount": str(round(weighted_amount, 4)),
                    "obligation_type": position["obligation_type"]
                })
        
        return optimized_positions
    
    def _calculate_required_trades(
        self,
        current_positions: List[Dict[str, Any]],
        target_positions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate the trades required to move from current to target positions.
        
        Returns a list of trades with action (add, remove, or adjust),
        protocol, market, and amount.
        """
        # Create maps for current and target positions
        current_map = {}
        for position in current_positions:
            key = f"{position['protocol_name']}|{position['market_name']}"
            current_map[key] = position
        
        target_map = {}
        for position in target_positions:
            key = f"{position['protocol_name']}|{position['market_name']}"
            target_map[key] = position
        
        # Calculate required trades
        trades = []
        
        # Find positions to remove or adjust down
        for key, position in current_map.items():
            if key not in target_map:
                # Position needs to be removed
                trades.append({
                    "action": "remove",
                    "symbol": position["symbol"],
                    "protocol_name": position["protocol_name"],
                    "market_name": position["market_name"],
                    "amount": position["amount"],
                    "obligation_type": position["obligation_type"]
                })
            else:
                # Position exists in both, check if adjustment needed
                current_amount = float(position["amount"])
                target_amount = float(target_map[key]["amount"])
                difference = target_amount - current_amount
                
                if abs(difference) / current_amount > 0.05:  # >5% change
                    trades.append({
                        "action": "adjust",
                        "symbol": position["symbol"],
                        "protocol_name": position["protocol_name"],
                        "market_name": position["market_name"],
                        "current_amount": position["amount"],
                        "target_amount": target_map[key]["amount"],
                        "difference": str(round(difference, 4)),
                        "obligation_type": position["obligation_type"]
                    })
        
        # Find positions to add
        for key, position in target_map.items():
            if key not in current_map:
                # New position to add
                trades.append({
                    "action": "add",
                    "symbol": position["symbol"],
                    "protocol_name": position["protocol_name"],
                    "market_name": position["market_name"],
                    "amount": position["amount"],
                    "obligation_type": position["obligation_type"]
                })
        
        return trades
    
    def _calculate_current_yield(
        self,
        positions: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> float:
        """Calculate the current yield of the portfolio."""
        if not positions:
            return 0.0
            
        total_amount = sum(float(pos["amount"]) for pos in positions)
        if total_amount == 0:
            return 0.0
            
        weighted_yield = 0.0
        
        for position in positions:
            protocol = position["protocol_name"]
            market = position["market_name"]
            amount = float(position["amount"])
            
            # Find the yield for this position
            position_yield = 0.0
            
            for token_data in market_data:
                for reserve in token_data.get("lending_reserves", []):
                    if reserve["protocol_name"] == protocol and reserve["market_name"] == market:
                        try:
                            position_yield = float(reserve["supply_rate"])
                            break
                        except (ValueError, TypeError):
                            pass
                
                if position_yield > 0:
                    break
            
            # Add weighted yield
            weight = amount / total_amount
            weighted_yield += weight * position_yield
        
        return round(weighted_yield, 2)
    
    def _calculate_expected_yield(
        self,
        positions: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> float:
        """Calculate the expected yield of optimized positions."""
        # Uses the same logic as _calculate_current_yield but with target positions
        return self._calculate_current_yield(positions, market_data)
    
    def _determine_trade_urgency(
        self,
        yield_change: float,
        required_trades: List[Dict[str, Any]]
    ) -> str:
        """
        Determine the urgency of executing the recommended trades.
        
        Returns one of: "high", "medium", "low"
        """
        if not required_trades:
            return "none"
        
        # Count significant trades (additions or removals)
        significant_trades = [
            t for t in required_trades 
            if t["action"] in ["add", "remove"]
        ]
        
        # Check for large yield improvement
        significant_yield_change = yield_change >= 1.0  # >1% improvement
        
        if significant_yield_change and len(significant_trades) >= 2:
            return "high"
        elif significant_yield_change or len(significant_trades) >= 2:
            return "medium"
        else:
            return "low"
    
    def _recommend_execution_timeline(
        self,
        required_trades: List[Dict[str, Any]],
        yield_change: float
    ) -> str:
        """
        Recommend a timeline for executing the trades.
        
        Returns a string with a timeline recommendation.
        """
        urgency = self._determine_trade_urgency(yield_change, required_trades)
        
        if urgency == "high":
            return "Execute trades immediately to capture yield opportunity"
        elif urgency == "medium":
            return "Execute trades within the next 24-48 hours"
        elif urgency == "low":
            return "Execute trades during regular rebalancing schedule"
        else:
            return "No trades required at this time"
    
    def _extract_market_notes(self, research_data: Optional[str]) -> List[str]:
        """
        Extract relevant market notes from research data.
        
        In a real implementation, this would parse the research document
        to extract key insights. For demonstration, we'll return sample notes.
        """
        if not research_data:
            return [
                "No research data available for market insights",
                "Consider reviewing recent protocol developments"
            ]
        
        # Sample notes - in a real implementation, these would be extracted from research
        return [
            "Market utilization rates remain stable across major protocols",
            "Recent governance proposals may affect Drift's yield rates in coming weeks",
            "Kamino continues to show consistent performance in the JLP Market"
        ]
    
    def _review_current_portfolio(
        self,
        market_data: Dict[str, Any],
        wallet_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Review the current portfolio allocation and performance.
        
        This provides an assessment without generating new recommendations.
        """
        # Extract current wallet positions
        positions = wallet_data.get("wallet_positions", [])
        balances = wallet_data.get("wallet_balances", [])
        
        # Calculate total portfolio value
        position_value = sum(float(pos["amount"]) for pos in positions)
        balance_value = sum(float(bal["amount"]) for bal in balances)
        total_value = position_value + balance_value
        
        # Calculate allocation by protocol
        protocol_allocations = {}
        for position in positions:
            protocol = position["protocol_name"]
            amount = float(position["amount"])
            
            if protocol not in protocol_allocations:
                protocol_allocations[protocol] = 0
                
            protocol_allocations[protocol] += amount
        
        # Convert to percentages
        protocol_percentages = {}
        for protocol, amount in protocol_allocations.items():
            protocol_percentages[protocol] = (amount / total_value) * 100 if total_value > 0 else 0
        
        # Calculate current yield and yield by protocol
        current_yield = self._calculate_current_yield(positions, market_data)
        
        protocol_yields = {}
        for protocol in protocol_allocations:
            protocol_positions = [p for p in positions if p["protocol_name"] == protocol]
            protocol_yields[protocol] = self._calculate_current_yield(protocol_positions, market_data)
        
        # Calculate unallocated percentage
        unallocated_percentage = (balance_value / total_value) * 100 if total_value > 0 else 0
        
        # Prepare the review
        review = {
            "total_portfolio_value": str(total_value),
            "current_yield": current_yield,
            "allocated_value": str(position_value),
            "unallocated_value": str(balance_value),
            "unallocated_percentage": round(unallocated_percentage, 2),
            "protocol_allocations": {
                protocol: round(percentage, 2)
                for protocol, percentage in protocol_percentages.items()
            },
            "protocol_yields": {
                protocol: yield_value
                for protocol, yield_value in protocol_yields.items()
            },
            "positions": positions,
            "balances": balances
        }
        
        return review
    
    def _format_optimization_as_markdown(self, optimization: Dict[str, Any]) -> str:
        """Format portfolio optimization as markdown."""
        md = "# DeFi Portfolio Optimization Recommendation\n\n"
        
        # Portfolio Overview Section
        md += "## Portfolio Overview\n\n"
        md += f"**Total Portfolio Value:** ${optimization['total_portfolio_value']}\n"
        md += f"**Current Yield:** {optimization['current_yield']}%\n"
        md += f"**Expected Yield After Optimization:** {optimization['expected_yield']}%\n"
        md += f"**Potential Yield Improvement:** {optimization['yield_change']}%\n"
        md += f"**Risk Level:** {optimization['risk_level'].upper()}\n"
        md += f"**Risk Score:** {optimization['risk_score']}/10\n\n"
        
        # Optimization Approach Section
        md += "## Optimization Approach\n\n"
        md += f"**Strategy:** {optimization['optimization_approach'].replace('_', ' ').title()}\n\n"
        md += f"{optimization['approach_description']}\n\n"
        
        # Recommended Positions Section
        md += "## Recommended Positions\n\n"
        md += "| Token | Protocol | Market | Amount | % of Portfolio |\n"
        md += "| ----- | -------- | ------ | ------ | -------------- |\n"
        
        total_value = float(optimization["total_portfolio_value"])
        
        for position in optimization["optimized_positions"]:
            amount = float(position["amount"])
            percentage = (amount / total_value) * 100 if total_value > 0 else 0
            
            md += f"| {position['symbol']} | {position['protocol_name']} | {position['market_name']} | "
            md += f"${amount:.2f} | {percentage:.2f}% |\n"
        
        md += "\n"
        
        # Required Trades Section
        md += "## Required Trades\n\n"
        
        if not optimization["required_trades"]:
            md += "No trades required. Current allocation is optimal.\n\n"
        else:
            # Group trades by action
            additions = [t for t in optimization["required_trades"] if t["action"] == "add"]
            removals = [t for t in optimization["required_trades"] if t["action"] == "remove"]
            adjustments = [t for t in optimization["required_trades"] if t["action"] == "adjust"]
            
            if additions:
                md += "### New Positions to Add\n\n"
                md += "| Token | Protocol | Market | Amount |\n"
                md += "| ----- | -------- | ------ | ------ |\n"
                
                for trade in additions:
                    md += f"| {trade['symbol']} | {trade['protocol_name']} | {trade['market_name']} | "
                    md += f"${float(trade['amount']):.2f} |\n"
                
                md += "\n"
            
            if removals:
                md += "### Positions to Remove\n\n"
                md += "| Token | Protocol | Market | Amount |\n"
                md += "| ----- | -------- | ------ | ------ |\n"
                
                for trade in removals:
                    md += f"| {trade['symbol']} | {trade['protocol_name']} | {trade['market_name']} | "
                    md += f"${float(trade['amount']):.2f} |\n"
                
                md += "\n"
            
            if adjustments:
                md += "### Positions to Adjust\n\n"
                md += "| Token | Protocol | Market | Current | Target | Change |\n"
                md += "| ----- | -------- | ------ | ------- | ------ | ------ |\n"
                
                for trade in adjustments:
                    md += f"| {trade['symbol']} | {trade['protocol_name']} | {trade['market_name']} | "
                    md += f"${float(trade['current_amount']):.2f} | ${float(trade['target_amount']):.2f} | "
                    
                    diff = float(trade['difference'])
                    sign = "+" if diff > 0 else ""
                    md += f"{sign}{diff:.2f} |\n"
                
                md += "\n"
        
        # Execution Plan Section
        md += "## Execution Plan\n\n"
        md += f"**Trade Urgency:** {optimization['trade_urgency'].upper()}\n"
        md += f"**Recommended Timeline:** {optimization['execution_timeline']}\n\n"
        
        # Market Notes Section
        md += "## Market Notes\n\n"
        
        for note in optimization["market_notes"]:
            md += f"- {note}\n"
        
        return md
    
    def _format_review_as_markdown(self, review: Dict[str, Any]) -> str:
        """Format portfolio review as markdown."""
        md = "# DeFi Portfolio Review\n\n"
        
        # Portfolio Overview Section
        md += "## Portfolio Overview\n\n"
        md += f"**Total Portfolio Value:** ${review['total_portfolio_value']}\n"
        md += f"**Current Yield:** {review['current_yield']}%\n"
        md += f"**Allocated Value:** ${review['allocated_value']}\n"
        md += f"**Unallocated Value:** ${review['unallocated_value']} "
        md += f"({review['unallocated_percentage']}% of portfolio)\n\n"
        
        # Allocation Section
        md += "## Current Allocation\n\n"
        md += "| Protocol | Allocation | Yield |\n"
        md += "| -------- | ---------- | ----- |\n"
        
        for protocol, allocation in review["protocol_allocations"].items():
            yield_value = review["protocol_yields"].get(protocol, 0)
            md += f"| {protocol} | {allocation:.2f}% | {yield_value}% |\n"
        
        md += f"| Unallocated | {review['unallocated_percentage']:.2f}% | 0% |\n"
        md += "\n"
        
        # Positions Section
        md += "## Current Positions\n\n"
        md += "| Token | Protocol | Market | Amount |\n"
        md += "| ----- | -------- | ------ | ------ |\n"
        
        for position in review["positions"]:
            md += f"| {position['symbol']} | {position['protocol_name']} | {position['market_name']} | "
            md += f"${float(position['amount']):.2f} |\n"
        
        md += "\n"
        
        # Balances Section
        if review["balances"]:
            md += "## Unallocated Balances\n\n"
            md += "| Token | Amount |\n"
            md += "| ----- | ------ |\n"
            
            for balance in review["balances"]:
                md += f"| {balance['symbol']} | ${float(balance['amount']):.2f} |\n"
        
        return md