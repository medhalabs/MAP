"""
Risk rules for order validation.

All rules are stateless and can be evaluated independently.
Rules return RiskResult indicating if order should be allowed.
"""

from typing import Optional, Dict, Any, List
from decimal import Decimal
from dataclasses import dataclass

from database.models import RiskEventType, OrderStatus
from database.session import SessionLocal
from database.models import (
    Order,
    Position,
    StrategyRun,
    RiskEvent,
    PnlSnapshot,
)


@dataclass
class RiskResult:
    """Result of risk rule evaluation."""
    is_allowed: bool
    event_type: Optional[RiskEventType] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RiskRule:
    """Base class for risk rules."""
    
    def evaluate(
        self,
        db: SessionLocal,
        order_request: Dict[str, Any],
        strategy_run_id: Optional[int] = None,
        broker_account_id: Optional[int] = None,
    ) -> RiskResult:
        """
        Evaluate risk rule.
        
        Args:
            db: Database session
            order_request: Order request details
            strategy_run_id: Optional strategy run ID
            broker_account_id: Optional broker account ID
            
        Returns:
            RiskResult indicating if order is allowed
        """
        raise NotImplementedError


class MaxDailyLossRule(RiskRule):
    """Enforce maximum daily loss limit."""
    
    def __init__(self, max_daily_loss_percent: float = 5.0):
        """
        Initialize rule.
        
        Args:
            max_daily_loss_percent: Maximum daily loss as percentage of capital
        """
        self.max_daily_loss_percent = max_daily_loss_percent
    
    def evaluate(
        self,
        db: SessionLocal,
        order_request: Dict[str, Any],
        strategy_run_id: Optional[int] = None,
        broker_account_id: Optional[int] = None,
    ) -> RiskResult:
        """Check if daily loss limit is exceeded."""
        if not strategy_run_id:
            return RiskResult(is_allowed=True)
        
        # Get latest P&L snapshot for today
        from datetime import datetime, date
        today_start = datetime.combine(date.today(), datetime.min.time())
        
        latest_pnl = db.query(PnlSnapshot).filter(
            PnlSnapshot.strategy_run_id == strategy_run_id,
            PnlSnapshot.timestamp >= today_start,
        ).order_by(PnlSnapshot.timestamp.desc()).first()
        
        if not latest_pnl:
            return RiskResult(is_allowed=True)
        
        # Get initial capital (from first snapshot or strategy config)
        # For simplicity, assume we track this in strategy_run config
        strategy_run = db.query(StrategyRun).filter(
            StrategyRun.id == strategy_run_id
        ).first()
        
        if not strategy_run:
            return RiskResult(is_allowed=True)
        
        # Calculate loss percentage
        # This is simplified - in production, track initial capital properly
        if latest_pnl.total_pnl < 0:
            loss_percent = abs(float(latest_pnl.total_pnl)) / float(latest_pnl.capital_used) * 100
            if loss_percent >= self.max_daily_loss_percent:
                return RiskResult(
                    is_allowed=False,
                    event_type=RiskEventType.MAX_DAILY_LOSS,
                    message=f"Daily loss limit exceeded: {loss_percent:.2f}% >= {self.max_daily_loss_percent}%",
                    metadata={
                        "current_loss_percent": loss_percent,
                        "max_allowed": self.max_daily_loss_percent,
                        "total_pnl": float(latest_pnl.total_pnl),
                    }
                )
        
        return RiskResult(is_allowed=True)


class MaxOpenPositionsRule(RiskRule):
    """Enforce maximum number of open positions."""
    
    def __init__(self, max_open_positions: int = 10):
        """
        Initialize rule.
        
        Args:
            max_open_positions: Maximum number of open positions
        """
        self.max_open_positions = max_open_positions
    
    def evaluate(
        self,
        db: SessionLocal,
        order_request: Dict[str, Any],
        strategy_run_id: Optional[int] = None,
        broker_account_id: Optional[int] = None,
    ) -> RiskResult:
        """Check if max open positions limit is exceeded."""
        if not broker_account_id:
            return RiskResult(is_allowed=True)
        
        # Count open positions (non-zero quantity)
        open_positions_count = db.query(Position).filter(
            Position.broker_account_id == broker_account_id,
            Position.quantity != 0,
        ).count()
        
        if open_positions_count >= self.max_open_positions:
            return RiskResult(
                is_allowed=False,
                event_type=RiskEventType.MAX_OPEN_POSITIONS,
                message=f"Maximum open positions limit exceeded: {open_positions_count} >= {self.max_open_positions}",
                metadata={
                    "current_positions": open_positions_count,
                    "max_allowed": self.max_open_positions,
                }
            )
        
        return RiskResult(is_allowed=True)


class CapitalAllocationRule(RiskRule):
    """Enforce capital allocation limits per order."""
    
    def __init__(self, max_order_size_percent: float = 10.0):
        """
        Initialize rule.
        
        Args:
            max_order_size_percent: Maximum order size as percentage of available capital
        """
        self.max_order_size_percent = max_order_size_percent
    
    def evaluate(
        self,
        db: SessionLocal,
        order_request: Dict[str, Any],
        strategy_run_id: Optional[int] = None,
        broker_account_id: Optional[int] = None,
    ) -> RiskResult:
        """Check if order size exceeds capital allocation limit."""
        if not broker_account_id:
            return RiskResult(is_allowed=True)
        
        # Get order value
        quantity = order_request.get("quantity", 0)
        price = order_request.get("price") or order_request.get("intended_price")
        
        if not price:
            # For market orders, we might need to fetch current price
            # For now, allow if price not available
            return RiskResult(is_allowed=True)
        
        order_value = float(price) * quantity
        
        # Get available capital (simplified - in production, fetch from broker)
        # For now, use a placeholder - this should come from broker account balance
        # TODO: Fetch actual available capital from broker
        
        # Placeholder logic
        return RiskResult(is_allowed=True)


class PerStrategyRiskRule(RiskRule):
    """Enforce per-strategy risk limits."""
    
    def __init__(self, max_strategy_capital_percent: float = 30.0):
        """
        Initialize rule.
        
        Args:
            max_strategy_capital_percent: Maximum capital allocation per strategy
        """
        self.max_strategy_capital_percent = max_strategy_capital_percent
    
    def evaluate(
        self,
        db: SessionLocal,
        order_request: Dict[str, Any],
        strategy_run_id: Optional[int] = None,
        broker_account_id: Optional[int] = None,
    ) -> RiskResult:
        """Check if strategy has exceeded its capital allocation."""
        if not strategy_run_id or not broker_account_id:
            return RiskResult(is_allowed=True)
        
        # Get strategy's current capital usage
        latest_pnl = db.query(PnlSnapshot).filter(
            PnlSnapshot.strategy_run_id == strategy_run_id,
        ).order_by(PnlSnapshot.timestamp.desc()).first()
        
        if latest_pnl:
            # Check if strategy has exceeded its allocation
            # This is simplified - in production, track total account capital
            pass
        
        return RiskResult(is_allowed=True)


class RiskEngine:
    """
    Risk engine that evaluates all risk rules.
    
    Stateless - can be instantiated per request or reused.
    """
    
    def __init__(self, rules: Optional[List[RiskRule]] = None):
        """
        Initialize risk engine with rules.
        
        Args:
            rules: List of risk rules to evaluate. If None, uses default rules.
        """
        if rules is None:
            self.rules = [
                MaxDailyLossRule(max_daily_loss_percent=5.0),
                MaxOpenPositionsRule(max_open_positions=10),
                CapitalAllocationRule(max_order_size_percent=10.0),
                PerStrategyRiskRule(max_strategy_capital_percent=30.0),
            ]
        else:
            self.rules = rules
    
    def validate_order(
        self,
        db: SessionLocal,
        order_request: Dict[str, Any],
        strategy_run_id: Optional[int] = None,
        broker_account_id: Optional[int] = None,
    ) -> RiskResult:
        """
        Validate order against all risk rules.
        
        Args:
            db: Database session
            order_request: Order request details
            strategy_run_id: Optional strategy run ID
            broker_account_id: Optional broker account ID
            
        Returns:
            RiskResult - first failing rule stops evaluation
        """
        for rule in self.rules:
            result = rule.evaluate(
                db=db,
                order_request=order_request,
                strategy_run_id=strategy_run_id,
                broker_account_id=broker_account_id,
            )
            
            if not result.is_allowed:
                # Log risk event
                self._log_risk_event(
                    db=db,
                    result=result,
                    strategy_run_id=strategy_run_id,
                    broker_account_id=broker_account_id,
                )
                return result
        
        return RiskResult(is_allowed=True)
    
    def _log_risk_event(
        self,
        db: SessionLocal,
        result: RiskResult,
        strategy_run_id: Optional[int],
        broker_account_id: Optional[int],
    ):
        """Log risk event to database."""
        risk_event = RiskEvent(
            strategy_run_id=strategy_run_id,
            broker_account_id=broker_account_id,
            event_type=result.event_type,
            message=result.message or "Risk rule violation",
            event_metadata=result.metadata,
            was_blocked=True,
        )
        db.add(risk_event)
        db.commit()

