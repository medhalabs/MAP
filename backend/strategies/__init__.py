"""
Strategy module - register all available strategies.
"""

from strategies.base import StrategyRegistry
from strategies.example_strategy import SimpleMovingAverageStrategy

# Register available strategies
# Map strategy_code from database to strategy class
StrategyRegistry.register("ma_crossover", SimpleMovingAverageStrategy)
StrategyRegistry.register("simple_ma", SimpleMovingAverageStrategy)
StrategyRegistry.register("moving_average", SimpleMovingAverageStrategy)

# Note: For production, you should create and register actual strategy classes
# that match the strategy_code values in your database (e.g., "rsi_mean_reversion", 
# "bb_breakout", "momentum", "support_resistance", "macd_divergence")
