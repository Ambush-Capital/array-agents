# Trading Strategies AI

This project uses AI agents to develop and execute trading strategies based on raw CSV data files.

## Project Structure

```
brains-py/
├── agents/                      # Agent modules for different analysis tasks
│   ├── __init__.py
│   ├── base_agent.py           # Base class for all agents
│   ├── execution_agent.py      # Handles trade execution logic
│   ├── portfolio_manager.py    # Manages portfolio allocation
│   ├── reporting_agent.py      # Generates analysis reports
│   ├── researcher.py           # Conducts market research
│   ├── risk_manager.py         # Analyzes and manages risk
│   └── yield_analyst.py        # Analyzes yield opportunities
│
├── config/                      # Configuration files
│   ├── __init__.py
│   ├── agent_config.py         # Agent-specific configurations
│   ├── risk_parameters.py      # Risk management parameters
│   └── settings.py             # Global settings
│
├── data/                       # Data storage
│   ├── market_data/           # Market-related data
│   ├── reports/               # Generated reports
│   ├── research/              # Research findings
│   └── wallet_data/           # Wallet and portfolio data
│
├── knowledge/                  # Knowledge base
│   ├── __init__.py
│   ├── base_knowledge_source.py
│   └── 2025_Q1_Research.md    # Quarterly research data
│
├── tools/                      # Utility functions and tools
│   ├── fetch_market_data.py   # Market data retrieval
│   ├── fetch_wallet_data.py   # Wallet data retrieval
│   └── send_email.py          # Email notification system
│
├── outputs/                    # Output directory for analysis results
│   └── [timestamp]/           # Timestamped analysis outputs
│       ├── analysis/
│       ├── data/
│       ├── recommendations/
│       └── reports/
│
├── .env                        # Environment variables
├── config.py                   # Root configuration
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
└── LICENSE                    # License information
```

```mermaid
flowchart TD
    User([User]) --> Inputs
    Inputs[/"Inputs:
    - Wallet ID
    - Risk Level
      - Low
      - Med
      - High"/] --> PortfolioManager
    
    Tools["Tools:
    - Fetch Data
    - Send Email
    - Research
    - Call LLM"] -.-> PortfolioManager
    
    subgraph PortfolioManager["Portfolio Team"]
        PM([Portfolio Manager]) 
        YA([Yield Analyst])
        RM([Risk Manager])
    end
    
    Knowledge["Knowledge:
    - Research
    - Past Performance
    - Risk Parameters
    - Op. Rules"] --> PortfolioManager
    
    ArrayDB[(Array DB)] <--> |Market Data| PortfolioManager
    
    ArrayDB <--> |API Calls| PortfolioManager
    
    ArrayDB --> |Wallet Data| PortfolioManager
    
    Kamino[Kamino] --> ArrayDB
    Marginfi[Marginfi] --> ArrayDB
    SAVE[SAVE] --> ArrayDB
    DRIFT[DRIFT] --> ArrayDB
    SOLANA[SOLANA] --> ArrayDB
    
    PortfolioManager --> |Final Recommendation| TransactionSpecialist
    
    TransactionSpecialist([Transaction Specialist])
    
    TransactionSpecialist -.-> SmartContract["Smart Contract"]