# Trading Strategies AI

This project uses AI agents to develop and execute trading strategies based on raw CSV data files.

## Directory Structure

- `data/`: Contains all data-related files.
  - `market_data/`: Contains raw CSV data files with lending market data.
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