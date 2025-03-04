from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path
from decimal import Decimal

from agents.base_agent import BaseAgent
from models.market_model import MarketData, LendingReserve

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
                    
        knowledge_sources = ["MarketDataKnowledgeSource"]
        
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
        task_type = task_input.get("task_type", "yield_analysis")
        
        if task_type == "yield_analysis":
            return self._analyze_yields(task_input)
        elif task_type == "yield_strategy":
            return self._generate_yield_strategy(task_input)
        else:
            return {
                "error": f"Unknown task type: {task_type}",
                "status": "failed"
            }
    
    def _analyze_yields(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze yields from market data."""
        market_data_path = task_input.get("market_data_path")
        output_format = task_input.get("output_format", "markdown")
        
        if not market_data_path:
            return {
                "error": "Market data path is required for yield analysis",
                "status": "failed"
            }
        
        try:
            # Access market data through knowledge source
            market_data = self.access_knowledge(
                "MarketDataKnowledgeSource", 
                {"path": market_data_path}
            )
            
            if "error" in market_data:
                return market_data
            
            # Perform yield analysis
            analysis_results = self._perform_yield_analysis(market_data["data"])
            
            # Format the analysis results based on the requested format
            if output_format == "markdown":
                formatted_results = self._format_yield_analysis_as_markdown(analysis_results)
            else:
                formatted_results = analysis_results
            
            # Save the results if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(formatted_results, output_path)
            
            return {
                "status": "success",
                "data": formatted_results,
                "message": "Yield analysis completed successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error analyzing yields: {str(e)}")
            return {
                "error": f"Error analyzing yields: {str(e)}",
                "status": "failed"
            }
    
    def _generate_yield_strategy(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate yield strategy using market data and wallet data."""
        market_data_path = task_input.get("market_data_path")
        wallet_data_path = task_input.get("wallet_data_path")
        output_format = task_input.get("output_format", "json")
        
        if not market_data_path:
            return {
                "error": "Market data path is required for yield strategy",
                "status": "failed"
            }
        
        if not wallet_data_path:
            return {
                "error": "Wallet data path is required for yield strategy",
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
            
            # Generate yield strategy
            strategy = self._generate_strategy(
                market_data_result["data"],
                wallet_data_result["data"]
            )
            
            # Format the strategy based on the requested format
            if output_format == "markdown":
                formatted_strategy = self._format_strategy_as_markdown(strategy)
            else:
                formatted_strategy = strategy
            
            # Save the strategy if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(formatted_strategy, output_path)
            
            return {
                "status": "success",
                "data": formatted_strategy,
                "message": "Yield strategy generated successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error generating yield strategy: {str(e)}")
            return {
                "error": f"Error generating yield strategy: {str(e)}",
                "status": "failed"
            }
    
    def _perform_yield_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform yield analysis on market data.
        
        In a real implementation, this would involve complex analysis of yield opportunities.
        For demonstration, we'll implement a simplified version.
        """
        analysis_results = {
            "best_yields": [],
            "protocol_comparison": {},
            "market_insights": []
        }
        
        # Process lending reserves across all tokens
        all_reserves = []
        for token_data in market_data:
            token_symbol = token_data["symbol"]
            
            for reserve in token_data.get("lending_reserves", []):
                reserve_data = {
                    "token": token_symbol,
                    "protocol": reserve["protocol_name"],
                    "market": reserve["market_name"],
                    "supply_rate": float(reserve["supply_rate"]),
                    "total_supply": reserve["total_supply"],
                    "total_borrows": reserve["total_borrows"]
                }
                
                # Calculate utilization rate
                try:
                    total_supply = float(reserve["total_supply"])
                    total_borrows = float(reserve["total_borrows"])
                    utilization = total_borrows / total_supply if total_supply > 0 else 0
                    reserve_data["utilization"] = round(utilization * 100, 2)
                except (ValueError, TypeError):
                    reserve_data["utilization"] = 0
                
                # Add trend if available
                if "supply_rate_7d" in reserve and "supply_rate_30d" in reserve:
                    try:
                        current_rate = float(reserve["supply_rate"])
                        rate_7d = float(reserve["supply_rate_7d"])
                        rate_30d = float(reserve["supply_rate_30d"])
                        
                        if abs(current_rate - rate_30d) < 0.1:
                            trend = "stable"
                        else:
                            trend = "up" if current_rate > rate_30d else "down"
                            
                        reserve_data["trend"] = trend
                        reserve_data["supply_rate_7d"] = rate_7d
                        reserve_data["supply_rate_30d"] = rate_30d
                    except (ValueError, TypeError):
                        reserve_data["trend"] = "unknown"
                
                all_reserves.append(reserve_data)
        
        # Find best yields
        best_yields = sorted(all_reserves, key=lambda r: r["supply_rate"], reverse=True)[:5]
        analysis_results["best_yields"] = best_yields
        
        # Compare protocols
        protocols = {}
        for reserve in all_reserves:
            protocol = reserve["protocol"]
            if protocol not in protocols:
                protocols[protocol] = {
                    "yields": [],
                    "avg_utilization": []
                }
            
            protocols[protocol]["yields"].append(reserve["supply_rate"])
            protocols[protocol]["avg_utilization"].append(reserve["utilization"])
        
        protocol_comparison = {}
        for protocol, data in protocols.items():
            yields = data["yields"]
            utilizations = data["avg_utilization"]
            
            protocol_comparison[protocol] = {
                "avg_yield": round(sum(yields) / len(yields), 2) if yields else 0,
                "max_yield": round(max(yields), 2) if yields else 0,
                "min_yield": round(min(yields), 2) if yields else 0,
                "avg_utilization": round(sum(utilizations) / len(utilizations), 2) if utilizations else 0,
                "market_count": len(yields)
            }
        
        analysis_results["protocol_comparison"] = protocol_comparison
        
        # Generate market insights
        analysis_results["market_insights"] = self._generate_market_insights(all_reserves, protocol_comparison)
        
        return analysis_results
    
    def _generate_market_insights(
        self, 
        reserves: List[Dict[str, Any]], 
        protocol_comparison: Dict[str, Any]
    ) -> List[str]:
        """Generate insights based on market data analysis."""
        insights = []
        
        # Find highest yield protocol
        if protocol_comparison:
            highest_yield_protocol = max(
                protocol_comparison.items(), 
                key=lambda x: x[1]["avg_yield"]
            )
            insights.append(
                f"{highest_yield_protocol[0]} currently offers the highest average yield at "
                f"{highest_yield_protocol[1]['avg_yield']}%"
            )
        
        # Check for protocols with high utilization
        high_util_protocols = [
            p for p, data in protocol_comparison.items() 
            if data["avg_utilization"] > 80
        ]
        if high_util_protocols:
            protocols_str = ", ".join(high_util_protocols)
            insights.append(
                f"{protocols_str} {'has' if len(high_util_protocols) == 1 else 'have'} high utilization rates, "
                f"which may indicate increased borrowing demand and potential for higher rates"
            )
        
        # Find markets with yield trends
        up_trend_markets = [r for r in reserves if r.get("trend") == "up"]
        down_trend_markets = [r for r in reserves if r.get("trend") == "down"]
        
        if up_trend_markets:
            up_trend_example = max(up_trend_markets, key=lambda r: r["supply_rate"])
            insights.append(
                f"{up_trend_example['protocol']}'s {up_trend_example['market']} has an upward yield trend, "
                f"currently at {up_trend_example['supply_rate']}%"
            )
        
        if down_trend_markets:
            down_trend_example = max(down_trend_markets, key=lambda r: r["supply_rate"])
            insights.append(
                f"{down_trend_example['protocol']}'s {down_trend_example['market']} has a downward yield trend, "
                f"currently at {down_trend_example['supply_rate']}%"
            )
        
        return insights
    
    def _generate_strategy(
        self, 
        market_data: Dict[str, Any], 
        wallet_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a yield strategy based on market data and wallet data.
        
        This would involve analyzing current positions, identifying optimal allocations,
        and creating a plan for rebalancing.
        """
        # Get total portfolio value
        portfolio_value = 0
        
        for balance in wallet_data.get("wallet_balances", []):
            portfolio_value += float(balance["amount"])
            
        for position in wallet_data.get("wallet_positions", []):
            portfolio_value += float(position["amount"])
        
        # Get yield analysis for market opportunities
        analysis = self._perform_yield_analysis(market_data)
        
        # Generate ideal positions based on analysis
        ideal_positions = []
        
        # For demonstration, we'll allocate to the top 3 yield opportunities
        # with equal distribution
        if analysis["best_yields"] and portfolio_value > 0:
            top_yields = analysis["best_yields"][:3]
            allocation_per_position = portfolio_value / len(top_yields)
            
            for opportunity in top_yields:
                ideal_positions.append({
                    "symbol": opportunity["token"],
                    "protocol_name": opportunity["protocol"],
                    "market_name": opportunity["market"],
                    "amount": str(round(allocation_per_position, 4)),
                    "obligation_type": "Supply"
                })
        
        strategy = {
            "total_portfolio_value": str(portfolio_value),
            "ideal_positions": ideal_positions,
            "rebalancing_required": True,
            "expected_avg_yield": self._calculate_expected_yield(ideal_positions, analysis["best_yields"]),
            "yield_increase": self._calculate_yield_increase(wallet_data, ideal_positions, analysis["best_yields"])
        }
        
        return strategy
    
    def _calculate_expected_yield(
        self, 
        positions: List[Dict[str, Any]], 
        yield_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate the expected yield for a set of positions."""
        if not positions:
            return 0.0
            
        total_amount = sum(float(pos["amount"]) for pos in positions)
        if total_amount == 0:
            return 0.0
            
        weighted_yield = 0.0
        
        for position in positions:
            # Find the yield data for this position
            for yield_info in yield_data:
                if (yield_info["protocol"] == position["protocol_name"] and 
                    yield_info["market"] == position["market_name"]):
                    
                    amount = float(position["amount"])
                    weight = amount / total_amount
                    weighted_yield += weight * yield_info["supply_rate"]
                    break
        
        return round(weighted_yield, 2)
    
    def _calculate_yield_increase(
        self, 
        wallet_data: Dict[str, Any], 
        ideal_positions: List[Dict[str, Any]], 
        yield_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate the potential yield increase from current to ideal positions."""
        # Calculate current yield
        current_positions = wallet_data.get("wallet_positions", [])
        current_yield = 0.0
        
        if current_positions:
            total_current_amount = sum(float(pos["amount"]) for pos in current_positions)
            
            if total_current_amount > 0:
                for position in current_positions:
                    # Find the yield data for this position
                    for yield_info in yield_data:
                        if (yield_info["protocol"] == position["protocol_name"] and 
                            yield_info["market"] == position["market_name"]):
                            
                            amount = float(position["amount"])
                            weight = amount / total_current_amount
                            current_yield += weight * yield_info["supply_rate"]
                            break
        
        # Calculate ideal yield
        ideal_yield = self._calculate_expected_yield(ideal_positions, yield_data)
        
        # Calculate increase
        yield_increase = ideal_yield - current_yield
        
        return round(yield_increase, 2)
    
    def _format_yield_analysis_as_markdown(self, analysis: Dict[str, Any]) -> str:
        """Format yield analysis results as markdown."""
        md = "# DeFi Lending Yield Analysis\n\n"
        
        # Best Yields Section
        md += "## Top Yield Opportunities\n\n"
        md += "| Token | Protocol | Market | Supply Rate | Utilization | Trend |\n"
        md += "| ----- | -------- | ------ | ----------- | ----------- | ----- |\n"
        
        for yield_info in analysis["best_yields"]:
            trend = yield_info.get("trend", "N/A")
            trend_icon = "→" if trend == "stable" else "↑" if trend == "up" else "↓" if trend == "down" else ""
            md += f"| {yield_info['token']} | {yield_info['protocol']} | {yield_info['market']} | "
            md += f"{yield_info['supply_rate']}% | {yield_info['utilization']}% | {trend} {trend_icon} |\n"
        
        md += "\n"
        
        # Protocol Comparison Section
        md += "## Protocol Comparison\n\n"
        md += "| Protocol | Avg Yield | Max Yield | Min Yield | Avg Utilization | Markets |\n"
        md += "| -------- | --------- | --------- | --------- | --------------- | ------- |\n"
        
        for protocol, data in analysis["protocol_comparison"].items():
            md += f"| {protocol} | {data['avg_yield']}% | {data['max_yield']}% | "
            md += f"{data['min_yield']}% | {data['avg_utilization']}% | {data['market_count']} |\n"
        
        md += "\n"
        
        # Market Insights Section
        md += "## Market Insights\n\n"
        
        for insight in analysis["market_insights"]:
            md += f"- {insight}\n"
        
        return md
    
    def _format_strategy_as_markdown(self, strategy: Dict[str, Any]) -> str:
        """Format yield strategy as markdown."""
        md = "# DeFi Lending Yield Strategy\n\n"
        
        md += f"**Total Portfolio Value:** ${strategy['total_portfolio_value']}\n"
        md += f"**Expected Average Yield:** {strategy['expected_avg_yield']}%\n"
        md += f"**Potential Yield Increase:** {strategy['yield_increase']}%\n\n"
        
        md += "## Recommended Positions\n\n"
        md += "| Token | Protocol | Market | Amount | % of Portfolio |\n"
        md += "| ----- | -------- | ------ | ------ | -------------- |\n"
        
        total_amount = sum(float(pos["amount"]) for pos in strategy["ideal_positions"])
        
        for position in strategy["ideal_positions"]:
            amount = float(position["amount"])
            percentage = (amount / float(strategy["total_portfolio_value"])) * 100
            
            md += f"| {position['symbol']} | {position['protocol_name']} | {position['market_name']} | "
            md += f"${amount:.2f} | {percentage:.2f}% |\n"
        
        md += "\n"
        
        md += "## Action Required\n\n"
        md += f"**Rebalancing Required:** {'Yes' if strategy['rebalancing_required'] else 'No'}\n\n"
        
        return md