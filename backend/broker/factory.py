"""
Broker factory for creating broker adapters.
"""

from typing import Optional
from broker.base import BrokerInterface
from broker.dhan_adapter import DhanAdapter


def create_broker_adapter(
    broker_name: str,
    api_key: str,
    access_token: Optional[str] = None,
    account_id: Optional[str] = None,
    sandbox: bool = False,
) -> BrokerInterface:
    """
    Factory function to create broker adapter instances.
    
    Args:
        broker_name: Name of broker ("dhan", etc.)
        api_key: Broker API key
        access_token: Pre-authenticated token (required for Dhan)
        account_id: Broker account ID (required for Dhan)
        sandbox: Use sandbox environment
        
    Returns:
        BrokerInterface instance
        
    Raises:
        ValueError: If broker_name is not supported or required parameters are missing
    """
    broker_name_lower = broker_name.lower()
    
    if broker_name_lower == "dhan":
        if not access_token:
            raise ValueError("Dhan adapter requires access_token")
        if not account_id:
            raise ValueError("Dhan adapter requires account_id")
        return DhanAdapter(
            api_key=api_key,
            access_token=access_token,
            account_id=account_id,
            sandbox=sandbox,
        )
    else:
        raise ValueError(f"Unsupported broker: {broker_name}")

