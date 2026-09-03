import { useEffect, useRef } from 'react';
import { WS_URL } from '../api/client';

export const useBoardSocket = (
  boardId: string | undefined,
  onEventReceived: (event: string, data: any) => void
) => {
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!boardId || !token) return;

    const ws = new WebSocket(`${WS_URL}/ws/boards/${boardId}?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event && payload.data) {
          onEventReceived(payload.event, payload.data);
        }
      } catch (err) {
        console.error('Erro ao ler mensagem WebSocket:', err);
      }
    };

    ws.onerror = (err) => console.error('Erro na conexão WebSocket:', err);

    return () => {
      ws.close();
    };
  }, [boardId]);
};