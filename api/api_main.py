# api_main.py - DeFi Portfolio Optimizer API Main Function

import json
import logging
from datetime import datetime

# Import agent classes
from agents.yield_analyst import YieldAnalyst
from agents.risk_manager import RiskManager
from agents.portfolio_manager import PortfolioManager
from agents.execution_agent import ExecutionAgent
from tools.fetch_market_data import MarketData
from tools.fetch_wallet_data import WalletData
from tools.send_email import SendEmail

# Import config and utilities
from config.settings import load_config
from main import setup_environment

def api_main(wallet_id, risk_level, email):
    """
    API version of the main execution function.
    
    Args:
        wallet_id (str): The wallet ID to analyze
        risk_level (str): Risk tolerance level (low, medium, high)
        email (str): Email address to send the analysis results to
        
    Returns:
        dict: Analysis results as a dictionary
    """
    # Create args similar to what parse_arguments would return
    class Args:
        def __init__(self):
            self.api_url = "http://localhost:3001/current_markets"
            self.output_dir = "outputs"
            self.debug = False
    
    args = Args()

    try:
        # Set up environment
        env = setup_environment(args)
        logger = env["logger"]
        
        logger.info("Starting DeFi Portfolio Optimization process via API")
        logger.info(f"Wallet ID: {wallet_id}, Risk Level: {risk_level}, Email: {email}")
        
        # Validate risk level
        if risk_level not in ['low', 'medium', 'high']:
            return {"error": "Risk tolerance must be one of: 'low', 'medium', 'high'"}, 400
        
        # Run the pipeline
        md = MarketData()
        market_data = md.fetch_market_data()
        
        wd = WalletData()
        # Pass wallet_id to fetch_wallet_data
        wallet_data = wd.fetch_wallet_data(wallet_id=wallet_id)
        
        # Initialize the YieldAnalyst and pass market data
        yield_analyst = YieldAnalyst(config=env["config"])
        (yield_analysis_results, yield_strategy_results) = yield_analyst.execute_task(market_data)
        
        # Initialize the RiskManager and pass analysis results
        risk_manager = RiskManager(config=env["config"])
        risk_analysis_results = risk_manager.execute_task(
            market_data, 
            wallet_data, 
            risk_level, 
            yield_strategy_results
        )

        # Initialize the PortfolioManager and pass analysis results
        portfolio_manager = PortfolioManager(config=env["config"])
        (optimized_portfolio, final_recc_to_execute) = portfolio_manager.execute_task(
            market_data, 
            wallet_data, 
            yield_analysis_results, 
            yield_strategy_results, 
            risk_analysis_results,
            risk_level
        )

        # Initialize the ExecutionAgent and pass final recommendation
        execution_agent = ExecutionAgent(config=env["config"])
        execution_plan = execution_agent.execute_task(
            wallet_data, 
            final_recc_to_execute
        )

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the output for email
        output = f"""
        Market Data: {market_data}
        Wallet Data: {wallet_data}
        Yield Analysis Results: {yield_analysis_results}
        Yield Strategy Results: {yield_strategy_results}
        Risk Analysis Results: {risk_analysis_results}
        Optimized Portfolio: {optimized_portfolio}
        Final Recommendations: {final_recc_to_execute}
        Execution Plan: {execution_plan}
        """
        
        # Send email if an email address was provided
        if email:
            SendEmail().send_full_analysis(output, email, current_time)
        
        # Prepare the response data
        response_data = {
            "wallet_id": wallet_id,
            "risk_level": risk_level,
            "timestamp": current_time,
            "market_data": market_data,
            "wallet_data": wallet_data,
            "yield_analysis": yield_analysis_results,
            "yield_strategy": yield_strategy_results,
            "risk_analysis": risk_analysis_results,
            "optimized_portfolio": optimized_portfolio,
            "final_recommendations": final_recc_to_execute,
            "execution_plan": execution_plan
        }
        
        return response_data
        
    except Exception as e:
        if 'logger' in locals():
            logger.exception("Portfolio optimization failed")
        else:
            print(f"Error: {str(e)}")
        return {"error": str(e)}, 500
