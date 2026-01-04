"""
WebSocket routes for real-time updates.

Provides real-time updates for:
- Order status changes
- P&L updates
- Strategy logs
- Risk alerts
"""

from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.websockets import WebSocketState
import json
from datetime import datetime

from database.schemas import WebSocketEvent

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        # Map user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a WebSocket for a user."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to all connections for a user."""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                if connection.client_state == WebSocketState.CONNECTED:
                    try:
                        await connection.send_json(message)
                    except Exception:
                        disconnected.add(connection)
                else:
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast(self, message: dict, user_ids: Set[int] = None):
        """Broadcast message to specified users (or all if None)."""
        if user_ids is None:
            user_ids = set(self.active_connections.keys())
        
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for real-time updates.
    
    Query params:
        token: JWT authentication token
    """
    # Validate token and get user_id
    from jose import jwt
    from config import settings
    
    try:
        # Decode token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back (or handle client messages)
            await websocket.send_json({
                "event_type": "pong",
                "data": {"message": "Received"},
                "timestamp": datetime.utcnow().isoformat(),
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


# Helper functions to send events
async def send_order_update(user_id: int, order_data: dict):
    """Send order update event."""
    event = WebSocketEvent(
        event_type="order_update",
        data=order_data,
    )
    await manager.send_personal_message(event.dict(), user_id)


async def send_pnl_update(user_id: int, pnl_data: dict):
    """Send P&L update event."""
    event = WebSocketEvent(
        event_type="pnl_update",
        data=pnl_data,
    )
    await manager.send_personal_message(event.dict(), user_id)


async def send_strategy_log(user_id: int, log_data: dict):
    """Send strategy log event."""
    event = WebSocketEvent(
        event_type="strategy_log",
        data=log_data,
    )
    await manager.send_personal_message(event.dict(), user_id)


async def send_risk_alert(user_id: int, alert_data: dict):
    """Send risk alert event."""
    event = WebSocketEvent(
        event_type="risk_alert",
        data=alert_data,
    )
    await manager.send_personal_message(event.dict(), user_id)

