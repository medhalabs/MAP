"""
Abstract broker interface.

All broker adapters must implement this interface.
This allows swapping brokers without changing strategy or trading engine code.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from decimal import Decimal

from database.models import OrderType, ProductType, TransactionType


class BrokerOrderRequest:
    """Standardized order request."""
    def __init__(
        self,
        symbol: str,
        exchange: str,
        order_type: OrderType,
        product_type: ProductType,
        transaction_type: TransactionType,
        quantity: int,
        price: Optional[Decimal] = None,
        trigger_price: Optional[Decimal] = None,
        client_order_id: Optional[str] = None,
        disclosed_quantity: Optional[int] = None,
        after_market_order_flag: Optional[str] = None,
        amo_time: Optional[str] = None,
        bo_profit_value: Optional[Decimal] = None,
        bo_stop_loss_value: Optional[Decimal] = None,
        drp: Optional[str] = None,
        validity: Optional[str] = None,
        tag: Optional[str] = None,
        algo_id: Optional[str] = None,
        leg_name: Optional[str] = None,
    ):
        self.symbol = symbol
        self.exchange = exchange
        self.order_type = order_type
        self.product_type = product_type
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.price = price
        self.trigger_price = trigger_price
        self.client_order_id = client_order_id
        self.disclosed_quantity = disclosed_quantity
        self.after_market_order_flag = after_market_order_flag
        self.amo_time = amo_time
        self.bo_profit_value = bo_profit_value
        self.bo_stop_loss_value = bo_stop_loss_value
        self.drp = drp
        self.validity = validity
        self.tag = tag
        self.algo_id = algo_id
        self.leg_name = leg_name


class BrokerOrderResponse:
    """Standardized order response."""
    def __init__(
        self,
        broker_order_id: str,
        status: str,
        message: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None,
        client_order_id: Optional[str] = None,
    ):
        self.broker_order_id = broker_order_id
        self.status = status  # "success", "pending", "rejected"
        self.message = message
        self.raw_response = raw_response
        self.client_order_id = client_order_id


class BrokerPosition:
    """Standardized position representation."""
    def __init__(
        self,
        symbol: str,
        exchange: str,
        quantity: int,
        average_price: Decimal,
        last_price: Optional[Decimal] = None,
        product_type: ProductType = ProductType.INTRADAY,
    ):
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity  # Positive for long, negative for short
        self.average_price = average_price
        self.last_price = last_price
        self.product_type = product_type


class BrokerOrderStatus:
    """Standardized order status."""
    def __init__(
        self,
        broker_order_id: str,
        status: str,
        filled_quantity: int = 0,
        average_price: Optional[Decimal] = None,
        message: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None,
        client_order_id: Optional[str] = None,
        symbol: Optional[str] = None,
        exchange: Optional[str] = None,
        order_type: Optional[OrderType] = None,
        product_type: Optional[ProductType] = None,
        transaction_type: Optional[TransactionType] = None,
        quantity: Optional[int] = None,
        price: Optional[Decimal] = None,
        trigger_price: Optional[Decimal] = None,
        order_timestamp: Optional[Any] = None,
        exchange_order_id: Optional[str] = None,
        exchange_timestamp: Optional[Any] = None,
        status_message: Optional[str] = None,
        filled_price: Optional[Decimal] = None,
        remaining_quantity: Optional[int] = None,
        order_tag: Optional[str] = None,
        algo_id: Optional[str] = None,
        leg_name: Optional[str] = None,
        message_code: Optional[str] = None,
        message_description: Optional[str] = None,
    ):
        self.broker_order_id = broker_order_id
        self.status = status
        self.filled_quantity = filled_quantity
        self.average_price = average_price
        self.message = message
        self.raw_response = raw_response
        self.client_order_id = client_order_id
        self.symbol = symbol
        self.exchange = exchange
        self.order_type = order_type
        self.product_type = product_type
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.price = price
        self.trigger_price = trigger_price
        self.order_timestamp = order_timestamp
        self.exchange_order_id = exchange_order_id
        self.exchange_timestamp = exchange_timestamp
        self.status_message = status_message
        self.filled_price = filled_price
        self.remaining_quantity = remaining_quantity
        self.order_tag = order_tag
        self.algo_id = algo_id
        self.leg_name = leg_name
        self.message_code = message_code
        self.message_description = message_description


class BrokerInterface(ABC):
    """
    Abstract broker interface.
    
    All broker adapters must implement these methods.
    Broker failures should raise BrokerException, not crash the trading engine.
    """

    @abstractmethod
    async def authenticate(self, api_key: str, api_secret: str) -> str:
        """
        Authenticate with broker and return access token.
        
        Args:
            api_key: Broker API key
            api_secret: Broker API secret
            
        Returns:
            Access token string
            
        Raises:
            BrokerException: If authentication fails
        """
        pass

    @abstractmethod
    async def place_order(self, order_request: BrokerOrderRequest) -> BrokerOrderResponse:
        """
        Place an order with the broker.
        
        Args:
            order_request: Standardized order request
            
        Returns:
            BrokerOrderResponse with broker_order_id
            
        Raises:
            BrokerException: If order placement fails
        """
        pass

    @abstractmethod
    async def cancel_order(self, broker_order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            broker_order_id: Broker's order identifier
            
        Returns:
            True if cancellation successful
            
        Raises:
            BrokerException: If cancellation fails
        """
        pass

    @abstractmethod
    async def get_order_status(self, broker_order_id: str) -> BrokerOrderStatus:
        """
        Get current status of an order.
        
        Args:
            broker_order_id: Broker's order identifier
            
        Returns:
            BrokerOrderStatus
            
        Raises:
            BrokerException: If status fetch fails
        """
        pass

    @abstractmethod
    async def fetch_positions(self) -> List[BrokerPosition]:
        """
        Fetch all current positions.
        
        Returns:
            List of BrokerPosition objects
            
        Raises:
            BrokerException: If fetch fails
        """
        pass

    @abstractmethod
    async def fetch_orders(
        self,
        status: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> List[BrokerOrderStatus]:
        """
        Fetch orders (optionally filtered).
        
        Args:
            status: Optional status filter
            symbol: Optional symbol filter
            
        Returns:
            List of BrokerOrderStatus objects
            
        Raises:
            BrokerException: If fetch fails
        """
        pass

    @abstractmethod
    async def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance and margin details.
        
        Returns:
            Dictionary with balance information
            
        Raises:
            BrokerException: If fetch fails
        """
        pass


class BrokerException(Exception):
    """Base exception for broker operations."""
    pass


class BrokerAuthenticationError(BrokerException):
    """Raised when broker authentication fails."""
    pass


class BrokerOrderError(BrokerException):
    """Raised when order operation fails."""
    pass

