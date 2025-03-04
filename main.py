# main.py - DeFi Portfolio Optimizer

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path

# Import agent classes
from agents.data_aggregator import DataAggregator
from agents.researcher import Researcher
from agents.yield_analyst import YieldAnalyst
from agents.risk_manager import RiskManager
from agents.portfolio_manager import PortfolioManager
from agents.execution_agent import ExecutionAgent
from agents.reporting_agent import ReportingAgent

# Import config and utilities
from config.settings import load_config
from utils.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DeFi Portfolio Optimizer")
    
    parser.add_argument("--api-url", default="http://localhost:3001/current_markets", 
                      help="API URL for market data")
    parser.add_argument("--wallet-address", required=True,
                      help="Wallet address to analyze")
    parser.add_argument("--risk-level", default="medium", choices=["low", "medium", "high"],
                      help="Risk tolerance level")
    parser.add_argument("--output-dir", default="outputs",
                      help="Directory for output files")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug logging")
    
    return parser.parse_args()


def setup_environment(args):
    """Set up the execution environment."""
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(log_level)
    
    # Create output directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(args.output_dir) / timestamp
    
    data_dir = run_dir / "data"
    analysis_dir = run_dir / "analysis"
    recommendations_dir = run_dir / "recommendations"
    reports_dir = run_dir / "reports"
    
    for directory in [data_dir, analysis_dir, recommendations_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Load configuration
    config = load_config(args.risk_level)
    
    return {
        "logger": logger,
        "config": config,
        "dirs": {
            "run": str(run_dir),
            "data": str(data_dir),
            "analysis": str(analysis_dir),
            "recommendations": str(recommendations_dir),
            "reports": str(reports_dir)
        }
    }


def run_data_aggregation(env, args):
    """Run the data aggregation process."""
    logger = env["logger"]
    logger.info("Starting data aggregation")
    
    data_aggregator = DataAggregator(config=env["config"])
    
    result = data_aggregator.execute_task({
        "task_type": "aggregate_all_data",
        "api_url": args.api_url,
        "wallet_address": args.wallet_address,
        "output_dir": env["dirs"]["data"],
        "timestamp": datetime.now().isoformat()
    })
    
    if "error" in result:
        logger.error(f"Data aggregation failed: {result['error']}")
        raise Exception(f"Data aggregation failed: {result['error']}")
    
    logger.info("Data aggregation completed successfully")
    return result["data"]


def run_research(env, data_paths):
    """Run the research process."""
    logger = env["logger"]
    logger.info("Starting market research")
    
    researcher = Researcher(config=env["config"])
    
    result = researcher.execute_task({
        "task_type": "market_research",
        "protocol_names": ["marginfi", "kamino", "drift", "solend"],
        "output_format": "markdown",
        "output_path": f"{env['dirs']['analysis']}/market_research.md"
    })
    
    if "error" in result:
        logger.error(f"Market research failed: {result['error']}")
        raise Exception(f"Market research failed: {result['error']}")
    
    logger.info("Market research completed successfully")
    return {
        "research_path": f"{env['dirs']['analysis']}/market_research.md"
    }


def run_yield_analysis(env, data_paths):
    """Run the yield analysis process."""
    logger = env["logger"]
    logger.info("Starting yield analysis")
    
    yield_analyst = YieldAnalyst(config=env["config"])
    
    # First, analyze yields
    analysis_result = yield_analyst.execute_task({
        "task_type": "yield_analysis",
        "market_data_path": data_paths["market_data_path"],
        "output_format": "markdown",
        "output_path": f"{env['dirs']['analysis']}/yield_analysis.md"
    })
    
    if "error" in analysis_result:
        logger.error(f"Yield analysis failed: {analysis_result['error']}")
        raise Exception(f"Yield analysis failed: {analysis_result['error']}")
    
    # Then, generate yield strategy
    strategy_result = yield_analyst.execute_task({
        "task_type": "yield_strategy",
        "market_data_path": data_paths["market_data_path"],
        "wallet_data_path": data_paths["wallet_data_path"],
        "output_format": "json",
        "output_path": f"{env['dirs']['recommendations']}/yield_strategy.json"
    })
    
    if "error" in strategy_result:
        logger.error(f"Yield strategy generation failed: {strategy_result['error']}")
        raise Exception(f"Yield strategy generation failed: {strategy_result['error']}")
    
    logger.info("Yield analysis and strategy generation completed successfully")
    return {
        "yield_analysis_path": f"{env['dirs']['analysis']}/yield_analysis.md",
        "yield_strategy_path": f"{env['dirs']['recommendations']}/yield_strategy.json"
    }


def run_risk_assessment(env, data_paths):
    """Run the risk assessment process."""
    logger = env["logger"]
    logger.info("Starting risk assessment")
    
    risk_manager = RiskManager(config=env["config"])
    
    # Assess current portfolio risks
    assessment_result = risk_manager.execute_task({
        "task_type": "risk_assessment",
        "market_data_path": data_paths["market_data_path"],
        "wallet_data_path": data_paths["wallet_data_path"],
        "output_format": "markdown",
        "output_path": f"{env['dirs']['analysis']}/risk_assessment.md"
    })
    
    if "error" in assessment_result:
        logger.error(f"Risk assessment failed: {assessment_result['error']}")
        raise Exception(f"Risk assessment failed: {assessment_result['error']}")
    
    # Generate risk-adjusted strategy
    strategy_result = risk_manager.execute_task({
        "task_type": "risk_adjusted_strategy",
        "market_data_path": data_paths["market_data_path"],
        "wallet_data_path": data_paths["wallet_data_path"],
        "yield_strategy_path": data_paths["yield_strategy_path"],
        "output_format": "json",
        "output_path": f"{env['dirs']['recommendations']}/risk_adjusted_strategy.json"
    })
    
    if "error" in strategy_result:
        logger.error(f"Risk-adjusted strategy generation failed: {strategy_result['error']}")
        raise Exception(f"Risk-adjusted strategy generation failed: {strategy_result['error']}")
    
    logger.info("Risk assessment and strategy adjustment completed successfully")
    return {
        "risk_assessment_path": f"{env['dirs']['analysis']}/risk_assessment.md",
        "risk_adjusted_strategy_path": f"{env['dirs']['recommendations']}/risk_adjusted_strategy.json"
    }


def run_portfolio_optimization(env, data_paths):
    """Run the portfolio optimization process."""
    logger = env["logger"]
    logger.info("Starting portfolio optimization")
    
    portfolio_manager = PortfolioManager(config=env["config"])
    
    result = portfolio_manager.execute_task({
        "task_type": "portfolio_optimization",
        "market_data_path": data_paths["market_data_path"],
        "wallet_data_path": data_paths["wallet_data_path"],
        "yield_strategy_path": data_paths["yield_strategy_path"],
        "risk_adjusted_strategy_path": data_paths["risk_adjusted_strategy_path"],
        "research_path": data_paths["research_path"],
        "output_format": "json",
        "output_path": f"{env['dirs']['recommendations']}/portfolio_recommendation.json"
    })
    
    if "error" in result:
        logger.error(f"Portfolio optimization failed: {result['error']}")
        raise Exception(f"Portfolio optimization failed: {result['error']}")
    
    logger.info("Portfolio optimization completed successfully")
    return {
        "portfolio_recommendation_path": f"{env['dirs']['recommendations']}/portfolio_recommendation.json"
    }


def run_execution_planning(env, data_paths):
    """Run the execution planning process."""
    logger = env["logger"]
    logger.info("Starting execution planning")
    
    execution_agent = ExecutionAgent(config=env["config"])
    
    result = execution_agent.execute_task({
        "task_type": "create_execution_plan",
        "wallet_data_path": data_paths["wallet_data_path"],
        "portfolio_recommendation_path": data_paths["portfolio_recommendation_path"],
        "output_format": "json",
        "output_path": f"{env['dirs']['recommendations']}/execution_plan.json"
    })
    
    if "error" in result:
        logger.error(f"Execution planning failed: {result['error']}")
        raise Exception(f"Execution planning failed: {result['error']}")
    
    logger.info("Execution planning completed successfully")
    return {
        "execution_plan_path": f"{env['dirs']['recommendations']}/execution_plan.json"
    }


def generate_final_report(env, data_paths):
    """Generate the final report."""
    logger = env["logger"]
    logger.info("Generating final report")
    
    reporting_agent = ReportingAgent(config=env["config"])
    
    result = reporting_agent.execute_task({
        "task_type": "generate_report",
        "data_paths": data_paths,
        "output_format": "markdown",
        "output_path": f"{env['dirs']['reports']}/final_report.md"
    })
    
    if "error" in result:
        logger.error(f"Report generation failed: {result['error']}")
        raise Exception(f"Report generation failed: {result['error']}")
    
    logger.info("Final report generated successfully")
    return {
        "final_report_path": f"{env['dirs']['reports']}/final_report.md"
    }


def main():
    """Main execution function."""
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Set up environment
        env = setup_environment(args)
        logger = env["logger"]
        
        logger.info("Starting DeFi Portfolio Optimization process")
        
        # Run the pipeline
        data_paths = run_data_aggregation(env, args)
        
        research_paths = run_research(env, data_paths)
        data_paths.update(research_paths)
        
        yield_paths = run_yield_analysis(env, data_paths)
        data_paths.update(yield_paths)
        
        risk_paths = run_risk_assessment(env, data_paths)
        data_paths.update(risk_paths)
        
        portfolio_paths = run_portfolio_optimization(env, data_paths)
        data_paths.update(portfolio_paths)
        
        execution_paths = run_execution_planning(env, data_paths)
        data_paths.update(execution_paths)
        
        report_paths = generate_final_report(env, data_paths)
        data_paths.update(report_paths)
        
        # Print summary
        logger.info(f"Portfolio optimization completed successfully")
        logger.info(f"Final report available at: {report_paths['final_report_path']}")
        logger.info(f"Portfolio recommendation available at: {portfolio_paths['portfolio_recommendation_path']}")
        logger.info(f"Execution plan available at: {execution_paths['execution_plan_path']}")
        
        print("\n" + "="*80)
        print("DeFi Portfolio Optimization Completed Successfully")
        print("="*80)
        print(f"Final report: {report_paths['final_report_path']}")
        print(f"Portfolio recommendation: {portfolio_paths['portfolio_recommendation_path']}")
        print(f"Execution plan: {execution_paths['execution_plan_path']}")
        print("="*80 + "\n")
        
        return 0
        
    except Exception as e:
        if 'logger' in locals():
            logger.exception("Portfolio optimization failed")
        else:
            print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)