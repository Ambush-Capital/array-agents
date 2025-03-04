from typing import List, Dict, Any, Union
from dataclasses import dataclass
from decimal import Decimal
import json

@dataclass
class WalletBalance:
    """Represents a token balance in a wallet."""
    symbol: str
    amount: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "symbol": self.symbol,
            "amount": self.amount
        }


@dataclass
class WalletPosition:
    """Represents a DeFi position in a lending protocol."""
    symbol: str
    protocol_name: str
    market_name: str
    amount: str
    obligation_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "symbol": self.symbol,
            "protocol_name": self.protocol_name,
            "market_name": self.market_name,
            "amount": self.amount,
            "obligation_type": self.obligation_type
        }


class WalletData:
    """Container for wallet data including balances and positions."""
    
    def __init__(self):
        self.wallet_balances: List[WalletBalance] = []
        self.wallet_positions: List[WalletPosition] = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WalletData':
        """Create a WalletData instance from a dictionary."""
        wallet_data = cls()
        
        # Add balances
        for balance_data in data.get("wallet_balances", []):
            balance = WalletBalance(
                symbol=balance_data["symbol"],
                amount=balance_data["amount"]
            )
            wallet_data.wallet_balances.append(balance)
        
        # Add positions
        for position_data in data.get("wallet_positions", []):
            position = WalletPosition(
                symbol=position_data["symbol"],
                protocol_name=position_data["protocol_name"],
                market_name=position_data["market_name"],
                amount=position_data["amount"],
                obligation_type=position_data["obligation_type"]
            )
            wallet_data.wallet_positions.append(position)
            
        return wallet_data
    
    @classmethod
    def from_json(cls, json_data: str) -> 'WalletData':
        """Create a WalletData instance from a JSON string."""
        data = json.loads(json_data)
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the wallet data to a dictionary."""
        return {
            "wallet_balances": [balance.to_dict() for balance in self.wallet_balances],
            "wallet_positions": [position.to_dict() for position in self.wallet_positions]
        }
    
    def to_json(self) -> str:
        """Convert the wallet data to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def get_total_portfolio_value(self) -> Decimal:
        """
        Calculate the total portfolio value including positions and balances.
        
        Returns:
            Total value as Decimal
        """
        total = Decimal('0')
        
        # Add value from positions
        for position in self.wallet_positions:
            total += Decimal(position.amount)
        
        # Add value from balances
        for balance in self.wallet_balances:
            total += Decimal(balance.amount)
            
        return total
    
    def get_allocation_percentages(self) -> List[Dict[str, Any]]:
        """
        Calculate the percentage allocation of each position and balance
        relative to the total portfolio value.
        
        Returns:
            List of dictionaries with allocation details and percentages
        """
        total_value = self.get_total_portfolio_value()
        
        # Handle case where portfolio is empty
        if total_value == 0:
            return []
        
        allocations = []
        
        # Add position allocations
        for position in self.wallet_positions:
            amount = Decimal(position.amount)
            percentage = (amount / total_value) * 100
            
            allocations.append({
                "type": "position",
                "symbol": position.symbol,
                "protocol_name": position.protocol_name,
                "market_name": position.market_name,
                "amount": position.amount,
                "obligation_type": position.obligation_type,
                "percentage": round(float(percentage), 2)
            })
        
        # Add balance allocations
        for balance in self.wallet_balances:
            amount = Decimal(balance.amount)
            percentage = (amount / total_value) * 100
            
            allocations.append({
                "type": "balance",
                "symbol": balance.symbol,
                "amount": balance.amount,
                "percentage": round(float(percentage), 2)
            })
        
        # Sort by percentage (descending)
        return sorted(allocations, key=lambda x: x["percentage"], reverse=True)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the wallet data with allocation percentages.
        
        Returns:
            Dictionary with total value and allocation details
        """
        total_value = self.get_total_portfolio_value()
        allocations = self.get_allocation_percentages()
        
        # Calculate total allocated vs unallocated
        allocated_sum = sum(
            Decimal(item["percentage"]) for item in allocations 
            if item["type"] == "position"
        )
        unallocated_sum = sum(
            Decimal(item["percentage"]) for item in allocations 
            if item["type"] == "balance"
        )
        
        # Calculate protocol allocations
        protocol_allocations = {}
        for item in allocations:
            if item["type"] == "position":
                protocol = item["protocol_name"]
                if protocol not in protocol_allocations:
                    protocol_allocations[protocol] = 0
                protocol_allocations[protocol] += item["percentage"]
        
        return {
            "total_value": str(total_value),
            "allocated_percentage": round(float(allocated_sum), 2),
            "unallocated_percentage": round(float(unallocated_sum), 2),
            "protocol_allocations": protocol_allocations,
            "detailed_allocations": allocations
        }