import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_RISK_LEVEL = "medium"

def load_config(risk_level=DEFAULT_RISK_LEVEL):
    """
    Load configuration based on the specified risk level.
    
    Args:
        risk_level (str): Risk level - 'low', 'medium', or 'high'
        
    Returns:
        dict: Configuration dictionary with risk parameters and operational rules
    """
    # Validate risk level input
    if risk_level not in ['low', 'medium', 'high']:
        raise ValueError("Risk level must be one of: 'low', 'medium', 'high'")
    
    # Risk parameters
    max_exposure_risk_low = 0.2
    max_exposure_risk_medium = 0.4
    max_exposure_risk_high = 0.6
    
    # Operational rules
    min_yield = 4.0
    max_positions = 5.0
    min_position_size = 1.0
    
    # Create the configuration dictionary
    config = {
        'risk_parameters': {
            'max_exposure_risk_low': max_exposure_risk_low,
            'max_exposure_risk_medium': max_exposure_risk_medium,
            'max_exposure_risk_high': max_exposure_risk_high,
            'current_risk': risk_level
        },
        'operational_rules': {
            'min_yield': min_yield,
            'max_positions': max_positions,
            'min_position_size': min_position_size
        },
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')  # Add the API key to the config
    }
    
    return config