# Trading Strategies AI

This project uses AI agents to develop and execute trading strategies based on raw CSV data files.

## Directory Structure

- `data/`: Contains all data-related files.
  - `wallet_data/`: Contains raw CSV data files with current wallet positions.
- `src/`: Contains all source code files.
  - `data_processing.py`: Script for processing raw data.
  - `strategy_generation.py`: Script for generating trading strategies using LLMs.
  - `strategy_evaluation.py`: Script for evaluating trading strategies.
  - `strategy_execution.py`: Script for executing trading strategies.
  - `utils.py`: Utility functions used across the project.
- `tests/`: Contains all test files.
  - `test_data_processing.py`: Unit tests for data processing.
  - `test_strategy_generation.py`: Unit tests for strategy generation.
  - `test_strategy_evaluation.py`: Unit tests for strategy evaluation.
  - `test_strategy_execution.py`: Unit tests for strategy execution.
- `requirements.txt`: Lists all project dependencies.

## Market Data Management

The project includes a `MarketData` class for handling market data operations. This class is responsible for fetching and managing market data from the API.

### MarketData Class Usage

```python
from agents.fetch_market_data import MarketData

# Initialize the MarketData object
market_data = MarketData()

# Fetch market data from API
api_url = "http://localhost:3001/current_markets"
market_data.fetch_market_data(api_url)

# Access the stored market data
data = market_data.get_market_data()
```

## Directory Structure

- `agents/`: Contains agent-related code
  - `fetch_market_data.py`: Contains the MarketData class for market data operations
- `data/`: Contains all data-related files
  - `market_data/`: Contains market data files
  - `wallet_data/`: Contains raw CSV data files with current wallet positions
- `src/`: Contains all source code files.
  - `data_processing.py`: Script for processing raw data.
  - `strategy_generation.py`: Script for generating trading strategies using LLMs.
  - `strategy_evaluation.py`: Script for evaluating trading strategies.
  - `strategy_execution.py`: Script for executing trading strategies.
  - `utils.py`: Utility functions used across the project.
- `tests/`: Contains all test files.
  - `test_data_processing.py`: Unit tests for data processing.
  - `test_strategy_generation.py`: Unit tests for strategy generation.
  - `test_strategy_evaluation.py`: Unit tests for strategy evaluation.
  - `test_strategy_execution.py`: Unit tests for strategy execution.
- `requirements.txt`: Lists all project dependencies.



- Using a virtual environment
    - Create environment (new project)
        * python -m venv env (in project directory)
    - Activate
        - source env/bin/activate
    - Deactivate
        - deactivate

#Step 1: Create a virtual environment  
- python -m venv env (create)
- source env/bin/activate (activate)
#Step 2: Initialize all the shit
- pip install -r requirements.txt
#