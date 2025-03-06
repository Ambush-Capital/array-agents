"""
Portfolio Reporting Agent

This module implements a reporting agent for DeFi lending portfolios, responsible for:
- Generating detailed portfolio reports based on aggregated data
- Calculating performance metrics and returns
- Creating visualizations of portfolio composition and performance
- Providing insights on portfolio allocation and historical trends
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Optional, Union, Any

class PortfolioReportingAgent:
    """
    A class that handles the reporting and analysis of DeFi lending portfolios.
    
    Responsibilities:
    - Generate detailed reports on portfolio composition, performance, and risk metrics
    - Calculate key performance indicators (KPIs) and returns
    - Create visualizations for portfolio analysis
    - Track historical performance and compare against benchmarks
    """
    
    def __init__(self, data_source_path: str = None):
        """
        Initialize the Portfolio Reporting Agent.
        
        Args:
            data_source_path (str, optional): Path to the data source file. Defaults to None.
        """
        self.data_source_path = data_source_path
        self.portfolio_data = None
        self.historical_data = None
        self.report_date = datetime.now()
        self.benchmark_data = None
        
    def load_data(self, portfolio_data_path: str = None, historical_data_path: str = None, benchmark_data_path: str = None) -> None:
        """
        Load portfolio, historical, and benchmark data from specified paths.
        
        Args:
            portfolio_data_path (str, optional): Path to portfolio data. Defaults to None.
            historical_data_path (str, optional): Path to historical data. Defaults to None.
            benchmark_data_path (str, optional): Path to benchmark data. Defaults to None.
        """
        if portfolio_data_path:
            self.portfolio_data = pd.read_json(portfolio_data_path)
        
        if historical_data_path:
            self.historical_data = pd.read_json(historical_data_path)
            
        if benchmark_data_path:
            self.benchmark_data = pd.read_json(benchmark_data_path)
    
    def calculate_portfolio_metrics(self) -> Dict[str, float]:
        """
        Calculate key portfolio metrics including total value, allocation percentages,
        and performance metrics.
        
        Returns:
            Dict[str, float]: Dictionary containing portfolio metrics
        """
        if self.portfolio_data is None:
            raise ValueError("Portfolio data must be loaded before calculating metrics")
        
        metrics = {}
        
        # Total value metrics
        metrics['total_value'] = self.portfolio_data['value'].sum()
        
        # Calculate allocation percentages
        allocation = self.portfolio_data.groupby('protocol')['value'].sum() / metrics['total_value'] * 100
        metrics['protocol_allocation'] = allocation.to_dict()
        
        # Calculate asset allocation percentages
        asset_allocation = self.portfolio_data.groupby('asset')['value'].sum() / metrics['total_value'] * 100
        metrics['asset_allocation'] = asset_allocation.to_dict()
        
        # Calculate performance metrics if historical data is available
        if self.historical_data is not None:
            # Calculate daily returns
            daily_values = self.historical_data.pivot(index='date', columns='asset', values='value')
            daily_returns = daily_values.pct_change().dropna()
            
            # Calculate portfolio return metrics
            metrics['daily_return'] = daily_returns.mean().mean() * 100
            metrics['annualized_return'] = ((1 + metrics['daily_return']/100) ** 365 - 1) * 100
            metrics['volatility'] = daily_returns.std().mean() * np.sqrt(365) * 100
            metrics['sharpe_ratio'] = metrics['annualized_return'] / metrics['volatility'] if metrics['volatility'] > 0 else 0
            
            # Calculate max drawdown
            cumulative_returns = (1 + daily_returns).cumprod()
            rolling_max = cumulative_returns.cummax()
            drawdowns = (cumulative_returns / rolling_max) - 1
            metrics['max_drawdown'] = drawdowns.min().min() * 100
        
        # Calculate current yield metrics
        metrics['avg_yield'] = self.portfolio_data['yield'].mean()
        metrics['yield_weighted_avg'] = (self.portfolio_data['yield'] * self.portfolio_data['value']).sum() / metrics['total_value']
        
        return metrics
    
    def generate_performance_report(self, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report for the portfolio.
        
        Args:
            lookback_days (int, optional): Number of days to look back for historical analysis. Defaults to 30.
            
        Returns:
            Dict[str, Any]: Report containing portfolio performance data
        """
        if self.portfolio_data is None or self.historical_data is None:
            raise ValueError("Portfolio and historical data must be loaded before generating a report")
            
        # Calculate date range
        end_date = self.report_date
        start_date = end_date - timedelta(days=lookback_days)
        
        # Filter historical data for the lookback period
        period_data = self.historical_data[
            (self.historical_data['date'] >= start_date.strftime('%Y-%m-%d')) & 
            (self.historical_data['date'] <= end_date.strftime('%Y-%m-%d'))
        ]
        
        # Calculate portfolio metrics
        metrics = self.calculate_portfolio_metrics()
        
        # Calculate returns over different time periods
        daily_values = period_data.pivot(index='date', columns='asset', values='value')
        daily_returns = daily_values.pct_change().dropna()
        
        # Create report structure
        report = {
            'report_date': self.report_date.strftime('%Y-%m-%d'),
            'portfolio_value': metrics['total_value'],
            'performance_metrics': {
                'daily_return': metrics['daily_return'],
                'annualized_return': metrics['annualized_return'],
                'volatility': metrics['volatility'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown': metrics['max_drawdown']
            },
            'allocation': {
                'by_protocol': metrics['protocol_allocation'],
                'by_asset': metrics['asset_allocation']
            },
            'yield_metrics': {
                'average_yield': metrics['avg_yield'],
                'weighted_average_yield': metrics['yield_weighted_avg'],
                'yield_by_protocol': self.portfolio_data.groupby('protocol')['yield'].mean().to_dict()
            },
            'historical_performance': {
                'daily_returns': daily_returns.mean(axis=1).to_dict(),
                'cumulative_return': ((1 + daily_returns.mean(axis=1)).cumprod() - 1).iloc[-1] * 100
            }
        }
        
        # Add benchmark comparison if available
        if self.benchmark_data is not None:
            benchmark_period_data = self.benchmark_data[
                (self.benchmark_data['date'] >= start_date.strftime('%Y-%m-%d')) & 
                (self.benchmark_data['date'] <= end_date.strftime('%Y-%m-%d'))
            ]
            benchmark_returns = benchmark_period_data.set_index('date')['value'].pct_change().dropna()
            benchmark_cumulative_return = ((1 + benchmark_returns).cumprod() - 1).iloc[-1] * 100
            
            report['benchmark_comparison'] = {
                'benchmark_return': benchmark_cumulative_return,
                'outperformance': report['historical_performance']['cumulative_return'] - benchmark_cumulative_return
            }
        
        return report
    
    def generate_risk_report(self) -> Dict[str, Any]:
        """
        Generate a risk analysis report for the portfolio.
        
        Returns:
            Dict[str, Any]: Report containing risk analysis data
        """
        if self.portfolio_data is None or self.historical_data is None:
            raise ValueError("Portfolio and historical data must be loaded before generating a risk report")
        
        # Calculate portfolio metrics
        metrics = self.calculate_portfolio_metrics()
        
        # Calculate risk metrics by protocol
        protocol_risk = self.portfolio_data.groupby('protocol').agg({
            'risk_score': 'mean',
            'value': 'sum'
        })
        protocol_risk['allocation_percentage'] = protocol_risk['value'] / protocol_risk['value'].sum() * 100
        
        # Create risk report
        risk_report = {
            'report_date': self.report_date.strftime('%Y-%m-%d'),
            'overall_risk_metrics': {
                'portfolio_volatility': metrics['volatility'],
                'max_drawdown': metrics['max_drawdown'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'weighted_risk_score': (self.portfolio_data['risk_score'] * self.portfolio_data['value']).sum() / metrics['total_value']
            },
            'protocol_risk_analysis': protocol_risk.to_dict(),
            'concentration_risk': {
                'protocol_concentration': self._calculate_herfindahl_index(metrics['protocol_allocation']),
                'asset_concentration': self._calculate_herfindahl_index(metrics['asset_allocation'])
            }
        }
        
        return risk_report
    
    def _calculate_herfindahl_index(self, allocation_dict: Dict[str, float]) -> float:
        """
        Calculate the Herfindahl-Hirschman Index (HHI) to measure concentration.
        Higher values indicate higher concentration (more risk).
        
        Args:
            allocation_dict (Dict[str, float]): Dictionary of allocation percentages
            
        Returns:
            float: HHI value between 0 and 10000
        """
        return sum([(pct/100)**2 for pct in allocation_dict.values()]) * 10000
    
    def generate_visualization(self, report_type: str, output_path: str = None) -> plt.Figure:
        """
        Generate visualization based on the report type.
        
        Args:
            report_type (str): Type of visualization to generate ('allocation', 'performance', 'risk', 'yield')
            output_path (str, optional): Path to save the visualization. Defaults to None.
            
        Returns:
            plt.Figure: Matplotlib figure object
        """
        if self.portfolio_data is None:
            raise ValueError("Portfolio data must be loaded before generating visualizations")
        
        fig = plt.figure(figsize=(12, 8))
        
        if report_type == 'allocation':
            # Create protocol allocation pie chart
            metrics = self.calculate_portfolio_metrics()
            plt.subplot(1, 2, 1)
            plt.pie(metrics['protocol_allocation'].values(), labels=metrics['protocol_allocation'].keys(), autopct='%1.1f%%')
            plt.title('Protocol Allocation')
            
            # Create asset allocation pie chart
            plt.subplot(1, 2, 2)
            plt.pie(metrics['asset_allocation'].values(), labels=metrics['asset_allocation'].keys(), autopct='%1.1f%%')
            plt.title('Asset Allocation')
            
        elif report_type == 'performance' and self.historical_data is not None:
            # Create historical performance line chart
            daily_values = self.historical_data.pivot(index='date', columns='asset', values='value')
            portfolio_value = daily_values.sum(axis=1)
            portfolio_value = portfolio_value / portfolio_value.iloc[0]  # Normalize to starting value
            
            plt.plot(pd.to_datetime(portfolio_value.index), portfolio_value)
            plt.title('Portfolio Value (Normalized)')
            plt.xlabel('Date')
            plt.ylabel('Value (Normalized)')
            plt.grid(True)
            
        elif report_type == 'risk':
            # Create risk heatmap
            risk_data = self.portfolio_data.pivot_table(
                values='risk_score', 
                index='protocol', 
                columns='asset', 
                aggfunc='mean'
            )
            
            sns.heatmap(risk_data, annot=True, cmap='YlOrRd')
            plt.title('Risk Score by Protocol and Asset')
            
        elif report_type == 'yield':
            # Create yield comparison bar chart
            yield_by_protocol = self.portfolio_data.groupby('protocol')['yield'].mean().sort_values(ascending=False)
            
            plt.bar(yield_by_protocol.index, yield_by_protocol.values)
            plt.title('Average Yield by Protocol')
            plt.xlabel('Protocol')
            plt.ylabel('Yield (%)')
            plt.xticks(rotation=45)
            plt.grid(axis='y')
            
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            
        return fig
    
    def export_report(self, report_data: Dict, output_format: str = 'json', output_path: str = None) -> Union[str, None]:
        """
        Export the report data to the specified format.
        
        Args:
            report_data (Dict): Report data to export
            output_format (str, optional): Format to export the report ('json', 'csv', 'html'). Defaults to 'json'.
            output_path (str, optional): Path to save the exported report. Defaults to None.
            
        Returns:
            Union[str, None]: Report string if output_path is None, otherwise None
        """
        if output_format == 'json':
            report_str = json.dumps(report_data, indent=4)
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(report_str)
                return None
            else:
                return report_str
                
        elif output_format == 'csv':
            # Flatten the dictionary for CSV export
            flattened_data = self._flatten_dict(report_data)
            df = pd.DataFrame([flattened_data])
            
            if output_path:
                df.to_csv(output_path, index=False)
                return None
            else:
                return df.to_csv(index=False)
                
        elif output_format == 'html':
            # Create a simple HTML report
            html_parts = ['<html><head><title>Portfolio Report</title></head><body>']
            html_parts.append(f'<h1>Portfolio Report - {report_data["report_date"]}</h1>')
            
            # Add report sections
            for section, data in report_data.items():
                if isinstance(data, dict):
                    html_parts.append(f'<h2>{section.replace("_", " ").title()}</h2>')
                    html_parts.append('<ul>')
                    for key, value in data.items():
                        if isinstance(value, dict):
                            html_parts.append(f'<li>{key.replace("_", " ").title()}:<ul>')
                            for sub_key, sub_value in value.items():
                                html_parts.append(f'<li>{sub_key.replace("_", " ").title()}: {sub_value}</li>')
                            html_parts.append('</ul></li>')
                        else:
                            html_parts.append(f'<li>{key.replace("_", " ").title()}: {value}</li>')
                    html_parts.append('</ul>')
                else:
                    html_parts.append(f'<p><strong>{section.replace("_", " ").title()}:</strong> {data}</p>')
            
            html_parts.append('</body></html>')
            html_report = '\n'.join(html_parts)
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(html_report)
                return None
            else:
                return html_report
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """
        Flatten a nested dictionary structure.
        
        Args:
            d (Dict): Dictionary to flatten
            parent_key (str, optional): Parent key for nested dictionaries. Defaults to ''.
            sep (str, optional): Separator for nested keys. Defaults to '_'.
            
        Returns:
            Dict: Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


# Example usage
if __name__ == "__main__":
    # Create reporting agent
    reporting_agent = PortfolioReportingAgent()
    
    # Load sample data (in a real scenario, this would be actual data)
    # These paths would point to actual data files
    reporting_agent.load_data(
        portfolio_data_path="sample_data/portfolio_data.json",
        historical_data_path="sample_data/historical_data.json",
        benchmark_data_path="sample_data/benchmark_data.json"
    )
    
    # Generate performance report
    performance_report = reporting_agent.generate_performance_report(lookback_days=30)
    
    # Generate risk report
    risk_report = reporting_agent.generate_risk_report()
    
    # Create visualizations
    performance_fig = reporting_agent.generate_visualization('performance', 'reports/performance_chart.png')
    allocation_fig = reporting_agent.generate_visualization('allocation', 'reports/allocation_chart.png')
    
    # Export reports
    reporting_agent.export_report(performance_report, 'json', 'reports/performance_report.json')
    reporting_agent.export_report(risk_report, 'html', 'reports/risk_report.html')
    
    print("Portfolio reports generated successfully!")