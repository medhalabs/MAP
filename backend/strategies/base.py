"""
Base strategy interface.

Strategies are stateless functions that:
- Accept market data + config
- Return trade intent (not orders)
- Never talk to broker directly
- Are reusable for backtesting, paper trading, and live trading
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketData:
    """Market data for strategy execution."""
    symbol: str
    exchange: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    # Additional indicators can be added here


@dataclass
class TradeIntent:
    """
    Trade intent emitted by strategy.
    
    This is NOT an order - it's the strategy's intent.
    The trading engine will convert this to orders after risk validation.
    """
    symbol: str
    exchange: str
    transaction_type: str  # "BUY" or "SELL"
    quantity: int
    intended_price: Optional[Decimal] = None  # None for market orders
    product_type: str = "INTRADAY"
    order_type: str = "MARKET"  # "MARKET" or "LIMIT"
    reason: Optional[str] = None  # Strategy's reason for this trade


@dataclass
class StrategyState:
    """
    Strategy state (managed by trading engine, not strategy itself).
    
    Strategies should be stateless, but the engine maintains state
    for position tracking, indicators, etc.
    """
    positions: Dict[str, int]  # symbol -> quantity
    indicators: Dict[str, Any]  # Strategy-specific indicators
    last_signals: List[TradeIntent]  # Recent signals
    config: Dict[str, Any]  # Strategy configuration


class BaseStrategy(ABC):
    """
    Base class for all strategies.
    
    Strategies must be stateless and return trade intents.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration.
        
        Args:
            config: Strategy-specific configuration
        """
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def on_candle_close(
        self,
        market_data: MarketData,
        state: StrategyState,
    ) -> List[TradeIntent]:
        """
        Called when a candle closes.
        
        Args:
            market_data: Market data for the closed candle
            state: Current strategy state
            
        Returns:
            List of TradeIntent objects (can be empty)
        """
        pass
    
    @abstractmethod
    def on_indicator_signal(
        self,
        signal: Dict[str, Any],
        state: StrategyState,
    ) -> List[TradeIntent]:
        """
        Called when an indicator emits a signal.
        
        Args:
            signal: Indicator signal data
            state: Current strategy state
            
        Returns:
            List of TradeIntent objects (can be empty)
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate strategy configuration.
        
        Returns:
            True if config is valid
        """
        return True
    
    def get_required_indicators(self) -> List[str]:
        """
        Return list of required indicators for this strategy.
        
        Returns:
            List of indicator names
        """
        return []


class StrategyRegistry:
    """Registry for strategy classes."""
    
    _strategies: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, strategy_class: type):
        """Register a strategy class."""
        cls._strategies[name] = strategy_class
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Get a strategy class by name."""
        return cls._strategies.get(name)
    
    @classmethod
    def list_all(cls) -> List[str]:
        """List all registered strategy names."""
        return list(cls._strategies.keys())

