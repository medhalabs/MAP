# Creating Your Own Trading Strategy

This guide will walk you through creating a custom trading strategy for MedhaAlgoPilot.

## Table of Contents

1. [Understanding Strategies](#understanding-strategies)
2. [Strategy Architecture](#strategy-architecture)
3. [Creating a Strategy Class](#creating-a-strategy-class)
4. [Registering Your Strategy](#registering-your-strategy)
5. [Creating Strategy via UI](#creating-strategy-via-ui)
6. [Creating Strategy via API](#creating-strategy-via-api)
7. [Testing Your Strategy](#testing-your-strategy)
8. [Best Practices](#best-practices)
9. [Example Strategies](#example-strategies)

---

## Understanding Strategies

In MedhaAlgoPilot, strategies are **stateless functions** that:
- Accept market data and configuration
- Return trade intents (not orders)
- Never directly interact with brokers
- Are reusable for backtesting, paper trading, and live trading

### Key Concepts

- **Stateless**: Strategies don't store state between calls. The trading engine manages state.
- **Trade Intents**: Strategies return what they *want* to do, not actual orders.
- **Market Data**: Strategies receive candle data, indicators, and current positions.
- **Configuration**: Each strategy run can have different parameters.

---

## Strategy Architecture

### Strategy Lifecycle

```
1. Strategy Created (Template)
   ↓
2. Strategy Run Started (Instance with config)
   ↓
3. Market Events → Strategy Called
   ↓
4. Strategy Returns Trade Intents
   ↓
5. Risk Engine Validates Intents
   ↓
6. Orders Created & Sent to Broker
   ↓
7. Positions Updated
   ↓
8. P&L Calculated
```

### Components

- **Strategy Class**: Python class that implements `BaseStrategy`
- **Strategy Template**: Database record (name, description, config schema)
- **Strategy Run**: Active instance of a strategy with specific config
- **Trade Intent**: Request to buy/sell with quantity and conditions

---

## Creating a Strategy Class

### Step 1: Create Your Strategy File

Create a new file in `backend/strategies/` directory:

```python
# backend/strategies/my_strategy.py

from typing import List
from decimal import Decimal
from strategies.base import (
    BaseStrategy,
    MarketData,
    StrategyState,
    TradeIntent,
    TransactionType,
)
```

### Step 2: Implement BaseStrategy

Your strategy must inherit from `BaseStrategy` and implement two methods:

```python
class MyCustomStrategy(BaseStrategy):
    """
    Your strategy description here.
    
    This strategy does X when Y happens.
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        # Initialize your strategy parameters from config
        self.param1 = config.get("param1", 10)
        self.param2 = config.get("param2", 20)
        self.quantity = config.get("quantity", 1)
    
    def on_candle_close(
        self,
        market_data: MarketData,
        state: StrategyState,
    ) -> List[TradeIntent]:
        """
        Called when a candle closes.
        
        This is where you implement your main trading logic.
        """
        intents = []
        
        # Your logic here
        # Example: Check indicators, calculate signals, etc.
        
        # Return list of TradeIntent objects
        return intents
    
    def on_indicator_signal(
        self,
        signal: dict,
        state: StrategyState,
    ) -> List[TradeIntent]:
        """
        Called when an indicator emits a signal.
        
        This is optional - you can return empty list if not used.
        """
        intents = []
        # Handle indicator signals
        return intents
```

### Step 3: Understanding MarketData

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class MarketData:
    symbol: str           # Stock symbol (e.g., "RELIANCE")
    timestamp: datetime   # Candle timestamp
    open: Decimal         # Open price
    high: Decimal         # High price
    low: Decimal          # Low price
    close: Decimal        # Close price
    volume: int           # Volume
    interval: str         # Timeframe (e.g., "1m", "5m", "1h", "1d")
```

### Step 4: Understanding StrategyState

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class StrategyState:
    positions: Dict[str, int]           # Current positions {symbol: quantity}
    indicators: Dict[str, Any]          # Calculated indicators
    config: Dict[str, Any]              # Strategy configuration
    # Additional state managed by trading engine
```

**Available Indicators** (examples):
- `sma_10`, `sma_20`, `sma_50` - Simple Moving Averages
- `ema_12`, `ema_26` - Exponential Moving Averages
- `rsi_14` - Relative Strength Index
- `bb_upper`, `bb_middle`, `bb_lower` - Bollinger Bands
- `macd`, `macd_signal`, `macd_histogram` - MACD
- Custom indicators can be added by the trading engine

### Step 5: Creating Trade Intents

```python
from strategies.base import TradeIntent
from decimal import Decimal

# Buy intent (Market Order)
buy_intent = TradeIntent(
    symbol="RELIANCE",
    exchange="NSE",
    transaction_type="BUY",  # "BUY" or "SELL"
    quantity=10,
    intended_price=None,  # None = Market order
    product_type="INTRADAY",  # "INTRADAY" or "DELIVERY"
    order_type="MARKET",  # "MARKET" or "LIMIT"
    reason="Fast MA crossed above slow MA",  # Optional reason
)

# Sell intent (Limit Order)
sell_intent = TradeIntent(
    symbol="RELIANCE",
    exchange="NSE",
    transaction_type="SELL",
    quantity=5,
    intended_price=Decimal("2500.50"),  # Limit price
    product_type="INTRADAY",
    order_type="LIMIT",
    reason="Take profit target reached",
)

# Return list of intents
return [buy_intent, sell_intent]
```

**TradeIntent Fields**:
- `symbol`: Stock symbol (required, e.g., "RELIANCE")
- `exchange`: Exchange code (required, e.g., "NSE", "BSE")
- `transaction_type`: `"BUY"` or `"SELL"` (required)
- `quantity`: Number of shares (required, must be > 0)
- `intended_price`: `None` for market order, `Decimal` for limit order (optional)
- `product_type`: `"INTRADAY"` or `"DELIVERY"` (default: "INTRADAY")
- `order_type`: `"MARKET"` or `"LIMIT"` (default: "MARKET")
- `reason`: Optional string explaining why this trade (optional)

---

## Complete Example: Simple Moving Average Crossover

```python
# backend/strategies/ma_crossover.py

from typing import List
from decimal import Decimal
from strategies.base import (
    BaseStrategy,
    MarketData,
    StrategyState,
    TradeIntent,
    TransactionType,
)


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.
    
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
        
        # Need previous values to detect crossover
        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return intents
        
        current_position = state.positions.get(market_data.symbol, 0)
        
        # Bullish crossover: fast MA crosses above slow MA
        if prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma:
            if current_position == 0:  # No position, buy
                intents.append(TradeIntent(
                    symbol=market_data.symbol,
                    exchange=market_data.exchange,
                    transaction_type="BUY",
                    quantity=self.quantity,
                    intended_price=None,  # Market order
                    product_type="INTRADAY",
                    order_type="MARKET",
                    reason="Fast MA crossed above slow MA",
                ))
        
        # Bearish crossover: fast MA crosses below slow MA
        elif prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma:
            if current_position > 0:  # Have position, sell
                intents.append(TradeIntent(
                    symbol=market_data.symbol,
                    exchange=market_data.exchange,
                    transaction_type="SELL",
                    quantity=min(current_position, self.quantity),
                    intended_price=None,  # Market order
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
        """Not used in this strategy."""
        return []
    
    def get_required_indicators(self) -> List[str]:
        """Return list of indicators this strategy needs."""
        return [
            f"sma_{self.fast_period}",
            f"sma_{self.slow_period}",
        ]
```

---

## Registering Your Strategy

### Option 1: Add to Strategy Registry

Edit `backend/strategies/__init__.py`:

```python
from strategies.ma_crossover import MovingAverageCrossoverStrategy
from strategies.base import StrategyRegistry

# Register your strategy
StrategyRegistry.register("ma_crossover", MovingAverageCrossoverStrategy)
```

### Option 2: Dynamic Registration

Strategies can also be loaded dynamically from the database `strategy_code` field. The trading engine will look up the strategy class by `strategy_code` when starting a run.

**Note**: Currently, strategies need to be registered in code. Future versions may support dynamic loading from database.

---

## Creating Strategy via UI

### Step 1: Navigate to Strategies Page

Go to `/dashboard/strategies` in your browser.

### Step 2: Click "Create Strategy"

Click the "Create Strategy" button.

### Step 3: Fill in the Form

- **Name**: Display name (e.g., "My MA Crossover")
- **Description**: What the strategy does
- **Config Schema**: JSON schema defining configuration parameters

Example Config Schema:

```json
{
  "type": "object",
  "properties": {
    "fast_period": {
      "type": "integer",
      "default": 10,
      "description": "Fast moving average period"
    },
    "slow_period": {
      "type": "integer",
      "default": 20,
      "description": "Slow moving average period"
    },
    "quantity": {
      "type": "integer",
      "default": 1,
      "description": "Number of shares to trade"
    },
    "symbols": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of symbols to trade"
    }
  },
  "required": ["fast_period", "slow_period", "quantity"]
}
```

### Step 4: Submit

Click "Create" to save your strategy template.

---

## Creating Strategy via API

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/strategies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Strategy",
    "description": "Strategy description",
    "strategy_code": "my_custom_strategy",
    "config_schema": {
      "type": "object",
      "properties": {
        "param1": {"type": "integer", "default": 10},
        "param2": {"type": "string", "default": "value"}
      }
    }
  }'
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/strategies"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "name": "My Custom Strategy",
    "description": "Strategy description",
    "strategy_code": "my_custom_strategy",
    "config_schema": {
        "type": "object",
        "properties": {
            "param1": {"type": "integer", "default": 10},
            "param2": {"type": "string", "default": "value"}
        }
    }
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## Starting a Strategy Run

Once your strategy is created, you can start a run:

### Via UI

1. Go to `/dashboard/strategies`
2. Find your strategy
3. Click "Start"
4. Select broker account (or it uses default)
5. Strategy run starts in paper trading mode

### Via API

```bash
curl -X POST "http://localhost:8000/api/strategies/{strategy_id}/runs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "broker_account_id": 1,
    "trading_mode": "paper",
    "config": {
      "fast_period": 10,
      "slow_period": 20,
      "quantity": 1,
      "symbols": ["RELIANCE", "TCS"]
    }
  }'
```

---

## Testing Your Strategy

### 1. Paper Trading

Start with paper trading mode to test without real money:

```python
{
  "trading_mode": "paper",
  "config": {...}
}
```

### 2. Check Logs

Monitor strategy execution:
- Dashboard shows active strategies
- Strategy detail page shows runs and status
- Orders page shows generated orders
- Positions page shows current positions

### 3. Backtesting (Future Feature)

Backtesting will allow you to test strategies on historical data.

---

## Best Practices

### 1. Keep Strategies Stateless

❌ **Don't:**
```python
class BadStrategy(BaseStrategy):
    def __init__(self, config):
        self.counter = 0  # Don't store state!
    
    def on_candle_close(self, market_data, state):
        self.counter += 1  # Bad!
```

✅ **Do:**
```python
class GoodStrategy(BaseStrategy):
    def on_candle_close(self, market_data, state):
        # Use state.indicators or state.positions
        # Don't store instance variables
```

### 2. Validate Configuration

```python
def validate_config(self) -> bool:
    """Validate strategy configuration."""
    if self.fast_period >= self.slow_period:
        return False  # Fast must be less than slow
    if self.quantity <= 0:
        return False
    return True
```

### 3. Handle Edge Cases

```python
def on_candle_close(self, market_data, state):
    intents = []
    
    # Check if we have required data
    if not market_data or not state:
        return intents
    
    # Check if indicators are available
    if "sma_10" not in state.indicators:
        return intents  # Not enough data yet
    
    # Your logic here
    return intents
```

### 4. Use Meaningful Names

- Strategy class: `MovingAverageCrossoverStrategy`
- Strategy code: `ma_crossover`
- Config parameters: `fast_period`, `slow_period` (not `p1`, `p2`)

### 5. Document Your Strategy

```python
class MyStrategy(BaseStrategy):
    """
    Clear description of what the strategy does.
    
    Entry Conditions:
    - Condition 1
    - Condition 2
    
    Exit Conditions:
    - Condition 1
    - Condition 2
    
    Risk Management:
    - Stop loss: X%
    - Take profit: Y%
    """
```

### 6. Test with Small Quantities

Start with `quantity: 1` in paper trading mode.

### 7. Use Limit Orders for Better Control

```python
# Market order (executes immediately at market price)
TradeIntent(
    symbol="RELIANCE",
    exchange="NSE",
    transaction_type="BUY",
    quantity=10,
    intended_price=None,  # Market order
    order_type="MARKET",
)

# Limit order (executes only at specified price or better)
TradeIntent(
    symbol="RELIANCE",
    exchange="NSE",
    transaction_type="BUY",
    quantity=10,
    intended_price=Decimal("2500.00"),  # Limit price
    order_type="LIMIT",
)
```

---

## Example Strategies

### 1. RSI Mean Reversion

```python
class RSIMeanReversionStrategy(BaseStrategy):
    """Buy when RSI < 30, sell when RSI > 70."""
    
    def __init__(self, config):
        super().__init__(config)
        self.rsi_period = config.get("rsi_period", 14)
        self.oversold = config.get("oversold", 30)
        self.overbought = config.get("overbought", 70)
        self.quantity = config.get("quantity", 1)
    
    def on_candle_close(self, market_data, state):
        intents = []
        rsi = state.indicators.get(f"rsi_{self.rsi_period}")
        position = state.positions.get(market_data.symbol, 0)
        
        if not rsi:
            return intents
        
        if rsi < self.oversold and position == 0:
            intents.append(TradeIntent(
                symbol=market_data.symbol,
                exchange=market_data.exchange,
                transaction_type="BUY",
                quantity=self.quantity,
                product_type="INTRADAY",
                order_type="MARKET",
                reason=f"RSI oversold at {rsi:.2f}",
            ))
        elif rsi > self.overbought and position > 0:
            intents.append(TradeIntent(
                symbol=market_data.symbol,
                exchange=market_data.exchange,
                transaction_type="SELL",
                quantity=position,
                product_type="INTRADAY",
                order_type="MARKET",
                reason=f"RSI overbought at {rsi:.2f}",
            ))
        
        return intents
```

### 2. Breakout Strategy

```python
class BreakoutStrategy(BaseStrategy):
    """Buy when price breaks above resistance with volume."""
    
    def __init__(self, config):
        super().__init__(config)
        self.lookback = config.get("lookback", 20)
        self.volume_multiplier = config.get("volume_multiplier", 1.5)
        self.quantity = config.get("quantity", 1)
    
    def on_candle_close(self, market_data, state):
        intents = []
        position = state.positions.get(market_data.symbol, 0)
        
        # Get resistance level (highest high in lookback period)
        resistance = state.indicators.get(f"resistance_{self.lookback}")
        avg_volume = state.indicators.get(f"avg_volume_{self.lookback}")
        
        if not all([resistance, avg_volume]):
            return intents
        
        # Breakout condition: price > resistance AND volume > avg * multiplier
        if (market_data.close > resistance and 
            market_data.volume > avg_volume * self.volume_multiplier and
            position == 0):
            intents.append(TradeIntent(
                symbol=market_data.symbol,
                exchange=market_data.exchange,
                transaction_type="BUY",
                quantity=self.quantity,
                product_type="INTRADAY",
                order_type="MARKET",
                reason="Breakout above resistance with volume",
            ))
        
        return intents
```

---

## Troubleshooting

### Strategy Not Appearing

- Check that strategy is registered in `strategies/__init__.py`
- Verify `strategy_code` matches the registered name
- Check database for strategy record

### Strategy Not Generating Orders

- Check strategy logs for errors
- Verify indicators are being calculated
- Ensure strategy logic conditions are being met
- Check risk engine isn't blocking orders

### Strategy Generating Too Many Orders

- Add position checks to avoid duplicate entries
- Implement cooldown periods
- Add confirmation signals

---

## Next Steps

1. **Read the Architecture Docs**: `ARCHITECTURE.md`
2. **Study Example Strategies**: `backend/strategies/example_strategy.py`
3. **Understand Risk Engine**: `backend/risk_engine/rules.py`
4. **Learn Trading Engine**: `backend/trading_engine/engine.py`

---

## Support

For questions or issues:
1. Check existing strategies for examples
2. Review the codebase documentation
3. Test in paper trading mode first
4. Start with simple strategies and iterate

Happy Trading! 🚀

