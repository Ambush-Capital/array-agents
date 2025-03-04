from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path
import requests
from datetime import datetime

from agents.base_agent import BaseAgent

class Researcher(BaseAgent):
    """
    Agent responsible for researching DeFi lending markets.
    """
    
    def __init__(
        self,
        agent_id: str = "researcher",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the Researcher agent."""
        role = "DeFi Lending Market Senior Data Researcher"
        goal = "Uncover cutting-edge developments in DeFi lending markets"
        backstory = """You're a seasoned researcher with a knack for uncovering the latest
                   developments in the DeFi lending market. Known for your ability to find the most relevant
                   information and present it in a clear and concise manner. You specialize in the following 
                   solana lending markets: marginfi, kamino, drift and solend (SAVE)"""
        
        super().__init__(
            agent_id=agent_id,
            role=role,
            goal=goal,
            backstory=backstory,
            config=config
        )
    
    def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research tasks for DeFi lending markets.
        
        Args:
            task_input: Dictionary containing task parameters
                - "task_type": Type of research task
                - "protocol_names": List of protocols to research
                - "output_format": Format of the output (markdown, json, etc.)
                - "output_path": Path to save the output
                
        Returns:
            Dictionary with task results or error information
        """
        task_type = task_input.get("task_type", "market_research")
        
        if task_type == "market_research":
            return self._conduct_market_research(task_input)
        elif task_type == "protocol_research":
            return self._research_specific_protocols(task_input)
        else:
            return {
                "error": f"Unknown task type: {task_type}",
                "status": "failed"
            }
    
    def _conduct_market_research(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct general market research on DeFi lending markets."""
        protocols = task_input.get("protocol_names", ["marginfi", "kamino", "drift", "solend"])
        output_format = task_input.get("output_format", "markdown")
        
        try:
            # This would typically involve calling LLM API or other research methods
            # For demonstration, we'll return a static research report
            research_data = {
                "timestamp": datetime.now().isoformat(),
                "protocols": {}
            }
            
            for protocol in protocols:
                research_data["protocols"][protocol] = self._get_protocol_info(protocol)
            
            # Format the research results based on the requested format
            if output_format == "markdown":
                result = self._format_as_markdown(research_data)
            else:
                result = research_data
            
            # Save the results if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(result, output_path)
            
            return {
                "status": "success",
                "data": result,
                "message": "Market research completed successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error conducting market research: {str(e)}")
            return {
                "error": f"Error conducting market research: {str(e)}",
                "status": "failed"
            }
    
    def _research_specific_protocols(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Research specific DeFi lending protocols in detail."""
        protocols = task_input.get("protocol_names", [])
        output_format = task_input.get("output_format", "markdown")
        
        if not protocols:
            return {
                "error": "No protocols specified for research",
                "status": "failed"
            }
        
        try:
            # This would typically involve calling LLM API or other research methods
            # For demonstration, we'll return a static research report
            research_data = {
                "timestamp": datetime.now().isoformat(),
                "protocols": {}
            }
            
            for protocol in protocols:
                research_data["protocols"][protocol] = self._get_protocol_detailed_info(protocol)
            
            # Format the research results based on the requested format
            if output_format == "markdown":
                result = self._format_as_markdown(research_data, detailed=True)
            else:
                result = research_data
            
            # Save the results if output_path is specified
            output_path = task_input.get("output_path")
            if output_path:
                self.save_output(result, output_path)
            
            return {
                "status": "success",
                "data": result,
                "message": "Protocol research completed successfully"
            }
            
        except Exception as e:
            self.logger.exception(f"Error researching protocols: {str(e)}")
            return {
                "error": f"Error researching protocols: {str(e)}",
                "status": "failed"
            }
    
    def _get_protocol_info(self, protocol_name: str) -> Dict[str, Any]:
        """Get basic information about a protocol."""
        # In a real implementation, this would fetch actual data from APIs or databases
        # For demonstration, we'll return mock data
        protocol_info = {
            "name": protocol_name,
            "tvl": self._mock_tvl(protocol_name),
            "risks": self._mock_risk_info(protocol_name),
            "recent_news": self._mock_recent_news(protocol_name)
        }
        return protocol_info
    
    def _get_protocol_detailed_info(self, protocol_name: str) -> Dict[str, Any]:
        """Get detailed information about a protocol."""
        # Basic info
        info = self._get_protocol_info(protocol_name)
        
        # Add additional detailed information
        info.update({
            "markets": self._mock_markets(protocol_name),
            "governance": self._mock_governance(protocol_name),
            "performance": self._mock_performance(protocol_name),
            "security": self._mock_security(protocol_name)
        })
        
        return info
    
    def _format_as_markdown(self, research_data: Dict[str, Any], detailed: bool = False) -> str:
        """Format research data as markdown."""
        md = "# DeFi Lending Market Research Report\n\n"
        md += f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        
        for protocol_name, info in research_data["protocols"].items():
            md += f"## {protocol_name.title()}\n\n"
            
            md += f"**TVL:** {info['tvl']}\n\n"
            
            md += "### Risk Assessment\n"
            for risk, description in info["risks"].items():
                md += f"- **{risk}:** {description}\n"
            md += "\n"
            
            md += "### Recent News\n"
            for news_item in info["recent_news"]:
                md += f"- {news_item['date']}: {news_item['headline']}\n"
            md += "\n"
            
            if detailed:
                md += "### Markets\n"
                for market in info["markets"]:
                    md += f"- **{market['name']}**\n"
                    md += f"  - Supply Rate: {market['supply_rate']}\n"
                    md += f"  - Borrow Rate: {market['borrow_rate']}\n"
                    md += f"  - Utilization: {market['utilization']}\n"
                md += "\n"
                
                md += "### Governance\n"
                md += f"{info['governance']['description']}\n\n"
                
                md += "### Performance\n"
                for period, value in info["performance"].items():
                    md += f"- **{period}:** {value}\n"
                md += "\n"
                
                md += "### Security\n"
                md += f"**Audit Status:** {info['security']['audit_status']}\n"
                md += f"**Security Features:** {info['security']['features']}\n\n"
            
            md += "---\n\n"
        
        return md
    
    # Mock data methods for demonstration
    def _mock_tvl(self, protocol_name: str) -> str:
        tvl_map = {
            "marginfi": "$82.81M",
            "kamino": "$540.03M",
            "drift": "$275.12M",
            "solend": "$71.38M"
        }
        return tvl_map.get(protocol_name.lower(), "$100M")
    
    def _mock_risk_info(self, protocol_name: str) -> Dict[str, str]:
        # In a real implementation, this would be actual risk assessment
        return {
            "Smart Contract Risk": "Medium - Multiple audits conducted",
            "Market Risk": "Medium - Moderate volatility in underlying assets",
            "Oracle Risk": "Low - Uses Pyth and Switchboard for price feeds",
            "Centralization Risk": "Medium - Multisig governance with time-lock"
        }
    
    def _mock_recent_news(self, protocol_name: str) -> List[Dict[str, str]]:
        # In a real implementation, this would fetch actual news
        return [
            {
                "date": "2025-02-28",
                "headline": f"{protocol_name.title()} launches new USDC lending pool with enhanced yields"
            },
            {
                "date": "2025-02-15",
                "headline": f"{protocol_name.title()} completes security audit by Certik"
            },
            {
                "date": "2025-01-30",
                "headline": f"{protocol_name.title()} reaches $100M TVL milestone"
            }
        ]
    
    def _mock_markets(self, protocol_name: str) -> List[Dict[str, str]]:
        return [
            {
                "name": "USDC Main Pool",
                "supply_rate": "4.5%",
                "borrow_rate": "6.8%",
                "utilization": "75%"
            },
            {
                "name": "SOL Pool",
                "supply_rate": "2.1%",
                "borrow_rate": "3.5%",
                "utilization": "60%"
            }
        ]
    
    def _mock_governance(self, protocol_name: str) -> Dict[str, str]:
        return {
            "description": f"{protocol_name.title()} uses a DAO governance model with token holders voting on protocol changes. Proposals require a 5-day voting period and minimum quorum of 10% of tokens."
        }
    
    def _mock_performance(self, protocol_name: str) -> Dict[str, str]:
        return {
            "7-day average supply APY": "4.2%",
            "30-day average supply APY": "4.5%",
            "90-day average supply APY": "4.8%"
        }
    
    def _mock_security(self, protocol_name: str) -> Dict[str, str]:
        return {
            "audit_status": "Audited by Certik and Quantstamp in February 2025",
            "features": "Timelock for admin functions, circuit breakers for unusual activity, insurance fund for liquidity"
        }