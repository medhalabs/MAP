"""
Broker factory for creating broker adapters.
"""

from typing import Optional
from broker.base import BrokerInterface
from broker.dhan_adapter import DhanAdapter


def create_broker_adapter(
    broker_name: str,
    api_key: str,
    api_secret: Optional[str] = None,
    access_token: Optional[str] = None,
) -> BrokerInterface:
    """
    Factory function to create broker adapter instances.
    
    Args:
        broker_name: Name of broker ("dhan", etc.)
        api_key: Broker API key
        api_secret: Broker API secret (if needed)
        access_token: Pre-authenticated token (if available)
        
    Returns:
        BrokerInterface instance
        
    Raises:
        ValueError: If broker_name is not supported
    """
    broker_name_lower = broker_name.lower()
    
    if broker_name_lower == "dhan":
        adapter = DhanAdapter(api_key=api_key, access_token=access_token)
        if not access_token and api_secret:
            adapter.authenticate(api_key, api_secret)
        return adapter
    else:
        raise ValueError(f"Unsupported broker: {broker_name}")

