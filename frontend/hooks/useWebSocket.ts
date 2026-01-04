'use client'

import { useEffect, useState, useRef } from 'react'

interface WebSocketEvent {
  event_type: string
  data: any
  timestamp: string
}

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false)
  const [events, setEvents] = useState<WebSocketEvent[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      return
    }

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/api/ws/?token=${token}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setEvents((prev) => [...prev, data])
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      setIsConnected(false)
      // Reconnect after 5 seconds
      setTimeout(() => {
        if (token) {
          // Reconnect logic would go here
        }
      }, 5000)
    }

    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [])

  return {
    isConnected,
    events,
  }
}

