"""
Trading Engine - Event-driven strategy execution.

Responsibilities:
- Subscribe to market events
- Execute strategies based on events
- Convert trade intents to orders
- Manage strategy state
- Update positions and P&L
"""

import asyncio
from typing import Dict, Optional, List
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from database.models import (
    StrategyRun,
    Trade,
    Order,
    Position,
    PnlSnapshot,
    StrategyStatus,
    OrderStatus,
    TransactionType,
    ProductType,
    OrderType,
)
from database.session import get_db_context
from strategies.base import (
    BaseStrategy,
    MarketData,
    StrategyState,
    TradeIntent,
    StrategyRegistry,
)
from risk_engine.rules import RiskEngine
from broker.base import BrokerInterface, BrokerOrderRequest
from broker.factory import create_broker_adapter


class TradingEngine:
    """
    Event-driven trading engine.
    
    Manages strategy execution, order placement, and position tracking.
    """
    
    def __init__(self):
        """Initialize trading engine."""
        self.running_strategies: Dict[int, asyncio.Task] = {}
        self.strategy_states: Dict[int, StrategyState] = {}
        self.risk_engine = RiskEngine()
    
    async def start_strategy(self, strategy_run_id: int):
        """
        Start a strategy run.
        
        Args:
            strategy_run_id: Strategy run ID
        """
        if strategy_run_id in self.running_strategies:
            return  # Already running
        
        with get_db_context() as db:
            strategy_run = db.query(StrategyRun).filter(
                StrategyRun.id == strategy_run_id
            ).first()
            
            if not strategy_run:
                raise ValueError(f"Strategy run {strategy_run_id} not found")
            
            if strategy_run.status != StrategyStatus.PENDING:
                raise ValueError(f"Strategy run {strategy_run_id} is not in PENDING status")
            
            # Load strategy class
            strategy_class = StrategyRegistry.get(strategy_run.strategy.name)
            if not strategy_class:
                raise ValueError(f"Strategy class not found: {strategy_run.strategy.name}")
            
            # Create strategy instance
            strategy = strategy_class(strategy_run.config)
            
            # Initialize state
            self.strategy_states[strategy_run_id] = StrategyState(
                positions={},
                indicators={},
                last_signals=[],
                config=strategy_run.config,
            )
            
            # Update status
            strategy_run.status = StrategyStatus.RUNNING
            strategy_run.started_at = datetime.utcnow()
            db.commit()
        
        # Start strategy execution task
        task = asyncio.create_task(self._run_strategy(strategy_run_id))
        self.running_strategies[strategy_run_id] = task
    
    async def stop_strategy(self, strategy_run_id: int):
        """
        Stop a strategy run.
        
        Args:
            strategy_run_id: Strategy run ID
        """
        if strategy_run_id not in self.running_strategies:
            return
        
        # Cancel task
        task = self.running_strategies[strategy_run_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        del self.running_strategies[strategy_run_id]
        
        # Update status
        with get_db_context() as db:
            strategy_run = db.query(StrategyRun).filter(
                StrategyRun.id == strategy_run_id
            ).first()
            if strategy_run:
                strategy_run.status = StrategyStatus.STOPPED
                strategy_run.stopped_at = datetime.utcnow()
                db.commit()
        
        # Clean up state
        if strategy_run_id in self.strategy_states:
            del self.strategy_states[strategy_run_id]
    
    async def _run_strategy(self, strategy_run_id: int):
        """
        Main strategy execution loop.
        
        This is a simplified version. In production, you would:
        - Subscribe to real-time market data
        - Handle candle close events
        - Process indicator signals
        """
        try:
            with get_db_context() as db:
                strategy_run = db.query(StrategyRun).filter(
                    StrategyRun.id == strategy_run_id
                ).first()
                
                if not strategy_run:
                    return
                
                # Load strategy
                strategy_class = StrategyRegistry.get(strategy_run.strategy.name)
                strategy = strategy_class(strategy_run.config)
                
                # Get broker adapter
                broker_account = strategy_run.broker_account
                broker = create_broker_adapter(
                    broker_name=broker_account.broker_name,
                    api_key=broker_account.api_key,
                    access_token=broker_account.access_token,
                )
            
            # Main loop (simplified - in production, this would be event-driven)
            while strategy_run_id in self.running_strategies:
                # TODO: Subscribe to market data events
                # For now, this is a placeholder
                await asyncio.sleep(60)  # Check every minute
                
                # Process any pending market data events
                # This would come from a market data feed
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # Log error and update status
            with get_db_context() as db:
                strategy_run = db.query(StrategyRun).filter(
                    StrategyRun.id == strategy_run_id
                ).first()
                if strategy_run:
                    strategy_run.status = StrategyStatus.ERROR
                    strategy_run.error_message = str(e)
                    db.commit()
    
    async def process_candle_close(
        self,
        strategy_run_id: int,
        market_data: MarketData,
    ):
        """
        Process candle close event.
        
        Args:
            strategy_run_id: Strategy run ID
            market_data: Market data for closed candle
        """
        if strategy_run_id not in self.strategy_states:
            return
        
        state = self.strategy_states[strategy_run_id]
        
        with get_db_context() as db:
            strategy_run = db.query(StrategyRun).filter(
                StrategyRun.id == strategy_run_id
            ).first()
            
            if not strategy_run or strategy_run.status != StrategyStatus.RUNNING:
                return
            
            # Load strategy
            strategy_class = StrategyRegistry.get(strategy_run.strategy.name)
            strategy = strategy_class(strategy_run.config)
            
            # Update indicators (simplified - in production, use proper indicator library)
            # TODO: Calculate indicators from historical data
            
            # Get trade intents from strategy
            intents = strategy.on_candle_close(market_data, state)
            
            # Process each intent
            for intent in intents:
                await self._process_trade_intent(
                    db=db,
                    strategy_run=strategy_run,
                    intent=intent,
                )
            
            # Update state
            state.last_signals = intents
    
    async def _process_trade_intent(
        self,
        db: Session,
        strategy_run: StrategyRun,
        intent: TradeIntent,
    ):
        """
        Process trade intent: validate risk, create trade, place order.
        
        Args:
            db: Database session
            strategy_run: Strategy run
            intent: Trade intent from strategy
        """
        # Risk validation
        order_request = {
            "symbol": intent.symbol,
            "exchange": intent.exchange,
            "quantity": intent.quantity,
            "price": float(intent.intended_price) if intent.intended_price else None,
            "transaction_type": intent.transaction_type,
            "product_type": intent.product_type,
        }
        
        risk_result = self.risk_engine.validate_order(
            db=db,
            order_request=order_request,
            strategy_run_id=strategy_run.id,
            broker_account_id=strategy_run.broker_account_id,
        )
        
        if not risk_result.is_allowed:
            return  # Risk check failed
        
        # Create trade record
        trade = Trade(
            strategy_run_id=strategy_run.id,
            symbol=intent.symbol,
            exchange=intent.exchange,
            transaction_type=TransactionType(intent.transaction_type),
            quantity=intent.quantity,
            intended_price=intent.intended_price,
            product_type=ProductType(intent.product_type),
        )
        db.add(trade)
        db.flush()
        
        # Create order record
        order = Order(
            broker_account_id=strategy_run.broker_account_id,
            strategy_run_id=strategy_run.id,
            trade_id=trade.id,
            symbol=intent.symbol,
            exchange=intent.exchange,
            order_type=OrderType(intent.order_type),
            product_type=ProductType(intent.product_type),
            transaction_type=TransactionType(intent.transaction_type),
            quantity=intent.quantity,
            price=intent.intended_price,
            status=OrderStatus.PENDING,
        )
        db.add(order)
        db.commit()
        
        # Place order with broker (async, non-blocking)
        asyncio.create_task(self._place_order_with_broker(order.id))
    
    async def _place_order_with_broker(self, order_id: int):
        """
        Place order with broker (async, handles failures gracefully).
        
        Args:
            order_id: Order ID
        """
        try:
            with get_db_context() as db:
                order = db.query(Order).filter(Order.id == order_id).first()
                if not order:
                    return
                
                # Get broker adapter
                broker_account = order.broker_account
                broker = create_broker_adapter(
                    broker_name=broker_account.broker_name,
                    api_key=broker_account.api_key,
                    access_token=broker_account.access_token,
                )
                
                # Create broker order request
                broker_request = BrokerOrderRequest(
                    symbol=order.symbol,
                    exchange=order.exchange,
                    order_type=order.order_type,
                    product_type=order.product_type,
                    transaction_type=order.transaction_type,
                    quantity=order.quantity,
                    price=order.price,
                    trigger_price=order.trigger_price,
                )
                
                # Place order
                response = broker.place_order(broker_request)
                
                # Update order
                order.broker_order_id = response.broker_order_id
                order.status = OrderStatus.SUBMITTED
                order.submitted_at = datetime.utcnow()
                order.broker_response = response.raw_response
                db.commit()
                
        except Exception as e:
            # Handle broker failure gracefully
            with get_db_context() as db:
                order = db.query(Order).filter(Order.id == order_id).first()
                if order:
                    order.status = OrderStatus.REJECTED
                    order.error_message = str(e)
                    db.commit()


# Global trading engine instance
trading_engine = TradingEngine()

