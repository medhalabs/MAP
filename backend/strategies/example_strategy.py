"""
Example strategy implementation.

This demonstrates how to create a stateless strategy.
"""

from typing import List
from decimal import Decimal

from strategies.base import (
    BaseStrategy,
    MarketData,
    StrategyState,
    TradeIntent,
)


class SimpleMovingAverageStrategy(BaseStrategy):
    """
    Simple moving average crossover strategy.
    
    Buys when fast MA crosses above slow MA.
    Sells when fast MA crosses below slow MA.
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.fast_period = config.get("fast_period", 10)
        self.slow_period = config.get("slow_period", 20)
        self.quantity = config.get("quantity", 1)
    
    def on_candle_close(
        self,
        market_data: MarketData,
        state: StrategyState,
    ) -> List[TradeIntent]:
        """Generate trade intents based on MA crossover."""
        intents = []
        
        # Get MA values from state (calculated by trading engine)
        fast_ma = state.indicators.get(f"sma_{self.fast_period}")
        slow_ma = state.indicators.get(f"sma_{self.slow_period}")
        prev_fast_ma = state.indicators.get(f"prev_sma_{self.fast_period}")
        prev_slow_ma = state.indicators.get(f"prev_sma_{self.slow_period}")
        
        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return intents
        
        current_position = state.positions.get(market_data.symbol, 0)
        
        # Bullish crossover: fast MA crosses above slow MA
        if prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma:
            if current_position <= 0:  # No position or short
                intents.append(TradeIntent(
                    symbol=market_data.symbol,
                    exchange=market_data.exchange,
                    transaction_type="BUY",
                    quantity=self.quantity,
                    product_type="INTRADAY",
                    order_type="MARKET",
                    reason="Fast MA crossed above slow MA",
                ))
        
        # Bearish crossover: fast MA crosses below slow MA
        elif prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma:
            if current_position > 0:  # Long position
                intents.append(TradeIntent(
                    symbol=market_data.symbol,
                    exchange=market_data.exchange,
                    transaction_type="SELL",
                    quantity=abs(current_position),
                    product_type="INTRADAY",
                    order_type="MARKET",
                    reason="Fast MA crossed below slow MA",
                ))
        
        return intents
    
    def on_indicator_signal(
        self,
        signal: dict,
        state: StrategyState,
    ) -> List[TradeIntent]:
        """Handle indicator signals (not used in this simple strategy)."""
        return []
    
    def get_required_indicators(self) -> List[str]:
        """Return required indicators."""
        return [
            f"sma_{self.fast_period}",
            f"sma_{self.slow_period}",
        ]

