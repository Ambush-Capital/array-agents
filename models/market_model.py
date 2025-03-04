from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class LendingReserve:
    """Represents a lending reserve within a DeFi lending protocol."""
    protocol_name: str
    market_name: str
    total_supply: str
    total_borrows: str
    supply_rate: str
    supply_rate_7d: Optional[str] = None
    supply_rate_30d: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "protocol_name": self.protocol_name,
            "market_name": self.market_name,
            "total_supply": self.total_supply,
            "total_borrows": self.total_borrows,
            "supply_rate": self.supply_rate
        }
        
        if self.supply_rate_7d:
            result["supply_rate_7d"] = self.supply_rate_7d
            
        if self.supply_rate_30d:
            result["supply_rate_30d"] = self.supply_rate_30d
            
        return result
    
    def get_utilization_rate(self) -> float:
        """Calculate the utilization rate (total_borrows / total_supply)."""
        try:
            total_supply = float(self.total_supply)
            total_borrows = float(self.total_borrows)
            
            if total_supply == 0:
                return 0.0
                
            return total_borrows / total_supply
        except (ValueError, TypeError):
            return 0.0


@dataclass
class MarketData:
    """Represents market data for a specific token."""
    name: str
    symbol: str
    market_price_sf: int
    mint: str
    lending_reserves: List[LendingReserve]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketData':
        """Create a MarketData instance from a dictionary."""
        reserves = []
        
        for reserve_data in data.get("lending_reserves", []):
            reserve = LendingReserve(
                protocol_name=reserve_data["protocol_name"],
                market_name=reserve_data["market_name"],
                total_supply=reserve_data["total_supply"],
                total_borrows=reserve_data["total_borrows"],
                supply_rate=reserve_data["supply_rate"],
                supply_rate_7d=reserve_data.get("supply_rate_7d"),
                supply_rate_30d=reserve_data.get("supply_rate_30d")
            )
            reserves.append(reserve)
        
        return cls(
            name=data["name"],
            symbol=data["symbol"],
            market_price_sf=data["market_price_sf"],
            mint=data["mint"],
            lending_reserves=reserves
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "symbol": self.symbol,
            "market_price_sf": self.market_price_sf,
            "mint": self.mint,
            "lending_reserves": [reserve.to_dict() for reserve in self.lending_reserves]
        }


class MarketDataManager:
    """Simple manager for handling market data."""
    
    def __init__(self):
        self.market_data_list: List[MarketData] = []
    
    def load_from_json(self, json_data: str) -> None:
        """Load market data from JSON string."""
        data = json.loads(json_data)
        self.market_data_list = []
        
        for item in data:
            market_data = MarketData.from_dict(item)
            self.market_data_list.append(market_data)
    
    def to_json(self) -> str:
        """Convert all market data to a JSON string."""
        data = [market.to_dict() for market in self.market_data_list]
        return json.dumps(data, indent=2)