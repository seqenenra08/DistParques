/**
 * Hook personalizado para manejar WebSocket en componentes React
 */

import { useEffect, useState } from 'react';
import socketService from '../services/socketService';

export function useSocket() {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Conectar al montar el componente
    socketService.connect();

    // Escuchar eventos de conexión
    const handleConnect = (data) => {
      console.log('[useSocket] Conectado:', data);
      setConnected(true);
      
      // ✨ Intentar reconexión automática al conectar
      if (typeof window !== 'undefined') {
        const savedRoomCode = sessionStorage.getItem('room_code');
        const savedPlayerId = sessionStorage.getItem('player_id');
        
        if (savedRoomCode) {
          console.log('[RECONNECT] Intentando reconectar a sala:', savedRoomCode);
          setTimeout(() => {
            socketService.emit('reconnect_to_game', {
              roomCode: savedRoomCode,
              playerId: savedPlayerId
            });
          }, 500);
        }
      }
    };

    const handleDisconnect = (data) => {
      console.log('[useSocket] Desconectado:', data);
      setConnected(false);
    };

    socketService.on('connect', handleConnect);
    socketService.on('disconnect', handleDisconnect);

    // Cleanup al desmontar
    return () => {
      socketService.off('connect', handleConnect);
      socketService.off('disconnect', handleDisconnect);
      socketService.disconnect();
    };
  }, []);

  return {
    socket: socketService, // Devolver el socketService completo, no el WebSocket nativo
    connected,
    emit: (event, data) => socketService.emit(event, data),
    on: (event, callback) => socketService.on(event, callback),
    off: (event, callback) => socketService.off(event, callback)
  };
}
