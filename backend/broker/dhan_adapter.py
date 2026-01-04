"""
Dhan API adapter implementation.

This adapter implements the BrokerInterface for Dhan broker.
Handles Dhan-specific API calls and response mapping.
"""

import requests
from typing import List, Optional, Dict, Any
from decimal import Decimal

from broker.base import (
    BrokerInterface,
    BrokerOrderRequest,
    BrokerOrderResponse,
    BrokerPosition,
    BrokerOrderStatus,
    BrokerException,
    BrokerAuthenticationError,
    BrokerOrderError,
)
from database.models import OrderType, ProductType, TransactionType


class DhanAdapter(BrokerInterface):
    """
    Dhan API adapter.
    
    Maps Dhan API to standardized broker interface.
    """
    
    BASE_URL = "https://api.dhan.co"
    
    def __init__(self, api_key: str, access_token: Optional[str] = None):
        """
        Initialize Dhan adapter.
        
        Args:
            api_key: Dhan API key
            access_token: Optional pre-authenticated token
        """
        self.api_key = api_key
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": self.api_key,
        })
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
            })
    
    def authenticate(self, api_key: str, api_secret: str) -> str:
        """
        Authenticate with Dhan API.
        
        Note: Dhan uses API key + secret. The access token may be
        generated differently. Adjust based on actual Dhan API docs.
        """
        # TODO: Implement actual Dhan authentication
        # This is a placeholder - check Dhan API documentation
        try:
            response = self.session.post(
                f"{self.BASE_URL}/oauth/token",
                json={
                    "api_key": api_key,
                    "api_secret": api_secret,
                }
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            if not self.access_token:
                raise BrokerAuthenticationError("No access token in response")
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
            })
            return self.access_token
        except requests.RequestException as e:
            raise BrokerAuthenticationError(f"Dhan authentication failed: {str(e)}")
    
    def place_order(self, order_request: BrokerOrderRequest) -> BrokerOrderResponse:
        """
        Place order via Dhan API.
        
        Maps standardized order request to Dhan API format.
        """
        try:
            # Map to Dhan order format
            dhan_order = self._map_order_to_dhan(order_request)
            
            response = self.session.post(
                f"{self.BASE_URL}/orders",
                json=dhan_order
            )
            response.raise_for_status()
            data = response.json()
            
            # Map Dhan response to standardized format
            broker_order_id = data.get("orderId") or data.get("dhanOrderId")
            if not broker_order_id:
                raise BrokerOrderError("No order ID in Dhan response")
            
            status = "success" if data.get("status") == "SUCCESS" else "pending"
            
            return BrokerOrderResponse(
                broker_order_id=str(broker_order_id),
                status=status,
                message=data.get("message"),
                raw_response=data,
            )
        except requests.RequestException as e:
            raise BrokerOrderError(f"Dhan order placement failed: {str(e)}")
    
    def cancel_order(self, broker_order_id: str) -> bool:
        """Cancel order via Dhan API."""
        try:
            response = self.session.delete(
                f"{self.BASE_URL}/orders/{broker_order_id}"
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            raise BrokerOrderError(f"Dhan order cancellation failed: {str(e)}")
    
    def get_order_status(self, broker_order_id: str) -> BrokerOrderStatus:
        """Get order status from Dhan API."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/orders/{broker_order_id}"
            )
            response.raise_for_status()
            data = response.json()
            
            # Map Dhan order status to standardized format
            return BrokerOrderStatus(
                broker_order_id=broker_order_id,
                status=self._map_dhan_status(data.get("orderStatus")),
                filled_quantity=data.get("filledQty", 0),
                average_price=Decimal(str(data.get("averagePrice", 0))) if data.get("averagePrice") else None,
                message=data.get("message"),
                raw_response=data,
            )
        except requests.RequestException as e:
            raise BrokerOrderError(f"Dhan order status fetch failed: {str(e)}")
    
    def fetch_positions(self) -> List[BrokerPosition]:
        """Fetch positions from Dhan API."""
        try:
            response = self.session.get(f"{self.BASE_URL}/positions")
            response.raise_for_status()
            data = response.json()
            
            positions = []
            for pos_data in data.get("data", []):
                positions.append(BrokerPosition(
                    symbol=pos_data.get("symbol"),
                    exchange=pos_data.get("exchange", "NSE"),
                    quantity=int(pos_data.get("quantity", 0)),
                    average_price=Decimal(str(pos_data.get("averagePrice", 0))),
                    last_price=Decimal(str(pos_data.get("lastPrice", 0))) if pos_data.get("lastPrice") else None,
                    product_type=ProductType(pos_data.get("productType", "INTRADAY")),
                ))
            return positions
        except requests.RequestException as e:
            raise BrokerException(f"Dhan positions fetch failed: {str(e)}")
    
    def fetch_orders(
        self,
        status: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> List[BrokerOrderStatus]:
        """Fetch orders from Dhan API."""
        try:
            params = {}
            if status:
                params["status"] = status
            if symbol:
                params["symbol"] = symbol
            
            response = self.session.get(f"{self.BASE_URL}/orders", params=params)
            response.raise_for_status()
            data = response.json()
            
            orders = []
            for order_data in data.get("data", []):
                orders.append(BrokerOrderStatus(
                    broker_order_id=str(order_data.get("orderId")),
                    status=self._map_dhan_status(order_data.get("orderStatus")),
                    filled_quantity=order_data.get("filledQty", 0),
                    average_price=Decimal(str(order_data.get("averagePrice", 0))) if order_data.get("averagePrice") else None,
                    raw_response=order_data,
                ))
            return orders
        except requests.RequestException as e:
            raise BrokerException(f"Dhan orders fetch failed: {str(e)}")
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance from Dhan API."""
        try:
            response = self.session.get(f"{self.BASE_URL}/funds")
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            raise BrokerException(f"Dhan balance fetch failed: {str(e)}")
    
    def _map_order_to_dhan(self, order_request: BrokerOrderRequest) -> Dict[str, Any]:
        """
        Map standardized order request to Dhan API format.
        
        Adjust based on actual Dhan API documentation.
        """
        dhan_order = {
            "securityId": order_request.symbol,
            "exchangeSegment": order_request.exchange,
            "transactionType": order_request.transaction_type.value,
            "quantity": order_request.quantity,
            "productType": order_request.product_type.value,
            "orderType": order_request.order_type.value,
        }
        
        if order_request.price:
            dhan_order["price"] = float(order_request.price)
        
        if order_request.trigger_price:
            dhan_order["triggerPrice"] = float(order_request.trigger_price)
        
        return dhan_order
    
    def _map_dhan_status(self, dhan_status: str) -> str:
        """
        Map Dhan order status to standardized status.
        
        Adjust based on actual Dhan status values.
        """
        status_map = {
            "PENDING": "pending",
            "OPEN": "open",
            "EXECUTED": "filled",
            "PARTIALLY_EXECUTED": "partially_filled",
            "CANCELLED": "cancelled",
            "REJECTED": "rejected",
            "EXPIRED": "expired",
        }
        return status_map.get(dhan_status.upper(), "pending")

