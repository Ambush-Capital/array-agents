import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
import requests
from pydantic import BaseModel, Field
from typing import Dict, Any

class SendEmail(BaseModel):
    current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_data(self, data: Any) -> str:
        """Format data for email display"""
        if isinstance(data, (dict, list)):
            return str(data).replace('{', '').replace('}', '').replace('[', '').replace(']', '')
        return str(data)

    def send_full_analysis(self, output: Dict[str, Any], recipient_email: str):
        # CSS styles for email
        styles = """
            <style>
                .container { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .section { margin-bottom: 30px; }
                .section-title { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
                .content { background-color: #ffffff; padding: 15px; border-radius: 5px; border: 1px solid #eee; }
                .timestamp { color: #666; font-size: 0.9em; }
                pre { white-space: pre-wrap; word-wrap: break-word; }
            </style>
        """

        # Email content
        html_content = f"""
        <div class="container">
            <div class="header">
                <h1>Array Portfolio Analysis Report</h1>
                <p class="timestamp">Generated on {self.current_time}</p>
            </div>

            <div class="section">
                <h2 class="section-title">Market Data</h2>
                <div class="content">
                    <pre>{self._format_data(output.get('market_data', 'No data available'))}</pre>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">Wallet Analysis</h2>
                <div class="content">
                    <pre>{self._format_data(output.get('wallet_data', 'No data available'))}</pre>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">Yield Analysis</h2>
                <div class="content">
                    <h3>Analysis Results</h3>
                    <pre>{self._format_data(output.get('yield_analysis', 'No data available'))}</pre>
                    <h3>Strategy</h3>
                    <pre>{self._format_data(output.get('yield_strategy', 'No data available'))}</pre>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">Risk Analysis</h2>
                <div class="content">
                    <pre>{self._format_data(output.get('risk_analysis', 'No data available'))}</pre>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">Portfolio Optimization</h2>
                <div class="content">
                    <pre>{self._format_data(output.get('optimized_portfolio', 'No data available'))}</pre>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">Recommendations</h2>
                <div class="content">
                    <pre>{self._format_data(output.get('recommendations', 'No data available'))}</pre>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">Execution Plan</h2>
                <div class="content">
                    <pre>{self._format_data(output.get('execution_plan', 'No data available'))}</pre>
                </div>
            </div>
        </div>
        """

        message = Mail(
            from_email='carly@ambush.capital',
            to_emails=recipient_email,
            subject=f'Array Portfolio Analysis Report - {self.current_time}',
            html_content=styles + html_content
        )
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"Email sent successfully with status code {response.status_code}")
        except Exception as e:
            print(f"Error sending email: {e}")

if __name__ == "__main__":
    test_data = {
        "market_data": "Test market data",
        "wallet_data": "Test wallet data",
        "yield_analysis": "Test yield analysis",
        "yield_strategy": "Test yield strategy",
        "risk_analysis": "Test risk analysis",
        "optimized_portfolio": "Test portfolio",
        "recommendations": "Test recommendations",
        "execution_plan": "Test plan"
    }
    SendEmail().send_full_analysis(test_data, "mike@ambush.capital")