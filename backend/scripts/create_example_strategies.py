"""
Script to create example strategies for testing.
Run with: uv run python scripts/create_example_strategies.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.session import get_db, init_db
from database.models import Strategy, User, Tenant
from sqlalchemy.orm import Session


def create_example_strategies(db: Session, tenant_id: int):
    """Create example strategies for a tenant."""
    
    strategies = [
        {
            "name": "Moving Average Crossover",
            "description": "Classic MA crossover strategy - buys when short MA crosses above long MA, sells when it crosses below",
            "strategy_code": "ma_crossover",
            "config_schema": {
                "type": "object",
                "properties": {
                    "short_ma_period": {"type": "integer", "default": 20},
                    "long_ma_period": {"type": "integer", "default": 50},
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "position_size": {"type": "integer", "default": 1000},
                    "stop_loss_percent": {"type": "number", "default": 2.0},
                    "take_profit_percent": {"type": "number", "default": 5.0},
                },
            },
            "is_active": True,
        },
        {
            "name": "RSI Mean Reversion",
            "description": "Buys when RSI is oversold (<30) and sells when RSI is overbought (>70)",
            "strategy_code": "rsi_mean_reversion",
            "config_schema": {
                "type": "object",
                "properties": {
                    "rsi_period": {"type": "integer", "default": 14},
                    "oversold_threshold": {"type": "integer", "default": 30},
                    "overbought_threshold": {"type": "integer", "default": 70},
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "position_size": {"type": "integer", "default": 500},
                    "stop_loss_percent": {"type": "number", "default": 1.5},
                },
            },
            "is_active": True,
        },
        {
            "name": "Bollinger Bands Breakout",
            "description": "Trades breakouts when price moves outside Bollinger Bands with volume confirmation",
            "strategy_code": "bb_breakout",
            "config_schema": {
                "type": "object",
                "properties": {
                    "bb_period": {"type": "integer", "default": 20},
                    "bb_std": {"type": "number", "default": 2.0},
                    "volume_multiplier": {"type": "number", "default": 1.5},
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "position_size": {"type": "integer", "default": 800},
                    "stop_loss_percent": {"type": "number", "default": 2.5},
                    "take_profit_percent": {"type": "number", "default": 4.0},
                },
            },
            "is_active": True,
        },
        {
            "name": "Momentum Strategy",
            "description": "Buys stocks with strong momentum (price and volume) and holds for short term gains",
            "strategy_code": "momentum",
            "config_schema": {
                "type": "object",
                "properties": {
                    "momentum_period": {"type": "integer", "default": 10},
                    "volume_period": {"type": "integer", "default": 20},
                    "min_momentum": {"type": "number", "default": 0.05},
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "position_size": {"type": "integer", "default": 1200},
                    "stop_loss_percent": {"type": "number", "default": 3.0},
                    "hold_period_days": {"type": "integer", "default": 5},
                },
            },
            "is_active": True,
        },
        {
            "name": "Support/Resistance Trading",
            "description": "Trades bounces off support levels and breakouts above resistance with confirmation",
            "strategy_code": "support_resistance",
            "config_schema": {
                "type": "object",
                "properties": {
                    "lookback_period": {"type": "integer", "default": 50},
                    "support_touch_count": {"type": "integer", "default": 2},
                    "resistance_touch_count": {"type": "integer", "default": 2},
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "position_size": {"type": "integer", "default": 600},
                    "stop_loss_percent": {"type": "number", "default": 2.0},
                    "take_profit_percent": {"type": "number", "default": 6.0},
                },
            },
            "is_active": True,
        },
        {
            "name": "MACD Divergence",
            "description": "Detects MACD divergences to identify potential trend reversals",
            "strategy_code": "macd_divergence",
            "config_schema": {
                "type": "object",
                "properties": {
                    "macd_fast": {"type": "integer", "default": 12},
                    "macd_slow": {"type": "integer", "default": 26},
                    "macd_signal": {"type": "integer", "default": 9},
                    "divergence_lookback": {"type": "integer", "default": 20},
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "position_size": {"type": "integer", "default": 1000},
                    "stop_loss_percent": {"type": "number", "default": 2.5},
                },
            },
            "is_active": True,
        },
    ]
    
    created_count = 0
    for strategy_data in strategies:
        # Check if strategy already exists
        existing = db.query(Strategy).filter(
            Strategy.name == strategy_data["name"],
            Strategy.tenant_id == tenant_id,
        ).first()
        
        if existing:
            print(f"Strategy '{strategy_data['name']}' already exists, skipping...")
            continue
        
        # Get first user for this tenant
        user = db.query(User).filter(User.tenant_id == tenant_id).first()
        if not user:
            print(f"No user found for tenant {tenant_id}, skipping strategy creation")
            return 0
        
        strategy = Strategy(
            tenant_id=tenant_id,
            user_id=user.id,
            name=strategy_data["name"],
            description=strategy_data["description"],
            strategy_code=strategy_data["strategy_code"],
            config_schema=strategy_data["config_schema"],
            is_active=strategy_data["is_active"],
        )
        db.add(strategy)
        created_count += 1
        print(f"Created strategy: {strategy_data['name']}")
    
    db.commit()
    print(f"\n✅ Created {created_count} new strategies!")
    return created_count


def main():
    """Main function."""
    print("Creating example strategies...")
    
    # Initialize database
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get first tenant (or create one if none exists)
        tenant = db.query(Tenant).first()
        if not tenant:
            print("No tenant found. Please create a user first (register via API or frontend).")
            return
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Create strategies
        create_example_strategies(db, tenant.id)
        
        # List all strategies
        strategies = db.query(Strategy).filter(Strategy.tenant_id == tenant.id).all()
        print(f"\n📊 Total strategies for tenant: {len(strategies)}")
        for strategy in strategies:
            print(f"  - {strategy.name} ({'Active' if strategy.is_active else 'Inactive'})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

