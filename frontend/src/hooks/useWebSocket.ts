import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  data?: any;
}

export function useWebSocket(channel: 'dashboard' | 'alerts' = 'dashboard', onMessageReceived?: (msg: WebSocketMessage) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/${channel}`;

    try {
      const socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const parsed: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(parsed);
          if (onMessageReceived) {
            onMessageReceived(parsed);
          }
        } catch (err) {
          // Non-json ping/pong
        }
      };

      socket.onclose = () => {
        setIsConnected(false);
        // Automatic reconnection attempt after 3s
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 3000);
      };

      socket.onerror = () => {
        socket.close();
      };
    } catch (e) {
      setIsConnected(false);
    }
  }, [channel, onMessageReceived]);

  useEffect(() => {
    connect();
    // Keep alive heartbeat ping every 25s
    const pingInterval = window.setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 25000);

    return () => {
      window.clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected, lastMessage };
}
