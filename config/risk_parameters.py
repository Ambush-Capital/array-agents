risk_parameters = {
    "max_exposure_risk_low": 0.2,  # Max exposure per protocol as a fraction of total assets in low risk
    "max_exposure_risk_medium": 0.4,  # Max exposure per protocol as a fraction of total assets in medium risk
    "max_exposure_risk_high": 0.6,  # Max exposure per protocol as a fraction of total assets in high risk
}

operational_rules = {
    "min_yield": 4.0,         # Minimum acceptable yield percentage
    "max_positions": 5.0,     # Maximum number of positions > $1000
    "min_position_size": 1.0,  # Rule to not close a position
    "min_position_allocation": .10  # Rule to hold very small positions
}