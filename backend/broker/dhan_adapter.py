"""
Dhan API v2 adapter implementation using official DhanHQ Python SDK.

Based on official DhanHQ Python SDK: https://github.com/dhan-oss/DhanHQ-py
API Documentation: https://dhanhq.co/docs/v2/
"""

import asyncio
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from dhanhq import dhanhq

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


class DhanAdapter(BrokerInterface):
    """
    Dhan API v2 adapter using official DhanHQ Python SDK.
    
    API Documentation: https://dhanhq.co/docs/v2/
    SDK Repository: https://github.com/dhan-oss/DhanHQ-py
    """
    
    def __init__(
        self,
        api_key: str,
        access_token: str,
        account_id: str,
        sandbox: bool = False,
    ):
        """
        Initialize Dhan adapter using official SDK.
        
        Args:
            api_key: Dhan API key (client_id)
            access_token: Dhan access token (JWT, valid for 24 hours)
            account_id: Dhan account ID (clientId)
            sandbox: Use sandbox environment (Note: SDK may handle this automatically)
        """
        self.api_key = api_key  # This is the client-id
        self.access_token = access_token
        self.account_id = account_id  # This should be the same as client-id
        self.sandbox = sandbox
        
        # Initialize DhanHQ SDK
        # SDK constructor: dhanhq(client_id, access_token, disable_ssl=False, pool=None)
        self.dhan = dhanhq(self.api_key, self.access_token, disable_ssl=False)
    
    async def authenticate(self, api_key: str, api_secret: str) -> str:
        """
        Authenticate with Dhan API.
        
        Note: Dhan v2 uses pre-generated access tokens via OAuth.
        Access tokens are valid for 24 hours.
        This method is provided for interface compatibility.
        
        Args:
            api_key: Dhan API key (client_id)
            api_secret: Not used in v2 (kept for interface compatibility)
            
        Returns:
            Access token (uses existing access_token if available)
            
        Raises:
            BrokerAuthenticationError: If authentication fails
        """
        if not self.access_token:
            raise BrokerAuthenticationError("Dhan v2 requires a pre-generated access token")
        return self.access_token
    
    async def place_order(self, order_request: BrokerOrderRequest) -> BrokerOrderResponse:
        """
        Place an order via Dhan API v2 using official SDK.
        
        Reference: https://github.com/dhan-oss/DhanHQ-py
        """
        try:
            # Map our order request to Dhan SDK format
            exchange = getattr(order_request, 'exchange', 'NSE')
            exchange_segment = self._get_exchange_segment(exchange)
            
            # Get transaction type constant from SDK
            # SDK uses: BUY, SELL
            transaction_type = self.dhan.BUY if order_request.transaction_type.value.upper() == "BUY" else self.dhan.SELL
            
            # Get order type constant from SDK
            # SDK uses: MARKET, LIMIT, SL, SL-M
            order_type_map = {
                "MARKET": self.dhan.MARKET,
                "LIMIT": self.dhan.LIMIT,
                "STOP_LOSS_MARKET": "SL",
                "STOP_LOSS_LIMIT": "SL-M",
            }
            order_type = order_type_map.get(order_request.order_type.value.upper(), self.dhan.MARKET)
            
            # Get product type constant from SDK
            # SDK uses: INTRADAY, MARGIN, CASH, CNC, CO, BO
            product_type_map = {
                "INTRADAY": self.dhan.INTRA,
                "MARGIN": self.dhan.MARGIN,
                "CASH": self.dhan.CASH,
                "CNC": self.dhan.CNC,
                "CO": self.dhan.CO,
                "BO": self.dhan.BO,
            }
            product_type = product_type_map.get(order_request.product_type.value.upper(), self.dhan.INTRA)
            
            # SDK place_order signature:
            # place_order(security_id, exchange_segment, transaction_type, quantity, order_type, product_type, price, ...)
            security_id = self._get_security_id(order_request.symbol, exchange)
            quantity = order_request.quantity
            price = float(order_request.price) if order_request.price else 0
            
            # Optional parameters
            trigger_price = float(order_request.trigger_price) if hasattr(order_request, 'trigger_price') and order_request.trigger_price else 0
            disclosed_quantity = order_request.disclosed_quantity if hasattr(order_request, 'disclosed_quantity') and order_request.disclosed_quantity else 0
            validity = order_request.validity if hasattr(order_request, 'validity') and order_request.validity else 'DAY'
            tag = order_request.tag if hasattr(order_request, 'tag') and order_request.tag else None
            
            # Call SDK method in thread pool (SDK is synchronous)
            # Positional arguments as per SDK signature
            result = await asyncio.to_thread(
                self.dhan.place_order,
                security_id,
                exchange_segment,
                transaction_type,
                quantity,
                order_type,
                product_type,
                price,
                trigger_price,
                disclosed_quantity,
                False,  # after_market_order
                validity,
                'OPEN',  # amo_time
                None,  # bo_profit_value
                None,  # bo_stop_loss_Value
                tag
            )
            
            # Map SDK response to our format
            if isinstance(result, dict):
                return BrokerOrderResponse(
                    broker_order_id=str(result.get("orderId", "")),
                    status=self._map_order_status(result.get("orderStatus", "PENDING")),
                    message=result.get("message", "Order placed successfully"),
                    raw_response=result,
                    client_order_id=order_request.client_order_id,
                )
            else:
                # SDK might return order ID directly
                return BrokerOrderResponse(
                    broker_order_id=str(result),
                    status="pending",
                    message="Order placed successfully",
                    raw_response={"orderId": result},
                    client_order_id=order_request.client_order_id,
                )
            
        except Exception as e:
            error_msg = str(e)
            if "error" in error_msg.lower() or "failed" in error_msg.lower():
                raise BrokerOrderError(f"Dhan API error: {error_msg}") from e
            raise BrokerOrderError(f"Failed to place order: {error_msg}") from e
    
    async def cancel_order(self, broker_order_id: str) -> bool:
        """
        Cancel an order via Dhan API v2 using official SDK.
        """
        try:
            result = await asyncio.to_thread(self.dhan.cancel_order, broker_order_id)
            return bool(result)
        except Exception as e:
            raise BrokerOrderError(f"Failed to cancel order: {str(e)}") from e
    
    async def modify_order(
        self,
        broker_order_id: str,
        quantity: Optional[int] = None,
        price: Optional[Decimal] = None,
    ) -> bool:
        """
        Modify an order via Dhan API v2 using official SDK.
        """
        try:
            # Build modify parameters
            modify_params = {}
            if quantity is not None:
                modify_params['quantity'] = quantity
            if price is not None:
                modify_params['price'] = float(price)
            
            result = await asyncio.to_thread(
                self.dhan.modify_order,
                broker_order_id,
                **modify_params
            )
            return bool(result)
        except Exception as e:
            raise BrokerOrderError(f"Failed to modify order: {str(e)}") from e
    
    async def get_order_status(self, broker_order_id: str) -> BrokerOrderStatus:
        """
        Get order status from Dhan API v2 using official SDK.
        """
        try:
            result = await asyncio.to_thread(self.dhan.get_order_by_id, broker_order_id)
            
            if not result:
                raise BrokerException(f"Order {broker_order_id} not found")
            
            # SDK returns order data as dict
            order_data = result if isinstance(result, dict) else {}
            
            return BrokerOrderStatus(
                broker_order_id=str(order_data.get("orderId", broker_order_id)),
                status=self._map_order_status(order_data.get("orderStatus", "PENDING")),
                filled_quantity=order_data.get("filledQuantity", 0),
                average_price=Decimal(str(order_data.get("averagePrice", 0))) if order_data.get("averagePrice") else None,
                message=order_data.get("message"),
                raw_response=order_data,
                client_order_id=order_data.get("clientOrderId"),
                symbol=order_data.get("symbol", ""),
                exchange=order_data.get("exchangeSegment", "NSE"),
                order_type=self._map_order_type(order_data.get("orderType")),
                product_type=self._map_product_type(order_data.get("productType")),
                transaction_type=self._map_transaction_type(order_data.get("transactionType")),
                quantity=order_data.get("quantity", 0),
                price=Decimal(str(order_data.get("price", 0))) if order_data.get("price") else None,
                trigger_price=Decimal(str(order_data.get("triggerPrice", 0))) if order_data.get("triggerPrice") else None,
                order_timestamp=self._parse_datetime(order_data.get("orderTime") or order_data.get("orderTimestamp")),
                exchange_order_id=order_data.get("exchangeOrderId"),
                exchange_timestamp=self._parse_datetime(order_data.get("exchangeTime") or order_data.get("exchangeTimestamp")),
                status_message=order_data.get("statusMessage"),
                filled_price=Decimal(str(order_data.get("filledPrice", 0))) if order_data.get("filledPrice") else None,
                remaining_quantity=order_data.get("remainingQuantity"),
                order_tag=order_data.get("orderTag"),
                algo_id=order_data.get("algoId"),
                leg_name=order_data.get("legName"),
                message_code=order_data.get("messageCode"),
                message_description=order_data.get("messageDescription"),
            )
        except Exception as e:
            raise BrokerException(f"Failed to get order status: {str(e)}") from e
    
    async def fetch_positions(self) -> List[BrokerPosition]:
        """
        Fetch positions from Dhan API v2 using official SDK.
        """
        try:
            result = await asyncio.to_thread(self.dhan.get_positions)
            
            positions = []
            positions_data = result if isinstance(result, list) else (result.get("data", []) if isinstance(result, dict) else [])
            
            for pos in positions_data:
                positions.append(BrokerPosition(
                    symbol=pos.get("symbol", ""),
                    exchange=pos.get("exchangeSegment", "NSE"),
                    quantity=int(pos.get("quantity", 0)),
                    average_price=Decimal(str(pos.get("averagePrice", 0))) if pos.get("averagePrice") else Decimal("0"),
                    last_price=Decimal(str(pos.get("ltp", 0))) if pos.get("ltp") else None,
                    product_type=self._map_product_type(pos.get("productType")),
                ))
            
            return positions
        except Exception as e:
            raise BrokerException(f"Failed to fetch positions: {str(e)}") from e
    
    async def fetch_orders(
        self,
        status: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> List[BrokerOrderStatus]:
        """
        Fetch orders from Dhan API v2 using official SDK.
        """
        try:
            result = await asyncio.to_thread(self.dhan.get_order_list)
            
            orders = []
            orders_data = result if isinstance(result, list) else (result.get("data", []) if isinstance(result, dict) else [])
            
            # Filter by status and symbol if provided
            for order in orders_data:
                if status and order.get("orderStatus", "").upper() != status.upper():
                    continue
                if symbol and order.get("symbol", "") != symbol:
                    continue
                
                orders.append(BrokerOrderStatus(
                    broker_order_id=str(order.get("orderId", "")),
                    status=self._map_order_status(order.get("orderStatus", "PENDING")),
                    filled_quantity=order.get("filledQuantity", 0),
                    average_price=Decimal(str(order.get("averagePrice", 0))) if order.get("averagePrice") else None,
                    message=order.get("message"),
                    raw_response=order,
                    client_order_id=order.get("clientOrderId"),
                    symbol=order.get("symbol", ""),
                    exchange=order.get("exchangeSegment", "NSE"),
                    order_type=self._map_order_type(order.get("orderType")),
                    product_type=self._map_product_type(order.get("productType")),
                    transaction_type=self._map_transaction_type(order.get("transactionType")),
                    quantity=order.get("quantity", 0),
                    price=Decimal(str(order.get("price", 0))) if order.get("price") else None,
                    trigger_price=Decimal(str(order.get("triggerPrice", 0))) if order.get("triggerPrice") else None,
                    order_timestamp=self._parse_datetime(order.get("orderTime") or order.get("orderTimestamp")),
                    exchange_order_id=order.get("exchangeOrderId"),
                    exchange_timestamp=self._parse_datetime(order.get("exchangeTime") or order.get("exchangeTimestamp")),
                    status_message=order.get("statusMessage"),
                    filled_price=Decimal(str(order.get("filledPrice", 0))) if order.get("filledPrice") else None,
                    remaining_quantity=order.get("remainingQuantity"),
                    order_tag=order.get("orderTag"),
                    algo_id=order.get("algoId"),
                    leg_name=order.get("legName"),
                    message_code=order.get("messageCode"),
                    message_description=order.get("messageDescription"),
                ))
            
            return orders
        except Exception as e:
            raise BrokerException(f"Failed to fetch orders: {str(e)}") from e
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance from Dhan API v2 using official SDK.
        
        Uses get_fund_limits() method from SDK which provides fund information.
        """
        try:
            # Use SDK's get_fund_limits() method
            result = await asyncio.to_thread(self.dhan.get_fund_limits)
            
            if not result:
                raise BrokerException("No fund data received from Dhan API")
            
            # SDK returns fund limits data
            fund_data = result if isinstance(result, dict) else {}
            
            # Map SDK response to standardized format
            # The SDK returns fields like: availableBalance, usedMargin, totalMargin, etc.
            available_balance = (
                fund_data.get("availableBalance") or 
                fund_data.get("available_balance") or 
                fund_data.get("available") or 
                fund_data.get("balance") or 
                0
            )
            used_margin = (
                fund_data.get("usedMargin") or 
                fund_data.get("used_margin") or 
                fund_data.get("marginUsed") or 
                0
            )
            total_margin = (
                fund_data.get("totalMargin") or 
                fund_data.get("total_margin") or 
                fund_data.get("marginTotal") or 
                0
            )
            collateral = (
                fund_data.get("collateral") or 
                fund_data.get("collateralValue") or 
                0
            )
            
            return {
                "available_balance": Decimal(str(available_balance)),
                "used_margin": Decimal(str(used_margin)),
                "total_margin": Decimal(str(total_margin)),
                "collateral": Decimal(str(collateral)),
                "raw_response": fund_data,
            }
        except Exception as e:
            error_msg = str(e)
            raise BrokerException(f"Failed to get account balance: {error_msg}") from e
    
    async def close(self):
        """Close SDK connection (if needed)."""
        # SDK doesn't require explicit closing, but we can clean up if needed
        pass
    
    # Helper methods
    
    def _get_exchange_segment(self, exchange: str) -> str:
        """Map exchange name to Dhan exchange segment."""
        mapping = {
            "NSE": "NSE_EQ",
            "BSE": "BSE_EQ",
            "NSE_FO": "NSE_FO",
            "BSE_FO": "BSE_FO",
            "MCX": "MCX_COMM",
        }
        return mapping.get(exchange.upper(), "NSE_EQ")
    
    def _get_security_id(self, symbol: str, exchange: str) -> str:
        """
        Get security ID for a symbol.
        
        Note: In v2 API, you need to use securityId instead of symbol.
        This requires mapping symbol to securityId using the instrument list.
        For now, we'll use the symbol as-is, but in production you should
        maintain a mapping of symbol -> securityId.
        
        TODO: Use SDK's fetch_security_list() to get proper securityId mapping
        """
        # For now, return symbol as-is (this may need to be updated based on actual API)
        # In production, you should fetch securityId from SDK's fetch_security_list() method
        return symbol
    
    def _map_order_status(self, dhan_status: str) -> str:
        """Map Dhan order status to our status enum."""
        status_mapping = {
            "PENDING": "pending",
            "OPEN": "open",
            "TRANSIT": "submitted",
            "REJECTED": "rejected",
            "CANCELLED": "cancelled",
            "EXECUTED": "filled",
            "PARTIALLY_EXECUTED": "partially_filled",
        }
        return status_mapping.get(dhan_status.upper(), "pending")
    
    def _map_order_type(self, dhan_order_type: Optional[str]):
        """Map Dhan order type to our OrderType enum."""
        from database.models import OrderType
        if not dhan_order_type:
            return OrderType.MARKET
        mapping = {
            "MARKET": OrderType.MARKET,
            "LIMIT": OrderType.LIMIT,
            "SL": OrderType.STOP_LOSS_MARKET,
            "SL-M": OrderType.STOP_LOSS_LIMIT,
        }
        return mapping.get(dhan_order_type.upper(), OrderType.MARKET)
    
    def _map_product_type(self, dhan_product_type: Optional[str]):
        """Map Dhan product type to our ProductType enum."""
        from database.models import ProductType
        if not dhan_product_type:
            return ProductType.INTRADAY
        mapping = {
            "INTRADAY": ProductType.INTRADAY,
            "MARGIN": ProductType.MARGIN,
            "CASH": ProductType.CASH,
            "CNC": ProductType.CNC,
            "CO": ProductType.CO,
            "BO": ProductType.BO,
        }
        return mapping.get(dhan_product_type.upper(), ProductType.INTRADAY)
    
    def _map_transaction_type(self, dhan_transaction_type: Optional[str]):
        """Map Dhan transaction type to our TransactionType enum."""
        from database.models import TransactionType
        if not dhan_transaction_type:
            return TransactionType.BUY
        mapping = {
            "BUY": TransactionType.BUY,
            "SELL": TransactionType.SELL,
        }
        return mapping.get(dhan_transaction_type.upper(), TransactionType.BUY)
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse Dhan datetime string."""
        if not dt_str:
            return None
        try:
            # Try common formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%d-%m-%Y %H:%M:%S",
                "%Y-%m-%d",
            ]:
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
            # Try ISO format
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            return None
