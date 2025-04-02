# main.py - DeFi Portfolio Optimizer

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Import agent classes
# from agents.data_aggregator import DataAggregator
# from agents.researcher import Researcher
from agents.yield_analyst import YieldAnalyst
from agents.risk_manager import RiskManager
from agents.portfolio_manager import PortfolioManager
from agents.execution_agent import ExecutionAgent
# from agents.reporting_agent import ReportingAgent
from tools.fetch_market_data import MarketData
from tools.fetch_wallet_data import WalletData
from tools.send_email import SendEmail

# Import config and utilities
from config.settings import load_config
from utils.logger import setup_logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DeFi Portfolio Optimizer")
    
    parser.add_argument("--api-url", default="http://localhost:3001/current_markets", 
                      help="API URL for market data")
    # parser.add_argument("--wallet-address", default=DEFAULT_WALLET_ADDRESS, required=True,
    #                   help="Wallet address to analyze")
    parser.add_argument("--output-dir", default="outputs",
                      help="Directory for output files")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug logging")
    
    return parser.parse_args()

def setup_environment(args):
    """Set up the execution environment."""
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger("defi_optimizer", log_level)
    
    # Create output directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(args.output_dir) / timestamp
    
    data_dir = run_dir / "data"
    analysis_dir = run_dir / "analysis"
    recommendations_dir = run_dir / "recommendation"
    
    for directory in [data_dir, analysis_dir, recommendations_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Load configuration
    config = load_config()
    
    return {
        "logger": logger,
        "config": config,
        "dirs": {
            "run": str(run_dir),
            "data": str(data_dir),
            "analysis": str(analysis_dir),
            "recommendations": str(recommendations_dir)
        }
    }

def get_risk_tolerance():
    """
    Collect risk tolerance from the user and store it as a global variable.
    
    Returns:
        str: The user's risk tolerance level
    """
    
    # Request risk tolerance from the user
    user_input = input("Please enter your risk tolerance (low, medium, high): ").strip().lower()
    print(f"Setting risk tolerance to: {user_input}")
    
    # Validate risk tolerance input
    if user_input not in ['low', 'medium', 'high']:
        raise ValueError("Risk tolerance must be one of: 'low', 'medium', 'high'")
    
    # Store in global variable
    return user_input
    
def main():
    """Main execution function."""
    args = parse_arguments()

    # Requests inputs for analysis
    # Request wallet id (placeholder)

    # Request risk tolerance from the user
    risk_tolerance_input = get_risk_tolerance()

    try:
        # Set up environment
        env = setup_environment(args)
        logger = env["logger"]
        
        logger.info("Starting DeFi Portfolio Optimization process")
        
        # Run the pipeline
        md = MarketData()
        market_data = md.fetch_market_data()
        # print(market_data)
        wd = WalletData()
        wallet_data = wd.fetch_wallet_data()
        # print(wallet_data)
        
        # Initialize the YieldAnalyst and pass market data
        yield_analyst = YieldAnalyst(config=env["config"])
        (yield_analysis_results, yield_strategy_results) = yield_analyst.execute_task(market_data)
        print(yield_analysis_results)
        print(yield_strategy_results)
        
        # Initialize the RiskManager and pass analysis results
        risk_manager = RiskManager(config=env["config"])
        risk_analysis_results = risk_manager.execute_task(
            market_data, 
            wallet_data, 
            yield_strategy_results, 
            risk_tolerance_input
        )
        print(risk_analysis_results)

        # Initialize the PortfolioManager and pass analysis results
        portfolio_manager = PortfolioManager(config=env["config"])
        (optimized_portfolio, final_recc_to_execute) = portfolio_manager.execute_task(
            market_data, 
            wallet_data, 
            yield_analysis_results, 
            yield_strategy_results, 
            risk_analysis_results,
            risk_tolerance_input
        )
        print(optimized_portfolio)
        print(final_recc_to_execute)

        # Initialize the ExecutionAgent and pass final reccomendation
        execution_agent = ExecutionAgent(config=env["config"])
        execution_plan = execution_agent.execute_task(
            wallet_data, 
            final_recc_to_execute
        )
        print(wallet_data)
        print(final_recc_to_execute)
        print(execution_plan)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # using SendGrid's Python Library
        # https://github.com/sendgrid/sendgrid-python
        output= f"""
        Market Data: {market_data}
        Wallet Data: {wallet_data}
        Yield Analysis Results: {yield_analysis_results}
        Yield Strategy Results: {yield_strategy_results}
        Risk Analysis Results: {risk_analysis_results}
        Optimized Portfolio: {optimized_portfolio}
        Final Recommendations: {final_recc_to_execute}
        Execution Plan: {execution_plan}
        """
        SendEmail().send_full_analysis(output, 'carly@ambush.capital', current_time)
        
        # Print summary
        # logger.info(f"Portfolio optimization completed successfully")
        # logger.info(f"Final report available at: {report_paths['final_report_path']}")
        # logger.info(f"Portfolio recommendation available at: {portfolio_paths['portfolio_recommendation_path']}")
        # logger.info(f"Execution plan available at: {execution_paths['execution_plan_path']}")
        
        # print("\n" + "="*80)
        # print("DeFi Portfolio Optimization Completed Successfully")
        # print("="*80)
        # print(f"Final report: {report_paths['final_report_path']}")
        # print(f"Portfolio recommendation: {portfolio_paths['portfolio_recommendation_path']}")
        # print(f"Execution plan: {execution_paths['execution_plan_path']}")
        # print("="*80 + "\n")
        
        return 0
        

        
        # Print summary
        # logger.info(f"Portfolio optimization completed successfully")
        # logger.info(f"Final report available at: {report_paths['final_report_path']}")
        # logger.info(f"Portfolio recommendation available at: {portfolio_paths['portfolio_recommendation_path']}")
        # logger.info(f"Execution plan available at: {execution_paths['execution_plan_path']}")
        
        # print("\n" + "="*80)
        # print("DeFi Portfolio Optimization Completed Successfully")
        # print("="*80)
        # print(f"Final report: {report_paths['final_report_path']}")
        # print(f"Portfolio recommendation: {portfolio_paths['portfolio_recommendation_path']}")
        # print(f"Execution plan: {execution_paths['execution_plan_path']}")
        # print("="*80 + "\n")
        
        return 0
        
    except Exception as e:
        if 'logger' in locals():
            logger.exception("Portfolio optimization failed")
        else:
            print(f"Error: {str(e)}")
        return 1


# Run the main function
if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
