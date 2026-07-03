import { useCallback, useEffect, useRef, useState } from "react";

const WS_URL = (import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000") + "/ws";

type Handler = (payload: unknown) => void;

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null);
  const listeners = useRef<Map<string, Set<Handler>>>(new Map());
  const retry = useRef(0);
  const [connected, setConnected] = useState(false);

  const connect = useCallback(() => {
    const token = localStorage.getItem("fc_token");
    if (!token) return;
    const socket = new WebSocket(`${WS_URL}?token=${encodeURIComponent(token)}`);
    ws.current = socket;

    socket.onopen = () => { setConnected(true); retry.current = 0; };
    socket.onmessage = (e) => {
      try {
        const { event, payload } = JSON.parse(e.data);
        listeners.current.get(event)?.forEach(h => h(payload));
      } catch {}
    };
    socket.onclose = () => {
      setConnected(false);
      if (retry.current < 5) {
        setTimeout(connect, 1000 * Math.pow(2, retry.current++));
      }
    };
  }, []);

  useEffect(() => {
    connect();
    return () => ws.current?.close();
  }, [connect]);

  const send = useCallback((event: string, payload: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN)
      ws.current.send(JSON.stringify({ event, payload }));
  }, []);

  const subscribe = useCallback((event: string, handler: Handler) => {
    if (!listeners.current.has(event)) listeners.current.set(event, new Set());
    listeners.current.get(event)!.add(handler);
    return () => listeners.current.get(event)?.delete(handler);
  }, []);

  return { connected, send, subscribe };
}
