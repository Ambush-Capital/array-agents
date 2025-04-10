# api_server.py - DeFi Portfolio Optimizer API Server

import logging
from flask import Flask, request, jsonify
from utils.logger import setup_logger

# Import api_main function
from api.api_main import api_main

# Create Flask app
app = Flask(__name__)

# Configure logging
logger = setup_logger("defi_optimizer_api", logging.INFO)

@app.route('/analyze/<wallet_id>', methods=['GET'])
def analyze_wallet(wallet_id):
    """
    API endpoint to analyze a wallet with specified risk level and email.
    
    URL format: /analyze/<wallet_id>?risk_level=<risk_level>&email=<email>
    
    Args:
        wallet_id (str): The wallet ID to analyze
        
    Query Parameters:
        risk_level (str): Risk tolerance level (low, medium, high)
        email (str): Email address to send the analysis results to
        
    Returns:
        JSON: Analysis results
    """
    risk_level = request.args.get('risk_level', 'medium')
    email = request.args.get('email', '')
    
    result = api_main(wallet_id, risk_level, email)
    
    # Check if result is an error response
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], dict) and 'error' in result[0]:
        return jsonify(result[0]), result[1]
    
    return jsonify(result)

if __name__ == "__main__":
    # Run the Flask app
    print("Starting DeFi Portfolio Optimizer API server on http://0.0.0.0:5001")
    print("API endpoint available at: /analyze/<wallet_id>?risk_level=<low|medium|high>&email=<email_address>")
    app.run(host='0.0.0.0', port=5001, debug=True)